"""
BEA API Django Views
动态、数据库驱动的BEA指标API端点
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView

import json
from datetime import datetime
from django.utils import timezone

from .models import BeaIndicator, BeaSeriesInfo, BeaIndicatorConfig
from .serializers import (
    BeaIndicatorSerializer, BeaIndicatorConfigSerializer,
    BeaApiResponseSerializer, BeaAllIndicatorsSerializer,
    BeaConfigCreateSerializer, BeaConfigUpdateSerializer
)
from .dynamic_config import DynamicBeaConfigManager
from .indicator_processor import BeaIndicatorProcessor, BeaCompatibilityProcessor

import logging

logger = logging.getLogger(__name__)


class BeaIndicatorViewSet(viewsets.ModelViewSet):
    """BEA指标数据ViewSet - 支持CRUD操作"""
    
    queryset = BeaIndicator.objects.all()
    serializer_class = BeaIndicatorSerializer
    
    def get_queryset(self):
        """根据查询参数过滤数据"""
        queryset = super().get_queryset()
        series_id = self.request.query_params.get('series_id')
        if series_id:
            queryset = queryset.filter(series_id=series_id)
        
        # 按时间倒序排列
        return queryset.order_by('-time_period')


class BeaConfigViewSet(viewsets.ModelViewSet):
    """BEA指标配置ViewSet - 动态配置管理"""
    
    queryset = BeaIndicatorConfig.objects.all()
    serializer_class = BeaIndicatorConfigSerializer
    
    def get_serializer_class(self):
        """根据操作选择序列化器"""
        if self.action == 'create':
            return BeaConfigCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BeaConfigUpdateSerializer
        return BeaIndicatorConfigSerializer
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取所有激活的配置"""
        active_configs = BeaIndicatorConfig.get_active_configs()
        serializer = self.get_serializer(active_configs, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        })
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """获取所有指标分类"""
        categories = BeaIndicatorConfig.objects.values_list('category', flat=True).distinct()
        return Response({
            'success': True,
            'data': list(categories),
            'count': len(categories)
        })
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """激活指标配置"""
        config = self.get_object()
        config.is_active = True
        config.save()
        
        # 清除缓存
        DynamicBeaConfigManager.clear_all_cache()
        
        return Response({
            'success': True,
            'message': f'Indicator {config.series_id} activated successfully'
        })
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """停用指标配置"""
        config = self.get_object()
        config.is_active = False
        config.save()
        
        # 清除缓存
        DynamicBeaConfigManager.clear_all_cache()
        
        return Response({
            'success': True,
            'message': f'Indicator {config.series_id} deactivated successfully'
        })


@api_view(['GET'])
def index(request):
    """BEA API首页 - 动态端点列表"""
    try:
        # 获取动态配置的端点
        all_configs = DynamicBeaConfigManager.get_all_indicators()
        dynamic_endpoints = [f"/indicators{config['api_endpoint']}" for config in all_configs.values()]
        
        return Response({
            'service': 'MEM Dashboard Django API - BEA (Dynamic)',
            'status': 'running',
            'timestamp': timezone.now().isoformat(),
            'dynamic_endpoints': dynamic_endpoints,
            'management_endpoints': [
                '/configs/',
                '/configs/active/',
                '/configs/categories/',
                '/stats/',
                '/all_indicators/'
            ],
            'legacy_endpoints': [
                '/indicators/',
                '/indicators/motor_vehicles/',
                '/indicators/recreational_goods/',
                '/health/'
            ]
        })
    except Exception as e:
        logger.error(f"Error in BEA index: {e}")
        return Response({
            'error': str(e),
            'status': 'error'
        }, status=500)


@api_view(['GET'])
def all_indicators(request):
    """获取所有指标数据 - 动态处理"""
    try:
        result = BeaIndicatorProcessor.process_all_indicators()
        return Response(result)
    except Exception as e:
        logger.error(f"Error processing all indicators: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'data': {}
        }, status=500)


@api_view(['GET'])
def category_indicators(request, category):
    """按分类获取指标数据"""
    try:
        result = BeaIndicatorProcessor.process_category_indicators(category)
        return Response(result)
    except Exception as e:
        logger.error(f"Error processing category {category}: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'data': {}
        }, status=500)


@api_view(['GET'])
def dynamic_indicator(request, series_id):
    """动态指标端点 - 根据series_id获取数据"""
    try:
        include_quarterly = request.GET.get('quarterly', 'true').lower() == 'true'
        result = BeaIndicatorProcessor.process_indicator_data(series_id, include_quarterly)
        return Response(result)
    except Exception as e:
        logger.error(f"Error processing indicator {series_id}: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'series_id': series_id
        }, status=500)


@api_view(['GET'])
def stats(request):
    """BEA系统统计信息"""
    try:
        total_configs = BeaIndicatorConfig.objects.count()
        active_configs = BeaIndicatorConfig.objects.filter(is_active=True).count()
        categories = list(BeaIndicatorConfig.objects.values_list('category', flat=True).distinct())
        auto_fetch_count = BeaIndicatorConfig.objects.filter(auto_fetch=True, is_active=True).count()
        
        # 获取最新数据更新时间
        latest_data = BeaIndicator.objects.order_by('-created_at').first()
        last_data_update = latest_data.created_at if latest_data else None
        
        return Response({
            'success': True,
            'data': {
                'total_indicators': total_configs,
                'active_indicators': active_configs,
                'categories': categories,
                'last_data_update': last_data_update,
                'auto_fetch_count': auto_fetch_count,
                'database_size': f"{BeaIndicator.objects.count()} records"
            },
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# 兼容性端点 - 保持向后兼容
def bea_indicators(request):
    """BEA指标数据端点 - 兼容性版本"""
    try:
        all_configs = DynamicBeaConfigManager.get_all_indicators()
        available_indicators = list(all_configs.keys())
        
        return JsonResponse({
            'service': 'BEA Indicators (Dynamic)',
            'status': 'available',
            'message': 'BEA指标数据服务正常运行 - 动态配置',
            'timestamp': timezone.now().isoformat(),
            'available_indicators': available_indicators,
            'total_count': len(available_indicators)
        })
    except Exception as e:
        logger.error(f"Error in bea_indicators: {e}")
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)


def motor_vehicles_data(request):
    """Motor Vehicles数据端点 - 兼容Flask API格式"""
    try:
        result = BeaCompatibilityProcessor.get_motor_vehicles_data()
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Error in motor_vehicles_data: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'series_id': 'MOTOR_VEHICLES'
        }, status=500)


