# Railway Deployment Commands - AetherOS Project

**Project ID:** `359de66a-b9de-486c-8fb4-c56fda52344f`  
**Environment ID:** `b7d7b4ec-c4d7-4a98-9d8a-e7c257afa56b` (production)

## Executive Summary

This document contains the Railway CLI commands needed to fix the three monkey-coder services in the AetherOS project. Execute these commands after code changes are committed and pushed to GitHub.

---

## Service Overview

| Service | Service ID | Status | Issue | Priority |
|---------|-----------|--------|-------|----------|
| monkey-coder-backend | `6af98d25-621b-4a2d-bbcb-7acb314fbfed` | ❌ FAILED | Stale build cache | **P0** |
| monkey-coder-ml | `07ef6ac7-e412-4a24-a0dc-74e301413eaa` | ✅ SUCCESS | Wrong root directory | **P1** |
| monkey-coder | `ccc58ca2-1f4b-4086-beb6-2321ac7dab40` | ✅ SUCCESS | None | - |

---

## Prerequisites

1. Install Railway CLI:
   ```bash
   # Using npm/yarn (temporary, ephemeral)
   yarn dlx @railway/cli@latest
   # or
   npx @railway/cli@latest
   
   # Using curl (permanent installation)
   bash <(curl -fsSL cli.new)
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Link to the AetherOS project:
   ```bash
   railway link 359de66a-b9de-486c-8fb4-c56fda52344f
   ```

---

## Phase 1: Backend Service - Trigger Fresh Deployment (CRITICAL)

**Issue:** Railway built from a stale snapshot that doesn't include `services/backend/requirements-deploy.txt`

**Status:** File exists in repository (SHA: ce36405) but wasn't in the build snapshot from Jan 12, 10:27 AM

### Command 1: Redeploy Backend Service

```bash
railway service \
  --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  --environment b7d7b4ec-c4d7-4a98-9d8a-e7c257afa56b \
  redeploy
```

### Expected Outcome:
1. Build pulls fresh code including `requirements-deploy.txt`
2. Build command: `python -m uv pip install -r requirements-deploy.txt` succeeds
3. Install command: `python -m uv pip install --no-cache-dir git+https://github.com/GaryOcean428/monkey-coder.git#subdirectory=packages/core` completes
4. Service starts successfully
5. Health check passes: `/api/health` returns 200

### Monitor Deployment:

```bash
# Watch logs in real-time
railway logs \
  --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  --tail

# Check deployment status
railway status \
  --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed
```

### Verify Health:

```bash
curl https://monkey-coder-backend-production.up.railway.app/api/health
```

---

## Phase 2: ML Service - Fix Root Directory Configuration

**Issue:** Root directory is `/` but should be `services/ml` to align with monorepo structure

**Status:** Service is currently successful but misconfigured. The code changes update railpack.json to work with `services/ml` as root.

### Changes Made:
1. ✅ Updated `services/ml/railpack.json`:
   - Changed Python version from 3.12 to 3.13
   - Fixed absolute path `/app/requirements.txt` to relative `requirements.txt`
   - Updated PYTHONPATH from `/app:/app/services/ml` to `/app`
   - Updated startCommand from `python -m uvicorn services.ml.ml_server:app` to `python -m uvicorn ml_server:app`

### Command 2: Update ML Service Root Directory

```bash
railway service \
  --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa \
  --environment b7d7b4ec-c4d7-4a98-9d8a-e7c257afa56b \
  update \
  --root-directory services/ml
```

### Expected Outcome:
1. Service rebuilds with `services/ml` as root context
2. Build command uses relative path: `uv pip install -r requirements.txt --system`
3. Start command resolves: `python -m uvicorn ml_server:app`
4. Health check passes: `/api/health` returns 200

### Monitor Deployment:

```bash
# Watch logs in real-time
railway logs \
  --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa \
  --tail

# Check deployment status
railway status \
  --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa
```

### Verify Health:

```bash
curl https://monkey-coder-ml-production.up.railway.app/api/health
```

---

## Phase 3: Frontend Service - No Action Required

**Service ID:** `ccc58ca2-1f4b-4086-beb6-2321ac7dab40`  
**Status:** ✅ SUCCESS  
**Root Directory:** `services/frontend` ✅  
**Health Check:** `/` ✅

