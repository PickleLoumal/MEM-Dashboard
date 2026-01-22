"""
CSI300 Admin - Unified Company Architecture

Admin interface for the unified Company model supporting multiple exchanges.
"""

from django.contrib import admin

from .models import Company, GenerationTask, InvestmentSummary


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Admin interface for companies (all exchanges)"""

    list_display = [
        "ticker",
        "name",
        "exchange",
        "region",
        "im_sector",
        "price_local_currency",
        "market_cap_local",
        "pe_ratio_trailing",
        "roe_trailing",
        "updated_at",
    ]
    list_filter = [
        "exchange",
        "region",
        "im_sector",
        "gics_industry",
        "industry",
        "currency",
        "last_trade_date",
    ]
    search_fields = ["ticker", "name", "naming", "im_sector", "gics_industry", "region"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Identification",
            {"fields": ("exchange", "ticker", "name", "region", "naming")},
        ),
        (
            "Classification",
            {"fields": ("im_sector", "industry", "gics_industry", "gics_sub_industry")},
        ),
        (
            "Price Information",
            {
                "fields": (
                    "price_local_currency",
                    "previous_close",
                    "currency",
                    "last_trade_date",
                    "price_52w_high",
                    "price_52w_low",
                    "total_return_2018_to_2025",
                )
            },
        ),
        (
            "Market Cap & Revenue",
            {
                "fields": (
                    "market_cap_local",
                    "market_cap_usd",
                    "total_revenue_local",
                    "ltm_revenue_local",
                    "ntm_revenue_local",
                )
            },
        ),
        (
            "Assets & Liabilities",
            {
                "fields": (
                    "total_assets_local",
                    "net_assets_local",
                    "total_debt_local",
                    "asset_turnover_ltm",
                )
            },
        ),
        (
            "Profitability",
            {
                "fields": (
                    "net_profits_fy0",
                    "operating_margin_trailing",
                    "operating_profits_per_share",
                    "roa_trailing",
                    "roe_trailing",
                    "operating_leverage",
                )
            },
        ),
        (
            "Earnings Per Share",
            {
                "fields": (
                    "eps_trailing",
                    "eps_actual_fy0",
                    "eps_forecast_fy1",
                    "eps_growth_percent",
                )
            },
        ),
        (
            "Valuation Ratios",
            {"fields": ("pe_ratio_trailing", "pe_ratio_consensus", "peg_ratio")},
        ),
        (
            "Risk Metrics",
            {"fields": ("altman_z_score_manufacturing", "altman_z_score_non_manufacturing")},
        ),
        (
            "Cash Flow",
            {
                "fields": (
                    "ebitda_fy0",
                    "ebitda_fy_minus_1",
                    "cash_flow_operations_fy0",
                    "cash_flow_operations_fy_minus_1",
                )
            },
        ),
        (
            "Debt & Interest",
            {
                "fields": (
                    "interest_expense_fy0",
                    "effective_interest_rate",
                    "interest_coverage_ratio",
                    "debt_to_total_assets",
                    "debt_to_equity",
                )
            },
        ),
        ("Liquidity Ratios", {"fields": ("current_ratio", "quick_ratio")}),
        (
            "Dividends",
            {
                "fields": (
                    "dividend_yield_fy0",
                    "dividend_payout_ratio",
                    "dividend_local_currency",
                    "dividend_3yr_cagr",
                    "dividend_5yr_cagr",
                    "dividend_10yr_cagr",
                )
            },
        ),
        (
            "Company Details",
            {"fields": ("business_description", "company_info", "directors")},
        ),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(InvestmentSummary)
class InvestmentSummaryAdmin(admin.ModelAdmin):
    """Admin interface for investment summaries"""

    list_display = [
        "company",
        "get_exchange",
        "report_date",
        "recommended_action",
        "market_cap_display",
        "updated_at",
    ]
    list_filter = [
        "report_date",
        "recommended_action",
        "company__exchange",
        "company__im_sector",
    ]
    search_fields = ["company__name", "company__ticker", "recommended_action"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "company",
                    "report_date",
                    "stock_price_previous_close",
                    "market_cap_display",
                )
            },
        ),
        ("Recommendation", {"fields": ("recommended_action", "recommended_action_detail")}),
        (
            "Analysis",
            {
                "fields": (
                    "business_overview",
                    "business_performance",
                    "industry_context",
                    "financial_stability",
                    "key_financials_valuation",
                    "big_trends_events",
                )
            },
        ),
        (
            "Market Analysis",
            {
                "fields": (
                    "customer_segments",
                    "competitive_landscape",
                    "risks_anomalies",
                    "forecast_outlook",
                    "investment_firms_views",
                    "industry_ratio_analysis",
                )
            },
        ),
        (
            "Risk Assessment",
            {"fields": ("tariffs_supply_chain_risks", "key_takeaways", "sources")},
        ),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Exchange", ordering="company__exchange")
    def get_exchange(self, obj):
        """Display the company's exchange."""
        return obj.company.exchange


@admin.register(GenerationTask)
class GenerationTaskAdmin(admin.ModelAdmin):
    """Admin interface for generation tasks"""

    list_display = [
        "task_id",
        "company",
        "get_exchange",
        "status",
        "progress_percent",
        "created_at",
        "completed_at",
    ]
    list_filter = ["status", "company__exchange", "created_at", "completed_at"]
    search_fields = ["task_id", "company__name", "company__ticker"]
    readonly_fields = [
        "task_id",
        "created_at",
        "updated_at",
        "completed_at",
        "result_data",
    ]

    fieldsets = (
        (
            "Task Information",
            {"fields": ("task_id", "company", "status")},
        ),
        (
            "Progress",
            {"fields": ("progress_percent", "progress_message")},
        ),
        (
            "Result",
            {
                "fields": ("result_data", "error_message"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at", "completed_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="Exchange", ordering="company__exchange")
    def get_exchange(self, obj):
        """Display the company's exchange."""
        return obj.company.exchange
