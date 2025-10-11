# 🚨 Railway Deployment Crisis - Complete Resolution Guide

## Executive Summary

**Status**: ✅ SOLUTION IMPLEMENTED - Railway service configuration fixes ready to deploy

**Problem**: 100% deployment failure across all three Railway services since October 3rd due to architectural misconfiguration

**Root Cause**: Services configured as "Isolated Monorepo" with `rootDirectory` set to subdirectories, when repository uses "Shared Monorepo" pattern requiring all services to operate from repository root

**Impact**: Production frontend at `coder.fastmonkey.au` completely down, backend and ML services failing to build

**Solution**: Reconfigure all Railway services to use `rootDirectory: /` with appropriate railpack configuration files

---

## What Happened?

### The Error
```
ERROR: sh: 1: cd: can't cd to packages/web
Build Command: cd packages/web && yarn install --frozen-lockfile && yarn build
Root Directory: services/frontend
```

### Why It Failed

1. **Railway reads railpack.json from repository root** - ALWAYS, regardless of service `rootDirectory` setting
2. **Services execute in subdirectories** - When `rootDirectory: services/frontend` is set
3. **Yarn workspace commands require repo root** - Where `package.json`, `yarn.lock`, and workspace configuration exist
4. **Path resolution breaks** - `packages/web` doesn't exist relative to `services/frontend/`

### The Architecture Mismatch

```
CONFIGURED AS (WRONG):
Railway Service → rootDirectory: services/frontend
                → Execute commands in /app/services/frontend
                → Try: cd packages/web (doesn't exist here!)
                → Result: FAIL

SHOULD BE (CORRECT):
Railway Service → rootDirectory: /
                → Execute commands in /app (repo root)
                → Try: yarn workspace @monkey-coder/web build
                → Result: SUCCESS
```

---

## What Was Fixed?

### 1. Configuration Files Created/Updated ✅

#### Root Configuration Files (NEW)
- `/railpack.json` - Default frontend configuration
- `/railpack-backend.json` - Backend Python service
- `/railpack-ml.json` - ML Python service

#### Service Configurations (UPDATED)
- `/services/frontend/railpack.json` - Added deprecation warning + workaround
- `/services/backend/railpack.json` - Added deprecation warning + workaround
- `/services/ml/railpack.json` - Added deprecation warning + workaround

### 2. Documentation Created ✅

#### Primary Documentation
- **RAILWAY_FIX_INSTRUCTIONS.md** (5,000+ chars) - Quick step-by-step fix guide
- **RAILWAY_DEPLOYMENT.md** (11,000+ chars) - Comprehensive authoritative guide

#### Deprecated (Marked as Incorrect)
- **RAILWAY_SERVICE_SETUP.md** - Previous incorrect instructions
- **RAILWAY_QUICK_CONFIG.md** - Previous incorrect configuration

### 3. Automation Scripts Created ✅

#### Validation Script
```bash
scripts/validate-railway-config.sh
```
- Validates all railpack.json files (JSON syntax)
- Checks workspace structure
- Tests Yarn commands
- Verifies Python package structure
- **Status**: All checks pass ✓

#### Fix Script
```bash
scripts/fix-railway-services.sh
```
- Interactive Railway CLI command generator
- Step-by-step service configuration
- Environment variable setup
- Verification commands

---

## How to Fix (Choose One Method)

### Method 1: Quick CLI Fix (Fastest)

```bash
# Validate configuration first
bash scripts/validate-railway-config.sh

# Apply fix with interactive script
bash scripts/fix-railway-services.sh

# Or use direct Railway CLI commands:
railway link
railway service  # Select: monkey-coder
railway service update --root-directory /
railway up

# Repeat for backend and ML services
```

### Method 2: Railway Dashboard (Visual)

**For Each Service (monkey-coder, monkey-coder-backend, monkey-coder-ml):**

1. Go to: https://railway.app/project/[your-project-id]
2. Click on service
3. Settings → Service → **Root Directory**: Change to `/`
4. Settings → Config as Code:
   - Frontend: `railpack.json`
   - Backend: `railpack-backend.json`
   - ML: `railpack-ml.json`
5. Clear any manual "Build Command" or "Start Command" overrides
6. Save changes and redeploy

