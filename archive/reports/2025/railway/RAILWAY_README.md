# Railway Deployment Documentation

## 🚨 If You're Having Deployment Issues - START HERE

### Current Status: Railway Deployment Crisis Resolution Available

**Symptoms**:
- ❌ Services failing to build with "can't cd to packages/web" error
- ❌ Frontend at `coder.fastmonkey.au` is down
- ❌ 100% deployment failure rate since October 3rd

**Quick Fix**: See **RAILWAY_FIX_INSTRUCTIONS.md** (2 minutes read)

---

## 📚 Documentation Index

### 🔥 Critical Documents (Read First)

1. **[RAILWAY_FIX_INSTRUCTIONS.md](RAILWAY_FIX_INSTRUCTIONS.md)**
   - Quick step-by-step fix guide
   - Railway CLI and Dashboard instructions
   - Environment variable checklists
   - **Start here if services are failing**

2. **[RAILWAY_CRISIS_RESOLUTION.md](RAILWAY_CRISIS_RESOLUTION.md)**
   - Comprehensive crisis overview
   - Root cause analysis
   - Complete resolution guide
   - Post-deployment verification

3. **[RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)**
   - Authoritative deployment guide (350+ lines)
   - Detailed configuration explanations
   - Common pitfalls and solutions
   - Debugging procedures

### 🛠️ Tools & Scripts

4. **[scripts/validate-railway-config.sh](scripts/validate-railway-config.sh)**
   ```bash
   bash scripts/validate-railway-config.sh
   ```
   - Validates all railpack.json files
   - Checks repository structure
   - Tests workspace commands
   - **Run this before deploying**

5. **[scripts/fix-railway-services.sh](scripts/fix-railway-services.sh)**
   ```bash
   bash scripts/fix-railway-services.sh
   ```
   - Interactive Railway CLI command generator
   - Step-by-step service configuration
   - Color-coded output
   - **Run this to get exact fix commands**

### ⚙️ Configuration Files

6. **[railpack.json](railpack.json)** - Frontend Service
   - Next.js with Yarn workspaces
   - Used by `monkey-coder` service
   - Default configuration

7. **[railpack-backend.json](railpack-backend.json)** - Backend Service
   - Python FastAPI backend
   - Used by `monkey-coder-backend` service
   - No ML dependencies

8. **[railpack-ml.json](railpack-ml.json)** - ML Service
   - Python ML inference server
   - Used by `monkey-coder-ml` service
   - Includes torch/transformers

### ⚠️ Deprecated Documents (Do Not Use)

9. ~~[RAILWAY_SERVICE_SETUP.md](RAILWAY_SERVICE_SETUP.md)~~ - **DEPRECATED**
   - Contains incorrect `rootDirectory` configuration
   - Caused the deployment failures
   - Marked with warnings

10. ~~[RAILWAY_QUICK_CONFIG.md](RAILWAY_QUICK_CONFIG.md)~~ - **DEPRECATED**
    - Contains incorrect service configuration
    - Use RAILWAY_FIX_INSTRUCTIONS.md instead

### 📖 Reference Documents

11. **[RAILWAY_DEPLOYMENT_GUIDE.md](RAILWAY_DEPLOYMENT_GUIDE.md)** - General guidance
12. **[RAILWAY_MONITORING_README.md](RAILWAY_MONITORING_README.md)** - Monitoring setup
13. **[RAILWAY_QUICK_REFERENCE.md](RAILWAY_QUICK_REFERENCE.md)** - Quick reference

---

## 🎯 Quick Start Guide

### Option 1: Automated Fix (Recommended)

```bash
# Step 1: Validate configuration
bash scripts/validate-railway-config.sh

# Step 2: Get fix commands
bash scripts/fix-railway-services.sh

# Step 3: Follow the interactive prompts
```

### Option 2: Manual Fix (Railway Dashboard)

1. Open Railway Dashboard: https://railway.app/project/[your-project]
2. For **EACH** service (monkey-coder, monkey-coder-backend, monkey-coder-ml):
   - Click on service
   - Settings → Service → Root Directory: **Change to `/`**
   - Settings → Config as Code → Set appropriate config file
   - Save and redeploy

**Config Files per Service**:
- `monkey-coder` (Frontend): `railpack.json`
- `monkey-coder-backend` (Backend): `railpack-backend.json`
- `monkey-coder-ml` (ML): `railpack-ml.json`

### Option 3: Railway CLI (Advanced)

