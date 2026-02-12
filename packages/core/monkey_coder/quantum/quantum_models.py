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

from monkey_coder.manifest import get_models, get_models_for_provider


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


# ---------------------------------------------------------------------------
# Capability mapping: manifest capability strings → ModelCapability enum
# ---------------------------------------------------------------------------
_CAP_MAP = {
    "code": ModelCapability.CODE,
    "reasoning": ModelCapability.REASONING,
    "vision": ModelCapability.ANALYSIS,
    "tools": ModelCapability.TESTING,
    "function_calling": ModelCapability.TESTING,
    "structured_outputs": ModelCapability.ACCURACY,
    "extended_thinking": ModelCapability.LOGIC,
    "adaptive_thinking": ModelCapability.PROBLEM_SOLVING,
    "deep_research": ModelCapability.ARCHITECTURE,
    "computer_use": ModelCapability.DEBUGGING,
    "prompt_caching": ModelCapability.OPTIMIZATION,
    "context_caching": ModelCapability.OPTIMIZATION,
    "audio": ModelCapability.CREATIVITY,
    "image_generation": ModelCapability.CREATIVITY,
    "live_api": ModelCapability.SPEED,
    "agentic": ModelCapability.ARCHITECTURE,
}


def _manifest_to_model_config(m: dict) -> ModelConfig:
    """Convert a raw manifest model dict into a quantum ModelConfig."""
    caps_raw = m.get("capabilities", [])
    caps = list(dict.fromkeys(  # deduplicate, preserve order
        _CAP_MAP.get(c, ModelCapability.REASONING) for c in caps_raw
    ))
    if not caps:
        caps = [ModelCapability.REASONING]

    return ModelConfig(
        model_id=m["id"],
        provider=m.get("provider", "unknown"),
        cost_per_1k_tokens=float(m.get("cost_input", 0)) / 1000.0,
        max_tokens=int(m.get("output_limit", 8192)),
        capabilities=caps,
        context_window=int(m.get("context_limit", 128000)),
        supports_streaming=bool(m.get("supports_streaming", True)),
        supports_json=True,
        supports_functions=bool(m.get("supports_tools", False)),
        temperature_range=(0.0, 2.0),
    )


def _build_quantum_model_registry() -> Dict[str, ModelConfig]:
    """Build QUANTUM_MODEL_REGISTRY dynamically from the canonical manifest."""
    registry: Dict[str, ModelConfig] = {}
    for mid, mdata in get_models().items():
        try:
            registry[mid] = _manifest_to_model_config(mdata)
        except (KeyError, ValueError):
            continue  # skip malformed entries
    return registry


# Auto-built at import time from model_manifest.json
QUANTUM_MODEL_REGISTRY: Dict[str, ModelConfig] = _build_quantum_model_registry()

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
