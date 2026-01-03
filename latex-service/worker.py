"""
LaTeX Compiler Service Worker

Main SQS consumer process that:
1. Polls PDF generation tasks from SQS
2. Generates charts using matplotlib
3. Renders Jinja2 LaTeX templates
4. Compiles to PDF using XeLaTeX
5. Uploads results to S3
6. Sends status callbacks to Django

Usage:
    python worker.py
"""

from __future__ import annotations

import json
import logging
import os
import signal
import sys
import time
from functools import lru_cache
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import ClientError

from callback_client import (
    mark_compiling,
    mark_completed,
    mark_failed,
    mark_generating_charts,
    mark_processing,
    mark_uploading,
)
from chart_generator import ChartResult, generate_charts, generate_default_charts
from config import config
from latex_utils import LaTeXCompilationError, compile_latex
from s3_client import upload_chart, upload_pdf
from template_renderer import TemplateRenderError, render_template

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Graceful shutdown flag
shutdown_requested = False


def signal_handler(signum: int, frame: Any) -> None:
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_requested = True


# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


@lru_cache(maxsize=1)
def get_sqs_client():
    """Get cached SQS client instance."""
    return boto3.client("sqs", region_name=config.aws_region)


def poll_messages() -> list[dict[str, Any]]:
    """
    Poll SQS for new messages.

    Returns:
        List of message dicts with 'Body' and 'ReceiptHandle'
    """
    sqs = get_sqs_client()

    try:
        response = sqs.receive_message(
            QueueUrl=config.sqs_queue_url,
            MaxNumberOfMessages=config.worker_max_messages,
            WaitTimeSeconds=config.worker_poll_interval,
            VisibilityTimeout=config.worker_visibility_timeout,
            MessageAttributeNames=["All"],
        )
        return response.get("Messages", [])
    except ClientError as e:
        logger.exception("Failed to receive SQS messages")
        return []


def delete_message(receipt_handle: str) -> bool:
    """
    Delete a processed message from SQS.

    Args:
        receipt_handle: SQS message receipt handle

    Returns:
        True if deleted successfully
    """
    sqs = get_sqs_client()

    try:
        sqs.delete_message(
            QueueUrl=config.sqs_queue_url,
            ReceiptHandle=receipt_handle,
        )
        return True
    except ClientError as e:
        logger.exception("Failed to delete SQS message")
        return False


def process_message(message: dict[str, Any]) -> bool:
    """
    Process a single PDF generation message.

    Args:
        message: SQS message dict

    Returns:
        True if processing succeeded
    """
    body = message.get("Body", "{}")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in message: {e}")
        return False

    task_id = payload.get("task_id")
    if not task_id:
        logger.error("Message missing task_id")
        return False

    logger.info(f"Processing task: {task_id}")

    try:
        # Step 1: Mark as processing
        mark_processing(task_id, progress=10)

        # Step 2: Generate charts
        mark_generating_charts(task_id, progress=20)
        charts = generate_task_charts(task_id, payload)
        logger.info(f"Generated {len(charts)} charts for task {task_id}")

        # Step 3: Upload charts to S3
        chart_paths = upload_task_charts(task_id, charts)
        logger.info(f"Uploaded charts to S3: {chart_paths}")

        # Step 4: Render LaTeX template
        mark_compiling(task_id, progress=50)
        tex_content = render_task_template(payload, charts)
        logger.info(f"Rendered LaTeX template for task {task_id}")

        # Step 5: Save charts locally for LaTeX compilation
        save_charts_locally(task_id, charts)

        # Step 6: Compile PDF
        pdf_path = compile_latex(tex_content, task_id)
        logger.info(f"Compiled PDF: {pdf_path}")

        # Step 7: Upload PDF to S3
        mark_uploading(task_id, progress=90)
        s3_key = upload_pdf(task_id, pdf_path)
        logger.info(f"Uploaded PDF to S3: {s3_key}")

        # Step 8: Mark as completed
        mark_completed(task_id, s3_key)
        logger.info(f"Task {task_id} completed successfully")

        return True

    except LaTeXCompilationError as e:
        logger.error(f"LaTeX compilation failed for task {task_id}: {e}")
        mark_failed(task_id, f"LaTeX compilation failed: {e}")
        return False

    except TemplateRenderError as e:
        logger.error(f"Template rendering failed for task {task_id}: {e}")
        mark_failed(task_id, f"Template rendering failed: {e}")
        return False

    except Exception as e:
        logger.exception(f"Unexpected error processing task {task_id}")
        mark_failed(task_id, f"Unexpected error: {e}")
        return False


def generate_task_charts(
    task_id: str,
    payload: dict[str, Any],
) -> list[ChartResult]:
    """
    Generate charts for a task.

    Args:
        task_id: Task UUID
        payload: Message payload with data and chart config

    Returns:
        List of generated charts
    """
    data = payload.get("data", {})
    charts_config = payload.get("charts_config", [])

    if charts_config:
        return generate_charts(data, charts_config)
    else:
        return generate_default_charts(data)


