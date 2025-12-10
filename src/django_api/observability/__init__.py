"""
OpenTelemetry Observability Package

This package provides enterprise-grade observability with:
- Distributed Tracing (via AWS X-Ray or OTLP)
- Metrics Collection (via CloudWatch or OTLP)
- Structured Logging (via CloudWatch Logs or OTLP)
- Frontend Trace Context Propagation (via X-Trace-ID)

Usage:
    # In Django settings.py or wsgi.py/asgi.py
    from observability import setup_observability
    setup_observability()

    # In views or services - get frontend trace ID
    from observability import get_frontend_trace_id
    trace_id = get_frontend_trace_id()  # Returns the X-Trace-ID from frontend

    # Create custom spans with tracer
    from observability import get_tracer
    tracer = get_tracer(__name__)
    with tracer.start_as_current_span("my_operation") as span:
        span.set_attribute("frontend_trace_id", get_frontend_trace_id())
        # ... do work ...
"""

from .config import get_logger, get_meter, get_tracer, setup_observability
from .middleware import (
    TraceContextFilter,
    get_frontend_span_id,
    get_frontend_trace_id,
    get_request_id,
)

__all__ = [
    # Logging filter
    "TraceContextFilter",
    "get_frontend_span_id",
    # Frontend trace context (from middleware)
    "get_frontend_trace_id",
    "get_logger",
    "get_meter",
    "get_request_id",
    # Telemetry providers
    "get_tracer",
    # Core setup
    "setup_observability",
]

__version__ = "1.0.0"
