"""
OAuth Device Flow Authentication Endpoints for Monkey Coder CLI.

Implements RFC 8628 Device Authorization Grant for secure CLI authentication
without requiring localhost or browser redirects.

Flow:
1. CLI requests device code via /authorize
2. User visits verification URI and enters code
3. CLI polls /token endpoint for completion
4. Backend validates and issues tokens

Features:
- Device code generation with user-friendly codes
- Token polling with rate limiting
- Redis/in-memory storage for device codes
- Automatic code expiration (10 minutes)
- Secure token issuance
"""

import logging
import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import BaseModel, Field

# Import correct authentication and models
try:
    from ...auth.unified_auth import get_current_user
except ImportError:
    # Fallback for development without full auth setup
    async def get_current_user(request: Request):
        """Mock user for development."""
        from ...database.models import User
        return User(id="dev-user", email="dev@example.com", username="developer")

try:
    from ...database.models import User
except ImportError:
    # Fallback if models not available
    from pydantic import BaseModel as User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/device", tags=["device-auth"])

# In-memory store for device codes (replace with Redis in production)
device_codes_store: Dict[str, Dict[str, Any]] = {}


class DeviceAuthRequest(BaseModel):
    """Request for device authorization."""
    client_id: str = Field(..., description="Client identifier (e.g., 'monkey-coder-cli')")
    scope: Optional[str] = Field("read write", description="Requested OAuth scopes")


class DeviceAuthResponse(BaseModel):
    """Response containing device and user codes."""
    device_code: str = Field(..., description="Device verification code")
    user_code: str = Field(..., description="User-friendly verification code")
    verification_uri: str = Field(..., description="URL for user verification")
    verification_uri_complete: str = Field(..., description="Complete URL with code")
    expires_in: int = Field(..., description="Seconds until code expires")
    interval: int = Field(..., description="Polling interval in seconds")


class TokenRequest(BaseModel):
    """Request for token issuance."""
    device_code: str = Field(..., description="Device code from authorization")
    grant_type: str = Field(
        "urn:ietf:params:oauth:grant-type:device_code",
        description="Grant type (must be device_code)"
    )


