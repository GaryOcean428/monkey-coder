"""
Enhanced Security Middleware for Railway Production Deployment.

This module provides production-ready security middleware with:
- Content Security Policy (CSP) headers optimized for Railway and Google Fonts
- CORS configuration with proper credential handling
- Authentication-aware security headers
- Environment-specific security policies
"""

import logging
import os
from typing import Dict, List, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from ..config.production_config import get_production_config
from ..config.cors import CORS_CONFIG

logger = logging.getLogger(__name__)


class EnhancedSecurityMiddleware(BaseHTTPMiddleware):
    """
    Enhanced security middleware for production deployment.
    
    Provides CSP headers that allow Google Fonts and essential resources
    while maintaining security standards for Railway deployment.
    """
    
    def __init__(self, app, enable_csp: bool = True, enable_cors_headers: bool = True):
        super().__init__(app)
        self.enable_csp = enable_csp
        self.enable_cors_headers = enable_cors_headers
        self.production_config = get_production_config()
        
        # Cache security headers to avoid regenerating on each request
        self._cached_headers = None
        self._last_config_check = None
        
    async def dispatch(self, request: Request, call_next):
        """Process request and add security headers to response."""
        
        # Process the request
        response = await call_next(request)
        
        # Add security headers
        if self.enable_csp:
            self._add_security_headers(response)
            
        # Add CORS headers if needed (for API endpoints)
        if self.enable_cors_headers and request.url.path.startswith("/api/"):
            self._add_cors_headers(request, response)
            
        return response
        
    def _add_security_headers(self, response: Response) -> None:
        """Add security headers to response."""
        # Get cached headers or refresh if needed
        if self._cached_headers is None:
            self._cached_headers = self.production_config.get_security_headers()
            
        # Apply security headers
        for header, value in self._cached_headers.items():
            response.headers[header] = value
            
        # Add custom Railway-specific headers
        self._add_railway_headers(response)
        
    def _add_cors_headers(self, request: Request, response: Response) -> None:
        """Add CORS headers for API endpoints."""
        origin = request.headers.get("origin")
        
        # Check if origin is allowed
        if origin and self._is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            
        # Add other CORS headers
        response.headers["Access-Control-Allow-Methods"] = ", ".join(CORS_CONFIG["allow_methods"])
        response.headers["Access-Control-Allow-Headers"] = ", ".join(CORS_CONFIG["allow_headers"])
        response.headers["Access-Control-Expose-Headers"] = ", ".join(CORS_CONFIG["expose_headers"])
        response.headers["Access-Control-Max-Age"] = str(CORS_CONFIG["max_age"])
        
    def _add_railway_headers(self, response: Response) -> None:
        """Add Railway-specific headers for monitoring and debugging."""
        # Add service identification
        response.headers["X-Service"] = "monkey-coder-core"
        response.headers["X-Version"] = "2.0.0"
        
        # Add Railway environment info if available
        railway_env = os.getenv("RAILWAY_ENVIRONMENT")
        if railway_env:
            response.headers["X-Railway-Environment"] = railway_env
            
    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is in allowed CORS origins."""
        from ..config.cors import get_cors_origins
        allowed_origins = get_cors_origins()
        return origin in allowed_origins


class CSPViolationReporter(BaseHTTPMiddleware):
    """
    Middleware to log CSP violations for debugging and monitoring.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Log CSP violations and forward requests."""
        
        # Check if this is a CSP violation report
        if request.url.path == "/csp-report" and request.method == "POST":
            await self._handle_csp_violation(request)
            return Response(status_code=204)  # No content response
            
        return await call_next(request)
        
    async def _handle_csp_violation(self, request: Request) -> None:
        """Handle CSP violation reports."""
        try:
            violation_data = await request.json()
            
            # Log the violation for monitoring
            logger.warning(
                "CSP Violation reported",
                extra={
                    "csp_violation": violation_data,
                    "user_agent": request.headers.get("user-agent", "unknown"),
                    "ip": request.client.host if request.client else "unknown"
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to process CSP violation report: {e}")


def get_railway_security_config() -> Dict[str, str]:
    """
    Get Railway-specific security configuration from environment variables.
    
    Enhanced to allow Google Fonts and fix CSP issues while maintaining security.
    
    Returns:
        Dict of security configuration values
    """
    return {
        "csp_font_src": os.getenv(
            "CSP_FONT_SRC", 
            "'self' data: https://fonts.gstatic.com https://fonts.googleapis.com"
        ),
        "csp_style_src": os.getenv(
            "CSP_STYLE_SRC",
            "'self' 'unsafe-inline' https://fonts.googleapis.com https://*.fastmonkey.au https://*.railway.app"
        ),
        "csp_default_src": os.getenv(
            "CSP_DEFAULT_SRC",
            "'self' https://*.fastmonkey.au https://*.railway.app blob: data:"
        ),
        "csp_connect_src": os.getenv(
            "CSP_CONNECT_SRC",
            "'self' https://coder.fastmonkey.au wss://coder.fastmonkey.au https://*.railway.app https://*.railway.internal"
        ),
        "csp_script_src": os.getenv(
            "CSP_SCRIPT_SRC",
            "'self' 'unsafe-inline' 'unsafe-eval' https://*.fastmonkey.au https://*.railway.app"
        ),
        "csp_img_src": os.getenv(
            "CSP_IMG_SRC",
            "'self' data: https: blob:"
        ),
        "cors_allow_credentials": os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true",
        "cors_allowed_headers": os.getenv(
            "CORS_ALLOWED_HEADERS",
            "Content-Type,Authorization,X-Requested-With,Accept,Origin,Cache-Control,X-CSRF-Token"
        ),
        "cors_allowed_methods": os.getenv(
            "CORS_ALLOWED_METHODS",
            "GET,POST,PUT,DELETE,OPTIONS,PATCH"
        )
    }


class DynamicCSPMiddleware(BaseHTTPMiddleware):
    """
    Dynamic CSP middleware that can be configured via environment variables.
    
    This allows for real-time CSP adjustments without code changes.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.config = get_railway_security_config()
        
    async def dispatch(self, request: Request, call_next):
        """Apply dynamic CSP headers based on environment configuration."""
        response = await call_next(request)
        
        # Build CSP from environment variables with enhanced Google Fonts support
        csp_directives = [
            f"default-src {self.config['csp_default_src']}",
            f"font-src {self.config['csp_font_src']}",
            f"style-src {self.config['csp_style_src']}",
            f"connect-src {self.config['csp_connect_src']}",
            f"script-src {self.config.get('csp_script_src', \"'self' 'unsafe-inline' 'unsafe-eval'\")}",
            f"img-src {self.config.get('csp_img_src', \"'self' data: https: blob:\")}",
            "media-src 'self' data: blob:",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
            "upgrade-insecure-requests"
        ]
        
        # Add CSP violation reporting endpoint
        environment = os.getenv("RAILWAY_ENVIRONMENT", "development")
        if environment == "production":
            csp_directives.append("report-uri /csp-report")
        
        # Set relaxed CSP for development, strict for production
        if environment == "development":
            # More permissive CSP for development
            response.headers["Content-Security-Policy-Report-Only"] = "; ".join(csp_directives)
        else:
            response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        return response