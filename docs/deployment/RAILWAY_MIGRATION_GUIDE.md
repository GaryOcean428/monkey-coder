# Railway Migration: AetherOS → Monkey Project

> **⚠️ HISTORICAL REFERENCE ONLY**
>
> This document describes the migration from AetherOS to Monkey project structure.
> Much of the guidance here has been superseded by newer best practices.
>
> **For current deployment guidance, see:**
> - [docs/deployment/railway-configuration.md](docs/deployment/railway-configuration.md) - Current guide
>
> **Archived:** 2025-10-16
>
> This file is preserved for historical reference only.

---

## Overview
Moving monkey-coder services from AetherOS to Monkey project using **railpack.json** configurations.

**Key Point**: All build/deploy configs are in railpack.json files - Railway uses these automatically via Railpack builder.

## Architecture

```
monkey-coder/
├─ railpack.json                    # Frontend (root deployment)
└─ services/
   ├─ frontend/railpack.json        # Same as root (reference)
   ├─ backend/railpack.json         # Backend API (lightweight)
   └─ ml/railpack.json              # ML service (PyTorch + transformers)
```

## Railpack Best Practices (from monkey1/monkey2)

✅ **DO**:
- Use `$schema: "https://schema.railpack.com"`
- Use `steps` with `install` and `build`
- Use `inputs: [{ "step": "install" }]` for build dependencies
- Use `uv` for Python (fast, modern)
- Use `corepack` + Yarn 4.9.2 for Node
- Use `healthcheckPath` and `healthcheckTimeout`
- Put env vars in `deploy.variables`
- Use `host ::` for IPv4+IPv6 support

❌ **DON'T**:
- Use `build.provider` or `build.packages` (old Nixpacks syntax)
- Use separate `build.env` and `deploy.env` (use `deploy.variables`)
- Use `healthCheckPath` (old syntax - use `healthcheckPath`)
- Use `0.0.0.0` (use `::` instead)

## Migration Steps

### 1. Link to Monkey Project

```bash
cd /home/braden/Desktop/Dev/monkey-projects/monkey-coder
railway link
```
- Select: **Monkey**
- Environment: **production**

### 2. Create Frontend Service

```bash
railway service create
```
- Name: `monkey-coder-frontend`
- Root directory: `/` (default)
- Uses: `/railpack.json` (auto-detected)

**Add Custom Domain**:
```bash
railway domain add coder.fastmonkey.au
```

The frontend railpack.json handles:
- Yarn 4.9.2 with immutable installs
- Next.js workspace build
- Static export to `packages/web/out/`
- Serve with `serve` package

### 3. Create Backend Service

```bash
railway service create
```
- Name: `monkey-coder-backend`

**Set Root Directory**:
```bash
railway service
# Select: monkey-coder-backend
railway variables set RAILWAY_ROOT_DIRECTORY="services/backend"
```

The backend railpack.json handles:
- `uv pip install -r services/backend/requirements.txt` (lightweight - NO ML!)
- Python 3.12/3.13 auto-detected
- uvicorn with 2 workers + uvloop
- Health check `/api/health`
- All env vars pre-configured

**Add Required Environment Variables**:
```bash
# API Keys
railway variables set ANTHROPIC_API_KEY="sk-ant-..."
railway variables set OPENAI_API_KEY="sk-..."
railway variables set GEMINI_API_KEY="..."
railway variables set GROQ_API_KEY="gsk_..."
railway variables set TAVILY_API_KEY="tvly-..."

# Database (if using shared Postgres)
railway variables set DATABASE_URL="\${{Postgres.DATABASE_URL}}"

# Redis (if using shared Redis)
railway variables set REDIS_URL="\${{Redis.REDIS_URL}}"
```

### 4. Create ML Service

```bash
railway service create
```
- Name: `monkey-coder-ml`

**Set Root Directory**:
```bash
railway service
# Select: monkey-coder-ml
railway variables set RAILWAY_ROOT_DIRECTORY="services/ml"
```

The ML railpack.json handles:
- `uv pip install -r services/ml/requirements.txt` (PyTorch + transformers = 2.5GB)
- Python 3.13 auto-detected
- uvicorn with 1 worker (ML models are memory-heavy)
- Health check `/api/health`
- Transformer cache configuration
- CUDA device selection

**Note**: This service takes 5-10 minutes to build due to large ML dependencies.

### 5. Deploy All Services

```bash
# Commit railpack.json changes
git add .
git commit -m "Configure Railway services with railpack.json

- Update all railpack.json files to follow monkey1/monkey2 best practices
- Use uv for fast Python installs
- Use Yarn 4.9.2 with corepack
- Configure proper healthchecks and restart policies
- Separate backend (lightweight) from ML (heavy) requirements

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to trigger deployments
git push origin main
```

