"""
Django REST Framework Serializers for MEM Dashboard FRED API
维持与Flask API完全相同的响应格式
"""

from rest_framework import serializers
from datetime import datetime
from .models import FredIndicator, FredSeriesInfo


class FredObservationSerializer(serializers.ModelSerializer):
    """FRED指标观测数据序列化器 - 用于observations数组"""
    
    class Meta:
        model = FredIndicator
        fields = ['date', 'value', 'indicator_name', 'indicator_type', 'unit', 'frequency', 'created_at']
        
    def to_representation(self, instance):
        """转换为与Flask API兼容的格式"""
        return {
            'date': instance.date.isoformat(),
            'value': str(instance.value),
            'indicator_name': instance.indicator_name,
            'indicator_type': instance.indicator_type,
            'unit': instance.unit,
            'frequency': instance.frequency,
            'created_at': instance.created_at.isoformat() if instance.created_at else None
        }


class FredLatestValueSerializer(serializers.Serializer):
    """FRED指标最新值序列化器 - 对应Flask API的data字段格式"""
    value = serializers.DecimalField(max_digits=15, decimal_places=4)
    date = serializers.DateField()
    formatted_date = serializers.CharField()
    yoy_change = serializers.FloatField(allow_null=True)
    unit = serializers.CharField()
    indicator_name = serializers.CharField()
    series_id = serializers.CharField()
    source = serializers.CharField(default="PostgreSQL Database (Django DRF)")
    last_updated = serializers.DateTimeField(allow_null=True)
    
    def to_representation(self, instance):
        """格式化输出，与Flask API保持一致"""
        if isinstance(instance, dict):
            data = instance
        else:
            # 如果是模型实例，使用实际存在的字段
            data = {
                'value': float(instance.value) if instance.value else 0.0,
                'date': instance.date,
                'formatted_date': instance.date.strftime('%b %Y') if instance.date else '',
                'unit': getattr(instance, 'unit', '') or '',
                'indicator_name': getattr(instance, 'indicator_name', '') or '',
                'series_id': getattr(instance, 'series_id', '') or '',
                'last_updated': getattr(instance, 'created_at', None)
            }
        
        # 安全的数据访问和转换
        last_updated = data.get('last_updated')
        return {
            'value': float(data.get('value', 0)),
            'date': data['date'].isoformat() if hasattr(data.get('date'), 'isoformat') else str(data.get('date', '')),
            'formatted_date': data.get('formatted_date', ''),
            'yoy_change': data.get('yoy_change'),
            'unit': data.get('unit', ''),
            'indicator_name': data.get('indicator_name', ''),
            'series_id': data.get('series_id', ''),
            'source': "PostgreSQL Database (Django DRF)",
            'last_updated': last_updated.isoformat() if last_updated and hasattr(last_updated, 'isoformat') else None
        }


class FredIndicatorResponseSerializer(serializers.Serializer):
    """完整的FRED指标响应序列化器 - 对应Flask API完整响应格式"""
    success = serializers.BooleanField(default=True)
    data = FredLatestValueSerializer()
    observations = FredObservationSerializer(many=True)
    source = serializers.CharField(default="PostgreSQL Database (Django DRF)")
    series_id = serializers.CharField()
    total_records = serializers.IntegerField()
    last_updated = serializers.DateTimeField(allow_null=True)


class FredStatusSerializer(serializers.Serializer):
    """FRED系统状态序列化器 - 对应Flask /api/fred/status"""
    success = serializers.BooleanField(default=True)
    system = serializers.CharField(default="FRED Unified System (Django)")
    database_available = serializers.BooleanField()
    status = serializers.DictField()
    supported_indicators = serializers.ListField()
    last_updated = serializers.DateTimeField()


class FredAllIndicatorsSerializer(serializers.Serializer):
    """所有指标序列化器 - 对应Flask /api/fred/all"""
    success = serializers.BooleanField(default=True)
    data = serializers.DictField()
    source = serializers.CharField(default="PostgreSQL Database (Django DRF)")
    indicators_count = serializers.IntegerField()
    last_updated = serializers.DateTimeField()


class FredHealthCheckSerializer(serializers.Serializer):
    """健康检查序列化器 - 对应Flask /api/health"""
    status = serializers.CharField(default="healthy")
    timestamp = serializers.DateTimeField()
    service = serializers.CharField(default="MEM Dashboard Django API")
    database_available = serializers.BooleanField()
    version = serializers.CharField(default="1.0.0")


class FredErrorResponseSerializer(serializers.Serializer):
    """错误响应序列化器 - 统一错误格式"""
    success = serializers.BooleanField(default=False)
    error = serializers.CharField()
    message = serializers.CharField()
    series_id = serializers.CharField(required=False)
    supported_indicators = serializers.ListField(required=False)
    timestamp = serializers.DateTimeField()
