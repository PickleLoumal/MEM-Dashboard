"""
BEA动态配置管理器
从数据库驱动的配置系统，替代硬编码的配置文件
"""

import logging

from django.core.cache import cache
from django.db import transaction

from .models import BeaIndicatorConfig

logger = logging.getLogger(__name__)


class DynamicBeaConfigManager:
    """BEA动态配置管理器 - 数据库驱动的配置系统"""

    CACHE_KEY_PREFIX = "bea_config_"
    CACHE_TIMEOUT = 300  # 5分钟缓存

    @classmethod
    def get_all_indicators(cls):
        """获取所有激活的指标配置（缓存版本）"""
        cache_key = f"{cls.CACHE_KEY_PREFIX}all_active"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return cached_data

        try:
            configs = BeaIndicatorConfig.get_active_configs()
            result = {}

            for config in configs:
                result[config.series_id] = config.to_config_dict()

            cache.set(cache_key, result, cls.CACHE_TIMEOUT)
            logger.info(f"Loaded {len(result)} BEA indicator configs from database")
            return result

        except Exception:
            logger.exception("Error loading BEA configs from database")
            return cls._get_fallback_config()

    @classmethod
    def get_auto_fetch_indicators(cls):
        """获取需要自动抓取的指标配置"""
        cache_key = f"{cls.CACHE_KEY_PREFIX}auto_fetch"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return cached_data

        try:
            configs = BeaIndicatorConfig.get_auto_fetch_configs()
            result = {}

            for config in configs:
                result[config.series_id] = config.to_config_dict()

            cache.set(cache_key, result, cls.CACHE_TIMEOUT)
            return result

        except Exception:
            logger.exception("Error loading auto-fetch configs")
            return cls._get_fallback_config()

    @classmethod
    def get_indicator_config(cls, series_id):
        """获取单个指标配置"""
        cache_key = f"{cls.CACHE_KEY_PREFIX}indicator_{series_id}"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return cached_data

        try:
            config = BeaIndicatorConfig.objects.filter(series_id=series_id, is_active=True).first()

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
            configs = BeaIndicatorConfig.get_configs_by_category(category)
            result = {}

            for config in configs:
                result[config.series_id] = config.to_config_dict()

            cache.set(cache_key, result, cls.CACHE_TIMEOUT)
            return result

        except Exception:
            logger.exception("Error loading configs for category {category}")
            return {}

    @classmethod
    def create_indicator(cls, config_data):
        """创建新的指标配置"""
        try:
            with transaction.atomic():
                config = BeaIndicatorConfig.objects.create(**config_data)
                cls._clear_related_cache()
                logger.info(f"Created new indicator config: {config.series_id}")
                return config

        except Exception:
            logger.exception("Error creating indicator config")
            raise

    @classmethod
    def update_indicator(cls, series_id, config_data):
        """更新指标配置"""
        try:
            with transaction.atomic():
                config = BeaIndicatorConfig.objects.get(series_id=series_id)

                for key, value in config_data.items():
                    setattr(config, key, value)

                config.save()
                cls._clear_related_cache(series_id)
                logger.info(f"Updated indicator config: {series_id}")
                return config

        except BeaIndicatorConfig.DoesNotExist:
            logger.exception(f"Indicator config not found: {series_id}")
            return None
        except Exception:
            logger.exception("Error updating indicator config {series_id}")
            raise

    @classmethod
    def activate_indicator(cls, series_id):
        """激活指标"""
        try:
            config = BeaIndicatorConfig.objects.get(series_id=series_id)
            config.activate()
            cls._clear_related_cache(series_id)
            logger.info(f"Activated indicator: {series_id}")
            return True

        except BeaIndicatorConfig.DoesNotExist:
            logger.exception(f"Indicator config not found: {series_id}")
            return False

    @classmethod
    def deactivate_indicator(cls, series_id):
        """禁用指标"""
        try:
            config = BeaIndicatorConfig.objects.get(series_id=series_id)
            config.deactivate()
            cls._clear_related_cache(series_id)
            logger.info(f"Deactivated indicator: {series_id}")
            return True

        except BeaIndicatorConfig.DoesNotExist:
            logger.exception(f"Indicator config not found: {series_id}")
            return False

    @classmethod
    def get_statistics(cls):
        """获取配置统计信息"""
        try:
            total = BeaIndicatorConfig.objects.count()
            active = BeaIndicatorConfig.objects.filter(is_active=True).count()
            auto_fetch = BeaIndicatorConfig.objects.filter(is_active=True, auto_fetch=True).count()

            categories = (
                BeaIndicatorConfig.objects.filter(is_active=True)
                .values_list("category", flat=True)
                .distinct()
            )

            return {
                "total_indicators": total,
                "active_indicators": active,
                "auto_fetch_indicators": auto_fetch,
                "categories": list(categories),
                "category_count": len(categories),
            }

        except Exception:
            logger.exception("Error getting statistics")
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

            # 清除该指标所属类别的缓存
            try:
                config = BeaIndicatorConfig.objects.get(series_id=series_id)
                cache_keys.append(f"{cls.CACHE_KEY_PREFIX}category_{config.category}")
            except BeaIndicatorConfig.DoesNotExist:
                pass

        cache.delete_many(cache_keys)
        logger.info(f"Cleared {len(cache_keys)} cache keys")

    @classmethod
    def clear_all_cache(cls):
        """清除所有相关缓存"""
        # 获取所有可能的缓存键
        try:
            all_series = BeaIndicatorConfig.objects.values_list("series_id", flat=True)
            all_categories = BeaIndicatorConfig.objects.values_list(
                "category", flat=True
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

            cache.delete_many(cache_keys)
            logger.info(f"Cleared all {len(cache_keys)} BEA config cache keys")

        except Exception:
            logger.exception("Error clearing all cache")

    @classmethod
    def _get_fallback_config(cls):
        """获取备用配置（当数据库访问失败时）"""
        return {
            # 原有的9个消费支出指标
            "MOTOR_VEHICLES": {
                "name": "Motor Vehicles and Parts",
                "description": "Personal consumption expenditures on motor vehicles and parts",
                "table": "T20405",
                "line_description": "Motor vehicles and parts",
                "line_number": 4,
                "units": "Millions of dollars",
                "frequency": "Q",
                "years": "2022,2023,2024,2025",
                "category": "consumer_spending",
                "fallback_value": 750144.0,
                "api_endpoint": "motor_vehicles",
                "priority": 1,
            },
            "RECREATIONAL_GOODS": {
                "name": "Recreational Goods and Vehicles",
                "description": "Personal consumption expenditures on recreational goods and vehicles",
                "table": "T20405",
                "line_description": "Recreational goods and vehicles",
                "line_number": 5,
                "units": "Millions of dollars",
                "frequency": "Q",
                "years": "2022,2023,2024,2025",
                "category": "consumer_spending",
                "fallback_value": 677100.0,
                "api_endpoint": "recreational_goods",
                "priority": 2,
            },
            # 新增的主要经济指标
            "PCE_TOTAL": {
                "name": "Personal Consumption Expenditures",
                "description": "Total personal consumption expenditures",
                "table": "T20405",
                "line_description": "Personal consumption expenditures",
                "line_number": 1,
                "units": "Millions of dollars",
                "frequency": "Q",
                "years": "2022,2023,2024,2025",
                "category": "consumer_spending",
                "fallback_value": 17800000.0,
                "api_endpoint": "pce_total",
                "priority": 10,
            },
            "GDP": {
                "name": "Gross Domestic Product",
                "description": "Total value of goods and services produced",
                "table": "T10101",
                "line_description": "Gross domestic product",
                "line_number": 1,
                "units": "Millions of dollars",
                "frequency": "Q",
                "years": "2022,2023,2024,2025",
                "category": "gdp",
                "fallback_value": 26900000.0,
                "api_endpoint": "gdp_total",
                "priority": 14,
            },
            "GDP_REAL": {
                "name": "Real Gross Domestic Product",
                "description": "Inflation-adjusted gross domestic product",
                "table": "T10106",
                "line_description": "Gross domestic product",
                "line_number": 1,
                "units": "Millions of chained 2017 dollars",
                "frequency": "Q",
                "years": "2022,2023,2024,2025",
                "category": "gdp",
                "fallback_value": 22996000.0,
                "api_endpoint": "gdp_real",
                "priority": 15,
            },
        }


# 兼容性函数，保持与旧代码的接口一致
def get_bea_indicators_config():
    """兼容性函数 - 返回所有指标配置"""
    return DynamicBeaConfigManager.get_all_indicators()


def get_indicator_by_series_id(series_id):
    """兼容性函数 - 根据series_id获取指标配置"""
    return DynamicBeaConfigManager.get_indicator_config(series_id)
