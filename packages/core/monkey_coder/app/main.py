"""
FastAPI main application for Monkey Coder Core Orchestration Engine.

This module provides the core FastAPI application with:
- /api/v1/execute endpoint for task routing & quantum execution
- /api/v1/billing/usage endpoint for metering
- Integration with SuperClaude, monkey1, and Gary8D systems
"""

import logging
import os
import asyncio
import traceback
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import time
from pathlib import Path
from .streaming_endpoints import router as streaming_router
from .streaming_execute import router as streaming_execute_router

from ..core.orchestrator import MultiAgentOrchestrator
from ..core.quantum_executor import QuantumExecutor
from ..core.persona_router import PersonaRouter
from ..providers import ProviderRegistry
from ..models import (
    ExecuteRequest,
    ExecuteResponse,
    UsageRequest,
    UsageResponse,
    TaskStatus,
    ExecutionError,
)
# Context Manager imports (feature-flagged)
from ..context.simple_manager import SimpleContextManager  # existing lightweight manager
try:
    from ..context.context_manager import ContextManager as AdvancedContextManager  # heavy version
except Exception:  # pragma: no cover - safe fallback
    AdvancedContextManager = None
from ..security import (
    get_api_key,
    verify_permissions,
    get_current_user,
    JWTUser,
    UserRole,
)
from ..auth.enhanced_cookie_auth import enhanced_auth_manager
from ..auth.cookie_auth import get_current_user_from_cookie
from ..monitoring import MetricsCollector, BillingTracker
from ..monitoring import quantum_performance
from ..database import run_migrations
from ..pricing import PricingMiddleware, load_pricing_from_file
from ..billing import StripeClient, BillingPortalSession
from .routes import stripe_checkout
from ..feedback_collector import FeedbackCollector
from ..database.models import User
from ..config.env_config import get_config
from ..auth import get_api_key_manager

# Import Railway-optimized logging first
from ..logging_utils import setup_logging, get_performance_logger

# Configure Railway-optimized logging
setup_logging()
logger = logging.getLogger(__name__)
performance_logger = get_performance_logger("app_performance")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown tasks.
    """
    # Startup
    logger.info("Starting Monkey Coder Core Orchestration Engine...")

    # Initialize environment configuration
    try:
        config = get_config()
        app.state.config = config

        # Log configuration summary
        config_summary = config.get_config_summary()
        logger.info(f"Environment configuration loaded: {config_summary}")

        # Validate required configuration
        validation_result = config.validate_required_config()
        if validation_result["missing"]:
            logger.error(f"Missing required configuration: {validation_result['missing']}")
        if validation_result["warnings"]:
            logger.warning(f"Configuration warnings: {validation_result['warnings']}")

    except Exception as e:
        logger.error(f"Failed to initialize environment configuration: {e}")
        # Continue startup with default configuration

    # Run database migrations
    try:
        await run_migrations()
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Database migrations failed: {e}")
        # Continue startup even if migrations fail (for development)

    # Initialize core components with health checks
    try:
        app.state.provider_registry = ProviderRegistry()
        logger.info("✅ ProviderRegistry initialized successfully")

        app.state.orchestrator = MultiAgentOrchestrator(provider_registry=app.state.provider_registry)
        logger.info("✅ MultiAgentOrchestrator initialized successfully")

        app.state.quantum_executor = QuantumExecutor(provider_registry=app.state.provider_registry)
        logger.info("✅ QuantumExecutor initialized successfully")

        app.state.persona_router = PersonaRouter()
        logger.info("✅ PersonaRouter initialized successfully")

        app.state.metrics_collector = MetricsCollector()
        logger.info("✅ MetricsCollector initialized successfully")

        app.state.billing_tracker = BillingTracker()
        logger.info("✅ BillingTracker initialized successfully")

        app.state.feedback_collector = FeedbackCollector()
        logger.info("✅ FeedbackCollector initialized successfully")

        app.state.api_key_manager = get_api_key_manager()
        logger.info("✅ APIKeyManager initialized successfully")

        # Initialize context manager for multi-turn conversations
        enable_context = os.getenv("ENABLE_CONTEXT_MANAGER", "true").lower() == "true"
        context_mode = os.getenv("CONTEXT_MODE", "simple").lower()
        if enable_context:
            if context_mode == "advanced" and AdvancedContextManager is not None:
                try:
                    app.state.context_manager = AdvancedContextManager()
                    logger.info("✅ AdvancedContextManager initialized")
                except Exception as e:  # fallback gracefully
                    logger.warning(f"AdvancedContextManager failed ({e}); falling back to SimpleContextManager")
                    app.state.context_manager = SimpleContextManager()
            else:
                app.state.context_manager = SimpleContextManager()
                logger.info("✅ SimpleContextManager initialized")
        else:
            app.state.context_manager = None
            logger.info("ℹ️ Context management disabled (ENABLE_CONTEXT_MANAGER=false)")

        # Start periodic context cleanup task
        async def periodic_cleanup():
            while True:
                try:
                    await asyncio.sleep(3600)  # Run every hour
                    await app.state.context_manager.cleanup_expired_sessions()
                    logger.info("Periodic context cleanup completed")
                except Exception as e:
                    logger.error(f"Periodic context cleanup failed: {e}")

        app.state.cleanup_task = asyncio.create_task(periodic_cleanup())
        logger.info("✅ Periodic context cleanup task started")

        # Initialize providers with timeout
        await app.state.provider_registry.initialize_all()
        logger.info("✅ All providers initialized successfully")

    except Exception as e:
        logger.error(f"❌ Component initialization failed: {e}")
        traceback.print_exc()
        # Continue startup even if some components fail
        # This allows the health endpoint to report component status

    logger.info("Orchestration engine started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Monkey Coder Core...")

    # Cancel periodic cleanup task
    if hasattr(app.state, 'cleanup_task'):
        app.state.cleanup_task.cancel()
        try:
            await app.state.cleanup_task
        except asyncio.CancelledError:
            pass
        logger.info("Periodic cleanup task cancelled")

    await app.state.provider_registry.cleanup_all()
    logger.info("Shutdown complete")


# Create FastAPI application with API docs under /api path
app = FastAPI(
    title="Monkey Coder Core",
    description="Python orchestration core for AI-powered code generation and analysis",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Load pricing data from file (if exists) on startup
load_pricing_from_file()
# Mount Stripe Checkout routes with /api prefix
app.include_router(stripe_checkout.router, prefix="/api/v1/stripe", tags=["stripe"])

# Mount streaming endpoints with /api prefix
app.include_router(streaming_router, prefix="/api")
app.include_router(streaming_execute_router, prefix="/api")

# Initialize configuration for middleware setup
middleware_config = get_config()

# Add pricing middleware
enable_pricing = middleware_config._get_env_bool("ENABLE_PRICING_MIDDLEWARE", True)
app.add_middleware(PricingMiddleware, enabled=enable_pricing)

# Add other middleware with environment-aware configuration
# Normalize comma-separated env values (trim spaces, drop empties) and ensure Railway internal domain is allowed
if middleware_config.environment == "production":
    allowed_origins = [
        o.strip() for o in middleware_config._get_env("CORS_ORIGINS", "").split(",")
        if o.strip()
    ]
    allowed_hosts = [
        h.strip() for h in middleware_config._get_env("TRUSTED_HOSTS", "").split(",")
        if h.strip()
    ]

    # Ensure Railway's internal routing is permitted by TrustedHostMiddleware
    if not any("railway.internal" in h for h in allowed_hosts):
        allowed_hosts.append("*.railway.internal")

    # If CORS_ORIGINS is empty in production, fall back to public domain (if present)
    if not allowed_origins:
        public_domain = middleware_config._get_env("RAILWAY_PUBLIC_DOMAIN", "").strip()
        if public_domain:
            # Include both https and http for local testing through Railway domain
            allowed_origins = [
                f"https://{public_domain}",
                f"http://{public_domain}",
                "https://coder.fastmonkey.au",
                "http://coder.fastmonkey.au"
            ]
        else:
            # Safe fallback to Railway domains
            allowed_origins = [
                "https://aetheros-production.up.railway.app",
                "https://coder.fastmonkey.au"
            ]
else:
    # Development: keep permissive defaults
    allowed_origins = ["*"]
    allowed_hosts = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts
)

# Add Sentry middleware for error tracking
app.add_middleware(SentryAsgiMiddleware)

# Add production security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add production security headers to all responses."""
    response = await call_next(request)

    # Get production security headers
    if middleware_config.environment == "production":
        from ..config.production_config import get_production_config
        prod_config = get_production_config()
        security_headers = prod_config.get_security_headers()

        for header, value in security_headers.items():
            response.headers[header] = value

    return response

