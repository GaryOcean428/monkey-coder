"""
Authentication routes for the FastAPI application.

This module provides authentication endpoints:
- POST /api/v1/auth/login - User login
- POST /api/v1/auth/signup - User registration
- POST /api/v1/auth/refresh - Token refresh
- POST /api/v1/auth/logout - User logout
- POST /api/v1/auth/supabase - Exchange Supabase OAuth token for backend JWT
- GET /api/v1/auth/status - Auth status check
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field, EmailStr
from jose import jwt, JWTError

from ...security import (
    get_current_user,
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    JWTUser,
    UserRole,
    get_user_permissions,
)
from ...database import get_user_store, User
from ...config.env_config import get_config

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

# Request/Response Models
class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class SignupRequest(BaseModel):
    """Signup request model."""
    name: str = Field(..., description="User full name")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password", min_length=8)
    plan: str = Field(default="hobby", description="Subscription plan")


class AuthResponse(BaseModel):
    """Authentication response model."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    user: Dict[str, Any] = Field(..., description="User information")


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str = Field(..., description="JWT refresh token")


class SupabaseTokenRequest(BaseModel):
    """Supabase token exchange request model."""
    access_token: str = Field(..., description="Supabase access token from OAuth flow")


class UserStatusResponse(BaseModel):
    """User status response model."""
    authenticated: bool = Field(..., description="User authentication status")
    user: Optional[Dict[str, Any]] = Field(None, description="User information if authenticated")
    session_expires: Optional[str] = Field(None, description="Session expiration timestamp")


