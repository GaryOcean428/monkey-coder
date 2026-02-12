"""
Anthropic Provider Adapter for Monkey Coder Core.

This adapter provides integration with Anthropic's API, including Claude models.
All model names are validated against official Anthropic documentation.
Updated to include only Claude 3.5+ models as of August 2025.

Features:
- Full streaming support with fine-grained token streaming
- Tool use and function calling
- Vision capabilities for image analysis
- Extended thinking for complex reasoning
- System prompts and XML structuring
- Multi-shot prompting support
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, AsyncIterator

try:
    from anthropic import AsyncAnthropic
    from anthropic.types import Message, TextBlock, ToolUseBlock
except ImportError:
    AsyncAnthropic = None
    Message = None
    TextBlock = None
    ToolUseBlock = None
    logging.warning(
        "Anthropic package not installed. Install it with: pip install anthropic"
    )

from . import BaseProvider
from ..models import ProviderType, ProviderError, ModelInfo
from ..logging_utils import monitor_api_calls

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseProvider):
    """
    Anthropic provider adapter implementing the BaseProvider interface.

    Provides access to Anthropic's Claude models 3.5 and above, including
    Claude Opus 4.1, Claude 4 Opus/Sonnet, Claude 3.7 Sonnet, and Claude 3.5 variants.
    """

    # Official Anthropic model names validated against API documentation (Feb 2026)
    VALIDATED_MODELS: Dict[str, Dict[str, Any]] = {
        "claude-opus-4-6": {
            "name": "claude-opus-4-6",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 5.00,  # per 1M tokens
            "output_cost": 25.00,  # per 1M tokens
            "description": "Most intelligent model with adaptive thinking, 128K output, 1M context beta",
            "capabilities": ["text", "vision", "function_calling", "extended_thinking", "computer_use", "adaptive_thinking"],
            "version": "4.6-opus",
            "release_date": datetime(2026, 1, 15),
            "max_output": 128000,
            "training_cutoff": "Jan 2025",
        },
        "claude-opus-4-5": {
            "name": "claude-opus-4-5",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 5.00,  # per 1M tokens
            "output_cost": 25.00,  # per 1M tokens
            "description": "Premium model combining maximum intelligence with practical performance",
            "capabilities": ["text", "vision", "function_calling", "extended_thinking", "effort_control", "computer_use"],
            "version": "4.5-opus",
            "release_date": datetime(2025, 11, 1),
            "max_output": 16000,
            "training_cutoff": "Jan 2025",
            "supports_effort": True,
        },
        "claude-sonnet-4-5": {
            "name": "claude-sonnet-4-5",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 3.00,  # per 1M tokens
            "output_cost": 15.00,  # per 1M tokens
            "description": "Smart model for complex agents and coding with computer use",
            "capabilities": ["text", "vision", "function_calling", "extended_thinking", "computer_use"],
            "version": "4.5-sonnet",
            "release_date": datetime(2025, 9, 29),
            "max_output": 64000,
            "training_cutoff": "Jan 2025",
        },
        "claude-haiku-4-5": {
            "name": "claude-haiku-4-5",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 1.00,  # per 1M tokens
            "output_cost": 5.00,  # per 1M tokens
            "description": "Fastest model with near-frontier intelligence",
            "capabilities": ["text", "vision", "function_calling"],
            "version": "4.5-haiku",
            "release_date": datetime(2025, 10, 1),
            "max_output": 8192,
            "training_cutoff": "Jul 2025",
        },
    }

    # Model aliases — legacy names resolve to current canonical names
    MODEL_ALIASES: Dict[str, str] = {
        "claude-opus-4-5-20251101": "claude-opus-4-5",
        "claude-sonnet-4-5-20250929": "claude-sonnet-4-5",
        "claude-haiku-4-5-20251001": "claude-haiku-4-5",
        "claude-opus-latest": "claude-opus-4-6",
        "claude-opus-4-1-20250805": "claude-opus-4-6",
        "claude-opus-4-20250514": "claude-opus-4-6",
        "claude-sonnet-4-20250514": "claude-sonnet-4-5",
        "claude-3-7-sonnet-20250219": "claude-sonnet-4-5",
        "claude-3-7-sonnet-latest": "claude-sonnet-4-5",
        "claude-3-5-sonnet-20241022": "claude-sonnet-4-5",
        "claude-3-5-sonnet-20240620": "claude-sonnet-4-5",
        "claude-3-5-sonnet-latest": "claude-sonnet-4-5",
        "claude-3-5-haiku-20241022": "claude-haiku-4-5",
        "claude-3-5-haiku-latest": "claude-haiku-4-5",
        "claude-3-opus-20240229": "claude-opus-4-6",
        "claude-3-sonnet-20240229": "claude-sonnet-4-5",
        "claude-2.1": "claude-haiku-4-5",
        "claude-4.5-sonnet-20250930": "claude-sonnet-4-5",
        "claude-4.5-haiku-20250930": "claude-haiku-4-5",
    }

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get("base_url")

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.ANTHROPIC

    @property
    def name(self) -> str:
        return "Anthropic"

    def _resolve_model_alias(self, model_name: str) -> str:
        """Resolve model alias to actual model name."""
        return self.MODEL_ALIASES.get(model_name, model_name)

    async def initialize(self) -> None:
        """Initialize the Anthropic client."""
        if AsyncAnthropic is None:
            raise ProviderError(
                "Anthropic package not installed. Install it with: pip install anthropic",
                provider="Anthropic",
                error_code="PACKAGE_NOT_INSTALLED",
            )

        try:
            self.client = AsyncAnthropic(
                api_key=self.api_key,
                base_url=self.base_url,
            )

            # Test the connection using Claude 3.5 Haiku (fastest model)
            await self._test_connection()
            logger.info("Anthropic provider initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Anthropic provider: {e}")
            raise ProviderError(
                f"Anthropic initialization failed: {e}",
                provider="Anthropic",
                error_code="INIT_FAILED",
            )

    async def cleanup(self) -> None:
        """Cleanup Anthropic client resources."""
        if self.client:
            await self.client.close()
            self.client = None
        logger.info("Anthropic provider cleaned up")

    @monitor_api_calls("anthropic_connection_test")
    async def _test_connection(self) -> None:
        """Test the Anthropic API connection using Claude 3.5 Haiku."""
        if not self.client:
            raise ProviderError(
                "Anthropic client not available for testing",
                provider="Anthropic",
                error_code="CLIENT_NOT_INITIALIZED",
            )

        try:
            # Simple API call to test connection using fastest model
            response = await self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1,
            )
            if not response:
                raise ProviderError(
                    "No response from Anthropic API",
                    provider="Anthropic",
                    error_code="NO_RESPONSE",
                )
        except Exception as e:
            raise ProviderError(
                f"Anthropic API connection test failed: {e}",
                provider="Anthropic",
                error_code="CONNECTION_FAILED",
            )

    async def validate_model(self, model_name: str) -> bool:
        """Validate model name against official Anthropic documentation."""
        resolved_model = self._resolve_model_alias(model_name)
        return resolved_model in self.VALIDATED_MODELS

    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models from Anthropic (3.5+ only)."""
        models = []

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

        return models

    async def get_model_info(self, model_name: str) -> ModelInfo:
        """Get detailed information about a specific model."""
        resolved_model = self._resolve_model_alias(model_name)

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

        raise ProviderError(
            f"Model {model_name} not found. Available models (3.5+): {list(self.VALIDATED_MODELS.keys())}",
            provider="Anthropic",
            error_code="MODEL_NOT_FOUND",
        )

    async def generate_completion(
        self, model: str, messages: List[Dict[str, Any]], **kwargs
    ) -> Dict[str, Any]:
        """Generate completion using Anthropic's API with real HTTP calls."""
        if not self.client:
            raise ProviderError(
                "Anthropic client not initialized",
                provider="Anthropic",
                error_code="CLIENT_NOT_INITIALIZED",
            )

        try:
            # Resolve alias and validate model
            resolved_model = self._resolve_model_alias(model)

            # Map future models to currently available ones
            actual_model = self._get_actual_model(resolved_model)

            logger.info(f"Generating completion with model: {actual_model} (requested: {resolved_model})")

            # Convert messages to Anthropic format if needed
            system = None
            anthropic_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system = msg["content"]
                else:
                    anthropic_messages.append(
                        {"role": msg["role"], "content": msg["content"]}
                    )

            # Get model info for max_tokens validation (use default if not found)
            model_info = self.VALIDATED_MODELS.get(resolved_model, {})
            max_output_tokens = model_info.get("max_output", 4096)
            requested_max_tokens = kwargs.get("max_tokens", 4096)

            # Ensure we don't exceed model's max output
            max_tokens = min(requested_max_tokens, max_output_tokens)

            # Prepare parameters for real API call
            params = {
                "model": actual_model,
                "messages": anthropic_messages,
                "max_tokens": max_tokens,
                "temperature": kwargs.get("temperature", 0.0),
            }

            # Add effort parameter for Claude Opus 4.5 (beta feature)
            effort = kwargs.get("effort")
            if effort and model_info.get("supports_effort"):
                valid_efforts = ["low", "medium", "high"]
                if effort in valid_efforts:
                    params["effort"] = effort
                    logger.info(f"Using effort level: {effort} for {actual_model}")
                else:
                    logger.warning(
                        f"Invalid effort '{effort}' for {actual_model}. "
                        f"Valid options: {valid_efforts}. Ignoring."
                    )

            # Add extended thinking support
            extended_thinking = kwargs.get("extended_thinking", False)
            thinking_budget = kwargs.get("thinking_budget", 10000)
            if extended_thinking:
                params["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": min(thinking_budget, 32000)  # Max 32K thinking tokens
                }
                logger.info(f"Extended thinking enabled with budget: {thinking_budget} tokens")

            # Only add optional parameters if they're provided
            if kwargs.get("top_p") is not None:
                params["top_p"] = kwargs["top_p"]

            if system:
                params["system"] = system

            # Add tool use support if tools are provided
            if kwargs.get("tools"):
                params["tools"] = self._convert_tools_to_anthropic_format(kwargs["tools"])

            # Add stop sequences if provided
            if kwargs.get("stop"):
                params["stop_sequences"] = kwargs["stop"]

            # Add metadata if provided
            if kwargs.get("metadata"):
                params["metadata"] = kwargs["metadata"]

            # Handle streaming if requested
            if kwargs.get("stream", False):
                logger.info(f"Starting streaming completion with {actual_model}")

                # Create streaming response
                client = self.client  # type: ignore[assignment]

                async def stream_generator():
                    # Guard against None at runtime (should be initialized above)
                    if not client:
                        return
                    async with client.messages.stream(**params) as s:  # type: ignore[attr-defined]
                        async for event in s:  # type: ignore[operator]
                            # Yield raw SDK events; higher layer will adapt
                            yield event

                return {
                    "stream": stream_generator(),
                    "model": resolved_model,
                    "actual_model": actual_model,
                    "provider": "anthropic",
                    "is_streaming": True,
                }

            # Make the real API call
            start_time = datetime.utcnow()
            logger.info(f"Making real API call to Anthropic with {actual_model}")
            response = await self.client.messages.create(**params)
            end_time = datetime.utcnow()

            # Calculate metrics
            execution_time = (end_time - start_time).total_seconds()

            # Extract content from actual API response
            content = ""
            thinking_content = ""

            for block in response.content:
                block_any: Any = block
                text_val = getattr(block_any, "text", None)
                if isinstance(text_val, str):
                    content += text_val
                thinking_val = getattr(block_any, "thinking", None)
                if isinstance(thinking_val, str) and thinking_val:
                    thinking_content += thinking_val

            # Build response with actual API data
            usage_info = {}
            if hasattr(response, 'usage'):
                usage_info = {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                }

            logger.info(f"Completion successful with {actual_model}: {len(content)} chars, {usage_info.get('total_tokens', 0)} tokens")

            result = {
                "content": content,
                "role": "assistant",
                "finish_reason": response.stop_reason if hasattr(response, 'stop_reason') else "stop",
                "usage": usage_info,
                "model": resolved_model,
                "actual_model": actual_model,
                "execution_time": execution_time,
                "provider": "anthropic",
            }

            # Add thinking content if available
            if thinking_content:
                result["thinking"] = thinking_content

            return result

        except Exception as e:
            logger.error(f"Anthropic completion failed: {e}")
            raise ProviderError(
                f"Completion generation failed: {e}",
                provider="Anthropic",
                error_code="COMPLETION_FAILED",
            )

    def _get_actual_model(self, resolved_model: str) -> str:
        """Resolve any alias / deprecated name to the canonical model ID."""
        from monkey_coder.manifest import resolve_model

        actual = resolve_model(resolved_model)

        if actual != resolved_model:
            logger.info("Model %s resolved to canonical %s", resolved_model, actual)

        return actual

    def _convert_tools_to_anthropic_format(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert OpenAI-style tools to Anthropic format."""
        anthropic_tools = []

        for tool in tools:
            if tool.get("type") == "function":
                function = tool.get("function", {})
                anthropic_tool = {
                    "name": function.get("name"),
                    "description": function.get("description"),
                    "input_schema": function.get("parameters", {})
                }
                anthropic_tools.append(anthropic_tool)

        return anthropic_tools

    async def generate_completion_with_vision(
        self, model: str, messages: List[Dict[str, Any]], images: List[str], **kwargs
    ) -> Dict[str, Any]:
        """Generate completion with vision capabilities for image analysis."""
        if not self.client:
            raise ProviderError(
                "Anthropic client not initialized",
                provider="Anthropic",
                error_code="CLIENT_NOT_INITIALIZED",
            )

        # Convert images to base64 and add to messages
        vision_messages = []
        for msg in messages:
            if msg["role"] == "user":
                content = [
                    {"type": "text", "text": msg["content"]}
                ]

                # Add images if this is the last user message
                if msg == messages[-1] and images:
                    for image in images:
                        content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image
                            }
                        })

                vision_messages.append({
                    "role": msg["role"],
                    "content": content
                })
            else:
                vision_messages.append(msg)

        # Call regular generate_completion with vision-formatted messages
        return await self.generate_completion(model, vision_messages, **kwargs)

    async def stream_completion(
        self, model: str, messages: List[Dict[str, Any]], **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream completion tokens as they're generated."""
        kwargs["stream"] = True
        result = await self.generate_completion(model, messages, **kwargs)

        if result.get("is_streaming"):
            stream = result.get("stream")
            if not stream:
                return
            async for event in stream:
                # Convert Anthropic streaming events to standard format
                if hasattr(event, "type"):
                    if event.type == "content_block_delta":
                        if hasattr(event.delta, "text"):
                            yield {
                                "type": "delta",
                                "content": event.delta.text,
                                "index": event.index
                            }
                    elif event.type == "message_stop":
                        yield {
                            "type": "done",
                            "usage": getattr(event, "usage", {})
                        }
        else:
            # Non-streaming fallback
            yield {
                "type": "complete",
                "content": result.get("content", ""),
                "usage": result.get("usage", {})
            }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Anthropic provider."""
        if not self.client:
            return {
                "status": "unhealthy",
                "error": "Anthropic client not initialized",
                "last_updated": datetime.utcnow().isoformat(),
            }

        try:
            # Test a simple completion using Claude 3.5 Haiku (fastest)
            test_response = await self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
            )

            content = ""
            for block in test_response.content:
                block_any: Any = block
                text_val = getattr(block_any, "text", None)
                if isinstance(text_val, str):
                    content += text_val

            return {
                "status": "healthy",
                "model_count": len(self.VALIDATED_MODELS),
                "available_models": list(self.VALIDATED_MODELS.keys()),
                "model_aliases": self.MODEL_ALIASES,
                "test_completion": content,
                "minimum_version": "3.5",
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Anthropic health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat(),
            }
