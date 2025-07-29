#!/usr/bin/env python3
"""
Development server for Monkey Coder API.
Simplified version without complex dependencies.
"""

import os
import logging
import secrets
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple API key validation
def validate_api_key(authorization: str = Header(None)):
    """Simple API key validation."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Remove "Bearer " prefix if present
    api_key = authorization.replace("Bearer ", "").strip()
    
    # Validate format (mk-* and longer than 10 chars)
    if not api_key.startswith('mk-') or len(api_key) <= 10:
        raise HTTPException(status_code=401, detail="Invalid API key format")
    
    return api_key

# Create FastAPI app
app = FastAPI(
    title="Monkey Coder API",
    description="AI-powered code generation and analysis API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    components: Dict[str, str] = {
        "api": "active",
        "authentication": "active"
    }

class FileData(BaseModel):
    path: str
    content: str
    type: str

class Context(BaseModel):
    user_id: str
    session_id: str
    environment: str
    timeout: Optional[int] = 30
    max_tokens: Optional[int] = 4096
    temperature: Optional[float] = 0.7

class SuperClaudeConfig(BaseModel):
    persona: str = "assistant"
    slash_commands: list = []
    context_window: int = 32768
    use_markdown_spec: bool = True
    custom_instructions: Optional[str] = None

class ExecuteRequest(BaseModel):
    task_id: str
    task_type: str
    prompt: str = Field(..., description="Task or code generation prompt")
    files: Optional[list[FileData]] = Field(default=[], description="Input files")
    context: Context
    superclaude_config: SuperClaudeConfig
    preferred_providers: list[str] = ["openai"]
    model_preferences: Dict[str, str] = {}
    model_config: Optional[Dict[str, Any]] = {}

class ExecuteResponse(BaseModel):
    task_id: str
    status: str = "completed"
    result: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class UsageResponse(BaseModel):
    api_key_hash: str
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    current_month: Dict[str, Any] = {}

# Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Monkey Coder API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse()

@app.post("/v1/execute", response_model=ExecuteResponse)
async def execute_task(
    request: ExecuteRequest,
    api_key: str = Depends(validate_api_key)
):
    """Execute AI task."""
    task_id = f"task_{secrets.token_hex(8)}"
    
    logger.info(f"Executing task {task_id} for API key {api_key[:15]}...")
    
    # Mock response for development
    persona = request.superclaude_config.persona
    task_type = request.task_type
    
    if task_type == 'chat':
        result = {
            "result": f"Hello! I'm your {persona} assistant. You said: '{request.prompt}'. I'm a mock AI response for development. How can I help you with coding today?",
            "provider": request.preferred_providers[0] if request.preferred_providers else "openai",
            "model": "gpt-4.1-mock",
            "persona": persona
        }
    else:
        result = {
            "result": f"# Generated code for: {request.prompt}\nprint('Hello from Monkey Coder!')\n\n# This is a mock response for task type: {task_type}",
            "explanation": f"This code implements: {request.prompt}",
            "provider": request.preferred_providers[0] if request.preferred_providers else "openai",
            "model": "gpt-4.1-mock",
            "persona": persona
        }
    
    return ExecuteResponse(
        task_id=task_id,
        result=result
    )

@app.post("/v1/execute/stream")
async def execute_task_stream(
    request: ExecuteRequest,
    api_key: str = Depends(validate_api_key)
):
    """Execute AI task with streaming (simplified mock)."""
    from fastapi.responses import StreamingResponse
    import json
    import asyncio
    
    task_id = f"task_{secrets.token_hex(8)}"
    logger.info(f"Executing streaming task {task_id} for API key {api_key[:15]}...")
    
    async def event_stream():
        # Start event
        yield f"data: {json.dumps({'type': 'start', 'data': {'task_id': task_id}})}\n\n"
        await asyncio.sleep(0.1)  # Small delay for realism
        
        # Progress event
        yield f"data: {json.dumps({'type': 'progress', 'progress': {'step': 'Processing request', 'percentage': 50}})}\n\n"
        await asyncio.sleep(0.2)  # Small delay for realism
        
        # Mock response for development
        persona = request.superclaude_config.persona
        task_type = request.task_type
        
        if task_type == 'chat':
            result = {
                "result": f"Hello! I'm your {persona} assistant. You said: '{request.prompt}'. I'm a mock AI response for development. How can I help you with coding today?",
                "provider": request.preferred_providers[0] if request.preferred_providers else "openai",
                "model": "gpt-4.1-mock",
                "persona": persona
            }
        else:
            result = {
                "result": f"# Generated code for: {request.prompt}\nprint('Hello from Monkey Coder!')\n\n# This is a mock response for task type: {task_type}",
                "explanation": f"This code implements: {request.prompt}",
                "provider": request.preferred_providers[0] if request.preferred_providers else "openai",
                "model": "gpt-4.1-mock",
                "persona": persona
            }
        
        response = ExecuteResponse(
            task_id=task_id,
            result=result
        )
        
        # Complete event
        yield f"data: {json.dumps({'type': 'complete', 'data': response.dict()})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

@app.get("/v1/billing/usage", response_model=UsageResponse)
async def get_billing_usage(api_key: str = Depends(validate_api_key)):
    """Get billing usage information."""
    # Mock response for development
    import hashlib
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
    
    return UsageResponse(
        api_key_hash=api_key_hash,
        total_requests=42,
        total_tokens=1337,
        total_cost=5.67,
        current_month={
            "requests": 15,
            "tokens": 500,
            "cost": 2.34
        }
    )

@app.get("/v1/models")
async def list_models(api_key: str = Depends(validate_api_key)):
    """List available AI models."""
    return {
        "models": [
            {"id": "gpt-4.1", "provider": "openai", "description": "GPT-4.1 flagship model"},
            {"id": "gpt-4.1-mini", "provider": "openai", "description": "GPT-4.1 Mini model"},
            {"id": "claude-sonnet-4-20250514", "provider": "anthropic", "description": "Claude Sonnet 4"},
            {"id": "qwen/qwen3-32b", "provider": "groq", "description": "Qwen 3 32B via Groq"}
        ]
    }

@app.get("/v1/providers")
async def list_providers(api_key: str = Depends(validate_api_key)):
    """List available AI providers."""
    return {
        "providers": [
            {"id": "openai", "name": "OpenAI", "status": "active"},
            {"id": "anthropic", "name": "Anthropic", "status": "active"},
            {"id": "google", "name": "Google GenAI", "status": "active"},
            {"id": "qwen", "name": "Qwen", "status": "active"}
        ]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    
    print(f"""
🚀 MONKEY CODER API SERVER STARTING
======================================
📍 URL: http://localhost:{port}
📚 Docs: http://localhost:{port}/docs
🔍 Health: http://localhost:{port}/health

🔑 API Key Format: mk-dev-<random>
Example: mk-dev-EeSR4-BBpJsUTZCgIUjbdN3-_WoUIcgvyFn1VU6iKWU

To test with curl:
curl -H "Authorization: Bearer mk-dev-EeSR4-BBpJsUTZCgIUjbdN3-_WoUIcgvyFn1VU6iKWU" http://localhost:{port}/health

Ready for requests! 🎉
""")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
