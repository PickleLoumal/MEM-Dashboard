"""
Django API Root Views for MEM Dashboard
提供API概览和根路径响应
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime


@api_view(['GET'])
def api_root(request):
    """根路径 - API欢迎信息"""
    return Response({
        'message': 'MEM Dashboard Django API',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'documentation': '/api/',
        'health_check': '/api/health/',
        'status': 'operational'
    })


@api_view(['GET'])
def api_overview(request):
    """API概览 - 所有可用端点"""
    return Response({
        'api_name': 'MEM Dashboard Django REST API',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'health': '/api/health/',
            'fred_status': '/api/fred/status/',
            'fred_all': '/api/fred/all/',
            'money_supply': {
                'm2': '/api/fred/m2/',
                'm1': '/api/fred/m1/',
                'm2_velocity': '/api/fred/m2v/',
                'monetary_base': '/api/fred/monetary-base/'
            },
            'economic_indicators': {
                'cpi': '/api/fred/cpi/',
                'unemployment': '/api/fred/unemployment/',
                'housing_starts': '/api/fred/housing/',
                'fed_funds_rate': '/api/fred/fed-funds/',
                'debt_to_gdp': '/api/fred/debt-to-gdp/'
            }
        },
        'documentation': 'Django REST Framework compatible API',
        'migration_status': 'Django-Only deployment - Flask completely removed'
    })


@api_view(['GET'])
def global_health_check(request):
    """全局健康检查端点 - 前端和Docker健康检查使用"""
    try:
        from django.db import connection
        
        # 检查数据库连接
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            database_available = True
    except Exception:
        database_available = False
    
    return Response({
        'status': 'healthy' if database_available else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'service': 'MEM Dashboard Django API',
        'environment': 'development',
        'database_available': database_available,
        'version': '2.0.0',
        'components': {
            'fred_us': 'available',
            'fred_jp': 'available', 
            'bea': 'available',
            'content': 'available'
        }
    })