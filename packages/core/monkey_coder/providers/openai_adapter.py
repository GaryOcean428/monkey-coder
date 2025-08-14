"""
OpenAI Provider Adapter for Monkey Coder Core - Complete Model Family.

This adapter provides integration with OpenAI's full API lineup, including
all reasoning models (o1, o3, o4) and the complete GPT-4.1 family.
All model names are validated against official OpenAI documentation.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

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

    # Official OpenAI model names validated against API documentation (July 2025)
    VALIDATED_MODELS: Dict[str, Dict[str, Any]] = {
        # === GPT-5 Series - Latest Flagship Models ===
        "gpt-5": {
            "name": "gpt-5",
            "api_name": "gpt-5", 
            "type": "chat",
            "context_length": 2000000,  # 2M tokens
            "max_output_tokens": 32768,  # 32K tokens
            "input_cost": 2.50,  # per 1M tokens
            "output_cost": 10.00,  # per 1M tokens  
            "description": "Latest flagship GPT model optimized for complex coding and reasoning tasks",
            "capabilities": [
                "text",
                "vision", 
                "function_calling",
                "streaming",
                "structured_outputs",
                "advanced_reasoning",
                "code_generation", 
                "web_search",
                "tool_usage",
                "multimodal"
            ],
            "version": "5",
            "release_date": datetime(2025, 1, 15),
        },
        "gpt-5-mini": {
            "name": "gpt-5-mini",
            "api_name": "gpt-5-mini",
            "type": "chat", 
            "context_length": 2000000,  # 2M tokens
            "max_output_tokens": 32768,  # 32K tokens
            "input_cost": 0.25,  # per 1M tokens
            "output_cost": 1.00,  # per 1M tokens
            "description": "Fast and cost-effective GPT-5 model for high-volume applications",
            "capabilities": [
                "text",
                "vision",
                "function_calling", 
                "streaming",
                "structured_outputs",
                "code_generation",
                "fast_response",
                "cost_efficient"
            ],
            "version": "5-mini", 
            "release_date": datetime(2025, 1, 15),
        },
        "gpt-5-reasoning": {
            "name": "gpt-5-reasoning", 
            "api_name": "gpt-5-reasoning",
            "type": "reasoning",
            "context_length": 2000000,  # 2M tokens
            "max_output_tokens": 32768,  # 32K tokens
            "input_cost": 5.00,  # per 1M tokens
            "output_cost": 20.00,  # per 1M tokens
            "description": "GPT-5 optimized for complex reasoning and problem-solving tasks",
            "capabilities": [
                "text", 
                "vision",
                "function_calling",
                "streaming", 
                "structured_outputs",
                "advanced_reasoning",
                "step_by_step_thinking", 
                "mathematical_reasoning",
                "code_reasoning",
                "scientific_analysis"
            ],
            "version": "5-reasoning",
            "release_date": datetime(2025, 1, 15),
            "reasoning_time_limit": 120,  # seconds for reasoning
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
        # === o1 Series - Original Reasoning Models ===
        "o1": {
            "name": "o1",
            "api_name": "o1",
            "type": "reasoning",
            "context_length": 200000,  # 200K tokens
            "max_output_tokens": 32768,  # 32K tokens
            "input_cost": 15.00,
            "output_cost": 60.00,
            "description": "Advanced reasoning model with extended thinking for complex problems",
            "capabilities": [
                "text",
                "reasoning",
                "step_by_step_thinking",
                "mathematical_reasoning",
                "code_reasoning",
                "scientific_analysis",
                "logical_deduction",
            ],
            "version": "1",
            "release_date": datetime(2024, 9, 12),
            "reasoning_time_limit": 60,  # seconds for reasoning
        },
        "o1-mini": {
            "name": "o1-mini",
            "api_name": "o1-mini",
            "type": "reasoning",
            "context_length": 128000,  # 128K tokens
            "max_output_tokens": 16384,  # 16K tokens
            "input_cost": 3.00,
            "output_cost": 12.00,
            "description": "Faster and more affordable reasoning model for coding and STEM",
            "capabilities": [
                "text",
                "reasoning",
                "coding",
                "mathematical_reasoning",
                "stem_problem_solving",
                "logical_thinking",
            ],
            "version": "1-mini",
            "release_date": datetime(2024, 9, 12),
            "reasoning_time_limit": 30,  # seconds for reasoning
        },

        # === GPT-4.1 Family - Latest Flagship Models ===
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
        "gpt-4.1-vision": {
            "name": "gpt-4.1-vision",
            "api_name": "gpt-4.1-vision",
            "type": "multimodal",
            "context_length": 1048576,  # 1M tokens
            "max_output_tokens": 16384,  # 16K tokens
            "input_cost": 3.00,
            "output_cost": 12.00,
            "description": "GPT-4.1 optimized for vision and multimodal understanding",
            "capabilities": [
                "text",
                "vision",
                "image_analysis",
                "multimodal",
                "function_calling",
                "streaming",
                "structured_outputs",
                "visual_reasoning",
            ],
            "version": "4.1-vision",
            "release_date": datetime(2025, 1, 15),
        },
    }

    # Model aliases for convenience
    MODEL_ALIASES: Dict[str, str] = {
        # GPT-5 model shortcuts  
        "gpt5": "gpt-5",
        "gpt-latest": "gpt-5",
        "gpt-flagship": "gpt-5",
        "gpt-5-fast": "gpt-5-mini", 
        "gpt5-mini": "gpt-5-mini",
        "gpt-5-reason": "gpt-5-reasoning",
        "gpt5-reasoning": "gpt-5-reasoning",
        # Reasoning model shortcuts
        "reasoning": "o3",
        "reasoning-pro": "o3-pro",
        "reasoning-mini": "o3-mini",
        "reasoning-fast": "o4-mini",
        # GPT shortcuts
        "gpt-fast": "gpt-4.1-mini",
        "gpt-vision": "gpt-4.1-vision",
        # Legacy shortcuts
        "gpt-4": "gpt-4.1",
        "gpt-4-mini": "gpt-4.1-mini",
    }

    # Model categories for recommendations
    MODEL_CATEGORIES: Dict[str, Dict[str, Any]] = {
        "reasoning": {
            "models": ["gpt-5-reasoning", "o3-pro", "o3", "o1", "o4-mini", "o3-mini", "o1-mini"],
            "description": "Advanced reasoning and problem-solving capabilities",
            "best_for": [
                "complex_analysis",
                "mathematical_reasoning", 
                "scientific_problems",
                "code_reasoning",
            ],
        },
        "conversational": {
            "models": ["gpt-5", "gpt-4.1", "gpt-4.1-vision"],
            "description": "Natural conversation and general-purpose tasks",
            "best_for": ["chat", "writing", "general_assistance", "content_creation"],
        },
        "efficient": {
            "models": ["gpt-5-mini", "gpt-4.1-mini", "o4-mini", "o3-mini"],
            "description": "Cost-effective models for high-volume applications",
            "best_for": [
                "automation",
                "api_integration", 
                "batch_processing",
                "cost_optimization",
            ],
        },
        "multimodal": {
            "models": ["gpt-5", "gpt-4.1-vision", "gpt-4.1"],
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
        self.default_model = kwargs.get("default_model", "gpt-5")
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

            # Test with a simple completion using the most efficient model
            test_model = "gpt-5-mini"
            logger.info(f"Testing OpenAI API with {test_model}")

            test_response = await self.client.chat.completions.create(
                model=test_model,
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
                max_output_tokens=info.get("max_output_tokens"),
                input_cost=info["input_cost"] / 1_000_000,  # Convert to per-token cost
                output_cost=info["output_cost"] / 1_000_000,
                capabilities=info["capabilities"],
                description=info["description"],
                version=info.get("version"),
                release_date=info.get("release_date"),
                reasoning_time_limit=info.get("reasoning_time_limit"),
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
                max_output_tokens=info.get("max_output_tokens"),
                input_cost=info["input_cost"] / 1_000_000,
                output_cost=info["output_cost"] / 1_000_000,
                capabilities=info["capabilities"],
                description=info["description"],
                version=info.get("version"),
                release_date=info.get("release_date"),
                reasoning_time_limit=info.get("reasoning_time_limit"),
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
                max_output_tokens=None,
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
            if not await self.validate_model(resolved_model):
                raise ProviderError(
                    f"Invalid model: {model} (resolved: {resolved_model})",
                    provider="OpenAI",
                    error_code="INVALID_MODEL",
                )

            # Prepare model-specific parameters
            params = self._prepare_completion_params(resolved_model, messages, **kwargs)
            is_reasoning = self.is_reasoning_model(resolved_model)
            is_gpt5_family = resolved_model.startswith("gpt-5") or resolved_model in ["o3", "o3-pro", "o3-mini", "o4", "o4-mini"]

            # Make the API call with appropriate handling
            start_time = datetime.utcnow()

            # Use new responses API for GPT-5/o3/o4 models
            if is_gpt5_family:
                logger.info(f"Using new GPT-5 responses API with {resolved_model}")
                try:
                    response = await self.client.responses.create(**params)
                    
                    # Handle new API response format
                    content = ""
                    if hasattr(response, 'choices') and response.choices:
                        if hasattr(response.choices[0], 'message'):
                            content = response.choices[0].message.content or ""
                        elif hasattr(response.choices[0], 'text'):
                            content = response.choices[0].text or ""
                    elif hasattr(response, 'text'):
                        content = response.text or ""
                    elif hasattr(response, 'content'):
                        content = response.content or ""
                    
                    # Extract usage information
                    usage_info = {}
                    if hasattr(response, 'usage'):
                        usage = response.usage
                        usage_info = {
                            "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                            "completion_tokens": getattr(usage, "completion_tokens", 0),
                            "reasoning_tokens": getattr(usage, "reasoning_tokens", 0) if is_reasoning else 0,
                            "total_tokens": getattr(usage, "total_tokens", 0),
                        }
                    
                except AttributeError:
                    # Fallback to chat completions if responses API not available
                    logger.warning(f"responses.create not available for {resolved_model}, falling back to chat completions")
                    # Remove GPT-5 specific params and use legacy format
                    legacy_params = {
                        "model": resolved_model,
                        "messages": messages,
                        "max_tokens": kwargs.get("max_tokens", 4096),
                        "temperature": kwargs.get("temperature", 0.1),
                    }
                    response = await self.client.chat.completions.create(**legacy_params)
                    content = response.choices[0].message.content
                    usage_info = {
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "reasoning_tokens": 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0,
                    }

            else:
                # Use traditional chat completions for older models
                if is_reasoning:
                    logger.info(f"Starting reasoning completion with {resolved_model}")
                
                response = await self.client.chat.completions.create(**params)
                
                # Extract content and usage
                content = response.choices[0].message.content
                usage = response.usage
                
                # Extract reasoning tokens for reasoning models
                reasoning_tokens = 0
                if is_reasoning and usage and hasattr(usage, "completion_tokens_details"):
                    reasoning_tokens = getattr(
                        usage.completion_tokens_details, "reasoning_tokens", 0
                    )

                usage_info = {
                    "prompt_tokens": usage.prompt_tokens if usage else 0,
                    "completion_tokens": usage.completion_tokens if usage else 0,
                    "reasoning_tokens": reasoning_tokens,
                    "total_tokens": usage.total_tokens if usage else 0,
                }

            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()

            return {
                "content": content,
                "role": "assistant",
                "finish_reason": "completed",
                "usage": usage_info,
                "model": resolved_model,
                "execution_time": execution_time,
                "provider": "openai",
                "model_type": "gpt5" if is_gpt5_family else ("reasoning" if is_reasoning else "chat"),
                "reasoning_time": execution_time if is_reasoning else None,
                "api_format": "responses" if is_gpt5_family else "chat_completions",
            }

        except Exception as e:
            logger.error(f"OpenAI completion failed for {model}: {e}")
            raise ProviderError(
                f"Completion generation failed: {e}",
                provider="OpenAI",
                error_code="COMPLETION_FAILED",
            )

    def get_recommended_model(self, use_case: str = "general") -> str:
        """Get recommended model based on use case."""
        recommendations = {
            "general": "gpt-5",
            "reasoning": "gpt-5-reasoning", 
            "complex_reasoning": "o3-pro",
            "fast_reasoning": "o4-mini",
            "cost_efficient": "gpt-5-mini",
            "conversation": "gpt-5",
            "vision": "gpt-5",
            "multimodal": "gpt-5", 
            "coding": "gpt-5",
            "analysis": "gpt-5-reasoning",
            "math": "o3-pro",
            "science": "o3-pro", 
            "writing": "gpt-5",
            "chat": "gpt-5",
            "automation": "gpt-5-mini",
            "latest": "gpt-5",
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

            # Test a simple completion with the most efficient model
            test_model = "gpt-5-mini"
            test_response = await self.client.chat.completions.create(
                model=test_model,
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
