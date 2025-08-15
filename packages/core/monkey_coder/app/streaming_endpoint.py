"""
Streaming endpoint integration for FastAPI.
Connects the SSE handler with the main orchestrator.
"""

import asyncio
import json
import logging
import uuid
from typing import AsyncGenerator, Optional

from fastapi import HTTPException, Request, status
from sse_starlette.sse import EventSourceResponse

from ..models.api_models import ExecuteRequest
from ..core.orchestration_coordinator import OrchestrationCoordinator
from ..core.persona_validation import PersonaValidator
from ..providers import get_provider_adapter
from ..config.env_config import get_config

logger = logging.getLogger(__name__)

# Track active streaming connections
active_streams = {}


async def stream_orchestration_response(
    request: Request,
    execute_request: ExecuteRequest,
    request_id: str
) -> AsyncGenerator[str, None]:
    """
    Stream orchestration responses as SSE events.
    """
    try:
        # Track connection
        logger.info(f"Starting stream for request: {request_id}")
        active_streams[request_id] = True
        
        # Initialize components
        config = get_config()
        validator = PersonaValidator()
        coordinator = OrchestrationCoordinator()
        
        # Validate and enhance request
        validation_result = validator.validate_prompt(
            execute_request.prompt,
            execute_request.persona
        )
        
        # Send validation event
        yield f"data: {json.dumps({'event': 'validation', 'status': 'success', 'confidence': validation_result.confidence})}\n\n"
        
        # Enhanced prompt
        enhanced_prompt = validation_result.enhanced_prompt or execute_request.prompt
        
        # Send orchestration start event
        yield f"data: {json.dumps({'event': 'orchestration_start', 'strategy': coordinator.current_strategy})}\n\n"
        
        # Get provider and model info
        provider_name = execute_request.provider or "openai"
        model_name = execute_request.model
        
        # Get provider adapter
        provider_adapter = get_provider_adapter(provider_name)
        if not provider_adapter:
            yield f"data: {json.dumps({'event': 'error', 'message': f'Provider {provider_name} not available'})}\n\n"
            return
        
        # Check if provider supports streaming
        if hasattr(provider_adapter, 'stream_completion'):
            # Stream tokens from provider
            token_count = 0
            full_response = ""
            
            async for chunk in provider_adapter.stream_completion(
                prompt=enhanced_prompt,
                model=model_name,
                temperature=execute_request.temperature,
                max_tokens=execute_request.max_tokens
            ):
                if await request.is_disconnected():
                    logger.info(f"Client disconnected: {request_id}")
                    break
                
                # Send token event
                if chunk.get('token'):
                    token = chunk['token']
                    full_response += token
                    token_count += 1
                    
                    yield f"data: {json.dumps({'event': 'token', 'content': token, 'token_count': token_count})}\n\n"
                
                # Yield control
                await asyncio.sleep(0)
        else:
            # Fallback to non-streaming with progress updates
            yield f"data: {json.dumps({'event': 'progress', 'message': 'Processing with non-streaming provider...'})}\n\n"
            
            # Execute through orchestrator
            result = await coordinator.execute_async(
                prompt=enhanced_prompt,
                persona=execute_request.persona,
                task_type=execute_request.task_type,
                context=execute_request.context,
                provider=provider_name,
                model=model_name
            )
            
            # Send complete response
            yield f"data: {json.dumps({'event': 'complete', 'content': result.get('response', ''), 'tokens_used': result.get('total_tokens', 0)})}\n\n"
        
        # Send done event
        yield f"data: {json.dumps({'event': 'done', 'token_count': token_count if 'token_count' in locals() else 0})}\n\n"
        
    except asyncio.CancelledError:
        logger.info(f"Stream cancelled: {request_id}")
    except Exception as e:
        logger.exception(f"Stream error for {request_id}")
        yield f"data: {json.dumps({'event': 'error', 'message': str(e)})}\n\n"
    finally:
        # Clean up
        active_streams.pop(request_id, None)
        logger.info(f"Stream closed: {request_id}")


def create_streaming_endpoint(app):
    """
    Add streaming endpoint to FastAPI app.
    """
    
    @app.post("/api/v1/execute/stream")
    async def execute_stream(
        request: Request,
        execute_request: ExecuteRequest
    ):
        """
        Stream execution results using Server-Sent Events.
        """
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Check if request ID already active
        if request_id in active_streams:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Request already being processed"
            )
        
        # Create SSE response
        generator = stream_orchestration_response(
            request=request,
            execute_request=execute_request,
            request_id=request_id
        )
        
        return EventSourceResponse(generator)
    
    @app.get("/api/v1/streams/active")
    async def get_active_streams():
        """
        Get list of active streaming connections.
        """
        return {
            "active_streams": list(active_streams.keys()),
            "count": len(active_streams)
        }
    
    logger.info("Streaming endpoints added to FastAPI app")