"""
Sandbox Monitoring and Metrics

Provides resource monitoring, performance metrics, and usage tracking for sandbox operations.
"""

import asyncio
import logging
import os
import psutil
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog
from prometheus_client import Counter, Histogram, Gauge, generate_latest

logger = logging.getLogger(__name__)


# Prometheus metrics
SANDBOX_EXECUTIONS_TOTAL = Counter(
    'sandbox_executions_total',
    'Total number of sandbox executions',
    ['sandbox_type', 'status']
)

SANDBOX_EXECUTION_DURATION = Histogram(
    'sandbox_execution_duration_seconds',
    'Sandbox execution duration in seconds',
    ['sandbox_type']
)

SANDBOX_MEMORY_USAGE = Gauge(
    'sandbox_memory_usage_bytes',
    'Current memory usage in bytes'
)

SANDBOX_CPU_USAGE = Gauge(
    'sandbox_cpu_usage_percent',
    'Current CPU usage percentage'
)

SANDBOX_ACTIVE_SESSIONS = Gauge(
    'sandbox_active_sessions',
    'Number of active sandbox sessions',
    ['sandbox_type']
)


class ResourceMonitor:
    """Monitors system resources and tracks usage over time."""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.resource_history = deque(maxlen=history_size)
        self.execution_resources = {}
        self.monitoring = False
        self.monitor_task = None
        
    async def start(self):
        """Start resource monitoring."""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_task = asyncio.create_task(self._monitor_loop())
            logger.info("Resource monitoring started")
    
    async def stop(self):
        """Stop resource monitoring."""
        if self.monitoring:
            self.monitoring = False
            if self.monitor_task:
                self.monitor_task.cancel()
                try:
                    await self.monitor_task
                except asyncio.CancelledError:
                    pass
            logger.info("Resource monitoring stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                # Collect resource metrics
                metrics = await self._collect_metrics()
                self.resource_history.append(metrics)
                
                # Update Prometheus metrics
                SANDBOX_MEMORY_USAGE.set(metrics['memory']['used_bytes'])
                SANDBOX_CPU_USAGE.set(metrics['cpu']['percent'])
                
                # Sleep for monitoring interval
                await asyncio.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                logger.error(f"Resource monitoring error: {str(e)}")
                await asyncio.sleep(10)  # Wait longer on error
    
    async def _collect_metrics(self) -> Dict[str, Any]:
        """Collect current resource metrics."""
        try:
            # System-wide metrics
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/sandbox')
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Process-specific metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            # Network metrics (simplified)
            network = psutil.net_io_counters()
            
            return {
                'timestamp': datetime.utcnow(),
                'memory': {
                    'total_bytes': memory.total,
                    'used_bytes': memory.used,
                    'available_bytes': memory.available,
                    'percent': memory.percent,
                    'process_bytes': process_memory.rss
                },
                'cpu': {
                    'percent': cpu_percent,
                    'process_percent': process_cpu,
                    'count': psutil.cpu_count()
                },
                'disk': {
                    'total_bytes': disk.total,
                    'used_bytes': disk.used,
                    'free_bytes': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {str(e)}")
            return {}
    
    async def get_current_usage(self) -> Dict[str, Any]:
        """Get current resource usage."""
        if self.resource_history:
            return self.resource_history[-1]
        return await self._collect_metrics()
    
    async def get_execution_usage(self, execution_id: str) -> Dict[str, Any]:
        """Get resource usage for a specific execution."""
        return self.execution_resources.get(execution_id, {})
    
    def start_execution_tracking(self, execution_id: str):
        """Start tracking resources for an execution."""
        self.execution_resources[execution_id] = {
            'start_time': datetime.utcnow(),
            'start_metrics': self.resource_history[-1] if self.resource_history else {},
            'peak_memory': 0,
            'peak_cpu': 0
        }
    
    def end_execution_tracking(self, execution_id: str) -> Dict[str, Any]:
        """End tracking and return usage summary."""
        if execution_id not in self.execution_resources:
            return {}
        
        tracking_data = self.execution_resources[execution_id]
        end_metrics = self.resource_history[-1] if self.resource_history else {}
        
        usage_summary = {
            'duration_seconds': (datetime.utcnow() - tracking_data['start_time']).total_seconds(),
            'memory_used_mb': end_metrics.get('memory', {}).get('process_bytes', 0) / 1024 / 1024,
            'peak_memory_mb': tracking_data.get('peak_memory', 0) / 1024 / 1024,
            'peak_cpu_percent': tracking_data.get('peak_cpu', 0),
            'disk_usage_mb': end_metrics.get('disk', {}).get('used_bytes', 0) / 1024 / 1024
        }
        
        # Cleanup
        del self.execution_resources[execution_id]
        
        return usage_summary


class SandboxMetrics:
    """Tracks sandbox execution metrics and performance."""
    
    def __init__(self):
        self.execution_count = defaultdict(int)
        self.execution_times = defaultdict(list)
        self.error_count = defaultdict(int)
        self.active_executions = {}
    
    def start_execution(self, request) -> str:
        """Start tracking an execution."""
        import uuid
        execution_id = str(uuid.uuid4())
        
        self.active_executions[execution_id] = {
            'start_time': time.time(),
            'sandbox_type': request.sandbox_type,
            'action': request.action,
            'metadata': request.metadata
        }
        
        return execution_id
    
    def record_execution(self, execution_id: str, response):
        """Record completed execution metrics."""
        if execution_id not in self.active_executions:
            return
        
        execution_data = self.active_executions[execution_id]
        sandbox_type = execution_data['sandbox_type']
        
        # Record metrics
        SANDBOX_EXECUTIONS_TOTAL.labels(
            sandbox_type=sandbox_type,
            status='success'
        ).inc()
        
        SANDBOX_EXECUTION_DURATION.labels(
            sandbox_type=sandbox_type
        ).observe(response.execution_time)
        
        # Update internal metrics
        self.execution_count[sandbox_type] += 1
        self.execution_times[sandbox_type].append(response.execution_time)
        
        # Keep only last 100 execution times per type
        if len(self.execution_times[sandbox_type]) > 100:
            self.execution_times[sandbox_type] = self.execution_times[sandbox_type][-100:]
        
        # Cleanup
        del self.active_executions[execution_id]
    
    def record_error(self, execution_id: str, error: str):
        """Record execution error."""
        if execution_id not in self.active_executions:
            return
        
        execution_data = self.active_executions[execution_id]
        sandbox_type = execution_data['sandbox_type']
        
        # Record error metrics
        SANDBOX_EXECUTIONS_TOTAL.labels(
            sandbox_type=sandbox_type,
            status='error'
        ).inc()
        
        self.error_count[sandbox_type] += 1
        
        # Cleanup
        del self.active_executions[execution_id]
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        stats = {}
        
        for sandbox_type in self.execution_count:
            execution_times = self.execution_times[sandbox_type]
            
            stats[sandbox_type] = {
                'total_executions': self.execution_count[sandbox_type],
                'total_errors': self.error_count[sandbox_type],
                'success_rate': (
                    (self.execution_count[sandbox_type] - self.error_count[sandbox_type]) /
                    max(self.execution_count[sandbox_type], 1)
                ) * 100,
                'avg_execution_time': sum(execution_times) / len(execution_times) if execution_times else 0,
                'min_execution_time': min(execution_times) if execution_times else 0,
                'max_execution_time': max(execution_times) if execution_times else 0,
                'active_executions': len([
                    e for e in self.active_executions.values()
                    if e['sandbox_type'] == sandbox_type
                ])
            }
        
        return stats


class StructuredLogger:
    """Structured logging for sandbox operations."""
    
    def __init__(self):
        # Configure structured logging
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        self.logger = structlog.get_logger()
    
    def log_execution_start(self, execution_id: str, sandbox_type: str, metadata: Dict[str, Any]):
        """Log execution start."""
        self.logger.info(
            "sandbox_execution_start",
            execution_id=execution_id,
            sandbox_type=sandbox_type,
            metadata=metadata
        )
    
    def log_execution_end(self, execution_id: str, status: str, duration: float, resource_usage: Dict[str, Any]):
        """Log execution completion."""
        self.logger.info(
            "sandbox_execution_end",
            execution_id=execution_id,
            status=status,
            duration_seconds=duration,
            resource_usage=resource_usage
        )
    
    def log_error(self, execution_id: str, error: str, context: Dict[str, Any]):
        """Log execution error."""
        self.logger.error(
            "sandbox_execution_error",
            execution_id=execution_id,
            error=error,
            context=context
        )


async def get_metrics_endpoint():
    """Get Prometheus metrics endpoint."""
    return generate_latest()
