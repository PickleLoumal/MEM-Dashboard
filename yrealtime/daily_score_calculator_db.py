"""
Daily Stock Score Calculator with PostgreSQL Storage
每天自动计算所有股票的买卖信号评分并存储到数据库

Enhanced Quantitative Trading Strategy (Updated: 2025-10-23)
================================================================

基于新量化策略的评分体系，整合以下指标：
1. 动量交易 (Momentum, 20%): 14天价格变化率
2. RSI (20%): 相对强度指数，识别超买/超卖
3. CMF (15%): Chaikin Money Flow，资金流向
4. MFM (5%): Money Flow Multiplier，资金流乘数
5. OBV (15%): On-Balance Volume，成交量趋势
6. 双均线 (10%): MA5/MA10金叉死叉
7. 背离分析 (10%): RSI/CMF/OBV看涨/看跌背离
8. 网格交易 (5%): 支撑位/阻力位机会识别

评分体系：
- 买入评分：0-100分（各组件加权求和）
- 卖出评分：0-100分（各组件加权求和）
- 买入阈值：≥70分触发买入信号
- 卖出阈值：≥70分触发卖出信号
- 成交量过滤：当前成交量需>5日均量的120%

该策略适用于短期（1-7天）交易，强调系统化决策和风险管理。
"""
import yfinance as yf
import requests
import pandas as pd
import numpy as np
from datetime import datetime, date
import os
import sys
import traceback
from pathlib import Path

from pandas.tseries.offsets import BDay
import psycopg2
from psycopg2.extras import Json, execute_values

# Note: yfinance 0.2.36+ handles sessions internally with curl_cffi
# No need to create custom session - let yfinance handle it

# 数据库配置 - 直接从环境变量读取（适配 ECS Secrets Manager）
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'mem_dashboard'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password'),
}

print(f"🔧 Database Configuration:")
print(f"   Environment: {ENVIRONMENT}")
print(f"   Host: {DB_CONFIG['host']}")
print(f"   Database: {DB_CONFIG['database']}")
print(f"   User: {DB_CONFIG['user']}")


