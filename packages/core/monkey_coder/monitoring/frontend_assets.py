"""
Frontend Asset Monitoring System

This module monitors the availability and integrity of frontend assets
served by the Railway deployment, including static files, build outputs,
and API integration points.
"""

import asyncio
import logging
import hashlib
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import json
import aiohttp
import ssl
import certifi


logger = logging.getLogger(__name__)


@dataclass
class AssetStatus:
    """Frontend asset status tracking."""
    path: str
    exists: bool
    size_bytes: Optional[int] = None
    checksum: Optional[str] = None
    last_modified: Optional[datetime] = None
    served_correctly: bool = False
    response_time: Optional[float] = None
    content_type: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class FrontendHealthCheck:
    """Frontend health check result."""
    timestamp: datetime
    overall_status: str  # "healthy", "degraded", "failed"
    assets_checked: int
    assets_available: int
    critical_assets_missing: List[str]
    warnings: List[str]
    total_size_mb: float
    avg_response_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "overall_status": self.overall_status,
            "assets_checked": self.assets_checked,
            "assets_available": self.assets_available,
            "critical_assets_missing": self.critical_assets_missing,
            "warnings": self.warnings,
            "total_size_mb": self.total_size_mb,
            "avg_response_time": self.avg_response_time
        }


class FrontendAssetMonitor:
    """Monitors frontend asset availability and integrity."""
    
    def __init__(self, deployment_url: str, frontend_path: str = None):
        self.deployment_url = deployment_url.rstrip('/')
        self.frontend_path = Path(frontend_path or "/app/packages/web/out")
        
        # Critical assets that must be available
        self.critical_assets = [
            "/",
            "/index.html",
            "/favicon.ico",
            "/_next/static/css/",  # CSS bundles (will be dynamic)
            "/_next/static/js/",   # JS bundles (will be dynamic)
        ]
        
        # Asset patterns to check
        self.asset_patterns = [
            "*.html",
            "*.css", 
            "*.js",
            "*.ico",
            "*.png",
            "*.jpg",
            "*.svg",
            "*.woff2"
        ]
        
        # Monitoring state
        self.last_check: Optional[FrontendHealthCheck] = None
        self.check_history: List[FrontendHealthCheck] = []
        self.asset_cache: Dict[str, AssetStatus] = {}
    
    def scan_local_assets(self) -> Dict[str, AssetStatus]:
        """Scan local filesystem for frontend assets."""
        assets = {}
        
        if not self.frontend_path.exists():
            logger.warning(f"Frontend path does not exist: {self.frontend_path}")
            return assets
        
        # Scan for asset files
        for pattern in self.asset_patterns:
            for file_path in self.frontend_path.rglob(pattern):
                if file_path.is_file():
                    relative_path = "/" + str(file_path.relative_to(self.frontend_path))
                    
                    # Calculate file checksum
                    checksum = self._calculate_file_checksum(file_path)
                    
                    assets[relative_path] = AssetStatus(
                        path=relative_path,
                        exists=True,
                        size_bytes=file_path.stat().st_size,
                        checksum=checksum,
                        last_modified=datetime.fromtimestamp(file_path.stat().st_mtime)
                    )
        
        return assets
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()[:16]  # First 16 chars for brevity
        except Exception as e:
            logger.warning(f"Failed to calculate checksum for {file_path}: {e}")
            return "unknown"
    
    async def check_asset_availability(self, asset_path: str) -> AssetStatus:
        """Check if an asset is available via HTTP."""
        url = f"{self.deployment_url}{asset_path}"
        
        try:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            timeout = aiohttp.ClientTimeout(total=10)
            
            start_time = time.time()
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.get(url) as response:
                    response_time = time.time() - start_time
                    
                    asset_status = AssetStatus(
                        path=asset_path,
                        exists=response.status == 200,
                        served_correctly=response.status == 200,
                        response_time=response_time,
                        content_type=response.headers.get('content-type')
                    )
                    
                    if response.status == 200:
                        content = await response.read()
                        asset_status.size_bytes = len(content)
                        asset_status.checksum = hashlib.sha256(content).hexdigest()[:16]
                    else:
                        asset_status.error_message = f"HTTP {response.status}"
                    
                    return asset_status
                    
        except asyncio.TimeoutError:
            return AssetStatus(
                path=asset_path,
                exists=False,
                served_correctly=False,
                error_message="Request timeout"
            )
        except Exception as e:
            return AssetStatus(
                path=asset_path,
                exists=False,
                served_correctly=False,
                error_message=str(e)
            )
    
    async def discover_dynamic_assets(self) -> List[str]:
        """Discover dynamic assets like webpack bundles."""
        discovered_assets = []
        
        try:
            # Check if main page loads and parse for asset references
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.deployment_url}/") as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Look for _next/static references (Next.js)
                        import re
                        static_refs = re.findall(r'/_next/static/[^"\'>\s]+', content)
                        discovered_assets.extend(static_refs)
                        
                        # Look for other asset references
                        asset_refs = re.findall(r'/[^"\'>\s]*\.(css|js|png|jpg|svg|ico|woff2)', content)
                        discovered_assets.extend(asset_refs)
        
        except Exception as e:
            logger.warning(f"Failed to discover dynamic assets: {e}")
        
        return list(set(discovered_assets))  # Remove duplicates
    
    async def comprehensive_asset_check(self) -> FrontendHealthCheck:
        """Perform comprehensive frontend asset check."""
        start_time = datetime.utcnow()
        
        # Scan local assets
        local_assets = self.scan_local_assets()
        
        # Discover dynamic assets
        dynamic_assets = await self.discover_dynamic_assets()
        
        # Combine critical assets with discovered assets
        all_assets_to_check = set(self.critical_assets + dynamic_assets + list(local_assets.keys()))
        
        # Check asset availability
        asset_checks = []
        for asset_path in all_assets_to_check:
            asset_status = await self.check_asset_availability(asset_path)
            asset_checks.append(asset_status)
            self.asset_cache[asset_path] = asset_status
        
        # Analyze results
        assets_available = len([a for a in asset_checks if a.served_correctly])
        critical_missing = []
        warnings = []
        
        for critical_asset in self.critical_assets:
            # For pattern-based assets, check if any matching assets exist
            if critical_asset.endswith('/'):
                matching_assets = [a for a in asset_checks if a.path.startswith(critical_asset)]
                if not matching_assets or not any(a.served_correctly for a in matching_assets):
                    critical_missing.append(critical_asset)
            else:
                asset_status = next((a for a in asset_checks if a.path == critical_asset), None)
                if not asset_status or not asset_status.served_correctly:
                    critical_missing.append(critical_asset)
        
        # Calculate metrics
        total_size_bytes = sum(a.size_bytes or 0 for a in asset_checks if a.size_bytes)
        total_size_mb = total_size_bytes / (1024 * 1024)
        
        response_times = [a.response_time for a in asset_checks if a.response_time]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Determine overall status
        if critical_missing:
            overall_status = "failed"
        elif len(warnings) > 0 or assets_available < len(asset_checks) * 0.9:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        # Add warnings for various issues
        if not local_assets:
            warnings.append("No local frontend assets found")
        
        if avg_response_time > 2.0:
            warnings.append(f"Slow asset response time: {avg_response_time:.2f}s")
        
        if total_size_mb > 50:
            warnings.append(f"Large total asset size: {total_size_mb:.2f}MB")
        
        health_check = FrontendHealthCheck(
            timestamp=start_time,
            overall_status=overall_status,
            assets_checked=len(asset_checks),
            assets_available=assets_available,
            critical_assets_missing=critical_missing,
            warnings=warnings,
            total_size_mb=total_size_mb,
            avg_response_time=avg_response_time
        )
        
        # Update state
        self.last_check = health_check
        self.check_history.append(health_check)
        
        # Keep only recent history (last 24 hours worth)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.check_history = [h for h in self.check_history if h.timestamp >= cutoff]
        
        return health_check
    
    def get_asset_details(self) -> Dict[str, Any]:
        """Get detailed asset information."""
        return {
            "assets": {path: {
                "path": asset.path,
                "exists": asset.exists,
                "size_bytes": asset.size_bytes,
                "checksum": asset.checksum,
                "served_correctly": asset.served_correctly,
                "response_time": asset.response_time,
                "content_type": asset.content_type,
                "error_message": asset.error_message,
                "last_modified": asset.last_modified.isoformat() if asset.last_modified else None
            } for path, asset in self.asset_cache.items()},
            "summary": {
                "total_assets": len(self.asset_cache),
                "available_assets": len([a for a in self.asset_cache.values() if a.served_correctly]),
                "total_size_bytes": sum(a.size_bytes or 0 for a in self.asset_cache.values()),
                "last_check": self.last_check.timestamp.isoformat() if self.last_check else None
            }
        }
    
    def get_availability_trend(self, hours: int = 6) -> Dict[str, Any]:
        """Get frontend availability trend over time."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent_checks = [h for h in self.check_history if h.timestamp >= cutoff]
        
        if not recent_checks:
            return {"trend": "no_data", "checks": 0}
        
        healthy_checks = len([h for h in recent_checks if h.overall_status == "healthy"])
        degraded_checks = len([h for h in recent_checks if h.overall_status == "degraded"])
        failed_checks = len([h for h in recent_checks if h.overall_status == "failed"])
        
        availability_percentage = (healthy_checks / len(recent_checks)) * 100
        
        return {
            "availability_percentage": availability_percentage,
            "total_checks": len(recent_checks),
            "healthy_checks": healthy_checks,
            "degraded_checks": degraded_checks,
            "failed_checks": failed_checks,
            "trend": "improving" if recent_checks[-1].overall_status == "healthy" else "declining",
            "query_period_hours": hours,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global frontend monitor instance
frontend_monitor = None


def get_frontend_monitor(deployment_url: str = None, frontend_path: str = None) -> FrontendAssetMonitor:
    """Get the global frontend monitor instance."""
    global frontend_monitor
    
    if frontend_monitor is None:
        if deployment_url is None:
            deployment_url = os.getenv("RAILWAY_DEPLOYMENT_URL", "https://coder.fastmonkey.au")
        if frontend_path is None:
            frontend_path = os.getenv("FRONTEND_OUT_PATH", "/app/packages/web/out")
            
        frontend_monitor = FrontendAssetMonitor(deployment_url, frontend_path)
    
    return frontend_monitor