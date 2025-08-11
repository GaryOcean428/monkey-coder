"""
Advanced State Encoding for Quantum Routing DQN

This module provides comprehensive state representation for the DQN routing agent,
significantly enhancing the basic RoutingState with sophisticated encoding strategies
for better learning and decision-making accuracy.

Features:
- Multi-dimensional task complexity encoding
- Provider capability and availability modeling
- Historical performance with temporal awareness
- Dynamic context type classification
- User preference learning and adaptation
- Resource constraint optimization
"""

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum

import numpy as np

from monkey_coder.models import ProviderType, TaskType


class ContextComplexity(Enum):
    """Context complexity categories for enhanced encoding."""
    SIMPLE = "simple"           # Basic operations, single-step tasks
    MODERATE = "moderate"       # Multi-step operations, some reasoning
    COMPLEX = "complex"         # Advanced reasoning, multi-domain
    CRITICAL = "critical"       # High-stakes, maximum quality requirements


class TimeWindow(Enum):
    """Time windows for historical performance analysis."""
    RECENT = "recent"           # Last 24 hours
    SHORT_TERM = "short_term"   # Last 7 days
    MEDIUM_TERM = "medium_term" # Last 30 days
    LONG_TERM = "long_term"     # Last 90+ days


@dataclass
class TaskContextProfile:
    """Detailed task context profile for enhanced routing decisions."""

    # Core task characteristics
    task_type: TaskType
    estimated_complexity: float  # 0.0-1.0
    complexity_category: ContextComplexity
    domain_requirements: Set[str]  # e.g., {"programming", "analysis", "creative"}

    # Quality and performance requirements
    quality_threshold: float = 0.7  # Minimum acceptable quality
    latency_requirement: float = 30.0  # Maximum acceptable latency (seconds)
    cost_sensitivity: float = 0.5  # 0.0 = cost-insensitive, 1.0 = cost-critical

    # Contextual factors
    is_production: bool = False
    requires_reasoning: bool = False
    requires_creativity: bool = False
    requires_accuracy: bool = True

    # Temporal context
    time_of_day: float = 0.5  # 0.0 = midnight, 0.5 = noon, 1.0 = midnight
    day_of_week: int = 1  # 1-7, Monday-Sunday
    timezone_offset: float = 0.0  # UTC offset in hours


@dataclass
class ProviderPerformanceHistory:
    """Detailed provider performance history with temporal awareness."""

    # Recent performance metrics
    recent_success_rate: float = 0.8
    recent_avg_latency: float = 2.0
    recent_avg_quality: float = 0.75
    recent_cost_efficiency: float = 0.7

    # Short-term trends
    short_term_success_rate: float = 0.8
    short_term_avg_latency: float = 2.0
    short_term_quality_trend: float = 0.0  # -1.0 to 1.0 (declining to improving)

    # Medium-term stability
    medium_term_variance: float = 0.1  # Performance variance
    medium_term_reliability: float = 0.9  # Consistency score

    # Long-term reputation
    long_term_reputation: float = 0.85  # Overall reputation score
    total_interactions: int = 100  # Total number of interactions

    # Specialized performance
    domain_expertise: Dict[str, float] = field(default_factory=dict)  # Domain-specific performance
    complexity_performance: Dict[ContextComplexity, float] = field(default_factory=dict)

    def get_performance_vector(self) -> np.ndarray:
        """Convert performance history to vector representation."""
        return np.array([
            self.recent_success_rate,
            self.recent_avg_latency / 10.0,  # Normalize to ~0-1 range
            self.recent_avg_quality,
            self.recent_cost_efficiency,
            self.short_term_success_rate,
            self.short_term_avg_latency / 10.0,
            (self.short_term_quality_trend + 1.0) / 2.0,  # Normalize to 0-1
            self.medium_term_variance,
            self.medium_term_reliability,
            self.long_term_reputation,
            min(self.total_interactions / 1000.0, 1.0),  # Normalize experience
        ], dtype=np.float32)


@dataclass
class UserPreferences:
    """Enhanced user preferences with learning capabilities."""

    # Provider preferences (learned from usage patterns)
    provider_preference_scores: Dict[ProviderType, float] = field(default_factory=dict)

    # Strategy preferences
    preferred_strategies: Dict[str, float] = field(default_factory=lambda: {
        "task_optimized": 0.25,
        "cost_efficient": 0.25,
        "performance": 0.25,
        "balanced": 0.25
    })

    # Quality vs. speed trade-off preference
    quality_vs_speed_preference: float = 0.5  # 0.0 = speed priority, 1.0 = quality priority

    # Cost sensitivity
    cost_sensitivity: float = 0.5  # 0.0 = cost-insensitive, 1.0 = cost-critical

    # Risk tolerance
    risk_tolerance: float = 0.5  # 0.0 = risk-averse, 1.0 = risk-tolerant

    # Personalization strength
    personalization_strength: float = 0.3  # How much to weight user preferences

    def get_preference_vector(self) -> np.ndarray:
        """Convert preferences to vector representation."""
        # Provider preference scores
        provider_scores = []
        for provider in ProviderType:
            provider_scores.append(self.provider_preference_scores.get(provider, 0.5))

        # Strategy preferences
        strategy_scores = [
            self.preferred_strategies["task_optimized"],
            self.preferred_strategies["cost_efficient"],
            self.preferred_strategies["performance"],
            self.preferred_strategies["balanced"]
        ]

        return np.array([
            *provider_scores,  # 5 provider scores
            *strategy_scores,  # 4 strategy scores
            self.quality_vs_speed_preference,
            self.cost_sensitivity,
            self.risk_tolerance,
            self.personalization_strength
        ], dtype=np.float32)


@dataclass
class ResourceConstraints:
    """Enhanced resource constraints with dynamic weighting."""

    # Hard constraints (must be satisfied)
    max_cost_per_request: Optional[float] = None
    max_latency_seconds: Optional[float] = None
    min_quality_threshold: Optional[float] = None

    # Soft constraints (preferences with weights)
    cost_weight: float = 0.33
    latency_weight: float = 0.33
    quality_weight: float = 0.34

    # Dynamic constraint adjustment
    constraint_flexibility: float = 0.2  # How much constraints can be relaxed

    # Business context
    is_premium_user: bool = False
    has_priority_access: bool = False
    billing_tier: str = "standard"  # "free", "standard", "premium", "enterprise"

    def get_constraint_vector(self) -> np.ndarray:
        """Convert constraints to vector representation."""
        return np.array([
            self.max_cost_per_request / 10.0 if self.max_cost_per_request else 1.0,  # Normalized
            self.max_latency_seconds / 60.0 if self.max_latency_seconds else 1.0,   # Normalized
            self.min_quality_threshold if self.min_quality_threshold else 0.0,
            self.cost_weight,
            self.latency_weight,
            self.quality_weight,
            self.constraint_flexibility,
            1.0 if self.is_premium_user else 0.0,
            1.0 if self.has_priority_access else 0.0,
            {"free": 0.0, "standard": 0.33, "premium": 0.66, "enterprise": 1.0}.get(self.billing_tier, 0.33)
        ], dtype=np.float32)


