"""
OpenTelemetry Tracing Configuration

Configures distributed tracing with support for:
- AWS X-Ray (production)
- OTLP exporter (generic/local)
- Console exporter (development)
"""

import os
import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, SpanProcessor
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.sdk.trace.sampling import (
    TraceIdRatioBased,
    ParentBased,
    ALWAYS_ON,
)
from opentelemetry.sdk.resources import Resource

logger = logging.getLogger(__name__)

# Configuration from environment
USE_AWS_XRAY = os.getenv('USE_AWS_XRAY', 'false').lower() == 'true'
OTEL_EXPORTER_ENDPOINT = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4317')
OTEL_EXPORTER_PROTOCOL = os.getenv('OTEL_EXPORTER_OTLP_PROTOCOL', 'grpc')
TRACE_SAMPLE_RATE = float(os.getenv('OTEL_TRACE_SAMPLE_RATE', '1.0'))
DEBUG_MODE = os.getenv('DEBUG', 'false').lower() == 'true'
DEPLOYMENT_ENV = os.getenv('DEPLOYMENT_ENVIRONMENT', 'development')


def get_sampler():
    """
    Get the appropriate sampler based on environment.
    
    In production, we may want to sample only a percentage of traces
    to reduce costs and noise.
    """
    if TRACE_SAMPLE_RATE >= 1.0:
        return ALWAYS_ON
    
    # ParentBased ensures child spans follow parent's sampling decision
    return ParentBased(root=TraceIdRatioBased(TRACE_SAMPLE_RATE))


def get_span_exporter():
    """
    Get the appropriate span exporter based on configuration.
    
    Priority:
    1. AWS X-Ray (if USE_AWS_XRAY=true)
    2. OTLP exporter (if endpoint configured)
    3. Console exporter (fallback for development)
    """
    # AWS X-Ray exporter
    if USE_AWS_XRAY:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            from opentelemetry.propagators.aws.aws_xray_propagator import AwsXRayPropagator
            from opentelemetry import propagate
            
            # Set AWS X-Ray propagator for distributed tracing
            propagate.set_global_textmap(AwsXRayPropagator())
            
            # AWS X-Ray typically uses OTLP through the AWS Distro for OpenTelemetry (ADOT)
            # ADOT collector endpoint (usually running as a sidecar in ECS)
            xray_endpoint = os.getenv('AWS_XRAY_DAEMON_ADDRESS', 'http://localhost:4317')
            
            logger.info(f"Using AWS X-Ray exporter with endpoint: {xray_endpoint}")
            return OTLPSpanExporter(endpoint=xray_endpoint, insecure=True)
        except ImportError as e:
            logger.warning(f"AWS X-Ray exporter not available: {e}, falling back to OTLP")
    
    # OTLP exporter (generic)
    if OTEL_EXPORTER_ENDPOINT:
        try:
            if OTEL_EXPORTER_PROTOCOL == 'http/protobuf':
                from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
                logger.info(f"Using OTLP HTTP exporter with endpoint: {OTEL_EXPORTER_ENDPOINT}")
                return OTLPSpanExporter(endpoint=f"{OTEL_EXPORTER_ENDPOINT}/v1/traces")
            else:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
                logger.info(f"Using OTLP gRPC exporter with endpoint: {OTEL_EXPORTER_ENDPOINT}")
                return OTLPSpanExporter(endpoint=OTEL_EXPORTER_ENDPOINT, insecure=True)
        except ImportError as e:
            logger.warning(f"OTLP exporter not available: {e}, falling back to console")
    
    # Console exporter (development fallback)
    logger.info("Using Console span exporter (development mode)")
    return ConsoleSpanExporter()


def configure_tracing(resource: Resource) -> TracerProvider:
    """
    Configure and set up the global TracerProvider.
    
    Args:
        resource: OpenTelemetry Resource identifying this service
        
    Returns:
        Configured TracerProvider
    """
    sampler = get_sampler()
    
    provider = TracerProvider(
        resource=resource,
        sampler=sampler,
    )
    
    # Get the appropriate exporter
    exporter = get_span_exporter()
    
    # Use BatchSpanProcessor in production for better performance
    # Use SimpleSpanProcessor in development for immediate output
    if DEPLOYMENT_ENV == 'production':
        processor = BatchSpanProcessor(
            exporter,
            max_queue_size=2048,
            max_export_batch_size=512,
            export_timeout_millis=30000,
        )
    else:
        processor = SimpleSpanProcessor(exporter)
    
    provider.add_span_processor(processor)
    
    # Set as global provider
    trace.set_tracer_provider(provider)
    
    logger.info(
        f"Tracing configured: sampler={type(sampler).__name__}, "
        f"exporter={type(exporter).__name__}, "
        f"processor={type(processor).__name__}"
    )
    
    return provider


def create_span_with_context(
    tracer: trace.Tracer,
    name: str,
    attributes: Optional[dict] = None,
    kind: trace.SpanKind = trace.SpanKind.INTERNAL,
):
    """
    Convenience function to create a span with common attributes.
    
    Usage:
        from observability.traces import create_span_with_context
        from observability import get_tracer
        
        tracer = get_tracer(__name__)
        with create_span_with_context(tracer, "fetch_stock_data", {"symbol": "AAPL"}):
            # ... do work ...
    """
    span = tracer.start_as_current_span(name, kind=kind)
    if attributes:
        for key, value in attributes.items():
            span.set_attribute(key, value)
    return span

