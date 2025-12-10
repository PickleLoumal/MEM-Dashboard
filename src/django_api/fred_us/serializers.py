"""
Django REST Framework Serializers for US FRED API
美国FRED数据序列化器 - 分离架构实现
"""

from datetime import timedelta

from rest_framework import serializers

from .models import FredUsIndicator


class FredUsObservationSerializer(serializers.ModelSerializer):
    """美国FRED指标观测数据序列化器"""

    class Meta:
        model = FredUsIndicator
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
        """转换为标准格式"""
        return {
            "date": instance.date.isoformat(),
            "value": str(instance.value),
            "indicator_name": instance.indicator_name,
            "indicator_type": instance.indicator_type,
            "unit": instance.unit,
            "frequency": instance.frequency,
            "created_at": instance.created_at.isoformat() if instance.created_at else None,
            "country": "US",
        }


class FredUsLatestValueSerializer(serializers.Serializer):
    """美国FRED指标最新值序列化器"""

    value = serializers.DecimalField(max_digits=15, decimal_places=4)
    date = serializers.DateField()
    formatted_date = serializers.CharField()
    yoy_change = serializers.FloatField(allow_null=True)
    unit = serializers.CharField()
    indicator_name = serializers.CharField()
    series_id = serializers.CharField()
    country = serializers.CharField(default="US")
    source = serializers.CharField(default="PostgreSQL Database (US FRED)")
    last_updated = serializers.DateTimeField(allow_null=True)

    def to_representation(self, instance):
        """格式化输出"""
        if isinstance(instance, dict):
            data = instance
        else:
            # 如果是模型实例
            data = {
                "value": float(instance.value) if instance.value else 0.0,
                "date": instance.date.isoformat() if instance.date else None,
                "formatted_date": instance.formatted_date
                if hasattr(instance, "formatted_date")
                else "",
                "yoy_change": self._calculate_yoy_change(instance),
                "unit": instance.unit or "",
                "indicator_name": instance.indicator_name,
                "series_id": instance.series_id,
                "country": "US",
                "source": "PostgreSQL Database (US FRED)",
                "last_updated": instance.updated_at.isoformat() if instance.updated_at else None,
            }

        return data

    def _calculate_yoy_change(self, instance):
        """计算年同比变化率"""
        try:
            if not instance.date or not instance.value:
                return None

            # 查找一年前的数据
            year_ago = instance.date - timedelta(days=365)
            previous_record = (
                FredUsIndicator.objects.filter(series_id=instance.series_id, date__lte=year_ago)
                .order_by("-date")
                .first()
            )

            if previous_record and previous_record.value:
                current_value = float(instance.value)
                previous_value = float(previous_record.value)
                yoy_change = ((current_value - previous_value) / previous_value) * 100
                return round(yoy_change, 2)

        except Exception:
            pass

        return None


class FredUsIndicatorResponseSerializer(serializers.Serializer):
    """美国FRED指标响应序列化器 - 与前端API格式兼容"""

    success = serializers.BooleanField(default=True)
    data = serializers.DictField()
    observations = serializers.ListField()
    metadata = serializers.DictField()

    def to_representation(self, instance):
        """标准化API响应格式"""
        if isinstance(instance, dict):
            return instance

        return {
            "success": True,
            "data": instance,
            "observations": [],
            "metadata": {"country": "US", "source": "FRED", "api_version": "1.0"},
        }


class FredUsStatusSerializer(serializers.Serializer):
    """美国FRED状态序列化器"""

    status = serializers.CharField()
    database = serializers.CharField()
    country = serializers.CharField(default="US")
    total_indicators = serializers.IntegerField()
    last_updated = serializers.DateTimeField(allow_null=True)
    api_key_configured = serializers.BooleanField()


class FredUsAllIndicatorsSerializer(serializers.Serializer):
    """美国FRED所有指标序列化器"""

    success = serializers.BooleanField(default=True)
    data = serializers.DictField()
    country = serializers.CharField(default="US")
    total_count = serializers.IntegerField()


class FredUsHealthCheckSerializer(serializers.Serializer):
    """美国FRED健康检查序列化器"""

    status = serializers.CharField()
    database_connection = serializers.BooleanField()
    api_connection = serializers.BooleanField()
    country = serializers.CharField(default="US")
    timestamp = serializers.DateTimeField()


class FredUsErrorResponseSerializer(serializers.Serializer):
    """美国FRED错误响应序列化器"""

    success = serializers.BooleanField(default=False)
    error = serializers.CharField()
    country = serializers.CharField(default="US")
    details = serializers.DictField(required=False)
    timestamp = serializers.DateTimeField()
