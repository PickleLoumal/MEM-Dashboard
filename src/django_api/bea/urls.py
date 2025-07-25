"""
BEA API URL Configuration
支持动态配置驱动的端点路由
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r'data', views.BeaIndicatorViewSet, basename='bea-indicator')
router.register(r'configs', views.BeaConfigViewSet, basename='bea-config')

app_name = 'bea'

urlpatterns = [
    # DRF API Routes
    path('api/', include(router.urls)),
    
    # Main endpoints
    path('', views.index, name='bea_index'),
    path('all_indicators/', views.all_indicators, name='all_indicators'),
    path('stats/', views.stats, name='bea_stats'),
    path('health/', views.health_check, name='bea_health_check'),
    
    # Category endpoints
    path('category/<str:category>/', views.category_indicators, name='category_indicators'),
    
    # Dynamic indicator endpoints
    path('indicator/<str:series_id>/', views.dynamic_indicator, name='dynamic_indicator'),
    
    # Legacy compatibility endpoints
    path('indicators/', views.bea_indicators, name='bea_indicators'),
    path('indicators/motor_vehicles/', views.motor_vehicles_data, name='motor_vehicles_data'),
    path('indicators/recreational_goods/', views.recreational_goods_data, name='recreational_goods_data'),
]
