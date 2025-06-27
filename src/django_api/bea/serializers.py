"""
BEA API Django REST Framework Serializers
用于API请求/响应数据的序列化和验证
"""

from rest_framework import serializers
from .models import BeaIndicator, BeaSeriesInfo, BeaIndicatorConfig
from django.utils import timezone


class BeaIndicatorSerializer(serializers.ModelSerializer):
    """BEA指标数据序列化器"""
    
    yoy_change = serializers.SerializerMethodField()
    formatted_date = serializers.SerializerMethodField()
    value_billions = serializers.SerializerMethodField()
    
    class Meta:
        model = BeaIndicator
        fields = [
            'series_id', 'time_period', 'value', 'created_at',
            'yoy_change', 'formatted_date', 'value_billions'
        ]
        read_only_fields = ['created_at']
    
    def get_yoy_change(self, obj):
        """计算同比变化"""
        return obj.get_yoy_change()
    
    def get_formatted_date(self, obj):
        """格式化日期显示"""
        return obj.get_formatted_date()
    
    def get_value_billions(self, obj):
        """转换为十亿美元单位"""
        try:
            return round(float(obj.value) / 1000000, 3)
        except (ValueError, TypeError):
            return None


class BeaSeriesInfoSerializer(serializers.ModelSerializer):
    """BEA系列信息序列化器"""
    
    class Meta:
        model = BeaSeriesInfo
        fields = [
            'series_id', 'table_name', 'line_number', 'series_code', 
            'cl_unit', 'unit_mult', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class BeaIndicatorConfigSerializer(serializers.ModelSerializer):
    """BEA指标配置序列化器"""
    
    last_updated = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = BeaIndicatorConfig
        fields = [
            'id', 'series_id', 'name', 'category', 'description',
            'api_endpoint', 'table_name', 'line_description', 'units',
            'auto_fetch', 'is_active', 'priority', 'fallback_value',
            'additional_config', 'created_at', 'updated_at', 'last_updated'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_updated']
    
    def validate_series_id(self, value):
        """验证系列ID格式"""
        if not value or len(value) < 3:
            raise serializers.ValidationError("Series ID must be at least 3 characters long")
        return value.upper()
    
    def validate_api_endpoint(self, value):
        """验证API端点格式"""
        if not value:
            raise serializers.ValidationError("API endpoint is required")
        
        # 确保以/开头和/结尾
        if not value.startswith('/'):
            value = '/' + value
        if not value.endswith('/'):
            value = value + '/'
        
        return value
    
    def validate_priority(self, value):
        """验证优先级范围"""
        if value is not None and (value < 1 or value > 100):
            raise serializers.ValidationError("Priority must be between 1 and 100")
        return value


class BeaIndicatorDataResponseSerializer(serializers.Serializer):
    """BEA指标API响应数据序列化器"""
    
    value = serializers.FloatField()
    date = serializers.DateField()
    formatted_date = serializers.CharField()
    yoy_change = serializers.FloatField(allow_null=True)
    series_id = serializers.CharField()
    source = serializers.CharField()
    last_updated = serializers.DateTimeField()
    quarterly_data = serializers.ListField(required=False)


class BeaApiResponseSerializer(serializers.Serializer):
    """BEA API标准响应序列化器"""
    
    success = serializers.BooleanField()
    error = serializers.CharField(required=False, allow_null=True)
    message = serializers.CharField(required=False, allow_null=True)
    timestamp = serializers.DateTimeField(required=False)
    last_updated = serializers.DateTimeField(required=False)
    source = serializers.CharField(required=False)
    # Note: data field removed as JSONField is not available in this DRF version


class BeaAllIndicatorsSerializer(serializers.Serializer):
    """所有BEA指标响应序列化器"""
    
    success = serializers.BooleanField()
    indicators_count = serializers.IntegerField()
    source = serializers.CharField()
    last_updated = serializers.DateTimeField()
    # Note: data field removed as JSONField is not available in this DRF version


class BeaCategorySerializer(serializers.Serializer):
    """BEA指标分类序列化器"""
    
    category = serializers.CharField()
    indicators = serializers.ListField()
    count = serializers.IntegerField()


class BeaStatsSerializer(serializers.Serializer):
    """BEA系统统计序列化器"""
    
    total_indicators = serializers.IntegerField()
    active_indicators = serializers.IntegerField()
    categories = serializers.ListField()
    last_data_update = serializers.DateTimeField(allow_null=True)
    auto_fetch_count = serializers.IntegerField()
    database_size = serializers.CharField()


class BeaConfigCreateSerializer(serializers.ModelSerializer):
    """创建BEA配置的序列化器"""
    
    class Meta:
        model = BeaIndicatorConfig
        fields = [
            'series_id', 'name', 'category', 'description',
            'api_endpoint', 'table_name', 'line_description', 'units',
            'auto_fetch', 'is_active', 'priority', 'fallback_value', 'additional_config'
        ]
    
    def create(self, validated_data):
        """创建新的指标配置"""
        # 确保series_id唯一性
        series_id = validated_data['series_id']
        if BeaIndicatorConfig.objects.filter(series_id=series_id).exists():
            raise serializers.ValidationError(
                f"Indicator config with series_id '{series_id}' already exists"
            )
        
        return super().create(validated_data)


class BeaConfigUpdateSerializer(serializers.ModelSerializer):
    """更新BEA配置的序列化器"""
    
    class Meta:
        model = BeaIndicatorConfig
        fields = [
            'name', 'category', 'description', 'api_endpoint',
            'table_name', 'line_description', 'units', 'auto_fetch',
            'is_active', 'priority', 'fallback_value', 'additional_config'
        ]
    
    def validate(self, attrs):
        """验证更新数据"""
        # 如果设置为非激活状态，确认是否有依赖
        if 'is_active' in attrs and not attrs['is_active']:
            # 这里可以添加依赖检查逻辑
            pass
        
        return attrs
