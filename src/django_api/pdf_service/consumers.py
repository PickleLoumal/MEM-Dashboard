"""
PDF Service WebSocket Consumers

Provides real-time status updates for PDF generation tasks via WebSocket.
"""

from __future__ import annotations

import json
import logging
import uuid as uuid_module
from typing import Any

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class PDFTaskConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for PDF task status updates.

    Clients connect to /ws/pdf/{task_id}/ to receive real-time updates
    about a specific PDF generation task.
    """

    task_id: str
    room_group_name: str

    async def connect(self):
        """Handle WebSocket connection."""
        raw_task_id = self.scope["url_route"]["kwargs"]["task_id"]

        # Validate UUID format to prevent injection
        try:
            uuid_module.UUID(raw_task_id)
            self.task_id = raw_task_id
        except (ValueError, AttributeError):
            logger.warning(
                "Invalid task_id format in WebSocket connection",
                extra={"raw_task_id": raw_task_id[:50] if raw_task_id else "None"},
            )
            await self.close(code=4000)  # Custom close code for invalid input
            return

        self.room_group_name = f"pdf_task_{self.task_id}"

        # Join task-specific group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        logger.info(
            "WebSocket connected for PDF task",
            extra={"task_id": self.task_id},
        )

        # Send initial status
        await self.send_initial_status()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave task group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        logger.info(
            "WebSocket disconnected for PDF task",
            extra={"task_id": self.task_id, "close_code": close_code},
        )

    async def receive(self, text_data: str):
        """
        Handle incoming messages from client.

        Currently supports:
        - {"type": "ping"} - Keep-alive ping
        - {"type": "get_status"} - Request current status
        """
        try:
            data = json.loads(text_data)
            message_type = data.get("type", "")

            if message_type == "ping":
                await self.send(text_data=json.dumps({"type": "pong"}))
            elif message_type == "get_status":
                await self.send_initial_status()

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"type": "error", "message": "Invalid JSON"}))

    async def task_update(self, event: dict[str, Any]):
        """
        Handle task update events from channel layer.

        Called when the task status is updated by the worker callback.
        """
        await self.send(
            text_data=json.dumps(
                {
                    "type": "status_update",
                    "task_id": event.get("task_id", self.task_id),
                    "status": event["status"],
                    "status_display": event.get("status_display", event["status"]),
                    "progress": event.get("progress", 0),
                    "error_message": event.get("error_message", ""),
                    "download_url": event.get("download_url", ""),
                }
            )
        )

    async def send_initial_status(self):
        """Fetch and send current task status."""
        from asgiref.sync import sync_to_async  # noqa: PLC0415

        from .models import PDFTask  # noqa: PLC0415

        try:
            task = await sync_to_async(
                lambda: PDFTask.objects.select_related("company", "template").get(
                    task_id=self.task_id
                )
            )()

            await self.send(
                text_data=json.dumps(
                    {
                        "type": "initial_status",
                        "task_id": str(task.task_id),
                        "status": task.status,
                        "status_display": task.get_status_display(),
                        "progress": task.progress,
                        "error_message": task.error_message,
                        "download_url": task.download_url or "",
                        "company_ticker": task.company.ticker,
                        "company_name": task.company.name,
                        "template_name": task.template.display_name,
                    }
                )
            )
        except PDFTask.DoesNotExist:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "error",
                        "message": f"Task {self.task_id} not found",
                    }
                )
            )
            await self.close()


async def send_task_status_update(
    task_id: str,
    status: str,
    status_display: str,
    progress: int,
    error_message: str = "",
    download_url: str = "",
):
    """
    Send task status update to all connected WebSocket clients.

    This function should be called whenever a task status changes.

    Args:
        task_id: UUID string of the task
        status: Status code
        status_display: Human-readable status
        progress: Progress percentage (0-100)
        error_message: Error message (for failed tasks)
        download_url: Download URL (for completed tasks)
    """
    from channels.layers import get_channel_layer  # noqa: PLC0415

    channel_layer = get_channel_layer()
    if channel_layer is None:
        logger.warning("Channel layer not configured, skipping WebSocket update")
        return

    room_group_name = f"pdf_task_{task_id}"

    await channel_layer.group_send(
        room_group_name,
        {
            "type": "task_update",
            "task_id": task_id,
            "status": status,
            "status_display": status_display,
            "progress": progress,
            "error_message": error_message,
            "download_url": download_url,
        },
    )
