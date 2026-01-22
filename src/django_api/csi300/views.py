"""
CSI300 API Views - Unified Company Architecture

提供统一公司数据的 REST API 端点，支持多交易所 (SSE, SZSE, HKEX)。

类型注解说明:
- 所有公共方法都有完整的类型注解
- 使用 shared_types 模块中定义的类型
- Response 返回值类型为 rest_framework.response.Response

对应前端类型: csi300-app/src/shared/api-types/csi300.types.ts
"""

from __future__ import annotations

import contextlib
import logging
import threading
import uuid
from datetime import UTC, datetime
from typing import Any

from django.db import connection
from django.db.models import Max, Min, Q
from django.db.models.query import QuerySet
from django.http import Http404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers as drf_serializers
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

# Backward compatibility imports
from .models import (
    Company,
    GenerationTask,
    InvestmentSummary,
)
from .serializers import (
    CompanyListSerializer,
    CompanySerializer,
    FilterOptionsSerializer,
    GenerationTaskStartResponseSerializer,
    GenerationTaskStatusResponseSerializer,
    IndustryPeersComparisonSerializer,
    InvestmentSummarySerializer,
    PeerComparisonResponseSerializer,
)

# TODO: Remove backward compatibility aliases after full migration to unified Company model
CSI300CompanySerializer = CompanySerializer
CSI300CompanyListSerializer = CompanyListSerializer
CSI300FilterOptionsSerializer = FilterOptionsSerializer
CSI300InvestmentSummarySerializer = InvestmentSummarySerializer
CSI300IndustryPeersComparisonSerializer = IndustryPeersComparisonSerializer
CSI300PeerComparisonResponseSerializer = PeerComparisonResponseSerializer

logger = logging.getLogger(__name__)

# 类型别名
SerializerClass = type[Serializer[Any]]


class CompanyPagination(PageNumberPagination):
    """Company API 分页配置"""

    page_size: int = 20
    page_size_query_param: str = "page_size"
    max_page_size: int = 100


# TODO: Remove backward compatibility alias after full migration
CSI300Pagination = CompanyPagination