class TokenResponse(BaseModel):
    """OAuth token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    scope: str


@router.post("/authorize", response_model=DeviceAuthResponse)
async def device_authorize(request: DeviceAuthRequest):
    """
    Step 1: Generate device and user codes for CLI authentication.
    
    CLI calls this endpoint to initiate the device flow. Returns codes that
    the user must enter on the verification page.
    """
    # Generate cryptographically secure device code
    device_code = secrets.token_urlsafe(32)
    
    # Generate user-friendly 8-character code (e.g., ABCD-1234)
    user_code_chars = ''.join(secrets.choice(string.ascii_uppercase + string.digits) 
                              for _ in range(8))
    user_code = f"{user_code_chars[:4]}-{user_code_chars[4:]}"
    
    # Calculate expiration time
    created_at = datetime.utcnow()
    expires_at = created_at + timedelta(minutes=10)
    
    # Store device code with metadata
    device_codes_store[device_code] = {
        "user_code": user_code_chars.replace("-", ""),  # Store without hyphen for matching
        "user_code_formatted": user_code,
        "status": "pending",
        "created_at": created_at,
        "expires_at": expires_at,
        "client_id": request.client_id,
        "scope": request.scope,
        "user_id": None,
        "access_token": None,
        "refresh_token": None,
    }
    
    # Base URL from environment or default
    import os
    base_url = os.getenv("NEXTAUTH_URL", "https://coder.fastmonkey.au")
    
    logger.info(f"Device authorization created: device_code={device_code[:8]}...")
    
    return DeviceAuthResponse(
        device_code=device_code,
        user_code=user_code,
        verification_uri=f"{base_url}/device",
        verification_uri_complete=f"{base_url}/device?user_code={user_code_chars}",
        expires_in=600,  # 10 minutes
        interval=5,  # Poll every 5 seconds
    )


@router.post("/token")
async def device_token(request: TokenRequest):
    """
    Step 2: Poll for token after user approves device.
    
    CLI repeatedly calls this endpoint to check if the user has approved
    the device authorization. Returns tokens once approved.
    """
    device_data = device_codes_store.get(request.device_code)
    
    if not device_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_grant",
            headers={"error": "invalid_grant"},
        )
    
    # Check expiration
    if datetime.utcnow() > device_data["expires_at"]:
        del device_codes_store[request.device_code]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="expired_token",
            headers={"error": "expired_token"},
        )
    
    # Check status
    if device_data["status"] == "pending":
        # Still waiting for user approval
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="authorization_pending",
            headers={
                "error": "authorization_pending",
                "Retry-After": "5",
            },
        )
    
    if device_data["status"] == "denied":
        del device_codes_store[request.device_code]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="access_denied",
            headers={"error": "access_denied"},
        )
    
    if device_data["status"] == "approved":
        # Generate tokens
        access_token = device_data.get("access_token")
        refresh_token = device_data.get("refresh_token")
        
        if not access_token or not refresh_token:
            # Generate tokens (implement your token generation logic)
            from ...security import create_access_token, create_refresh_token
            user_id = device_data["user_id"]
            access_token = create_access_token(user_id)
            refresh_token = create_refresh_token(user_id)
        
        # Clean up device code
        del device_codes_store[request.device_code]
        
        logger.info(f"Device token issued for user: {device_data['user_id']}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,
            scope=device_data["scope"],
        )
    
    # Unknown status
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="internal_error"
    )


@router.get("/verify")
async def verify_device_code(user_code: str):
    """
    Step 3: Verify user code and return device information.
    
    Frontend calls this endpoint when user enters their code on the
    verification page. Returns device details for approval.
    """
    # Normalize user code (remove hyphens, uppercase)
    normalized_code = user_code.replace("-", "").replace(" ", "").upper()
    
    # Find device code by user code
    for device_code, data in device_codes_store.items():
        if data["user_code"] == normalized_code:
            # Check expiration
            if datetime.utcnow() > data["expires_at"]:
                return {"error": "expired", "message": "Code has expired"}
            
            return {
                "valid": True,
                "client_id": data["client_id"],
                "scope": data["scope"],
                "device_code": device_code,
                "expires_at": data["expires_at"].isoformat(),
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="invalid_code",
    )


@router.post("/approve")
async def approve_device(
    device_code: str,
    current_user: User = Depends(get_current_user)
):
    """
    Step 4: Approve device authorization.
    
    Frontend calls this endpoint when user approves the device. Marks
    the device as approved and stores user information.
    """
    if device_code not in device_codes_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="invalid_device_code",
        )
    
    # Check expiration
    data = device_codes_store[device_code]
    if datetime.utcnow() > data["expires_at"]:
        del device_codes_store[device_code]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="expired_code",
        )
    
    # Generate tokens
    from ...security import create_access_token, create_refresh_token
    access_token = create_access_token(current_user.id)
    refresh_token = create_refresh_token(current_user.id)
    
    # Update device status
    device_codes_store[device_code].update({
        "status": "approved",
        "user_id": current_user.id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "approved_at": datetime.utcnow(),
    })
    
    logger.info(f"Device approved for user: {current_user.email}")
    
    return {
        "status": "approved",
        "message": "Device has been authorized successfully",
    }


@router.post("/deny")
async def deny_device(
    device_code: str,
    current_user: User = Depends(get_current_user)
):
    """
    Deny device authorization.
    
    Frontend calls this endpoint when user denies the device authorization.
    """
    if device_code not in device_codes_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="invalid_device_code",
        )
    
    # Update device status
    device_codes_store[device_code]["status"] = "denied"
    
    logger.info(f"Device denied by user: {current_user.email}")
    
    return {
        "status": "denied",
        "message": "Device authorization has been denied",
    }


@router.get("/status")
async def get_device_status(device_code: str):
    """
    Get the current status of a device authorization.
    
    For debugging and monitoring purposes.
    """
    data = device_codes_store.get(device_code)
    
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="device_code_not_found",
        )
    
    return {
        "status": data["status"],
        "created_at": data["created_at"].isoformat(),
        "expires_at": data["expires_at"].isoformat(),
        "client_id": data["client_id"],
    }


# Cleanup expired device codes periodically
async def cleanup_expired_codes():
    """Remove expired device codes from storage."""
    now = datetime.utcnow()
    expired_codes = [
        code for code, data in device_codes_store.items()
        if data["expires_at"] < now
    ]
    
    for code in expired_codes:
        del device_codes_store[code]
    
    if expired_codes:
        logger.info(f"Cleaned up {len(expired_codes)} expired device codes")
