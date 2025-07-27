"""
Sandbox Security Manager

Implements security controls, resource limits, and authentication for sandbox operations.
"""

import asyncio
import hashlib
import hmac
import logging
import os
import psutil
import resource
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)


# Security configuration
SANDBOX_TOKEN_SECRET = os.getenv("SANDBOX_TOKEN_SECRET", "default-sandbox-secret-change-me")
MAX_MEMORY_MB = int(os.getenv("SANDBOX_MAX_MEMORY_MB", "512"))
MAX_CPU_PERCENT = float(os.getenv("SANDBOX_MAX_CPU_PERCENT", "50.0"))
MAX_DISK_MB = int(os.getenv("SANDBOX_MAX_DISK_MB", "1024"))
MAX_NETWORK_MBPS = float(os.getenv("SANDBOX_MAX_NETWORK_MBPS", "10.0"))

# Security bearer token scheme
security = HTTPBearer()


class SecurityManager:
    """Manages security policies and resource limits for sandbox operations."""
    
    def __init__(self):
        self.resource_usage_history: Dict[str, Any] = {}
        self.blocked_domains: set = {
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
            "169.254.169.254",  # AWS metadata
            "metadata.google.internal",  # GCP metadata
        }
        self.allowed_protocols = {"http", "https"}
    
    def validate_url(self, url: str) -> bool:
        """
        Validate that URL is safe for sandbox access.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is safe, False otherwise
        """
        try:
            from urllib.parse import urlparse
            
            parsed = urlparse(url)
            
            # Check protocol
            if parsed.scheme not in self.allowed_protocols:
                logger.warning(f"Blocked URL with invalid protocol: {url}")
                return False
            
            # Check for blocked domains
            hostname = parsed.hostname
            if hostname in self.blocked_domains:
                logger.warning(f"Blocked access to restricted domain: {hostname}")
                return False
            
            # Check for private IP ranges
            if self._is_private_ip(hostname):
                logger.warning(f"Blocked access to private IP: {hostname}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"URL validation failed: {str(e)}")
            return False
    
    def _is_private_ip(self, hostname: str) -> bool:
        """Check if hostname is a private IP address."""
        try:
            import ipaddress
            ip = ipaddress.ip_address(hostname)
            return ip.is_private or ip.is_loopback or ip.is_link_local
        except ValueError:
            # Not an IP address
            return False
    
    def validate_code(self, code: str) -> bool:
        """
        Validate that code is safe for execution.
        
        Args:
            code: Python code to validate
            
        Returns:
            True if code is safe, False otherwise
        """
        # List of dangerous imports and functions
        dangerous_patterns = [
            "import os",
            "import sys",
            "import subprocess",
            "import socket",
            "import requests",
            "import urllib",
            "import http",
            "import ftplib",
            "import smtplib",
            "import telnetlib",
            "__import__",
            "eval(",
            "exec(",
            "compile(",
            "open(",
            "file(",
            "input(",
            "raw_input(",
        ]
        
        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                logger.warning(f"Blocked code containing dangerous pattern: {pattern}")
                return False
        
        return True
    
    async def check_resource_limits(self) -> Dict[str, Any]:
        """
        Check current resource usage against limits.
        
        Returns:
            Dictionary with resource usage and limit status
        """
        try:
            # Get current process
            process = psutil.Process()
            
            # Memory usage
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            memory_percent = (memory_mb / MAX_MEMORY_MB) * 100
            
            # CPU usage
            cpu_percent = process.cpu_percent(interval=0.1)
            
            # Disk usage (of /sandbox directory)
            disk_usage = psutil.disk_usage('/sandbox')
            disk_used_mb = (disk_usage.total - disk_usage.free) / 1024 / 1024
            disk_percent = (disk_used_mb / MAX_DISK_MB) * 100
            
            return {
                "memory": {
                    "used_mb": memory_mb,
                    "limit_mb": MAX_MEMORY_MB,
                    "percent": memory_percent,
                    "exceeded": memory_mb > MAX_MEMORY_MB
                },
                "cpu": {
                    "percent": cpu_percent,
                    "limit_percent": MAX_CPU_PERCENT,
                    "exceeded": cpu_percent > MAX_CPU_PERCENT
                },
                "disk": {
                    "used_mb": disk_used_mb,
                    "limit_mb": MAX_DISK_MB,
                    "percent": disk_percent,
                    "exceeded": disk_used_mb > MAX_DISK_MB
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to check resource limits: {str(e)}")
            return {}


def generate_sandbox_token(execution_id: str, expires_in: int = 3600) -> str:
    """
    Generate a secure token for sandbox operations.
    
    Args:
        execution_id: Unique execution identifier
        expires_in: Token expiration time in seconds
        
    Returns:
        Base64 encoded token
    """
    import base64
    import json
    
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    
    payload = {
        "execution_id": execution_id,
        "expires_at": expires_at.isoformat(),
    }
    
    payload_json = json.dumps(payload, sort_keys=True)
    signature = hmac.new(
        SANDBOX_TOKEN_SECRET.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()
    
    token_data = {
        "payload": payload,
        "signature": signature
    }
    
    token_json = json.dumps(token_data)
    return base64.b64encode(token_json.encode()).decode()


def verify_sandbox_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a sandbox token.
    
    Args:
        token: Base64 encoded token
        
    Returns:
        Token payload if valid
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    import base64
    import json
    
    try:
        # Decode token
        token_json = base64.b64decode(token.encode()).decode()
        token_data = json.loads(token_json)
        
        payload = token_data["payload"]
        signature = token_data["signature"]
        
        # Verify signature
        payload_json = json.dumps(payload, sort_keys=True)
        expected_signature = hmac.new(
            SANDBOX_TOKEN_SECRET.encode(),
            payload_json.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            raise HTTPException(status_code=401, detail="Invalid token signature")
        
        # Check expiration
        expires_at = datetime.fromisoformat(payload["expires_at"])
        if datetime.utcnow() > expires_at:
            raise HTTPException(status_code=401, detail="Token expired")
        
        return payload
        
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_sandbox_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract and validate sandbox token from Authorization header.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        Validated token payload
    """
    try:
        token = credentials.credentials
        payload = verify_sandbox_token(token)
        return payload["execution_id"]
        
    except Exception as e:
        logger.error(f"Token extraction failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Valid sandbox token required"
        )


async def enforce_resource_limits():
    """
    Enforce resource limits and raise exception if exceeded.
    
    Raises:
        HTTPException: If resource limits are exceeded
    """
    security_manager = SecurityManager()
    limits = await security_manager.check_resource_limits()
    
    if not limits:
        return
    
    # Check for limit violations
    violations = []
    
    if limits.get("memory", {}).get("exceeded"):
        violations.append(f"Memory limit exceeded: {limits['memory']['used_mb']:.1f}MB > {MAX_MEMORY_MB}MB")
    
    if limits.get("cpu", {}).get("exceeded"):
        violations.append(f"CPU limit exceeded: {limits['cpu']['percent']:.1f}% > {MAX_CPU_PERCENT}%")
    
    if limits.get("disk", {}).get("exceeded"):
        violations.append(f"Disk limit exceeded: {limits['disk']['used_mb']:.1f}MB > {MAX_DISK_MB}MB")
    
    if violations:
        logger.error(f"Resource limit violations: {violations}")
        raise HTTPException(
            status_code=429,
            detail=f"Resource limits exceeded: {'; '.join(violations)}"
        )


def configure_process_limits():
    """Configure OS-level process limits for the sandbox."""
    try:
        # Set memory limit (in bytes)
        memory_limit = MAX_MEMORY_MB * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
        
        # Set CPU time limit (30 seconds per execution)
        resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
        
        # Set file size limit (100MB)
        file_size_limit = 100 * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_FSIZE, (file_size_limit, file_size_limit))
        
        # Set number of processes limit
        resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
        
        logger.info("Process resource limits configured")
        
    except Exception as e:
        logger.warning(f"Failed to configure process limits: {str(e)}")


# Initialize process limits on import
configure_process_limits()
