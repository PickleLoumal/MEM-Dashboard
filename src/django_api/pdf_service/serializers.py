"""
PDF Service Serializers

Defines serializers for API request/response handling.
"""

from __future__ import annotations

from rest_framework import serializers

from .models import PDFTask, PDFTemplate


class PDFTemplateSerializer(serializers.ModelSerializer):
    """Serializer for PDF templates (read-only, for listing available templates)."""

    class Meta:
        model = PDFTemplate
        fields = [
            "id",
            "name",
            "display_name",
            "description",
            "version",
            "is_default",
            "page_size",
        ]
        read_only_fields = fields


class PDFTemplateDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for PDF templates (includes content for preview)."""

    class Meta:
        model = PDFTemplate
        fields = [
            "id",
            "name",
            "display_name",
            "description",
            "version",
            "is_default",
            "page_size",
            "margins",
            "header_left",
            "header_right",
            "footer_center",
            "charts_config",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class PDFRequestSerializer(serializers.Serializer):
    """
    Serializer for PDF generation request.

    Note: Validation only checks existence, actual objects are fetched in the view
    to avoid duplicate queries. View handles race conditions with try-except.
    """

    company_id = serializers.IntegerField(
        min_value=1,
        help_text="ID of the company for which to generate PDF",
    )
    template_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        help_text="Optional template ID (uses default template if not specified)",
    )

    def validate_company_id(self, value: int) -> int:
        """
        Validate that company exists.

        Uses exists() for efficiency - actual object fetch happens in view.
        """
        from csi300.models import CSI300Company  # noqa: PLC0415

        if not CSI300Company.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f"Company with ID {value} not found")
        return value

    def validate_template_id(self, value: int | None) -> int | None:
        """
        Validate that template exists and is active.

        Uses exists() for efficiency - actual object fetch happens in view.
        """
        if value is None:
            return value

        if not PDFTemplate.objects.filter(pk=value, is_active=True).exists():
            raise serializers.ValidationError(f"Template with ID {value} not found or inactive")
        return value


class PDFTaskSerializer(serializers.ModelSerializer):
    """Serializer for PDF task status responses."""

    company_ticker = serializers.CharField(
        source="company.ticker",
        read_only=True,
        help_text="Company ticker symbol",
    )
    company_name = serializers.CharField(
        source="company.name",
        read_only=True,
        help_text="Company name",
    )
    template_name = serializers.CharField(
        source="template.display_name",
        read_only=True,
        help_text="Template display name",
    )
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
        help_text="Human-readable status",
    )

    class Meta:
        model = PDFTask
        fields = [
            "task_id",
            "company_ticker",
            "company_name",
            "template_name",
            "status",
            "status_display",
            "progress",
            "error_message",
            "download_url",
            "download_url_expires_at",
            "created_at",
            "completed_at",
            "processing_time_ms",
        ]
        read_only_fields = fields


class PDFTaskCreateResponseSerializer(serializers.Serializer):
    """Response serializer for task creation endpoint."""

    task_id = serializers.UUIDField(
        help_text="Unique task identifier for tracking",
    )
    status = serializers.CharField(
        help_text="Initial task status (pending)",
    )
    message = serializers.CharField(
        help_text="Confirmation message",
    )
    websocket_url = serializers.CharField(
        help_text="WebSocket URL for real-time status updates",
    )


class PDFDownloadResponseSerializer(serializers.Serializer):
    """Response serializer for download URL endpoint."""

    task_id = serializers.UUIDField(
        help_text="Task identifier",
    )
    download_url = serializers.URLField(
        help_text="Pre-signed S3 URL for downloading the PDF",
    )
    expires_at = serializers.DateTimeField(
        help_text="Expiration time for the download URL",
    )
    filename = serializers.CharField(
        help_text="Suggested filename for the download",
    )


class WebSocketStatusUpdateSerializer(serializers.Serializer):
    """Serializer for WebSocket status update messages."""

    task_id = serializers.UUIDField(
        help_text="Task identifier",
    )
    status = serializers.CharField(
        help_text="Current task status code",
    )
    status_display = serializers.CharField(
        help_text="Human-readable status",
    )
    progress = serializers.IntegerField(
        help_text="Progress percentage (0-100)",
    )
    error_message = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Error message (only present on failure)",
    )
    download_url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="Download URL (only present on completion)",
    )
