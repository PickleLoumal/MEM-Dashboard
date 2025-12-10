"""
通用动态配置管理器基类

为 FRED US, BEA, FRED JP 等提供统一的配置管理接口。
子类只需定义 CACHE_KEY_PREFIX, config_model 和 _get_fallback_config()。
"""

import logging
from abc import ABC, abstractmethod

from django.core.cache import cache
from django.db import transaction

logger = logging.getLogger(__name__)


class BaseDynamicConfigManager(ABC):
    """
    动态配置管理器基类 - 数据库驱动的配置系统

    子类需要定义:
    - CACHE_KEY_PREFIX: 缓存键前缀
    - config_model: 对应的 Config Model 类
    - service_name: 服务名称（用于日志）
    - _get_fallback_config(): 备用配置方法
    """

    CACHE_KEY_PREFIX = "base_config_"
    CACHE_TIMEOUT = 300  # 5分钟缓存

    @classmethod
    @property
    @abstractmethod
    def config_model(cls):
        """子类必须返回对应的 Config Model"""

    @classmethod
    @property
    def service_name(cls) -> str:
        """服务名称，用于日志。子类可覆盖"""
        return "Base"

    @classmethod
    def get_all_indicators(cls):
        """获取所有激活的指标配置（缓存版本）"""
        cache_key = f"{cls.CACHE_KEY_PREFIX}all_active"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return cached_data

        try:
            configs = cls.config_model.get_active_configs()
            result = {}

            for config in configs:
                result[config.series_id] = config.to_config_dict()

            cache.set(cache_key, result, cls.CACHE_TIMEOUT)
            logger.info(f"Loaded {len(result)} {cls.service_name} indicator configs from database")
            return result

        except Exception:
            logger.exception("Error loading {cls.service_name} configs from database")
            return cls._get_fallback_config()

    @classmethod
    def get_auto_fetch_indicators(cls):
        """获取需要自动抓取的指标配置"""
        cache_key = f"{cls.CACHE_KEY_PREFIX}auto_fetch"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return cached_data

        try:
            configs = cls.config_model.get_auto_fetch_configs()
            result = {}

            for config in configs:
                result[config.series_id] = config.to_config_dict()

            cache.set(cache_key, result, cls.CACHE_TIMEOUT)
            return result

        except Exception:
            logger.exception("Error loading {cls.service_name} auto-fetch configs")
            return {}

    @classmethod
    def get_indicator_config(cls, series_id: str):
        """获取单个指标配置"""
        cache_key = f"{cls.CACHE_KEY_PREFIX}indicator_{series_id}"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return cached_data

        try:
            config = cls.config_model.objects.filter(series_id=series_id, is_active=True).first()

            if config:
                result = config.to_config_dict()
                cache.set(cache_key, result, cls.CACHE_TIMEOUT)
                return result

            return None

        except Exception:
            logger.exception("Error loading {cls.service_name} config for {series_id}")
            return None

    @classmethod
    def get_configs_by_category(cls, category: str):
        """按类别获取指标配置"""
        cache_key = f"{cls.CACHE_KEY_PREFIX}category_{category}"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return cached_data

        try:
            configs = cls.config_model.get_configs_by_category(category)
            result = {}

            for config in configs:
                result[config.series_id] = config.to_config_dict()

            cache.set(cache_key, result, cls.CACHE_TIMEOUT)
            return result

        except Exception:
            logger.exception("Error loading {cls.service_name} configs for category {category}")
            return {}

    @classmethod
    def create_indicator(cls, config_data: dict):
        """创建新的指标配置"""
        try:
            with transaction.atomic():
                config = cls.config_model.objects.create(**config_data)
                cls._clear_related_cache()
                logger.info(f"Created new {cls.service_name} indicator config: {config.series_id}")
                return config

        except Exception:
            logger.exception("Error creating {cls.service_name} indicator config")
            raise

    @classmethod
    def update_indicator(cls, series_id: str, config_data: dict):
        """更新指标配置"""
        try:
            with transaction.atomic():
                config = cls.config_model.objects.get(series_id=series_id)

                for key, value in config_data.items():
                    setattr(config, key, value)

                config.save()
                cls._clear_related_cache(series_id)
                logger.info(f"Updated {cls.service_name} indicator config: {series_id}")
                return config

        except cls.config_model.DoesNotExist:
            logger.exception(f"{cls.service_name} indicator config not found: {series_id}")
            return None
        except Exception:
            logger.exception("Error updating {cls.service_name} indicator config {series_id}")
            raise

    @classmethod
    def activate_indicator(cls, series_id: str) -> bool:
        """激活指标"""
        try:
            config = cls.config_model.objects.get(series_id=series_id)
            config.activate()
            cls._clear_related_cache(series_id)
            logger.info(f"Activated {cls.service_name} indicator: {series_id}")
            return True

        except cls.config_model.DoesNotExist:
            logger.exception(f"{cls.service_name} indicator config not found: {series_id}")
            return False

    @classmethod
    def deactivate_indicator(cls, series_id: str) -> bool:
        """禁用指标"""
        try:
            config = cls.config_model.objects.get(series_id=series_id)
            config.deactivate()
            cls._clear_related_cache(series_id)
            logger.info(f"Deactivated {cls.service_name} indicator: {series_id}")
            return True

        except cls.config_model.DoesNotExist:
            logger.exception(f"{cls.service_name} indicator config not found: {series_id}")
            return False

    @classmethod
    def get_statistics(cls) -> dict:
        """获取配置统计信息"""
        try:
            total = cls.config_model.objects.count()
            active = cls.config_model.objects.filter(is_active=True).count()
            auto_fetch = cls.config_model.objects.filter(is_active=True, auto_fetch=True).count()

            categories = (
                cls.config_model.objects.filter(is_active=True)
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
            logger.exception("Error getting {cls.service_name} statistics")
            return {}

    @classmethod
    def _clear_related_cache(cls, series_id: str | None = None):
        """清除相关缓存"""
        cache_keys = [
            f"{cls.CACHE_KEY_PREFIX}all_active",
            f"{cls.CACHE_KEY_PREFIX}auto_fetch",
        ]

        if series_id:
            cache_keys.append(f"{cls.CACHE_KEY_PREFIX}indicator_{series_id}")

            # 清除该指标所属类别的缓存
            try:
                config = cls.config_model.objects.get(series_id=series_id)
                cache_keys.append(f"{cls.CACHE_KEY_PREFIX}category_{config.category}")
            except Exception:
                pass

        cache.delete_many(cache_keys)
        logger.debug(f"Cleared {len(cache_keys)} {cls.service_name} cache keys")

    @classmethod
    def clear_all_cache(cls):
        """清除所有相关缓存"""
        try:
            all_series = cls.config_model.objects.values_list("series_id", flat=True)
            all_categories = cls.config_model.objects.values_list("category", flat=True).distinct()

            cache_keys = [
                f"{cls.CACHE_KEY_PREFIX}all_active",
                f"{cls.CACHE_KEY_PREFIX}auto_fetch",
            ]

            for series_id in all_series:
                cache_keys.append(f"{cls.CACHE_KEY_PREFIX}indicator_{series_id}")

            for category in all_categories:
                cache_keys.append(f"{cls.CACHE_KEY_PREFIX}category_{category}")

            cache.delete_many(cache_keys)
            logger.info(f"Cleared all {len(cache_keys)} {cls.service_name} config cache keys")

        except Exception:
            logger.exception("Error clearing all {cls.service_name} cache")

    @classmethod
    @abstractmethod
    def _get_fallback_config(cls) -> dict:
        """
        获取备用配置（当数据库访问失败时）
        子类必须实现此方法
        """


__all__ = ["BaseDynamicConfigManager"]
