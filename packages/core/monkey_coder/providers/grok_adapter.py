"""
Grok (xAI) Provider Adapter for Monkey Coder Core.

This adapter provides integration with xAI's Grok API.
All model names are validated against official xAI documentation.
Updated for August 2025 with Grok-4 series.

Features:
- Grok-4, Grok-3 series support
- Full streaming support with fine-grained token control
- Function calling and tool use
- Advanced reasoning capabilities
- Extended context windows up to 131K tokens
- Real-time analysis and generation
"""

import os
import aiohttp
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, AsyncIterator

from . import BaseProvider
from ..models import ProviderType, ProviderError, ModelInfo

logger = logging.getLogger(__name__)


class GrokProvider(BaseProvider):
    """
    Grok (xAI) provider adapter implementing the BaseProvider interface.

    Provides access to xAI's Grok models including Grok-3 and Grok-4 variants.
    """

    # Official xAI Grok model names validated against docs (Feb 2026)
    VALIDATED_MODELS: Dict[str, Dict[str, Any]] = {
        # === Grok 4.1 (Latest) ===
        "grok-4.1-fast-reasoning": {
            "name": "grok-4.1-fast-reasoning",
            "type": "reasoning",
            "context_length": 2000000,
            "input_cost": 2.00,
            "output_cost": 10.00,
            "description": "Fast reasoning with 2M context window",
            "capabilities": ["text", "function_calling", "reasoning", "analysis", "vision"],
            "version": "4.1-fast-reasoning",
            "release_date": datetime(2025, 12, 1),
            "max_output": 16384,
        },
        "grok-4.1-fast-non-reasoning": {
            "name": "grok-4.1-fast-non-reasoning",
            "type": "chat",
            "context_length": 1000000,
            "input_cost": 0.50,
            "output_cost": 2.00,
            "description": "Instant response for standard tasks (1M context)",
            "capabilities": ["text", "function_calling", "analysis"],
            "version": "4.1-fast-non-reasoning",
            "release_date": datetime(2025, 12, 1),
            "max_output": 16384,
        },
        # === Grok 4 (Production) ===
        "grok-4": {
            "name": "grok-4",
            "type": "reasoning",
            "context_length": 131072,
            "input_cost": 10.00,
            "output_cost": 20.00,
            "description": "Reasoning model (no non-reasoning mode)",
            "capabilities": ["text", "function_calling", "reasoning", "analysis"],
            "version": "4",
            "release_date": datetime(2025, 6, 1),
            "max_output": 8192,
        },
        # === Grok 3 (Production) ===
        "grok-3": {
            "name": "grok-3",
            "type": "chat",
            "context_length": 131072,
            "input_cost": 5.00,
            "output_cost": 15.00,
            "description": "Flagship model with vision and multimodal capabilities",
            "capabilities": ["text", "function_calling", "reasoning", "vision"],
            "version": "3",
            "release_date": datetime(2025, 3, 1),
            "max_output": 8192,
        },
        "grok-3-mini": {
            "name": "grok-3-mini",
            "type": "chat",
            "context_length": 131072,
            "input_cost": 0.50,
            "output_cost": 1.50,
            "description": "Smaller, faster version of Grok 3",
            "capabilities": ["text", "function_calling"],
            "version": "3-mini",
            "release_date": datetime(2025, 3, 1),
            "max_output": 4096,
        },
        # === Specialized ===
        "grok-code-fast-1": {
            "name": "grok-code-fast-1",
            "type": "chat",
            "context_length": 256000,
            "input_cost": 0.20,
            "output_cost": 1.50,
            "description": "314B MoE reasoning model optimized for agentic coding",
            "capabilities": ["text", "function_calling", "code_generation", "reasoning"],
            "version": "code-fast-1",
            "release_date": datetime(2025, 6, 1),
            "max_output": 65536,
        },
    }

    # Model aliases — legacy names resolve to current canonical names
    MODEL_ALIASES: Dict[str, str] = {
        "grok-latest": "grok-4",
        "grok": "grok-4",
        "grok-4-latest": "grok-4",
        "grok-4.0": "grok-4",
        "grok-3.0": "grok-3",
        "grok-3-fast": "grok-3",
        "grok-3-mini-fast": "grok-3-mini",
        "grok-2": "grok-3",
    }

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get("base_url", "https://api.x.ai/v1")
        self.session = None

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GROK

    @property
    def name(self) -> str:
        return "xAI/Grok"
    
    def _resolve_model_alias(self, model_name: str) -> str:
        """Resolve model alias to actual model name."""
        return self.MODEL_ALIASES.get(model_name, model_name)

    async def initialize(self) -> None:
        """Initialize the xAI/Grok client."""
        try:
            # Create aiohttp session for async HTTP requests
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )
            
            # Test the connection
            await self._test_connection()
            logger.info("xAI/Grok provider initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize xAI/Grok provider: {e}")
            raise ProviderError(
                f"xAI/Grok initialization failed: {e}",
                provider="xAI/Grok",
                error_code="INIT_FAILED",
            )

    async def cleanup(self) -> None:
        """Cleanup xAI/Grok client resources."""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("xAI/Grok provider cleaned up")

    async def _test_connection(self) -> None:
        """Test the xAI/Grok API connection."""
        if not self.session:
            raise ProviderError(
                "xAI/Grok session not available for testing",
                provider="xAI/Grok",
                error_code="SESSION_NOT_INITIALIZED",
            )
        
        try:
            # Test with a minimal API call to list models
            async with self.session.get(f"{self.base_url}/models") as response:
                if response.status != 200:
                    text = await response.text()
                    raise ProviderError(
                        f"xAI/Grok API test failed: {text}",
                        provider="xAI/Grok",
                        error_code="CONNECTION_FAILED",
                    )
                
                data = await response.json()
                logger.info(f"xAI/Grok models available: {len(data.get('data', []))} models")
                
        except Exception as e:
            logger.warning(f"xAI/Grok API connection test failed: {e}")
            # Don't fail initialization if test fails
            logger.info("Continuing with xAI/Grok provider initialization despite test failure")

    async def validate_model(self, model_name: str) -> bool:
        """Validate model name against official xAI documentation."""
        resolved_model = self._resolve_model_alias(model_name)
        return resolved_model in self.VALIDATED_MODELS

    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models from Grok."""
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
        if model_name in self.VALIDATED_MODELS:
            info = self.VALIDATED_MODELS[model_name]
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
            f"Model {model_name} not found",
            provider="Grok",
            error_code="MODEL_NOT_FOUND",
        )

    async def generate_completion(
        self, model: str, messages: List[Dict[str, Any]], **kwargs
    ) -> Dict[str, Any]:
        """Generate completion using xAI/Grok API with real HTTP calls."""
        if not self.session:
            raise ProviderError(
                "xAI/Grok session not initialized",
                provider="xAI/Grok",
                error_code="SESSION_NOT_INITIALIZED",
            )
        
        try:
            # Resolve alias and validate model
            resolved_model = self._resolve_model_alias(model)
            
            # Map future models to currently available ones if needed
            actual_model = self._get_actual_model(resolved_model)
            
            logger.info(f"Generating completion with model: {actual_model} (requested: {resolved_model})")
            
            # Prepare request parameters (OpenAI-compatible format)
            params = {
                "model": actual_model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.95),
                "n": kwargs.get("n", 1),
                "stream": kwargs.get("stream", False),
            }
            
            # Add optional parameters
            if kwargs.get("stop"):
                params["stop"] = kwargs["stop"]
            
            if kwargs.get("presence_penalty") is not None:
                params["presence_penalty"] = kwargs["presence_penalty"]
            
            if kwargs.get("frequency_penalty") is not None:
                params["frequency_penalty"] = kwargs["frequency_penalty"]
            
            # Add tools if provided
            if kwargs.get("tools"):
                params["tools"] = kwargs["tools"]
            
            if kwargs.get("tool_choice"):
                params["tool_choice"] = kwargs["tool_choice"]
            
            # Handle streaming if requested
            if kwargs.get("stream", False):
                logger.info(f"Starting streaming completion with {actual_model}")
                
                async def stream_generator():
                    async with self.session.post(
                        f"{self.base_url}/chat/completions",
                        json=params
                    ) as response:
                        if response.status != 200:
                            text = await response.text()
                            raise ProviderError(
                                f"xAI/Grok API error: {text}",
                                provider="xAI/Grok",
                                error_code="API_ERROR",
                            )
                        
                        async for line in response.content:
                            line = line.decode('utf-8').strip()
                            if line.startswith("data: "):
                                data = line[6:]
                                if data == "[DONE]":
                                    yield {"type": "done"}
                                    break
                                
                                try:
                                    chunk = json.loads(data)
                                    if chunk.get("choices") and chunk["choices"][0].get("delta"):
                                        delta = chunk["choices"][0]["delta"]
                                        if delta.get("content"):
                                            yield {
                                                "type": "delta",
                                                "content": delta["content"],
                                                "index": 0
                                            }
                                except json.JSONDecodeError:
                                    continue
                
                return {
                    "stream": stream_generator(),
                    "model": resolved_model,
                    "actual_model": actual_model,
                    "provider": "xai/grok",
                    "is_streaming": True,
                }
            
            # Make the real API call (non-streaming)
            start_time = datetime.utcnow()
            logger.info(f"Making real API call to xAI/Grok with {actual_model}")
            
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=params
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    raise ProviderError(
                        f"xAI/Grok API error: {text}",
                        provider="xAI/Grok",
                        error_code="API_ERROR",
                    )
                
                data = await response.json()
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            # Extract response data
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            
            # Build response with actual API data
            usage_info = data.get("usage", {})
            
            logger.info(f"Completion successful with {actual_model}: {usage_info.get('total_tokens', 0)} tokens")
            
            result = {
                "content": message.get("content", ""),
                "role": message.get("role", "assistant"),
                "finish_reason": choice.get("finish_reason", "stop"),
                "usage": {
                    "prompt_tokens": usage_info.get("prompt_tokens", 0),
                    "completion_tokens": usage_info.get("completion_tokens", 0),
                    "total_tokens": usage_info.get("total_tokens", 0),
                },
                "model": resolved_model,
                "actual_model": actual_model,
                "execution_time": execution_time,
                "provider": "xai/grok",
            }
            
            # Add tool calls if present
            if message.get("tool_calls"):
                result["tool_calls"] = message["tool_calls"]
            
            return result
            
        except Exception as e:
            logger.error(f"xAI/Grok completion failed: {e}")
            raise ProviderError(
                f"Completion generation failed: {e}",
                provider="xAI/Grok",
                error_code="COMPLETION_FAILED",
            )
    
    def _get_actual_model(self, resolved_model: str) -> str:
        """Resolve any alias / deprecated name to the canonical model ID."""
        from monkey_coder.manifest import resolve_model

        actual = resolve_model(resolved_model)

        if actual != resolved_model:
            logger.info("Model %s resolved to canonical %s", resolved_model, actual)

        return actual
    
    async def stream_completion(
        self, model: str, messages: List[Dict[str, Any]], **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream completion tokens as they're generated."""
        kwargs["stream"] = True
        result = await self.generate_completion(model, messages, **kwargs)
        
        if result.get("is_streaming"):
            stream = result.get("stream")
            async for chunk in stream:
                yield chunk
        else:
            # Non-streaming fallback
            yield {
                "type": "complete",
                "content": result.get("content", ""),
                "usage": result.get("usage", {})
            }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on xAI/Grok provider."""
        if not self.session:
            return {
                "status": "unhealthy",
                "error": "xAI/Grok session not initialized",
                "last_updated": datetime.utcnow().isoformat(),
            }
        
        try:
            # Test with a simple API call
            async with self.session.get(f"{self.base_url}/models") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "healthy",
                        "model_count": len(self.VALIDATED_MODELS),
                        "available_models": list(self.VALIDATED_MODELS.keys()),
                        "model_aliases": self.MODEL_ALIASES,
                        "api_models": len(data.get("data", [])),
                        "last_updated": datetime.utcnow().isoformat(),
                    }
                else:
                    text = await response.text()
                    return {
                        "status": "unhealthy",
                        "error": f"API returned status {response.status}: {text}",
                        "last_updated": datetime.utcnow().isoformat(),
                    }
                    
        except Exception as e:
            logger.error(f"xAI/Grok health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat(),
            }
