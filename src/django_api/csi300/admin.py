from django.contrib import admin
from .models import CSI300Company, CSI300InvestmentSummary


@admin.register(CSI300Company)
class CSI300CompanyAdmin(admin.ModelAdmin):
    """Admin interface for CSI300 companies"""
    
    list_display = [
        'ticker', 'name', 'industry', 'market_cap_local', 
        'pe_ratio_trailing', 'roe_trailing', 'updated_at'
    ]
    list_filter = ['industry', 'gics_industry', 'im_code']
    search_fields = ['ticker', 'name', 'naming', 'industry']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('ticker', 'name', 'naming')
        }),
        ('Classification', {
            'fields': ('im_code', 'industry', 'sub_industry', 'gics_industry', 'gics_sub_industry')
        }),
        ('Financial Metrics', {
            'fields': ('market_cap_local', 'market_cap_usd', 'total_assets_local', 'total_revenue_local', 'net_profits_fy0')
        }),
        ('Financial Ratios', {
            'fields': ('pe_ratio_trailing', 'pe_ratio_consensus', 'roe_trailing', 'roa_trailing', 'debt_to_equity')
        }),
        ('Company Details', {
            'fields': ('business_description', 'company_info', 'directors')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CSI300InvestmentSummary)
class CSI300InvestmentSummaryAdmin(admin.ModelAdmin):
    """Admin interface for CSI300 investment summaries"""
    
    list_display = [
        'company', 'report_date', 'recommended_action', 'market_cap_display', 'updated_at'
    ]
    list_filter = ['report_date', 'recommended_action', 'company__industry']
    search_fields = ['company__name', 'company__ticker', 'recommended_action']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('company', 'report_date', 'stock_price_previous_close', 'market_cap_display')
        }),
        ('Recommendation', {
            'fields': ('recommended_action', 'recommended_action_detail')
        }),
        ('Analysis', {
            'fields': (
                'business_overview', 'business_performance', 'industry_context', 
                'financial_stability', 'key_financials_valuation', 'big_trends_events'
            )
        }),
        ('Market Analysis', {
            'fields': (
                'customer_segments', 'competitive_landscape', 'risks_anomalies', 
                'forecast_outlook', 'investment_firms_views', 'industry_ratio_analysis'
            )
        }),
        ('Risk Assessment', {
            'fields': ('tariffs_supply_chain_risks', 'key_takeaways', 'sources')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

