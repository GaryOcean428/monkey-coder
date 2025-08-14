from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

# --- 1. Mount Next.js static files ---
frontend_dir = Path(__file__).parent.parent / "web" / "out"
app.mount("/_next", StaticFiles(directory=frontend_dir / "_next"), name="next-static")
app.mount("/static", StaticFiles(directory=frontend_dir / "static"), name="static")

# --- 2. Move all API routers under /api ---
from .routes import api_router  # Import your APIRouter instance
app.include_router(api_router, prefix="/api")

# --- 3. Serve index.html for all other routes (SSR fallback) ---
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_spa(request: Request, full_path: str):
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>Frontend not built</h1>", status_code=500)