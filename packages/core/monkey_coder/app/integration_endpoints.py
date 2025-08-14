from fastapi import FastAPI, Depends, HTTPException, status, Request, APIRouter
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from typing import List

# Import your modules (implementations not shown here)
from auth import (
    login_user, refresh_jwt, get_auth_status, logout_user,
    get_current_user, APIKeyHeader, JWTBearer
)
from streaming import stream_ai_tokens
from context import (
    execute_with_context, get_conversation_context, store_response_in_context
)
from sessions import (
    list_user_sessions, get_session_history, clear_session
)

app = FastAPI(title="AI Platform API")

# --- Streaming Endpoint ---
stream_router = APIRouter(prefix="/v1/stream", tags=["streaming"])

@stream_router.get("/{request_id}")
async def stream_response(
    request_id: str,
    user=Depends(get_current_user)
):
    try:
        async def event_generator():
            async for token in stream_ai_tokens(request_id, user):
                yield {"data": token}
        return EventSourceResponse(event_generator())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Auth Endpoints ---
auth_router = APIRouter(prefix="/v1/auth", tags=["auth"])

@auth_router.post("/login")
async def login(data: dict):
    # data: {username, password}
    jwt_token, api_key = await login_user(data)
    return {"jwt": jwt_token, "api_key": api_key}

@auth_router.post("/refresh")
async def refresh(token: str = Depends(JWTBearer())):
    new_token = await refresh_jwt(token)
    return {"jwt": new_token}

@auth_router.get("/status")
async def status(user=Depends(get_current_user)):
    return await get_auth_status(user)

@auth_router.post("/logout")
async def logout(user=Depends(get_current_user)):
    await logout_user(user)
    return {"detail": "Logged out"}

# --- Context-aware Execute Endpoint ---
execute_router = APIRouter(prefix="/v1", tags=["execute"])

@execute_router.post("/execute")
async def execute(
    payload: dict,
    session_id: str,
    user=Depends(get_current_user)
):
    # Retrieve conversation context
    context = await get_conversation_context(user, session_id)
    # Execute with context
    response = await execute_with_context(payload, context)
    # Store response in context
    await store_response_in_context(user, session_id, response)
    return response

# --- Session Management Endpoints ---
sessions_router = APIRouter(prefix="/v1/sessions", tags=["sessions"])

@sessions_router.get("")
async def list_sessions(user=Depends(get_current_user)):
    return await list_user_sessions(user)

@sessions_router.get("/{session_id}")
async def get_session(session_id: str, user=Depends(get_current_user)):
    return await get_session_history(user, session_id)

@sessions_router.delete("/{session_id}")
async def delete_session(session_id: str, user=Depends(get_current_user)):
    await clear_session(user, session_id)
    return {"detail": "Session cleared"}

# --- Register Routers ---
app.include_router(auth_router)
app.include_router(stream_router)
app.include_router(execute_router)
app.include_router(sessions_router)

# --- Optional: Custom Exception Handlers, Middleware, etc. ---

# Example: Add CORS middleware if needed
# from fastapi.middleware.cors import CORSMiddleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# --- Main entrypoint (if running directly) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)