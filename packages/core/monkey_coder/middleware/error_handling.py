"""
Production Error Handling Middleware

Enhanced error handling for Railway deployment with:
- Structured error responses
- Security-aware error sanitization  
- Performance monitoring integration
- Request correlation IDs
"""

import os
import json
import time
import uuid
import traceback
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Production error handling middleware for Railway deployment.
    
    Provides comprehensive error handling with:
    - Request correlation tracking
    - Performance monitoring
    - Security-aware error responses
    - Sentry integration for error tracking
    """
    
    def __init__(self, app: ASGIApp, 
                 enable_debug: bool = False,
                 enable_performance_logging: bool = True,
                 enable_sentry: bool = True):
        super().__init__(app)
        self.enable_debug = enable_debug or os.getenv('DEBUG', 'false').lower() == 'true'
        self.enable_performance_logging = enable_performance_logging
        self.enable_sentry = enable_sentry and SENTRY_AVAILABLE
        self.environment = os.getenv('ENVIRONMENT', 'development')
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with error handling and performance monitoring."""
        # Generate correlation ID for request tracking
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        # Add correlation ID to response headers
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate request duration
            duration = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Add performance and correlation headers
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Response-Time"] = f"{duration:.2f}ms"
            
            # Log performance if enabled
            if self.enable_performance_logging:
                self._log_request_performance(
                    request, response, duration, correlation_id
                )
            
            return response
            
        except HTTPException as http_exc:
            # Handle HTTP exceptions (4xx, 5xx)
            duration = (time.time() - start_time) * 1000
            return await self._handle_http_exception(
                request, http_exc, duration, correlation_id
            )
            
        except Exception as exc:
            # Handle unexpected exceptions
            duration = (time.time() - start_time) * 1000
            return await self._handle_unexpected_exception(
                request, exc, duration, correlation_id
            )
    
    def _log_request_performance(self, request: Request, response: Response,
                               duration: float, correlation_id: str):
        """Log request performance metrics."""
        try:
            from ..config.logging_config import get_performance_logger
            
            perf_logger = get_performance_logger()
            perf_logger.log_request_performance(
                endpoint=str(request.url.path),
                method=request.method,
                execution_time=duration,
                status_code=response.status_code,
                request_id=correlation_id
            )
        except Exception as e:
            logger.warning(f"Failed to log performance: {e}")
    
    async def _handle_http_exception(self, request: Request, 
                                   http_exc: HTTPException,
                                   duration: float, 
                                   correlation_id: str) -> JSONResponse:
        """Handle HTTP exceptions with structured response."""
        
        # Log the exception
        logger.warning(
            f"HTTP exception {http_exc.status_code}: {http_exc.detail}",
            extra={
                'correlation_id': correlation_id,
                'endpoint': str(request.url.path),
                'method': request.method,
                'status_code': http_exc.status_code,
                'duration_ms': duration
            }
        )
        
        # Create structured error response
        error_response = self._create_error_response(
            status_code=http_exc.status_code,
            error_type="http_exception",
            message=http_exc.detail,
            correlation_id=correlation_id,
            request=request
        )
        
        return JSONResponse(
            status_code=http_exc.status_code,
            content=error_response,
            headers={
                "X-Correlation-ID": correlation_id,
                "X-Response-Time": f"{duration:.2f}ms"
            }
        )
    
    async def _handle_unexpected_exception(self, request: Request, 
                                         exc: Exception,
                                         duration: float,
                                         correlation_id: str) -> JSONResponse:
        """Handle unexpected exceptions with security-aware responses."""
        
        # Log the full exception details
        logger.error(
            f"Unexpected exception: {str(exc)}",
            exc_info=True,
            extra={
                'correlation_id': correlation_id,
                'endpoint': str(request.url.path),
                'method': request.method,
                'duration_ms': duration,
                'exception_type': type(exc).__name__
            }
        )
        
        # Send to Sentry if enabled
        if self.enable_sentry:
            try:
                with sentry_sdk.push_scope() as scope:
                    scope.set_tag("correlation_id", correlation_id)
                    scope.set_tag("endpoint", str(request.url.path))
                    scope.set_tag("method", request.method)
                    scope.set_context("request", {
                        "url": str(request.url),
                        "headers": dict(request.headers),
                        "method": request.method
                    })
                    sentry_sdk.capture_exception(exc)
            except Exception as sentry_exc:
                logger.warning(f"Failed to send exception to Sentry: {sentry_exc}")
        
        # Determine response details based on environment
        if self.environment == 'production':
            # Sanitized response for production
            status_code = 500
            error_type = "internal_error"
            message = "An internal error occurred. Please try again later."
            debug_info = None
        else:
            # Detailed response for development
            status_code = 500
            error_type = type(exc).__name__
            message = str(exc)
            debug_info = {
                "traceback": traceback.format_exc(),
                "exception_type": type(exc).__name__
            }
        
        # Create structured error response
        error_response = self._create_error_response(
            status_code=status_code,
            error_type=error_type,
            message=message,
            correlation_id=correlation_id,
            request=request,
            debug_info=debug_info
        )
        
        return JSONResponse(
            status_code=status_code,
            content=error_response,
            headers={
                "X-Correlation-ID": correlation_id,
                "X-Response-Time": f"{duration:.2f}ms"
            }
        )
    
    def _create_error_response(self, status_code: int, error_type: str,
                             message: str, correlation_id: str,
                             request: Request, debug_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Create structured error response."""
        
        error_response = {
            "error": {
                "type": error_type,
                "message": message,
                "status_code": status_code,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "correlation_id": correlation_id,
                "request": {
                    "method": request.method,
                    "path": str(request.url.path),
                    "query_params": dict(request.query_params) if request.query_params else None
                }
            }
        }
        
        # Add debug information if provided and enabled
        if debug_info and (self.enable_debug or self.environment != 'production'):
            error_response["debug"] = debug_info
        
        # Add helpful links for common errors
        if status_code == 401:
            error_response["help"] = {
                "message": "Authentication required",
                "documentation": "/docs#authentication"
            }
        elif status_code == 403:
            error_response["help"] = {
                "message": "Insufficient permissions",
                "documentation": "/docs#authorization"
            }
        elif status_code == 429:
            error_response["help"] = {
                "message": "Rate limit exceeded",
                "documentation": "/docs#rate-limiting"
            }
        
        return error_response


class SecurityErrorSanitizer:
    """
    Utility for sanitizing error messages to prevent information disclosure.
    """
    
    SENSITIVE_PATTERNS = [
        r'password["\s]*[:=]["\s]*[^\s"]+',
        r'api[_-]?key["\s]*[:=]["\s]*[^\s"]+',
        r'secret["\s]*[:=]["\s]*[^\s"]+',
        r'token["\s]*[:=]["\s]*[^\s"]+',
        r'database[_-]?url["\s]*[:=]["\s]*[^\s"]+',
    ]
    
    @classmethod
    def sanitize_message(cls, message: str) -> str:
        """Sanitize error message by removing sensitive information."""
        import re
        
        sanitized = message
        
        # Replace sensitive patterns
        for pattern in cls.SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)
        
        # Replace file paths that might contain sensitive info
        sanitized = re.sub(r'/[^/\s]+/[^/\s]+/[^/\s]+', '[PATH]', sanitized)
        
        return sanitized
    
    @classmethod
    def sanitize_traceback(cls, tb: str) -> str:
        """Sanitize traceback by removing sensitive file paths and data."""
        lines = tb.split('\n')
        sanitized_lines = []
        
        for line in lines:
            # Sanitize file paths
            if 'File "' in line:
                line = re.sub(r'File "[^"]*"', 'File "[PATH]"', line)
            
            # Sanitize sensitive data
            line = cls.sanitize_message(line)
            sanitized_lines.append(line)
        
        return '\n'.join(sanitized_lines)


def create_production_error_handler() -> ErrorHandlingMiddleware:
    """
    Create production-ready error handling middleware.
    
    Configures middleware with appropriate settings for Railway deployment.
    """
    environment = os.getenv('ENVIRONMENT', 'development')
    enable_debug = environment != 'production'
    
    return ErrorHandlingMiddleware(
        app=None,  # Will be set by FastAPI
        enable_debug=enable_debug,
        enable_performance_logging=True,
        enable_sentry=True
    )


# Custom exception classes for specific error scenarios
class DatabaseConnectionError(Exception):
    """Raised when database connection fails."""
    pass


class AIProviderError(Exception):
    """Raised when AI provider API fails."""
    pass


class RateLimitExceededError(Exception):
    """Raised when rate limit is exceeded."""
    pass


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass