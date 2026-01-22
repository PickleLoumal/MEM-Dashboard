"""
CSI300 Serializers - Unified Company Architecture

Serializers for the unified Company model supporting multiple exchanges.
"""

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Company, GenerationTask, InvestmentSummary

# TODO: Remove backward compatibility aliases after full migration to unified Company model
CSI300Company = Company
CSI300HSharesCompany = Company
CSI300InvestmentSummary = InvestmentSummary


class CompanySerializer(serializers.ModelSerializer):
    """Company serializer for API responses - includes all fields."""

    class Meta:
        model = Company
        fields = "__all__"


# Fields for list view - commonly used subset
COMPANY_LIST_FIELDS = [
    # Identification
    "id",
    "exchange",
    "ticker",
    "name",
    "region",
    "im_sector",
    "industry",
    "gics_industry",
    "gics_sub_industry",
    "naming",
    "business_description",
    "company_info",
    "directors",
    "currency",
    "last_trade_date",
    # Market Data
    "price_local_currency",
    "previous_close",
    "market_cap_local",
    "market_cap_usd",
    "price_52w_high",
    "price_52w_low",
    "total_return_2018_to_2025",
    # Revenue
    "total_revenue_local",
    "ltm_revenue_local",
    "ntm_revenue_local",
    # Assets & Liabilities
    "total_assets_local",
    "net_assets_local",
    "total_debt_local",
    # Profitability
    "net_profits_fy0",
    "operating_margin_trailing",
    "operating_profits_per_share",
    "roe_trailing",
    "roa_trailing",
    # Earnings Per Share
    "eps_trailing",
    "eps_actual_fy0",
    "eps_forecast_fy1",
    "eps_growth_percent",
    # Financial Ratios
    "asset_turnover_ltm",
    "operating_leverage",
    # Risk Metrics
    "altman_z_score_manufacturing",
    "altman_z_score_non_manufacturing",
    # Cash Flow
    "ebitda_fy0",
    "ebitda_fy_minus_1",
    "cash_flow_operations_fy0",
    "cash_flow_operations_fy_minus_1",
    # Interest & Debt
    "interest_expense_fy0",
    "effective_interest_rate",
    "interest_coverage_ratio",
    "debt_to_total_assets",
    "debt_to_equity",
    # Liquidity Ratios
    "current_ratio",
    "quick_ratio",
    # Valuation Ratios
    "pe_ratio_trailing",
    "pe_ratio_consensus",
    "peg_ratio",
    # Dividends
    "dividend_yield_fy0",
    "dividend_payout_ratio",
    "dividend_local_currency",
    "dividend_3yr_cagr",
    "dividend_5yr_cagr",
    "dividend_10yr_cagr",
]


class CompanyListSerializer(serializers.ModelSerializer):
    """Serializer for company list view - includes commonly used fields."""

    class Meta:
        model = Company
        fields = COMPANY_LIST_FIELDS


class FilterOptionsSerializer(serializers.Serializer):
    """Serializer for filter options response."""

    exchanges = serializers.ListField(
        child=serializers.CharField(),
        help_text="Available exchange codes (SSE, SZSE, HKEX)",
    )
    regions = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Available regions",
    )
    im_sectors = serializers.ListField(
        child=serializers.CharField(),
        help_text="Available IM sectors",
    )
    industries = serializers.ListField(
        child=serializers.CharField(),
        help_text="Available industries",
    )
    gics_industries = serializers.ListField(
        child=serializers.CharField(),
        help_text="Available GICS industries",
    )
    market_cap_range = serializers.DictField(
        help_text="Market cap range (min/max)",
    )
    filtered_by_exchange = serializers.BooleanField(
        required=False,
        help_text="Whether filtered by exchange",
    )
    filtered_by_region = serializers.BooleanField(
        required=False,
        help_text="Whether filtered by region",
    )
    filtered_by_sector = serializers.BooleanField(
        required=False,
        help_text="Whether filtered by sector",
    )
    exchange_filter = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Current exchange filter",
    )
    region_filter = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Current region filter",
    )
    sector_filter = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Current sector filter",
    )


