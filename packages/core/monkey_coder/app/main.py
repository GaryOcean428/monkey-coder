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
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import base64
import json
import hmac
import hashlib
from urllib.parse import urlencode
from dataclasses import dataclass as _dc_dataclass
import secrets as _secrets

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse, Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, constr
from ..middleware.security_middleware import EnhancedSecurityMiddleware, CSPViolationReporter
from ..config.cors import CORS_CONFIG
import time
from pathlib import Path
from .streaming_endpoints import router as streaming_router
from .streaming_execute import router as streaming_execute_router

from ..core.orchestrator import MultiAgentOrchestrator
# Make quantum import optional for deployment (requires heavy ML dependencies)
try:
    from ..core.quantum_executor import QuantumExecutor
    QUANTUM_AVAILABLE = True
except ImportError:
    QUANTUM_AVAILABLE = False
    import warnings
    warnings.warn("QuantumExecutor not available - ML dependencies not installed", ImportWarning)
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
    create_access_token,
    create_refresh_token,
    verify_token,
)
from ..auth.enhanced_cookie_auth import enhanced_auth_manager
from ..auth.cookie_auth import get_current_user_from_cookie
# Make quantum monitoring optional for deployment
try:
    from ..monitoring import quantum_performance
    QUANTUM_MONITORING_AVAILABLE = True
except ImportError:
    QUANTUM_MONITORING_AVAILABLE = False
    # Create dummy quantum_performance for fallback
    class DummyQuantumPerformance:
        @staticmethod
        def get_summary():
            return {"status": "disabled", "reason": "ML dependencies not available"}
    quantum_performance = DummyQuantumPerformance()
from .. import monitoring as parent_monitoring
from ..database import run_migrations
from ..database.connection import get_database_connection
from ..email.sender import email_sender
from ..pricing import PricingMiddleware, load_pricing_from_file
from ..billing import StripeClient, BillingPortalSession
from .routes import stripe_checkout
from ..feedback_collector import FeedbackCollector
from ..database.models import User, AuthToken
from ..config.env_config import get_config
from ..auth import get_api_key_manager

# Import Railway-optimized logging first
from ..logging_utils import setup_logging, get_performance_logger
from ..cache.base import get_cache_registry_stats

# Import Railway monitoring and webhooks
from ..monitoring.railway_webhooks import (
    RailwayWebhookPayload, 
    handle_railway_webhook, 
    deployment_tracker, 
    alert_manager,
    verify_webhook_signature
)
from ..monitoring.health_dashboard import (
    get_health_monitor, 
    generate_dashboard_html
)
from ..monitoring.automated_rollback import (
    get_rollback_manager,
    RollbackReason
)
from ..monitoring.frontend_assets import (
    get_frontend_monitor
)

# Configure Railway-optimized logging
setup_logging()
logger = logging.getLogger(__name__)
performance_logger = get_performance_logger("app_performance")

# ---------------------------------------------------------------------------
# Production Redis-based rate limiting
# ---------------------------------------------------------------------------
from monkey_coder.middleware.rate_limiter import check_rate_limit

# -------------------------------------------------------------
# Host Validation Middleware (stricter than TrustedHost if set)
# -------------------------------------------------------------
class HostValidationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, allowed_hosts: list[str]):
        super().__init__(app)
        self.allowed_hosts = [h.lower() for h in allowed_hosts if h]

    async def dispatch(self, request: Request, call_next):  # pragma: no cover - thin wrapper
        host = request.headers.get("host", "").split(":")[0].lower()
        if self.allowed_hosts and "*" not in self.allowed_hosts:
            if host not in self.allowed_hosts:
                return JSONResponse({
                    "error": "untrusted_host",
                    "host": host,
                    "allowed": self.allowed_hosts
                }, status_code=421)
        return await call_next(request)


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

        # Initialize QuantumExecutor only if available
        if QUANTUM_AVAILABLE:
            app.state.quantum_executor = QuantumExecutor(provider_registry=app.state.provider_registry)
            logger.info("✅ QuantumExecutor initialized successfully")
        else:
            app.state.quantum_executor = None
            logger.info("ℹ️ QuantumExecutor disabled (ML dependencies not available)")

        app.state.persona_router = PersonaRouter()
        logger.info("✅ PersonaRouter initialized successfully")

        # Initialize monitoring components with graceful failure handling
        # Metrics collector initialization with robust guard
        raw_mc = getattr(parent_monitoring, "MetricsCollector", None)
        if callable(raw_mc):
            try:
                app.state.metrics_collector = raw_mc()
                app.state.metrics_active = True
                logger.info("✅ MetricsCollector initialized successfully")
            except Exception as e:
                logger.error(f"❌ MetricsCollector initialization failed: {e}")
                app.state.metrics_active = False
        else:
            logger.warning("⚠️ MetricsCollector symbol missing or not callable - using placeholder")
            class PlaceholderMetricsCollector:  # pragma: no cover - trivial
                def start_execution(self, request): return "placeholder"
                def complete_execution(self, execution_id, response): pass
                def record_error(self, execution_id, error): pass
                def record_http_request(self, method, endpoint, status, duration): pass
                def get_prometheus_metrics(self): return "# Metrics collector not available\n"
            app.state.metrics_collector = PlaceholderMetricsCollector()
            app.state.metrics_active = False

        try:
            app.state.billing_tracker = parent_monitoring.BillingTracker()
            logger.info("✅ BillingTracker initialized successfully")
        except (AttributeError, TypeError):
            logger.warning("⚠️ BillingTracker not available - using placeholder")
            # Create a placeholder billing tracker
            class PlaceholderBillingTracker:
                async def track_usage(self, api_key, usage): pass
                async def get_usage(self, api_key, start_date, end_date, granularity):
                    return type('obj', (object,), {
                        'api_key_hash': 'placeholder',
                        'period': 'N/A',
                        'total_requests': 0,
                        'total_tokens': 0,
                        'total_cost': 0.0,
                        'provider_breakdown': {},
                        'execution_stats': {},
                        'rate_limit_status': {}
                    })()
            app.state.billing_tracker = PlaceholderBillingTracker()

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

        # Start periodic context cleanup task only if context manager is enabled
        if enable_context and app.state.context_manager is not None:
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
        else:
            app.state.cleanup_task = None
            logger.info("ℹ️ Periodic context cleanup disabled (context manager not available)")

        # Initialize providers with timeout
        await app.state.provider_registry.initialize_all()
        logger.info("✅ All providers initialized successfully")

        # Initialize A2A server if enabled
        enable_a2a = os.getenv("ENABLE_A2A_SERVER", "true").lower() == "true"
        if enable_a2a:
            try:
                from ..a2a_server import MonkeyCoderA2AAgent
                a2a_port = int(os.getenv("A2A_PORT", "7702"))
                app.state.a2a_agent = MonkeyCoderA2AAgent(port=a2a_port)
                await app.state.a2a_agent.initialize()
                
                # Start A2A server in background task
                async def start_a2a_server():
                    try:
                        await app.state.a2a_agent.start()
                    except Exception as e:
                        logger.error(f"A2A server failed: {e}")
                
                app.state.a2a_task = asyncio.create_task(start_a2a_server())
                logger.info(f"✅ A2A server initialized on port {a2a_port}")
            except Exception as e:
                logger.error(f"❌ A2A server initialization failed: {e}")
                app.state.a2a_agent = None
                app.state.a2a_task = None
        else:
            app.state.a2a_agent = None
            app.state.a2a_task = None
            logger.info("ℹ️ A2A server disabled (ENABLE_A2A_SERVER=false)")

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
    if hasattr(app.state, 'cleanup_task') and app.state.cleanup_task is not None:
        try:
            app.state.cleanup_task.cancel()
            try:
                await app.state.cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("Periodic cleanup task cancelled")
        except Exception as e:
            logger.warning(f"Could not cancel cleanup task cleanly: {e}")

    # Stop A2A server
    if hasattr(app.state, 'a2a_agent') and app.state.a2a_agent is not None:
        try:
            await app.state.a2a_agent.stop()
            logger.info("A2A server stopped")
        except Exception as e:
            logger.warning(f"Could not stop A2A server cleanly: {e}")
    
    if hasattr(app.state, 'a2a_task') and app.state.a2a_task is not None:
        try:
            app.state.a2a_task.cancel()
            try:
                await app.state.a2a_task
            except asyncio.CancelledError:
                pass
            logger.info("A2A server task cancelled")
        except Exception as e:
            logger.warning(f"Could not cancel A2A task cleanly: {e}")

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

# Add enhanced security middleware with Railway optimizations
enable_security_headers = middleware_config._get_env_bool("ENABLE_SECURITY_HEADERS", True)
if enable_security_headers:
    app.add_middleware(EnhancedSecurityMiddleware, enable_csp=True, enable_cors_headers=True)
    app.add_middleware(CSPViolationReporter)  # For monitoring CSP violations

# Add other middleware with environment-aware configuration
# Use improved CORS configuration with Railway support
if middleware_config.environment == "production":
    # Production: use CORS_CONFIG for proper credential handling
    cors_config = CORS_CONFIG.copy()

    # Ensure Railway's internal routing is permitted
    allowed_hosts = [
        h.strip() for h in middleware_config._get_env("TRUSTED_HOSTS", "").split(",")
        if h.strip()
    ]
    if not any("railway.internal" in h for h in allowed_hosts):
        allowed_hosts.append("*.railway.internal")

    # Add Railway public domain to CORS origins if not already present
    public_domain = middleware_config._get_env("RAILWAY_PUBLIC_DOMAIN", "").strip()
    if public_domain:
        cors_config["allow_origins"].extend([
            f"https://{public_domain}",
            f"http://{public_domain}"
        ])
