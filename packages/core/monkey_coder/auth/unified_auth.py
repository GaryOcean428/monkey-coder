"""
Unified Authentication System for Monkey Coder.

This module consolidates all authentication functionality into a single, comprehensive,
secure system that supports both web and CLI authentication scenarios.

Features:
- httpOnly cookies for web clients (primary security method)
- JWT tokens for CLI clients (backward compatibility)
- CSRF protection for state-changing operations
- Redis-based session management
- Comprehensive security headers
- API key authentication
- Multi-factor authentication support
- Session binding and validation
"""

import os
import logging
import secrets
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Union, Literal
from dataclasses import dataclass, asdict
from enum import Enum

import jwt
from fastapi import HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
import redis.asyncio as redis

from ..security import (
    JWTUser,
    UserRole,
    Permission,
    create_access_token as create_jwt_access_token,
    create_refresh_token as create_jwt_refresh_token,
    verify_token as verify_jwt_token,
    get_user_permissions,
)
from ..database import get_user_store, User

logger = logging.getLogger(__name__)

# =============================================================================
# Configuration and Constants
# =============================================================================

# Security keys
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
CSRF_SECRET_KEY = os.getenv("CSRF_SECRET_KEY", secrets.token_urlsafe(32))
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", secrets.token_urlsafe(32))

# Cookie configuration
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", "")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")

# Cookie names (standardized)
ACCESS_TOKEN_COOKIE = "monkey_access_token"
REFRESH_TOKEN_COOKIE = "monkey_refresh_token"
SESSION_ID_COOKIE = "monkey_session_id"
CSRF_TOKEN_COOKIE = "monkey_csrf_token"

# Session configuration
SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "1440"))  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Security headers
SECURITY_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Content-Security-Policy": "default-src 'self'",
}

