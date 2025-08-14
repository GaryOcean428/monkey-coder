"""
OpenAI Adapter for Monkey Coder Unified AI SDK

This module implements the UnifiedProvider interface for OpenAI's API,
supporting both streaming and non-streaming completions, robust error handling,
logging, and response mapping to the UnifiedResponse format.

Author: Monkey Coder Team
"""

import logging
import time
from typing import Any, Dict, Generator, List, Optional, Union

import openai
from openai.error import (
    OpenAIError,
    RateLimitError,
    APIConnectionError,
    APIError,
    Timeout,
    AuthenticationError,
    InvalidRequestError,
)

from packages.sdk.unified.base import (
    UnifiedProvider,
    UnifiedResponse,
    UnifiedMessage,
    UnifiedError,
    UnifiedHealthStatus,
)

# Configure module-level logger
logger = logging.getLogger("unified.openai_adapter")
logger.setLevel(logging.INFO)


class OpenAIAdapter(UnifiedProvider):
    """
    OpenAI Adapter implementing the UnifiedProvider interface.

    Supports both streaming and non-streaming completions, robust error handling,
    logging, and response mapping to the UnifiedResponse format.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-3.5-turbo",
        organization: Optional[str] = None,
        max_retries: int = 3,
        retry_backoff: float = 2.0,
        timeout: float = 30.0,
    ):
        """
        Initialize the OpenAIAdapter.

        Args:
            api_key (str): OpenAI API key.
            model (str): Model name (e.g., 'gpt-4', 'gpt-3.5-turbo').
            organization (Optional[str]): OpenAI organization ID.
            max_retries (int): Maximum number of retries for rate limiting.
            retry_backoff (float): Backoff multiplier for retries.
            timeout (float): Timeout for API requests in seconds.
        """
        self.api_key = api_key
        self.model = model
        self.organization = organization
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.timeout = timeout

        openai.api_key = self.api_key
        if self.organization:
            openai.organization = self.organization

        logger.info(
            f"Initialized OpenAIAdapter with model={self.model}, organization={self.organization}"
        )

    def _map_unified_to_openai_messages(
        self, messages: List[UnifiedMessage]
    ) -> List[Dict[str, str]]:
        """
        Map UnifiedMessage list to OpenAI's message format.

        Args:
            messages (List[UnifiedMessage]): List of UnifiedMessage objects.

        Returns:
            List[Dict[str, str]]: List of OpenAI-formatted messages.
        """
        role_map = {
            "user": "user",
            "assistant": "assistant",
            "system": "system",
        }
        openai_messages = []
        for msg in messages:
            role = role_map.get(msg.role, "user")
            openai_messages.append({"role": role, "content": msg.content})
        logger.debug(f"Mapped messages: {openai_messages}")
        return openai_messages

    def _map_openai_to_unified_response(
        self, openai_response: Any
    ) -> UnifiedResponse:
        """
        Map OpenAI response to UnifiedResponse.

        Args:
            openai_response (Any): OpenAI API response object.

        Returns:
            UnifiedResponse: Mapped response.
        """
        try:
            choice = openai_response.choices[0]
            message = choice.message
            content = message.get("content", "")
            role = message.get("role", "assistant")
            usage = getattr(openai_response, "usage", None)
            prompt_tokens = usage.get("prompt_tokens", 0) if usage else 0
            completion_tokens = usage.get("completion_tokens", 0) if usage else 0
            total_tokens = usage.get("total_tokens", 0) if usage else 0

            unified_response = UnifiedResponse(
                messages=[UnifiedMessage(role=role, content=content)],
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                raw=openai_response,
            )
            logger.debug(f"Mapped OpenAI response to UnifiedResponse: {unified_response}")
            return unified_response
        except Exception as e:
            logger.error(f"Failed to map OpenAI response: {e}")
            raise UnifiedError(f"Failed to map OpenAI response: {e}")

    def _count_tokens(self, messages: List[UnifiedMessage]) -> int:
        """
        Estimate token count for a list of messages.

        Args:
            messages (List[UnifiedMessage]): List of UnifiedMessage objects.

        Returns:
            int: Estimated token count.
        """
        # For production, use tiktoken or OpenAI's tokenizer.
        # Here, we use a simple heuristic: 1 token ≈ 4 characters (English).
        total_chars = sum(len(msg.content) for msg in messages)
        estimated_tokens = total_chars // 4
        logger.debug(f"Estimated token count: {estimated_tokens}")
        return estimated_tokens

    def _retry_on_rate_limit(self, func, *args, **kwargs):
        """
        Retry a function on rate limit errors.

        Args:
            func: Function to call.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            Any: Function result.

        Raises:
            UnifiedError: If all retries fail.
        """
        retries = 0
        while retries <= self.max_retries:
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                if retries == self.max_retries:
                    logger.error("Rate limit exceeded and max retries reached.")
                    raise UnifiedError("Rate limit exceeded. Please try again later.") from e
                wait_time = self.retry_backoff ** retries
                logger.warning(
                    f"Rate limit hit. Retrying in {wait_time:.1f}s... (attempt {retries+1}/{self.max_retries})"
                )
                time.sleep(wait_time)
                retries += 1
            except (APIConnectionError, Timeout) as e:
                if retries == self.max_retries:
                    logger.error("API connection/timeout error and max retries reached.")
                    raise UnifiedError("API connection/timeout error.") from e
                wait_time = self.retry_backoff ** retries
                logger.warning(
                    f"API connection/timeout error. Retrying in {wait_time:.1f}s... (attempt {retries+1}/{self.max_retries})"
                )
                time.sleep(wait_time)
                retries += 1

    def complete(
        self,
        messages: List[UnifiedMessage],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stop: Optional[List[str]] = None,
        **kwargs,
    ) -> UnifiedResponse:
        """
        Get a non-streaming completion from OpenAI.

        Args:
            messages (List[UnifiedMessage]): Conversation history.
            temperature (float): Sampling temperature.
            max_tokens (int): Max tokens to generate.
            stop (Optional[List[str]]): Stop sequences.
            **kwargs: Additional OpenAI parameters.

        Returns:
            UnifiedResponse: Unified response object.

        Raises:
            UnifiedError: On API or mapping errors.
        """
        logger.info("Starting OpenAI completion (non-streaming)...")
        openai_messages = self._map_unified_to_openai_messages(messages)
        params = {
            "model": self.model,
            "messages": openai_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stop": stop,
            "timeout": self.timeout,
            **kwargs,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        try:
            response = self._retry_on_rate_limit(openai.ChatCompletion.create, **params)
            logger.info("OpenAI completion successful.")
            return self._map_openai_to_unified_response(response)
        except AuthenticationError as e:
            logger.error("Authentication failed with OpenAI API.")
            raise UnifiedError("Authentication failed with OpenAI API.") from e
        except InvalidRequestError as e:
            logger.error(f"Invalid request to OpenAI API: {e}")
            raise UnifiedError(f"Invalid request to OpenAI API: {e}") from e
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise UnifiedError(f"OpenAI API error: {e}") from e
        except OpenAIError as e:
            logger.error(f"OpenAI error: {e}")
            raise UnifiedError(f"OpenAI error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during completion: {e}")
            raise UnifiedError(f"Unexpected error during completion: {e}") from e

    def stream(
        self,
        messages: List[UnifiedMessage],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stop: Optional[List[str]] = None,
        **kwargs,
    ) -> Generator[UnifiedResponse, None, None]:
        """
        Get a streaming completion from OpenAI.

        Args:
            messages (List[UnifiedMessage]): Conversation history.
            temperature (float): Sampling temperature.
            max_tokens (int): Max tokens to generate.
            stop (Optional[List[str]]): Stop sequences.
            **kwargs: Additional OpenAI parameters.

        Yields:
            UnifiedResponse: Unified response chunk.

        Raises:
            UnifiedError: On API or mapping errors.
        """
        logger.info("Starting OpenAI completion (streaming)...")
        openai_messages = self._map_unified_to_openai_messages(messages)
        params = {
            "model": self.model,
            "messages": openai_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stop": stop,
            "stream": True,
            "timeout": self.timeout,
            **kwargs,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        try:
            stream = self._retry_on_rate_limit(openai.ChatCompletion.create, **params)
            content_accum = ""
            role = "assistant"
            prompt_tokens = self._count_tokens(messages)
            completion_tokens = 0

            for chunk in stream:
                if "choices" not in chunk or not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                chunk_content = delta.get("content", "")
                if "role" in delta:
                    role = delta["role"]
                content_accum += chunk_content
                completion_tokens += self._count_tokens([UnifiedMessage(role=role, content=chunk_content)])

                unified_chunk = UnifiedResponse(
                    messages=[UnifiedMessage(role=role, content=content_accum)],
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                    raw=chunk,
                )
                logger.debug(f"Yielding streaming UnifiedResponse chunk: {unified_chunk}")
                yield unified_chunk

            logger.info("OpenAI streaming completion finished.")
        except AuthenticationError as e:
            logger.error("Authentication failed with OpenAI API.")
            raise UnifiedError("Authentication failed with OpenAI API.") from e
        except InvalidRequestError as e:
            logger.error(f"Invalid request to OpenAI API: {e}")
            raise UnifiedError(f"Invalid request to OpenAI API: {e}") from e
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise UnifiedError(f"OpenAI API error: {e}") from e
        except OpenAIError as e:
            logger.error(f"OpenAI error: {e}")
            raise UnifiedError(f"OpenAI error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during streaming: {e}")
            raise UnifiedError(f"Unexpected error during streaming: {e}") from e

    def health_check(self) -> UnifiedHealthStatus:
        """
        Perform a health check against the OpenAI API.

        Returns:
            UnifiedHealthStatus: Health status object.
        """
        logger.info("Performing OpenAI health check...")
        try:
            # Use a lightweight request to check API health
            openai.Engine.list(timeout=10)
            logger.info("OpenAI health check passed.")
            return UnifiedHealthStatus(
                healthy=True,
                message="OpenAI API is reachable and healthy.",
            )
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return UnifiedHealthStatus(
                healthy=False,
                message=f"OpenAI API health check failed: {e}",
            )