"""
API 响应类型定义

定义各个 API 模块的响应类型，使用 TypedDict 确保类型安全。
与前端 TypeScript 类型一一对应。

对应前端:
- csi300-app/src/shared/api-types/csi300.types.ts
- csi300-app/src/shared/api-types/fred.types.ts
- csi300-app/src/shared/api-types/bea.types.ts
"""

from __future__ import annotations

from typing import (
    Any,
    Literal,
    TypedDict,
)

from .common import ISODateString, ISODateTimeString

# ============================================================================
# CSI300 类型定义
# ============================================================================


class CSI300CompanyDict(TypedDict, total=False):
    """
    CSI300 公司完整详情字典类型

    对应:
    - Model: csi300/models.py::CSI300Company
    - Serializer: csi300/serializers.py::CSI300CompanySerializer
    - TypeScript: CSI300Company
    """

    id: int

    # 基本信息
    name: str
    ticker: str | None
    region: str | None
    im_sector: str | None
    industry: str | None
    gics_industry: str | None
    gics_sub_industry: str | None

    # 公司详情
    naming: str | None
    business_description: str | None
    company_info: str | None
    directors: str | None

    # 价格信息
    price_local_currency: float | None
    previous_close: float | None
    currency: str | None
    total_return_2018_to_2025: float | None
    last_trade_date: ISODateString | None
    price_52w_high: float | None
    price_52w_low: float | None

    # 市值
    market_cap_local: float | None
    market_cap_usd: float | None

    # 营收
    total_revenue_local: float | None
    ltm_revenue_local: float | None
    ntm_revenue_local: float | None

    # 资产负债
    total_assets_local: float | None
    net_assets_local: float | None
    total_debt_local: float | None

    # 盈利能力
    net_profits_fy0: float | None
    operating_margin_trailing: float | None
    operating_profits_per_share: float | None

    # 每股收益
    eps_trailing: float | None
    eps_actual_fy0: float | None
    eps_forecast_fy1: float | None
    eps_growth_percent: float | None

    # 财务比率
    asset_turnover_ltm: float | None
    roa_trailing: float | None
    roe_trailing: float | None
    operating_leverage: float | None

    # 风险指标
    altman_z_score_manufacturing: float | None
    altman_z_score_non_manufacturing: float | None

    # 现金流
    ebitda_fy0: float | None
    ebitda_fy_minus_1: float | None
    cash_flow_operations_fy0: float | None
    cash_flow_operations_fy_minus_1: float | None

    # 利息与债务
    interest_expense_fy0: float | None
    effective_interest_rate: float | None
    interest_coverage_ratio: float | None
    debt_to_total_assets: float | None
    debt_to_equity: float | None

    # 流动性比率
    current_ratio: float | None
    quick_ratio: float | None

    # 估值比率
    pe_ratio_trailing: float | None
    pe_ratio_consensus: float | None
    peg_ratio: float | None

    # 股息
    dividend_yield_fy0: float | None
    dividend_payout_ratio: float | None
    dividend_local_currency: float | None
    dividend_3yr_cagr: float | None
    dividend_5yr_cagr: float | None
    dividend_10yr_cagr: float | None

    # 元数据
    created_at: ISODateTimeString | None
    updated_at: ISODateTimeString | None


# CSI300 公司列表项 (与 CSI300CompanyDict 结构相同，但不包含元数据)
CSI300CompanyListItemDict = CSI300CompanyDict


class CSI300InvestmentSummaryDict(TypedDict, total=False):
    """
    CSI300 投资摘要字典类型

    对应:
    - Model: csi300/models.py::CSI300InvestmentSummary
    - Serializer: csi300/serializers.py::CSI300InvestmentSummarySerializer
    - TypeScript: CSI300InvestmentSummary
    """

    id: int
    company: int
    company_name: str
    company_ticker: str
    im_sector: str
    industry: str

    report_date: ISODateString

    # 市场数据
    stock_price_previous_close: float
    market_cap_display: str
    recommended_action: str
    recommended_action_detail: str

    # 分析章节 (Markdown 内容)
    business_overview: str
    business_performance: str
    industry_context: str
    financial_stability: str
    key_financials_valuation: str
    big_trends_events: str
    customer_segments: str
    competitive_landscape: str
    risks_anomalies: str
    forecast_outlook: str
    investment_firms_views: str
    industry_ratio_analysis: str
    tariffs_supply_chain_risks: str
    key_takeaways: str
    sources: str

    # 元数据
    created_at: ISODateTimeString | None
    updated_at: ISODateTimeString | None


class CSI300PeerComparisonItemDict(TypedDict, total=False):
    """
    同行业公司对比项字典类型

    对应:
    - Serializer: csi300/serializers.py::CSI300IndustryPeersComparisonSerializer
    - TypeScript: CSI300PeerComparisonItem
    """

    id: int
    ticker: str
    name: str
    im_sector: str | None

    # 原始数值
    market_cap_local: float | None
    market_cap_usd: float | None
    pe_ratio_trailing: float | None
    roe_trailing: float | None
    operating_margin_trailing: float | None

    # 格式化显示值
    market_cap_display: str
    pe_ratio_display: str
    pb_ratio_display: str
    roe_display: str
    revenue_growth_display: str
    operating_margin_display: str

    # 排名信息 (动态添加)
    rank: int | None
    is_current_company: bool | None


class CSI300TargetCompanyDict(TypedDict):
    """目标公司信息"""

    id: int
    name: str
    ticker: str
    im_sector: str | None
    rank: int | None


