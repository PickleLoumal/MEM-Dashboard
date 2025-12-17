from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import CSI300Company, CSI300HSharesCompany, CSI300InvestmentSummary, GenerationTask


class CSI300CompanySerializer(serializers.ModelSerializer):
    """CSI300 Company serializer for API responses"""

    class Meta:
        model = CSI300Company
        fields = "__all__"


CSI300_COMPANY_LIST_FIELDS = [
    # Basic Information
    "id",
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


class CSI300CompanyListSerializer(serializers.ModelSerializer):
    """Serializer for company list view - includes all fields that exist in the database model"""

    class Meta:
        model = CSI300Company
        fields = CSI300_COMPANY_LIST_FIELDS


class CSI300HSharesCompanySerializer(serializers.ModelSerializer):
    """Serializer for H-shares company detail responses"""

    class Meta:
        model = CSI300HSharesCompany
        fields = "__all__"


class CSI300HSharesCompanyListSerializer(serializers.ModelSerializer):
    """Serializer for H-shares list responses"""

    class Meta:
        model = CSI300HSharesCompany
        fields = CSI300_COMPANY_LIST_FIELDS


class CSI300FilterOptionsSerializer(serializers.Serializer):
    """Serializer for filter options"""

    regions = serializers.ListField(child=serializers.CharField(), required=False)
    im_sectors = serializers.ListField(child=serializers.CharField())
    industries = serializers.ListField(child=serializers.CharField())
    gics_industries = serializers.ListField(child=serializers.CharField())
    market_cap_range = serializers.DictField()
    filtered_by_region = serializers.BooleanField(required=False)
    filtered_by_sector = serializers.BooleanField(required=False)
    region_filter = serializers.CharField(required=False, allow_null=True)
    sector_filter = serializers.CharField(required=False, allow_null=True)


class CSI300InvestmentSummarySerializer(serializers.ModelSerializer):
    """CSI300 Investment Summary serializer"""

    company_name = serializers.CharField(source="company.name", read_only=True)
    company_ticker = serializers.CharField(source="company.ticker", read_only=True)
    im_sector = serializers.CharField(source="company.im_sector", read_only=True)
    industry = serializers.CharField(source="company.industry", read_only=True)

    class Meta:
        model = CSI300InvestmentSummary
        fields = "__all__"


class CSI300IndustryPeersComparisonSerializer(serializers.ModelSerializer):
    """Serializer for industry peers comparison data (single item)"""

    market_cap_display = serializers.SerializerMethodField()
    pe_ratio_display = serializers.SerializerMethodField()
    pb_ratio_display = serializers.SerializerMethodField()
    roe_display = serializers.SerializerMethodField()
    revenue_growth_display = serializers.SerializerMethodField()
    operating_margin_display = serializers.SerializerMethodField()

    class Meta:
        model = CSI300Company
        fields = [
            "id",
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
        """Format market cap for display"""
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
        """Format P/E ratio for display"""
        if obj.pe_ratio_trailing:
            return f"{obj.pe_ratio_trailing:.2f}"
        return "N/A"

    @extend_schema_field(str)
    def get_pb_ratio_display(self, obj):
        """Calculate and format P/B ratio for display"""
        # Note: P/B ratio calculation would need book value per share
        # For now, return placeholder
        return "N/A"

    @extend_schema_field(str)
    def get_roe_display(self, obj):
        """Format ROE for display"""
        if obj.roe_trailing:
            return f"{obj.roe_trailing:.2f}%"
        return "N/A"

    @extend_schema_field(str)
    def get_revenue_growth_display(self, obj):
        """Calculate revenue growth for display"""
        # Revenue growth calculation would need historical data
        # For now, return placeholder
        return "N/A"

    @extend_schema_field(str)
    def get_operating_margin_display(self, obj):
        """Format Operating Margin for display"""
        if obj.operating_margin_trailing:
            return f"{obj.operating_margin_trailing:.2f}%"
        return "N/A"


class CSI300PeerComparisonItemSerializer(CSI300IndustryPeersComparisonSerializer):
    """Serializer for a single peer comparison item with extra fields"""

    rank = serializers.IntegerField(read_only=True)
    is_current_company = serializers.BooleanField(read_only=True)

    class Meta(CSI300IndustryPeersComparisonSerializer.Meta):
        fields = [
            *CSI300IndustryPeersComparisonSerializer.Meta.fields,
            "rank",
            "is_current_company",
        ]


class CSI300PeerComparisonResponseSerializer(serializers.Serializer):
    """Serializer for the full peer comparison response"""

    target_company = CSI300PeerComparisonItemSerializer()
    industry = serializers.CharField()
    comparison_data = CSI300PeerComparisonItemSerializer(many=True)
    total_top_companies_shown = serializers.IntegerField()
    total_companies_in_industry = serializers.IntegerField()


# ============================================
# Generation Task Serializers (异步任务相关)
# ============================================


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
