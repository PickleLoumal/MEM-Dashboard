"""
S3 Client Module

Handles all S3 operations: uploading charts, PDFs, and downloading templates.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from config import config

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_s3_client():
    """Get cached S3 client instance."""
    return boto3.client("s3", region_name=config.aws_region)


def upload_file(
    file_path: Path,
    s3_key: str,
    content_type: str = "application/octet-stream",
) -> str:
    """
    Upload a file to S3.

    Args:
        file_path: Local file path
        s3_key: S3 object key
        content_type: MIME type of the file

    Returns:
        Full S3 URI (s3://bucket/key)

    Raises:
        ClientError: If upload fails
    """
    s3 = get_s3_client()

    try:
        s3.upload_file(
            str(file_path),
            config.s3_bucket,
            s3_key,
            ExtraArgs={"ContentType": content_type},
        )
        logger.info(
            "Uploaded file to S3",
            extra={"s3_key": s3_key, "size_bytes": file_path.stat().st_size},
        )
        return f"s3://{config.s3_bucket}/{s3_key}"
    except ClientError as e:
        logger.exception("Failed to upload file to S3", extra={"s3_key": s3_key})
        raise


def upload_bytes(
    data: bytes,
    s3_key: str,
    content_type: str = "application/octet-stream",
) -> str:
    """
    Upload bytes directly to S3.

    Args:
        data: Bytes to upload
        s3_key: S3 object key
        content_type: MIME type

    Returns:
        Full S3 URI
    """
    s3 = get_s3_client()

    try:
        s3.put_object(
            Bucket=config.s3_bucket,
            Key=s3_key,
            Body=data,
            ContentType=content_type,
        )
        logger.info(
            "Uploaded bytes to S3",
            extra={"s3_key": s3_key, "size_bytes": len(data)},
        )
        return f"s3://{config.s3_bucket}/{s3_key}"
    except ClientError as e:
        logger.exception("Failed to upload bytes to S3", extra={"s3_key": s3_key})
        raise


def upload_chart(task_id: str, chart_name: str, image_data: bytes) -> str:
    """
    Upload a chart image to S3.

    Args:
        task_id: Task UUID for namespacing
        chart_name: Chart identifier (e.g., "stock_price", "roe_trend")
        image_data: PNG image bytes

    Returns:
        S3 key of uploaded chart
    """
    s3_key = f"{config.s3_charts_prefix}{task_id}/{chart_name}.png"
    upload_bytes(image_data, s3_key, content_type="image/png")
    return s3_key


def upload_pdf(task_id: str, pdf_path: Path) -> str:
    """
    Upload a generated PDF to S3.

    Args:
        task_id: Task UUID
        pdf_path: Local path to PDF file

    Returns:
        S3 key of uploaded PDF
    """
    s3_key = f"{config.s3_reports_prefix}{task_id}/report.pdf"
    upload_file(pdf_path, s3_key, content_type="application/pdf")
    return s3_key


def download_file(s3_key: str, local_path: Path) -> Path:
    """
    Download a file from S3.

    Args:
        s3_key: S3 object key
        local_path: Local destination path

    Returns:
        Path to downloaded file
    """
    s3 = get_s3_client()

    try:
        local_path.parent.mkdir(parents=True, exist_ok=True)
        s3.download_file(config.s3_bucket, s3_key, str(local_path))
        logger.info("Downloaded file from S3", extra={"s3_key": s3_key})
        return local_path
    except ClientError as e:
        logger.exception("Failed to download file from S3", extra={"s3_key": s3_key})
        raise


def get_chart_url(task_id: str, chart_name: str) -> str:
    """
    Get the S3 key for a chart (for LaTeX \includegraphics).

    Note: In the LaTeX template, we'll use local paths since
    charts are downloaded to the compilation directory.
    """
    return f"{chart_name}.png"

