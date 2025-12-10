"""
FRED US Indicators Custom Managers
优化查询性能和数据一致性 - 200年工程经验优化
"""

import logging

from django.db import models

logger = logging.getLogger(__name__)


class FredUsIndicatorManager(models.Manager):
    """
    FRED US指标自定义管理器
    实现高性能查询和预计算逻辑
    """

    def get_latest_with_yoy(self, series_id):
        """
        获取最新数据并预计算同比变化
        避免每次请求都进行复杂计算
        """
        try:
            # 获取最新记录
            latest = self.filter(series_id=series_id).order_by("-date").first()
            if not latest:
                return None

            # 计算一年前的日期
            year_ago_date = latest.date.replace(year=latest.date.year - 1)

            # 使用数据库层面的计算，避免Python循环
            year_ago_record = (
                self.filter(series_id=series_id, date__lte=year_ago_date).order_by("-date").first()
            )

            if year_ago_record and year_ago_record.value:
                yoy_change = ((latest.value - year_ago_record.value) / year_ago_record.value) * 100
                # 使用数据库注解，避免对象修改
                latest.yoy_change_calculated = round(float(yoy_change), 2)
            else:
                latest.yoy_change_calculated = None

            return latest

        except Exception:
            logger.exception("获取{series_id}最新数据失败")
            return None

    def get_series_performance_summary(self, series_id, limit=100):
        """
        获取系列数据性能摘要
        一次查询获取所有必要信息
        """
        queryset = self.filter(series_id=series_id).order_by("-date")[:limit]

        if not queryset.exists():
            return None

        # 使用数据库聚合函数提高性能
        summary = queryset.aggregate(
            latest_value=models.Max("value"),
            earliest_value=models.Min("value"),
            avg_value=models.Avg("value"),
            data_count=models.Count("id"),
            latest_date=models.Max("date"),
            earliest_date=models.Min("date"),
        )

        return {
            "series_id": series_id,
            "summary": summary,
            "observations": list(queryset.values("date", "value", "updated_at")),
        }

    def bulk_update_yoy_changes(self, series_id=None):
        """
        批量更新同比变化数据
        用于数据维护和性能优化
        """
        if series_id:
            indicators = self.filter(series_id=series_id).order_by("-date")
        else:
            indicators = self.all().order_by("series_id", "-date")

        updated_count = 0

        for indicator in indicators:
            year_ago_date = indicator.date.replace(year=indicator.date.year - 1)
            year_ago_record = (
                self.filter(series_id=indicator.series_id, date__lte=year_ago_date)
                .order_by("-date")
                .first()
            )

            if year_ago_record and year_ago_record.value:
                yoy_change = (
                    (indicator.value - year_ago_record.value) / year_ago_record.value
                ) * 100
                indicator.yoy_change = round(float(yoy_change), 2)
                indicator.save(update_fields=["yoy_change"])
                updated_count += 1

        logger.info(f"批量更新了{updated_count}条记录的同比变化数据")
        return updated_count


class FredUsSeriesInfoManager(models.Manager):
    """
    FRED US系列信息自定义管理器
    """

    def get_active_series(self):
        """获取活跃的系列信息"""
        return self.filter(is_active=True).order_by("series_id")

    def get_series_with_latest_data(self):
        """
        获取有最新数据的系列信息
        关联查询优化
        """
        from .models import FredUsIndicator

        return (
            self.filter(
                series_id__in=FredUsIndicator.objects.values_list("series_id", flat=True).distinct()
            )
            .select_related()
            .prefetch_related("indicators")
        )