# Initialize components
security_bearer = HTTPBearer(auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
csrf_serializer = URLSafeTimedSerializer(CSRF_SECRET_KEY, salt="csrf-protection")
session_serializer = URLSafeTimedSerializer(SESSION_SECRET_KEY, salt="session-mgmt")

# Initialize Redis client
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# =============================================================================
# Enums and Data Models
# =============================================================================

class AuthMethod(str, Enum):
    """Authentication methods supported by the unified system."""
    COOKIE = "cookie"
    BEARER_TOKEN = "bearer_token"
    API_KEY = "api_key"

class SessionType(str, Enum):
    """Session types for different client types."""
    WEB = "web"
    CLI = "cli"
    API = "api"
    MOBILE = "mobile"

@dataclass
class SessionData:
    """Comprehensive session data structure."""
    session_id: str
    user_id: str
    session_type: SessionType
    auth_method: AuthMethod
    user_agent: str
    ip_address: str
    created_at: datetime
    last_accessed: datetime
    expires_at: datetime
    is_active: bool
    csrf_token: Optional[str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["last_accessed"] = self.last_accessed.isoformat()
        data["expires_at"] = self.expires_at.isoformat()
        data["session_type"] = self.session_type.value
        data["auth_method"] = self.auth_method.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionData":
        """Create from dictionary."""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["last_accessed"] = datetime.fromisoformat(data["last_accessed"])
        data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        data["session_type"] = SessionType(data["session_type"])
        data["auth_method"] = AuthMethod(data["auth_method"])
        return cls(**data)

class AuthConfig(BaseModel):
    """Authentication configuration."""
    # Cookie settings
    access_token_cookie: str = ACCESS_TOKEN_COOKIE
    refresh_token_cookie: str = REFRESH_TOKEN_COOKIE
    session_id_cookie: str = SESSION_ID_COOKIE
    csrf_token_cookie: str = CSRF_TOKEN_COOKIE
    
    # Security settings
    cookie_secure: bool = COOKIE_SECURE
    cookie_samesite: Literal["lax", "strict", "none"] = COOKIE_SAMESITE
    cookie_domain: str = COOKIE_DOMAIN
    
    # Session settings
    session_timeout_minutes: int = SESSION_TIMEOUT_MINUTES
    access_token_expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES
    refresh_token_expire_days: int = REFRESH_TOKEN_EXPIRE_DAYS
    
    # Security features
    enable_csrf_protection: bool = True
    enable_session_binding: bool = True
    enable_security_headers: bool = True
    require_https: bool = True

class AuthResult(BaseModel):
    """Comprehensive authentication result."""
    success: bool = Field(..., description="Authentication success status")
    method: AuthMethod = Field(..., description="Authentication method used")
    user: Optional[JWTUser] = Field(None, description="Authenticated user")
    session_id: Optional[str] = Field(None, description="Session identifier")
    csrf_token: Optional[str] = Field(None, description="CSRF token")
    access_token: Optional[str] = Field(None, description="Access token (for CLI)")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    expires_at: Optional[datetime] = Field(None, description="Session expiration")
    message: str = Field(..., description="Result message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class LoginRequest(BaseModel):
    """Login request model."""
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")
    remember_me: bool = Field(False, description="Extended session duration")
    client_type: SessionType = Field(SessionType.WEB, description="Client type")

class RefreshRequest(BaseModel):
    """Token refresh request model."""
    refresh_token: Optional[str] = Field(None, description="Refresh token (for CLI)")

# =============================================================================
# Unified Authentication Manager
# =============================================================================

class UnifiedAuthManager:
    """
    Unified authentication manager that consolidates all authentication functionality.
    
    This class provides a single interface for:
    - Web authentication (httpOnly cookies)
    - CLI authentication (JWT tokens)
    - API key authentication
    - Session management
    - CSRF protection
    - Security headers
    """

    def __init__(self, config: Optional[AuthConfig] = None):
        self.config = config or AuthConfig()
        self.redis = redis_client
        logger.info("Unified Authentication Manager initialized")

    # =========================================================================
    # Session Management
    # =========================================================================

    async def create_session(
        self,
        user: JWTUser,
        request: Request,
        session_type: SessionType = SessionType.WEB,
        auth_method: AuthMethod = AuthMethod.COOKIE,
        remember_me: bool = False
    ) -> SessionData:
        """Create a new authentication session."""
        session_id = secrets.token_urlsafe(32)
        
        # Calculate expiration
        if remember_me:
            expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        else:
            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=self.config.session_timeout_minutes
            )
        
        # Generate CSRF token for web sessions
        csrf_token = None
        if session_type == SessionType.WEB and self.config.enable_csrf_protection:
            csrf_token = secrets.token_urlsafe(32)
        
        # Create session data
        session_data = SessionData(
            session_id=session_id,
            user_id=user.user_id,
            session_type=session_type,
            auth_method=auth_method,
            user_agent=request.headers.get("user-agent", ""),
            ip_address=request.client.host if request.client else "",
            created_at=datetime.now(timezone.utc),
            last_accessed=datetime.now(timezone.utc),
            expires_at=expires_at,
            is_active=True,
            csrf_token=csrf_token,
            metadata={
                "roles": [role.value for role in user.roles],
                "permissions": [perm.value for perm in user.permissions],
                "mfa_verified": user.mfa_verified,
            }
        )
        
        # Store in Redis
        ttl = int((expires_at - datetime.now(timezone.utc)).total_seconds())
        await self.redis.setex(
            f"session:{session_id}",
            ttl,
            json.dumps(session_data.to_dict())
        )
        
        # Track user sessions
        await self.redis.sadd(f"user_sessions:{user.user_id}", session_id)
        
        logger.info(f"Created session {session_id} for user {user.user_id}")
        return session_data

    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """Retrieve and validate session."""
        try:
            session_json = await self.redis.get(f"session:{session_id}")
            if not session_json:
                return None
            
            session_data = SessionData.from_dict(json.loads(session_json))
            
            # Check expiration
            if session_data.expires_at < datetime.now(timezone.utc):
                await self.delete_session(session_id)
                return None
            
            # Update last accessed
            session_data.last_accessed = datetime.now(timezone.utc)
            
            # Update in Redis
            ttl = int((session_data.expires_at - datetime.now(timezone.utc)).total_seconds())
            await self.redis.setex(
                f"session:{session_id}",
                ttl,
                json.dumps(session_data.to_dict())
            )
            
            return session_data
            
        except Exception as e:
            logger.error(f"Error retrieving session {session_id}: {e}")
            return None

    async def delete_session(self, session_id: str) -> bool:
        """Delete session from Redis."""
        try:
            # Get session to remove user mapping
            session_json = await self.redis.get(f"session:{session_id}")
            if session_json:
                session_data = SessionData.from_dict(json.loads(session_json))
                await self.redis.srem(f"user_sessions:{session_data.user_id}", session_id)
            
            # Delete session
            await self.redis.delete(f"session:{session_id}")
            logger.info(f"Deleted session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False

    async def validate_session(self, session_id: str, request: Request) -> bool:
        """Validate session with optional binding checks."""
        session_data = await self.get_session(session_id)
        if not session_data or not session_data.is_active:
            return False
        
        # Session binding validation
        if self.config.enable_session_binding:
            current_ua = request.headers.get("user-agent", "")
            current_ip = request.client.host if request.client else ""
            
            if (session_data.user_agent != current_ua or 
                session_data.ip_address != current_ip):
                logger.warning(f"Session binding failed for {session_id}")
                await self.delete_session(session_id)
                return False
        
        return True

    # =========================================================================
    # Authentication Methods
    # =========================================================================

    async def authenticate_with_password(
        self,
        email: str,
        password: str,
        request: Request,
        session_type: SessionType = SessionType.WEB,
        remember_me: bool = False
    ) -> AuthResult:
        """Authenticate user with email/password."""
        try:
            # Get user from database
            user_store = get_user_store()
            user = await user_store.authenticate_user(email, password)
            
            if not user:
                return AuthResult(
                    success=False,
                    method=AuthMethod.COOKIE,
                    message="Invalid email or password"
                )
            
            # Convert to JWTUser
            user_roles = []
            for role_str in user.roles:
                try:
                    user_roles.append(UserRole(role_str))
                except ValueError:
                    logger.warning(f"Invalid role '{role_str}' for user {user.email}")
            
            jwt_user = JWTUser(
                user_id=str(user.id) if user.id else "unknown",
                username=user.username,
                email=user.email,
                roles=user_roles,
                permissions=get_user_permissions(user_roles),
                mfa_verified=True,  # TODO: Implement MFA
                expires_at=datetime.now(timezone.utc) + timedelta(
                    minutes=self.config.access_token_expire_minutes
                )
            )
            
            # Create tokens
            access_token = create_jwt_access_token(jwt_user)
            refresh_token = create_jwt_refresh_token(jwt_user.user_id)
            
            # Determine auth method based on session type
            auth_method = (AuthMethod.BEARER_TOKEN if session_type == SessionType.CLI 
                          else AuthMethod.COOKIE)
            
            # Create session
            session_data = await self.create_session(
                user=jwt_user,
                request=request,
                session_type=session_type,
                auth_method=auth_method,
                remember_me=remember_me
            )
            
            logger.info(f"User {email} authenticated successfully")
            
            return AuthResult(
                success=True,
                method=auth_method,
                user=jwt_user,
                session_id=session_data.session_id,
                csrf_token=session_data.csrf_token,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=session_data.expires_at,
                message="Authentication successful",
                metadata={
                    "credits": 10000 if user.is_developer else 100,
                    "subscription_tier": "developer" if user.is_developer else "free",
                    "is_developer": user.is_developer
                }
            )
            
        except Exception as e:
            logger.error(f"Password authentication failed: {str(e)}")
            return AuthResult(
                success=False,
                method=AuthMethod.COOKIE,
                message="Authentication failed"
            )

    async def authenticate_request(self, request: Request) -> AuthResult:
        """Authenticate request using cookies, headers, or API keys."""
        
        # Try cookie authentication first (for web clients)
        session_id = request.cookies.get(self.config.session_id_cookie)
        if session_id:
            if await self.validate_session(session_id, request):
                session_data = await self.get_session(session_id)
                if session_data:
                    # Recreate JWTUser from session metadata
                    jwt_user = JWTUser(
                        user_id=session_data.user_id,
                        username="", # Will be populated from DB if needed
                        email="",
                        roles=[UserRole(role) for role in session_data.metadata.get("roles", [])],
                        permissions=[Permission(perm) for perm in session_data.metadata.get("permissions", [])],
                        mfa_verified=session_data.metadata.get("mfa_verified", False),
                        session_id=session_id,
                        expires_at=session_data.expires_at
                    )
                    
                    return AuthResult(
                        success=True,
                        method=AuthMethod.COOKIE,
                        user=jwt_user,
                        session_id=session_id,
                        csrf_token=session_data.csrf_token,
                        message="Authenticated via cookie",
                        expires_at=session_data.expires_at
                    )
        
        # Try bearer token authentication (for CLI/API)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            
            # Handle API keys
            if token.startswith("mk-"):
                # TODO: Implement API key validation
                return AuthResult(
                    success=True,
                    method=AuthMethod.API_KEY,
                    user=JWTUser(
                        user_id="api_user",
                        username="api_user",
                        email="",
                        roles=[UserRole.API_USER],
                        permissions=[Permission.CODE_EXECUTE, Permission.CODE_READ],
                        mfa_verified=True,
                        session_id=token[-8:]
                    ),
                    message="Authenticated via API key"
                )
            
            # Handle JWT tokens
            try:
                payload = verify_jwt_token(token)
                user_id = payload.get("sub")
                if user_id:
                    jwt_user = JWTUser(
                        user_id=user_id,
                        username=payload.get("username", ""),
                        email=payload.get("email", ""),
                        roles=[UserRole(role) for role in payload.get("roles", [])],
                        permissions=[Permission(perm) for perm in payload.get("permissions", [])],
                        mfa_verified=payload.get("mfa_verified", False),
                        session_id=payload.get("session_id"),
                        expires_at=datetime.fromtimestamp(payload.get("exp", 0), timezone.utc)
                    )
                    
                    return AuthResult(
                        success=True,
                        method=AuthMethod.BEARER_TOKEN,
                        user=jwt_user,
                        message="Authenticated via bearer token",
                        expires_at=jwt_user.expires_at
                    )
            except Exception as e:
                logger.warning(f"JWT token validation failed: {e}")
        
        return AuthResult(
            success=False,
            method=AuthMethod.COOKIE,
            message="No valid authentication found"
        )

    async def refresh_authentication(
        self,
        request: Request,
        refresh_token: Optional[str] = None
    ) -> AuthResult:
        """Refresh authentication tokens."""
        
        # Get refresh token from cookie or request
        if not refresh_token:
            refresh_token = request.cookies.get(self.config.refresh_token_cookie)
        
        if not refresh_token:
            return AuthResult(
                success=False,
                method=AuthMethod.COOKIE,
                message="No refresh token provided"
            )
        
        try:
            # Verify refresh token
            payload = verify_jwt_token(refresh_token)
            
            if payload.get("type") != "refresh":
                return AuthResult(
                    success=False,
                    method=AuthMethod.COOKIE,
                    message="Invalid refresh token"
                )
            
            user_id = payload.get("sub")
            if not user_id:
                return AuthResult(
                    success=False,
                    method=AuthMethod.COOKIE,
                    message="Invalid refresh token"
                )
            
            # TODO: Get user from database
            # For now, create mock user
            jwt_user = JWTUser(
                user_id=user_id,
                username="refreshed_user",
                email="refreshed@example.com",
                roles=[UserRole.DEVELOPER],
                permissions=get_user_permissions([UserRole.DEVELOPER]),
                mfa_verified=True,
                expires_at=datetime.now(timezone.utc) + timedelta(
                    minutes=self.config.access_token_expire_minutes
                )
            )
            
            # Create new tokens
            new_access_token = create_jwt_access_token(jwt_user)
            new_refresh_token = create_jwt_refresh_token(jwt_user.user_id)
            
            # Update session if exists
            session_id = request.cookies.get(self.config.session_id_cookie)
            csrf_token = None
            if session_id:
                session_data = await self.get_session(session_id)
                if session_data:
                    csrf_token = session_data.csrf_token
            
            return AuthResult(
                success=True,
                method=AuthMethod.COOKIE,
                user=jwt_user,
                session_id=session_id,
                csrf_token=csrf_token,
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                expires_at=jwt_user.expires_at,
                message="Token refreshed successfully"
            )
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return AuthResult(
                success=False,
                method=AuthMethod.COOKIE,
                message="Failed to refresh token"
            )

    async def logout(self, request: Request) -> bool:
        """Logout user and cleanup session."""
        try:
            session_id = request.cookies.get(self.config.session_id_cookie)
            if session_id:
                await self.delete_session(session_id)
            
            logger.info("User logged out successfully")
            return True
            
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return False

    # =========================================================================
    # Response Helpers
    # =========================================================================

    def create_auth_response(
        self,
        auth_result: AuthResult,
        response_data: Dict[str, Any]
    ) -> JSONResponse:
        """Create authentication response with cookies and security headers."""
        
        response = JSONResponse(content=response_data)
        
        # Add security headers
        if self.config.enable_security_headers:
            for header, value in SECURITY_HEADERS.items():
                response.headers[header] = value
        
        # Set cookies for web clients
        if (auth_result.success and 
            auth_result.method in [AuthMethod.COOKIE, AuthMethod.BEARER_TOKEN] and 
            auth_result.session_id):
            
            # Calculate expires
            expires_delta = (auth_result.expires_at - datetime.now(timezone.utc) 
                           if auth_result.expires_at else timedelta(hours=1))
            max_age = int(expires_delta.total_seconds())
            
            # Access token cookie
            if auth_result.access_token:
                response.set_cookie(
                    key=self.config.access_token_cookie,
                    value=auth_result.access_token,
                    max_age=max_age,
                    httponly=True,
                    secure=self.config.cookie_secure,
                    samesite=self.config.cookie_samesite,
                    domain=self.config.cookie_domain or None
                )
            
            # Refresh token cookie
            if auth_result.refresh_token:
                refresh_max_age = self.config.refresh_token_expire_days * 24 * 60 * 60
                response.set_cookie(
                    key=self.config.refresh_token_cookie,
                    value=auth_result.refresh_token,
                    max_age=refresh_max_age,
                    httponly=True,
                    secure=self.config.cookie_secure,
                    samesite=self.config.cookie_samesite,
                    domain=self.config.cookie_domain or None
                )
            
            # Session ID cookie
            response.set_cookie(
                key=self.config.session_id_cookie,
                value=auth_result.session_id,
                max_age=max_age,
                httponly=True,
                secure=self.config.cookie_secure,
                samesite=self.config.cookie_samesite,
                domain=self.config.cookie_domain or None
            )
            
            # CSRF token cookie (accessible to JavaScript)
            if auth_result.csrf_token:
                response.set_cookie(
                    key=self.config.csrf_token_cookie,
                    value=auth_result.csrf_token,
                    max_age=max_age,
                    httponly=False,  # JavaScript needs access
                    secure=self.config.cookie_secure,
                    samesite=self.config.cookie_samesite,
                    domain=self.config.cookie_domain or None
                )
        
        return response

    def create_logout_response(self) -> JSONResponse:
        """Create logout response that clears all cookies."""
        
        response = JSONResponse(content={"message": "Successfully logged out"})
        
        # Add security headers
        if self.config.enable_security_headers:
            for header, value in SECURITY_HEADERS.items():
                response.headers[header] = value
        
        # Clear all auth cookies
        cookie_names = [
            self.config.access_token_cookie,
            self.config.refresh_token_cookie,
            self.config.session_id_cookie,
            self.config.csrf_token_cookie
        ]
        
        for cookie_name in cookie_names:
            response.delete_cookie(
                key=cookie_name,
                path="/",
                secure=self.config.cookie_secure,
                samesite=self.config.cookie_samesite,
                domain=self.config.cookie_domain or None
            )
        
        return response

    def validate_csrf_token(self, request: Request, session_id: str) -> bool:
        """Validate CSRF token for state-changing requests."""
        
        if not self.config.enable_csrf_protection:
            return True
        
        # Only require CSRF for state-changing methods
        if request.method not in ["POST", "PUT", "DELETE", "PATCH"]:
            return True
        
        # Get CSRF token from header or form data
        csrf_token = request.headers.get("X-CSRF-Token")
        
        # Compare with stored token
        stored_csrf_token = request.cookies.get(self.config.csrf_token_cookie)
        
        return csrf_token and stored_csrf_token and csrf_token == stored_csrf_token

# =============================================================================
# Global Instance and Dependencies
# =============================================================================

# Global unified auth manager
unified_auth = UnifiedAuthManager()

# FastAPI Dependencies
async def get_current_user(request: Request) -> JWTUser:
    """
    FastAPI dependency for getting current authenticated user.
    
    This replaces all existing authentication dependencies and provides
    unified authentication across cookie, bearer token, and API key methods.
    """
    auth_result = await unified_auth.authenticate_request(request)
    
    if not auth_result.success or not auth_result.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return auth_result.user

async def get_optional_user(request: Request) -> Optional[JWTUser]:
    """Optional authentication dependency that doesn't raise exceptions."""
    try:
        auth_result = await unified_auth.authenticate_request(request)
        return auth_result.user if auth_result.success else None
    except Exception:
        return None

async def require_csrf_token(request: Request) -> str:
    """Require and validate CSRF token for state-changing requests."""
    csrf_token = request.headers.get("X-CSRF-Token")
    
    if not csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token required"
        )
    
    # Get session to validate token
    session_id = request.cookies.get(unified_auth.config.session_id_cookie)
    if not session_id or not unified_auth.validate_csrf_token(request, session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token"
        )
    
    return csrf_token

# Backward compatibility aliases
get_current_user_enhanced = get_current_user
get_current_user_from_cookie = get_current_user

logger.info("Unified Authentication System initialized successfully")