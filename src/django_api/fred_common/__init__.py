"""
FRED Common Module - 通用基础模块
为美国和日本FRED应用提供共享的基础功能
"""

__version__ = '1.0.0'
__author__ = 'MEM Dashboard Team'

# 导入通用基础类
from .base_models import BaseFredModel, BaseFredSeriesInfo
from .base_fetcher import BaseFredDataFetcher
from .base_config import BaseDynamicConfigManager
from .viewset_mixins import HealthCheckMixin, ErrorResponseMixin, StatusMixin, FredViewSetMixin
from .base_serializers import (
    BaseObservationSerializer,
    BaseLatestValueSerializer,
    BaseStatusSerializer,
    BaseErrorResponseSerializer,
    BaseHealthCheckSerializer,
    BaseIndicatorResponseSerializer,
    BaseAllIndicatorsSerializer,
)
from .utils import (
    format_date,
    calculate_yoy_change,
    validate_series_id,
    clean_numeric_value,
    get_formatted_date_range
)
from .constants import (
    FRED_BASE_URL,
    DEFAULT_TIMEOUT,
    MAX_RETRIES,
    SUPPORTED_FREQUENCIES,
    DEFAULT_DATE_FORMAT
)

__all__ = [
    'BaseFredModel',
    'BaseFredSeriesInfo', 
    'BaseFredDataFetcher',
    'BaseDynamicConfigManager',
    'HealthCheckMixin',
    'ErrorResponseMixin',
    'StatusMixin',
    'FredViewSetMixin',
    'BaseObservationSerializer',
    'BaseLatestValueSerializer',
    'BaseStatusSerializer',
    'BaseErrorResponseSerializer',
    'BaseHealthCheckSerializer',
    'BaseIndicatorResponseSerializer',
    'BaseAllIndicatorsSerializer',
    'format_date',
    'calculate_yoy_change',
    'validate_series_id',
    'clean_numeric_value',
    'get_formatted_date_range',
    'FRED_BASE_URL',
    'DEFAULT_TIMEOUT',
    'MAX_RETRIES',
    'SUPPORTED_FREQUENCIES',
    'DEFAULT_DATE_FORMAT'
]
