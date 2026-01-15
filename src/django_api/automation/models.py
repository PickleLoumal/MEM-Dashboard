from django.db import models
from django.utils import timezone


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
