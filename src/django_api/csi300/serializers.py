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

