"""
Configuration Manager for Japan FRED API
管理日本经济指标的配置和数据获取设置
"""

import logging

logger = logging.getLogger(__name__)


class JapanFredConfigManager:
    """日本FRED配置管理器"""

    # 日本经济指标配置
    JAPAN_INDICATORS = {
        "cpi": {
            "series_id": "JPNCCPIALLMINMEI",
            "name": "Japan Consumer Price Index",
            "category": "inflation",
            "unit": "Index",
            "frequency": "Monthly",
            "description": "日本消费者价格指数 - 全部项目",
        },
        "gdp": {
            "series_id": "JPNGDPDEFAISMEI",
            "name": "Japan GDP Deflator",
            "category": "economic_growth",
            "unit": "Index",
            "frequency": "Quarterly",
            "description": "日本GDP平减指数",
        },
        "unemployment": {
            "series_id": "LRUN64TTJPQ156S",
            "name": "Japan Unemployment Rate",
            "category": "labor_market",
            "unit": "Percent",
            "frequency": "Monthly",
            "description": "日本失业率",
        },
        "interest-rate": {
            "series_id": "INTDSRJPM193N",
            "name": "Japan Interest Rate",
            "category": "monetary_policy",
            "unit": "Percent",
            "frequency": "Monthly",
            "description": "日本基准利率",
        },
        "export": {
            "series_id": "XTEXVA01JPM667S",
            "name": "Japan Exports",
            "category": "trade",
            "unit": "Million USD",
            "frequency": "Monthly",
            "description": "日本出口总额",
        },
        "import": {
            "series_id": "XTIMVA01JPM667S",
            "name": "Japan Imports",
            "category": "trade",
            "unit": "Million USD",
            "frequency": "Monthly",
            "description": "日本进口总额",
        },
        "population": {
            "series_id": "POPTOTJPA647NWDB",
            "name": "Japan Population",
            "category": "demographics",
            "unit": "Persons",
            "frequency": "Annual",
            "description": "日本总人口",
        },
        "trade-balance": {
            "series_id": "BPBLTT01JPQ188S",
            "name": "Japan Trade Balance",
            "category": "trade",
            "unit": "Million USD",
            "frequency": "Quarterly",
            "description": "日本贸易平衡",
        },
        "money-supply": {
            "series_id": "JPNMABMM101IXNB",
            "name": "Japan Money Supply M2",
            "category": "monetary_policy",
            "unit": "Billion Yen",
            "frequency": "Monthly",
            "description": "日本货币供应量M2",
        },
    }

    # 数据库表配置
    DB_CONFIG = {
        "series_info_table": "fred_jp_series_info",
        "indicators_table": "fred_jp_indicators",
        "schema": "public",
    }

    # API配置
    API_CONFIG = {
        "base_path": "/api/fred-jp/",
        "version": "1.0.0",
        "country": "Japan",
        "source": "FRED (Federal Reserve Economic Data)",
        "default_limit": 100,
        "max_limit": 1000,
    }

    @classmethod
    def get_indicator_config(cls, indicator_name: str) -> dict | None:
        """获取指定指标的配置"""
        return cls.JAPAN_INDICATORS.get(indicator_name.lower())

    @classmethod
    def get_series_id(cls, indicator_name: str) -> str | None:
        """获取指标对应的FRED series ID"""
        config = cls.get_indicator_config(indicator_name)
        return config.get("series_id") if config else None

    @classmethod
    def get_all_indicators(cls) -> list[str]:
        """获取所有支持的指标名称"""
        return list(cls.JAPAN_INDICATORS.keys())

    @classmethod
    def get_indicators_by_category(cls, category: str) -> list[str]:
        """根据类别获取指标列表"""
        return [
            name
            for name, config in cls.JAPAN_INDICATORS.items()
            if config.get("category") == category
        ]

    @classmethod
    def get_categories(cls) -> list[str]:
        """获取所有指标类别"""
        categories = set()
        for config in cls.JAPAN_INDICATORS.values():
            if config.get("category"):
                categories.add(config["category"])
        return sorted(categories)

    @classmethod
    def validate_indicator(cls, indicator_name: str) -> bool:
        """验证指标名称是否有效"""
        return indicator_name.lower() in cls.JAPAN_INDICATORS

    @classmethod
    def get_api_info(cls) -> dict:
        """获取API基本信息"""
        return {
            **cls.API_CONFIG,
            "indicators_count": len(cls.JAPAN_INDICATORS),
            "supported_indicators": cls.get_all_indicators(),
            "categories": cls.get_categories(),
        }
