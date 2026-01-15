from django.contrib import admin
from .models import AutomationTask


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
