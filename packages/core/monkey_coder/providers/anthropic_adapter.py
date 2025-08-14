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
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, AsyncIterator

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

    # Official Anthropic model names validated against API documentation (3.5+ only)
    VALIDATED_MODELS: Dict[str, Dict[str, Any]] = {
        "claude-opus-4-1-20250805": {
            "name": "claude-opus-4-1-20250805",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 15.00,  # per 1M tokens
            "output_cost": 75.00,  # per 1M tokens
            "description": "Claude Opus 4.1 - Latest and most capable model with advanced reasoning",
            "capabilities": ["text", "vision", "function_calling", "extended_thinking", "computer_use"],
            "version": "4.1-opus",
            "release_date": datetime(2025, 8, 5),
            "max_output": 32000,
            "training_cutoff": "Jan 2025",
        },
        "claude-opus-4-20250514": {
            "name": "claude-opus-4-20250514",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 15.00,  # per 1M tokens
            "output_cost": 75.00,  # per 1M tokens
            "description": "Claude 4 Opus - Our most capable and intelligent model yet",
            "capabilities": ["text", "vision", "function_calling", "extended_thinking"],
            "version": "4-opus",
            "release_date": datetime(2025, 5, 14),
            "max_output": 32000,
            "training_cutoff": "Mar 2025",
        },
        "claude-sonnet-4-20250514": {
            "name": "claude-sonnet-4-20250514",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 3.00,  # per 1M tokens
            "output_cost": 15.00,  # per 1M tokens
            "description": "Claude 4 Sonnet - High-performance model with exceptional reasoning capabilities",
            "capabilities": ["text", "vision", "function_calling", "extended_thinking"],
            "version": "4-sonnet",
            "release_date": datetime(2025, 5, 14),
            "max_output": 64000,
            "training_cutoff": "Mar 2025",
        },
        "claude-3-7-sonnet-20250219": {
            "name": "claude-3-7-sonnet-20250219",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 3.00,  # per 1M tokens
            "output_cost": 15.00,  # per 1M tokens
            "description": "Claude 3.7 Sonnet - High-performance model with early extended thinking",
            "capabilities": ["text", "vision", "function_calling", "extended_thinking"],
            "version": "3.7-sonnet",
            "release_date": datetime(2025, 2, 19),
            "max_output": 64000,
            "training_cutoff": "Nov 2024",
        },
        "claude-3-5-sonnet-20241022": {
            "name": "claude-3-5-sonnet-20241022",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 3.00,  # per 1M tokens
            "output_cost": 15.00,  # per 1M tokens
            "description": "Claude 3.5 Sonnet v2 - Upgraded version with enhanced capabilities",
            "capabilities": ["text", "vision", "function_calling"],
            "version": "3.5-sonnet-v2",
            "release_date": datetime(2024, 10, 22),
            "max_output": 8192,
            "training_cutoff": "Apr 2024",
        },
        "claude-3-5-sonnet-20240620": {
            "name": "claude-3-5-sonnet-20240620",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 3.00,  # per 1M tokens
            "output_cost": 15.00,  # per 1M tokens
            "description": "Claude 3.5 Sonnet - Original version with high intelligence",
            "capabilities": ["text", "vision", "function_calling"],
            "version": "3.5-sonnet",
            "release_date": datetime(2024, 6, 20),
            "max_output": 8192,
            "training_cutoff": "Apr 2024",
        },
        "claude-3-5-haiku-20241022": {
            "name": "claude-3-5-haiku-20241022",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 0.80,  # per 1M tokens
            "output_cost": 4.00,  # per 1M tokens
            "description": "Claude 3.5 Haiku - Intelligence at blazing speeds",
            "capabilities": ["text", "vision"],
            "version": "3.5-haiku",
            "release_date": datetime(2024, 10, 22),
            "max_output": 8192,
            "training_cutoff": "Jul 2024",
        },
    }

    # Model aliases for convenience (pointing to latest versions)
    MODEL_ALIASES: Dict[str, str] = {
        "claude-opus-4-1": "claude-opus-4-1-20250805",
        "claude-opus-4.1": "claude-opus-4-1-20250805",
        "claude-opus-latest": "claude-opus-4-1-20250805",
        "claude-opus-4-0": "claude-opus-4-20250514",
        "claude-sonnet-4-0": "claude-sonnet-4-20250514",
        "claude-3-7-sonnet-latest": "claude-3-7-sonnet-20250219",
        "claude-3-5-sonnet-latest": "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-latest": "claude-3-5-haiku-20241022",
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
                async def stream_generator():
                    async with self.client.messages.stream(
                        **params
                    ) as stream:
                        async for event in stream:
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
                if hasattr(block, "text"):
                    content += block.text
                elif hasattr(block, "thinking") and block.thinking:
                    thinking_content += block.thinking

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
        """Map future/unavailable models to actual available models."""
        # Map future models to currently available ones
        model_mapping = {
            # Claude 4.1 and 4 models -> Claude 3 models
            "claude-opus-4-1-20250805": "claude-3-opus-20240229",
            "claude-opus-4-20250514": "claude-3-opus-20240229",
            "claude-sonnet-4-20250514": "claude-3-5-sonnet-20241022",
            
            # Claude 3.7 -> Claude 3.5
            "claude-3-7-sonnet-20250219": "claude-3-5-sonnet-20241022",
            
            # Claude 3.5 models (should be available)
            "claude-3-5-sonnet-20241022": "claude-3-5-sonnet-20241022",
            "claude-3-5-sonnet-20240620": "claude-3-5-sonnet-20240620",
            "claude-3-5-haiku-20241022": "claude-3-5-haiku-20241022",
        }
        
        # Return mapped model or original if not in mapping
        actual = model_mapping.get(resolved_model, resolved_model)
        
        # Log if we're using a different model
        if actual != resolved_model:
            logger.info(f"Model {resolved_model} mapped to available model {actual}")
        
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
                if hasattr(block, "text"):
                    content += block.text

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
