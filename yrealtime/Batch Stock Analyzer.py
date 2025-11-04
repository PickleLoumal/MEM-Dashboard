import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_pdf import PdfPages
import lseg.data as ld
import datetime
import os
import numpy as np

# 设置matplotlib中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
today_short = datetime.datetime.now().strftime("%m%d") 
class BatchStockAnalyzer:
    def __init__(self):
        self.session = None
        
    def connect_api(self):
        """连接LSEG API - 使用多种连接方法"""
        try:
            print("🔗 Connecting to LSEG API...")
            
            # 方法1: 默认连接
            try:
                ld.open_session()
                self.session = True
                print("✅ Connected to LSEG API successfully (Default)")
                return True
            except Exception as e1:
                print(f"❌ Default connection failed: {str(e1)[:100]}...")
            
            # 方法2: Desktop Workspace
            try:
                ld.open_session('desktop.workspace')
                self.session = True
                print("✅ Connected to LSEG API successfully (Desktop)")
                return True
            except Exception as e2:
                print(f"❌ Desktop connection failed: {str(e2)[:100]}...")
            
            # 方法3: Deployed session
            try:
                ld.open_session('platform.deployed')
                self.session = True
                print("✅ Connected to LSEG API successfully (Deployed)")
                return True
            except Exception as e3:
                print(f"❌ Deployed connection failed: {str(e3)[:100]}...")
            
            print("❌ All connection methods failed")
            return False
            
        except Exception as e:
            print(f"❌ API connection failed: {str(e)}")
            return False
    
    def get_company_name(self, symbol):
        """获取公司名称"""
        try:
            # 尝试获取公司信息
            df = ld.get_data(
                universe=[symbol],
                fields=['TR.CompanyName']
            )
            if not df.empty and 'Company Name' in df.columns:
                company_name = df['Company Name'].iloc[0]
                if pd.notna(company_name) and company_name.strip():
                    return company_name.strip()
        except:
            pass
        
        # 如果获取失败，返回股票代码
        return symbol
    
    def get_stock_data(self, symbol, days=30):
        """获取股票数据（收集60个交易日，使用最近30日，确保CMF有足够数据）"""
        try:
            print(f"📈 Fetching data for {symbol}...")
            
            # 收集60个交易日的数据，用于计算CMF（需要21天）和均线
            fetch_days = days + 30  # 多收集30天确保CMF计算充足
            
            # 计算日期范围 - 排除当天，获取更多天数以确保有足够的交易日
            end_date = datetime.date.today() - datetime.timedelta(days=1)  # 前一天
            start_date = end_date - datetime.timedelta(days=fetch_days*3)  # 多取一些天数以确保有足够的交易日
            
            # 获取历史数据
            df = ld.get_history(
                universe=[symbol],
                fields=['TR.PriceOpen', 'TR.PriceHigh', 'TR.PriceLow', 'TR.PriceClose', 'TR.Volume'],
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d')
            )
            
            if df.empty:
                print(f"❌ No data returned for {symbol}")
                return None
            
            # 检查列名并重命名
            column_mapping = {}
            for col in df.columns:
                if 'open' in col.lower():
                    column_mapping[col] = 'Open'
                elif 'high' in col.lower():
                    column_mapping[col] = 'High'
                elif 'low' in col.lower():
                    column_mapping[col] = 'Low'
                elif 'close' in col.lower():
                    column_mapping[col] = 'Close'
                elif 'volume' in col.lower():
                    column_mapping[col] = 'Volume'
            
            df = df.rename(columns=column_mapping)
            
            # 确保日期列
            if 'Date' not in df.columns:
                df.reset_index(inplace=True)
            
            # 检查必需的列是否存在
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"❌ Missing columns for {symbol}: {missing_columns}")
                print(f"Available columns: {df.columns.tolist()}")
                return None
            
            # 转换日期并排序
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date').reset_index(drop=True)
            
            # 过滤有效数据（只保留有交易数据的日期）
            df = df.dropna(subset=['Close', 'Volume'])
            df = df[df['Volume'] > 0]  # 确保有交易量的才是交易日
            
            # 获取60个交易日用于计算CMF和均线，然后只取最近30个用于显示
            df_full = df.tail(fetch_days).copy().reset_index(drop=True)
            
            # 确保数据类型正确
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                if col in df_full.columns:
                    df_full[col] = pd.to_numeric(df_full[col], errors='coerce')
            
            # 计算全部60天的移动平均线
            df_full['MA5'] = df_full['Close'].rolling(window=5).mean()
            df_full['MA10'] = df_full['Close'].rolling(window=10).mean()
            
            # 计算OBV（在全部60天数据上）
            df_full = self.calculate_obv_for_dataframe(df_full)
            
            # 计算OBV的移动平均线（基于60天的OBV数据）
            df_full['OBV_MA5'] = df_full['OBV'].rolling(window=5).mean()
            df_full['OBV_MA10'] = df_full['OBV'].rolling(window=10).mean()
            
            # 计算CMF指标（基于60天数据，使用21天周期）
            df_full = self.calculate_cmf_for_dataframe(df_full, period=21)
            
            # 只返回最近30天的数据（但包含完整的均线计算结果）
            df_display = df_full.tail(days).copy().reset_index(drop=True)
            
            # 打印日期范围信息
            if len(df_display) > 0:
                print(f"✅ Got {len(df_display)} trading days for display (from {len(df_full)} days collected)")
                print(f"   Date range: {df_display['Date'].iloc[0].strftime('%Y-%m-%d')} to {df_display['Date'].iloc[-1].strftime('%Y-%m-%d')}")
            else:
                print(f"❌ No valid trading data for {symbol}")
                return None
            
            return df_display
            
        except Exception as e:
            print(f"❌ Error fetching data for {symbol}: {str(e)}")
            return None
    
    def calculate_obv_for_dataframe(self, data):
        """为数据框计算OBV指标（不重新复制数据）"""
        try:
            if len(data) < 2:
                data['OBV'] = 0.0
                return data
            
            data['OBV'] = 0.0
            
            # 第一天OBV设为0
            data.loc[0, 'OBV'] = 0
            
            # 计算后续每天的OBV
            for i in range(1, len(data)):
                current_close = data.loc[i, 'Close']
                previous_close = data.loc[i-1, 'Close']
                current_volume = data.loc[i, 'Volume']
                previous_obv = data.loc[i-1, 'OBV']
                
                if pd.isna(current_close) or pd.isna(previous_close) or pd.isna(current_volume):
                    data.loc[i, 'OBV'] = previous_obv
                    continue
                
                if current_close > previous_close:
                    new_obv = previous_obv + current_volume
                elif current_close < previous_close:
                    new_obv = previous_obv - current_volume
                else:
                    new_obv = previous_obv
                
                data.loc[i, 'OBV'] = new_obv
            
            return data
            
        except Exception as e:
            print(f"❌ OBV calculation error: {str(e)}")
            data['OBV'] = 0.0
            return data
    
    def calculate_cmf_for_dataframe(self, data, period=21):
        """为数据框计算CMF指标（Chaikin Money Flow）"""
        try:
            # Step 1: Calculate Money Flow Multiplier
            data['MF_Multiplier'] = ((data['Close'] - data['Low']) - (data['High'] - data['Close'])) / (data['High'] - data['Low'])
            
            # 处理分母为0的情况（High = Low）
            data.loc[data['High'] == data['Low'], 'MF_Multiplier'] = 0
            
            # Step 2: Calculate Money Flow Volume
            data['MF_Volume'] = data['MF_Multiplier'] * data['Volume']
            
            # Step 3: Calculate CMF (21-period default)
            data['CMF'] = data['MF_Volume'].rolling(window=period).sum() / data['Volume'].rolling(window=period).sum()
            
            return data
            
        except Exception as e:
            print(f"❌ CMF calculation error: {str(e)}")
            data['CMF'] = 0.0
            return data
    
    def calculate_obv(self, data):
        """计算OBV指标（保持原有接口兼容性）"""
        try:
            if len(data) < 2:
                return data
            
            result_data = data.copy()
            result_data['OBV'] = 0.0
            
            # 第一天OBV设为0
            result_data.loc[0, 'OBV'] = 0
            
            # 计算后续每天的OBV
            for i in range(1, len(result_data)):
                current_close = result_data.loc[i, 'Close']
                previous_close = result_data.loc[i-1, 'Close']
                current_volume = result_data.loc[i, 'Volume']
                previous_obv = result_data.loc[i-1, 'OBV']
                
                if pd.isna(current_close) or pd.isna(previous_close) or pd.isna(current_volume):
                    result_data.loc[i, 'OBV'] = previous_obv
                    continue
                
                if current_close > previous_close:
                    new_obv = previous_obv + current_volume
                elif current_close < previous_close:
                    new_obv = previous_obv - current_volume
                else:
                    new_obv = previous_obv
                
                result_data.loc[i, 'OBV'] = new_obv
            
            return result_data
            
        except Exception as e:
            print(f"❌ OBV calculation error: {str(e)}")
            return data
    
    def create_stock_chart(self, data, symbol, company_name):
        """创建股票价格走势图 (K线图 + 价格折线 + 5日10日均线)"""
        try:
            fig, ax = plt.subplots(figsize=(14, 8))
            
            dates = data['Date']
            opens = data['Open']
            highs = data['High']
            lows = data['Low']
            closes = data['Close']
            
            # 使用预计算的移动平均线（如果存在）
            if 'MA5' in data.columns and 'MA10' in data.columns:
                ma5 = data['MA5']
                ma10 = data['MA10']
            else:
                # 后备方案：重新计算移动平均线
                ma5 = closes.rolling(window=5).mean()
                ma10 = closes.rolling(window=10).mean()
            
            # 创建交易日索引，让每个交易日等距显示
            trading_day_indices = list(range(len(dates)))
            
            # 设置x轴刻度，每隔几个交易日显示一次日期
            if len(dates) <= 10:
                step = 1  # 少于10天，每天都显示
            elif len(dates) <= 20:
                step = 2  # 10-20天，每隔1天显示
            else:
                step = 3  # 20天以上，每隔2天显示
            
            tick_positions = list(trading_day_indices[::step])
            tick_labels = [dates.iloc[i].strftime('%m-%d') for i in tick_positions]
            
            # 确保显示第一天和最后一天
            if tick_positions[0] != 0:
                tick_positions = [0] + tick_positions
                tick_labels = [dates.iloc[0].strftime('%m-%d')] + tick_labels
            if tick_positions[-1] != len(dates) - 1:
                tick_positions.append(len(dates) - 1)
                tick_labels.append(dates.iloc[-1].strftime('%m-%d'))
            
            # 绘制K线图 - 使用交易日索引，高透明度
            width = 0.6
            up_mask = closes >= opens
            
            for i in range(len(data)):
                trading_day_idx = i  # 交易日索引
                open_price = opens.iloc[i]
                high_price = highs.iloc[i]
                low_price = lows.iloc[i]
                close_price = closes.iloc[i]
                
                if up_mask.iloc[i]:  # 上涨
                    color = 'red'
                    edge_color = 'darkred'
                    alpha = 0.3  # 高透明度
                    body_bottom = open_price
                    body_height = close_price - open_price
                else:  # 下跌
                    color = 'green'
                    edge_color = 'darkgreen'
                    alpha = 0.3  # 高透明度
                    body_bottom = close_price
                    body_height = open_price - close_price
                
                # 影线 - 使用更深的颜色
                ax.plot([trading_day_idx, trading_day_idx], [low_price, high_price], 
                       color=edge_color, linewidth=1.2, alpha=alpha)
                
                # 实体 - 使用更强的对比
                rect = Rectangle((trading_day_idx - width/2, body_bottom), 
                               width, body_height, 
                               facecolor=color, edgecolor=edge_color, 
                               linewidth=0.8, alpha=alpha)
                ax.add_patch(rect)
            
            # 绘制价格折线图 - 使用交易日索引，粗蓝线
            ax.plot(trading_day_indices, closes, color='blue', linewidth=2.5, alpha=0.9, label='Close Price')
            
            # 绘制移动平均线 - 使用交易日索引，虚线/点线，保持原来的粗细
            if len(data) >= 5:
                ax.plot(trading_day_indices, ma5, color='orange', linewidth=2, alpha=0.8, 
                       linestyle='--', label='MA5')
            if len(data) >= 10:
                ax.plot(trading_day_indices, ma10, color='purple', linewidth=2, alpha=0.8, 
                       linestyle=':', label='MA10')
            
            # 标题和格式 - 全英文
            ax.set_title(f'{company_name} ({symbol}) - Stock Price Chart\n{dates.iloc[0].strftime("%Y-%m-%d")} to {dates.iloc[-1].strftime("%Y-%m-%d")}', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Trading Days', fontsize=12)
            ax.set_ylabel('Price', fontsize=12)
            
            # 设置x轴刻度和标签 - 使用交易日刻度
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels, rotation=45)
            ax.grid(True, alpha=0.3)
            
            # 设置x轴范围确保对齐
            ax.set_xlim(-0.5, len(dates) - 0.5)
            
            # 价格信息 - 全英文
            latest_price = closes.iloc[-1]
            price_change = closes.iloc[-1] - closes.iloc[-2] if len(closes) > 1 else 0
            price_change_pct = (price_change / closes.iloc[-2] * 100) if len(closes) > 1 and closes.iloc[-2] != 0 else 0
            
            latest_ma5 = ma5.iloc[-1] if len(ma5) >= 5 and pd.notna(ma5.iloc[-1]) else 0
            latest_ma10 = ma10.iloc[-1] if len(ma10) >= 10 and pd.notna(ma10.iloc[-1]) else 0
            
            info_text = f'Latest Price: {latest_price:.2f}\nChange: {price_change:+.2f} ({price_change_pct:+.2f}%)\n'
            info_text += f'High: {highs.max():.2f} | Low: {lows.min():.2f}\n'
            if latest_ma5 > 0:
                info_text += f'MA5: {latest_ma5:.2f}\n'
            if latest_ma10 > 0:
                info_text += f'MA10: {latest_ma10:.2f}'
            
            # 调整子图位置，为图例留出空间
            plt.subplots_adjust(bottom=0.2)
            
            # 添加图例 - 移到图外下方
            ax.legend(bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=3)
            
            # 信息框 - 移回图内左上角，调低字体和背景透明度
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
                   verticalalignment='top', alpha=0.7,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.2))
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            print(f"❌ Stock chart creation error: {str(e)}")
            return None
    
    def create_obv_chart(self, data, symbol, company_name):
        """创建OBV指标图 (OBV + OBV的5日10日均线)"""
        try:
            fig, ax = plt.subplots(figsize=(14, 8))
            
            dates = data['Date']
            obvs = data['OBV']
            
            # 使用预计算的OBV移动平均线（如果存在）
            if 'OBV_MA5' in data.columns and 'OBV_MA10' in data.columns:
                obv_ma5 = data['OBV_MA5']
                obv_ma10 = data['OBV_MA10']
            else:
                # 后备方案：重新计算OBV移动平均线
                obv_ma5 = obvs.rolling(window=5).mean()
                obv_ma10 = obvs.rolling(window=10).mean()
            
            # 创建交易日索引，与股价图保持一致
            trading_day_indices = list(range(len(dates)))
            
            # 绘制OBV主线 - 使用交易日索引，粗线，不同颜色
            ax.plot(trading_day_indices, obvs, color='red', linewidth=2.5, label='OBV', alpha=0.9)
            
            # 绘制OBV移动平均线 - 使用交易日索引，虚线/点线，不同颜色
            if len(data) >= 5:
                ax.plot(trading_day_indices, obv_ma5, color='darkblue', linewidth=2, alpha=0.8, 
                       linestyle='--', label='OBV MA5')
            if len(data) >= 10:
                ax.plot(trading_day_indices, obv_ma10, color='green', linewidth=2, alpha=0.8, 
                       linestyle=':', label='OBV MA10')
            
            # 标题和格式 - 全英文
            ax.set_title(f'{company_name} ({symbol}) - OBV Indicator Chart\n{dates.iloc[0].strftime("%Y-%m-%d")} to {dates.iloc[-1].strftime("%Y-%m-%d")}', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Trading Days', fontsize=12)
            ax.set_ylabel('OBV', fontsize=12)
            
            # 格式化x轴 - 与股价图保持一致的交易日显示
            if len(dates) <= 10:
                step = 1
            elif len(dates) <= 20:
                step = 2
            else:
                step = 3
            
            tick_positions = list(trading_day_indices[::step])
            tick_labels = [dates.iloc[i].strftime('%m-%d') for i in tick_positions]
            
            # 确保显示第一天和最后一天
            if tick_positions[0] != 0:
                tick_positions = [0] + tick_positions
                tick_labels = [dates.iloc[0].strftime('%m-%d')] + tick_labels
            if tick_positions[-1] != len(dates) - 1:
                tick_positions.append(len(dates) - 1)
                tick_labels.append(dates.iloc[-1].strftime('%m-%d'))
            
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels, rotation=45)
            ax.grid(True, alpha=0.3)
            
            # 设置x轴范围确保对齐
            ax.set_xlim(-0.5, len(dates) - 0.5)
            
            # OBV信息 - 全英文
            latest_obv = obvs.iloc[-1]
            obv_change = obvs.iloc[-1] - obvs.iloc[-2] if len(obvs) > 1 else 0
            
            latest_obv_ma5 = obv_ma5.iloc[-1] if len(obv_ma5) >= 5 and pd.notna(obv_ma5.iloc[-1]) else 0
            latest_obv_ma10 = obv_ma10.iloc[-1] if len(obv_ma10) >= 10 and pd.notna(obv_ma10.iloc[-1]) else 0
            
            info_text = f'Latest OBV: {latest_obv:,.0f}\nChange: {obv_change:+,.0f}\n'
            info_text += f'Max: {obvs.max():,.0f} | Min: {obvs.min():,.0f}\n'
            if latest_obv_ma5 > 0:
                info_text += f'OBV MA5: {latest_obv_ma5:,.0f}\n'
            if latest_obv_ma10 > 0:
                info_text += f'OBV MA10: {latest_obv_ma10:,.0f}'
            
            # 调整子图位置，为图例留出空间
            plt.subplots_adjust(bottom=0.2)
            
            # 添加图例 - 移到图外下方
            ax.legend(bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=3)
            
            # 信息框 - 移回图内左上角，调低字体和背景透明度
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
                   verticalalignment='top', alpha=0.7,
                   bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.2))
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            print(f"❌ OBV chart creation error: {str(e)}")
            return None
    
    def create_cmf_chart(self, data, symbol, company_name):
        """创建CMF指标图 (Chaikin Money Flow)"""
        try:
            fig, ax = plt.subplots(figsize=(14, 8))
            
            dates = data['Date']
            cmf = data['CMF']
            
            # 创建交易日索引，与其他图表保持一致
            trading_day_indices = list(range(len(dates)))
            
            # 绘制CMF线 - 使用交易日索引，只绘制非NaN的值
            valid_mask = ~cmf.isna()
            valid_indices = [i for i, valid in enumerate(valid_mask) if valid]
            valid_cmf = cmf[valid_mask]
            
            ax.plot(valid_indices, valid_cmf, color='purple', linewidth=2.5, label='CMF (21-day)', alpha=0.9)
            
            # 添加零线
            ax.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
            
            # 添加±0.05和±0.10的参考线
            ax.axhline(y=0.05, color='green', linestyle='--', linewidth=1, alpha=0.3, label='+0.05 (Bullish)')
            ax.axhline(y=-0.05, color='red', linestyle='--', linewidth=1, alpha=0.3, label='-0.05 (Bearish)')
            ax.axhline(y=0.10, color='darkgreen', linestyle=':', linewidth=1, alpha=0.3)
            ax.axhline(y=-0.10, color='darkred', linestyle=':', linewidth=1, alpha=0.3)
            
            # 填充正负区域 - 只填充有效数据
            if len(valid_indices) > 0:
                ax.fill_between(valid_indices, 0, valid_cmf, where=(valid_cmf >= 0), 
                               color='green', alpha=0.2, interpolate=True)
                ax.fill_between(valid_indices, 0, valid_cmf, where=(valid_cmf < 0), 
                               color='red', alpha=0.2, interpolate=True)
            
            # 标题和格式 - 全英文
            ax.set_title(f'{company_name} ({symbol}) - Chaikin Money Flow (CMF) Chart\n{dates.iloc[0].strftime("%Y-%m-%d")} to {dates.iloc[-1].strftime("%Y-%m-%d")}', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Trading Days', fontsize=12)
            ax.set_ylabel('CMF Value', fontsize=12)
            
            # 格式化x轴 - 与其他图表保持一致的交易日显示
            if len(dates) <= 10:
                step = 1
            elif len(dates) <= 20:
                step = 2
            else:
                step = 3
            
            tick_positions = list(trading_day_indices[::step])
            tick_labels = [dates.iloc[i].strftime('%m-%d') for i in tick_positions]
            
            # 确保显示第一天和最后一天
            if tick_positions[0] != 0:
                tick_positions = [0] + tick_positions
                tick_labels = [dates.iloc[0].strftime('%m-%d')] + tick_labels
            if tick_positions[-1] != len(dates) - 1:
                tick_positions.append(len(dates) - 1)
                tick_labels.append(dates.iloc[-1].strftime('%m-%d'))
            
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels, rotation=45)
            ax.grid(True, alpha=0.3)
            
            # 设置x轴范围与其他图表一致
            ax.set_xlim(-0.5, len(dates) - 0.5)
            
            # CMF信息 - 全英文
            # 获取最后一个有效的CMF值
            valid_cmf_values = cmf.dropna()
            if len(valid_cmf_values) > 0:
                latest_cmf = valid_cmf_values.iloc[-1]
                if len(valid_cmf_values) > 1:
                    cmf_change = valid_cmf_values.iloc[-1] - valid_cmf_values.iloc[-2]
                else:
                    cmf_change = 0
            else:
                latest_cmf = 0
                cmf_change = 0
            
            # 判断信号
            if latest_cmf > 0.05:
                signal = 'Strong Buying Pressure'
                signal_color = 'green'
            elif latest_cmf > 0:
                signal = 'Buying Pressure'
                signal_color = 'lightgreen'
            elif latest_cmf < -0.05:
                signal = 'Strong Selling Pressure'
                signal_color = 'red'
            else:
                signal = 'Selling Pressure'
                signal_color = 'lightcoral'
            
            # 计算CMF的最大最小值（只考虑非NaN值）
            cmf_max = valid_cmf_values.max() if len(valid_cmf_values) > 0 else 0
            cmf_min = valid_cmf_values.min() if len(valid_cmf_values) > 0 else 0
            
            info_text = f'Latest CMF: {latest_cmf:.4f}\nChange: {cmf_change:+.4f}\n'
            info_text += f'Max: {cmf_max:.4f} | Min: {cmf_min:.4f}\n'
            info_text += f'Signal: {signal}'
            
            # 调整子图位置，为图例留出空间
            plt.subplots_adjust(bottom=0.2)
            
            # 添加图例 - 移到图外下方
            ax.legend(bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=3)
            
            # 信息框 - 移回图内左上角，调低字体和背景透明度
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
                   verticalalignment='top', alpha=0.7,
                   bbox=dict(boxstyle='round', facecolor=signal_color, alpha=0.2))
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            print(f"❌ CMF chart creation error: {str(e)}")
            return None
    
    def process_stock_list(self):
        """处理股票列表，每个股票输出单独的PDF文件"""
        try:
            # 创建输出文件夹
            output_dir = 'charts_output'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"📁 Created output directory: {output_dir}")
            
            stocks_df = pd.read_excel(f'List - {today_short}.xlsx')
            print(f"✅ Found {len(stocks_df)} stocks in the list")
            
            # 连接API
            if not self.connect_api():
                return False
            
            successful_count = 0
            failed_stocks = []
            
            # 获取今天的日期用于文件命名
            today_date = datetime.datetime.now().strftime('%Y%m%d')
            
            for index, row in stocks_df.iterrows():
                # 从正确的列获取股票代码和公司名称
                symbol = row['Ticker']  # Ticker列包含股票代码
                company_name = row['Name ']  # Name 列包含公司名称（注意空格）
                
                print(f"\n📊 Processing {symbol}...")
                
                try:
                    # 获取股票数据
                    data = self.get_stock_data(symbol)
                    if data is None or len(data) == 0:
                        print(f"❌ No data for {symbol}")
                        failed_stocks.append(symbol)
                        continue
                    
                    # 获取公司名称（如果需要更完整的名称可以再次获取）
                    if pd.isna(company_name) or not company_name.strip():
                        company_name = self.get_company_name(symbol)
                    
                    # 数据已经包含了OBV和所有均线，无需重新计算
                    # data = self.calculate_obv(data)  # 已在get_stock_data中计算
                    
                    # 为每个股票创建单独的PDF文件
                    output_filename = os.path.join(output_dir, f'{symbol}_{today_date}.pdf')
                    
                    with PdfPages(output_filename) as pdf:
                        # 第一页：股票价格图（K线 + 价格折线 + 均线）
                        stock_fig = self.create_stock_chart(data, symbol, company_name)
                        if stock_fig:
                            pdf.savefig(stock_fig, bbox_inches='tight', dpi=300)
                            plt.close(stock_fig)
                        
                        # 第二页：OBV指标图（OBV + OBV均线）
                        obv_fig = self.create_obv_chart(data, symbol, company_name)
                        if obv_fig:
                            pdf.savefig(obv_fig, bbox_inches='tight', dpi=300)
                            plt.close(obv_fig)
                        
                        # 第三页：CMF指标图（Chaikin Money Flow）
                        cmf_fig = self.create_cmf_chart(data, symbol, company_name)
                        if cmf_fig:
                            pdf.savefig(cmf_fig, bbox_inches='tight', dpi=300)
                            plt.close(cmf_fig)
                    
                    print(f"✅ {symbol} completed - saved to {output_filename}")
                    successful_count += 1
                    
                except Exception as e:
                    print(f"❌ Error processing {symbol}: {str(e)}")
                    failed_stocks.append(symbol)
                    continue
            
            print(f"\n🎯 Summary:")
            print(f"✅ Successful: {successful_count} stocks")
            print(f"❌ Failed: {len(failed_stocks)} stocks")
            if failed_stocks:
                print(f"Failed stocks: {', '.join(failed_stocks)}")
            print(f"📂 Output directory: {output_dir}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in batch processing: {str(e)}")
            return False

def main():
    """主函数"""
    print("🚀 Batch Stock and OBV Analyzer - Enhanced Version")
    print("=" * 60)
    
    # 初始化分析器
    analyzer = BatchStockAnalyzer()
    
    # 批量处理
    success = analyzer.process_stock_list()
    
    if success:
        print("🎉 Batch processing completed!")
    else:
        print("❌ Batch processing failed!")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