### Method 3: Environment Variable Configuration (Alternative)

If Railway doesn't support per-service config paths, set `SERVICE_TYPE` environment variable:

```bash
# Frontend service
railway variables set SERVICE_TYPE=frontend

# Backend service  
railway variables set SERVICE_TYPE=backend

# ML service
railway variables set SERVICE_TYPE=ml
```

Then use a unified railpack.json with conditional start commands.

---

## Verification Checklist

After applying configuration changes:

### Step 1: Check Build Logs

```bash
railway logs --service monkey-coder --deployment latest

# Expected indicators:
✓ "Using config file 'railpack.json'"
✓ "Running from /app" (repo root)
✓ "yarn install --immutable" succeeds
✓ "yarn workspace @monkey-coder/web build" succeeds
✓ Server starts on 0.0.0.0:$PORT
```

### Step 2: Test Health Endpoints

```bash
# Frontend
curl https://coder.fastmonkey.au/api/health
# Expected: 200 OK

# Backend
curl https://monkey-coder-backend-production.up.railway.app/api/health
# Expected: 200 OK
```

### Step 3: Monitor for Stability

```bash
railway logs --service monkey-coder --follow

# Watch for:
✓ No restart loops
✓ No OOM errors
✓ Successful incoming requests
✓ No uncaught exceptions
```

---

## Environment Variables Required

### Frontend (monkey-coder)
```bash
NODE_ENV=production
NEXT_OUTPUT_EXPORT=true
NEXT_TELEMETRY_DISABLED=1
NEXT_PUBLIC_APP_URL=https://coder.fastmonkey.au
NEXT_PUBLIC_API_URL=https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}
```

### Backend (monkey-coder-backend)
```bash
PYTHON_ENV=production
PYTHONPATH=/app:/app/packages/core
ML_SERVICE_URL=http://${{monkey-coder-ml.RAILWAY_PRIVATE_DOMAIN}}
# Plus all API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
```

### ML (monkey-coder-ml)
```bash
PYTHON_ENV=production
PYTHONPATH=/app:/app/services/ml
TRANSFORMERS_CACHE=/app/.cache/huggingface
CUDA_VISIBLE_DEVICES=0
```

---

## Expected Build Times

| Service | First Build | Cached Build |
|---------|-------------|--------------|
| Frontend | 2-3 min | ~1 min |
| Backend | ~2 min | ~1 min |
| ML | 25+ min | ~5 min |

**Note**: ML first build takes 25+ minutes due to torch/CUDA downloads (2.5GB+)

---

## Troubleshooting

### Error: "yarn: command not found"
**Solution**: Verify railpack.json includes Corepack setup:
```json
"install": {
  "commands": [
    "corepack enable",
    "corepack prepare yarn@4.9.2 --activate"
  ]
}
```

### Error: "Module not found: monkey_coder"
**Solution**: Set correct PYTHONPATH:
```bash
railway variables set PYTHONPATH=/app:/app/packages/core
```

### Error: "Health check failed"
**Solution**: Verify service binds to `0.0.0.0:$PORT`:
```python
uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
```

### Error: "Workspace not found"
**Solution**: Confirm rootDirectory is `/` not a subdirectory

---

## Success Criteria

✅ **Frontend Service**
- Build completes in 2-3 minutes
- Static export generated to `packages/web/out`
- Next.js server starts successfully
- Health check passes at `/api/health`
- Accessible at `https://coder.fastmonkey.au`

✅ **Backend Service**
- Build completes in ~2 minutes
- Uvicorn starts FastAPI app
- Can communicate with ML service
- Health check passes at `/api/health`

✅ **ML Service**
- First build completes (25+ min expected)
- Subsequent builds use cache
- Uvicorn starts ML inference service
- Health check passes at `/api/health`

---

## Documentation Map

```
START HERE:
├── scripts/validate-railway-config.sh ← Run first (validation)
├── RAILWAY_FIX_INSTRUCTIONS.md ← Quick fix guide
└── scripts/fix-railway-services.sh ← Interactive helper

REFERENCE:
├── RAILWAY_DEPLOYMENT.md ← Comprehensive guide
├── railpack.json ← Frontend config
├── railpack-backend.json ← Backend config
└── railpack-ml.json ← ML config

DEPRECATED (DO NOT USE):
├── RAILWAY_SERVICE_SETUP.md
└── RAILWAY_QUICK_CONFIG.md
```

