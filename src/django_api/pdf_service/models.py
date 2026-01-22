"""
PDF Service Models

Defines the database models for PDF template management and task tracking.
"""

from __future__ import annotations

import uuid
from typing import ClassVar

from django.db import models


class PDFTemplate(models.Model):
    """
    Database-stored LaTeX templates for Admin editing.

    Allows non-technical users to modify report templates through
    Django Admin without code deployments.
    """

    # Type hints for Django dynamic attributes
    objects: ClassVar[models.Manager]  # type: ignore[type-arg]
    DoesNotExist: ClassVar[type[Exception]]

    # Template identification
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Template identifier (e.g., 'investment_summary_v1')",
    )
    display_name = models.CharField(
        max_length=200,
        help_text="Human-readable template name (e.g., 'Investment Summary Report')",
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Template description and usage notes",
    )

    # LaTeX content (Jinja2 syntax)
    latex_content = models.TextField(
        help_text="Main LaTeX template content using Jinja2 syntax for variable substitution",
    )
    preamble = models.TextField(
        blank=True,
        default="",
        help_text="LaTeX preamble (package imports, custom commands)",
    )

    # Page settings
    page_size = models.CharField(
        max_length=20,
        default="a4paper",
        help_text="LaTeX page size (a4paper, letterpaper, etc.)",
    )
    margins = models.JSONField(
        default=dict,
        blank=True,
        help_text='Page margins as JSON (e.g., {"top": "2cm", "bottom": "2cm", "left": "2.5cm", "right": "2.5cm"})',
    )

    # Header/Footer configuration
    header_left = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Left header content",
    )
    header_right = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Right header content",
    )
    footer_center = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Center footer content (e.g., page numbers)",
    )

    # Charts configuration
    charts_config = models.JSONField(
        default=list,
        blank=True,
        help_text="Chart definitions as JSON array",
    )

    # Versioning and status
    version = models.CharField(
        max_length=20,
        default="1.0",
        help_text="Template version",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is available for use",
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is the default template for new reports",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pdf_template"
        verbose_name = "PDF Template"
        verbose_name_plural = "PDF Templates"
        ordering = ["-is_default", "-is_active", "name"]

    def __str__(self) -> str:
        status = "✓" if self.is_active else "✗"
        default = " (default)" if self.is_default else ""
        return f"{status} {self.display_name} v{self.version}{default}"

    def save(self, *args, **kwargs) -> None:
        """
        Override save to ensure only one default template exists.
        """
        if self.is_default:
            # Set all other templates to non-default
            PDFTemplate.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class PDFTask(models.Model):
    """
    Track PDF generation tasks.

    Records the status, progress, and results of async PDF generation jobs.
    Supports real-time status updates via WebSocket.
    """

    # Type hints for Django dynamic attributes
    objects: ClassVar[models.Manager]  # type: ignore[type-arg]
    DoesNotExist: ClassVar[type[Exception]]

    class Status(models.TextChoices):
        """Task status enumeration."""

        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        GENERATING_CHARTS = "generating_charts", "Generating Charts"
        COMPILING = "compiling", "Compiling LaTeX"
        UPLOADING = "uploading", "Uploading to S3"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    # Task identification (UUID primary key)
    task_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique task identifier",
    )

    # Related entities
    company = models.ForeignKey(
        "csi300.Company",
        on_delete=models.CASCADE,
        related_name="pdf_tasks",
        help_text="Company for which PDF is being generated",
    )
    template = models.ForeignKey(
        PDFTemplate,
        on_delete=models.PROTECT,
        related_name="tasks",
        help_text="Template used for this PDF generation",
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text="Current task status",
    )
    progress = models.IntegerField(
        default=0,
        help_text="Progress percentage (0-100)",
    )
    error_message = models.TextField(
        blank=True,
        default="",
        help_text="Error message if task failed",
    )

    # Result storage
    s3_key = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="S3 object key for the generated PDF",
    )
    download_url = models.URLField(
        max_length=2000,
        blank=True,
        default="",
        help_text="Pre-signed S3 download URL",
    )
    download_url_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Expiration time for the download URL",
    )

    # Request metadata
    requested_by = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="User ID or IP address of requester",
    )
    request_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional request metadata (user agent, etc.)",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When task completed (success or failure)",
    )
    processing_time_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="Total processing time in milliseconds",
    )

    class Meta:
        db_table = "pdf_task"
        verbose_name = "PDF Task"
        verbose_name_plural = "PDF Tasks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["company", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"PDF Task {str(self.task_id)[:8]} - {self.company.ticker} ({self.status})"

    @property
    def is_terminal(self) -> bool:
        """Check if task is in a terminal state (completed or failed)."""
        return self.status in (self.Status.COMPLETED, self.Status.FAILED)

    @property
    def is_in_progress(self) -> bool:
        """Check if task is currently being processed."""
        return self.status in (
            self.Status.PROCESSING,
            self.Status.GENERATING_CHARTS,
            self.Status.COMPILING,
            self.Status.UPLOADING,
        )
