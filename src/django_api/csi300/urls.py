from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r'companies', views.CSI300CompanyViewSet, basename='csi300-company')

app_name = 'csi300'

urlpatterns = [
    # API routes with DRF router
    path('api/', include(router.urls)),
    
    # Main endpoints
    path('', views.csi300_index, name='csi300_index'),
    path('health/', views.health_check, name='csi300_health_check'),
    
    # Investment Summary 生成
    path('api/generate-summary/', views.generate_investment_summary, name='generate_investment_summary'),
]