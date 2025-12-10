"""
Django Models for US FRED Economic Indicators
美国FRED经济指标数据模型 - 分离架构实现
"""

from django.db import models
from django.utils import timezone

from fred_common.base_models import BaseFredModel, BaseFredSeriesInfo


class FredUsSeriesInfo(BaseFredSeriesInfo):
    """美国FRED系列信息表 - 基于通用基类"""

    class Meta:
        db_table = "fred_us_series_info"  # 使用独立的美国表
        verbose_name = "US FRED Series Info"
        verbose_name_plural = "US FRED Series Info"

    def __str__(self):
        return f"US-{self.series_id}: {self.title}"


class FredUsIndicator(BaseFredModel):
    """美国FRED指标数据表 - 基于通用基类"""

    class Meta:
        db_table = "fred_us_indicators"  # 使用独立的美国表
        unique_together = ["series_id", "date"]
        ordering = ["-date"]
        verbose_name = "US FRED Indicator"
        verbose_name_plural = "US FRED Indicators"
        indexes = [
            models.Index(fields=["series_id", "-date"], name="idx_us_series_date"),
            models.Index(fields=["indicator_type", "-date"], name="idx_us_type_date"),
            models.Index(fields=["series_id", "-updated_at"], name="idx_us_series_updated"),
        ]

    def __str__(self):
        return f"US-{self.series_id} - {self.date}: {self.value}"

    @property
    def country(self):
        """返回国家标识"""
        return "US"


class FredUsIndicatorConfig(models.Model):
    """美国FRED指标动态配置模型 - 数据库驱动的指标管理"""

    series_id = models.CharField(max_length=50, unique=True, help_text="FRED系列ID")
    name = models.CharField(max_length=200, help_text="指标名称")
    description = models.TextField(blank=True, help_text="详细描述")
    indicator_type = models.CharField(max_length=50, help_text="指标类型分类")
    units = models.CharField(max_length=100, blank=True, help_text="数据单位")
    frequency = models.CharField(max_length=20, default="Monthly", help_text="数据频率")
    category = models.CharField(max_length=100, default="economic", help_text="指标分类")

    # API配置
    api_endpoint = models.CharField(max_length=100, unique=True, help_text="API端点路径")
    fallback_value = models.DecimalField(
        max_digits=15, decimal_places=4, null=True, blank=True, help_text="备用数值"
    )

    # 系统配置
    priority = models.IntegerField(default=999, help_text="处理优先级")
    is_active = models.BooleanField(default=True, help_text="是否启用")
    auto_fetch = models.BooleanField(default=True, help_text="是否自动抓取")
    fetch_frequency = models.CharField(
        max_length=20,
        default="daily",
        choices=[
            ("hourly", "Hourly"),
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
        ],
        help_text="自动抓取频率",
    )

    # 元数据字段
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, default="system")
    updated_by = models.CharField(max_length=100, default="system")

    # 扩展配置
    additional_config = models.JSONField(default=dict, blank=True, help_text="额外JSON配置")
    last_fetch_time = models.DateTimeField(null=True, blank=True, help_text="最后抓取时间")
    fetch_status = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "Pending"),
            ("success", "Success"),
            ("failed", "Failed"),
            ("disabled", "Disabled"),
        ],
        help_text="抓取状态",
    )

    class Meta:
        managed = True  # 启用数据库管理以创建配置表
        db_table = "fred_us_indicator_configs"
        ordering = ["priority", "series_id"]
        verbose_name = "US FRED Indicator Configuration"
        verbose_name_plural = "US FRED Indicator Configurations"

    def __str__(self):
        return f"US-{self.series_id}: {self.name}"

    def to_config_dict(self):
        """转换为配置字典格式，保持与旧代码的兼容性"""
        return {
            "name": self.name,
            "description": self.description,
            "indicator_type": self.indicator_type,
            "units": self.units,
            "frequency": self.frequency,
            "category": self.category,
            "api_endpoint": self.api_endpoint,
            "fallback_value": float(self.fallback_value) if self.fallback_value else None,
            "priority": self.priority,
            "fetch_frequency": self.fetch_frequency,
            "last_fetch_time": self.last_fetch_time.isoformat() if self.last_fetch_time else None,
            "fetch_status": self.fetch_status,
        }

    @classmethod
    def get_active_configs(cls):
        """获取所有激活的指标配置"""
        return cls.objects.filter(is_active=True).order_by("priority")

    @classmethod
    def get_configs_by_category(cls, category):
        """按类别获取指标配置"""
        return cls.objects.filter(is_active=True, category=category).order_by("priority")

    @classmethod
    def get_auto_fetch_configs(cls):
        """获取需要自动抓取的指标配置"""
        return cls.objects.filter(is_active=True, auto_fetch=True).order_by("priority")

    @classmethod
    def get_configs_by_fetch_frequency(cls, frequency):
        """按抓取频率获取配置"""
        return cls.objects.filter(
            is_active=True, auto_fetch=True, fetch_frequency=frequency
        ).order_by("priority")

    def activate(self):
        """激活指标"""
        self.is_active = True
        self.save()

    def deactivate(self):
        """禁用指标"""
        self.is_active = False
        self.save()

    def update_fetch_status(self, status, error_message=None):
        """更新抓取状态"""
        self.fetch_status = status
        self.last_fetch_time = timezone.now()
        if error_message:
            if self.additional_config is None:
                self.additional_config = {}
            self.additional_config["last_error"] = error_message
        self.save()
