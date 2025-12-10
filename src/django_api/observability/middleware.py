"""
OpenTelemetry Django Middleware

Provides automatic instrumentation for Django requests:
- Request/response tracing with detailed attributes
- Frontend trace context propagation (X-Trace-ID, X-Span-ID)
- Metrics collection (latency, status codes, etc.)
- Error tracking and logging
"""

import time
import logging
import contextvars
from typing import Callable, Optional

from django.http import HttpRequest, HttpResponse
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from .metrics import (
    record_request,
    record_error,
    record_request_duration,
    increment_active_requests,
    decrement_active_requests,
)
from .config import get_tracer

logger = logging.getLogger(__name__)

# Context variables for trace propagation
# 这些变量在整个请求生命周期内可用，可以被业务代码读取
frontend_trace_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'frontend_trace_id', default=None
)
frontend_span_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'frontend_span_id', default=None
)
request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'request_id', default=None
)


def get_frontend_trace_id() -> Optional[str]:
    """获取当前请求的前端 Trace ID"""
    return frontend_trace_id_var.get()


def get_frontend_span_id() -> Optional[str]:
    """获取当前请求的前端 Span ID"""
    return frontend_span_id_var.get()


def get_request_id() -> Optional[str]:
    """获取当前请求的 Request ID（后端生成）"""
    return request_id_var.get()


