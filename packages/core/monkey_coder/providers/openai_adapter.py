"""
OpenAI Provider Adapter for Monkey Coder Core - Complete Model Family.

This adapter provides integration with OpenAI's full API lineup, including
all reasoning models (o1, o3, o4) and the complete GPT-4.1 family.
All model names are validated against official OpenAI documentation.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

try:
    from openai import AsyncOpenAI  # type: ignore
    from openai.types.chat import ChatCompletion, ChatCompletionMessage
    from openai.types import Model
except ImportError:
    AsyncOpenAI = None
    ChatCompletion = None
    ChatCompletionMessage = None
    Model = None
    logging.warning("OpenAI package not installed. Install it with: pip install openai")

from . import BaseProvider
from ..models import ProviderType, ProviderError, ModelInfo
from ..logging_utils import monitor_api_calls

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseProvider):
    """
    OpenAI provider adapter implementing the BaseProvider interface.

    Provides access to OpenAI's complete model lineup including:
    - o1 Series: Advanced reasoning models with extended thinking
    - o3 Series: Most powerful reasoning models
    - o4 Series: Next-generation reasoning models
    - GPT-4.1 Family: Latest flagship conversational models
    - GPT-4o Series: Optimized multimodal models
    """

    # Official OpenAI model names validated against API documentation (Feb 2026)
    VALIDATED_MODELS: Dict[str, Dict[str, Any]] = {
        # === GPT-5.x Series - Latest Flagship Models ===
        "gpt-5.2": {
            "name": "gpt-5.2",
            "api_name": "gpt-5.2",
            "type": "chat",
            "context_length": 400000,
            "max_output_tokens": 128000,
            "input_cost": 1.75,
            "output_cost": 14.00,
            "description": "Best model for coding and agentic tasks across industries",
            "capabilities": [
                "advanced_reasoning", "multimodal", "function_calling", "tool_use",
                "structured_outputs", "streaming", "code_generation", "vision_understanding",
                "prompt_caching", "reasoning_tokens"
            ],
            "version": "5.2",
            "release_date": datetime(2025, 12, 1),
        },
        "gpt-5.2-codex": {
            "name": "gpt-5.2-codex",
            "api_name": "gpt-5.2-codex",
            "type": "chat",
            "context_length": 400000,
            "max_output_tokens": 128000,
            "input_cost": 1.75,
            "output_cost": 14.00,
            "description": "Agentic coding specialist with context compaction",
            "capabilities": [
                "advanced_reasoning", "code_generation", "function_calling", "tool_use",
                "structured_outputs", "streaming", "context_compaction"
            ],
            "version": "5.2-codex",
            "release_date": datetime(2025, 12, 1),
        },
        "gpt-5.2-pro": {
            "name": "gpt-5.2-pro",
            "api_name": "gpt-5.2-pro",
            "type": "reasoning",
            "context_length": 400000,
            "max_output_tokens": 128000,
            "input_cost": 21.00,
            "output_cost": 168.00,
            "description": "Smarter and more precise responses with extended compute",
            "capabilities": [
                "advanced_reasoning", "multimodal", "function_calling", "tool_use",
                "structured_outputs", "streaming", "extended_thinking"
            ],
            "version": "5.2-pro",
            "release_date": datetime(2025, 12, 1),
        },
        "gpt-5.3-codex": {
            "name": "gpt-5.3-codex",
            "api_name": "gpt-5.3-codex",
            "type": "chat",
            "context_length": 400000,
            "max_output_tokens": 128000,
            "input_cost": 2.00,
            "output_cost": 14.00,
            "description": "Latest Codex model, 25% faster than GPT-5.2-Codex",
            "capabilities": [
                "advanced_reasoning", "code_generation", "function_calling", "tool_use",
                "structured_outputs", "streaming", "context_compaction"
            ],
            "version": "5.3-codex",
            "release_date": datetime(2026, 1, 15),
        },
        "gpt-5.1": {
            "name": "gpt-5.1",
            "api_name": "gpt-5.1",
            "type": "chat",
            "context_length": 400000,
            "max_output_tokens": 128000,
            "input_cost": 1.25,
            "output_cost": 10.00,
            "description": "Flagship GPT with 400K context and advanced reasoning",
            "capabilities": [
                "advanced_reasoning", "multimodal", "function_calling", "tool_use",
                "structured_outputs", "streaming", "code_generation", "vision_understanding",
                "prompt_caching"
            ],
            "version": "5.1",
            "release_date": datetime(2025, 10, 1),
        },
        "gpt-5": {
            "name": "gpt-5",
            "api_name": "gpt-5",
            "type": "chat",
            "context_length": 400000,  # 400K tokens per MODEL_MANIFEST.md
            "max_output_tokens": 128000,  # 128K tokens per MODEL_MANIFEST.md
            "input_cost": 2.50,  # per 1M tokens per MODEL_MANIFEST.md
            "output_cost": 10.00,  # per 1M tokens per MODEL_MANIFEST.md
            "description": "Advanced reasoning model with multimodal capabilities and long context reasoning",
            "capabilities": [
                "advanced_reasoning",
                "multimodal",
                "function_calling",
                "tool_use",
                "structured_outputs",
                "streaming",
                "code_generation",
                "vision_understanding",
                "enhanced_planning",
                "long_context_reasoning",
                "reasoning_tokens"
            ],
            "version": "5",
            "knowledge_cutoff": datetime(2024, 5, 31),  # May 31, 2024 knowledge cutoff
            "release_date": datetime(2024, 5, 31),
        },
        "gpt-5-mini-2025-08-07": {
            "name": "gpt-5-mini-2025-08-07",
            "api_name": "gpt-5-mini",
            "type": "chat",
            "context_length": 400000,  # 400K tokens per MODEL_MANIFEST.md
            "max_output_tokens": 128000,  # 128K tokens per MODEL_MANIFEST.md
            "input_cost": 0.25,  # per 1M tokens per MODEL_MANIFEST.md
            "output_cost": 1.00,  # per 1M tokens per MODEL_MANIFEST.md
            "description": "Cost-efficient reasoning model with multimodal capabilities",
            "capabilities": [
                "reasoning",
                "multimodal",
                "function_calling",
                "tool_use",
                "structured_outputs",
                "streaming",
                "code_generation",
                "vision_understanding",
                "reasoning_tokens"
            ],
            "version": "5-mini-2025-08-07",
            "release_date": datetime(2025, 8, 7),
        },
        "gpt-5-nano-2025-08-07": {
            "name": "gpt-5-nano-2025-08-07",
            "api_name": "gpt-5-nano",
            "type": "chat",
            "context_length": 400000,  # 400K tokens per MODEL_MANIFEST.md
            "max_output_tokens": 128000,  # 128K tokens per MODEL_MANIFEST.md
            "input_cost": 0.10,  # per 1M tokens per MODEL_MANIFEST.md
            "output_cost": 0.40,  # per 1M tokens per MODEL_MANIFEST.md
            "description": "Ultra-low cost model for simple text generation and high throughput",
            "capabilities": [
                "basic_reasoning",
                "text_generation",
                "function_calling",
                "streaming",
                "code_completion",
                "reasoning_tokens"
            ],
            "version": "5-nano-2025-08-07",
            "release_date": datetime(2025, 8, 7),
        },

        # === o4 Series - Next-Generation Reasoning Models ===
        "o4-mini": {
            "name": "o4-mini",
            "api_name": "o4-mini",
            "type": "reasoning",
            "context_length": 200000,  # 200K tokens
            "max_output_tokens": 16384,  # 16K tokens
            "input_cost": 1.10,  # per 1M tokens
            "output_cost": 4.40,  # per 1M tokens
            "description": "Faster, more affordable reasoning model with advanced problem-solving capabilities",
            "capabilities": [
                "text",
                "vision",
                "function_calling",
                "streaming",
                "structured_outputs",
                "reasoning",
                "step_by_step_thinking",
                "mathematical_reasoning",
            ],
            "version": "4-mini",
            "release_date": datetime(2025, 1, 15),
            "reasoning_time_limit": 30,  # seconds for reasoning
        },
        # === o3 Series - Most Powerful Reasoning Models ===
        "o3-pro": {
            "name": "o3-pro",
            "api_name": "o3-pro",
            "type": "reasoning",
            "context_length": 200000,  # 200K tokens
            "max_output_tokens": 16384,  # 16K tokens
            "input_cost": 20.00,  # per 1M tokens
            "output_cost": 80.00,  # per 1M tokens
            "description": "Version of o3 with more compute for better responses and complex reasoning",
            "capabilities": [
                "text",
                "vision",
                "function_calling",
                "streaming",
                "structured_outputs",
                "advanced_reasoning",
                "extended_thinking",
                "complex_problem_solving",
                "multi_step_reasoning",
                "scientific_reasoning",
            ],
            "version": "3-pro",
            "release_date": datetime(2025, 1, 15),
            "reasoning_time_limit": 120,  # seconds for reasoning
        },
        "o3": {
            "name": "o3",
            "api_name": "o3",
            "type": "reasoning",
            "context_length": 200000,  # 200K tokens
            "max_output_tokens": 16384,  # 16K tokens
            "input_cost": 2.00,
            "output_cost": 8.00,
            "description": "Most powerful reasoning model for complex problem-solving and analysis",
            "capabilities": [
                "text",
                "vision",
                "function_calling",
                "streaming",
                "structured_outputs",
                "reasoning",
                "logical_thinking",
                "mathematical_reasoning",
                "code_reasoning",
            ],
            "version": "3",
            "release_date": datetime(2025, 1, 15),
            "reasoning_time_limit": 60,  # seconds for reasoning
        },
        "o3-mini": {
            "name": "o3-mini",
            "api_name": "o3-mini",
            "type": "reasoning",
            "context_length": 200000,  # 200K tokens
            "max_output_tokens": 16384,  # 16K tokens
            "input_cost": 0.60,
            "output_cost": 2.40,
            "description": "Compact reasoning model optimized for speed and efficiency",
            "capabilities": [
                "text",
                "vision",
                "function_calling",
                "streaming",
                "structured_outputs",
                "reasoning",
                "quick_thinking",
                "logical_analysis",
            ],
            "version": "3-mini",
            "release_date": datetime(2025, 1, 15),
            "reasoning_time_limit": 20,  # seconds for reasoning
        },
        # === Deep Research Models ===
        "o3-deep-research": {
            "name": "o3-deep-research",
            "api_name": "o3-deep-research",
            "type": "reasoning",
            "context_length": 200000,
            "max_output_tokens": 100000,
            "input_cost": 15.00,
            "output_cost": 60.00,
            "description": "Most powerful deep research model for comprehensive analysis",
            "capabilities": [
                "reasoning",
                "deep_research",
                "web_search",
                "tools",
                "file_search",
            ],
            "version": "3-deep-research",
            "release_date": datetime(2025, 6, 1),
        },
        "o4-mini-deep-research": {
            "name": "o4-mini-deep-research",
            "api_name": "o4-mini-deep-research",
            "type": "reasoning",
            "context_length": 200000,
            "max_output_tokens": 100000,
            "input_cost": 3.00,
            "output_cost": 12.00,
            "description": "Faster, more affordable deep research model",
            "capabilities": [
                "reasoning",
                "deep_research",
                "web_search",
                "tools",
            ],
            "version": "4-mini-deep-research",
            "release_date": datetime(2025, 6, 1),
        },

        # === Open-Weight Models (Apache 2.0) ===
        "gpt-oss-120b": {
            "name": "gpt-oss-120b",
            "api_name": "gpt-oss-120b",
            "type": "chat",
            "context_length": 131072,
            "max_output_tokens": 32768,
            "input_cost": 0.0,
            "output_cost": 0.0,
            "description": "Most powerful open-weight model (Apache 2.0)",
            "capabilities": ["text", "function_calling", "structured_outputs", "streaming"],
            "version": "oss-120b",
            "release_date": datetime(2025, 9, 1),
        },
        "gpt-oss-20b": {
            "name": "gpt-oss-20b",
            "api_name": "gpt-oss-20b",
            "type": "chat",
            "context_length": 131072,
            "max_output_tokens": 32768,
            "input_cost": 0.0,
            "output_cost": 0.0,
            "description": "Medium-sized open-weight model for low latency (Apache 2.0)",
            "capabilities": ["text", "function_calling", "structured_outputs", "streaming"],
            "version": "oss-20b",
            "release_date": datetime(2025, 9, 1),
        },

        # === GPT-4.1 Family - Production Models ===
        "gpt-4.1": {
            "name": "gpt-4.1",
            "api_name": "gpt-4.1",
            "type": "chat",
            "context_length": 1048576,  # 1M tokens
            "max_output_tokens": 16384,  # 16K tokens
            "input_cost": 2.00,
            "output_cost": 8.00,
            "description": "Flagship GPT model for complex conversational tasks and analysis",
            "capabilities": [
                "text",
                "vision",
                "function_calling",
                "streaming",
                "structured_outputs",
                "multimodal",
                "advanced_conversation",
                "code_generation",
                "analysis",
            ],
            "version": "4.1",
            "release_date": datetime(2025, 1, 15),
        },
        "gpt-4.1-mini": {
            "name": "gpt-4.1-mini",
            "api_name": "gpt-4.1-mini",
            "type": "chat",
            "context_length": 1048576,  # 1M tokens
            "max_output_tokens": 16384,  # 16K tokens
            "input_cost": 0.12,
            "output_cost": 0.48,
            "description": "Efficient GPT-4.1 model optimized for fast, lightweight tasks",
            "capabilities": [
                "text",
                "vision",
                "function_calling",
                "streaming",
                "structured_outputs",
                "fast_response",
                "cost_efficient",
            ],
            "version": "4.1-mini",
            "release_date": datetime(2025, 1, 1),
        },
        "gpt-4.1-nano": {
            "name": "gpt-4.1-nano",
            "api_name": "gpt-4.1-nano",
            "type": "chat",
            "context_length": 1047576,  # ~1M tokens per MODEL_MANIFEST.md
            "max_output_tokens": 32768,  # 32K tokens per MODEL_MANIFEST.md
            "input_cost": 0.10,  # per 1M tokens per MODEL_MANIFEST.md
            "output_cost": 0.40,  # per 1M tokens per MODEL_MANIFEST.md
            "description": "Ultra-fast, cost-efficient model for quick tasks and tool orchestration",
            "capabilities": [
                "instruction_following",
                "tool_calling",
                "text",
                "vision_input",
                "fast_response",
                "cost_efficient"
            ],
            "version": "4.1-nano",
            "release_date": datetime(2024, 6, 1),
        },
    }

    # Model aliases for convenience
    MODEL_ALIASES: Dict[str, str] = {
        # GPT-5.x shortcuts
        "gpt-latest": "gpt-5.2",
        "gpt-flagship": "gpt-5.2",
        "gpt5": "gpt-5",
        "gpt-5-fast": "gpt-5-mini",
        "gpt5-mini": "gpt-5-mini",
        "gpt5-nano": "gpt-5-nano",
        # Reasoning model shortcuts
        "reasoning": "o3",
        "reasoning-pro": "o3-pro",
        "reasoning-mini": "o3-mini",
        "reasoning-fast": "o4-mini",
        # GPT-4.1 shortcuts
        "gpt-fast": "gpt-4.1-nano",
        "gpt-4.1-vision": "gpt-4.1",
        "chatgpt-4.1": "gpt-4.1",
        # Legacy shortcuts — map to current models
        "gpt-4": "gpt-4.1",
        "gpt-4-mini": "gpt-4.1-mini",
        "gpt-4o": "gpt-4.1",
        "gpt-4o-mini": "gpt-4.1-mini",
        "gpt-4-turbo": "gpt-4.1",
        "gpt-3.5-turbo": "gpt-4.1-nano",
        "o1": "o3",
        "o1-mini": "o4-mini",
        "o1-preview": "o3",
    }

    # Model categories for recommendations
    MODEL_CATEGORIES: Dict[str, Dict[str, Any]] = {
        "reasoning": {
            "models": ["o3-pro", "o3", "o4-mini", "o3-mini", "gpt-5.2-pro"],
            "description": "Advanced reasoning and problem-solving capabilities",
            "best_for": [
                "complex_analysis",
                "mathematical_reasoning",
                "scientific_problems",
                "code_reasoning",
            ],
        },
        "conversational": {
            "models": ["gpt-5.2", "gpt-5", "gpt-4.1"],
            "description": "Natural conversation and general-purpose tasks",
            "best_for": ["chat", "writing", "general_assistance", "content_creation"],
        },
        "efficient": {
            "models": ["gpt-5-nano", "gpt-5-mini", "gpt-4.1-nano", "gpt-4.1-mini", "o4-mini", "o3-mini"],
            "description": "Cost-effective models for high-volume applications",
            "best_for": [
                "automation",
                "api_integration",
                "batch_processing",
                "cost_optimization",
            ],
        },
        "coding": {
            "models": ["gpt-5.2-codex", "gpt-5.3-codex", "gpt-5.2"],
            "description": "Specialized for code generation and agentic coding",
            "best_for": [
                "code_generation",
                "code_review",
                "refactoring",
                "agentic_coding",
            ],
        },
        "multimodal": {
            "models": ["gpt-5.2", "gpt-5", "gpt-4.1"],
            "description": "Text and vision capabilities for multimodal tasks",
            "best_for": [
                "image_analysis",
                "visual_reasoning",
                "document_understanding",
                "multimodal_chat",
            ],
        },
    }

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get("base_url")
        self.organization = kwargs.get("organization")
        self.project = kwargs.get("project")
        self.default_model = kwargs.get("default_model", "gpt-5.2")
        self.reasoning_patience = kwargs.get(
            "reasoning_patience", True
        )  # Wait for reasoning models

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OPENAI

    @property
    def name(self) -> str:
        return "OpenAI"

    def resolve_model_name(self, model: str) -> str:
        """Resolve model aliases to actual model names."""
        return self.MODEL_ALIASES.get(model, model)

    def is_reasoning_model(self, model: str) -> bool:
        """Check if a model is a reasoning model (o1/o3/o4 series)."""
        resolved_model = self.resolve_model_name(model)
        model_info = self.VALIDATED_MODELS.get(resolved_model, {})
        return model_info.get("type") == "reasoning"

    async def initialize(self) -> None:
        """Initialize the OpenAI client with enhanced configuration."""
        if AsyncOpenAI is None:
            raise ProviderError(
                "OpenAI package not installed. Install it with: pip install openai",
                provider="OpenAI",
                error_code="PACKAGE_NOT_INSTALLED",
            )

        try:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                organization=self.organization,
                project=self.project,
                timeout=300.0,  # Extended timeout for reasoning models
            )

            # Test the connection
            await self._test_connection()
            logger.info(
                "OpenAI provider initialized successfully with complete model family"
            )

        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {e}")
            raise ProviderError(
                f"OpenAI initialization failed: {e}",
                provider="OpenAI",
                error_code="INIT_FAILED",
            )

    async def cleanup(self) -> None:
        """Cleanup OpenAI client resources."""
        if hasattr(self, "client") and self.client:
            await self.client.close()
            self.client = None
        logger.info("OpenAI provider cleaned up")

    @monitor_api_calls("openai_connection_test")
    async def _test_connection(self) -> None:
        """Test the OpenAI API connection with the most efficient model."""
        if not self.client:
            raise ProviderError(
                "OpenAI client not available for testing",
                provider="OpenAI",
                error_code="CLIENT_NOT_INITIALIZED",
            )

        try:
            # Test with model listing first
            models = await self.client.models.list()
            if not models.data:
                raise ProviderError(
                    "No models returned from OpenAI API",
                    provider="OpenAI",
                    error_code="NO_MODELS",
                )

            # Test with a simple completion using an actual available model
            test_model = "gpt-4.1-mini"  # Use a real, available model for testing
            actual_test_model = self._get_actual_model(test_model)
            logger.info(f"Testing OpenAI API with {actual_test_model}")

            test_response = await self.client.chat.completions.create(
                model=actual_test_model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5,
                timeout=30,
            )

            if not test_response.choices:
                raise ProviderError(
                    "Empty response from OpenAI API test",
                    provider="OpenAI",
                    error_code="EMPTY_RESPONSE",
                )

            logger.info("OpenAI API connection test successful")

        except Exception as e:
            raise ProviderError(
                f"OpenAI API connection test failed: {e}",
                provider="OpenAI",
                error_code="CONNECTION_FAILED",
            )

    async def validate_model(self, model_name: str) -> bool:
        """Validate model name against official OpenAI documentation."""
        resolved_model = self.resolve_model_name(model_name)

        # Check against our validated models list first
        if resolved_model in self.VALIDATED_MODELS:
            return True

        # If client not initialized, we can only check validated models
        if not self.client:
            logger.warning(f"Cannot validate {model_name} - client not initialized")
            return False

        # For dynamic validation, query the API
        try:
            models = await self.client.models.list()
            api_models = {model.id for model in models.data}

            if resolved_model in api_models:
                logger.info(f"Model {resolved_model} validated via OpenAI API")
                return True

            logger.warning(f"Model {resolved_model} not found in OpenAI API")
            available_models = list(self.VALIDATED_MODELS.keys())
            logger.info(f"Available models: {', '.join(available_models[:5])}...")
            return False

        except Exception as e:
            logger.error(f"Model validation failed for {model_name}: {e}")
            return False

    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models from OpenAI."""
        models = []

        # Use our validated models as the primary source
        for model_name, info in self.VALIDATED_MODELS.items():
            model_info = ModelInfo(
                name=info["name"],
                provider=self.provider_type,
                type=info["type"],
                context_length=info["context_length"],
                input_cost=info["input_cost"] / 1_000_000,  # Convert to per-token cost
                output_cost=info["output_cost"] / 1_000_000,
                capabilities=info["capabilities"],
                description=info["description"],
                version=info.get("version"),
                release_date=info.get("release_date"),
            )
            models.append(model_info)

        # Sort by capability score and release date
        models.sort(
            key=lambda m: (
                m.release_date or datetime.min,
                len(m.capabilities or []),
                -m.input_cost,
            ),
            reverse=True,
        )

        return models

    async def get_model_info(self, model_name: str) -> ModelInfo:
        """Get detailed information about a specific model."""
        resolved_model = self.resolve_model_name(model_name)

        if resolved_model in self.VALIDATED_MODELS:
            info = self.VALIDATED_MODELS[resolved_model]
            return ModelInfo(
                name=info["name"],
                provider=self.provider_type,
                type=info["type"],
                context_length=info["context_length"],
                input_cost=info["input_cost"] / 1_000_000,
                output_cost=info["output_cost"] / 1_000_000,
                capabilities=info["capabilities"],
                description=info["description"],
                version=info.get("version"),
                release_date=info.get("release_date"),
            )

        # Try to get from API for unknown models
        if not self.client:
            raise ProviderError(
                "OpenAI client not initialized",
                provider="OpenAI",
                error_code="CLIENT_NOT_INITIALIZED",
            )

        try:
            model = await self.client.models.retrieve(resolved_model)
            return ModelInfo(
                name=model.id,
                provider=self.provider_type,
                type="unknown",
                context_length=0,  # Not provided by API
                input_cost=0.0,  # Not provided by API
                output_cost=0.0,  # Not provided by API
                capabilities=[],
                description=f"OpenAI model {model.id}",
                version=None,
                release_date=None,
            )
        except Exception as e:
            raise ProviderError(
                f"Model {model_name} not found in OpenAI collection: {e}",
                provider="OpenAI",
                error_code="MODEL_NOT_FOUND",
            )

    def _prepare_completion_params(
        self, model: str, messages: List[Dict[str, Any]], **kwargs
    ) -> Dict[str, Any]:
        """Prepare parameters for completion request based on model type."""
        resolved_model = self.resolve_model_name(model)
        model_info = self.VALIDATED_MODELS.get(resolved_model, {})
        is_reasoning = self.is_reasoning_model(resolved_model)
        is_gpt5_family = resolved_model.startswith("gpt-5") or resolved_model in ["o3", "o3-pro", "o3-mini", "o4", "o4-mini"]

        # Use new GPT-5/o3/o4 API format for latest models
        if is_gpt5_family:
            # Convert messages to new input format
            input_messages = []
            for msg in messages:
                if msg.get("role") == "user":
                    input_messages.append({
                        "role": "developer",  # GPT-5 uses "developer" role
                        "content": [
                            {
                                "type": "input_text",
                                "text": msg.get("content", "")
                            }
                        ]
                    })
                elif msg.get("role") == "system":
                    # System messages can be converted to developer context
                    input_messages.append({
                        "role": "developer",
                        "content": [
                            {
                                "type": "input_text",
                                "text": f"System context: {msg.get('content', '')}"
                            }
                        ]
                    })
                else:
                    # Other roles converted to developer
                    input_messages.append({
                        "role": "developer",
                        "content": [
                            {
                                "type": "input_text",
                                "text": msg.get("content", "")
                            }
                        ]
                    })

            # New GPT-5 API parameters
            params = {
                "model": resolved_model,
                "input": input_messages,
                "text": {
                    "format": {
                        "type": "text"
                    },
                    "verbosity": kwargs.get("verbosity", "medium")
                },
                "store": kwargs.get("store", True)
            }

            # Add reasoning configuration for reasoning models
            if is_reasoning:
                params["reasoning"] = {
                    "effort": kwargs.get("reasoning_effort", "medium"),
                    "summary": kwargs.get("reasoning_summary", "auto")
                }

            # Add tools if provided
            if tools := kwargs.get("tools"):
                # Convert tools to new format
                new_tools = []
                for tool in tools:
                    if tool.get("type") == "function":
                        # Keep function tools as-is for compatibility
                        new_tools.append(tool)
                    else:
                        new_tools.append(tool)

                # Add web search capability for enhanced functionality
                if kwargs.get("enable_web_search", False):
                    new_tools.append({
                        "type": "web_search_preview",
                        "user_location": {
                            "type": "approximate",
                            "country": kwargs.get("user_country", "US"),
                            "region": kwargs.get("user_region", ""),
                            "city": kwargs.get("user_city", "")
                        },
                        "search_context_size": "high"
                    })

                params["tools"] = new_tools

            # Extended timeout for reasoning models
            if self.reasoning_patience and is_reasoning:
                reasoning_time = model_info.get("reasoning_time_limit", 60)
                params["timeout"] = reasoning_time + 30

        else:
            # Legacy chat completion format for older models
            params = {
                "model": resolved_model,
                "messages": messages,
            }

            # Reasoning models have different parameter sets
            if is_reasoning:
                params.update({
                    "max_completion_tokens": kwargs.get("max_tokens", 16384),
                })

                # Extended timeout for reasoning models
                if self.reasoning_patience:
                    reasoning_time = model_info.get("reasoning_time_limit", 60)
                    params["timeout"] = reasoning_time + 30
            else:
                # Standard chat models support full parameter set
                params.update({
                    "max_tokens": kwargs.get("max_tokens", 4096),
                    "temperature": kwargs.get("temperature", 0.1),
                    "top_p": kwargs.get("top_p", 1.0),
                    "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
                    "presence_penalty": kwargs.get("presence_penalty", 0.0),
                    "stream": kwargs.get("stream", False),
                })

                # Add tools if provided
                if tools := kwargs.get("tools"):
                    params["tools"] = tools

                # Add response format if provided
                if response_format := kwargs.get("response_format"):
                    params["response_format"] = response_format

        return params

    async def generate_completion(
        self, model: str, messages: List[Dict[str, Any]], **kwargs
    ) -> Dict[str, Any]:
        """Generate completion using OpenAI's API with model-specific handling."""
        if not self.client:
            raise ProviderError(
                "OpenAI client not initialized",
                provider="OpenAI",
                error_code="CLIENT_NOT_INITIALIZED",
            )

        try:
            # Resolve and validate model
            resolved_model = self.resolve_model_name(model)

            # For now, use standard GPT-4 models that are actually available
            # Map GPT-5 and other future models to existing ones
            actual_model = self._get_actual_model(resolved_model)

            logger.info(f"Generating completion with model: {actual_model} (requested: {resolved_model})")

            # Prepare parameters for real API call
            params = {
                "model": actual_model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 0.1),
                "top_p": kwargs.get("top_p", 1.0),
                "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
                "presence_penalty": kwargs.get("presence_penalty", 0.0),
                "stream": kwargs.get("stream", False),
            }

            # Add tools if provided
            if tools := kwargs.get("tools"):
                params["tools"] = tools

            # Add response format if provided
            if response_format := kwargs.get("response_format"):
                params["response_format"] = response_format

            # Add reasoning-specific parameters for o1 models
            is_reasoning = self.is_reasoning_model(resolved_model)
            if is_reasoning and actual_model in ["o3", "o4-mini", "o3-pro", "o3-mini"]:
                # o1 models have different parameter requirements
                params.pop("temperature", None)
                params.pop("top_p", None)
                params.pop("frequency_penalty", None)
                params.pop("presence_penalty", None)
                params["max_completion_tokens"] = params.pop("max_tokens", 4096)

            # Make the actual API call
            start_time = datetime.utcnow()

            if params.get("stream", False):
                # Handle streaming response
                logger.info(f"Starting streaming completion with {actual_model}")
                stream = await self.client.chat.completions.create(**params)

                # Return the stream object for the caller to iterate
                return {
                    "stream": stream,
                    "model": resolved_model,
                    "actual_model": actual_model,
                    "provider": "openai",
                    "is_streaming": True,
                }
            else:
                # Regular non-streaming completion
                response = await self.client.chat.completions.create(**params)

                # Extract content and usage from actual API response
                content = response.choices[0].message.content if response.choices else ""

                usage_info = {}
                if response.usage:
                    usage_info = {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }

                    # Add reasoning tokens if available (for o1 models)
                    if hasattr(response.usage, "completion_tokens_details"):
                        details = response.usage.completion_tokens_details
                        if hasattr(details, "reasoning_tokens"):
                            usage_info["reasoning_tokens"] = details.reasoning_tokens

                end_time = datetime.utcnow()
                execution_time = (end_time - start_time).total_seconds()

                logger.info(f"Completion successful with {actual_model}: {len(content)} chars, {usage_info.get('total_tokens', 0)} tokens")

                return {
                    "content": content,
                    "role": "assistant",
                    "finish_reason": response.choices[0].finish_reason if response.choices else "stop",
                    "usage": usage_info,
                    "model": resolved_model,
                    "actual_model": actual_model,
                    "execution_time": execution_time,
                    "provider": "openai",
                    "model_type": "reasoning" if is_reasoning else "chat",
                    "reasoning_time": execution_time if is_reasoning else None,
                }

        except Exception as e:
            logger.error(f"OpenAI completion failed for {model}: {e}")
            raise ProviderError(
                f"Completion generation failed: {e}",
                provider="OpenAI",
                error_code="COMPLETION_FAILED",
            )

    def _get_actual_model(self, resolved_model: str) -> str:
        """Resolve any alias / deprecated name to the canonical model ID."""
        from monkey_coder.manifest import resolve_model

        actual = resolve_model(resolved_model)

        if actual != resolved_model:
            logger.info("Model %s resolved to canonical %s", resolved_model, actual)

        return actual

    def get_recommended_model(self, use_case: str = "general") -> str:
        """Get recommended model based on use case - GPT-5 is preferred per MODEL_MANIFEST.md."""
        recommendations = {
            "general": "gpt-5",
            "reasoning": "o3-pro",  # o3-pro is best for reasoning per MODEL_MANIFEST.md
            "complex_reasoning": "o3-pro",
            "fast_reasoning": "o4-mini",
            "cost_efficient": "gpt-5-nano-2025-08-07",  # Ultra low cost
            "conversation": "gpt-5",
            "vision": "gpt-5",  # GPT-5 has multimodal capabilities
            "multimodal": "gpt-5",
            "coding": "gpt-5",
            "analysis": "gpt-5",  # GPT-5 has advanced reasoning
            "math": "o3-pro",
            "science": "o3-pro",
            "writing": "gpt-5",
            "chat": "gpt-5",
            "automation": "gpt-5-mini-2025-08-07",  # Cost-efficient for automation
            "latest": "gpt-5",
            "high_throughput": "gpt-5-nano-2025-08-07",  # Best for high throughput
        }

        return recommendations.get(use_case, "gpt-5")

    def get_models_by_category(self, category: str) -> List[str]:
        """Get models filtered by category."""
        if category in self.MODEL_CATEGORIES:
            return self.MODEL_CATEGORIES[category]["models"]
        return []

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check on OpenAI provider."""
        if not self.client:
            return {
                "status": "unhealthy",
                "error": "OpenAI client not initialized",
                "last_updated": datetime.utcnow().isoformat(),
            }

        try:
            # Test API connectivity
            models = await self.client.models.list()

            # Test a simple completion with an actual available model
            test_model = "gpt-4.1-mini"
            actual_test_model = self._get_actual_model(test_model)
            test_response = await self.client.chat.completions.create(
                model=actual_test_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
                timeout=30,
            )

            # Count models by type
            model_stats = {
                "total": len(self.VALIDATED_MODELS),
                "reasoning_models": len(
                    [
                        m
                        for m in self.VALIDATED_MODELS.values()
                        if m["type"] == "reasoning"
                    ]
                ),
                "chat_models": len(
                    [m for m in self.VALIDATED_MODELS.values() if m["type"] == "chat"]
                ),
                "multimodal_models": len(
                    [
                        m
                        for m in self.VALIDATED_MODELS.values()
                        if m["type"] == "multimodal"
                    ]
                ),
            }

            # Get latest models
            latest_models = sorted(
                self.VALIDATED_MODELS.items(),
                key=lambda x: x[1].get("release_date", datetime.min),
                reverse=True,
            )[:3]

            return {
                "status": "healthy",
                "provider": "OpenAI Complete Family",
                "api_models_available": len(models.data),
                "validated_models": model_stats,
                "latest_models": [model[0] for model in latest_models],
                "model_families": ["gpt-5", "o1", "o3", "o4", "gpt-4.1"],
                "capabilities": [
                    "reasoning",
                    "conversation",
                    "vision",
                    "function_calling",
                    "structured_outputs",
                    "streaming",
                    "multimodal",
                ],
                "test_completion": test_response.choices[0].message.content,
                "default_model": self.default_model,
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat(),
            }
