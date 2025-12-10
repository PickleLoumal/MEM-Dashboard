"""
FRED US 自动数据获取器
基于BEA系统模式的数据库驱动配置系统
"""

import logging
import os
import time
from typing import Any

from django.conf import settings
from django.utils import timezone

from .data_fetcher import UsFredDataFetcher
from .dynamic_config import DynamicFredUsConfigManager
from .models import FredUsIndicatorConfig

logger = logging.getLogger(__name__)


class FredUsAutoFetcher:
    """美国FRED指标自动获取器 - 基于配置的自动化数据抓取"""

    def __init__(self, api_key: str | None = None):
        self.config_manager = DynamicFredUsConfigManager()
        self.fetch_delay = getattr(settings, "FRED_US_FETCH_DELAY_SECONDS", 1)
        self.api_key = (
            api_key or getattr(settings, "FRED_API_KEY", None) or os.environ.get("FRED_API_KEY")
        )

    def should_fetch_indicator(self, config: FredUsIndicatorConfig) -> bool:
        """判断指标是否需要获取"""
        if not config.auto_fetch or not config.is_active:
            return False

        if config.fetch_status == "disabled":
            return False

        # 检查上次获取时间
        if not config.last_fetch_time:
            return True

        now = timezone.now()
        time_diff = now - config.last_fetch_time

        # 根据频率判断是否需要更新
        frequency_hours = {
            "hourly": 1,
            "daily": 24,
            "weekly": 168,  # 7 * 24
            "monthly": 720,  # 30 * 24
        }

        required_hours = frequency_hours.get(config.fetch_frequency, 24)
        return time_diff.total_seconds() >= required_hours * 3600

    def fetch_single_indicator(self, config: FredUsIndicatorConfig) -> bool:
        """获取单个指标数据"""
        try:
            logger.info(f"开始获取指标数据: {config.series_id}")

            # 创建数据获取器实例，传递API密钥
            fetcher = UsFredDataFetcher(api_key=self.api_key)

            # 获取系列信息
            series_info = fetcher.get_series_info(config.series_id)
            if series_info:
                fetcher.save_series_info(config.series_id, series_info)

            # 获取观测数据 (默认获取最近100条记录)
            limit = config.additional_config.get("data_limit", 100)
            observations = fetcher.get_series_observations(config.series_id, limit=limit)
            if observations:
                saved_count = fetcher.save_observations(config.series_id, observations)

                # 更新获取状态
                config.update_fetch_status("success")
                config.additional_config["last_success_count"] = saved_count
                config.additional_config["last_error"] = None
                config.save()

                logger.info(f"成功获取指标数据: {config.series_id}, 保存了 {saved_count} 条记录")
                return True
            # 处理获取失败
            config.update_fetch_status("failed", "No observations data received")
            logger.error(f"获取指标数据失败: {config.series_id} - 未获取到观测数据")
            return False

        except Exception as e:
            logger.exception("获取指标数据异常: {config.series_id}")
            config.update_fetch_status("failed", str(e))
            return False

    def fetch_by_frequency(self, frequency: str = "daily") -> dict[str, Any]:
        """按频率自动获取数据"""
        logger.info(f"开始执行 {frequency} 频率的数据获取")

        # 获取指定频率的配置
        configs = self.config_manager.get_configs_by_frequency(frequency)
        if not configs:
            logger.info(f"没有找到 {frequency} 频率的自动获取配置")
            return {
                "status": "no_configs",
                "frequency": frequency,
                "message": f"No {frequency} configs found",
            }

        results = []
        processed = 0

        for series_id, _config_dict in configs.items():
            # 获取数据库中的配置对象
            try:
                config = FredUsIndicatorConfig.objects.get(series_id=series_id)
                # 检查是否需要抓取
                if self.should_fetch_indicator(config):
                    result = self.fetch_single_indicator(config)
                    results.append(result)
                    processed += 1

                    # 添加延迟避免API限制
                    time.sleep(self.fetch_delay)
                else:
                    logger.info(f"跳过 {series_id}: 尚未到抓取时间")
            except FredUsIndicatorConfig.DoesNotExist:
                logger.warning(f"配置不存在: {series_id}")
                continue

        summary = {
            "status": "completed",
            "frequency": frequency,
            "total_indicators": len(configs),
            "processed": processed,
            "successful": sum(1 for r in results if r),
            "failed": sum(1 for r in results if not r),
            "timestamp": timezone.now().isoformat(),
        }

        logger.info(f"{frequency} 数据获取完成: 处理了 {processed}/{len(configs)} 个指标")
        return summary

    def fetch_all_auto_indicators(self) -> dict[str, Any]:
        """获取所有自动抓取指标数据"""
        logger.info("开始获取所有FRED US自动指标")

        # 直接从数据库获取所有自动抓取配置
        configs = FredUsIndicatorConfig.get_auto_fetch_configs()
        if not configs:
            logger.info("没有找到自动抓取配置")
            return {"status": "no_configs", "message": "No auto-fetch configs found"}

        results = []
        processed = 0

        for config in configs:
            if self.should_fetch_indicator(config):
                result = self.fetch_single_indicator(config)
                results.append(result)
                processed += 1

                # 添加延迟
                time.sleep(self.fetch_delay)
            else:
                logger.info(f"跳过 {config.series_id}: 尚未到抓取时间")

        summary = {
            "status": "completed",
            "total_indicators": len(configs),
            "processed": processed,
            "successful": sum(1 for r in results if r),
            "failed": sum(1 for r in results if not r),
            "timestamp": timezone.now().isoformat(),
        }

        logger.info(f"所有自动指标获取完成: 处理了 {processed}/{len(configs)} 个指标")
        return summary

    def fetch_by_category(self, category: str) -> dict[str, Any]:
        """按类别获取指标数据"""
        logger.info(f"开始获取 {category} 类别的指标数据")

        # 直接从数据库获取分类配置
        configs = FredUsIndicatorConfig.get_configs_by_category(category)
        if not configs:
            logger.info(f"没有找到 {category} 类别的配置")
            return {
                "status": "no_configs",
                "category": category,
                "message": f"No configs found for category: {category}",
            }

        results = []
        processed = 0

        for config in configs:
            if config.auto_fetch and self.should_fetch_indicator(config):
                result = self.fetch_single_indicator(config)
                results.append(result)
                processed += 1

                # 添加延迟
                time.sleep(self.fetch_delay)
            else:
                logger.info(f"跳过 {config.series_id}: 非自动抓取或尚未到抓取时间")

        summary = {
            "status": "completed",
            "category": category,
            "total_indicators": len(configs),
            "processed": processed,
            "successful": sum(1 for r in results if r),
            "failed": sum(1 for r in results if not r),
            "timestamp": timezone.now().isoformat(),
        }

        logger.info(f"{category} 类别数据获取完成: 处理了 {processed}/{len(configs)} 个指标")
        return summary

    def fetch_specific_indicators(self, series_ids: list[str]) -> dict[str, Any]:
        """获取指定的指标数据"""
        logger.info(f"开始获取指定指标数据: {series_ids}")

        results = {}

        for series_id in series_ids:
            try:
                config = FredUsIndicatorConfig.objects.get(series_id=series_id, is_active=True)
                result = self.fetch_single_indicator(config)
                results[series_id] = {"success": result, "timestamp": timezone.now().isoformat()}

                # 添加延迟
                time.sleep(self.fetch_delay)

            except FredUsIndicatorConfig.DoesNotExist:
                results[series_id] = {
                    "success": False,
                    "error": "Configuration not found or inactive",
                }

            except Exception as e:
                logger.exception("获取指标失败 {series_id}")
                results[series_id] = {"success": False, "error": str(e)}

        summary = {
            "status": "completed",
            "total_requested": len(series_ids),
            "total_processed": len(
                [
                    r
                    for r in results.values()
                    if "error" not in r or r["error"] != "Configuration not found or inactive"
                ]
            ),
            "successful": len([r for r in results.values() if r.get("success")]),
            "failed": len([r for r in results.values() if not r.get("success")]),
            "results": results,
            "timestamp": timezone.now().isoformat(),
        }

        logger.info(
            f"指定指标数据获取完成: {summary['successful']}/{summary['total_requested']} 成功"
        )
        return summary

    def get_fetch_status(self) -> dict[str, Any]:
        """获取抓取状态统计"""
        try:
            # 获取统计信息
            stats = self.config_manager.get_statistics()

            # 获取最近的抓取状态
            recent_configs = FredUsIndicatorConfig.objects.filter(
                is_active=True, auto_fetch=True
            ).order_by("-last_fetch_time")[:10]

            recent_fetches = []
            for config in recent_configs:
                recent_fetches.append(
                    {
                        "series_id": config.series_id,
                        "name": config.name,
                        "fetch_status": config.fetch_status,
                        "last_fetch_time": config.last_fetch_time.isoformat()
                        if config.last_fetch_time
                        else None,
                        "fetch_frequency": config.fetch_frequency,
                        "last_error": config.additional_config.get("last_error"),
                    }
                )

            # 统计各状态的数量
            status_counts = {}
            for status_choice in ["success", "failed", "pending", "disabled"]:
                count = FredUsIndicatorConfig.objects.filter(
                    is_active=True, auto_fetch=True, fetch_status=status_choice
                ).count()
                status_counts[status_choice] = count

            return {
                "statistics": stats,
                "recent_fetches": recent_fetches,
                "status_counts": status_counts,
                "last_updated": timezone.now().isoformat(),
            }

        except Exception as e:
            logger.exception("获取抓取状态失败")
            return {"error": str(e), "last_updated": timezone.now().isoformat()}


# 工厂函数
def get_fred_us_auto_fetcher(api_key: str | None = None):
    """获取美国FRED自动获取器实例"""
    return FredUsAutoFetcher(api_key=api_key)
