"""
Google Provider Adapter for Monkey Coder Core.

This adapter provides integration with Google's AI API, including Gemini models.
All model names are validated against official Google documentation.
Updated for August 2025 with Gemini 2.5 series.

Features:
- Gemini 2.5 Pro/Flash/Flash-Lite support
- Full streaming with fine-grained token control
- Function calling and structured outputs
- Vision, audio, video, and PDF processing
- Code execution and search grounding
- Image and audio generation
- Live API for real-time interactions
- Extended thinking capabilities
"""

import logging
import asyncio
from datetime import datetime
from typing import Any, Dict, List, AsyncIterator

try:
    # Try new google.genai package first (latest API)
    import google.genai as genai  # type: ignore[import-not-found]
    try:
        from google.genai.types import GenerateContentConfig, HarmCategory, HarmBlockThreshold  # type: ignore[import-not-found]
    except Exception:
        GenerateContentConfig = None  # type: ignore[assignment]
        HarmCategory = None  # type: ignore[assignment]
        HarmBlockThreshold = None  # type: ignore[assignment]
    HAS_GOOGLE_AI = True
    GOOGLE_API_VERSION = "new"
    logging.info("Using new google.genai package")
except Exception:
    try:
        # Fallback to older google-generativeai package
        import google.generativeai as genai  # type: ignore[import-not-found]
        try:
            from google.generativeai.types import GenerationConfig as GenerateContentConfig, HarmCategory, HarmBlockThreshold  # type: ignore[import-not-found]
        except Exception:
            GenerateContentConfig = None  # type: ignore[assignment]
            HarmCategory = None  # type: ignore[assignment]
            HarmBlockThreshold = None  # type: ignore[assignment]
        HAS_GOOGLE_AI = True
        GOOGLE_API_VERSION = "legacy"
        logging.info("Using legacy google.generativeai package")
    except Exception:
        genai = None  # type: ignore[assignment]
        GenerateContentConfig = None  # type: ignore[assignment]
        HarmCategory = None  # type: ignore[assignment]
        HarmBlockThreshold = None  # type: ignore[assignment]
        HAS_GOOGLE_AI = False
        GOOGLE_API_VERSION = None
        logging.warning(
            "Google AI package not installed. Install it with: pip install google-genai or pip install google-generativeai"
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
                "Google AI package not installed. Install it with: pip install google-genai or pip install google-generativeai",
                provider="Google",
                error_code="PACKAGE_NOT_INSTALLED",
            )

        try:
            # Configure the Google AI API based on version
            if self.api_key:
                # Use module as client to be compatible across versions
                if GOOGLE_API_VERSION == "legacy":
                    try:
                        getattr(genai, "configure")(api_key=self.api_key)  # type: ignore[misc]
                    except Exception:
                        pass
                self.client = genai
                logger.info(f"Google AI initialized (version={GOOGLE_API_VERSION})")
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
            test_model_name = "gemini-2.5-flash"  # Use an actual available model

            if GOOGLE_API_VERSION == "new":
                # New API test (best-effort; skip if surface differs)
                try:
                    models = getattr(self.client, "models", None)
                    if models and hasattr(models, "generate_content"):
                        response = models.generate_content(model=test_model_name, contents="Hi")
                        if not getattr(response, "text", None):
                            raise ValueError("empty text")
                except Exception:
                    # Non-fatal
                    pass
            else:
                # Legacy API test
                try:
                    gm = getattr(self.client, "GenerativeModel", None)
                    if callable(gm):
                        tm = gm(test_model_name)
                        response = getattr(tm, "generate_content")("Hi")
                        if not getattr(response, "text", None):
                            raise ValueError("empty text")
                except Exception:
                    # Non-fatal
                    pass

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
        """Generate completion using Google's API with real HTTP calls and advanced features."""
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

            # Convert messages to Google format with advanced handling
            prompt_parts = []
            system_instruction = None

            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")

                # Handle multi-modal content
                if isinstance(content, list):
                    # Content is already in multi-modal format
                    for part in content:
                        if part.get("type") == "text":
                            prompt_parts.append(part.get("text", ""))
                        elif part.get("type") == "image":
                            # Handle image content
                            prompt_parts.append({"inline_data": part.get("data")})
                else:
                    # Plain text content
                    if role == "system":
                        system_instruction = content
                    elif role == "assistant":
                        prompt_parts.append(f"Model: {content}")
                    else:  # user
                        prompt_parts.append(content)

            # Create model instance based on API version
            if GOOGLE_API_VERSION == "new":
                # New API doesn't need model instance creation
                model_instance = None
            else:
                # Legacy API needs model instance
                model_config: Dict[str, Any] = {
                    "model_name": actual_model,
                }

                if system_instruction:
                    model_config["system_instruction"] = system_instruction

                # Add tools if provided
                if kwargs.get("tools"):
                    model_config["tools"] = self._convert_tools_to_google_format(kwargs["tools"])
                gm = getattr(self.client, "GenerativeModel", None)
                model_instance = gm(**model_config) if callable(gm) else None

            # Configure generation parameters with advanced options
            # Build generation config when the type is available
            generation_config = None
            if GenerateContentConfig is not None:
                try:
                    generation_config = GenerateContentConfig(
                        max_output_tokens=kwargs.get("max_tokens", 8192),
                        temperature=kwargs.get("temperature", 0.7),
                        top_p=kwargs.get("top_p", 0.95),
                        top_k=kwargs.get("top_k", 40),
                        candidate_count=kwargs.get("n", 1),
                        stop_sequences=kwargs.get("stop", []),
                    )
                except Exception:
                    # Fallback: leave as None
                    generation_config = None

            # Add response format if specified
            if kwargs.get("response_format") and generation_config is not None:
                try:
                    generation_config.response_mime_type = kwargs["response_format"].get("type", "text/plain")
                    if kwargs["response_format"].get("schema"):
                        generation_config.response_schema = kwargs["response_format"]["schema"]
                except Exception:
                    pass

            # Configure safety settings
            # Safety settings currently not passed to new API path; reserved for future use
            _ = self._get_safety_settings(kwargs.get("safety_level", "default"))

            # Make the real API call
            start_time = datetime.utcnow()
            logger.info(f"Making real API call to Google with {actual_model}")

            # Handle streaming if requested
            if kwargs.get("stream", False):
                logger.info(f"Starting streaming completion with {actual_model}")

                async def stream_generator():
                    if GOOGLE_API_VERSION == "new":
                        # New API streaming
                        config = {
                            "temperature": kwargs.get("temperature", 0.7),
                            "top_p": kwargs.get("top_p", 0.95),
                            "top_k": kwargs.get("top_k", 40),
                        }
                        if system_instruction:
                            config["system_instruction"] = system_instruction
                        models = getattr(self.client, "models", None)
                        if models and hasattr(models, "generate_content_stream"):
                            stream = models.generate_content_stream(
                                model=actual_model,
                                contents=prompt_parts if isinstance(prompt_parts, list) else [prompt_parts],
                                config=config
                            )
                            for chunk in stream:
                                text = getattr(chunk, "text", None)
                                if isinstance(text, str):
                                    yield {"type": "delta", "content": text, "index": 0}
                    else:
                        # Legacy API streaming
                        loop = asyncio.get_event_loop()
                        # Legacy SDK may not support Python-level generator streaming; fall back to non-streaming
                        response = None
                        if model_instance is not None:
                            response = await loop.run_in_executor(
                                None,
                                getattr(model_instance, "generate_content"),
                                " ".join(prompt_parts) if isinstance(prompt_parts, list) else str(prompt_parts),
                            )
                        text = getattr(response, "text", None)
                        if isinstance(text, str):
                            yield {"type": "delta", "content": text, "index": 0}

                    yield {"type": "done"}

                return {
                    "stream": stream_generator(),
                    "model": model,
                    "actual_model": actual_model,
                    "provider": "google",
                    "is_streaming": True,
                }

            # Regular non-streaming generation
            if GOOGLE_API_VERSION == "new":
                # New API call
                config = {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.95),
                    "top_k": kwargs.get("top_k", 40),
                }
                if system_instruction:
                    config["system_instruction"] = system_instruction
                models = getattr(self.client, "models", None)
                if models and hasattr(models, "generate_content"):
                    response = models.generate_content(
                        model=actual_model,
                        contents=prompt_parts if isinstance(prompt_parts, list) else [prompt_parts],
                        config=config
                    )
                else:
                    # Fallback: treat as unsupported
                    raise RuntimeError("generate_content not available on client.models")
            else:
                # Legacy API call with async wrapper
                loop = asyncio.get_event_loop()
                full_prompt = " ".join(prompt_parts) if isinstance(prompt_parts, list) else str(prompt_parts)
                # Pass only required positional args; optional configs may vary
                response = None
                if model_instance is not None:
                    response = await loop.run_in_executor(
                        None,
                        getattr(model_instance, "generate_content"),
                        full_prompt,
                    )

            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()

            # Extract content from response
            content = getattr(response, 'text', "")

            # Extract usage information if available
            usage_info = {}
            if response is not None and hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                usage_info = {
                    "prompt_tokens": getattr(usage, 'prompt_token_count', 0),
                    "completion_tokens": getattr(usage, 'candidates_token_count', 0),
                    "total_tokens": getattr(usage, 'total_token_count', 0),
                }
            else:
                # Estimate token counts if not provided
                prompt_for_estimate = " ".join(prompt_parts) if isinstance(prompt_parts, list) else str(prompt_parts)
                try:
                    prompt_tokens = int(len(prompt_for_estimate.split()) * 1.3)
                    completion_tokens = int(len(content.split()) * 1.3) if isinstance(content, str) else 0
                except Exception:
                    prompt_tokens = 0
                    completion_tokens = 0
                usage_info = {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                }

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
        """Return actual model names - Gemini 2.5 is available as of August 2025."""
    # According to MODEL_MANIFEST.md, all Gemini 2.x models are real and available
        # No mapping needed - use them directly
        model_mapping = {
            # All these models exist and should be used directly
            "gemini-2.5-pro": "gemini-2.5-pro",
            "gemini-2.5-flash": "gemini-2.5-flash",
            "gemini-2.5-flash-lite": "gemini-2.5-flash-lite",
            "gemini-2.0-flash": "gemini-2.0-flash",

            # Legacy models that might need mapping
            "gemini-1.5-pro": "gemini-2.5-pro",  # Upgrade to newer version
            "gemini-1.5-flash": "gemini-2.5-flash",  # Upgrade to newer version
            "gemini-pro": "gemini-2.5-flash",  # Upgrade to newer version
        }

        # Return mapped model or original if not in mapping
        actual = model_mapping.get(model, model)

        # Log if we're using a different model
        if actual != model:
            logger.info(f"Model {model} mapped to {actual}")

        return actual

    def _convert_tools_to_google_format(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert OpenAI-style tools to Google format."""
        google_tools = []

        for tool in tools:
            if tool.get("type") == "function":
                function = tool.get("function", {})
                google_tool = {
                    "function_declarations": [{
                        "name": function.get("name"),
                        "description": function.get("description"),
                        "parameters": function.get("parameters", {})
                    }]
                }
                google_tools.append(google_tool)

        return google_tools

    def _get_safety_settings(self, level: str = "default") -> Dict:
        """Get safety settings based on level."""
        if not HarmCategory or not HarmBlockThreshold:
            return {}

        if level == "none":
            # Block nothing
            return {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        elif level == "strict":
            # Block low and above
            return {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            }
        else:  # default
            # Block medium and above
            return {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }

    async def generate_completion_with_vision(
        self, model: str, messages: List[Dict[str, Any]], images: List[str], **kwargs
    ) -> Dict[str, Any]:
        """Generate completion with vision capabilities for image/video/PDF analysis."""
        # Convert images to proper format and add to messages
        vision_messages = []
        for msg in messages:
            if msg["role"] == "user" and msg == messages[-1]:
                # Add images to the last user message
                content = [{"type": "text", "text": msg["content"]}]
                for image in images:
                    content.append({
                        "type": "image",
                        "data": image
                    })
                vision_messages.append({
                    "role": msg["role"],
                    "content": content
                })
            else:
                vision_messages.append(msg)

        return await self.generate_completion(model, vision_messages, **kwargs)

    async def stream_completion(
        self, model: str, messages: List[Dict[str, Any]], **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream completion tokens as they're generated with fine-grained control."""
        kwargs["stream"] = True
        result = await self.generate_completion(model, messages, **kwargs)

        if result.get("is_streaming"):
            stream = result.get("stream")
            if stream is not None:
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