class CSI300IndustryPeersComparisonResponseDict(TypedDict):
    """
    同行业对比响应字典类型

    对应:
    - Views: csi300/views.py::industry_peers_comparison action
    - TypeScript: CSI300IndustryPeersComparisonResponse
    """

    target_company: CSI300TargetCompanyDict
    industry: str | None
    comparison_data: list[CSI300PeerComparisonItemDict]
    total_top_companies_shown: int
    total_companies_in_industry: int


class CSI300FilterOptionsDict(TypedDict, total=False):
    """
    CSI300 筛选选项字典类型

    对应 TypeScript: FilterOptions
    """

    regions: list[str]
    im_sectors: list[str]
    industries: list[str]
    gics_industries: list[str]
    market_cap_range: dict[str, float]
    filtered_by_region: bool
    region_filter: str | None
    filtered_by_sector: bool
    sector_filter: str | None


# ============================================================================
# FRED 类型定义
# ============================================================================


class FredObservationDict(TypedDict, total=False):
    """
    FRED 指标观测数据字典类型

    对应:
    - Serializer: fred_us/serializers.py::FredUsObservationSerializer
    - TypeScript: FredObservation
    """

    date: ISODateString
    value: str
    realtime_start: ISODateString | None
    realtime_end: ISODateString | None
    indicator_name: str | None
    indicator_type: str | None
    unit: str | None
    frequency: str | None
    created_at: ISODateTimeString | None
    country: Literal["US", "JP"]


class FredLatestValueDict(TypedDict, total=False):
    """
    FRED 指标最新值数据字典类型

    对应:
    - Serializer: fred_us/serializers.py::FredUsLatestValueSerializer
    - TypeScript: FredLatestValue
    """

    value: float
    date: ISODateString
    formatted_date: str
    yoy_change: float | None
    unit: str
    indicator_name: str
    series_id: str
    country: Literal["US", "JP"]
    source: str
    last_updated: ISODateTimeString | None


class FredIndicatorResponseDict(TypedDict):
    """
    FRED 指标响应字典类型

    对应:
    - Serializer: fred_us/serializers.py::FredUsIndicatorResponseSerializer
    - TypeScript: FredUsIndicatorResponse
    """

    success: Literal[True]
    data: FredLatestValueDict
    observations: list[FredObservationDict]
    series_id: str
    count: int
    limit: int
    country: Literal["US", "JP"]


class FredStatusResponseDict(TypedDict):
    """
    FRED 状态响应字典类型

    对应:
    - Serializer: fred_us/serializers.py::FredUsStatusSerializer
    - TypeScript: FredUsStatusResponse
    """

    status: str
    database: str
    country: Literal["US", "JP"]
    total_indicators: int
    last_updated: ISODateTimeString | None
    api_key_configured: bool


class FredHealthCheckResponseDict(TypedDict):
    """
    FRED 健康检查响应字典类型

    对应:
    - Serializer: fred_us/serializers.py::FredUsHealthCheckSerializer
    - TypeScript: FredUsHealthCheckResponse
    """

    status: Literal["healthy", "unhealthy"]
    database_connection: bool
    api_connection: bool
    country: Literal["US", "JP"]
    timestamp: ISODateTimeString


class FredErrorResponseDict(TypedDict, total=False):
    """
    FRED 错误响应字典类型

    对应:
    - Serializer: fred_us/serializers.py::FredUsErrorResponseSerializer
    - TypeScript: FredUsErrorResponse
    """

    success: Literal[False]
    error: str
    country: Literal["US", "JP"]
    details: dict[str, Any] | None
    timestamp: ISODateTimeString


# ============================================================================
# BEA 类型定义
# ============================================================================


class BeaIndicatorDict(TypedDict, total=False):
    """
    BEA 指标数据字典类型

    对应:
    - Model: bea/models.py::BeaIndicator
    - TypeScript: BeaIndicator
    """

    id: int
    series_id: str
    indicator_name: str
    indicator_type: str
    table_name: str | None
    line_number: str | None
    date: ISODateString
    time_period: str
    value: float
    source: str
    unit: str | None
    frequency: str | None
    dataset_name: str | None
    metadata: dict[str, Any]
    created_at: ISODateTimeString
    updated_at: ISODateTimeString


class BeaQuarterlyDataDict(TypedDict, total=False):
    """BEA 季度数据字典类型"""

    period: str
    value: float | None
    formatted_value: str | None
    yoy_change: float | None


class BeaIndicatorResponseDict(TypedDict, total=False):
    """
    BEA 指标数据响应字典类型

    对应 TypeScript: BeaIndicatorResponse
    """

    success: bool
    series_id: str
    display_name: str
    latest_value: float | None
    latest_period: str | None
    yoy_change: float | None
    qoq_change: float | None
    unit: str
    data: list[BeaIndicatorDict]
    quarterly_data: list[BeaQuarterlyDataDict]
    error: str | None


class BeaConfigDict(TypedDict, total=False):
    """
    BEA 指标配置字典类型

    对应:
    - Model: bea/models.py::BeaIndicatorConfig
    - TypeScript: BeaIndicatorConfig
    """

    id: int
    series_id: str
    name: str
    description: str
    table_name: str
    line_description: str
    line_number: int | None
    units: str
    frequency: str
    years: str
    category: str
    fallback_value: float | None
    api_endpoint: str
    priority: int
    is_active: bool
    auto_fetch: bool
    dataset_name: str
    created_at: ISODateTimeString
    updated_at: ISODateTimeString