No changes needed. Service is properly configured.

---

## Complete Deployment Workflow

Execute these commands in order:

```bash
# 1. Login and link to project
railway login
railway link 359de66a-b9de-486c-8fb4-c56fda52344f

# 2. Redeploy backend (pulls fresh code with requirements-deploy.txt)
railway service \
  --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  --environment b7d7b4ec-c4d7-4a98-9d8a-e7c257afa56b \
  redeploy

# 3. Wait for backend to complete, then fix ML root directory
railway service \
  --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa \
  --environment b7d7b4ec-c4d7-4a98-9d8a-e7c257afa56b \
  update \
  --root-directory services/ml

# 4. Monitor all services
railway status
```

---

## Alternative: Trigger via GitHub Commit

If Railway CLI is not available, trigger deployments via GitHub push:

```bash
# Create an empty commit to trigger deployment
git commit --allow-empty -m "chore: trigger Railway redeployment for backend and ML fixes"
git push origin main
```

**Note:** This will trigger deployments for all services with GitHub integration enabled. Make sure the ML service root directory is updated in Railway dashboard manually if CLI is unavailable.

---

## Verification Checklist

After executing commands, verify:

### Backend Service:
- [ ] Deployment status shows SUCCESS
- [ ] Build logs show: `python -m uv pip install -r requirements-deploy.txt` succeeded
- [ ] Build logs show: `python -m uv pip install --no-cache-dir git+https://github.com/GaryOcean428/monkey-coder.git#subdirectory=packages/core` completed
- [ ] Health endpoint returns 200: `curl https://monkey-coder-backend-production.up.railway.app/api/health`

### ML Service:
- [ ] Root directory is set to `services/ml` (check in Railway dashboard)
- [ ] Deployment status shows SUCCESS
- [ ] Build logs show: `uv pip install -r requirements.txt --system` succeeded
- [ ] Start command runs: `python -m uvicorn ml_server:app`
- [ ] Health endpoint returns 200: `curl https://monkey-coder-ml-production.up.railway.app/api/health`

### Frontend Service:
- [ ] Status remains SUCCESS (no changes needed)
- [ ] Health endpoint accessible: `curl https://monkey-coder-production.up.railway.app/`

---

## Troubleshooting

### Backend Still Fails After Redeploy

**Issue:** Build snapshot still doesn't have requirements-deploy.txt

**Solution:**
1. Verify file exists in GitHub repository:
   ```bash
   curl -I https://raw.githubusercontent.com/GaryOcean428/monkey-coder/main/services/backend/requirements-deploy.txt
   ```
2. If file is missing, commit and push it:
   ```bash
   git add services/backend/requirements-deploy.txt
   git commit -m "fix: add requirements-deploy.txt for Railway backend"
   git push origin main
   ```
3. Trigger another redeploy

### ML Service Import Errors After Root Change

**Issue:** Python can't import ml_server module

**Solution:**
1. Check PYTHONPATH is set correctly: `/app`
2. Verify start command: `python -m uvicorn ml_server:app --host 0.0.0.0 --port $PORT`
3. Check Railway logs for specific error
4. If persistent, rollback root directory and investigate railpack.json

### Railway CLI Not Available

**Solution:**
1. Use ephemeral installation: `yarn dlx @railway/cli@latest login`
2. Or use Railway Dashboard UI:
   - Navigate to service settings
   - Update root directory manually
   - Trigger manual redeploy

---

## Additional Resources

- **Railway Dashboard:** https://railway.app/project/359de66a-b9de-486c-8fb4-c56fda52344f
- **Railway Docs:** https://docs.railway.app/
- **Railway CLI Reference:** https://docs.railway.app/reference/cli-api
- **GitHub Repository:** https://github.com/GaryOcean428/monkey-coder

---

## Summary

**Critical Actions:**
1. ✅ Code changes committed (ML railpack.json fixed)
2. ⏳ Execute Railway CLI command to redeploy backend
3. ⏳ Execute Railway CLI command to update ML root directory
4. ⏳ Verify all health checks pass

**Time Estimate:** 5-10 minutes total (including build times)

**Risk Assessment:** Low - Backend fix is non-destructive, ML fix has fallback to current working state
