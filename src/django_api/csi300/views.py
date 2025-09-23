from django.shortcuts import render
from django.db.models import Q, Min, Max
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import CSI300Company, CSI300InvestmentSummary
from .serializers import (
    CSI300CompanySerializer, 
    CSI300CompanyListSerializer,
    CSI300FilterOptionsSerializer,
    CSI300InvestmentSummarySerializer,
    CSI300IndustryPeersComparisonSerializer
)


class CSI300Pagination(PageNumberPagination):
    """Custom pagination for CSI300 API"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CSI300CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """CSI300 Company ViewSet"""
    
    queryset = CSI300Company.objects.all()
    serializer_class = CSI300CompanySerializer
    pagination_class = CSI300Pagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CSI300CompanyListSerializer
        return CSI300CompanySerializer
    
    def get_queryset(self):
        queryset = CSI300Company.objects.all()
        
        # Filtering
        im_code = self.request.query_params.get('im_code')
        industry = self.request.query_params.get('industry')
        sector = self.request.query_params.get('sector')
        market_cap_min = self.request.query_params.get('market_cap_min')
        market_cap_max = self.request.query_params.get('market_cap_max')
        search = self.request.query_params.get('search')
        
        if im_code:
            queryset = queryset.filter(im_code=im_code)
        
        if industry:
            queryset = queryset.filter(industry__icontains=industry)
            
        if sector:
            queryset = queryset.filter(sub_industry__icontains=sector)
            
        if market_cap_min:
            try:
                queryset = queryset.filter(market_cap_local__gte=float(market_cap_min))
            except (ValueError, TypeError):
                pass
                
        if market_cap_max:
            try:
                queryset = queryset.filter(market_cap_local__lte=float(market_cap_max))
            except (ValueError, TypeError):
                pass
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(ticker__icontains=search) |
                Q(naming__icontains=search)
            )
        
        return queryset.order_by('ticker')
    
    @action(detail=False, methods=['get'])
    def filter_options(self, request):
        """Get available filter options"""
        
        # Get unique IM codes
        im_codes = list(CSI300Company.objects.exclude(
            im_code__isnull=True
        ).exclude(
            im_code__exact=''
        ).values_list('im_code', flat=True).distinct().order_by('im_code'))
        
        # Get unique industries
        industries = list(CSI300Company.objects.exclude(
            industry__isnull=True
        ).exclude(
            industry__exact=''
        ).values_list('industry', flat=True).distinct().order_by('industry'))
        
        # Get unique sectors (using sub_industry)
        sectors = list(CSI300Company.objects.exclude(
            sub_industry__isnull=True
        ).exclude(
            sub_industry__exact=''
        ).values_list('sub_industry', flat=True).distinct().order_by('sub_industry'))
        
        # Get market cap range
        market_cap_range = CSI300Company.objects.exclude(
            market_cap_local__isnull=True
        ).aggregate(
            min_cap=Min('market_cap_local'),
            max_cap=Max('market_cap_local')
        )
        
        data = {
            'im_codes': im_codes,
            'industries': industries,
            'sectors': sectors,
            'market_cap_range': {
                'min': float(market_cap_range['min_cap']) if market_cap_range['min_cap'] else 0,
                'max': float(market_cap_range['max_cap']) if market_cap_range['max_cap'] else 0
            }
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search companies by name or code"""
        query = request.query_params.get('q', '')
        
        if not query:
            return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        companies = CSI300Company.objects.filter(
            Q(name__icontains=query) |
            Q(ticker__icontains=query) |
            Q(naming__icontains=query)
        ).order_by('ticker')[:10]  # Limit to 10 results for search
        
        serializer = CSI300CompanyListSerializer(companies, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def investment_summary(self, request, pk=None):
        """Get investment summary for a company"""
        try:
            company = self.get_object()
            summary = CSI300InvestmentSummary.objects.filter(company=company).first()
            
            if not summary:
                return Response(
                    {'error': 'Investment summary not found for this company'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = CSI300InvestmentSummarySerializer(summary)
            return Response(serializer.data)
            
        except CSI300Company.DoesNotExist:
            return Response(
                {'error': 'Company not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def industry_peers_comparison(self, request, pk=None):
        """Get industry peers comparison for a company"""
        try:
            company = self.get_object()
            
            if not company.industry:
                return Response(
                    {'error': 'Company industry information not available'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get all companies in the same industry
            # Order by market cap descending to calculate rankings
            all_industry_companies = CSI300Company.objects.filter(
                industry=company.industry
            ).exclude(
                market_cap_local__isnull=True
            ).order_by('-market_cap_local')
            
            # Calculate current company's rank in the industry
            current_company_rank = None
            for idx, comp in enumerate(all_industry_companies, 1):
                if comp.id == company.id:
                    current_company_rank = idx
                    break
            
            # Get top 3 companies (固定前3名，不排除任何公司)
            top_3_companies = all_industry_companies[:3]
            
            if not top_3_companies:
                return Response(
                    {'error': 'No companies found in the same industry'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Prepare comparison data with rankings
            comparison_data = []
            
            # Always add current company first
            company_serializer = CSI300IndustryPeersComparisonSerializer(company)
            company_data = company_serializer.data
            company_data['rank'] = current_company_rank
            company_data['is_current_company'] = True
            comparison_data.append(company_data)
            
            # Add top 3 companies (固定显示前3名)
            for idx, top_company in enumerate(top_3_companies, 1):
                top_serializer = CSI300IndustryPeersComparisonSerializer(top_company)
                top_data = top_serializer.data
                top_data['rank'] = idx
                top_data['is_current_company'] = (top_company.id == company.id)
                comparison_data.append(top_data)
            
            return Response({
                'target_company': {
                    'id': company.id,
                    'name': company.name,
                    'ticker': company.ticker,
                    'industry': company.industry,
                    'rank': current_company_rank
                },
                'industry': company.industry,
                'comparison_data': comparison_data,
                'total_top_companies_shown': len(top_3_companies),
                'total_companies_in_industry': all_industry_companies.count()
            })
            
        except CSI300Company.DoesNotExist:
            return Response(
                {'error': 'Company not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
def csi300_index(request):
    """CSI300 API index"""
    return Response({
        'message': 'CSI300 Companies API',
        'version': '1.0.0',
        'endpoints': {
            'companies': '/api/csi300/api/companies/',
            'company_detail': '/api/csi300/api/companies/{id}/',
            'filter_options': '/api/csi300/api/companies/filter_options/',
            'search': '/api/csi300/api/companies/search/',
        },
        'total_companies': CSI300Company.objects.count()
    })


@api_view(['GET'])
def health_check(request):
    """CSI300 health check"""
    try:
        count = CSI300Company.objects.count()
        return Response({
            'status': 'healthy',
            'service': 'CSI300 API',
            'total_companies': count,
            'database_available': True
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'service': 'CSI300 API',
            'error': str(e),
            'database_available': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

