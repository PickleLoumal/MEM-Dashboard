"""
通用类型定义

定义所有 API 共享的基础类型，包括响应格式、分页、错误处理等。
与前端 TypeScript 类型一一对应。

对应前端: csi300-app/src/shared/api-types/common.types.ts
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import (
    Any,
    Literal,
    TypedDict,
    TypeVar,
    Union,
)

# ============================================================================
# 类型别名
# ============================================================================

# ISO 8601 日期字符串 (格式: "YYYY-MM-DD")
ISODateString = str

# ISO 8601 日期时间字符串 (格式: "YYYY-MM-DDTHH:mm:ss.sssZ")
ISODateTimeString = str

# JSON 值类型
JSONValue = Union[str, int, float, bool, None, dict[str, Any], list[Any]]

# JSON 字典类型
JSONDict = dict[str, JSONValue]

# 泛型数据类型
T = TypeVar("T")


# ============================================================================
# API 响应类型
# ============================================================================


class ApiMetadata(TypedDict, total=False):
    """API 元数据"""

    country: str
    source: str
    api_version: str
    total_records: int
    series_id: str


class ApiSuccessResponse[T](TypedDict):
    """
    成功响应的基础结构

    对应 TypeScript: ApiSuccessResponse<T>
    """

    success: Literal[True]
    data: T
    metadata: ApiMetadata | None


class ApiErrorResponse(TypedDict):
    """
    错误响应结构

    对应 TypeScript: ApiErrorResponse
    对应 Python Serializer: FredUsErrorResponseSerializer
    """

    success: Literal[False]
    error: str
    details: dict[str, Any] | None
    timestamp: ISODateTimeString | None
    country: str | None


# 通用 API 响应类型
ApiResponse = Union[ApiSuccessResponse[T], ApiErrorResponse]


# ============================================================================
# 分页类型
# ============================================================================


class PaginationParams(TypedDict, total=False):
    """分页请求参数"""

    page: int
    page_size: int


class PaginatedResponse[T](TypedDict):
    """
    分页响应结构

    对应 Django REST Framework 的 PageNumberPagination
    对应 TypeScript: PaginatedResponse<T>
    """

    count: int
    next: str | None
    previous: str | None
    results: list[T]


# ============================================================================
# 筛选选项类型
# ============================================================================


class MarketCapRange(TypedDict):
    """市值范围"""

    min: float
    max: float


class FilterOptions(TypedDict, total=False):
    """
    CSI300 筛选选项

    对应 TypeScript: FilterOptions
    """

    regions: list[str]
    im_sectors: list[str]
    industries: list[str]
    gics_industries: list[str]
    market_cap_range: MarketCapRange
    filtered_by_region: bool
    region_filter: str | None
    filtered_by_sector: bool
    sector_filter: str | None


# ============================================================================
# 健康检查类型
# ============================================================================

HealthStatus = Literal["healthy", "unhealthy", "error"]


class HealthCheckResponse(TypedDict, total=False):
    """
    健康检查响应

    对应 TypeScript: HealthCheckResponse
    """

    status: HealthStatus
    database_connection: bool
    api_connection: bool
    country: str
    timestamp: ISODateTimeString
    service: str
    total_companies: int
    database_available: bool


class ServiceStatusResponse(TypedDict):
    """
    服务状态响应

    对应 TypeScript: ServiceStatusResponse
    """

    status: str
    database: str
    country: str
    total_indicators: int
    last_updated: ISODateTimeString | None
    api_key_configured: bool


# ============================================================================
# 类型守卫函数
# ============================================================================


def is_success_response(response: dict[str, Any]) -> bool:
    """
    检查是否为成功响应

    Args:
        response: API 响应字典

    Returns:
        如果 success 字段为 True 则返回 True

    Example:
        >>> is_success_response({'success': True, 'data': {...}})
        True
        >>> is_success_response({'success': False, 'error': 'Not found'})
        False
    """
    return response.get("success") is True


def is_error_response(response: dict[str, Any]) -> bool:
    """
    检查是否为错误响应

    Args:
        response: API 响应字典

    Returns:
        如果 success 字段为 False 则返回 True
    """
    return response.get("success") is False


def is_paginated_response(response: dict[str, Any]) -> bool:
    """
    检查是否为分页响应

    Args:
        response: API 响应字典

    Returns:
        如果包含 count 和 results 字段则返回 True
    """
    return (
        isinstance(response, dict)
        and "count" in response
        and "results" in response
        and isinstance(response.get("results"), list)
    )


# ============================================================================
# 工具函数
# ============================================================================


def to_iso_date(d: date | None) -> ISODateString | None:
    """
    将 date 对象转换为 ISO 日期字符串

    Args:
        d: Python date 对象

    Returns:
        ISO 格式日期字符串 "YYYY-MM-DD" 或 None
    """
    return d.isoformat() if d else None


def to_iso_datetime(dt: datetime | None) -> ISODateTimeString | None:
    """
    将 datetime 对象转换为 ISO 日期时间字符串

    Args:
        dt: Python datetime 对象

    Returns:
        ISO 格式日期时间字符串或 None
    """
    return dt.isoformat() if dt else None


def decimal_to_float(value: Decimal | None) -> float | None:
    """
    安全地将 Decimal 转换为 float

    Args:
        value: Decimal 值

    Returns:
        float 值或 None
    """
    return float(value) if value is not None else None
