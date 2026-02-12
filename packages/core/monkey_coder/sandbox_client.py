"""
Sandbox Client Integration

Provides interface for core application to communicate with sandbox service.
"""

import base64
import hashlib
import hmac
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SandboxRequest(BaseModel):
    """Request model for sandbox operations."""
    sandbox_type: str
    action: str
    code: str | None = None
    url: str | None = None
    timeout: int = 30
    metadata: dict[str, Any] = {}


class SandboxResponse(BaseModel):
    """Response model from sandbox service."""
    execution_id: str
    status: str
    result: Any = None
    logs: list = []
    execution_time: float = 0.0
    resource_usage: dict[str, Any] = {}


class SandboxClient:
    """Client for communicating with the sandbox service."""

    def __init__(self) -> None:
        self.sandbox_url = os.getenv("SANDBOX_SERVICE_URL", "http://localhost:8001")
        self.token_secret = os.getenv("SANDBOX_TOKEN_SECRET", "default-secret")
        self.timeout = 60  # Default timeout for HTTP requests

    async def execute_code(
        self,
        code: str,
        execution_id: str,
        timeout: int = 30,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute Python code in E2B sandbox.

        Args:
            code: Python code to execute
            execution_id: Unique execution identifier
            timeout: Execution timeout in seconds
            metadata: Additional execution metadata

        Returns:
            Dictionary containing execution results
        """
        request = SandboxRequest(
            sandbox_type="code",
            action="execute",
            code=code,
            timeout=timeout,
            metadata=metadata or {}
        )

        return await self._make_sandbox_request(request, execution_id)

    async def execute_browser_action(
        self,
        url: str,
        action: str,
        execution_id: str,
        timeout: int = 30,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute browser automation action using BrowserBase.

        Args:
            url: Target URL
            action: Browser action to perform
            execution_id: Unique execution identifier
            timeout: Execution timeout in seconds
            metadata: Additional execution metadata

        Returns:
            Dictionary containing action results
        """
        request = SandboxRequest(
            sandbox_type="browser",
            action=action,
            url=url,
            timeout=timeout,
            metadata=metadata or {}
        )

        return await self._make_sandbox_request(request, execution_id)

    async def _make_sandbox_request(
        self,
        request: SandboxRequest,
        execution_id: str,
    ) -> dict[str, Any]:
        """Make authenticated request to sandbox service."""
        try:
            token = _generate_sandbox_token(execution_id)
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.sandbox_url}/sandbox/execute",
                    json=request.model_dump(),
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            logger.error(f"Sandbox request timeout for {execution_id}")
            return {
                "execution_id": execution_id,
                "status": "error",
                "result": None,
                "logs": ["Sandbox request timed out"],
                "error": "TIMEOUT",
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"Sandbox HTTP error for {execution_id}: {e.response.status_code}")
            return {
                "execution_id": execution_id,
                "status": "error",
                "result": None,
                "logs": [f"HTTP {e.response.status_code}: {e.response.text}"],
                "error": f"HTTP_{e.response.status_code}",
            }
        except Exception as e:
            logger.error(f"Sandbox request failed for {execution_id}: {e!s}")
            return {
                "execution_id": execution_id,
                "status": "error",
                "result": None,
                "logs": [f"Request failed: {e!s}"],
                "error": str(e),
            }

    async def get_sandbox_metrics(self) -> dict[str, Any]:
        """Get sandbox service metrics."""
        try:
            token = _generate_sandbox_token("metrics")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    f"{self.sandbox_url}/sandbox/metrics",
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Failed to get sandbox metrics: {e!s}")
            return {}

    async def cleanup_sandbox_resources(self) -> dict[str, Any]:
        """Trigger cleanup of idle sandbox resources."""
        try:
            token = _generate_sandbox_token("cleanup")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.sandbox_url}/sandbox/cleanup",
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Failed to cleanup sandbox resources: {e!s}")
            return {"status": "error", "message": str(e)}

    async def health_check(self) -> bool:
        """Check if sandbox service is healthy."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.sandbox_url}/sandbox/health")
                return response.status_code == 200
        except Exception:
            return False


def _generate_sandbox_token(execution_id: str, expires_in: int = 3600) -> str:
    """Generate a secure HMAC token for sandbox service authentication."""
    secret = os.getenv("SANDBOX_TOKEN_SECRET", "default-secret")
    expires_at = datetime.now(datetime.UTC) + timedelta(seconds=expires_in)

    payload = {
        "execution_id": execution_id,
        "expires_at": expires_at.isoformat(),
    }

    payload_json = json.dumps(payload, sort_keys=True)
    signature = hmac.new(
        secret.encode(),
        payload_json.encode(),
        hashlib.sha256,
    ).hexdigest()

    token_data = {"payload": payload, "signature": signature}
    return base64.b64encode(json.dumps(token_data).encode()).decode()
