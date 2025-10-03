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
        im_sector = self.request.query_params.get('im_sector')
        industry = self.request.query_params.get('industry')
        legacy_sub_industry = self.request.query_params.get('sub_industry')
        if not industry and legacy_sub_industry:
            industry = legacy_sub_industry
        gics_industry = self.request.query_params.get('gics_industry')
        market_cap_min = self.request.query_params.get('market_cap_min')
        market_cap_max = self.request.query_params.get('market_cap_max')
        search = self.request.query_params.get('search')
        industry_search = self.request.query_params.get('industry_search')
        
        # Debug logging
        print(f"Filtering with: im_sector='{im_sector}', industry='{industry}', industry_search='{industry_search}'")
        
        if im_sector:
            queryset = queryset.filter(im_sector__exact=im_sector)
            print(f"After IM Sector filter: {queryset.count()} companies")
        
        if industry:
            queryset = queryset.filter(industry__exact=industry)
            print(f"After Industry filter: {queryset.count()} companies")
            
        if gics_industry:
            queryset = queryset.filter(gics_industry__icontains=gics_industry)
            
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
        
        if industry_search:
            queryset = queryset.filter(
                Q(industry__icontains=industry_search)
            )
            print(f"After Industry search filter: {queryset.count()} companies")
        
        return queryset.order_by('ticker')
    
    @action(detail=False, methods=['get'])
    def filter_options(self, request):
        """Get available filter options with optional IM Sector filtering for cascading Industry options"""
        
        # Get query parameter for cascading filter
        im_sector_filter = request.query_params.get('im_sector')
        
        # Base queryset
        base_queryset = CSI300Company.objects.all()
        
        # Get unique IM sectors (not affected by filtering)
        im_sectors = list(base_queryset.exclude(
            im_sector__isnull=True
        ).exclude(
            im_sector__exact=''
        ).values_list('im_sector', flat=True).distinct().order_by('im_sector'))
        
        # Get industries (filtered by IM Sector if provided)
        industry_queryset = base_queryset.exclude(
            industry__isnull=True
        ).exclude(
            industry__exact=''
        )
        
        # Apply IM Sector filter to industries if specified
        if im_sector_filter:
            industry_queryset = industry_queryset.filter(im_sector=im_sector_filter)
        
        industries = list(industry_queryset.values_list(
            'industry', flat=True
        ).distinct().order_by('industry'))
        
        # Get unique GICS industries (not affected by IM Sector filtering)
        gics_industries = list(base_queryset.exclude(
            gics_industry__isnull=True
        ).exclude(
            gics_industry__exact=''
        ).values_list('gics_industry', flat=True).distinct().order_by('gics_industry'))
        
        # Get market cap range (not affected by IM Sector filtering)
        market_cap_range = base_queryset.exclude(
            market_cap_local__isnull=True
        ).aggregate(
            min_cap=Min('market_cap_local'),
            max_cap=Max('market_cap_local')
        )
        
        data = {
            'im_sectors': im_sectors,
            'industries': industries,
            'gics_industries': gics_industries,
            'market_cap_range': {
                'min': float(market_cap_range['min_cap']) if market_cap_range['min_cap'] else 0,
                'max': float(market_cap_range['max_cap']) if market_cap_range['max_cap'] else 0
            },
            # Add metadata about filtering state
            'filtered_by_sector': bool(im_sector_filter),
            'sector_filter': im_sector_filter
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
            
            if not company.im_sector:
                return Response(
                    {'error': 'Company industry information not available'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get all companies in the same industry
            # Order by market cap descending to calculate rankings
            all_industry_companies = CSI300Company.objects.filter(
                im_sector=company.im_sector
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
                    'im_sector': company.im_sector,
                    'rank': current_company_rank
                },
                'industry': company.im_sector,
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

