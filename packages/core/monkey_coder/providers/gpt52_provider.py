"""
GPT-5.2 Provider Adapter for Monkey Coder Core.

This adapter provides integration with OpenAI's GPT-5.2 family, including:
- GPT-5.2: Advanced reasoning model with multimodal capabilities
- GPT-5.2 Pro: Deep reasoning for complex tasks
- GPT-5.2-Codex: Agentic coding specialist
- GPT-5.1-Codex-Max: Optimized for coding workflows

Features:
- Reasoning effort control (low, medium, high, xhigh)
- Responses API for chain-of-thought continuity
- 400K token context window
- Automatic prompt caching (90% cost reduction)
- Streaming support with reasoning tokens
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, AsyncGenerator, Optional

try:
    from openai import AsyncOpenAI
    from openai.types.chat import ChatCompletion, ChatCompletionChunk
except ImportError:
    AsyncOpenAI = None
    ChatCompletion = None
    ChatCompletionChunk = None
    logging.warning("OpenAI package not installed. Install it with: pip install openai>=2.1.0")

from . import BaseProvider
from ..models import ProviderType, ProviderError, ModelInfo
from ..logging_utils import monitor_api_calls

logger = logging.getLogger(__name__)


class GPT52Provider(BaseProvider):
    """
    GPT-5.2 provider adapter implementing the BaseProvider interface.
    
    Provides access to OpenAI's GPT-5.2 family with advanced reasoning capabilities.
    """

    # GPT-5.2 family models with validated specifications
    VALIDATED_MODELS: Dict[str, Dict[str, Any]] = {
        "gpt-5.2": {
            "name": "gpt-5.2",
            "api_name": "gpt-5.2",
            "type": "chat",
            "context_length": 400000,  # 400K tokens
            "max_output_tokens": 128000,  # 128K tokens
            "input_cost": 1.75,  # per 1M tokens
            "output_cost": 14.00,  # per 1M tokens
            "description": "Advanced reasoning model with multimodal capabilities",
            "capabilities": [
                "advanced_reasoning",
                "multimodal",
                "function_calling",
                "tool_use",
                "structured_outputs",
                "streaming",
                "code_generation",
                "reasoning_tokens",
                "prompt_caching",
            ],
            "version": "5.2",
            "knowledge_cutoff": datetime(2025, 8, 31),  # Aug 31, 2025
            "release_date": datetime(2025, 12, 1),
        },
        "gpt-5.2-pro": {
            "name": "gpt-5.2-pro",
            "api_name": "gpt-5.2-pro",
            "type": "chat",
            "context_length": 400000,
            "max_output_tokens": 128000,
            "input_cost": 21.00,  # per 1M tokens
            "output_cost": 168.00,  # per 1M tokens
            "description": "Deep reasoning for complex architectural planning",
            "capabilities": [
                "advanced_reasoning",
                "deep_thinking",
                "multimodal",
                "function_calling",
                "tool_use",
                "structured_outputs",
                "streaming",
                "code_generation",
                "reasoning_tokens",
                "prompt_caching",
            ],
            "version": "5.2-pro",
            "knowledge_cutoff": datetime(2025, 8, 31),
            "release_date": datetime(2025, 12, 1),
        },
        "gpt-5.2-codex": {
            "name": "gpt-5.2-codex",
            "api_name": "gpt-5.2-codex",
            "type": "chat",
            "context_length": 400000,
            "max_output_tokens": 128000,
            "input_cost": 2.50,  # TBD - estimated
            "output_cost": 15.00,  # TBD - estimated
            "description": "Agentic coding specialist with context compaction",
            "capabilities": [
                "advanced_reasoning",
                "agentic_coding",
                "multimodal",
                "function_calling",
                "tool_use",
                "structured_outputs",
                "streaming",
                "code_generation",
                "context_compaction",
                "reasoning_tokens",
                "prompt_caching",
            ],
            "version": "5.2-codex",
            "knowledge_cutoff": datetime(2025, 8, 31),
            "release_date": datetime(2025, 12, 1),
        },
        "gpt-5.1-codex-max": {
            "name": "gpt-5.1-codex-max",
            "api_name": "gpt-5.1-codex-max",
            "type": "chat",
            "context_length": 400000,
            "max_output_tokens": 128000,
            "input_cost": 2.25,
            "output_cost": 12.00,
            "description": "Optimized for coding workflows with Codex interface",
            "capabilities": [
                "advanced_reasoning",
                "agentic_coding",
                "multimodal",
                "function_calling",
                "tool_use",
                "structured_outputs",
                "streaming",
                "code_generation",
                "prompt_caching",
            ],
            "version": "5.1-codex-max",
            "knowledge_cutoff": datetime(2025, 8, 31),
            "release_date": datetime(2025, 10, 1),
        },
    }

    def __init__(self, api_key: str, **kwargs):
        """Initialize GPT-5.2 provider."""
        super().__init__(api_key, **kwargs)
        if AsyncOpenAI is None:
            raise ProviderError(
                "OpenAI package not installed. Install it with: pip install openai>=2.1.0"
            )
        self.client = AsyncOpenAI(api_key=api_key)
        self._use_responses_api = kwargs.get("use_responses_api", False)

    @property
    def provider_type(self) -> ProviderType:
        """Return the provider type."""
        return ProviderType.OPENAI

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "openai-gpt52"

    async def initialize(self) -> None:
        """Initialize the provider client."""
        logger.info("Initialized GPT-5.2 provider")

    async def cleanup(self) -> None:
        """Cleanup provider resources."""
        if self.client:
            await self.client.close()
            logger.info("Closed GPT-5.2 provider client")

    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of available GPT-5.2 models."""
        models = []
        for model_id, model_data in self.VALIDATED_MODELS.items():
            models.append(
                ModelInfo(
                    id=model_id,
                    name=model_data["name"],
                    provider=self.provider_type,
                    context_length=model_data["context_length"],
                    input_cost=model_data["input_cost"],
                    output_cost=model_data["output_cost"],
                    capabilities=model_data["capabilities"],
                    description=model_data["description"],
                )
            )
        return models

    @monitor_api_calls("gpt52_completion")
    async def _generate_completion_impl(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate completion using GPT-5.2.
        
        Args:
            model: Model name (already validated)
            messages: Conversation messages
            **kwargs: Additional parameters including:
                - effort: Reasoning effort level (low, medium, high, xhigh)
                - use_responses_api: Use Responses API for CoT continuity
                - max_tokens: Maximum output tokens
                - temperature: Sampling temperature
                - stream: Enable streaming
        
        Returns:
            Completion response
        """
        model_info = self.VALIDATED_MODELS.get(model, {})
        effort = kwargs.get("effort", "medium")
        use_responses_api = kwargs.get("use_responses_api", self._use_responses_api)
        stream = kwargs.get("stream", False)

        # Validate effort parameter
        valid_efforts = ["low", "medium", "high", "xhigh"]
        if effort not in valid_efforts:
            logger.warning(
                f"Invalid effort '{effort}', defaulting to 'medium'. "
                f"Valid options: {valid_efforts}"
            )
            effort = "medium"

        request_params = {
            "model": model_info.get("api_name", model),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 16000),
            "temperature": kwargs.get("temperature", 0.7),
            "stream": stream,
        }

        # Add reasoning effort control
        if use_responses_api:
            # Responses API - maintains thinking across turns
            request_params["reasoning"] = {"effort": effort}
            logger.info(f"Using Responses API with effort: {effort}")
        else:
            # Standard Chat Completions API
            request_params["reasoning_effort"] = effort
            logger.info(f"Using Chat Completions API with effort: {effort}")

        # Add function calling if provided
        if "functions" in kwargs:
            request_params["functions"] = kwargs["functions"]
        if "tools" in kwargs:
            request_params["tools"] = kwargs["tools"]

        try:
            if stream:
                return {"stream": self._stream_completion(request_params, use_responses_api)}
            else:
                if use_responses_api:
                    response = await self.client.responses.create(**request_params)
                else:
                    response = await self.client.chat.completions.create(**request_params)
                
                return self._format_response(response)

        except Exception as e:
            logger.error(f"GPT-5.2 completion error: {e}")
            raise ProviderError(f"GPT-5.2 completion failed: {str(e)}")

    async def _stream_completion(
        self,
        request_params: Dict[str, Any],
        use_responses_api: bool
    ) -> AsyncGenerator[str, None]:
        """Stream completion tokens."""
        try:
            if use_responses_api:
                async with self.client.responses.stream(**request_params) as stream:
                    async for chunk in stream:
                        if hasattr(chunk, 'reasoning_content') and chunk.reasoning_content:
                            # Optional: stream thinking process
                            yield f"[THINKING] {chunk.reasoning_content}\n"
                        if hasattr(chunk, 'content') and chunk.content:
                            yield chunk.content
            else:
                async for chunk in await self.client.chat.completions.create(**request_params):
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if delta.content:
                            yield delta.content

        except Exception as e:
            logger.error(f"GPT-5.2 streaming error: {e}")
            raise ProviderError(f"GPT-5.2 streaming failed: {str(e)}")

    def _format_response(self, response: Any) -> Dict[str, Any]:
        """Format OpenAI response to standard format."""
        if hasattr(response, 'choices') and len(response.choices) > 0:
            choice = response.choices[0]
            return {
                "content": choice.message.content if hasattr(choice.message, 'content') else "",
                "role": choice.message.role if hasattr(choice.message, 'role') else "assistant",
                "finish_reason": choice.finish_reason if hasattr(choice, 'finish_reason') else None,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else 0,
                    "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else 0,
                    "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') else 0,
                    "cached_tokens": getattr(response.usage, 'cached_tokens', 0) if hasattr(response, 'usage') else 0,
                },
                "model": response.model if hasattr(response, 'model') else None,
            }
        return {}

    async def get_model_info(self, model_name: str) -> ModelInfo:
        """Get detailed information about a specific GPT-5.2 model."""
        model_data = self.VALIDATED_MODELS.get(model_name)
        if not model_data:
            raise ProviderError(f"Model {model_name} not found in GPT-5.2 provider")

        return ModelInfo(
            id=model_name,
            name=model_data["name"],
            provider=self.provider_type,
            context_length=model_data["context_length"],
            input_cost=model_data["input_cost"],
            output_cost=model_data["output_cost"],
            capabilities=model_data["capabilities"],
            description=model_data["description"],
        )

    async def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        model: str = "gpt-5.2",
        effort: str = "medium",
        use_responses_api: bool = False,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat responses with GPT-5.2.
        
        Args:
            messages: Conversation messages
            model: Model to use (default: gpt-5.2)
            effort: Reasoning effort (low, medium, high, xhigh)
            use_responses_api: Use Responses API for CoT continuity
            **kwargs: Additional parameters
        
        Yields:
            Response chunks
        """
        # Validate and fix model name
        valid_model = self.validate_and_fix_model(model)

        request_params = {
            "model": valid_model,
            "messages": messages,
            "stream": True,
            "effort": effort,
            "use_responses_api": use_responses_api,
            **kwargs
        }

        response = await self._generate_completion_impl(**request_params)
        async for chunk in response["stream"]:
            yield chunk
