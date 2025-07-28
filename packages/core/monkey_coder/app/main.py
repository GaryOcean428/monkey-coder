"""
FastAPI main application for Monkey Coder Core Orchestration Engine.

This module provides the core FastAPI application with:
- /v1/execute endpoint for task routing & quantum execution
- /v1/billing/usage endpoint for metering
- Integration with SuperClaude, monkey1, and Gary8D systems
"""

import logging
import os
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response, HTMLResponse
from pydantic import BaseModel, Field
import time
from pathlib import Path

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
from ..security import get_api_key, verify_permissions
from ..monitoring import MetricsCollector, BillingTracker
from ..database import run_migrations
from ..pricing import PricingMiddleware, load_pricing_from_file
from ..billing import StripeClient, BillingPortalSession
from ..feedback_collector import FeedbackCollector

# Import Railway-optimized logging first
from ..logging_utils import setup_logging, get_performance_logger, monitor_api_calls

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
    
    # Run database migrations
    try:
        await run_migrations()
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Database migrations failed: {e}")
        # Continue startup even if migrations fail (for development)
    
    # Initialize core components
    app.state.orchestrator = MultiAgentOrchestrator()
    app.state.quantum_executor = QuantumExecutor()
    app.state.persona_router = PersonaRouter()
    app.state.provider_registry = ProviderRegistry()
    app.state.metrics_collector = MetricsCollector()
    app.state.billing_tracker = BillingTracker()
    app.state.feedback_collector = FeedbackCollector()
    
    # Initialize providers
    await app.state.provider_registry.initialize_all()
    
    logger.info("Orchestration engine started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Monkey Coder Core...")
    await app.state.provider_registry.cleanup_all()
    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Monkey Coder Core",
    description="Python orchestration core for AI-powered code generation and analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Load pricing data from file (if exists) on startup
load_pricing_from_file()

# Add pricing middleware
enable_pricing = os.getenv("ENABLE_PRICING_MIDDLEWARE", "true") == "true"
app.add_middleware(PricingMiddleware, enabled=enable_pricing)

# Add other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Add Sentry middleware for error tracking
app.add_middleware(SentryAsgiMiddleware)

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


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Root endpoint that returns an HTML landing page.
    """
    # Get the directory of this file
    current_dir = Path(__file__).parent
    index_path = current_dir / "index.html"
    
    # Read and return the HTML file
    if index_path.exists():
        with open(index_path, "r") as f:
            return HTMLResponse(content=f.read())
    else:
        # Fallback HTML if file not found
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Monkey Coder API</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 40px; text-align: center; }
                h1 { color: #333; }
                a { color: #007bff; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>Monkey Coder Core API</h1>
            <p>Welcome to the Monkey Coder API. This is a backend service.</p>
            <p>
                <a href="/docs">API Documentation</a> | 
                <a href="/health">Health Check</a>
            </p>
        </body>
        </html>
        """)


@app.get("/health", response_model=HealthResponse)
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
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        components=components
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


@app.post("/v1/execute", response_model=ExecuteResponse)
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
            status=TaskStatus.COMPLETED,
            result=execution_result.result,
            metadata=execution_result.metadata,
            usage=execution_result.usage,
            execution_time=execution_result.execution_time,
        )
        
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


@app.get("/v1/billing/usage", response_model=UsageResponse)
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


@app.post("/v1/billing/portal", response_model=BillingPortalSession)
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
            customer_id=billing_customer.stripe_customer_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create billing portal session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create billing portal session")


@app.get("/v1/providers", response_model=Dict[str, Any])
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


@app.get("/v1/models", response_model=Dict[str, Any])
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


@app.post("/v1/router/debug", response_model=Dict[str, Any])
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
