"""
Django REST Framework Views for MEM Dashboard FRED API
实现与Flask API完全相同的端点和响应格式
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db.models import Q
from django.db import connection
from datetime import datetime
from .models import FredIndicator, FredSeriesInfo
from .serializers import (
    FredIndicatorResponseSerializer,
    FredLatestValueSerializer,
    FredObservationSerializer,
    FredStatusSerializer,
    FredAllIndicatorsSerializer,
    FredHealthCheckSerializer,
    FredErrorResponseSerializer
)
import logging

logger = logging.getLogger(__name__)


class FredIndicatorViewSet(viewsets.ReadOnlyModelViewSet):
    """FRED指标视图集 - 对应Flask API功能"""
    queryset = FredIndicator.objects.all()
    serializer_class = FredIndicatorResponseSerializer

    # 对应Flask的FRED_ENDPOINT_MAPPING
    INDICATOR_MAPPING = {
        'm2': 'M2SL',
        'm1': 'M1SL', 
        'm2v': 'M2V',
        'monetary-base': 'BOGMBASE',
        'debt-to-gdp': 'GFDEGDQ188S',
        'cpi': 'CPIAUCSL',
        'unemployment': 'UNRATE',
        'unrate': 'UNRATE',
        'housing': 'HOUST',
        'fed-funds': 'FEDFUNDS',
        # Alternative naming for consistency
        'm2-money-supply': 'M2SL',
        'm1-money-stock': 'M1SL', 
        'm2-velocity': 'M2V',
        'unemployment-rate': 'UNRATE',
        'housing-starts': 'HOUST'
    }
    
    # 备用数据 - 对应Flask的BACKUP_DATA
    FALLBACK_DATA = {
        'M2SL': {
            'value': 21000.5,
            'yoy_change': 4.44,
            'date': '2024-05-01',
            'formatted_date': 'May 2024',
            'unit': 'Billions',
            'source': 'Fallback data'
        },
        'M1SL': {
            'value': 18670.0,
            'yoy_change': 3.86,
            'date': '2024-05-01',
            'formatted_date': 'May 2024',
            'unit': 'Billions',
            'source': 'Fallback data'
        },
        'M2V': {
            'value': 1.383,
            'yoy_change': 0.73,
            'date': '2024-01-01',
            'formatted_date': 'Q1 2024',
            'unit': 'Ratio',
            'source': 'Fallback data'
        },
        'GFDEGDQ188S': {
            'value': 120.81,
            'yoy_change': -0.5,
            'date': '2024-01-01',
            'formatted_date': 'Q1 2024',
            'unit': 'Percent',
            'source': 'Fallback data'
        },
        'CPIAUCSL': {
            'value': 307.8,
            'yoy_change': 2.4,
            'date': '2024-05-01',
            'formatted_date': 'May 2024',
            'unit': 'Index',
            'source': 'Fallback data'
        },
        'UNRATE': {
            'value': 3.7,
            'yoy_change': -0.1,
            'date': '2024-05-01',
            'formatted_date': 'May 2024',
            'unit': 'Percent',
            'source': 'Fallback data'
        },
        'HOUST': {
            'value': 1420.0,
            'yoy_change': 8.5,
            'date': '2024-04-01',
            'formatted_date': 'Apr 2024',
            'unit': 'Thousands',
            'source': 'Fallback data'
        },
        'FEDFUNDS': {
            'value': 5.33,
            'yoy_change': 0.0,
            'date': '2024-05-01',
            'formatted_date': 'May 2024',
            'unit': 'Percent',
            'source': 'Fallback data'
        }
    }

    def get_indicator_data(self, series_id: str, limit: int = 100):
        """获取指标数据 - 核心数据获取逻辑"""
        try:
            # 从数据库获取数据
            observations = FredIndicator.objects.filter(
                series_id=series_id
            ).order_by('-date')[:limit]
            
            if not observations:
                return None
                
            observations_list = list(observations)
            
            # 计算年同比变化
            yoy_change = None
            if len(observations_list) >= 13:  # 需要13个月数据计算年同比
                try:
                    current_value = float(observations_list[0].value)
                    year_ago_value = float(observations_list[12].value)
                    yoy_change = ((current_value - year_ago_value) / year_ago_value) * 100
                except (ValueError, IndexError, ZeroDivisionError):
                    yoy_change = None
            
            # 构建与Flask API相同的响应格式
            latest = observations_list[0]
            data = {
                'value': float(latest.value),
                'date': latest.date.isoformat(),
                'formatted_date': latest.date.strftime('%b %Y'),
                'yoy_change': round(yoy_change, 2) if yoy_change is not None else None,
                'unit': latest.unit,
                'indicator_name': latest.indicator_name,
                'series_id': series_id,
                'source': 'PostgreSQL Database (Django DRF)',
                'last_updated': latest.created_at.isoformat() if latest.created_at else None
            }
            
            # 观测数据数组
            observations_data = []
            for obs in observations_list:
                observations_data.append({
                    'date': obs.date.isoformat(),
                    'value': str(obs.value),
                    'indicator_name': obs.indicator_name,
                    'indicator_type': obs.indicator_type,
                    'unit': obs.unit,
                    'frequency': obs.frequency,
                    'created_at': obs.created_at.isoformat() if obs.created_at else None
                })
            
            return {
                'success': True,
                'data': data,
                'observations': observations_data,
                'source': 'PostgreSQL Database (Django DRF)',
                'series_id': series_id,
                'total_records': len(observations_data),
                'last_updated': latest.created_at.isoformat() if latest.created_at else None
            }
            
        except Exception as e:
            logger.error(f"获取 {series_id} 数据失败: {e}")
            return None

    @action(detail=False, methods=['get'], url_path='health')
    def health_check(self, request):
        """健康检查 - 对应Flask /api/health"""
        return Response({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'MEM Dashboard Django API',
            'database_available': True,
            'version': '1.0.0'
        })

    @action(detail=False, methods=['get'], url_path='status')
    def fred_status(self, request):
        """FRED系统状态 - 对应Flask /api/fred/status"""
        try:
            total_records = FredIndicator.objects.count()
            series_count = FredIndicator.objects.values('series_id').distinct().count()
            
            # 获取每个系列的记录数统计
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT series_id, COUNT(*) as count, MAX(date) as latest_date
                    FROM fred_indicators 
                    GROUP BY series_id
                    ORDER BY series_id
                """)
                
                indicators_status = {}
                for row in cursor.fetchall():
                    series_id, count, latest_date = row
                    indicators_status[series_id] = {
                        'record_count': count,
                        'latest_date': latest_date.isoformat() if latest_date else None
                    }
            
            status_data = {
                'database_available': True,
                'connection_status': 'connected',
                'total_records': total_records,
                'indicators_count': series_count,
                'indicators_status': indicators_status,
                'supported_indicators': list(self.INDICATOR_MAPPING.keys())
            }
            
            return Response({
                'success': True,
                'system': 'FRED Unified System (Django)',
                'database_available': True,
                'status': status_data,
                'supported_indicators': list(self.INDICATOR_MAPPING.keys()),
                'last_updated': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"状态检查失败: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'system': 'FRED Unified System (Django)',
                'database_available': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='all')
    def all_indicators(self, request):
        """所有指标 - 对应Flask /api/fred/all"""
        all_data = {}
        for endpoint, series_id in self.INDICATOR_MAPPING.items():
            data = self.get_indicator_data(series_id, 1)  # 只获取最新值
            if data and data['success']:
                all_data[endpoint] = data['data']
        
        return Response({
            'success': True,
            'data': all_data,
            'source': 'PostgreSQL Database (Django DRF)',
            'indicators_count': len(all_data),
            'last_updated': datetime.now().isoformat()
        })

    # 单个指标端点 - 对应Flask的动态路由
    @action(detail=False, methods=['get'], url_path='(?P<indicator_name>[^/.]+)')
    def single_indicator(self, request, indicator_name=None):
        """单个指标 - 对应Flask /api/fred/<indicator>"""
        if indicator_name not in self.INDICATOR_MAPPING:
            return Response({
                'success': False,
                'error': 'Indicator not found',
                'message': f'Indicator {indicator_name} not supported',
                'supported_indicators': list(self.INDICATOR_MAPPING.keys())
            }, status=status.HTTP_404_NOT_FOUND)

        series_id = self.INDICATOR_MAPPING[indicator_name]
        limit = int(request.query_params.get('limit', 100))
        
        data = self.get_indicator_data(series_id, limit)
        if data:
            return Response(data)
        else:
            # 使用Flask的备用数据逻辑
            fallback_data = self.FALLBACK_DATA.get(series_id)
            if fallback_data:
                return Response({
                    'success': True,
                    'data': fallback_data,
                    'source': 'Fallback data',
                    'message': 'No database data available, using fallback',
                    'series_id': series_id
                })
            else:
                return Response({
                    'success': False,
                    'error': 'No data available',
                    'message': f'No data found for {indicator_name}',
                    'series_id': series_id
                }, status=status.HTTP_404_NOT_FOUND)

    # 具体的指标端点 - 对应Flask的单独路由
    @action(detail=False, methods=['get'])
    def m2(self, request):
        """M2货币供应量 - 对应Flask /api/fred/m2"""
        data = self.get_indicator_data('M2SL')
        return Response(data if data else {'success': False, 'error': 'No M2 data available'})

    @action(detail=False, methods=['get'])
    def m1(self, request):
        """M1货币供应量 - 对应Flask /api/fred/m1"""
        data = self.get_indicator_data('M1SL')
        return Response(data if data else {'success': False, 'error': 'No M1 data available'})

    @action(detail=False, methods=['get'])
    def m2v(self, request):
        """M2货币流通速度 - 对应Flask /api/fred/m2v"""
        data = self.get_indicator_data('M2V')
        return Response(data if data else {'success': False, 'error': 'No M2V data available'})

    @action(detail=False, methods=['get'], url_path='debt-to-gdp')
    def debt_to_gdp(self, request):
        """债务对GDP比率 - 对应Flask /api/fred/debt-to-gdp"""
        data = self.get_indicator_data('GFDEGDQ188S')
        return Response(data if data else {'success': False, 'error': 'No debt-to-GDP data available'})

    @action(detail=False, methods=['get'])
    def cpi(self, request):
        """消费者价格指数 - 对应Flask /api/fred/cpi"""
        data = self.get_indicator_data('CPIAUCSL')
        return Response(data if data else {'success': False, 'error': 'No CPI data available'})

    @action(detail=False, methods=['get'])
    def unemployment(self, request):
        """失业率 - 对应Flask /api/fred/unemployment"""
        data = self.get_indicator_data('UNRATE')
        return Response(data if data else {'success': False, 'error': 'No unemployment data available'})

    @action(detail=False, methods=['get'])
    def housing(self, request):
        """住房开工 - 对应Flask /api/fred/housing"""
        data = self.get_indicator_data('HOUST')
        return Response(data if data else {'success': False, 'error': 'No housing data available'})

    @action(detail=False, methods=['get'], url_path='fed-funds')
    def fed_funds(self, request):
        """联邦基金利率 - 对应Flask /api/fred/fed-funds"""
        data = self.get_indicator_data('FEDFUNDS')
        return Response(data if data else {'success': False, 'error': 'No fed funds data available'})

    @action(detail=False, methods=['get'], url_path='monetary-base')
    def monetary_base(self, request):
        """货币基础 - 对应Flask /api/fred/monetary-base"""
        data = self.get_indicator_data('BOGMBASE')
        return Response(data if data else {'success': False, 'error': 'No monetary base data available'})


# ============================================================================
# Flask 兼容性视图函数
# ============================================================================

from rest_framework.decorators import api_view

@api_view(['GET'])
def flask_compatibility_view(request, series_id):
    """
    Flask兼容性视图 - 处理所有遗留端点
    提供与Flask API完全相同的响应格式
    """
    try:
        # 创建视图集实例来复用数据获取逻辑
        viewset = FredIndicatorViewSet()
        limit = int(request.query_params.get('limit', 100))
        
        # 获取数据
        data = viewset.get_indicator_data(series_id, limit)
        
        if data:
            return Response(data)
        else:
            # 使用备用数据
            fallback_data = viewset.FALLBACK_DATA.get(series_id)
            if fallback_data:
                return Response({
                    'success': True,
                    'data': fallback_data,
                    'source': 'Fallback data - Database unavailable'
                })
            else:
                return Response({
                    'success': False,
                    'error': 'Data not available',
                    'series_id': series_id
                }, status=status.HTTP_404_NOT_FOUND)
                
    except Exception as e:
        logger.error(f"Flask兼容性视图错误 {series_id}: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'series_id': series_id
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def fred_api_status(request):
    """FRED API状态检查"""
    from django.http import JsonResponse
    from django.db.models import Max
    
    try:
        # 检查数据库连接和数据
        total_indicators = FredIndicator.objects.count()
        total_series = FredSeriesInfo.objects.count()
        
        # 获取最新更新时间
        latest_update = FredIndicator.objects.aggregate(
            latest=Max('updated_at')
        )['latest']
        
        return JsonResponse({
            'success': True,
            'status': 'healthy',
            'data': {
                'total_indicators': total_indicators,
                'total_series': total_series,
                'latest_update': latest_update.isoformat() if latest_update else None,
                'available_series': list(FredSeriesInfo.objects.values_list('series_id', flat=True))
            }
        })
        
    except Exception as e:
        logger.error(f"FRED API Status Error: {e}")
        return JsonResponse({
            'success': False,
            'status': 'error',
            'error': str(e)
        }, status=500)