class HealthMixin:
    """健康检查 Mixin"""

    @action(detail=False, methods=["get"], url_path="health")
    def health(self, request: Request) -> Response:
        """健康检查端点"""
        try:
            database_available = True
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
            except Exception:
                database_available = False

            count = Company.objects.count() if database_available else 0

            # Count by exchange
            exchange_counts = {}
            if database_available:
                for exchange in Company.Exchange.values:
                    exchange_counts[exchange] = Company.objects.filter(exchange=exchange).count()

            return Response(
                {
                    "status": "healthy" if database_available else "degraded",
                    "service": "Company API",
                    "total_companies": count,
                    "exchange_counts": exchange_counts,
                    "database_available": database_available,
                    "timestamp": datetime.now(tz=UTC).isoformat(),
                }
            )
        except Exception as e:
            logger.exception("Health check failed")
            return Response(
                {
                    "status": "error",
                    "service": "Company API",
                    "error": str(e),
                    "database_available": False,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# TODO: Remove backward compatibility alias after full migration
CSI300HealthMixin = HealthMixin


class SummaryGenerationMixin:
    """摘要生成 Mixin - 异步模式"""

    @extend_schema(
        request=inline_serializer(
            name="GenerateSummaryRequest",
            fields={
                "company_id": drf_serializers.IntegerField(help_text="公司数据库 ID"),
            },
        ),
        responses={
            202: GenerationTaskStartResponseSerializer,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        description="异步启动 Investment Summary 生成任务。立即返回 task_id，前端可通过 task-status API 轮询进度。",
    )
    @action(detail=False, methods=["post"], url_path="generate-summary")
    def generate_summary(self, request: Request) -> Response:
        """
        异步启动 Investment Summary 生成任务

        立即返回 task_id，前端可通过 task-status API 轮询进度。
        支持所有交易所的公司 (SSE, SZSE, HKEX)。
        """
        company_id_raw = request.data.get("company_id")

        if not company_id_raw:
            return Response(
                {"status": "error", "message": "缺少必需参数: company_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            company_id = int(str(company_id_raw))
        except (ValueError, TypeError):
            return Response(
                {"status": "error", "message": "company_id 必须是整数"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 验证公司存在 (支持所有交易所)
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response(
                {"status": "error", "message": f"公司 ID {company_id} 不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 清理僵尸任务：超过 5 分钟仍在 pending/processing 状态的任务
        from datetime import timedelta

        zombie_threshold = datetime.now(tz=UTC) - timedelta(minutes=5)
        zombie_tasks = GenerationTask.objects.filter(
            company_id=company_id,
            status__in=[GenerationTask.Status.PENDING, GenerationTask.Status.PROCESSING],
            updated_at__lt=zombie_threshold,
        )
        zombie_count = zombie_tasks.count()
        if zombie_count > 0:
            zombie_tasks.update(
                status=GenerationTask.Status.FAILED,
                error_message="任务超时，已自动清理",
                completed_at=datetime.now(tz=UTC),
            )
            logger.warning(f"Cleaned up {zombie_count} zombie tasks for company {company_id}")

        # 检查是否已有进行中的任务（非僵尸）
        existing_task = GenerationTask.objects.filter(
            company_id=company_id,
            status__in=[GenerationTask.Status.PENDING, GenerationTask.Status.PROCESSING],
        ).first()

        if existing_task:
            return Response(
                {
                    "status": "accepted",
                    "message": "任务已在进行中",
                    "task_id": existing_task.task_id,
                    "task_status": existing_task.status,
                    "progress_percent": existing_task.progress_percent,
                    "progress_message": existing_task.progress_message,
                },
                status=status.HTTP_202_ACCEPTED,
            )

        # 创建新任务
        task_id = str(uuid.uuid4())
        GenerationTask.objects.create(
            task_id=task_id,
            company=company,
            status=GenerationTask.Status.PENDING,
            progress_message="任务已创建，等待处理...",
            progress_percent=0,
        )

        # 启动后台线程执行生成
        thread = threading.Thread(
            target=self._run_generation_task,
            args=(task_id, company_id),
            daemon=True,
        )
        thread.start()

        logger.info(
            f"Started async generation task {task_id} for company "
            f"{company.ticker} ({company.exchange})"
        )

        return Response(
            {
                "status": "accepted",
                "message": "任务已启动",
                "task_id": task_id,
                "task_status": GenerationTask.Status.PENDING,
                "progress_percent": 0,
                "progress_message": "任务已创建，等待处理...",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    def _run_generation_task(self, task_id: str, company_id: int) -> None:
        """
        后台线程执行生成任务

        注意：此方法在独立线程中运行，需要独立的数据库连接。
        """
        import django

        django.setup()

        from django.db import connection as db_connection

        try:
            # 更新任务状态为处理中
            task = GenerationTask.objects.get(task_id=task_id)
            task.status = GenerationTask.Status.PROCESSING
            task.progress_message = "正在调用 AI 服务..."
            task.progress_percent = 10
            task.save(
                update_fields=["status", "progress_message", "progress_percent", "updated_at"]
            )

            # 导入并调用生成服务
            from .services import generate_company_summary

            # 更新进度
            task.progress_message = "AI 正在搜索和分析数据..."
            task.progress_percent = 30
            task.save(update_fields=["progress_message", "progress_percent", "updated_at"])

            result = generate_company_summary(company_id)

            # 更新任务状态
            task.refresh_from_db()
            if result.get("status") == "success":
                task.status = GenerationTask.Status.COMPLETED
                task.progress_message = "生成完成"
                task.progress_percent = 100
                task.result_data = result.get("data", {})
                task.completed_at = datetime.now(tz=UTC)
                logger.info(f"Task {task_id} completed successfully")
            else:
                task.status = GenerationTask.Status.FAILED
                task.progress_message = "生成失败"
                task.error_message = result.get("message", "未知错误")
                task.completed_at = datetime.now(tz=UTC)
                logger.warning(f"Task {task_id} failed: {task.error_message}")

            task.save()

        except Exception as e:
            logger.exception(f"Task {task_id} failed with exception")
            try:
                task = GenerationTask.objects.get(task_id=task_id)
                task.status = GenerationTask.Status.FAILED
                task.progress_message = "生成失败"
                task.error_message = str(e)
                task.completed_at = datetime.now(tz=UTC)
                task.save()
            except Exception:
                logger.exception(f"Failed to update task {task_id} status after error")
        finally:
            # 关闭数据库连接（线程安全）
            db_connection.close()

    @extend_schema(
        responses={
            200: GenerationTaskStatusResponseSerializer,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        parameters=[
            OpenApiParameter(
                name="task_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="任务 UUID",
            ),
        ],
        description="查询异步生成任务的状态和进度。前端轮询此 API 获取生成进度。",
    )
    @action(detail=False, methods=["get"], url_path="task-status/(?P<task_id>[^/.]+)")
    def task_status(self, request: Request, task_id: str = "") -> Response:
        """
        查询任务状态

        前端轮询此 API 获取生成进度。
        """
        if not task_id:
            return Response(
                {"status": "error", "message": "缺少 task_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            task = GenerationTask.objects.select_related("company").get(task_id=task_id)
        except GenerationTask.DoesNotExist:
            return Response(
                {"status": "error", "message": f"任务 {task_id} 不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_data = {
            "status": "success",
            "task_id": task.task_id,
            "task_status": task.status,
            "progress_percent": task.progress_percent,
            "progress_message": task.progress_message,
            "company_id": task.company_id,
            "company_name": task.company.name,
            "company_ticker": task.company.ticker,
            "exchange": task.company.exchange,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        }

        if task.status == GenerationTask.Status.COMPLETED:
            response_data["result"] = task.result_data
            response_data["completed_at"] = (
                task.completed_at.isoformat() if task.completed_at else None
            )
        elif task.status == GenerationTask.Status.FAILED:
            response_data["error"] = task.error_message
            response_data["completed_at"] = (
                task.completed_at.isoformat() if task.completed_at else None
            )

        return Response(response_data, status=status.HTTP_200_OK)


# TODO: Remove backward compatibility alias after full migration
CSI300SummaryMixin = SummaryGenerationMixin


class CompanyViewSet(HealthMixin, SummaryGenerationMixin, viewsets.ReadOnlyModelViewSet):
    """
    公司数据 ViewSet - 支持多交易所

    提供统一的公司数据 API 端点:
    - list: 获取公司列表 (支持按 exchange 筛选)
    - retrieve: 获取单个公司详情
    - filter_options: 获取筛选选项
    - search: 搜索公司
    - investment_summary: 获取投资摘要
    - industry_peers_comparison: 获取同行业对比
    - health: 健康检查
    - generate_summary: 生成投资摘要
    """

    queryset: QuerySet[Company] = Company.objects.all()
    serializer_class: SerializerClass = CompanySerializer
    pagination_class: type[PageNumberPagination] = CompanyPagination

    def get_serializer_class(self) -> SerializerClass:
        """根据请求动态返回序列化器类"""
        if self.action == "list":
            return CompanyListSerializer
        return CompanySerializer

    def _normalize_region(self, region_value: str | None) -> str | None:
        """标准化地区参数值"""
        if not region_value:
            return None
        normalized = region_value.strip()
        if normalized.lower() == "hong kong (h-shares)":
            return "Hong Kong"
        return normalized

    def _get_exchange_filter(self) -> str | None:
        """从请求参数获取交易所过滤值"""
        exchange = self.request.query_params.get("exchange")
        if exchange:
            exchange_upper = exchange.upper()
            if exchange_upper in Company.Exchange.values:
                return exchange_upper
        return None

    def _region_to_exchange(self, region: str | None) -> str | None:
        """将 region 参数映射到 exchange (向后兼容)"""
        if not region:
            return None
        region_lower = region.lower()
        if "hong kong" in region_lower:
            return Company.Exchange.HKEX
        return None

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="exchange",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by exchange (SSE, SZSE, HKEX)",
                enum=["SSE", "SZSE", "HKEX"],
            ),
            OpenApiParameter(
                name="region",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by region (legacy, prefer using 'exchange')",
            ),
            OpenApiParameter(
                name="im_sector",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by Industry Matrix sector",
            ),
            OpenApiParameter(
                name="industry",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by industry name",
            ),
            OpenApiParameter(
                name="gics_industry",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by GICS industry (partial match)",
            ),
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search by company name or ticker",
            ),
            OpenApiParameter(
                name="industry_search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search by industry name (partial match)",
            ),
            OpenApiParameter(
                name="market_cap_min",
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.QUERY,
                description="Minimum market cap filter",
            ),
            OpenApiParameter(
                name="market_cap_max",
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.QUERY,
                description="Maximum market cap filter",
            ),
        ],
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """获取公司列表或 API 概览"""
        # 检查是否请求 API 概览
        if request.query_params.get("overview") == "true":
            return self._api_overview(request)
        return super().list(request, *args, **kwargs)

    def _api_overview(self, request: Request) -> Response:
        """返回 API 概览信息"""
        total_companies = Company.objects.count()
        exchange_counts = {
            exchange: Company.objects.filter(exchange=exchange).count()
            for exchange in Company.Exchange.values
        }
        return Response(
            {
                "message": "Company API (Multi-Exchange)",
                "version": "2.0.0",
                "supported_exchanges": list(Company.Exchange.values),
                "endpoints": {
                    "companies": "/api/csi300/api/companies/",
                    "company_detail": "/api/csi300/api/companies/{id}/",
                    "filter_options": "/api/csi300/api/companies/filter_options/",
                    "search": "/api/csi300/api/companies/search/",
                    "health": "/api/csi300/api/companies/health/",
                    "generate_summary": "/api/csi300/api/companies/generate-summary/",
                },
                "total_companies": total_companies,
                "exchange_counts": exchange_counts,
            }
        )

    def get_queryset(self) -> Any:
        """获取查询集，根据请求参数动态筛选"""
        queryset = Company.objects.all()

        # Exchange filter (new parameter)
        exchange = self._get_exchange_filter()
        if exchange:
            queryset = queryset.filter(exchange=exchange)

        # TODO: Remove legacy region filter after full migration to exchange
        # Region filter (backward compatibility - maps to exchange)
        region = self._normalize_region(self.request.query_params.get("region"))
        if region and not exchange:
            # Map region to exchange for backward compatibility (deprecated)
            mapped_exchange = self._region_to_exchange(region)
            if mapped_exchange:
                queryset = queryset.filter(exchange=mapped_exchange)
            else:
                # Filter by region field directly
                queryset = queryset.filter(region__iexact=region)

        # IM Sector filter
        im_sector = self.request.query_params.get("im_sector")
        if im_sector:
            queryset = queryset.filter(im_sector__exact=im_sector)

        # Industry filter
        industry = self.request.query_params.get("industry")
        legacy_sub_industry = self.request.query_params.get("sub_industry")
        if not industry and legacy_sub_industry:
            industry = legacy_sub_industry
        if industry:
            queryset = queryset.filter(industry__exact=industry)

        # GICS Industry filter
        gics_industry = self.request.query_params.get("gics_industry")
        if gics_industry:
            queryset = queryset.filter(gics_industry__icontains=gics_industry)

        # Market cap filters
        market_cap_min = self.request.query_params.get("market_cap_min")
        market_cap_max = self.request.query_params.get("market_cap_max")

        if market_cap_min:
            with contextlib.suppress(ValueError, TypeError):
                queryset = queryset.filter(market_cap_local__gte=float(market_cap_min))

        if market_cap_max:
            with contextlib.suppress(ValueError, TypeError):
                queryset = queryset.filter(market_cap_local__lte=float(market_cap_max))

        # Text search
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(ticker__icontains=search)
                | Q(naming__icontains=search)
            )

        # Industry search
        industry_search = self.request.query_params.get("industry_search")
        if industry_search:
            queryset = queryset.filter(Q(industry__icontains=industry_search))

        return queryset.order_by("exchange", "ticker")

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """获取单个公司详情"""
        pk = kwargs.get(self.lookup_field, None)
        if pk is None:
            raise Http404("Company identifier is required")

        instance = Company.objects.filter(pk=pk).first()
        if instance is None:
            raise Http404("Company not found")

        serializer = CompanySerializer(instance, context=self.get_serializer_context())
        return Response(serializer.data)

    @extend_schema(
        responses={200: FilterOptionsSerializer},
        parameters=[
            OpenApiParameter(
                name="exchange",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=["SSE", "SZSE", "HKEX"],
            ),
            OpenApiParameter(
                name="region",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="im_sector",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
        ],
    )
    @action(detail=False, methods=["get"])
    def filter_options(self, request: Request) -> Response:
        """获取可用的筛选选项"""
        exchange_filter = self._get_exchange_filter()
        region_filter = self._normalize_region(request.query_params.get("region"))
        im_sector_filter = request.query_params.get("im_sector")

        base_queryset = Company.objects.all()

        # Apply exchange filter
        if exchange_filter:
            base_queryset = base_queryset.filter(exchange=exchange_filter)
        elif region_filter:
            # TODO: Remove legacy region filter after full migration to exchange
            mapped_exchange = self._region_to_exchange(region_filter)
            if mapped_exchange:
                base_queryset = base_queryset.filter(exchange=mapped_exchange)
            else:
                base_queryset = base_queryset.filter(region__iexact=region_filter)

        # Get available exchanges
        exchanges = list(
            Company.objects.values_list("exchange", flat=True).distinct().order_by("exchange")
        )

        # Get IM sectors
        im_sectors = list(
            base_queryset.exclude(im_sector__isnull=True)
            .exclude(im_sector__exact="")
            .values_list("im_sector", flat=True)
            .distinct()
            .order_by("im_sector")
        )

        # Get industries (optionally filtered by im_sector)
        industry_queryset = base_queryset.exclude(industry__isnull=True).exclude(industry__exact="")
        if im_sector_filter:
            industry_queryset = industry_queryset.filter(im_sector=im_sector_filter)

        industries = list(
            industry_queryset.values_list("industry", flat=True).distinct().order_by("industry")
        )

        # Get GICS industries
        gics_industries = list(
            base_queryset.exclude(gics_industry__isnull=True)
            .exclude(gics_industry__exact="")
            .values_list("gics_industry", flat=True)
            .distinct()
            .order_by("gics_industry")
        )

        # Get market cap range
        market_cap_range = base_queryset.exclude(market_cap_local__isnull=True).aggregate(
            min_cap=Min("market_cap_local"), max_cap=Max("market_cap_local")
        )

        # TODO: Remove legacy regions field after full migration to exchange
        regions = list(
            Company.objects.exclude(region__isnull=True)
            .exclude(region__exact="")
            .values_list("region", flat=True)
            .distinct()
            .order_by("region")
        )

        return Response(
            {
                "exchanges": exchanges,
                "regions": regions,
                "im_sectors": im_sectors,
                "industries": industries,
                "gics_industries": gics_industries,
                "market_cap_range": {
                    "min": float(market_cap_range["min_cap"]) if market_cap_range["min_cap"] else 0,
                    "max": float(market_cap_range["max_cap"]) if market_cap_range["max_cap"] else 0,
                },
                "filtered_by_exchange": bool(exchange_filter),
                "exchange_filter": exchange_filter,
                "filtered_by_region": bool(region_filter),
                "region_filter": region_filter,
                "filtered_by_sector": bool(im_sector_filter),
                "sector_filter": im_sector_filter,
            }
        )

    @extend_schema(
        responses={200: CompanyListSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="q",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
            ),
            OpenApiParameter(
                name="exchange",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=["SSE", "SZSE", "HKEX"],
            ),
        ],
    )
    @action(detail=False, methods=["get"])
    def search(self, request: Request) -> Response:
        """搜索公司"""
        query = request.query_params.get("q", "") or ""

        if not query:
            return Response(
                {"error": "Search query is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        queryset = Company.objects.filter(
            Q(name__icontains=query) | Q(ticker__icontains=query) | Q(naming__icontains=query)
        )

        # Optional exchange filter
        exchange = self._get_exchange_filter()
        if exchange:
            queryset = queryset.filter(exchange=exchange)

        companies = queryset.order_by("exchange", "ticker")[:10]

        serializer = CompanyListSerializer(companies, many=True)
        return Response(serializer.data)

    @extend_schema(responses={200: InvestmentSummarySerializer})
    @action(detail=True, methods=["get"])
    def investment_summary(self, request: Request, pk: str | None = None) -> Response:
        """获取公司投资摘要"""
        try:
            company = self.get_object()
            summary = InvestmentSummary.objects.filter(company=company).first()

            if not summary:
                return Response(
                    {"error": "Investment summary not found for this company"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = InvestmentSummarySerializer(summary)
            return Response(serializer.data)

        except Exception:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(responses={200: PeerComparisonResponseSerializer})
    @action(detail=True, methods=["get"])
    def industry_peers_comparison(self, request: Request, pk: str | None = None) -> Response:
        """获取同行业公司对比数据"""
        try:
            company = self.get_object()

            if not company.im_sector:
                return Response(
                    {"error": "Company industry information not available"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get all companies in the same im_sector (across all exchanges)
            all_industry_companies = (
                Company.objects.filter(im_sector=company.im_sector)
                .exclude(market_cap_local__isnull=True)
                .order_by("-market_cap_local")
            )

            current_company_rank: int | None = None
            for idx, comp in enumerate(all_industry_companies, 1):
                if comp.id == company.id:
                    current_company_rank = idx
                    break

            top_3_companies = all_industry_companies[:3]

            if not top_3_companies:
                return Response(
                    {"error": "No companies found in the same industry"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            comparison_data: list[dict[str, Any]] = []

            company_serializer = IndustryPeersComparisonSerializer(company)
            company_data: dict[str, Any] = company_serializer.data
            company_data["rank"] = current_company_rank
            company_data["is_current_company"] = True
            comparison_data.append(company_data)

            for idx, top_company in enumerate(top_3_companies, 1):
                top_serializer = IndustryPeersComparisonSerializer(top_company)
                top_data: dict[str, Any] = top_serializer.data
                top_data["rank"] = idx
                top_data["is_current_company"] = top_company.id == company.id
                comparison_data.append(top_data)

            return Response(
                {
                    "target_company": {
                        "id": company.id,
                        "exchange": company.exchange,
                        "name": company.name,
                        "ticker": company.ticker,
                        "im_sector": company.im_sector,
                        "rank": current_company_rank,
                    },
                    "industry": company.im_sector,
                    "comparison_data": comparison_data,
                    "total_top_companies_shown": len(top_3_companies),
                    "total_companies_in_industry": all_industry_companies.count(),
                }
            )

        except Exception:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)


# TODO: Remove backward compatibility alias after full migration
CSI300CompanyViewSet = CompanyViewSet


# ==========================================
# 向后兼容的独立函数视图 (保持旧 URL 可用)
# ==========================================


@extend_schema(
    responses={
        200: inline_serializer(
            name="CSI300IndexResponse",
            fields={
                "message": drf_serializers.CharField(),
                "version": drf_serializers.CharField(),
                "supported_exchanges": drf_serializers.ListField(child=drf_serializers.CharField()),
                "endpoints": drf_serializers.DictField(),
                "total_companies": drf_serializers.IntegerField(),
            },
        )
    }
)
@api_view(["GET"])
def csi300_index(request: Request) -> Response:
    """CSI300 API 索引端点 (向后兼容)"""
    total_companies = Company.objects.count()

    return Response(
        {
            "message": "Company API (Multi-Exchange)",
            "version": "2.0.0",
            "supported_exchanges": list(Company.Exchange.values),
            "endpoints": {
                "companies": "/api/csi300/api/companies/",
                "company_detail": "/api/csi300/api/companies/{id}/",
                "filter_options": "/api/csi300/api/companies/filter_options/",
                "search": "/api/csi300/api/companies/search/",
                "health": "/api/csi300/api/companies/health/",
            },
            "total_companies": total_companies,
        }
    )


@extend_schema(
    responses={
        200: inline_serializer(
            name="CSI300HealthCheckResponse",
            fields={
                "status": drf_serializers.CharField(),
                "service": drf_serializers.CharField(),
                "total_companies": drf_serializers.IntegerField(),
                "database_available": drf_serializers.BooleanField(),
            },
        )
    }
)
@api_view(["GET"])
def health_check(request: Request) -> Response:
    """CSI300 API 健康检查端点 (向后兼容)"""
    try:
        count = Company.objects.count()
        return Response(
            {
                "status": "healthy",
                "service": "Company API",
                "total_companies": count,
                "database_available": True,
            }
        )
    except Exception as e:
        return Response(
            {
                "status": "error",
                "service": "Company API",
                "error": str(e),
                "database_available": False,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    request=inline_serializer(
        name="GenerateInvestmentSummaryRequest",
        fields={
            "company_id": drf_serializers.IntegerField(help_text="公司数据库 ID"),
        },
    ),
    responses={
        202: GenerationTaskStartResponseSerializer,
        400: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
    description="异步启动 Investment Summary 生成任务 (向后兼容端点)",
)
@api_view(["POST"])
def generate_investment_summary(request: Request) -> Response:
    """生成指定公司的 Investment Summary (向后兼容)"""
    # 委托给 ViewSet 的实现
    viewset = CompanyViewSet()
    viewset.request = request
    viewset.format_kwarg = None
    return viewset.generate_summary(request)


@extend_schema(
    summary="查询任务状态",
    description="查询异步生成任务的状态和进度 (向后兼容端点)",
    responses={
        200: GenerationTaskStatusResponseSerializer,
        400: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
    parameters=[
        OpenApiParameter(
            name="task_id",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description="任务 UUID",
        ),
    ],
)
@api_view(["GET"])
def task_status_view(request: Request, task_id: str) -> Response:
    """查询任务状态 (向后兼容)"""
    # 委托给 ViewSet 的实现
    viewset = CompanyViewSet()
    viewset.request = request
    viewset.format_kwarg = None
    return viewset.task_status(request, task_id=task_id)
