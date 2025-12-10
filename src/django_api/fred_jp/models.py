"""
Django Models for Japan FRED Economic Indicators
映射专用的日本经济指标PostgreSQL数据库表
"""

from django.db import models
from django.utils import timezone

from fred_common.base_models import BaseFredModel, BaseFredSeriesInfo


class FredJpSeriesInfo(BaseFredSeriesInfo):
    """日本FRED系列信息表 - 基于通用基类"""
    
    class Meta:
        db_table = 'fred_jp_series_info'
        verbose_name = 'Japan FRED Series Info'
        verbose_name_plural = 'Japan FRED Series Info'


class FredJpIndicator(BaseFredModel):
    """日本FRED指标数据表 - 基于通用基类"""
    
    class Meta:
        db_table = 'fred_jp_indicators'
        unique_together = ['series_id', 'date']
        ordering = ['-date']
        verbose_name = 'Japan FRED Indicator'
        verbose_name_plural = 'Japan FRED Indicators'
        indexes = [
            models.Index(fields=['series_id', '-date'], name='idx_jp_series_date'),
            models.Index(fields=['indicator_type', '-date'], name='idx_jp_type_date'),
            models.Index(fields=['series_id', '-updated_at'], name='idx_jp_series_updated'),
        ]
    
    @property
    def country(self):
        """返回国家代码"""
        return 'JP'


class FredJpIndicatorConfig(models.Model):
    """日本FRED指标动态配置模型 - 数据库驱动的指标管理"""
    
    series_id = models.CharField(max_length=50, unique=True, help_text="FRED系列ID")
    name = models.CharField(max_length=200, help_text="指标名称")
    description = models.TextField(blank=True, help_text="详细描述")
    indicator_type = models.CharField(max_length=50, help_text="指标类型分类")
    units = models.CharField(max_length=100, blank=True, help_text="数据单位")
    frequency = models.CharField(max_length=20, default='Monthly', help_text="数据频率")
    category = models.CharField(max_length=100, default='economic', help_text="指标分类")
    
    # API配置
    api_endpoint = models.CharField(max_length=100, unique=True, help_text="API端点路径")
    fallback_value = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, help_text="备用数值")
    
    # 系统配置
    priority = models.IntegerField(default=999, help_text="处理优先级")
    is_active = models.BooleanField(default=True, help_text="是否启用")
    auto_fetch = models.BooleanField(default=True, help_text="是否自动抓取")
    fetch_frequency = models.CharField(
        max_length=20, 
        default='daily',
        choices=[
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        help_text="自动抓取频率"
    )
    
    # 元数据字段
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, default='system')
    updated_by = models.CharField(max_length=100, default='system')
    
    # 扩展配置
    additional_config = models.JSONField(default=dict, blank=True, help_text="额外JSON配置")
    last_fetch_time = models.DateTimeField(null=True, blank=True, help_text="最后抓取时间")
    fetch_status = models.CharField(
        max_length=20,
        default='pending',
        choices=[
            ('pending', 'Pending'),
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('disabled', 'Disabled'),
        ],
        help_text="抓取状态"
    )

    class Meta:
        managed = True
        db_table = 'fred_jp_indicator_configs'
        ordering = ['priority', 'series_id']
        verbose_name = 'Japan FRED Indicator Configuration'
        verbose_name_plural = 'Japan FRED Indicator Configurations'

    def __str__(self):
        return f"JP-{self.series_id}: {self.name}"

    def to_config_dict(self):
        """转换为配置字典格式"""
        return {
            'name': self.name,
            'description': self.description,
            'indicator_type': self.indicator_type,
            'units': self.units,
            'frequency': self.frequency,
            'category': self.category,
            'api_endpoint': self.api_endpoint,
            'fallback_value': float(self.fallback_value) if self.fallback_value else None,
            'priority': self.priority,
            'fetch_frequency': self.fetch_frequency,
            'last_fetch_time': self.last_fetch_time.isoformat() if self.last_fetch_time else None,
            'fetch_status': self.fetch_status
        }

    @classmethod
    def get_active_configs(cls):
        """获取所有激活的指标配置"""
        return cls.objects.filter(is_active=True).order_by('priority')

    @classmethod
    def get_configs_by_category(cls, category):
        """按类别获取指标配置"""
        return cls.objects.filter(is_active=True, category=category).order_by('priority')

    @classmethod
    def get_auto_fetch_configs(cls):
        """获取需要自动抓取的指标配置"""
        return cls.objects.filter(is_active=True, auto_fetch=True).order_by('priority')

    def activate(self):
        """激活此配置"""
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])

    def deactivate(self):
        """禁用此配置"""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])

    def update_fetch_status(self, status, error_message=None):
        """更新抓取状态"""
        self.fetch_status = status
        self.last_fetch_time = timezone.now()
        if error_message:
            if not self.additional_config:
                self.additional_config = {}
            self.additional_config['last_error'] = error_message
        self.save(update_fields=['fetch_status', 'last_fetch_time', 'additional_config', 'updated_at'])
