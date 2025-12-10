# Django Content Models for Modal Content Management


from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models


class ContentCategory(models.Model):
    """Content Category Model"""

    name = models.CharField(max_length=100, unique=True, verbose_name="Category Name")
    description = models.TextField(blank=True, verbose_name="Description")
    slug = models.SlugField(unique=True, verbose_name="URL Slug")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = "content_contentcategory"
        verbose_name = "Content Category"
        verbose_name_plural = "Content Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ModalContent(models.Model):
    """Modal Content Model"""

    CONTENT_TYPES = [
        ("consumer-spending", "Consumer Spending"),
        ("motor-vehicles", "Motor Vehicles"),
        ("services-exports", "Services Exports"),
        ("goods-exports", "Goods Exports"),
        ("economic-indicators", "Economic Indicators"),
        ("investment-components", "Investment Components"),
        ("market-analysis", "Market Analysis"),
    ]

    # Basic identifiers
    modal_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Modal ID",
        help_text="Modal ID used by frontend, e.g.: motor-vehicles",
    )
    title = models.CharField(
        max_length=200, verbose_name="Title", help_text="Title displayed in the modal"
    )
    category = models.ForeignKey(
        ContentCategory,
        on_delete=models.CASCADE,
        verbose_name="Category",
        help_text="Category this content belongs to",
        null=True,
        blank=True,
    )
    content_type = models.CharField(
        max_length=50,
        choices=CONTENT_TYPES,
        verbose_name="Content Type",
        help_text="Specific type of content",
    )

    # Core content fields
    description = models.TextField(
        verbose_name="Description", help_text="Detailed description displayed in the modal"
    )
    importance = models.TextField(
        verbose_name="Importance",
        help_text="Explanation of why this indicator/content is important",
    )
    source = models.CharField(
        max_length=500, verbose_name="Data Source", help_text="Source of the data"
    )

    # Structured data fields
    breakdown_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Breakdown Data",
        help_text="Structured breakdown data in JSON format",
    )
    additional_info = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Additional Information",
        help_text="Additional information in JSON format",
    )

    # Status and metadata
    is_active = models.BooleanField(
        default=True, verbose_name="Is Active", help_text="Whether to display in frontend"
    )
    priority = models.IntegerField(
        default=100, verbose_name="Priority", help_text="Lower number = higher priority"
    )

    # Audit fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_contents",
        verbose_name="Created By",
        blank=True,
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="updated_contents",
        verbose_name="Updated By",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = "content_modalcontent"
        verbose_name = "Modal Content"
        verbose_name_plural = "Modal Contents"
        ordering = ["priority", "title"]
        indexes = [
            models.Index(fields=["modal_id"]),
            models.Index(fields=["content_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.modal_id})"

    def get_breakdown_items(self):
        """Get breakdown data items"""
        if self.breakdown_data and isinstance(self.breakdown_data, dict):
            return self.breakdown_data.get("items", [])
        return []

    def set_current_user(self, user):
        """Set current user (for audit fields)"""
        self._current_user = user

    def save(self, *args, **kwargs):
        # Get current user
        current_user = kwargs.pop("user", None)

        # If no user passed as parameter, try to get from instance attribute
        if not current_user and hasattr(self, "_current_user"):
            current_user = getattr(self, "_current_user", None)

        # Set audit fields
        if current_user:
            if not self.pk:  # New record
                self.created_by = current_user
            self.updated_by = current_user

        super().save(*args, **kwargs)

        # Clear related cache
        try:
            cache.delete(f"modal_content_{self.modal_id}")
            cache.delete("all_modal_content")
        except Exception:
            pass  # Ignore if cache is not available
