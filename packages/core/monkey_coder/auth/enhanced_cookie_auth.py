"""
Enhanced authentication system with unified cookie and token support.

This module provides a comprehensive authentication solution that:
1. Uses httpOnly cookies as the primary authentication method
2. Maintains backward compatibility with Authorization headers
3. Provides secure token refresh and session management
4. Implements proper security headers and CORS configuration
5. Supports both web and CLI authentication scenarios
6. (Planned) Bridge for external identity providers (Google/GitHub) via NextAuth
    - Not yet implemented: no OAuth callback consumption / account linking logic present.
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Literal
from dataclasses import dataclass
from enum import Enum

from fastapi import HTTPException, status, Request, Response
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

from ..security import (
    JWTUser,
    UserRole,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_user_permissions,
)
from ..database import get_user_store, User

logger = logging.getLogger(__name__)

# Enhanced cookie configuration
COOKIE_ACCESS_TOKEN_NAME = "monkey_access_token"
COOKIE_REFRESH_TOKEN_NAME = "monkey_refresh_token"
COOKIE_SESSION_ID_NAME = "monkey_session_id"
COOKIE_CSRF_TOKEN_NAME = "monkey_csrf_token"

# Security configuration
COOKIE_MAX_AGE_DAYS = 30
COOKIE_SECURE = True  # HTTPS only
COOKIE_HTTPONLY = True  # Prevent JavaScript access
COOKIE_SAMESITE = "lax"  # CSRF protection
CSRF_TOKEN_LENGTH = 32

# Session configuration
SESSION_TIMEOUT_MINUTES = 1440  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30

class AuthMethod(Enum):
    """Authentication method enumeration."""
    COOKIE = "cookie"
    HEADER = "header"
    API_KEY = "api_key"

@dataclass
class AuthConfig:
    """Configuration for enhanced authentication."""

    # Cookie settings
    access_token_name: str = COOKIE_ACCESS_TOKEN_NAME
    refresh_token_name: str = COOKIE_REFRESH_TOKEN_NAME
    session_id_name: str = COOKIE_SESSION_ID_NAME
    csrf_token_name: str = COOKIE_CSRF_TOKEN_NAME

    # Security settings
    secure: bool = COOKIE_SECURE
    httponly: bool = COOKIE_HTTPONLY
    samesite: Literal["lax", "strict", "none"] = COOKIE_SAMESITE
    max_age_days: int = COOKIE_MAX_AGE_DAYS

    # Session settings
    session_timeout_minutes: int = SESSION_TIMEOUT_MINUTES
    refresh_token_expire_days: int = REFRESH_TOKEN_EXPIRE_DAYS

    # Security features
    enable_csrf_protection: bool = True
    enable_session_binding: bool = True
    enable_token_refresh: bool = True

class AuthResult(BaseModel):
    """Authentication result model."""

    success: bool = Field(..., description="Authentication success status")
    method: AuthMethod = Field(..., description="Authentication method used")
    user: Optional[JWTUser] = Field(None, description="Authenticated user")
    session_id: Optional[str] = Field(None, description="Session identifier")
    csrf_token: Optional[str] = Field(None, description="CSRF token for web clients")
    access_token: Optional[str] = Field(None, description="Access token (for CLI)")
    refresh_token: Optional[str] = Field(None, description="Refresh token (for CLI)")
    expires_at: Optional[datetime] = Field(None, description="Token expiration time")
    message: str = Field(..., description="Authentication result message")

class EnhancedAuthManager:
    """Enhanced authentication manager supporting multiple auth methods."""

    def __init__(self, config: Optional[AuthConfig] = None):
        self.config = config or AuthConfig()
        self.security = HTTPBearer(auto_error=False)

        # Session storage (in production, use Redis or similar)
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def generate_session_id(self) -> str:
        """Generate a secure session ID."""
        return secrets.token_urlsafe(32)

    def generate_csrf_token(self) -> str:
        """Generate a CSRF token."""
        return secrets.token_urlsafe(CSRF_TOKEN_LENGTH)

    def create_session(self, user_id: str, user_agent: str, ip_address: str) -> str:
        """Create a new authentication session."""
        session_id = self.generate_session_id()
        csrf_token = self.generate_csrf_token() if self.config.enable_csrf_protection else None

        session_data = {
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc),
            "last_activity": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=self.config.session_timeout_minutes),
            "user_agent": user_agent,
            "ip_address": ip_address,
            "csrf_token": csrf_token,
            "is_active": True,
        }

        self._sessions[session_id] = session_data
        logger.info(f"Created new session {session_id} for user {user_id}")

        return session_id

    def validate_session(self, session_id: str, request: Request) -> bool:
        """Validate a session and update last activity."""
        if session_id not in self._sessions:
            return False

        session = self._sessions[session_id]

        # Check if session is expired
        if datetime.now(timezone.utc) > session["expires_at"]:
            del self._sessions[session_id]
            logger.info(f"Session {session_id} expired")
            return False

        # Check if session is active
        if not session["is_active"]:
            return False

        # Update last activity
        session["last_activity"] = datetime.now(timezone.utc)

        # Optional: Validate user agent and IP for session binding
        if self.config.enable_session_binding:
            current_user_agent = request.headers.get("user-agent", "")
            current_ip = request.client.host if request.client else ""

            if (session["user_agent"] != current_user_agent or
                session["ip_address"] != current_ip):
                logger.warning(f"Session binding failed for {session_id}")
                return False

        return True

    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session."""
        if session_id in self._sessions:
            self._sessions[session_id]["is_active"] = False
            del self._sessions[session_id]
            logger.info(f"Invalidated session {session_id}")
            return True
        return False

    def set_auth_cookies(
        self,
        response: Response,
        access_token: str,
        refresh_token: str,
        session_id: str,
        csrf_token: Optional[str] = None
    ) -> Response:
        """Set authentication cookies in the HTTP response."""

        # Calculate expiration
        expires_at = datetime.now(timezone.utc) + timedelta(days=self.config.max_age_days)
        max_age_seconds = self.config.max_age_days * 24 * 60 * 60

        # Set access token cookie
        response.set_cookie(
            key=self.config.access_token_name,
            value=access_token,
            max_age=max_age_seconds,
            expires=expires_at,
            path="/",
            secure=self.config.secure,
            httponly=self.config.httponly,
            samesite=self.config.samesite,
        )

        # Set refresh token cookie
        response.set_cookie(
            key=self.config.refresh_token_name,
            value=refresh_token,
            max_age=max_age_seconds,
            expires=expires_at,
            path="/",
            secure=self.config.secure,
            httponly=self.config.httponly,
            samesite=self.config.samesite,
        )

        # Set session ID cookie
        response.set_cookie(
            key=self.config.session_id_name,
            value=session_id,
            max_age=max_age_seconds,
            expires=expires_at,
            path="/",
            secure=self.config.secure,
            httponly=self.config.httponly,
            samesite=self.config.samesite,
        )

        # Set CSRF token cookie (not httpOnly so JavaScript can read it)
        if csrf_token and self.config.enable_csrf_protection:
            response.set_cookie(
                key=self.config.csrf_token_name,
                value=csrf_token,
                max_age=max_age_seconds,
                expires=expires_at,
                path="/",
                secure=self.config.secure,
                httponly=False,  # Allow JavaScript access
                samesite=self.config.samesite,
            )

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        logger.info("Authentication cookies set successfully")
        return response

    def clear_auth_cookies(self, response: Response) -> Response:
        """Clear authentication cookies from the HTTP response."""

        cookies_to_clear = [
            self.config.access_token_name,
            self.config.refresh_token_name,
            self.config.session_id_name,
        ]

        if self.config.enable_csrf_protection:
            cookies_to_clear.append(self.config.csrf_token_name)

        for cookie_name in cookies_to_clear:
            response.delete_cookie(
                key=cookie_name,
                path="/",
                secure=self.config.secure,
                httponly=self.config.httponly,
                samesite=self.config.samesite,
            )

        logger.info("Authentication cookies cleared")
        return response

    def get_token_from_cookie(self, request: Request, token_name: str) -> Optional[str]:
        """Extract token from HTTP cookies."""
        return request.cookies.get(token_name)

    def get_token_from_header(self, request: Request) -> Optional[str]:
        """Extract token from Authorization header."""
        try:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                return auth_header[7:]  # Remove "Bearer " prefix
        except Exception:
            pass
        return None

    async def authenticate_user(
        self,
        email: str,
        password: str,
        request: Request,
        for_cli: bool = False
    ) -> AuthResult:
        """
        Authenticate user with email and password.

        Args:
            email: User email address
            password: User password
            request: FastAPI request object
            for_cli: Whether this authentication is for CLI usage

        Returns:
            AuthResult with authentication details
        """
        try:
            # Authenticate user against database
            user = await get_user_store().authenticate_user(email, password)

            if not user:
                return AuthResult(
                    success=False,
                    method=AuthMethod.COOKIE,
                    user=None,
                    session_id=None,
                    csrf_token=None,
                    access_token=None,
                    refresh_token=None,
                    expires_at=None,
                    message="Invalid email or password"
                )

            # --- Legacy password hash migration (sha256 -> bcrypt) ---
            # If user.password_hash looks like a raw hex SHA256 (64 hex chars, no bcrypt prefix),
            # verify by recomputing and then upgrade to bcrypt via security.hash_password.
            try:
                from ..security import hash_password
                import re
                import hashlib
                raw_hash = user.password_hash
                if raw_hash and re.fullmatch(r"[a-fA-F0-9]{64}", raw_hash):
                    if hashlib.sha256(password.encode()).hexdigest() == raw_hash:
                        # Rehash with bcrypt and update user record
                        new_hash = hash_password(password)
                        await user.update(password_hash=new_hash)
                        logger.info(f"Upgraded legacy SHA256 password hash for user {user.email}")
                # else assume already bcrypt / supported by passlib
            except Exception as mig_e:  # pragma: no cover - non-critical path
                logger.warning(f"Password migration check failed for {getattr(user,'email','?')}: {mig_e}")

            # Convert database user roles to UserRole enums
            user_roles = []
            for role_str in user.roles:
                try:
                    user_roles.append(UserRole(role_str))
                except ValueError:
                    logger.warning(f"Invalid role '{role_str}' for user {user.email}")

            # Create JWT user
            jwt_user = JWTUser(
                user_id=str(user.id) if user.id else "unknown_user",
                username=user.username,
                email=user.email,
                roles=user_roles,
                permissions=get_user_permissions(user_roles),
                mfa_verified=True,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
            )

            # Create tokens
            access_token = create_access_token(jwt_user)
            refresh_token = create_refresh_token(jwt_user.user_id)

            # For web clients, create session and cookies
            if not for_cli:
                session_id = self.create_session(
                    user_id=jwt_user.user_id,
                    user_agent=request.headers.get("user-agent", ""),
                    ip_address=request.client.host if request.client else ""
                )

                csrf_token = self.generate_csrf_token() if self.config.enable_csrf_protection else None

                return AuthResult(
                    success=True,
                    method=AuthMethod.COOKIE,
                    user=jwt_user,
                    session_id=session_id,
                    csrf_token=csrf_token,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    expires_at=jwt_user.expires_at,
                    message="Authentication successful"
                )
            else:
                # For CLI, return tokens directly
                return AuthResult(
                    success=True,
                    method=AuthMethod.HEADER,
                    user=jwt_user,
                    session_id=None,
                    csrf_token=None,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    expires_at=jwt_user.expires_at,
                    message="Authentication successful"
                )

        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return AuthResult(
                success=False,
                method=AuthMethod.COOKIE,
                user=None,
                session_id=None,
                csrf_token=None,
                access_token=None,
                refresh_token=None,
                expires_at=None,
                message="Authentication failed"
            )

    async def create_user(
        self,
        username: str,
        name: str,
        email: str,
        password: str,
        plan: str = "free"
    ) -> AuthResult:
        """
        Create a new user account and return authentication tokens.

        Args:
            username: Unique username for the account
            name: Full name of the user
            email: User email address
            password: User password
            plan: Subscription plan (free, pro, enterprise)

        Returns:
            AuthResult: Authentication result with tokens and user info

        Raises:
            Exception: If user creation fails
        """
        try:
            from ..database.models import User
            # Use centralized secure password hashing (bcrypt via passlib) instead of insecure sha256.
            # NOTE: Legacy accounts created before this change may still have a raw sha256 hash; migration is handled
            # during authentication in authenticate_user (rehash path to be added separately if needed).
            from ..security import hash_password

            password_hash = hash_password(password)

            # Create user in database
            new_user = await User.create(
                username=username,
                email=email,
                full_name=name,  # Use full_name instead of name
                password_hash=password_hash,
                is_developer=(plan in ["pro", "enterprise"]),
                subscription_plan=plan  # Use subscription_plan instead of subscription_tier
            )

            if not new_user:
                return AuthResult(
                    success=False,
                    method=AuthMethod.COOKIE,
                    user=None,
                    session_id=None,
                    csrf_token=None,
                    access_token=None,
                    refresh_token=None,
                    expires_at=None,
                    message="Failed to create user account"
                )

            # Create JWT tokens
            # Base role selection: system currently defines VIEWER / DEVELOPER / ADMIN / API_USER.
            user_roles = [UserRole.VIEWER]
            if new_user.is_developer:
                user_roles.append(UserRole.DEVELOPER)

            from ..security import get_user_permissions
            jwt_user = JWTUser(
                user_id=str(new_user.id),
                email=new_user.email,
                username=new_user.username,
                roles=user_roles,
                permissions=get_user_permissions(user_roles),
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=30)
            )

            access_token = create_access_token(jwt_user)
            refresh_token = create_refresh_token(jwt_user.user_id)

            return AuthResult(
                success=True,
                method=AuthMethod.COOKIE,
                user=jwt_user,
                session_id=self.generate_session_id(),
                csrf_token=self.generate_csrf_token() if self.config.enable_csrf_protection else None,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=jwt_user.expires_at,
                message="User created successfully"
            )

        except Exception as e:
            logger.error(f"User creation failed: {str(e)}")
            return AuthResult(
                success=False,
                method=AuthMethod.COOKIE,
                user=None,
                session_id=None,
                csrf_token=None,
                access_token=None,
                refresh_token=None,
                expires_at=None,
                message=f"User creation failed: {str(e)}"
            )

    async def authenticate_request(self, request: Request) -> AuthResult:
        """
        Authenticate a request using cookies or headers.

        Args:
            request: FastAPI request object

        Returns:
            AuthResult with authentication details
        """
        # Try cookie authentication first (more secure)
        access_token = self.get_token_from_cookie(request, self.config.access_token_name)
        session_id = self.get_token_from_cookie(request, self.config.session_id_name)

        if access_token and session_id:
            try:
                # Validate session
                if not self.validate_session(session_id, request):
                    return AuthResult(
                        success=False,
                        method=AuthMethod.COOKIE,
                        user=None,
                        session_id=None,
                        csrf_token=None,
                        access_token=None,
                        refresh_token=None,
                        expires_at=None,
                        message="Invalid or expired session"
                    )

                # Verify token
                payload = verify_token(access_token)

                # Extract user information
                user_id = payload.get("sub")
                if not user_id:
                    return AuthResult(
                        success=False,
                        method=AuthMethod.COOKIE,
                        user=None,
                        session_id=None,
                        csrf_token=None,
                        access_token=None,
                        refresh_token=None,
                        expires_at=None,
                        message="Invalid token"
                    )

                # Create JWT user
                jwt_user = JWTUser(
                    user_id=user_id,
                    username=payload.get("username", "unknown"),
                    email=payload.get("email", "unknown@example.com"),
                    roles=[UserRole(role) for role in payload.get("roles", [])],
                    permissions=payload.get("permissions", []),
                    mfa_verified=payload.get("mfa_verified", False),
                    expires_at=datetime.fromtimestamp(payload.get("exp", 0), timezone.utc) if payload.get("exp") else None
                )

                return AuthResult(
                    success=True,
                    method=AuthMethod.COOKIE,
                    user=jwt_user,
                    session_id=session_id,
                    csrf_token=None,
                    access_token=None,
                    refresh_token=None,
                    expires_at=jwt_user.expires_at,
                    message="Authenticated via cookies"
                )

            except Exception as e:
                logger.warning(f"Cookie authentication failed: {str(e)}")

        # Fall back to header authentication (for CLI and backward compatibility)
        access_token = self.get_token_from_header(request)
        if access_token:
            try:
                payload = verify_token(access_token)

                user_id = payload.get("sub")
                if not user_id:
                    return AuthResult(
                        success=False,
                        method=AuthMethod.HEADER,
                        user=None,
                        session_id=None,
                        csrf_token=None,
                        access_token=None,
                        refresh_token=None,
                        expires_at=None,
                        message="Invalid token"
                    )

                jwt_user = JWTUser(
                    user_id=user_id,
                    username=payload.get("username", "unknown"),
                    email=payload.get("email", "unknown@example.com"),
                    roles=[UserRole(role) for role in payload.get("roles", [])],
                    permissions=payload.get("permissions", []),
                    mfa_verified=payload.get("mfa_verified", False),
                    expires_at=datetime.fromtimestamp(payload.get("exp", 0), timezone.utc) if payload.get("exp") else None
                )

                return AuthResult(
                    success=True,
                    method=AuthMethod.HEADER,
                    user=jwt_user,
                    session_id=None,
                    csrf_token=None,
                    access_token=None,
                    refresh_token=None,
                    expires_at=jwt_user.expires_at,
                    message="Authenticated via header"
                )

            except Exception as e:
                logger.warning(f"Header authentication failed: {str(e)}")

        return AuthResult(
            success=False,
            method=AuthMethod.COOKIE,
            user=None,
            session_id=None,
            csrf_token=None,
            access_token=None,
            refresh_token=None,
            expires_at=None,
            message="No valid authentication found"
        )

    async def refresh_authentication(self, request: Request) -> AuthResult:
        """
        Refresh authentication using refresh token.

        Args:
            request: FastAPI request object

        Returns:
            AuthResult with refreshed authentication details
        """
        # Try to get refresh token from cookie first
        refresh_token = self.get_token_from_cookie(request, self.config.refresh_token_name)
        session_id = self.get_token_from_cookie(request, self.config.session_id_name)

        if not refresh_token:
            # Fall back to refresh token from request body (for CLI)
            return AuthResult(
                success=False,
                method=AuthMethod.COOKIE,
                user=None,
                session_id=None,
                csrf_token=None,
                access_token=None,
                refresh_token=None,
                expires_at=None,
                message="No refresh token provided"
            )

        try:
            # Verify refresh token
            payload = verify_token(refresh_token)

            if payload.get("type") != "refresh":
                return AuthResult(
                    success=False,
                    method=AuthMethod.COOKIE,
                    user=None,
                    session_id=None,
                    csrf_token=None,
                    access_token=None,
                    refresh_token=None,
                    expires_at=None,
                    message="Invalid refresh token"
                )

            user_id = payload.get("sub")
            if not user_id:
                return AuthResult(
                    success=False,
                    method=AuthMethod.COOKIE,
                    user=None,
                    session_id=None,
                    csrf_token=None,
                    access_token=None,
                    refresh_token=None,
                    expires_at=None,
                    message="Invalid refresh token"
                )

            # Get user information (in production, fetch from database)
            user = await User.get_by_id(user_id)

            if not user:
                return AuthResult(
                    success=False,
                    method=AuthMethod.COOKIE,
                    user=None,
                    session_id=None,
                    csrf_token=None,
                    access_token=None,
                    refresh_token=None,
                    expires_at=None,
                    message="User not found"
                )

            # Convert roles
            user_roles = []
            for role_str in user.roles:
                try:
                    user_roles.append(UserRole(role_str))
                except ValueError:
                    logger.warning(f"Invalid role '{role_str}' for user {user.email}")

            # Create new JWT user
            jwt_user = JWTUser(
                user_id=str(user.id) if user.id else "unknown_user",
                username=user.username,
                email=user.email,
                roles=user_roles,
                permissions=get_user_permissions(user_roles),
                mfa_verified=True,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
            )

            # Create new tokens
            new_access_token = create_access_token(jwt_user)
            new_refresh_token = create_refresh_token(jwt_user.user_id)

            # If we have a session, update it
            csrf_token = None
            if session_id and session_id in self._sessions:
                self._sessions[session_id]["last_activity"] = datetime.now(timezone.utc)
                csrf_token = self._sessions[session_id].get("csrf_token")

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
                user=None,
                session_id=None,
                csrf_token=None,
                access_token=None,
                refresh_token=None,
                expires_at=None,
                message="Failed to refresh token"
            )

    async def logout(self, request: Request) -> bool:
        """
        Logout user by invalidating session and clearing cookies.

        Args:
            request: FastAPI request object

        Returns:
            True if logout was successful
        """
        try:
            # Get session ID from cookie
            session_id = self.get_token_from_cookie(request, self.config.session_id_name)

            # Invalidate session
            if session_id:
                self.invalidate_session(session_id)

            logger.info("User logged out successfully")
            return True

        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return False

# Global enhanced auth manager instance
enhanced_auth_manager = EnhancedAuthManager()

# Dependency for FastAPI routes
async def get_current_user_enhanced(request: Request) -> JWTUser:
    """
    Enhanced authentication dependency for FastAPI routes.

    This function provides unified authentication that:
    1. First attempts cookie-based authentication (more secure)
    2. Falls back to Authorization header (backward compatibility)
    3. Handles API keys seamlessly

    Args:
        request: FastAPI request object

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    auth_result = await enhanced_auth_manager.authenticate_request(request)

    if not auth_result.success or not auth_result.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return auth_result.user

# Optional authentication dependency (doesn't raise exception)
async def get_optional_user(request: Request) -> Optional[JWTUser]:
    """
    Optional authentication dependency that doesn't raise exceptions.

    Args:
        request: FastAPI request object

    Returns:
        Authenticated user or None
    """
    try:
        auth_result = await enhanced_auth_manager.authenticate_request(request)
        return auth_result.user if auth_result.success else None
    except Exception:
        return None
