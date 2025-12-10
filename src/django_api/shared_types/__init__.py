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

from .api_types import (
    BeaConfigDict,
    # BEA 类型
    BeaIndicatorDict,
    BeaIndicatorResponseDict,
    # CSI300 类型
    CSI300CompanyDict,
    CSI300CompanyListItemDict,
    CSI300FilterOptionsDict,
    CSI300IndustryPeersComparisonResponseDict,
    CSI300InvestmentSummaryDict,
    CSI300PeerComparisonItemDict,
    FredErrorResponseDict,
    FredHealthCheckResponseDict,
    FredIndicatorResponseDict,
    FredLatestValueDict,
    # FRED 类型
    FredObservationDict,
    FredStatusResponseDict,
)
from .common import (
    ApiErrorResponse,
    ApiResponse,
    # 响应类型
    ApiSuccessResponse,
    HealthCheckResponse,
    # 类型别名
    ISODateString,
    ISODateTimeString,
    JSONDict,
    JSONValue,
    PaginatedResponse,
    is_error_response,
    # 类型守卫
    is_success_response,
)
from .model_types import (
    BeaIndicatorFields,
    # 类型化模型属性
    CSI300CompanyFields,
    DateFieldType,
    DateTimeFieldType,
    # 模型字段类型
    DecimalFieldType,
    FredUsIndicatorFields,
)

__all__ = [
    "ApiErrorResponse",
    "ApiResponse",
    "ApiSuccessResponse",
    "BeaConfigDict",
    # BEA types
    "BeaIndicatorDict",
    "BeaIndicatorFields",
    "BeaIndicatorResponseDict",
    # CSI300 types
    "CSI300CompanyDict",
    "CSI300CompanyFields",
    "CSI300CompanyListItemDict",
    "CSI300FilterOptionsDict",
    "CSI300IndustryPeersComparisonResponseDict",
    "CSI300InvestmentSummaryDict",
    "CSI300PeerComparisonItemDict",
    "DateFieldType",
    "DateTimeFieldType",
    # Model types
    "DecimalFieldType",
    "FredErrorResponseDict",
    "FredHealthCheckResponseDict",
    "FredIndicatorResponseDict",
    "FredLatestValueDict",
    # FRED types
    "FredObservationDict",
    "FredStatusResponseDict",
    "FredUsIndicatorFields",
    "HealthCheckResponse",
    # Common types
    "ISODateString",
    "ISODateTimeString",
    "JSONDict",
    "JSONValue",
    "PaginatedResponse",
    "is_error_response",
    "is_success_response",
]
