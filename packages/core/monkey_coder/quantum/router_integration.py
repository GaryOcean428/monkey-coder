"""
Quantum Router Integration

This module integrates the Phase 2 Quantum Routing Manager with the existing
routing infrastructure, providing a seamless upgrade path and backward compatibility.
"""

import logging
import asyncio
from typing import Any, Dict, Optional

from ..models import ExecuteRequest, PersonaType
from ..core.routing import AdvancedRouter, RoutingDecision
from .quantum_routing_manager import (
    QuantumRoutingManager,
    QuantumRoutingResult,
    RoutingStrategy
)
from .performance_metrics import PerformanceMetricsCollector, MetricType

logger = logging.getLogger(__name__)


class QuantumRouterIntegration:
    """
    Integration layer between the quantum routing system and existing infrastructure.

    Provides:
    - Seamless fallback to classic routing
    - Performance comparison between routing methods
    - Gradual migration capabilities
    - Comprehensive analytics
    """

    def __init__(
        self,
        enable_quantum: bool = True,
        quantum_timeout: float = 30.0,
        fallback_on_failure: bool = True,
        performance_comparison: bool = True
    ):
        """
        Initialize the quantum router integration.

        Args:
            enable_quantum: Whether to enable quantum routing
            quantum_timeout: Timeout for quantum routing operations
            fallback_on_failure: Whether to fallback to classic routing on quantum failure
            performance_comparison: Whether to compare quantum vs classic performance
        """
        self.enable_quantum = enable_quantum
        self.quantum_timeout = quantum_timeout
        self.fallback_on_failure = fallback_on_failure
        self.performance_comparison = performance_comparison

        # Initialize components
        self.classic_router = AdvancedRouter()

        if self.enable_quantum:
            self.quantum_manager = QuantumRoutingManager(
                max_threads=6,
                default_timeout=quantum_timeout
            )
        else:
            self.quantum_manager = None

        # Performance tracking
        self.metrics_collector = PerformanceMetricsCollector(enable_real_time_monitoring=False)

        # Routing statistics
        self.routing_stats = {
            "quantum_requests": 0,
            "classic_requests": 0,
            "quantum_failures": 0,
            "fallback_usage": 0,
            "performance_improvements": []
        }

        logger.info("Initialized Quantum Router Integration")

    async def start_monitoring(self):
        """Start the performance monitoring task."""
        await self.metrics_collector.start_monitoring()
        logger.info("Started performance monitoring")

    async def route_request(
        self,
        request: ExecuteRequest,
        force_method: Optional[str] = None  # "quantum", "classic", or None for auto
    ) -> RoutingDecision:
        """
        Route request using integrated quantum/classic routing.

        Args:
            request: The execution request to route
            force_method: Force specific routing method for testing

        Returns:
            Routing decision from quantum or classic router
        """
        routing_method = self._determine_routing_method(request, force_method)

        if routing_method == "quantum" and self.quantum_manager:
            return await self._route_with_quantum(request)
        else:
            return await self._route_with_classic(request)

    async def _route_with_quantum(self, request: ExecuteRequest) -> RoutingDecision:
        """Route request using quantum routing manager."""

        start_time = asyncio.get_event_loop().time()

        try:
            # Execute quantum routing
            if self.quantum_manager is None:
                raise RuntimeError("Quantum manager is not initialized")

            quantum_result = await asyncio.wait_for(
                self.quantum_manager.route_with_quantum_strategies(
                    request=request,
                    strategies=[
                        RoutingStrategy.TASK_OPTIMIZED,
                        RoutingStrategy.PERFORMANCE,
                        RoutingStrategy.BALANCED
                    ]
                ),
                timeout=self.quantum_timeout
            )

            execution_time = asyncio.get_event_loop().time() - start_time

            # Record quantum routing metrics
            self.metrics_collector.record_routing_decision(
                provider=quantum_result.provider.value,
                model=quantum_result.model,
                execution_time=execution_time,
                success=True,
                confidence_score=quantum_result.confidence,
                strategy_used=quantum_result.strategy_used
            )

            self.routing_stats["quantum_requests"] += 1

            # Performance comparison if enabled
            if self.performance_comparison:
                await self._compare_routing_performance(request, quantum_result, execution_time)

            # Create a RoutingDecision from the quantum result
            routing_decision = RoutingDecision(
                provider=quantum_result.provider,
                model=quantum_result.model,
                persona=PersonaType.DEVELOPER,  # Default persona
                complexity_score=0.5,  # Default complexity
                context_score=0.5,  # Default context score
                capability_score=quantum_result.confidence,
                confidence=quantum_result.confidence,
                reasoning=f"Quantum routing using {quantum_result.strategy_used} strategy",
                metadata={
                    "quantum_strategy": quantum_result.strategy_used,
                    "execution_time": execution_time,
                    "thread_results": [
                        {
                            "strategy": tr.strategy.value,
                            "provider": tr.provider.value,
                            "model": tr.model,
                            "confidence": tr.confidence,
                            "execution_time": tr.execution_time,
                            "success": tr.success
                        }
                        for tr in quantum_result.thread_results
                    ]
                }
            )

            logger.info(f"Quantum routing successful: {quantum_result.provider.value}/{quantum_result.model}")
            return routing_decision

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time

            logger.warning(f"Quantum routing failed: {e}")
            self.routing_stats["quantum_failures"] += 1

            # Record failure metrics
            self.metrics_collector.record_metric(
                MetricType.ROUTING_DECISION,
                0.0,  # Failed routing
                metadata={
                    "method": "quantum",
                    "error": str(e),
                    "execution_time": execution_time
                }
            )

            # Fallback to classic routing if enabled
            if self.fallback_on_failure:
                logger.info("Falling back to classic routing")
                self.routing_stats["fallback_usage"] += 1
                return await self._route_with_classic(request)
            else:
                raise

    async def _route_with_classic(self, request: ExecuteRequest) -> RoutingDecision:
        """Route request using classic advanced router."""

        start_time = asyncio.get_event_loop().time()

        try:
            # Execute classic routing (run in thread pool since it's synchronous)
            loop = asyncio.get_event_loop()
            decision = await loop.run_in_executor(
                None,
                self.classic_router.route_request,
                request
            )

            execution_time = asyncio.get_event_loop().time() - start_time

            # Record classic routing metrics
            self.metrics_collector.record_routing_decision(
                provider=decision.provider.value,
                model=decision.model,
                execution_time=execution_time,
                success=True,
                confidence_score=decision.confidence,
                strategy_used="classic"
            )

            self.routing_stats["classic_requests"] += 1

            logger.debug(f"Classic routing successful: {decision.provider.value}/{decision.model}")
            return decision

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time

            logger.error(f"Classic routing failed: {e}")

            # Record failure metrics
            self.metrics_collector.record_metric(
                MetricType.ROUTING_DECISION,
                0.0,  # Failed routing
                metadata={
                    "method": "classic",
                    "error": str(e),
                    "execution_time": execution_time
                }
            )

            raise

    async def _compare_routing_performance(
        self,
        request: ExecuteRequest,
        quantum_result: QuantumRoutingResult,
        quantum_time: float
    ):
        """Compare quantum vs classic routing performance."""

        try:
            # Get classic routing decision for comparison
            classic_start = asyncio.get_event_loop().time()
            classic_decision = await self._route_with_classic(request)
            classic_time = asyncio.get_event_loop().time() - classic_start

            # Calculate performance improvement
            time_improvement = (classic_time - quantum_time) / classic_time if classic_time > 0 else 0
            confidence_improvement = quantum_result.confidence - classic_decision.confidence

            # Store performance comparison
            comparison = {
                "quantum_time": quantum_time,
                "classic_time": classic_time,
                "time_improvement": time_improvement,
                "confidence_improvement": confidence_improvement,
                "quantum_provider": quantum_result.provider.value,
                "classic_provider": classic_decision.provider.value,
                "quantum_model": quantum_result.model,
                "classic_model": classic_decision.model
            }

            self.routing_stats["performance_improvements"].append(comparison)

            # Keep only last 100 comparisons
            if len(self.routing_stats["performance_improvements"]) > 100:
                self.routing_stats["performance_improvements"] = self.routing_stats["performance_improvements"][-100:]

            logger.debug(f"Performance comparison: quantum={quantum_time:.3f}s, classic={classic_time:.3f}s")

        except Exception as e:
            logger.warning(f"Performance comparison failed: {e}")

    def _determine_routing_method(
        self,
        request: ExecuteRequest,
        force_method: Optional[str] = None
    ) -> str:
        """Determine which routing method to use."""

        if force_method:
            return force_method

        if not self.enable_quantum or not self.quantum_manager:
            return "classic"

        # Use quantum routing by default when enabled
        return "quantum"

    async def get_routing_analytics(self) -> Dict[str, Any]:
        """Get comprehensive routing analytics."""

        # Basic routing statistics
        total_requests = self.routing_stats["quantum_requests"] + self.routing_stats["classic_requests"]
        quantum_success_rate = 1.0 - (self.routing_stats["quantum_failures"] / max(self.routing_stats["quantum_requests"], 1))

        analytics = {
            "routing_statistics": {
                "total_requests": total_requests,
                "quantum_requests": self.routing_stats["quantum_requests"],
                "classic_requests": self.routing_stats["classic_requests"],
                "quantum_success_rate": quantum_success_rate,
                "fallback_usage": self.routing_stats["fallback_usage"],
                "quantum_enabled": self.enable_quantum
            },
            "performance_metrics": self.metrics_collector.get_real_time_dashboard_data(),
            "configuration": {
                "quantum_timeout": self.quantum_timeout,
                "fallback_on_failure": self.fallback_on_failure,
                "performance_comparison": self.performance_comparison
            }
        }

        # Add quantum manager analytics if available
        if self.quantum_manager:
            analytics["quantum_analytics"] = await self.quantum_manager.get_routing_analytics()

        # Add performance improvements summary
        if self.routing_stats["performance_improvements"]:
            improvements = self.routing_stats["performance_improvements"]
            avg_time_improvement = sum(c["time_improvement"] for c in improvements) / len(improvements)
            avg_confidence_improvement = sum(c["confidence_improvement"] for c in improvements) / len(improvements)

            analytics["performance_comparison"] = {
                "average_time_improvement": avg_time_improvement,
                "average_confidence_improvement": avg_confidence_improvement,
                "comparison_count": len(improvements),
                "latest_comparisons": improvements[-10:]  # Last 10 comparisons
            }

        return analytics

    async def optimize_routing(self):
        """Optimize routing parameters based on collected metrics."""

        if self.quantum_manager:
            await self.quantum_manager.optimize_routing_parameters()
            logger.info("Optimized quantum routing parameters")

    async def export_performance_data(self) -> Dict[str, Any]:
        """Export comprehensive performance data for analysis."""

        export_data = {
            "routing_analytics": await self.get_routing_analytics(),
            "metrics_export": self.metrics_collector.export_metrics(),
            "routing_statistics": self.routing_stats.copy()
        }

        return export_data

    async def save_models(self, filepath_prefix: str):
        """Save trained routing models."""

        if self.quantum_manager:
            await self.quantum_manager.save_routing_model(f"{filepath_prefix}_quantum")
            logger.info(f"Saved quantum routing model to {filepath_prefix}_quantum")

    async def load_models(self, filepath_prefix: str) -> bool:
        """Load trained routing models."""

        if self.quantum_manager:
            success = await self.quantum_manager.load_routing_model(f"{filepath_prefix}_quantum")
            if success:
                logger.info(f"Loaded quantum routing model from {filepath_prefix}_quantum")
            return success

        return False

    def enable_quantum_routing(self):
        """Enable quantum routing if currently disabled."""

        if not self.quantum_manager:
            self.quantum_manager = QuantumRoutingManager(
                max_threads=6,
                default_timeout=self.quantum_timeout
            )

        self.enable_quantum = True
        logger.info("Enabled quantum routing")

    def disable_quantum_routing(self):
        """Disable quantum routing and use only classic routing."""

        self.enable_quantum = False
        logger.info("Disabled quantum routing - using classic routing only")

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of routing components."""

        status = {
            "quantum_enabled": self.enable_quantum,
            "quantum_manager_healthy": self.quantum_manager is not None,
            "classic_router_healthy": self.classic_router is not None,
            "metrics_collector_healthy": self.metrics_collector is not None,
            "recent_errors": []
        }

        # Check for recent failures
        if self.routing_stats["quantum_failures"] > 0:
            failure_rate = self.routing_stats["quantum_failures"] / max(self.routing_stats["quantum_requests"], 1)
            if failure_rate > 0.1:  # More than 10% failure rate
                status["recent_errors"].append(f"High quantum routing failure rate: {failure_rate:.2%}")

        # Check quantum manager health if available
        if self.quantum_manager:
            quantum_analytics = asyncio.run(self.quantum_manager.get_routing_analytics())
            if quantum_analytics.get("cache_status", {}).get("enabled") and not quantum_analytics.get("cache_status", {}).get("connected"):
                status["recent_errors"].append("Redis cache connection failed")

        status["overall_health"] = "healthy" if not status["recent_errors"] else "degraded"

        return status
