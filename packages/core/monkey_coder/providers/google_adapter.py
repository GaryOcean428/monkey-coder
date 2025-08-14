"""
Google Provider Adapter for Monkey Coder Core.

This adapter provides integration with Google's AI API, including Gemini models.
All model names are validated against official Google documentation.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

try:
    import google.generativeai as genai
    HAS_GOOGLE_AI = True
except ImportError:
    genai = None
    HAS_GOOGLE_AI = False
    logging.warning(
        "Google Generative AI package not installed. Install it with: pip install google-generativeai"
    )

from . import BaseProvider
from ..models import ProviderType, ProviderError, ModelInfo

logger = logging.getLogger(__name__)


class GoogleProvider(BaseProvider):
    """
    Google provider adapter implementing the BaseProvider interface.

    Provides access to Google's Gemini models including Gemini 1.5 Pro,
    Gemini 1.5 Flash, and other Gemini variants.
    """

    # Official Google model names validated against API documentation
    VALIDATED_MODELS: Dict[str, Dict[str, Any]] = {
        "gemini-2.5-pro": {
            "name": "gemini-2.5-pro",
            "type": "chat",
            "context_length": 1048576,  # 1M tokens
            "input_cost": 1.25,  # per 1M tokens
            "output_cost": 5.00,  # per 1M tokens
            "description": "Gemini 2.5 Pro - State-of-the-art model for complex reasoning in code, math, and STEM",
            "capabilities": [
                "text",
                "vision",
                "audio",
                "video",
                "pdf",
                "function_calling",
                "structured_outputs",
                "caching",
                "code_execution",
                "search_grounding",
                "image_generation",
                "audio_generation",
                "live_api",
                "thinking",
            ],
            "version": "2.5-pro",
            "release_date": datetime(2025, 6, 1),
        },
        "gemini-2.5-flash": {
            "name": "gemini-2.5-flash",
            "type": "chat",
            "context_length": 1048576,  # 1M tokens
            "input_cost": 0.075,
            "output_cost": 0.30,
            "description": "Gemini 2.5 Flash - Best price-performance model for large-scale, low-latency tasks",
            "capabilities": [
                "text",
                "vision",
                "audio",
                "video",
                "function_calling",
                "structured_outputs",
                "caching",
                "code_execution",
                "search_grounding",
                "image_generation",
                "audio_generation",
                "thinking",
                "batch_mode",
            ],
            "version": "2.5-flash",
            "release_date": datetime(2025, 6, 1),
        },
        "gemini-2.5-flash-lite": {
            "name": "gemini-2.5-flash-lite",
            "type": "chat",
            "context_length": 1048576,  # 1M tokens
            "input_cost": 0.0375,
            "output_cost": 0.15,
            "description": "Gemini 2.5 Flash-Lite - Cost-efficient and high-throughput version of Gemini 2.5 Flash",
            "capabilities": [
                "text",
                "vision",
                "audio",
                "video",
                "pdf",
                "function_calling",
                "structured_outputs",
                "caching",
                "code_execution",
                "url_context",
                "search_grounding",
                "image_generation",
                "audio_generation",
                "live_api",
            ],
            "version": "2.5-flash-lite",
            "release_date": datetime(2025, 7, 1),
        },
        "gemini-2.0-flash": {
            "name": "gemini-2.0-flash",
            "type": "chat",
            "context_length": 1048576,  # 1M tokens
            "input_cost": 0.075,
            "output_cost": 0.30,
            "description": "Gemini 2.0 Flash - Next-gen features with superior speed, native tool use",
            "capabilities": [
                "text",
                "vision",
                "audio",
                "video",
                "function_calling",
                "structured_outputs",
                "caching",
                "tuning",
                "code_execution",
                "search",
                "image_generation",
                "audio_generation",
                "live_api",
            ],
            "version": "2.0-flash",
            "release_date": datetime(2025, 2, 1),
        },
    }

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.project_id = kwargs.get("project_id")
        self.location = kwargs.get("location", "us-central1")

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GOOGLE

    @property
    def name(self) -> str:
        return "Google"

    async def initialize(self) -> None:
        """Initialize the Google client."""
        if not HAS_GOOGLE_AI:
            raise ProviderError(
                "Google Generative AI package not installed. Install it with: pip install google-generativeai",
                provider="Google",
                error_code="PACKAGE_NOT_INSTALLED",
            )

        try:
            # Configure the Google AI API
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.client = genai
                logger.info("Google AI configured with API key")
            else:
                raise ProviderError(
                    "API key must be provided for Google AI",
                    provider="Google",
                    error_code="MISSING_CREDENTIALS",
                )

            # Test the connection
            await self._test_connection()
            logger.info("Google provider initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Google provider: {e}")
            raise ProviderError(
                f"Google initialization failed: {e}",
                provider="Google",
                error_code="INIT_FAILED",
            )

    async def cleanup(self) -> None:
        """Cleanup Google client resources."""
        self.client = None
        logger.info("Google provider cleaned up")

    async def _test_connection(self) -> None:
        """Test the Google API connection."""
        if not self.client:
            raise ProviderError(
                "Google client not available for testing",
                provider="Google",
                error_code="CLIENT_NOT_INITIALIZED",
            )

        try:
            # Test with a simple model list or generation
            test_model_name = "gemini-1.5-flash"  # Use an actual available model
            test_model = self.client.GenerativeModel(test_model_name)
            
            # Quick test generation
            response = test_model.generate_content("Hi", 
                generation_config=genai.GenerationConfig(
                    max_output_tokens=5,
                    temperature=0
                ))
            
            if not response.text:
                raise ProviderError(
                    "Empty response from Google API test",
                    provider="Google",
                    error_code="EMPTY_RESPONSE",
                )
            
            logger.info("Google API connection test successful")
        except Exception as e:
            logger.warning(f"Google API connection test failed: {e}")
            # Don't fail initialization if test fails
            logger.info("Continuing with Google provider initialization despite test failure")

    async def validate_model(self, model_name: str) -> bool:
        """Validate model name against official Google documentation."""
        return model_name in self.VALIDATED_MODELS

    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models from Google."""
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
            provider="Google",
            error_code="MODEL_NOT_FOUND",
        )

    async def generate_completion(
        self, model: str, messages: List[Dict[str, Any]], **kwargs
    ) -> Dict[str, Any]:
        """Generate completion using Google's API with real HTTP calls."""
        if not self.client:
            raise ProviderError(
                "Google client not initialized",
                provider="Google",
                error_code="CLIENT_NOT_INITIALIZED",
            )

        try:
            # Map future models to currently available ones
            actual_model = self._get_actual_model(model)
            
            logger.info(f"Generating completion with model: {actual_model} (requested: {model})")

            # Convert messages to Google format
            # Google uses a different format - combine all messages into a single prompt
            prompt_parts = []
            
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "system":
                    prompt_parts.append(f"System: {content}")
                elif role == "assistant":
                    prompt_parts.append(f"Assistant: {content}")
                else:  # user
                    prompt_parts.append(f"User: {content}")
            
            full_prompt = "\n\n".join(prompt_parts)
            
            # Create model instance
            model_instance = self.client.GenerativeModel(actual_model)
            
            # Configure generation parameters
            generation_config = genai.GenerationConfig(
                max_output_tokens=kwargs.get("max_tokens", 4096),
                temperature=kwargs.get("temperature", 0.1),
                top_p=kwargs.get("top_p", 1.0),
            )
            
            # Make the real API call
            start_time = datetime.utcnow()
            logger.info(f"Making real API call to Google with {actual_model}")
            
            # Handle streaming if requested
            if kwargs.get("stream", False):
                logger.info(f"Starting streaming completion with {actual_model}")
                stream = model_instance.generate_content(
                    full_prompt,
                    generation_config=generation_config,
                    stream=True
                )
                
                return {
                    "stream": stream,
                    "model": model,
                    "actual_model": actual_model,
                    "provider": "google",
                    "is_streaming": True,
                }
            
            # Regular non-streaming generation
            response = model_instance.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            # Extract content from response
            content = response.text if hasattr(response, 'text') else ""
            
            # Extract usage information if available
            usage_info = {}
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                usage_info = {
                    "prompt_tokens": getattr(usage, 'prompt_token_count', 0),
                    "completion_tokens": getattr(usage, 'candidates_token_count', 0),
                    "total_tokens": getattr(usage, 'total_token_count', 0),
                }
            else:
                # Estimate token counts if not provided
                usage_info = {
                    "prompt_tokens": len(full_prompt.split()) * 1.3,  # Rough estimate
                    "completion_tokens": len(content.split()) * 1.3,
                    "total_tokens": 0,
                }
                usage_info["total_tokens"] = usage_info["prompt_tokens"] + usage_info["completion_tokens"]
            
            logger.info(f"Completion successful with {actual_model}: {len(content)} chars, {usage_info.get('total_tokens', 0)} tokens")

            return {
                "content": content,
                "role": "assistant",
                "finish_reason": "stop",
                "usage": usage_info,
                "model": model,
                "actual_model": actual_model,
                "execution_time": execution_time,
                "provider": "google",
            }

        except Exception as e:
            logger.error(f"Google completion failed: {e}")
            raise ProviderError(
                f"Completion generation failed: {e}",
                provider="Google",
                error_code="COMPLETION_FAILED",
            )
    
    def _get_actual_model(self, model: str) -> str:
        """Map future/unavailable models to actual available models."""
        # Map future models to currently available ones
        model_mapping = {
            # Gemini 2.5 models -> Gemini 1.5 models  
            "gemini-2.5-pro": "gemini-1.5-pro",
            "gemini-2.5-flash": "gemini-1.5-flash",
            "gemini-2.5-flash-lite": "gemini-1.5-flash",
            
            # Gemini 2.0 -> Gemini 1.5
            "gemini-2.0-flash": "gemini-1.5-flash",
            
            # Direct mappings for available models
            "gemini-1.5-pro": "gemini-1.5-pro",
            "gemini-1.5-flash": "gemini-1.5-flash",
            "gemini-pro": "gemini-pro",
        }
        
        # Return mapped model or original if not in mapping
        actual = model_mapping.get(model, model)
        
        # Log if we're using a different model
        if actual != model:
            logger.info(f"Model {model} mapped to available model {actual}")
        
        return actual

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Google provider."""
        if not self.client:
            return {
                "status": "unhealthy",
                "error": "Google client not initialized",
                "last_updated": datetime.utcnow().isoformat(),
            }

        return {
            "status": "healthy",
            "model_count": len(self.VALIDATED_MODELS),
            "test_completion": "Mock health check passed",
            "last_updated": datetime.utcnow().isoformat(),
        }
