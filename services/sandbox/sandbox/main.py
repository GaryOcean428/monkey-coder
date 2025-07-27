"""
Sandbox Service Main Application

Provides secure containerized environment for code execution and browser automation
using E2B and BrowserBase integrations.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .e2b_integration import E2BSandboxManager
from .browserbase_integration import BrowserBaseSandboxManager
from .security import SecurityManager, get_sandbox_token, enforce_resource_limits
from .monitoring import SandboxMetrics, ResourceMonitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SandboxRequest(BaseModel):
    """Request model for sandbox operations."""
    sandbox_type: str = Field(..., description="Type of sandbox: 'code' or 'browser'")
    action: str = Field(..., description="Action to perform")
    code: Optional[str] = Field(None, description="Code to execute")
    url: Optional[str] = Field(None, description="URL for browser actions")
    timeout: int = Field(30, description="Timeout in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SandboxResponse(BaseModel):
    """Response model for sandbox operations."""
    execution_id: str = Field(..., description="Unique execution ID")
    status: str = Field(..., description="Execution status")
    result: Any = Field(None, description="Execution result")
    logs: List[str] = Field(default_factory=list)
    execution_time: float = Field(..., description="Execution time in seconds")
    resource_usage: Dict[str, Any] = Field(default_factory=dict)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Sandbox Service...")
    
    # Initialize sandbox managers
    app.state.e2b_manager = E2BSandboxManager()
    app.state.browserbase_manager = BrowserBaseSandboxManager()
    app.state.security_manager = SecurityManager()
    app.state.resource_monitor = ResourceMonitor()
    app.state.metrics = SandboxMetrics()
    
    # Start resource monitoring
    await app.state.resource_monitor.start()
    
    logger.info("Sandbox Service started successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Sandbox Service...")
    await app.state.resource_monitor.stop()
    await app.state.e2b_manager.cleanup_all()
    await app.state.browserbase_manager.cleanup_all()
    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Monkey Coder Sandbox Service",
    description="Secure containerized environment for code execution and browser automation",
    version="1.0.0",
    docs_url="/sandbox/docs",
    redoc_url="/sandbox/redoc",
    openapi_url="/sandbox/openapi.json",
    lifespan=lifespan,
)

# Add security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Restrict to known origins
    allow_credentials=False,  # No credentials in sandbox
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.railway.app"]
)


@app.get("/sandbox/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "sandbox",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "resources": await app.state.resource_monitor.get_current_usage()
    }


@app.post("/sandbox/execute", response_model=SandboxResponse)
async def execute_sandbox_task(
    request: SandboxRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(get_sandbox_token),
) -> SandboxResponse:
    """
    Execute code or browser automation in secure sandbox.
    
    Supports:
    - E2B code execution sandboxes
    - BrowserBase browser automation
    - Resource limits and monitoring
    - Security isolation
    """
    
    # Enforce resource limits
    await enforce_resource_limits()
    
    try:
        execution_id = app.state.metrics.start_execution(request)
        start_time = asyncio.get_event_loop().time()
        
        # Route to appropriate sandbox manager
        if request.sandbox_type == "code":
            result = await app.state.e2b_manager.execute_code(
                code=request.code,
                execution_id=execution_id,
                timeout=request.timeout,
                metadata=request.metadata
            )
        elif request.sandbox_type == "browser":
            result = await app.state.browserbase_manager.execute_browser_action(
                url=request.url,
                action=request.action,
                execution_id=execution_id,
                timeout=request.timeout,
                metadata=request.metadata
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported sandbox type: {request.sandbox_type}"
            )
        
        execution_time = asyncio.get_event_loop().time() - start_time
        
        # Get resource usage
        resource_usage = await app.state.resource_monitor.get_execution_usage(execution_id)
        
        response = SandboxResponse(
            execution_id=execution_id,
            status="completed",
            result=result.get("output"),
            logs=result.get("logs", []),
            execution_time=execution_time,
            resource_usage=resource_usage
        )
        
        # Record metrics in background
        background_tasks.add_task(
            app.state.metrics.record_execution,
            execution_id,
            response
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Sandbox execution failed: {str(e)}")
        
        if 'execution_id' in locals():
            app.state.metrics.record_error(execution_id, str(e))
        
        raise HTTPException(
            status_code=500,
            detail=f"Sandbox execution failed: {str(e)}"
        )


@app.get("/sandbox/metrics")
async def get_sandbox_metrics(
    token: str = Depends(get_sandbox_token),
):
    """Get sandbox performance and resource metrics."""
    try:
        return {
            "current_usage": await app.state.resource_monitor.get_current_usage(),
            "execution_stats": app.state.metrics.get_execution_stats(),
            "active_sandboxes": {
                "e2b": await app.state.e2b_manager.get_active_count(),
                "browserbase": await app.state.browserbase_manager.get_active_count()
            }
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")


@app.post("/sandbox/cleanup")
async def cleanup_sandboxes(
    token: str = Depends(get_sandbox_token),
):
    """Clean up idle sandboxes and resources."""
    try:
        e2b_cleaned = await app.state.e2b_manager.cleanup_idle()
        browserbase_cleaned = await app.state.browserbase_manager.cleanup_idle()
        
        return {
            "status": "success",
            "cleaned_up": {
                "e2b_sandboxes": e2b_cleaned,
                "browserbase_sessions": browserbase_cleaned
            }
        }
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Cleanup failed")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "sandbox.main:app",
        host=host,
        port=port,
        reload=False,  # Disabled in sandbox for security
        log_level="info",
        access_log=True,
    )
