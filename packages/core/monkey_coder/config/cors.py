"""
CORS Configuration for FastAPI Backend
Supports both local development and production deployment
"""

from typing import List

# Define allowed origins based on environment
def get_cors_origins() -> List[str]:
    """Get list of allowed CORS origins based on deployment environment."""
    import os
    
    origins = [
        # Local development
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5675",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5675",
        
        # Production domains
        "https://coder.fastmonkey.au",
        "https://monkey-coder.up.railway.app",
    ]
    
    # Add custom origin from environment if provided
    custom_origin = os.getenv("CORS_ORIGIN")
    if custom_origin:
        origins.append(custom_origin)
    
    return origins

# CORS middleware configuration
CORS_CONFIG = {
    "allow_origins": get_cors_origins(),
    "allow_credentials": True,  # Required for cookies
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": [
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRF-Token",
    ],
    "expose_headers": [
        "X-Total-Count",
        "X-Page-Count",
        "X-Current-Page",
        "X-Rate-Limit-Remaining",
    ],
    "max_age": 3600,  # Cache preflight requests for 1 hour
}

# Security headers configuration
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
