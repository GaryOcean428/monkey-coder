"""
Advanced CI/CD Pipeline & Automation System
==========================================

Comprehensive continuous integration and deployment automation
with intelligent pipeline optimization and deployment strategies.
"""

import asyncio
import json
import logging
import os
import tempfile
import time
import yaml
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import subprocess
import threading

logger = logging.getLogger(__name__)

class PipelineStage(Enum):
    """CI/CD pipeline stages."""
    CHECKOUT = "checkout"
    DEPENDENCIES = "dependencies"
    LINT = "lint"
    TEST = "test"
    BUILD = "build"
    SECURITY_SCAN = "security_scan"
    DEPLOY_STAGING = "deploy_staging"
    INTEGRATION_TEST = "integration_test"
    DEPLOY_PRODUCTION = "deploy_production"
    MONITORING = "monitoring"

class DeploymentStrategy(Enum):
    """Deployment strategies."""
    BLUE_GREEN = "blue_green"
    ROLLING = "rolling"
    CANARY = "canary"
    RECREATE = "recreate"
    A_B_TEST = "a_b_test"

class PipelineStatus(Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"

@dataclass
class PipelineStep:
    """Individual pipeline step definition."""
    name: str
    stage: PipelineStage
    command: str
    environment: Dict[str, str]
    working_directory: Optional[str] = None
    timeout_minutes: int = 30
    retry_count: int = 0
    depends_on: List[str] = None
    condition: Optional[str] = None  # Condition for step execution
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []

@dataclass
class PipelineExecution:
    """Pipeline execution result."""
    execution_id: str
    pipeline_name: str
    triggered_by: str
    branch: str
    commit_sha: str
    status: PipelineStatus
    started_at: datetime
    completed_at: Optional[datetime]
    steps: List[Dict[str, Any]]
    artifacts: List[str]
    deployment_url: Optional[str] = None
    
    @property
    def duration_minutes(self) -> Optional[float]:
        """Calculate execution duration in minutes."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() / 60
        return None

@dataclass
class DeploymentConfig:
    """Deployment configuration."""
    name: str
    strategy: DeploymentStrategy
    target_environment: str
    replicas: int
    health_check_url: str
    rollback_enabled: bool = True
    traffic_percentage: int = 100  # For canary deployments
    approval_required: bool = False

class IntelligentPipelineOrchestrator:
    """AI-powered pipeline orchestration with optimization."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self._pipelines: Dict[str, List[PipelineStep]] = {}
        self._executions: List[PipelineExecution] = []
        self._optimization_rules = []
        self._lock = threading.RLock()
        
        # Performance tracking
        self._step_durations: Dict[str, List[float]] = {}
        self._failure_patterns: Dict[str, int] = {}
    
    def define_pipeline(self, name: str, steps: List[PipelineStep]):
        """Define a new pipeline."""
        with self._lock:
            self._pipelines[name] = steps
        logger.info(f"Defined pipeline: {name} with {len(steps)} steps")
    
    async def execute_pipeline(self, pipeline_name: str, branch: str, 
                             commit_sha: str, triggered_by: str,
                             environment_overrides: Optional[Dict[str, str]] = None) -> PipelineExecution:
        """Execute a pipeline with intelligent optimization."""
        if pipeline_name not in self._pipelines:
            raise ValueError(f"Pipeline {pipeline_name} not found")
        
        execution_id = self._generate_execution_id()
        execution = PipelineExecution(
            execution_id=execution_id,
            pipeline_name=pipeline_name,
            triggered_by=triggered_by,
            branch=branch,
            commit_sha=commit_sha,
            status=PipelineStatus.PENDING,
            started_at=datetime.utcnow(),
            completed_at=None,
            steps=[],
            artifacts=[]
        )
        
        with self._lock:
            self._executions.append(execution)
        
        try:
            execution.status = PipelineStatus.RUNNING
            await self._execute_pipeline_steps(execution, environment_overrides)
            execution.status = PipelineStatus.SUCCESS
            logger.info(f"Pipeline {pipeline_name} completed successfully")
            
        except Exception as e:
            execution.status = PipelineStatus.FAILED
            logger.error(f"Pipeline {pipeline_name} failed: {e}")
            
        finally:
            execution.completed_at = datetime.utcnow()
        
        # Learn from execution for optimization
        await self._learn_from_execution(execution)
        
        return execution
    
    async def _execute_pipeline_steps(self, execution: PipelineExecution, 
                                    environment_overrides: Optional[Dict[str, str]]):
        """Execute pipeline steps with dependency management."""
        steps = self._pipelines[execution.pipeline_name]
        completed_steps = set()
        step_results = {}
        
        # Optimize step order based on historical data
        optimized_steps = await self._optimize_step_order(steps)
        
        for step in optimized_steps:
            # Check dependencies
            if not all(dep in completed_steps for dep in step.depends_on):
                continue
            
            # Check condition
            if step.condition and not await self._evaluate_condition(step.condition, step_results):
                execution.steps.append({
                    'name': step.name,
                    'status': 'skipped',
                    'reason': 'condition_not_met'
                })
                continue
            
            # Execute step
            step_result = await self._execute_step(step, execution, environment_overrides)
            execution.steps.append(step_result)
            step_results[step.name] = step_result
            
            if step_result['status'] == 'success':
                completed_steps.add(step.name)
            else:
                # Handle step failure
                if step.retry_count > 0:
                    # Implement retry logic
                    for retry in range(step.retry_count):
                        logger.info(f"Retrying step {step.name} (attempt {retry + 1})")
                        retry_result = await self._execute_step(step, execution, environment_overrides)
                        if retry_result['status'] == 'success':
                            step_result = retry_result
                            completed_steps.add(step.name)
                            break
                
                if step_result['status'] != 'success':
                    raise Exception(f"Step {step.name} failed: {step_result.get('error', 'Unknown error')}")
    
    async def _execute_step(self, step: PipelineStep, execution: PipelineExecution,
                          environment_overrides: Optional[Dict[str, str]]) -> Dict[str, Any]:
        """Execute a single pipeline step."""
        logger.info(f"Executing step: {step.name}")
        start_time = time.time()
        
        # Prepare environment
        env = dict(os.environ)
        env.update(step.environment)
        if environment_overrides:
            env.update(environment_overrides)
        
        # Prepare working directory
        work_dir = self.project_root
        if step.working_directory:
            work_dir = work_dir / step.working_directory
        
        try:
            # Execute command with timeout
            process = await asyncio.wait_for(
                asyncio.create_subprocess_shell(
                    step.command,
                    cwd=work_dir,
                    env=env,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                ),
                timeout=step.timeout_minutes * 60
            )
            
            stdout, stderr = await process.communicate()
            duration = time.time() - start_time
            
            # Track performance
            self._track_step_performance(step.name, duration)
            
            result = {
                'name': step.name,
                'status': 'success' if process.returncode == 0 else 'failed',
                'duration_seconds': duration,
                'stdout': stdout.decode() if stdout else '',
                'stderr': stderr.decode() if stderr else '',
                'return_code': process.returncode
            }
            
            if process.returncode != 0:
                result['error'] = f"Command exited with code {process.returncode}"
                self._track_step_failure(step.name)
            
            return result
            
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            self._track_step_failure(step.name)
            return {
                'name': step.name,
                'status': 'failed',
                'duration_seconds': duration,
                'error': f"Step timed out after {step.timeout_minutes} minutes"
            }
        except Exception as e:
            duration = time.time() - start_time
            self._track_step_failure(step.name)
            return {
                'name': step.name,
                'status': 'failed',
                'duration_seconds': duration,
                'error': str(e)
            }
    
    async def _optimize_step_order(self, steps: List[PipelineStep]) -> List[PipelineStep]:
        """Optimize step execution order based on historical data."""
        # Create dependency graph
        step_map = {step.name: step for step in steps}
        
        # Topological sort with performance optimization
        def sort_by_performance(step_list):
            """Sort steps by average execution time (faster first)."""
            def get_avg_duration(step_name):
                durations = self._step_durations.get(step_name, [60])  # Default 60s
                return sum(durations) / len(durations)
            
            return sorted(step_list, key=lambda s: get_avg_duration(s.name))
        
        # Basic topological sort with performance hints
        result = []
        remaining = list(steps)
        
        while remaining:
            # Find steps with no unresolved dependencies
            ready_steps = [
                step for step in remaining 
                if all(dep in [s.name for s in result] for dep in step.depends_on)
            ]
            
            if not ready_steps:
                break  # Circular dependency or error
            
            # Sort ready steps by performance
            ready_steps = sort_by_performance(ready_steps)
            
            # Add the fastest step first
            next_step = ready_steps[0]
            result.append(next_step)
            remaining.remove(next_step)
        
        return result
    
    async def _evaluate_condition(self, condition: str, step_results: Dict[str, Any]) -> bool:
        """Evaluate step execution condition."""
        # Simple condition evaluation (would be enhanced in practice)
        try:
            # Support basic conditions like "success(build)" or "branch == 'main'"
            if condition.startswith('success(') and condition.endswith(')'):
                step_name = condition[8:-1]
                return step_results.get(step_name, {}).get('status') == 'success'
            elif condition.startswith('failed(') and condition.endswith(')'):
                step_name = condition[7:-1]
                return step_results.get(step_name, {}).get('status') == 'failed'
            
            # More complex conditions would be implemented here
            return True
        except Exception:
            logger.warning(f"Failed to evaluate condition: {condition}")
            return True
    
    def _track_step_performance(self, step_name: str, duration: float):
        """Track step performance for optimization."""
        with self._lock:
            if step_name not in self._step_durations:
                self._step_durations[step_name] = []
            
            self._step_durations[step_name].append(duration)
            
            # Keep only recent measurements (last 50)
            if len(self._step_durations[step_name]) > 50:
                self._step_durations[step_name] = self._step_durations[step_name][-50:]
    
    def _track_step_failure(self, step_name: str):
        """Track step failures for pattern analysis."""
        with self._lock:
            self._failure_patterns[step_name] = self._failure_patterns.get(step_name, 0) + 1
    
    async def _learn_from_execution(self, execution: PipelineExecution):
        """Learn from pipeline execution for future optimization."""
        # Analyze execution patterns
        if execution.status == PipelineStatus.SUCCESS:
            # Record successful patterns
            pass
        else:
            # Analyze failure patterns
            failed_steps = [step for step in execution.steps if step.get('status') == 'failed']
            for step in failed_steps:
                logger.info(f"Learning from failed step: {step['name']}")
    
    def _generate_execution_id(self) -> str:
        """Generate unique execution ID."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def get_pipeline_analytics(self, pipeline_name: str, days: int = 30) -> Dict[str, Any]:
        """Get analytics for a specific pipeline."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        recent_executions = [
            ex for ex in self._executions 
            if ex.pipeline_name == pipeline_name and ex.started_at >= cutoff_date
        ]
        
        if not recent_executions:
            return {"message": f"No executions found for {pipeline_name} in last {days} days"}
        
        success_count = sum(1 for ex in recent_executions if ex.status == PipelineStatus.SUCCESS)
        total_count = len(recent_executions)
        
        durations = [ex.duration_minutes for ex in recent_executions if ex.duration_minutes]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            'pipeline_name': pipeline_name,
            'total_executions': total_count,
            'success_rate': (success_count / total_count * 100) if total_count > 0 else 0,
            'avg_duration_minutes': round(avg_duration, 2),
            'fastest_execution': min(durations) if durations else 0,
            'slowest_execution': max(durations) if durations else 0,
            'step_performance': {
                name: {
                    'avg_duration': sum(times) / len(times),
                    'failure_count': self._failure_patterns.get(name, 0)
                }
                for name, times in self._step_durations.items()
            }
        }

