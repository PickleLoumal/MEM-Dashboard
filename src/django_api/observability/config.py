"""
OpenTelemetry Configuration - Main Entry Point

Centralizes all observability configuration for the MEM Dashboard.
Supports both local development and AWS ECS production environments.
"""

import os
import logging
from typing import Optional
from functools import lru_cache

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT

from .traces import configure_tracing
from .metrics import configure_metrics
from .logs import configure_logging

# Service identification
SERVICE_NAME_VALUE = os.getenv('OTEL_SERVICE_NAME', 'mem-dashboard')
SERVICE_VERSION_VALUE = os.getenv('OTEL_SERVICE_VERSION', '1.0.0')
DEPLOYMENT_ENV = os.getenv('DEPLOYMENT_ENVIRONMENT', 'development')

# OpenTelemetry endpoint configuration
OTEL_EXPORTER_ENDPOINT = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4317')
OTEL_EXPORTER_PROTOCOL = os.getenv('OTEL_EXPORTER_OTLP_PROTOCOL', 'grpc')  # grpc or http/protobuf

# AWS-specific configuration
AWS_REGION = os.getenv('AWS_REGION', 'ap-east-1')
USE_AWS_XRAY = os.getenv('USE_AWS_XRAY', 'false').lower() == 'true'
USE_CLOUDWATCH = os.getenv('USE_CLOUDWATCH', 'false').lower() == 'true'

# Feature flags
ENABLE_TRACING = os.getenv('OTEL_ENABLE_TRACING', 'true').lower() == 'true'
ENABLE_METRICS = os.getenv('OTEL_ENABLE_METRICS', 'true').lower() == 'true'
ENABLE_LOGGING = os.getenv('OTEL_ENABLE_LOGGING', 'true').lower() == 'true'

# Sampling configuration
TRACE_SAMPLE_RATE = float(os.getenv('OTEL_TRACE_SAMPLE_RATE', '1.0'))  # 1.0 = 100%

_initialized = False


def get_resource() -> Resource:
    """
    Create OpenTelemetry Resource with service metadata.
    This identifies the service in all telemetry data.
    """
    return Resource.create({
        SERVICE_NAME: SERVICE_NAME_VALUE,
        SERVICE_VERSION: SERVICE_VERSION_VALUE,
        DEPLOYMENT_ENVIRONMENT: DEPLOYMENT_ENV,
        'service.namespace': 'mem-dashboard',
        'cloud.provider': 'aws' if USE_AWS_XRAY else 'local',
        'cloud.region': AWS_REGION,
    })


def setup_observability(
    enable_tracing: Optional[bool] = None,
    enable_metrics: Optional[bool] = None,
    enable_logging: Optional[bool] = None,
) -> None:
    """
    Initialize OpenTelemetry observability stack.
    
    This should be called once at application startup, typically in:
    - Django's settings.py
    - wsgi.py or asgi.py
    - manage.py for development
    
    Args:
        enable_tracing: Override OTEL_ENABLE_TRACING env var
        enable_metrics: Override OTEL_ENABLE_METRICS env var
        enable_logging: Override OTEL_ENABLE_LOGGING env var
    """
    global _initialized
    
    if _initialized:
        logging.getLogger(__name__).debug("OpenTelemetry already initialized, skipping")
        return
    
    # Use provided values or fall back to environment variables
    tracing_enabled = enable_tracing if enable_tracing is not None else ENABLE_TRACING
    metrics_enabled = enable_metrics if enable_metrics is not None else ENABLE_METRICS
    logging_enabled = enable_logging if enable_logging is not None else ENABLE_LOGGING
    
    resource = get_resource()
    
    logger = logging.getLogger(__name__)
    logger.info(
        f"Initializing OpenTelemetry: service={SERVICE_NAME_VALUE}, "
        f"env={DEPLOYMENT_ENV}, tracing={tracing_enabled}, "
        f"metrics={metrics_enabled}, logging={logging_enabled}"
    )
    
    # Configure each telemetry signal
    if tracing_enabled:
        configure_tracing(resource)
        logger.info("Tracing configured successfully")
    
    if metrics_enabled:
        configure_metrics(resource)
        logger.info("Metrics configured successfully")
    
    if logging_enabled:
        configure_logging(resource)
        logger.info("Logging configured successfully")
    
    # Auto-instrument Django and other libraries
    _auto_instrument()
    
    _initialized = True
    logger.info("OpenTelemetry initialization complete")


def _auto_instrument() -> None:
    """
    Auto-instrument common libraries used in the project.
    These warnings are non-critical - the app will work without instrumentation.
    """
    logger = logging.getLogger(__name__)
    
    # Django instrumentation
    try:
        from opentelemetry.instrumentation.django import DjangoInstrumentor
        if not DjangoInstrumentor().is_instrumented_by_opentelemetry:
            DjangoInstrumentor().instrument()
            logger.debug("Django instrumentation enabled")
    except ImportError as e:
        logger.debug(f"Django instrumentation not available: {e}")
    except Exception as e:
        logger.debug(f"Django instrumentation skipped: {e}")
    
    # psycopg2 (PostgreSQL) instrumentation
    try:
        from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
        if not Psycopg2Instrumentor().is_instrumented_by_opentelemetry:
            Psycopg2Instrumentor().instrument()
            logger.debug("psycopg2 instrumentation enabled")
    except ImportError as e:
        logger.debug(f"psycopg2 instrumentation not available: {e}")
    except Exception as e:
        logger.debug(f"psycopg2 instrumentation skipped: {e}")
    
    # Redis instrumentation
    try:
        from opentelemetry.instrumentation.redis import RedisInstrumentor
        if not RedisInstrumentor().is_instrumented_by_opentelemetry:
            RedisInstrumentor().instrument()
            logger.debug("Redis instrumentation enabled")
    except ImportError as e:
        logger.debug(f"Redis instrumentation not available: {e}")
    except Exception as e:
        logger.debug(f"Redis instrumentation skipped: {e}")
    
    # Requests library instrumentation (for external API calls)
    try:
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        if not RequestsInstrumentor().is_instrumented_by_opentelemetry:
            RequestsInstrumentor().instrument()
            logger.debug("Requests instrumentation enabled")
    except ImportError as e:
        logger.debug(f"Requests instrumentation not available: {e}")
    except Exception as e:
        logger.debug(f"Requests instrumentation skipped: {e}")


@lru_cache(maxsize=None)
def get_tracer(name: str = __name__) -> trace.Tracer:
    """
    Get a tracer instance for creating spans.
    
    Usage:
        from observability import get_tracer
        tracer = get_tracer(__name__)
        
        with tracer.start_as_current_span("my_operation") as span:
            span.set_attribute("key", "value")
            # ... do work ...
    """
    return trace.get_tracer(name, SERVICE_VERSION_VALUE)


@lru_cache(maxsize=None)
def get_meter(name: str = __name__) -> metrics.Meter:
    """
    Get a meter instance for creating metrics.
    
    Usage:
        from observability import get_meter
        meter = get_meter(__name__)
        
        request_counter = meter.create_counter(
            "requests_total",
            description="Total requests processed"
        )
        request_counter.add(1, {"endpoint": "/api/health"})
    """
    return metrics.get_meter(name, SERVICE_VERSION_VALUE)


def get_logger(name: str = __name__) -> logging.Logger:
    """
    Get a logger instance with OpenTelemetry context injection.
    
    Usage:
        from observability import get_logger
        logger = get_logger(__name__)
        
        logger.info("Processing request", extra={"user_id": 123})
    """
    return logging.getLogger(name)

