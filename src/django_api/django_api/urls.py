"""
Django + DRF URL Configuration for MEM Dashboard 
映射Flask API端点，保持完全兼容性，支持FRED和BEA APIs
分离架构实现 - 支持fred_us和fred_jp独立应用
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Django API主要URL配置
# 映射Flask API端点，保持完全兼容性，支持FRED和BEA APIs
# 分离架构实现 - 支持fred_us和fred_jp独立应用

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建DRF路由器
router = DefaultRouter()

urlpatterns = [
    # 根路径 - API概览
    path('', views.api_root, name='api-root'),
    path('api/', views.api_overview, name='api-overview'),
    
    # 全局健康检查端点 - 前端和Docker需要
    path('api/health/', views.global_health_check, name='global-health'),
    
    # Django管理
    path('admin/', admin.site.urls),
    
    # API路由 - 对应Flask的/api前缀
    path('api/', include(router.urls)),
    
    # FRED API路由 - 分离架构
    path('api/fred-us/', include('fred_us.urls')),      # 美国FRED指标
    
    # 向后兼容路由 - 将旧的/api/fred/重定向到/api/fred-us/
    path('api/fred/', include('fred_us.urls')),         # 兼容性重定向
    
    # Japan FRED API路由  
    path('api/fred-jp/', include('fred_jp.urls')),
    
    # BEA API路由
    path('api/bea/', include('bea.urls')),
    
    # CSI300 API路由
    path('api/csi300/', include('csi300.urls')),
    
    # Content API路由
    path('', include('content.urls')),
]
