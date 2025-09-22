"""
Railway Automated Rollback System

This module provides automated rollback functionality for Railway deployments
when startup failures or health check failures are detected.
"""

import asyncio
import logging
import json
import os
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import aiohttp
import subprocess

from .railway_webhooks import DeploymentStatus, DeploymentMetrics


logger = logging.getLogger(__name__)


class RollbackReason(str, Enum):
    """Reasons for triggering a rollback."""
    STARTUP_FAILURE = "startup_failure"
    HEALTH_CHECK_FAILURE = "health_check_failure"
    CRASH_LOOP = "crash_loop"
    MANUAL_TRIGGER = "manual_trigger"
    PERFORMANCE_DEGRADATION = "performance_degradation"


@dataclass
class RollbackEvent:
    """Rollback event tracking."""
    deployment_id: str
    previous_deployment_id: Optional[str]
    reason: RollbackReason
    timestamp: datetime
    success: bool = False
    error_message: Optional[str] = None
    rollback_duration: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "deployment_id": self.deployment_id,
            "previous_deployment_id": self.previous_deployment_id,
            "reason": self.reason.value,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "error_message": self.error_message,
            "rollback_duration": self.rollback_duration
        }


class RollbackManager:
    """Manages automated rollback functionality for Railway deployments."""
    
    def __init__(self, project_id: str = None, service_id: str = None):
        self.project_id = project_id or os.getenv("RAILWAY_PROJECT_ID")
        self.service_id = service_id or os.getenv("RAILWAY_SERVICE_ID") 
        self.api_token = os.getenv("RAILWAY_TOKEN")
        self.rollback_enabled = os.getenv("RAILWAY_ROLLBACK_ENABLED", "true").lower() == "true"
        
        # Rollback thresholds
        self.startup_timeout = int(os.getenv("RAILWAY_STARTUP_TIMEOUT", "300"))  # 5 minutes
        self.health_check_timeout = int(os.getenv("RAILWAY_HEALTH_CHECK_TIMEOUT", "30"))  # 30 seconds
        self.crash_threshold = int(os.getenv("RAILWAY_CRASH_THRESHOLD", "3"))  # 3 crashes
        self.crash_window = int(os.getenv("RAILWAY_CRASH_WINDOW", "600"))  # 10 minutes
        
        # State tracking
        self.rollback_history: List[RollbackEvent] = []
        self.recent_deployments: List[DeploymentMetrics] = []
        self.monitoring_active = False
        
        # Load existing history
        self._load_rollback_history()
    
    def _load_rollback_history(self):
        """Load rollback history from file."""
        history_file = "data/rollback_history.json"
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    self.rollback_history = [
                        RollbackEvent(
                            deployment_id=item["deployment_id"],
                            previous_deployment_id=item.get("previous_deployment_id"),
                            reason=RollbackReason(item["reason"]),
                            timestamp=datetime.fromisoformat(item["timestamp"]),
                            success=item.get("success", False),
                            error_message=item.get("error_message"),
                            rollback_duration=item.get("rollback_duration")
                        )
                        for item in data
                    ]
            except Exception as e:
                logger.warning(f"Failed to load rollback history: {e}")
    
    def _save_rollback_history(self):
        """Save rollback history to file."""
        history_file = "data/rollback_history.json"
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        
        try:
            with open(history_file, 'w') as f:
                json.dump([event.to_dict() for event in self.rollback_history], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save rollback history: {e}")
    
    async def check_deployment_health(self, deployment_id: str) -> Tuple[bool, str]:
        """Check if a deployment is healthy."""
        try:
            deployment_url = os.getenv("RAILWAY_DEPLOYMENT_URL", "https://coder.fastmonkey.au")
            health_url = f"{deployment_url}/health"
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=self.health_check_timeout)) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            if data.get("status") == "healthy":
                                return True, f"Health check passed in {response_time:.2f}s"
                            else:
                                return False, f"Health check returned unhealthy status: {data.get('status')}"
                        except:
                            return False, "Health check response is not valid JSON"
                    else:
                        return False, f"Health check returned HTTP {response.status}"
                        
        except asyncio.TimeoutError:
            return False, f"Health check timed out after {self.health_check_timeout}s"
        except Exception as e:
            return False, f"Health check failed: {str(e)}"
    
    def should_rollback(self, deployment: DeploymentMetrics) -> Tuple[bool, RollbackReason]:
        """Determine if a deployment should be rolled back."""
        if not self.rollback_enabled:
            return False, None
        
        # Check for startup failure
        if deployment.status == DeploymentStatus.FAILED:
            if deployment.deployment_duration and deployment.deployment_duration < self.startup_timeout:
                return True, RollbackReason.STARTUP_FAILURE
        
        # Check for crash loop
        if deployment.status == DeploymentStatus.CRASHED:
            # Count recent crashes
            cutoff = datetime.now() - timedelta(seconds=self.crash_window)
            recent_crashes = [
                d for d in self.recent_deployments
                if (d.start_time >= cutoff and 
                    d.status == DeploymentStatus.CRASHED and
                    d.service_id == deployment.service_id)
            ]
            
            if len(recent_crashes) >= self.crash_threshold:
                return True, RollbackReason.CRASH_LOOP
        
        # Check for health check failure
        if (deployment.status == DeploymentStatus.SUCCESS and 
            not deployment.health_check_passed):
            return True, RollbackReason.HEALTH_CHECK_FAILURE
        
        return False, None
    
    async def find_previous_stable_deployment(self, current_deployment_id: str) -> Optional[str]:
        """Find the most recent stable deployment to rollback to."""
        try:
            # Look for the most recent successful deployment before the current one
            stable_deployments = [
                d for d in self.recent_deployments
                if (d.deployment_id != current_deployment_id and
                    d.status == DeploymentStatus.SUCCESS and
                    d.health_check_passed and
                    d.service_id == self.service_id)
            ]
            
            if stable_deployments:
                # Sort by start time and get the most recent
                stable_deployments.sort(key=lambda x: x.start_time, reverse=True)
                return stable_deployments[0].deployment_id
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find previous stable deployment: {e}")
            return None
    
    async def execute_rollback(
        self, 
        current_deployment_id: str, 
        target_deployment_id: str,
        reason: RollbackReason
    ) -> RollbackEvent:
        """Execute a rollback to a previous deployment."""
        rollback_event = RollbackEvent(
            deployment_id=current_deployment_id,
            previous_deployment_id=target_deployment_id,
            reason=reason,
            timestamp=datetime.utcnow()
        )
        
        if not self.api_token:
            rollback_event.error_message = "No Railway API token configured"
            logger.error(rollback_event.error_message)
            return rollback_event
        
        start_time = time.time()
        
        try:
            # Use Railway CLI for rollback if available
            if await self._rollback_via_cli(target_deployment_id):
                rollback_event.success = True
                rollback_event.rollback_duration = time.time() - start_time
                logger.info(f"Rollback successful via CLI: {current_deployment_id} -> {target_deployment_id}")
            else:
                # Fallback to API rollback
                if await self._rollback_via_api(target_deployment_id):
                    rollback_event.success = True
                    rollback_event.rollback_duration = time.time() - start_time
                    logger.info(f"Rollback successful via API: {current_deployment_id} -> {target_deployment_id}")
                else:
                    rollback_event.error_message = "Both CLI and API rollback methods failed"
                    logger.error(rollback_event.error_message)
            
        except Exception as e:
            rollback_event.error_message = f"Rollback execution failed: {str(e)}"
            logger.error(rollback_event.error_message)
        
        # Record rollback event
        self.rollback_history.append(rollback_event)
        self._save_rollback_history()
        
        return rollback_event
    
    async def _rollback_via_cli(self, target_deployment_id: str) -> bool:
        """Attempt rollback using Railway CLI."""
        try:
            # Check if Railway CLI is available
            result = subprocess.run(
                ["railway", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode != 0:
                logger.warning("Railway CLI not available")
                return False
            
            # Perform rollback
            result = subprocess.run([
                "railway", "redeploy", 
                "--deployment", target_deployment_id,
                "--confirm"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"Railway CLI rollback successful: {result.stdout}")
                return True
            else:
                logger.error(f"Railway CLI rollback failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Railway CLI rollback timed out")
            return False
        except Exception as e:
            logger.error(f"Railway CLI rollback error: {e}")
            return False
    
    async def _rollback_via_api(self, target_deployment_id: str) -> bool:
        """Attempt rollback using Railway GraphQL API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            # GraphQL mutation for redeployment
            mutation = """
            mutation DeploymentRedeploy($id: String!) {
                deploymentRedeploy(id: $id) {
                    id
                    status
                }
            }
            """
            
            payload = {
                "query": mutation,
                "variables": {"id": target_deployment_id}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://backboard.railway.app/graphql/v2",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        if not result.get("errors"):
                            logger.info(f"Railway API rollback successful: {result}")
                            return True
                        else:
                            logger.error(f"Railway API rollback failed: {result['errors']}")
                            return False
                    else:
                        logger.error(f"Railway API rollback failed: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Railway API rollback error: {e}")
            return False
    
    async def monitor_deployment(self, deployment: DeploymentMetrics):
        """Monitor a deployment and trigger rollback if necessary."""
        # Add to recent deployments
        self.recent_deployments.append(deployment)
        
        # Keep only recent deployments (last 24 hours)
        cutoff = datetime.now() - timedelta(hours=24)
        self.recent_deployments = [
            d for d in self.recent_deployments
            if d.start_time >= cutoff
        ]
        
        # Check if rollback is needed
        should_rollback, reason = self.should_rollback(deployment)
        
        if should_rollback:
            logger.warning(f"Rollback triggered for deployment {deployment.deployment_id}: {reason.value}")
            
            # Find target deployment for rollback
            target_deployment = await self.find_previous_stable_deployment(deployment.deployment_id)
            
            if target_deployment:
                # Execute rollback
                rollback_event = await self.execute_rollback(
                    deployment.deployment_id,
                    target_deployment,
                    reason
                )
                
                if rollback_event.success:
                    logger.info(f"Automated rollback completed successfully")
                    return rollback_event
                else:
                    logger.error(f"Automated rollback failed: {rollback_event.error_message}")
                    return rollback_event
            else:
                logger.error(f"No stable deployment found for rollback")
                return None
        
        return None
    
    def get_rollback_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get rollback statistics for the specified time period."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_rollbacks = [
            r for r in self.rollback_history
            if r.timestamp >= cutoff
        ]
        
        successful_rollbacks = [r for r in recent_rollbacks if r.success]
        
        rollback_reasons = {}
        for rollback in recent_rollbacks:
            reason = rollback.reason.value
            rollback_reasons[reason] = rollback_reasons.get(reason, 0) + 1
        
        avg_duration = 0
        if successful_rollbacks:
            durations = [r.rollback_duration for r in successful_rollbacks if r.rollback_duration]
            if durations:
                avg_duration = sum(durations) / len(durations)
        
        return {
            "total_rollbacks": len(recent_rollbacks),
            "successful_rollbacks": len(successful_rollbacks),
            "failed_rollbacks": len(recent_rollbacks) - len(successful_rollbacks),
            "success_rate": (len(successful_rollbacks) / len(recent_rollbacks) * 100) if recent_rollbacks else 0,
            "average_rollback_duration": avg_duration,
            "rollback_reasons": rollback_reasons,
            "rollback_enabled": self.rollback_enabled,
            "query_period_hours": hours
        }


# Global rollback manager instance
rollback_manager = None


def get_rollback_manager() -> RollbackManager:
    """Get the global rollback manager instance."""
    global rollback_manager
    
    if rollback_manager is None:
        rollback_manager = RollbackManager()
    
    return rollback_manager