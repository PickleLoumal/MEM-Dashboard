from typing import Optional

"""
Django REST Framework Views for US FRED API
美国FRED经济指标API视图 - 分离架构实现
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Max
from django.db import connection
from datetime import datetime, timedelta
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
import logging

logger = logging.getLogger(__name__)


class FredUsIndicatorViewSet(viewsets.ReadOnlyModelViewSet):
    """美国FRED指标视图集 - 分离架构实现"""
    queryset = FredUsIndicator.objects.all()
    serializer_class = FredUsIndicatorResponseSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_fetcher = None

    def list(self, request):
        """根端点 - 返回API概览信息 - GET /api/fred-us/"""
        try:
            total_indicators = FredUsIndicator.objects.values('series_id').distinct().count()
            last_updated = FredUsIndicator.objects.aggregate(Max('updated_at'))['updated_at__max']
            
            api_info = {
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

    def get_data_fetcher(self):
        """获取数据获取器实例"""
        if not self.data_fetcher:
            try:
                self.data_fetcher = UsFredDataFetcher()
            except Exception as e:
                logger.error(f"美国FRED数据获取器初始化失败: {e}")
                return None
        return self.data_fetcher

    @action(detail=False, methods=['get'])
    def indicator(self, request):
        """获取指定美国FRED指标数据 - GET /api/fred-us/indicator/"""
        indicator_name = request.query_params.get('name', '').lower()
        limit = int(request.query_params.get('limit', 100))
        
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

    def _get_specific_indicator(self, series_id: str, request):
        """获取特定指标数据的通用方法 - 返回前端期望的简单格式"""
        try:
            limit = int(request.query_params.get('limit', 100))
            
            # 从数据库获取数据 - 不先切片
            base_queryset = FredUsIndicator.objects.filter(
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

    def _error_response(self, message: str, details: Optional[dict] = None):
        """生成错误响应"""
        error_data = {
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
