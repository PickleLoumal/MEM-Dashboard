"""
通用 ViewSet Mixins

为所有 ViewSet 提供统一的健康检查、错误响应和状态端点。
"""

import logging
from datetime import UTC, datetime
from typing import Any

from django.db import connection
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class HealthCheckMixin:
    """
    健康检查 Mixin - 所有 ViewSet 共用

    子类可覆盖 service_name 和 country 属性。
    """

    @property
    def service_name(self) -> str:
        """服务名称，子类应覆盖此属性"""
        return "API Service"

    @property
    def country(self) -> str:
        """国家/地区代码，子类应覆盖此属性"""
        return "Unknown"

    @action(detail=False, methods=["get"])
    def health(self, request) -> Response:
        """
        通用健康检查端点

        GET /api/{service}/health/
        """
        try:
            database_available = True
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
            except Exception:
                database_available = False

            api_connection = self._check_api_connection()
            health_status = "healthy" if (database_available and api_connection) else "degraded"

            return Response(
                {
                    "status": health_status,
                    "timestamp": datetime.now(tz=UTC).isoformat(),
                    "service": self.service_name,
                    "database_available": database_available,
                    "api_connection": api_connection,
                    "version": "1.0.0",
                    "country": self.country,
                }
            )
        except Exception as e:
            logger.exception("Health check failed for {self.service_name}")
            return Response(
                {
                    "status": "unhealthy",
                    "timestamp": datetime.now(tz=UTC).isoformat(),
                    "service": self.service_name,
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _check_api_connection(self) -> bool:
        """
        检查 API 连接状态
        子类可覆盖此方法以实现自定义检查
        """
        # 默认返回 True，子类可覆盖
        return True


class ErrorResponseMixin:
    """
    标准化错误响应 Mixin

    提供统一的错误响应格式。
    """

    @property
    def country(self) -> str:
        """国家/地区代码，子类应覆盖此属性"""
        return "Unknown"

    def error_response(
        self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, **kwargs
    ) -> Response:
        """
        生成标准化错误响应

        Args:
            message: 错误消息
            status_code: HTTP 状态码
            **kwargs: 额外的错误详情

        Returns:
            Response: 错误响应
        """
        error_data: dict[str, Any] = {
            "success": False,
            "error": message,
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "country": self.country,
            **kwargs,
        }
        return Response(error_data, status=status_code)

    def not_found_response(self, resource: str, identifier: str) -> Response:
        """生成 404 响应"""
        return self.error_response(
            f"{resource} not found: {identifier}", status_code=status.HTTP_404_NOT_FOUND
        )

    def server_error_response(self, exception: Exception) -> Response:
        """生成 500 响应"""
        logger.error(f"Server error: {exception}")
        return self.error_response(
            "Internal server error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=str(exception),
        )


class StatusMixin:
    """
    系统状态 Mixin

    提供系统状态端点。
    """

    @property
    def service_name(self) -> str:
        """服务名称，子类应覆盖此属性"""
        return "API Service"

    @property
    def country(self) -> str:
        """国家/地区代码，子类应覆盖此属性"""
        return "Unknown"

    @action(detail=False, methods=["get"])
    def status(self, request) -> Response:
        """
        系统状态端点

        GET /api/{service}/status/
        """
        try:
            database_available = True
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
            except Exception:
                database_available = False

            return Response(
                {
                    "success": True,
                    "system": self.service_name,
                    "database_available": database_available,
                    "status": {
                        "last_check": datetime.now(tz=UTC).isoformat(),
                        "country": self.country,
                    },
                }
            )
        except Exception as e:
            logger.exception("Status check failed for {self.service_name}")
            return Response(
                {"success": False, "system": self.service_name, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FredViewSetMixin(HealthCheckMixin, ErrorResponseMixin, StatusMixin):
    """
    组合 Mixin - 包含健康检查、错误响应和状态功能

    继承此 Mixin 即可获得所有通用功能。
    子类需要设置 service_name 和 country 属性。
    """


__all__ = [
    "ErrorResponseMixin",
    "FredViewSetMixin",
    "HealthCheckMixin",
    "StatusMixin",
]