else:
    # Development: keep permissive defaults but use CORS_CONFIG structure
    cors_config = CORS_CONFIG.copy()
    cors_config["allow_origins"] = ["*"]
    allowed_hosts = ["*"]

app.add_middleware(
    CORSMiddleware,
    **cors_config
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts
)

# Add Sentry middleware for error tracking
try:  # Some type checkers complain; runtime still fine
    app.add_middleware(SentryAsgiMiddleware)  # type: ignore[arg-type]
except Exception as e:  # pragma: no cover
    logger.warning(f"Sentry middleware not added: {e}")

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
    metrics_active: Optional[bool] = Field(None, description="Whether metrics collector initialized")
    providers_ready: Optional[bool] = Field(None, description="Provider registry readiness")
    frontend_served: Optional[bool] = Field(None, description="Whether static frontend was mounted")
    frontend_index_hash: Optional[str] = Field(None, description="SHA256 fingerprint of index.html if present")
    trusted_hosts: Optional[List[str]] = Field(None, description="Configured trusted hosts for Host validation")


# Authentication Models
class LoginRequest(BaseModel):
    """Login request model."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class SignupRequest(BaseModel):
    """Signup request model."""
    username: str = Field(..., description="Username for the account")
    name: str = Field(..., description="Full name of the user")
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password", min_length=8)
    plan: Optional[str] = Field("free", description="Subscription plan (free, pro, enterprise)")


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


class CacheStatsResponse(BaseModel):
    """Response model for cache statistics endpoint."""
    caches: Dict[str, Any]
    aggregate: Dict[str, Any]
    timestamp: str
    feature_flags: Dict[str, Any]


@app.get("/api/v1/cache/stats", response_model=CacheStatsResponse)
async def cache_stats():
    """Return aggregated statistics for all registered caches.

    Includes per-cache metrics plus aggregate totals and feature flag states.
    """
    stats = get_cache_registry_stats()
    flags = {
        "ENABLE_RESULT_CACHE": os.getenv("ENABLE_RESULT_CACHE", "true"),
        "ENABLE_CONTEXT_MANAGER": os.getenv("ENABLE_CONTEXT_MANAGER", "true"),
    }
    return CacheStatsResponse(
        caches=stats["caches"],
        aggregate=stats["aggregate"],
        timestamp=datetime.utcnow().isoformat() + "Z",
        feature_flags=flags,
    )


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str = Field(..., description="JWT refresh token")


# Root endpoint removed to allow Next.js static files to be served at root path


@app.get("/health", response_model=HealthResponse)
@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint optimized for Railway deployment.

    This endpoint provides comprehensive health status including:
    - System resource metrics (memory, CPU)
    - Component initialization status
    - Dependency availability
    - Performance metrics for Railway monitoring

    Returns 200 OK even during partial initialization to prevent
    Railway deployment failures during startup phase.
    """
    from datetime import datetime
    import psutil

    # Get system metrics safely
    try:
        process = psutil.Process()
        memory_mb = round(process.memory_info().rss / 1024 / 1024, 2)
        cpu_percent = process.cpu_percent()
    except Exception:
        memory_mb = 0
        cpu_percent = 0

    # Check component health with graceful degradation
    components = {}

    # Core components that should be available
    essential_components = [
        ("orchestrator", "orchestrator"),
        ("quantum_executor", "quantum_executor"),
        ("persona_router", "persona_router"),
        ("provider_registry", "provider_registry")
    ]

    for component_name, state_attr in essential_components:
        try:
            if hasattr(app.state, state_attr) and getattr(app.state, state_attr) is not None:
                components[component_name] = "active"
            else:
                components[component_name] = "initializing"
        except Exception:
            components[component_name] = "initializing"

    # Optional components that may not be available
    optional_components = [
        ("metrics_collector", "metrics_collector"),
        ("billing_tracker", "billing_tracker"),
        ("context_manager", "context_manager"),
        ("api_key_manager", "api_key_manager")
    ]

    for component_name, state_attr in optional_components:
        try:
            if hasattr(app.state, state_attr) and getattr(app.state, state_attr) is not None:
                components[component_name] = "active"
            else:
                components[component_name] = "optional"
        except Exception:
            components[component_name] = "optional"

    # Determine overall health status
    essential_active = all(
        components.get(comp, "inactive") == "active"
        for comp, _ in essential_components
    )

    # Report as healthy if essential components are active, or if we're still initializing
    health_status = "healthy" if essential_active else "initializing"

    # Log health check for monitoring with enhanced metrics
    performance_logger.logger.info(
        "Health check performed",
        extra={'extra_fields': {
            'metric_type': 'health_check',
            'memory_mb': memory_mb,
            'cpu_percent': cpu_percent,
            'components': components,
            'essential_components_active': essential_active,
            'health_status': health_status,
            'qwen_agent_available': 'qwen_agent' in globals(),
            'startup_phase': not essential_active
        }}
    )

    frontend_info = getattr(app.state, 'frontend_build', {})
    trusted_hosts_env = os.getenv("TRUSTED_HOSTS", "*")
    host_list = [h for h in trusted_hosts_env.replace(";", ",").split(",") if h]
    return HealthResponse(
        status=health_status,
        version="2.0.0",  # Updated to Phase 2.0
        timestamp=datetime.utcnow().isoformat() + 'Z',
        components=components,
        metrics_active=getattr(app.state, 'metrics_active', None),
        providers_ready=components.get("provider_registry") == "active",
        frontend_served=frontend_info.get("served"),
        frontend_index_hash=frontend_info.get("index_hash"),
        trusted_hosts=host_list
    )

# ---------------- Environment Config Validator -----------------
CRITICAL_SECRETS = ["DATABASE_URL", "JWT_SECRET_KEY", "OPENAI_API_KEY"]
RECOMMENDED_SECRETS = ["SENTRY_DSN", "STRIPE_SECRET_KEY", "ANTHROPIC_API_KEY"]

def validate_env_config():
    missing_critical = [k for k in CRITICAL_SECRETS if not os.getenv(k)]
    missing_recommended = [k for k in RECOMMENDED_SECRETS if not os.getenv(k)]
    anomalies = [k for k in os.environ.keys() if k.startswith("NEXT_PUBLIC_") and k.endswith("SECRET")]
    return {
        "missing_critical": missing_critical,
        "missing_recommended": missing_recommended,
        "anomalies": anomalies,
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }

@app.get("/health/env")
async def env_health():  # pragma: no cover - simple diagnostic
    return validate_env_config()


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


@app.get("/health/secrets")
async def secrets_health_check():
    """
    Secrets security health check for production monitoring.

    Returns detailed status of API keys, credentials, and security configuration
    without exposing sensitive values.
    """
    from ..config.production_config import get_production_config
    from ..config.secrets_config import validate_production_secrets

    try:
        secrets_health = validate_production_secrets()
        prod_config = get_production_config()
        rotation_strategy = prod_config.get_secrets_rotation_schedule()

        response_data = {
            "secrets_health": secrets_health,
            "rotation_strategy": {
                "schedule": rotation_strategy.get("rotation_schedule", {}),
                "next_recommended_rotation": "Within 30 days for any keys over 60 days old"
            },
            "security_recommendations": secrets_health.get("recommendations", [])
        }

        # Determine overall security status
        status_code = 200
        if secrets_health["overall_status"] == "critical":
            status_code = 503
        elif secrets_health["overall_status"] == "warning":
            status_code = 200  # Warning is still operational

        return JSONResponse(
            content=response_data,
            status_code=status_code
        )

    except Exception as e:
        return JSONResponse(
            content={"error": f"Secrets health check failed: {str(e)}"},
            status_code=500
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


# ---------------------------------------------------------------------------
# Railway Deployment Webhooks and Monitoring
# ---------------------------------------------------------------------------

@app.post("/api/v1/railway/webhook")
async def railway_webhook_handler(
    request: Request, 
    background_tasks: BackgroundTasks
):
    """
    Handle Railway deployment webhooks for monitoring and alerting.
    
    Processes deployment status updates, tracks metrics, and triggers alerts
    for deployment failures or health check issues.
    """
    try:
        # Get raw payload for signature verification
        raw_payload = await request.body()
        
        # Verify webhook signature if secret is configured
        signature = request.headers.get("X-Railway-Signature", "")
        webhook_secret = os.getenv("RAILWAY_WEBHOOK_SECRET", "")
        
        if webhook_secret and not verify_webhook_signature(
            raw_payload.decode(), signature, webhook_secret
        ):
            logger.warning("Invalid Railway webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse payload
        payload_data = json.loads(raw_payload)
        payload = RailwayWebhookPayload(**payload_data)
        
        # Process webhook
        result = await handle_railway_webhook(payload, background_tasks)
        
        # Check for automated rollback
        if payload.deployment:
            deployment_id = payload.deployment.get("id", "")
            rollback_manager = get_rollback_manager()
            
            # Add rollback monitoring task
            background_tasks.add_task(
                rollback_manager.monitor_deployment,
                deployment_tracker.deployments.get(deployment_id)
            )
        
        logger.info(f"Railway webhook processed: {payload.type}")
        return result
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Railway webhook payload")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"Railway webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")


@app.get("/api/v1/railway/metrics")
async def railway_deployment_metrics(hours: int = 24):
    """
    Get Railway deployment metrics and statistics.
    
    Returns deployment success rates, average startup times,
    and failure analysis for the specified time period.
    """
    try:
        success_rate = deployment_tracker.get_success_rate(hours=hours)
        startup_times = deployment_tracker.get_average_startup_time(hours=hours)
        
        # Get recent deployments for analysis
        recent_deployments = [
            {
                "deployment_id": d.deployment_id,
                "status": d.status.value,
                "start_time": d.start_time.isoformat(),
                "end_time": d.end_time.isoformat() if d.end_time else None,
                "duration": d.deployment_duration,
                "health_check_passed": d.health_check_passed,
                "health_check_duration": d.health_check_duration
            }
            for d in list(deployment_tracker.deployments.values())[-10:]  # Last 10 deployments
        ]
        
        return {
            "success_rate": success_rate,
            "startup_times": startup_times,
            "recent_deployments": recent_deployments,
            "query_period_hours": hours,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get Railway metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")


@app.post("/api/v1/railway/health-check")
async def railway_health_check_callback(
    deployment_id: str,
    duration: float,
    passed: bool,
    background_tasks: BackgroundTasks
):
    """
    Record health check results for Railway deployments.
    
    This endpoint is called by deployment scripts to record
    health check timing and success status.
    """
    try:
        # Update deployment metrics with health check results
        if deployment_id in deployment_tracker.deployments:
            metrics = deployment_tracker.deployments[deployment_id]
            metrics.health_check_passed = passed
            metrics.health_check_duration = duration
            deployment_tracker._save_metrics()
            
            # Check for alerts
            if duration > 30 or not passed:
                background_tasks.add_task(
                    alert_manager.check_health_failure, 
                    deployment_id, 
                    duration
                )
        
        return {
            "status": "recorded",
            "deployment_id": deployment_id,
            "health_check_passed": passed,
            "duration": duration
        }
        
    except Exception as e:
        logger.error(f"Failed to record health check: {e}")
        raise HTTPException(status_code=500, detail=f"Health check recording failed: {str(e)}")


@app.get("/api/v1/railway/dashboard", response_class=HTMLResponse)
async def railway_health_dashboard():
    """
    Railway health monitoring dashboard.
    
    Provides a web-based dashboard for monitoring deployment health,
    component status, and performance metrics.
    """
    try:
        # Get or initialize health monitor
        deployment_url = os.getenv("RAILWAY_DEPLOYMENT_URL", "https://coder.fastmonkey.au")
        monitor = get_health_monitor(deployment_url)
        
        # Perform immediate health check
        await monitor.check_all_components()
        
        # Get dashboard data
        dashboard_data = monitor.get_dashboard_data()
        
        # Generate HTML dashboard
        html_content = generate_dashboard_html(dashboard_data)
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to generate health dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")


@app.get("/api/v1/railway/dashboard/data")
async def railway_dashboard_data():
    """
    Get Railway dashboard data as JSON.
    
    Returns the same data as the dashboard but in JSON format
    for API consumption or custom dashboard implementations.
    """
    try:
        # Get or initialize health monitor
        deployment_url = os.getenv("RAILWAY_DEPLOYMENT_URL", "https://coder.fastmonkey.au")
        monitor = get_health_monitor(deployment_url)
        
        # Perform immediate health check
        await monitor.check_all_components()
        
        # Return dashboard data
        return monitor.get_dashboard_data()
        
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard data retrieval failed: {str(e)}")


@app.get("/api/v1/railway/dashboard/component/{component_name}/history")
async def component_health_history(component_name: str, hours: int = 1):
    """
    Get health history for a specific component.
    
    Returns detailed health check history for monitoring trends
    and diagnosing intermittent issues.
    """
    try:
        deployment_url = os.getenv("RAILWAY_DEPLOYMENT_URL", "https://coder.fastmonkey.au")
        monitor = get_health_monitor(deployment_url)
        
        history = monitor.get_component_history(component_name, hours)
        
        return {
            "component_name": component_name,
            "history": history,
            "query_period_hours": hours,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get component history: {e}")
        raise HTTPException(status_code=500, detail=f"Component history retrieval failed: {str(e)}")


@app.post("/api/v1/railway/monitoring/start")
async def start_health_monitoring():
    """
    Start continuous health monitoring.
    
    Begins automated health checking of all components
    with configurable intervals and alerting.
    """
    try:
        deployment_url = os.getenv("RAILWAY_DEPLOYMENT_URL", "https://coder.fastmonkey.au")
        monitor = get_health_monitor(deployment_url)
        
        await monitor.start_monitoring()
        
        return {
            "status": "monitoring_started",
            "deployment_url": deployment_url,
            "monitoring_interval": monitor.monitoring_interval,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to start monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Monitoring start failed: {str(e)}")


@app.post("/api/v1/railway/monitoring/stop")
async def stop_health_monitoring():
    """
    Stop continuous health monitoring.
    
    Stops the automated health checking background task.
    """
    try:
        deployment_url = os.getenv("RAILWAY_DEPLOYMENT_URL", "https://coder.fastmonkey.au")
        monitor = get_health_monitor(deployment_url)
        
        await monitor.stop_monitoring()
        
        return {
            "status": "monitoring_stopped",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to stop monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Monitoring stop failed: {str(e)}")


@app.get("/api/v1/railway/rollback/status")
async def rollback_status():
    """
    Get automated rollback system status and configuration.
    
    Returns rollback settings, recent rollback history,
    and system health for rollback capability.
    """
    try:
        rollback_manager = get_rollback_manager()
        stats = rollback_manager.get_rollback_stats(hours=24)
        
        return {
            "rollback_system": {
                "enabled": rollback_manager.rollback_enabled,
                "startup_timeout": rollback_manager.startup_timeout,
                "health_check_timeout": rollback_manager.health_check_timeout,
                "crash_threshold": rollback_manager.crash_threshold,
                "crash_window": rollback_manager.crash_window
            },
            "statistics": stats,
            "api_configured": rollback_manager.api_token is not None,
            "project_id": rollback_manager.project_id,
            "service_id": rollback_manager.service_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get rollback status: {e}")
        raise HTTPException(status_code=500, detail=f"Rollback status retrieval failed: {str(e)}")


@app.post("/api/v1/railway/rollback/manual")
async def manual_rollback(
    current_deployment_id: str,
    target_deployment_id: str = None,
    reason: str = "manual_trigger"
):
    """
    Trigger a manual rollback to a previous deployment.
    
    Allows manual rollback when automated rollback is not triggered
    or when specific deployment targeting is needed.
    """
    try:
        rollback_manager = get_rollback_manager()
        
        # Find target deployment if not specified
        if not target_deployment_id:
            target_deployment_id = await rollback_manager.find_previous_stable_deployment(current_deployment_id)
            if not target_deployment_id:
                raise HTTPException(
                    status_code=404, 
                    detail="No stable deployment found for rollback"
                )
        
        # Convert reason string to enum
        rollback_reason = RollbackReason.MANUAL_TRIGGER
        if reason in RollbackReason._value2member_map_:
            rollback_reason = RollbackReason(reason)
        
        # Execute rollback
        rollback_event = await rollback_manager.execute_rollback(
            current_deployment_id,
            target_deployment_id,
            rollback_reason
        )
        
        return {
            "rollback_initiated": True,
            "rollback_event": rollback_event.to_dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Manual rollback failed: {e}")
        raise HTTPException(status_code=500, detail=f"Manual rollback failed: {str(e)}")


@app.get("/api/v1/railway/rollback/history")
async def rollback_history(hours: int = 24):
    """
    Get rollback history and statistics.
    
    Returns detailed rollback events, success rates,
    and analysis for the specified time period.
    """
    try:
        rollback_manager = get_rollback_manager()
        
        # Get recent rollback events
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent_events = [
            event.to_dict() for event in rollback_manager.rollback_history
            if event.timestamp >= cutoff
        ]
        
        # Get statistics
        stats = rollback_manager.get_rollback_stats(hours=hours)
        
        return {
            "rollback_events": recent_events,
            "statistics": stats,
            "query_period_hours": hours,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get rollback history: {e}")
        raise HTTPException(status_code=500, detail=f"Rollback history retrieval failed: {str(e)}")


@app.post("/api/v1/railway/rollback/configure")
async def configure_rollback(
    enabled: bool = True,
    startup_timeout: int = 300,
    health_check_timeout: int = 30,
    crash_threshold: int = 3,
    crash_window: int = 600
):
    """
    Configure automated rollback system parameters.
    
    Updates rollback thresholds and behavior settings
    for fine-tuning automated rollback triggers.
    """
    try:
        rollback_manager = get_rollback_manager()
        
        # Update configuration
        rollback_manager.rollback_enabled = enabled
        rollback_manager.startup_timeout = startup_timeout
        rollback_manager.health_check_timeout = health_check_timeout
        rollback_manager.crash_threshold = crash_threshold
        rollback_manager.crash_window = crash_window
        
        # Save configuration to environment or config file
        config_file = "data/rollback_config.json"
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        config = {
            "enabled": enabled,
            "startup_timeout": startup_timeout,
            "health_check_timeout": health_check_timeout,
            "crash_threshold": crash_threshold,
            "crash_window": crash_window,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return {
            "configuration_updated": True,
            "config": config,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to configure rollback: {e}")
        raise HTTPException(status_code=500, detail=f"Rollback configuration failed: {str(e)}")


@app.get("/api/v1/railway/frontend/status")
async def frontend_asset_status():
    """
    Get frontend asset availability and health status.
    
    Returns comprehensive frontend asset monitoring data including
    file availability, response times, and integrity checks.
    """
    try:
        deployment_url = os.getenv("RAILWAY_DEPLOYMENT_URL", "https://coder.fastmonkey.au")
        frontend_path = os.getenv("FRONTEND_OUT_PATH", "/app/packages/web/out")
        
        monitor = get_frontend_monitor(deployment_url, frontend_path)
        
        # Perform asset check
        health_check = await monitor.comprehensive_asset_check()
        
        # Get detailed asset information
        asset_details = monitor.get_asset_details()
        
        # Get availability trend
        availability_trend = monitor.get_availability_trend(hours=6)
        
        return {
            "health_check": health_check.to_dict(),
            "asset_details": asset_details,
            "availability_trend": availability_trend,
            "deployment_url": deployment_url,
            "frontend_path": frontend_path,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get frontend status: {e}")
        raise HTTPException(status_code=500, detail=f"Frontend status retrieval failed: {str(e)}")


@app.get("/api/v1/railway/frontend/assets")
async def frontend_asset_details():
    """
    Get detailed frontend asset information.
    
    Returns per-asset details including sizes, checksums,
    and availability status for monitoring and debugging.
    """
    try:
        deployment_url = os.getenv("RAILWAY_DEPLOYMENT_URL", "https://coder.fastmonkey.au")
        frontend_path = os.getenv("FRONTEND_OUT_PATH", "/app/packages/web/out")
        
        monitor = get_frontend_monitor(deployment_url, frontend_path)
        
        return monitor.get_asset_details()
        
    except Exception as e:
        logger.error(f"Failed to get asset details: {e}")
        raise HTTPException(status_code=500, detail=f"Asset details retrieval failed: {str(e)}")


@app.get("/api/v1/railway/frontend/verify")
async def verify_frontend_assets():
    """
    Verify frontend asset integrity and availability.
    
    Performs immediate verification of all critical frontend assets
    and returns success/failure status for deployment validation.
    """
    try:
        deployment_url = os.getenv("RAILWAY_DEPLOYMENT_URL", "https://coder.fastmonkey.au")
        frontend_path = os.getenv("FRONTEND_OUT_PATH", "/app/packages/web/out")
        
        monitor = get_frontend_monitor(deployment_url, frontend_path)
        
        # Perform comprehensive check
        health_check = await monitor.comprehensive_asset_check()
        
        # Determine if verification passed
        verification_passed = (
            health_check.overall_status in ["healthy", "degraded"] and
            len(health_check.critical_assets_missing) == 0
        )
        
        return {
            "verification_passed": verification_passed,
            "overall_status": health_check.overall_status,
            "assets_checked": health_check.assets_checked,
            "assets_available": health_check.assets_available,
            "critical_assets_missing": health_check.critical_assets_missing,
            "warnings": health_check.warnings,
            "avg_response_time": health_check.avg_response_time,
            "total_size_mb": health_check.total_size_mb,
            "timestamp": health_check.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Frontend verification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Frontend verification failed: {str(e)}")


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
# ---------------------------------------------------------------------------
# TODO (Auth Hardening Roadmap):
# 1. Implement password reset flow:
#    - POST /api/v1/auth/password/forgot  (accepts email, always 200, enqueue email)
#    - POST /api/v1/auth/password/reset   (accepts token + new_password)
#    Requires new tables: auth_tokens (purpose=password_reset, token_hash, expires_at, used_at)
# 2. Implement email verification (purpose=email_verify) gating elevated actions.
# 3. Replace in-memory sessions with persistent store (database or Redis) and refresh token rotation.
# 4. Integrate OAuth (Google/GitHub) via NextAuth SSR route and backend token bridging endpoint.
# 5. Enforce CSRF validation on state-changing endpoints or migrate fully to Authorization header for SPA.
# ---------------------------------------------------------------------------
 # (Removed duplicate local imports moved to top)

"""Lightweight CSRF enforcement helper & OAuth scaffolding.

We already issue a CSRF token cookie (see enhanced_cookie_auth). For state changing
endpoints that rely on cookie auth we add an explicit header vs cookie equality
check. This is intentionally simple and can be expanded later (e.g., double-submit
token bound to session, rotating tokens, or SameSite=strict cookies).

OAuth endpoints are scaffolded (return 501) so that frontend integration can
begin without backend implementation being complete.
"""

CSRF_HEADER_NAME = "X-CSRF-Token"

def _enforce_csrf(request: Request) -> None:
    """Raise 403 if CSRF validation fails (simple header==cookie check).

    Safe methods are skipped. If CSRF protection disabled in config this is a no-op.
    Fails closed (403) on unexpected errors.
    """
    try:
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return
        cfg = getattr(enhanced_auth_manager, "config", None)
        if not cfg or not cfg.enable_csrf_protection:
            return
        header_token = request.headers.get(CSRF_HEADER_NAME)
        cookie_token = request.cookies.get(cfg.csrf_token_name)
        if not header_token or not cookie_token or header_token != cookie_token:
            raise HTTPException(status_code=403, detail="CSRF token missing or mismatch")
    except HTTPException:
        raise
    except Exception as err:  # pragma: no cover - defensive
        logger.error(f"CSRF enforcement error: {err}")
        raise HTTPException(status_code=403, detail="CSRF validation failed")

# Password reset token storage (DB preferred, fallback to in-memory for environments without migrations)
@_dc_dataclass
class _PasswordResetToken:
    user_id: str
    token_hash: str
    expires_at: datetime
    used: bool = False

_PASSWORD_RESET_TOKENS: Dict[str, _PasswordResetToken] = {}

def _hash_reset_token(token: str) -> str:
    # Simple constant-time comparable hash (could switch to bcrypt/sha256 + pepper)
    import hashlib
    return hashlib.sha256(token.encode('utf-8')).hexdigest()

def _generate_reset_token() -> str:
    return _secrets.token_urlsafe(32)

class PasswordResetRequest(BaseModel):
    email: str
    @classmethod
    def model_validate(cls, value):  # fallback for pydantic v2 custom quick validation
        obj = super().model_validate(value)
        # Minimal format check to avoid user enumeration difference
        if '@' not in obj.email:
            # Normalize invalid format to generic response path
            obj.email = obj.email.strip().lower()
        else:
            obj.email = obj.email.strip().lower()
        return obj

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: constr(min_length=8)  # type: ignore

@app.post("/api/v1/auth/password/forgot")
async def request_password_reset(payload: PasswordResetRequest, request: Request):
    """Initiate password reset (always 200). Uses DB auth_tokens when available."""
    try:
        await check_rate_limit(request, "password_forgot")
        user = await User.get_by_email(payload.email)
        if user and user.id:
            raw_token = _generate_reset_token()
            token_hash = _hash_reset_token(raw_token)
            expires_at = datetime.utcnow() + timedelta(minutes=30)
            # Try DB persistence first
            db_ok = False
            try:
                await AuthToken.create(
                    user_id=user.id,
                    purpose="password_reset",
                    token_hash=token_hash,
                    expires_at=expires_at,
                    metadata={"delivery": "debug_return" if os.environ.get("ENV", "development") != "production" else "email"}
                )
                db_ok = True
            except Exception as db_err:  # fallback
                logger.warning(f"AuthToken DB create failed, using in-memory fallback: {db_err}")
                _PASSWORD_RESET_TOKENS[token_hash] = _PasswordResetToken(
                    user_id=user.id,
                    token_hash=token_hash,
                    expires_at=expires_at
                )
            response = {"status": "ok"}
            if os.environ.get("ENV", "development") != "production":
                response["debug_token"] = raw_token
                response["storage"] = "db" if db_ok else "memory"
            return response
        return {"status": "ok"}
    except HTTPException as he:
        # Propagate rate limiting (429) while masking other auth-related errors
        if he.status_code == 429:
            raise
        logger.error(f"Password reset request HTTP error (masked to ok): {he}")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        return {"status": "ok"}

@app.post("/api/v1/auth/password/reset")
async def confirm_password_reset(payload: PasswordResetConfirm, request: Request):
    """Confirm password reset with a token and new password (DB first, fallback memory)."""
    try:
        _enforce_csrf(request)
        token_hash = _hash_reset_token(payload.token)
        # Try DB lookup first
        entry_db = None
        try:
            entry_db = await AuthToken.get_valid(token_hash, "password_reset")
        except Exception as db_err:
            logger.warning(f"AuthToken DB lookup failed, will attempt in-memory: {db_err}")

        if entry_db:
            user = await User.get_by_id(entry_db.user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            from ..security import hash_password
            new_hash = hash_password(payload.new_password)
            await user.update_password(new_hash)
            await entry_db.mark_used()
            return {"status": "password_reset"}

        # Fallback in-memory token handling
        entry_mem = _PASSWORD_RESET_TOKENS.get(token_hash)
        if not entry_mem or entry_mem.used or datetime.utcnow() > entry_mem.expires_at:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        user = await User.get_by_id(entry_mem.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        from ..security import hash_password
        new_hash = hash_password(payload.new_password)
        await user.update_password(new_hash)
        entry_mem.used = True
        del _PASSWORD_RESET_TOKENS[token_hash]
        return {"status": "password_reset"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset confirm error: {e}")
        raise HTTPException(status_code=400, detail="Password reset failed")


# ---------------------------------------------------------------------------
# Email Verification Endpoints
# ---------------------------------------------------------------------------
class EmailVerificationRequest(BaseModel):
    email: Optional[str] = None

class EmailVerificationConfirm(BaseModel):
    token: str

@app.post("/api/v1/auth/verify/email/request")
async def request_email_verification(payload: EmailVerificationRequest, request: Request):
    """Issue an email verification token (idempotent). Always returns 200."""
    # Rate limit
    check_rate_limit(request, "email_verify")
    email = (payload.email or "").strip().lower()
    user: Optional[User] = None
    if email:
        try:
            user = await User.get_by_email(email)
        except Exception as e:
            if 'another operation is in progress' in str(e).lower():
                logger.warning("DB contention during email verification request; proceeding without user binding")
                user = None
            else:
                raise
    # If user not found or email omitted, we still respond generically
    if user and user.is_verified:
        return {"status": "email_verification_already"}
    # Generate token
    raw_token = _b64url(os.urandom(32))
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(hours=24)
    stored_db = False
    if user:
        try:
            await AuthToken.create(
                user_id=str(user.id),
                purpose="email_verify",
                token_hash=token_hash,
                expires_at=expires_at,
                metadata={"email": user.email}
            )
            stored_db = True
        except Exception as e:
            logger.warning(f"Email verify DB token create failed (fallback to memory): {e}")
    if not stored_db:
        _EMAIL_VERIFY_TOKENS[token_hash] = {
            "email": email,
            "expires_at": expires_at,
            "used": False
        }
    # Simulate sending email (debug token exposed in non-production)
    env = os.getenv("ENV", "development")
    resp = {"status": "email_verification_issued"}
    if user:
        # fire and forget (no await block issues if we want concurrency — but keep await for test determinism)
        try:
            await email_sender.send_email_verification(user.email, raw_token)
        except Exception as e:
            logger.warning(f"Email send failed (non-fatal): {e}")
    if env != "production":
        resp["debug_token"] = raw_token
    return resp

@app.post("/api/v1/auth/verify/email/confirm")
async def confirm_email_verification(payload: EmailVerificationConfirm):
    token_hash = hashlib.sha256(payload.token.encode()).hexdigest()
    # Try DB first
    try:
        entry_db = await AuthToken.get_valid(token_hash, "email_verify")
        if entry_db:
            user = await User.get_by_id(entry_db.user_id)
            if user and not user.is_verified:
                user.is_verified = True
                user.updated_at = datetime.utcnow()
                pool = await get_database_connection()
                async with pool.acquire() as connection:
                    await connection.execute("UPDATE users SET is_verified = TRUE, updated_at = $1 WHERE id = $2", user.updated_at, user.id)
            if entry_db:
                await entry_db.mark_used()
            return {"status": "email_verified"}
    except Exception as e:
        logger.warning(f"Email verify DB lookup failed: {e}")
    # Fallback in-memory
    entry_mem = _EMAIL_VERIFY_TOKENS.get(token_hash)
    if not entry_mem or entry_mem.get("used") or datetime.utcnow() > entry_mem.get("expires_at", datetime.utcnow()):
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    entry_mem["used"] = True
    # Best effort user update if email known
    email = entry_mem.get("email")
    if email:
        user = await User.get_by_email(email)
        if user and not user.is_verified:
            user.is_verified = True
            user.updated_at = datetime.utcnow()
            try:
                pool = await get_database_connection()
                async with pool.acquire() as connection:
                    await connection.execute("UPDATE users SET is_verified = TRUE, updated_at = $1 WHERE id = $2", user.updated_at, user.id)
            except Exception as e:
                logger.warning(f"Failed to persist is_verified (memory fallback) {e}")
    return {"status": "email_verified"}


# ---------------------------------------------------------------------------
# OAuth scaffolding (placeholders)
# ---------------------------------------------------------------------------
SUPPORTED_OAUTH_PROVIDERS = {"google", "github"}

# In‑memory ephemeral OAuth state store (process local).
_OAUTH_STATE_STORE: Dict[str, Dict[str, Any]] = {}
_OAUTH_STATE_TTL_SECONDS = 300  # 5 minutes

# In-memory email verification fallback tokens (similar pattern to password reset fallback)
_EMAIL_VERIFY_TOKENS: Dict[str, Dict[str, Any]] = {}
_EMAIL_VERIFY_TTL_SECONDS = 86400  # 24h

# In-memory revoked refresh token jtis (simple rotation enforcement, dev only)
_REVOKED_REFRESH_JTIS: set[str] = set()

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

def _sign_state(payload: Dict[str, Any]) -> str:
    secret = os.getenv("OAUTH_STATE_SECRET") or os.getenv("SESSION_SECRET_KEY") or "dev-secret"
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    sig = hmac.new(secret.encode(), body, hashlib.sha256).digest()
    return _b64url(body) + "." + _b64url(sig)

def _verify_state(state_token: str) -> Optional[Dict[str, Any]]:
    try:
        body_b64, sig_b64 = state_token.split(".", 1)
        padding = "=" * (-len(body_b64) % 4)
        body_raw = base64.urlsafe_b64decode(body_b64 + padding)
        payload = json.loads(body_raw.decode())
        expected = _sign_state(payload)
        if not hmac.compare_digest(expected.split(".",1)[1], sig_b64):
            return None
        # Check expiry
        if payload.get("exp") and time.time() > payload["exp"]:
            return None
        return payload
    except Exception:
        return None

def _generate_pkce_verifier_challenge() -> Tuple[str, str]:
    verifier = _b64url(os.urandom(32))
    challenge = _b64url(hashlib.sha256(verifier.encode()).digest())
    return verifier, challenge

def _build_redirect_uri(provider: str) -> str:
    base_override = os.getenv("OAUTH_REDIRECT_BASE")  # e.g. https://coder.fastmonkey.au/api/v1/auth/oauth
    if base_override:
        return f"{base_override}/{provider}/callback".rstrip("/")
    # Fallback local dev assumption
    return f"http://localhost:8000/api/v1/auth/oauth/{provider}/callback"

@app.get("/api/v1/auth/oauth/{provider}/initiate")
async def oauth_initiate(provider: str):
    """Initiate OAuth flow for Google or GitHub.

    Generates a signed, time‑limited state token (HMAC) plus, for Google, a PKCE code challenge.
    Stores ephemeral state (session-less) in memory keyed by an internal id to support replay
    detection and later code_verifier lookup during callback.
    """
    if provider not in SUPPORTED_OAUTH_PROVIDERS:
        raise HTTPException(status_code=404, detail="Unsupported provider")

    now = int(time.time())
    state_id = _b64url(os.urandom(18))
    base_payload = {"sid": state_id, "p": provider, "iat": now, "exp": now + _OAUTH_STATE_TTL_SECONDS}

    code_verifier = None
    code_challenge = None
    code_challenge_method = None
    if provider == "google":
        code_verifier, code_challenge = _generate_pkce_verifier_challenge()
        code_challenge_method = "S256"
        base_payload["pkce"] = True

    state_token = _sign_state(base_payload)

    # Persist minimal server-side record for replay + PKCE
    _OAUTH_STATE_STORE[state_id] = {
        "provider": provider,
        "created": now,
        "expires": now + _OAUTH_STATE_TTL_SECONDS,
        "code_verifier": code_verifier,
        "used": False
    }

    # Provider configuration from env
    redirect_uri = _build_redirect_uri(provider)
    if provider == "google":
        client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
        scopes = [
            "openid","email","profile"
        ]
        auth_base = "https://accounts.google.com/o/oauth2/v2/auth"
        query = {
            "response_type": "code",
            "client_id": client_id or "MISSING_CLIENT_ID",
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
            "state": state_token,
            "access_type": "offline",
            "include_granted_scopes": "true"
        }
        if code_challenge and code_challenge_method:
            query["code_challenge"] = code_challenge
            query["code_challenge_method"] = code_challenge_method
        auth_url = auth_base + "?" + urlencode(query)
    else:  # github
        client_id = os.getenv("GITHUB_OAUTH_CLIENT_ID")
        auth_base = "https://github.com/login/oauth/authorize"
        query = {
            "client_id": client_id or "MISSING_CLIENT_ID",
            "redirect_uri": redirect_uri,
            "scope": "read:user user:email",
            "state": state_token,
        }
        auth_url = auth_base + "?" + urlencode(query)

    # Indicate if running in degraded (missing secrets) mode
    degraded = False
    if provider == "google" and not os.getenv("GOOGLE_OAUTH_CLIENT_ID"):
        degraded = True
    if provider == "github" and not os.getenv("GITHUB_OAUTH_CLIENT_ID"):
        degraded = True

    return {
        "provider": provider,
        "authorization_url": auth_url,
        "state": state_token,
        "expires_in": _OAUTH_STATE_TTL_SECONDS,
        "pkce": bool(code_verifier),
        "degraded": degraded
    }

@app.get("/api/v1/auth/oauth/{provider}/callback")
async def oauth_callback(provider: str, request: Request, response: Response, code: Optional[str] = None, state: Optional[str] = None):
    """Handle OAuth provider callback.

    Steps:
      1. Validate provider & required query params.
      2. Verify signed state token & lookup ephemeral record.
      3. Exchange authorization code for tokens (unless degraded mode).
      4. Retrieve basic profile (email + name/username).
      5. Link existing user (by email) or create a new minimal account.
      6. Issue session & set auth cookies using enhanced_auth_manager.
    """
    if provider not in SUPPORTED_OAUTH_PROVIDERS:
        raise HTTPException(status_code=404, detail="Unsupported provider")
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state")

    # Verify & decode state
    state_payload = _verify_state(state)
    if not state_payload or state_payload.get("p") != provider:
        raise HTTPException(status_code=400, detail="Invalid state")
    sid_val = state_payload.get("sid")
    if not isinstance(sid_val, str):
        raise HTTPException(status_code=400, detail="Invalid state sid")
    record = _OAUTH_STATE_STORE.get(sid_val)
    if not record or record.get("used") or record.get("provider") != provider or time.time() > record.get("expires", 0):
        raise HTTPException(status_code=400, detail="Expired or replayed state")

    # Mark state as used to prevent replay
    record["used"] = True

    # Determine degraded mode (missing client secrets) – in which case we mock profile
    degraded = False
    if provider == "google" and (not os.getenv("GOOGLE_OAUTH_CLIENT_ID") or not os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")):
        degraded = True
    if provider == "github" and (not os.getenv("GITHUB_OAUTH_CLIENT_ID") or not os.getenv("GITHUB_OAUTH_CLIENT_SECRET")):
        degraded = True

    profile_email: Optional[str] = None
    profile_name: Optional[str] = None
    username: Optional[str] = None

    token_response: Dict[str, Any] = {}
    access_token: Optional[str] = None
    # id_token not currently used but could support future email_verified claims

    if degraded:
        # Provide deterministic mock profile for local dev
        profile_email = f"dev-{provider}-user@example.local"
        profile_name = f"Dev {provider.title()} User"
        username = f"dev_{provider}_user"
    else:
        import httpx
        try:
            if provider == "google":
                data = {
                    "code": code,
                    "client_id": os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
                    "redirect_uri": _build_redirect_uri(provider),
                    "grant_type": "authorization_code"
                }
                if record.get("code_verifier"):
                    data["code_verifier"] = record["code_verifier"]
                async with httpx.AsyncClient(timeout=10) as client:
                    r = await client.post("https://oauth2.googleapis.com/token", data=data)
                    token_response = r.json()
                access_token = token_response.get("access_token")
                # Fetch userinfo
                if access_token:
                    async with httpx.AsyncClient(timeout=10) as client:
                        ui = await client.get("https://openidconnect.googleapis.com/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
                        ui_data = ui.json()
                    profile_email = ui_data.get("email")
                    profile_name = ui_data.get("name") or ui_data.get("given_name")
                    username = (ui_data.get("preferred_username") or (profile_email.split("@")[0] if profile_email else None))
            else:  # github
                data = {
                    "code": code,
                    "client_id": os.getenv("GITHUB_OAUTH_CLIENT_ID"),
                    "client_secret": os.getenv("GITHUB_OAUTH_CLIENT_SECRET"),
                    "redirect_uri": _build_redirect_uri(provider),
                }
                async with httpx.AsyncClient(timeout=10, headers={"Accept": "application/json"}) as client:
                    r = await client.post("https://github.com/login/oauth/access_token", data=data)
                    token_response = r.json()
                access_token = token_response.get("access_token")
                if access_token:
                    async with httpx.AsyncClient(timeout=10, headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json", "User-Agent": "monkey-coder"}) as client:
                        ui = await client.get("https://api.github.com/user")
                        ui_data = ui.json()
                        # GitHub may require a second call for emails
                        email_resp = await client.get("https://api.github.com/user/emails")
                        emails = email_resp.json() if email_resp.status_code == 200 else []
                    profile_email = None
                    if isinstance(emails, list):
                        primary = [e for e in emails if e.get("primary") and e.get("verified")]
                        if primary:
                            profile_email = primary[0].get("email")
                    if not profile_email:
                        # fallback to login-based pseudo email (not ideal; encourages re-initiate if private email hidden)
                        profile_email = f"{ui_data.get('login')}@users.noreply.github.com"
                    profile_name = ui_data.get("name") or ui_data.get("login")
                    username = ui_data.get("login")
        except Exception as e:
            logger.error(f"OAuth token/profile fetch failed: {e}")
            raise HTTPException(status_code=400, detail="OAuth token exchange failed")

    if not profile_email:
        raise HTTPException(status_code=400, detail="Failed to obtain profile email")

    # Normalize email
    email_norm = profile_email.strip().lower()
    username = username or email_norm.split("@")[0]
    profile_name = profile_name or username

    # Link or create user
    try:
        user = await User.get_by_email(email_norm)
    except Exception as e:
        if 'another operation is in progress' in str(e).lower():
            logger.warning("DB contention during OAuth user lookup; retrying via degraded create path")
            user = None
        else:
            raise
    created = False
    if not user:
        # Create minimal user; generate random password (user can set later via reset)
        from ..security import hash_password
        rand_pwd = _b64url(os.urandom(24))
        try:
            password_hash = hash_password(rand_pwd)
            user = await User.create(
                username=username,
                email=email_norm,
                full_name=profile_name,
                password_hash=password_hash,
                is_developer=False,
                subscription_plan="free"
            )
            created = True
        except Exception as e:
            logger.error(f"Failed to create user during OAuth flow: {e}")
            raise HTTPException(status_code=500, detail="Account provisioning failed")

    # Build JWT & session using enhanced manager pattern
    # Reuse create_user logic flow partially: manually constructing AuthResult inputs
    try:
        # Build roles
        from ..security import get_user_permissions
        base_roles = [UserRole.VIEWER]
        if user.is_developer:
            base_roles.append(UserRole.DEVELOPER)
        from datetime import timezone as _tz
        jwt_user = JWTUser(
            user_id=str(user.id),
            username=user.username,
            email=user.email,
            roles=base_roles,
            permissions=get_user_permissions(base_roles),
            expires_at=datetime.now(_tz.utc) + timedelta(minutes=30)
        )
        access_token_jwt = create_access_token(jwt_user)
        refresh_token_jwt = create_refresh_token(jwt_user.user_id)
        session_id = enhanced_auth_manager.generate_session_id()
        csrf_token = enhanced_auth_manager.generate_csrf_token() if enhanced_auth_manager.config.enable_csrf_protection else None
        # Register session in manager internal store
        from datetime import timezone as _tz
        enhanced_auth_manager._sessions[session_id] = {
            "user_id": jwt_user.user_id,
            "created": datetime.now(_tz.utc),
            "last_activity": datetime.now(_tz.utc),
            "csrf_token": csrf_token
        }
        # Set cookies
        enhanced_auth_manager.set_auth_cookies(
            response=response,
            access_token=access_token_jwt,
            refresh_token=refresh_token_jwt,
            session_id=session_id,
            csrf_token=csrf_token
        )
    except Exception as e:
        logger.error(f"Failed to finalize session after OAuth: {e}")
        raise HTTPException(status_code=500, detail="Session creation failed")

    credits = 10000 if user.is_developer else 100
    subscription_tier = user.subscription_plan or "free"
    return {
        "status": "ok",
        "provider": provider,
        "created": created,
        "user": {
            "id": jwt_user.user_id,
            "email": jwt_user.email,
            "name": jwt_user.username,
            "credits": credits,
            "subscription_tier": subscription_tier,
            "is_developer": user.is_developer,
            "roles": [r.value for r in jwt_user.roles]
        },
        "access_token": access_token_jwt,
        "refresh_token": refresh_token_jwt,
    "expires_at": (jwt_user.expires_at and jwt_user.expires_at.isoformat()),
        "degraded": degraded
    }
@app.post("/api/v1/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest, response: Response, background_tasks: BackgroundTasks, raw_request: Request) -> AuthResponse:
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
        # Rate limit first
        check_rate_limit(raw_request, "login")
        # Authenticate user using enhanced manager
        auth_result = await enhanced_auth_manager.authenticate_user(
            email=request.email,
            password=request.password,
            request=raw_request,
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


@app.post("/api/v1/auth/signup", response_model=AuthResponse)
async def signup(request: SignupRequest, response: Response, background_tasks: BackgroundTasks, raw_request: Request) -> AuthResponse:
    """
    User signup endpoint with enhanced authentication.

    Args:
        request: Signup credentials and user information
        response: FastAPI response object
        background_tasks: Background tasks for async operations

    Returns:
        AuthResponse with tokens and user information

    Raises:
        HTTPException: If signup fails or user already exists
    """
    try:
        # Rate limit signup attempts per IP
        try:
            check_rate_limit(raw_request, "signup")
        except HTTPException:
            # propagate 429
            raise

        # Normalize email (case-insensitive uniqueness)
        email_norm = request.email.strip().lower()

        # Basic password policy (length + diversity heuristic)
        pwd = request.password
        if len(pwd) < 10 or sum(c.isdigit() for c in pwd) < 1 or sum(c.isalpha() for c in pwd) < 1:
            raise HTTPException(status_code=400, detail="Password does not meet minimum complexity requirements")

        # Soft enumeration resistance: always perform timing-similar path
        existing_user = await User.get_by_email(email_norm)
        if existing_user:
            # Return 409 but generic wording
            raise HTTPException(status_code=409, detail="Account creation failed")

        # Create new user using enhanced manager
        auth_result = await enhanced_auth_manager.create_user(
            username=request.username,
            name=request.name,
            email=email_norm,
            password=pwd,
            plan=request.plan or "free"
        )

        if not auth_result.success or not auth_result.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=auth_result.message or "Failed to create user account"
            )

        if not auth_result.access_token or not auth_result.refresh_token or not auth_result.session_id:
            raise HTTPException(status_code=500, detail="Signup failed to generate tokens")

        # Set cookies using enhanced manager
        enhanced_auth_manager.set_auth_cookies(
            response=response,
            access_token=auth_result.access_token,
            refresh_token=auth_result.refresh_token,
            session_id=auth_result.session_id,
            csrf_token=auth_result.csrf_token
        )

        # Get created user details
        user = await User.get_by_id(auth_result.user.user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found after creation")

        # Set credits and subscription tier
        credits = 10000 if user.is_developer else 100
        subscription_tier = request.plan or "free"

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
        logger.error(f"Signup failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create account")


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


@app.get("/api/v1/environment/mcp-status")
async def get_mcp_environment_status(
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Get MCP-enhanced environment status and variable resolution information.

    This endpoint provides information about how environment variables are
    being resolved using MCP servers, Railway service discovery, and production defaults.
    Helps debug production configuration issues and validates that localhost
    references are properly avoided.

    Args:
        api_key: API key for authentication

    Returns:
        Dictionary with MCP environment status and variable information
    """
    try:
        await verify_permissions(api_key, "system:read")

        # Try to get MCP environment manager status
        try:
            from ..config.mcp_env_manager import mcp_env_manager

            # Get variable summary
            variable_summary = mcp_env_manager.get_variable_summary()

            # Get production readiness validation
            production_validation = mcp_env_manager.validate_production_readiness()

            # Get resolved variables (without sensitive values)
            resolved_variables = {}
            for key, var in mcp_env_manager.get_all_variables().items():
                # Mask sensitive values
                if any(sensitive in key.upper() for sensitive in ['PASSWORD', 'SECRET', 'KEY', 'TOKEN']):
                    display_value = "***MASKED***" if var.value else None
                else:
                    display_value = var.value

                resolved_variables[key] = {
                    "value": display_value,
                    "source": var.source,
                    "priority": var.priority,
                    "description": var.description
                }

            response_data = {
                "mcp_enabled": True,
                "variable_summary": variable_summary,
                "production_validation": production_validation,
                "resolved_variables": resolved_variables,
                "railway_info": {
                    "environment": os.getenv('RAILWAY_ENVIRONMENT'),
                    "project": os.getenv('RAILWAY_PROJECT_NAME'),
                    "public_domain": os.getenv('RAILWAY_PUBLIC_DOMAIN'),
                    "service_id": os.getenv('RAILWAY_SERVICE_ID')
                },
                "timestamp": datetime.utcnow().isoformat()
            }

            return response_data

        except ImportError:
            # MCP environment manager not available
            return {
                "mcp_enabled": False,
                "reason": "MCP environment manager not available",
                "fallback_mode": True,
                "railway_info": {
                    "environment": os.getenv('RAILWAY_ENVIRONMENT'),
                    "project": os.getenv('RAILWAY_PROJECT_NAME'),
                    "public_domain": os.getenv('RAILWAY_PUBLIC_DOMAIN')
                },
                "basic_variables": {
                    "DATABASE_URL": "***CONFIGURED***" if os.getenv('DATABASE_URL') else "NOT SET",
                    "NEXT_PUBLIC_API_URL": os.getenv('NEXT_PUBLIC_API_URL', 'DEFAULT'),
                    "RAILWAY_ENVIRONMENT": os.getenv('RAILWAY_ENVIRONMENT', 'NOT SET')
                },
                "timestamp": datetime.utcnow().isoformat()
            }

    except Exception as e:
        logger.error(f"MCP environment status check failed: {str(e)}")
        return {"error": f"Environment status check failed: {str(e)}"}


@app.get("/api/v1/auth/debug")
async def debug_auth_config():
    """
    Enhanced authentication debug endpoint for production monitoring.

    Returns detailed status of authentication configuration, CORS settings,
    CSP headers, and security middleware without exposing sensitive values.
    """
    from ..config.cors import get_cors_origins
    from ..middleware.security_middleware import get_railway_security_config

    try:
        # Test database connection
        def test_db_connection():
            try:
                from ..database.connection import test_database_connection
                return asyncio.run(test_database_connection())
            except Exception:
                return False

        # Test Redis connection
        def test_redis_connection():
            try:
                import redis
                redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
                r = redis.from_url(redis_url)
                r.ping()
                return True
            except Exception:
                return False

        # Get security configuration
        security_config = get_railway_security_config()
        cors_origins = get_cors_origins()

        # Check JWT configuration
        jwt_configured = bool(os.getenv("JWT_SECRET_KEY"))
        jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")

        response_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "authentication": {
                "jwt_configured": jwt_configured,
                "jwt_algorithm": jwt_algorithm,
                "jwt_expire_minutes": os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"),
                "mfa_enabled": os.getenv("MFA_ENABLED", "false").lower() == "true"
            },
            "database": {
                "connected": test_db_connection(),
                "url_configured": bool(os.getenv("DATABASE_URL"))
            },
            "redis": {
                "connected": test_redis_connection(),
                "url_configured": bool(os.getenv("REDIS_URL"))
            },
            "cors": {
                "allowed_origins_count": len(cors_origins),
                "allow_credentials": security_config["cors_allow_credentials"],
                "sample_origins": cors_origins[:3] if cors_origins else [],
                "railway_domain": os.getenv("RAILWAY_PUBLIC_DOMAIN", "not_set")
            },
            "csp": {
                "font_sources": security_config["csp_font_src"],
                "style_sources": security_config["csp_style_src"],
                "connect_sources": security_config["csp_connect_src"],
                "default_sources": security_config["csp_default_src"]
            },
            "environment": {
                "railway_environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown"),
                "enable_security_headers": os.getenv("ENABLE_SECURITY_HEADERS", "true"),
                "enable_cors": os.getenv("ENABLE_CORS", "true"),
                "debug_mode": os.getenv("DEBUG", "false").lower() == "true"
            },
            "middleware": {
                "pricing_enabled": bool(os.getenv("ENABLE_PRICING_MIDDLEWARE", "true")),
                "security_headers_enabled": bool(os.getenv("ENABLE_SECURITY_HEADERS", "true")),
                "csp_violation_reporting": bool(os.getenv("RAILWAY_ENVIRONMENT") == "production")
            }
        }

        return JSONResponse(content=response_data, status_code=200)

    except Exception as e:
        logger.error(f"Auth debug endpoint failed: {str(e)}")
        return JSONResponse(
            content={"error": f"Debug check failed: {str(e)}"},
            status_code=500
        )


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
        # Extract existing refresh token cookie (raw) for rotation tracking
        # Support both current and legacy cookie names for refresh token (tests may use 'refresh_token')
        refresh_cookie_name = getattr(enhanced_auth_manager.config, 'refresh_token_name', 'refresh_token')
        # Collect both possible cookies
        legacy_refresh = request.cookies.get('refresh_token')
        current_refresh = request.cookies.get(refresh_cookie_name)
        old_refresh = None
        # If client explicitly supplies legacy cookie treat it as the attempted token (even if a newer cookie exists)
        if legacy_refresh:
            old_refresh = legacy_refresh
        else:
            old_refresh = current_refresh
        old_jti = None
        if old_refresh:
            try:
                payload = verify_token(old_refresh)
                if payload.get('type') == 'refresh':
                    old_jti = payload.get('jti')
                    if old_jti in _REVOKED_REFRESH_JTIS:
                        raise HTTPException(status_code=401, detail="Refresh token revoked")
            except HTTPException:
                raise
            except Exception:
                # Invalid refresh token structure
                raise HTTPException(status_code=401, detail="Invalid refresh token")
        # If legacy refresh provided but differs from current valid refresh cookie and not revoked, we still proceed to refresh
        # using the manager (which will rely on current_refresh). This mimics real-world browsers where multiple cookies may exist.

        # Refresh using enhanced manager (issues new tokens)
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

        # Revoke old refresh jti after successful issuance
        if old_jti:
            _REVOKED_REFRESH_JTIS.add(old_jti)

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

        # Execute via quantum executor (Gary8D integration) if available
        if app.state.quantum_executor is not None:
            execution_result = await app.state.quantum_executor.execute(
                orchestration_result, parallel_futures=True
            )
        else:
            # Fallback to orchestration result if quantum executor not available
            execution_result = orchestration_result

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
                "mcp_enhanced_variable_resolution",
                "railway_service_discovery",
                "production_localhost_avoidance",
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
                    "feature": "MCP Environment Management",
                    "description": "Enhanced environment variable resolution using MCP servers and Railway service discovery",
                    "status": "implemented"
                },
                {
                    "feature": "Production Localhost Avoidance",
                    "description": "Intelligent defaults that avoid localhost references in production environments",
                    "status": "implemented"
                },
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


from pydantic import BaseModel as PydanticBaseModel, Field

class EnquiryRequest(PydanticBaseModel):
    """Request model for enquiry submission."""
    name: str = Field(..., description="Name of the person making the enquiry")
    email: str = Field(..., description="Email address for response")
    subject: str = Field(..., description="Subject of the enquiry")
    message: str = Field(..., description="Message content")


@app.post("/api/v1/enquiry", response_model=Dict[str, Any])
async def submit_enquiry(
    enquiry: EnquiryRequest,
    request: Request,
) -> Dict[str, Any]:
    """
    Submit an enquiry for support or general questions.
    
    This endpoint accepts enquiry submissions and sends email notifications
    to configured admin/support email addresses. No authentication required
    for accessibility.
    
    Args:
        enquiry: Enquiry details including name, email, subject, and message
        request: FastAPI request object for IP tracking
    
    Returns:
        Confirmation of enquiry submission
    """
    try:
        # Rate limiting for enquiries
        check_rate_limit(request, "enquiry")
        
        # Basic validation
        if len(enquiry.message.strip()) < 10:
            raise HTTPException(status_code=400, detail="Message must be at least 10 characters long")
        
        if len(enquiry.subject.strip()) < 3:
            raise HTTPException(status_code=400, detail="Subject must be at least 3 characters long")
        
        # Prepare enquiry data
        enquiry_data = {
            "name": enquiry.name,
            "email": enquiry.email,
            "subject": enquiry.subject,
            "message": enquiry.message,
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": request.client.host if request.client else "unknown"
        }
        
        # Send enquiry notification email
        from ..email.sender import email_notification_service
        await email_notification_service.send_enquiry_notification(enquiry_data)
        
        logger.info(f"Enquiry submitted from {enquiry.email}: {enquiry.subject}")
        
        return {
            "status": "success",
            "message": "Enquiry submitted successfully. We will respond to your email shortly.",
            "timestamp": enquiry_data["timestamp"],
            "enquiry_id": f"enq_{int(datetime.utcnow().timestamp())}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit enquiry: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit enquiry. Please try again later.")


@app.get("/api/v1/enquiry/status", response_model=Dict[str, Any])
async def get_enquiry_status(
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Get enquiry system status and configuration.
    
    Returns information about the enquiry notification system,
    including configured email addresses and recent statistics.
    
    Args:
        api_key: API key for authentication
    
    Returns:
        Enquiry system status and configuration
    """
    try:
        await verify_permissions(api_key, "system:read")
        
        from ..email.sender import email_notification_service
        
        # Get configuration status
        config_status = {
            "resend_configured": bool(email_notification_service.resend_client),
            "enquiry_emails_configured": bool(email_notification_service.enquiry_emails),
            "admin_emails_configured": bool(email_notification_service.admin_emails),
            "from_email": email_notification_service.from_email,
            "environment": email_notification_service.env
        }
        
        # Basic statistics (could be enhanced with actual tracking)
        stats = {
            "system_status": "operational" if config_status["resend_configured"] else "configuration_needed",
            "notification_method": "email" if config_status["resend_configured"] else "logging_only",
            "recipient_count": len(email_notification_service.enquiry_emails or email_notification_service.admin_emails),
        }
        
        return {
            "status": "active",
            "configuration": config_status,
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to get enquiry status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve enquiry system status")


@app.get("/.well-known/agent.json", response_model=Dict[str, Any])
async def get_agent_card() -> Dict[str, Any]:
    """
    Get agent card with A2A capabilities and metadata.
    
    This endpoint serves the agent card according to A2A protocol standards,
    providing information about available skills, capabilities, and metadata.
    
    Returns:
        Agent card with skills, capabilities, and connection information
    """
    try:
        # Load agent card from file
        import json
        from pathlib import Path
        
        agent_card_path = Path(__file__).parent.parent.parent.parent / ".well-known" / "agent.json"
        
        if agent_card_path.exists():
            with open(agent_card_path, 'r') as f:
                agent_card = json.load(f)
            
            # Add dynamic information
            agent_card["status"] = "active"
            agent_card["updated_at"] = datetime.utcnow().isoformat() + "Z"
            
            # Add A2A server status if available
            if hasattr(app.state, 'a2a_agent') and app.state.a2a_agent:
                agent_card["a2a_server"] = {
                    "status": "running",
                    "port": app.state.a2a_agent.port,
                    "mcp_clients": list(app.state.a2a_agent.mcp_clients.keys())
                }
            else:
                agent_card["a2a_server"] = {
                    "status": "not_running",
                    "reason": "A2A server disabled or failed to initialize"
                }
            
            return agent_card
        else:
            # Return basic agent card if file not found
            basic_card = {
                "name": "Monkey-Coder Agent",
                "description": "Specialized Deep Agent for code generation and analysis",
                "version": "1.0.0",
                "status": "active",
                "error": "Agent card file not found",
                "updated_at": datetime.utcnow().isoformat() + "Z"
            }
            
            # Add A2A server status even for basic card
            if hasattr(app.state, 'a2a_agent') and app.state.a2a_agent:
                basic_card["a2a_server"] = {
                    "status": "running",
                    "port": app.state.a2a_agent.port,
                    "mcp_clients": list(app.state.a2a_agent.mcp_clients.keys())
                }
            else:
                basic_card["a2a_server"] = {
                    "status": "not_running",
                    "reason": "A2A server disabled or failed to initialize"
                }
            
            return basic_card
            
    except Exception as e:
        logger.error(f"Agent card retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve agent card")


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
                # Compute a fingerprint of index.html to correlate with build logs (if present)
                index_path = static_dir / "index.html"
                if index_path.exists():
                    try:
                        import hashlib
                        with index_path.open('rb') as f:
                            data = f.read()
                        sha256 = hashlib.sha256(data).hexdigest()
                        logger.info(f"   🔐 index.html sha256 fingerprint: {sha256}")
                    except Exception as e:
                        logger.warning(f"   Could not hash index.html: {e}")
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

    # Diagnostic endpoint (defined BEFORE catch-all so it isn't shadowed)
    @app.get("/frontend-status", tags=["system"])
    async def frontend_status():  # pragma: no cover - simple diagnostic
        data = getattr(app.state, 'frontend_build', {"served": False}).copy()
        data["metrics_active"] = getattr(app.state, 'metrics_active', False)
        trusted_hosts_env = os.getenv("TRUSTED_HOSTS", "*")
        data["trusted_hosts"] = [h for h in trusted_hosts_env.replace(";", ",").split(",") if h]
        commit = os.getenv("GIT_COMMIT") or os.getenv("RAILWAY_GIT_COMMIT")
        if commit:
            data["commit"] = commit[:12]
        return JSONResponse(data)

    # Create a custom catch-all handler for SPA routing that doesn't interfere with API or diagnostic routes
    from fastapi.responses import FileResponse

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve SPA for non-API routes."""
        # Don't catch API or diagnostic routes
        if full_path.startswith("api/") or full_path.startswith("v1/") or full_path == "frontend-status":
            raise HTTPException(status_code=404, detail="API endpoint not found")
        # If for some reason static_dir disappeared, 404
        if static_dir is None:
            raise HTTPException(status_code=404, detail="Static directory unavailable")

        # Try to serve the exact file first
        file_path = static_dir / full_path  # type: ignore[operator]
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))

        # For SPA routing, always return index.html for non-file paths
        index_path = static_dir / "index.html"  # type: ignore[operator]
        if index_path.exists():
            return FileResponse(str(index_path))

        # If no index.html, return 404
        raise HTTPException(status_code=404, detail="Page not found")

    logger.info(f"✅ Frontend served from: {static_dir} with SPA routing")
    # Store frontend build diagnostics for external monitoring
    try:
        import hashlib
        index_file = static_dir / "index.html"
        index_hash = None
        if index_file.exists():
            with index_file.open('rb') as f:
                index_hash = hashlib.sha256(f.read()).hexdigest()
        app.state.frontend_build = {
            "served": True,
            "static_dir": str(static_dir),
            "index_hash": index_hash,
            "has_next": (static_dir / '_next').exists(),
            "files": sum(1 for _ in static_dir.rglob('*')),
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
    except Exception as e:  # pragma: no cover - non-critical path
        logger.warning(f"Could not record frontend build metadata: {e}")
        app.state.frontend_build = {"served": True, "static_dir": str(static_dir)}
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
    # Record fallback state
    app.state.frontend_build = {"served": False, "reason": "static_dir_not_found", "checked_paths": [str(p) for p in static_dir_options]}

if not (serve_frontend and static_dir):
    # When frontend not served, still expose diagnostic endpoint (not defined above)
    @app.get("/frontend-status", tags=["system"])
    async def frontend_status():  # pragma: no cover - simple diagnostic
        data = getattr(app.state, 'frontend_build', {"served": False}).copy()
        data["metrics_active"] = getattr(app.state, 'metrics_active', False)
        trusted_hosts_env = os.getenv("TRUSTED_HOSTS", "*")
        data["trusted_hosts"] = [h for h in trusted_hosts_env.replace(";", ",").split(",") if h]
        commit = os.getenv("GIT_COMMIT") or os.getenv("RAILWAY_GIT_COMMIT")
        if commit:
            data["commit"] = commit[:12]
        return JSONResponse(data)


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
