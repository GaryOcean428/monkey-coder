# Railway Configuration Guide

**Last Updated:** 2025-10-16
**Status:** ✅ Current and Verified

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Service Configuration](#service-configuration)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## Overview

Monkey Coder uses Railway for deployment with a **service-based architecture**. Each Railway service deploys from its own directory with a dedicated `railpack.json` configuration file.

### Key Principles

✅ **Service-Level Configuration**: Each service has its own `railpack.json` in `services/{service}/`
✅ **Modern Tooling**: Uses `uv` for Python, Yarn 4.9.2 for Node.js
✅ **IPv6 Support**: Binds to `::` for IPv4+IPv6 compatibility
✅ **Optimized Workers**: Backend uses 2 workers, ML uses 1 worker
✅ **Proper Timeouts**: Backend 300s, ML 600s (for slow model loading)

---

## Architecture

### Monorepo Structure

```
monkey-coder/
├── services/
│   ├── frontend/
│   │   └── railpack.json  ← Frontend configuration
│   ├── backend/
│   │   ├── railpack.json  ← Backend configuration
│   │   └── requirements.txt
│   └── ml/
│       ├── railpack.json  ← ML configuration
│       └── requirements.txt
├── packages/
│   ├── web/           ← Next.js static export
│   └── core/          ← Python core (shared)
```

### Railway Service Mapping

| Railway Service | Root Directory | Config File | Port | Purpose |
|----------------|---------------|-------------|------|---------|
| `monkey-coder-frontend` | `services/frontend/` | `railpack.json` | $PORT | Next.js static |
| `monkey-coder-backend` | `services/backend/` | `railpack.json` | $PORT | FastAPI + Auth |
| `monkey-coder-ml` | `services/ml/` | `railpack.json` | $PORT | PyTorch + Transformers |

---

## Quick Start

### Prerequisites

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link
```

### Deployment Steps

1. **Configure Service Root Directories**

   For each Railway service in the dashboard:

   **Settings → Service → Root Directory:**
   - Frontend: `services/frontend`
   - Backend: `services/backend`
   - ML: `services/ml`

2. **Set Environment Variables**

   See [Environment Variables](#environment-variables) section below.

3. **Deploy**

   ```bash
   # Deploy specific service
   railway up --service monkey-coder-backend

   # Or deploy all (if multi-service setup configured)
   git push  # Auto-deploys on push if GitHub connected
   ```

---

## Service Configuration

### Frontend Service

**File:** `services/frontend/railpack.json`

```json
{
  "$schema": "https://schema.railpack.com",
  "version": "1",
  "metadata": {
    "name": "monkey-coder-frontend",
    "description": "Next.js static export frontend"
  },
  "build": {
    "provider": "node",
    "packages": { "node": "20" }
  },
  "steps": {
    "install": {
      "commands": [
        "corepack enable && corepack prepare yarn@4.9.2 --activate",
        "yarn install --immutable"
      ]
    },
    "build": {
      "inputs": [{ "step": "install" }],
      "commands": [
        "yarn workspace @monkey-coder/web build",
        "yarn global add serve@14.2.4"
      ]
    }
  },
  "deploy": {
    "startCommand": "serve -s packages/web/out -l $PORT --no-clipboard",
    "healthcheckPath": "/",
    "healthcheckTimeout": 120,
    "restartPolicyType": "always"
  }
}
```

**Railway Settings:**
- Root Directory: `services/frontend`
- Build Command: (leave blank - railpack handles it)
- Start Command: (leave blank - railpack handles it)
- Health Check Path: `/`
- Health Check Timeout: 120 seconds

---

### Backend Service

**File:** `services/backend/railpack.json`

```json
{
  "$schema": "https://schema.railpack.com",
  "version": "1",
  "metadata": {
    "name": "monkey-coder-backend",
    "description": "FastAPI backend (lightweight - no ML)"
  },
  "build": {
    "provider": "python",
    "packages": { "python": "3.13" }
  },
  "steps": {
    "install": {
      "commands": [
        "pip install -U pip uv",
        "uv pip install -r services/backend/requirements.txt --system"
      ]
    }
  },
  "deploy": {
    "startCommand": "python -m uvicorn monkey_coder.app.main:app --host :: --port $PORT --workers 2 --loop uvloop",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

**Railway Settings:**
- Root Directory: `services/backend`
- Build Command: (leave blank - railpack handles it)
- Start Command: (leave blank - railpack handles it)
- Health Check Path: `/api/health`
- Health Check Timeout: 300 seconds

**Key Features:**
- **uv**: Modern Python package installer (faster than pip)
- **--system**: Installs packages system-wide (no venv needed in Railway)
- **--host ::**: Binds to IPv6 (includes IPv4)
- **--workers 2**: Multiple workers for performance
- **--loop uvloop**: High-performance event loop

---

### ML Service

**File:** `services/ml/railpack.json`

```json
{
  "$schema": "https://schema.railpack.com",
  "version": "1",
  "metadata": {
    "name": "monkey-coder-ml",
    "description": "ML inference with PyTorch + Transformers"
  },
  "build": {
    "provider": "python",
    "packages": { "python": "3.13" }
  },
  "steps": {
    "install": {
      "commands": [
        "pip install -U pip uv",
        "uv pip install -r services/ml/requirements.txt --system"
      ]
    }
  },
  "deploy": {
    "startCommand": "python -m uvicorn services.ml.ml_server:app --host :: --port $PORT --workers 1",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 600,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

**Railway Settings:**
- Root Directory: `services/ml`
- Build Command: (leave blank - railpack handles it)
- Start Command: (leave blank - railpack handles it)
- Health Check Path: `/api/health`
- Health Check Timeout: 600 seconds (ML models take time to load)

**Key Features:**
- **--workers 1**: Single worker (ML models are memory-intensive)
- **600s timeout**: ML model loading requires extended startup time
- **TRANSFORMERS_CACHE**: Caches Hugging Face models

---

## Environment Variables

### Frontend Variables

**Required:**
```bash
NODE_ENV=production
NEXT_OUTPUT_EXPORT=true
NEXT_TELEMETRY_DISABLED=1
YARN_ENABLE_TELEMETRY=0
NEXT_PUBLIC_API_URL=https://${BACKEND_DOMAIN}
```

**Setting via CLI:**
```bash
railway variables set \
  --service monkey-coder-frontend \
  NODE_ENV=production \
  NEXT_OUTPUT_EXPORT=true \
  NEXT_TELEMETRY_DISABLED=1 \
  NEXT_PUBLIC_API_URL="https://monkey-coder-backend-production.up.railway.app"
```

---

### Backend Variables

**Critical Secrets (Set First):**
```bash
# Generate secure secrets
JWT_SECRET_KEY=$(openssl rand -hex 32)
NEXTAUTH_SECRET=$(openssl rand -hex 32)

# Set secrets
railway variables set \
  --service monkey-coder-backend \
  JWT_SECRET_KEY="$JWT_SECRET_KEY" \
  NEXTAUTH_SECRET="$NEXTAUTH_SECRET" \
  OPENAI_API_KEY="sk-..." \
  ANTHROPIC_API_KEY="sk-ant-..."
```

**Required Variables:**
```bash
railway variables set \
  --service monkey-coder-backend \
  ENV=production \
  NODE_ENV=production \
  PYTHON_ENV=production \
  LOG_LEVEL=INFO \
  PYTHONPATH="/app:/app/packages/core" \
  PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  HOSTNAME="::" \
  ML_SERVICE_URL="http://${ML_PRIVATE_DOMAIN}"
```

**Using Railway References:**
```bash
# Reference ML service (private domain for internal communication)
ML_SERVICE_URL="http://${{monkey-coder-ml.RAILWAY_PRIVATE_DOMAIN}}"
```

**Optional (Production Features):**
```bash
# CORS
CORS_ORIGINS="https://coder.fastmonkey.au"
TRUSTED_HOSTS="coder.fastmonkey.au,*.railway.app,*.railway.internal"
ENABLE_SECURITY_HEADERS=true

# Redis (if using Railway Redis plugin)
SESSION_BACKEND=redis
RATE_LIMIT_BACKEND=redis
REDIS_URL="${REDIS_URL}"  # Auto-provided by Railway plugin

# Email (Resend)
RESEND_API_KEY="re_..."
NOTIFICATION_EMAIL_FROM="noreply@fastmonkey.au"
EMAIL_PROVIDER=resend

# Error Tracking
SENTRY_DSN="https://...@sentry.io/..."
```

---

### ML Variables

**Required:**
```bash
railway variables set \
  --service monkey-coder-ml \
  ENV=production \
  NODE_ENV=production \
  PYTHON_ENV=production \
  LOG_LEVEL=INFO \
  PYTHONPATH="/app:/app/services/ml" \
  PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  HOSTNAME="::" \
  TRANSFORMERS_CACHE="/app/.cache/huggingface" \
  HF_HOME="/app/.cache/huggingface" \
  CUDA_VISIBLE_DEVICES="0"
```

---

## Deployment

### Initial Deployment

1. **Create Railway Services**

   In Railway dashboard:
   - Create 3 new services: frontend, backend, ml
   - Connect to GitHub repository
   - Set Root Directory for each service (see [Quick Start](#quick-start))

2. **Configure Service Settings**

   For each service:
   - Set Root Directory
   - Leave Build/Start Commands blank (railpack handles it)
   - Configure Health Check path and timeout

3. **Set Environment Variables**

   Use Railway CLI or dashboard to set variables (see [Environment Variables](#environment-variables))

4. **Deploy**

   ```bash
   # Push to trigger deployment
   git push origin main

   # Or manually deploy
   railway up --service monkey-coder-backend
   ```

### Update Deployment

```bash
# Push changes
git push origin main

# Or force redeploy
railway redeploy --service monkey-coder-backend
```

### Rollback

```bash
# View deployment history
railway deployment list --service monkey-coder-backend

# Rollback to specific deployment
railway rollback <DEPLOYMENT_ID> --service monkey-coder-backend
```

---

## Troubleshooting

### Build Failures

**Problem:** `Nixpacks build failed`

**Solution:**
1. Verify railpack.json exists in service directory
2. Check syntax: `cat services/backend/railpack.json | jq '.'`
3. Ensure Root Directory is set correctly in Railway dashboard
4. Check build logs: `railway logs --service <SERVICE> --deployment`

---

### Health Check Failures

**Problem:** `Health check failed: service unavailable`

**Solution:**
1. Verify health endpoint exists and returns 200:
   ```bash
   # For backend/ML
   curl https://your-service.up.railway.app/api/health

   # For frontend
   curl https://your-service.up.railway.app/
   ```

2. Check if service is binding to correct host:
   - Must bind to `::` or `0.0.0.0`, NOT `localhost` or `127.0.0.1`
   - Verify in railpack.json: `--host ::`

3. Ensure PORT is read from environment:
   ```python
   # Python
   port = int(os.environ.get("PORT", 8000))
   ```

4. Increase timeout if service needs more startup time (especially ML)

---

### Port Binding Issues

**Problem:** `Application failed to respond`

**Solution:**
```python
# ❌ WRONG
app.listen(3000)  # Hardcoded port
app.run(host="127.0.0.1", port=5000)  # Wrong host

# ✅ CORRECT
port = int(os.environ.get("PORT", 8000))
app.run(host="::", port=port)  # IPv6 + IPv4
```

---

### Service Communication Issues

**Problem:** Backend can't reach ML service

**Solution:**
1. Use Railway's private domain (not public):
   ```bash
   # ✅ CORRECT (internal, fast)
   ML_SERVICE_URL="http://${{monkey-coder-ml.RAILWAY_PRIVATE_DOMAIN}}"

   # ❌ WRONG (external, slow)
   ML_SERVICE_URL="https://monkey-coder-ml-production.up.railway.app"
   ```

2. Verify variable reference syntax:
   ```bash
   # Template: ${{SERVICE_NAME.RAILWAY_PRIVATE_DOMAIN}}
   ```

3. Check if ML service is deployed and healthy

---

### Environment Variable Not Taking Effect

**Problem:** Changed variable but service still uses old value

**Solution:**
1. Variables require redeployment:
   ```bash
   railway redeploy --service monkey-coder-backend
   ```

2. Verify variable is set:
   ```bash
   railway variables --service monkey-coder-backend | grep MY_VAR
   ```

3. Check for typos in variable names (case-sensitive)

---

## Best Practices

### Configuration

✅ **Use service-level railpack.json** (in `services/{service}/`)
✅ **Set Root Directory** to service directory
✅ **Leave Build/Start commands blank** (let railpack handle it)
✅ **Use correct healthcheckPath syntax** (lowercase 'c')
✅ **Bind to `::`** for IPv4+IPv6 support
✅ **Read PORT from environment** (never hardcode)
✅ **Use Railway references** for service-to-service communication

### Security

✅ **Generate strong secrets** using `openssl rand -hex 32`
✅ **Never commit secrets** to git
✅ **Use Railway's secret storage** for sensitive values
✅ **Rotate secrets regularly** (every 60-90 days)
✅ **Use private domains** for internal service communication
✅ **Enable CORS** only for trusted domains

### Performance

✅ **Use uv** for faster Python package installation
✅ **Configure appropriate workers** (2 for backend, 1 for ML)
✅ **Use uvloop** for backend (high-performance event loop)
✅ **Cache dependencies** (node_modules, .venv, transformers)
✅ **Set appropriate timeouts** (300s backend, 600s ML)

---

## Migration Notes

### From Root-Level Configs

If you previously used root-level `railpack-*.json` files with `RAILWAY_CONFIG_FILE` variable:

**Old Approach:**
```bash
# ❌ OLD (deprecated)
Root Directory: /
RAILWAY_CONFIG_FILE=railpack-backend.json
```

**New Approach:**
```bash
# ✅ NEW (current)
Root Directory: services/backend
# No RAILWAY_CONFIG_FILE variable needed
```

**Migration Steps:**
1. Remove `RAILWAY_CONFIG_FILE` variable
2. Update Root Directory to service directory
3. Ensure `railpack.json` exists in service directory
4. Redeploy service

---

## Additional Resources

- [Railway Architecture](./railway-architecture.md) - Understanding Railway's build system
- [Railway Optimization](./railway-optimization.md) - Performance and monitoring
- [Railway MCP Setup](./railway-services-setup.md) - MCP integration
- [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) - Detailed deployment guide
- [RAILWAY_PRODUCTION_CHECKLIST.md](./RAILWAY_PRODUCTION_CHECKLIST.md) - Pre-deployment checklist

---

## Getting Help

- **GitHub Issues:** [Report bugs](https://github.com/GaryOcean428/monkey-coder/issues)
- **Railway Support:** [Railway Help Center](https://railway.app/help)
- **Railway Docs:** [docs.railway.app](https://docs.railway.app)

---

**Last Updated:** 2025-10-16
**Maintained By:** Monkey Coder Team
