"""
URL Configuration for Japan FRED API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建DRF路由器
router = DefaultRouter()
router.register(r'indicators', views.FredJpIndicatorViewSet, basename='fred-jp-indicators')

app_name = 'fred_jp'

urlpatterns = [
    # DRF路由
    path('', include(router.urls)),
    
    # 兼容性API端点
    path('status/', views.FredJpIndicatorViewSet.as_view({'get': 'status'}), name='status'),
    path('health/', views.health_check_jp, name='health'),
]
