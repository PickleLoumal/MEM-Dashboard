"""
OpenTelemetry Observability Package for MEM Dashboard

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

from .config import setup_observability, get_tracer, get_meter, get_logger
from .middleware import (
    get_frontend_trace_id,
    get_frontend_span_id,
    get_request_id,
    TraceContextFilter,
)

__all__ = [
    # Core setup
    'setup_observability',
    
    # Telemetry providers
    'get_tracer',
    'get_meter', 
    'get_logger',
    
    # Frontend trace context (from middleware)
    'get_frontend_trace_id',
    'get_frontend_span_id',
    'get_request_id',
    
    # Logging filter
    'TraceContextFilter',
]

__version__ = '1.0.0'
