from rest_framework import serializers
from .models import CSI300Company, CSI300InvestmentSummary


class CSI300CompanySerializer(serializers.ModelSerializer):
    """CSI300 Company serializer for API responses"""
    
    class Meta:
        model = CSI300Company
        fields = '__all__'


class CSI300CompanyListSerializer(serializers.ModelSerializer):
    """Simplified serializer for company list view"""
    
    class Meta:
        model = CSI300Company
        fields = [
            'id', 'ticker', 'name', 'im_code', 'industry', 
            'market_cap_local', 'market_cap_usd', 'pe_ratio_trailing', 'roe_trailing', 'price_local_currency'
        ]


class CSI300FilterOptionsSerializer(serializers.Serializer):
    """Serializer for filter options"""
    
    im_codes = serializers.ListField(child=serializers.CharField())
    industries = serializers.ListField(child=serializers.CharField())
    sectors = serializers.ListField(child=serializers.CharField())
    market_cap_range = serializers.DictField()


class CSI300InvestmentSummarySerializer(serializers.ModelSerializer):
    """CSI300 Investment Summary serializer"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_ticker = serializers.CharField(source='company.ticker', read_only=True)
    
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
            'id', 'ticker', 'name', 'industry',
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

