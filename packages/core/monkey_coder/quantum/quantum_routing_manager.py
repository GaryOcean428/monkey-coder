"""Quantum Routing Manager for parallel strategy execution.

This module implements the Quantum Routing Manager that executes multiple
routing strategies in parallel and uses collapse mechanisms to select
the best result.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from monkey_coder.models import ExecuteRequest, ProviderType
from monkey_coder.quantum.dqn_agent import DQNRoutingAgent, RoutingState
from monkey_coder.quantum.state_encoder import StateEncoder

logger = logging.getLogger(__name__)


class CollapseStrategy(Enum):
    """Strategies for collapsing quantum routing results."""

    BEST_SCORE = "best_score"  # Select highest-scoring result
    WEIGHTED = "weighted"  # Weighted combination based on confidence
    CONSENSUS = "consensus"  # Majority vote
    FIRST_SUCCESS = "first_success"  # First successful result
    COMBINED = "combined"  # Aggregate multiple results


class RoutingStrategy(Enum):
    """Available routing strategies."""

    TASK_OPTIMIZED = "task_optimized"
    COST_EFFICIENT = "cost_efficient"
    PERFORMANCE = "performance"
    BALANCED = "balanced"
    DQN_BASED = "dqn_based"
    RANDOM = "random"


@dataclass
class ThreadResult:
    """Result from a quantum routing thread."""

    strategy: RoutingStrategy
    provider: ProviderType
    model: str
    confidence: float
    execution_time: float
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class QuantumRoutingResult:
    """Final result from quantum routing."""

    provider: ProviderType
    model: str
    confidence: float
    strategy_used: str
    execution_time: float
    thread_results: List[ThreadResult]
    collapse_reasoning: str


class QuantumThread:
    """Individual quantum routing thread."""

    def __init__(
        self,
        thread_id: int,
        strategy: RoutingStrategy,
        routing_func: Callable,
        timeout: float = 0.15,
    ):
        """Initialize quantum thread.

        Args:
            thread_id: Unique thread identifier
            strategy: Routing strategy to use
            routing_func: Function to execute routing
            timeout: Maximum execution time in seconds
        """
        self.thread_id = thread_id
        self.strategy = strategy
        self.routing_func = routing_func
        self.timeout = timeout
        self.status = "PENDING"
        self.result: Optional[ThreadResult] = None

    async def execute(
        self, state: RoutingState, request: ExecuteRequest
    ) -> ThreadResult:
        """Execute routing strategy.

        Args:
            state: Current routing state
            request: Execution request

        Returns:
            Thread execution result
        """
        self.status = "RUNNING"
        start_time = time.time()

        try:
            # Execute routing with timeout
            result = await asyncio.wait_for(
                self.routing_func(state, request, self.strategy),
                timeout=self.timeout,
            )

            execution_time = time.time() - start_time
            self.status = "SUCCESS"

            self.result = ThreadResult(
                strategy=self.strategy,
                provider=result["provider"],
                model=result["model"],
                confidence=result.get("confidence", 0.5),
                execution_time=execution_time,
                success=True,
                metadata=result.get("metadata", {}),
            )

        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            self.status = "TIMEOUT"
            self.result = ThreadResult(
                strategy=self.strategy,
                provider=ProviderType.OPENAI,
                model="gpt-4.1-mini",
                confidence=0.0,
                execution_time=execution_time,
                success=False,
                error="Strategy execution timeout",
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.status = "FAILED"
            self.result = ThreadResult(
                strategy=self.strategy,
                provider=ProviderType.OPENAI,
                model="gpt-4.1-mini",
                confidence=0.0,
                execution_time=execution_time,
                success=False,
                error=str(e),
            )

        return self.result


class QuantumRoutingManager:
    """Manager for quantum routing with parallel execution."""

    def __init__(
        self,
        dqn_agent: Optional[DQNRoutingAgent] = None,
        state_encoder: Optional[StateEncoder] = None,
        max_threads: int = 5,
        default_timeout: float = 0.15,
    ):
        """Initialize quantum routing manager.

        Args:
            dqn_agent: DQN agent for intelligent routing
            state_encoder: State encoder for DQN
            max_threads: Maximum parallel threads
            default_timeout: Default timeout for threads
        """
        self.dqn_agent = dqn_agent
        self.state_encoder = state_encoder or StateEncoder()
        self.max_threads = max_threads
        self.default_timeout = default_timeout

        # Performance tracking
        self.execution_history: List[QuantumRoutingResult] = []
        self.strategy_performance: Dict[str, List[float]] = {}

    async def route_with_quantum_strategies(
        self,
        request: ExecuteRequest,
        strategies: Optional[List[RoutingStrategy]] = None,
        collapse_strategy: CollapseStrategy = CollapseStrategy.BEST_SCORE,
        timeout: Optional[float] = None,
    ) -> QuantumRoutingResult:
        """Execute quantum routing with parallel strategies.

        Args:
            request: Execution request
            strategies: List of strategies to execute
            collapse_strategy: Strategy for collapsing results
            timeout: Override timeout for threads

        Returns:
            Quantum routing result
        """
        start_time = time.time()

        # Default strategies if none provided
        if not strategies:
            strategies = [
                RoutingStrategy.TASK_OPTIMIZED,
                RoutingStrategy.PERFORMANCE,
                RoutingStrategy.BALANCED,
            ]
            if self.dqn_agent:
                strategies.append(RoutingStrategy.DQN_BASED)

        # Create routing state
        state = self._create_routing_state(request)

        # Create quantum threads
        threads = []
        for i, strategy in enumerate(strategies[:self.max_threads]):
            thread = QuantumThread(
                thread_id=i,
                strategy=strategy,
                routing_func=self._execute_strategy,
                timeout=timeout or self.default_timeout,
            )
            threads.append(thread)

        # Execute threads in parallel
        tasks = [thread.execute(state, request) for thread in threads]
        thread_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter successful results
        valid_results = [
            result for result in thread_results
            if isinstance(result, ThreadResult) and result.success
        ]

        # Collapse results
        final_result = self._collapse_results(
            valid_results, collapse_strategy, time.time() - start_time
        )

        # Store for learning
        self._update_performance_history(final_result)

        return final_result

    def _create_routing_state(self, request: ExecuteRequest) -> RoutingState:
        """Create routing state from request.

        Args:
            request: Execution request

        Returns:
            Routing state
        """
        # Analyze task complexity
        task_complexity = self._analyze_task_complexity(request)

        # Determine context type
        context_type = self._determine_context_type(request)

        # Get provider availability
        provider_availability = self._get_provider_availability()

        # Get historical performance
        historical_performance = self._get_historical_performance()

        return RoutingState(
            task_complexity=task_complexity,
            context_type=context_type,
            provider_availability=provider_availability,
            historical_performance=historical_performance,
            resource_constraints={
                "cost_weight": 0.3,
                "time_weight": 0.3,
                "quality_weight": 0.4,
            },
            user_preferences={
                "preference_strength": 0.8,
            },
        )

    async def _execute_strategy(
        self, state: RoutingState, request: ExecuteRequest, strategy: RoutingStrategy
    ) -> Dict[str, Any]:
        """Execute a specific routing strategy.

        Args:
            state: Current routing state
            request: Execution request
            strategy: Strategy to execute

        Returns:
            Routing result
        """
        if strategy == RoutingStrategy.TASK_OPTIMIZED:
            return self._task_optimized_routing(state, request)
        elif strategy == RoutingStrategy.COST_EFFICIENT:
            return self._cost_efficient_routing(state, request)
        elif strategy == RoutingStrategy.PERFORMANCE:
            return self._performance_routing(state, request)
        elif strategy == RoutingStrategy.BALANCED:
            return self._balanced_routing(state, request)
        elif strategy == RoutingStrategy.DQN_BASED:
            return self._dqn_based_routing(state, request)
        elif strategy == RoutingStrategy.RANDOM:
            return self._random_routing(state, request)
        else:
            return self._balanced_routing(state, request)

    def _task_optimized_routing(
        self, state: RoutingState, request: ExecuteRequest
    ) -> Dict[str, Any]:
        """Route based on task optimization."""
        if state.task_complexity > 0.8:
            return {
                "provider": ProviderType.OPENAI,
                "model": "gpt-4",
                "confidence": 0.9,
                "metadata": {"reason": "high_complexity_task"},
            }
        elif state.context_type in ["python", "javascript"]:
            return {
                "provider": ProviderType.ANTHROPIC,
                "model": "claude-3-sonnet-20240229",
                "confidence": 0.85,
                "metadata": {"reason": "code_specialized"},
            }
        else:
            return {
                "provider": ProviderType.OPENAI,
                "model": "gpt-4o-mini",
                "confidence": 0.7,
                "metadata": {"reason": "general_task"},
            }

    def _cost_efficient_routing(
        self, state: RoutingState, request: ExecuteRequest
    ) -> Dict[str, Any]:
        """Route based on cost efficiency."""
        estimated_tokens = self._estimate_tokens(request)
        if estimated_tokens and estimated_tokens < 1000:
            return {
                "provider": ProviderType.OPENAI,
                "model": "gpt-4o-mini",
                "confidence": 0.8,
                "metadata": {"reason": "low_token_count"},
            }
        else:
            return {
                "provider": ProviderType.ANTHROPIC,
                "model": "claude-3-haiku-20240307",
                "confidence": 0.75,
                "metadata": {"reason": "cost_optimized"},
            }

    def _performance_routing(
        self, state: RoutingState, request: ExecuteRequest
    ) -> Dict[str, Any]:
        """Route based on performance."""
        return {
            "provider": ProviderType.OPENAI,
            "model": "gpt-4",
            "confidence": 0.95,
            "metadata": {"reason": "maximum_performance"},
        }

    def _balanced_routing(
        self, state: RoutingState, request: ExecuteRequest
    ) -> Dict[str, Any]:
        """Route based on balanced criteria."""
        if state.task_complexity > 0.6:
            return {
                "provider": ProviderType.OPENAI,
                "model": "gpt-4o",
                "confidence": 0.85,
                "metadata": {"reason": "balanced_high_complexity"},
            }
        else:
            return {
                "provider": ProviderType.ANTHROPIC,
                "model": "claude-3-sonnet-20240229",
                "confidence": 0.8,
                "metadata": {"reason": "balanced_standard"},
            }

    def _dqn_based_routing(
        self, state: RoutingState, request: ExecuteRequest
    ) -> Dict[str, Any]:
        """Route using DQN agent."""
        if not self.dqn_agent:
            return self._balanced_routing(state, request)

        # Get action from DQN (pass RoutingState directly)
        action = self.dqn_agent.act(state)

        # Extract provider and model from RoutingAction
        provider = action.provider
        model = action.model

        return {
            "provider": provider,
            "model": model,
            "confidence": 0.9,
            "metadata": {"reason": "dqn_decision", "strategy": action.strategy},
        }

    def _random_routing(
        self, state: RoutingState, request: ExecuteRequest
    ) -> Dict[str, Any]:
        """Random routing for exploration."""
        import random

        providers = [ProviderType.OPENAI, ProviderType.ANTHROPIC]
        models = {
            ProviderType.OPENAI: ["gpt-4", "gpt-4o", "gpt-4o-mini"],
            ProviderType.ANTHROPIC: [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
            ],
        }

        provider = random.choice(providers)
        model = random.choice(models[provider])

        return {
            "provider": provider,
            "model": model,
            "confidence": 0.5,
            "metadata": {"reason": "random_exploration"},
        }

    def _collapse_results(
        self,
        results: List[ThreadResult],
        strategy: CollapseStrategy,
        total_time: float,
    ) -> QuantumRoutingResult:
        """Collapse multiple results into final decision.

        Args:
            results: List of thread results
            strategy: Collapse strategy
            total_time: Total execution time

        Returns:
            Final quantum routing result
        """
        if not results:
            # Fallback result
            return QuantumRoutingResult(
                provider=ProviderType.OPENAI,
                model="gpt-4o-mini",
                confidence=0.1,
                strategy_used="fallback",
                execution_time=total_time,
                thread_results=[],
                collapse_reasoning="No successful results, using fallback",
            )

        if strategy == CollapseStrategy.BEST_SCORE:
            best_result = max(results, key=lambda r: r.confidence)
            return QuantumRoutingResult(
                provider=best_result.provider,
                model=best_result.model,
                confidence=best_result.confidence,
                strategy_used=best_result.strategy.value,
                execution_time=total_time,
                thread_results=results,
                collapse_reasoning=f"Selected best confidence: {best_result.confidence:.3f}",
            )

        elif strategy == CollapseStrategy.FIRST_SUCCESS:
            first_result = results[0]
            return QuantumRoutingResult(
                provider=first_result.provider,
                model=first_result.model,
                confidence=first_result.confidence,
                strategy_used=first_result.strategy.value,
                execution_time=total_time,
                thread_results=results,
                collapse_reasoning="Selected first successful result",
            )

        elif strategy == CollapseStrategy.WEIGHTED:
            # Weighted average based on confidence
            total_weight = sum(r.confidence for r in results)
            if total_weight == 0:
                return self._collapse_results(results, CollapseStrategy.FIRST_SUCCESS, total_time)

            # Find most confident result for final selection
            best_result = max(results, key=lambda r: r.confidence)
            avg_confidence = total_weight / len(results)

            return QuantumRoutingResult(
                provider=best_result.provider,
                model=best_result.model,
                confidence=avg_confidence,
                strategy_used="weighted_" + best_result.strategy.value,
                execution_time=total_time,
                thread_results=results,
                collapse_reasoning=f"Weighted selection, avg confidence: {avg_confidence:.3f}",
            )

        else:  # Default to best score
            return self._collapse_results(results, CollapseStrategy.BEST_SCORE, total_time)

    def _analyze_task_complexity(self, request: ExecuteRequest) -> float:
        """Analyze task complexity from request."""
        complexity = 0.5  # Base complexity

        if request.prompt:
            # Length factor
            length_factor = min(len(request.prompt) / 1000, 1.0)
            complexity += length_factor * 0.3

            # Keyword complexity
            complex_keywords = [
                "architecture", "design", "optimize", "refactor",
                "algorithm", "performance", "scale", "distributed"
            ]
            keyword_count = sum(1 for kw in complex_keywords if kw in request.prompt.lower())
            complexity += min(keyword_count / len(complex_keywords), 0.5) * 0.2

        return min(complexity, 1.0)

    def _determine_context_type(self, request: ExecuteRequest) -> str:
        """Determine context type from request."""
        if not request.prompt:
            return "general"

        prompt_lower = request.prompt.lower()

        # Language detection
        if any(kw in prompt_lower for kw in ["python", "py", "import", "def "]):
            return "python"
        elif any(kw in prompt_lower for kw in ["javascript", "js", "function", "const", "let"]):
            return "javascript"
        elif any(kw in prompt_lower for kw in ["typescript", "ts", "interface", "type"]):
            return "typescript"
        elif any(kw in prompt_lower for kw in ["java", "class", "public", "private"]):
            return "java"
        else:
            return "general"

    def _get_provider_availability(self) -> Dict[str, bool]:
        """Get provider availability status."""
        return {
            provider.value: True for provider in ProviderType
        }

    def _get_historical_performance(self) -> Dict[str, float]:
        """Get historical performance metrics."""
        return {
            provider.value: 0.8 for provider in ProviderType
        }

    def _estimate_tokens(self, request: ExecuteRequest) -> int:
        """Estimate token count for request."""
        if not request.prompt:
            return 100

        # Rough estimation: 4 characters per token
        return len(request.prompt) // 4

    def _action_to_provider_model(self, action: int) -> Tuple[ProviderType, str]:
        """Map DQN action to provider and model."""
        # Simple mapping for demo
        action_map = {
            0: (ProviderType.OPENAI, "gpt-4"),
            1: (ProviderType.OPENAI, "gpt-4o"),
            2: (ProviderType.OPENAI, "gpt-4o-mini"),
            3: (ProviderType.ANTHROPIC, "claude-3-opus-20240229"),
            4: (ProviderType.ANTHROPIC, "claude-3-sonnet-20240229"),
            5: (ProviderType.ANTHROPIC, "claude-3-haiku-20240307"),
        }

        return action_map.get(action, (ProviderType.OPENAI, "gpt-4o-mini"))

    def _update_performance_history(self, result: QuantumRoutingResult):
        """Update performance tracking."""
        self.execution_history.append(result)

        # Keep only recent history
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-500:]

        # Update strategy performance
        strategy = result.strategy_used
        if strategy not in self.strategy_performance:
            self.strategy_performance[strategy] = []

        self.strategy_performance[strategy].append(result.confidence)

        # Keep only recent performance data
        if len(self.strategy_performance[strategy]) > 100:
            self.strategy_performance[strategy] = self.strategy_performance[strategy][-50:]

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        stats = {
            "total_executions": len(self.execution_history),
            "strategy_performance": {},
            "average_confidence": 0.0,
            "average_execution_time": 0.0,
        }

        if self.execution_history:
            stats["average_confidence"] = np.mean([r.confidence for r in self.execution_history])
            stats["average_execution_time"] = np.mean([r.execution_time for r in self.execution_history])

        for strategy, performances in self.strategy_performance.items():
            if performances:
                stats["strategy_performance"][strategy] = {
                    "count": len(performances),
                    "average_confidence": np.mean(performances),
                    "std_confidence": np.std(performances),
                }

        return stats

    def _create_fallback_result(
        self, thread_results: List[Any]
    ) -> QuantumRoutingResult:
        """Create fallback result when all strategies fail.

        Args:
            thread_results: List of thread results (may include exceptions)

        Returns:
            Fallback quantum routing result
        """
        # Extract any ThreadResult objects
        results = [r for r in thread_results if isinstance(r, ThreadResult)]

        return QuantumRoutingResult(
            provider=ProviderType.OPENAI,
            model="gpt-4.1-mini",
            confidence=0.3,
            strategy_used="fallback",
            execution_time=self.default_timeout,
            thread_results=results,
            collapse_reasoning="All strategies failed, using fallback model",
        )

    async def _get_system_state(self) -> Dict[str, Any]:
        """Get current system state for routing.

        Returns:
            System state dictionary
        """
        # This should be populated from actual system monitoring
        return {
            "provider_availability": {
                "openai": True,
                "anthropic": True,
                "google": True,
                "groq": True,
            },
            "historical_performance": {
                "openai": 0.85,
                "anthropic": 0.88,
                "google": 0.82,
                "groq": 0.78,
            },
            "memory_available": 0.8,
            "cpu_available": 0.7,
        }

    def _update_performance_metrics(self, result: QuantumRoutingResult):
        """Update performance tracking metrics.

        Args:
            result: Quantum routing result
        """
        # Store result
        self.execution_history.append(result)

        # Update strategy performance
        for thread_result in result.thread_results:
            strategy_name = thread_result.strategy.value
            if strategy_name not in self.strategy_performance:
                self.strategy_performance[strategy_name] = []

            # Store confidence as performance metric
            self.strategy_performance[strategy_name].append(thread_result.confidence)

        # Limit history size
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-1000:]

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for quantum routing.

        Returns:
            Performance summary dictionary
        """
        summary = {
            "total_executions": len(self.execution_history),
            "strategy_performance": {},
            "average_execution_time": 0.0,
            "average_confidence": 0.0,
        }

        # Calculate strategy performance
        for strategy, scores in self.strategy_performance.items():
            if scores:
                summary["strategy_performance"][strategy] = {
                    "avg_confidence": np.mean(scores),
                    "executions": len(scores),
                }

        # Calculate averages
        if self.execution_history:
            summary["average_execution_time"] = np.mean(
                [r.execution_time for r in self.execution_history]
            )
            summary["average_confidence"] = np.mean(
                [r.confidence for r in self.execution_history]
            )

        return summary

    async def get_routing_analytics(self) -> Dict[str, Any]:
        """Get comprehensive routing analytics.

        Returns:
            Analytics dictionary with detailed routing information
        """
        return {
            "performance_summary": self.get_performance_summary(),
            "execution_history_size": len(self.execution_history),
            "strategy_performance": self.strategy_performance,
            "thread_statistics": self._calculate_thread_statistics(),
            "recent_results": [
                {
                    "strategy": r.strategy_used,
                    "provider": r.provider.value,
                    "model": r.model,
                    "confidence": r.confidence,
                    "execution_time": r.execution_time,
                    "timestamp": time.time(),  # In real implementation, store actual timestamp
                }
                for r in self.execution_history[-10:]  # Last 10 results
            ],
            "system_state": await self._get_system_state(),
        }

    def _calculate_thread_statistics(self) -> Dict[str, Any]:
        """Calculate thread execution statistics.

        Returns:
            Thread statistics dictionary
        """
        stats = {
            "total_threads": 0,
            "successful_threads": 0,
            "failed_threads": 0,
            "timeout_threads": 0,
            "average_thread_time": 0.0,
        }

        total_threads = 0
        successful_threads = 0
        failed_threads = 0
        timeout_threads = 0
        thread_times = []

        for result in self.execution_history:
            for thread in result.thread_results:
                total_threads += 1
                thread_times.append(thread.execution_time)

                if thread.success:
                    successful_threads += 1
                else:
                    if "timeout" in (thread.error or "").lower():
                        timeout_threads += 1
                    else:
                        failed_threads += 1

        if total_threads > 0:
            stats.update({
                "total_threads": total_threads,
                "successful_threads": successful_threads,
                "failed_threads": failed_threads,
                "timeout_threads": timeout_threads,
                "average_thread_time": np.mean(thread_times) if thread_times else 0.0,
            })

        return stats

    async def optimize_routing_parameters(self):
        """Optimize routing parameters based on performance data.

        This method analyzes historical performance and adjusts
        routing parameters for better results.
        """
        if not self.execution_history:
            return

        # Analyze strategy performance
        strategy_stats = {}
        for strategy, performances in self.strategy_performance.items():
            if performances:
                strategy_stats[strategy] = {
                    "avg_confidence": np.mean(performances),
                    "stability": 1.0 - (np.std(performances) / np.mean(performances) if np.mean(performances) > 0 else 0),
                    "usage_count": len(performances),
                }

        # Log optimization insights
        logger.info("Quantum routing parameter optimization completed")
        logger.info(f"Strategy performance: {strategy_stats}")

        # In a real implementation, you would adjust parameters like:
        # - Thread timeouts based on execution times
        # - Strategy selection weights based on performance
        # - Confidence thresholds for collapse strategies

    async def save_routing_model(self, filepath: str) -> bool:
        """Save trained routing model to file.

        Args:
            filepath: Path to save the model

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.dqn_agent:
                # Save DQN model
                import pickle
                model_data = {
                    "execution_history": self.execution_history,
                    "strategy_performance": self.strategy_performance,
                    "dqn_agent_state": self.dqn_agent.get_state_dict(),
                }
                with open(filepath, "wb") as f:
                    pickle.dump(model_data, f)
                logger.info(f"Saved quantum routing model to {filepath}")
                return True
        except Exception as e:
            logger.error(f"Failed to save routing model: {e}")
        return False

    async def load_routing_model(self, filepath: str) -> bool:
        """Load trained routing model from file.

        Args:
            filepath: Path to load the model from

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.dqn_agent:
                import pickle
                with open(filepath, "rb") as f:
                    model_data = pickle.load(f)

                self.execution_history = model_data.get("execution_history", [])
                self.strategy_performance = model_data.get("strategy_performance", {})

                if "dqn_agent_state" in model_data:
                    self.dqn_agent.load_state_dict(model_data["dqn_agent_state"])

                logger.info(f"Loaded quantum routing model from {filepath}")
                return True
        except Exception as e:
            logger.error(f"Failed to load routing model: {e}")
        return False
