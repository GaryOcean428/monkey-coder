"""
Advanced Performance Monitoring & Metrics System
==================================================

Enterprise-grade monitoring system with real-time metrics collection,
alerting, and performance optimization recommendations.
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import statistics
from concurrent.futures import ThreadPoolExecutor
import threading
from contextlib import asynccontextmanager

# Set up logging
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    CUSTOM = "custom"

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class MetricData:
    """Container for metric data."""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str]
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AlertRule:
    """Definition of an alert rule."""
    name: str
    metric_name: str
    condition: str  # e.g., "> 100", "< 50", "== 0"
    threshold: float
    severity: AlertSeverity
    cooldown_seconds: int = 300  # 5 minutes default
    callback: Optional[Callable] = None

@dataclass
class PerformanceProfile:
    """Performance profiling data."""
    operation: str
    duration_ms: float
    memory_mb: float
    cpu_percent: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class MetricsCollector:
    """Advanced metrics collection system."""
    
    def __init__(self, max_history: int = 10000, flush_interval: int = 60):
        self._metrics: List[MetricData] = []
        self._alerts: List[AlertRule] = []
        self._alert_history: Dict[str, datetime] = {}
        self._max_history = max_history
        self._flush_interval = flush_interval
        self._running = False
        self._lock = threading.RLock()
        self._background_task: Optional[asyncio.Task] = None
        
        # Performance tracking
        self._performance_profiles: List[PerformanceProfile] = []
        self._operation_stats: Dict[str, Dict[str, Any]] = {}
        
        # Real-time aggregations
        self._counters: Dict[str, float] = {}
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = {}
    
    async def start(self):
        """Start the metrics collection system."""
        if self._running:
            return
            
        self._running = True
        self._background_task = asyncio.create_task(self._background_processor())
        logger.info("Advanced metrics collection system started")
    
    async def stop(self):
        """Stop the metrics collection system."""
        self._running = False
        if self._background_task:
            self._background_task.cancel()
            try:
                await self._background_task
            except asyncio.CancelledError:
                pass
        logger.info("Advanced metrics collection system stopped")
    
    def record_metric(self, name: str, value: float, metric_type: MetricType, 
                     tags: Optional[Dict[str, str]] = None, 
                     metadata: Optional[Dict[str, Any]] = None):
        """Record a metric data point."""
        if tags is None:
            tags = {}
            
        metric = MetricData(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.utcnow(),
            tags=tags,
            metadata=metadata
        )
        
        with self._lock:
            self._metrics.append(metric)
            
            # Update real-time aggregations
            if metric_type == MetricType.COUNTER:
                self._counters[name] = self._counters.get(name, 0) + value
            elif metric_type == MetricType.GAUGE:
                self._gauges[name] = value
            elif metric_type == MetricType.HISTOGRAM:
                if name not in self._histograms:
                    self._histograms[name] = []
                self._histograms[name].append(value)
                
                # Keep histogram size manageable
                if len(self._histograms[name]) > 1000:
                    self._histograms[name] = self._histograms[name][-1000:]
            
            # Trim history if needed
            if len(self._metrics) > self._max_history:
                self._metrics = self._metrics[-self._max_history:]
        
        # Check alerts
        asyncio.create_task(self._check_alerts(metric))
    
    def record_counter(self, name: str, value: float = 1, tags: Optional[Dict[str, str]] = None):
        """Record a counter metric."""
        self.record_metric(name, value, MetricType.COUNTER, tags)
    
    def record_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a gauge metric."""
        self.record_metric(name, value, MetricType.GAUGE, tags)
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a histogram metric."""
        self.record_metric(name, value, MetricType.HISTOGRAM, tags)
    
    @asynccontextmanager
    async def timer(self, operation: str, tags: Optional[Dict[str, str]] = None):
        """Context manager for timing operations."""
        start_time = time.time()
        success = True
        error_message = None
        
        try:
            yield
        except Exception as e:
            success = False
            error_message = str(e)
            raise
        finally:
            duration = (time.time() - start_time) * 1000  # Convert to milliseconds
            self.record_metric(f"{operation}_duration_ms", duration, MetricType.TIMER, tags)
            
            # Record performance profile
            profile = PerformanceProfile(
                operation=operation,
                duration_ms=duration,
                memory_mb=0,  # Could be enhanced with memory tracking
                cpu_percent=0,  # Could be enhanced with CPU tracking
                success=success,
                error_message=error_message
            )
            self._record_performance_profile(profile)
    
    def _record_performance_profile(self, profile: PerformanceProfile):
        """Record a performance profile."""
        with self._lock:
            self._performance_profiles.append(profile)
            
            # Update operation statistics
            op_name = profile.operation
            if op_name not in self._operation_stats:
                self._operation_stats[op_name] = {
                    'count': 0,
                    'success_count': 0,
                    'total_duration': 0,
                    'min_duration': float('inf'),
                    'max_duration': 0,
                    'durations': []
                }
            
            stats = self._operation_stats[op_name]
            stats['count'] += 1
            if profile.success:
                stats['success_count'] += 1
            stats['total_duration'] += profile.duration_ms
            stats['min_duration'] = min(stats['min_duration'], profile.duration_ms)
            stats['max_duration'] = max(stats['max_duration'], profile.duration_ms)
            stats['durations'].append(profile.duration_ms)
            
            # Keep duration history manageable
            if len(stats['durations']) > 1000:
                stats['durations'] = stats['durations'][-1000:]
            
            # Trim profile history
            if len(self._performance_profiles) > 1000:
                self._performance_profiles = self._performance_profiles[-1000:]
    
    def add_alert_rule(self, alert_rule: AlertRule):
        """Add an alert rule."""
        with self._lock:
            self._alerts.append(alert_rule)
        logger.info(f"Added alert rule: {alert_rule.name}")
    
    async def _check_alerts(self, metric: MetricData):
        """Check if any alerts should be triggered."""
        for alert in self._alerts:
            if alert.metric_name != metric.name:
                continue
                
            # Check cooldown
            last_alert = self._alert_history.get(alert.name)
            if last_alert and (datetime.utcnow() - last_alert).total_seconds() < alert.cooldown_seconds:
                continue
            
            # Evaluate condition
            try:
                condition_met = self._evaluate_condition(metric.value, alert.condition, alert.threshold)
                if condition_met:
                    await self._trigger_alert(alert, metric)
            except Exception as e:
                logger.error(f"Error evaluating alert condition for {alert.name}: {e}")
    
    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate an alert condition."""
        if condition == ">":
            return value > threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<":
            return value < threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return value == threshold
        elif condition == "!=":
            return value != threshold
        else:
            raise ValueError(f"Unknown condition: {condition}")
    
    async def _trigger_alert(self, alert: AlertRule, metric: MetricData):
        """Trigger an alert."""
        self._alert_history[alert.name] = datetime.utcnow()
        
        alert_data = {
            'alert_name': alert.name,
            'metric_name': metric.name,
            'metric_value': metric.value,
            'threshold': alert.threshold,
            'condition': alert.condition,
            'severity': alert.severity.value,
            'timestamp': metric.timestamp.isoformat(),
            'tags': metric.tags
        }
        
        logger.warning(f"ALERT TRIGGERED: {alert.name} - {metric.name} {alert.condition} {alert.threshold} (actual: {metric.value})")
        
        # Call custom callback if provided
        if alert.callback:
            try:
                if asyncio.iscoroutinefunction(alert.callback):
                    await alert.callback(alert_data)
                else:
                    alert.callback(alert_data)
            except Exception as e:
                logger.error(f"Error executing alert callback for {alert.name}: {e}")
    
    async def _background_processor(self):
        """Background task for processing metrics."""
        while self._running:
            try:
                await asyncio.sleep(self._flush_interval)
                await self._process_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in background metrics processor: {e}")
    
    async def _process_metrics(self):
        """Process accumulated metrics."""
        # This could be enhanced to:
        # - Send metrics to external systems (Prometheus, DataDog, etc.)
        # - Perform anomaly detection
        # - Generate reports
        # - Clean up old data
        
        with self._lock:
            metric_count = len(self._metrics)
            profile_count = len(self._performance_profiles)
        
        logger.debug(f"Processing {metric_count} metrics and {profile_count} performance profiles")
    
    def get_metrics_summary(self, minutes: int = 60) -> Dict[str, Any]:
        """Get a summary of metrics from the last N minutes."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        with self._lock:
            recent_metrics = [m for m in self._metrics if m.timestamp >= cutoff_time]
            recent_profiles = [p for p in self._performance_profiles if p.timestamp >= cutoff_time]
        
        # Calculate statistics
        summary = {
            'time_window_minutes': minutes,
            'total_metrics': len(recent_metrics),
            'total_operations': len(recent_profiles),
            'counters': dict(self._counters),
            'gauges': dict(self._gauges),
            'operation_stats': {}
        }
        
        # Add histogram statistics
        histogram_stats = {}
        for name, values in self._histograms.items():
            if values:
                histogram_stats[name] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'p95': self._percentile(values, 95),
                    'p99': self._percentile(values, 99)
                }
        summary['histograms'] = histogram_stats
        
        # Add operation statistics
        for op_name, stats in self._operation_stats.items():
            if stats['durations']:
                summary['operation_stats'][op_name] = {
                    'total_count': stats['count'],
                    'success_count': stats['success_count'],
                    'success_rate': stats['success_count'] / stats['count'] if stats['count'] > 0 else 0,
                    'avg_duration_ms': stats['total_duration'] / stats['count'] if stats['count'] > 0 else 0,
                    'min_duration_ms': stats['min_duration'] if stats['min_duration'] != float('inf') else 0,
                    'max_duration_ms': stats['max_duration'],
                    'p50_duration_ms': self._percentile(stats['durations'], 50),
                    'p95_duration_ms': self._percentile(stats['durations'], 95),
                    'p99_duration_ms': self._percentile(stats['durations'], 99)
                }
        
        return summary
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def get_health_score(self) -> Dict[str, Any]:
        """Calculate a health score based on recent metrics."""
        summary = self.get_metrics_summary(minutes=10)
        
        health_score = 100.0  # Start with perfect score
        issues = []
        
        # Check operation success rates
        for op_name, stats in summary['operation_stats'].items():
            success_rate = stats['success_rate']
            if success_rate < 0.95:  # Less than 95% success rate
                penalty = (0.95 - success_rate) * 50  # Up to 25 point penalty
                health_score -= penalty
                issues.append(f"Low success rate for {op_name}: {success_rate:.1%}")
            
            # Check for high latency
            p95_duration = stats['p95_duration_ms']
            if p95_duration > 5000:  # 5 seconds
                penalty = min((p95_duration - 5000) / 1000 * 5, 20)  # Up to 20 point penalty
                health_score -= penalty
                issues.append(f"High P95 latency for {op_name}: {p95_duration:.0f}ms")
        
        # Ensure score doesn't go below 0
        health_score = max(0, health_score)
        
        # Determine health status
        if health_score >= 90:
            status = "excellent"
        elif health_score >= 75:
            status = "good"
        elif health_score >= 50:
            status = "warning"
        else:
            status = "critical"
        
        return {
            'health_score': round(health_score, 1),
            'status': status,
            'issues': issues,
            'summary': summary
        }

# Global metrics collector instance
_global_collector: Optional[MetricsCollector] = None

def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _global_collector
    if _global_collector is None:
        _global_collector = MetricsCollector()
    return _global_collector

async def setup_default_alerts():
    """Setup default alert rules for common scenarios."""
    collector = get_metrics_collector()
    
    # High error rate alert
    collector.add_alert_rule(AlertRule(
        name="high_error_rate",
        metric_name="error_count",
        condition=">",
        threshold=10,
        severity=AlertSeverity.WARNING,
        cooldown_seconds=300
    ))
    
    # High response time alert
    collector.add_alert_rule(AlertRule(
        name="high_response_time",
        metric_name="response_time_ms",
        condition=">",
        threshold=5000,
        severity=AlertSeverity.WARNING,
        cooldown_seconds=180
    ))
    
    # Memory usage alert
    collector.add_alert_rule(AlertRule(
        name="high_memory_usage",
        metric_name="memory_usage_mb",
        condition=">",
        threshold=1024,
        severity=AlertSeverity.ERROR,
        cooldown_seconds=600
    ))

# Convenience functions
async def record_operation_metrics(operation: str, duration_ms: float, success: bool, tags: Optional[Dict[str, str]] = None):
    """Convenience function to record operation metrics."""
    collector = get_metrics_collector()
    
    if tags is None:
        tags = {}
    
    tags['operation'] = operation
    tags['success'] = str(success)
    
    collector.record_histogram(f"{operation}_duration_ms", duration_ms, tags)
    collector.record_counter(f"{operation}_total", 1, tags)
    
    if not success:
        collector.record_counter(f"{operation}_errors", 1, tags)