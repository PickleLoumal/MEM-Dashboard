# ==========================================
# Refinitiv API Views
# ==========================================

import logging

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from .rdp_client import RDPClient
from .serializers import (
    FinancialContextSerializer,
    RefinitivConnectionStatusSerializer,
)

logger = logging.getLogger(__name__)


class RefinitivViewSet(viewsets.ViewSet):
    """Refinitiv 数据 API。"""

    # 默认序列化器（用于 drf-spectacular schema 生成）
    serializer_class = FinancialContextSerializer

    @extend_schema(
        summary="测试 Refinitiv 连接",
        description="测试与 Refinitiv Data Platform 的连接状态。",
        responses={200: RefinitivConnectionStatusSerializer},
        tags=["Refinitiv"],
    )
    @action(detail=False, methods=["get"], url_path="status")
    def connection_status(self, request: Request) -> Response:
        """测试 Refinitiv API 连接状态。"""
        with RDPClient() as client:
            result = client.test_connection()

        serializer = RefinitivConnectionStatusSerializer(result)
        return Response(serializer.data)

    @extend_schema(
        summary="获取公司财务数据",
        description="从 Refinitiv 获取指定公司的完整财务数据，用于 Investment Summary 生成。",
        parameters=[
            OpenApiParameter(
                name="ric",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Reuters Instrument Code (e.g., 0425.SZ for XCMG)",
                required=True,
            ),
        ],
        responses={200: FinancialContextSerializer},
        tags=["Refinitiv"],
    )
    @action(detail=False, methods=["get"], url_path="financial-data")
    def financial_data(self, request: Request) -> Response:
        """获取公司财务数据。"""
        ric = request.query_params.get("ric")

        if not ric:
            return Response(
                {"error": "RIC parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with RDPClient() as client:
            # 测试连接
            conn_status = client.test_connection()
            if not conn_status["authenticated"]:
                return Response(
                    {
                        "error": "Refinitiv authentication failed",
                        "details": conn_status.get("error"),
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            # 获取数据
            data = client.get_investment_summary_data(ric)

        # 返回原始数据（用于调试/测试）
        return Response(data)

    @extend_schema(
        summary="搜索股票代码",
        description="通过公司名称或代码搜索 Refinitiv 股票代码 (RIC)。",
        parameters=[
            OpenApiParameter(
                name="query",
                type=str,
                location=OpenApiParameter.QUERY,
                description="搜索关键词 (e.g., 'XCMG', 'construction machinery')",
                required=True,
            ),
            OpenApiParameter(
                name="limit",
                type=int,
                location=OpenApiParameter.QUERY,
                description="最大返回数量",
                required=False,
                default=10,
            ),
        ],
        tags=["Refinitiv"],
    )
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request: Request) -> Response:
        """搜索股票代码。"""
        query = request.query_params.get("query")
        limit = int(request.query_params.get("limit", 10))

        if not query:
            return Response(
                {"error": "Query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with RDPClient() as client:
            conn_status = client.test_connection()
            if not conn_status["authenticated"]:
                return Response(
                    {"error": "Refinitiv authentication failed"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            result = client.search_symbology(query, limit=limit)

        return Response(result or {"results": []})