# Authentication Endpoints
@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest) -> AuthResponse:
    """
    User login endpoint.

    Args:
        request: Login credentials (email and password)

    Returns:
        JWT tokens and user information

    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Authenticate user against the user store
        user_store = get_user_store()
        user = await user_store.authenticate_user(request.email, request.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Convert database user roles to UserRole enums
        user_roles = []
        for role_str in user.roles:
            try:
                user_roles.append(UserRole(role_str))
            except ValueError:
                # Handle any invalid roles gracefully
                logger.warning(f"Invalid role '{role_str}' for user {user.email}")

        # Validate user has an ID
        if not user.id:
            logger.error(f"User {user.email} has no ID - database integrity issue")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User account error"
            )

        # Create JWT user from authenticated user
        jwt_user = JWTUser(
            user_id=str(user.id),
            username=user.username,
            email=user.email,
            roles=user_roles,
            permissions=get_user_permissions(user_roles),
            mfa_verified=True,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )

        # Create tokens
        access_token = create_access_token(jwt_user)
        refresh_token = create_refresh_token(jwt_user.user_id)

        # Set credits and subscription tier based on user type
        credits = 10000 if user.is_developer else 100
        subscription_tier = "developer" if user.is_developer else user.subscription_plan

        logger.info(f"User {user.email} logged in successfully")

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": jwt_user.user_id,
                "email": jwt_user.email,
                "name": jwt_user.username,
                "credits": credits,
                "subscription_tier": subscription_tier,
                "is_developer": user.is_developer,
                "roles": [role.value for role in user_roles],
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed for {request.email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest) -> AuthResponse:
    """
    User signup endpoint.

    Args:
        request: User registration data

    Returns:
        JWT tokens and user information

    Raises:
        HTTPException: If signup fails
    """
    try:
        user_store = get_user_store()

        # Check if user already exists
        existing_user = await User.get_by_email(request.email.lower())
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password
        password_hash = hash_password(request.password)

        # Create new user
        user = await user_store.create_user(
            username=request.name,
            email=request.email.lower(),
            password_hash=password_hash,
            full_name=request.name,
            subscription_plan=request.plan,
            is_developer=False,
            roles=["user"]
        )

        # Convert database user roles to UserRole enums
        user_roles = []
        for role_str in user.roles:
            try:
                user_roles.append(UserRole(role_str))
            except ValueError:
                logger.warning(f"Invalid role '{role_str}' for user {user.email}")

        # Create JWT user
        jwt_user = JWTUser(
            user_id=str(user.id),
            username=user.username,
            email=user.email,
            roles=user_roles,
            permissions=get_user_permissions(user_roles),
            mfa_verified=False,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )

        # Create tokens
        access_token = create_access_token(jwt_user)
        refresh_token = create_refresh_token(jwt_user.user_id)

        # Set initial credits based on plan
        credits = 100  # Default for new users
        subscription_tier = request.plan

        logger.info(f"User {user.email} signed up successfully")

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": jwt_user.user_id,
                "email": jwt_user.email,
                "name": jwt_user.username,
                "credits": credits,
                "subscription_tier": subscription_tier,
                "is_developer": False,
                "roles": [role.value for role in user_roles],
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup failed for {request.email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signup failed. Please try again."
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(request: RefreshTokenRequest) -> AuthResponse:
    """
    Refresh access token using refresh token.

    Args:
        request: Refresh token request

    Returns:
        New JWT tokens

    Raises:
        HTTPException: If refresh fails
    """
    try:
        config = get_config()
        
        # Decode refresh token
        try:
            payload = jwt.decode(
                request.refresh_token,
                config.jwt_secret_key,
                algorithms=["HS256"]
            )
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        # Get user from database
        user = await User.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Convert database user roles to UserRole enums
        user_roles = []
        for role_str in user.roles:
            try:
                user_roles.append(UserRole(role_str))
            except ValueError:
                logger.warning(f"Invalid role '{role_str}' for user {user.email}")

        # Create JWT user
        jwt_user = JWTUser(
            user_id=str(user.id),
            username=user.username,
            email=user.email,
            roles=user_roles,
            permissions=get_user_permissions(user_roles),
            mfa_verified=True,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )

        # Create new tokens
        access_token = create_access_token(jwt_user)
        new_refresh_token = create_refresh_token(jwt_user.user_id)

        # Set credits and subscription tier
        credits = 10000 if user.is_developer else 100
        subscription_tier = "developer" if user.is_developer else user.subscription_plan

        return AuthResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            user={
                "id": jwt_user.user_id,
                "email": jwt_user.email,
                "name": jwt_user.username,
                "credits": credits,
                "subscription_tier": subscription_tier,
                "is_developer": user.is_developer,
                "roles": [role.value for role in user_roles],
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout(current_user: JWTUser = Depends(get_current_user)) -> Dict[str, str]:
    """
    User logout endpoint.

    Args:
        current_user: Current authenticated user from JWT

    Returns:
        Logout confirmation
    """
    logger.info(f"User {current_user.email} logged out")
    return {"message": "Successfully logged out"}


@router.post("/supabase", response_model=AuthResponse)
async def exchange_supabase_token(request: SupabaseTokenRequest) -> AuthResponse:
    """
    Exchange a Supabase OAuth access token for a backend JWT.

    This bridges the Supabase OAuth flow to the backend auth system:
    1. Verifies the Supabase token by calling the Supabase REST API
    2. Extracts user info (email, name) from the Supabase response
    3. Finds or creates a user in the backend store
    4. Returns backend JWT tokens

    Args:
        request: Contains the Supabase access token

    Returns:
        Backend JWT tokens and user information

    Raises:
        HTTPException: If token verification or user creation fails
    """
    supabase_url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    if not supabase_url:
        logger.error("SUPABASE_URL not configured on backend")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OAuth service not configured"
        )

    # Resolve API key — supports new secret key (sb_secret_xxx) and legacy service_role/anon
    apikey = (
        os.getenv("SUPABASE_SECRET_KEY")
        or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")
        or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")
    )

    # Verify the Supabase token by calling Supabase's /auth/v1/user endpoint.
    # Per Supabase docs (2025): for HS256/legacy JWT secret projects, server-side
    # verification via the Auth API is the recommended approach over local JWT
    # decoding with the shared secret. This avoids shared-secret exposure risks.
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{supabase_url}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {request.access_token}",
                    "apikey": apikey,
                },
                timeout=10.0,
            )
    except httpx.RequestError as e:
        logger.error(f"Failed to contact Supabase: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to verify OAuth token"
        )

    if resp.status_code != 200:
        logger.warning(f"Supabase token verification failed: {resp.status_code} {resp.text[:200]}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OAuth token"
        )

    supabase_user = resp.json()
    email = supabase_user.get("email", "").lower()
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth account has no email address"
        )

    # Extract name from Supabase user metadata
    user_meta = supabase_user.get("user_metadata", {})
    name = (
        user_meta.get("full_name")
        or user_meta.get("name")
        or user_meta.get("preferred_username")
        or email.split("@")[0]
    )
    provider = supabase_user.get("app_metadata", {}).get("provider", "oauth")

    # Find or create user in backend store
    user_store = get_user_store()
    user = await User.get_by_email(email)

    if not user:
        # Create a new user for this OAuth account (no password needed)
        import secrets
        oauth_password_hash = hash_password(secrets.token_urlsafe(32))
        user = await user_store.create_user(
            username=name,
            email=email,
            password_hash=oauth_password_hash,
            full_name=name,
            subscription_plan="hobby",
            is_developer=False,
            roles=["user"],
        )
        logger.info(f"Created new user from {provider} OAuth: {email}")
    else:
        logger.info(f"Existing user authenticated via {provider} OAuth: {email}")

    # Convert database user roles to UserRole enums
    user_roles = []
    for role_str in user.roles:
        try:
            user_roles.append(UserRole(role_str))
        except ValueError:
            logger.warning(f"Invalid role '{role_str}' for user {user.email}")

    if not user.id:
        logger.error(f"OAuth user {email} has no ID")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User account error"
        )

    # Create JWT user and tokens
    jwt_user = JWTUser(
        user_id=str(user.id),
        username=user.username,
        email=user.email,
        roles=user_roles,
        permissions=get_user_permissions(user_roles),
        mfa_verified=True,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
    )

    access_token = create_access_token(jwt_user)
    refresh_token = create_refresh_token(jwt_user.user_id)

    credits = 10000 if user.is_developer else 100
    subscription_tier = "developer" if user.is_developer else user.subscription_plan

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": jwt_user.user_id,
            "email": jwt_user.email,
            "name": jwt_user.username,
            "credits": credits,
            "subscription_tier": subscription_tier,
            "is_developer": user.is_developer,
            "roles": [role.value for role in user_roles],
        },
    )


@router.get("/status", response_model=UserStatusResponse)
async def get_status(current_user: JWTUser = Depends(get_current_user)) -> UserStatusResponse:
    """
    Get current user authentication status.

    Args:
        current_user: Current authenticated user from JWT

    Returns:
        User status information
    """
    return UserStatusResponse(
        authenticated=True,
        user={
            "id": current_user.user_id,
            "email": current_user.email,
            "name": current_user.username,
            "roles": [role.value for role in current_user.roles],
        },
        session_expires=current_user.expires_at.isoformat() if current_user.expires_at else None
    )