class TraceContextFilter(logging.Filter):
    """
    Logging Filter that injects trace context into all log records.
    
    这个 filter 会自动将前端 trace ID 注入到所有日志记录中，
    使得前后端日志可以通过同一个 trace_id 关联。
    
    Usage in logging config:
        'filters': {
            'trace_context': {
                '()': 'observability.middleware.TraceContextFilter',
            },
        },
        'handlers': {
            'console': {
                'filters': ['trace_context'],
                ...
            },
        },
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        # 注入前端 trace context
        record.frontend_trace_id = frontend_trace_id_var.get() or ''
        record.frontend_span_id = frontend_span_id_var.get() or ''
        record.request_id = request_id_var.get() or ''
        
        # 尝试获取 OpenTelemetry trace context
        span = trace.get_current_span()
        span_context = span.get_span_context() if span else None
        
        if span_context and span_context.is_valid:
            record.otel_trace_id = format(span_context.trace_id, '032x')
            record.otel_span_id = format(span_context.span_id, '016x')
        else:
            record.otel_trace_id = ''
            record.otel_span_id = ''
        
        return True


class OpenTelemetryMiddleware:
    """
    Middleware that provides OpenTelemetry observability for all requests.
    
    Features:
    - Extracts X-Trace-ID from frontend requests for correlation
    - Creates spans with frontend context as attributes
    - Records request metrics and timing
    - Handles errors and slow request logging
    
    Add to MIDDLEWARE in settings.py:
        'observability.middleware.OpenTelemetryMiddleware',
    """
    
    # HTTP header names for trace propagation
    TRACE_ID_HEADER = 'HTTP_X_TRACE_ID'
    SPAN_ID_HEADER = 'HTTP_X_SPAN_ID'
    REQUEST_ID_HEADER = 'HTTP_X_REQUEST_ID'
    
    def __init__(self, get_response: Callable):
        self.get_response = get_response
        self.tracer = get_tracer('mem_dashboard.middleware')
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Extract frontend trace context from headers
        frontend_trace_id = request.META.get(self.TRACE_ID_HEADER, '')
        frontend_span_id = request.META.get(self.SPAN_ID_HEADER, '')
        
        # Generate backend request ID if not provided
        import uuid
        request_id = request.META.get(self.REQUEST_ID_HEADER, '') or str(uuid.uuid4())[:8]
        
        # Set context variables for this request
        trace_token = frontend_trace_id_var.set(frontend_trace_id)
        span_token = frontend_span_id_var.set(frontend_span_id)
        request_token = request_id_var.set(request_id)
        
        try:
            return self._process_request(request, frontend_trace_id, frontend_span_id, request_id)
        finally:
            # Reset context variables
            frontend_trace_id_var.reset(trace_token)
            frontend_span_id_var.reset(span_token)
            request_id_var.reset(request_token)
    
    def _process_request(
        self, 
        request: HttpRequest, 
        frontend_trace_id: str,
        frontend_span_id: str,
        request_id: str
    ) -> HttpResponse:
        # Start timing
        start_time = time.perf_counter()
        
        # Track active requests
        increment_active_requests()
        
        # Extract request info
        endpoint = self._get_endpoint(request)
        method = request.method
        
        # Log incoming request with trace context
        if frontend_trace_id:
            logger.info(
                f"[TRACE] {method} {request.path}",
                extra={
                    'frontend_trace_id': frontend_trace_id,
                    'frontend_span_id': frontend_span_id,
                    'request_id': request_id,
                    'endpoint': endpoint,
                }
            )
        
        # Get or create span from Django instrumentation
        span = trace.get_current_span()
        
        # Add custom attributes to span
        if span and span.is_recording():
            span.set_attribute('http.endpoint', endpoint)
            span.set_attribute('http.user_agent', request.META.get('HTTP_USER_AGENT', ''))
            span.set_attribute('http.client_ip', self._get_client_ip(request))
            span.set_attribute('request.id', request_id)
            
            # Add frontend trace context as span attributes
            # This allows correlating frontend and backend traces
            if frontend_trace_id:
                span.set_attribute('frontend.trace_id', frontend_trace_id)
            if frontend_span_id:
                span.set_attribute('frontend.span_id', frontend_span_id)
            
            # Add query parameters (be careful with sensitive data)
            if request.GET:
                span.set_attribute('http.query_params_count', len(request.GET))
        
        response = None
        error_occurred = False
        
        try:
            response = self.get_response(request)
            
            # Add trace ID to response header for debugging
            if frontend_trace_id:
                response['X-Trace-ID'] = frontend_trace_id
            response['X-Request-ID'] = request_id
            
            return response
        except Exception as e:
            error_occurred = True
            
            # Record error in span
            if span and span.is_recording():
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
            
            # Record error metrics
            record_error(
                error_type=type(e).__name__,
                endpoint=endpoint,
            )
            
            logger.exception(
                f"[ERROR] {method} {endpoint}",
                extra={
                    'frontend_trace_id': frontend_trace_id,
                    'request_id': request_id,
                    'endpoint': endpoint,
                    'method': method,
                    'error_type': type(e).__name__,
                }
            )
            raise
        finally:
            # Calculate duration
            duration = time.perf_counter() - start_time
            duration_ms = duration * 1000
            
            # Decrement active requests
            decrement_active_requests()
            
            # Get status code
            status_code = 500 if error_occurred else (response.status_code if response else 500)
            
            # Add response attributes to span
            if span and span.is_recording():
                span.set_attribute('http.status_code', status_code)
                span.set_attribute('http.response_time_ms', duration_ms)
            
            # Record metrics
            record_request(
                endpoint=endpoint,
                method=method,
                status_code=status_code,
            )
            
            record_request_duration(
                duration_seconds=duration,
                endpoint=endpoint,
                method=method,
            )
            
            # Log request completion with trace context
            log_extra = {
                'frontend_trace_id': frontend_trace_id,
                'request_id': request_id,
                'endpoint': endpoint,
                'method': method,
                'status_code': status_code,
                'duration_ms': round(duration_ms, 2),
            }
            
            if duration > 1.0:  # More than 1 second = slow request
                logger.warning(
                    f"[SLOW] {method} {endpoint} - {status_code} ({duration_ms:.0f}ms)",
                    extra=log_extra
                )
            else:
                logger.debug(
                    f"[DONE] {method} {endpoint} - {status_code} ({duration_ms:.0f}ms)",
                    extra=log_extra
                )
    
    def _get_endpoint(self, request: HttpRequest) -> str:
        """
        Get a normalized endpoint path for metrics grouping.
        Removes specific IDs to group similar endpoints together.
        """
        path = request.path
        
        # Normalize common patterns
        # e.g., /api/companies/123/ -> /api/companies/{id}/
        import re
        
        # UUID pattern
        path = re.sub(
            r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/',
            '/{uuid}/',
            path
        )
        
        # Numeric ID pattern
        path = re.sub(r'/\d+/', '/{id}/', path)
        
        # Stock symbol pattern (6 digits)
        path = re.sub(r'/\d{6}/', '/{symbol}/', path)
        
        return path
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Extract client IP from request, handling proxies."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')


class RequestLoggingMiddleware:
    """
    Simple request logging middleware for debugging.
    Logs all requests with timing information.
    
    Add to MIDDLEWARE in settings.py (optional, for debugging):
        'observability.middleware.RequestLoggingMiddleware',
    """
    
    def __init__(self, get_response: Callable):
        self.get_response = get_response
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        start_time = time.perf_counter()
        
        # Get trace context
        frontend_trace_id = get_frontend_trace_id() or ''
        request_id = get_request_id() or ''
        
        response = self.get_response(request)
        
        duration = time.perf_counter() - start_time
        
        logger.info(
            f"{request.method} {request.path} - {response.status_code} ({duration*1000:.1f}ms)",
            extra={
                'frontend_trace_id': frontend_trace_id,
                'request_id': request_id,
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': duration * 1000,
            }
        )
        
        return response
