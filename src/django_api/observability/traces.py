"""
OpenTelemetry Tracing Configuration

Configures distributed tracing with support for:
- AWS X-Ray (production)
- OTLP exporter (generic/local)
- Pretty console exporter (development)
"""

import logging
import os
import sys
from collections.abc import Sequence

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult,
)
from opentelemetry.sdk.trace.sampling import (
    ALWAYS_ON,
    ParentBased,
    TraceIdRatioBased,
)

logger = logging.getLogger(__name__)


# ANSI color codes for pretty output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    RED = "\033[31m"
    GRAY = "\033[90m"


class PrettySpanExporter(SpanExporter):
    """
    A development-friendly span exporter that outputs readable, colored logs.

    Instead of dumping full JSON, shows concise span information:
    - HTTP requests with method, path, status, duration
    - Database queries (abbreviated)
    - Custom spans with key attributes
    """

    def __init__(self, show_db_queries: bool = False):
        self.show_db_queries = show_db_queries

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        for span in spans:
            self._print_span(span)
        return SpanExportResult.SUCCESS

    def _print_span(self, span: ReadableSpan) -> None:
        attrs = dict(span.attributes) if span.attributes else {}
        name = span.name
        duration_ns = span.end_time - span.start_time if span.end_time and span.start_time else 0
        duration_ms = duration_ns / 1_000_000

        # Skip internal/noisy spans
        if name.startswith(("opentelemetry.", "_")):
            return

        # Database spans - optionally show abbreviated
        if attrs.get("db.system") == "postgresql":
            if not self.show_db_queries:
                return  # Skip DB queries by default
            statement = attrs.get("db.statement", "")
            # Abbreviate long queries
            if len(statement) > 80:
                statement = statement[:77] + "..."
            print(  # noqa: T201
                f"{Colors.GRAY}   📊 DB {Colors.DIM}({duration_ms:.1f}ms){Colors.RESET} "
                f"{Colors.GRAY}{statement}{Colors.RESET}",
                file=sys.stderr,
            )
            return

        # HTTP server spans
        http_method = attrs.get("http.method") or attrs.get("http.request.method")
        http_route = attrs.get("http.route") or attrs.get("http.target") or attrs.get("url.path")
        http_status = attrs.get("http.status_code") or attrs.get("http.response.status_code")

        if http_method and http_route:
            # Skip static assets and health checks
            if any(
                skip in str(http_route) for skip in ["/static/", "favicon", "/__vite", "/health"]
            ):
                return

            # Color code by status
            if http_status:
                status_int = int(http_status)
                if status_int < 300:
                    status_color = Colors.GREEN
                elif status_int < 400:
                    status_color = Colors.YELLOW
                else:
                    status_color = Colors.RED
            else:
                status_color = Colors.GRAY

            print(  # noqa: T201
                f"{Colors.CYAN}→{Colors.RESET} {Colors.BOLD}{http_method}{Colors.RESET} "
                f"{http_route} "
                f"{status_color}{http_status or '...'}{Colors.RESET} "
                f"{Colors.DIM}({duration_ms:.0f}ms){Colors.RESET}",
                file=sys.stderr,
            )
            return

        # HTTP client spans (external API calls)
        if "http.url" in attrs or "url.full" in attrs:
            url = attrs.get("http.url") or attrs.get("url.full", "")
            # Only show for external APIs, not localhost
            if "localhost" not in str(url) and "127.0.0.1" not in str(url):
                print(  # noqa: T201
                    f"{Colors.MAGENTA}⇢{Colors.RESET} {Colors.DIM}External{Colors.RESET} "
                    f"{url[:60]}{'...' if len(str(url)) > 60 else ''} "
                    f"{Colors.DIM}({duration_ms:.0f}ms){Colors.RESET}",
                    file=sys.stderr,
                )
            return

        # Other custom spans - show if they took significant time
        if duration_ms > 10:  # Only show spans > 10ms
            print(  # noqa: T201
                f"{Colors.BLUE}◆{Colors.RESET} {name} "
                f"{Colors.DIM}({duration_ms:.0f}ms){Colors.RESET}",
                file=sys.stderr,
            )

    def shutdown(self) -> None:
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True


# Configuration from environment
USE_AWS_XRAY = os.getenv("USE_AWS_XRAY", "false").lower() == "true"
OTEL_EXPORTER_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
OTEL_EXPORTER_PROTOCOL = os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL", "grpc")
TRACE_SAMPLE_RATE = float(os.getenv("OTEL_TRACE_SAMPLE_RATE", "1.0"))
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"
DEPLOYMENT_ENV = os.getenv("DEPLOYMENT_ENVIRONMENT", "development")


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
            from opentelemetry import propagate
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            from opentelemetry.propagators.aws.aws_xray_propagator import AwsXRayPropagator

            # Set AWS X-Ray propagator for distributed tracing
            propagate.set_global_textmap(AwsXRayPropagator())

            # AWS X-Ray typically uses OTLP through the AWS Distro for OpenTelemetry (ADOT)
            # ADOT collector endpoint (usually running as a sidecar in ECS)
            xray_endpoint = os.getenv("AWS_XRAY_DAEMON_ADDRESS", "http://localhost:4317")

            logger.info(f"Using AWS X-Ray exporter with endpoint: {xray_endpoint}")
            return OTLPSpanExporter(endpoint=xray_endpoint, insecure=True)
        except ImportError as e:
            logger.warning(f"AWS X-Ray exporter not available: {e}, falling back to OTLP")

    # OTLP exporter (only in production or when explicitly configured)
    # Skip OTLP in development to avoid blocking on non-existent collector
    use_otlp = os.getenv("OTEL_USE_OTLP", "false").lower() == "true"
    if use_otlp and OTEL_EXPORTER_ENDPOINT:
        try:
            if OTEL_EXPORTER_PROTOCOL == "http/protobuf":
                from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

                logger.info(f"Using OTLP HTTP exporter with endpoint: {OTEL_EXPORTER_ENDPOINT}")
                return OTLPSpanExporter(endpoint=f"{OTEL_EXPORTER_ENDPOINT}/v1/traces")
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

            logger.info(f"Using OTLP gRPC exporter with endpoint: {OTEL_EXPORTER_ENDPOINT}")
            return OTLPSpanExporter(endpoint=OTEL_EXPORTER_ENDPOINT, insecure=True)
        except ImportError as e:
            logger.warning(f"OTLP exporter not available: {e}, falling back to console")

    # Pretty console exporter for development
    # Set OTEL_SHOW_DB_QUERIES=true to see database query spans
    show_db = os.getenv("OTEL_SHOW_DB_QUERIES", "false").lower() == "true"
    logger.info("Using Pretty console span exporter (development mode)")
    return PrettySpanExporter(show_db_queries=show_db)


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
    if DEPLOYMENT_ENV == "production":
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
    attributes: dict | None = None,
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
