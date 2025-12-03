"""
Django API 共享类型定义模块

为整个 Django 后端提供统一的类型定义，包括:
- API 响应类型 (api_types.py)
- 模型相关类型 (model_types.py)
- 通用工具类型 (common.py)

使用方式:
    from shared_types import (
        ApiResponse,
        PaginatedResponse,
        CSI300CompanyDict,
        FredIndicatorDict,
    )

类型映射说明 (TypeScript -> Python):
- string -> str
- number -> int | float | Decimal
- boolean -> bool
- null -> None
- T | null -> Optional[T]
- T[] -> List[T]
- Record<string, T> -> Dict[str, T]
- ISO datetime string -> datetime (via isoformat())

版本: 1.0.0
"""

from .common import (
    # 类型别名
    ISODateString,
    ISODateTimeString,
    JSONValue,
    JSONDict,
    # 响应类型
    ApiSuccessResponse,
    ApiErrorResponse,
    ApiResponse,
    PaginatedResponse,
    HealthCheckResponse,
    # 类型守卫
    is_success_response,
    is_error_response,
)

from .api_types import (
    # CSI300 类型
    CSI300CompanyDict,
    CSI300CompanyListItemDict,
    CSI300InvestmentSummaryDict,
    CSI300PeerComparisonItemDict,
    CSI300IndustryPeersComparisonResponseDict,
    CSI300FilterOptionsDict,
    # FRED 类型
    FredObservationDict,
    FredLatestValueDict,
    FredIndicatorResponseDict,
    FredStatusResponseDict,
    FredHealthCheckResponseDict,
    FredErrorResponseDict,
    # BEA 类型
    BeaIndicatorDict,
    BeaIndicatorResponseDict,
    BeaConfigDict,
)

from .model_types import (
    # 模型字段类型
    DecimalFieldType,
    DateFieldType,
    DateTimeFieldType,
    # 类型化模型属性
    CSI300CompanyFields,
    FredUsIndicatorFields,
    BeaIndicatorFields,
)

__all__ = [
    # Common types
    'ISODateString',
    'ISODateTimeString',
    'JSONValue',
    'JSONDict',
    'ApiSuccessResponse',
    'ApiErrorResponse',
    'ApiResponse',
    'PaginatedResponse',
    'HealthCheckResponse',
    'is_success_response',
    'is_error_response',
    # CSI300 types
    'CSI300CompanyDict',
    'CSI300CompanyListItemDict',
    'CSI300InvestmentSummaryDict',
    'CSI300PeerComparisonItemDict',
    'CSI300IndustryPeersComparisonResponseDict',
    'CSI300FilterOptionsDict',
    # FRED types
    'FredObservationDict',
    'FredLatestValueDict',
    'FredIndicatorResponseDict',
    'FredStatusResponseDict',
    'FredHealthCheckResponseDict',
    'FredErrorResponseDict',
    # BEA types
    'BeaIndicatorDict',
    'BeaIndicatorResponseDict',
    'BeaConfigDict',
    # Model types
    'DecimalFieldType',
    'DateFieldType',
    'DateTimeFieldType',
    'CSI300CompanyFields',
    'FredUsIndicatorFields',
    'BeaIndicatorFields',
]

