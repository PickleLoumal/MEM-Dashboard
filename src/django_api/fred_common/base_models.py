"""
FRED Base Models - 通用基础数据模型
为美国和日本FRED应用提供共同的数据模型抽象类
"""

from abc import ABC, abstractmethod
from django.db import models
from django.utils import timezone
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseFredModel(models.Model):
    """FRED基础模型抽象类 - 为所有FRED指标提供共同字段和方法"""
    
    # 通用字段
    series_id = models.CharField(max_length=50, db_index=True)
    indicator_name = models.CharField(max_length=200)
    indicator_type = models.CharField(max_length=50)
    date = models.DateField(db_index=True)
    value = models.DecimalField(max_digits=15, decimal_places=4)
    source = models.CharField(max_length=100, default='FRED')
    unit = models.CharField(max_length=50, blank=True, null=True)
    frequency = models.CharField(max_length=50, blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-date']
        unique_together = ['series_id', 'date']

    def __str__(self):
        return f"{self.series_id} - {self.date}: {self.value}"

    @property
    def formatted_date(self):
        """格式化日期显示"""
        return self.date.strftime('%b %Y')

    @property
    def value_as_float(self):
        """将值转换为浮点数"""
        try:
            return float(self.value)
        except (ValueError, TypeError):
            return 0.0

    @property
    def formatted_value(self):
        """格式化数值显示"""
        try:
            val = float(self.value)
            if self.unit and 'Percent' in self.unit:
                return f"{val:.2f}%"
            elif self.unit and 'Billion' in self.unit:
                return f"{val:,.1f}B"
            elif self.unit and 'Million' in self.unit:
                return f"{val:,.1f}M"
            else:
                return f"{val:,.2f}"
        except (ValueError, TypeError):
            return str(self.value)

    def calculate_yoy_change(self, previous_value: Optional[float] = None) -> Optional[float]:
        """计算同比变化率"""
        if previous_value is None:
            return None
        
        try:
            current_val = self.value_as_float
            if previous_value == 0:
                return None
            return ((current_val - previous_value) / previous_value) * 100
        except (ValueError, TypeError, ZeroDivisionError):
            return None

    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """安全获取元数据值"""
        if not self.metadata:
            return default
        return self.metadata.get(key, default)

    def set_metadata_value(self, key: str, value: Any) -> None:
        """设置元数据值"""
        if not self.metadata:
            self.metadata = {}
        self.metadata[key] = value

    @classmethod
    def get_latest_by_series(cls, series_id: str) -> Optional['BaseFredModel']:
        """获取指定系列的最新数据"""
        try:
            return cls.objects.filter(series_id=series_id).first()
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_date_range_data(cls, series_id: str, start_date: str, end_date: str):
        """获取指定日期范围的数据"""
        return cls.objects.filter(
            series_id=series_id,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')


class BaseFredSeriesInfo(models.Model):
    """FRED系列信息基础模型抽象类"""
    
    series_id = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True, null=True)
    units = models.CharField(max_length=50, blank=True, null=True)
    frequency = models.CharField(max_length=50, blank=True, null=True)
    seasonal_adjustment = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.series_id}: {self.title}"

    @property
    def is_seasonal_adjusted(self):
        """检查是否季节性调整"""
        if not self.seasonal_adjustment:
            return False
        return 'Seasonally Adjusted' in self.seasonal_adjustment

    @property
    def frequency_display(self):
        """显示友好的频率名称"""
        frequency_mapping = {
            'Annual': '年度',
            'Quarterly': '季度', 
            'Monthly': '月度',
            'Weekly': '周度',
            'Daily': '日度'
        }
        return frequency_mapping.get(self.frequency or '', self.frequency or '')

    def get_description(self) -> str:
        """获取完整描述"""
        parts = [self.title]
        if self.units:
            parts.append(f"单位: {self.units}")
        if self.frequency:
            parts.append(f"频率: {self.frequency_display}")
        return " | ".join(parts)
