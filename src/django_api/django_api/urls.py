from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from . import views

# 创建DRF路由器
router = DefaultRouter()

urlpatterns = [
    # 根路径 - API概览
    path("", views.api_root, name="api-root"),
    path("api/", views.api_overview, name="api-overview"),
    # 全局健康检查端点 - 前端和Docker需要
    path("api/health/", views.global_health_check, name="global-health"),
    # Django管理
    path("admin/", admin.site.urls),
    # OpenAPI Schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # API路由 - 对应Flask的/api前缀
    path("api/", include(router.urls)),
    # FRED API路由 - 分离架构
    path("api/fred-us/", include("fred_us.urls")),  # 美国FRED指标
    # 向后兼容路由 - 将旧的/api/fred/重定向到/api/fred-us/
    path("api/fred/", include("fred_us.urls", namespace="fred_us_legacy")),  # 兼容性重定向
    # Japan FRED API路由
    path("api/fred-jp/", include("fred_jp.urls")),
    # BEA API路由
    path("api/bea/", include("bea.urls")),
    # Federal Register policy updates
    path("api/policy/", include("policy_updates.urls")),
    # CSI300 API路由
    path("api/csi300/", include("csi300.urls")),
    # CSI300 Django模板路由 (兼容旧版本)
    path("csi300/", include("csi300.urls", namespace="csi300_legacy")),
    # Stock data API路由 (AkShare integration)
    path("api/stocks/", include("stocks.urls")),
    # Refinitiv API路由
    path("api/", include("refinitiv.urls")),
    # Content API路由
    path("", include("content.urls")),
]
