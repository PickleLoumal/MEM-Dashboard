"""
Django API Callback Client

Sends status updates back to the Django API for task progress tracking.
"""

from __future__ import annotations

import logging
from typing import Literal

import requests
from requests.exceptions import RequestException

from config import config

logger = logging.getLogger(__name__)

# Type alias for status values
TaskStatus = Literal[
    "pending",
    "processing",
    "generating_charts",
    "compiling",
    "uploading",
    "completed",
    "failed",
]


def update_task_status(
    task_id: str,
    status: TaskStatus,
    progress: int = 0,
    error_message: str = "",
    s3_key: str = "",
) -> bool:
    """
    Send task status update to Django API.

    Args:
        task_id: UUID string of the task
        status: Current status code
        progress: Progress percentage (0-100)
        error_message: Error message (for failed status)
        s3_key: S3 object key (for completed status)

    Returns:
        True if callback succeeded, False otherwise
    """
    if not config.django_callback_url:
        logger.warning("Django callback URL not configured, skipping status update")
        return False

    payload = {
        "task_id": task_id,
        "status": status,
        "progress": progress,
        "error_message": error_message,
        "s3_key": s3_key,
    }

    headers = {
        "Content-Type": "application/json",
    }

    # Add API key if configured
    if config.internal_api_key:
        headers["X-Internal-API-Key"] = config.internal_api_key

    try:
        response = requests.post(
            config.django_callback_url,
            json=payload,
            headers=headers,
            timeout=30,
        )

        if response.status_code == 200:
            logger.info(
                "Task status updated",
                extra={
                    "task_id": task_id,
                    "status": status,
                    "progress": progress,
                },
            )
            return True
        else:
            logger.error(
                "Failed to update task status",
                extra={
                    "task_id": task_id,
                    "status_code": response.status_code,
                    "response": response.text[:500],
                },
            )
            return False

    except RequestException as e:
        logger.exception(
            "Error calling Django callback",
            extra={"task_id": task_id, "error": str(e)},
        )
        return False


def mark_processing(task_id: str, progress: int = 10) -> bool:
    """Mark task as processing."""
    return update_task_status(task_id, "processing", progress)


def mark_generating_charts(task_id: str, progress: int = 20) -> bool:
    """Mark task as generating charts."""
    return update_task_status(task_id, "generating_charts", progress)


def mark_compiling(task_id: str, progress: int = 50) -> bool:
    """Mark task as compiling LaTeX."""
    return update_task_status(task_id, "compiling", progress)


def mark_uploading(task_id: str, progress: int = 90) -> bool:
    """Mark task as uploading to S3."""
    return update_task_status(task_id, "uploading", progress)


def mark_completed(task_id: str, s3_key: str) -> bool:
    """Mark task as completed with S3 key."""
    return update_task_status(task_id, "completed", progress=100, s3_key=s3_key)


def mark_failed(task_id: str, error_message: str) -> bool:
    """Mark task as failed with error message."""
    return update_task_status(task_id, "failed", progress=0, error_message=error_message)

