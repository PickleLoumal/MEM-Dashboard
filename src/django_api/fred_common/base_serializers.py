"""
通用 Serializer 基类

为 FRED US, FRED JP, BEA 等提供统一的序列化接口。
"""

from rest_framework import serializers


class BaseObservationSerializer(serializers.Serializer):
    """观测数据基础序列化器"""

    date = serializers.DateField()
    value = serializers.DecimalField(max_digits=20, decimal_places=6)
    series_id = serializers.CharField()


class BaseLatestValueSerializer(serializers.Serializer):
    """最新值基础序列化器"""

    value = serializers.DecimalField(max_digits=20, decimal_places=6)
    date = serializers.DateField()
    formatted_date = serializers.CharField()
    yoy_change = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    unit = serializers.CharField()


class BaseStatusSerializer(serializers.Serializer):
    """状态基础序列化器"""

    success = serializers.BooleanField()
    system = serializers.CharField()
    database_available = serializers.BooleanField()
    status = serializers.DictField()


class BaseErrorResponseSerializer(serializers.Serializer):
    """错误响应基础序列化器"""

    success = serializers.BooleanField(default=False)
    error = serializers.CharField()
    message = serializers.CharField(required=False)
    timestamp = serializers.DateTimeField()


class BaseHealthCheckSerializer(serializers.Serializer):
    """健康检查基础序列化器"""

    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    service = serializers.CharField()
    database_available = serializers.BooleanField()
    api_connection = serializers.BooleanField()
    version = serializers.CharField()
    country = serializers.CharField()


class BaseIndicatorResponseSerializer(serializers.Serializer):
    """指标响应基础序列化器"""

    success = serializers.BooleanField()
    data = serializers.DictField(required=False)
    observations = serializers.ListField(child=serializers.DictField(), required=False)
    metadata = serializers.DictField(required=False)


class BaseAllIndicatorsSerializer(serializers.Serializer):
    """所有指标概览基础序列化器"""

    success = serializers.BooleanField()
    data = serializers.DictField()
    country = serializers.CharField()
    total_count = serializers.IntegerField()


__all__ = [
    "BaseAllIndicatorsSerializer",
    "BaseErrorResponseSerializer",
    "BaseHealthCheckSerializer",
    "BaseIndicatorResponseSerializer",
    "BaseLatestValueSerializer",
    "BaseObservationSerializer",
    "BaseStatusSerializer",
]