# Add metrics collection middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware to collect HTTP request metrics for Prometheus and Railway."""
    start_time = time.time()

    response = await call_next(request)

    # Calculate request duration
    duration = time.time() - start_time

    # Record metrics
    if hasattr(app.state, 'metrics_collector'):
        app.state.metrics_collector.record_http_request(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
            duration=duration
        )

    # Record performance metrics for Phase 2.0 monitoring
    from ..optimization.performance_cache import get_performance_monitor
    try:
        performance_monitor = get_performance_monitor()
        performance_monitor.record_request(
            endpoint=request.url.path,
            method=request.method,
            duration=duration,
            status_code=response.status_code,
            user_id=getattr(request.state, 'user_id', None)
        )
    except Exception as e:
        logger.debug(f"Performance monitoring error: {e}")

    # Log performance data for Railway
    performance_logger.logger.info(
        "Request processed",
        extra={'extra_fields': {
            'metric_type': 'http_request',
            'method': request.method,
            'path': request.url.path,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'user_agent': request.headers.get('user-agent', 'unknown')
        }}
    )

    # Add performance headers
    response.headers["X-Process-Time"] = f"{duration:.4f}"

    return response


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: str = Field(..., description="Current timestamp")
    components: Dict[str, str] = Field(..., description="Component status")


# Authentication Models
class LoginRequest(BaseModel):
    """Login request model."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class AuthResponse(BaseModel):
    """Authentication response model."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    user: Dict[str, Any] = Field(..., description="User information")
    expires_at: Optional[str] = Field(None, description="Access token expiration timestamp")


class UserStatusResponse(BaseModel):
    """User status response model."""
    authenticated: bool = Field(..., description="User authentication status")
    user: Optional[Dict[str, Any]] = Field(None, description="User information if authenticated")
    session_expires: Optional[str] = Field(None, description="Session expiration timestamp")


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str = Field(..., description="JWT refresh token")


# Root endpoint removed to allow Next.js static files to be served at root path


