"""
Stock Data Services - VWAP and Technical Indicators
Provides calculation services for VWAP, MA, OBV, CMF indicators
Integrates with yfinance for real-time and historical data
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time as datetime_time
from typing import Optional, Dict, List
import logging
import requests

from .models import StockScore

logger = logging.getLogger(__name__)

# Note: yfinance 0.2.36+ handles sessions internally with curl_cffi
# No need to create custom session - let yfinance handle it


class VWAPCalculationService:
    """VWAP and technical indicators calculation service"""

    @staticmethod
    def get_latest_stock_score(symbol: str) -> Optional[Dict]:
        """
        Fetch latest stored scoring snapshot for a ticker from stock_scores table.
        """
        if not symbol:
            return None

        try:
            score = (
                StockScore.objects
                .filter(ticker=symbol)
                .order_by('-calculation_date', '-updated_at')
                .first()
            )
            if not score:
                return None

            def to_float(value):
                if value is None:
                    return None
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return None

            return {
                'calculation_date': score.calculation_date.isoformat() if score.calculation_date else None,
                'total_score': to_float(score.total_score),
                'recommended_action': score.recommended_action or '',
                'recommended_action_detail': score.recommended_action_detail or '',
                'last_trading_date': score.last_trading_date.isoformat() if score.last_trading_date else None,
                'last_close': to_float(score.last_close),
                'score_components': score.score_components or {},
                'signal_date': score.signal_date.isoformat() if score.signal_date else None,
                'execution_date': score.execution_date.isoformat() if score.execution_date else None,
                'suggested_position_pct': to_float(score.suggested_position_pct),
                'stop_loss_price': to_float(score.stop_loss_price),
                'take_profit_price': to_float(score.take_profit_price),
            }
        except Exception as exc:
            logger.warning("Unable to fetch stock score for %s: %s", symbol, exc)
            return None
    
    @staticmethod
    def filter_trading_hours(df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter trading hours: 9:15-11:30, 13:00-15:00 (strict filtering for China market)
        """
        if df.empty:
            return df
        
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        times = df.index.time
        morning_start = datetime_time(9, 15)
        morning_end = datetime_time(11, 30)
        afternoon_start = datetime_time(13, 0)
        afternoon_end = datetime_time(15, 0)
        
        mask = ((times >= morning_start) & (times <= morning_end)) | \
               ((times >= afternoon_start) & (times <= afternoon_end))
        
        filtered_df = df[mask].copy()
        
        if not filtered_df.empty:
            filtered_df = filtered_df[~filtered_df.index.duplicated(keep='first')]
        
        return filtered_df
    
    @staticmethod
    def calculate_vwap(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate VWAP Indicator"""
        df = df.copy()
        df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['TP_Volume'] = df['Typical_Price'] * df['Volume']
        df['Cumulative_TP_Volume'] = df['TP_Volume'].cumsum()
        df['Cumulative_Volume'] = df['Volume'].cumsum()
        df['VWAP'] = df['Cumulative_TP_Volume'] / df['Cumulative_Volume']
        return df
    
    @staticmethod
    def calculate_ma(df: pd.DataFrame, periods: List[int] = [5, 10]) -> pd.DataFrame:
        """Calculate Moving Averages"""
        df = df.copy()
        for period in periods:
            df[f'MA{period}'] = df['Close'].rolling(window=period).mean()
        return df
    
    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate On-Balance Volume (OBV)"""
        df = df.copy()
        df['OBV'] = 0.0
        
        for i in range(1, len(df)):
            if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
                df.loc[df.index[i], 'OBV'] = df['OBV'].iloc[i-1] + df['Volume'].iloc[i]
            elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
                df.loc[df.index[i], 'OBV'] = df['OBV'].iloc[i-1] - df['Volume'].iloc[i]
            else:
                df.loc[df.index[i], 'OBV'] = df['OBV'].iloc[i-1]
        
        df['OBV_MA5'] = df['OBV'].rolling(window=5).mean()
        df['OBV_MA10'] = df['OBV'].rolling(window=10).mean()
        
        return df
    
    @staticmethod
    def calculate_cmf(df: pd.DataFrame, period: int = 21) -> pd.DataFrame:
        """Calculate Chaikin Money Flow (CMF)"""
        df = df.copy()
        
        df['MF_Multiplier'] = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
        df.loc[df['High'] == df['Low'], 'MF_Multiplier'] = 0
        df['MF_Volume'] = df['MF_Multiplier'] * df['Volume']
        df['CMF'] = df['MF_Volume'].rolling(window=period).sum() / df['Volume'].rolling(window=period).sum()
        
        return df
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        df = VWAPCalculationService.calculate_ma(df, [5, 10])
        df = VWAPCalculationService.calculate_obv(df)
        df = VWAPCalculationService.calculate_cmf(df, 21)
        return df
    
    @staticmethod
    def get_intraday_data(symbol: str, market: str = 'CN') -> Optional[pd.DataFrame]:
        """
        Get Intraday Minute-level Data (Real-time)
        
        Args:
            symbol: Stock symbol (e.g., '600519.SS' for China, 'AAPL' for US)
            market: Market type ('CN' for China, 'US' for US markets)
        
        Returns:
            DataFrame with intraday data or None if failed
        """
        try:
            stock = yf.Ticker(symbol)
            # 使用 period='1d' 获取今日数据，interval='1m' 获取分钟级数据
            # yfinance 会自动获取最新可用数据
            df = stock.history(period='1d', interval='1m', prepost=False)
            
            if df.empty:
                logger.warning(f"No intraday data available for {symbol}")
                return None
            
            # 记录数据时间范围用于调试
            if not df.empty:
                first_time = df.index[0]
                last_time = df.index[-1]
                logger.info(f"Intraday data for {symbol}: {first_time} to {last_time} ({len(df)} bars)")
            
            # 过滤掉成交量为0的数据
            df = df[df['Volume'] > 0]
            
            if market == 'CN':
                df = VWAPCalculationService.filter_trading_hours(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to get intraday data for {symbol}: {e}")
            return None
    
    @staticmethod
    def get_historical_data(symbol: str, days: int = 30, interval: str = '1d', period: str = None) -> Optional[pd.DataFrame]:
        """
        Get Historical Data
        
        Args:
            symbol: Stock symbol
            days: Number of trading days to retrieve (1-3650 days, supporting up to 10 years)
            interval: Data interval ('1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo')
            period: yfinance period string ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y')
                   If not provided, will be auto-determined based on days
        
        Returns:
            DataFrame with historical data or None if failed
        
        Note:
            yfinance has limitations on intraday data:
            - 1m interval: max 7 days
            - 5m interval: max 60 days
            - 15m interval: max 60 days
            - 1h interval: max 730 days
        """
        try:
            stock = yf.Ticker(symbol)
            
            # Validate interval and adjust period based on yfinance limitations
            if interval in ['1m', '2m', '5m', '15m', '30m']:
                # For minute intervals, yfinance has strict limits
                if interval == '1m':
                    # 1m interval: max 7 days
                    if period is None or period not in ['1d', '5d', '7d']:
                        period = '5d'  # Default to 5 days for 1-minute data
                        logger.warning(f"1m interval limited to max 7 days, using period={period}")
                elif interval in ['5m', '15m', '30m']:
                    # 5m, 15m, 30m interval: max 60 days
                    if period is None:
                        period = '5d'  # For 5D range, use 5 days
                    # Ensure period doesn't exceed 60 days
                    valid_periods = ['1d', '5d', '1mo']
                    if period not in valid_periods:
                        period = '1mo'
                        logger.warning(f"{interval} interval limited to max 60 days, using period={period}")
            elif interval == '1h':
                # 1h interval: max 730 days
                if period is None:
                    period = '1mo'
            else:
                # Daily or longer intervals - use original logic
                if period is None:
                    # Extended period mapping for comprehensive historical data (up to 10 years)
                    if days <= 5:
                        period = '5d'
                    elif days <= 30:
                        period = '1mo'
                    elif days <= 60:
                        period = '3mo'
                    elif days <= 180:
                        period = '6mo'
                    elif days <= 365:
                        period = '1y'
                    elif days <= 730:
                        period = '2y'
                    elif days <= 1825:
                        period = '5y'
                    else:  # 10 years
                        period = '10y'
            
            logger.info(f"Fetching {symbol} data: period={period}, interval={interval}")
            df = stock.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No historical data available for {symbol}")
                return None
            
            df = df[df['Volume'] > 0].copy()
            
            # For intraday intervals (minute-level data), use all data without tail()
            # For daily intervals, use calculation window
            if interval in ['1m', '2m', '5m', '15m', '30m', '1h']:
                # Intraday data - use all available data
                df_full = df.copy()
                # For intraday, only calculate indicators if we have enough data points
                if len(df_full) > 21:  # CMF needs 21 periods
                    df_full = VWAPCalculationService.calculate_all_indicators(df_full)
                logger.info(f"Intraday data: {len(df_full)} data points for {symbol} at {interval} interval")
            else:
                # Daily or longer intervals - use calculation window
                min_calc_days = 30
                calculation_days = max(min_calc_days, min(days * 2, len(df)))
                df_full = df.tail(calculation_days).copy()
                df_full = VWAPCalculationService.calculate_all_indicators(df_full)
                logger.info(f"Daily data: {len(df_full)} data points for {symbol}")
            
            # Return all calculated data for maximum chart flexibility
            df_display = df_full.copy()
            
            df_display = df_display.reset_index()
            
            # Format date string based on interval type
            # yfinance uses 'Datetime' for intraday data and 'Date' for daily data
            if interval in ['1m', '2m', '5m', '15m', '30m', '1h']:
                # Intraday: include time
                # Check which column name yfinance used
                if 'Datetime' in df_display.columns:
                    df_display['Date_Str'] = df_display['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
                elif 'Date' in df_display.columns:
                    df_display['Date_Str'] = df_display['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    # Fallback: use index
                    df_display['Date_Str'] = df_display.index.strftime('%Y-%m-%d %H:%M:%S')
            else:
                # Daily: date only
                if 'Date' in df_display.columns:
                    df_display['Date_Str'] = df_display['Date'].dt.strftime('%Y-%m-%d')
                else:
                    df_display['Date_Str'] = df_display.index.strftime('%Y-%m-%d')
            
            df_display['Trading_Day'] = range(1, len(df_display) + 1)
            
            return df_display
            
        except Exception as e:
            logger.error(f"Failed to get historical data for {symbol}: {e}")
            return None
    
    @staticmethod
    def format_intraday_response(df: pd.DataFrame, symbol: str, company_name: str, company_data: dict = None) -> Dict:
        """
        Format intraday data for API response
        
        Args:
            df: DataFrame with intraday data
            symbol: Stock symbol
            company_name: Company name
            company_data: Optional dict with company data from database (previous_close, open, etc.)
        
        Returns:
            Dictionary with formatted data for frontend consumption
        """
        if df is None or df.empty:
            return {
                'success': False,
                'message': 'No data available',
                'data': None
            }
        
        df = VWAPCalculationService.calculate_vwap(df)
        open_price = float(df['Open'].iloc[0])
        
        # Use database values if available
        if company_data:
            if company_data.get('previous_close') is not None:
                previous_close = float(company_data['previous_close'])
            else:
                previous_close = open_price  # Fallback
            
            if company_data.get('open') is not None:
                open_price = float(company_data['open'])
        else:
            previous_close = open_price
        
        data_points = []
        for idx, row in df.iterrows():
            data_points.append({
                'time': idx.strftime('%Y-%m-%d %H:%M:%S'),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume']),
                'vwap': float(row['VWAP'])
            })
        
        latest = df.iloc[-1]
        current_price = float(latest['Close'])
        
        score_snapshot = VWAPCalculationService.get_latest_stock_score(symbol)

        return {
            'success': True,
            'symbol': symbol,
            'company_name': company_name,
            'previous_close': previous_close,
            'open_price': open_price,
            'current_price': current_price,
            'change': current_price - previous_close,
            'change_pct': (current_price - previous_close) / previous_close * 100 if previous_close != 0 else 0,
            'high': float(df['High'].max()),
            'low': float(df['Low'].min()),
            'volume': int(df['Volume'].sum()),
            'day_range': f"{float(df['Low'].min()):.2f} - {float(df['High'].max()):.2f}",
            'data_points': data_points,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            # Add database fields if available
            'price_52w_high': company_data.get('price_52w_high') if company_data else None,
            'price_52w_low': company_data.get('price_52w_low') if company_data else None,
            'last_trade_date': str(company_data.get('last_trade_date')) if company_data and company_data.get('last_trade_date') else None,
            'stock_score': score_snapshot
        }
    
    @staticmethod
    def format_historical_response(df: pd.DataFrame, symbol: str, company_name: str, company_data: dict = None) -> Dict:
        """
        Format historical data for API response
        
        Args:
            df: DataFrame with historical data
            symbol: Stock symbol
            company_name: Company name
            company_data: Optional dict with company data from database (previous_close, open, etc.)
        
        Returns:
            Dictionary with formatted data for frontend consumption
        """
        if df is None or df.empty:
            return {
                'success': False,
                'message': 'No data available',
                'data': None
            }
        
        data_points = []
        for _, row in df.iterrows():
            point = {
                'date': row['Date_Str'],
                'trading_day': int(row['Trading_Day']),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume']),
            }
            
            if pd.notna(row.get('MA5')):
                point['ma5'] = float(row['MA5'])
            if pd.notna(row.get('MA10')):
                point['ma10'] = float(row['MA10'])
            if pd.notna(row.get('OBV')):
                point['obv'] = float(row['OBV'])
            if pd.notna(row.get('OBV_MA5')):
                point['obv_ma5'] = float(row['OBV_MA5'])
            if pd.notna(row.get('OBV_MA10')):
                point['obv_ma10'] = float(row['OBV_MA10'])
            if pd.notna(row.get('CMF')):
                point['cmf'] = float(row['CMF'])
            
            data_points.append(point)
        
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        # Calculate day range from data
        high_val = float(df['High'].max())
        low_val = float(df['Low'].min())
        day_range = f"{low_val:.2f} - {high_val:.2f}"
        
        # Use database values if available
        if company_data:
            previous_close = float(company_data['previous_close']) if company_data.get('previous_close') else float(prev['Close'])
            open_price = float(company_data['open']) if company_data.get('open') else float(latest['Open'])
        else:
            previous_close = float(prev['Close'])
            open_price = float(latest['Open'])
        
        score_snapshot = VWAPCalculationService.get_latest_stock_score(symbol)

        return {
            'success': True,
            'symbol': symbol,
            'company_name': company_name,
            'previous_close': previous_close,
            'open_price': open_price,
            'current_price': float(latest['Close']),
            'latest_close': float(latest['Close']),
            'change': float(latest['Close'] - previous_close),
            'change_pct': float((latest['Close'] - previous_close) / previous_close * 100) if previous_close != 0 else 0,
            'day_range': day_range,
            'volume': int(df['Volume'].sum()),
            'cmf': float(latest['CMF']) if pd.notna(latest.get('CMF')) else 0,
            'obv': int(latest['OBV']) if pd.notna(latest.get('OBV')) else 0,
            'trading_days': len(df),
            'data_points': data_points,
            # Add database fields if available
            'price_52w_high': company_data.get('price_52w_high') if company_data else None,
            'price_52w_low': company_data.get('price_52w_low') if company_data else None,
            'last_trade_date': str(company_data.get('last_trade_date')) if company_data and company_data.get('last_trade_date') else None,
            'stock_score': score_snapshot
        }
