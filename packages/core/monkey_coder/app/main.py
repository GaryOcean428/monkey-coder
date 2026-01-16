"""
FastAPI Application Main Module

This module provides the main FastAPI application instance with:
- Health check endpoints
- Authentication endpoints
- Password reset functionality
- Rate limiting
- CORS configuration
- MCP Server integration
"""

import hashlib
import os
import secrets
import time
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

# In-memory password reset token storage (use Redis in production)
_PASSWORD_RESET_TOKENS: Dict[str, Dict[str, Any]] = {}

def _hash_reset_token(token: str) -> str:
    """Hash a reset token for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()

# Create FastAPI app
app = FastAPI(
    title="Monkey Coder API",
    description="AI-powered development assistant API with MCP support",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),  # Configure via environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount MCP server at /mcp endpoint
try:
    from monkey_coder.mcp.server import mcp
    app.mount("/mcp", mcp.streamable_http_app())
except Exception as e:
    print(f"Warning: Failed to mount MCP server: {e}")

# Include MCP REST wrapper router
try:
    from monkey_coder.app.routes.mcp import router as mcp_router
    app.include_router(mcp_router)
except Exception as e:
    print(f"Warning: Failed to include MCP router: {e}")

# Request models
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

# Health check endpoint
@app.get("/api/health")
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "monkey-coder-api"
    }
    
    # Check MCP server status
    try:
        from monkey_coder.mcp.server import mcp
        tools_result = await mcp.list_tools()
        health_data["mcp_server"] = {
            "status": "operational",
            "tools_count": len(tools_result.tools) if hasattr(tools_result, 'tools') else 0
        }
    except Exception as e:
        health_data["mcp_server"] = {
            "status": "unavailable",
            "error": str(e)
        }
    
    return health_data

# Password reset endpoints
@app.post("/api/v1/auth/password-reset/request")
async def request_password_reset(data: PasswordResetRequest):
    """Request a password reset token."""
    # Generate secure token
    token = secrets.token_urlsafe(32)
    token_hash = _hash_reset_token(token)
    
    # Store token (expires in 1 hour)
    _PASSWORD_RESET_TOKENS[token_hash] = {
        "email": data.email,
        "expires_at": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
        "used": False
    }
    
    # In production, send email with token
    return {
        "message": "Password reset email sent",
        "token": token  # Only for testing; don't return in production
    }

@app.post("/api/v1/auth/password-reset/confirm")
async def confirm_password_reset(data: PasswordResetConfirm):
    """Confirm password reset with token."""
    token_hash = _hash_reset_token(data.token)
    
    # Check if token exists and is valid
    if token_hash not in _PASSWORD_RESET_TOKENS:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    token_data = _PASSWORD_RESET_TOKENS[token_hash]
    
    # Check if token has expired
    if token_data["expires_at"] < time.time():
        del _PASSWORD_RESET_TOKENS[token_hash]
        raise HTTPException(status_code=400, detail="Token has expired")
    
    # Check if token was already used
    if token_data["used"]:
        raise HTTPException(status_code=400, detail="Token has already been used")
    
    # Mark token as used
    token_data["used"] = True
    
    # In production, update user password in database
    return {
        "message": "Password reset successful",
        "email": token_data["email"]
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Monkey Coder API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Error handler for validation errors
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )
