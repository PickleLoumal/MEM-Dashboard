"""
OpenTelemetry Metrics Configuration

Configures metrics collection with support for:
- AWS CloudWatch (production)
- OTLP exporter (generic/local)
- Console exporter (development)

Includes pre-defined metrics for common application patterns.
"""

import os
import logging
from typing import Optional, Callable

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
    ConsoleMetricExporter,
)
from opentelemetry.sdk.resources import Resource

logger = logging.getLogger(__name__)

# Configuration from environment
USE_CLOUDWATCH = os.getenv('USE_CLOUDWATCH', 'false').lower() == 'true'
OTEL_EXPORTER_ENDPOINT = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4317')
OTEL_EXPORTER_PROTOCOL = os.getenv('OTEL_EXPORTER_OTLP_PROTOCOL', 'grpc')
METRICS_EXPORT_INTERVAL = int(os.getenv('OTEL_METRICS_EXPORT_INTERVAL_MS', '60000'))
DEPLOYMENT_ENV = os.getenv('DEPLOYMENT_ENVIRONMENT', 'development')

# Global meter reference for pre-defined metrics
_app_meter: Optional[metrics.Meter] = None


def get_metric_exporter():
    """
    Get the appropriate metric exporter based on configuration.
    """
    # OTLP exporter (only in production or when explicitly configured)
    # Skip OTLP in development to avoid blocking on non-existent collector
    use_otlp = os.getenv('OTEL_USE_OTLP', 'false').lower() == 'true'
    if use_otlp and (USE_CLOUDWATCH or OTEL_EXPORTER_ENDPOINT):
        try:
            if OTEL_EXPORTER_PROTOCOL == 'http/protobuf':
                from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
                logger.info(f"Using OTLP HTTP metrics exporter: {OTEL_EXPORTER_ENDPOINT}")
                return OTLPMetricExporter(endpoint=f"{OTEL_EXPORTER_ENDPOINT}/v1/metrics")
            else:
                from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
                logger.info(f"Using OTLP gRPC metrics exporter: {OTEL_EXPORTER_ENDPOINT}")
                return OTLPMetricExporter(endpoint=OTEL_EXPORTER_ENDPOINT, insecure=True)
        except ImportError as e:
            logger.warning(f"OTLP metrics exporter not available: {e}")
    
    # Console exporter (development fallback)
    logger.info("Using Console metrics exporter (development mode)")
    return ConsoleMetricExporter()


def configure_metrics(resource: Resource) -> MeterProvider:
    """
    Configure and set up the global MeterProvider.
    
    Args:
        resource: OpenTelemetry Resource identifying this service
        
    Returns:
        Configured MeterProvider
    """
    global _app_meter
    
    exporter = get_metric_exporter()
    
    # Configure metric reader with export interval
    reader = PeriodicExportingMetricReader(
        exporter,
        export_interval_millis=METRICS_EXPORT_INTERVAL,
    )
    
    provider = MeterProvider(
        resource=resource,
        metric_readers=[reader],
    )
    
    # Set as global provider
    metrics.set_meter_provider(provider)
    
    # Create application meter for pre-defined metrics
    _app_meter = metrics.get_meter('mem_dashboard.metrics', '1.0.0')
    
    # Initialize pre-defined metrics
    _initialize_application_metrics()
    
    logger.info(
        f"Metrics configured: exporter={type(exporter).__name__}, "
        f"export_interval={METRICS_EXPORT_INTERVAL}ms"
    )
    
    return provider


# ============================================================================
# Pre-defined Application Metrics
# ============================================================================

# Counters
_request_counter: Optional[metrics.Counter] = None
_error_counter: Optional[metrics.Counter] = None
_api_call_counter: Optional[metrics.Counter] = None

# Histograms
_request_duration: Optional[metrics.Histogram] = None
_db_query_duration: Optional[metrics.Histogram] = None
_external_api_duration: Optional[metrics.Histogram] = None

# Gauges (using UpDownCounter as proxy)
_active_requests: Optional[metrics.UpDownCounter] = None
_cache_size: Optional[metrics.UpDownCounter] = None


def _initialize_application_metrics():
    """Initialize pre-defined metrics for the application."""
    global _request_counter, _error_counter, _api_call_counter
    global _request_duration, _db_query_duration, _external_api_duration
    global _active_requests, _cache_size
    
    if _app_meter is None:
        return
    
    # Request counter
    _request_counter = _app_meter.create_counter(
        name="http_requests_total",
        description="Total number of HTTP requests",
        unit="1",
    )
    
    # Error counter
    _error_counter = _app_meter.create_counter(
        name="errors_total",
        description="Total number of errors",
        unit="1",
    )
    
    # External API call counter
    _api_call_counter = _app_meter.create_counter(
        name="external_api_calls_total",
        description="Total number of external API calls (FRED, BEA, AkShare)",
        unit="1",
    )
    
    # Request duration histogram
    _request_duration = _app_meter.create_histogram(
        name="http_request_duration_seconds",
        description="HTTP request duration in seconds",
        unit="s",
    )
    
    # Database query duration
    _db_query_duration = _app_meter.create_histogram(
        name="db_query_duration_seconds",
        description="Database query duration in seconds",
        unit="s",
    )
    
    # External API duration
    _external_api_duration = _app_meter.create_histogram(
        name="external_api_duration_seconds",
        description="External API call duration in seconds",
        unit="s",
    )
    
    # Active requests gauge
    _active_requests = _app_meter.create_up_down_counter(
        name="http_requests_active",
        description="Number of active HTTP requests",
        unit="1",
    )
    
    logger.debug("Application metrics initialized")


# ============================================================================
# Metric Recording Functions
# ============================================================================

def record_request(endpoint: str, method: str, status_code: int):
    """Record an HTTP request."""
    if _request_counter:
        _request_counter.add(1, {
            "endpoint": endpoint,
            "method": method,
            "status_code": str(status_code),
        })


def record_error(error_type: str, endpoint: str = "unknown"):
    """Record an error occurrence."""
    if _error_counter:
        _error_counter.add(1, {
            "error_type": error_type,
            "endpoint": endpoint,
        })


def record_api_call(api_name: str, success: bool = True):
    """Record an external API call (FRED, BEA, AkShare, etc.)."""
    if _api_call_counter:
        _api_call_counter.add(1, {
            "api_name": api_name,
            "success": str(success),
        })


def record_request_duration(duration_seconds: float, endpoint: str, method: str):
    """Record HTTP request duration."""
    if _request_duration:
        _request_duration.record(duration_seconds, {
            "endpoint": endpoint,
            "method": method,
        })


def record_db_query_duration(duration_seconds: float, operation: str):
    """Record database query duration."""
    if _db_query_duration:
        _db_query_duration.record(duration_seconds, {
            "operation": operation,
        })


def record_external_api_duration(duration_seconds: float, api_name: str):
    """Record external API call duration."""
    if _external_api_duration:
        _external_api_duration.record(duration_seconds, {
            "api_name": api_name,
        })


def increment_active_requests():
    """Increment active request counter."""
    if _active_requests:
        _active_requests.add(1)


def decrement_active_requests():
    """Decrement active request counter."""
    if _active_requests:
        _active_requests.add(-1)

