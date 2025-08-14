"""
Streaming Response Implementation for FastAPI Backend

This module provides Server-Sent Events (SSE) endpoints for real-time streaming
of AI-generated responses, with progress tracking and error handling.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, Optional, Protocol
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import APIRouter, Request, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Create the streaming router
router = APIRouter(prefix="/v1/stream", tags=["streaming"])


class StreamEventType(str, Enum):
    """Types of streaming events."""
    MESSAGE = "message"
    PROGRESS = "progress"
    STATUS = "status"
    ERROR = "error"
    COMPLETE = "complete"
    HEARTBEAT = "heartbeat"


@dataclass
class StreamEvent:
    """Represents a streaming event."""
    event: StreamEventType
    data: Any
    id: Optional[str] = None
    retry: Optional[int] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_sse(self) -> str:
        """Convert to SSE format."""
        lines = []
        
        if self.id:
            lines.append(f"id: {self.id}")
        
        lines.append(f"event: {self.event}")
        
        if self.retry:
            lines.append(f"retry: {self.retry}")
        
        # Format data as JSON
        if isinstance(self.data, str):
            data_str = self.data
        else:
            data_str = json.dumps(self.data)
        
        lines.append(f"data: {data_str}")
        lines.append("")  # Empty line to signal end of event
        
        return "\n".join(lines) + "\n"


class StreamingRequest(BaseModel):
    """Request model for streaming endpoints."""
    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = 4096
    temperature: Optional[float] = 0.7
    stream_options: Optional[Dict[str, Any]] = None


class AIStreamProvider(Protocol):
    """Protocol for AI providers that support streaming."""
    
    async def stream_response(
        self,
        prompt: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response from AI provider."""
        ...


