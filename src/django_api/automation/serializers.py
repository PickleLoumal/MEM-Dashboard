from rest_framework import serializers

from .models import AutomationTask, DailyBriefingData, DailyBriefingReport


class AutomationTaskSerializer(serializers.ModelSerializer):
    """
    Serializer for AutomationTask model.
    Used for task status responses in all automation endpoints.
    """

    stage2_countdown_remaining = serializers.IntegerField(
        read_only=True,
        help_text="Seconds remaining until Stage 2 starts (only present when status is waiting_stage2)",
    )

    task_type = serializers.ChoiceField(
        choices=AutomationTask.TASK_TYPES,
        help_text="Type of automation task: daily_briefing or forensic_accounting",
    )

    status = serializers.ChoiceField(
        choices=AutomationTask.STATUS_CHOICES,
        read_only=True,
        help_text="Current task status: pending, scraping, waiting_stage2, generating, uploading, completed, or failed",
    )

    class Meta:
        model = AutomationTask
        fields = [
            "id",
            "task_type",
            "celery_task_id",
            "status",
            "started_at",
            "stage1_completed_at",
            "stage2_scheduled_at",
            "stage2_countdown_remaining",
            "completed_at",
            "error_message",
            "result_urls",
            "created_by",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "celery_task_id",
            "status",
            "started_at",
            "stage1_completed_at",
            "stage2_scheduled_at",
            "completed_at",
            "error_message",
            "result_urls",
            "created_by",
            "created_at",
        ]


class DailyBriefingTriggerSerializer(serializers.Serializer):
    """Request serializer for triggering Daily Briefing workflow"""

    scrape_only = serializers.BooleanField(
        required=False,
        default=False,
        help_text="If true, only run Stage 1 (scraping) without triggering Stage 2 (AI generation)",
    )


class CompanyInfoSerializer(serializers.Serializer):
    """Serializer for company information in Forensic Accounting requests"""

    name = serializers.CharField(help_text="Company name (e.g., 'Apple Inc.')")
    ticker = serializers.CharField(help_text="Stock ticker symbol (e.g., 'AAPL')")


class ForensicAccountingTriggerSerializer(serializers.Serializer):
    """Request serializer for triggering Forensic Accounting analysis"""

    companies = serializers.ListField(
        child=CompanyInfoSerializer(),
        required=False,
        help_text="List of companies to analyze, each with 'name' and 'ticker' fields",
    )
    # Note: excel_file upload would require multipart/form-data handling
    # For now, we only support JSON list input


class ErrorResponseSerializer(serializers.Serializer):
    """Standard error response serializer for OpenAPI documentation"""

    error = serializers.CharField(help_text="Error message describing what went wrong")
    detail = serializers.CharField(required=False, help_text="Additional error details")


class DailyBriefingDataSerializer(serializers.ModelSerializer):
    """
    Serializer for DailyBriefingData model.

    Used for API responses when querying scraped briefing data.
    """

    source_type = serializers.ChoiceField(
        choices=DailyBriefingData.SOURCE_TYPES,
        help_text="Type of source: page_one, stock_market, or bond_market",
    )
    source_type_display = serializers.CharField(
        source="get_source_type_display",
        read_only=True,
        help_text="Human-readable source type name",
    )

    class Meta:
        model = DailyBriefingData
        fields = [
            "id",
            "date",
            "source_type",
            "source_type_display",
            "source_url",
            "content",
            "content_length",
            "scraped_at",
        ]
        read_only_fields = [
            "id",
            "date",
            "source_type",
            "source_url",
            "content",
            "content_length",
            "scraped_at",
        ]


class DailyBriefingReportSerializer(serializers.ModelSerializer):
    """
    Serializer for DailyBriefingReport model.

    Used for API responses when querying generated briefing reports.
    """

    report_type = serializers.ChoiceField(
        choices=DailyBriefingReport.REPORT_TYPES,
        help_text="Type of report: long_version or quick_version",
    )
    report_type_display = serializers.CharField(
        source="get_report_type_display",
        read_only=True,
        help_text="Human-readable report type name",
    )
    task_id = serializers.IntegerField(
        source="task.id",
        read_only=True,
        help_text="ID of the automation task that generated this report",
    )

    class Meta:
        model = DailyBriefingReport
        fields = [
            "id",
            "task_id",
            "date",
            "report_type",
            "report_type_display",
            "content",
            "drive_url",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "task_id",
            "date",
            "report_type",
            "content",
            "drive_url",
            "created_at",
        ]
