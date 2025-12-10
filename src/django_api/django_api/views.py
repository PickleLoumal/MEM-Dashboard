"""
Django API Root Views for MEM Dashboard
提供API概览和根路径响应
"""

from datetime import UTC, datetime

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response


@extend_schema(
    responses={
        200: inline_serializer(
            name="ApiRootResponse",
            fields={
                "message": serializers.CharField(),
                "version": serializers.CharField(),
                "timestamp": serializers.CharField(),
                "documentation": serializers.CharField(),
                "health_check": serializers.CharField(),
                "status": serializers.CharField(),
            },
        )
    }
)
@api_view(["GET"])
def api_root(request):
    """根路径 - API欢迎信息"""
    return Response(
        {
            "message": "MEM Dashboard Django API",
            "version": "2.0.0",
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "documentation": "/api/",
            "health_check": "/api/health/",
            "status": "operational",
        }
    )


@extend_schema(
    responses={
        200: inline_serializer(
            name="ApiOverviewResponse",
            fields={
                "api_name": serializers.CharField(),
                "version": serializers.CharField(),
                "timestamp": serializers.CharField(),
                "endpoints": serializers.DictField(),
                "documentation": serializers.CharField(),
                "migration_status": serializers.CharField(),
            },
        )
    }
)
@api_view(["GET"])
def api_overview(request):
    """API概览 - 所有可用端点"""
    return Response(
        {
            "api_name": "MEM Dashboard Django REST API",
            "version": "2.0.0",
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "endpoints": {
                "health": "/api/health/",
                "fred_status": "/api/fred/status/",
                "fred_all": "/api/fred/all/",
                "money_supply": {
                    "m2": "/api/fred/m2/",
                    "m1": "/api/fred/m1/",
                    "m2_velocity": "/api/fred/m2v/",
                    "monetary_base": "/api/fred/monetary-base/",
                },
                "economic_indicators": {
                    "cpi": "/api/fred/cpi/",
                    "unemployment": "/api/fred/unemployment/",
                    "housing_starts": "/api/fred/housing/",
                    "fed_funds_rate": "/api/fred/fed-funds/",
                    "debt_to_gdp": "/api/fred/debt-to-gdp/",
                },
            },
            "documentation": "Django REST Framework compatible API",
            "migration_status": "Django-Only deployment - Flask completely removed",
        }
    )


@extend_schema(
    responses={
        200: inline_serializer(
            name="GlobalHealthCheckResponse",
            fields={
                "status": serializers.CharField(),
                "timestamp": serializers.CharField(),
                "service": serializers.CharField(),
                "environment": serializers.CharField(),
                "database_available": serializers.BooleanField(),
                "version": serializers.CharField(),
                "components": serializers.DictField(),
                "csi300_companies_count": serializers.IntegerField(),
            },
        )
    }
)
@api_view(["GET"])
def global_health_check(request):
    """全局健康检查端点 - 前端和Docker健康检查使用"""
    try:
        from django.db import connection

        # 检查数据库连接
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            database_available = True

        # 检查CSI300组件
        try:
            from csi300.models import CSI300Company

            csi300_available = True
            total_companies = CSI300Company.objects.count()
        except Exception:
            csi300_available = False
            total_companies = 0

    except Exception:
        database_available = False
        csi300_available = False
        total_companies = 0

    return Response(
        {
            "status": "healthy" if (database_available and csi300_available) else "degraded",
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "service": "MEM Dashboard Django API",
            "environment": "development",
            "database_available": database_available,
            "version": "2.0.0",
            "components": {
                "fred_us": "available",
                "fred_jp": "available",
                "bea": "available",
                "content": "available",
                "csi300": "available" if csi300_available else "unavailable",
            },
            "csi300_companies_count": total_companies,
        }
    )
