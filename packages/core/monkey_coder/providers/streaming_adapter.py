"""
Streaming Adapter for AI Provider Responses

This module provides a unified streaming interface for all AI providers,
enabling real-time response streaming via Server-Sent Events (SSE).
"""

import asyncio
import json
import logging
import time
from typing import AsyncGenerator, Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class StreamChunk:
    """Represents a single chunk of streaming content."""
    content: str
    index: int
    tokens: int = 0
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class StreamingAdapter:
    """
    Adapter to provide streaming capabilities for AI providers.
    """
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.chunk_count = 0
        self.total_tokens = 0
        self.start_time = None
        
    async def stream_openai_response(
        self,
        stream_response: Any,
        **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Stream response from OpenAI provider.
        
        Args:
            stream_response: OpenAI streaming response object
            
        Yields:
            StreamChunk objects containing content and metadata
        """
        self.start_time = time.time()
        self.chunk_count = 0
        self.total_tokens = 0
        
        try:
            async for chunk in stream_response:
                if chunk.choices and len(chunk.choices) > 0:
                    choice = chunk.choices[0]
                    
                    # Extract content from delta
                    content = ""
                    if hasattr(choice, 'delta') and hasattr(choice.delta, 'content'):
                        content = choice.delta.content or ""
                    
                    if content:
                        self.chunk_count += 1
                        # Estimate tokens (rough approximation)
                        estimated_tokens = len(content.split()) // 4 + 1
                        self.total_tokens += estimated_tokens
                        
                        yield StreamChunk(
                            content=content,
                            index=self.chunk_count,
                            tokens=estimated_tokens,
                            finish_reason=choice.finish_reason,
                            metadata={
                                "provider": "openai",
                                "timestamp": datetime.now().isoformat(),
                                "chunk_id": chunk.id if hasattr(chunk, 'id') else None,
                            }
                        )
                    
                    # Check for finish reason
                    if choice.finish_reason:
                        logger.info(f"Stream finished: {choice.finish_reason}")
                        break
                        
        except Exception as e:
            logger.error(f"Error streaming OpenAI response: {e}")
            yield StreamChunk(
                content=f"[Error: {str(e)}]",
                index=self.chunk_count + 1,
                tokens=0,
                finish_reason="error",
                metadata={"error": str(e)}
            )
    
    async def stream_anthropic_response(
        self,
        stream_response: Any,
        **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Stream response from Anthropic provider.
        
        Args:
            stream_response: Anthropic streaming response object
            
        Yields:
            StreamChunk objects containing content and metadata
        """
        self.start_time = time.time()
        self.chunk_count = 0
        self.total_tokens = 0
        
        try:
            async for event in stream_response:
                if event.type == "message_start":
                    # Initial message metadata
                    logger.debug(f"Stream started: {event.message.id}")
                    
                elif event.type == "content_block_delta":
                    # Content chunk
                    if hasattr(event, 'delta') and hasattr(event.delta, 'text'):
                        content = event.delta.text or ""
                        
                        if content:
                            self.chunk_count += 1
                            estimated_tokens = len(content.split()) // 4 + 1
                            self.total_tokens += estimated_tokens
                            
                            yield StreamChunk(
                                content=content,
                                index=self.chunk_count,
                                tokens=estimated_tokens,
                                finish_reason=None,
                                metadata={
                                    "provider": "anthropic",
                                    "timestamp": datetime.now().isoformat(),
                                    "block_index": event.index if hasattr(event, 'index') else None,
                                }
                            )
                
                elif event.type == "message_stop":
                    # Stream finished
                    logger.info("Anthropic stream finished")
                    break
                    
        except Exception as e:
            logger.error(f"Error streaming Anthropic response: {e}")
            yield StreamChunk(
                content=f"[Error: {str(e)}]",
                index=self.chunk_count + 1,
                tokens=0,
                finish_reason="error",
                metadata={"error": str(e)}
            )
    
    async def stream_google_response(
        self,
        stream_response: Any,
        **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Stream response from Google Gemini provider.
        
        Args:
            stream_response: Google streaming response object
            
        Yields:
            StreamChunk objects containing content and metadata
        """
        self.start_time = time.time()
        self.chunk_count = 0
        self.total_tokens = 0
        
        try:
            async for chunk in stream_response:
                if hasattr(chunk, 'text'):
                    content = chunk.text or ""
                    
                    if content:
                        self.chunk_count += 1
                        estimated_tokens = len(content.split()) // 4 + 1
                        self.total_tokens += estimated_tokens
                        
                        yield StreamChunk(
                            content=content,
                            index=self.chunk_count,
                            tokens=estimated_tokens,
                            finish_reason=None,
                            metadata={
                                "provider": "google",
                                "timestamp": datetime.now().isoformat(),
                            }
                        )
                        
        except Exception as e:
            logger.error(f"Error streaming Google response: {e}")
            yield StreamChunk(
                content=f"[Error: {str(e)}]",
                index=self.chunk_count + 1,
                tokens=0,
                finish_reason="error",
                metadata={"error": str(e)}
            )
    
    async def stream_groq_response(
        self,
        stream_response: Any,
        **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Stream response from Groq provider.
        
        Args:
            stream_response: Groq streaming response object
            
        Yields:
            StreamChunk objects containing content and metadata
        """
        self.start_time = time.time()
        self.chunk_count = 0
        self.total_tokens = 0
        
        try:
            async for chunk in stream_response:
                if chunk.choices and len(chunk.choices) > 0:
                    choice = chunk.choices[0]
                    
                    # Similar to OpenAI format
                    content = ""
                    if hasattr(choice, 'delta') and hasattr(choice.delta, 'content'):
                        content = choice.delta.content or ""
                    
                    if content:
                        self.chunk_count += 1
                        estimated_tokens = len(content.split()) // 4 + 1
                        self.total_tokens += estimated_tokens
                        
                        yield StreamChunk(
                            content=content,
                            index=self.chunk_count,
                            tokens=estimated_tokens,
                            finish_reason=choice.finish_reason,
                            metadata={
                                "provider": "groq",
                                "timestamp": datetime.now().isoformat(),
                            }
                        )
                    
                    if choice.finish_reason:
                        logger.info(f"Groq stream finished: {choice.finish_reason}")
                        break
                        
        except Exception as e:
            logger.error(f"Error streaming Groq response: {e}")
            yield StreamChunk(
                content=f"[Error: {str(e)}]",
                index=self.chunk_count + 1,
                tokens=0,
                finish_reason="error",
                metadata={"error": str(e)}
            )
    
    async def simulate_streaming(
        self,
        content: str,
        chunk_size: int = 50,
        delay: float = 0.05,
        **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Simulate streaming for providers that don't support it natively.
        
        Args:
            content: Full content to stream
            chunk_size: Number of characters per chunk
            delay: Delay between chunks in seconds
            
        Yields:
            StreamChunk objects simulating streaming
        """
        self.start_time = time.time()
        self.chunk_count = 0
        self.total_tokens = 0
        
        # Split content into chunks
        words = content.split()
        chunks = []
        current_chunk = []
        
        for word in words:
            current_chunk.append(word)
            if len(" ".join(current_chunk)) >= chunk_size:
                chunks.append(" ".join(current_chunk) + " ")
                current_chunk = []
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        # Stream chunks
        for i, chunk_text in enumerate(chunks):
            self.chunk_count += 1
            estimated_tokens = len(chunk_text.split()) // 4 + 1
            self.total_tokens += estimated_tokens
            
            yield StreamChunk(
                content=chunk_text,
                index=self.chunk_count,
                tokens=estimated_tokens,
                finish_reason="stop" if i == len(chunks) - 1 else None,
                metadata={
                    "provider": self.provider_name,
                    "simulated": True,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            
            # Add delay between chunks
            if i < len(chunks) - 1:
                await asyncio.sleep(delay)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get streaming metrics."""
        duration = time.time() - self.start_time if self.start_time else 0
        
        return {
            "provider": self.provider_name,
            "chunks": self.chunk_count,
            "total_tokens": self.total_tokens,
            "duration": duration,
            "chunks_per_second": self.chunk_count / duration if duration > 0 else 0,
            "tokens_per_second": self.total_tokens / duration if duration > 0 else 0,
        }


class UnifiedStreamHandler:
    """
    Unified handler for streaming responses across all providers.
    """
    
    def __init__(self):
        self.adapters = {}
        
    def get_adapter(self, provider: str) -> StreamingAdapter:
        """Get or create streaming adapter for provider."""
        if provider not in self.adapters:
            self.adapters[provider] = StreamingAdapter(provider)
        return self.adapters[provider]
    
    async def stream_response(
        self,
        provider: str,
        stream_response: Any,
        **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Stream response from any provider.
        
        Args:
            provider: Provider name (openai, anthropic, google, groq, xai)
            stream_response: Provider-specific streaming response
            
        Yields:
            Unified StreamChunk objects
        """
        adapter = self.get_adapter(provider)
        
        if provider == "openai":
            async for chunk in adapter.stream_openai_response(stream_response, **kwargs):
                yield chunk
                
        elif provider == "anthropic":
            async for chunk in adapter.stream_anthropic_response(stream_response, **kwargs):
                yield chunk
                
        elif provider == "google":
            async for chunk in adapter.stream_google_response(stream_response, **kwargs):
                yield chunk
                
        elif provider == "groq":
            async for chunk in adapter.stream_groq_response(stream_response, **kwargs):
                yield chunk
                
        else:
            # Fallback to simulation if provider not supported
            logger.warning(f"Provider {provider} not directly supported, simulating streaming")
            content = kwargs.get("content", "")
            async for chunk in adapter.simulate_streaming(content, **kwargs):
                yield chunk
    
    async def stream_to_sse(
        self,
        provider: str,
        stream_response: Any,
        stream_id: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Convert provider streaming response to SSE format.
        
        Args:
            provider: Provider name
            stream_response: Provider-specific streaming response
            stream_id: Unique stream identifier
            
        Yields:
            SSE-formatted strings
        """
        # Send initial status
        yield f"id: {stream_id}\n"
        yield f"event: status\n"
        yield f"data: {json.dumps({'status': 'started', 'provider': provider})}\n\n"
        
        total_content = []
        chunk_count = 0
        
        async for chunk in self.stream_response(provider, stream_response, **kwargs):
            chunk_count += 1
            total_content.append(chunk.content)
            
            # Send content chunk
            yield f"id: {stream_id}-{chunk.index}\n"
            yield f"event: message\n"
            yield f"data: {json.dumps({'content': chunk.content, 'index': chunk.index})}\n\n"
            
            # Send progress update every 5 chunks
            if chunk_count % 5 == 0:
                yield f"event: progress\n"
                yield f"data: {json.dumps({'chunks': chunk_count, 'tokens': chunk.tokens})}\n\n"
            
            # Check for completion
            if chunk.finish_reason:
                break
        
        # Send completion event
        yield f"id: {stream_id}-complete\n"
        yield f"event: complete\n"
        yield f"data: {json.dumps({'total_chunks': chunk_count, 'content': ''.join(total_content)})}\n\n"


# Global unified stream handler
unified_stream_handler = UnifiedStreamHandler()

__all__ = [
    "StreamChunk",
    "StreamingAdapter", 
    "UnifiedStreamHandler",
    "unified_stream_handler"
]