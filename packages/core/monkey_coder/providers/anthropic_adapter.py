"""
Anthropic Provider Adapter for Monkey Coder Core.

This adapter provides integration with Anthropic's API, including Claude models.
All model names are validated against official Anthropic documentation.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None
    logging.warning("Anthropic package not installed. Install it with: pip install anthropic")

from . import BaseProvider
from ..models import ProviderType, ProviderError, ModelInfo

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseProvider):
    """
    Anthropic provider adapter implementing the BaseProvider interface.
    
    Provides access to Anthropic's Claude models including Claude 3.5 Sonnet,
    Claude 3 Opus, and other Claude variants.
    """
    
    # Official Anthropic model names validated against API documentation
    VALIDATED_MODELS: Dict[str, Dict[str, Any]] = {
        "claude-3-5-sonnet-20241022": {
            "name": "claude-3-5-sonnet-20241022",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 3.00,  # per 1M tokens
            "output_cost": 15.00,  # per 1M tokens
            "description": "Claude 3.5 Sonnet - Most capable Claude model",
            "capabilities": ["text", "vision", "function_calling"],
            "version": "3.5-sonnet",
            "release_date": datetime(2024, 10, 22),
        },
        "claude-3-opus-20240229": {
            "name": "claude-3-opus-20240229",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 15.00,
            "output_cost": 75.00,
            "description": "Claude 3 Opus - Powerful model for complex tasks",
            "capabilities": ["text", "vision", "function_calling"],
            "version": "3-opus",
            "release_date": datetime(2024, 2, 29),
        },
        "claude-3-sonnet-20240229": {
            "name": "claude-3-sonnet-20240229",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 3.00,
            "output_cost": 15.00,
            "description": "Claude 3 Sonnet - Balanced speed and intelligence",
            "capabilities": ["text", "vision", "function_calling"],
            "version": "3-sonnet",
            "release_date": datetime(2024, 2, 29),
        },
        "claude-3-haiku-20240307": {
            "name": "claude-3-haiku-20240307",
            "type": "chat",
            "context_length": 200000,
            "input_cost": 0.25,
            "output_cost": 1.25,
            "description": "Claude 3 Haiku - Fast and affordable",
            "capabilities": ["text", "vision"],
            "version": "3-haiku",
            "release_date": datetime(2024, 3, 7),
        },
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
    
    async def initialize(self) -> None:
        """Initialize the Anthropic client."""
        if AsyncAnthropic is None:
            raise ProviderError(
                "Anthropic package not installed. Install it with: pip install anthropic",
                provider="Anthropic",
                error_code="PACKAGE_NOT_INSTALLED"
            )
        
        try:
            self.client = AsyncAnthropic(
                api_key=self.api_key,
                base_url=self.base_url,
            )
            
            # Test the connection
            await self._test_connection()
            logger.info("Anthropic provider initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic provider: {e}")
            raise ProviderError(
                f"Anthropic initialization failed: {e}",
                provider="Anthropic",
                error_code="INIT_FAILED"
            )
    
    async def cleanup(self) -> None:
        """Cleanup Anthropic client resources."""
        if self.client:
            await self.client.close()
            self.client = None
        logger.info("Anthropic provider cleaned up")
    
    async def _test_connection(self) -> None:
        """Test the Anthropic API connection."""
        if not self.client:
            raise ProviderError(
                "Anthropic client not available for testing",
                provider="Anthropic",
                error_code="CLIENT_NOT_INITIALIZED"
            )
        
        try:
            # Simple API call to test connection
            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1
            )
            if not response:
                raise ProviderError(
                    "No response from Anthropic API",
                    provider="Anthropic",
                    error_code="NO_RESPONSE"
                )
        except Exception as e:
            raise ProviderError(
                f"Anthropic API connection test failed: {e}",
                provider="Anthropic", 
                error_code="CONNECTION_FAILED"
            )
    
    async def validate_model(self, model_name: str) -> bool:
        """Validate model name against official Anthropic documentation."""
        return model_name in self.VALIDATED_MODELS
    
    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models from Anthropic."""
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
            provider="Anthropic",
            error_code="MODEL_NOT_FOUND"
        )
    
    async def generate_completion(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate completion using Anthropic's API."""
        if not self.client:
            raise ProviderError(
                "Anthropic client not initialized",
                provider="Anthropic",
                error_code="CLIENT_NOT_INITIALIZED"
            )
        
        try:
            # Validate model first
            if not await self.validate_model(model):
                raise ProviderError(
                    f"Invalid model: {model}",
                    provider="Anthropic",
                    error_code="INVALID_MODEL"
                )
            
            # Convert messages to Anthropic format if needed
            system = None
            anthropic_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system = msg["content"]
                else:
                    anthropic_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Prepare parameters
            params = {
                "model": model,
                "messages": anthropic_messages,
                "max_tokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 0.1),
                "top_p": kwargs.get("top_p", 1.0),
            }
            
            if system:
                params["system"] = system
            
            # Make the API call
            start_time = datetime.utcnow()
            response = await self.client.messages.create(**params)
            end_time = datetime.utcnow()
            
            # Calculate metrics
            execution_time = (end_time - start_time).total_seconds()
            
            # Extract content
            content = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    content += block.text
            
            return {
                "content": content,
                "role": "assistant",
                "finish_reason": response.stop_reason,
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
                "model": response.model,
                "execution_time": execution_time,
                "provider": "anthropic",
            }
            
        except Exception as e:
            logger.error(f"Anthropic completion failed: {e}")
            raise ProviderError(
                f"Completion generation failed: {e}",
                provider="Anthropic",
                error_code="COMPLETION_FAILED"
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Anthropic provider."""
        if not self.client:
            return {
                "status": "unhealthy",
                "error": "Anthropic client not initialized",
                "last_updated": datetime.utcnow().isoformat(),
            }
        
        try:
            # Test a simple completion
            test_response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            content = ""
            for block in test_response.content:
                if hasattr(block, 'text'):
                    content += block.text
            
            return {
                "status": "healthy",
                "model_count": len(self.VALIDATED_MODELS),
                "test_completion": content,
                "last_updated": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Anthropic health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat(),
            }
