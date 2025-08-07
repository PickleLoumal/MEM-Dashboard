"""
Django REST Framework Views for Japan FRED API
实现与美国FRED API完全相同的端点和响应格式，但针对日本经济指标
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db.models import Q
from django.db import connection
from datetime import datetime
from .models import FredJpIndicator, FredJpSeriesInfo
from .serializers import (
    FredJpLatestValueSerializer,
    FredJpObservationSerializer,
    FredJpSeriesInfoSerializer,
    FredJpStatusSerializer,
    FredJpErrorResponseSerializer
)
from .data_fetcher import JapanFredDataFetcher
from .config_manager import JapanFredConfigManager
import logging

logger = logging.getLogger(__name__)


class FredJpIndicatorViewSet(viewsets.ReadOnlyModelViewSet):
    """日本FRED指标视图集 - 对应Flask API功能"""
    queryset = FredJpIndicator.objects.all()
    serializer_class = FredJpLatestValueSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_fetcher = None
        self.config_manager = JapanFredConfigManager()

    def get_data_fetcher(self):
        """获取数据获取器实例"""
        if not self.data_fetcher:
            try:
                self.data_fetcher = JapanFredDataFetcher()
            except Exception as e:
                logger.error(f"数据获取器初始化失败: {e}")
                return None
        return self.data_fetcher
    
    # 日本备用数据
    FALLBACK_DATA = {
        'JPNCCPIALLMINMEI': {
            'value': 105.2,
            'yoy_change': 3.1,
            'date': '2024-05-01',
            'formatted_date': 'May 2024',
            'unit': 'Index',
            'source': 'Fallback data (Japan)'
        },
        'JPNGDPDEFAISMEI': {
            'value': 102.8,
            'yoy_change': 1.2,
            'date': '2024-01-01',
            'formatted_date': 'Q1 2024',
            'unit': 'Index',
            'source': 'Fallback data (Japan)'
        },
        'LRUN64TTJPQ156S': {
            'value': 2.8,
            'yoy_change': -0.2,
            'date': '2024-05-01',
            'formatted_date': 'May 2024',
            'unit': 'Percent',
            'source': 'Fallback data (Japan)'
        },
        'INTDSRJPM193N': {
            'value': -0.1,
            'yoy_change': 0.0,
            'date': '2024-05-01',
            'formatted_date': 'May 2024',
            'unit': 'Percent',
            'source': 'Fallback data (Japan)'
        }
    }

    def get_indicator_data(self, series_id: str, limit: int = 100):
        """获取日本指标数据 - 核心数据获取逻辑"""
        try:
            # 从日本数据库表获取数据
            observations = FredJpIndicator.objects.filter(
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
                'source': 'PostgreSQL Database (Django DRF - Japan)',
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
            
            # 元数据
            meta = {
                'series_id': series_id,
                'total_records': len(observations_data),
                'last_updated': latest.created_at.isoformat() if latest.created_at else None
            }
            
            return {
                'data': data,
                'observations': observations_data,
                'meta': meta
            }
            
        except Exception as e:
            logger.error(f"Error fetching Japan indicator data for {series_id}: {str(e)}")
            return None

    @action(detail=False, methods=['get'], url_path=r'(?P<indicator_name>[^/.]+)')
    def get_indicator(self, request, indicator_name=None):
        """获取特定日本指标数据"""
        try:
            if not indicator_name:
                return Response({
                    'success': False,
                    'error': 'Missing indicator name',
                    'message': 'Indicator name is required',
                    'timestamp': datetime.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 转换指标名称到series_id
            series_id = self.config_manager.get_series_id(indicator_name.lower())
            
            if not series_id:
                # 如果没有找到映射，返回错误
                return Response({
                    'success': False,
                    'error': 'Indicator not found',
                    'message': f'Japan indicator "{indicator_name}" is not supported',
                    'supported_indicators': self.config_manager.get_all_indicators(),
                    'timestamp': datetime.now().isoformat()
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 获取数据
            result = self.get_indicator_data(series_id)
            
            if result:
                return Response(result)
            else:
                # 使用备用数据
                fallback = self.FALLBACK_DATA.get(series_id)
                if fallback:
                    return Response({
                        'data': fallback,
                        'observations': [fallback],
                        'meta': {
                            'series_id': series_id,
                            'total_records': 1,
                            'last_updated': datetime.now().isoformat(),
                            'note': 'Fallback data - Japan database not available'
                        }
                    })
                else:
                    return Response({
                        'success': False,
                        'error': 'No data available',
                        'message': f'No data found for Japan indicator {indicator_name}',
                        'series_id': series_id,
                        'timestamp': datetime.now().isoformat()
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                    
        except Exception as e:
            logger.error(f"Error in Japan get_indicator for {indicator_name}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def status(self, request):
        """日本FRED系统状态"""
        try:
            # 检查数据库连接
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                database_available = True
        except Exception:
            database_available = False
        
        status_data = {
            'success': True,
            'system': 'Japan FRED System (Django)',
            'database_available': database_available,
            'status': {
                'indicators_available': len(self.config_manager.get_all_indicators()),
                'last_check': datetime.now().isoformat(),
                'country': 'Japan'
            },
            'supported_indicators': self.config_manager.get_all_indicators(),
            'last_updated': datetime.now()
        }
        
        serializer = FredJpStatusSerializer(status_data)
        return Response(serializer.data)


@api_view(['GET'])
def health_check_jp(request):
    """日本FRED健康检查端点"""
    try:
        # 检查数据库连接
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            database_available = True
    except Exception:
        database_available = False
    
    return Response({
        'status': 'healthy' if database_available else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'service': 'MEM Dashboard Django API - Japan',
        'database_available': database_available,
        'version': '1.0.0',
        'country': 'Japan'
    })
