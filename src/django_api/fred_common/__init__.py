"""
FRED Common Module - 通用基础模块
为美国和日本FRED应用提供共享的基础功能
"""

__version__ = "1.0.0"
__author__ = "Development Team"

# 导入通用基础类
from .base_config import BaseDynamicConfigManager
from .base_fetcher import BaseFredDataFetcher
from .base_models import BaseFredModel, BaseFredSeriesInfo
from .base_serializers import (
    BaseAllIndicatorsSerializer,
    BaseErrorResponseSerializer,
    BaseHealthCheckSerializer,
    BaseIndicatorResponseSerializer,
    BaseLatestValueSerializer,
    BaseObservationSerializer,
    BaseStatusSerializer,
)
from .constants import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_TIMEOUT,
    FRED_BASE_URL,
    MAX_RETRIES,
    SUPPORTED_FREQUENCIES,
)
from .utils import (
    calculate_yoy_change,
    clean_numeric_value,
    format_date,
    get_formatted_date_range,
    validate_series_id,
)
from .viewset_mixins import ErrorResponseMixin, FredViewSetMixin, HealthCheckMixin, StatusMixin

__all__ = [
    "DEFAULT_DATE_FORMAT",
    "DEFAULT_TIMEOUT",
    "FRED_BASE_URL",
    "MAX_RETRIES",
    "SUPPORTED_FREQUENCIES",
    "BaseAllIndicatorsSerializer",
    "BaseDynamicConfigManager",
    "BaseErrorResponseSerializer",
    "BaseFredDataFetcher",
    "BaseFredModel",
    "BaseFredSeriesInfo",
    "BaseHealthCheckSerializer",
    "BaseIndicatorResponseSerializer",
    "BaseLatestValueSerializer",
    "BaseObservationSerializer",
    "BaseStatusSerializer",
    "ErrorResponseMixin",
    "FredViewSetMixin",
    "HealthCheckMixin",
    "StatusMixin",
    "calculate_yoy_change",
    "clean_numeric_value",
    "format_date",
    "get_formatted_date_range",
    "validate_series_id",
]
