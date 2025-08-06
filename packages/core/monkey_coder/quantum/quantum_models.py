"""
Quantum Routing System Models

This module defines the data models and configurations specifically for the
quantum routing engine, including model configurations, provider settings,
and routing-specific data structures.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
import numpy as np


class ModelCapability(Enum):
    """Model capability enumeration"""
    CODE = "code"
    REASONING = "reasoning"
    ANALYSIS = "analysis"
    WRITING = "writing"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    ARCHITECTURE = "architecture"
    DEBUGGING = "debugging"
    OPTIMIZATION = "optimization"
    SPEED = "speed"
    ACCURACY = "accuracy"
    CREATIVITY = "creativity"
    STRUCTURE = "structure"
    PATTERN_RECOGNITION = "pattern_recognition"
    LOGIC = "logic"
    PROBLEM_SOLVING = "problem_solving"
    CLARITY = "clarity"
    COMPLETENESS = "completeness"
    SCALABILITY = "scalability"
    PATTERNS = "patterns"
    EDGE_CASES = "edge_cases"


@dataclass
class ModelConfig:
    """Configuration for an AI model in the quantum routing system"""
    model_id: str
    provider: str
    cost_per_1k_tokens: float
    max_tokens: int
    capabilities: List[ModelCapability]
    context_window: int
    supports_streaming: bool = True
    supports_json: bool = True
    supports_functions: bool = True
    temperature_range: tuple = (0.0, 2.0)
    version: Optional[str] = None

    def __post_init__(self):
        """Validate model configuration"""
        if self.cost_per_1k_tokens <= 0:
            raise ValueError("Cost per 1k tokens must be positive")
        if self.max_tokens <= 0:
            raise ValueError("Max tokens must be positive")
        if self.context_window <= 0:
            raise ValueError("Context window must be positive")
        if not self.capabilities:
            raise ValueError("Model must have at least one capability")


@dataclass
class ProviderConfig:
    """Configuration for an AI provider"""
    name: str
    base_url: str
    api_key_required: bool = True
    rate_limit_rpm: int = 60  # requests per minute
    rate_limit_rpd: int = 10000  # requests per day
    supports_batch: bool = False
    supports_streaming: bool = True
    default_timeout: float = 30.0
    health_check_endpoint: Optional[str] = None
    priority: int = 0  # Higher number = higher priority

    def __post_init__(self):
        """Validate provider configuration"""
        if not self.name:
            raise ValueError("Provider name cannot be empty")
        if not self.base_url:
            raise ValueError("Base URL cannot be empty")
        if self.rate_limit_rpm <= 0:
            raise ValueError("Rate limit RPM must be positive")
        if self.rate_limit_rpd <= 0:
            raise ValueError("Rate limit RPD must be positive")


# Pre-defined model configurations
QUANTUM_MODEL_REGISTRY = {
    # OpenAI Models
    "gpt-4.1": ModelConfig(
        model_id="gpt-4.1",
        provider="openai",
        cost_per_1k_tokens=0.03,
        max_tokens=8192,
        capabilities=[
            ModelCapability.CODE,
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.WRITING,
            ModelCapability.TESTING,
            ModelCapability.DOCUMENTATION,
            ModelCapability.ARCHITECTURE
        ],
        context_window=128000,
        supports_streaming=True,
        supports_json=True,
        supports_functions=True,
        temperature_range=(0.0, 2.0)
    ),
    "gpt-4.1-mini": ModelConfig(
        model_id="gpt-4.1-mini",
        provider="openai",
        cost_per_1k_tokens=0.015,
        max_tokens=16384,
        capabilities=[
            ModelCapability.CODE,
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.WRITING,
            ModelCapability.SPEED,
            ModelCapability.TESTING
        ],
        context_window=128000,
        supports_streaming=True,
        supports_json=True,
        supports_functions=True,
        temperature_range=(0.0, 2.0)
    ),
    "o1": ModelConfig(
        model_id="o1",
        provider="openai",
        cost_per_1k_tokens=0.015,
        max_tokens=32768,
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.LOGIC,
            ModelCapability.PROBLEM_SOLVING,
            ModelCapability.ACCURACY
        ],
        context_window=128000,
        supports_streaming=False,
        supports_json=True,
        supports_functions=False,
        temperature_range=(0.0, 1.0)
    ),
    "o1-mini": ModelConfig(
        model_id="o1-mini",
        provider="openai",
        cost_per_1k_tokens=0.003,
        max_tokens=65536,
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.LOGIC,
            ModelCapability.SPEED,
            ModelCapability.ACCURACY
        ],
        context_window=128000,
        supports_streaming=False,
        supports_json=True,
        supports_functions=False,
        temperature_range=(0.0, 1.0)
    ),
    "o3": ModelConfig(
        model_id="o3",
        provider="openai",
        cost_per_1k_tokens=0.03,
        max_tokens=32768,
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.LOGIC,
            ModelCapability.PROBLEM_SOLVING,
            ModelCapability.ACCURACY,
            ModelCapability.CODE
        ],
        context_window=128000,
        supports_streaming=False,
        supports_json=True,
        supports_functions=False,
        temperature_range=(0.0, 1.0)
    ),
    "o3-pro": ModelConfig(
        model_id="o3-pro",
        provider="openai",
        cost_per_1k_tokens=0.06,
        max_tokens=32768,
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.LOGIC,
            ModelCapability.PROBLEM_SOLVING,
            ModelCapability.ACCURACY,
            ModelCapability.CODE,
            ModelCapability.ARCHITECTURE
        ],
        context_window=128000,
        supports_streaming=False,
        supports_json=True,
        supports_functions=False,
        temperature_range=(0.0, 1.0)
    ),

    # Anthropic Models
    "claude-opus-4-20250514": ModelConfig(
        model_id="claude-opus-4-20250514",
        provider="anthropic",
        cost_per_1k_tokens=0.015,
        max_tokens=8192,
        capabilities=[
            ModelCapability.CODE,
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.WRITING,
            ModelCapability.TESTING,
            ModelCapability.DOCUMENTATION,
            ModelCapability.ARCHITECTURE,
            ModelCapability.DEBUGGING,
            ModelCapability.OPTIMIZATION
        ],
        context_window=200000,
        supports_streaming=True,
        supports_json=True,
        supports_functions=True,
        temperature_range=(0.0, 1.0)
    ),
    "claude-sonnet-4-20250514": ModelConfig(
        model_id="claude-sonnet-4-20250514",
        provider="anthropic",
        cost_per_1k_tokens=0.003,
        max_tokens=8192,
        capabilities=[
            ModelCapability.CODE,
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.WRITING,
            ModelCapability.TESTING,
            ModelCapability.DOCUMENTATION,
            ModelCapability.SPEED,
            ModelCapability.ACCURACY
        ],
        context_window=200000,
        supports_streaming=True,
        supports_json=True,
        supports_functions=True,
        temperature_range=(0.0, 1.0)
    ),
    "claude-3-7-sonnet-20250219": ModelConfig(
        model_id="claude-3-7-sonnet-20250219",
        provider="anthropic",
        cost_per_1k_tokens=0.003,
        max_tokens=8192,
        capabilities=[
            ModelCapability.CODE,
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.WRITING,
            ModelCapability.TESTING,
            ModelCapability.DOCUMENTATION,
            ModelCapability.SPEED
        ],
        context_window=200000,
        supports_streaming=True,
        supports_json=True,
        supports_functions=True,
        temperature_range=(0.0, 1.0)
    ),

    # Google Models
    "gemini-2.5-pro": ModelConfig(
        model_id="gemini-2.5-pro",
        provider="google",
        cost_per_1k_tokens=0.0125,
        max_tokens=8192,
        capabilities=[
            ModelCapability.CODE,
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.WRITING,
            ModelCapability.TESTING,
            ModelCapability.DOCUMENTATION,
            ModelCapability.ARCHITECTURE,
            ModelCapability.PROBLEM_SOLVING
        ],
        context_window=2097152,
        supports_streaming=True,
        supports_json=True,
        supports_functions=True,
        temperature_range=(0.0, 2.0)
    ),
    "models/gemini-2.5-flash": ModelConfig(
        model_id="models/gemini-2.5-flash",
        provider="google",
        cost_per_1k_tokens=0.000075,
        max_tokens=8192,
        capabilities=[
            ModelCapability.CODE,
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.WRITING,
            ModelCapability.SPEED,
            ModelCapability.TESTING
        ],
        context_window=1048576,
        supports_streaming=True,
        supports_json=True,
        supports_functions=True,
        temperature_range=(0.0, 2.0)
    ),
    "models/gemini-2.0-flash": ModelConfig(
        model_id="models/gemini-2.0-flash",
        provider="google",
        cost_per_1k_tokens=0.0001,
        max_tokens=8192,
        capabilities=[
            ModelCapability.CODE,
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.WRITING,
            ModelCapability.SPEED,
            ModelCapability.TESTING
        ],
        context_window=1048576,
        supports_streaming=True,
        supports_json=True,
        supports_functions=True,
        temperature_range=(0.0, 2.0)
    ),

    # Groq Models
    "llama-3.3-70b-versatile": ModelConfig(
        model_id="llama-3.3-70b-versatile",
        provider="groq",
        cost_per_1k_tokens=0.00059,
        max_tokens=8192,
        capabilities=[
            ModelCapability.CODE,
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.WRITING,
            ModelCapability.SPEED,
            ModelCapability.TESTING
        ],
        context_window=131072,
        supports_streaming=True,
        supports_json=True,
        supports_functions=False,
        temperature_range=(0.0, 2.0)
    ),
    "llama-3.1-8b-instant": ModelConfig(
        model_id="llama-3.1-8b-instant",
        provider="groq",
        cost_per_1k_tokens=0.00005,
        max_tokens=8192,
        capabilities=[
            ModelCapability.CODE,
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.WRITING,
            ModelCapability.SPEED
        ],
        context_window=131072,
        supports_streaming=True,
        supports_json=True,
        supports_functions=False,
        temperature_range=(0.0, 2.0)
    ),

    # xAI Models
    "grok-4-latest": ModelConfig(
        model_id="grok-4-latest",
        provider="xAI",
        cost_per_1k_tokens=0.005,
        max_tokens=8192,
        capabilities=[
            ModelCapability.CODE,
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.WRITING,
            ModelCapability.TESTING,
            ModelCapability.DOCUMENTATION,
            ModelCapability.REASONING
        ],
        context_window=131072,
        supports_streaming=True,
        supports_json=True,
        supports_functions=True,
        temperature_range=(0.0, 2.0)
    ),
    "grok-3": ModelConfig(
        model_id="grok-3",
        provider="xAI",
        cost_per_1k_tokens=0.003,
        max_tokens=8192,
        capabilities=[
            ModelCapability.CODE,
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.WRITING,
            ModelCapability.TESTING
        ],
        context_window=131072,
        supports_streaming=True,
        supports_json=True,
        supports_functions=True,
        temperature_range=(0.0, 2.0)
    )
}

# Provider configurations
QUANTUM_PROVIDER_REGISTRY = {
    "openai": ProviderConfig(
        name="openai",
        base_url="https://api.openai.com/v1",
        api_key_required=True,
        rate_limit_rpm=500,
        rate_limit_rpd=10000,
        supports_batch=True,
        supports_streaming=True,
        default_timeout=30.0,
        health_check_endpoint="/models",
        priority=10
    ),
    "anthropic": ProviderConfig(
        name="anthropic",
        base_url="https://api.anthropic.com",
        api_key_required=True,
        rate_limit_rpm=60,
        rate_limit_rpd=10000,
        supports_batch=False,
        supports_streaming=True,
        default_timeout=30.0,
        health_check_endpoint=None,
        priority=9
    ),
    "google": ProviderConfig(
        name="google",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        api_key_required=True,
        rate_limit_rpm=60,
        rate_limit_rpd=10000,
        supports_batch=False,
        supports_streaming=True,
        default_timeout=30.0,
        health_check_endpoint=None,
        priority=8
    ),
    "groq": ProviderConfig(
        name="groq",
        base_url="https://api.groq.com/openai/v1",
        api_key_required=True,
        rate_limit_rpm=30,
        rate_limit_rpd=14400,
        supports_batch=False,
        supports_streaming=True,
        default_timeout=30.0,
        health_check_endpoint="/models",
        priority=7
    ),
    "xAI": ProviderConfig(
        name="xAI",
        base_url="https://api.x.ai/v1",
        api_key_required=True,
        rate_limit_rpm=60,
        rate_limit_rpd=10000,
        supports_batch=False,
        supports_streaming=True,
        default_timeout=30.0,
        health_check_endpoint="/models",
        priority=6
    )
}


def get_model_config(model_id: str) -> Optional[ModelConfig]:
    """Get model configuration by model ID"""
    return QUANTUM_MODEL_REGISTRY.get(model_id)


def get_provider_config(provider_name: str) -> Optional[ProviderConfig]:
    """Get provider configuration by provider name"""
    return QUANTUM_PROVIDER_REGISTRY.get(provider_name)


def get_models_by_provider(provider_name: str) -> List[ModelConfig]:
    """Get all models for a specific provider"""
    return [
        model for model in QUANTUM_MODEL_REGISTRY.values()
        if model.provider == provider_name
    ]


def get_models_by_capability(capability: ModelCapability) -> List[ModelConfig]:
    """Get all models that have a specific capability"""
    return [
        model for model in QUANTUM_MODEL_REGISTRY.values()
        if capability in model.capabilities
    ]


def get_all_models() -> List[ModelConfig]:
    """Get all available models"""
    return list(QUANTUM_MODEL_REGISTRY.values())


def get_all_providers() -> List[ProviderConfig]:
    """Get all available providers"""
    return list(QUANTUM_PROVIDER_REGISTRY.values())
