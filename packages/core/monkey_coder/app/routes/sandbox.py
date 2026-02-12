"""
Sandbox API routes for the FastAPI application.

Proxies requests to the sandbox microservice for secure code execution
and browser automation (E2B / BrowserBase).

Endpoints:
- POST /api/v1/sandbox/execute   — Execute code in a sandboxed environment
- POST /api/v1/sandbox/browse    — Run browser automation action
- GET  /api/v1/sandbox/health    — Sandbox service health check
- GET  /api/v1/sandbox/metrics   — Sandbox resource metrics
- POST /api/v1/sandbox/cleanup   — Trigger idle-resource cleanup
"""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ...sandbox_client import SandboxClient
from ...security import (
    JWTUser,
    Permission,
    get_current_user,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/sandbox", tags=["sandbox"])

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_sandbox_client: SandboxClient | None = None


def _get_sandbox_client() -> SandboxClient:
    """Lazy-initialise a module-level SandboxClient singleton."""
    global _sandbox_client  # noqa: PLW0603
    if _sandbox_client is None:
        _sandbox_client = SandboxClient()
    return _sandbox_client


def _require_permission(user: JWTUser, permission: Permission) -> None:
    """Raise 403 if the user lacks the required permission."""
    if permission not in user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing permission: {permission.value}",
        )


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class CodeExecuteRequest(BaseModel):
    """Request to execute code in a sandbox."""

    code: str = Field(..., description="Source code to execute")
    timeout: int = Field(30, ge=1, le=300, description="Timeout in seconds")
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowseRequest(BaseModel):
    """Request to run a browser automation action."""

    url: str = Field(..., description="Target URL")
    action: str = Field(..., description="Browser action (e.g. 'screenshot', 'scrape')")
    timeout: int = Field(30, ge=1, le=120, description="Timeout in seconds")
    metadata: dict[str, Any] = Field(default_factory=dict)


class SandboxExecutionResponse(BaseModel):
    """Sandbox execution result."""

    execution_id: str
    status: str
    result: Any = None
    logs: list[str] = Field(default_factory=list)
    execution_time: float = 0.0
    resource_usage: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/execute", response_model=SandboxExecutionResponse)
async def execute_code(
    request: CodeExecuteRequest,
    current_user: JWTUser = Depends(get_current_user),
) -> SandboxExecutionResponse:
    """Execute code in a sandboxed E2B environment."""
    _require_permission(current_user, Permission.SANDBOX_CREATE)

    execution_id = str(uuid.uuid4())
    client = _get_sandbox_client()

    logger.info(
        "Sandbox code execution requested by %s (exec_id=%s)",
        current_user.email,
        execution_id,
    )

    result = await client.execute_code(
        code=request.code,
        execution_id=execution_id,
        timeout=request.timeout,
        metadata={
            **request.metadata,
            "user_id": current_user.user_id,
            "user_email": current_user.email,
        },
    )

    return SandboxExecutionResponse(**result)


@router.post("/browse", response_model=SandboxExecutionResponse)
async def browse(
    request: BrowseRequest,
    current_user: JWTUser = Depends(get_current_user),
) -> SandboxExecutionResponse:
    """Run a browser automation action via the sandbox service."""
    _require_permission(current_user, Permission.SANDBOX_CREATE)

    execution_id = str(uuid.uuid4())
    client = _get_sandbox_client()

    logger.info(
        "Sandbox browse action '%s' requested by %s (exec_id=%s)",
        request.action,
        current_user.email,
        execution_id,
    )

    result = await client.execute_browser_action(
        url=request.url,
        action=request.action,
        execution_id=execution_id,
        timeout=request.timeout,
        metadata={
            **request.metadata,
            "user_id": current_user.user_id,
            "user_email": current_user.email,
        },
    )

    return SandboxExecutionResponse(**result)


@router.get("/health")
async def sandbox_health(
    current_user: JWTUser = Depends(get_current_user),
) -> dict[str, Any]:
    """Proxy health check to the sandbox service."""
    _require_permission(current_user, Permission.SANDBOX_ACCESS)

    client = _get_sandbox_client()
    healthy = await client.health_check()

    return {
        "sandbox_healthy": healthy,
        "sandbox_url": client.sandbox_url,
    }


@router.get("/metrics")
async def sandbox_metrics(
    current_user: JWTUser = Depends(get_current_user),
) -> dict[str, Any]:
    """Fetch resource metrics from the sandbox service."""
    _require_permission(current_user, Permission.SANDBOX_ACCESS)

    client = _get_sandbox_client()
    return await client.get_sandbox_metrics()


@router.post("/cleanup")
async def sandbox_cleanup(
    current_user: JWTUser = Depends(get_current_user),
) -> dict[str, Any]:
    """Trigger cleanup of idle sandbox resources."""
    _require_permission(current_user, Permission.SANDBOX_DELETE)

    client = _get_sandbox_client()

    logger.info("Sandbox cleanup triggered by %s", current_user.email)

    return await client.cleanup_sandbox_resources()
