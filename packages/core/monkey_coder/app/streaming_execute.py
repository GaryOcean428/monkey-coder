"""
Enhanced Streaming Execution Endpoint with Real AI Provider Support

This module provides the main streaming execution endpoint that integrates
with all AI providers for real-time streaming responses.
"""

import asyncio
import json
import logging
import time
import uuid
from typing import AsyncGenerator, Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..models import ExecuteRequest, TaskStatus
from ..providers.streaming_adapter import unified_stream_handler, StreamChunk
from ..security import get_api_key, verify_permissions
from ..core.agent_executor import AgentExecutor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["streaming"])


class StreamingExecuteRequest(BaseModel):
    """Request model for streaming execution."""
    prompt: str
    task_type: Optional[str] = "code_generation"
    persona: Optional[str] = "developer"
    provider: Optional[str] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = 4096
    temperature: Optional[float] = 0.7
    enable_web_search: Optional[bool] = False
    stream_options: Optional[Dict[str, Any]] = None


async def create_sse_stream(
    request: StreamingExecuteRequest,
    agent_executor: AgentExecutor,
    stream_id: str
) -> AsyncGenerator[str, None]:
    """
    Create an SSE stream for AI execution.
    
    Args:
        request: Streaming execution request
        agent_executor: Agent executor instance
        stream_id: Unique stream identifier
        
    Yields:
        SSE-formatted strings
    """
    try:
        # Send initial status
        yield f"id: {stream_id}\n"
        yield f"event: status\n"
        yield f"data: {json.dumps({'status': 'started', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        # Prepare messages for AI provider
        messages = [
            {"role": "system", "content": f"You are a {request.persona} assistant."},
            {"role": "user", "content": request.prompt}
        ]
        
        # Determine provider and model
        provider = request.provider or "openai"
        model = request.model
        
        # Get provider adapter
        provider_adapter = agent_executor.provider_registry.get_provider(provider)
        if not provider_adapter:
            raise HTTPException(status_code=400, detail=f"Provider {provider} not available")
        
        # Get default model if not specified
        if not model:
            model = provider_adapter.default_model if hasattr(provider_adapter, 'default_model') else "gpt-4-turbo"
        
        logger.info(f"Starting streaming execution with {provider}/{model}")
        
        # Call provider with streaming enabled
        response = await provider_adapter.generate_completion(
            model=model,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=True
        )
        
        # Check if response is streaming
        if isinstance(response, dict) and response.get("is_streaming"):
            stream_response = response.get("stream")
            
            # Stream chunks through unified handler
            total_content = []
            chunk_count = 0
            total_tokens = 0
            
            async for chunk in unified_stream_handler.stream_response(provider, stream_response):
                chunk_count += 1
                total_content.append(chunk.content)
                total_tokens += chunk.tokens
                
                # Send content chunk
                yield f"id: {stream_id}-{chunk.index}\n"
                yield f"event: message\n"
                yield f"data: {json.dumps({'content': chunk.content, 'index': chunk.index})}\n\n"
                
                # Send progress every 5 chunks
                if chunk_count % 5 == 0:
                    yield f"event: progress\n"
                    yield f"data: {json.dumps({'chunks': chunk_count, 'tokens': total_tokens, 'progress': min(95, chunk_count * 2)})}\n\n"
                
                # Check for completion
                if chunk.finish_reason:
                    break
            
            # Final content
            full_content = "".join(total_content)
            
        else:
            # Non-streaming response, simulate streaming
            full_content = response.get("content", "")
            
            # Simulate streaming for non-streaming responses
            async for chunk in unified_stream_handler.stream_response(
                provider,
                None,
                content=full_content,
                chunk_size=100,
                delay=0.05
            ):
                yield f"id: {stream_id}-{chunk.index}\n"
                yield f"event: message\n"
                yield f"data: {json.dumps({'content': chunk.content, 'index': chunk.index})}\n\n"
        
        # Send completion event
        yield f"id: {stream_id}-complete\n"
        yield f"event: complete\n"
        yield f"data: {json.dumps({
            'execution_id': stream_id,
            'status': 'completed',
            'result': full_content,
            'total_tokens': total_tokens if 'total_tokens' in locals() else len(full_content.split()),
            'provider': provider,
            'model': model
        })}\n\n"
        
    except Exception as e:
        logger.error(f"Streaming execution failed: {e}")
        
        # Send error event
        yield f"id: {stream_id}-error\n"
        yield f"event: error\n"
        yield f"data: {json.dumps({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })}\n\n"


@router.post("/execute/stream")
async def stream_execution(
    request: Request,
    streaming_request: StreamingExecuteRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key),
):
    """
    Stream AI execution results via Server-Sent Events.
    
    This endpoint provides real-time streaming of AI-generated responses
    from any configured provider (OpenAI, Anthropic, Google, Groq, xAI).
    
    Args:
        request: FastAPI request object
        streaming_request: Streaming execution request
        background_tasks: Background tasks for async operations
        api_key: API key for authentication
        
    Returns:
        StreamingResponse with SSE content
    """
    try:
        # Verify permissions
        await verify_permissions(api_key, "execute")
        
        # Generate stream ID
        stream_id = str(uuid.uuid4())
        
        # Get agent executor from app state
        app = request.app
        if not hasattr(app.state, 'provider_registry'):
            raise HTTPException(status_code=500, detail="Provider registry not initialized")
        
        # Create agent executor
        agent_executor = AgentExecutor(provider_registry=app.state.provider_registry)
        
        # Create SSE stream
        return StreamingResponse(
            create_sse_stream(streaming_request, agent_executor, stream_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable Nginx buffering
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start streaming execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/streams/active")
async def get_active_streams(
    api_key: str = Depends(get_api_key),
):
    """
    Get list of active streaming sessions.
    
    Args:
        api_key: API key for authentication
        
    Returns:
        Dictionary with active stream information
    """
    try:
        await verify_permissions(api_key, "execute")
        
        # In a real implementation, this would track active streams
        # For now, return placeholder data
        return {
            "active_streams": 0,
            "streams": []
        }
        
    except Exception as e:
        logger.error(f"Failed to get active streams: {e}")
        raise HTTPException(status_code=500, detail=str(e))