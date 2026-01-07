"""
PDF Service Views

API endpoints for PDF generation requests, status tracking, and downloads.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import uuid as uuid_module

from csi300.models import CSI300Company, CSI300InvestmentSummary
from django.db import transaction
from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from fred_common.viewset_mixins import ErrorResponseMixin

from .consumers import send_task_status_update
from .models import PDFTask, PDFTemplate
from .serializers import (
    PDFDownloadResponseSerializer,
    PDFRequestSerializer,
    PDFTaskCreateResponseSerializer,
    PDFTaskSerializer,
    PDFTemplateDetailSerializer,
    PDFTemplateSerializer,
)
from .tasks import generate_presigned_download_url, publish_pdf_task, update_task_status_from_worker

logger = logging.getLogger(__name__)


class PDFTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing available PDF templates.

    Provides read-only access to active templates for selection.
    """

    queryset = PDFTemplate.objects.filter(is_active=True)
    serializer_class = PDFTemplateSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PDFTemplateDetailSerializer
        return PDFTemplateSerializer


class PDFTaskViewSet(ErrorResponseMixin, viewsets.ViewSet):
    """
    ViewSet for PDF generation task management.

    Endpoints:
    - POST /request/ - Request new PDF generation
    - GET /status/{task_id}/ - Get task status
    - GET /download/{task_id}/ - Get download URL
    """

    @extend_schema(
        request=PDFRequestSerializer,
        responses={
            201: PDFTaskCreateResponseSerializer,
            400: dict,
            404: dict,
        },
        description="Request generation of a PDF report for a company",
    )
    @action(detail=False, methods=["post"], url_path="request")
    def request_pdf(self, request: Request) -> Response:
        """
        Request PDF generation for a company.

        Creates a new PDFTask and publishes to SQS for async processing.
        Returns task_id for status tracking via polling or WebSocket.
        """
        serializer = PDFRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        company_id = serializer.validated_data["company_id"]
        template_id = serializer.validated_data.get("template_id")

        # Get company (already validated in serializer, but verify for race conditions)
        try:
            company = CSI300Company.objects.get(pk=company_id)
        except CSI300Company.DoesNotExist:
            return Response(
                {"success": False, "error": f"Company {company_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get template with proper exception handling
        try:
            if template_id:
                template = PDFTemplate.objects.get(pk=template_id, is_active=True)
            else:
                template = PDFTemplate.objects.filter(is_default=True, is_active=True).first()
                if not template:
                    template = PDFTemplate.objects.filter(is_active=True).first()
                if not template:
                    return Response(
                        {"success": False, "error": "No active PDF template available"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        except PDFTemplate.DoesNotExist:
            return Response(
                {"success": False, "error": f"Template {template_id} not found or inactive"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Prepare data payloads
        summary_data = self._prepare_summary_data(company)
        company_data = self._prepare_company_data(company)

        # Get requester info
        requested_by = self._get_requester_id(request)

        # Create task and publish to SQS atomically
        try:
            with transaction.atomic():
                task = PDFTask.objects.create(
                    company=company,
                    template=template,
                    requested_by=requested_by,
                    request_metadata={
                        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                        "ip_address": self._get_client_ip(request),
                    },
                )

                # Publish to SQS - if fails, mark task as failed
                sqs_success = publish_pdf_task(task, summary_data, company_data)

                if not sqs_success:
                    # Mark task as failed if SQS publish fails
                    task.status = PDFTask.Status.FAILED
                    task.error_message = "Failed to queue task for processing"
                    task.save(update_fields=["status", "error_message"])

                    logger.error(
                        "Failed to publish PDF task to SQS",
                        extra={
                            "task_id": str(task.task_id),
                            "company_ticker": company.ticker,
                        },
                    )
                    return Response(
                        {
                            "success": False,
                            "error": "Failed to queue PDF generation task",
                            "task_id": str(task.task_id),
                        },
                        status=status.HTTP_503_SERVICE_UNAVAILABLE,
                    )

        except Exception as e:
            logger.exception(
                "Failed to create PDF task",
                extra={"company_id": company_id, "error": str(e)},
            )
            return Response(
                {"success": False, "error": "Internal error creating PDF task"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        logger.info(
            "PDF generation task created",
            extra={
                "task_id": str(task.task_id),
                "company_ticker": company.ticker,
                "template": template.name,
            },
        )

        # Build WebSocket URL
        # Determine if request is HTTPS:
        # 1. request.is_secure() with SECURE_PROXY_SSL_HEADER in settings.py
        # 2. X-Forwarded-Proto header (set by ALB/CloudFront)
        # 3. CloudFront URLs are always HTTPS
        host = request.get_host()
        is_https = (
            request.is_secure()
            or request.headers.get("X-Forwarded-Proto") == "https"
            or "cloudfront.net" in host  # CloudFront URLs are always HTTPS
            or request.headers.get("CloudFront-Forwarded-Proto") == "https"
        )
        ws_protocol = "wss" if is_https else "ws"
        websocket_url = f"{ws_protocol}://{host}/ws/pdf/{task.task_id}/"

        return Response(
            {
                "task_id": str(task.task_id),
                "status": task.status,
                "message": f"PDF generation started for {company.ticker}",
                "websocket_url": websocket_url,
            },
            status=status.HTTP_201_CREATED,
        )

    def _prepare_summary_data(self, company: CSI300Company) -> dict:
        """Extract investment summary data for PDF generation."""
        try:
            summary = CSI300InvestmentSummary.objects.get(company=company)
            return {
                # Required by LaTeX template (line 37)
                "company_name": company.name,
                "report_date": str(summary.report_date),
                "stock_price_previous_close": float(summary.stock_price_previous_close or 0),
                "market_cap_display": summary.market_cap_display,
                "recommended_action": summary.recommended_action,
                "recommended_action_detail": summary.recommended_action_detail,
                "business_overview": summary.business_overview,
                "business_performance": summary.business_performance,
                "industry_context": summary.industry_context,
                "financial_stability": summary.financial_stability,
                "key_financials_valuation": summary.key_financials_valuation,
                "big_trends_events": summary.big_trends_events,
                "customer_segments": summary.customer_segments,
                "competitive_landscape": summary.competitive_landscape,
                "risks_anomalies": summary.risks_anomalies,
                "forecast_outlook": summary.forecast_outlook,
                # Alias for template compatibility (line 268)
                "growth_analysis": summary.forecast_outlook,
                "investment_firms_views": summary.investment_firms_views,
                "industry_ratio_analysis": summary.industry_ratio_analysis,
                "tariffs_supply_chain_risks": summary.tariffs_supply_chain_risks,
                "key_takeaways": summary.key_takeaways,
                "sources": summary.sources,
                # Risk factors list (template lines 232-241)
                "risk_factors": [],  # Placeholder - can be populated from structured data
            }
        except CSI300InvestmentSummary.DoesNotExist:
            return {
                "company_name": company.name,
                "risk_factors": [],
            }

    def _prepare_company_data(self, company: CSI300Company) -> dict:
        """Extract company financial data for PDF generation."""
        return {
            # Basic Info
            "name": company.name,
            "ticker": company.ticker,
            "region": company.region,
            "industry": company.industry,
            "im_sector": company.im_sector,
            "business_description": company.business_description,
            # Alias mappings for LaTeX template compatibility
            "sector": company.im_sector,  # Template uses 'sector' (lines 47, 107)
            "country": company.region,  # Template uses 'country' (line 110)
            "exchange_code": self._get_exchange_code(company),  # Lines 46, 109
            # Price Data
            "price_local_currency": float(company.price_local_currency or 0),
            "previous_close": float(company.previous_close or 0),
            "currency": company.currency,
            "price_date": str(company.last_trade_date) if company.last_trade_date else "",  # Line 87
            "price_52w_low": float(company.price_52w_low or 0),  # Line 89
            "price_52w_high": float(company.price_52w_high or 0),  # Line 89
            # Market Cap
            "market_cap_local": float(company.market_cap_local or 0),
            "market_cap_usd": float(company.market_cap_usd or 0),
            # Valuation Ratios
            "pe_ratio_trailing": float(company.pe_ratio_trailing or 0),
            "pe_ratio_consensus": float(company.pe_ratio_consensus or 0),
            "pe_ratio_forward": None,  # Not in DB - template will show N/A (line 127)
            "pb_ratio": None,  # Not in DB - template will show N/A (line 128)
            "ps_ratio": None,  # Not in DB - template will show N/A (line 129)
            "ev_ebitda": None,  # Not in DB - template will show N/A (line 130)
            # Earnings
            "eps_trailing": float(company.eps_trailing or 0),
            "eps_growth_percent": float(company.eps_growth_percent or 0),  # Line 257
            "revenue_growth_percent": None,  # Not in DB - requires calculation
            # Profitability
            "roe_trailing": float(company.roe_trailing or 0),
            "roa_trailing": float(company.roa_trailing or 0),
            "gross_margin": None,  # Not in DB - template will show N/A (line 145)
            "operating_margin": float(company.operating_margin_trailing or 0),  # Line 146
            "net_margin": None,  # Not in DB - template will show N/A (line 147)
            # Dividend
            "dividend_yield_fy0": float(company.dividend_yield_fy0 or 0),
            # Liquidity & Solvency
            "debt_to_equity": float(company.debt_to_equity or 0),
            "current_ratio": float(company.current_ratio or 0),
            "quick_ratio": float(company.quick_ratio or 0),
            "interest_coverage": float(company.interest_coverage_ratio or 0),  # Line 169
            # Target Prices (Growth Outlook section)
            "target_price_mean": None,  # Not in DB currently
            "target_price_high": None,  # Not in DB currently
            "target_price_low": None,  # Not in DB currently
        }

    def _get_exchange_code(self, company: CSI300Company) -> str:
        """Derive exchange code from ticker or region."""
        ticker = company.ticker or ""
        region = company.region or ""

        if ".SS" in ticker or ".SH" in ticker:
            return "SSE"  # Shanghai Stock Exchange
        if ".SZ" in ticker:
            return "SZSE"  # Shenzhen Stock Exchange
        if ".HK" in ticker or "Hong Kong" in region:
            return "HKEX"  # Hong Kong Exchange
        if "Mainland China" in region:
            return "A-Share"

        return "N/A"

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="task_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="Task UUID",
            ),
        ],
        responses={
            200: PDFTaskSerializer,
            404: dict,
        },
        description="Get current status and progress of a PDF generation task",
    )
    @action(detail=False, methods=["get"], url_path="status/(?P<task_id>[^/.]+)")
    def task_status(self, request: Request, task_id: str) -> Response:
        """Get status of a PDF generation task."""
        try:
            task = PDFTask.objects.select_related("company", "template").get(task_id=task_id)
        except PDFTask.DoesNotExist:
            return Response(
                {"success": False, "error": f"Task {task_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PDFTaskSerializer(task)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="task_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="Task UUID",
            ),
        ],
        responses={
            200: PDFDownloadResponseSerializer,
            400: dict,
            404: dict,
        },
        description="Get pre-signed download URL for a completed PDF",
    )
    @action(detail=False, methods=["get"], url_path="download/(?P<task_id>[^/.]+)")
    def download_url(self, request: Request, task_id: str) -> Response:
        """Get download URL for a completed PDF."""
        try:
            task = PDFTask.objects.select_related("company").get(task_id=task_id)
        except PDFTask.DoesNotExist:
            return Response(
                {"success": False, "error": f"Task {task_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if task.status != PDFTask.Status.COMPLETED:
            return Response(
                {
                    "success": False,
                    "error": f"PDF not ready. Current status: {task.get_status_display()}",
                    "status": task.status,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not task.s3_key:
            return Response(
                {"success": False, "error": "PDF file not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate fresh presigned URL
        url, expires_at = generate_presigned_download_url(task.s3_key)

        # Update task with new URL
        task.download_url = url
        task.download_url_expires_at = expires_at
        task.save(update_fields=["download_url", "download_url_expires_at"])

        # Generate filename
        ticker = task.company.ticker or "report"
        filename = f"{ticker}_investment_summary.pdf"

        return Response(
            {
                "task_id": str(task.task_id),
                "download_url": url,
                "expires_at": expires_at.isoformat(),
                "filename": filename,
            }
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="company_id",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Optional company ID filter",
                required=False,
            ),
        ],
        responses={200: PDFTaskSerializer(many=True)},
        description="List recent PDF generation tasks",
    )
    @action(detail=False, methods=["get"], url_path="history")
    def task_history(self, request: Request) -> Response:
        """List recent PDF generation tasks."""
        # Build query with optional company filter BEFORE slicing
        company_id = request.query_params.get("company_id")

        queryset: QuerySet[PDFTask] = PDFTask.objects.select_related(
            "company", "template"
        ).order_by("-created_at")

        if company_id:
            with contextlib.suppress(ValueError, TypeError):
                queryset = queryset.filter(company_id=int(company_id))

        # Apply limit AFTER filtering
        tasks = queryset[:50]

        serializer = PDFTaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def _get_requester_id(self, request: Request) -> str:
        """Extract requester identifier from request."""
        # Try authenticated user first
        if request.user and request.user.is_authenticated:
            return str(request.user.id)
        # Fall back to IP address
        return self._get_client_ip(request)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")


class PDFStatusCallbackViewSet(viewsets.ViewSet):
    """
    ViewSet for receiving status callbacks from the LaTeX worker service.

    This is an internal API called by the LaTeX microservice to update
    task status in the Django database.

    Security: In production, this endpoint should be protected by:
    - API key validation (X-Internal-API-Key header)
    - VPC/security group restrictions (only allow from ECS worker)
    """

    @extend_schema(
        request=dict,
        responses={200: dict},
        description="Internal callback for LaTeX worker status updates",
    )
    @action(detail=False, methods=["post"], url_path="callback")
    def status_callback(self, request: Request) -> Response:
        """
        Receive status update from LaTeX worker.

        Expected payload:
        {
            "task_id": "uuid-string",
            "status": "processing|generating_charts|compiling|uploading|completed|failed",
            "progress": 0-100,
            "error_message": "optional error",
            "s3_key": "optional s3 key on completion"
        }
        """
        # Validate internal API key in production
        internal_api_key = os.getenv("PDF_INTERNAL_API_KEY", "")
        if internal_api_key:
            provided_key = request.headers.get("X-Internal-API-Key", "")
            if provided_key != internal_api_key:
                logger.warning(
                    "Invalid internal API key for PDF callback",
                    extra={"ip": self._get_client_ip(request)},
                )
                return Response(
                    {"success": False, "error": "Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        task_id = request.data.get("task_id")
        if not task_id:
            return Response(
                {"success": False, "error": "task_id required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate UUID format
        try:
            uuid_module.UUID(str(task_id))
        except ValueError:
            return Response(
                {"success": False, "error": "Invalid task_id format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_status = request.data.get("status", "processing")
        progress = request.data.get("progress", 0)
        error_message = request.data.get("error_message", "")
        s3_key = request.data.get("s3_key", "")

        success = update_task_status_from_worker(
            task_id=task_id,
            status=new_status,
            progress=progress,
            error_message=error_message,
            s3_key=s3_key,
        )

        if not success:
            return Response(
                {"success": False, "error": "Task not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Send WebSocket notification for real-time updates
        self._send_websocket_update(task_id, new_status, progress, error_message, s3_key)

        return Response({"success": True})

    def _send_websocket_update(
        self,
        task_id: str,
        task_status: str,
        progress: int,
        error_message: str,
        s3_key: str,
    ) -> None:
        """Send status update via WebSocket to connected clients."""
        # Get status display name
        status_display = dict(PDFTask.Status.choices).get(task_status, task_status)

        # Generate download URL if completed
        download_url = ""
        if task_status == PDFTask.Status.COMPLETED and s3_key:
            try:
                url, _ = generate_presigned_download_url(s3_key)
                download_url = url
            except Exception as e:
                logger.warning(f"Failed to generate download URL: {e}")

        # Run async function from sync context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(
                send_task_status_update(
                    task_id=task_id,
                    status=task_status,
                    status_display=status_display,
                    progress=progress,
                    error_message=error_message,
                    download_url=download_url,
                )
            )
        except Exception as e:
            # Log but don't fail the callback if WebSocket fails
            logger.warning(
                "Failed to send WebSocket update",
                extra={"task_id": task_id, "error": str(e)},
            )

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")
