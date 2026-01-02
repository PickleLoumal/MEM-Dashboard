"""
PDF Service URL Configuration

Defines the URL routes for the PDF generation API.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PDFStatusCallbackViewSet, PDFTaskViewSet, PDFTemplateViewSet

app_name = "pdf_service"

router = DefaultRouter()
router.register(r"templates", PDFTemplateViewSet, basename="pdf-templates")
router.register(r"tasks", PDFTaskViewSet, basename="pdf-tasks")
router.register(r"internal", PDFStatusCallbackViewSet, basename="pdf-internal")

urlpatterns = [
    path("", include(router.urls)),
]