---

## Technical Details

### Shared Monorepo Pattern

This repository uses **Shared Monorepo** architecture:
- Single railpack.json at root defines ALL services
- All services execute from repository root
- Logical service separation via start commands, not directories
- Yarn workspaces require execution from root

### Railway Behavior

- Railway ALWAYS reads railpack.json from repository root
- `rootDirectory` setting only changes WHERE commands execute
- Setting `rootDirectory` to subdirectory breaks workspace commands
- Solution: All services must use `rootDirectory: /`

### Why Previous Configuration Failed

```
┌─────────────────────────────────────────────────────────┐
│ Railway Configuration (BROKEN)                          │
├─────────────────────────────────────────────────────────┤
│ Service: monkey-coder                                   │
│ Root Directory: services/frontend ← WRONG               │
│ Build Command: cd packages/web && ... ← FAILS           │
│                                                          │
│ Execution Context: /app/services/frontend               │
│ Looking for: packages/web                               │
│ Result: Directory not found!                            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Railway Configuration (CORRECT)                         │
├─────────────────────────────────────────────────────────┤
│ Service: monkey-coder                                   │
│ Root Directory: / ← CORRECT                             │
│ Build: yarn workspace @monkey-coder/web build ← WORKS   │
│                                                          │
│ Execution Context: /app (repo root)                     │
│ Looking for: packages/web (exists here!)                │
│ Result: Success!                                        │
└─────────────────────────────────────────────────────────┘
```

---

## Post-Deployment Actions

After successful deployment:

1. **Monitor Services**
   ```bash
   railway logs --service monkey-coder --follow
   ```

2. **Load Test**
   ```bash
   curl https://coder.fastmonkey.au
   curl https://coder.fastmonkey.au/api/health
   ```

3. **Check Metrics**
   - Response times < 200ms
   - Memory usage stable
   - No error spikes

4. **Update Documentation**
   - Mark this incident as resolved
   - Document any additional findings

---

## Lessons Learned

1. **Railway's rootDirectory is not intuitive**
   - It changes WHERE commands run, not WHICH config is used
   - Always use `/` for Shared Monorepo patterns

2. **Yarn workspaces require repo root**
   - Cannot be executed from subdirectories
   - Must have access to root package.json

3. **Documentation must match reality**
   - Previous docs caused the exact failure they aimed to prevent
   - Always validate configuration before deploying

4. **Validation is critical**
   - Created `validate-railway-config.sh` to catch issues early
   - All configurations should have automated validation

---

## Support Resources

- **Railway Docs**: https://docs.railway.com/guides/monorepo#deploying-a-shared-monorepo
- **Railpack Docs**: https://railpack.com/config/file/
- **Yarn Workspaces**: https://yarnpkg.com/features/workspaces

---

## Status Summary

| Task | Status |
|------|--------|
| Root Cause Identified | ✅ Complete |
| Configuration Files Created | ✅ Complete |
| Documentation Written | ✅ Complete |
| Scripts Created | ✅ Complete |
| Validation Script | ✅ Complete (All checks pass) |
| Railway Service Configuration | ⏳ **USER ACTION REQUIRED** |
| Deployment Verification | ⏳ Pending Railway config |
| Production Restoration | ⏳ Pending deployment |

---

**Last Updated**: 2025-01-16  
**Status**: Ready for Railway Service Configuration  
**Action Required**: User must apply Railway service configuration changes

---

## Quick Command Reference

```bash
# Validate configuration
bash scripts/validate-railway-config.sh

# Get fix commands
bash scripts/fix-railway-services.sh

# Or direct Railway CLI:
railway link
railway service  # Select service
railway service update --root-directory /
railway variables set [KEY]=[VALUE]
railway up

# Check logs
railway logs --service [service-name] --follow

# Test endpoints
curl https://coder.fastmonkey.au/api/health
```

---

**🎉 Configuration is ready - apply to Railway services to resolve the crisis!**
