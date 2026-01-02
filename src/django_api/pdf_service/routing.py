"""
PDF Service WebSocket Routing

Defines WebSocket URL patterns for the PDF service.
"""

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/pdf/(?P<task_id>[0-9a-f-]+)/$",
        consumers.PDFTaskConsumer.as_asgi(),
    ),
]
