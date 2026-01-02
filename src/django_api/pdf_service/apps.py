"""PDF Service app configuration."""

from django.apps import AppConfig


class PdfServiceConfig(AppConfig):
    """Configuration for the PDF Service application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "pdf_service"
    verbose_name = "PDF Report Generation Service"

    def ready(self):
        """
        Initialize app when Django starts.

        Import signals here if needed in the future.
        """
