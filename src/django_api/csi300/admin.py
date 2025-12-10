from django.contrib import admin

from .models import CSI300Company, CSI300HSharesCompany, CSI300InvestmentSummary


@admin.register(CSI300Company)
class CSI300CompanyAdmin(admin.ModelAdmin):
    """Admin interface for CSI300 companies"""

    list_display = [
        "ticker",
        "name",
        "region",
        "im_sector",
        "price_local_currency",
        "market_cap_local",
        "pe_ratio_trailing",
        "roe_trailing",
        "updated_at",
    ]
    list_filter = [
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
        ("Basic Information", {"fields": ("ticker", "name", "region", "naming")}),
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
        ("Valuation Ratios", {"fields": ("pe_ratio_trailing", "pe_ratio_consensus", "peg_ratio")}),
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
        ("Company Details", {"fields": ("business_description", "company_info", "directors")}),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(CSI300HSharesCompany)
class CSI300HSharesCompanyAdmin(admin.ModelAdmin):
    """Admin interface for CSI300 H-Shares companies"""

    list_display = [
        "ticker",
        "name",
        "region",
        "im_sector",
        "price_local_currency",
        "market_cap_usd",
        "pe_ratio_trailing",
        "roe_trailing",
        "updated_at",
    ]
    list_filter = [
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
        ("Basic Information", {"fields": ("ticker", "name", "region", "naming")}),
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
        ("Valuation Ratios", {"fields": ("pe_ratio_trailing", "pe_ratio_consensus", "peg_ratio")}),
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
        ("Company Details", {"fields": ("business_description", "company_info", "directors")}),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(CSI300InvestmentSummary)
class CSI300InvestmentSummaryAdmin(admin.ModelAdmin):
    """Admin interface for CSI300 investment summaries"""

    list_display = [
        "company",
        "report_date",
        "recommended_action",
        "market_cap_display",
        "updated_at",
    ]
    list_filter = ["report_date", "recommended_action", "company__im_sector"]
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
        ("Risk Assessment", {"fields": ("tariffs_supply_chain_risks", "key_takeaways", "sources")}),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
