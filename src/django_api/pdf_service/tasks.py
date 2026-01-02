"""
PDF Service Task Publisher

Handles publishing PDF generation tasks to SQS for async processing
by the LaTeX compiler microservice.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta
from functools import lru_cache
from typing import TYPE_CHECKING, Any

import boto3
from botocore.exceptions import ClientError
from django.utils import timezone

if TYPE_CHECKING:
    from .models import PDFTask

logger = logging.getLogger(__name__)

# Configuration from environment
PDF_QUEUE_URL = os.getenv("PDF_SQS_QUEUE_URL", "")
AWS_REGION = os.getenv("AWS_REGION", "ap-east-1")
PDF_S3_BUCKET = os.getenv("PDF_S3_BUCKET", "alfie-pdf-reports")


@lru_cache(maxsize=1)
def get_sqs_client() -> Any:
    """
    Get cached boto3 SQS client.

    Uses lru_cache to avoid creating new clients on every call.
    """
    return boto3.client("sqs", region_name=AWS_REGION)


@lru_cache(maxsize=1)
def get_s3_client() -> Any:
    """
    Get cached boto3 S3 client.

    Uses lru_cache to avoid creating new clients on every call.
    """
    return boto3.client("s3", region_name=AWS_REGION)


def _is_fifo_queue(queue_url: str) -> bool:
    """Check if the queue URL indicates a FIFO queue."""
    return queue_url.endswith(".fifo")


def publish_pdf_task(
    task: PDFTask,
    summary_data: dict,
    company_data: dict,
) -> bool:
    """
    Publish PDF generation task to SQS.

    Args:
        task: PDFTask instance with template and company references
        summary_data: Investment summary data for the report
        company_data: Company financial data for the report

    Returns:
        True if message was successfully sent, False otherwise
    """
    if not PDF_QUEUE_URL:
        logger.warning(
            "PDF_SQS_QUEUE_URL not configured, skipping SQS publish",
            extra={"task_id": str(task.task_id)},
        )
        return False

    message = {
        "task_id": str(task.task_id),
        "template_id": task.template.id,
        "template_name": task.template.name,
        "template_content": task.template.latex_content,
        "preamble": task.template.preamble,
        "charts_config": task.template.charts_config,
        "data": {
            "summary": summary_data,
            "company": company_data,
        },
        "settings": {
            "page_size": task.template.page_size,
            "margins": task.template.margins,
            "header_left": task.template.header_left,
            "header_right": task.template.header_right,
            "footer_center": task.template.footer_center,
        },
        "metadata": {
            "company_ticker": task.company.ticker,
            "company_name": task.company.name,
            "requested_at": timezone.now().isoformat(),  # Use Django timezone
            "requested_by": task.requested_by,
        },
    }

    try:
        sqs = get_sqs_client()

        # Build send_message parameters
        send_params = {
            "QueueUrl": PDF_QUEUE_URL,
            "MessageBody": json.dumps(message, default=str),
        }

        # Only add FIFO-specific parameters if queue is FIFO
        if _is_fifo_queue(PDF_QUEUE_URL):
            send_params["MessageGroupId"] = f"pdf-{task.company.ticker or 'default'}"
            send_params["MessageDeduplicationId"] = str(task.task_id)

        response = sqs.send_message(**send_params)
        message_id = response.get("MessageId", "unknown")
        logger.info(
            "Published PDF task to SQS",
            extra={
                "task_id": str(task.task_id),
                "message_id": message_id,
                "company_ticker": task.company.ticker,
            },
        )
        return True
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", "Unknown error")
        logger.exception(
            "Failed to publish PDF task to SQS",
            extra={
                "task_id": str(task.task_id),
                "error_code": error_code,
                "error_message": error_message,
            },
        )
        return False
    except Exception as e:
        logger.exception(
            "Unexpected error publishing PDF task to SQS",
            extra={"task_id": str(task.task_id), "error": str(e)},
        )
        return False


def update_task_status_from_worker(
    task_id: str,
    status: str,
    progress: int = 0,
    error_message: str = "",
    s3_key: str = "",
) -> bool:
    """
    Update task status in database (called by worker or via callback).

    This function is typically called via an API callback from the LaTeX
    worker service, or can be used for local development/testing.

    Args:
        task_id: UUID string of the task
        status: New status value
        progress: Progress percentage (0-100)
        error_message: Error message if failed
        s3_key: S3 object key if completed

    Returns:
        True if update was successful
    """
    # Import here to avoid circular import at module load time
    from .models import PDFTask  # noqa: PLC0415

    try:
        task = PDFTask.objects.get(task_id=task_id)

        task.status = status
        task.progress = progress

        if error_message:
            task.error_message = error_message

        if s3_key:
            task.s3_key = s3_key

        if status in (PDFTask.Status.COMPLETED, PDFTask.Status.FAILED):
            task.completed_at = timezone.now()
            if task.created_at:
                delta = timezone.now() - task.created_at
                task.processing_time_ms = int(delta.total_seconds() * 1000)

        task.save()

        logger.info(
            "Updated task status",
            extra={
                "task_id": task_id,
                "status": status,
                "progress": progress,
            },
        )
        return True

    except PDFTask.DoesNotExist:
        logger.warning(
            "Task not found for status update",
            extra={"task_id": task_id},
        )
        return False


def generate_presigned_download_url(
    s3_key: str,
    expiration_seconds: int = 3600,
) -> tuple[str, datetime]:
    """
    Generate a pre-signed URL for downloading a PDF from S3.

    Args:
        s3_key: S3 object key
        expiration_seconds: URL expiration time in seconds (default 1 hour)

    Returns:
        Tuple of (presigned_url, expiration_datetime)

    Raises:
        ClientError: If URL generation fails due to S3 issues
    """
    try:
        s3 = get_s3_client()

        url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": PDF_S3_BUCKET,
                "Key": s3_key,
            },
            ExpiresIn=expiration_seconds,
        )

        expires_at = timezone.now() + timedelta(seconds=expiration_seconds)

        return url, expires_at

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        logger.exception(
            "Failed to generate presigned URL",
            extra={
                "s3_key": s3_key,
                "bucket": PDF_S3_BUCKET,
                "error_code": error_code,
            },
        )
        raise
    except Exception as e:
        logger.exception(
            "Unexpected error generating presigned URL",
            extra={"s3_key": s3_key, "error": str(e)},
        )
        raise
