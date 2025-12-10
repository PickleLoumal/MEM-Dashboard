"""
Django REST Framework Serializers for Japan FRED API
维持与美国FRED API完全相同的响应格式
"""

from rest_framework import serializers

from .models import FredJpIndicator, FredJpSeriesInfo


class FredJpObservationSerializer(serializers.ModelSerializer):
    """日本FRED指标观测数据序列化器 - 用于observations数组"""

    class Meta:
        model = FredJpIndicator
        fields = [
            "date",
            "value",
            "indicator_name",
            "indicator_type",
            "unit",
            "frequency",
            "created_at",
        ]

    def to_representation(self, instance):
        """转换为与Flask API兼容的格式"""
        return {
            "date": instance.date.isoformat(),
            "value": str(instance.value),
            "indicator_name": instance.indicator_name,
            "indicator_type": instance.indicator_type,
            "unit": instance.unit,
            "frequency": instance.frequency,
            "created_at": instance.created_at.isoformat() if instance.created_at else None,
        }


class FredJpLatestValueSerializer(serializers.Serializer):
    """日本FRED指标最新值序列化器 - 对应Flask API的data字段格式"""

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
                "value": float(instance.value) if instance.value else 0.0,
                "date": instance.date.isoformat() if instance.date else None,
                "formatted_date": instance.formatted_date
                if hasattr(instance, "formatted_date")
                else None,
                "yoy_change": instance.yoy_change if hasattr(instance, "yoy_change") else None,
                "unit": instance.unit or "",
                "indicator_name": instance.indicator_name or "",
                "series_id": instance.series_id or "",
                "source": "PostgreSQL Database (Django DRF)",
                "last_updated": instance.updated_at.isoformat()
                if hasattr(instance, "updated_at") and instance.updated_at
                else None,
            }

        return data


class FredJpSeriesInfoSerializer(serializers.ModelSerializer):
    """日本FRED系列信息序列化器"""

    class Meta:
        model = FredJpSeriesInfo
        fields = "__all__"

    def to_representation(self, instance):
        """标准化输出格式"""
        return {
            "series_id": instance.series_id,
            "title": instance.title,
            "category": instance.category,
            "units": instance.units,
            "frequency": instance.frequency,
            "seasonal_adjustment": instance.seasonal_adjustment,
            "notes": instance.notes,
            "last_updated": instance.last_updated.isoformat() if instance.last_updated else None,
        }


class FredJpStatusSerializer(serializers.Serializer):
    """日本FRED系统状态序列化器"""

    success = serializers.BooleanField(default=True)
    system = serializers.CharField(default="Japan FRED System (Django)")
    database_available = serializers.BooleanField()
    status = serializers.DictField()
    supported_indicators = serializers.ListField()
    last_updated = serializers.DateTimeField()


class FredJpErrorResponseSerializer(serializers.Serializer):
    """日本FRED错误响应序列化器 - 统一错误格式"""

    success = serializers.BooleanField(default=False)
    error = serializers.CharField()
    message = serializers.CharField()
    series_id = serializers.CharField(required=False)
    supported_indicators = serializers.ListField(required=False)
    timestamp = serializers.DateTimeField()
