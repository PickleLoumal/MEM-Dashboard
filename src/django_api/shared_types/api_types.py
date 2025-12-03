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
    TypedDict,
    Literal,
    List,
    Dict,
    Any,
    Optional,
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
    ticker: Optional[str]
    region: Optional[str]
    im_sector: Optional[str]
    industry: Optional[str]
    gics_industry: Optional[str]
    gics_sub_industry: Optional[str]
    
    # 公司详情
    naming: Optional[str]
    business_description: Optional[str]
    company_info: Optional[str]
    directors: Optional[str]
    
    # 价格信息
    price_local_currency: Optional[float]
    previous_close: Optional[float]
    currency: Optional[str]
    total_return_2018_to_2025: Optional[float]
    last_trade_date: Optional[ISODateString]
    price_52w_high: Optional[float]
    price_52w_low: Optional[float]
    
    # 市值
    market_cap_local: Optional[float]
    market_cap_usd: Optional[float]
    
    # 营收
    total_revenue_local: Optional[float]
    ltm_revenue_local: Optional[float]
    ntm_revenue_local: Optional[float]
    
    # 资产负债
    total_assets_local: Optional[float]
    net_assets_local: Optional[float]
    total_debt_local: Optional[float]
    
    # 盈利能力
    net_profits_fy0: Optional[float]
    operating_margin_trailing: Optional[float]
    operating_profits_per_share: Optional[float]
    
    # 每股收益
    eps_trailing: Optional[float]
    eps_actual_fy0: Optional[float]
    eps_forecast_fy1: Optional[float]
    eps_growth_percent: Optional[float]
    
    # 财务比率
    asset_turnover_ltm: Optional[float]
    roa_trailing: Optional[float]
    roe_trailing: Optional[float]
    operating_leverage: Optional[float]
    
    # 风险指标
    altman_z_score_manufacturing: Optional[float]
    altman_z_score_non_manufacturing: Optional[float]
    
    # 现金流
    ebitda_fy0: Optional[float]
    ebitda_fy_minus_1: Optional[float]
    cash_flow_operations_fy0: Optional[float]
    cash_flow_operations_fy_minus_1: Optional[float]
    
    # 利息与债务
    interest_expense_fy0: Optional[float]
    effective_interest_rate: Optional[float]
    interest_coverage_ratio: Optional[float]
    debt_to_total_assets: Optional[float]
    debt_to_equity: Optional[float]
    
    # 流动性比率
    current_ratio: Optional[float]
    quick_ratio: Optional[float]
    
    # 估值比率
    pe_ratio_trailing: Optional[float]
    pe_ratio_consensus: Optional[float]
    peg_ratio: Optional[float]
    
    # 股息
    dividend_yield_fy0: Optional[float]
    dividend_payout_ratio: Optional[float]
    dividend_local_currency: Optional[float]
    dividend_3yr_cagr: Optional[float]
    dividend_5yr_cagr: Optional[float]
    dividend_10yr_cagr: Optional[float]
    
    # 元数据
    created_at: Optional[ISODateTimeString]
    updated_at: Optional[ISODateTimeString]


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
    created_at: Optional[ISODateTimeString]
    updated_at: Optional[ISODateTimeString]


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
    im_sector: Optional[str]
    
    # 原始数值
    market_cap_local: Optional[float]
    market_cap_usd: Optional[float]
    pe_ratio_trailing: Optional[float]
    roe_trailing: Optional[float]
    operating_margin_trailing: Optional[float]
    
    # 格式化显示值
    market_cap_display: str
    pe_ratio_display: str
    pb_ratio_display: str
    roe_display: str
    revenue_growth_display: str
    operating_margin_display: str
    
    # 排名信息 (动态添加)
    rank: Optional[int]
    is_current_company: Optional[bool]


class CSI300TargetCompanyDict(TypedDict):
    """目标公司信息"""
    id: int
    name: str
    ticker: str
    im_sector: Optional[str]
    rank: Optional[int]


