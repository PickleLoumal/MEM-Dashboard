#!/usr/bin/env python3
"""
验证Exchange Rate汇率指标的FRED数据可用性
基于trade_deficits测试模板，专注于汇率、利率、贸易平衡等金融市场指标
"""

import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import json
import statistics
from datetime import datetime, timedelta

# FRED API配置
FRED_API_KEY = "1cdac6b8c1173f83a10444d17e73b32e"  # 从实际环境获取
BASE_URL = "https://api.stlouisfed.org/fred"

def test_fred_indicator(series_id, description):
    """测试单个FRED指标的可用性"""
    print(f"\n=== 测试指标: {series_id} ({description}) ===")
    
    # 获取系列信息
    series_url = f"{BASE_URL}/series"
    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json'
    }
    
    try:
        # 构建URL
        query_string = urllib.parse.urlencode(params)
        full_url = f"{series_url}?{query_string}"
        
        with urllib.request.urlopen(full_url) as response:
            series_data = json.loads(response.read().decode())
        
        if 'seriess' in series_data and len(series_data['seriess']) > 0:
            series_info = series_data['seriess'][0]
            print(f"✅ 系列ID: {series_info['id']}")
            print(f"   标题: {series_info['title']}")
            print(f"   单位: {series_info['units']}")
            print(f"   频率: {series_info['frequency']}")
            print(f"   开始日期: {series_info['observation_start']}")
            print(f"   结束日期: {series_info['observation_end']}")
            print(f"   最后更新: {series_info['last_updated']}")
            
            # 获取最新数据
            obs_url = f"{BASE_URL}/series/observations"
            obs_params = {
                'series_id': series_id,
                'api_key': FRED_API_KEY,
                'file_type': 'json',
                'limit': 5,
                'sort_order': 'desc'
            }
            
            obs_query_string = urllib.parse.urlencode(obs_params)
            obs_full_url = f"{obs_url}?{obs_query_string}"
            
            with urllib.request.urlopen(obs_full_url) as obs_response:
                obs_data = json.loads(obs_response.read().decode())
            
            if 'observations' in obs_data and len(obs_data['observations']) > 0:
                latest_obs = obs_data['observations'][0]
                print(f"   最新值: {latest_obs['value']} ({latest_obs['date']})")
                return True
            else:
                print(f"⚠️  无观测数据")
                return False
                
        else:
            print(f"❌ 系列不存在")
            return False
            
    except urllib.error.URLError as e:
        print(f"❌ 请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        return False

def validate_series_data(series_id, expected_range=None, data_type='numeric'):
    """验证系列数据质量"""
    print(f"\n🔍 验证数据质量: {series_id}")
    
    try:
        # 获取系列观测数据
        obs_url = f"{BASE_URL}/series/observations"
        params = {
            'series_id': series_id,
            'api_key': FRED_API_KEY,
            'file_type': 'json',
            'limit': 100,
            'sort_order': 'desc'
        }
        
        query_string = urllib.parse.urlencode(params)
        full_url = f"{obs_url}?{query_string}"
        
        with urllib.request.urlopen(full_url) as response:
            obs_data = json.loads(response.read().decode())
        
        if 'observations' not in obs_data or len(obs_data['observations']) == 0:
            print(f"❌ 无观测数据")
            return False
            
        observations = obs_data['observations']
        print(f"📊 获取到 {len(observations)} 条观测数据")
        
        # 数据质量检查
        valid_values = []
        null_count = 0
        
        for obs in observations:
            if obs['value'] == '.' or obs['value'] == '' or obs['value'] is None:
                null_count += 1
            else:
                try:
                    value = float(obs['value'])
                    valid_values.append(value)
                except ValueError:
                    print(f"⚠️  无效数值: {obs['value']} 在日期 {obs['date']}")
        
        if not valid_values:
            print(f"❌ 没有有效数值")
            return False
            
        # 统计分析
        print(f"📊 数据质量分析:")
        print(f"   - 有效数值: {len(valid_values)}")
        print(f"   - 空值数量: {null_count}")
        print(f"   - 空值比例: {null_count/len(observations)*100:.1f}%")
        print(f"   - 数值范围: {min(valid_values):.2f} 到 {max(valid_values):.2f}")
        print(f"   - 平均值: {statistics.mean(valid_values):.2f}")
        if len(valid_values) > 1:
            print(f"   - 标准差: {statistics.stdev(valid_values):.2f}")
        
        # 范围验证
        if expected_range:
            min_val, max_val = expected_range
            out_of_range = [v for v in valid_values if v < min_val or v > max_val]
            if out_of_range:
                print(f"⚠️  {len(out_of_range)} 个值超出预期范围 [{min_val}, {max_val}]")
            else:
                print(f"✅ 所有值在预期范围内")
        
        # 时间序列连续性检查
        dates = [datetime.strptime(obs['date'], '%Y-%m-%d') for obs in observations]
        dates.sort()
        
        gaps = []
        for i in range(1, len(dates)):
            gap = (dates[i] - dates[i-1]).days
            if gap > 90:  # 超过90天的间隔视为异常
                gaps.append(gap)
        
        if gaps:
            print(f"⚠️  发现 {len(gaps)} 个大数据间隔，最大间隔: {max(gaps)} 天")
        else:
            print(f"✅ 时间序列连续性良好")
            
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def main():
    print("=== Exchange Rate 汇率和金融指标验证 ===")
    print("基于用户需求的8个核心汇率和金融市场指标")
    
    # 用户指定的8个Exchange Rate核心指标
    indicators = [
        # Real Effective Exchange Rate (REER)
        ('RBUSBIS', 'Real Effective Exchange Rate (REER) - 实际有效汇率'),
        
        # Federal Funds Rate (Effective)
        ('FEDFUNDS', 'Federal Funds Rate (Effective) - 联邦基金利率'),
        
        # U.S. Trade Balance
        ('BOPGSTB', 'U.S. Trade Balance - 美国贸易平衡'),
        
        # China/US Exchange Rate
        ('DEXCHUS', 'China/US Exchange Rate - 人民币/美元汇率'),
        
        # 10-Year Treasury Yield
        ('GS10', '10-Year Treasury Yield - 10年期国债收益率'),
        
        # USD/EUR Exchange Rate
        ('DEXUSEU', 'USD/EUR Exchange Rate - 美元/欧元汇率'),
        
        # Trade-Weighted U.S. Dollar Index (Broad)
        ('DTWEXBGS', 'Trade-Weighted U.S. Dollar Index (Broad) - 贸易加权美元指数'),
        
        # VIX作为金融市场波动性指标替代JPMorgan Global FX Volatility Index
        ('VIXCLS', 'CBOE Volatility Index (VIX) - 波动率指数'),
        
        # Japan/US Exchange Rate
        ('DEXJPUS', 'Japan/US Exchange Rate - 日元/美元汇率')
    ]
    
    valid_indicators = []
    
    print("\n" + "="*80)
    print("验证用户指定的Exchange Rate指标")
    print("="*80)
    
    for series_id, description in indicators:
        if test_fred_indicator(series_id, description):
            valid_indicators.append((series_id, description))
            # 根据指标类型设置验证范围
            if series_id in ['FEDFUNDS', 'GS10']:
                validate_series_data(series_id, expected_range=(0, 20))  # 利率指标
            elif series_id in ['DEXUSEU']:
                validate_series_data(series_id, expected_range=(0.5, 2.0))  # 汇率指标
            elif series_id in ['DTWEXBGS']:
                validate_series_data(series_id, expected_range=(80, 140))  # 美元指数
            elif series_id in ['VIXCLS']:
                validate_series_data(series_id, expected_range=(5, 100))  # 波动率指数
            elif series_id in ['RBUSBIS']:
                validate_series_data(series_id, expected_range=(50, 200))  # 实际有效汇率
            elif series_id in ['DEXCHUS']:
                validate_series_data(series_id, expected_range=(1.0, 10.0))  # 人民币/美元汇率
            elif series_id in ['DEXJPUS']:
                validate_series_data(series_id, expected_range=(80, 200))  # 日元/美元汇率
            else:
                validate_series_data(series_id)  # 其他指标不设范围限制
    
    print("\n" + "="*80)
    print("验证结果汇总")
    print("="*80)
    print(f"有效指标数量: {len(valid_indicators)}")
    
    if len(valid_indicators) >= 8:
        print("✅ 满足8个Exchange Rate指标要求")
        print("\n金融市场专家视角的指标分类:")
        
        print("📈 汇率指标:")
        exchange_rate_indicators = [
            ('RBUSBIS', 'Real Effective Exchange Rate (REER) - 实际有效汇率'),
            ('DEXUSEU', 'USD/EUR Exchange Rate - 美元/欧元汇率'),
            ('DTWEXBGS', 'Trade-Weighted U.S. Dollar Index (Broad) - 贸易加权美元指数')
        ]
        for i, (series_id, description) in enumerate(exchange_rate_indicators, 1):
            if (series_id, description) in valid_indicators:
                print(f"  {i}. {series_id}: {description}")
        
        print("📊 利率指标:")
        interest_rate_indicators = [
            ('FEDFUNDS', 'Federal Funds Rate (Effective) - 联邦基金利率'),
            ('GS10', '10-Year Treasury Yield - 10年期国债收益率')
        ]
        for i, (series_id, description) in enumerate(interest_rate_indicators, 4):
            if (series_id, description) in valid_indicators:
                print(f"  {i}. {series_id}: {description}")
                
        print("🌍 国际收支指标:")
        balance_indicators = [
            ('BOPGSTB', 'U.S. Trade Balance - 美国贸易平衡'),
            ('TICASSETS', 'Treasury International Capital (TIC) Net Flows - 国际资本流动')
        ]
        for i, (series_id, description) in enumerate(balance_indicators, 6):
            if (series_id, description) in valid_indicators:
                print(f"  {i}. {series_id}: {description}")
            
        print("📉 市场风险指标:")
        risk_indicators = [
            ('VIXCLS', 'CBOE Volatility Index (VIX) - 波动率指数')
        ]
        for i, (series_id, description) in enumerate(risk_indicators, 8):
            if (series_id, description) in valid_indicators:
                print(f"  {i}. {series_id}: {description}")
                
    else:
        print(f"⚠️  仅有{len(valid_indicators)}个有效指标，需要补充")
        print("\n建议补充的相关指标:")
        alternative_indicators = [
            ('DEXCHUS', 'China / U.S. Foreign Exchange Rate - 人民币/美元汇率'),
            ('DEXJPUS', 'Japan / U.S. Foreign Exchange Rate - 日元/美元汇率'),
            ('DEXCAUS', 'Canada / U.S. Foreign Exchange Rate - 加元/美元汇率'),
            ('DEXMXUS', 'Mexico / U.S. Foreign Exchange Rate - 比索/美元汇率'),
        ]
        
        for series_id, description in alternative_indicators:
            print(f"   - {series_id}: {description}")

    print(f"\n📋 金融分析解读:")
    print("• RBUSBIS: 实际有效汇率，衡量美元相对购买力，反映美国在国际贸易中的竞争力")
    print("• FEDFUNDS: 联邦基金利率，美联储货币政策的核心工具，影响全球资本流动")
    print("• BOPGSTB: 美国贸易平衡，反映商品和服务贸易差额，影响汇率走势")
    print("• DEXCHUS: 人民币/美元汇率，中美两大经济体之间的汇率，影响全球贸易")
    print("• DEXJPUS: 日元/美元汇率，亚洲主要货币对，影响亚洲地区贸易和资本流动")
    print("• GS10: 10年期国债收益率，长期利率基准，影响汇率和资本流动")
    print("• DEXUSEU: 美元/欧元汇率，全球最重要的货币对之一")
    print("• DTWEXBGS: 贸易加权美元指数，衡量美元相对于主要贸易伙伴货币的强度")
    print("• VIXCLS: 波动率指数，市场恐慌情绪指标，影响风险资产和避险货币")

if __name__ == "__main__":
    main()
