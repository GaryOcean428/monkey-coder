"""
Gemini 3 Pro Provider Adapter for Monkey Coder Core.

This adapter provides integration with Google's Gemini 3 Pro model, featuring:
- 1M token context window (largest available)
- Thinking level control (lo, mid, hi)
- Thought signatures for reasoning continuity
- Google Search grounding
- Code execution sandbox
- Multimodal support (images, audio, video, PDF)
- Image and audio generation
- Context caching (75% cost reduction)

Features:
- Media resolution control for optimal token usage
- Native Python sandbox with NumPy, Pandas, Matplotlib
- Built-in web search with grounding
- Extended thinking capabilities
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, AsyncGenerator, Optional

try:
    import google.genai as genai
    from google.genai.types import GenerateContentConfig, Tool
    HAS_GOOGLE_AI = True
except ImportError:
    genai = None
    GenerateContentConfig = None
    Tool = None
    HAS_GOOGLE_AI = False
    logging.warning(
        "Google AI package not installed. Install it with: pip install google-genai>=1.41.0"
    )

from . import BaseProvider
from ..models import ProviderType, ProviderError, ModelInfo
from ..logging_utils import monitor_api_calls

logger = logging.getLogger(__name__)


class Gemini3Provider(BaseProvider):
    """
    Gemini 3 Pro provider adapter implementing the BaseProvider interface.
    
    Provides access to Google's Gemini 3 Pro with 1M context window and thinking control.
    """

    # Gemini 3 Pro model with validated specifications
    VALIDATED_MODELS: Dict[str, Dict[str, Any]] = {
        "gemini-3-pro": {
            "name": "gemini-3-pro",
            "api_name": "gemini-3-pro",
            "type": "chat",
            "context_length": 1048576,  # 1M tokens
            "max_output_tokens": 128000,
            "input_cost": 2.00,  # per 1M tokens (<200K tokens)
            "output_cost": 12.00,  # per 1M tokens (<200K tokens)
            "cached_input_cost": 0.025,  # 75% discount
            "description": "Most intelligent Gemini model with 1M context and thinking control",
            "capabilities": [
                "text",
                "vision",
                "audio",
                "video",
                "pdf",
                "thinking_control",
                "thought_signatures",
                "function_calling",
                "structured_outputs",
                "code_execution",
                "search_grounding",
                "image_generation",
                "audio_generation",
                "live_api",
                "context_caching",
            ],
            "version": "3-pro",
            "knowledge_cutoff": datetime(2025, 11, 1),
            "release_date": datetime(2025, 11, 1),
        },
    }

    def __init__(self, api_key: str, **kwargs):
        """Initialize Gemini 3 Pro provider."""
        super().__init__(api_key, **kwargs)
        if not HAS_GOOGLE_AI:
            raise ProviderError(
                "Google AI package not installed. Install it with: pip install google-genai>=1.41.0"
            )
        
        genai.configure(api_key=api_key)
        self.client = genai.Client(api_key=api_key)
        self._cached_content = {}

    @property
    def provider_type(self) -> ProviderType:
        """Return the provider type."""
        return ProviderType.GOOGLE

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "google-gemini3"

    async def initialize(self) -> None:
        """Initialize the provider client."""
        logger.info("Initialized Gemini 3 Pro provider")

    async def cleanup(self) -> None:
        """Cleanup provider resources."""
        # Clear cached content
        self._cached_content.clear()
        logger.info("Cleaned up Gemini 3 Pro provider")

    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of available Gemini 3 models."""
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

    @monitor_api_calls("gemini3_completion")
    async def _generate_completion_impl(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate completion using Gemini 3 Pro.
        
        Args:
            model: Model name (already validated)
            messages: Conversation messages
            **kwargs: Additional parameters including:
                - thinking_level: Reasoning depth (lo, mid, hi)
                - enable_grounding: Enable Google Search grounding
                - enable_code_execution: Enable Python sandbox
                - media_resolution: Image/video resolution (low, medium, high)
                - temperature: Sampling temperature
                - stream: Enable streaming
        
        Returns:
            Completion response
        """
        model_info = self.VALIDATED_MODELS.get(model, {})
        thinking_level = kwargs.get("thinking_level", "mid")
        enable_grounding = kwargs.get("enable_grounding", False)
        enable_code_execution = kwargs.get("enable_code_execution", False)
        stream = kwargs.get("stream", False)

        # Validate thinking level
        valid_levels = ["lo", "mid", "hi"]
        if thinking_level not in valid_levels:
            logger.warning(
                f"Invalid thinking level '{thinking_level}', defaulting to 'mid'. "
                f"Valid options: {valid_levels}"
            )
            thinking_level = "mid"

        # Build tools list
        tools = []
        if enable_grounding:
            tools.append(Tool(google_search={}))
            logger.info("Enabled Google Search grounding")
        if enable_code_execution:
            tools.append(Tool(code_execution={}))
            logger.info("Enabled code execution sandbox")

        # Build generation config
        generation_config = GenerateContentConfig(
            thinking_level=thinking_level,
            temperature=kwargs.get("temperature", 0.7),
            max_output_tokens=kwargs.get("max_tokens", 128000),
            media_resolution=kwargs.get("media_resolution", "medium"),
        )

        # Format messages for Gemini
        contents = self._format_messages_for_gemini(messages)

        try:
            model_instance = self.client.models.get(model_info.get("api_name", model))
            
            if stream:
                return {"stream": self._stream_completion(
                    model_instance,
                    contents,
                    generation_config,
                    tools
                )}
            else:
                response = await model_instance.generate_content_async(
                    contents=contents,
                    generation_config=generation_config,
                    tools=tools if tools else None,
                )
                
                # Store thought signature for continuity
                if hasattr(response, 'thought_signature'):
                    self._cached_content['last_thought_signature'] = response.thought_signature
                
                return self._format_response(response)

        except Exception as e:
            logger.error(f"Gemini 3 Pro completion error: {e}")
            raise ProviderError(f"Gemini 3 Pro completion failed: {str(e)}")

    def _format_messages_for_gemini(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert standard message format to Gemini format."""
        gemini_messages = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Gemini uses "user" and "model" roles
            gemini_role = "user" if role in ["user", "system"] else "model"
            
            gemini_messages.append({
                "role": gemini_role,
                "parts": [{"text": content}]
            })
        
        return gemini_messages

    async def _stream_completion(
        self,
        model_instance: Any,
        contents: List[Dict[str, Any]],
        generation_config: Any,
        tools: List[Any]
    ) -> AsyncGenerator[str, None]:
        """Stream completion tokens from Gemini 3 Pro."""
        try:
            response = await model_instance.generate_content_async(
                contents=contents,
                generation_config=generation_config,
                tools=tools if tools else None,
                stream=True,
            )
            
            async for chunk in response:
                # Store thought signature if present
                if hasattr(chunk, 'thought_signature'):
                    self._cached_content['last_thought_signature'] = chunk.thought_signature
                
                # Yield text content
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Gemini 3 Pro streaming error: {e}")
            raise ProviderError(f"Gemini 3 Pro streaming failed: {str(e)}")

    def _format_response(self, response: Any) -> Dict[str, Any]:
        """Format Gemini response to standard format."""
        text_content = ""
        if hasattr(response, 'text'):
            text_content = response.text
        elif hasattr(response, 'candidates') and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                text_content = " ".join(
                    part.text for part in candidate.content.parts if hasattr(part, 'text')
                )

        usage = {}
        if hasattr(response, 'usage_metadata'):
            usage = {
                "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0),
                "cached_tokens": getattr(response.usage_metadata, 'cached_content_token_count', 0),
            }

        return {
            "content": text_content,
            "role": "assistant",
            "finish_reason": "stop",
            "usage": usage,
            "model": "gemini-3-pro",
            "thought_signature": self._cached_content.get('last_thought_signature'),
        }

    async def create_cached_content(
        self,
        system_instruction: str,
        contents: List[Dict[str, Any]],
        ttl: int = 3600
    ) -> str:
        """
        Create cached content for large contexts.
        
        Args:
            system_instruction: System instruction to cache
            contents: Repository context or large documents
            ttl: Time-to-live in seconds (default: 1 hour)
        
        Returns:
            Cache ID for reuse
        """
        try:
            cache = await genai.caching.CachedContent.create_async(
                model="gemini-3-pro",
                system_instruction=system_instruction,
                contents=contents,
                ttl=ttl,
            )
            cache_id = cache.name
            self._cached_content[cache_id] = cache
            logger.info(f"Created cached content: {cache_id} (TTL: {ttl}s)")
            return cache_id

        except Exception as e:
            logger.error(f"Failed to create cached content: {e}")
            raise ProviderError(f"Caching failed: {str(e)}")

    async def get_model_info(self, model_name: str) -> ModelInfo:
        """Get detailed information about Gemini 3 Pro."""
        model_data = self.VALIDATED_MODELS.get(model_name)
        if not model_data:
            raise ProviderError(f"Model {model_name} not found in Gemini 3 provider")

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
        model: str = "gemini-3-pro",
        thinking_level: str = "mid",
        enable_grounding: bool = False,
        enable_code_execution: bool = False,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat responses with Gemini 3 Pro.
        
        Args:
            messages: Conversation messages
            model: Model to use (default: gemini-3-pro)
            thinking_level: Reasoning depth (lo, mid, hi)
            enable_grounding: Enable Google Search
            enable_code_execution: Enable Python sandbox
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
            "thinking_level": thinking_level,
            "enable_grounding": enable_grounding,
            "enable_code_execution": enable_code_execution,
            **kwargs
        }

        response = await self._generate_completion_impl(**request_params)
        async for chunk in response["stream"]:
            yield chunk
