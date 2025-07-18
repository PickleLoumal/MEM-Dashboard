"""
URL Configuration for FRED API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建DRF路由器
router = DefaultRouter()
router.register(r'indicators', views.FredIndicatorViewSet, basename='fred-indicators')

app_name = 'fred'

urlpatterns = [
    # DRF路由
    path('', include(router.urls)),
    
    # 兼容性API端点
    path('status/', views.fred_api_status, name='status'),
]