def get_db_connection():
    """创建数据库连接"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise


# 新量化策略阈值 (基于-100到+100评分体系)
# 正分 = 买入信号，负分 = 卖出信号
BUY_THRESHOLD = 70   # 总分 > +70触发买入
SELL_THRESHOLD = -70  # 总分 < -70触发卖出

# 指标权重配置 (总和100%)
WEIGHTS = {
    'momentum': 0.20,      # 动量交易 20%
    'rsi': 0.20,           # RSI 20%
    'cmf': 0.15,           # CMF 15%
    'mfm': 0.05,           # MFM 5%
    'obv': 0.15,           # OBV 15%
    'dual_ma': 0.10,       # 双均线 10%
    'divergence': 0.10,    # 背离分析 10%
    'grid': 0.05,          # 网格交易 5% (可选)
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-6, "WEIGHTS must sum to 1.0"

# === 执行与风控参数（可根据回测调优） ===
MAX_HOLD_DAYS = 7               # 最长持仓天数
STOP_LOSS_PCT = 0.02            # 止损阈值（2%）
TAKE_PROFIT_PCT = 0.05          # 止盈/跟踪止盈起点（5%）
ENFORCE_VOLUME_FILTER = True    # 成交量过滤不通过则不下单
NEXT_DAY_EXECUTION = True       # 信号次一交易日执行
SUGGESTED_POSITION_PCT = 0.05   # 单笔建议仓位（5%）

# 成交量放大过滤阈值
VOLUME_EXPANSION_THRESHOLD = 1.20  # 当前交易日成交量 > 5日均量的120%

def determine_recommended_action(total_score, volume_passed):
    """
    根据统一评分生成投资建议
    
    Args:
        total_score: -100到+100的统一评分
            正分 = 买入信号
            负分 = 卖出信号
    
    Returns:
        str: "Buy", "Sell", 或 "Hold"
    """
    if not volume_passed and ENFORCE_VOLUME_FILTER:
        return "Hold"
    if total_score >= BUY_THRESHOLD:
        return "Buy"
    elif total_score <= SELL_THRESHOLD:
        return "Sell"
    else:
        return "Hold"


def build_recommendation_detail(data, calculation_date):
    """构建推荐详情描述（增强版，包含新指标）"""
    lines = [
        f"Calculation date: {calculation_date.isoformat()}",
    ]

    last_date = data.get('last_date')
    if last_date:
        lines.append(f"Last trading date: {last_date.isoformat()}")

    last_close = data.get('last_close')
    if last_close is not None:
        lines.append(f"Previous close: {last_close:.2f}")

    # 新增指标值显示
    lines.append("")
    lines.append("Key Indicators:")
    
    rsi = data.get('rsi')
    if rsi is not None:
        lines.append(f"- RSI: {rsi:.1f}")
    
    momentum_pct = data.get('momentum_pct')
    if momentum_pct is not None:
        lines.append(f"- Momentum (14d): {momentum_pct:+.2f}%")
    
    cmf_value = data.get('cmf_value')
    if cmf_value is not None:
        lines.append(f"- CMF: {cmf_value:.3f}")
    
    obv_value = data.get('obv_value')
    if obv_value is not None:
        lines.append(f"- OBV: {obv_value:,}")
    
    ma5 = data.get('ma5')
    ma10 = data.get('ma10')
    ma20 = data.get('ma20')
    if ma5 and ma20:
        lines.append(f"- MA5: {ma5:.2f}, MA20: {ma20:.2f}")
    elif ma5 and ma10:
        lines.append(f"- MA5: {ma5:.2f}, MA10: {ma10:.2f}")

    lines.append("")
    total_score = data.get('total_score', 0)
    
    lines.append(f"Total Score: {total_score:+.1f} / 100")
    lines.append(f"  Buy Threshold: ≥ {BUY_THRESHOLD}")
    lines.append(f"  Sell Threshold: ≤ {SELL_THRESHOLD}")
    lines.append("")
    
    stop_loss_price = data.get('stop_loss_price')
    take_profit_price = data.get('take_profit_price')
    position_pct = data.get('suggested_position_pct')
    execution_date = data.get('execution_date')
    signal_date = data.get('signal_date') or data.get('last_date')
    lines.append("Execution & Risk:")
    execution_label = "Next open (T+1)" if NEXT_DAY_EXECUTION else "Same day"
    if execution_date:
        lines.append(f"- Execution: {execution_label} (target {execution_date})")
    else:
        lines.append(f"- Execution: {execution_label}")
    if signal_date:
        lines.append(f"- Signal date: {signal_date}")
    if stop_loss_price and take_profit_price:
        lines.append(f"- Risk band: SL {stop_loss_price:.4f} | TP {take_profit_price:.4f}")
    if position_pct is not None:
        lines.append(f"- Suggested position: {position_pct*100:.0f}%")
    lines.append("")
    
    signal_reasons = data.get('signal_reasons') or []
    if signal_reasons:
        if total_score > 0:
            lines.append("Bullish Signals (Positive Score):")
        elif total_score < 0:
            lines.append("Bearish Signals (Negative Score):")
        else:
            lines.append("Neutral Signals:")
        lines.extend(f"- {reason}" for reason in signal_reasons)
    else:
        lines.append("No significant signals detected")
    
    components = data.get('score_components') or {}
    if components:
        lines.append("")
        lines.append("Component Contributions (raw | weight | weighted):")
        for component_key in WEIGHTS.keys():
            comp = components.get(component_key, {})
            raw = comp.get('raw', 0)
            weight = comp.get('weight', WEIGHTS[component_key])
            weighted = comp.get('weighted', raw * weight)
            lines.append(f"- {component_key:<10s}: {raw:+.0f} | {weight*100:>2.0f}% | {weighted:+.2f}")

    return "\n".join(lines)


def check_volume_expansion(df):
    """
    成交量放大过滤：当前交易日成交量必须超过过去5天平均成交量的120%
    返回: (bool, reason_str)
    """
    if df is None or len(df) < 6:
        return False, "Insufficient data for volume check"
    
    latest_volume = df.iloc[-1]['Volume']
    avg_5day_volume = df['Volume'].iloc[-6:-1].mean()
    
    if avg_5day_volume == 0:
        return False, "Zero average volume"
    
    expansion_ratio = latest_volume / avg_5day_volume
    
    if expansion_ratio >= VOLUME_EXPANSION_THRESHOLD:
        return True, f"Volume expansion: {expansion_ratio:.2f}x (>1.20x required)"
    else:
        return False, f"Volume insufficient: {expansion_ratio:.2f}x (<1.20x required)"


def detect_bullish_divergence(df, indicator_name='RSI'):
    """
    检测看涨背离：价格创更低低点，但指标形成更高低点
    返回: (score, reason)
    """
    if df is None or len(df) < 10:
        return 0, ""
    
    recent_10 = df.tail(10)
    price_lows = []
    indicator_lows = []
    
    # 寻找价格和指标的局部低点
    for i in range(1, len(recent_10) - 1):
        if (recent_10.iloc[i]['Close'] < recent_10.iloc[i-1]['Close'] and 
            recent_10.iloc[i]['Close'] < recent_10.iloc[i+1]['Close']):
            price_lows.append((i, recent_10.iloc[i]['Close']))
            
            if pd.notna(recent_10.iloc[i][indicator_name]):
                indicator_lows.append((i, recent_10.iloc[i][indicator_name]))
    
    # 至少需要2个低点才能判断背离
    if len(price_lows) >= 2 and len(indicator_lows) >= 2:
        # 比较最后两个低点
        if (price_lows[-1][1] < price_lows[-2][1] and  # 价格创新低
            indicator_lows[-1][1] > indicator_lows[-2][1]):  # 指标更高
            return 100, f"Strong bullish divergence detected ({indicator_name})"
        elif price_lows[-1][1] < price_lows[-2][1]:  # 仅价格新低，指标未明显更高
            return 50, f"Weak bullish divergence ({indicator_name})"
    
    return 0, ""


def detect_bearish_divergence(df, indicator_name='RSI'):
    """
    检测看跌背离：价格创更高高点，但指标形成更低高点
    返回: (score, reason)
    """
    if df is None or len(df) < 10:
        return 0, ""
    
    recent_10 = df.tail(10)
    price_highs = []
    indicator_highs = []
    
    # 寻找价格和指标的局部高点
    for i in range(1, len(recent_10) - 1):
        if (recent_10.iloc[i]['Close'] > recent_10.iloc[i-1]['Close'] and 
            recent_10.iloc[i]['Close'] > recent_10.iloc[i+1]['Close']):
            price_highs.append((i, recent_10.iloc[i]['Close']))
            
            if pd.notna(recent_10.iloc[i][indicator_name]):
                indicator_highs.append((i, recent_10.iloc[i][indicator_name]))
    
    # 至少需要2个高点才能判断背离
    if len(price_highs) >= 2 and len(indicator_highs) >= 2:
        # 比较最后两个高点
        if (price_highs[-1][1] > price_highs[-2][1] and  # 价格创新高
            indicator_highs[-1][1] < indicator_highs[-2][1]):  # 指标更低
            return 100, f"Strong bearish divergence detected ({indicator_name})"
        elif price_highs[-1][1] > price_highs[-2][1]:  # 仅价格新高，指标未明显更低
            return 50, f"Weak bearish divergence ({indicator_name})"
    
    return 0, ""


def calculate_indicators(df):
    """
    计算技术指标：MA5, MA10, MA20, OBV, CMF, RSI, Momentum, MFM
    基于新量化策略要求
    """
    if df is None or len(df) < 20:
        return df
    
    df = df.copy()
    
    # 移动平均线：MA5, MA10, MA20
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA10'] = df['Close'].rolling(window=10).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    
    # 动量指标 (14天周期)
    df['Momentum'] = df['Close'] - df['Close'].shift(14)
    df['Momentum_Pct'] = (df['Momentum'] / df['Close'].shift(14) * 100).replace([np.inf, -np.inf], np.nan)
    
    # RSI (14天，Wilder平滑)
    delta = df['Close'].diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = gains.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    avg_loss = losses.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    avg_loss = avg_loss.replace(0, np.nan)
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # OBV (向量化)
    close_diff = df['Close'].diff().fillna(0)
    direction = np.sign(close_diff)
    df['OBV'] = (direction * df['Volume']).cumsum()
    df['OBV_MA5'] = df['OBV'].rolling(window=5).mean()
    df['OBV_MA10'] = df['OBV'].rolling(window=10).mean()
    df['OBV_MA20'] = df['OBV'].rolling(window=20).mean()
    
    # MFM (Money Flow Multiplier) - CMF的组成部分
    df['MF_Multiplier'] = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
    df['MF_Multiplier'] = df['MF_Multiplier'].fillna(0)
    df['MF_Volume'] = df['MF_Multiplier'] * df['Volume']
    
    # CMF (Chaikin Money Flow, 21天周期)
    df['CMF'] = df['MF_Volume'].rolling(window=21).sum() / df['Volume'].rolling(window=21).sum()
    
    # 支撑位和阻力位 (20天高低点)
    df['Support'] = df['Low'].rolling(window=20).min()
    df['Resistance'] = df['High'].rolling(window=20).max()
    
    return df


def store_component(components, name, raw_score, reasons_list):
    """Helper to store component scoring data."""
    components[name] = {
        'raw': raw_score,
        'weight': WEIGHTS[name],
        'weighted': raw_score * WEIGHTS[name],
        'reasons': reasons_list[:] if reasons_list else []
    }


def format_reason(raw_score, text):
    """Prefix reason text with directional icon."""
    if raw_score > 0:
        icon = "✓"
    elif raw_score < 0:
        icon = "✗"
    else:
        icon = "•"
    return f"{icon} {text}"


def calculate_unified_signal(df):
    """
    计算统一信号评分 (-100到+100分体系)
    
    每个指标组件：
    - 满分+100分 = 强烈买入信号
    - 满分-100分 = 强烈卖出信号
    - 0分 = 中性
    
    采用加权评分机制：
    - 动量 (20%): 基于14天价格变化率
    - RSI (20%): 超买/超卖识别
    - CMF (15%): 资金流向确认
    - MFM (5%): 资金流乘数趋势
    - OBV (15%): 成交量趋势确认
    - 双均线 (10%): MA5/MA10金叉/死叉
    - 背离分析 (10%): 看涨/看跌背离检测
    - 网格交易 (5%): 支撑位/阻力位机会
    
    返回: (total_score, reasons_list, component_scores_dict)
    """
    if df is None or len(df) < 20:
        return 0, ["Insufficient data"], {}
    
    latest = df.iloc[-1]
    reasons = []
    components = {}
    
    # 1. 动量交易评分 (Momentum, 权重20%) - 正负双向
    momentum_score = 0
    momentum_notes = []
    momentum_pct = latest.get('Momentum_Pct', np.nan)
    if pd.notna(momentum_pct):
        if momentum_pct > 5:
            momentum_score = 100
            momentum_notes.append(f"Strong positive momentum: +{momentum_pct:.2f}% (>5%)")
        elif momentum_pct > 3:
            momentum_score = 67
            momentum_notes.append(f"Moderate positive momentum: +{momentum_pct:.2f}% (>3%)")
        elif momentum_pct > 0:
            momentum_score = 50
            momentum_notes.append(f"Positive momentum: +{momentum_pct:.2f}%")
        elif momentum_pct < -5:
            momentum_score = -100
            momentum_notes.append(f"Strong negative momentum: {momentum_pct:.2f}% (<-5%)")
        elif momentum_pct < -3:
            momentum_score = -67
            momentum_notes.append(f"Moderate negative momentum: {momentum_pct:.2f}% (<-3%)")
        elif momentum_pct < 0:
            momentum_score = -50
            momentum_notes.append(f"Negative momentum: {momentum_pct:.2f}%")
    if momentum_notes and momentum_score != 0:
        reasons.extend(format_reason(momentum_score, note) for note in momentum_notes)
    store_component(components, 'momentum', momentum_score, momentum_notes)
    
    # 2. RSI评分 (权重20%) - 正负双向
    rsi_score = 0
    rsi_notes = []
    rsi = latest.get('RSI', np.nan)
    if pd.notna(rsi):
        if rsi < 30:
            rsi_score = 100
            rsi_notes.append(f"RSI oversold ({rsi:.1f} < 30)")
        elif rsi < 40:
            rsi_score = 67
            rsi_notes.append(f"RSI near oversold ({rsi:.1f})")
        elif rsi > 70:
            rsi_score = -100
            rsi_notes.append(f"RSI overbought ({rsi:.1f} > 70)")
        elif rsi > 60:
            rsi_score = -67
            rsi_notes.append(f"RSI near overbought ({rsi:.1f})")
    if rsi_notes and rsi_score != 0:
        reasons.extend(format_reason(rsi_score, note) for note in rsi_notes)
    store_component(components, 'rsi', rsi_score, rsi_notes)
    
    # 3. CMF评分 (权重15%) - 正负双向
    cmf_score = 0
    cmf_notes = []
    cmf = latest.get('CMF', np.nan)
    if pd.notna(cmf):
        cmf_cross_up = False
        cmf_cross_down = False
        for i in range(max(1, len(df) - 3), len(df)):
            if i > 0:
                prev_cmf = df.iloc[i-1]['CMF']
                curr_cmf = df.iloc[i]['CMF']
                if pd.notna(prev_cmf) and pd.notna(curr_cmf):
                    if prev_cmf < 0 <= curr_cmf:
                        cmf_cross_up = True
                    elif prev_cmf > 0 >= curr_cmf:
                        cmf_cross_down = True
        recent_cmf = df['CMF'].tail(3).dropna().values
        cmf_strong_positive = len(recent_cmf) >= 2 and (recent_cmf > 0.2).sum() >= 2
        cmf_strong_negative = len(recent_cmf) >= 2 and (recent_cmf < -0.2).sum() >= 2
        
        if cmf_cross_up and cmf_strong_positive:
            cmf_score = 100
            cmf_notes.append("CMF crossed above zero and held > 0.2 (funds flowing in)")
        elif cmf > 0.2:
            cmf_score = 67
            cmf_notes.append(f"CMF strong positive ({cmf:.3f})")
        elif cmf > 0:
            cmf_score = 50
            cmf_notes.append(f"CMF positive ({cmf:.3f})")
        elif cmf_cross_down and cmf_strong_negative:
            cmf_score = -100
            cmf_notes.append("CMF crossed below zero and held < -0.2 (funds flowing out)")
        elif cmf < -0.2:
            cmf_score = -67
            cmf_notes.append(f"CMF strong negative ({cmf:.3f})")
        elif cmf < 0:
            cmf_score = -50
            cmf_notes.append(f"CMF negative ({cmf:.3f})")
    if cmf_notes and cmf_score != 0:
        reasons.extend(format_reason(cmf_score, note) for note in cmf_notes)
    store_component(components, 'cmf', cmf_score, cmf_notes)
    
    # 4. MFM趋势评分 (权重5%) - 正负双向
    mfm_score = 0
    mfm_notes = []
    if len(df) >= 3:
        recent_mfm = df['MF_Multiplier'].tail(3).dropna().values
        if len(recent_mfm) >= 2:
            if (recent_mfm > 0.5).sum() >= 2:
                mfm_score = 100
                mfm_notes.append("MFM > 0.5 for 2+ days (strong inflow)")
            elif (recent_mfm > 0).sum() >= 2:
                mfm_score = 67
                mfm_notes.append("MFM > 0 for 2+ days (positive inflow)")
            elif (recent_mfm < -0.5).sum() >= 2:
                mfm_score = -100
                mfm_notes.append("MFM < -0.5 for 2+ days (strong outflow)")
            elif (recent_mfm < 0).sum() >= 2:
                mfm_score = -67
                mfm_notes.append("MFM < 0 for 2+ days (negative inflow)")
    if mfm_notes and mfm_score != 0:
        reasons.extend(format_reason(mfm_score, note) for note in mfm_notes)
    store_component(components, 'mfm', mfm_score, mfm_notes)
    
    # 5. OBV评分 (权重15%) - 正负双向
    obv_score = 0
    obv_notes = []
    if len(df) >= 3:
        obv = latest.get('OBV', np.nan)
        obv_ma5 = latest.get('OBV_MA5', np.nan)
        if pd.notna(obv) and pd.notna(obv_ma5):
            obv_rising = obv > df.iloc[-3]['OBV']
            obv_falling = obv < df.iloc[-3]['OBV']
            obv_above_ma = obv > obv_ma5
            obv_below_ma = obv < obv_ma5
            if obv_rising and obv_above_ma:
                obv_score = 100
                obv_notes.append("OBV rising and above MA5")
            elif obv_rising:
                obv_score = 67
                obv_notes.append("OBV rising trend")
            elif obv_falling and obv_below_ma:
                obv_score = -100
                obv_notes.append("OBV falling and below MA5")
            elif obv_falling:
                obv_score = -67
                obv_notes.append("OBV falling trend")
    if obv_notes and obv_score != 0:
        reasons.extend(format_reason(obv_score, note) for note in obv_notes)
    store_component(components, 'obv', obv_score, obv_notes)
    
    # 6. 双均线评分 (权重10%) - 正负双向（使用MA5/MA20）
    ma_score = 0
    ma_notes = []
    ma_short = latest.get('MA5', np.nan)
    ma_long = latest.get('MA20', np.nan)
    if pd.notna(ma_short) and pd.notna(ma_long):
        ma_golden_cross = False
        ma_death_cross = False
        for i in range(max(1, len(df) - 3), len(df)):
            if i > 0:
                prev_short = df.iloc[i-1]['MA5']
                prev_long = df.iloc[i-1]['MA20']
                curr_short = df.iloc[i]['MA5']
                curr_long = df.iloc[i]['MA20']
                if pd.notna(prev_short) and pd.notna(prev_long) and pd.notna(curr_short) and pd.notna(curr_long):
                    if prev_short <= prev_long and curr_short > curr_long:
                        ma_golden_cross = True
                    elif prev_short >= prev_long and curr_short < curr_long:
                        ma_death_cross = True
        if ma_golden_cross:
            ma_score = 100
            ma_notes.append("MA5 crossed above MA20 (golden cross)")
        elif ma_short > ma_long:
            ma_score = 67
            ma_notes.append("MA5 above MA20 (trend confirmed)")
        elif ma_death_cross:
            ma_score = -100
            ma_notes.append("MA5 crossed below MA20 (death cross)")
        elif ma_short < ma_long:
            ma_score = -67
            ma_notes.append("MA5 below MA20 (downtrend)")
    if ma_notes and ma_score != 0:
        reasons.extend(format_reason(ma_score, note) for note in ma_notes)
    store_component(components, 'dual_ma', ma_score, ma_notes)
    
    # 7. 背离分析评分 (权重10%) - 正负双向
    div_score = 0
    div_notes = []
    bullish_best = 0
    bullish_reason = None
    bearish_best = 0
    bearish_reason = None
    for indicator in ['RSI', 'CMF', 'OBV']:
        score, reason = detect_bullish_divergence(df, indicator)
        if score > bullish_best:
            bullish_best = score
            bullish_reason = reason
    for indicator in ['RSI', 'CMF', 'OBV']:
        score, reason = detect_bearish_divergence(df, indicator)
        if score > bearish_best:
            bearish_best = score
            bearish_reason = reason
    if bullish_best >= bearish_best and bullish_best > 0 and bullish_reason:
        div_score = bullish_best
        div_notes.append(bullish_reason)
    elif bearish_best > bullish_best and bearish_best > 0 and bearish_reason:
        div_score = -bearish_best
        div_notes.append(bearish_reason)
    if div_notes and div_score != 0:
        reasons.extend(format_reason(div_score, note) for note in div_notes)
    store_component(components, 'divergence', div_score, div_notes)
    
    # 8. 网格交易评分 (权重5%) - 正负双向
    grid_score = 0
    grid_notes = []
    support = latest.get('Support', np.nan)
    resistance = latest.get('Resistance', np.nan)
    close = latest.get('Close', np.nan)
    if pd.notna(support) and pd.notna(close) and support > 0:
        distance_to_support = ((close - support) / support) * 100
        if distance_to_support <= 1.5 and ma_short > ma_long:
            grid_score = 100
            grid_notes.append(f"Price within {distance_to_support:.1f}% of support (trend confirmed)")
        elif distance_to_support <= 2:
            grid_score = 50
            grid_notes.append(f"Price near support ({distance_to_support:.1f}% away)")
    if pd.notna(resistance) and pd.notna(close) and resistance > 0:
        distance_to_resistance = ((resistance - close) / close) * 100
        if distance_to_resistance <= 1.5 and ma_short < ma_long:
            grid_score = -100
            grid_notes.append(f"Price within {distance_to_resistance:.1f}% of resistance (trend confirmed)")
        elif distance_to_resistance <= 2:
            grid_score = -50
            grid_notes.append(f"Price near resistance ({distance_to_resistance:.1f}% away)")
    if grid_notes and grid_score != 0:
        reasons.extend(format_reason(grid_score, note) for note in grid_notes)
    store_component(components, 'grid', grid_score, grid_notes)
    
    # 计算总分 (-100到+100分)
    total_score = float(round(sum(component['weighted'] for component in components.values()), 2))
    
    return total_score, reasons, components


# 旧的calculate_sell_signal函数已被删除
# 现在使用统一的calculate_unified_signal函数来计算-100到+100的评分


def load_stock_list(conn):
    """从CSI300数据库加载股票列表"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, ticker, COALESCE(name, ticker) AS name
                FROM csi300_company
                WHERE ticker IS NOT NULL AND ticker <> ''
                ORDER BY ticker
            """)
            rows = cur.fetchall()

        stock_list = [
            {
                'company_id': row[0],
                'symbol': row[1],
                'name': row[2],
            }
            for row in rows
        ]

        print(f"✅ Loaded {len(stock_list)} companies from csi300_company table")
        return stock_list

    except Exception as e:
        print(f"❌ Error loading CSI300 companies: {e}")
        return []


def create_calculation_log(conn, calculation_date):
    """创建计算日志记录"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO score_calculation_logs 
                (calculation_date, start_time, status)
                VALUES (%s, %s, %s)
                ON CONFLICT (calculation_date) 
                DO UPDATE SET 
                    start_time = EXCLUDED.start_time,
                    status = 'running'
                RETURNING id
            """, (calculation_date, datetime.now(), 'running'))
            log_id = cur.fetchone()[0]
            conn.commit()
            return log_id
    except Exception as e:
        print(f"⚠️ Warning: Could not create calculation log: {e}")
        conn.rollback()
        return None


def update_calculation_log(conn, calculation_date, status, total, successful, failed, error_msg=None):
    """更新计算日志"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE score_calculation_logs
                SET end_time = %s,
                    status = %s,
                    total_stocks = %s,
                    successful_stocks = %s,
                    failed_stocks = %s,
                    error_message = %s
                WHERE calculation_date = %s
            """, (datetime.now(), status, total, successful, failed, error_msg, calculation_date))
            conn.commit()
    except Exception as e:
        print(f"⚠️ Warning: Could not update calculation log: {e}")
        conn.rollback()


def save_scores_to_db(conn, calculation_date, scores_data):
    """
    批量保存评分到数据库
    
    Args:
        conn: 数据库连接
        calculation_date: 计算日期
        scores_data: 评分数据列表
    """
    if not scores_data:
        return 0
    
    try:
        # 准备批量插入数据
        values = []
        for data in scores_data:
            values.append((
                calculation_date,
                data['symbol'],
                data['name'],
                0,  # legacy buy_score retired
                Json([]),
                0,  # legacy sell_score retired
                Json([]),
                data.get('total_score'),
                data['last_close'],
                data['last_date'],
                data.get('cmf_value'),
                data.get('obv_value'),
                data.get('ma5'),
                data.get('ma10'),
                data.get('recommended_action', ''),
                data.get('recommended_action_detail', ''),
                Json(data.get('score_components', {})),
                data.get('signal_date'),
                data.get('execution_date'),
                data.get('suggested_position_pct'),
                data.get('stop_loss_price'),
                data.get('take_profit_price'),
            ))
        
        with conn.cursor() as cur:
            # 使用ON CONFLICT处理重复数据
            insert_sql = """
                INSERT INTO stock_scores 
                (calculation_date, ticker, company_name, buy_score, buy_reasons, 
                 sell_score, sell_reasons, total_score, last_close, last_trading_date,
                 cmf_value, obv_value, ma5, ma10, recommended_action, recommended_action_detail,
                 score_components, signal_date, execution_date, suggested_position_pct, stop_loss_price, take_profit_price,
                 created_at, updated_at)
                VALUES %s
                ON CONFLICT (calculation_date, ticker) 
                DO UPDATE SET
                    company_name = EXCLUDED.company_name,
                    buy_score = EXCLUDED.buy_score,
                    buy_reasons = EXCLUDED.buy_reasons,
                    sell_score = EXCLUDED.sell_score,
                    sell_reasons = EXCLUDED.sell_reasons,
                    total_score = EXCLUDED.total_score,
                    last_close = EXCLUDED.last_close,
                    last_trading_date = EXCLUDED.last_trading_date,
                    cmf_value = EXCLUDED.cmf_value,
                    obv_value = EXCLUDED.obv_value,
                    ma5 = EXCLUDED.ma5,
                    ma10 = EXCLUDED.ma10,
                    recommended_action = EXCLUDED.recommended_action,
                    recommended_action_detail = EXCLUDED.recommended_action_detail,
                    score_components = EXCLUDED.score_components,
                    signal_date = EXCLUDED.signal_date,
                    execution_date = EXCLUDED.execution_date,
                    suggested_position_pct = EXCLUDED.suggested_position_pct,
                    stop_loss_price = EXCLUDED.stop_loss_price,
                    take_profit_price = EXCLUDED.take_profit_price,
                    updated_at = CURRENT_TIMESTAMP
            """
            template = "(" + ", ".join(["%s"] * 22 + ["CURRENT_TIMESTAMP", "CURRENT_TIMESTAMP"]) + ")"
            execute_values(cur, insert_sql, values, template=template)
            
            conn.commit()
            return len(values)
            
    except Exception as e:
        print(f"❌ Error saving to database: {e}")
        traceback.print_exc()
        conn.rollback()
        raise


def calculate_all_scores():
    """
    计算所有股票的评分并存储到数据库
    注意：使用前一天及之前的数据，不包含当天数据
    """
    print("=" * 80)
    print(f"🚀 Starting Daily Score Calculation")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 Environment: {ENVIRONMENT}")
    print(f"⚠️  Using data up to YESTERDAY (excluding today)")
    print("=" * 80)
    
    # 连接数据库
    try:
        conn = get_db_connection()
        print(f"✅ Database connected: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return
    
    # 加载股票列表
    stock_list = load_stock_list(conn)
    if not stock_list:
        print("❌ No stocks to process")
        conn.close()
        return
    
    calculation_date = date.today()
    
    # 创建计算日志
    log_id = create_calculation_log(conn, calculation_date)
    
    # 计算评分
    total_stocks = len(stock_list)
    successful = 0
    failed = 0
    scores_data = []
    
    print(f"\n📊 Processing {total_stocks} stocks...")
    print("-" * 80)
    
    for idx, stock in enumerate(stock_list, 1):
        symbol = stock['symbol']
        name = stock['name']
        
        try:
            # 获取历史数据（90天）
            ticker = yf.Ticker(symbol)
            df = ticker.history(period='90d', interval='1d')
            df = df[df['Volume'] > 0].copy()
            
            # 关键：排除今天的数据，只使用昨天及之前的数据
            from datetime import date as date_type
            today = date_type.today()
            df = df[df.index.date < today]  # 只保留今天之前的数据
            
            df = df.tail(60).copy()
            
            if len(df) < 20:
                print(f"  [{idx}/{total_stocks}] ⚠️  {symbol:15s} - Insufficient data ({len(df)} days)")
                failed += 1
                continue
            
            # 计算指标
            df = calculate_indicators(df)
            
            # 步骤1：成交量放大过滤（初步筛选）
            volume_passed, volume_reason = check_volume_expansion(df)
            
            # 计算统一评分（新量化策略：-100到+100）
            total_score, signal_reasons, components = calculate_unified_signal(df)
            
            latest = df.iloc[-1]
            
            # 收集数据
            last_close = float(latest['Close'])
            signal_date = latest.name.date() if hasattr(latest.name, 'date') else None
            execution_date = None
            if NEXT_DAY_EXECUTION and signal_date:
                try:
                    execution_date = (latest.name + BDay(1)).date()
                except Exception:
                    execution_date = None
            stop_loss_price = round(last_close * (1 - STOP_LOSS_PCT), 4)
            take_profit_price = round(last_close * (1 + TAKE_PROFIT_PCT), 4)

            record = {
                'company_id': stock.get('company_id'),
                'symbol': symbol,
                'name': name,
                'total_score': total_score,
                'signal_reasons': signal_reasons,
                'last_close': last_close,
                'last_date': latest.name.date() if hasattr(latest.name, 'date') else None,
                'cmf_value': float(latest['CMF']) if pd.notna(latest['CMF']) else None,
                'obv_value': int(latest['OBV']) if pd.notna(latest['OBV']) else None,
                'ma5': float(latest['MA5']) if pd.notna(latest['MA5']) else None,
                'ma10': float(latest['MA10']) if pd.notna(latest['MA10']) else None,
                'ma20': float(latest['MA20']) if pd.notna(latest['MA20']) else None,
                'rsi': float(latest['RSI']) if pd.notna(latest['RSI']) else None,
                'momentum_pct': float(latest['Momentum_Pct']) if pd.notna(latest['Momentum_Pct']) else None,
                'volume_filter_passed': volume_passed,
                'suggested_position_pct': SUGGESTED_POSITION_PCT,
                'stop_loss_price': stop_loss_price,
                'take_profit_price': take_profit_price,
                'signal_date': signal_date,
                'execution_date': execution_date,
                'score_components': {
                    key: {
                        'raw': float(value['raw']) if value and value['raw'] is not None else 0.0,
                        'weight': float(value['weight']) if value and value['weight'] is not None else 0.0,
                        'weighted': float(value['weighted']) if value and value['weighted'] is not None else 0.0,
                        'reasons': value.get('reasons', []) if value else []
                    }
                    for key, value in components.items()
                }
            }

            record['recommended_action'] = determine_recommended_action(total_score, volume_passed)
            
            # 增强推荐详情：包含成交量过滤和组件评分
            detail_lines = [volume_reason]
            if not volume_passed:
                detail_lines.append("⚠️ Volume filter not passed - signals may be less reliable")
            detail_lines.append("")
            detail_lines.append(build_recommendation_detail(record, calculation_date))
            
            record['recommended_action_detail'] = "\n".join(detail_lines)

            scores_data.append(record)
            
            successful += 1
            
            # 显示进度（新阈值±70分）
            signal_flag = ""
            vol_flag = "✓" if volume_passed else "✗"
            if total_score >= BUY_THRESHOLD:
                signal_flag = "🟢 BUY"
            elif total_score <= SELL_THRESHOLD:
                signal_flag = "🔴 SELL"
            
            print(f"  [{idx}/{total_stocks}] ✅ {symbol:15s} | Score: {total_score:+6.1f} | Vol:{vol_flag} | Action: {record['recommended_action']:4s} {signal_flag}")
            
            # 每50只股票批量保存一次
            if len(scores_data) >= 50:
                saved_scores = save_scores_to_db(conn, calculation_date, scores_data)
                print(f"    💾 Saved {saved_scores} scores to database")
                scores_data = []
            
        except Exception as e:
            print(f"  [{idx}/{total_stocks}] ❌ {symbol:15s} - Error: {str(e)[:50]}")
            failed += 1
            continue
    
    # 保存剩余数据
    if scores_data:
        saved_scores = save_scores_to_db(conn, calculation_date, scores_data)
        print(f"    💾 Saved {saved_scores} scores to database")
    
    # 更新计算日志
    status = 'completed' if failed == 0 else 'completed'
    update_calculation_log(conn, calculation_date, status, total_stocks, successful, failed)
    
    # 关闭连接
    conn.close()
    
    # 输出统计
    print("-" * 80)
    print(f"\n✅ Calculation Completed!")
    print(f"   Total: {total_stocks} | Success: {successful} | Failed: {failed}")
    print(f"   Success Rate: {(successful/total_stocks*100):.1f}%")
    print(f"   Calculation Date: {calculation_date}")
    print(f"   Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == '__main__':
    calculate_all_scores()
