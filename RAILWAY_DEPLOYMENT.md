# Railway Deployment Configuration Guide

## Overview

This monorepo contains three Railway services that need to be configured separately:
1. **Frontend (monkey-coder)**: Next.js static export served with `serve`
2. **Backend (monkey-coder-backend)**: FastAPI Python service
3. **ML (monkey-coder-ml)**: Python ML service with transformer models

## Service Configuration

### 1. Frontend Service (monkey-coder)

**Railway Service Settings:**
- **Root Directory**: `/` (or leave blank)
- **Build Provider**: Use `railpack.json` in root directory
- **Config File**: `/railpack.json`

**Important Notes:**
- The root directory contains both Python and Node.js files
- Railway must use the railpack.json which specifies `"provider": "node"`
- If Railway auto-detects Python, ensure the service is using the correct railpack.json

**Railpack Configuration:**
```json
{
  "build": {
    "provider": "node",
    "packages": {
      "node": "20"
    }
  }
}
```

### 2. Backend Service (monkey-coder-backend)

**Railway Service Settings:**
- **Root Directory**: `/services/backend` OR `/` with backend railpack.json
- **Build Provider**: Use `railpack.json`
- **Config File**: `/services/backend/railpack.json`

**Environment Variables Required:**
- `LOG_LEVEL=info`
- `HEALTH_CHECK_PATH=/api/health`
- `PYTHONPATH=/app:/app/packages/core`
- `ML_SERVICE_URL=http://${{monkey-coder-ml.RAILWAY_PRIVATE_DOMAIN}}`

**Start Command:**
```bash
/app/.venv/bin/python -m uvicorn monkey_coder.app.main:app --host 0.0.0.0 --port $PORT
```

### 3. ML Service (monkey-coder-ml)

**Railway Service Settings:**
- **Root Directory**: `/services/ml` OR `/` with ML railpack.json
- **Build Provider**: Use `railpack.json`
- **Config File**: `/services/ml/railpack.json`

**Environment Variables Required:**
- `LOG_LEVEL=info`
- `HEALTH_CHECK_PATH=/api/health`
- `PYTHONPATH=/app:/app/services/ml`
- `CUDA_VISIBLE_DEVICES=0`
- `TRANSFORMERS_CACHE=/app/.cache/huggingface`

**Start Command:**
```bash
/app/.venv/bin/python -m uvicorn services.ml.ml_server:app --host 0.0.0.0 --port $PORT
```

## Critical Fixes Applied

### Issue 1: Frontend Yarn Not Found
**Problem**: Railway was auto-detecting Python instead of Node.js for frontend service
**Fix**: Updated `/railpack.json` to use proper Railpack v1 schema with explicit steps structure

### Issue 2: Backend/ML Runtime Failure
**Problem**: `.venv/bin/python: No such file or directory`
**Cause**: Start commands used relative paths that didn't work at runtime
**Fix**: Changed all Python paths to absolute paths (`/app/.venv/bin/python`)

### Issue 3: .venv Excluded from Deployment
**Problem**: `.railwayignore` was excluding `.venv/` directory
**Fix**: Removed `.venv/` from `.railwayignore` to ensure venv persists to runtime

## Health Checks

All services are configured with health check endpoints:

- **Frontend**: `GET /` (timeout: 300s)
- **Backend**: `GET /api/health` (timeout: 300s)
- **ML**: `GET /api/health` (timeout: 600s - longer due to model loading)

## Troubleshooting

### Frontend fails with "yarn: not found"
- Verify Railway service is using `/railpack.json`
- Check that railpack.json has `"provider": "node"` in the build section
- Ensure Railway isn't detecting Python instead of Node.js

### Backend/ML fails with "No such file or directory"
- Verify start command uses absolute path: `/app/.venv/bin/python`
- Check that `.venv` is not excluded in `.railwayignore`
- Ensure environment variables include correct PATH and PYTHONPATH

### Health check timeout
- Backend/ML services may take time to start (installing dependencies, loading models)
- Health check timeouts are set appropriately (300s for backend, 600s for ML)
- Check deploy logs for startup errors

## Build Time Expectations

- **Frontend**: 2-3 minutes (Node.js dependencies + Next.js build)
- **Backend**: 3-4 minutes (Python dependencies)
- **ML**: 4-6 minutes (Python + large ML dependencies like torch, transformers)

## Notes

- All services use Railway Railpack builder (v0.9.1+)
- Python services use Python 3.12
- Frontend uses Node.js 20 with Yarn 4.9.2
- Virtual environments are created at `/app/.venv` during build and must persist to runtime