def recreational_goods_data(request):
    """Recreational Goods数据端点 - 兼容性版本"""
    try:
        result = BeaCompatibilityProcessor.get_recreational_goods_data()
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Error in recreational_goods_data: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'series_id': 'RECREATIONAL_GOODS'
        }, status=500)


def health_check(request):
    """BEA健康检查端点"""
    try:
        total_endpoints = BeaIndicatorConfig.objects.filter(is_active=True).count()
        
        return JsonResponse({
            'service': 'BEA Django API Health Check (Dynamic)',
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'available_endpoints': total_endpoints + 4,  # +4 for management endpoints
            'database_connected': True,
            'dynamic_config_enabled': True
        })
    except Exception as e:
        logger.error(f"Error in health_check: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)

# Gross Domestic Investment indicators - 投资指标 (10个指标)
@api_view(['GET'])
def investment_total(request):
    """Gross Private Domestic Investment - GET /bea/investment-total/"""
    try:
        result = BeaIndicatorProcessor.process_indicator_data('INVESTMENT_TOTAL', True)
        return Response(result)
    except Exception as e:
        logger.error(f"Error processing investment total: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'series_id': 'INVESTMENT_TOTAL'
        }, status=500)

@api_view(['GET'])
def investment_fixed(request):
    """Fixed Investment - GET /bea/investment-fixed/"""
    try:
        result = BeaIndicatorProcessor.process_indicator_data('INVESTMENT_FIXED', True)
        return Response(result)
    except Exception as e:
        logger.error(f"Error processing investment fixed: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'series_id': 'INVESTMENT_FIXED'
        }, status=500)

@api_view(['GET'])
def investment_nonresidential(request):
    """Nonresidential Investment - GET /bea/investment-nonresidential/"""
    try:
        result = BeaIndicatorProcessor.process_indicator_data('INVESTMENT_NONRESIDENTIAL', True)
        return Response(result)
    except Exception as e:
        logger.error(f"Error processing investment nonresidential: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'series_id': 'INVESTMENT_NONRESIDENTIAL'
        }, status=500)

@api_view(['GET'])
def investment_structures(request):
    """Structures Investment - GET /bea/investment-structures/"""
    try:
        result = BeaIndicatorProcessor.process_indicator_data('INVESTMENT_STRUCTURES', True)
        return Response(result)
    except Exception as e:
        logger.error(f"Error processing investment structures: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'series_id': 'INVESTMENT_STRUCTURES'
        }, status=500)

@api_view(['GET'])
def investment_equipment(request):
    """Equipment Investment - GET /bea/investment-equipment/"""
    try:
        result = BeaIndicatorProcessor.process_indicator_data('INVESTMENT_EQUIPMENT', True)
        return Response(result)
    except Exception as e:
        logger.error(f"Error processing investment equipment: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'series_id': 'INVESTMENT_EQUIPMENT'
        }, status=500)

@api_view(['GET'])
def investment_ip(request):
    """Intellectual Property Products Investment - GET /bea/investment-ip/"""
    try:
        result = BeaIndicatorProcessor.process_indicator_data('INVESTMENT_IP', True)
        return Response(result)
    except Exception as e:
        logger.error(f"Error processing investment ip: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'series_id': 'INVESTMENT_IP'
        }, status=500)

@api_view(['GET'])
def investment_residential(request):
    """Residential Investment - GET /bea/investment-residential/"""
    try:
        result = BeaIndicatorProcessor.process_indicator_data('INVESTMENT_RESIDENTIAL', True)
        return Response(result)
    except Exception as e:
        logger.error(f"Error processing investment residential: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'series_id': 'INVESTMENT_RESIDENTIAL'
        }, status=500)

@api_view(['GET'])
def investment_inventories(request):
    """Change in Private Inventories - GET /bea/investment-inventories/"""
    try:
        result = BeaIndicatorProcessor.process_indicator_data('INVESTMENT_INVENTORIES', True)
        return Response(result)
    except Exception as e:
        logger.error(f"Error processing investment inventories: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'series_id': 'INVESTMENT_INVENTORIES'
        }, status=500)

@api_view(['GET'])
def investment_net(request):
    """Net Private Domestic Investment - GET /bea/investment-net/"""
    try:
        result = BeaIndicatorProcessor.process_indicator_data('INVESTMENT_NET', True)
        return Response(result)
    except Exception as e:
        logger.error(f"Error processing investment net: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'series_id': 'INVESTMENT_NET'
        }, status=500)

@api_view(['GET'])
def govt_investment_total(request):
    """Gross Government Investment - GET /bea/govt-investment-total/"""
    try:
        result = BeaIndicatorProcessor.process_indicator_data('GOVT_INVESTMENT_TOTAL', True)
        return Response(result)
    except Exception as e:
        logger.error(f"Error processing govt investment total: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'series_id': 'GOVT_INVESTMENT_TOTAL'
        }, status=500)
