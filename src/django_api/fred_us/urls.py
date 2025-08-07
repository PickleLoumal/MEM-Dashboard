"""
URL Configuration for US FRED API
美国FRED经济指标API路由配置 - 分离架构实现
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()
router.register(r'', views.FredUsIndicatorViewSet, basename='fred-us')

app_name = 'fred_us'

urlpatterns = [
    # 美国FRED API端点
    path('', include(router.urls)),
]

# 可用的API端点：
# GET  /api/fred-us/                     - 列出所有端点
# GET  /api/fred-us/indicator/           - 获取指定指标数据 (?name=UNRATE&limit=100)
# GET  /api/fred-us/status/              - 获取服务状态
# GET  /api/fred-us/all-indicators/      - 获取所有指标概览
# GET  /api/fred-us/health/              - 健康检查
# POST /api/fred-us/fetch-data/          - 手动获取数据