def upload_task_charts(
    task_id: str,
    charts: list[ChartResult],
) -> list[str]:
    """
    Upload all charts to S3.

    Args:
        task_id: Task UUID
        charts: List of generated charts

    Returns:
        List of S3 keys
    """
    s3_keys = []

    for chart in charts:
        s3_key = upload_chart(task_id, chart.name, chart.image_data)
        s3_keys.append(s3_key)

    return s3_keys


def save_charts_locally(task_id: str, charts: list[ChartResult]) -> None:
    """
    Save charts to local directory for LaTeX compilation.

    XeLaTeX needs local file access to include images.
    """
    output_dir = config.output_dir / task_id
    output_dir.mkdir(parents=True, exist_ok=True)

    for chart in charts:
        chart_path = output_dir / f"{chart.name}.png"
        chart_path.write_bytes(chart.image_data)
        logger.debug(f"Saved chart locally: {chart_path}")


def render_task_template(
    payload: dict[str, Any],
    charts: list[ChartResult],
) -> str:
    """
    Render the LaTeX template for a task.

    Args:
        payload: Message payload with template and data
        charts: Generated charts

    Returns:
        Complete LaTeX document content
    """
    template_content = payload.get("template_content", "")
    preamble = payload.get("preamble", "")
    data = payload.get("data", {})
    settings = payload.get("settings", {})

    if not template_content:
        # Use default template
        template_content = get_default_template()

    return render_template(
        template_content=template_content,
        preamble=preamble,
        data=data,
        charts=charts,
        settings=settings,
    )


def get_default_template() -> str:
    """Load the default investment summary template."""
    default_template_path = Path(__file__).parent / "templates" / "investment_summary.tex.j2"

    if default_template_path.exists():
        return default_template_path.read_text(encoding="utf-8")

    # Fallback minimal template
    return r"""
\section*{\VAR{ summary.company_name | escape } Investment Summary}

\subsection*{Company Overview}
\VAR{ summary.business_overview | escape_para }

\subsection*{Key Metrics}
\begin{itemize}
    \item Stock Price: \VAR{ company.previous_close | currency('USD') }
    \item Market Cap: \VAR{ summary.market_cap_display | escape }
    \item P/E Ratio: \VAR{ company.pe_ratio_trailing | number }
    \item ROE: \VAR{ company.roe_trailing | percentage }
\end{itemize}

\subsection*{Charts}
\BLOCK{ for name, path in charts.items() }
\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\textwidth]{\VAR{ path }}
    \caption{\VAR{ name | escape }}
\end{figure}
\BLOCK{ endfor }

\subsection*{Recommendation}
\VAR{ summary.recommended_action_detail | escape_para }
"""


def run_worker() -> None:
    """
    Main worker loop.

    Polls SQS continuously until shutdown is requested.
    """
    logger.info("=" * 60)
    logger.info("LaTeX Compiler Service Worker Starting")
    logger.info("=" * 60)
    logger.info(f"SQS Queue: {config.sqs_queue_url}")
    logger.info(f"S3 Bucket: {config.s3_bucket}")
    logger.info(f"Django Callback: {config.django_callback_url}")
    logger.info(f"Poll Interval: {config.worker_poll_interval}s")
    logger.info("=" * 60)

    # Validate configuration
    if not config.sqs_queue_url:
        logger.error("PDF_SQS_QUEUE_URL not configured!")
        sys.exit(1)

    # Ensure directories exist
    config.tmp_dir.mkdir(parents=True, exist_ok=True)
    config.output_dir.mkdir(parents=True, exist_ok=True)

    consecutive_errors = 0
    max_consecutive_errors = 10

    while not shutdown_requested:
        try:
            messages = poll_messages()

            if not messages:
                logger.debug("No messages received, continuing...")
                consecutive_errors = 0
                continue

            for message in messages:
                if shutdown_requested:
                    break

                receipt_handle = message.get("ReceiptHandle")
                success = process_message(message)

                # Always delete the message after processing to prevent infinite retry loops
                # Failed tasks have their status updated via callback before this point
                if receipt_handle:
                    if success:
                        delete_message(receipt_handle)
                    else:
                        # Delete failed messages to prevent infinite retry
                        # The task status is already marked as FAILED via callback
                        # Use DLQ configuration on SQS side for retry/analysis needs
                        delete_message(receipt_handle)
                        logger.warning(
                            "Deleted failed message to prevent retry loop",
                            extra={"receipt_handle": receipt_handle[:50]},
                        )

                consecutive_errors = 0

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            break

        except Exception as e:
            consecutive_errors += 1
            logger.exception(f"Error in worker loop (attempt {consecutive_errors})")

            if consecutive_errors >= max_consecutive_errors:
                logger.critical(f"Too many consecutive errors ({max_consecutive_errors}), exiting")
                sys.exit(1)

            # Exponential backoff
            backoff = min(30, 2**consecutive_errors)
            logger.info(f"Backing off for {backoff}s...")
            time.sleep(backoff)

    logger.info("Worker shutdown complete")


if __name__ == "__main__":
    run_worker()

