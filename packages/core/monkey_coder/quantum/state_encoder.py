"""State Encoder for Quantum Routing.

This module provides comprehensive state encoding for the DQN agent,
including task complexity, context type, provider availability,
historical performance, and user preferences.
"""

import hashlib
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

from monkey_coder.models import ProviderType

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of tasks for routing."""

    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    CODE_REVIEW = "code_review"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    DEBUGGING = "debugging"
    REFACTORING = "refactoring"
    ARCHITECTURE = "architecture"
    UNKNOWN = "unknown"


class ContextType(Enum):
    """Types of context for routing."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    GO = "go"
    RUST = "rust"
    GENERAL = "general"
    UNKNOWN = "unknown"


@dataclass
class RoutingState:
    """Comprehensive state representation for routing decisions."""

    task_complexity: float  # 0.0 to 1.0
    context_type: str
    provider_availability: Dict[str, bool]
    historical_performance: Dict[str, float]
    resource_constraints: Dict[str, Any]
    user_preferences: Dict[str, Any]
    task_type: Optional[str] = None
    prompt_length: Optional[int] = None
    estimated_tokens: Optional[int] = None
    priority_level: Optional[float] = None  # 0.0 to 1.0


class StateEncoder:
    """Encode routing states for DQN agent."""

    # Feature dimensions
    TASK_FEATURES = 5  # complexity, type, length, tokens, priority
    CONTEXT_FEATURES = len(ContextType)
    PROVIDER_FEATURES = len(ProviderType) * 2  # availability + performance
    CONSTRAINT_FEATURES = 4  # memory, cpu, time, cost
    PREFERENCE_FEATURES = 5  # speed, quality, cost, reliability, familiarity

    TOTAL_FEATURES = (
        TASK_FEATURES
        + CONTEXT_FEATURES
        + PROVIDER_FEATURES
        + CONSTRAINT_FEATURES
        + PREFERENCE_FEATURES
    )

    def __init__(self):
        """Initialize state encoder."""
        self.task_type_map = {t.value: i for i, t in enumerate(TaskType)}
        self.context_type_map = {c.value: i for i, c in enumerate(ContextType)}
        self.provider_map = {p.value: i for i, p in enumerate(ProviderType)}

    def encode_state(self, state: RoutingState) -> np.ndarray:
        """Encode routing state into feature vector.

        Args:
            state: Routing state to encode

        Returns:
            Encoded feature vector
        """
        features = []

        # Task features
        task_features = self._encode_task_features(state)
        features.extend(task_features)

        # Context features
        context_features = self._encode_context_features(state)
        features.extend(context_features)

        # Provider features
        provider_features = self._encode_provider_features(state)
        features.extend(provider_features)

        # Constraint features
        constraint_features = self._encode_constraint_features(state)
        features.extend(constraint_features)

        # Preference features
        preference_features = self._encode_preference_features(state)
        features.extend(preference_features)

        return np.array(features, dtype=np.float32)

    def _encode_task_features(self, state: RoutingState) -> List[float]:
        """Encode task-related features.

        Args:
            state: Routing state

        Returns:
            List of task features
        """
        features = []

        # Task complexity (already normalized)
        features.append(state.task_complexity)

        # Task type (one-hot encoding compressed to single value)
        if state.task_type:
            task_idx = self.task_type_map.get(state.task_type, len(TaskType) - 1)
            task_value = task_idx / len(TaskType)
        else:
            task_value = 0.5  # Default to middle value
        features.append(task_value)

        # Prompt length (normalized)
        if state.prompt_length:
            # Normalize to 0-1 range (assuming max 10000 chars)
            length_norm = min(state.prompt_length / 10000.0, 1.0)
        else:
            length_norm = 0.1  # Default small value
        features.append(length_norm)

        # Estimated tokens (normalized)
        if state.estimated_tokens:
            # Normalize to 0-1 range (assuming max 8000 tokens)
            tokens_norm = min(state.estimated_tokens / 8000.0, 1.0)
        else:
            tokens_norm = 0.1  # Default small value
        features.append(tokens_norm)

        # Priority level
        priority = state.priority_level if state.priority_level else 0.5
        features.append(priority)

        return features

    def _encode_context_features(self, state: RoutingState) -> List[float]:
        """Encode context-related features.

        Args:
            state: Routing state

        Returns:
            List of context features (one-hot encoding)
        """
        features = [0.0] * len(ContextType)

        if state.context_type:
            ctx_idx = self.context_type_map.get(
                state.context_type, len(ContextType) - 1
            )
            features[ctx_idx] = 1.0

        return features

    def _encode_provider_features(self, state: RoutingState) -> List[float]:
        """Encode provider-related features.

        Args:
            state: Routing state

        Returns:
            List of provider features
        """
        features = []

        # Provider availability
        for provider in ProviderType:
            available = state.provider_availability.get(provider.value, False)
            features.append(1.0 if available else 0.0)

        # Provider historical performance
        for provider in ProviderType:
            performance = state.historical_performance.get(provider.value, 0.5)
            features.append(performance)

        return features

    def _encode_constraint_features(self, state: RoutingState) -> List[float]:
        """Encode resource constraint features.

        Args:
            state: Routing state

        Returns:
            List of constraint features
        """
        features = []

        # Memory constraint (normalized)
        memory = state.resource_constraints.get("memory_available", 1.0)
        features.append(min(memory, 1.0))

        # CPU constraint (normalized)
        cpu = state.resource_constraints.get("cpu_available", 1.0)
        features.append(min(cpu, 1.0))

        # Time constraint (normalized, in seconds)
        time_limit = state.resource_constraints.get("time_limit", 10.0)
        time_norm = min(time_limit / 30.0, 1.0)  # Normalize to 30s max
        features.append(time_norm)

        # Cost constraint (normalized)
        cost_limit = state.resource_constraints.get("cost_limit", 1.0)
        features.append(min(cost_limit, 1.0))

        return features

    def _encode_preference_features(self, state: RoutingState) -> List[float]:
        """Encode user preference features.

        Args:
            state: Routing state

        Returns:
            List of preference features
        """
        features = []

        # Speed preference
        speed = state.user_preferences.get("speed_priority", 0.5)
        features.append(speed)

        # Quality preference
        quality = state.user_preferences.get("quality_priority", 0.5)
        features.append(quality)

        # Cost preference
        cost = state.user_preferences.get("cost_priority", 0.5)
        features.append(cost)

        # Reliability preference
        reliability = state.user_preferences.get("reliability_priority", 0.5)
        features.append(reliability)

        # Model familiarity
        familiarity = state.user_preferences.get("model_familiarity", 0.5)
        features.append(familiarity)

        return features

    def decode_action(self, action_idx: int) -> Dict[str, Any]:
        """Decode action index to routing decision.

        Args:
            action_idx: Action index from DQN

        Returns:
            Routing decision dictionary
        """
        # Map action index to provider and model combination
        providers = list(ProviderType)
        models_per_provider = 10  # Approximate models per provider

        provider_idx = action_idx // models_per_provider
        model_idx = action_idx % models_per_provider

        if provider_idx >= len(providers):
            provider_idx = 0  # Default to first provider

        provider = providers[provider_idx]

        # Get available models for provider
        available_models = self._get_provider_models(provider)
        if model_idx >= len(available_models):
            model_idx = 0

        return {
            "provider": provider.value,
            "model": available_models[model_idx] if available_models else None,
            "action_idx": action_idx,
        }

    def _get_provider_models(self, provider: ProviderType) -> List[str]:
        """Get available models for a provider.

        Args:
            provider: Provider type

        Returns:
            List of model names
        """
        # This should be populated from actual model registry
        model_map = {
            ProviderType.OPENAI: [
                "gpt-4.1",
                "gpt-4.1-mini",
                "o3",
                "o3-mini",
                "o1",
                "o1-mini",
            ],
            ProviderType.ANTHROPIC: [
                "claude-opus-4-20250514",
                "claude-sonnet-4-20250514",
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022",
            ],
            ProviderType.GOOGLE: [
                "gemini-2.5-pro",
                "gemini-2.5-flash",
                "gemini-2.0-flash",
            ],
            ProviderType.GROQ: [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "qwen/qwen3-32b",
            ],
        }

        return model_map.get(provider, [])

    def get_state_hash(self, state: RoutingState) -> str:
        """Generate hash for state (for caching).

        Args:
            state: Routing state

        Returns:
            Hash string
        """
        # Create a deterministic string representation
        state_str = (
            f"{state.task_complexity:.2f}"
            f"{state.context_type}"
            f"{sorted(state.provider_availability.items())}"
            f"{state.task_type}"
            f"{state.prompt_length}"
            f"{state.priority_level}"
        )

        # Generate hash
        return hashlib.md5(state_str.encode()).hexdigest()

    def create_state_from_request(
        self, request: Dict[str, Any], system_state: Dict[str, Any]
    ) -> RoutingState:
        """Create routing state from request and system state.

        Args:
            request: User request dictionary
            system_state: Current system state

        Returns:
            Routing state
        """
        # Extract task complexity
        prompt = request.get("prompt", "")
        task_complexity = self._estimate_complexity(prompt)

        # Determine context type
        context_type = self._detect_context_type(prompt, request.get("context", {}))

        # Get provider availability
        provider_availability = system_state.get("provider_availability", {})

        # Get historical performance
        historical_performance = system_state.get("historical_performance", {})

        # Extract resource constraints
        resource_constraints = {
            "memory_available": system_state.get("memory_available", 1.0),
            "cpu_available": system_state.get("cpu_available", 1.0),
            "time_limit": request.get("timeout", 10.0),
            "cost_limit": request.get("max_cost", 1.0),
        }

        # Extract user preferences
        user_preferences = request.get(
            "preferences",
            {
                "speed_priority": 0.5,
                "quality_priority": 0.5,
                "cost_priority": 0.5,
                "reliability_priority": 0.5,
                "model_familiarity": 0.5,
            },
        )

        # Detect task type
        task_type = self._detect_task_type(prompt)

        return RoutingState(
            task_complexity=task_complexity,
            context_type=context_type,
            provider_availability=provider_availability,
            historical_performance=historical_performance,
            resource_constraints=resource_constraints,
            user_preferences=user_preferences,
            task_type=task_type,
            prompt_length=len(prompt),
            estimated_tokens=len(prompt) // 4,  # Rough estimate
            priority_level=request.get("priority", 0.5),
        )

    def _estimate_complexity(self, prompt: str) -> float:
        """Estimate task complexity from prompt.

        Args:
            prompt: User prompt

        Returns:
            Complexity score (0.0 to 1.0)
        """
        # Simple heuristic based on prompt characteristics
        complexity = 0.0

        # Length factor
        if len(prompt) > 1000:
            complexity += 0.3
        elif len(prompt) > 500:
            complexity += 0.2
        elif len(prompt) > 100:
            complexity += 0.1

        # Keyword indicators
        complex_keywords = [
            "architecture",
            "optimize",
            "refactor",
            "analyze",
            "design",
            "implement",
            "integrate",
            "scale",
            "performance",
            "security",
        ]

        for keyword in complex_keywords:
            if keyword.lower() in prompt.lower():
                complexity += 0.1

        # Code presence
        if "```" in prompt or "def " in prompt or "class " in prompt:
            complexity += 0.2

        return min(complexity, 1.0)

    def _detect_context_type(self, prompt: str, context: Dict[str, Any]) -> str:
        """Detect context type from prompt and context.

        Args:
            prompt: User prompt
            context: Additional context

        Returns:
            Context type string
        """
        # Check explicit context
        if "language" in context:
            lang = context["language"].lower()
            for ctx_type in ContextType:
                if ctx_type.value in lang:
                    return ctx_type.value

        # Detect from prompt
        prompt_lower = prompt.lower()
        language_indicators = {
            "python": ["python", "pip", "django", "flask", "pandas"],
            "javascript": ["javascript", "js", "node", "npm", "react"],
            "typescript": ["typescript", "ts", "angular", "tsx"],
            "java": ["java", "spring", "maven", "gradle"],
            "cpp": ["c++", "cpp", "cmake", "std::"],
            "go": ["golang", "go ", "goroutine"],
            "rust": ["rust", "cargo", "rustc"],
        }

        for lang, indicators in language_indicators.items():
            for indicator in indicators:
                if indicator in prompt_lower:
                    return lang

        return ContextType.GENERAL.value

    def _detect_task_type(self, prompt: str) -> str:
        """Detect task type from prompt.

        Args:
            prompt: User prompt

        Returns:
            Task type string
        """
        prompt_lower = prompt.lower()

        task_indicators = {
            TaskType.CODE_GENERATION: ["create", "generate", "write", "implement"],
            TaskType.CODE_ANALYSIS: ["analyze", "review", "examine", "assess"],
            TaskType.CODE_REVIEW: ["review", "check", "validate", "audit"],
            TaskType.DOCUMENTATION: ["document", "explain", "describe", "comment"],
            TaskType.TESTING: ["test", "unit test", "integration", "coverage"],
            TaskType.DEBUGGING: ["debug", "fix", "error", "bug", "issue"],
            TaskType.REFACTORING: ["refactor", "improve", "optimize", "clean"],
            TaskType.ARCHITECTURE: ["architecture", "design", "structure", "pattern"],
        }

        for task_type, indicators in task_indicators.items():
            for indicator in indicators:
                if indicator in prompt_lower:
                    return task_type.value

        return TaskType.UNKNOWN.value