@app.get("/health", response_model=HealthResponse)
@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint optimized for Railway deployment.
    """
    from datetime import datetime
    import psutil

    # Get system metrics
    try:
        process = psutil.Process()
        memory_mb = round(process.memory_info().rss / 1024 / 1024, 2)
        cpu_percent = process.cpu_percent()
    except Exception:
        memory_mb = 0
        cpu_percent = 0

    # Check component health
    components = {
        "orchestrator": "active" if hasattr(app.state, 'orchestrator') else "inactive",
        "quantum_executor": "active" if hasattr(app.state, 'quantum_executor') else "inactive",
        "persona_router": "active" if hasattr(app.state, 'persona_router') else "inactive",
        "provider_registry": "active" if hasattr(app.state, 'provider_registry') else "inactive",
    }

    # Log health check for monitoring
    performance_logger.logger.info(
        "Health check performed",
        extra={'extra_fields': {
            'metric_type': 'health_check',
            'memory_mb': memory_mb,
            'cpu_percent': cpu_percent,
            'components': components,
            'qwen_agent_available': 'qwen_agent' in globals()
        }}
    )

    return HealthResponse(
        status="healthy",
        version="2.0.0",  # Updated to Phase 2.0
        timestamp=datetime.utcnow().isoformat(),
        components=components
    )


@app.get("/health/comprehensive")
async def comprehensive_health_check():
    """
    Comprehensive health check for production monitoring.

    Provides detailed health status including system resources,
    database connectivity, AI provider status, and component health.
    """
    from ..config.production_config import get_production_config

    prod_config = get_production_config()
    health_status = await prod_config.comprehensive_health_check()

    return JSONResponse(
        content=health_status,
        status_code=200 if health_status["status"] == "healthy" else 503
    )


@app.get("/health/readiness")
async def readiness_check():
    """
    Kubernetes-style readiness check for production deployment.

    Returns 200 if the application is ready to receive traffic,
    503 if still initializing or experiencing issues.
    """
    # Check if critical components are initialized
    if not all([
        hasattr(app.state, 'orchestrator'),
        hasattr(app.state, 'quantum_executor'),
        hasattr(app.state, 'provider_registry')
    ]):
        return JSONResponse(
            content={"status": "not_ready", "message": "Core components not initialized"},
            status_code=503
        )

    return JSONResponse(
        content={"status": "ready", "timestamp": datetime.utcnow().isoformat()},
        status_code=200
    )


@app.get("/api/v1/production/validate")
async def validate_production_readiness():
    """
    Production readiness validation endpoint.

    Performs comprehensive validation of production configuration,
    security settings, and system health for deployment readiness.
    """
    from ..config.production_config import get_production_config

    prod_config = get_production_config()
    validation_results = prod_config.validate_production_readiness()

    # Add additional runtime checks
    runtime_checks = {
        "components_initialized": all([
            hasattr(app.state, 'orchestrator'),
            hasattr(app.state, 'quantum_executor'),
            hasattr(app.state, 'provider_registry')
        ]),
        "metrics_enabled": hasattr(app.state, 'metrics_collector'),
        "security_headers_active": True,  # We added the middleware
        "performance_monitoring_active": True  # We added performance monitoring
    }

    validation_results["runtime_checks"] = runtime_checks
    validation_results["overall_ready"] = (
        validation_results["ready"] and
        all(runtime_checks.values())
    )

    status_code = 200 if validation_results["overall_ready"] else 503

    return JSONResponse(
        content=validation_results,
        status_code=status_code
    )


@app.get("/metrics")
async def prometheus_metrics():
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus text format for scraping.
    """
    if not hasattr(app.state, 'metrics_collector'):
        return Response(
            content="# Metrics collector not initialized\n",
            media_type="text/plain"
        )

    metrics_data = app.state.metrics_collector.get_prometheus_metrics()
    return Response(content=metrics_data, media_type="text/plain")


@app.get("/metrics/performance")
async def performance_metrics():
    """
    Performance metrics endpoint for monitoring dashboard.

    Returns detailed performance statistics including response times,
    cache hit rates, and slow request analysis.
    """
    from ..optimization.performance_cache import get_performance_monitor, get_cache

    performance_monitor = get_performance_monitor()
    cache = get_cache()

    metrics = {
        "performance": performance_monitor.get_performance_summary(),
        "cache": cache.get_stats(),
        "quantum": quantum_performance.get_summary(),
        "timestamp": datetime.utcnow().isoformat()
    }

    return JSONResponse(content=metrics)


@app.get("/metrics/cache")
async def cache_metrics():
    """
    Cache statistics endpoint for performance monitoring.
    """
    from ..optimization.performance_cache import get_cache

    cache = get_cache()
    stats = cache.get_stats()

    return JSONResponse(content=stats)


