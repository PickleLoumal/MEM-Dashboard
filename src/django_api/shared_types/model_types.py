"""
Django 模型字段类型定义

定义与 Django 模型字段对应的 Python 类型，
用于类型检查和 IDE 自动完成。

使用 Python 3.9+ 的 typing 特性。
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime
from decimal import Decimal
from typing import (
    Any,
    Literal,
    Optional,
    Protocol,
    TypedDict,
    Union,
    runtime_checkable,
)

# ============================================================================
# Django 字段类型别名
# ============================================================================

# Django DecimalField 类型
# Django 内部使用 Decimal，但序列化后变为 float/str
DecimalFieldType = Union[Decimal, float, None]

# Django DateField 类型
DateFieldType = Optional[date]

# Django DateTimeField 类型
DateTimeFieldType = Optional[datetime]

# Django CharField/TextField 类型
CharFieldType = Optional[str]

# Django IntegerField 类型
IntegerFieldType = Optional[int]

# Django BooleanField 类型
BooleanFieldType = bool

# Django JSONField 类型
JSONFieldType = Union[dict[str, Any], list[Any], None]


# ============================================================================
# CSI300 模型字段类型
# ============================================================================


class CSI300CompanyFields(TypedDict, total=False):
    """
    CSI300Company 模型字段类型定义

    用于类型检查模型实例的字段访问。

    对应: csi300/models.py::CSI300Company
    """

    # 基本信息
    id: int
    name: str
    ticker: CharFieldType
    region: CharFieldType
    im_sector: CharFieldType
    industry: CharFieldType
    gics_industry: CharFieldType
    gics_sub_industry: CharFieldType

    # 公司详情
    naming: CharFieldType
    business_description: CharFieldType
    company_info: CharFieldType
    directors: CharFieldType

    # 价格信息
    price_local_currency: DecimalFieldType
    previous_close: DecimalFieldType
    currency: CharFieldType
    total_return_2018_to_2025: DecimalFieldType
    last_trade_date: DateFieldType
    price_52w_high: DecimalFieldType
    price_52w_low: DecimalFieldType

    # 市值
    market_cap_local: DecimalFieldType
    market_cap_usd: DecimalFieldType

    # 营收
    total_revenue_local: DecimalFieldType
    ltm_revenue_local: DecimalFieldType
    ntm_revenue_local: DecimalFieldType

    # 资产负债
    total_assets_local: DecimalFieldType
    net_assets_local: DecimalFieldType
    total_debt_local: DecimalFieldType

    # 盈利能力
    net_profits_fy0: DecimalFieldType
    operating_margin_trailing: DecimalFieldType
    operating_profits_per_share: DecimalFieldType

    # 每股收益
    eps_trailing: DecimalFieldType
    eps_actual_fy0: DecimalFieldType
    eps_forecast_fy1: DecimalFieldType
    eps_growth_percent: DecimalFieldType

    # 财务比率
    asset_turnover_ltm: DecimalFieldType
    roa_trailing: DecimalFieldType
    roe_trailing: DecimalFieldType
    operating_leverage: DecimalFieldType

    # 风险指标
    altman_z_score_manufacturing: DecimalFieldType
    altman_z_score_non_manufacturing: DecimalFieldType

    # 现金流
    ebitda_fy0: DecimalFieldType
    ebitda_fy_minus_1: DecimalFieldType
    cash_flow_operations_fy0: DecimalFieldType
    cash_flow_operations_fy_minus_1: DecimalFieldType

    # 利息与债务
    interest_expense_fy0: DecimalFieldType
    effective_interest_rate: DecimalFieldType
    interest_coverage_ratio: DecimalFieldType
    debt_to_total_assets: DecimalFieldType
    debt_to_equity: DecimalFieldType

    # 流动性比率
    current_ratio: DecimalFieldType
    quick_ratio: DecimalFieldType

    # 估值比率
    pe_ratio_trailing: DecimalFieldType
    pe_ratio_consensus: DecimalFieldType
    peg_ratio: DecimalFieldType

    # 股息
    dividend_yield_fy0: DecimalFieldType
    dividend_payout_ratio: DecimalFieldType
    dividend_local_currency: DecimalFieldType
    dividend_3yr_cagr: DecimalFieldType
    dividend_5yr_cagr: DecimalFieldType
    dividend_10yr_cagr: DecimalFieldType

    # 元数据
    created_at: DateTimeFieldType
    updated_at: DateTimeFieldType


# ============================================================================
# FRED 模型字段类型
# ============================================================================


class FredUsIndicatorFields(TypedDict, total=False):
    """
    FredUsIndicator 模型字段类型定义

    对应: fred_us/models.py::FredUsIndicator
    """

    id: int
    series_id: str
    indicator_name: str
    indicator_type: CharFieldType
    date: DateFieldType
    value: DecimalFieldType
    unit: CharFieldType
    frequency: CharFieldType
    source: str
    country: Literal["US"]
    created_at: DateTimeFieldType
    updated_at: DateTimeFieldType


class FredUsIndicatorConfigFields(TypedDict, total=False):
    """
    FredUsIndicatorConfig 模型字段类型定义

    对应: fred_us/models.py::FredUsIndicatorConfig
    """

    id: int
    series_id: str
    name: str
    description: str
    indicator_type: str
    units: str
    frequency: str
    category: str
    api_endpoint: str
    fallback_value: DecimalFieldType
    priority: int
    is_active: bool
    auto_fetch: bool
    fetch_frequency: Literal["hourly", "daily", "weekly", "monthly"]
    created_at: DateTimeFieldType
    updated_at: DateTimeFieldType
    created_by: str
    updated_by: str
    additional_config: JSONFieldType
    last_fetch_time: DateTimeFieldType
    fetch_status: Literal["pending", "success", "failed", "disabled"]


# ============================================================================
# BEA 模型字段类型
# ============================================================================


class BeaIndicatorFields(TypedDict, total=False):
    """
    BeaIndicator 模型字段类型定义

    对应: bea/models.py::BeaIndicator
    """

    id: int
    series_id: str
    indicator_name: str
    indicator_type: str
    table_name: CharFieldType
    line_number: CharFieldType
    date: DateFieldType
    time_period: str
    value: DecimalFieldType
    source: str
    unit: CharFieldType
    frequency: CharFieldType
    dataset_name: CharFieldType
    metadata: JSONFieldType
    created_at: DateTimeFieldType
    updated_at: DateTimeFieldType


class BeaIndicatorConfigFields(TypedDict, total=False):
    """
    BeaIndicatorConfig 模型字段类型定义

    对应: bea/models.py::BeaIndicatorConfig
    """

    id: int
    series_id: str
    name: str
    description: str
    table_name: str
    line_description: str
    line_number: IntegerFieldType
    units: str
    frequency: str
    years: str
    category: str
    fallback_value: DecimalFieldType
    api_endpoint: str
    priority: int
    is_active: bool
    auto_fetch: bool
    dataset_name: str
    created_at: DateTimeFieldType
    updated_at: DateTimeFieldType
    created_by: str
    updated_by: str
    additional_config: JSONFieldType


# ============================================================================
# Protocol 类型 (用于鸭子类型检查)
# ============================================================================


@runtime_checkable
class HasTimestamps(Protocol):
    """带有时间戳字段的模型协议"""

    created_at: DateTimeFieldType
    updated_at: DateTimeFieldType


@runtime_checkable
class HasSeriesId(Protocol):
    """带有 series_id 字段的模型协议"""

    series_id: str


@runtime_checkable
class HasActiveStatus(Protocol):
    """带有激活状态字段的模型协议"""

    is_active: bool

    def activate(self) -> None:
        """激活"""
        ...

    def deactivate(self) -> None:
        """停用"""
        ...


# ============================================================================
# 类型转换工具
# ============================================================================


def model_to_dict_typed(
    instance: Any, fields: Sequence[str] | None = None, exclude: Sequence[str] | None = None
) -> dict[str, Any]:
    """
    将 Django 模型实例转换为类型化字典

    Args:
        instance: Django 模型实例
        fields: 要包含的字段列表
        exclude: 要排除的字段列表

    Returns:
        包含模型数据的字典
    """
    from django.forms.models import model_to_dict

    return model_to_dict(instance, fields=fields, exclude=exclude)
