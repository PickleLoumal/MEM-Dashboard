from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone

if TYPE_CHECKING:
    from django.db.models import QuerySet


class AutomationTask(models.Model):
    """Base model for all automation tasks"""

    TASK_TYPES = [
        ("daily_briefing", "Daily Briefing"),
        ("forensic_accounting", "Forensic Accounting"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("scraping", "Scraping Data"),  # Stage 1 for Daily Briefing
        ("waiting_stage2", "Waiting for Stage 2"),  # 等待 10 分钟后执行 Stage 2
        ("generating", "Generating Report"),  # Stage 2: AI generation
        ("uploading", "Uploading"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    celery_task_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    started_at = models.DateTimeField(null=True, blank=True)
    stage1_completed_at = models.DateTimeField(null=True, blank=True)  # Stage 1 完成时间
    stage2_scheduled_at = models.DateTimeField(null=True, blank=True)  # Stage 2 预计开始时间
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    result_urls = models.JSONField(default=dict, blank=True)  # S3/Drive URLs
    created_by = models.CharField(max_length=100, default="system")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_task_type_display()} ({self.created_at.strftime('%Y-%m-%d %H:%M')}) - {self.status}"

    @property
    def stage2_countdown_remaining(self):
        """返回距离 Stage 2 开始的剩余秒数"""
        if self.stage2_scheduled_at and self.status == "waiting_stage2":
            remaining = (self.stage2_scheduled_at - timezone.now()).total_seconds()
            return max(0, int(remaining))
        return None


class DailyBriefingData(models.Model):
    """
    Stores scraped data from Briefing.com for Daily Briefing reports.

    Replaces Google Sheets storage (cells H2/I2/J2) with database persistence.
    Each record represents one source type's content for a specific date.
    """

    SOURCE_TYPES = [
        ("page_one", "Page One"),
        ("stock_market", "Stock Market Update"),
        ("bond_market", "Bond Market Update"),
    ]

    date = models.DateField(db_index=True, help_text="Date when the data was scraped")
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPES,
        help_text="Type of source: page_one, stock_market, or bond_market",
    )
    source_url = models.URLField(help_text="URL of the scraped page")
    content = models.TextField(help_text="Scraped content from Briefing.com")
    content_length = models.IntegerField(help_text="Character count of the content")
    scraped_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when the content was scraped"
    )

    class Meta:
        unique_together = ["date", "source_type"]
        ordering = ["-date", "source_type"]
        verbose_name = "Daily Briefing Data"
        verbose_name_plural = "Daily Briefing Data"

    def __str__(self) -> str:
        return f"{self.get_source_type_display()} ({self.date})"

    @classmethod
    def get_data_for_date(cls, target_date: date) -> QuerySet[DailyBriefingData]:
        """
        Retrieve all scraped data for a specific date.

        Args:
            target_date: The date to query for.

        Returns:
            QuerySet of DailyBriefingData records for the given date.
        """
        return cls.objects.filter(date=target_date)

    @classmethod
    def get_combined_content(cls, target_date: date) -> str:
        """
        Get combined content from all sources for a specific date.

        Args:
            target_date: The date to query for.

        Returns:
            Combined content string formatted with section headers.
        """
        data_records = cls.get_data_for_date(target_date)
        if not data_records.exists():
            return ""

        sections = []
        for record in data_records:
            sections.append(f"=== {record.get_source_type_display()} ===\n{record.content}")

        return "\n\n".join(sections)


class DailyBriefingReport(models.Model):
    """
    Stores generated Daily Briefing reports.

    Each report is generated from scraped data using Perplexity AI and
    uploaded to Google Drive. Both long and quick versions are stored.
    """

    REPORT_TYPES = [
        ("long_version", "Long Version"),
        ("quick_version", "Quick Version"),
    ]

    task = models.ForeignKey(
        AutomationTask,
        on_delete=models.CASCADE,
        related_name="briefing_reports",
        help_text="The automation task that generated this report",
    )
    date = models.DateField(db_index=True, help_text="Date of the report")
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPES,
        help_text="Type of report: long_version or quick_version",
    )
    content = models.TextField(help_text="Report content in Markdown format")
    drive_url = models.URLField(
        blank=True, default="", help_text="Google Drive URL for the uploaded document"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when the report was created"
    )

    class Meta:
        unique_together = ["date", "report_type"]
        ordering = ["-date", "report_type"]
        verbose_name = "Daily Briefing Report"
        verbose_name_plural = "Daily Briefing Reports"

    def __str__(self) -> str:
        return f"{self.get_report_type_display()} ({self.date})"

    @classmethod
    def get_reports_for_date(cls, target_date: date) -> QuerySet[DailyBriefingReport]:
        """
        Retrieve all reports for a specific date.

        Args:
            target_date: The date to query for.

        Returns:
            QuerySet of DailyBriefingReport records for the given date.
        """
        return cls.objects.filter(date=target_date)
