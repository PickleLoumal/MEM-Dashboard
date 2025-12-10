"""
美国FRED动态配置管理器
从数据库驱动的配置系统，替代硬编码的配置文件
"""

import logging

from django.core.cache import cache
from django.db import transaction

from .models import FredUsIndicatorConfig

logger = logging.getLogger(__name__)


class DynamicFredUsConfigManager:
    """美国FRED动态配置管理器 - 数据库驱动的配置系统"""

    CACHE_KEY_PREFIX = "fred_us_config_"
    CACHE_TIMEOUT = 300  # 5分钟缓存

    @classmethod
    def get_all_indicators(cls):
        """获取所有激活的指标配置（缓存版本）"""
        cache_key = f"{cls.CACHE_KEY_PREFIX}all_active"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return cached_data

        try:
            configs = FredUsIndicatorConfig.get_active_configs()
            result = {}

            for config in configs:
                result[config.series_id] = config.to_config_dict()

            cache.set(cache_key, result, cls.CACHE_TIMEOUT)
            logger.info(f"Loaded {len(result)} FRED US indicator configs from database")
            return result

        except Exception:
            logger.exception("Error loading FRED US configs from database")
            return cls._get_fallback_config()

    @classmethod
    def get_auto_fetch_indicators(cls):
        """获取需要自动抓取的指标配置"""
        cache_key = f"{cls.CACHE_KEY_PREFIX}auto_fetch"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return cached_data

        try:
            configs = FredUsIndicatorConfig.get_auto_fetch_configs()
            result = {}

            for config in configs:
                result[config.series_id] = config.to_config_dict()

            cache.set(cache_key, result, cls.CACHE_TIMEOUT)
            return result

        except Exception:
            logger.exception("Error loading auto-fetch configs")
            return {}

    @classmethod
    def get_indicator_config(cls, series_id):
        """获取单个指标配置"""
        cache_key = f"{cls.CACHE_KEY_PREFIX}indicator_{series_id}"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return cached_data

        try:
            config = FredUsIndicatorConfig.objects.filter(
                series_id=series_id, is_active=True
            ).first()

            if config:
                result = config.to_config_dict()
                cache.set(cache_key, result, cls.CACHE_TIMEOUT)
                return result

            return None

        except Exception:
            logger.exception("Error loading config for {series_id}")
            return None

    @classmethod
    def get_configs_by_category(cls, category):
        """按类别获取指标配置"""
        cache_key = f"{cls.CACHE_KEY_PREFIX}category_{category}"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return cached_data

        try:
            configs = FredUsIndicatorConfig.get_configs_by_category(category)
            result = {}

            for config in configs:
                result[config.series_id] = config.to_config_dict()

            cache.set(cache_key, result, cls.CACHE_TIMEOUT)
            return result

        except Exception:
            logger.exception("Error loading configs for category {category}")
            return {}

    @classmethod
    def get_configs_by_frequency(cls, frequency):
        """按抓取频率获取指标配置"""
        cache_key = f"{cls.CACHE_KEY_PREFIX}frequency_{frequency}"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return cached_data

        try:
            configs = FredUsIndicatorConfig.get_configs_by_fetch_frequency(frequency)
            result = {}

            for config in configs:
                result[config.series_id] = config.to_config_dict()

            cache.set(cache_key, result, cls.CACHE_TIMEOUT)
            return result

        except Exception:
            logger.exception("Error loading configs for frequency {frequency}")
            return {}

    @classmethod
    def create_indicator(cls, config_data):
        """创建新的指标配置"""
        try:
            with transaction.atomic():
                config = FredUsIndicatorConfig.objects.create(**config_data)
                cls._clear_related_cache()
                logger.info(f"Created new FRED US indicator config: {config.series_id}")
                return config

        except Exception:
            logger.exception("Error creating FRED US indicator config")
            raise

    @classmethod
    def update_indicator(cls, series_id, config_data):
        """更新指标配置"""
        try:
            with transaction.atomic():
                config = FredUsIndicatorConfig.objects.get(series_id=series_id)

                for key, value in config_data.items():
                    setattr(config, key, value)

                config.save()
                cls._clear_related_cache(series_id)
                logger.info(f"Updated FRED US indicator config: {series_id}")
                return config

        except FredUsIndicatorConfig.DoesNotExist:
            logger.exception(f"FRED US indicator config not found: {series_id}")
            return None
        except Exception:
            logger.exception("Error updating FRED US indicator config {series_id}")
            raise

    @classmethod
    def activate_indicator(cls, series_id):
        """激活指标"""
        try:
            config = FredUsIndicatorConfig.objects.get(series_id=series_id)
            config.activate()
            cls._clear_related_cache(series_id)
            logger.info(f"Activated FRED US indicator: {series_id}")
            return True

        except FredUsIndicatorConfig.DoesNotExist:
            logger.exception(f"FRED US indicator config not found: {series_id}")
            return False

    @classmethod
    def deactivate_indicator(cls, series_id):
        """禁用指标"""
        try:
            config = FredUsIndicatorConfig.objects.get(series_id=series_id)
            config.deactivate()
            cls._clear_related_cache(series_id)
            logger.info(f"Deactivated FRED US indicator: {series_id}")
            return True

        except FredUsIndicatorConfig.DoesNotExist:
            logger.exception(f"FRED US indicator config not found: {series_id}")
            return False

    @classmethod
    def update_fetch_status(cls, series_id, status, error_message=None):
        """更新指标抓取状态"""
        try:
            config = FredUsIndicatorConfig.objects.get(series_id=series_id)
            config.update_fetch_status(status, error_message)
            cls._clear_related_cache(series_id)
            logger.info(f"Updated FRED US fetch status for {series_id}: {status}")
            return True

        except FredUsIndicatorConfig.DoesNotExist:
            logger.exception(f"FRED US indicator config not found: {series_id}")
            return False

    @classmethod
    def get_statistics(cls):
        """获取配置统计信息"""
        try:
            total = FredUsIndicatorConfig.objects.count()
            active = FredUsIndicatorConfig.objects.filter(is_active=True).count()
            auto_fetch = FredUsIndicatorConfig.objects.filter(
                is_active=True, auto_fetch=True
            ).count()

            categories = (
                FredUsIndicatorConfig.objects.filter(is_active=True)
                .values_list("category", flat=True)
                .distinct()
            )

            frequencies = (
                FredUsIndicatorConfig.objects.filter(is_active=True, auto_fetch=True)
                .values_list("fetch_frequency", flat=True)
                .distinct()
            )

            return {
                "total_indicators": total,
                "active_indicators": active,
                "auto_fetch_indicators": auto_fetch,
                "categories": list(categories),
                "category_count": len(categories),
                "fetch_frequencies": list(frequencies),
                "frequency_count": len(frequencies),
            }

        except Exception:
            logger.exception("Error getting FRED US statistics")
            return {}

    @classmethod
    def _clear_related_cache(cls, series_id=None):
        """清除相关缓存"""
        cache_keys = [
            f"{cls.CACHE_KEY_PREFIX}all_active",
            f"{cls.CACHE_KEY_PREFIX}auto_fetch",
        ]

        if series_id:
            cache_keys.append(f"{cls.CACHE_KEY_PREFIX}indicator_{series_id}")

            # 清除该指标所属类别和频率的缓存
            try:
                config = FredUsIndicatorConfig.objects.get(series_id=series_id)
                cache_keys.append(f"{cls.CACHE_KEY_PREFIX}category_{config.category}")
                cache_keys.append(f"{cls.CACHE_KEY_PREFIX}frequency_{config.fetch_frequency}")
            except FredUsIndicatorConfig.DoesNotExist:
                pass

        cache.delete_many(cache_keys)
        logger.info(f"Cleared {len(cache_keys)} FRED US cache keys")

    @classmethod
    def clear_all_cache(cls):
        """清除所有相关缓存"""
        try:
            all_series = FredUsIndicatorConfig.objects.values_list("series_id", flat=True)
            all_categories = FredUsIndicatorConfig.objects.values_list(
                "category", flat=True
            ).distinct()
            all_frequencies = FredUsIndicatorConfig.objects.values_list(
                "fetch_frequency", flat=True
            ).distinct()

            cache_keys = [
                f"{cls.CACHE_KEY_PREFIX}all_active",
                f"{cls.CACHE_KEY_PREFIX}auto_fetch",
            ]

            # 添加所有指标的缓存键
            for series_id in all_series:
                cache_keys.append(f"{cls.CACHE_KEY_PREFIX}indicator_{series_id}")

            # 添加所有分类的缓存键
            for category in all_categories:
                cache_keys.append(f"{cls.CACHE_KEY_PREFIX}category_{category}")

            # 添加所有频率的缓存键
            for frequency in all_frequencies:
                cache_keys.append(f"{cls.CACHE_KEY_PREFIX}frequency_{frequency}")

            cache.delete_many(cache_keys)
            logger.info(f"Cleared all {len(cache_keys)} FRED US config cache keys")

        except Exception:
            logger.exception("Error clearing all FRED US cache")

    @classmethod
    def _get_fallback_config(cls):
        """获取备用配置（当数据库访问失败时）"""
        return {
            # 核心货币政策指标
            "FEDFUNDS": {
                "name": "Federal Funds Effective Rate",
                "description": "The federal funds rate is the interest rate at which depository institutions trade federal funds",
                "indicator_type": "monetary_policy",
                "units": "Percent",
                "frequency": "Monthly",
                "category": "interest_rates",
                "api_endpoint": "fed-funds",
                "fallback_value": 4.33,
                "priority": 1,
            },
            "MORTGAGE30US": {
                "name": "30-Year Fixed Rate Mortgage Average in the United States",
                "description": "30-year fixed rate mortgage average in the United States",
                "indicator_type": "mortgage_rates",
                "units": "Percent",
                "frequency": "Weekly",
                "category": "interest_rates",
                "api_endpoint": "mortgage-30y",
                "fallback_value": 6.75,
                "priority": 2,
            },
            "DGS10": {
                "name": "10-Year Treasury Constant Maturity Rate",
                "description": "10-year treasury constant maturity rate",
                "indicator_type": "treasury_rates",
                "units": "Percent",
                "frequency": "Daily",
                "category": "interest_rates",
                "api_endpoint": "treasury-10y",
                "fallback_value": 4.25,
                "priority": 3,
            },
            "DGS2": {
                "name": "2-Year Treasury Constant Maturity Rate",
                "description": "2-year treasury constant maturity rate",
                "indicator_type": "treasury_rates",
                "units": "Percent",
                "frequency": "Daily",
                "category": "interest_rates",
                "api_endpoint": "treasury-2y",
                "fallback_value": 4.70,
                "priority": 4,
            },
            "TB3MS": {
                "name": "3-Month Treasury Bill",
                "description": "3-month treasury bill secondary market rate",
                "indicator_type": "treasury_rates",
                "units": "Percent",
                "frequency": "Monthly",
                "category": "interest_rates",
                "api_endpoint": "treasury-3m",
                "fallback_value": 4.50,
                "priority": 5,
            },
            "PCEPI": {
                "name": "Personal Consumption Expenditures Price Index",
                "description": "Personal consumption expenditures price index",
                "indicator_type": "inflation",
                "units": "Index 2012=100",
                "frequency": "Monthly",
                "category": "inflation",
                "api_endpoint": "pce-price-index",
                "fallback_value": 107.2,
                "priority": 6,
            },
            "CPIAUCSL": {
                "name": "Consumer Price Index for All Urban Consumers",
                "description": "Consumer price index for all urban consumers: all items in U.S. city average",
                "indicator_type": "inflation",
                "units": "Index 1982-84=100",
                "frequency": "Monthly",
                "category": "inflation",
                "api_endpoint": "cpi",
                "fallback_value": 320.58,
                "priority": 7,
            },
            "GFDEGDQ188S": {
                "name": "Federal Debt: Total Public Debt as Percent of Gross Domestic Product",
                "description": "Federal debt: total public debt as percent of gross domestic product",
                "indicator_type": "fiscal_policy",
                "units": "Percent of GDP",
                "frequency": "Quarterly",
                "category": "debt",
                "api_endpoint": "debt-to-gdp",
                "fallback_value": 120.81,
                "priority": 8,
            },
            # 核心经济指标
            "M1SL": {
                "name": "M1 Money Stock",
                "description": "M1 money stock",
                "indicator_type": "monetary_aggregates",
                "units": "Billions of Dollars",
                "frequency": "Monthly",
                "category": "money_supply",
                "api_endpoint": "m1",
                "fallback_value": 18668.0,
                "priority": 9,
            },
            "M2SL": {
                "name": "M2 Money Stock",
                "description": "M2 money stock",
                "indicator_type": "monetary_aggregates",
                "units": "Billions of Dollars",
                "frequency": "Monthly",
                "category": "money_supply",
                "api_endpoint": "m2",
                "fallback_value": 21000.0,
                "priority": 10,
            },
            "UNRATE": {
                "name": "Unemployment Rate",
                "description": "Civilian unemployment rate",
                "indicator_type": "employment",
                "units": "Percent",
                "frequency": "Monthly",
                "category": "labor_market",
                "api_endpoint": "unemployment",
                "fallback_value": 3.7,
                "priority": 11,
            },
            "HOUST": {
                "name": "Housing Starts",
                "description": "New privately-owned housing units started",
                "indicator_type": "housing",
                "units": "Thousands of Units",
                "frequency": "Monthly",
                "category": "housing",
                "api_endpoint": "housing",
                "fallback_value": 1450.0,
                "priority": 12,
            },
        }


# 兼容性函数，保持与旧代码的接口一致
def get_fred_us_indicators_config():
    """兼容性函数 - 返回所有指标配置"""
    return DynamicFredUsConfigManager.get_all_indicators()


def get_fred_us_indicator_by_series_id(series_id):
    """兼容性函数 - 根据series_id获取指标配置"""
    return DynamicFredUsConfigManager.get_indicator_config(series_id)
