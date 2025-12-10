"""
BEA应用的Django模型
包含BEA指标数据和动态配置管理
"""

from django.db import models


class BeaIndicator(models.Model):
    """BEA指标数据模型"""

    series_id = models.CharField(max_length=50)
    indicator_name = models.CharField(max_length=200)
    indicator_type = models.CharField(max_length=50)
    table_name = models.CharField(max_length=50, null=True, blank=True)
    line_number = models.CharField(max_length=10, null=True, blank=True)
    date = models.DateField()
    time_period = models.CharField(max_length=10)
    value = models.DecimalField(max_digits=15, decimal_places=4)
    source = models.CharField(max_length=100, default="BEA")
    unit = models.CharField(max_length=50, null=True, blank=True)
    frequency = models.CharField(max_length=20, null=True, blank=True)
    dataset_name = models.CharField(max_length=50, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True  # 改为True让Django管理此表
        db_table = "bea_indicators"
        unique_together = ("series_id", "time_period")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.series_id}: {self.value} ({self.time_period})"

    def get_yoy_change(self):
        """计算同比变化"""
        try:
            # 查找一年前的数据
            year_ago_period = f"{int(self.time_period[:4]) - 1}{self.time_period[4:]}"
            year_ago_data = BeaIndicator.objects.filter(
                series_id=self.series_id, time_period=year_ago_period
            ).first()

            if year_ago_data and year_ago_data.value != 0:
                return float((self.value - year_ago_data.value) / year_ago_data.value * 100)
            return None
        except (ValueError, TypeError, ZeroDivisionError):
            return None

    def get_formatted_date(self):
        """格式化日期显示"""
        if self.date:
            return self.date.strftime("%Y-%m-%d")
        return self.time_period

    @classmethod
    def get_latest_by_series(cls, series_id):
        """获取指定系列的最新数据"""
        return cls.objects.filter(series_id=series_id).first()

    @classmethod
    def get_quarterly_data(cls, series_id, limit=8):
        """获取指定系列的季度数据"""
        return cls.objects.filter(series_id=series_id, time_period__contains="Q")[:limit]


class BeaSeriesInfo(models.Model):
    """BEA系列信息模型"""

    series_id = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100, null=True, blank=True)
    table_name = models.CharField(max_length=50, null=True, blank=True)
    line_number = models.CharField(max_length=10, null=True, blank=True)
    line_description = models.CharField(max_length=200, null=True, blank=True)
    units = models.CharField(max_length=50, null=True, blank=True)
    frequency = models.CharField(max_length=20, null=True, blank=True)
    dataset_name = models.CharField(max_length=50, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False  # 遵循WARNING要求
        db_table = "bea_series_info"

    def __str__(self):
        return f"{self.series_id}: {self.title}"


class BeaIndicatorConfig(models.Model):
    """BEA指标动态配置模型 - 数据库驱动的指标管理"""

    series_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    table_name = models.CharField(max_length=50)
    line_description = models.CharField(max_length=500)
    line_number = models.IntegerField(null=True, blank=True)
    units = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=20, default="Q")
    years = models.CharField(max_length=100, default="2022,2023,2024,2025")
    category = models.CharField(max_length=100, default="consumer_spending")
    fallback_value = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    api_endpoint = models.CharField(max_length=100, unique=True)
    priority = models.IntegerField(default=999)
    is_active = models.BooleanField(default=True)
    auto_fetch = models.BooleanField(default=True)
    dataset_name = models.CharField(max_length=50, default="NIPA")

    # 元数据字段
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, default="system")
    updated_by = models.CharField(max_length=100, default="system")

    # 扩展字段
    additional_config = models.JSONField(default=dict, blank=True)

    class Meta:
        managed = False  # 遵循WARNING要求
        db_table = "bea_indicator_configs"
        ordering = ["priority", "series_id"]

    def __str__(self):
        return f"{self.series_id}: {self.name}"

    def to_config_dict(self):
        """转换为配置字典格式，保持与旧代码的兼容性"""
        return {
            "name": self.name,
            "description": self.description,
            "table": self.table_name,
            "line_description": self.line_description,
            "line_number": self.line_number,
            "units": self.units,
            "frequency": self.frequency,
            "years": self.years,
            "category": self.category,
            "fallback_value": float(self.fallback_value) if self.fallback_value else None,
            "api_endpoint": self.api_endpoint,
            "priority": self.priority,
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

    def activate(self):
        """激活指标"""
        self.is_active = True
        self.save()

    def deactivate(self):
        """禁用指标"""
        self.is_active = False
        self.save()
