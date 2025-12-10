"""
OpenTelemetry Logging Configuration

Configures structured logging with:
- OpenTelemetry context injection (trace_id, span_id)
- AWS CloudWatch Logs compatible format
- JSON structured logging for production
- Human-readable format for development
- Log rotation and management
"""

import json
import logging
import logging.handlers
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource

# Configuration from environment
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")  # 'json' or 'text'
LOG_DIR = os.getenv("LOG_DIR", "logs")
DEPLOYMENT_ENV = os.getenv("DEPLOYMENT_ENVIRONMENT", "development")

# Log rotation settings
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", str(10 * 1024 * 1024)))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))

# Service name for log identification
SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "mem-dashboard")


class OpenTelemetryLogFormatter(logging.Formatter):
    """
    Custom formatter that injects OpenTelemetry context into log records.
    Outputs JSON for production, human-readable text for development.
    """

    def __init__(self, use_json: bool = True):
        self.use_json = use_json
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        # Get current trace context
        span = trace.get_current_span()
        span_context = span.get_span_context() if span else None

        # Extract trace IDs if available
        trace_id = ""
        span_id = ""
        if span_context and span_context.is_valid:
            trace_id = format(span_context.trace_id, "032x")
            span_id = format(span_context.span_id, "016x")

        if self.use_json:
            return self._format_json(record, trace_id, span_id)
        return self._format_text(record, trace_id, span_id)

    def _format_json(self, record: logging.LogRecord, trace_id: str, span_id: str) -> str:
        """Format log record as JSON for CloudWatch and log aggregation."""
        log_entry = {
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": SERVICE_NAME,
            "environment": DEPLOYMENT_ENV,
        }

        # Add trace context if available
        if trace_id:
            log_entry["trace_id"] = trace_id
            log_entry["span_id"] = span_id

        # Add source location
        log_entry["source"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add any extra fields
        for key, value in record.__dict__.items():
            if key not in (
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "exc_info",
                "exc_text",
                "thread",
                "threadName",
                "message",
                "asctime",
                "taskName",
            ):
                try:
                    # Ensure value is JSON serializable
                    json.dumps(value)
                    log_entry[key] = value
                except (TypeError, ValueError):
                    log_entry[key] = str(value)

        return json.dumps(log_entry, default=str)

    def _format_text(self, record: logging.LogRecord, trace_id: str, span_id: str) -> str:
        """Format log record as human-readable text for development."""
        timestamp = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M:%S")

        # Build trace context string
        trace_str = ""
        if trace_id:
            trace_str = f" [trace:{trace_id[:8]}]"

        # Format the message
        message = f"{timestamp} | {record.levelname:8s} | {record.name}{trace_str} | {record.getMessage()}"

        # Add exception if present
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"

        return message


class OTelLoggingHandler(logging.Handler):
    """
    Custom handler that bridges Python logging with OpenTelemetry logs.
    This enables logs to be exported alongside traces and metrics.
    """

    def __init__(self):
        super().__init__()
        self._logger_provider = None

    def emit(self, record: logging.LogRecord):
        # OpenTelemetry logging is still experimental
        # For now, this is a placeholder for future OTel Logs SDK integration
        pass


def configure_logging(resource: Resource) -> None:
    """
    Configure application logging with OpenTelemetry integration.

    Args:
        resource: OpenTelemetry Resource identifying this service
    """
    # Create log directory if it doesn't exist
    log_path = Path(LOG_DIR)
    log_path.mkdir(parents=True, exist_ok=True)

    # Determine log format based on environment
    use_json = LOG_FORMAT == "json" or DEPLOYMENT_ENV == "production"
    formatter = OpenTelemetryLogFormatter(use_json=use_json)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))

    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_LEVEL))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation (for local development and backup)
    if DEPLOYMENT_ENV != "production":
        # In production, rely on CloudWatch; locally, write to files
        main_log_file = log_path / f"{SERVICE_NAME}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            main_log_file,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(getattr(logging, LOG_LEVEL))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        # Error-only log file
        error_log_file = log_path / f"{SERVICE_NAME}.error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)

    # Configure specific loggers
    _configure_library_loggers()

    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured: level={LOG_LEVEL}, format={'json' if use_json else 'text'}, "
        f"dir={LOG_DIR}"
    )


def _configure_library_loggers():
    """
    Configure log levels for third-party libraries to reduce noise.
    """
    # Reduce verbosity of noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("opentelemetry").setLevel(logging.WARNING)

    # Django loggers
    logging.getLogger("django.request").setLevel(logging.INFO)
    logging.getLogger("django.db.backends").setLevel(logging.WARNING)
    logging.getLogger("django.security").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with OpenTelemetry context injection.

    Usage:
        from observability.logs import get_logger
        logger = get_logger(__name__)

        # Basic logging
        logger.info("Processing request")

        # With extra context
        logger.info("Stock data fetched", extra={"symbol": "AAPL", "count": 100})
    """
    return logging.getLogger(name)
