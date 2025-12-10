"""
日本FRED动态配置管理器
从数据库驱动的配置系统，替代硬编码的配置文件
"""

import logging

from fred_common.base_config import BaseDynamicConfigManager

from .models import FredJpIndicatorConfig

logger = logging.getLogger(__name__)


class DynamicFredJpConfigManager(BaseDynamicConfigManager):
    """日本FRED动态配置管理器 - 数据库驱动的配置系统"""

    CACHE_KEY_PREFIX = "fred_jp_config_"
    CACHE_TIMEOUT = 300  # 5分钟缓存

    @classmethod
    @property
    def config_model(cls):
        return FredJpIndicatorConfig

    @classmethod
    @property
    def service_name(cls) -> str:
        return "FRED JP"

    @classmethod
    def _get_fallback_config(cls) -> dict:
        """
        获取备用配置（当数据库访问失败时）
        包含日本核心经济指标
        """
        return {
            # 日本CPI
            "JPNCCPIALLMINMEI": {
                "name": "Japan Consumer Price Index of All Items",
                "description": "日本全项目消费者价格指数",
                "indicator_type": "inflation",
                "units": "Index 2015=100",
                "frequency": "Monthly",
                "category": "inflation",
                "api_endpoint": "cpi",
                "fallback_value": 106.8,
                "priority": 1,
            },
            # 日本GDP
            "JPNGDPDEFQISMEI": {
                "name": "Japan Gross Domestic Product Deflator",
                "description": "日本GDP平减指数",
                "indicator_type": "gdp",
                "units": "Index 2015=100",
                "frequency": "Quarterly",
                "category": "gdp",
                "api_endpoint": "gdp-deflator",
                "fallback_value": 106.2,
                "priority": 2,
            },
            # 日本工业生产
            "JPNPROINDQISMEI": {
                "name": "Japan Industrial Production",
                "description": "日本工业生产指数",
                "indicator_type": "production",
                "units": "Index 2015=100",
                "frequency": "Monthly",
                "category": "production",
                "api_endpoint": "industrial-production",
                "fallback_value": 95.4,
                "priority": 3,
            },
            # 日本失业率
            "LRUN64TTJPM156S": {
                "name": "Japan Unemployment Rate",
                "description": "日本失业率",
                "indicator_type": "employment",
                "units": "Percent",
                "frequency": "Monthly",
                "category": "labor",
                "api_endpoint": "unemployment-rate",
                "fallback_value": 2.6,
                "priority": 4,
            },
            # 日元兑美元汇率
            "DEXJPUS": {
                "name": "Japan / U.S. Foreign Exchange Rate",
                "description": "日元兑美元汇率",
                "indicator_type": "exchange_rate",
                "units": "Japanese Yen to One U.S. Dollar",
                "frequency": "Daily",
                "category": "forex",
                "api_endpoint": "usd-jpy",
                "fallback_value": 154.5,
                "priority": 5,
            },
            # 日本政策利率
            "IRSTCI01JPM156N": {
                "name": "Japan Short-term Interest Rate",
                "description": "日本短期利率（政策利率）",
                "indicator_type": "interest_rate",
                "units": "Percent",
                "frequency": "Monthly",
                "category": "monetary",
                "api_endpoint": "policy-rate",
                "fallback_value": -0.1,
                "priority": 6,
            },
            # 日本10年期国债
            "IRLTLT01JPM156N": {
                "name": "Japan 10-Year Government Bond Yield",
                "description": "日本10年期国债收益率",
                "indicator_type": "interest_rate",
                "units": "Percent",
                "frequency": "Monthly",
                "category": "bonds",
                "api_endpoint": "jgb-10y",
                "fallback_value": 0.85,
                "priority": 7,
            },
            # 日本M2货币供应
            "MYAGM2JPM189N": {
                "name": "Japan M2 Money Stock",
                "description": "日本M2货币供应量",
                "indicator_type": "money_supply",
                "units": "Billions of Yen",
                "frequency": "Monthly",
                "category": "monetary",
                "api_endpoint": "m2",
                "fallback_value": 1250000,
                "priority": 8,
            },
        }


# 兼容性函数
def get_fred_jp_indicators_config():
    """兼容性函数 - 返回所有指标配置"""
    return DynamicFredJpConfigManager.get_all_indicators()


def get_fred_jp_indicator_by_series_id(series_id):
    """兼容性函数 - 根据series_id获取指标配置"""
    return DynamicFredJpConfigManager.get_indicator_config(series_id)
