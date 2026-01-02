"""
PDF Service Django App

Provides PDF report generation capabilities for investment summaries.
Uses LaTeX compilation via a separate microservice for high-quality output.

Components:
- PDFTemplate: Database-stored LaTeX templates for Admin editing
- PDFTask: Task tracking for async PDF generation
- API endpoints for requesting and monitoring PDF generation
- WebSocket support for real-time progress updates
- SQS integration for decoupled LaTeX compilation
"""

default_app_config = "pdf_service.apps.PdfServiceConfig"
