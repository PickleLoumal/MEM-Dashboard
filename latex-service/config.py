"""
LaTeX Service Configuration

Centralized configuration management using environment variables.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


def _safe_int(env_var: str, default: int) -> int:
    """
    Safely parse integer from environment variable.

    Args:
        env_var: Environment variable name
        default: Default value if parsing fails

    Returns:
        Parsed integer or default value
    """
    value = os.getenv(env_var, str(default))
    try:
        return int(value)
    except ValueError:
        logger.warning(
            f"Invalid integer for {env_var}: '{value}', using default {default}"
        )
        return default


@dataclass(frozen=True)
class Config:
    """Immutable configuration container."""

    # AWS Settings
    aws_region: str
    sqs_queue_url: str
    s3_bucket: str
    s3_charts_prefix: str
    s3_reports_prefix: str

    # Django Callback
    django_callback_url: str
    internal_api_key: str

    # Worker Settings
    worker_poll_interval: int
    worker_visibility_timeout: int
    worker_max_messages: int

    # LaTeX Settings
    latex_timeout_seconds: int
    latex_max_retries: int

    # Local Paths
    tmp_dir: Path
    output_dir: Path

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables with validation."""
        return cls(
            # AWS
            aws_region=os.getenv("AWS_REGION", "ap-east-1"),
            sqs_queue_url=os.getenv("PDF_SQS_QUEUE_URL", ""),
            s3_bucket=os.getenv("PDF_S3_BUCKET", "alfie-pdf-reports"),
            s3_charts_prefix=os.getenv("S3_CHARTS_PREFIX", "charts/"),
            s3_reports_prefix=os.getenv("S3_REPORTS_PREFIX", "reports/"),
            # Django
            django_callback_url=os.getenv(
                "DJANGO_CALLBACK_URL",
                "http://localhost:8001/api/pdf/internal/callback/",
            ),
            internal_api_key=os.getenv("PDF_INTERNAL_API_KEY", ""),
            # Worker - with safe integer parsing
            worker_poll_interval=_safe_int("WORKER_POLL_INTERVAL", 20),
            worker_visibility_timeout=_safe_int("WORKER_VISIBILITY_TIMEOUT", 300),
            worker_max_messages=_safe_int("WORKER_MAX_MESSAGES", 1),
            # LaTeX - with safe integer parsing
            latex_timeout_seconds=_safe_int("LATEX_TIMEOUT_SECONDS", 120),
            latex_max_retries=_safe_int("LATEX_MAX_RETRIES", 2),
            # Paths
            tmp_dir=Path(os.getenv("TMP_DIR", "/app/tmp")),
            output_dir=Path(os.getenv("OUTPUT_DIR", "/app/output")),
        )


# Global configuration instance
config = Config.from_env()

