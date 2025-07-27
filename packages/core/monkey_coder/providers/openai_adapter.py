"""
OpenAI Provider Adapter for Monkey Coder Core.

This adapter provides integration with OpenAI's API, including GPT models.
All model names are validated against official OpenAI documentation to ensure
accuracy and compliance.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from openai import AsyncOpenAI
from openai.types import Model as OpenAIModel

from . import BaseProvider
from ..models import ProviderType, ProviderError, ModelInfo

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseProvider):
    """
    OpenAI provider adapter implementing the BaseProvider interface.
    
    Provides access to OpenAI's GPT models including GPT-4, GPT-3.5-turbo,
    and o1 models. Validates all model names against the official OpenAI API.
    """
    
    # Official OpenAI model names validated against API documentation
    VALIDATED_MODELS = {
        # GPT-4 Models (current)
        "gpt-4o": {
            "name": "gpt-4o",
            "type": "chat",
            "context_length": 128000,
            "input_cost": 2.50,  # per 1M tokens
            "output_cost": 10.00,  # per 1M tokens
            "description": "GPT-4 Omni - Latest multimodal flagship model",
            "capabilities": ["text", "vision", "function_calling"],
        },
        "gpt-4o-mini": {
            "name": "gpt-4o-mini",
            "type": "chat", 
            "context_length": 128000,
            "input_cost": 0.15,
            "output_cost": 0.60,
            "description": "Affordable and intelligent small model for fast, lightweight tasks",
            "capabilities": ["text", "vision", "function_calling"],
        },
        "gpt-4-turbo": {
            "name": "gpt-4-turbo",
            "type": "chat",
            "context_length": 128000,
            "input_cost": 10.00,
            "output_cost": 30.00,
            "description": "GPT-4 Turbo with Vision",
            "capabilities": ["text", "vision", "function_calling"],
        },
        "gpt-4": {
            "name": "gpt-4",
            "type": "chat",
            "context_length": 8192,
            "input_cost": 30.00,
            "output_cost": 60.00,
            "description": "Original GPT-4 model",
            "capabilities": ["text", "function_calling"],
        },
        
        # GPT-3.5 Models
        "gpt-3.5-turbo": {
            "name": "gpt-3.5-turbo",
            "type": "chat",
            "context_length": 16385,
            "input_cost": 0.50,
            "output_cost": 1.50,
            "description": "Most capable GPT-3.5 model, optimized for chat",
            "capabilities": ["text", "function_calling"],
        },
        
        # o1 Models (reasoning)
        "o1-preview": {
            "name": "o1-preview",
            "type": "chat",
            "context_length": 128000,
            "input_cost": 15.00,
            "output_cost": 60.00,
            "description": "Reasoning model designed to solve hard problems",
            "capabilities": ["text", "reasoning"],
        },
        "o1-mini": {
            "name": "o1-mini",
            "type": "chat",
            "context_length": 128000,
            "input_cost": 3.00,
            "output_cost": 12.00,
            "description": "Faster and cheaper reasoning model",
            "capabilities": ["text", "reasoning"],
        },
    }
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get("base_url")
        self.organization = kwargs.get("organization")
        self.project = kwargs.get("project")
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OPENAI
    
    @property
    def name(self) -> str:
        return "OpenAI"
    
    async def initialize(self) -> None:
        """Initialize the OpenAI client."""
        try:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                organization=self.organization,
                project=self.project,
            )
            
            # Test the connection
            await self._test_connection()
            logger.info("OpenAI provider initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {e}")
            raise ProviderError(
                f"OpenAI initialization failed: {e}",
                provider="OpenAI",
                error_code="INIT_FAILED"
            )
    
    async def cleanup(self) -> None:
        """Cleanup OpenAI client resources."""
        if self.client:
            await self.client.close()
            self.client = None
        logger.info("OpenAI provider cleaned up")
    
    async def _test_connection(self) -> None:
        """Test the OpenAI API connection."""
        try:
            # Simple API call to test connection
            models = await self.client.models.list()
            if not models.data:
                raise ProviderError(
                    "No models returned from OpenAI API",
                    provider="OpenAI",
                    error_code="NO_MODELS"
                )
        except Exception as e:
            raise ProviderError(
                f"OpenAI API connection test failed: {e}",
                provider="OpenAI", 
                error_code="CONNECTION_FAILED"
            )
    
    async def validate_model(self, model_name: str) -> bool:
        """
        Validate model name against official OpenAI documentation.
        
        This method checks the model name against our curated list of
        officially supported OpenAI models, ensuring accuracy and compliance.
        """
        # Check against our validated models list
        if model_name in self.VALIDATED_MODELS:
            return True
        
        # For dynamic validation, query the API
        try:
            models = await self.client.models.list()
            api_models = {model.id for model in models.data}
            
            if model_name in api_models:
                logger.info(f"Model {model_name} validated via OpenAI API")
                return True
            
            logger.warning(f"Model {model_name} not found in OpenAI API")
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
            )
        
        # Try to get from API
        try:
            model = await self.client.models.retrieve(model_name)
            return ModelInfo(
                name=model.id,
                provider=self.provider_type,
                type="unknown",
                context_length=0,  # Not provided by API
                input_cost=0.0,    # Not provided by API
                output_cost=0.0,   # Not provided by API
                capabilities=[],
                description=f"OpenAI model {model.id}",
            )
        except Exception as e:
            raise ProviderError(
                f"Model {model_name} not found: {e}",
                provider="OpenAI",
                error_code="MODEL_NOT_FOUND"
            )
    
    async def generate_completion(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate completion using OpenAI's API."""
        try:
            # Validate model first
            if not await self.validate_model(model):
                raise ProviderError(
                    f"Invalid model: {model}",
                    provider="OpenAI",
                    error_code="INVALID_MODEL"
                )
            
            # Prepare parameters
            params = {
                "model": model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 0.1),
                "top_p": kwargs.get("top_p", 1.0),
                "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
                "presence_penalty": kwargs.get("presence_penalty", 0.0),
            }
            
            # Add tools if provided
            if tools := kwargs.get("tools"):
                params["tools"] = tools
            
            # Add response format if provided  
            if response_format := kwargs.get("response_format"):
                params["response_format"] = response_format
            
            # Make the API call
            start_time = datetime.utcnow()
            response = await self.client.chat.completions.create(**params)
            end_time = datetime.utcnow()
            
            # Calculate metrics
            usage = response.usage
            execution_time = (end_time - start_time).total_seconds()
            
            return {
                "content": response.choices[0].message.content,
                "role": response.choices[0].message.role,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens if usage else 0,
                    "completion_tokens": usage.completion_tokens if usage else 0,
                    "total_tokens": usage.total_tokens if usage else 0,
                },
                "model": response.model,
                "execution_time": execution_time,
                "provider": "openai",
            }
            
        except Exception as e:
            logger.error(f"OpenAI completion failed: {e}")
            raise ProviderError(
                f"Completion generation failed: {e}",
                provider="OpenAI",
                error_code="COMPLETION_FAILED"
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on OpenAI provider."""
        try:
            # Test API connectivity
            models = await self.client.models.list()
            
            # Test a simple completion
            test_response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            return {
                "status": "healthy",
                "model_count": len(models.data),
                "test_completion": test_response.choices[0].message.content,
                "last_updated": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat(),
            }
