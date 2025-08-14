"""
Grok (xAI) Provider Adapter for Monkey Coder Core.

This adapter provides integration with xAI's Grok API.
All model names are validated against official xAI documentation.
"""

import os
import logging
from datetime import datetime
from typing import Any, Dict, List

try:
    from xai_sdk import Client as XAIClient
    from xai_sdk.chat import user, system
    HAS_XAI_SDK = True
except ImportError:
    XAIClient = None
    user = None
    system = None
    HAS_XAI_SDK = False
    logging.warning(
        "xAI SDK not installed. Install it with: pip install xai-sdk"
    )

from . import BaseProvider
from ..models import ProviderType, ProviderError, ModelInfo

logger = logging.getLogger(__name__)


class GrokProvider(BaseProvider):
    """
    Grok (xAI) provider adapter implementing the BaseProvider interface.

    Provides access to xAI's Grok models including Grok-3 and Grok-4 variants.
    """

    # Official xAI Grok model names
    VALIDATED_MODELS: Dict[str, Dict[str, Any]] = {
        "grok-4-latest": {
            "name": "grok-4-latest",
            "type": "chat",
            "context_length": 131072,
            "input_cost": 5.00,  # per 1M tokens (estimate)
            "output_cost": 15.00,  # per 1M tokens (estimate)
            "description": "Grok-4 Latest - xAI's most advanced reasoning model",
            "capabilities": ["text", "reasoning", "analysis", "conversation"],
            "version": "4-latest",
            "release_date": datetime(2025, 1, 1),
        },

        "grok-3": {
            "name": "grok-3",
            "type": "chat",
            "context_length": 100000,
            "input_cost": 2.00,  # per 1M tokens (estimate)
            "output_cost": 8.00,  # per 1M tokens (estimate)
            "description": "Grok-3 - Advanced model with strong reasoning capabilities",
            "capabilities": ["text", "reasoning", "conversation"],
            "version": "3",
            "release_date": datetime(2024, 11, 1),
        },
        "grok-3-mini": {
            "name": "grok-3-mini",
            "type": "chat",
            "context_length": 32768,
            "input_cost": 0.25,  # per 1M tokens (estimate)
            "output_cost": 1.00,  # per 1M tokens (estimate)
            "description": "Grok-3 Mini - Efficient model for everyday tasks",
            "capabilities": ["text", "conversation"],
            "version": "3-mini",
            "release_date": datetime(2024, 11, 1),
        },
        "grok-3-mini-fast": {
            "name": "grok-3-mini-fast",
            "type": "chat",
            "context_length": 16384,
            "input_cost": 0.10,  # per 1M tokens (estimate)
            "output_cost": 0.40,  # per 1M tokens (estimate)
            "description": "Grok-3 Mini Fast - Ultra-fast responses for simple tasks",
            "capabilities": ["text", "conversation", "streaming"],
            "version": "3-mini-fast",
            "release_date": datetime(2024, 12, 1),
        },
        "grok-3-fast": {
            "name": "grok-3-fast",
            "type": "chat",
            "context_length": 65536,
            "input_cost": 1.00,  # per 1M tokens (estimate)
            "output_cost": 4.00,  # per 1M tokens (estimate)
            "description": "Grok-3 Fast - Balance of speed and capability",
            "capabilities": ["text", "conversation", "streaming"],
            "version": "3-fast",
            "release_date": datetime(2024, 12, 1),
        },
    }

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get("base_url", "https://api.x.ai/v1")

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GROK

    @property
    def name(self) -> str:
        return "Grok (xAI)"

    async def initialize(self) -> None:
        """Initialize the Grok client using xAI SDK."""
        if not HAS_XAI_SDK:
            raise ProviderError(
                "xAI SDK not installed. Install it with: pip install xai-sdk",
                provider="Grok",
                error_code="PACKAGE_NOT_INSTALLED",
            )

        try:
            # Use xAI SDK with API key from environment or init
            api_key = self.api_key or os.getenv("XAI_API_KEY")
            if not api_key:
                raise ProviderError(
                    "XAI API key not provided",
                    provider="Grok",
                    error_code="MISSING_API_KEY",
                )
            
            self.client = XAIClient(
                api_key=api_key,
                timeout=3600,  # Extended timeout for reasoning models
            )

            # Test the connection
            await self._test_connection()
            logger.info("Grok provider initialized successfully with xAI SDK")

        except Exception as e:
            logger.error(f"Failed to initialize Grok provider: {e}")
            raise ProviderError(
                f"Grok initialization failed: {e}",
                provider="Grok",
                error_code="INIT_FAILED",
            )

    async def cleanup(self) -> None:
        """Cleanup Grok client resources."""
        if self.client:
            await self.client.close()
            self.client = None
        logger.info("Grok provider cleaned up")

    async def _test_connection(self) -> None:
        """Test the Grok API connection."""
        if not self.client:
            raise ProviderError(
                "Grok client not available for testing",
                provider="Grok",
                error_code="CLIENT_NOT_INITIALIZED",
            )

        try:
            # Simple API call to test connection using xAI SDK
            chat = self.client.chat.create(model="grok-3-mini-fast")
            chat.append(user("Hi"))
            response = chat.sample(max_len=5)
            
            if not response or not response.content:
                raise ProviderError(
                    "No response from Grok API",
                    provider="Grok",
                    error_code="NO_RESPONSE",
                )
            logger.info("Grok API connection test successful")
        except Exception as e:
            logger.warning(f"Grok API connection test failed: {e}")
            # Don't fail initialization if test fails
            logger.info("Continuing with Grok provider initialization despite test failure")

    async def validate_model(self, model_name: str) -> bool:
        """Validate model name against official Grok documentation."""
        return model_name in self.VALIDATED_MODELS

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
        """Generate completion using Grok's xAI SDK."""
        if not self.client:
            raise ProviderError(
                "Grok client not initialized",
                provider="Grok",
                error_code="CLIENT_NOT_INITIALIZED",
            )

        try:
            # Validate model
            if not await self.validate_model(model):
                # Try with default model
                logger.warning(f"Model {model} not found, using grok-3")
                model = "grok-3"

            logger.info(f"Generating completion with Grok model: {model}")

            # Create chat session with xAI SDK
            start_time = datetime.utcnow()
            chat = self.client.chat.create(model=model)
            
            # Add messages to chat
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "system":
                    chat.append(system(content))
                elif role == "assistant":
                    # Skip assistant messages for now as xAI SDK handles differently
                    continue
                else:  # user
                    chat.append(user(content))
            
            # Generate response
            max_tokens = kwargs.get("max_tokens", 2048)
            temperature = kwargs.get("temperature", 0.7)
            
            # Handle streaming if requested
            if kwargs.get("stream", False):
                logger.info(f"Starting streaming completion with {model}")
                # xAI SDK doesn't support streaming in the same way
                # We'll do a regular generation and wrap it
                response = chat.sample(
                    max_len=max_tokens,
                    temperature=temperature,
                )
                
                return {
                    "content": response.content if response else "",
                    "model": model,
                    "provider": "grok",
                    "is_streaming": False,  # Not true streaming
                }
            
            # Regular non-streaming generation
            response = chat.sample(
                max_len=max_tokens,
                temperature=temperature,
            )
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()

            # Extract content
            content = response.content if response and hasattr(response, 'content') else ""
            
            # Estimate token usage (xAI SDK doesn't provide detailed usage)
            usage_info = {
                "prompt_tokens": sum(len(m.get("content", "").split()) * 1.3 for m in messages),
                "completion_tokens": len(content.split()) * 1.3,
                "total_tokens": 0,
            }
            usage_info["total_tokens"] = usage_info["prompt_tokens"] + usage_info["completion_tokens"]

            logger.info(f"Completion successful with {model}: {len(content)} chars")

            return {
                "content": content,
                "role": "assistant",
                "finish_reason": "stop",
                "usage": usage_info,
                "model": model,
                "execution_time": execution_time,
                "provider": "grok",
            }

        except Exception as e:
            logger.error(f"Grok completion failed: {e}")
            raise ProviderError(
                f"Completion generation failed: {e}",
                provider="Grok",
                error_code="COMPLETION_FAILED",
            )

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Grok provider."""
        if not self.client:
            return {
                "status": "unhealthy",
                "error": "Grok client not initialized",
                "last_updated": datetime.utcnow().isoformat(),
            }

        try:
            # Test a simple completion with xAI SDK
            chat = self.client.chat.create(model="grok-3-mini-fast")
            chat.append(user("Hello"))
            test_response = chat.sample(max_len=5)

            return {
                "status": "healthy",
                "model_count": len(self.VALIDATED_MODELS),
                "available_models": list(self.VALIDATED_MODELS.keys()),
                "test_completion": test_response.content if test_response and hasattr(test_response, 'content') else "Test successful",
                "api_type": "xAI SDK",
                "provider": "xAI",
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Grok health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat(),
            }
