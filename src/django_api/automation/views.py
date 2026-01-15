from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from observability import get_logger

from .models import AutomationTask
from .serializers import (
    AutomationTaskSerializer,
    DailyBriefingTriggerSerializer,
    ErrorResponseSerializer,
    ForensicAccountingTriggerSerializer,
)
from .tasks import (
    run_daily_briefing_full,
    run_daily_briefing_generator,
    run_daily_briefing_scraper,
    run_forensic_accounting,
)

logger = get_logger(__name__)


class AutomationTaskViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """
    ViewSet for managing automation tasks.

    Provides endpoints for triggering automation workflows and querying task status.
    """

    queryset = AutomationTask.objects.all()
    serializer_class = AutomationTaskSerializer

    @extend_schema(
        request=DailyBriefingTriggerSerializer,
        responses={
            202: OpenApiResponse(
                response=AutomationTaskSerializer,
                description="Task successfully created and queued",
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer, description="Invalid request parameters"
            ),
        },
        description="Trigger full Daily Briefing workflow (Stage 1: Scraping + Stage 2: AI Generation)",
        tags=["automation"],
    )
    @action(detail=False, methods=["post"], url_path="daily-briefing/trigger")
    def trigger_daily_briefing(self, request):
        """Trigger full Daily Briefing workflow (Stage 1 + 2)"""
        serializer = DailyBriefingTriggerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = AutomationTask.objects.create(
            task_type="daily_briefing",
            status="pending",
            created_by=request.user.username if request.user.is_authenticated else "api",
        )

        logger.info(
            "Daily Briefing task created",
            extra={"task_id": str(task.id), "task_type": "daily_briefing"},
        )

        # Trigger Celery task
        celery_task = run_daily_briefing_full.delay(str(task.id))

        task.celery_task_id = celery_task.id
        task.save()

        return Response(AutomationTaskSerializer(task).data, status=status.HTTP_202_ACCEPTED)

    @extend_schema(
        request=DailyBriefingTriggerSerializer,
        responses={
            202: OpenApiResponse(
                response=AutomationTaskSerializer,
                description="Scraping task successfully created and queued",
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer, description="Invalid request parameters"
            ),
        },
        description="Trigger only Stage 1 (Scraping from Briefing.com to Google Sheets)",
        tags=["automation"],
    )
    @action(detail=False, methods=["post"], url_path="daily-briefing/scrape")
    def trigger_daily_briefing_scrape(self, request):
        """Trigger only Stage 1 (Scraping)"""
        serializer = DailyBriefingTriggerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = AutomationTask.objects.create(
            task_type="daily_briefing",
            status="pending",
            created_by=request.user.username if request.user.is_authenticated else "api",
        )

        logger.info(
            "Daily Briefing scrape-only task created",
            extra={"task_id": str(task.id), "task_type": "daily_briefing_scrape"},
        )

        # Trigger Celery task
        celery_task = run_daily_briefing_scraper.delay(str(task.id))

        task.celery_task_id = celery_task.id
        task.save()

        return Response(AutomationTaskSerializer(task).data, status=status.HTTP_202_ACCEPTED)

    @extend_schema(
        request=DailyBriefingTriggerSerializer,
        responses={
            202: OpenApiResponse(
                response=AutomationTaskSerializer,
                description="Generation task successfully created and queued",
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer, description="Invalid request parameters"
            ),
        },
        description="Trigger only Stage 2 (AI Report Generation, skipping scraping delay)",
        tags=["automation"],
    )
    @action(detail=False, methods=["post"], url_path="daily-briefing/generate")
    def trigger_daily_briefing_generate(self, request):
        """Trigger only Stage 2 (Generation)"""
        serializer = DailyBriefingTriggerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = AutomationTask.objects.create(
            task_type="daily_briefing",
            status="pending",
            created_by=request.user.username if request.user.is_authenticated else "api",
        )

        logger.info(
            "Daily Briefing generate-only task created",
            extra={"task_id": str(task.id), "task_type": "daily_briefing_generate"},
        )

        # Trigger Celery task
        celery_task = run_daily_briefing_generator.delay(str(task.id))

        task.celery_task_id = celery_task.id
        task.save()

        return Response(AutomationTaskSerializer(task).data, status=status.HTTP_202_ACCEPTED)

    @extend_schema(
        request=ForensicAccountingTriggerSerializer,
        responses={
            202: OpenApiResponse(
                response=AutomationTaskSerializer,
                description="Forensic Accounting task successfully created and queued",
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Invalid request parameters or no companies provided",
            ),
        },
        description="Trigger Forensic Accounting analysis for a list of companies",
        tags=["automation"],
    )
    @action(detail=False, methods=["post"], url_path="forensic-accounting/trigger")
    def trigger_forensic_accounting(self, request):
        """Trigger Forensic Accounting"""
        serializer = ForensicAccountingTriggerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        companies = serializer.validated_data.get("companies", [])

        if not companies:
            logger.warning(
                "Forensic Accounting trigger rejected: no companies provided",
                extra={"request_data": request.data},
            )
            return Response({"error": "No companies provided"}, status=status.HTTP_400_BAD_REQUEST)

        task = AutomationTask.objects.create(
            task_type="forensic_accounting",
            status="pending",
            created_by=request.user.username if request.user.is_authenticated else "api",
        )

        logger.info(
            "Forensic Accounting task created",
            extra={
                "task_id": str(task.id),
                "task_type": "forensic_accounting",
                "company_count": len(companies),
            },
        )

        # Trigger Celery task
        celery_task = run_forensic_accounting.delay(str(task.id), companies)

        task.celery_task_id = celery_task.id
        task.save()

        return Response(AutomationTaskSerializer(task).data, status=status.HTTP_202_ACCEPTED)
