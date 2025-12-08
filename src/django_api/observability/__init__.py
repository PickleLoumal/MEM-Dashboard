"""
OpenTelemetry Observability Package for MEM Dashboard

This package provides enterprise-grade observability with:
- Distributed Tracing (via AWS X-Ray or OTLP)
- Metrics Collection (via CloudWatch or OTLP)
- Structured Logging (via CloudWatch Logs or OTLP)

Usage:
    # In Django settings.py or wsgi.py/asgi.py
    from observability import setup_observability
    setup_observability()
"""

from .config import setup_observability, get_tracer, get_meter, get_logger

__all__ = [
    'setup_observability',
    'get_tracer',
    'get_meter', 
    'get_logger',
]

__version__ = '1.0.0'

