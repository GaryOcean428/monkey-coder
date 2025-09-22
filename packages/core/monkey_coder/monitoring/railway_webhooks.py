"""
Railway Deployment Webhooks

This module provides webhook handlers for Railway deployment events to track
deployment success/failure rates and monitor deployment health.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
import json
import aiohttp
import hashlib
import hmac

from fastapi import HTTPException, BackgroundTasks
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class DeploymentStatus(str, Enum):
    """Railway deployment status enum."""
    PENDING = "pending"
    BUILDING = "building"
    DEPLOYING = "deploying"
    SUCCESS = "success"
    FAILED = "failed"
    CRASHED = "crashed"
    REMOVED = "removed"


class WebhookEventType(str, Enum):
    """Railway webhook event types."""
    DEPLOYMENT_STATUS = "deployment.status"
    SERVICE_STATUS = "service.status"
    BUILD_STATUS = "build.status"


@dataclass
class DeploymentMetrics:
    """Deployment metrics tracking."""
    deployment_id: str
    project_id: str
    service_id: str
    status: DeploymentStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    build_duration: Optional[float] = None
    deployment_duration: Optional[float] = None
    error_message: Optional[str] = None
    health_check_passed: bool = False
    health_check_duration: Optional[float] = None


class RailwayWebhookPayload(BaseModel):
    """Railway webhook payload model."""
    type: WebhookEventType
    timestamp: str
    data: Dict[str, Any]
    project: Dict[str, Any]
    service: Dict[str, Any]
    deployment: Optional[Dict[str, Any]] = None


class DeploymentTracker:
    """Tracks Railway deployment metrics and status."""
    
    def __init__(self):
        self.deployments: Dict[str, DeploymentMetrics] = {}
        self.metrics_file = Path("data/deployment_metrics.json")
        self.metrics_file.parent.mkdir(exist_ok=True)
        self._load_metrics()
    
    def _load_metrics(self):
        """Load existing metrics from file."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file) as f:
                    data = json.load(f)
                    for deployment_id, metrics_data in data.items():
                        self.deployments[deployment_id] = DeploymentMetrics(
                            deployment_id=metrics_data["deployment_id"],
                            project_id=metrics_data["project_id"],
                            service_id=metrics_data["service_id"],
                            status=DeploymentStatus(metrics_data["status"]),
                            start_time=datetime.fromisoformat(metrics_data["start_time"]),
                            end_time=datetime.fromisoformat(metrics_data["end_time"]) if metrics_data.get("end_time") else None,
                            build_duration=metrics_data.get("build_duration"),
                            deployment_duration=metrics_data.get("deployment_duration"),
                            error_message=metrics_data.get("error_message"),
                            health_check_passed=metrics_data.get("health_check_passed", False),
                            health_check_duration=metrics_data.get("health_check_duration")
                        )
            except Exception as e:
                logger.warning(f"Failed to load metrics: {e}")
    
    def _save_metrics(self):
        """Save metrics to file."""
        try:
            data = {}
            for deployment_id, metrics in self.deployments.items():
                data[deployment_id] = {
                    "deployment_id": metrics.deployment_id,
                    "project_id": metrics.project_id,
                    "service_id": metrics.service_id,
                    "status": metrics.status.value,
                    "start_time": metrics.start_time.isoformat(),
                    "end_time": metrics.end_time.isoformat() if metrics.end_time else None,
                    "build_duration": metrics.build_duration,
                    "deployment_duration": metrics.deployment_duration,
                    "error_message": metrics.error_message,
                    "health_check_passed": metrics.health_check_passed,
                    "health_check_duration": metrics.health_check_duration
                }
            
            with open(self.metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def track_deployment(self, payload: RailwayWebhookPayload) -> DeploymentMetrics:
        """Track a deployment event."""
        deployment_data = payload.deployment or {}
        deployment_id = deployment_data.get("id", "unknown")
        
        if deployment_id not in self.deployments:
            self.deployments[deployment_id] = DeploymentMetrics(
                deployment_id=deployment_id,
                project_id=payload.project.get("id", "unknown"),
                service_id=payload.service.get("id", "unknown"),
                status=DeploymentStatus.PENDING,
                start_time=datetime.fromisoformat(payload.timestamp.replace('Z', '+00:00'))
            )
        
        metrics = self.deployments[deployment_id]
        
        # Update status and timing
        new_status = deployment_data.get("status", "unknown")
        if new_status in DeploymentStatus._value2member_map_:
            metrics.status = DeploymentStatus(new_status)
        
        if metrics.status in [DeploymentStatus.SUCCESS, DeploymentStatus.FAILED, DeploymentStatus.CRASHED]:
            metrics.end_time = datetime.fromisoformat(payload.timestamp.replace('Z', '+00:00'))
            if metrics.start_time:
                metrics.deployment_duration = (metrics.end_time - metrics.start_time).total_seconds()
        
        # Track build duration if available
        if "buildDuration" in deployment_data:
            metrics.build_duration = deployment_data["buildDuration"]
        
        # Track error message for failed deployments
        if metrics.status == DeploymentStatus.FAILED:
            metrics.error_message = deployment_data.get("error", "Unknown deployment error")
        
        self._save_metrics()
        return metrics
    
    def get_success_rate(self, hours: int = 24) -> Dict[str, float]:
        """Calculate deployment success rate for the specified time period."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_deployments = [
            m for m in self.deployments.values()
            if m.start_time >= cutoff and m.status in [DeploymentStatus.SUCCESS, DeploymentStatus.FAILED, DeploymentStatus.CRASHED]
        ]
        
        if not recent_deployments:
            return {"success_rate": 0.0, "total_deployments": 0, "successful_deployments": 0}
        
        successful = len([d for d in recent_deployments if d.status == DeploymentStatus.SUCCESS])
        total = len(recent_deployments)
        
        return {
            "success_rate": (successful / total) * 100,
            "total_deployments": total,
            "successful_deployments": successful,
            "failed_deployments": total - successful
        }
    
    def get_average_startup_time(self, hours: int = 24) -> Dict[str, float]:
        """Calculate average container startup time."""
        cutoff = datetime.now() - timedelta(hours=hours)
        successful_deployments = [
            m for m in self.deployments.values()
            if (m.start_time >= cutoff and 
                m.status == DeploymentStatus.SUCCESS and 
                m.deployment_duration is not None)
        ]
        
        if not successful_deployments:
            return {"average_startup_time": 0.0, "sample_size": 0}
        
        total_duration = sum(d.deployment_duration for d in successful_deployments)
        average = total_duration / len(successful_deployments)
        
        return {
            "average_startup_time": average,
            "sample_size": len(successful_deployments),
            "min_startup_time": min(d.deployment_duration for d in successful_deployments),
            "max_startup_time": max(d.deployment_duration for d in successful_deployments)
        }


class AlertManager:
    """Manages alerts for deployment failures and health check issues."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url
        self.alert_cooldown = 300  # 5 minutes cooldown between alerts
        self.last_alert_times: Dict[str, datetime] = {}
    
    async def send_alert(self, alert_type: str, message: str, details: Dict[str, Any] = None):
        """Send an alert notification."""
        if not self.webhook_url:
            logger.warning(f"No webhook URL configured for alert: {alert_type}")
            return
        
        # Check cooldown
        last_alert = self.last_alert_times.get(alert_type)
        if last_alert and (datetime.now() - last_alert).total_seconds() < self.alert_cooldown:
            logger.debug(f"Alert {alert_type} skipped due to cooldown")
            return
        
        payload = {
            "text": f"🚨 Railway Deployment Alert: {alert_type}",
            "attachments": [{
                "color": "danger",
                "fields": [
                    {"title": "Alert Type", "value": alert_type, "short": True},
                    {"title": "Message", "value": message, "short": False},
                    {"title": "Timestamp", "value": datetime.now().isoformat(), "short": True}
                ]
            }]
        }
        
        if details:
            for key, value in details.items():
                payload["attachments"][0]["fields"].append({
                    "title": key.replace('_', ' ').title(),
                    "value": str(value),
                    "short": True
                })
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        self.last_alert_times[alert_type] = datetime.now()
                        logger.info(f"Alert sent successfully: {alert_type}")
                    else:
                        logger.error(f"Failed to send alert: HTTP {response.status}")
        except Exception as e:
            logger.error(f"Failed to send alert {alert_type}: {e}")
    
    async def check_deployment_failure(self, metrics: DeploymentMetrics):
        """Check for deployment failures and send alerts."""
        if metrics.status == DeploymentStatus.FAILED:
            await self.send_alert(
                alert_type="Deployment Failed",
                message=f"Deployment {metrics.deployment_id} failed",
                details={
                    "deployment_id": metrics.deployment_id,
                    "service_id": metrics.service_id,
                    "error_message": metrics.error_message or "Unknown error",
                    "duration": f"{metrics.deployment_duration:.2f}s" if metrics.deployment_duration else "Unknown"
                }
            )
        
        elif metrics.status == DeploymentStatus.CRASHED:
            await self.send_alert(
                alert_type="Deployment Crashed",
                message=f"Deployment {metrics.deployment_id} crashed after startup",
                details={
                    "deployment_id": metrics.deployment_id,
                    "service_id": metrics.service_id,
                    "uptime": f"{metrics.deployment_duration:.2f}s" if metrics.deployment_duration else "Unknown"
                }
            )
    
    async def check_health_failure(self, deployment_id: str, health_check_duration: float):
        """Check for health check failures and send alerts."""
        if health_check_duration > 30:  # Alert if health check takes more than 30 seconds
            await self.send_alert(
                alert_type="Health Check Slow",
                message=f"Health check for deployment {deployment_id} took {health_check_duration:.2f} seconds",
                details={
                    "deployment_id": deployment_id,
                    "health_check_duration": f"{health_check_duration:.2f}s",
                    "threshold": "30s"
                }
            )


# Global instances
deployment_tracker = DeploymentTracker()
alert_manager = AlertManager()


async def handle_railway_webhook(payload: RailwayWebhookPayload, background_tasks: BackgroundTasks):
    """Handle incoming Railway webhook events."""
    try:
        # Track deployment metrics
        metrics = deployment_tracker.track_deployment(payload)
        
        # Check for alerts
        background_tasks.add_task(alert_manager.check_deployment_failure, metrics)
        
        logger.info(f"Processed webhook event: {payload.type} for deployment {metrics.deployment_id}")
        
        return {
            "status": "processed",
            "deployment_id": metrics.deployment_id,
            "current_status": metrics.status.value
        }
    
    except Exception as e:
        logger.error(f"Failed to process webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")


def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify Railway webhook signature."""
    if not secret:
        logger.warning("No webhook secret configured - signature verification disabled")
        return True
    
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected_signature}", signature)