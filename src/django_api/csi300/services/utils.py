"""
Investment Summary Utilities Module

通用工具函数 - 包括数值转换、股票数据获取等。
"""

import os
import logging
from decimal import Decimal, InvalidOperation
from typing import Dict, Any

import yfinance as yf

logger = logging.getLogger(__name__)

# XAI SDK 配置 (从环境变量读取)
XAI_API_KEY = os.environ.get("XAI_API_KEY")
if not XAI_API_KEY:
    import warnings
    warnings.warn(
        "XAI_API_KEY environment variable is not set. "
        "Please configure it in your .env file for Investment Summary generation to work.",
        UserWarning
    )


def safe_decimal(value) -> Decimal:
    """安全地将值转换为 Decimal，失败时返回 0"""
    if value is None:
        return Decimal('0')
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal('0')


def format_market_cap(mcap) -> str:
    """格式化市值显示"""
    if not mcap:
        return "N/A"
    if mcap >= 1e12:
        return f"{mcap/1e12:.2f}T"
    if mcap >= 1e9:
        return f"{mcap/1e9:.2f}B"
    if mcap >= 1e6:
        return f"{mcap/1e6:.2f}M"
    return f"{mcap:,.0f}"


def get_stock_data_sync(symbol: str) -> Dict[str, Any]:
    """
    同步获取股票数据 (将在线程池中运行)
    
    Args:
        symbol: 股票代码
        
    Returns:
        包含 last_price, market_cap, currency, success 的字典
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        last_price = (
            info.get('regularMarketPreviousClose') or 
            info.get('previousClose') or 
            info.get('currentPrice')
        )
        market_cap = info.get('marketCap')
        currency = info.get('currency', 'USD')
        return {
            'last_price': last_price,
            'market_cap': market_cap,
            'currency': currency,
            'success': True
        }
    except Exception as e:
        logger.debug(f"Failed to fetch stock data for {symbol}: {e}")
        return {
            'last_price': None,
            'market_cap': None,
            'currency': '',
            'success': False
        }


__all__ = [
    'XAI_API_KEY',
    'safe_decimal',
    'format_market_cap',
    'get_stock_data_sync',
]

