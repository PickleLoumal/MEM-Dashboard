"""
Django + DRF URL Configuration for MEM Dashboard 
映射Flask API端点，保持完全兼容性，支持FRED和BEA APIs
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from fred.views import FredIndicatorViewSet, flask_compatibility_view
from . import views

# 创建DRF路由器
router = DefaultRouter()
router.register(r'fred', FredIndicatorViewSet, basename='fred')

urlpatterns = [
    # 根路径 - API概览
    path('', views.api_root, name='api-root'),
    path('api/', views.api_overview, name='api-overview'),
    
    # Django管理
    path('admin/', admin.site.urls),
    
    # API路由 - 对应Flask的/api前缀
    path('api/', include(router.urls)),
    
    # FRED API路由
    path('api/fred/', include('fred.urls')),
    
    # BEA API路由
    path('api/bea/', include('bea.urls')),
    
    # Content API路由
    path('', include('content.urls')),
    
    # 兼容性路由 - 直接映射到根API路径 (与Flask保持一致)
    path('api/motor-vehicles/', include('bea.urls')),
    
    # 额外的健康检查端点 - 对应Flask /api/health
    path('api/health/', FredIndicatorViewSet.as_view({'get': 'health_check'}), name='health-check'),
    
    # ============================================================================
    # Flask 兼容性端点 - 高优先级遗留端点
    # ============================================================================
    
    # 主要货币供应端点
    path('api/m2-money-supply/', flask_compatibility_view, {'series_id': 'M2SL'}, name='m2-money-supply'),
    path('api/m1-money-stock/', flask_compatibility_view, {'series_id': 'M1SL'}, name='m1-money-stock'),
    path('api/m2-velocity/', flask_compatibility_view, {'series_id': 'M2V'}, name='m2-velocity'),
    path('api/monetary-base/', flask_compatibility_view, {'series_id': 'BOGMBASE'}, name='monetary-base'),
    path('api/debt-to-gdp-db/', flask_compatibility_view, {'series_id': 'GFDEGDQ188S'}, name='debt-to-gdp-db'),
    
    # 数据库直接访问端点 (低优先级，但需要保持兼容性)
    path('api/m2-db/', flask_compatibility_view, {'series_id': 'M2SL'}, name='m2-db'),
    path('api/m1-db/', flask_compatibility_view, {'series_id': 'M1SL'}, name='m1-db'),
    path('api/m2v-db/', flask_compatibility_view, {'series_id': 'M2V'}, name='m2v-db'),
    path('api/monetary-base-db/', flask_compatibility_view, {'series_id': 'BOGMBASE'}, name='monetary-base-db'),
    path('api/cpi-db/', flask_compatibility_view, {'series_id': 'CPIAUCSL'}, name='cpi-db'),
    path('api/unrate-db/', flask_compatibility_view, {'series_id': 'UNRATE'}, name='unrate-db'),
    path('api/housing-db/', flask_compatibility_view, {'series_id': 'HOUST'}, name='housing-db'),
    
    # 指标状态端点
    path('api/indicators/status/', FredIndicatorViewSet.as_view({'get': 'fred_status'}), name='indicators-status'),
]
