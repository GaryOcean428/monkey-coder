# Railway Deployment Verification Guide

## Overview
This document provides verification steps for the fixed Railway deployment configurations for the monkey-coder project.

## Changes Summary

### 1. Root Service (monkey-coder)
**Service Type:** Unified Python FastAPI + Static Frontend  
**Configuration File:** `/railpack.json`

**Key Changes:**
- ✅ Provider changed from `node` to `python`
- ✅ Added both Python 3.12 and Node.js 20 for hybrid deployment
- ✅ Start command uses `run_server.py` which serves both API and frontend
- ✅ Added health check: `/health` with 300s timeout
- ✅ Added restart policy: `ON_FAILURE`
- ✅ Requirements path: `/app/requirements.txt` (absolute)

**Start Command:**
```bash
/app/.venv/bin/python run_server.py
```

**Build Process:**
1. Creates Python virtual environment at `/app/.venv`
2. Installs Python dependencies from `/app/requirements.txt`
3. Installs Node.js dependencies with Yarn 4.9.2
4. Builds Next.js frontend to `packages/web/out`

**Runtime:**
- Serves FastAPI backend on `$PORT`
- Mounts static frontend files from `packages/web/out`
- Health check available at `/health` and `/api/health`

### 2. Backend Service (monkey-coder-backend)
**Service Type:** Python FastAPI API  
**Configuration File:** `/services/backend/railpack.json`

**Key Changes:**
- ✅ Requirements path: `/app/requirements.txt` (absolute, fixed)
- ✅ Added health check: `/api/health` with 120s timeout
- ✅ Added restart policy: `ON_FAILURE`
- ✅ PYTHONPATH includes `/app/packages/core`
- ✅ Python version: 3.12

**Start Command:**
```bash
/app/.venv/bin/python -m uvicorn monkey_coder.app.main:app --host 0.0.0.0 --port $PORT
```

**PYTHONPATH:**
```
/app:/app/packages/core
```

### 3. ML Service (monkey-coder-ml)
**Service Type:** Python FastAPI ML Service  
**Configuration File:** `/services/ml/railpack.json`

**Key Changes:**
- ✅ Start command fixed: `cd /app/services/ml && uvicorn ml_server:app` (was broken)
- ✅ Requirements path: `/app/requirements.txt` (absolute, fixed)
- ✅ PYTHONPATH includes `/app/packages/core` (was missing)
- ✅ Added health check: `/api/health` with 120s timeout
- ✅ Added restart policy: `ON_FAILURE`
- ✅ Python version: 3.12

**Start Command:**
```bash
cd /app/services/ml && /app/.venv/bin/python -m uvicorn ml_server:app --host 0.0.0.0 --port $PORT
```

**PYTHONPATH:**
```
/app:/app/packages/core:/app/services/ml
```

### 4. Python Version Standardization
**Files Added:**
- `/services/backend/.python-version` → `3.12`
- `/services/ml/.python-version` → `3.12`

**Files Updated:**
- `/services/sandbox/Dockerfile` → Base image changed from `python:3.11-slim` to `python:3.12-slim`

## Verification Checklist

### Pre-Deployment Validation
- [x] All railpack.json files are valid JSON
- [x] Python version set to 3.12 in all configurations
- [x] Requirements.txt path uses absolute `/app/requirements.txt`
- [x] Health check endpoints exist in code
- [x] PYTHONPATH includes necessary paths

### Post-Deployment Testing

#### Root Service (Unified Deployment)
```bash
# Test health endpoint
curl -f https://your-railway-domain.railway.app/health

# Verify API is accessible
curl -f https://your-railway-domain.railway.app/api/health

# Test frontend is served
curl -f https://your-railway-domain.railway.app/ | grep "<!DOCTYPE html>"
```

#### Backend Service
```bash
# Test health endpoint
curl -f https://backend-domain.railway.app/api/health

# Verify service info
curl -f https://backend-domain.railway.app/health/comprehensive
```

#### ML Service
```bash
# Test health endpoint
curl -f https://ml-domain.railway.app/health

# Test API health alias
curl -f https://ml-domain.railway.app/api/health
```

## Railway Dashboard Configuration

### Root Service Settings
```
Service Name: monkey-coder
Root Directory: /
Build Command: (auto-detected from railpack.json)
Start Command: (auto-detected from railpack.json)
Health Check Path: /health
Health Check Timeout: 300
Python Version: 3.12
Node Version: 20
```

### Backend Service Settings
```
Service Name: monkey-coder-backend
Root Directory: /
Build Command: (auto-detected from services/backend/railpack.json)
Start Command: (auto-detected)
Health Check Path: /api/health
Health Check Timeout: 120
Python Version: 3.12

Environment Variables:
  - PYTHONPATH=/app:/app/packages/core
  - ML_SERVICE_URL=http://${{monkey-coder-ml.RAILWAY_PRIVATE_DOMAIN}}
  - LOG_LEVEL=info
```

### ML Service Settings
```
Service Name: monkey-coder-ml
Root Directory: /
Build Command: (auto-detected from services/ml/railpack.json)
Start Command: (auto-detected)
Health Check Path: /api/health
Health Check Timeout: 120
Python Version: 3.12

Environment Variables:
  - PYTHONPATH=/app:/app/packages/core:/app/services/ml
  - TRANSFORMERS_CACHE=/app/.cache/huggingface
  - CUDA_VISIBLE_DEVICES=0
  - LOG_LEVEL=info
```

## Common Issues and Solutions

### Issue: Requirements not found
**Symptom:** `FileNotFoundError: [Errno 2] No such file or directory: 'requirements.txt'`  
**Solution:** All railpack.json files now use absolute path `/app/requirements.txt`

### Issue: ML service cannot import from core
**Symptom:** `ModuleNotFoundError: No module named 'monkey_coder'`  
**Solution:** ML service PYTHONPATH now includes `/app/packages/core`

### Issue: ML service module not found
**Symptom:** `ModuleNotFoundError: No module named 'services.ml.ml_server'`  
**Solution:** Start command now uses `cd /app/services/ml` before running uvicorn

### Issue: Frontend not served in root deployment
**Symptom:** 404 on root URL  
**Solution:** Root service now uses `run_server.py` which mounts static files from `packages/web/out`

### Issue: Health check failing
**Symptom:** Railway shows service as unhealthy  
**Solutions:**
- Root service: Check `/health` endpoint (300s timeout)
- Backend: Check `/api/health` endpoint (120s timeout)
- ML: Check `/api/health` endpoint (120s timeout)

## Deployment Order

For fresh deployment, follow this order:
1. Deploy ML service first (lowest dependency)
2. Deploy Backend service (depends on ML service URL)
3. Deploy Root service (unified deployment)

## Rollback Plan

If deployment fails:
1. Check Railway logs for specific errors
2. Verify environment variables are set correctly
3. Ensure all required secrets are configured
4. Check health check endpoints are responding
5. Verify DATABASE_URL and other service references

## Success Criteria

All services deployed successfully when:
- ✅ All health checks are passing
- ✅ Root service serves both API and frontend
- ✅ Backend service can communicate with ML service
- ✅ No import or module errors in logs
- ✅ Services restart automatically on failure
- ✅ Python 3.12 is used consistently

## Additional Notes

- The unified root deployment (run_server.py) is the recommended approach
- All services use virtual environments at `/app/.venv`
- Health check timeouts are appropriate for service complexity
- Restart policies ensure services recover from transient failures
- PYTHONPATH configurations enable proper module imports