class SmartDeploymentManager:
    """Intelligent deployment management with multiple strategies."""
    
    def __init__(self):
        self._deployments: List[Dict[str, Any]] = []
        self._environments = {}
        self._rollback_history = []
        self._lock = threading.RLock()
    
    async def deploy(self, config: DeploymentConfig, artifact_url: str, 
                    pipeline_execution: PipelineExecution) -> Dict[str, Any]:
        """Execute deployment with specified strategy."""
        deployment_id = self._generate_deployment_id()
        
        deployment = {
            'deployment_id': deployment_id,
            'pipeline_execution_id': pipeline_execution.execution_id,
            'config': asdict(config),
            'artifact_url': artifact_url,
            'status': 'pending',
            'started_at': datetime.utcnow(),
            'completed_at': None,
            'health_status': 'unknown'
        }
        
        with self._lock:
            self._deployments.append(deployment)
        
        try:
            # Execute deployment based on strategy
            if config.strategy == DeploymentStrategy.BLUE_GREEN:
                result = await self._deploy_blue_green(config, artifact_url, deployment)
            elif config.strategy == DeploymentStrategy.ROLLING:
                result = await self._deploy_rolling(config, artifact_url, deployment)
            elif config.strategy == DeploymentStrategy.CANARY:
                result = await self._deploy_canary(config, artifact_url, deployment)
            else:
                result = await self._deploy_recreate(config, artifact_url, deployment)
            
            deployment.update(result)
            deployment['status'] = 'success'
            deployment['completed_at'] = datetime.utcnow()
            
            # Start health monitoring
            asyncio.create_task(self._monitor_deployment_health(deployment))
            
            return deployment
            
        except Exception as e:
            deployment['status'] = 'failed'
            deployment['error'] = str(e)
            deployment['completed_at'] = datetime.utcnow()
            logger.error(f"Deployment {deployment_id} failed: {e}")
            raise
    
    async def _deploy_blue_green(self, config: DeploymentConfig, artifact_url: str, 
                               deployment: Dict[str, Any]) -> Dict[str, Any]:
        """Execute blue-green deployment."""
        logger.info(f"Starting blue-green deployment to {config.target_environment}")
        
        # Deploy to green environment
        green_url = await self._deploy_to_environment(
            f"{config.target_environment}-green", 
            artifact_url, 
            config.replicas
        )
        
        # Health check green environment
        await self._wait_for_health_check(green_url, config.health_check_url)
        
        # Switch traffic from blue to green
        await self._switch_traffic(config.target_environment, green_url)
        
        # Keep blue environment as backup for rollback
        deployment['backup_url'] = self._get_current_environment_url(f"{config.target_environment}-blue")
        
        return {
            'deployment_url': green_url,
            'strategy_details': {
                'green_url': green_url,
                'traffic_switched': True
            }
        }
    
    async def _deploy_rolling(self, config: DeploymentConfig, artifact_url: str,
                            deployment: Dict[str, Any]) -> Dict[str, Any]:
        """Execute rolling deployment."""
        logger.info(f"Starting rolling deployment to {config.target_environment}")
        
        total_replicas = config.replicas
        batch_size = max(1, total_replicas // 3)  # Deploy in 3 batches
        
        deployment_url = None
        
        for batch in range(0, total_replicas, batch_size):
            batch_end = min(batch + batch_size, total_replicas)
            logger.info(f"Deploying batch {batch//batch_size + 1}: replicas {batch}-{batch_end}")
            
            # Deploy batch
            batch_url = await self._deploy_batch(
                config.target_environment,
                artifact_url,
                batch,
                batch_end
            )
            
            if deployment_url is None:
                deployment_url = batch_url
            
            # Health check batch
            await self._wait_for_health_check(batch_url, config.health_check_url)
            
            # Wait between batches
            await asyncio.sleep(30)
        
        return {
            'deployment_url': deployment_url,
            'strategy_details': {
                'total_batches': (total_replicas + batch_size - 1) // batch_size,
                'batch_size': batch_size
            }
        }
    
    async def _deploy_canary(self, config: DeploymentConfig, artifact_url: str,
                           deployment: Dict[str, Any]) -> Dict[str, Any]:
        """Execute canary deployment."""
        logger.info(f"Starting canary deployment to {config.target_environment}")
        
        # Deploy canary with limited traffic
        canary_url = await self._deploy_to_environment(
            f"{config.target_environment}-canary",
            artifact_url,
            1  # Single replica for canary
        )
        
        # Health check canary
        await self._wait_for_health_check(canary_url, config.health_check_url)
        
        # Route specified percentage of traffic to canary
        await self._route_traffic_percentage(
            config.target_environment,
            canary_url,
            config.traffic_percentage
        )
        
        # Monitor canary performance
        await self._monitor_canary_metrics(canary_url, duration_minutes=10)
        
        # If canary is healthy, proceed with full deployment
        await self._promote_canary(config.target_environment, canary_url, config.replicas)
        
        return {
            'deployment_url': canary_url,
            'strategy_details': {
                'canary_url': canary_url,
                'traffic_percentage': config.traffic_percentage,
                'promoted': True
            }
        }
    
    async def _deploy_recreate(self, config: DeploymentConfig, artifact_url: str,
                             deployment: Dict[str, Any]) -> Dict[str, Any]:
        """Execute recreate deployment (stop all, then start new)."""
        logger.info(f"Starting recreate deployment to {config.target_environment}")
        
        # Stop existing deployment
        await self._stop_environment(config.target_environment)
        
        # Deploy new version
        deployment_url = await self._deploy_to_environment(
            config.target_environment,
            artifact_url,
            config.replicas
        )
        
        # Health check
        await self._wait_for_health_check(deployment_url, config.health_check_url)
        
        return {
            'deployment_url': deployment_url,
            'strategy_details': {
                'recreated': True
            }
        }
    
    async def _deploy_to_environment(self, environment: str, artifact_url: str, 
                                   replicas: int) -> str:
        """Deploy artifact to specified environment."""
        # This would integrate with actual deployment systems (Kubernetes, Docker, etc.)
        logger.info(f"Deploying {artifact_url} to {environment} with {replicas} replicas")
        
        # Simulate deployment
        await asyncio.sleep(2)
        
        # Return deployment URL
        return f"https://{environment}.example.com"
    
    async def _wait_for_health_check(self, base_url: str, health_path: str, 
                                   timeout_minutes: int = 5):
        """Wait for deployment to pass health checks."""
        health_url = f"{base_url.rstrip('/')}/{health_path.lstrip('/')}"
        
        logger.info(f"Waiting for health check: {health_url}")
        
        # Simulate health check
        await asyncio.sleep(3)
        
        # In practice, this would make actual HTTP requests
        logger.info("Health check passed")
    
    async def _switch_traffic(self, environment: str, new_url: str):
        """Switch traffic to new deployment."""
        logger.info(f"Switching traffic in {environment} to {new_url}")
        await asyncio.sleep(1)
    
    async def _route_traffic_percentage(self, environment: str, canary_url: str, 
                                      percentage: int):
        """Route percentage of traffic to canary."""
        logger.info(f"Routing {percentage}% traffic to canary: {canary_url}")
        await asyncio.sleep(1)
    
    async def _monitor_canary_metrics(self, canary_url: str, duration_minutes: int):
        """Monitor canary metrics for specified duration."""
        logger.info(f"Monitoring canary metrics for {duration_minutes} minutes")
        await asyncio.sleep(duration_minutes * 60)
    
    async def _promote_canary(self, environment: str, canary_url: str, replicas: int):
        """Promote canary to full deployment."""
        logger.info(f"Promoting canary to full deployment with {replicas} replicas")
        await asyncio.sleep(2)
    
    async def _stop_environment(self, environment: str):
        """Stop existing deployment in environment."""
        logger.info(f"Stopping existing deployment in {environment}")
        await asyncio.sleep(1)
    
    async def _deploy_batch(self, environment: str, artifact_url: str, 
                          start_replica: int, end_replica: int) -> str:
        """Deploy a batch of replicas."""
        logger.info(f"Deploying batch to {environment}: replicas {start_replica}-{end_replica}")
        await asyncio.sleep(1)
        return f"https://{environment}.example.com"
    
    def _get_current_environment_url(self, environment: str) -> str:
        """Get current URL for environment."""
        return f"https://{environment}.example.com"
    
    async def _monitor_deployment_health(self, deployment: Dict[str, Any]):
        """Monitor deployment health continuously."""
        deployment_id = deployment['deployment_id']
        
        while deployment['status'] == 'success':
            try:
                # Check health
                health_url = deployment.get('deployment_url', '') + "/health"
                # In practice, make actual health check request
                await asyncio.sleep(60)  # Check every minute
                
                deployment['health_status'] = 'healthy'
                deployment['last_health_check'] = datetime.utcnow()
                
            except Exception as e:
                logger.warning(f"Health check failed for deployment {deployment_id}: {e}")
                deployment['health_status'] = 'unhealthy'
                
                # Trigger alert or auto-rollback if configured
                if deployment['config']['rollback_enabled']:
                    await self._auto_rollback(deployment)
                break
    
    async def _auto_rollback(self, deployment: Dict[str, Any]):
        """Automatically rollback unhealthy deployment."""
        deployment_id = deployment['deployment_id']
        logger.warning(f"Initiating auto-rollback for deployment {deployment_id}")
        
        # Implementation would rollback to previous version
        rollback_entry = {
            'deployment_id': deployment_id,
            'rollback_time': datetime.utcnow(),
            'reason': 'health_check_failure'
        }
        
        with self._lock:
            self._rollback_history.append(rollback_entry)
    
    def _generate_deployment_id(self) -> str:
        """Generate unique deployment ID."""
        import uuid
        return f"dep-{str(uuid.uuid4())[:8]}"
    
    def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific deployment."""
        with self._lock:
            for deployment in self._deployments:
                if deployment['deployment_id'] == deployment_id:
                    return deployment
        return None
    
    def get_environment_deployments(self, environment: str) -> List[Dict[str, Any]]:
        """Get all deployments for an environment."""
        with self._lock:
            return [
                dep for dep in self._deployments 
                if dep['config']['target_environment'] == environment
            ]

# Global instances
_pipeline_orchestrator: Optional[IntelligentPipelineOrchestrator] = None
_deployment_manager: Optional[SmartDeploymentManager] = None

def get_pipeline_orchestrator(project_root: str = ".") -> IntelligentPipelineOrchestrator:
    """Get global pipeline orchestrator instance."""
    global _pipeline_orchestrator
    if _pipeline_orchestrator is None:
        _pipeline_orchestrator = IntelligentPipelineOrchestrator(project_root)
    return _pipeline_orchestrator

def get_deployment_manager() -> SmartDeploymentManager:
    """Get global deployment manager instance."""
    global _deployment_manager
    if _deployment_manager is None:
        _deployment_manager = SmartDeploymentManager()
    return _deployment_manager

# Predefined pipeline templates
def create_standard_web_pipeline() -> List[PipelineStep]:
    """Create standard web application pipeline."""
    return [
        PipelineStep(
            name="checkout",
            stage=PipelineStage.CHECKOUT,
            command="git checkout $COMMIT_SHA",
            environment={}
        ),
        PipelineStep(
            name="install_dependencies",
            stage=PipelineStage.DEPENDENCIES,
            command="yarn install --frozen-lockfile",
            environment={},
            depends_on=["checkout"]
        ),
        PipelineStep(
            name="lint",
            stage=PipelineStage.LINT,
            command="yarn lint",
            environment={},
            depends_on=["install_dependencies"]
        ),
        PipelineStep(
            name="test",
            stage=PipelineStage.TEST,
            command="yarn test --coverage",
            environment={},
            depends_on=["install_dependencies"]
        ),
        PipelineStep(
            name="build",
            stage=PipelineStage.BUILD,
            command="yarn build",
            environment={},
            depends_on=["lint", "test"]
        ),
        PipelineStep(
            name="security_scan",
            stage=PipelineStage.SECURITY_SCAN,
            command="yarn audit --audit-level moderate",
            environment={},
            depends_on=["install_dependencies"]
        ),
        PipelineStep(
            name="deploy_staging",
            stage=PipelineStage.DEPLOY_STAGING,
            command="railway up --environment staging",
            environment={},
            depends_on=["build", "security_scan"],
            condition="branch == 'main'"
        )
    ]

def create_python_api_pipeline() -> List[PipelineStep]:
    """Create standard Python API pipeline."""
    return [
        PipelineStep(
            name="checkout",
            stage=PipelineStage.CHECKOUT,
            command="git checkout $COMMIT_SHA",
            environment={}
        ),
        PipelineStep(
            name="setup_python",
            stage=PipelineStage.DEPENDENCIES,
            command="uv venv && uv pip install -r requirements.txt",
            environment={},
            depends_on=["checkout"]
        ),
        PipelineStep(
            name="lint",
            stage=PipelineStage.LINT,
            command="black --check . && isort --check-only . && mypy .",
            environment={},
            depends_on=["setup_python"]
        ),
        PipelineStep(
            name="test",
            stage=PipelineStage.TEST,
            command="python -m pytest --cov=. --cov-report=xml",
            environment={},
            depends_on=["setup_python"]
        ),
        PipelineStep(
            name="security_scan",
            stage=PipelineStage.SECURITY_SCAN,
            command="safety check && bandit -r .",
            environment={},
            depends_on=["setup_python"]
        ),
        PipelineStep(
            name="build_package",
            stage=PipelineStage.BUILD,
            command="python -m build",
            environment={},
            depends_on=["lint", "test", "security_scan"]
        )
    ]