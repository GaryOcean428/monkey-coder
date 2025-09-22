"""
Railway Health Check Monitoring Dashboard

This module provides a comprehensive health check monitoring dashboard
for Railway deployments with real-time status tracking and alerting.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import aiohttp
import ssl
import certifi

from fastapi import HTTPException
from fastapi.responses import HTMLResponse


logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health check status enum."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Health check result data structure."""
    endpoint: str
    status: HealthStatus
    response_time: float
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class ComponentHealth:
    """Component health tracking."""
    name: str
    endpoint: str
    last_check: Optional[datetime] = None
    current_status: HealthStatus = HealthStatus.UNKNOWN
    response_time: Optional[float] = None
    consecutive_failures: int = 0
    uptime_percentage: float = 100.0
    history: List[HealthCheckResult] = None
    
    def __post_init__(self):
        if self.history is None:
            self.history = []


class HealthMonitor:
    """Monitors health of Railway deployed components."""
    
    def __init__(self, deployment_url: str):
        self.deployment_url = deployment_url.rstrip('/')
        self.components: Dict[str, ComponentHealth] = {}
        self.monitoring_interval = 30  # seconds
        self.alert_threshold = 3  # consecutive failures before alerting
        self.history_retention = 1440  # Keep 24 hours of history (1440 checks at 1 min intervals)
        
        # Initialize standard components
        self._initialize_components()
        
        # Monitoring state
        self._monitoring_active = False
        self._monitoring_task = None
    
    def _initialize_components(self):
        """Initialize standard Railway components to monitor."""
        standard_components = [
            ("API Health", "/health"),
            ("API Readiness", "/health/readiness"),
            ("Comprehensive Health", "/health/comprehensive"),
            ("API Documentation", "/api/docs"),
            ("Metrics Endpoint", "/metrics"),
            ("Frontend Root", "/"),
        ]
        
        for name, endpoint in standard_components:
            self.components[name] = ComponentHealth(
                name=name,
                endpoint=endpoint
            )
    
    async def check_component_health(self, component: ComponentHealth) -> HealthCheckResult:
        """Check health of a single component."""
        url = f"{self.deployment_url}{component.endpoint}"
        start_time = time.time()
        
        try:
            # Create SSL context for HTTPS requests
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.get(url) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        # For health endpoints, also check response content
                        if "/health" in component.endpoint:
                            try:
                                data = await response.json()
                                if data.get("status") == "healthy":
                                    status = HealthStatus.HEALTHY
                                else:
                                    status = HealthStatus.DEGRADED
                            except:
                                status = HealthStatus.DEGRADED
                        else:
                            status = HealthStatus.HEALTHY
                    elif response.status in [404, 503]:
                        status = HealthStatus.DEGRADED
                    else:
                        status = HealthStatus.UNHEALTHY
                    
                    return HealthCheckResult(
                        endpoint=component.endpoint,
                        status=status,
                        response_time=response_time,
                        status_code=response.status
                    )
                    
        except asyncio.TimeoutError:
            return HealthCheckResult(
                endpoint=component.endpoint,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                error_message="Request timeout"
            )
        except Exception as e:
            return HealthCheckResult(
                endpoint=component.endpoint,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def check_all_components(self) -> Dict[str, HealthCheckResult]:
        """Check health of all components."""
        tasks = []
        for component in self.components.values():
            tasks.append(self.check_component_health(component))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        health_results = {}
        for i, (name, component) in enumerate(self.components.items()):
            result = results[i]
            if isinstance(result, Exception):
                result = HealthCheckResult(
                    endpoint=component.endpoint,
                    status=HealthStatus.UNHEALTHY,
                    response_time=30.0,
                    error_message=str(result)
                )
            
            # Update component state
            component.last_check = result.timestamp
            component.current_status = result.status
            component.response_time = result.response_time
            
            # Track consecutive failures
            if result.status == HealthStatus.UNHEALTHY:
                component.consecutive_failures += 1
            else:
                component.consecutive_failures = 0
            
            # Add to history and maintain retention limit
            component.history.append(result)
            if len(component.history) > self.history_retention:
                component.history = component.history[-self.history_retention:]
            
            # Calculate uptime percentage
            if component.history:
                healthy_checks = sum(1 for h in component.history if h.status == HealthStatus.HEALTHY)
                component.uptime_percentage = (healthy_checks / len(component.history)) * 100
            
            health_results[name] = result
        
        return health_results
    
    async def start_monitoring(self):
        """Start continuous health monitoring."""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Health monitoring started")
    
    async def stop_monitoring(self):
        """Stop continuous health monitoring."""
        self._monitoring_active = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Health monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self._monitoring_active:
            try:
                await self.check_all_components()
                await asyncio.sleep(self.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        overall_status = HealthStatus.HEALTHY
        unhealthy_count = 0
        total_response_time = 0
        valid_response_times = 0
        
        components_data = {}
        for name, component in self.components.items():
            components_data[name] = {
                "name": component.name,
                "endpoint": component.endpoint,
                "status": component.current_status.value,
                "last_check": component.last_check.isoformat() if component.last_check else None,
                "response_time": component.response_time,
                "consecutive_failures": component.consecutive_failures,
                "uptime_percentage": round(component.uptime_percentage, 2),
                "needs_attention": component.consecutive_failures >= self.alert_threshold
            }
            
            if component.current_status == HealthStatus.UNHEALTHY:
                unhealthy_count += 1
                overall_status = HealthStatus.UNHEALTHY
            elif component.current_status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                overall_status = HealthStatus.DEGRADED
            
            if component.response_time is not None:
                total_response_time += component.response_time
                valid_response_times += 1
        
        average_response_time = (total_response_time / valid_response_times) if valid_response_times > 0 else 0
        
        return {
            "overall_status": overall_status.value,
            "components": components_data,
            "summary": {
                "total_components": len(self.components),
                "healthy_components": len([c for c in self.components.values() if c.current_status == HealthStatus.HEALTHY]),
                "unhealthy_components": unhealthy_count,
                "average_response_time": round(average_response_time, 3),
                "components_needing_attention": len([c for c in self.components.values() if c.consecutive_failures >= self.alert_threshold])
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_component_history(self, component_name: str, hours: int = 1) -> List[Dict[str, Any]]:
        """Get historical data for a specific component."""
        if component_name not in self.components:
            return []
        
        component = self.components[component_name]
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        history = [
            {
                "timestamp": h.timestamp.isoformat(),
                "status": h.status.value,
                "response_time": h.response_time,
                "status_code": h.status_code,
                "error_message": h.error_message
            }
            for h in component.history
            if h.timestamp >= cutoff
        ]
        
        return history


# Global health monitor instance
health_monitor = None


def get_health_monitor(deployment_url: str = None) -> HealthMonitor:
    """Get the global health monitor instance."""
    global health_monitor
    
    if health_monitor is None:
        if deployment_url is None:
            deployment_url = "https://coder.fastmonkey.au"  # Default Railway URL
        health_monitor = HealthMonitor(deployment_url)
    
    return health_monitor


def generate_dashboard_html(dashboard_data: Dict[str, Any]) -> str:
    """Generate HTML dashboard for health monitoring."""
    
    overall_status = dashboard_data["overall_status"]
    components = dashboard_data["components"]
    summary = dashboard_data["summary"]
    
    status_color = {
        "healthy": "#28a745",
        "degraded": "#ffc107", 
        "unhealthy": "#dc3545",
        "unknown": "#6c757d"
    }
    
    components_html = ""
    for name, component in components.items():
        status = component["status"]
        color = status_color.get(status, "#6c757d")
        attention_badge = "🔥" if component["needs_attention"] else ""
        
        components_html += f"""
        <div class="component-card" style="border-left: 4px solid {color};">
            <h4>{component['name']} {attention_badge}</h4>
            <div class="status-badge" style="background-color: {color};">{status.upper()}</div>
            <div class="component-details">
                <p><strong>Endpoint:</strong> {component['endpoint']}</p>
                <p><strong>Response Time:</strong> {component['response_time']:.3f}s</p>
                <p><strong>Uptime:</strong> {component['uptime_percentage']}%</p>
                <p><strong>Consecutive Failures:</strong> {component['consecutive_failures']}</p>
                <p><strong>Last Check:</strong> {component['last_check'] or 'Never'}</p>
            </div>
        </div>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Railway Health Monitoring Dashboard</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f8f9fa;
                color: #333;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .overall-status {{
                font-size: 2em;
                font-weight: bold;
                color: {status_color.get(overall_status, '#6c757d')};
                margin-bottom: 10px;
            }}
            .summary {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .summary-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .summary-number {{
                font-size: 2em;
                font-weight: bold;
                color: #007bff;
            }}
            .components-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
                gap: 20px;
            }}
            .component-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .status-badge {{
                display: inline-block;
                color: white;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 0.8em;
                font-weight: bold;
                margin-left: 10px;
            }}
            .component-details {{
                margin-top: 15px;
                font-size: 0.9em;
            }}
            .component-details p {{
                margin: 5px 0;
            }}
            .refresh-info {{
                text-align: center;
                margin-top: 30px;
                color: #6c757d;
                font-size: 0.9em;
            }}
        </style>
        <script>
            // Auto-refresh every 30 seconds
            setTimeout(function() {{
                window.location.reload();
            }}, 30000);
        </script>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Railway Health Monitoring Dashboard</h1>
            <div class="overall-status">{overall_status.upper()}</div>
            <p>Last updated: {dashboard_data['timestamp']}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <div class="summary-number">{summary['total_components']}</div>
                <div>Total Components</div>
            </div>
            <div class="summary-card">
                <div class="summary-number" style="color: #28a745;">{summary['healthy_components']}</div>
                <div>Healthy</div>
            </div>
            <div class="summary-card">
                <div class="summary-number" style="color: #dc3545;">{summary['unhealthy_components']}</div>
                <div>Unhealthy</div>
            </div>
            <div class="summary-card">
                <div class="summary-number">{summary['average_response_time']:.3f}s</div>
                <div>Avg Response Time</div>
            </div>
            <div class="summary-card">
                <div class="summary-number" style="color: #ffc107;">{summary['components_needing_attention']}</div>
                <div>Need Attention</div>
            </div>
        </div>
        
        <div class="components-grid">
            {components_html}
        </div>
        
        <div class="refresh-info">
            Dashboard auto-refreshes every 30 seconds
        </div>
    </body>
    </html>
    """
    
    return html