Railway will automatically:
1. Detect railpack.json in each service's root directory
2. Use Railpack builder (not Nixpacks)
3. Execute `steps.install` → `steps.build`
4. Run `deploy.startCommand`
5. Check health at `deploy.healthcheckPath`

### 6. Verify Deployments

**Frontend**:
```bash
curl https://coder.fastmonkey.au/
# Should return Next.js static site
```

**Backend**:
```bash
railway service
# Select: monkey-coder-backend
railway logs --follow

# Check health
curl https://monkey-coder-backend-production.up.railway.app/api/health
```

**ML Service**:
```bash
railway service
# Select: monkey-coder-ml
railway logs --follow

# Check health (may take 5-10 mins to load models)
curl https://monkey-coder-ml-production.up.railway.app/api/health
```

## Railpack Configuration Summary

### Frontend (`/railpack.json`)
```json
{
  "steps": {
    "install": ["corepack enable", "yarn install"],
    "build": ["yarn workspace @monkey-coder/web build", "yarn global add serve"]
  },
  "deploy": {
    "startCommand": "serve -s packages/web/out -l $PORT",
    "healthcheckPath": "/"
  }
}
```

### Backend (`services/backend/railpack.json`)
```json
{
  "steps": {
    "install": ["pip install -U pip uv", "uv pip install -r services/backend/requirements.txt --system"]
  },
  "deploy": {
    "startCommand": "python -m uvicorn monkey_coder.app.main:app --host :: --port $PORT --workers 2",
    "healthcheckPath": "/api/health",
    "variables": {
      "PYTHONPATH": "/app:/app/packages/core",
      "ML_SERVICE_URL": "http://${{monkey-coder-ml.RAILWAY_PRIVATE_DOMAIN}}"
    }
  }
}
```

### ML (`services/ml/railpack.json`)
```json
{
  "steps": {
    "install": ["pip install -U pip uv", "uv pip install -r services/ml/requirements.txt --system"]
  },
  "deploy": {
    "startCommand": "python -m uvicorn services.ml.ml_server:app --host :: --port $PORT --workers 1",
    "healthcheckPath": "/api/health",
    "variables": {
      "TRANSFORMERS_CACHE": "/app/.cache/huggingface",
      "HF_HOME": "/app/.cache/huggingface",
      "CUDA_VISIBLE_DEVICES": "0"
    }
  }
}
```

## Troubleshooting

### Build Fails: "lstat /.vscode/extensions.json: no such file or directory"
✅ **FIXED**: Removed from `.dockerignore`

### Build Fails: "no space left on device"
✅ **FIXED**: Backend now uses `services/backend/requirements.txt` (no PyTorch)
- Backend: ~500MB (FastAPI, AI SDKs, auth)
- ML: ~2.5GB (PyTorch, transformers, CUDA)

### Domain Not Migrating
1. Remove domain from AetherOS service in Railway dashboard
2. Add to Monkey project frontend service
3. Verify DNS: `dig coder.fastmonkey.au`

### Backend Can't Connect to ML Service
- Ensure `ML_SERVICE_URL` uses `RAILWAY_PRIVATE_DOMAIN` (internal networking)
- Check ML service logs for health check failures
- ML service may take 5-10 mins to load models on first deploy

### CLI Still Shows 405 Error
- Wait for backend deployment to complete
- Backend must be running the latest code with `/api/v1/auth/login` POST endpoint
- Check Railway logs: `railway logs` (should show FastAPI startup)

## Post-Migration Cleanup

Once verified working:

```bash
# Switch to AetherOS project
railway link
# Select: AetherOS

# Delete old services
railway service
# Select each old service
railway service delete
```

## Files Modified

- ✅ `.dockerignore` - Removed `.vscode/extensions.json`
- ✅ `packages/cli/src/cli.ts` - Dynamic version from package.json
- ✅ `packages/cli/src/api-client.ts` - Dynamic User-Agent
- ✅ `railpack.json` - Frontend config (Railpack format)
- ✅ `services/backend/railpack.json` - Backend config (Railpack format)
- ✅ `services/ml/railpack.json` - ML config (Railpack format)
- ✅ `services/frontend/railpack.json` - Frontend reference (matches root)

## Next Steps

1. ✅ Push changes: `git push origin main`
2. ⏳ Wait for Railway deployments (frontend: 2-3 mins, backend: 3-5 mins, ML: 8-12 mins)
3. ✅ Test CLI: `monkey auth login`
4. 📦 Publish updated packages:
   - `monkey-coder-cli` v1.5.0 → npm
   - `monkey-coder-core` v1.2.0 → PyPI
5. 🎯 Add code generation to monkey1/monkey2
6. 🔗 Add Ona integration to monkey1
