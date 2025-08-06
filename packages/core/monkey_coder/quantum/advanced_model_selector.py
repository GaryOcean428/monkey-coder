"""
Advanced Model Selector with Strategy Patterns and Provider Management

This module implements sophisticated model selection strategies with
intelligent fallback mechanisms and learning integration with DQN feedback.
"""

import asyncio
import time
import random
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
import numpy as np
from datetime import datetime, timedelta

from .quantum_models import ModelConfig, ProviderConfig, ModelCapability
from .dqn_agent import DQNAgent
from .state_encoder import StateEncoder
from .performance_metrics import PerformanceMetrics


def convert_capabilities_to_strings(capabilities: List[ModelCapability]) -> List[str]:
    """Convert ModelCapability enum values to strings"""
    return [cap.value for cap in capabilities] if capabilities else []


class SelectionStrategy(Enum):
    """Model selection strategies"""
    TASK_OPTIMIZED = "task_optimized"
    COST_EFFICIENT = "cost_efficient"
    PERFORMANCE = "performance"
    BALANCED = "balanced"
    DQN_BASED = "dqn_based"
    ADAPTIVE = "adaptive"
    LATENCY_OPTIMIZED = "latency_optimized"
    RELIABILITY_FOCUSED = "reliability_focused"


class ProviderStatus(Enum):
    """Provider health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"


@dataclass
class ProviderHealth:
    """Provider health information"""
    status: ProviderStatus
    latency_ms: float
    error_rate: float
    success_rate: float
    last_check: datetime
    consecutive_failures: int
    rate_limit_remaining: Optional[int] = None


@dataclass
class ModelScore:
    """Model selection score"""
    model_id: str
    provider: str
    score: float
    confidence: float
    reasoning: str
    estimated_cost: float
    estimated_latency: float
    capabilities: List[str]


class SelectionStrategyBase(ABC):
    """Base class for model selection strategies"""

    def __init__(self, name: str):
        self.name = name
        self.metrics = PerformanceMetrics()

    @abstractmethod
    async def select_model(
        self,
        task: str,
        context: Dict[str, Any],
        available_models: List[ModelConfig],
        provider_health: Dict[str, ProviderHealth]
    ) -> Optional[ModelScore]:
        """Select the best model for the given task"""
        pass

    def calculate_confidence(self, scores: List[float]) -> float:
        """Calculate selection confidence based on score distribution"""
        if not scores:
            return 0.0

        scores_array = np.array(scores)
        std_dev = float(np.std(scores_array))
        mean_score = float(np.mean(scores_array))

        # Higher confidence when scores are more differentiated
        if std_dev == 0:
            return 0.5

        confidence = min(1.0, std_dev / (mean_score + 1e-6))
        return confidence


class TaskOptimizedStrategy(SelectionStrategyBase):
    """Strategy that selects models based on task type optimization"""

    def __init__(self):
        super().__init__("task_optimized")
        self.task_model_mapping = {
            "code_generation": {
                "preferred": ["gpt-4.1", "claude-sonnet-4", "gemini-2.5-pro"],
                "capabilities": ["code", "reasoning", "structure"]
            },
            "code_analysis": {
                "preferred": ["claude-opus-4", "gpt-4.1", "o3-pro"],
                "capabilities": ["analysis", "pattern_recognition", "logic"]
            },
            "documentation": {
                "preferred": ["gpt-4.1", "claude-sonnet-4", "gemini-2.5-flash"],
                "capabilities": ["writing", "explanation", "clarity"]
            },
            "testing": {
                "preferred": ["gpt-4.1", "claude-sonnet-4", "o3"],
                "capabilities": ["testing", "edge_cases", "completeness"]
            },
            "architecture": {
                "preferred": ["claude-opus-4", "o3-pro", "gpt-4.1"],
                "capabilities": ["design", "scalability", "patterns"]
            }
        }

    async def select_model(
        self,
        task: str,
        context: Dict[str, Any],
        available_models: List[ModelConfig],
        provider_health: Dict[str, ProviderHealth]
    ) -> Optional[ModelScore]:
        """Select model based on task type optimization"""

        # Detect task type from prompt
        task_type = self._detect_task_type(task)

        # Get preferred models for this task type
        task_config = self.task_model_mapping.get(task_type, {})
        preferred_models = task_config.get("preferred", [])
        required_capabilities = task_config.get("capabilities", [])

        # Score models based on task suitability
        scores = []
        for model in available_models:
            if provider_health.get(model.provider, ProviderStatus.UNAVAILABLE) == ProviderStatus.UNAVAILABLE:
                continue

            score = self._calculate_task_score(model, task_type, preferred_models, required_capabilities)
            confidence = self._calculate_model_confidence(model, task_type)

            model_score = ModelScore(
                model_id=model.model_id,
                provider=model.provider,
                score=score,
                confidence=confidence,
                reasoning=f"Task-optimized for {task_type}",
                estimated_cost=model.cost_per_1k_tokens * 10,  # Estimate 10k tokens
                estimated_latency=provider_health[model.provider].latency_ms,
                capabilities=convert_capabilities_to_strings(model.capabilities) if model.capabilities else []
            )
            scores.append(model_score)

        if not scores:
            return None

        # Return highest scoring model
        return max(scores, key=lambda x: x.score)

    def _detect_task_type(self, task: str) -> str:
        """Detect the type of task from the prompt"""
        task_lower = task.lower()

        if any(word in task_lower for word in ["generate", "create", "write", "implement"]):
            if "code" in task_lower or "function" in task_lower:
                return "code_generation"

        if any(word in task_lower for word in ["analyze", "review", "examine", "audit"]):
            return "code_analysis"

        if any(word in task_lower for word in ["document", "explain", "describe", "comment"]):
            return "documentation"

        if any(word in task_lower for word in ["test", "unit test", "spec", "verify"]):
            return "testing"

        if any(word in task_lower for word in ["architecture", "design", "structure", "system"]):
            return "architecture"

        return "code_generation"  # Default

    def _calculate_task_score(
        self,
        model: ModelConfig,
        task_type: str,
        preferred_models: List[str],
        required_capabilities: List[str]
    ) -> float:
        """Calculate task suitability score"""
        score = 0.0

        # Base score for being a capable model
        score += 0.3

        # Bonus for being in preferred list
        if model.model_id in preferred_models:
            score += 0.4

        # Capability matching
        model_capabilities = model.capabilities or []
        capability_matches = len(set(required_capabilities) & set(model_capabilities))
        if required_capabilities:
            score += (capability_matches / len(required_capabilities)) * 0.3

        return min(1.0, score)

    def _calculate_model_confidence(self, model: ModelConfig, task_type: str) -> float:
        """Calculate confidence in model selection"""
        # Higher confidence for models with more capabilities
        capability_count = len(model.capabilities or [])
        return min(1.0, capability_count / 10.0)


class CostEfficientStrategy(SelectionStrategyBase):
    """Strategy that selects the most cost-effective capable model"""

    def __init__(self):
        super().__init__("cost_efficient")

    async def select_model(
        self,
        task: str,
        context: Dict[str, Any],
        available_models: List[ModelConfig],
        provider_health: Dict[str, ProviderHealth]
    ) -> Optional[ModelScore]:
        """Select most cost-effective model"""

        # Filter healthy providers
        healthy_models = [
            model for model in available_models
            if provider_health.get(model.provider, ProviderStatus.UNAVAILABLE) == ProviderStatus.HEALTHY
        ]

        if not healthy_models:
            return None

        # Score models based on cost efficiency
        scores = []
        for model in healthy_models:
            # Calculate cost efficiency (inverse of cost, adjusted for capabilities)
            cost_score = 1.0 / (model.cost_per_1k_tokens + 1e-6)
            capability_bonus = len(model.capabilities or []) * 0.1
            total_score = cost_score + capability_bonus

            model_score = ModelScore(
                model_id=model.model_id,
                provider=model.provider,
                score=total_score,
                confidence=0.8,  # High confidence in cost calculations
                reasoning="Cost-optimized selection",
                estimated_cost=model.cost_per_1k_tokens * 10,
                estimated_latency=provider_health[model.provider].latency_ms,
                capabilities=convert_capabilities_to_strings(model.capabilities) if model.capabilities else []
            )
            scores.append(model_score)

        return max(scores, key=lambda x: x.score)


class PerformanceStrategy(SelectionStrategyBase):
    """Strategy that selects the highest performing model"""

    def __init__(self):
        super().__init__("performance")
        self.performance_weights = {
            "reasoning": 0.3,
            "code": 0.25,
            "speed": 0.2,
            "accuracy": 0.25
        }

    async def select_model(
        self,
        task: str,
        context: Dict[str, Any],
        available_models: List[ModelConfig],
        provider_health: Dict[str, ProviderHealth]
    ) -> Optional[ModelScore]:
        """Select highest performing model"""

        scores = []
        for model in available_models:
            if provider_health.get(model.provider, ProviderStatus.UNAVAILABLE) == ProviderStatus.UNAVAILABLE:
                continue

            # Calculate performance score
            performance_score = self._calculate_performance_score(model)

            # Adjust for provider health
            health_adjustment = self._get_health_adjustment(provider_health[model.provider])
            adjusted_score = performance_score * health_adjustment

            model_score = ModelScore(
                model_id=model.model_id,
                provider=model.provider,
                score=adjusted_score,
                confidence=0.9,
                reasoning="Performance-optimized selection",
                estimated_cost=model.cost_per_1k_tokens * 10,
                estimated_latency=provider_health[model.provider].latency_ms,
                capabilities=convert_capabilities_to_strings(model.capabilities) if model.capabilities else []
            )
            scores.append(model_score)

        if not scores:
            return None

        return max(scores, key=lambda x: x.score)

    def _calculate_performance_score(self, model: ModelConfig) -> float:
        """Calculate performance score based on model characteristics"""
        score = 0.0

        # Base performance by model tier
        if "opus" in model.model_id or "o3-pro" in model.model_id:
            score += 0.9
        elif "sonnet" in model.model_id or "gpt-4.1" in model.model_id:
            score += 0.8
        elif "flash" in model.model_id or "mini" in model.model_id:
            score += 0.6
        else:
            score += 0.5

        # Capability bonuses
        capabilities = model.capabilities or []
        for capability, weight in self.performance_weights.items():
            if capability in capabilities:
                score += weight * 0.1

        return min(1.0, score)

    def _get_health_adjustment(self, health: ProviderHealth) -> float:
        """Get score adjustment based on provider health"""
        if health.status == ProviderStatus.HEALTHY:
            return 1.0
        elif health.status == ProviderStatus.DEGRADED:
            return 0.8
        elif health.status == ProviderStatus.RATE_LIMITED:
            return 0.5
        else:
            return 0.1


class DQNBasedStrategy(SelectionStrategyBase):
    """Strategy that uses DQN learning for model selection"""

    def __init__(self, dqn_agent: DQNAgent, state_encoder: StateEncoder):
        super().__init__("dqn_based")
        self.dqn_agent = dqn_agent
        self.state_encoder = state_encoder

    async def select_model(
        self,
        task: str,
        context: Dict[str, Any],
        available_models: List[ModelConfig],
        provider_health: Dict[str, ProviderHealth]
    ) -> Optional[ModelScore]:
        """Select model using DQN policy"""

        # Encode state for DQN
        state = await self.state_encoder.encode_state(task, context, available_models, provider_health)

        # Get DQN action (model selection)
        action_index = await self.dqn_agent.select_action(state)

        # Map action to model
        if action_index < len(available_models):
            selected_model = available_models[action_index]
            health = provider_health[selected_model.provider]

            # Calculate Q-value as confidence
            q_values = await self.dqn_agent.predict(state)
            confidence = float(q_values[action_index])

            return ModelScore(
                model_id=selected_model.model_id,
                provider=selected_model.provider,
                score=confidence,
                confidence=min(1.0, confidence),
                reasoning="DQN-based selection with learned policy",
                estimated_cost=selected_model.cost_per_1k_tokens * 10,
                estimated_latency=health.latency_ms,
                capabilities=convert_capabilities_to_strings(selected_model.capabilities) if selected_model.capabilities else []
            )

        return None


class AdaptiveStrategy(SelectionStrategyBase):
    """Adaptive strategy that combines multiple strategies based on context"""

    def __init__(self, strategies: Dict[str, SelectionStrategyBase]):
        super().__init__("adaptive")
        self.strategies = strategies
        self.strategy_performance = {}
        self.context_weights = {
            "urgent": {"performance": 0.6, "cost": 0.2, "task": 0.2},
            "budget_conscious": {"cost": 0.7, "task": 0.2, "performance": 0.1},
            "quality_focused": {"performance": 0.5, "task": 0.4, "cost": 0.1},
            "balanced": {"task": 0.4, "performance": 0.3, "cost": 0.3}
        }

    async def select_model(
        self,
        task: str,
        context: Dict[str, Any],
        available_models: List[ModelConfig],
        provider_health: Dict[str, ProviderHealth]
    ) -> Optional[ModelScore]:
        """Select model using adaptive strategy combination"""

        # Determine context type
        context_type = self._determine_context(task, context)
        weights = self.context_weights.get(context_type, self.context_weights["balanced"])

        # Get recommendations from each strategy
        strategy_results = {}
        for strategy_name, strategy in self.strategies.items():
            result = await strategy.select_model(task, context, available_models, provider_health)
            if result:
                strategy_results[strategy_name] = result

        if not strategy_results:
            return None

        # Combine scores based on weights
        combined_scores = {}
        for model_id in set(r.model_id for r in strategy_results.values()):
            combined_score = 0.0
            reasoning_parts = []

            for strategy_name, result in strategy_results.items():
                if result.model_id == model_id:
                    weight_key = strategy_name.replace("_optimized", "").replace("_based", "")
                    weight = weights.get(weight_key, 0.25)
                    combined_score += result.score * weight
                    reasoning_parts.append(f"{strategy_name}: {result.score:.2f}")

            combined_scores[model_id] = {
                "score": combined_score,
                "reasoning": " | ".join(reasoning_parts)
            }

        # Select best combined model
        best_model_id = max(combined_scores.keys(), key=lambda k: combined_scores[k]["score"])
        best_result = next(r for r in strategy_results.values() if r.model_id == best_model_id)

        return ModelScore(
            model_id=best_result.model_id,
            provider=best_result.provider,
            score=combined_scores[best_model_id]["score"],
            confidence=0.85,  # High confidence in adaptive approach
            reasoning=f"Adaptive selection: {combined_scores[best_model_id]['reasoning']}",
            estimated_cost=best_result.estimated_cost,
            estimated_latency=best_result.estimated_latency,
            capabilities=best_result.capabilities
        )

    def _determine_context(self, task: str, context: Dict[str, Any]) -> str:
        """Determine the context type for adaptive weighting"""
        task_lower = task.lower()

        # Check for urgency indicators
        if any(word in task_lower for word in ["urgent", "asap", "quickly", "fast"]):
            return "urgent"

        # Check for budget constraints
        if context.get("budget_constraints") or "cheap" in task_lower or "low cost" in task_lower:
            return "budget_conscious"

        # Check for quality focus
        if any(word in task_lower for word in ["best", "optimal", "perfect", "high quality"]):
            return "quality_focused"

        return "balanced"


class AdvancedModelSelector:
    """Advanced model selector with strategy patterns and provider management"""

    def __init__(self, dqn_agent: Optional[DQNAgent] = None, state_encoder: Optional[StateEncoder] = None):
        self.dqn_agent = dqn_agent
        self.state_encoder = state_encoder
        self.strategies = self._initialize_strategies()
        self.provider_health = {}
        self.selection_history = []
        self.ab_test_results = {}

        # Initialize provider monitoring
        self._start_provider_monitoring()

    def _initialize_strategies(self) -> Dict[str, SelectionStrategyBase]:
        """Initialize all selection strategies"""
        strategies = {
            "task_optimized": TaskOptimizedStrategy(),
            "cost_efficient": CostEfficientStrategy(),
            "performance": PerformanceStrategy()
        }

        # Add DQN-based strategy if available
        if self.dqn_agent and self.state_encoder:
            strategies["dqn_based"] = DQNBasedStrategy(self.dqn_agent, self.state_encoder)

        # Add adaptive strategy that combines others
        strategies["adaptive"] = AdaptiveStrategy(strategies)

        return strategies

    async def select_optimal_model(
        self,
        task: str,
        context: Dict[str, Any],
        available_models: List[ModelConfig],
        strategy: SelectionStrategy = SelectionStrategy.ADAPTIVE,
        enable_ab_test: bool = False
    ) -> Tuple[Optional[ModelScore], Dict[str, Any]]:
        """
        Select the optimal model for the given task

        Returns:
            Tuple of (selected_model_score, selection_metadata)
        """

        start_time = time.time()

        # Update provider health
        await self._update_provider_health()

        # Filter available models by health
        healthy_models = [
            model for model in available_models
            if self.provider_health.get(model.provider, ProviderStatus.HEALTHY) != ProviderStatus.UNAVAILABLE
        ]

        if not healthy_models:
            return None, {"error": "No healthy models available"}

        # Select strategy
        if enable_ab_test and random.random() < 0.1:  # 10% A/B test rate
            strategy = random.choice(list(SelectionStrategy))

        strategy_instance = self.strategies.get(strategy.value)
        if not strategy_instance:
            strategy_instance = self.strategies["adaptive"]  # Fallback

        # Get model selection
        selected_model = await strategy_instance.select_model(
            task, context, healthy_models, self.provider_health
        )

        # Record selection
        selection_metadata = {
            "strategy": strategy.value,
            "processing_time_ms": (time.time() - start_time) * 1000,
            "available_models": len(healthy_models),
            "provider_health": {k: v.status.value for k, v in self.provider_health.items()},
            "timestamp": datetime.utcnow().isoformat()
        }

        if selected_model:
            self.selection_history.append({
                "task": task[:100],  # Truncate for storage
                "selected_model": selected_model.model_id,
                "provider": selected_model.provider,
                "strategy": strategy.value,
                "score": selected_model.score,
                "timestamp": datetime.utcnow()
            })

            # Update strategy performance for A/B testing
            if enable_ab_test:
                self._update_ab_test_results(strategy.value, selected_model.score)

        return selected_model, selection_metadata

    async def _update_provider_health(self):
        """Update provider health status"""
        # This would normally involve actual health checks
        # For now, simulate health updates
        for provider in ["openai", "anthropic", "google", "groq", "xAI"]:
            if provider not in self.provider_health:
                self.provider_health[provider] = ProviderHealth(
                    status=ProviderStatus.HEALTHY,
                    latency_ms=random.uniform(50, 200),
                    error_rate=random.uniform(0.01, 0.05),
                    success_rate=random.uniform(0.95, 0.99),
                    last_check=datetime.utcnow(),
                    consecutive_failures=0
                )
            else:
                # Simulate health changes
                health = self.provider_health[provider]
                health.last_check = datetime.utcnow()

                # Randomly simulate some degradation
                if random.random() < 0.05:  # 5% chance of degradation
                    health.status = ProviderStatus.DEGRADED
                    health.latency_ms *= 1.5
                elif random.random() < 0.01:  # 1% chance of failure
                    health.status = ProviderStatus.UNAVAILABLE
                    health.consecutive_failures += 1
                else:
                    health.status = ProviderStatus.HEALTHY
                    health.consecutive_failures = max(0, health.consecutive_failures - 1)

    def _start_provider_monitoring(self):
        """Start background provider health monitoring"""
        # In a real implementation, this would start a background task
        # For now, we'll update health on each selection
        pass

    def _update_ab_test_results(self, strategy: str, score: float):
        """Update A/B testing results"""
        if strategy not in self.ab_test_results:
            self.ab_test_results[strategy] = {
                "selections": 0,
                "total_score": 0.0,
                "average_score": 0.0
            }

        results = self.ab_test_results[strategy]
        results["selections"] += 1
        results["total_score"] += score
        results["average_score"] = results["total_score"] / results["selections"]

    def get_strategy_performance(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics for all strategies"""
        return {
            strategy: {
                "selections": data["selections"],
                "average_score": data["average_score"],
                "usage_percentage": data["selections"] / max(1, sum(r["selections"] for r in self.ab_test_results.values()))
            }
            for strategy, data in self.ab_test_results.items()
        }

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get current provider health status"""
        return {
            provider: {
                "status": health.status.value,
                "latency_ms": health.latency_ms,
                "error_rate": health.error_rate,
                "success_rate": health.success_rate,
                "consecutive_failures": health.consecutive_failures
            }
            for provider, health in self.provider_health.items()
        }

    async def test_model_fallback(
        self,
        task: str,
        context: Dict[str, Any],
        available_models: List[ModelConfig],
        primary_strategy: SelectionStrategy = SelectionStrategy.ADAPTIVE
    ) -> Tuple[Optional[ModelScore], List[ModelScore]]:
        """
        Test model selection with fallback mechanisms

        Returns:
            Tuple of (final_selection, fallback_attempts)
        """
        fallback_attempts = []

        # Try primary strategy
        selected_model, metadata = await self.select_optimal_model(
            task, context, available_models, primary_strategy
        )

        if selected_model:
            return selected_model, fallback_attempts

        # Fallback 1: Try different strategies
        fallback_strategies = [
            SelectionStrategy.TASK_OPTIMIZED,
            SelectionStrategy.PERFORMANCE,
            SelectionStrategy.COST_EFFICIENT
        ]

        for strategy in fallback_strategies:
            fallback_model, _ = await self.select_optimal_model(
                task, context, available_models, strategy
            )

            if fallback_model:
                fallback_attempts.append(fallback_model)
                return fallback_model, fallback_attempts

        # Fallback 2: Try any available model
        for model in available_models:
            if self.provider_health.get(model.provider, ProviderStatus.UNAVAILABLE) != ProviderStatus.UNAVAILABLE:
                fallback_score = ModelScore(
                    model_id=model.model_id,
                    provider=model.provider,
                    score=0.1,  # Low score for fallback
                    confidence=0.5,
                    reasoning="Emergency fallback selection",
                    estimated_cost=model.cost_per_1k_tokens * 10,
                    estimated_latency=1000,  # Pessimistic estimate
                    capabilities=convert_capabilities_to_strings(model.capabilities) if model.capabilities else []
                )
                fallback_attempts.append(fallback_score)
                return fallback_score, fallback_attempts

        return None, fallback_attempts
