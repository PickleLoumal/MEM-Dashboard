"""
PDF Service Admin Configuration

Provides Django Admin interface for managing PDF templates and viewing tasks.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import PDFTask, PDFTemplate


@admin.register(PDFTemplate)
class PDFTemplateAdmin(admin.ModelAdmin):
    """Admin interface for PDF templates."""

    list_display = [
        "display_name",
        "name",
        "version",
        "is_active_badge",
        "is_default_badge",
        "updated_at",
    ]
    list_filter = ["is_active", "is_default", "page_size"]
    search_fields = ["name", "display_name", "description"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-is_default", "-is_active", "name"]

    fieldsets = (
        (
            "Template Identification",
            {
                "fields": ("name", "display_name", "description", "version"),
            },
        ),
        (
            "LaTeX Content",
            {
                "fields": ("preamble", "latex_content"),
                "classes": ("wide",),
            },
        ),
        (
            "Page Settings",
            {
                "fields": ("page_size", "margins"),
            },
        ),
        (
            "Header & Footer",
            {
                "fields": ("header_left", "header_right", "footer_center"),
            },
        ),
        (
            "Charts Configuration",
            {
                "fields": ("charts_config",),
                "classes": ("collapse",),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_active", "is_default"),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="Active", boolean=True)
    def is_active_badge(self, obj: PDFTemplate) -> bool:
        return obj.is_active

    @admin.display(description="Default", boolean=True)
    def is_default_badge(self, obj: PDFTemplate) -> bool:
        return obj.is_default


@admin.register(PDFTask)
class PDFTaskAdmin(admin.ModelAdmin):
    """Admin interface for viewing PDF generation tasks."""

    list_display = [
        "task_id_short",
        "company_ticker",
        "template_name",
        "status_badge",
        "progress_bar",
        "created_at",
        "processing_time_display",
    ]
    list_filter = ["status", "template", "created_at"]
    search_fields = ["task_id", "company__ticker", "company__name", "requested_by"]
    readonly_fields = [
        "task_id",
        "company",
        "template",
        "status",
        "progress",
        "error_message",
        "s3_key",
        "download_url",
        "download_url_expires_at",
        "requested_by",
        "request_metadata",
        "created_at",
        "updated_at",
        "completed_at",
        "processing_time_ms",
    ]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Task Information",
            {
                "fields": ("task_id", "company", "template"),
            },
        ),
        (
            "Status",
            {
                "fields": ("status", "progress", "error_message"),
            },
        ),
        (
            "Result",
            {
                "fields": ("s3_key", "download_url", "download_url_expires_at"),
            },
        ),
        (
            "Request Metadata",
            {
                "fields": ("requested_by", "request_metadata"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "completed_at",
                    "processing_time_ms",
                ),
            },
        ),
    )

    def has_add_permission(self, request) -> bool:
        """Disable manual task creation - tasks are created via API."""
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """Disable editing - tasks are managed by the system."""
        return False

    @admin.display(description="Task ID")
    def task_id_short(self, obj: PDFTask) -> str:
        return str(obj.task_id)[:8]

    @admin.display(description="Company")
    def company_ticker(self, obj: PDFTask) -> str:
        return obj.company.ticker or obj.company.name[:20]

    @admin.display(description="Template")
    def template_name(self, obj: PDFTask) -> str:
        return obj.template.display_name

    @admin.display(description="Status")
    def status_badge(self, obj: PDFTask) -> str:
        colors = {
            PDFTask.Status.PENDING: "#6c757d",  # Gray
            PDFTask.Status.PROCESSING: "#007bff",  # Blue
            PDFTask.Status.GENERATING_CHARTS: "#17a2b8",  # Cyan
            PDFTask.Status.COMPILING: "#ffc107",  # Yellow
            PDFTask.Status.UPLOADING: "#fd7e14",  # Orange
            PDFTask.Status.COMPLETED: "#28a745",  # Green
            PDFTask.Status.FAILED: "#dc3545",  # Red
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.display(description="Progress")
    def progress_bar(self, obj: PDFTask) -> str:
        if obj.status == PDFTask.Status.FAILED:
            return format_html(
                '<div style="width: 100px; background: #f8d7da; border-radius: 3px;">'
                '<div style="width: 100%; background: #dc3545; height: 10px; '
                'border-radius: 3px;"></div></div>'
            )
        return format_html(
            '<div style="width: 100px; background: #e9ecef; border-radius: 3px;">'
            '<div style="width: {}%; background: #28a745; height: 10px; '
            'border-radius: 3px;"></div></div> {}%',
            obj.progress,
            obj.progress,
        )

    @admin.display(description="Time (ms)")
    def processing_time_display(self, obj: PDFTask) -> str:
        if obj.processing_time_ms is None:
            return "-"
        if obj.processing_time_ms > 1000:
            return f"{obj.processing_time_ms / 1000:.1f}s"
        return f"{obj.processing_time_ms}ms"