```bash
railway link

# Fix frontend
railway service  # Select: monkey-coder
railway service update --root-directory /
railway up

# Fix backend
railway service  # Select: monkey-coder-backend
railway service update --root-directory /
railway up

# Fix ML
railway service  # Select: monkey-coder-ml
railway service update --root-directory /
railway up
```

---

## 🔍 Understanding the Problem

### What Went Wrong?

```
┌─────────────────────────────────────────┐
│ INCORRECT Configuration                 │
├─────────────────────────────────────────┤
│ Root Directory: services/frontend       │
│ Build: cd packages/web && ...           │
│ Context: /app/services/frontend         │
│ Result: ERROR - path not found!         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ CORRECT Configuration                   │
├─────────────────────────────────────────┤
│ Root Directory: /                       │
│ Build: yarn workspace @monkey-coder/web │
│ Context: /app (repo root)               │
│ Result: SUCCESS ✓                       │
└─────────────────────────────────────────┘
```

### Why `/` Must Be Used

1. **Railway reads railpack.json from repo root** - Always, regardless of service settings
2. **Yarn workspaces require repo root** - Where package.json and workspace config exist
3. **Python imports need correct structure** - PYTHONPATH must reference packages/core
4. **Shared Monorepo pattern** - All services logically separated via start commands

---

## ✅ Verification

After applying fixes, verify:

```bash
# Check health endpoints
curl https://coder.fastmonkey.au/api/health
curl https://[backend-domain]/api/health

# Check logs
railway logs --service monkey-coder

# Expected in logs:
✓ "Using config file 'railpack.json'"
✓ Running from /app
✓ yarn workspace commands succeed
✓ Server started on 0.0.0.0:$PORT
```

---

## 📊 Service Configuration Summary

| Service | Root Dir | Config File | Build Time | Status |
|---------|----------|-------------|------------|--------|
| monkey-coder | `/` | railpack.json | 2-3 min | ⏳ Needs fix |
| monkey-coder-backend | `/` | railpack-backend.json | ~2 min | ⏳ Needs fix |
| monkey-coder-ml | `/` | railpack-ml.json | 25+ min | ⏳ Needs fix |

---

## 🆘 Need Help?

### Common Issues

**Error: "can't cd to packages/web"**
→ Root directory not set to `/` - See RAILWAY_FIX_INSTRUCTIONS.md

**Error: "yarn: command not found"**
→ Corepack not enabled - Check railpack.json includes corepack setup

**Error: "Module not found: monkey_coder"**
→ PYTHONPATH incorrect - Should be `/app:/app/packages/core`

**Error: "Health check failed"**
→ Service not binding to `0.0.0.0:$PORT` - Check start command

### Getting More Help

1. Check [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) - Comprehensive troubleshooting
2. Run [scripts/validate-railway-config.sh](scripts/validate-railway-config.sh) - Find configuration issues
3. Review Railway logs: `railway logs --service [name]`
4. Check Railway status: https://status.railway.app

---

## 📝 Key Takeaways

1. ✅ **Always use `rootDirectory: /`** for Shared Monorepo pattern
2. ✅ **Never use subdirectories** in Railway root directory setting
3. ✅ **Validate before deploying** with validation script
4. ✅ **Use workspace commands** for Yarn monorepos
5. ✅ **Set PYTHONPATH correctly** for Python services

---

## 🎉 Success Indicators

After proper configuration:
- ✅ All services build successfully
- ✅ Frontend accessible at https://coder.fastmonkey.au
- ✅ Backend responds to API requests
- ✅ ML service handles inference requests
- ✅ Health checks return 200 OK
- ✅ No "can't cd to packages/web" errors

---

**Last Updated**: 2025-01-16  
**Status**: Crisis resolution available - user action required  
**Priority**: 🔴 Critical - Production services down

---

## Quick Links

- 🔥 [Quick Fix Guide](RAILWAY_FIX_INSTRUCTIONS.md)
- 📖 [Comprehensive Guide](RAILWAY_CRISIS_RESOLUTION.md)
- 📚 [Detailed Deployment Docs](RAILWAY_DEPLOYMENT.md)
- 🛠️ [Validation Script](scripts/validate-railway-config.sh)
- 🔧 [Fix Script](scripts/fix-railway-services.sh)
- ⚙️ [Frontend Config](railpack.json)
- ⚙️ [Backend Config](railpack-backend.json)
- ⚙️ [ML Config](railpack-ml.json)
