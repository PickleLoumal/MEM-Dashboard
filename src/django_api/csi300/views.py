"""
CSI300 API Views

提供 CSI300 指数成分股的 REST API 端点。

类型注解说明:
- 所有公共方法都有完整的类型注解
- 使用 shared_types 模块中定义的类型
- Response 返回值类型为 rest_framework.response.Response

对应前端类型: csi300-app/src/shared/api-types/csi300.types.ts
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type, Union, cast

from django.db.models import Q, Min, Max
from django.db.models.query import QuerySet
from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import Serializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .models import CSI300Company, CSI300HSharesCompany, CSI300InvestmentSummary
from .serializers import (
    CSI300CompanySerializer, 
    CSI300CompanyListSerializer,
    CSI300HSharesCompanySerializer,
    CSI300HSharesCompanyListSerializer,
    CSI300FilterOptionsSerializer,
    CSI300InvestmentSummarySerializer,
    CSI300IndustryPeersComparisonSerializer
)

# 类型别名
# 注意: Django 模型的动态特性（如 .objects 管理器）在静态类型检查时可能显示警告
# 这些警告不影响运行时行为
SerializerClass = Type[Serializer[Any]]


class CSI300Pagination(PageNumberPagination):
    """
    CSI300 API 分页配置
    
    配置:
    - 默认每页 20 条记录
    - 最大每页 100 条记录
    - 通过 page_size 查询参数自定义每页数量
    """
    page_size: int = 20
    page_size_query_param: str = 'page_size'
    max_page_size: int = 100


class CSI300CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    CSI300 公司数据 ViewSet
    
    提供 CSI300 指数成分股的只读 API 端点:
    - list: 获取公司列表 (支持筛选和分页)
    - retrieve: 获取单个公司详情
    - filter_options: 获取筛选选项
    - search: 搜索公司
    - investment_summary: 获取投资摘要
    - industry_peers_comparison: 获取同行业对比
    
    类型注解:
    - 所有方法返回 Response 对象
    - 查询参数通过 request.query_params 获取
    """
    
    queryset: QuerySet[CSI300Company] = CSI300Company.objects.all()
    serializer_class: SerializerClass = CSI300CompanySerializer
    pagination_class: Type[PageNumberPagination] = CSI300Pagination
    
    def get_serializer_class(self) -> SerializerClass:
        """
        根据请求动态返回序列化器类
        
        Returns:
            针对 list/retrieve 动作和 H股请求返回对应的序列化器
        """
        if self.action == 'list':
            if self._is_hshares_request():
                return CSI300HSharesCompanyListSerializer
            return CSI300CompanyListSerializer
        if self.action == 'retrieve' and self._is_hshares_request():
            return CSI300HSharesCompanySerializer
        return CSI300CompanySerializer
    
    def _normalize_region(self, region_value: Optional[str]) -> Optional[str]:
        """
        标准化地区参数值
        
        Args:
            region_value: 原始地区参数值
            
        Returns:
            标准化后的地区名称，如 'Hong Kong'
        """
        if not region_value:
            return None
        normalized = region_value.strip()
        if normalized.lower() == 'hong kong (h-shares)':
            return 'Hong Kong'
        return normalized
    
    def _is_hshares_request(self) -> bool:
        """
        判断当前请求是否为 H股数据请求
        
        Returns:
            如果请求的 region 参数为 Hong Kong 则返回 True
        """
        region = self._normalize_region(self.request.query_params.get('region'))
        if not region:
            return False
        return region.lower() == 'hong kong'
    
    def get_queryset(self) -> Any:
        """
        获取查询集，根据请求参数动态筛选
        
        支持的筛选参数:
        - region: 地区 (Mainland China, Hong Kong)
        - im_sector: IM 行业分类
        - industry: 细分行业
        - gics_industry: GICS 行业分类
        - market_cap_min/max: 市值范围
        - search: 公司名称/代码搜索
        - industry_search: 行业名称搜索
        
        Returns:
            QuerySet: 筛选后的公司查询集
        """
        use_hshares: bool = self._is_hshares_request()
        queryset = (
            CSI300HSharesCompany.objects.all() if use_hshares 
            else CSI300Company.objects.all()
        )
        
        # 获取筛选参数 (QueryDict.get 可能返回 str 或 None)
        region = self._normalize_region(self.request.query_params.get('region'))
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
        
        if region:
            queryset = queryset.filter(region__iexact=region)
            print(f"After Region filter ('{region}'): {queryset.count()} companies")
        
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
    
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        获取单个公司详情
        
        Args:
            request: DRF 请求对象
            *args: 位置参数
            **kwargs: 关键字参数，包含 pk (公司 ID)
            
        Returns:
            Response: 包含公司详情的响应
            
        Raises:
            Http404: 当公司不存在时
        """
        pk = kwargs.get(self.lookup_field, None)
        if pk is None:
            raise Http404("Company identifier is required")
        
        region = self._normalize_region(request.query_params.get('region'))
        prefer_hshares: bool = bool(region and region.lower() == 'hong kong')
        
        primary_model = CSI300HSharesCompany if prefer_hshares else CSI300Company
        primary_serializer = CSI300HSharesCompanySerializer if prefer_hshares else CSI300CompanySerializer
        fallback_model = CSI300Company if prefer_hshares else CSI300HSharesCompany
        fallback_serializer = CSI300CompanySerializer if prefer_hshares else CSI300HSharesCompanySerializer
        
        instance = primary_model.objects.filter(pk=pk).first()
        serializer_class = primary_serializer
        
        if instance is None:
            instance = fallback_model.objects.filter(pk=pk).first()
            serializer_class = fallback_serializer if instance else primary_serializer
        
        if instance is None:
            raise Http404("Company not found")
        
        serializer = serializer_class(instance, context=self.get_serializer_context())
        return Response(serializer.data)
    
    @extend_schema(
        responses={200: CSI300FilterOptionsSerializer},
        parameters=[
            OpenApiParameter(name='region', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='im_sector', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ]
    )
    @action(detail=False, methods=['get'])
    def filter_options(self, request: Request) -> Response:
        """
        获取可用的筛选选项
        
        支持级联筛选：
        - 根据 region 返回对应地区的选项
        - 根据 im_sector 返回对应行业的细分选项
        
        Args:
            request: DRF 请求对象
            
        Returns:
            Response: 包含筛选选项的响应
            {
                regions: List[str],
                im_sectors: List[str],
                industries: List[str],
                gics_industries: List[str],
                market_cap_range: { min: float, max: float },
                filtered_by_region: bool,
                filtered_by_sector: bool
            }
        """
        region_filter = self._normalize_region(request.query_params.get('region'))
        im_sector_filter = request.query_params.get('im_sector')
        base_queryset = (
            CSI300HSharesCompany.objects.all() if region_filter and region_filter.lower() == 'hong kong' 
            else CSI300Company.objects.all()
        )

        if region_filter:
            base_queryset = base_queryset.filter(region__iexact=region_filter)

        im_sectors = list(base_queryset.exclude(
            im_sector__isnull=True
        ).exclude(
            im_sector__exact=''
        ).values_list('im_sector', flat=True).distinct().order_by('im_sector'))

        industry_queryset = base_queryset.exclude(
            industry__isnull=True
        ).exclude(
            industry__exact=''
        )

        if im_sector_filter:
            industry_queryset = industry_queryset.filter(im_sector=im_sector_filter)

        industries = list(industry_queryset.values_list(
            'industry', flat=True
        ).distinct().order_by('industry'))

        gics_industries = list(base_queryset.exclude(
            gics_industry__isnull=True
        ).exclude(
            gics_industry__exact=''
        ).values_list('gics_industry', flat=True).distinct().order_by('gics_industry'))

        market_cap_range = base_queryset.exclude(
            market_cap_local__isnull=True
        ).aggregate(
            min_cap=Min('market_cap_local'),
            max_cap=Max('market_cap_local')
        )

        region_values = set(
            CSI300Company.objects.exclude(
                region__isnull=True
            ).exclude(
                region__exact=''
            ).values_list('region', flat=True)
        )

        region_values.update(
            CSI300HSharesCompany.objects.exclude(
                region__isnull=True
            ).exclude(
                region__exact=''
            ).values_list('region', flat=True)
        )

        regions = sorted(region_values, key=lambda value: value.lower())

        data = {
            'regions': regions,
            'im_sectors': im_sectors,
            'industries': industries,
            'gics_industries': gics_industries,
            'market_cap_range': {
                'min': float(market_cap_range['min_cap']) if market_cap_range['min_cap'] else 0,
                'max': float(market_cap_range['max_cap']) if market_cap_range['max_cap'] else 0
            },
            'filtered_by_region': bool(region_filter),
            'region_filter': region_filter,
            'filtered_by_sector': bool(im_sector_filter),
            'sector_filter': im_sector_filter
        }

        return Response(data)
    
    @extend_schema(
        responses={200: CSI300CompanyListSerializer(many=True)},
        parameters=[
            OpenApiParameter(name='q', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=True),
        ]
    )
    @action(detail=False, methods=['get'])
    def search(self, request: Request) -> Response:
        """
        搜索公司
        
        通过公司名称、股票代码或别名进行搜索。
        
        Args:
            request: DRF 请求对象，需要 'q' 查询参数
            
        Returns:
            Response: 匹配的公司列表 (最多 10 条)
        """
        query = request.query_params.get('q', '') or ''
        
        if not query:
            return Response(
                {'error': 'Search query is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        companies = CSI300Company.objects.filter(
            Q(name__icontains=query) |
            Q(ticker__icontains=query) |
            Q(naming__icontains=query)
        ).order_by('ticker')[:10]  # Limit to 10 results for search
        
        serializer = CSI300CompanyListSerializer(companies, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        responses={200: CSI300InvestmentSummarySerializer},
    )
    @action(detail=True, methods=['get'])
    def investment_summary(self, request: Request, pk: Optional[str] = None) -> Response:
        """
        获取公司投资摘要
        
        Args:
            request: DRF 请求对象
            pk: 公司 ID
            
        Returns:
            Response: 投资摘要数据或错误响应
        """
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
            
        except Exception:
            return Response(
                {'error': 'Company not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        responses={200: CSI300IndustryPeersComparisonSerializer},
    )
    @action(detail=True, methods=['get'])
    def industry_peers_comparison(self, request: Request, pk: Optional[str] = None) -> Response:
        """
        获取同行业公司对比数据
        
        返回目标公司与同行业前3名公司的关键指标对比。
        
        Args:
            request: DRF 请求对象
            pk: 公司 ID
            
        Returns:
            Response: 同行业对比数据
            {
                target_company: { id, name, ticker, im_sector, rank },
                industry: str,
                comparison_data: List[PeerComparisonItem],
                total_top_companies_shown: int,
                total_companies_in_industry: int
            }
        """
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
            current_company_rank: Optional[int] = None
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
            comparison_data: List[Dict[str, Any]] = []
            
            # Always add current company first
            company_serializer = CSI300IndustryPeersComparisonSerializer(company)
            company_data: Dict[str, Any] = company_serializer.data
            company_data['rank'] = current_company_rank
            company_data['is_current_company'] = True
            comparison_data.append(company_data)
            
            # Add top 3 companies (固定显示前3名)
            for idx, top_company in enumerate(top_3_companies, 1):
                top_serializer = CSI300IndustryPeersComparisonSerializer(top_company)
                top_data: Dict[str, Any] = top_serializer.data
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
            
        except Exception:
            return Response(
                {'error': 'Company not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
def csi300_index(request: Request) -> Response:
    """
    CSI300 API 索引端点
    
    返回 API 概览信息，包括可用端点和统计数据。
    
    Args:
        request: DRF 请求对象
        
    Returns:
        Response: API 概览信息
    """
    total_companies = CSI300Company.objects.count()
    
    return Response({
        'message': 'CSI300 Companies API',
        'version': '1.0.0',
        'endpoints': {
            'companies': '/api/csi300/api/companies/',
            'company_detail': '/api/csi300/api/companies/{id}/',
            'filter_options': '/api/csi300/api/companies/filter_options/',
            'search': '/api/csi300/api/companies/search/',
        },
        'total_companies': total_companies
    })


@api_view(['GET'])
def health_check(request: Request) -> Response:
    """
    CSI300 API 健康检查端点
    
    检查数据库连接和数据可用性。
    
    Args:
        request: DRF 请求对象
        
    Returns:
        Response: 健康状态信息
    """
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
