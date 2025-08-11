"""
Performance Metrics Collection System for Quantum Routing

This module provides comprehensive performance tracking, real-time monitoring,
and analytics for the quantum routing system in Phase 2.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics collected."""

    ROUTING_DECISION = "routing_decision"
    EXECUTION_TIME = "execution_time"
    PROVIDER_PERFORMANCE = "provider_performance"
    CACHE_PERFORMANCE = "cache_performance"
    LEARNING_PERFORMANCE = "learning_performance"
    QUALITY_SCORE = "quality_score"
    COST_EFFICIENCY = "cost_efficiency"


@dataclass
class MetricDataPoint:
    """Individual metric data point."""

    timestamp: float
    metric_type: MetricType
    value: float
    metadata: Dict[str, Any]
    tags: Dict[str, str]


@dataclass
class PerformanceAlert:
    """Performance alert for degraded metrics."""

    metric_type: MetricType
    severity: str  # "warning", "critical"
    message: str
    current_value: float
    threshold: float
    timestamp: float


class PerformanceMetricsCollector:
    """
    Collects and analyzes performance metrics for the quantum routing system.

    Features:
    - Real-time metric collection
    - Statistical analysis and trend detection
    - Performance alerting
    - Historical data retention
    - Metric aggregation and reporting
    """

    def __init__(
        self,
        max_datapoints: int = 10000,
        alert_thresholds: Optional[Dict[str, float]] = None,
        enable_real_time_monitoring: bool = True
    ):
        """
        Initialize the performance metrics collector.

        Args:
            max_datapoints: Maximum number of data points to retain
            alert_thresholds: Performance alert thresholds
            enable_real_time_monitoring: Whether to enable real-time monitoring
        """
        self.max_datapoints = max_datapoints
        self.enable_real_time_monitoring = enable_real_time_monitoring

        # Metric storage
        self.metrics: defaultdict[MetricType, deque] = defaultdict(lambda: deque(maxlen=max_datapoints))
        self.aggregated_metrics: Dict[str, Any] = {}
        self.alerts: List[PerformanceAlert] = []

        # Alert thresholds
        self.alert_thresholds = alert_thresholds or {
            "avg_response_time": 5.0,       # 5 seconds
            "cache_hit_rate": 0.7,          # 70%
            "routing_accuracy": 0.8,        # 80%
            "provider_success_rate": 0.9,   # 90%
            "learning_improvement": 0.05    # 5% improvement
        }

        # Real-time monitoring
        self.monitoring_task = None
        self.enable_real_time_monitoring = enable_real_time_monitoring
        # Don't start monitoring task immediately - defer to start_monitoring()

        # Performance counters
        self.counters = defaultdict(int)
        self.running_averages = defaultdict(float)

        logger.info("Initialized Performance Metrics Collector")

    async def start_monitoring(self):
        """Start the real-time monitoring task."""
        if self.enable_real_time_monitoring and self.monitoring_task is None:
            try:
                self.monitoring_task = asyncio.create_task(self._real_time_monitor())
                logger.info("Started real-time monitoring task")
            except RuntimeError as e:
                if "no running event loop" in str(e):
                    logger.warning("Cannot start monitoring task - no event loop running")
                else:
                    raise e

    def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Record a performance metric.

        Args:
            metric_type: Type of metric being recorded
            value: Metric value
            metadata: Additional metadata
            tags: Metric tags for categorization
        """
        datapoint = MetricDataPoint(
            timestamp=time.time(),
            metric_type=metric_type,
            value=value,
            metadata=metadata or {},
            tags=tags or {}
        )

        self.metrics[metric_type].append(datapoint)
        self._update_running_statistics(metric_type, value)

        # Check for alerts
        self._check_alerts(metric_type, value)

        logger.debug(f"Recorded metric: {metric_type.value} = {value}")

    def record_routing_decision(
        self,
        provider: str,
        model: str,
        execution_time: float,
        success: bool,
        confidence_score: float,
        strategy_used: str
    ):
        """Record routing decision metrics."""

        # Record execution time
        self.record_metric(
            MetricType.EXECUTION_TIME,
            execution_time,
            metadata={
                "provider": provider,
                "model": model,
                "strategy": strategy_used
            },
            tags={"provider": provider, "model": model}
        )

        # Record routing decision
        self.record_metric(
            MetricType.ROUTING_DECISION,
            1.0 if success else 0.0,
            metadata={
                "provider": provider,
                "model": model,
                "confidence": confidence_score,
                "strategy": strategy_used
            },
            tags={"provider": provider, "success": str(success)}
        )

        # Record quality score
        self.record_metric(
            MetricType.QUALITY_SCORE,
            confidence_score,
            metadata={
                "provider": provider,
                "model": model,
                "strategy": strategy_used
            },
            tags={"provider": provider}
        )

        # Update counters
        self.counters[f"routing_decisions_{provider}"] += 1
        self.counters["total_routing_decisions"] += 1

        if success:
            self.counters[f"successful_decisions_{provider}"] += 1
            self.counters["total_successful_decisions"] += 1

    def record_provider_performance(
        self,
        provider: str,
        model: str,
        response_time: float,
        success: bool,
        quality_score: float,
        cost_tokens: int
    ):
        """Record provider-specific performance metrics."""

        self.record_metric(
            MetricType.PROVIDER_PERFORMANCE,
            quality_score,
            metadata={
                "provider": provider,
                "model": model,
                "response_time": response_time,
                "success": success,
                "cost_tokens": cost_tokens
            },
            tags={"provider": provider, "model": model}
        )

        # Calculate cost efficiency (quality per token)
        cost_efficiency = quality_score / max(cost_tokens, 1)
        self.record_metric(
            MetricType.COST_EFFICIENCY,
            cost_efficiency,
            metadata={
                "provider": provider,
                "model": model,
                "tokens": cost_tokens
            },
            tags={"provider": provider}
        )

    def record_cache_performance(self, cache_hit: bool, response_time: float):
        """Record cache performance metrics."""

        self.record_metric(
            MetricType.CACHE_PERFORMANCE,
            1.0 if cache_hit else 0.0,
            metadata={"response_time": response_time},
            tags={"hit": str(cache_hit)}
        )

        self.counters["cache_requests"] += 1
        if cache_hit:
            self.counters["cache_hits"] += 1

    def record_learning_performance(
        self,
        training_loss: float,
        accuracy_improvement: float,
        exploration_rate: float,
        training_step: int
    ):
        """Record DQN learning performance metrics."""

        self.record_metric(
            MetricType.LEARNING_PERFORMANCE,
            accuracy_improvement,
            metadata={
                "training_loss": training_loss,
                "exploration_rate": exploration_rate,
                "training_step": training_step
            },
            tags={"training_step": str(training_step)}
        )

    def get_metric_statistics(
        self,
        metric_type: MetricType,
        time_window: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Get statistical analysis of a metric type.

        Args:
            metric_type: Type of metric to analyze
            time_window: Time window in seconds (None for all data)

        Returns:
            Dictionary with statistical measures
        """
        if metric_type not in self.metrics:
            return {}

        # Filter by time window if specified
        current_time = time.time()
        datapoints = self.metrics[metric_type]

        if time_window:
            datapoints = [
                dp for dp in datapoints
                if current_time - dp.timestamp <= time_window
            ]

        if not datapoints:
            return {}

        values = [dp.value for dp in datapoints]

        return {
            "count": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0,
            "min": min(values),
            "max": max(values),
            "p95": statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max(values),
            "p99": statistics.quantiles(values, n=100)[98] if len(values) >= 100 else max(values)
        }

    def get_provider_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive provider performance report."""

        report = {}

        # Get all provider metrics
        provider_metrics = defaultdict(lambda: defaultdict(list))

        for metric_type, datapoints in self.metrics.items():
            for dp in datapoints:
                if "provider" in dp.metadata:
                    provider = dp.metadata["provider"]
                    provider_metrics[provider][metric_type.value].append(dp.value)

        # Calculate statistics for each provider
        for provider, metrics in provider_metrics.items():
            provider_stats = {}

            for metric_name, values in metrics.items():
                if values:
                    provider_stats[metric_name] = {
                        "count": len(values),
                        "mean": statistics.mean(values),
                        "latest": values[-1] if values else 0.0
                    }

            # Calculate derived metrics
            success_rate = self._calculate_success_rate(provider)
            avg_response_time = self._calculate_avg_response_time(provider)
            cost_efficiency = self._calculate_cost_efficiency(provider)

            provider_stats["derived_metrics"] = {
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "cost_efficiency": cost_efficiency
            }

            report[provider] = provider_stats

        return report

    def get_trend_analysis(
        self,
        metric_type: MetricType,
        time_window: float = 3600  # 1 hour
    ) -> Dict[str, Any]:
        """
        Analyze trends in metric values over time.

        Args:
            metric_type: Type of metric to analyze
            time_window: Time window for trend analysis

        Returns:
            Trend analysis results
        """
        if metric_type not in self.metrics:
            return {}

        current_time = time.time()
        datapoints = [
            dp for dp in self.metrics[metric_type]
            if current_time - dp.timestamp <= time_window
        ]

        if len(datapoints) < 2:
            return {"trend": "insufficient_data"}

        # Sort by timestamp
        datapoints.sort(key=lambda dp: dp.timestamp)

        # Calculate trend slope
        timestamps = [dp.timestamp for dp in datapoints]
        values = [dp.value for dp in datapoints]

        # Simple linear regression
        n = len(datapoints)
        sum_x = sum(timestamps)
        sum_y = sum(values)
        sum_xy = sum(t * v for t, v in zip(timestamps, values))
        sum_x2 = sum(t * t for t in timestamps)

        # Check for division by zero (when all timestamps are the same)
        denominator = n * sum_x2 - sum_x * sum_x
        if abs(denominator) < 1e-10:
            # All timestamps are the same or very close, no trend can be calculated
            slope = 0.0
        else:
            slope = (n * sum_xy - sum_x * sum_y) / denominator

        # Determine trend direction
        if abs(slope) < 1e-6:
            trend = "stable"
        elif slope > 0:
            trend = "improving"
        else:
            trend = "degrading"

        # Calculate trend strength
        trend_strength = abs(slope) * time_window

        return {
            "trend": trend,
            "slope": slope,
            "trend_strength": trend_strength,
            "data_points": len(datapoints),
            "time_span": timestamps[-1] - timestamps[0],
            "latest_value": values[-1],
            "earliest_value": values[0]
        }

    def get_performance_alerts(self, severity: Optional[str] = None) -> List[PerformanceAlert]:
        """Get current performance alerts."""

        if severity:
            return [alert for alert in self.alerts if alert.severity == severity]

        return self.alerts.copy()

    def get_real_time_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time data for performance dashboard."""

        current_time = time.time()
        time_window = 300  # 5 minutes

        dashboard_data = {
            "timestamp": current_time,
            "summary": {
                "total_requests": self.counters.get("total_routing_decisions", 0),
                "success_rate": self._calculate_overall_success_rate(),
                "avg_response_time": self._calculate_overall_avg_response_time(),
                "cache_hit_rate": self._calculate_cache_hit_rate(),
                "active_alerts": len([a for a in self.alerts if a.severity == "critical"])
            },
            "recent_trends": {},
            "provider_status": self.get_provider_performance_report(),
            "alerts": [asdict(alert) for alert in self.alerts[-10:]]  # Last 10 alerts
        }

        # Get trends for key metrics
        for metric_type in [MetricType.EXECUTION_TIME, MetricType.QUALITY_SCORE, MetricType.CACHE_PERFORMANCE]:
            trend = self.get_trend_analysis(metric_type, time_window)
            dashboard_data["recent_trends"][metric_type.value] = trend

        return dashboard_data

    async def _real_time_monitor(self):
        """Real-time monitoring task."""

        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds

                # Update aggregated metrics
                self._update_aggregated_metrics()

                # Clean old alerts
                self._clean_old_alerts()

                logger.debug("Real-time monitoring check completed")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in real-time monitoring: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    def _update_running_statistics(self, metric_type: MetricType, value: float):
        """Update running statistics for a metric."""

        key = f"{metric_type.value}_running_avg"
        current_avg = self.running_averages.get(key, 0.0)
        count = self.counters.get(f"{metric_type.value}_count", 0)

        # Update running average
        new_avg = (current_avg * count + value) / (count + 1)
        self.running_averages[key] = new_avg
        self.counters[f"{metric_type.value}_count"] = count + 1

    def _check_alerts(self, metric_type: MetricType, value: float):
        """Check if metric value triggers any alerts."""

        # Define alert conditions
        alert_conditions = {
            MetricType.EXECUTION_TIME: ("avg_response_time", lambda v: v > self.alert_thresholds["avg_response_time"]),
            MetricType.CACHE_PERFORMANCE: ("cache_hit_rate", lambda v: v < self.alert_thresholds["cache_hit_rate"]),
            MetricType.PROVIDER_PERFORMANCE: ("provider_success_rate", lambda v: v < self.alert_thresholds["provider_success_rate"])
        }

        if metric_type in alert_conditions:
            threshold_name, condition = alert_conditions[metric_type]
            threshold = self.alert_thresholds[threshold_name]

            if condition(value):
                alert = PerformanceAlert(
                    metric_type=metric_type,
                    severity="warning" if value > threshold * 0.8 else "critical",
                    message=f"{metric_type.value} threshold exceeded: {value:.3f} > {threshold:.3f}",
                    current_value=value,
                    threshold=threshold,
                    timestamp=time.time()
                )

                self.alerts.append(alert)
                logger.warning(f"Performance alert: {alert.message}")

    def _calculate_success_rate(self, provider: str) -> float:
        """Calculate success rate for a specific provider."""

        total_key = f"routing_decisions_{provider}"
        success_key = f"successful_decisions_{provider}"

        total = self.counters.get(total_key, 0)
        successful = self.counters.get(success_key, 0)

        return successful / max(total, 1)

    def _calculate_avg_response_time(self, provider: str) -> float:
        """Calculate average response time for a provider."""

        # Get recent execution time metrics for this provider
        recent_times = []
        current_time = time.time()

        for dp in self.metrics[MetricType.EXECUTION_TIME]:
            if (current_time - dp.timestamp <= 3600 and  # Last hour
                dp.metadata.get("provider") == provider):
                recent_times.append(dp.value)

        return statistics.mean(recent_times) if recent_times else 0.0

    def _calculate_cost_efficiency(self, provider: str) -> float:
        """Calculate cost efficiency for a provider."""

        # Get recent cost efficiency metrics for this provider
        recent_efficiency = []
        current_time = time.time()

        for dp in self.metrics[MetricType.COST_EFFICIENCY]:
            if (current_time - dp.timestamp <= 3600 and  # Last hour
                dp.metadata.get("provider") == provider):
                recent_efficiency.append(dp.value)

        return statistics.mean(recent_efficiency) if recent_efficiency else 0.0

    def _calculate_overall_success_rate(self) -> float:
        """Calculate overall success rate across all providers."""

        total = self.counters.get("total_routing_decisions", 0)
        successful = self.counters.get("total_successful_decisions", 0)

        return successful / max(total, 1)

    def _calculate_overall_avg_response_time(self) -> float:
        """Calculate overall average response time."""

        key = f"{MetricType.EXECUTION_TIME.value}_running_avg"
        return self.running_averages.get(key, 0.0)

    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""

        total = self.counters.get("cache_requests", 0)
        hits = self.counters.get("cache_hits", 0)

        return hits / max(total, 1)

    def _update_aggregated_metrics(self):
        """Update aggregated metrics for reporting."""

        self.aggregated_metrics = {
            "overall_performance": {
                "success_rate": self._calculate_overall_success_rate(),
                "avg_response_time": self._calculate_overall_avg_response_time(),
                "cache_hit_rate": self._calculate_cache_hit_rate(),
                "total_requests": self.counters.get("total_routing_decisions", 0)
            },
            "provider_performance": self.get_provider_performance_report(),
            "last_updated": time.time()
        }

    def _clean_old_alerts(self):
        """Remove old alerts."""

        current_time = time.time()
        max_age = 3600  # Keep alerts for 1 hour

        self.alerts = [
            alert for alert in self.alerts
            if current_time - alert.timestamp <= max_age
        ]

    def export_metrics(
        self,
        metric_types: Optional[List[MetricType]] = None,
        time_window: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Export metrics data for external analysis.

        Args:
            metric_types: Specific metric types to export (None for all)
            time_window: Time window in seconds (None for all data)

        Returns:
            Exported metrics data
        """
        current_time = time.time()
        export_data = {
            "export_timestamp": current_time,
            "time_window": time_window,
            "metrics": {}
        }

        types_to_export = metric_types or list(self.metrics.keys())

        for metric_type in types_to_export:
            if metric_type in self.metrics:
                datapoints = self.metrics[metric_type]

                # Filter by time window if specified
                if time_window:
                    datapoints = [
                        dp for dp in datapoints
                        if current_time - dp.timestamp <= time_window
                    ]

                # Serialize dataclass with Enum fields to JSON-safe dicts
                export_data["metrics"][metric_type.value] = [
                    {
                        "timestamp": dp.timestamp,
                        "metric_type": dp.metric_type.value,
                        "value": dp.value,
                        "metadata": dp.metadata,
                        "tags": dp.tags,
                    }
                    for dp in datapoints
                ]

        export_data["summary"] = self.aggregated_metrics
        export_data["counters"] = dict(self.counters)

        return export_data

    def __del__(self):
        """Cleanup when collector is destroyed."""

        if self.monitoring_task and not self.monitoring_task.done():
            self.monitoring_task.cancel()
