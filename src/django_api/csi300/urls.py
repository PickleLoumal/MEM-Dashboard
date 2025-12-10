"""
CSI300 URL Configuration

提供两种访问方式:
1. 新路由 (推荐): 通过 ViewSet actions 访问
   - /api/csi300/api/companies/health/
   - /api/csi300/api/companies/generate-summary/
   
2. 旧路由 (向后兼容): 保持原有 URL 可用
   - /api/csi300/health/
   - /api/csi300/api/generate-summary/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r'companies', views.CSI300CompanyViewSet, basename='csi300-company')

app_name = 'csi300'

urlpatterns = [
    # API routes with DRF router (新路由)
    path('api/', include(router.urls)),
    
    # 向后兼容的旧路由
    path('', views.csi300_index, name='csi300_index'),
    path('health/', views.health_check, name='csi300_health_check'),
    path('api/generate-summary/', views.generate_investment_summary, name='generate_investment_summary'),
]
