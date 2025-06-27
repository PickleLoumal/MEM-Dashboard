from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime

# Create your views here.

def index(request):
    """指标API首页"""
    return JsonResponse({
        'service': 'MEM Dashboard Django API - Indicators',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'endpoints': [
            '/fred/',
            '/bea/',
            '/monetary-base/',
            '/health/'
        ]
    })

def fred_data(request):
    """FRED数据端点"""
    return JsonResponse({
        'service': 'FRED Data',
        'status': 'available',
        'message': 'FRED数据服务正常运行',
        'timestamp': datetime.now().isoformat()
    })

def bea_data(request):
    """BEA数据端点"""
    return JsonResponse({
        'service': 'BEA Data',
        'status': 'available',
        'message': 'BEA数据服务正常运行',
        'timestamp': datetime.now().isoformat()
    })

def monetary_base(request):
    """货币基础数据端点"""
    return JsonResponse({
        'service': 'Monetary Base',
        'status': 'available',
        'message': '货币基础数据服务正常运行',
        'timestamp': datetime.now().isoformat()
    })

def health_check(request):
    """健康检查端点"""
    return JsonResponse({
        'service': 'Django API Health Check',
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })
