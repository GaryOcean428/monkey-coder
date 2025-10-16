# Railway Deployment Configuration

> **⚠️ OUTDATED - SEE UPDATED GUIDE**
>
> This document contains outdated information about Railway deployment using root-level `railpack.json` files.
>
> **For current, accurate deployment instructions, see:**
> - [docs/deployment/railway-configuration.md](docs/deployment/railway-configuration.md) - Complete configuration guide
>
> **Last Updated:** 2025-01-16 (Archived 2025-10-16)
>
> This file is preserved for historical reference only.

---

# Railway Deployment Configuration - HISTORICAL

## 🚨 CRITICAL: Shared Monorepo Architecture

This repository uses a **Shared Monorepo** pattern with Yarn workspaces. All Railway services MUST be configured to operate from the **repository root**.

### Key Architecture Facts

1. **Railway Config File Location**: `railpack.json` at repository root
2. **Railway Behavior**: Always reads railpack.json from repo root, regardless of service `rootDirectory` settings
3. **Workspace Structure**: Yarn workspaces require execution from repo root where `package.json` is located
4. **Service Separation**: Logical separation via start commands, NOT via directory isolation

## ⚡ Quick Fix for Current Deployment Failures

### Problem Diagnosis

Current deployment failures show:
```
ERROR: sh: 1: cd: can't cd to packages/web
Build Command: cd packages/web && yarn install --frozen-lockfile && yarn build
Root Directory: services/frontend
```

**Root Cause**: Railway services configured with:
- ❌ Root Directory: `services/frontend` (WRONG)
- ❌ Manual build commands in Railway Dashboard (WRONG)
- ❌ Service railpack.json files being ignored (Railway reads root only)

### Solution

**ALL THREE SERVICES** must be configured in Railway Dashboard as follows:

#### Service: monkey-coder (Frontend)
```
Settings → Service:
  ├─ Root Directory: / (or leave BLANK)
  ├─ Build Command: LEAVE BLANK (uses railpack.json)
  └─ Start Command: LEAVE BLANK (uses railpack.json)

Settings → Config as Code:
  └─ Path: railpack.json (at repo root)

Settings → Environment Variables:
  ├─ NODE_ENV=production
  ├─ NEXT_OUTPUT_EXPORT=true
  ├─ NEXT_TELEMETRY_DISABLED=1
  ├─ NEXT_PUBLIC_API_URL=https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}
  └─ NEXT_PUBLIC_APP_URL=https://coder.fastmonkey.au
```

#### Service: monkey-coder-backend
```
Settings → Service:
  ├─ Root Directory: / (or leave BLANK)
  ├─ Build Command: LEAVE BLANK (uses railpack.json)
  └─ Start Command: LEAVE BLANK (uses railpack.json)

Settings → Environment Variables:
  ├─ PYTHON_ENV=production
  ├─ ML_SERVICE_URL=http://${{monkey-coder-ml.RAILWAY_PRIVATE_DOMAIN}}
  ├─ DATABASE_URL=${{Postgres.DATABASE_URL}}
  ├─ REDIS_URL=${{Redis.REDIS_URL}}
  ├─ OPENAI_API_KEY=${{...}}
  ├─ ANTHROPIC_API_KEY=${{...}}
  ├─ GROQ_API_KEY=${{...}}
  ├─ GOOGLE_API_KEY=${{...}}
  └─ XAI_API_KEY=${{...}}
```

#### Service: monkey-coder-ml
```
Settings → Service:
  ├─ Root Directory: / (or leave BLANK)
  ├─ Build Command: LEAVE BLANK (uses railpack.json)
  └─ Start Command: LEAVE BLANK (uses railpack.json)

Settings → Environment Variables:
  ├─ PYTHON_ENV=production
  └─ TRANSFORMERS_CACHE=/app/.cache/huggingface
```

## 📋 Root railpack.json Configuration

The root `railpack.json` serves as the **single source of truth** for all Railway deployments. It should be configured to:

1. **Frontend Service**: Build and serve Next.js static export
2. **Backend Service**: Build and run Python FastAPI backend
3. **ML Service**: Build and run Python ML inference service

### Current Root Configuration

```json
{
  "$schema": "https://schema.railpack.com",
  "version": "1",
  "metadata": {
    "name": "monkey-coder-frontend",
    "description": "Next.js frontend - deploys from repo root"
  },
  "build": {
    "provider": "node",
    "packages": {
      "node": "20"
    },
    "cache": {
      "paths": [
        "node_modules",
        ".yarn/cache",
        "packages/web/.next",
        "packages/web/out"
      ]
    },
    "steps": {
      "install": {
        "commands": [
          "corepack enable",
          "corepack prepare yarn@4.9.2 --activate",
          "yarn install --immutable"
        ]
      },
      "build": {
        "commands": [
          "yarn workspace @monkey-coder/web build"
        ]
      }
    },
    "env": {
      "NODE_ENV": "production",
      "NEXT_OUTPUT_EXPORT": "true",
      "NEXT_TELEMETRY_DISABLED": "1",
      "NEXT_PUBLIC_API_URL": "https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}"
    }
  },
  "deploy": {
    "startCommand": "yarn workspace @monkey-coder/web start --hostname 0.0.0.0 --port $PORT",
    "healthCheckPath": "/api/health",
    "healthCheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### Why This Works

1. **Corepack**: Enables Yarn 4.9.2 (exact version required)
2. **Yarn Install**: Installs ALL workspace dependencies from repo root
3. **Workspace Build**: `yarn workspace @monkey-coder/web build` targets specific package
4. **Workspace Start**: `yarn workspace @monkey-coder/web start` runs Next.js dev server
5. **Cache Paths**: Optimizes subsequent builds with proper cache locations

## 🔧 Service-Specific railpack.json Files (Deprecated)

The files in `services/*/railpack.json` are **NOT used by Railway** when services operate from repo root. They exist for reference but Railway reads only the root `railpack.json`.

### Migration Path

To properly support multi-service deployment from a single railpack.json:

**Option 1: Conditional Start Commands (Recommended)**
Use environment variables to determine which service to start:

```json
{
  "deploy": {
    "startCommand": "bash -c 'if [ \"$SERVICE_TYPE\" = \"backend\" ]; then python -m uvicorn monkey_coder.app.main:app --host 0.0.0.0 --port $PORT; elif [ \"$SERVICE_TYPE\" = \"ml\" ]; then python -m uvicorn ml_server:app --host 0.0.0.0 --port $PORT; else yarn workspace @monkey-coder/web start --hostname 0.0.0.0 --port $PORT; fi'"
  }
}
```

Then set `SERVICE_TYPE` environment variable per service in Railway.

**Option 2: Use run_server.py (Current)**
The repository includes `run_server.py` which handles both frontend build and backend startup:

```json
{
  "deploy": {
    "startCommand": "python run_server.py"
  }
}
```

## 🎯 Railway Service Configuration Checklist

Before deploying, verify each service has:

### Frontend (monkey-coder)
- [ ] Root Directory: `/` or blank
- [ ] Build Command: blank (let railpack.json handle)
- [ ] Start Command: blank (let railpack.json handle)
- [ ] Config Path: `railpack.json`
- [ ] Custom Domain: `coder.fastmonkey.au` configured
- [ ] Environment Variable: `NEXT_PUBLIC_API_URL` references backend service

### Backend (monkey-coder-backend)
- [ ] Root Directory: `/` or blank
- [ ] Build Command: blank (let railpack.json handle)
- [ ] Start Command: blank (let railpack.json handle)
- [ ] Config Path: `railpack.json`
- [ ] Environment Variable: `ML_SERVICE_URL` references ML service
- [ ] All API keys configured (OpenAI, Anthropic, etc.)

### ML (monkey-coder-ml)
- [ ] Root Directory: `/` or blank
- [ ] Build Command: blank (let railpack.json handle)
- [ ] Start Command: blank (let railpack.json handle)
- [ ] Config Path: `railpack.json`
- [ ] Health Check Timeout: 600 seconds (first build takes 25+ minutes)

## 🚀 Deployment Process

1. **Clear Manual Overrides**: Remove any manual build/start commands in Railway Dashboard
2. **Set Root Directory**: Change to `/` or blank for all services
3. **Set Config Path**: Ensure `railpack.json` (at root) is specified
4. **Configure Env Vars**: Set per-service environment variables
5. **Trigger Redeploy**: Manual redeploy or push to GitHub

### Expected Build Sequence

```
✓ Railpack 0.8.0 detected
✓ Using config file `railpack.json`
✓ Steps: install → build
✓ Running: corepack enable
✓ Running: corepack prepare yarn@4.9.2 --activate
✓ Running: yarn install --immutable
✓ Running: yarn workspace @monkey-coder/web build
✓ Deploy: yarn workspace @monkey-coder/web start
✓ Health check passed: /api/health
```

## ⚠️ Common Pitfalls

### 1. Setting rootDirectory to Subdirectories
**Error**: `can't cd to packages/web`  
**Cause**: Service executes in subdirectory where workspace commands fail  
**Fix**: Set rootDirectory to `/` or blank

### 2. Manual Build Commands Override
**Error**: Commands don't match railpack.json expectations  
**Cause**: Railway Dashboard has manual build commands that override railpack.json  
**Fix**: Clear manual commands, let railpack.json handle everything

### 3. Wrong Start Command for Service Type
**Error**: Backend tries to start Next.js, Frontend tries to start Python  
**Cause**: Copy-paste errors in service configuration  
**Fix**: Verify each service's start command matches its technology stack

### 4. Missing Environment Variables
**Error**: Services can't communicate or access external APIs  
**Cause**: Service references not configured (e.g., `${{service.RAILWAY_PUBLIC_DOMAIN}}`)  
**Fix**: Add all required env vars per service as documented above

## 🔍 Debugging Failed Deployments

### Check Railway Logs

```bash
# View build logs
railway logs --service monkey-coder --deployment latest

# Look for:
# - Which railpack.json is being used
# - Where commands are executing (should be from /app = repo root)
# - Whether workspace commands succeed
# - Port binding to 0.0.0.0:$PORT
```

### Verify Health Endpoints

```bash
# Frontend
curl https://coder.fastmonkey.au/api/health

# Backend
curl https://monkey-coder-backend-production.up.railway.app/api/health

# Expected: 200 OK with JSON response
```

### Check Service Communication

```bash
# From backend service logs, verify:
# - ML_SERVICE_URL resolves correctly
# - Requests to ML service succeed
# - No CORS or network errors
```

## 📚 Reference Documentation

- **Railway Docs**: https://docs.railway.com/guides/monorepo#deploying-a-shared-monorepo
- **Railpack Docs**: https://railpack.com/config/file/
- **Yarn Workspaces**: https://yarnpkg.com/features/workspaces

## 🔐 Security Considerations

1. **Never commit secrets**: Use Railway environment variables
2. **Use RAILWAY_PRIVATE_DOMAIN**: For internal service-to-service communication
3. **Use RAILWAY_PUBLIC_DOMAIN**: For external access only
4. **Enable HTTPS**: Railway provides automatic SSL for public domains

## 📝 Maintenance

### Updating Dependencies

```bash
# From repo root
yarn install
yarn workspace @monkey-coder/web add <package>
git commit -am "deps: update frontend dependencies"
git push
```

Railway will automatically detect changes and redeploy.

### Updating Python Dependencies

```bash
# Update requirements.txt in repo root or services/*/requirements.txt
# Railway will reinstall during next deployment
```

## 🎉 Success Indicators

After proper configuration, you should see:

1. **Frontend**: 
   - Build completes in 2-3 minutes
   - Static export generated to `packages/web/out`
   - Next.js server starts on `0.0.0.0:$PORT`
   - Health check passes at `/api/health`

2. **Backend**:
   - Build completes in ~2 minutes (no ML dependencies)
   - Uvicorn starts FastAPI app
   - Can communicate with ML service via private domain
   - Health check passes at `/api/health`

3. **ML**:
   - First build takes 25+ minutes (torch/CUDA downloads)
   - Subsequent builds use cache (~5 minutes)
   - Uvicorn starts ML inference service
   - Health check passes at `/api/health`

---

**Last Updated**: 2025-01-16  
**Status**: Authoritative Configuration Guide  
**Maintainer**: Monkey Coder DevOps Team