# Authentication Endpoints
@app.post("/api/v1/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest, response: Response, background_tasks: BackgroundTasks) -> AuthResponse:
    """
    User login endpoint with enhanced authentication.

    Args:
        request: Login credentials (email and password)
        response: FastAPI response object
        background_tasks: Background tasks for async operations

    Returns:
        AuthResponse with tokens and user information
    """
    try:
        # Authenticate user using enhanced manager
        auth_result = await enhanced_auth_manager.authenticate_user(
            email=request.email,
            password=request.password,
            request=Request(scope={}),  # Mock request for CLI compatibility
            for_cli=False
        )

        if not auth_result.success or not auth_result.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=auth_result.message or "Invalid email or password"
            )

        if not auth_result.access_token or not auth_result.refresh_token or not auth_result.session_id:
            raise HTTPException(status_code=500, detail="Authentication failed to generate tokens")

        # Set cookies using enhanced manager
        enhanced_auth_manager.set_auth_cookies(
            response=response,
            access_token=auth_result.access_token,
            refresh_token=auth_result.refresh_token,
            session_id=auth_result.session_id,
            csrf_token=auth_result.csrf_token
        )

        # Get user details
        user = await User.get_by_id(auth_result.user.user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found after authentication")

        # Set credits and subscription tier
        credits = 10000 if user.is_developer else 100
        subscription_tier = "developer" if user.is_developer else "free"

        return AuthResponse(
            access_token=auth_result.access_token,
            refresh_token=auth_result.refresh_token,
            user={
                "id": auth_result.user.user_id,
                "email": auth_result.user.email,
                "name": auth_result.user.username,
                "credits": credits,
                "subscription_tier": subscription_tier,
                "is_developer": user.is_developer,
                "roles": [r.value for r in auth_result.user.roles]
            },
            expires_at=auth_result.expires_at.isoformat() if auth_result.expires_at else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/api/v1/auth/status", response_model=UserStatusResponse)
async def get_user_status(request: Request) -> UserStatusResponse:
    """
    Get current user authentication status.

    Args:
        request: FastAPI request object

    Returns:
        User status and information
    """
    try:
        # Try to get user from cookie authentication
        try:
            current_user = await get_current_user_from_cookie(request)
            return UserStatusResponse(
                authenticated=True,
                user={
                    "email": current_user.email,
                    "name": current_user.username,
                    "credits": 10000,  # Mock credits
                    "subscription_tier": "developer"
                },
                session_expires=current_user.expires_at.isoformat() if current_user.expires_at else None
            )
        except HTTPException:
            # Not authenticated
            return UserStatusResponse(
                authenticated=False,
                user=None,
                session_expires=None
            )

    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return UserStatusResponse(
            authenticated=False,
            user=None,
            session_expires=None
        )


@app.post("/api/v1/auth/logout")
async def logout(request: Request, response: Response) -> Dict[str, str]:
    """
    User logout endpoint.

    Args:
        request: FastAPI request object
        response: FastAPI response object

    Returns:
        Logout confirmation
    """
    try:
        # Try to get current user for logging purposes
        current_user = None
        try:
            current_user = await get_current_user_from_cookie(request)
        except Exception:
            pass  # User might already be logged out

        # Logout using enhanced manager
        success = await enhanced_auth_manager.logout(request)

        if not success:
            # Still clear cookies even if session invalidation fails
            pass

        # Clear cookies
        enhanced_auth_manager.clear_auth_cookies(response)

        if current_user:
            logger.info(f"User {current_user.email} logged out successfully")

        return {"message": "Successfully logged out"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Logout failed")


@app.post("/api/v1/auth/refresh", response_model=AuthResponse)
async def refresh_token(request: Request, response: Response) -> AuthResponse:
    """
    Refresh JWT access token using refresh token.

    Args:
        request: FastAPI request object
        response: FastAPI response object

    Returns:
        New JWT tokens
    """
    try:
        # Refresh using enhanced manager
        auth_result = await enhanced_auth_manager.refresh_authentication(request)

        if not auth_result.success or not auth_result.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=auth_result.message or "Invalid refresh token"
            )

        if not auth_result.access_token or not auth_result.refresh_token or not auth_result.session_id:
            raise HTTPException(status_code=500, detail="Refresh failed to generate tokens")

        # Set refreshed cookies
        enhanced_auth_manager.set_auth_cookies(
            response=response,
            access_token=auth_result.access_token,
            refresh_token=auth_result.refresh_token,
            session_id=auth_result.session_id,
            csrf_token=auth_result.csrf_token
        )

        # Get user details
        user = await User.get_by_id(auth_result.user.user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found after refresh")

        return AuthResponse(
            access_token=auth_result.access_token,
            refresh_token=auth_result.refresh_token,
            user={
                "id": auth_result.user.user_id,
                "email": auth_result.user.email,
                "name": auth_result.user.username,
                "credits": 10000 if user.is_developer else 100,
                "subscription_tier": "developer" if user.is_developer else "free",
                "is_developer": user.is_developer,
                "roles": [r.value for r in auth_result.user.roles]
            },
            expires_at=auth_result.expires_at.isoformat() if auth_result.expires_at else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Failed to refresh token")


@app.post("/api/v1/execute", response_model=ExecuteResponse)
async def execute_task(
    request: ExecuteRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key),
) -> ExecuteResponse:
    """
    Main task execution endpoint with routing & quantum execution.

    This endpoint:
    1. Routes tasks through SuperClaude slash-command & persona router
    2. Orchestrates execution via monkey1 multi-agent system
    3. Executes tasks using Gary8D functional-quantum executor
    4. Tracks usage and billing metrics

    Args:
        request: Task execution request
        background_tasks: FastAPI background tasks
        api_key: API key for authentication

    Returns:
        ExecuteResponse with task results and metadata

    Raises:
        HTTPException: If task execution fails
    """
    try:
        # Verify permissions
        await verify_permissions(api_key, "execute")

        # Context Management Integration - Handle conversation history
        conversation_context = []

        if request.context.session_id:
            try:
                # Add user message to conversation
                await app.state.context_manager.add_message(
                    user_id=request.context.user_id,
                    session_id=request.context.session_id,
                    role="user",
                    content=request.prompt,
                    metadata={"task_type": str(request.task_type), "task_id": request.task_id}
                )

                # Get conversation context for better prompt understanding
                conversation_context = await app.state.context_manager.get_conversation_context(
                    user_id=request.context.user_id,
                    session_id=request.context.session_id,
                    include_system=True
                )
                logger.info(f"Loaded conversation context with {len(conversation_context)} messages")

            except Exception as e:
                logger.warning(f"Context management error (continuing without context): {e}")
                # Continue execution without context rather than failing
                conversation_context = []

        # Start metrics collection
        execution_id = app.state.metrics_collector.start_execution(request)

        # Route through persona system (SuperClaude integration)
        persona_context = await app.state.persona_router.route_request(request)

        # Execute through multi-agent orchestrator (monkey1 integration)
        orchestration_result = await app.state.orchestrator.orchestrate(
            request, persona_context
        )

        # Execute via quantum executor (Gary8D integration)
        execution_result = await app.state.quantum_executor.execute(
            orchestration_result, parallel_futures=True
        )

        # Prepare response
        response = ExecuteResponse(
            execution_id=execution_id,
            task_id=request.task_id,
            status=TaskStatus.COMPLETED,
            result=execution_result.result if hasattr(execution_result, "result") else None,
            error=None,
            completed_at=None,
            usage=getattr(execution_result, "usage", None),
            execution_time=getattr(execution_result, "execution_time", None),
            persona_routing={},
            orchestration_info={},
            quantum_execution={}
        )

        # Save assistant response to conversation context
        if request.context.session_id:
            try:
                assistant_content = response.result if response.result else "Task completed successfully"
                await app.state.context_manager.add_message(
                    user_id=request.context.user_id,
                    session_id=request.context.session_id,
                    role="assistant",
                    content=str(assistant_content),
                    metadata={"execution_id": execution_id, "task_type": str(request.task_type)}
                )
                logger.info("Saved assistant response to conversation context")
            except Exception as e:
                logger.warning(f"Failed to save assistant response to context: {e}")
                # Continue without failing the request

        # Track billing in background
        background_tasks.add_task(
            app.state.billing_tracker.track_usage,
            api_key,
            execution_result.usage
        )

        # Complete metrics collection
        app.state.metrics_collector.complete_execution(execution_id, response)

        return response

    except Exception as e:
        logger.error(f"Task execution failed: {str(e)}")

        # Track error metrics
        if 'execution_id' in locals():
            app.state.metrics_collector.record_error(execution_id, str(e))

        # Return appropriate error response
        if isinstance(e, ExecutionError):
            raise HTTPException(status_code=400, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/billing/usage", response_model=UsageResponse)
async def get_usage_metrics(
    request: UsageRequest = Depends(),
    api_key: str = Depends(get_api_key),
) -> UsageResponse:
    """
    Billing and usage metrics endpoint.

    Provides detailed usage statistics including:
    - Token consumption by provider
    - Execution counts and durations
    - Cost breakdowns
    - Rate limiting status

    Args:
        request: Usage request parameters
        api_key: API key for authentication

    Returns:
        UsageResponse with detailed usage metrics

    Raises:
        HTTPException: If metrics retrieval fails
    """
    try:
        # Verify permissions
        await verify_permissions(api_key, "billing:read")

        # Get usage data from billing tracker
        usage_data = await app.state.billing_tracker.get_usage(
            api_key=api_key,
            start_date=request.start_date,
            end_date=request.end_date,
            granularity=request.granularity,
        )

        return UsageResponse(
            api_key_hash=usage_data.api_key_hash,
            period=usage_data.period,
            total_requests=usage_data.total_requests,
            total_tokens=usage_data.total_tokens,
            total_cost=usage_data.total_cost,
            provider_breakdown=usage_data.provider_breakdown,
            execution_stats=usage_data.execution_stats,
            rate_limit_status=usage_data.rate_limit_status,
        )

    except Exception as e:
        logger.error(f"Usage metrics retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve usage metrics")


@app.post("/api/v1/billing/portal", response_model=BillingPortalSession)
async def create_billing_portal_session(
    api_key: str = Depends(get_api_key),
    return_url: str = "https://yourdomain.com/billing"
) -> BillingPortalSession:
    """
    Create a Stripe billing portal session.

    This endpoint creates a billing portal session that allows customers
    to manage their billing information, view invoices, and update payment methods.

    Args:
        api_key: API key for authentication
        return_url: URL to redirect to after session ends

    Returns:
        BillingPortalSession: Session information including URL

    Raises:
        HTTPException: If session creation fails
    """
    from ..database.models import BillingCustomer
    import hashlib

    try:
        # Verify permissions
        await verify_permissions(api_key, "billing:manage")

        # Hash API key to find customer
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]

        # Get billing customer
        billing_customer = await BillingCustomer.get_by_api_key_hash(api_key_hash)
        if not billing_customer:
            raise HTTPException(
                status_code=404,
                detail="No billing customer found. Please contact support to set up billing."
            )

        # Create Stripe client and billing portal session
        stripe_client = StripeClient()
        session_url = stripe_client.create_billing_portal_session(
            customer_id=billing_customer.stripe_customer_id,
            return_url=return_url
        )

        return BillingPortalSession(
            session_url=session_url,
            customer_id=billing_customer.stripe_customer_id,
            expires_at=None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create billing portal session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create billing portal session")


@app.get("/api/v1/providers", response_model=Dict[str, Any])
async def list_providers(
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    List available AI providers and their status.

    Returns information about supported providers:
    - OpenAI (GPT models)
    - Anthropic (Claude models)
    - Google (Gemini models)
    - Qwen (Qwen Coder models)

    Args:
        api_key: API key for authentication

    Returns:
        Dictionary with provider information and status
    """
    try:
        await verify_permissions(api_key, "providers:read")

        providers = app.state.provider_registry.get_all_providers()
        return {
            "providers": providers,
            "count": len(providers),
            "status": "active"
        }

    except Exception as e:
        logger.error(f"Provider listing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list providers")


@app.get("/api/v1/models", response_model=Dict[str, Any])
async def list_models(
    provider: Optional[str] = None,
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    List available AI models by provider.

    Args:
        provider: Optional provider filter (openai, anthropic, google, qwen)
        api_key: API key for authentication

    Returns:
        Dictionary with model information by provider
    """
    try:
        await verify_permissions(api_key, "models:read")

        models = await app.state.provider_registry.get_available_models(provider)
        return {
            "models": models,
            "provider_filter": provider,
            "count": sum(len(models[p]) for p in models),
        }

    except Exception as e:
        logger.error(f"Model listing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list models")


@app.post("/api/v1/router/debug", response_model=Dict[str, Any])
async def debug_routing(
    request: ExecuteRequest,
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Debug routing decisions for a given request.

    This endpoint provides detailed information about how the AdvancedRouter
    would route a given request, including:
    - Selected model and provider
    - Chosen persona
    - Complexity, context, and capability scores
    - Reasoning behind the decision
    - Available alternatives

    Args:
        request: The execution request to analyze
        api_key: API key for authentication

    Returns:
        Detailed routing debug information
    """
    try:
        await verify_permissions(api_key, "router:debug")

        # Get detailed routing debug information
        debug_info = app.state.persona_router.get_routing_debug_info(request)

        return {
            "debug_info": debug_info,
            "request_summary": {
                "task_type": request.task_type.value,
                "prompt_length": len(request.prompt),
                "has_files": bool(request.files),
                "file_count": len(request.files) if request.files else 0,
            },
            "personas_available": app.state.persona_router.get_available_personas(),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Router debug failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate routing debug info")


@app.get("/api/v1/capabilities", response_model=Dict[str, Any])
async def get_system_capabilities(
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Get comprehensive system capabilities information.

    This endpoint provides detailed information about:
    - Environment configuration status
    - Persona validation capabilities
    - Orchestration strategies and patterns
    - Available providers and models
    - System health and performance metrics

    Args:
        api_key: API key for authentication

    Returns:
        Comprehensive system capabilities information
    """
    try:
        await verify_permissions(api_key, "system:read")

        # Get environment configuration summary
        config_summary = None
        if hasattr(app.state, 'config'):
            config_summary = app.state.config.get_config_summary()

        # Get persona validation stats
        validation_stats = app.state.persona_router.get_validation_stats()

        # Get orchestration capabilities
        orchestration_caps = app.state.orchestrator.get_orchestration_capabilities()

        # Get provider information
        providers = app.state.provider_registry.get_all_providers()

        return {
            "system_info": {
                "version": "1.0.0",
                "environment": config_summary.get("environment") if config_summary else "unknown",
                "debug_mode": config_summary.get("debug") if config_summary else False,
                "timestamp": datetime.utcnow().isoformat()
            },

            "environment_configuration": {
                "status": "configured" if config_summary else "default",
                "summary": config_summary,
                "validation_warnings": [] if config_summary else ["Using default configuration"]
            },

            "persona_validation": {
                "enhanced_validation": True,
                "single_word_support": True,
                "edge_case_handling": True,
                "capabilities": validation_stats
            },

            "orchestration": {
                "enhanced_patterns": True,
                "multi_strategy_support": True,
                "intelligent_coordination": True,
                "capabilities": orchestration_caps
            },

            "providers": {
                "total_providers": len(providers),
                "active_providers": [p["name"] for p in providers if p.get("status") == "active"],
                "provider_details": providers
            },

            "features": [
                "environment_configuration_management",
                "persona_aware_routing_with_validation",
                "single_word_input_enhancement",
                "edge_case_prompt_handling",
                "multi_strategy_orchestration",
                "sequential_agent_coordination",
                "parallel_task_execution",
                "quantum_inspired_processing",
                "hybrid_orchestration_strategies",
                "intelligent_agent_handoff",
                "comprehensive_error_handling",
                "production_ready_deployment"
            ],

            "recent_enhancements": [
                {
                    "feature": "Environment Configuration",
                    "description": "Centralized environment variable management with validation",
                    "status": "implemented"
                },
                {
                    "feature": "Persona Validation",
                    "description": "Enhanced validation for single-word inputs and edge cases",
                    "status": "implemented"
                },
                {
                    "feature": "Orchestration Patterns",
                    "description": "Advanced orchestration strategies from reference projects",
                    "status": "implemented"
                },
                {
                    "feature": "Frontend Serving",
                    "description": "Improved static file serving with fallback handling",
                    "status": "implemented"
                }
            ]
        }

    except Exception as e:
        logger.error(f"Capabilities retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system capabilities")


# API Key Management Endpoints

class APIKeyCreateRequest(BaseModel):
    """Request model for creating new API keys."""
    name: str = Field(..., description="Human-readable name for the API key")
    description: str = Field("", description="Description of the key's purpose")
    permissions: Optional[List[str]] = Field(None, description="List of permissions (default: basic permissions)")
    expires_days: Optional[int] = Field(None, description="Number of days until expiration (None = no expiration)")


class APIKeyResponse(BaseModel):
    """Response model for API key operations."""
    key: Optional[str] = Field(None, description="The generated API key (only returned on creation)")
    key_id: str = Field(..., description="Unique key identifier")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Key description")
    status: str = Field(..., description="Key status")
    created_at: str = Field(..., description="Creation timestamp")
    expires_at: Optional[str] = Field(None, description="Expiration timestamp")
    last_used: Optional[str] = Field(None, description="Last used timestamp")
    usage_count: int = Field(..., description="Number of times used")
    permissions: List[str] = Field(..., description="Assigned permissions")


@app.post("/api/v1/auth/keys", response_model=APIKeyResponse)
async def create_api_key(
    request: APIKeyCreateRequest,
    current_user: JWTUser = Depends(get_current_user),
) -> APIKeyResponse:
    """
    Create a new API key.

    This endpoint allows authenticated users to generate new API keys
    for programmatic access to the API.

    Args:
        request: API key creation request
        current_user: Current authenticated user

    Returns:
        APIKeyResponse: The created API key information including the actual key

    Raises:
        HTTPException: If key creation fails
    """
    try:
        # Check permissions
        if not any(role in getattr(current_user, "roles", []) for role in [UserRole.ADMIN, UserRole.DEVELOPER]):
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions to create API keys"
            )

        # Create the API key
        key_data = app.state.api_key_manager.generate_api_key(
            name=request.name,
            description=request.description,
            permissions=request.permissions,
            expires_days=request.expires_days,
            metadata={"created_by": current_user.user_id}
        )

        logger.info(f"Created API key '{request.name}' for user {current_user.user_id}")

        return APIKeyResponse(
            key=key_data["key"],  # Only returned on creation
            key_id=key_data["key_id"],
            name=key_data["name"],
            description=key_data["description"],
            status=key_data["status"],
            created_at=key_data["created_at"],
            expires_at=key_data["expires_at"],
            last_used=None,
            usage_count=0,
            permissions=key_data["permissions"]
        )

    except Exception as e:
        logger.error(f"API key creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create API key")


@app.post("/api/v1/auth/keys/dev", response_model=APIKeyResponse)
async def create_development_api_key() -> APIKeyResponse:
    """
    Create a development API key for testing (no authentication required).

    This endpoint is for development and testing purposes only.
    It creates an API key without requiring authentication.

    Returns:
        APIKeyResponse: The created development API key

    Raises:
        HTTPException: If key creation fails
    """
    try:
        # Create a development API key
        key_data = app.state.api_key_manager.generate_api_key(
            name=f"Development Key {datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            description="Development/testing API key created via /v1/auth/keys/dev endpoint",
            permissions=["*"],  # Full permissions for development
            expires_days=30,    # 30 days expiration
            metadata={"type": "development", "created_via": "dev_endpoint"}
        )

        logger.info(f"Created development API key: {key_data['key'][:15]}...")

        return APIKeyResponse(
            key=key_data["key"],
            key_id=key_data["key_id"],
            name=key_data["name"],
            description=key_data["description"],
            status=key_data["status"],
            created_at=key_data["created_at"],
            expires_at=key_data["expires_at"],
            last_used=None,
            usage_count=0,
            permissions=key_data["permissions"]
        )

    except Exception as e:
        logger.error(f"Development API key creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create development API key")


@app.get("/api/v1/auth/keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: JWTUser = Depends(get_current_user),
) -> List[APIKeyResponse]:
    """
    List all API keys for the current user.

    Args:
        current_user: Current authenticated user

    Returns:
        List of API key information (without the actual keys)

    Raises:
        HTTPException: If listing fails
    """
    try:
        # Check permissions
        if not any(role in getattr(current_user, "roles", []) for role in [UserRole.ADMIN, UserRole.DEVELOPER]):
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions to list API keys"
            )

        # Get all API keys
        keys = app.state.api_key_manager.list_api_keys()

        # Convert to response format
        response_keys = []
        for key_data in keys:
            response_keys.append(APIKeyResponse(
                key=None,  # Never return actual keys in list
                key_id=key_data["key_id"],
                name=key_data["name"],
                description=key_data["description"],
                status=key_data["status"],
                created_at=key_data["created_at"],
                expires_at=key_data["expires_at"],
                last_used=key_data["last_used"],
                usage_count=key_data["usage_count"],
                permissions=key_data["permissions"]
            ))

        return response_keys

    except Exception as e:
        logger.error(f"API key listing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list API keys")


@app.delete("/api/v1/auth/keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: JWTUser = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Revoke an API key.

    Args:
        key_id: The ID of the API key to revoke
        current_user: Current authenticated user

    Returns:
        Success message

    Raises:
        HTTPException: If revocation fails or key not found
    """
    try:
        # Check permissions
        if not any(role in getattr(current_user, "roles", []) for role in [UserRole.ADMIN, UserRole.DEVELOPER]):
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions to revoke API keys"
            )

        # Revoke the key
        success = app.state.api_key_manager.revoke_api_key(key_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail="API key not found"
            )

        logger.info(f"Revoked API key {key_id} by user {current_user.user_id}")

        return {"message": "API key revoked successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API key revocation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to revoke API key")


@app.get("/api/v1/auth/keys/stats", response_model=Dict[str, Any])
async def get_api_key_stats(
    current_user: JWTUser = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get API key usage statistics.

    Args:
        current_user: Current authenticated user

    Returns:
        Dictionary containing API key statistics

    Raises:
        HTTPException: If user lacks permissions
    """
    try:
        # Check permissions
        if UserRole.ADMIN not in getattr(current_user, "roles", []):
            raise HTTPException(
                status_code=403,
                detail="Admin permissions required for API key statistics"
            )

        stats = app.state.api_key_manager.get_stats()

        return {
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API key stats retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve API key statistics")


# Context Management Endpoints
@app.get("/api/v1/context/history", response_model=Dict[str, Any])
async def get_conversation_history(
    user_id: str,
    limit: int = 10,
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Get conversation history for a user.

    Args:
        user_id: User identifier
        limit: Maximum number of conversations to return
        api_key: API key for authentication

    Returns:
        Dictionary with conversation history

    Raises:
        HTTPException: If history retrieval fails
    """
    try:
        # Verify permissions
        await verify_permissions(api_key, "execute")

        # Get conversation history
        history = await app.state.context_manager.get_conversation_history(user_id, limit)

        return {
            "user_id": user_id,
            "history": history,
            "total_conversations": len(history)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation history")


@app.get("/api/v1/context/session/{session_id}", response_model=Dict[str, Any])
async def get_session_context(
    session_id: str,
    user_id: str,
    include_system: bool = True,
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Get conversation context for a specific session.

    Args:
        session_id: Session identifier
        user_id: User identifier
        include_system: Whether to include system messages
        api_key: API key for authentication

    Returns:
        Dictionary with session context

    Raises:
        HTTPException: If context retrieval fails
    """
    try:
        # Verify permissions
        await verify_permissions(api_key, "execute")

        # Get session context
        context = await app.state.context_manager.get_conversation_context(
            user_id, session_id, include_system
        )

        return {
            "session_id": session_id,
            "user_id": user_id,
            "context": context,
            "message_count": len(context),
            "include_system": include_system
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session context: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session context")


@app.get("/api/v1/context/stats")
async def context_stats():
    cm = getattr(app.state, "context_manager", None)
    if not cm:
        return {"enabled": False}
    if hasattr(cm, "get_stats"):
        try:
            stats = cm.get_stats()
        except Exception as e:  # pragma: no cover
            return {"enabled": True, "mode": cm.__class__.__name__, "error": str(e)}
        return {"enabled": True, "mode": cm.__class__.__name__, **stats}
    return {"enabled": True, "mode": cm.__class__.__name__}


@app.get("/api/v1/context/metrics", response_model=Dict[str, Any])
async def context_metrics():
    """Lightweight JSON metrics for context manager.

    This complements the Prometheus /metrics endpoint by exposing
    raw conversation/message counts and eviction stats in a simple
    JSON structure suitable for dashboards or health probes that
    don't parse Prometheus format.
    """
    cm = getattr(app.state, "context_manager", None)
    if not cm:
        return {"enabled": False, "reason": "context manager disabled"}
    base: Dict[str, Any] = {"enabled": True, "mode": cm.__class__.__name__}
    if hasattr(cm, "get_stats"):
        try:
            stats = cm.get_stats()
            # Add a derived field for average messages per conversation (avoid div by zero)
            total_conversations = stats.get("total_conversations", 0)
            total_messages = stats.get("total_messages", 0)
            if total_conversations:
                stats["avg_messages_per_conversation"] = round(total_messages / total_conversations, 2)
            else:
                stats["avg_messages_per_conversation"] = 0.0
            base.update(stats)
        except Exception as e:  # pragma: no cover
            base["error"] = str(e)
    return base


@app.post("/api/v1/context/cleanup")
async def cleanup_context(
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key)
) -> Dict[str, str]:
    """
    Trigger cleanup of expired conversations.

    Args:
        api_key: API key for authentication
        background_tasks: FastAPI background tasks

    Returns:
        Cleanup confirmation

    Raises:
        HTTPException: If cleanup fails
    """
    try:
        # Verify permissions
        await verify_permissions(api_key, "execute")

        # Schedule cleanup in background
        background_tasks.add_task(app.state.context_manager.cleanup_expired_sessions)

        return {"message": "Cleanup scheduled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to schedule cleanup: {e}")
        raise HTTPException(status_code=500, detail="Failed to schedule context cleanup")


# Error handlers
@app.exception_handler(ExecutionError)
async def execution_error_handler(request, exc: ExecutionError):
    """Handle execution errors with proper error response."""
    return JSONResponse(
        status_code=400,
        content={
            "error": "ExecutionError",
            "message": str(exc),
            "type": exc.__class__.__name__,
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": exc.detail,
            "status_code": exc.status_code,
        }
    )


def create_app() -> FastAPI:
    """
    Application factory function.

    Returns:
        Configured FastAPI application instance
    """
    return app


# Mount static files for Next.js frontend (must be after all API routes)
# Can be disabled with SERVE_FRONTEND=false (use separate frontend service)
serve_frontend = os.getenv("SERVE_FRONTEND", "true").lower() in {"1", "true", "yes"}

# Try multiple possible locations for static files
static_dir_options = [
    # Primary: Expected location in Railway container
    Path("/app/packages/web/out"),  # Where yarn workspace builds to
    # Fallback locations
    Path("/app/out"),  # If someone copies it to root
    # Repo-root based fallbacks (works both locally and in container)
    Path(__file__).resolve().parents[4] / "packages" / "web" / "out",
    Path(__file__).resolve().parents[4] / "out",  # Root out for local dev
    # Docusaurus fallback (if docs is used as marketing site)
    Path("/app/docs/build"),
    Path(__file__).resolve().parents[4] / "docs" / "build",
    # Additional absolute fallback
    Path("/app/web/out"),
]

static_dir = None
if serve_frontend:
    logger.info("🔍 Searching for frontend static files...")
    for option in static_dir_options:
        logger.info(f"   Checking: {option} - Exists: {option.exists()}")
        if option.exists():
            static_dir = option
            logger.info(f"✅ Found static directory at: {static_dir}")
            # List some contents to verify
            try:
                contents = list(static_dir.iterdir())[:5]
                logger.info(f"   Contains {len(list(static_dir.iterdir()))} items including: {[p.name for p in contents]}")
            except Exception as e:
                logger.warning(f"   Could not list directory contents: {e}")
            break

if serve_frontend and static_dir:
    # Mount Next.js specific static directories first for proper asset loading
    next_dir = static_dir / "_next"
    if next_dir.exists():
        app.mount("/_next", StaticFiles(directory=str(next_dir)), name="next-static")
        logger.info(f"✅ Next.js assets served from: {next_dir}")

    # Mount other static assets
    static_assets_dir = static_dir / "static"
    if static_assets_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_assets_dir)), name="static-assets")
        logger.info(f"✅ Static assets served from: {static_assets_dir}")

    # Mount favicon and other root files
    favicon_path = static_dir / "favicon.ico"
    if favicon_path.exists():
        @app.get("/favicon.ico")
        async def favicon():
            from fastapi.responses import FileResponse
            return FileResponse(str(favicon_path))

    # Mount the main static files with fallback to index.html for SPA routing
    # This MUST be last to act as a catch-all for SPA routing
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
    logger.info(f"✅ Frontend served from: {static_dir}")
else:
    logger.warning(f"❌ Static directory not found in any of: {[str(p) for p in static_dir_options]}. Frontend will not be served.")

    # Add fallback route when static files are not available
    @app.get("/")
    async def frontend_fallback():
        """Fallback route when frontend static files are not available."""
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Monkey Coder API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                .header { background: #f4f4f4; padding: 20px; border-radius: 5px; }
                .api-link { color: #007cba; text-decoration: none; }
                .api-link:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🐒 Monkey Coder API</h1>
                <p>FastAPI backend is running successfully!</p>
            </div>

            <h2>API Documentation</h2>
            <ul>
                <li><a href="/api/docs" class="api-link">Interactive API Documentation (Swagger)</a></li>
                <li><a href="/api/redoc" class="api-link">ReDoc API Documentation</a></li>
                <li><a href="/health" class="api-link">Health Check</a></li>
                <li><a href="/metrics" class="api-link">Prometheus Metrics</a></li>
            </ul>

            <h2>Available Endpoints</h2>
            <ul>
                <li><code>POST /api/v1/auth/login</code> - User authentication</li>
                <li><code>GET /api/v1/auth/status</code> - Authentication status</li>
                <li><code>POST /api/v1/auth/keys/dev</code> - <strong>Create development API key</strong> 🔑</li>
                <li><code>GET /api/v1/auth/keys</code> - List API keys</li>
                <li><code>POST /api/v1/execute</code> - Task execution</li>
                <li><code>GET /api/v1/billing/usage</code> - Usage metrics</li>
                <li><code>GET /api/v1/providers</code> - List AI providers</li>
                <li><code>GET /api/v1/models</code> - List available models</li>
                <li><code>GET /api/v1/capabilities</code> - System capabilities and features</li>
            </ul>

            <h2>🚀 Quick Start</h2>
            <p><strong>Get an API key for testing:</strong></p>
            <pre><code>curl -X POST https://your-domain.railway.app/api/v1/auth/keys/dev</code></pre>
            <p><strong>Then use it to test the API:</strong></p>
            <pre><code>curl -H "Authorization: Bearer mk-YOUR_KEY" https://your-domain.railway.app/api/v1/auth/status</code></pre>

            <p><em>Frontend static files not found. API endpoints are fully functional.</em></p>
        </body>
        </html>
        """)


if __name__ == "__main__":
    # Development server
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "monkey_coder.app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
        access_log=True,
    )
