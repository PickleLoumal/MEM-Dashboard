from rest_framework import serializers
from .models import CSI300Company, CSI300HSharesCompany, CSI300InvestmentSummary


class CSI300CompanySerializer(serializers.ModelSerializer):
    """CSI300 Company serializer for API responses"""
    
    class Meta:
        model = CSI300Company
        fields = '__all__'


CSI300_COMPANY_LIST_FIELDS = [
    # Basic Information
    'id', 'ticker', 'name', 'region', 'im_sector', 'industry', 'gics_industry', 'gics_sub_industry',
    'naming', 'business_description', 'company_info', 'directors',
    'currency', 'last_trade_date',
    
    # Market Data
    'price_local_currency', 'market_cap_local', 'market_cap_usd',
    'price_52w_high', 'price_52w_low', 'total_return_2018_to_2025',
    
    # Revenue
    'total_revenue_local', 'ltm_revenue_local', 'ntm_revenue_local',
    
    # Assets & Liabilities
    'total_assets_local', 'net_assets_local', 'total_debt_local',
    
    # Profitability
    'net_profits_fy0', 'operating_margin_trailing', 'operating_profits_per_share',
    'roe_trailing', 'roa_trailing',
    
    # Earnings Per Share
    'eps_trailing', 'eps_actual_fy0', 'eps_forecast_fy1', 'eps_growth_percent',
    
    # Financial Ratios
    'asset_turnover_ltm', 'operating_leverage',
    
    # Risk Metrics
    'altman_z_score_manufacturing', 'altman_z_score_non_manufacturing',
    
    # Cash Flow
    'ebitda_fy0', 'ebitda_fy_minus_1',
    'cash_flow_operations_fy0', 'cash_flow_operations_fy_minus_1',
    
    # Interest & Debt
    'interest_expense_fy0', 'effective_interest_rate',
    'interest_coverage_ratio', 'debt_to_total_assets', 'debt_to_equity',
    
    # Liquidity Ratios
    'current_ratio', 'quick_ratio',
    
    # Valuation Ratios
    'pe_ratio_trailing', 'pe_ratio_consensus', 'peg_ratio',
    
    # Dividends
    'dividend_yield_fy0', 'dividend_payout_ratio', 'dividend_local_currency',
    'dividend_3yr_cagr', 'dividend_5yr_cagr', 'dividend_10yr_cagr'
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
        fields = '__all__'


class CSI300HSharesCompanyListSerializer(serializers.ModelSerializer):
    """Serializer for H-shares list responses"""
    
    class Meta:
        model = CSI300HSharesCompany
        fields = CSI300_COMPANY_LIST_FIELDS


class CSI300FilterOptionsSerializer(serializers.Serializer):
    """Serializer for filter options"""
    
    im_sectors = serializers.ListField(child=serializers.CharField())
    industries = serializers.ListField(child=serializers.CharField())
    gics_industries = serializers.ListField(child=serializers.CharField())
    market_cap_range = serializers.DictField()


class CSI300InvestmentSummarySerializer(serializers.ModelSerializer):
    """CSI300 Investment Summary serializer"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_ticker = serializers.CharField(source='company.ticker', read_only=True)
    im_sector = serializers.CharField(source='company.im_sector', read_only=True)
    industry = serializers.CharField(source='company.industry', read_only=True)
    
    class Meta:
        model = CSI300InvestmentSummary
        fields = '__all__'


class CSI300IndustryPeersComparisonSerializer(serializers.ModelSerializer):
    """Serializer for industry peers comparison data"""
    
    market_cap_display = serializers.SerializerMethodField()
    pe_ratio_display = serializers.SerializerMethodField()
    pb_ratio_display = serializers.SerializerMethodField()
    roe_display = serializers.SerializerMethodField()
    revenue_growth_display = serializers.SerializerMethodField()
    operating_margin_display = serializers.SerializerMethodField()
    
    class Meta:
        model = CSI300Company
        fields = [
            'id', 'ticker', 'name', 'im_sector',
            'market_cap_local', 'market_cap_usd', 'market_cap_display',
            'pe_ratio_trailing', 'pe_ratio_display',
            'pb_ratio_display', 
            'roe_trailing', 'roe_display',
            'revenue_growth_display', 'operating_margin_trailing', 'operating_margin_display'
        ]
    
    def get_market_cap_display(self, obj):
        """Format market cap for display"""
        if obj.market_cap_local:
            if obj.market_cap_local >= 1000000000000:  # Trillion
                return f"{obj.market_cap_local / 1000000000000:.2f}T"
            elif obj.market_cap_local >= 1000000000:  # Billion
                return f"{obj.market_cap_local / 1000000000:.2f}B"
            elif obj.market_cap_local >= 1000000:  # Million
                return f"{obj.market_cap_local / 1000000:.2f}M"
            else:
                return f"{obj.market_cap_local:.2f}"
        return "N/A"
    
    def get_pe_ratio_display(self, obj):
        """Format P/E ratio for display"""
        if obj.pe_ratio_trailing:
            return f"{obj.pe_ratio_trailing:.2f}"
        return "N/A"
    
    def get_pb_ratio_display(self, obj):
        """Calculate and format P/B ratio for display"""
        # Note: P/B ratio calculation would need book value per share
        # For now, return placeholder
        return "N/A"
    
    def get_roe_display(self, obj):
        """Format ROE for display"""
        if obj.roe_trailing:
            return f"{obj.roe_trailing:.2f}%"
        return "N/A"
    
    def get_revenue_growth_display(self, obj):
        """Calculate revenue growth for display"""
        # Revenue growth calculation would need historical data
        # For now, return placeholder
        return "N/A"
    
    def get_operating_margin_display(self, obj):
        """Format Operating Margin for display"""
        if obj.operating_margin_trailing:
            return f"{obj.operating_margin_trailing:.2f}%"
        return "N/A"
