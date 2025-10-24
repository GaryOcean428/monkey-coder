# Railway Deployment Fix - Yarn Command Not Found

## Issue Summary

Both `monkey-coder-backend` and `monkey-coder` (frontend) services are failing with the error:

```
/bin/bash: line 1: yarn: command not found
```

## Root Causes

### 1. Frontend Service Issue (FIXED)
The frontend service's `railpack.json` had `"startCommand": "yarn start"`. 

**Root Cause**: Yarn is only available during the build phase, not the deploy phase in Railway.

**Fix Applied**: Changed to use direct Node.js command:
```json
"startCommand": "node packages/serve/bin/serve.js -s packages/web/out -l $PORT -c serve.json"
```

This uses the bundled serve package in the repository, which is reliable and doesn't require yarn, npm, or npx.

### 2. Backend Service Issue (REQUIRES CONFIGURATION)
If the backend service is showing "yarn: command not found", it's reading the **wrong railpack.json file** (the root one for frontend instead of `services/backend/railpack.json`).

**Root Cause**: The Railway service Root Directory setting is incorrect.

**Fix Required**: Configure the Railway dashboard to use the correct root directory.

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
node packages/serve/bin/serve.js -s packages/web/out -l $PORT -c serve.json

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
   - Frontend: Should show Node.js build and direct Node.js serve command
3. **Check health checks**:
   - Backend: `https://monkey-coder-backend-production.up.railway.app/api/health`
   - Frontend: `https://coder.fastmonkey.au/`
4. **Verify logs** show services starting correctly without "yarn: command not found" errors

## Configuration Summary

| Service | Root Directory | Start Command Source | Health Check Path |
|---------|---------------|---------------------|-------------------|
| monkey-coder-backend | `services/backend` | railpack.json | `/api/health` |
| monkey-coder | `.` (root) | railpack.json | `/` |
| monkey-coder-ml | `services/ml` | railpack.json | `/api/health` |

## Files Modified in This Fix

- ✅ `railpack.json` - Changed frontend startCommand from `yarn start` to direct Node.js command using bundled serve
- ✅ `railpack.json` - Updated to use correct official Railpack schema structure (removed `version`, `metadata`, moved `provider` and `steps` to root)
- ✅ `services/backend/railpack.json` - Updated to use correct official Railpack schema structure
- ✅ `services/ml/railpack.json` - Updated to use correct official Railpack schema structure
- ✅ `RAILWAY_DEPLOYMENT_FIX.md` - Updated documentation to reflect the actual fix

## Railpack.json Structure Corrections

All railpack.json files have been updated to match the official Railpack schema:

### ❌ Old (Incorrect) Structure
```json
{
  "$schema": "https://schema.railpack.com",
  "version": "1",                    // ❌ Not in official schema
  "metadata": {                      // ❌ Not in official schema
    "name": "...",
    "description": "..."
  },
  "build": {                         // ❌ Incorrect nesting
    "provider": "node",
    "steps": { ... }
  }
}
```

### ✅ New (Correct) Structure
```json
{
  "$schema": "https://schema.railpack.com",
  "provider": "node",                // ✅ At root level
  "packages": {
    "node": "20"
  },
  "steps": {                         // ✅ At root level
    "install": {
      "commands": [...],
      "cache": { "paths": [...] }
    },
    "build": {
      "inputs": [{ "step": "install" }],
      "commands": [...],
      "cache": { "paths": [...] }
    }
  },
  "deploy": {
    "startCommand": "...",
    "variables": { ... },            // ✅ Use variables instead of env
    "paths": [...]                   // ✅ For PATH additions
  }
}
```

### Key Changes:
1. **Removed** `version` field (not in official schema)
2. **Removed** `metadata` object (not in official schema)
3. **Moved** `provider` to root level (was nested under `build`)
4. **Moved** `steps` to root level (was nested under `build`)
5. **Moved** `packages` to root level (was nested under `build`)
6. **Changed** `env` to `variables` in deploy section (correct field name)
7. **Added** `cache` per-step instead of global (more granular control)
8. **Added** `inputs` to define step dependencies
9. **Added** `paths` in deploy for PATH modifications
10. **Removed** unsupported fields: `healthCheckPath`, `healthCheckTimeout`, `restartPolicyType`, `restartPolicyMaxRetries` (these may be Railway-specific, not Railpack)

**Note**: Health check configuration should be done through Railway Dashboard service settings, not in railpack.json.

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
