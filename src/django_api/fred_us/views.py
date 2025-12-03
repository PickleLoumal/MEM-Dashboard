"""
Django REST Framework Views for US FRED API
美国FRED经济指标API视图 - 分离架构实现

类型注解说明:
- 所有公共方法都有完整的类型注解
- 使用 shared_types 模块中定义的类型
- Response 返回值类型为 rest_framework.response.Response

对应前端类型: csi300-app/src/shared/api-types/fred.types.ts
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type, Union

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from django.db.models import Q, Max
from django.db.models.query import QuerySet
from django.db import connection
from datetime import datetime, timedelta
import logging

from .models import FredUsIndicator, FredUsSeriesInfo
from .data_fetcher import UsFredDataFetcher
from .serializers import (
    FredUsIndicatorResponseSerializer,
    FredUsLatestValueSerializer,
    FredUsObservationSerializer,
    FredUsStatusSerializer,
    FredUsAllIndicatorsSerializer,
    FredUsHealthCheckSerializer,
    FredUsErrorResponseSerializer
)

logger = logging.getLogger(__name__)

# 类型别名
SerializerClass = Type[Serializer[Any]]


class FredUsIndicatorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    美国 FRED 指标数据 ViewSet
    
    提供美国 FRED 经济指标的 API 端点:
    - list: API 概览信息
    - indicator: 获取指定指标数据
    - status: 服务状态
    - all_indicators: 所有指标摘要
    - health: 健康检查
    - 各种特定指标端点 (debt-to-gdp, cpi, unemployment, etc.)
    
    类型注解:
    - 所有方法返回 Response 对象
    - 查询参数通过 request.query_params 获取
    """
    
    queryset: QuerySet[FredUsIndicator] = FredUsIndicator.objects.all()
    serializer_class: SerializerClass = FredUsIndicatorResponseSerializer
    data_fetcher: Optional[UsFredDataFetcher]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.data_fetcher = None

    def list(self, request: Request) -> Response:
        """
        API 根端点 - 返回 API 概览信息
        
        GET /api/fred-us/
        
        Args:
            request: DRF 请求对象
            
        Returns:
            Response: API 概览信息
        """
        try:
            total_indicators: int = FredUsIndicator.objects.values('series_id').distinct().count()
            last_updated: Optional[datetime] = FredUsIndicator.objects.aggregate(
                Max('updated_at')
            )['updated_at__max']
            
            api_info: Dict[str, Any] = {
                'api_name': 'US FRED Economic Indicators API',
                'country': 'US',
                'version': '1.0',
                'total_indicators': total_indicators,
                'last_updated': last_updated.isoformat() if last_updated else None,
                'available_endpoints': {
                    'indicator': '/api/fred-us/indicator/?name=UNRATE&limit=100',
                    'status': '/api/fred-us/status/',
                    'all_indicators': '/api/fred-us/all-indicators/',
                    'health': '/api/fred-us/health/',
                    'fetch_data': '/api/fred-us/fetch-data/?indicator=UNRATE&limit=100'
                },
                'description': 'US Federal Reserve Economic Data (FRED) API endpoint for economic indicators'
            }
            
            return Response(api_info)
            
        except Exception as e:
            logger.error(f"获取美国FRED API概览失败: {e}")
            return self._error_response(f"API概览获取失败: {str(e)}")

    def get_data_fetcher(self) -> Optional[UsFredDataFetcher]:
        """
        获取数据获取器实例 (延迟初始化)
        
        Returns:
            UsFredDataFetcher 实例或 None (初始化失败时)
        """
        if not self.data_fetcher:
            try:
                self.data_fetcher = UsFredDataFetcher()
            except Exception as e:
                logger.error(f"美国FRED数据获取器初始化失败: {e}")
                return None
        return self.data_fetcher

    @action(detail=False, methods=['get'])
    def indicator(self, request: Request) -> Response:
        """
        获取指定美国 FRED 指标数据
        
        GET /api/fred-us/indicator/?name=UNRATE&limit=100
        
        Args:
            request: DRF 请求对象
                - name: 指标名称 (必需)
                - limit: 返回记录数 (默认 100)
                
        Returns:
            Response: 指标数据或错误响应
        """
        indicator_name: str = request.query_params.get('name', '').lower()
        limit: int = int(request.query_params.get('limit', 100))
        
        try:
            # 验证指标名称
            fetcher = self.get_data_fetcher()
            if not fetcher:
                return self._error_response("数据获取器初始化失败")
            
            if not fetcher.validate_indicator(indicator_name.upper()):
                return self._error_response(
                    f"不支持的美国指标: {indicator_name}",
                    details={
                        'supported_indicators': fetcher.get_supported_indicators(),
                        'indicator_categories': fetcher.get_indicator_categories()
                    }
                )
            
            series_id = indicator_name.upper()
            
            # 从数据库获取数据
            latest_record = FredUsIndicator.objects.filter(
                series_id=series_id
            ).order_by('-date').first()
            
            if not latest_record:
                # 尝试从API获取数据
                logger.info(f"数据库中未找到美国指标 {series_id}，尝试从FRED API获取")
                api_result = fetcher.fetch_indicator_data(series_id, limit=limit)
                
                if api_result.get('success'):
                    # 重新查询最新记录
                    latest_record = FredUsIndicator.objects.filter(
                        series_id=series_id
                    ).order_by('-date').first()
                
                if not latest_record:
                    return self._error_response(f"无法获取美国指标数据: {series_id}")
            
            # 获取历史数据
            observations = FredUsIndicator.objects.filter(
                series_id=series_id
            ).order_by('-date')[:limit]
            
            # 序列化响应数据
            latest_data = FredUsLatestValueSerializer(latest_record).data
            observations_data = FredUsObservationSerializer(observations, many=True).data
            
            response_data = {
                'success': True,
                'data': latest_data,
                'observations': observations_data,
                'metadata': {
                    'country': 'US',
                    'series_id': series_id,
                    'total_records': len(observations_data),
                    'source': 'US FRED Database',
                    'api_version': '1.0'
                }
            }
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"获取美国FRED指标数据失败: {e}")
            return self._error_response(f"服务器内部错误: {str(e)}")

    @action(detail=False, methods=['get'])
    def status(self, request):
        """获取美国FRED服务状态 - GET /api/fred-us/status/"""
        try:
            total_indicators = FredUsIndicator.objects.values('series_id').distinct().count()
            last_updated = FredUsIndicator.objects.aggregate(Max('updated_at'))['updated_at__max']
            
            # 检查API连接
            fetcher = self.get_data_fetcher()
            api_key_configured = fetcher is not None and fetcher.api_key is not None
            
            status_data = {
                'status': 'healthy',
                'database': 'connected',
                'country': 'US',
                'total_indicators': total_indicators,
                'last_updated': last_updated.isoformat() if last_updated else None,
                'api_key_configured': api_key_configured
            }
            
            return Response(FredUsStatusSerializer(status_data).data)
            
        except Exception as e:
            logger.error(f"获取美国FRED状态失败: {e}")
            return self._error_response(f"状态检查失败: {str(e)}")

    @action(detail=False, methods=['get'])
    def all_indicators(self, request):
        """获取所有美国FRED指标概览 - GET /api/fred-us/all-indicators/"""
        try:
            fetcher = self.get_data_fetcher()
            if not fetcher:
                return self._error_response("数据获取器初始化失败")
            
            # 获取最新数据摘要
            summary_result = fetcher.get_latest_data_summary()
            
            if summary_result.get('success'):
                summary_data = summary_result['data']
                response_data = {
                    'success': True,
                    'data': summary_data,
                    'country': 'US',
                    'total_count': summary_data.get('total_indicators', 0)
                }
                return Response(FredUsAllIndicatorsSerializer(response_data).data)
            else:
                return self._error_response(
                    "获取美国指标摘要失败",
                    details=summary_result
                )
                
        except Exception as e:
            logger.error(f"获取美国所有指标失败: {e}")
            return self._error_response(f"服务器内部错误: {str(e)}")

    @action(detail=False, methods=['get'])
    def health(self, request):
        """健康检查端点 - GET /api/fred-us/health/"""
        try:
            # 数据库连接检查
            database_connection = True
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
            except Exception:
                database_connection = False
            
            # API配置检查
            fetcher = self.get_data_fetcher()
            api_connection = fetcher is not None and fetcher.api_key is not None
            
            health_status = 'healthy' if (database_connection and api_connection) else 'unhealthy'
            
            health_data = {
                'status': health_status,
                'database_connection': database_connection,
                'api_connection': api_connection,
                'country': 'US',
                'timestamp': datetime.now()
            }
            
            return Response(FredUsHealthCheckSerializer(health_data).data)
            
        except Exception as e:
            logger.error(f"美国FRED健康检查失败: {e}")
            return self._error_response(f"健康检查失败: {str(e)}")

    @action(detail=False, methods=['post'])
    def fetch_data(self, request):
        """手动获取美国FRED数据 - POST /api/fred-us/fetch-data/"""
        try:
            indicator_name = request.data.get('indicator', '').upper()
            limit = int(request.data.get('limit', 100))
            
            fetcher = self.get_data_fetcher()
            if not fetcher:
                return self._error_response("数据获取器初始化失败")
            
            if indicator_name:
                # 获取指定指标
                if not fetcher.validate_indicator(indicator_name):
                    return self._error_response(f"不支持的美国指标: {indicator_name}")
                
                result = fetcher.fetch_indicator_data(indicator_name, limit=limit)
            else:
                # 获取所有支持的指标
                supported_indicators = fetcher.get_supported_indicators()
                results = []
                
                for indicator in supported_indicators[:5]:  # 限制并发数量
                    result = fetcher.fetch_indicator_data(indicator, limit=50)
                    results.append({
                        'indicator': indicator,
                        'success': result.get('success', False),
                        'records_saved': result.get('records_saved', 0)
                    })
                
                return Response({
                    'success': True,
                    'message': f'批量获取美国指标数据完成',
                    'results': results,
                    'country': 'US'
                })
            
            if result.get('success'):
                return Response({
                    'success': True,
                    'message': f'成功获取美国指标数据: {indicator_name}',
                    'records_saved': result.get('records_saved', 0),
                    'country': 'US'
                })
            else:
                return self._error_response(
                    f"获取美国指标数据失败: {indicator_name}",
                    details=result
                )
                
        except Exception as e:
            logger.error(f"手动获取美国FRED数据失败: {e}")
            return self._error_response(f"数据获取失败: {str(e)}")

    # 特定指标端点 - 为前端兼容性提供直接端点
    @action(detail=False, methods=['get'], url_path='debt-to-gdp')
    def debt_to_gdp(self, request):
        """债务与GDP比率 - GET /api/fred-us/debt-to-gdp/"""
        return self._get_specific_indicator('GFDEGDQ188S', request)
    
    @action(detail=False, methods=['get'], url_path='m2')
    def m2_money_supply(self, request):
        """M2货币供应量 - GET /api/fred-us/m2/"""
        return self._get_specific_indicator('M2SL', request)
    
    @action(detail=False, methods=['get'], url_path='m1')
    def m1_money_supply(self, request):
        """M1货币供应量 - GET /api/fred-us/m1/"""
        return self._get_specific_indicator('M1SL', request)
    
    @action(detail=False, methods=['get'], url_path='m2v')
    def m2_velocity(self, request):
        """M2货币流通速度 - GET /api/fred-us/m2v/"""
        return self._get_specific_indicator('M2V', request)
    
    @action(detail=False, methods=['get'], url_path='monetary-base')
    def monetary_base(self, request):
        """货币基础 - GET /api/fred-us/monetary-base/"""
        return self._get_specific_indicator('BOGMBASE', request)
    
    @action(detail=False, methods=['get'], url_path='cpi')
    def consumer_price_index(self, request):
        """消费者价格指数 - GET /api/fred-us/cpi/"""
        return self._get_specific_indicator('CPIAUCSL', request)
    
    @action(detail=False, methods=['get'], url_path='unemployment')
    def unemployment_rate(self, request):
        """失业率 - GET /api/fred-us/unemployment/"""
        return self._get_specific_indicator('UNRATE', request)
    
    @action(detail=False, methods=['get'], url_path='housing')
    def housing_starts(self, request):
        """房屋开工数 - GET /api/fred-us/housing/"""
        return self._get_specific_indicator('HOUST', request)
    
    @action(detail=False, methods=['get'], url_path='fed-funds')
    def fed_funds_rate(self, request):
        """联邦基金利率 - GET /api/fred-us/fed-funds/"""
        return self._get_specific_indicator('FEDFUNDS', request)
    
    @action(detail=False, methods=['get'], url_path='mortgage-30y')
    def mortgage_30y_rate(self, request):
        """30年固定抵押贷款利率 - GET /api/fred-us/mortgage-30y/"""
        return self._get_specific_indicator('MORTGAGE30US', request)

    @action(detail=False, methods=['get'], url_path='pce-price-index')
    def pce_price_index(self, request):
        """PCE价格指数 - GET /api/fred-us/pce-price-index/"""
        return self._get_specific_indicator('PCEPI', request)

    @action(detail=False, methods=['get'], url_path='treasury-10y')
    def treasury_10y_rate(self, request):
        """10年期国债利率 - GET /api/fred-us/treasury-10y/"""
        return self._get_specific_indicator('DGS10', request)

    @action(detail=False, methods=['get'], url_path='treasury-2y')
    def treasury_2y_rate(self, request):
        """2年期国债利率 - GET /api/fred-us/treasury-2y/"""
        return self._get_specific_indicator('DGS2', request)

    @action(detail=False, methods=['get'], url_path='treasury-3m')
    def treasury_3m_rate(self, request):
        """3个月国债利率 - GET /api/fred-us/treasury-3m/"""
        return self._get_specific_indicator('TB3MS', request)

    # Consumer and Household Debt Indicators
    @action(detail=False, methods=['get'], url_path='household-debt-gdp')
    def household_debt_gdp(self, request):
        """家庭债务占GDP比重 - GET /api/fred-us/household-debt-gdp/"""
        return self._get_specific_indicator('HDTGPDUSQ163N', request)

    @action(detail=False, methods=['get'], url_path='debt-service-ratio')
    def debt_service_ratio(self, request):
        """家庭债务偿还比率 - GET /api/fred-us/debt-service-ratio/"""
        return self._get_specific_indicator('TDSP', request)

    @action(detail=False, methods=['get'], url_path='mortgage-debt')
    def mortgage_debt_outstanding(self, request):
        """抵押贷款债务未偿余额 - GET /api/fred-us/mortgage-debt/"""
        return self._get_specific_indicator('MDOAH', request)

    @action(detail=False, methods=['get'], url_path='credit-card-debt')
    def credit_card_balances(self, request):
        """信用卡债务余额 - GET /api/fred-us/credit-card-debt/"""
        return self._get_specific_indicator('RCCCBBALTOT', request)

    @action(detail=False, methods=['get'], url_path='student-loans')
    def student_loans(self, request):
        """学生贷款 - GET /api/fred-us/student-loans/"""
        return self._get_specific_indicator('SLOASM', request)

    @action(detail=False, methods=['get'], url_path='consumer-credit')
    def total_consumer_credit(self, request):
        """总消费者信贷 - GET /api/fred-us/consumer-credit/"""
        return self._get_specific_indicator('TOTALSL', request)

    @action(detail=False, methods=['get'], url_path='total-debt')
    def total_household_debt(self, request):
        """家庭总债务 - GET /api/fred-us/total-debt/"""
        return self._get_specific_indicator('DTCOLNVHFNM', request)

    # Government Debts Indicators
    @action(detail=False, methods=['get'], url_path='federal-debt-total')
    def federal_debt_total(self, request):
        """联邦债务总额 - GET /api/fred-us/federal-debt-total/"""
        return self._get_specific_indicator('GFDEBTN', request)

    @action(detail=False, methods=['get'], url_path='federal-debt-gdp-ratio')
    def federal_debt_gdp_ratio(self, request):
        """联邦债务占GDP比例 - GET /api/fred-us/federal-debt-gdp-ratio/"""
        return self._get_specific_indicator('GFDEGDQ188S', request)

    @action(detail=False, methods=['get'], url_path='federal-surplus-deficit')
    def federal_surplus_deficit(self, request):
        """联邦盈余或赤字 - GET /api/fred-us/federal-surplus-deficit/"""
        return self._get_specific_indicator('MTSDS133FMS', request)

    @action(detail=False, methods=['get'], url_path='population-55-over')
    def population_55_over(self, request):
        """55岁及以上人口 - GET /api/fred-us/population-55-over/"""
        return self._get_specific_indicator('LNU00024230', request)

    @action(detail=False, methods=['get'], url_path='gross-federal-debt')
    def gross_federal_debt(self, request):
        """联邦总债务 - GET /api/fred-us/gross-federal-debt/"""
        return self._get_specific_indicator('FYGFD', request)

    @action(detail=False, methods=['get'], url_path='federal-interest-gdp')
    def federal_interest_gdp(self, request):
        """联邦利息支出占GDP比例 - GET /api/fred-us/federal-interest-gdp/"""
        return self._get_specific_indicator('FYOIGDA188S', request)

    @action(detail=False, methods=['get'], url_path='federal-debt-public-gdp')
    def federal_debt_public_gdp(self, request):
        """联邦公共债务占GDP比例 - GET /api/fred-us/federal-debt-public-gdp/"""
        return self._get_specific_indicator('FYGFGDQ188S', request)

    @action(detail=False, methods=['get'], url_path='government-consumer-credit')
    def government_consumer_credit(self, request):
        """政府消费者信贷 - GET /api/fred-us/government-consumer-credit/"""
        return self._get_specific_indicator('TOTALGOV', request)

    # Trade Deficits and International Balance Indicators
    @action(detail=False, methods=['get'], url_path='trade-balance-goods-services')
    def trade_balance_goods_services(self, request):
        """贸易平衡：商品和服务（国际收支基础）- GET /api/fred-us/trade-balance-goods-services/"""
        return self._get_specific_indicator('BOPGSTB', request)

    @action(detail=False, methods=['get'], url_path='current-account-balance')
    def current_account_balance(self, request):
        """经常账户余额 - GET /api/fred-us/current-account-balance/"""
        return self._get_specific_indicator('IEABC', request)

    @action(detail=False, methods=['get'], url_path='foreign-treasury-holdings')
    def foreign_treasury_holdings(self, request):
        """外国官方机构持有的美国国债 - GET /api/fred-us/foreign-treasury-holdings/"""
        return self._get_specific_indicator('BOGZ1FL263061130Q', request)

    @action(detail=False, methods=['get'], url_path='customs-duties')
    def customs_duties(self, request):
        """联邦政府关税收入 - GET /api/fred-us/customs-duties/"""
        return self._get_specific_indicator('B235RC1Q027SBEA', request)

    @action(detail=False, methods=['get'], url_path='federal-surplus-deficit-mts')
    def federal_surplus_deficit_mts(self, request):
        """联邦财政盈余/赤字（月度财政报表）- GET /api/fred-us/federal-surplus-deficit-mts/"""
        return self._get_specific_indicator('MTSDS133FMS', request)

    @action(detail=False, methods=['get'], url_path='net-exports')
    def net_exports(self, request):
        """商品和服务净出口 - GET /api/fred-us/net-exports/"""
        return self._get_specific_indicator('NETEXP', request)

    @action(detail=False, methods=['get'], url_path='real-imports')
    def real_imports(self, request):
        """实际商品和服务进口 - GET /api/fred-us/real-imports/"""
        return self._get_specific_indicator('IMPGSC1', request)

    @action(detail=False, methods=['get'], url_path='real-exports')
    def real_exports(self, request):
        """实际商品和服务出口 - GET /api/fred-us/real-exports/"""
        return self._get_specific_indicator('EXPGSC1', request)

    # Employment Indicators
    @action(detail=False, methods=['get'], url_path='unemployment-rate')
    def unemployment_rate_employment(self, request):
        """失业率 - GET /api/fred-us/unemployment-rate/"""
        return self._get_specific_indicator('UNRATE', request)

    @action(detail=False, methods=['get'], url_path='labor-force-participation')
    def labor_force_participation_rate(self, request):
        """劳动力参与率 - GET /api/fred-us/labor-force-participation/"""
        return self._get_specific_indicator('CIVPART', request)

    @action(detail=False, methods=['get'], url_path='job-openings')
    def job_openings_total(self, request):
        """职位空缺总数 - GET /api/fred-us/job-openings/"""
        return self._get_specific_indicator('JTSJOL', request)

    @action(detail=False, methods=['get'], url_path='quits-rate')
    def quits_rate_total(self, request):
        """辞职率 - GET /api/fred-us/quits-rate/"""
        return self._get_specific_indicator('JTSQUR', request)

    @action(detail=False, methods=['get'], url_path='initial-jobless-claims')
    def initial_jobless_claims(self, request):
        """首次申请失业救济人数 - GET /api/fred-us/initial-jobless-claims/"""
        return self._get_specific_indicator('ICSA', request)

    @action(detail=False, methods=['get'], url_path='employment-cost-index')
    def employment_cost_index(self, request):
        """就业成本指数 - GET /api/fred-us/employment-cost-index/"""
        return self._get_specific_indicator('ECIWAG', request)

    @action(detail=False, methods=['get'], url_path='nonfarm-payroll')
    def nonfarm_payroll_growth(self, request):
        """非农就业人数 - GET /api/fred-us/nonfarm-payroll/"""
        return self._get_specific_indicator('PAYEMS', request)

    @action(detail=False, methods=['get'], url_path='average-hourly-earnings')
    def average_hourly_earnings_growth(self, request):
        """平均时薪增长 - GET /api/fred-us/average-hourly-earnings/"""
        return self._get_specific_indicator('AHETPI', request)

    def _get_specific_indicator(self, series_id: str, request: Request) -> Response:
        """
        获取特定指标数据的通用方法
        
        返回前端期望的简单格式，包含最新值、历史观测数据和元信息。
        
        Args:
            series_id: FRED 系列 ID (如 'UNRATE', 'CPIAUCSL')
            request: DRF 请求对象
            
        Returns:
            Response: 指标数据响应
            {
                success: true,
                data: { value, date, formatted_date, yoy_change, ... },
                observations: [...],
                series_id: str,
                count: int,
                country: 'US'
            }
        """
        try:
            limit: int = int(request.query_params.get('limit', 100))
            
            # 从数据库获取数据 - 不先切片
            base_queryset: QuerySet[FredUsIndicator] = FredUsIndicator.objects.filter(
                series_id=series_id
            ).order_by('-date')
            
            if not base_queryset.exists():
                # 如果数据库中没有数据，尝试从API获取
                fetcher = self.get_data_fetcher()
                if fetcher:
                    result = fetcher.fetch_indicator_data(series_id, limit=limit)
                    if result.get('success'):
                        # 重新查询数据库
                        base_queryset = FredUsIndicator.objects.filter(
                            series_id=series_id
                        ).order_by('-date')
            
            if base_queryset.exists():
                # 先获取所有数据用于计算
                all_indicators = list(base_queryset)
                
                # 然后获取限制数量的数据
                indicators = all_indicators[:limit]
                latest = indicators[0] if indicators else None
                
                if latest and latest.date and latest.value is not None:
                    # 计算同比变化 - 使用all_indicators而不是切片后的QuerySet
                    yoy_change = None
                    if len(all_indicators) > 1:
                        try:
                            # 尝试找到一年前的数据
                            year_ago = latest.date.replace(year=latest.date.year - 1)
                            year_ago_indicator = None
                            for indicator in all_indicators:
                                if indicator.date <= year_ago:
                                    year_ago_indicator = indicator
                                    break
                            
                            if year_ago_indicator and year_ago_indicator.value:
                                current_val = float(latest.value)
                                year_ago_val = float(year_ago_indicator.value)
                                yoy_change = ((current_val - year_ago_val) / year_ago_val) * 100
                        except (ValueError, AttributeError):
                            yoy_change = None
                    
                    # 格式化日期
                    formatted_date = latest.date.strftime('%b %Y')
                    
                    # 返回前端期望的简单格式
                    response_data = {
                        'success': True,
                        'data': {
                            'value': float(latest.value),
                            'date': latest.date.isoformat(),
                            'formatted_date': formatted_date,
                            'yoy_change': round(yoy_change, 2) if yoy_change is not None else None,
                            'series_id': series_id,
                            'indicator_name': latest.indicator_name or '',
                            'unit': latest.unit or '',
                            'source': 'PostgreSQL Database (Django DRF)',
                            'last_updated': latest.updated_at.isoformat() if latest.updated_at else None
                        },
                        'series_id': series_id,
                        'count': len(indicators),
                        'limit': limit,
                        'country': 'US'
                    }
                    
                    # 同时包含observations用于图表和其他用途
                    observations = []
                    for indicator in indicators:
                        if indicator.date and indicator.value is not None:
                            observations.append({
                                'date': indicator.date.isoformat(),
                                'value': str(indicator.value),
                                'realtime_start': indicator.date.isoformat(),
                                'realtime_end': indicator.date.isoformat()
                            })
                    response_data['observations'] = observations
                    
                    return Response(response_data)
                else:
                    return self._error_response(f"Invalid data for {series_id}")
            else:
                return self._error_response(f"No data available for {series_id}")
                
        except Exception as e:
            logger.error(f"获取指标 {series_id} 失败: {e}")
            return self._error_response(f"Failed to get indicator {series_id}: {str(e)}")

    def _error_response(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ) -> Response:
        """
        生成标准化的错误响应
        
        Args:
            message: 错误消息
            details: 额外的错误详情
            
        Returns:
            Response: 错误响应 (HTTP 400)
        """
        error_data: Dict[str, Any] = {
            'success': False,
            'error': message,
            'country': 'US',
            'details': details if details is not None else {},
            'timestamp': datetime.now()
        }
        return Response(
            FredUsErrorResponseSerializer(error_data).data,
            status=status.HTTP_400_BAD_REQUEST
        )

    # ==================== Government Deficit Financing API Endpoints ====================
    
    @action(detail=False, methods=['get'], url_path='federal-debt-total-gdf')
    def federal_debt_total_gdf(self, request):
        """联邦债务总额 (Government Deficit Financing) - GET /api/fred-us/federal-debt-total-gdf/"""
        return self._get_specific_indicator('GFDEBTN', request)
    
    @action(detail=False, methods=['get'], url_path='federal-debt-gdp-ratio-gdf')
    def federal_debt_gdp_ratio_gdf(self, request):
        """联邦债务占GDP比例 (Government Deficit Financing) - GET /api/fred-us/federal-debt-gdp-ratio-gdf/"""
        return self._get_specific_indicator('GFDEGDQ188S', request)
    
    @action(detail=False, methods=['get'], url_path='federal-surplus-deficit-gdf')
    def federal_surplus_deficit_gdf(self, request):
        """联邦盈余或赤字 (Government Deficit Financing) - GET /api/fred-us/federal-surplus-deficit-gdf/"""
        return self._get_specific_indicator('MTSDS133FMS', request)
    
    @action(detail=False, methods=['get'], url_path='federal-tax-receipts')
    def federal_tax_receipts(self, request):
        """联邦政府当期税收 - GET /api/fred-us/federal-tax-receipts/"""
        return self._get_specific_indicator('W006RC1Q027SBEA', request)
    
    @action(detail=False, methods=['get'], url_path='federal-net-outlays')
    def federal_net_outlays(self, request):
        """联邦净支出 - GET /api/fred-us/federal-net-outlays/"""
        return self._get_specific_indicator('FYONET', request)
    
    @action(detail=False, methods=['get'], url_path='federal-current-expenditures')
    def federal_current_expenditures(self, request):
        """联邦政府当期支出 - GET /api/fred-us/federal-current-expenditures/"""
        return self._get_specific_indicator('FGEXPND', request)
    
    @action(detail=False, methods=['get'], url_path='federal-current-receipts')
    def federal_current_receipts(self, request):
        """联邦政府当期收入 - GET /api/fred-us/federal-current-receipts/"""
        return self._get_specific_indicator('FGRECPT', request)
    
    @action(detail=False, methods=['get'], url_path='excess-reserves')
    def excess_reserves(self, request):
        """存款机构超额准备金 - GET /api/fred-us/excess-reserves/"""
        return self._get_specific_indicator('EXCSRESNW', request)

    # Private Sector Corporate Debts indicators - 企业债务指标
    @action(detail=False, methods=['get'], url_path='nber-recession-indicator')
    def nber_recession_indicator(self, request):
        """NBER经济衰退指标 - GET /api/fred-us/nber-recession-indicator/"""
        return self._get_specific_indicator('USREC', request)
    
    @action(detail=False, methods=['get'], url_path='consumer-price-inflation')
    def consumer_price_inflation(self, request):
        """美国消费者价格通胀率 - GET /api/fred-us/consumer-price-inflation/"""
        return self._get_specific_indicator('FPCPITOTLZGUSA', request)
    
    @action(detail=False, methods=['get'], url_path='high-yield-bond-spread')
    def high_yield_bond_spread(self, request):
        """ICE BofA美国高收益指数期权调整利差 - GET /api/fred-us/high-yield-bond-spread/"""
        return self._get_specific_indicator('BAMLH0A0HYM2', request)
    
    @action(detail=False, methods=['get'], url_path='primary-credit-loans')
    def primary_credit_loans(self, request):
        """资产流动性和信贷便利：主要信贷贷款 - GET /api/fred-us/primary-credit-loans/"""
        return self._get_specific_indicator('WPC', request)
    
    @action(detail=False, methods=['get'], url_path='corporate-debt-securities')
    def corporate_debt_securities(self, request):
        """非金融企业：债券和贷款负债水平 - GET /api/fred-us/corporate-debt-securities/"""
        return self._get_specific_indicator('BCNSDODNS', request)
    
    @action(detail=False, methods=['get'], url_path='aaa-corporate-bond-yield')
    def aaa_corporate_bond_yield(self, request):
        """穆迪季节性Aaa级企业债券收益率 - GET /api/fred-us/aaa-corporate-bond-yield/"""
        return self._get_specific_indicator('AAA', request)
    
    @action(detail=False, methods=['get'], url_path='baa-corporate-bond-yield')
    def baa_corporate_bond_yield(self, request):
        """穆迪季节性Baa级企业债券收益率 - GET /api/fred-us/baa-corporate-bond-yield/"""
        return self._get_specific_indicator('BAA', request)
    
    @action(detail=False, methods=['get'], url_path='corporate-debt-equity-ratio')
    def corporate_debt_equity_ratio(self, request):
        """非金融企业债务占股权市值比例 - GET /api/fred-us/corporate-debt-equity-ratio/"""
        return self._get_specific_indicator('NCBCMDPMVCE', request)

    # Money Supply indicators - 货币供应量指标
    @action(detail=False, methods=['get'], url_path='federal-funds-rate')
    def federal_funds_rate(self, request):
        """联邦基金利率 - GET /api/fred-us/federal-funds-rate/"""
        return self._get_specific_indicator('FEDFUNDS', request)
    
    @action(detail=False, methods=['get'], url_path='m2-money-supply')
    def m2_money_supply(self, request):
        """M2货币供应量 - GET /api/fred-us/m2-money-supply/"""
        return self._get_specific_indicator('M2SL', request)
    
    @action(detail=False, methods=['get'], url_path='fed-balance-sheet')
    def fed_balance_sheet(self, request):
        """美联储资产负债表总资产 - GET /api/fred-us/fed-balance-sheet/"""
        return self._get_specific_indicator('WALCL', request)
    
    @action(detail=False, methods=['get'], url_path='bank-lending-standards')
    def bank_lending_standards(self, request):
        """银行贷款标准 - GET /api/fred-us/bank-lending-standards/"""
        return self._get_specific_indicator('DRTSCIS', request)
    
    @action(detail=False, methods=['get'], url_path='commercial-bank-loans')
    def commercial_bank_loans(self, request):
        """商业银行贷款和租赁总额 - GET /api/fred-us/commercial-bank-loans/"""
        return self._get_specific_indicator('TOTLL', request)
    
    @action(detail=False, methods=['get'], url_path='interest-rate-reserve-balances')
    def interest_rate_reserve_balances(self, request):
        """准备金余额利率 - GET /api/fred-us/interest-rate-reserve-balances/"""
        return self._get_specific_indicator('IORB', request)
    
    @action(detail=False, methods=['get'], url_path='overnight-reverse-repo')
    def overnight_reverse_repo(self, request):
        """隔夜逆回购协议 - GET /api/fred-us/overnight-reverse-repo/"""
        return self._get_specific_indicator('RRPONTSYD', request)
    
    @action(detail=False, methods=['get'], url_path='m1-money-supply')
    def m1_money_supply(self, request):
        """M1货币供应量 - GET /api/fred-us/m1-money-supply/"""
        return self._get_specific_indicator('M1SL', request)

    # Banking Sector indicators - 银行业指标 (8个指标)
    @action(detail=False, methods=['get'], url_path='banking-federal-funds-rate')
    def banking_federal_funds_rate(self, request):
        """联邦基金利率 (Banking Sector) - GET /api/fred-us/banking-federal-funds-rate/"""
        return self._get_specific_indicator('FEDFUNDS', request)
    
    @action(detail=False, methods=['get'], url_path='banking-reserve-balances-interest')
    def banking_reserve_balances_interest(self, request):
        """准备金余额利率 - GET /api/fred-us/banking-reserve-balances-interest/"""
        return self._get_specific_indicator('IORB', request)
    
    @action(detail=False, methods=['get'], url_path='banking-total-reserves')
    def banking_total_reserves(self, request):
        """总准备金余额 - GET /api/fred-us/banking-total-reserves/"""
        return self._get_specific_indicator('TOTRESNS', request)
    
    @action(detail=False, methods=['get'], url_path='banking-fed-balance-sheet')
    def banking_fed_balance_sheet(self, request):
        """美联储资产负债表总资产 - GET /api/fred-us/banking-fed-balance-sheet/"""
        return self._get_specific_indicator('WALCL', request)
    
    @action(detail=False, methods=['get'], url_path='banking-pce-inflation')
    def banking_pce_inflation(self, request):
        """PCE价格指数 (通胀) - GET /api/fred-us/banking-pce-inflation/"""
        return self._get_specific_indicator('PCEPI', request)
    
    @action(detail=False, methods=['get'], url_path='banking-unemployment-rate')
    def banking_unemployment_rate(self, request):
        """失业率 - GET /api/fred-us/banking-unemployment-rate/"""
        return self._get_specific_indicator('UNRATE', request)
    
    @action(detail=False, methods=['get'], url_path='banking-commercial-loans')
    def banking_commercial_loans(self, request):
        """商业银行贷款和租赁 - GET /api/fred-us/banking-commercial-loans/"""
        return self._get_specific_indicator('TOTLL', request)
    
    @action(detail=False, methods=['get'], url_path='banking-prime-rate')
    def banking_prime_rate(self, request):
        """银行基准贷款利率 - GET /api/fred-us/banking-prime-rate/"""
        return self._get_specific_indicator('DPRIME', request)
    
    # Inflation indicators - 通胀指标 (8个指标)
    @action(detail=False, methods=['get'], url_path='inflation-consumer-price-index')
    def inflation_consumer_price_index(self, request):
        """消费者价格指数 (CPI) - GET /api/fred-us/inflation-consumer-price-index/"""
        return self._get_specific_indicator('CPIAUCSL', request)
    
    @action(detail=False, methods=['get'], url_path='inflation-core-pce-price-index')
    def inflation_core_pce_price_index(self, request):
        """核心PCE价格指数 - GET /api/fred-us/inflation-core-pce-price-index/"""
        return self._get_specific_indicator('PCEPILFE', request)
    
    @action(detail=False, methods=['get'], url_path='inflation-federal-funds-rate')
    def inflation_federal_funds_rate(self, request):
        """联邦基金利率 (Inflation) - GET /api/fred-us/inflation-federal-funds-rate/"""
        return self._get_specific_indicator('FEDFUNDS', request)
    
    @action(detail=False, methods=['get'], url_path='inflation-unemployment-rate')
    def inflation_unemployment_rate(self, request):
        """失业率 (Inflation) - GET /api/fred-us/inflation-unemployment-rate/"""
        return self._get_specific_indicator('UNRATE', request)
    
    @action(detail=False, methods=['get'], url_path='inflation-retail-sales')
    def inflation_retail_sales(self, request):
        """零售销售 - GET /api/fred-us/inflation-retail-sales/"""
        return self._get_specific_indicator('RSAFS', request)
    
    @action(detail=False, methods=['get'], url_path='inflation-producer-price-index')
    def inflation_producer_price_index(self, request):
        """生产者价格指数 - GET /api/fred-us/inflation-producer-price-index/"""
        return self._get_specific_indicator('PPIACO', request)
    
    @action(detail=False, methods=['get'], url_path='inflation-breakeven-rate')
    def inflation_breakeven_rate(self, request):
        """10年盈亏平衡通胀率 - GET /api/fred-us/inflation-breakeven-rate/"""
        return self._get_specific_indicator('T10YIEM', request)
    
    @action(detail=False, methods=['get'], url_path='inflation-oil-prices')
    def inflation_oil_prices(self, request):
        """原油价格 (WTI) - GET /api/fred-us/inflation-oil-prices/"""
        return self._get_specific_indicator('DCOILWTICO', request)
