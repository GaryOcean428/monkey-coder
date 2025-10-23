# Railway Deployment Health Check Failures - Fix Guide

## Issue Summary

Both `monkey-coder-backend` and `monkey-coder` (frontend) services are failing health checks with the error:

```
/bin/bash: line 1: serve: command not found
```

## Root Causes

### 1. Backend Service Issue
The backend service is trying to run the `serve` command instead of `uvicorn`, which indicates it's reading the **wrong railpack.json file** (the root one for frontend instead of `services/backend/railpack.json`).

**Root Cause**: The Railway service Root Directory setting is incorrect.

### 2. Frontend Service Issue
The frontend service is correctly trying to run `serve`, but the package wasn't installed properly in the build.

**Root Cause**: The `npm install -g serve` command in build steps doesn't work reliably in Railpack environments.

**Fix Applied**: Changed to use `npx serve@14.2.4` which downloads and runs the package on-the-fly.

## Required Railway Dashboard Configuration

You must update the Railway service settings in the dashboard:

### Step 1: Fix Backend Service Root Directory

1. Go to Railway dashboard: https://railway.app
2. Select your project
3. Click on the **`monkey-coder-backend`** service
4. Go to **Settings** tab
5. Scroll to **Service Settings** section
6. Find the **Root Directory** setting
7. **Change it to**: `services/backend`
8. Click **Save** or apply the changes
9. **Important**: Also check the **Start Command** override:
   - If there's a custom start command set, **clear it** (leave blank)
   - This ensures it uses the startCommand from railpack.json

### Step 2: Fix Frontend Service (if needed)

1. In Railway dashboard, click on **`monkey-coder`** (frontend) service
2. Go to **Settings** tab
3. Verify **Root Directory** is set to `.` or is blank (root directory)
4. Check **Start Command** override:
   - If there's a custom start command set, **clear it** (leave blank)
   - This ensures it uses the startCommand from railpack.json

### Step 3: Verify ML Service (should be working)

1. Click on **`monkey-coder-ml`** service
2. Go to **Settings** tab
3. Verify **Root Directory** is set to: `services/ml`
4. This service should already be working based on your logs

## Expected Behavior After Fix

### Backend Service
```
Deploy Command:
/app/.venv/bin/python -m uvicorn monkey_coder.app.main:app --host 0.0.0.0 --port $PORT

Health Check:
Path: /api/health
Status: ✅ Healthy
```

### Frontend Service
```
Deploy Command:
npx serve@14.2.4 -s packages/web/out -l $PORT -c serve.json

Health Check:
Path: /
Status: ✅ Healthy
```

## Alternative: Railway CLI Method

If you have Railway CLI installed, you can configure services via command line:

```bash
# Configure backend service
railway service --name monkey-coder-backend
railway up --service monkey-coder-backend --detach

# Or set via environment variable
railway variables set ROOT_DIR=services/backend --service monkey-coder-backend
```

## Verification Steps

After applying the fixes:

1. **Trigger new deployments** for both frontend and backend services
2. **Monitor build logs** to verify:
   - Backend: Should show Python installation and uvicorn command
   - Frontend: Should show Node.js build and npx serve command
3. **Check health checks**:
   - Backend: `https://monkey-coder-backend-production.up.railway.app/api/health`
   - Frontend: `https://coder.fastmonkey.au/`
4. **Verify logs** show services starting correctly without "serve: command not found" errors

## Configuration Summary

| Service | Root Directory | Start Command Source | Health Check Path |
|---------|---------------|---------------------|-------------------|
| monkey-coder-backend | `services/backend` | railpack.json | `/api/health` |
| monkey-coder | `.` (root) | railpack.json | `/` |
| monkey-coder-ml | `services/ml` | railpack.json | `/api/health` |

## Files Modified in This Fix

- ✅ `railpack.json` - Changed frontend startCommand to use `npx serve@14.2.4`
- ✅ `services/backend/railpack.json` - Already correct, no changes needed
- ✅ `services/ml/railpack.json` - Already correct, no changes needed

## Next Steps

1. Apply the Railway dashboard configuration changes above
2. Trigger new deployments for both services
3. Monitor the build and deploy logs
4. Verify health checks pass
5. Test the deployed applications

## Support

If issues persist after applying these fixes:
1. Check the deploy logs for any new error messages
2. Verify environment variables are set correctly
3. Ensure Railway service names match exactly
4. Check that no custom build/start commands are overriding railpack.json settings
