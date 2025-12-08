"""
OpenTelemetry Django Middleware

Provides automatic instrumentation for Django requests:
- Request/response tracing with detailed attributes
- Metrics collection (latency, status codes, etc.)
- Error tracking and logging
"""

import time
import logging
from typing import Callable

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


class OpenTelemetryMiddleware:
    """
    Middleware that provides OpenTelemetry observability for all requests.
    
    Add to MIDDLEWARE in settings.py:
        'observability.middleware.OpenTelemetryMiddleware',
    """
    
    def __init__(self, get_response: Callable):
        self.get_response = get_response
        self.tracer = get_tracer('mem_dashboard.middleware')
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Start timing
        start_time = time.perf_counter()
        
        # Track active requests
        increment_active_requests()
        
        # Extract request info
        endpoint = self._get_endpoint(request)
        method = request.method
        
        # Get or create span from Django instrumentation
        span = trace.get_current_span()
        
        # Add custom attributes to span
        if span and span.is_recording():
            span.set_attribute('http.endpoint', endpoint)
            span.set_attribute('http.user_agent', request.META.get('HTTP_USER_AGENT', ''))
            span.set_attribute('http.client_ip', self._get_client_ip(request))
            
            # Add query parameters (be careful with sensitive data)
            if request.GET:
                span.set_attribute('http.query_params_count', len(request.GET))
        
        response = None
        error_occurred = False
        
        try:
            response = self.get_response(request)
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
                f"Request error: {method} {endpoint}",
                extra={
                    'endpoint': endpoint,
                    'method': method,
                    'error_type': type(e).__name__,
                }
            )
            raise
        finally:
            # Calculate duration
            duration = time.perf_counter() - start_time
            
            # Decrement active requests
            decrement_active_requests()
            
            # Get status code
            status_code = 500 if error_occurred else (response.status_code if response else 500)
            
            # Add response attributes to span
            if span and span.is_recording():
                span.set_attribute('http.status_code', status_code)
                span.set_attribute('http.response_time_ms', duration * 1000)
            
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
            
            # Log slow requests
            if duration > 1.0:  # More than 1 second
                logger.warning(
                    f"Slow request: {method} {endpoint} took {duration:.2f}s",
                    extra={
                        'endpoint': endpoint,
                        'method': method,
                        'duration_seconds': duration,
                        'status_code': status_code,
                    }
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
        
        response = self.get_response(request)
        
        duration = time.perf_counter() - start_time
        
        logger.info(
            f"{request.method} {request.path} - {response.status_code} ({duration*1000:.1f}ms)",
            extra={
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': duration * 1000,
            }
        )
        
        return response

