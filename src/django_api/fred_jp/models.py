"""
Django Models for Japan FRED Economic Indicators
映射专用的日本经济指标PostgreSQL数据库表
"""

from django.db import models
from django.utils import timezone


class FredJpSeriesInfo(models.Model):
    """日本FRED系列信息表 - 映射fred_jp_series_info表"""
    series_id = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True, null=True)
    units = models.CharField(max_length=50, blank=True, null=True)
    frequency = models.CharField(max_length=20, blank=True, null=True)
    seasonal_adjustment = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fred_jp_series_info'  # 使用专用日本表
        managed = False  # Django不管理这个表，避免migration冲突

    def __str__(self):
        return f"{self.series_id}: {self.title}"


class FredJpIndicator(models.Model):
    """日本FRED指标数据表 - 映射fred_jp_indicators表"""
    id = models.AutoField(primary_key=True)
    series_id = models.CharField(max_length=50)
    indicator_name = models.CharField(max_length=200)
    indicator_type = models.CharField(max_length=50)
    date = models.DateField()
    value = models.DecimalField(max_digits=15, decimal_places=4)
    source = models.CharField(max_length=100, default='FRED')
    unit = models.CharField(max_length=50, blank=True, null=True)
    frequency = models.CharField(max_length=20, blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fred_jp_indicators'  # 使用专用日本表
        managed = False  # Django不管理这个表，避免migration冲突
        unique_together = ['series_id', 'date']
        ordering = ['-date']  # 按日期降序排列

    def __str__(self):
        return f"{self.series_id} - {self.date}: {self.value}"

    @property
    def formatted_date(self):
        """格式化日期显示"""
        return self.date.strftime('%b %Y')

    @property
    def value_as_float(self):
        """将值转换为浮点数"""
        return float(self.value)