class InvestmentSummarySerializer(serializers.ModelSerializer):
    """Investment Summary serializer with company details."""

    company_name = serializers.CharField(source="company.name", read_only=True)
    company_ticker = serializers.CharField(source="company.ticker", read_only=True)
    exchange = serializers.CharField(source="company.exchange", read_only=True)
    im_sector = serializers.CharField(source="company.im_sector", read_only=True)
    industry = serializers.CharField(source="company.industry", read_only=True)

    class Meta:
        model = InvestmentSummary
        fields = "__all__"


class IndustryPeersComparisonSerializer(serializers.ModelSerializer):
    """Serializer for industry peers comparison data (single item)."""

    market_cap_display = serializers.SerializerMethodField()
    pe_ratio_display = serializers.SerializerMethodField()
    pb_ratio_display = serializers.SerializerMethodField()
    roe_display = serializers.SerializerMethodField()
    revenue_growth_display = serializers.SerializerMethodField()
    operating_margin_display = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            "id",
            "exchange",
            "ticker",
            "name",
            "im_sector",
            "market_cap_local",
            "market_cap_usd",
            "market_cap_display",
            "pe_ratio_trailing",
            "pe_ratio_display",
            "pb_ratio_display",
            "roe_trailing",
            "roe_display",
            "revenue_growth_display",
            "operating_margin_trailing",
            "operating_margin_display",
        ]

    @extend_schema_field(str)
    def get_market_cap_display(self, obj):
        """Format market cap for display."""
        if obj.market_cap_local:
            if obj.market_cap_local >= 1000000000000:  # Trillion
                return f"{obj.market_cap_local / 1000000000000:.2f}T"
            if obj.market_cap_local >= 1000000000:  # Billion
                return f"{obj.market_cap_local / 1000000000:.2f}B"
            if obj.market_cap_local >= 1000000:  # Million
                return f"{obj.market_cap_local / 1000000:.2f}M"
            return f"{obj.market_cap_local:.2f}"
        return "N/A"

    @extend_schema_field(str)
    def get_pe_ratio_display(self, obj):
        """Format P/E ratio for display."""
        if obj.pe_ratio_trailing:
            return f"{obj.pe_ratio_trailing:.2f}"
        return "N/A"

    @extend_schema_field(str)
    def get_pb_ratio_display(self, obj):
        """Calculate and format P/B ratio for display."""
        return "N/A"

    @extend_schema_field(str)
    def get_roe_display(self, obj):
        """Format ROE for display."""
        if obj.roe_trailing:
            return f"{obj.roe_trailing:.2f}%"
        return "N/A"

    @extend_schema_field(str)
    def get_revenue_growth_display(self, obj):
        """Calculate revenue growth for display."""
        return "N/A"

    @extend_schema_field(str)
    def get_operating_margin_display(self, obj):
        """Format Operating Margin for display."""
        if obj.operating_margin_trailing:
            return f"{obj.operating_margin_trailing:.2f}%"
        return "N/A"


class PeerComparisonItemSerializer(IndustryPeersComparisonSerializer):
    """Serializer for a single peer comparison item with extra fields."""

    rank = serializers.IntegerField(read_only=True)
    is_current_company = serializers.BooleanField(read_only=True)

    class Meta(IndustryPeersComparisonSerializer.Meta):
        fields = [
            *IndustryPeersComparisonSerializer.Meta.fields,
            "rank",
            "is_current_company",
        ]


class PeerComparisonResponseSerializer(serializers.Serializer):
    """Serializer for the full peer comparison response."""

    target_company = PeerComparisonItemSerializer()
    industry = serializers.CharField()
    comparison_data = PeerComparisonItemSerializer(many=True)
    total_top_companies_shown = serializers.IntegerField()
    total_companies_in_industry = serializers.IntegerField()


# =============================================================================
# Generation Task Serializers (异步任务相关)
# =============================================================================