class AdvancedStateEncoder:
    """
    Advanced state encoder for quantum routing DQN.

    This encoder creates comprehensive state representations that include:
    - Multi-dimensional task analysis
    - Temporal performance patterns
    - Dynamic provider capabilities
    - User preference learning
    - Contextual decision factors
    """

    def __init__(
        self,
        enable_temporal_features: bool = True,
        enable_user_personalization: bool = True,
        enable_dynamic_weighting: bool = True,
        context_window_size: int = 10
    ):
        """
        Initialize the advanced state encoder.

        Args:
            enable_temporal_features: Include temporal performance patterns
            enable_user_personalization: Include user preference learning
            enable_dynamic_weighting: Adjust feature weights dynamically
            context_window_size: Size of historical context window
        """
        self.enable_temporal_features = enable_temporal_features
        self.enable_user_personalization = enable_user_personalization
        self.enable_dynamic_weighting = enable_dynamic_weighting
        self.context_window_size = context_window_size

        # Feature dimension calculation
        self.base_dimensions = 15      # Core task and complexity features
        self.provider_dimensions = 60  # 5 providers × (1 availability + 11 performance metrics)
        self.preference_dimensions = 13 # User preference vector
        self.constraint_dimensions = 10 # Resource constraint vector
        self.temporal_dimensions = 8 if enable_temporal_features else 0
        self.context_dimensions = 6     # Contextual factors

        self.total_dimensions = (
            self.base_dimensions +
            self.provider_dimensions +
            self.preference_dimensions +
            self.constraint_dimensions +
            self.temporal_dimensions +
            self.context_dimensions
        )

    def encode_state(
        self,
        task_context: TaskContextProfile,
        provider_history: Dict[ProviderType, ProviderPerformanceHistory],
        user_preferences: UserPreferences,
        resource_constraints: ResourceConstraints,
        provider_availability: Dict[ProviderType, bool]
    ) -> np.ndarray:
        """
        Encode complete state for DQN input.

        Args:
            task_context: Task context and requirements
            provider_history: Historical performance for all providers
            user_preferences: User preferences and personalization
            resource_constraints: Resource constraints and business context
            provider_availability: Current provider availability

        Returns:
            High-dimensional state vector for DQN
        """
        state_components = []

        # 1. Core task features (15 dimensions)
        task_features = self._encode_task_context(task_context)
        state_components.append(task_features)

        # 2. Provider performance features (55 dimensions: 5 providers × 11 metrics)
        provider_features = self._encode_provider_history(provider_history, provider_availability)
        state_components.append(provider_features)

        # 3. User preference features (13 dimensions)
        if self.enable_user_personalization:
            preference_features = user_preferences.get_preference_vector()
            state_components.append(preference_features)
        else:
            # Use neutral preferences if personalization disabled
            neutral_prefs = np.full(self.preference_dimensions, 0.5, dtype=np.float32)
            state_components.append(neutral_prefs)

        # 4. Resource constraint features (10 dimensions)
        constraint_features = resource_constraints.get_constraint_vector()
        state_components.append(constraint_features)

        # 5. Temporal features (8 dimensions)
        if self.enable_temporal_features:
            temporal_features = self._encode_temporal_context(task_context)
            state_components.append(temporal_features)

        # 6. Contextual features (6 dimensions)
        context_features = self._encode_contextual_factors(task_context, provider_availability)
        state_components.append(context_features)

        # Combine all features
        complete_state = np.concatenate(state_components)

        # Apply dynamic weighting if enabled
        if self.enable_dynamic_weighting:
            complete_state = self._apply_dynamic_weighting(complete_state, task_context)

        # Ensure correct dimensionality
        assert len(complete_state) == self.total_dimensions, \
            f"State vector has {len(complete_state)} dimensions, expected {self.total_dimensions}"

        return complete_state

    def _encode_task_context(self, task_context: TaskContextProfile) -> np.ndarray:
        """Encode task context into feature vector."""
        features = []

        # Basic complexity
        features.append(task_context.estimated_complexity)

        # Complexity category (one-hot)
        complexity_categories = [ContextComplexity.SIMPLE, ContextComplexity.MODERATE,
                               ContextComplexity.COMPLEX, ContextComplexity.CRITICAL]
        for category in complexity_categories:
            features.append(1.0 if task_context.complexity_category == category else 0.0)

        # Task type (one-hot encoding for major types)
        task_types = [TaskType.CODE_GENERATION, TaskType.CODE_ANALYSIS,
                     TaskType.DEBUGGING, TaskType.TESTING]
        for task_type in task_types:
            features.append(1.0 if task_context.task_type == task_type else 0.0)

        # Requirements
        features.extend([
            task_context.quality_threshold,
            min(task_context.latency_requirement / 30.0, 1.0),  # Normalize to 30s max
            task_context.cost_sensitivity,
            1.0 if task_context.requires_reasoning else 0.0,
            1.0 if task_context.requires_creativity else 0.0,
            1.0 if task_context.is_production else 0.0
        ])

        return np.array(features, dtype=np.float32)

    def _encode_provider_history(
        self,
        provider_history: Dict[ProviderType, ProviderPerformanceHistory],
        provider_availability: Dict[ProviderType, bool]
    ) -> np.ndarray:
        """Encode provider performance history."""
        features = []

        for provider in ProviderType:
            # Provider availability
            is_available = provider_availability.get(provider, True)
            features.append(1.0 if is_available else 0.0)

            # Performance history (11 dimensions from ProviderPerformanceHistory.get_performance_vector)
            if provider in provider_history and is_available:
                perf_vector = provider_history[provider].get_performance_vector()
                features.extend(perf_vector)
            else:
                # Use neutral values for unavailable providers
                features.extend([0.5] * 11)

        return np.array(features, dtype=np.float32)

    def _encode_temporal_context(self, task_context: TaskContextProfile) -> np.ndarray:
        """Encode temporal context features."""
        current_time = time.time()
        current_hour = (current_time // 3600) % 24 / 24.0  # Normalize to 0-1

        return np.array([
            task_context.time_of_day,
            task_context.day_of_week / 7.0,  # Normalize to 0-1
            task_context.timezone_offset / 12.0,  # Normalize to -1 to 1 range
            current_hour,
            np.sin(2 * np.pi * current_hour),  # Cyclical time encoding
            np.cos(2 * np.pi * current_hour),
            np.sin(2 * np.pi * task_context.day_of_week / 7.0),  # Cyclical day encoding
            np.cos(2 * np.pi * task_context.day_of_week / 7.0)
        ], dtype=np.float32)

    def _encode_contextual_factors(
        self,
        task_context: TaskContextProfile,
        provider_availability: Dict[ProviderType, bool]
    ) -> np.ndarray:
        """Encode additional contextual decision factors."""
        available_providers = sum(1 for available in provider_availability.values() if available)
        total_providers = len(provider_availability)

        return np.array([
            available_providers / max(total_providers, 1),  # Provider availability ratio
            len(task_context.domain_requirements) / 5.0,    # Domain complexity (normalize to 5 max)
            1.0 if task_context.requires_accuracy else 0.0,
            task_context.estimated_complexity ** 2,         # Non-linear complexity
            min(task_context.latency_requirement / 120.0, 1.0),  # Extended latency normalization
            1.0 if available_providers >= 3 else 0.5       # High availability indicator
        ], dtype=np.float32)

    def _apply_dynamic_weighting(
        self,
        state_vector: np.ndarray,
        task_context: TaskContextProfile
    ) -> np.ndarray:
        """Apply dynamic weighting based on task characteristics."""
        # Create weighting factors based on task requirements
        weights = np.ones_like(state_vector)

        # Boost provider performance features for production tasks
        if task_context.is_production:
            provider_start = self.base_dimensions
            provider_end = provider_start + self.provider_dimensions
            weights[provider_start:provider_end] *= 1.2

        # Boost quality features for high-accuracy tasks
        if task_context.requires_accuracy and task_context.quality_threshold > 0.8:
            # Emphasize quality-related provider metrics
            for i in range(5):  # 5 providers
                base_idx = self.base_dimensions + i * 11  # 11 metrics per provider
                weights[base_idx + 2] *= 1.3  # Quality metric

        # Boost temporal features for time-sensitive tasks
        if self.enable_temporal_features and task_context.latency_requirement < 10.0:
            temporal_start = (self.base_dimensions + self.provider_dimensions +
                            self.preference_dimensions + self.constraint_dimensions)
            temporal_end = temporal_start + self.temporal_dimensions
            weights[temporal_start:temporal_end] *= 1.1

        return state_vector * weights

    def create_routing_state(
        self,
        task_type: TaskType,
        prompt: str,
        complexity: float,
        context_requirements: Dict[str, Any],
        provider_availability: Dict[ProviderType, bool],
        user_id: Optional[str] = None
    ) -> np.ndarray:
        """
        Convenience method to create routing state from basic parameters.

        This method provides a simple interface for creating states from
        common routing parameters, using reasonable defaults for advanced features.
        """
        # Create task context profile
        task_context = TaskContextProfile(
            task_type=task_type,
            estimated_complexity=complexity,
            complexity_category=self._estimate_complexity_category(complexity),
            domain_requirements=self._extract_domain_requirements(prompt, task_type),
            quality_threshold=context_requirements.get("quality_threshold", 0.7),
            latency_requirement=context_requirements.get("timeout", 30.0),
            cost_sensitivity=context_requirements.get("cost_sensitivity", 0.5),
            is_production=context_requirements.get("is_production", False),
            requires_reasoning=self._requires_reasoning(prompt, task_type),
            requires_creativity=self._requires_creativity(prompt, task_type),
            time_of_day=time.time() % 86400 / 86400,  # Current time of day
            day_of_week=int(time.time() // 86400) % 7 + 1
        )

        # Create default provider performance history
        provider_history = {}
        for provider in ProviderType:
            provider_history[provider] = ProviderPerformanceHistory()

        # Create default user preferences
        user_preferences = UserPreferences()

        # Create default resource constraints
        resource_constraints = ResourceConstraints(
            max_latency_seconds=context_requirements.get("timeout"),
            min_quality_threshold=context_requirements.get("quality_threshold"),
        )

        return self.encode_state(
            task_context=task_context,
            provider_history=provider_history,
            user_preferences=user_preferences,
            resource_constraints=resource_constraints,
            provider_availability=provider_availability
        )

    def _estimate_complexity_category(self, complexity: float) -> ContextComplexity:
        """Estimate complexity category from numerical complexity."""
        if complexity < 0.25:
            return ContextComplexity.SIMPLE
        elif complexity < 0.5:
            return ContextComplexity.MODERATE
        elif complexity < 0.8:
            return ContextComplexity.COMPLEX
        else:
            return ContextComplexity.CRITICAL

    def _extract_domain_requirements(self, prompt: str, task_type: TaskType) -> Set[str]:
        """Extract domain requirements from prompt and task type."""
        domains = set()

        # Add domain based on task type
        if task_type == TaskType.CODE_GENERATION:
            domains.add("programming")
        elif task_type == TaskType.CODE_ANALYSIS:
            domains.add("analysis")
        elif task_type == TaskType.DEBUGGING:
            domains.add("debugging")
        elif task_type == TaskType.TESTING:
            domains.add("testing")

        # Simple keyword-based domain detection
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ["creative", "story", "design"]):
            domains.add("creative")
        if any(word in prompt_lower for word in ["analyze", "research", "study"]):
            domains.add("analysis")
        if any(word in prompt_lower for word in ["math", "calculate", "compute"]):
            domains.add("mathematical")
        if any(word in prompt_lower for word in ["logic", "reason", "deduce"]):
            domains.add("reasoning")

        return domains

    def _requires_reasoning(self, prompt: str, task_type: TaskType) -> bool:
        """Determine if task requires complex reasoning."""
        reasoning_keywords = ["analyze", "explain", "why", "how", "reason", "logic", "deduce", "infer"]

        # Check for reasoning keywords in prompt first
        has_reasoning_keywords = any(keyword in prompt.lower() for keyword in reasoning_keywords)

        # For CODE_ANALYSIS, only require reasoning if prompt actually involves analysis
        if task_type == TaskType.CODE_ANALYSIS:
            return has_reasoning_keywords
        elif task_type == TaskType.DEBUGGING:
            return True  # Debugging inherently requires reasoning
        else:
            return has_reasoning_keywords

    def _requires_creativity(self, prompt: str, task_type: TaskType) -> bool:
        """Determine if task requires creativity."""
        creativity_keywords = ["creative", "design", "innovative", "brainstorm", "generate ideas"]
        return any(keyword in prompt.lower() for keyword in creativity_keywords)

    @property
    def state_size(self) -> int:
        """Get the total state vector size."""
        return self.total_dimensions

    def get_feature_names(self) -> List[str]:
        """Get human-readable feature names for debugging and analysis."""
        names = []

        # Base task features
        names.extend([
            "task_complexity",
            "complexity_simple", "complexity_moderate", "complexity_complex", "complexity_critical",
            "type_code_gen", "type_analysis", "type_debug", "type_testing",
            "quality_threshold", "latency_requirement", "cost_sensitivity",
            "requires_reasoning", "requires_creativity", "is_production"
        ])

        # Provider features (12 features per provider: 1 availability + 11 performance metrics)
        for provider in ProviderType:
            names.extend([
                f"{provider.value}_available",
                f"{provider.value}_recent_success", f"{provider.value}_recent_latency",
                f"{provider.value}_recent_quality", f"{provider.value}_recent_cost",
                f"{provider.value}_short_success", f"{provider.value}_short_latency",
                f"{provider.value}_quality_trend", f"{provider.value}_variance",
                f"{provider.value}_reliability", f"{provider.value}_reputation",
                f"{provider.value}_experience"
            ])

        # User preference features
        for provider in ProviderType:
            names.append(f"pref_{provider.value}")
        names.extend([
            "pref_task_optimized", "pref_cost_efficient", "pref_performance", "pref_balanced",
            "quality_vs_speed", "user_cost_sensitivity", "risk_tolerance", "personalization_strength"
        ])

        # Resource constraint features
        names.extend([
            "max_cost_constraint", "max_latency_constraint", "min_quality_constraint",
            "cost_weight", "latency_weight", "quality_weight", "constraint_flexibility",
            "is_premium_user", "has_priority", "billing_tier"
        ])

        # Temporal features
        if self.enable_temporal_features:
            names.extend([
                "time_of_day", "day_of_week", "timezone_offset", "current_hour",
                "hour_sin", "hour_cos", "day_sin", "day_cos"
            ])

        # Contextual features
        names.extend([
            "provider_availability_ratio", "domain_complexity", "requires_accuracy",
            "nonlinear_complexity", "extended_latency", "high_availability"
        ])

        return names


# Convenience function for easy state encoder creation
def create_state_encoder(
    encoding_strategy: str = "comprehensive",
    **kwargs
) -> AdvancedStateEncoder:
    """
    Create state encoder with predefined strategy.

    Args:
        encoding_strategy: "basic", "standard", "comprehensive", "minimal"
        **kwargs: Additional arguments for AdvancedStateEncoder

    Returns:
        Configured AdvancedStateEncoder instance
    """
    if encoding_strategy == "minimal":
        return AdvancedStateEncoder(
            enable_temporal_features=False,
            enable_user_personalization=False,
            enable_dynamic_weighting=False,
            **kwargs
        )
    elif encoding_strategy == "basic":
        return AdvancedStateEncoder(
            enable_temporal_features=False,
            enable_user_personalization=True,
            enable_dynamic_weighting=False,
            **kwargs
        )
    elif encoding_strategy == "standard":
        return AdvancedStateEncoder(
            enable_temporal_features=True,
            enable_user_personalization=True,
            enable_dynamic_weighting=False,
            **kwargs
        )
    else:  # comprehensive
        return AdvancedStateEncoder(
            enable_temporal_features=True,
            enable_user_personalization=True,
            enable_dynamic_weighting=True,
            **kwargs
        )


# Backward compatibility alias for existing imports
StateEncoder = AdvancedStateEncoder