class CSI300IndustryPeersComparisonResponseDict(TypedDict):
    """
    同行业对比响应字典类型
    
    对应:
    - Views: csi300/views.py::industry_peers_comparison action
    - TypeScript: CSI300IndustryPeersComparisonResponse
    """
    target_company: CSI300TargetCompanyDict
    industry: Optional[str]
    comparison_data: List[CSI300PeerComparisonItemDict]
    total_top_companies_shown: int
    total_companies_in_industry: int


class CSI300FilterOptionsDict(TypedDict, total=False):
    """
    CSI300 筛选选项字典类型
    
    对应 TypeScript: FilterOptions
    """
    regions: List[str]
    im_sectors: List[str]
    industries: List[str]
    gics_industries: List[str]
    market_cap_range: Dict[str, float]
    filtered_by_region: bool
    region_filter: Optional[str]
    filtered_by_sector: bool
    sector_filter: Optional[str]


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
    realtime_start: Optional[ISODateString]
    realtime_end: Optional[ISODateString]
    indicator_name: Optional[str]
    indicator_type: Optional[str]
    unit: Optional[str]
    frequency: Optional[str]
    created_at: Optional[ISODateTimeString]
    country: Literal['US', 'JP']


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
    yoy_change: Optional[float]
    unit: str
    indicator_name: str
    series_id: str
    country: Literal['US', 'JP']
    source: str
    last_updated: Optional[ISODateTimeString]


class FredIndicatorResponseDict(TypedDict):
    """
    FRED 指标响应字典类型
    
    对应:
    - Serializer: fred_us/serializers.py::FredUsIndicatorResponseSerializer
    - TypeScript: FredUsIndicatorResponse
    """
    success: Literal[True]
    data: FredLatestValueDict
    observations: List[FredObservationDict]
    series_id: str
    count: int
    limit: int
    country: Literal['US', 'JP']


class FredStatusResponseDict(TypedDict):
    """
    FRED 状态响应字典类型
    
    对应:
    - Serializer: fred_us/serializers.py::FredUsStatusSerializer
    - TypeScript: FredUsStatusResponse
    """
    status: str
    database: str
    country: Literal['US', 'JP']
    total_indicators: int
    last_updated: Optional[ISODateTimeString]
    api_key_configured: bool


class FredHealthCheckResponseDict(TypedDict):
    """
    FRED 健康检查响应字典类型
    
    对应:
    - Serializer: fred_us/serializers.py::FredUsHealthCheckSerializer
    - TypeScript: FredUsHealthCheckResponse
    """
    status: Literal['healthy', 'unhealthy']
    database_connection: bool
    api_connection: bool
    country: Literal['US', 'JP']
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
    country: Literal['US', 'JP']
    details: Optional[Dict[str, Any]]
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
    table_name: Optional[str]
    line_number: Optional[str]
    date: ISODateString
    time_period: str
    value: float
    source: str
    unit: Optional[str]
    frequency: Optional[str]
    dataset_name: Optional[str]
    metadata: Dict[str, Any]
    created_at: ISODateTimeString
    updated_at: ISODateTimeString


class BeaQuarterlyDataDict(TypedDict, total=False):
    """BEA 季度数据字典类型"""
    period: str
    value: Optional[float]
    formatted_value: Optional[str]
    yoy_change: Optional[float]


class BeaIndicatorResponseDict(TypedDict, total=False):
    """
    BEA 指标数据响应字典类型
    
    对应 TypeScript: BeaIndicatorResponse
    """
    success: bool
    series_id: str
    display_name: str
    latest_value: Optional[float]
    latest_period: Optional[str]
    yoy_change: Optional[float]
    qoq_change: Optional[float]
    unit: str
    data: List[BeaIndicatorDict]
    quarterly_data: List[BeaQuarterlyDataDict]
    error: Optional[str]


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
    line_number: Optional[int]
    units: str
    frequency: str
    years: str
    category: str
    fallback_value: Optional[float]
    api_endpoint: str
    priority: int
    is_active: bool
    auto_fetch: bool
    dataset_name: str
    created_at: ISODateTimeString
    updated_at: ISODateTimeString

