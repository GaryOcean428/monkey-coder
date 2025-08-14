import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, Set, Optional

import httpx
from fastapi import FastAPI, Request, HTTPException, status
from sse_starlette.sse import EventSourceResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sse")

app = FastAPI()

# Track active connections by request_id
active_connections: Dict[str, EventSourceResponse] = {}

# SSE event formatting helper
def format_sse_event(event_type: str, data: dict) -> str:
    payload = {
        "event": event_type,
        "data": data
    }
    return f"data: {json.dumps(payload)}\n\n"

# Heartbeat interval (seconds)
HEARTBEAT_INTERVAL = 15

# --- Provider Streaming Integration ---

async def openai_stream(
    prompt: str,
    model: str,
    api_key: str,
    stream: bool = True,
    **kwargs
) -> AsyncGenerator[dict, None]:
    """
    Stream completions from OpenAI API.
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": stream,
        **kwargs
    }
    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream("POST", url, headers=headers, json=payload) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[len("data: "):].strip()
                    if data == "[DONE]":
                        yield {"event": "done"}
                        break
                    try:
                        chunk = json.loads(data)
                        # OpenAI returns choices[0].delta.content for streamed tokens
                        token = chunk.get("choices", [{}])[0].get("delta", {}).get("content")
                        if token:
                            yield {
                                "event": "token",
                                "token": token,
                                "model": model,
                                "provider": "openai"
                            }
                    except Exception as e:
                        logger.exception("Error parsing OpenAI stream chunk")
                        yield {"event": "error", "error": str(e)}
                        break

async def anthropic_stream(
    prompt: str,
    model: str,
    api_key: str,
    stream: bool = True,
    **kwargs
) -> AsyncGenerator[dict, None]:
    """
    Stream completions from Anthropic API.
    """
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": model,
        "max_tokens": 1024,
        "stream": stream,
        "messages": [{"role": "user", "content": prompt}],
        **kwargs
    }
    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream("POST", url, headers=headers, json=payload) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[len("data: "):].strip()
                    if data == "[DONE]":
                        yield {"event": "done"}
                        break
                    try:
                        chunk = json.loads(data)
                        # Anthropic returns content_block.delta.text for streamed tokens
                        token = chunk.get("delta", {}).get("text")
                        if token:
                            yield {
                                "event": "token",
                                "token": token,
                                "model": model,
                                "provider": "anthropic"
                            }
                    except Exception as e:
                        logger.exception("Error parsing Anthropic stream chunk")
                        yield {"event": "error", "error": str(e)}
                        break

async def generate_completion(
    provider: str,
    prompt: str,
    model: str,
    api_key: str,
    stream: bool = True,
    **kwargs
) -> AsyncGenerator[dict, None]:
    """
    Unified streaming generator for different providers.
    """
    if provider == "openai":
        async for event in openai_stream(prompt, model, api_key, stream=stream, **kwargs):
            yield event
    elif provider == "anthropic":
        async for event in anthropic_stream(prompt, model, api_key, stream=stream, **kwargs):
            yield event
    else:
        yield {"event": "error", "error": f"Unknown provider: {provider}"}

# --- SSE Endpoint Implementation ---

async def sse_event_generator(
    request: Request,
    request_id: str,
    provider: str,
    prompt: str,
    model: str,
    api_key: str,
    **kwargs
) -> AsyncGenerator[str, None]:
    """
    Async generator yielding SSE events.
    """
    tokens_used = 0
    try:
        # Track connection
        logger.info(f"Client connected: {request_id}")
        last_event = asyncio.get_event_loop().time()
        provider_stream = generate_completion(
            provider=provider,
            prompt=prompt,
            model=model,
            api_key=api_key,
            stream=True,
            **kwargs
        )
        async for event in provider_stream:
            if await request.is_disconnected():
                logger.info(f"Client disconnected: {request_id}")
                break
            last_event = asyncio.get_event_loop().time()
            if event["event"] == "token":
                tokens_used += 1
                event["tokens_used"] = tokens_used
                yield format_sse_event("token", event)
            elif event["event"] == "error":
                yield format_sse_event("error", event)
                break
            elif event["event"] == "done":
                event["tokens_used"] = tokens_used
                event["model"] = model
                event["provider"] = provider
                yield format_sse_event("done", event)
                break
            await asyncio.sleep(0)  # Yield control

        # Heartbeat loop (if stream is long-running)
        while not await request.is_disconnected():
            now = asyncio.get_event_loop().time()
            if now - last_event > HEARTBEAT_INTERVAL:
                yield ": heartbeat\n\n"
                last_event = now
            await asyncio.sleep(HEARTBEAT_INTERVAL)
    except asyncio.CancelledError:
        logger.info(f"Stream cancelled: {request_id}")
    except Exception as e:
        logger.exception("Unhandled SSE error")
        yield format_sse_event("error", {"error": str(e)})
    finally:
        # Clean up connection
        active_connections.pop(request_id, None)
        logger.info(f"Connection closed: {request_id}")

@app.get("/stream/{request_id}")
async def stream_response(
    request: Request,
    request_id: str,
    provider: str,
    prompt: str,
    model: str,
    api_key: str
):
    """
    SSE endpoint for streaming completions.
    """
    if request_id in active_connections:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Request ID already in use"
        )
    generator = sse_event_generator(
        request=request,
        request_id=request_id,
        provider=provider,
        prompt=prompt,
        model=model,
        api_key=api_key
    )
    response = EventSourceResponse(generator)
    active_connections[request_id] = response
    return response

# --- Optional: Endpoint to list active connections ---

@app.get("/connections")
async def list_connections():
    return {"active_connections": list(active_connections.keys())}