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

from typing import Any, Dict, Optional, Type

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from django.db.models import Max
from django.db.models.query import QuerySet
from django.db import connection
from datetime import datetime
import logging

from .models import FredUsIndicator
from .data_fetcher import UsFredDataFetcher
from .serializers import (
    FredUsIndicatorResponseSerializer,
    FredUsLatestValueSerializer,
    FredUsObservationSerializer,
    FredUsStatusSerializer,
    FredUsAllIndicatorsSerializer,
    FredUsHealthCheckSerializer,
)
from .helpers import FredUsHelperMixin
from .indicator_actions import (
    MonetaryIndicatorsMixin,
    DebtIndicatorsMixin,
    EmploymentIndicatorsMixin,
    BankingIndicatorsMixin,
    InflationIndicatorsMixin,
    TradeIndicatorsMixin,
    HousingTreasuryIndicatorsMixin,
)

logger = logging.getLogger(__name__)

# 类型别名
SerializerClass = Type[Serializer[Any]]


class FredUsIndicatorViewSet(
    FredUsHelperMixin,
    MonetaryIndicatorsMixin,
    DebtIndicatorsMixin,
    EmploymentIndicatorsMixin,
    BankingIndicatorsMixin,
    InflationIndicatorsMixin,
    TradeIndicatorsMixin,
    HousingTreasuryIndicatorsMixin,
    viewsets.ReadOnlyModelViewSet
):
    """
    美国 FRED 指标数据 ViewSet
    
    提供美国 FRED 经济指标的 API 端点:
    - list: API 概览信息
    - indicator: 获取指定指标数据
    - status: 服务状态
    - all_indicators: 所有指标摘要
    - health: 健康检查
    - 各种特定指标端点 (通过 Mixins 提供)
    """
    
    queryset: QuerySet[FredUsIndicator] = FredUsIndicator.objects.all()
    serializer_class: SerializerClass = FredUsIndicatorResponseSerializer
    data_fetcher: Optional[UsFredDataFetcher]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.data_fetcher = None

    def list(self, request: Request) -> Response:
        """API 根端点 - 返回 API 概览信息"""
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
                'description': 'US Federal Reserve Economic Data (FRED) API endpoint'
            }
            
            return Response(api_info)
            
        except Exception as e:
            logger.error(f"获取美国FRED API概览失败: {e}")
            return self._error_response(f"API概览获取失败: {str(e)}")

    def get_data_fetcher(self) -> Optional[UsFredDataFetcher]:
        """获取数据获取器实例 (延迟初始化)"""
        if not self.data_fetcher:
            try:
                self.data_fetcher = UsFredDataFetcher()
            except Exception as e:
                logger.error(f"美国FRED数据获取器初始化失败: {e}")
                return None
        return self.data_fetcher

    @action(detail=False, methods=['get'])
    def indicator(self, request: Request) -> Response:
        """获取指定美国 FRED 指标数据"""
        name_param = request.query_params.get('name', '')
        indicator_name: str = str(name_param).lower() if name_param else ''
        limit_param = request.query_params.get('limit', '100')
        limit: int = int(limit_param) if limit_param else 100
        
        try:
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
            
            latest_record = FredUsIndicator.objects.filter(
                series_id=series_id
            ).order_by('-date').first()
            
            if not latest_record:
                logger.info(f"数据库中未找到美国指标 {series_id}，尝试从FRED API获取")
                api_result = fetcher.fetch_indicator_data(series_id, limit=limit)
                
                if api_result.get('success'):
                    latest_record = FredUsIndicator.objects.filter(
                        series_id=series_id
                    ).order_by('-date').first()
                
                if not latest_record:
                    return self._error_response(f"无法获取美国指标数据: {series_id}")
            
            observations = FredUsIndicator.objects.filter(
                series_id=series_id
            ).order_by('-date')[:limit]
            
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
    def status(self, request: Request) -> Response:
        """获取美国FRED服务状态"""
        try:
            total_indicators = FredUsIndicator.objects.values('series_id').distinct().count()
            last_updated = FredUsIndicator.objects.aggregate(Max('updated_at'))['updated_at__max']
            
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
    def all_indicators(self, request: Request) -> Response:
        """获取所有美国FRED指标概览"""
        try:
            fetcher = self.get_data_fetcher()
            if not fetcher:
                return self._error_response("数据获取器初始化失败")
            
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
                return self._error_response("获取美国指标摘要失败", details=summary_result)
                
        except Exception as e:
            logger.error(f"获取美国所有指标失败: {e}")
            return self._error_response(f"服务器内部错误: {str(e)}")

    @action(detail=False, methods=['get'])
    def health(self, request: Request) -> Response:
        """健康检查端点"""
        try:
            database_connection = True
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
            except Exception:
                database_connection = False
            
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
    def fetch_data(self, request: Request) -> Response:
        """手动获取美国FRED数据"""
        try:
            indicator_param = request.data.get('indicator', '')
            indicator_name = str(indicator_param).upper() if indicator_param else ''
            limit_param = request.data.get('limit', 100)
            limit = int(limit_param) if limit_param else 100
            
            fetcher = self.get_data_fetcher()
            if not fetcher:
                return self._error_response("数据获取器初始化失败")
            
            if indicator_name:
                if not fetcher.validate_indicator(indicator_name):
                    return self._error_response(f"不支持的美国指标: {indicator_name}")
                
                result = fetcher.fetch_indicator_data(indicator_name, limit=limit)
            else:
                supported_indicators = fetcher.get_supported_indicators()
                results = []
                
                for indicator in supported_indicators[:5]:
                    result = fetcher.fetch_indicator_data(indicator, limit=50)
                    results.append({
                        'indicator': indicator,
                        'success': result.get('success', False),
                        'records_saved': result.get('records_saved', 0)
                    })
                
                return Response({
                    'success': True,
                    'message': '批量获取美国指标数据完成',
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
