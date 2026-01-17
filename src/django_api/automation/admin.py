from django.contrib import admin

from .models import AutomationTask, DailyBriefingData, DailyBriefingReport


@admin.register(AutomationTask)
class AutomationTaskAdmin(admin.ModelAdmin):
    list_display = (
        "task_type",
        "status",
        "created_at",
        "started_at",
        "completed_at",
        "created_by",
    )
    list_filter = ("task_type", "status", "created_at")
    search_fields = ("celery_task_id", "error_message", "created_by")
    readonly_fields = (
        "created_at",
        "started_at",
        "completed_at",
        "stage1_completed_at",
        "stage2_scheduled_at",
        "result_urls",
    )


@admin.register(DailyBriefingData)
class DailyBriefingDataAdmin(admin.ModelAdmin):
    """Admin configuration for DailyBriefingData model"""

    list_display = (
        "date",
        "source_type",
        "content_length",
        "scraped_at",
    )
    list_filter = ("source_type", "date")
    search_fields = ("content", "source_url")
    readonly_fields = ("scraped_at", "content_length")
    date_hierarchy = "date"
    ordering = ("-date", "source_type")

    fieldsets = (
        (None, {"fields": ("date", "source_type", "source_url")}),
        ("Content", {"fields": ("content", "content_length")}),
        ("Metadata", {"fields": ("scraped_at",)}),
    )


@admin.register(DailyBriefingReport)
class DailyBriefingReportAdmin(admin.ModelAdmin):
    """Admin configuration for DailyBriefingReport model"""

    list_display = (
        "date",
        "report_type",
        "task",
        "drive_url_short",
        "created_at",
    )
    list_filter = ("report_type", "date")
    search_fields = ("content", "drive_url")
    readonly_fields = ("created_at",)
    date_hierarchy = "date"
    ordering = ("-date", "report_type")
    raw_id_fields = ("task",)

    fieldsets = (
        (None, {"fields": ("task", "date", "report_type")}),
        ("Content", {"fields": ("content",)}),
        ("Links", {"fields": ("drive_url",)}),
        ("Metadata", {"fields": ("created_at",)}),
    )

    @admin.display(description="Drive URL")
    def drive_url_short(self, obj: DailyBriefingReport) -> str:
        """Display shortened Drive URL in list view"""
        if obj.drive_url:
            return obj.drive_url[:50] + "..." if len(obj.drive_url) > 50 else obj.drive_url
        return "-"