class TaskStatusEnum(serializers.ChoiceField):
    """任务状态枚举字段"""

    def __init__(self, **kwargs: object) -> None:
        super().__init__(choices=GenerationTask.Status.choices, **kwargs)


class GenerationTaskStartResponseSerializer(serializers.Serializer):
    """
    启动生成任务的响应序列化器

    用于 POST /generate-summary/ 的响应
    """

    status = serializers.ChoiceField(
        choices=["accepted", "error"],
        help_text="响应状态: 'accepted' 表示任务已接受, 'error' 表示错误",
    )
    message = serializers.CharField(help_text="响应消息")
    task_id = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="任务 UUID (仅当 status='accepted' 时返回)",
    )
    task_status = serializers.ChoiceField(
        choices=GenerationTask.Status.choices,
        required=False,
        allow_null=True,
        help_text="当前任务状态",
    )
    progress_percent = serializers.IntegerField(
        required=False,
        default=0,
        help_text="进度百分比 (0-100)",
    )
    progress_message = serializers.CharField(
        required=False,
        default="",
        help_text="进度消息",
    )


class GenerationTaskStatusResponseSerializer(serializers.Serializer):
    """
    任务状态查询响应序列化器

    用于 GET /task-status/{task_id}/ 的响应
    """

    status = serializers.ChoiceField(
        choices=["success", "error"],
        help_text="API 响应状态",
    )
    task_id = serializers.CharField(help_text="任务 UUID")
    task_status = serializers.ChoiceField(
        choices=GenerationTask.Status.choices,
        help_text="任务执行状态: pending, processing, completed, failed",
    )
    progress_percent = serializers.IntegerField(
        min_value=0,
        max_value=100,
        help_text="进度百分比 (0-100)",
    )
    progress_message = serializers.CharField(help_text="当前进度消息")
    company_id = serializers.IntegerField(help_text="公司 ID")
    company_name = serializers.CharField(help_text="公司名称")
    company_ticker = serializers.CharField(help_text="公司股票代码")
    exchange = serializers.CharField(
        help_text="交易所代码 (SSE, SZSE, HKEX)",
        required=False,
    )
    created_at = serializers.DateTimeField(help_text="任务创建时间")
    updated_at = serializers.DateTimeField(help_text="任务最后更新时间")
    completed_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="任务完成时间 (仅当任务完成或失败时返回)",
    )
    result = serializers.JSONField(
        required=False,
        allow_null=True,
        help_text="任务结果数据 (仅当 task_status='completed' 时返回)",
    )
    error = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="错误消息 (仅当 task_status='failed' 时返回)",
    )


# =============================================================================
# Backward Compatibility Aliases (Deprecated)
# =============================================================================

# Deprecated: Use CompanySerializer instead
CSI300CompanySerializer = CompanySerializer

# Deprecated: Use CompanyListSerializer instead
CSI300CompanyListSerializer = CompanyListSerializer

# Deprecated: Use CompanyListSerializer instead (H-shares now identified by exchange='HKEX')
CSI300HSharesCompanySerializer = CompanySerializer

# Deprecated: Use CompanyListSerializer instead
CSI300HSharesCompanyListSerializer = CompanyListSerializer

# Deprecated: Use FilterOptionsSerializer instead
CSI300FilterOptionsSerializer = FilterOptionsSerializer

# Deprecated: Use InvestmentSummarySerializer instead
CSI300InvestmentSummarySerializer = InvestmentSummarySerializer

# Deprecated: Use IndustryPeersComparisonSerializer instead
CSI300IndustryPeersComparisonSerializer = IndustryPeersComparisonSerializer

# Deprecated: Use PeerComparisonItemSerializer instead
CSI300PeerComparisonItemSerializer = PeerComparisonItemSerializer

# Deprecated: Use PeerComparisonResponseSerializer instead
CSI300PeerComparisonResponseSerializer = PeerComparisonResponseSerializer

# For backward compatibility - old field list name
CSI300_COMPANY_LIST_FIELDS = COMPANY_LIST_FIELDS