class StreamingService:
    """Service for managing streaming responses."""
    
    def __init__(self):
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.stream_metrics: Dict[str, Any] = {
            "total_streams": 0,
            "active_streams": 0,
            "completed_streams": 0,
            "failed_streams": 0,
            "total_tokens": 0
        }

    async def create_stream(
        self,
        request: Request,
        streaming_request: StreamingRequest,
        ai_provider: Optional[AIStreamProvider] = None
    ) -> AsyncGenerator[str, None]:
        """
        Create a streaming response with SSE.
        
        Args:
            request: FastAPI request object
            streaming_request: Streaming request parameters
            ai_provider: AI provider for streaming
            
        Yields:
            SSE formatted events
        """
        stream_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Track active stream
        self.active_streams[stream_id] = {
            "id": stream_id,
            "started_at": start_time,
            "prompt": streaming_request.prompt[:100],  # Store truncated prompt
            "status": "active",
            "tokens": 0,
            "chunks": 0
        }
        
        self.stream_metrics["total_streams"] += 1
        self.stream_metrics["active_streams"] = len(self.active_streams)
        
        try:
            # Send initial status
            yield StreamEvent(
                event=StreamEventType.STATUS,
                data={
                    "stream_id": stream_id,
                    "status": "started",
                    "timestamp": datetime.now().isoformat()
                }
            ).to_sse()
            
            # Stream from AI provider or simulate
            if ai_provider:
                async for chunk in self._stream_from_provider(
                    ai_provider,
                    streaming_request,
                    stream_id
                ):
                    # Check if client disconnected
                    if await request.is_disconnected():
                        logger.info(f"Client disconnected from stream {stream_id}")
                        break
                    
                    yield chunk
            else:
                # Simulate streaming for demo
                async for chunk in self._simulate_stream(streaming_request, stream_id):
                    if await request.is_disconnected():
                        break
                    yield chunk
            
            # Send completion event
            yield StreamEvent(
                event=StreamEventType.COMPLETE,
                data={
                    "stream_id": stream_id,
                    "total_tokens": self.active_streams[stream_id]["tokens"],
                    "duration": time.time() - start_time
                }
            ).to_sse()
            
            self.stream_metrics["completed_streams"] += 1
            
        except Exception as e:
            logger.error(f"Stream {stream_id} failed: {e}")
            
            # Send error event
            yield StreamEvent(
                event=StreamEventType.ERROR,
                data={
                    "stream_id": stream_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            ).to_sse()
            
            self.stream_metrics["failed_streams"] += 1
            
        finally:
            # Clean up stream
            if stream_id in self.active_streams:
                del self.active_streams[stream_id]
            self.stream_metrics["active_streams"] = len(self.active_streams)

    async def _stream_from_provider(
        self,
        provider: AIStreamProvider,
        request: StreamingRequest,
        stream_id: str
    ) -> AsyncGenerator[str, None]:
        """Stream response from AI provider."""
        total_chunks = 0
        
        async for chunk in provider.stream_response(
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        ):
            total_chunks += 1
            
            # Update metrics
            self.active_streams[stream_id]["chunks"] = total_chunks
            self.active_streams[stream_id]["tokens"] += len(chunk.split())
            
            # Send chunk as message event
            yield StreamEvent(
                event=StreamEventType.MESSAGE,
                data={
                    "content": chunk,
                    "chunk_index": total_chunks
                }
            ).to_sse()
            
            # Send progress update every 10 chunks
            if total_chunks % 10 == 0:
                yield StreamEvent(
                    event=StreamEventType.PROGRESS,
                    data={
                        "chunks": total_chunks,
                        "tokens": self.active_streams[stream_id]["tokens"]
                    }
                ).to_sse()

    async def _simulate_stream(
        self,
        request: StreamingRequest,
        stream_id: str
    ) -> AsyncGenerator[str, None]:
        """Simulate streaming response for demo purposes."""
        
        # Simulate processing stages
        stages = [
            "Analyzing request...",
            "Processing quantum routing...",
            "Generating response...",
            "Optimizing output...",
            "Finalizing results..."
        ]
        
        for i, stage in enumerate(stages):
            # Send status update
            yield StreamEvent(
                event=StreamEventType.STATUS,
                data={
                    "stage": stage,
                    "progress": (i + 1) / len(stages) * 100
                }
            ).to_sse()
            
            await asyncio.sleep(0.5)
        
        # Simulate chunked response
        response_parts = [
            "Based on the quantum routing analysis,",
            " here's the optimized solution:",
            "\n\n1. Initialize the quantum cache manager",
            "\n2. Configure Redis connection with TTL",
            "\n3. Implement cache invalidation logic",
            "\n4. Integrate with existing QuantumManager",
            "\n5. Monitor performance metrics",
            "\n\nThis implementation provides",
            " significant performance improvements",
            " through intelligent caching."
        ]
        
        for i, part in enumerate(response_parts):
            # Update metrics
            self.active_streams[stream_id]["chunks"] = i + 1
            self.active_streams[stream_id]["tokens"] += len(part.split())
            
            # Send content chunk
            yield StreamEvent(
                event=StreamEventType.MESSAGE,
                data={
                    "content": part,
                    "chunk_index": i + 1
                }
            ).to_sse()
            
            # Send progress
            yield StreamEvent(
                event=StreamEventType.PROGRESS,
                data={
                    "progress": (i + 1) / len(response_parts) * 100,
                    "chunks": i + 1,
                    "tokens": self.active_streams[stream_id]["tokens"]
                }
            ).to_sse()
            
            await asyncio.sleep(0.2)

    async def send_heartbeat(self, stream_id: str) -> str:
        """Send heartbeat to keep connection alive."""
        return StreamEvent(
            event=StreamEventType.HEARTBEAT,
            data={
                "stream_id": stream_id,
                "timestamp": datetime.now().isoformat()
            }
        ).to_sse()

    def get_metrics(self) -> Dict[str, Any]:
        """Get streaming metrics."""
        return {
            **self.stream_metrics,
            "active_stream_ids": list(self.active_streams.keys())
        }


# Global streaming service instance
streaming_service = StreamingService()


def get_streaming_service() -> StreamingService:
    """Dependency to get streaming service."""
    return streaming_service


@router.post("/execute")
async def stream_execution(
    request: Request,
    streaming_request: StreamingRequest,
    service: StreamingService = Depends(get_streaming_service)
):
    """
    Stream AI execution results via Server-Sent Events.
    
    This endpoint provides real-time streaming of AI-generated responses
    with progress tracking and status updates.
    """
    return StreamingResponse(
        service.create_stream(request, streaming_request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering
        }
    )


@router.get("/metrics")
async def get_stream_metrics(
    service: StreamingService = Depends(get_streaming_service)
):
    """Get streaming service metrics."""
    return service.get_metrics()


@router.get("/active")
async def get_active_streams(
    service: StreamingService = Depends(get_streaming_service)
):
    """Get list of active streams."""
    return {
        "active_streams": len(service.active_streams),
        "streams": [
            {
                "id": stream["id"],
                "status": stream["status"],
                "chunks": stream.get("chunks", 0),
                "tokens": stream.get("tokens", 0),
                "duration": time.time() - stream["started_at"]
            }
            for stream in service.active_streams.values()
        ]
    }


# CLI Support Functions
def parse_sse_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse an SSE line into event data."""
    if line.startswith("data: "):
        try:
            return json.loads(line[6:])
        except json.JSONDecodeError:
            return {"content": line[6:]}
    return None


async def stream_cli_handler(url: str, verbose: bool = False):
    """
    Handle streaming responses in CLI.
    
    Args:
        url: Streaming endpoint URL
        verbose: Show detailed progress information
    """
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            async for line in response.content:
                line_str = line.decode('utf-8').strip()
                
                if line_str.startswith("event:"):
                    event_type = line_str[7:]
                    if verbose:
                        print(f"[{event_type}]", end=" ")
                
                elif line_str.startswith("data:"):
                    data = parse_sse_line(line_str)
                    if data:
                        if "content" in data:
                            print(data["content"], end="", flush=True)
                        elif verbose:
                            print(json.dumps(data, indent=2))


# Example usage for testing
if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(router)
    
    uvicorn.run(app, host="0.0.0.0", port=8001)