# Railway Backend Service Configuration Fix

## Issue

The `monkey-coder-backend` service on Railway is failing to build with the error:

```
ERRO error creating app: directory /build-sessions/.../snapshot-target-unpack/backend does not exist
```

## Root Cause

The Railway service configuration has the **Root Directory** set to `backend`, but the actual backend code is located at `services/backend`.

## Fix Required (Railway Dashboard)

To fix this issue, update the Railway service configuration:

1. Go to Railway dashboard: https://railway.app
2. Select your project
3. Click on the `monkey-coder-backend` service
4. Go to **Settings** tab
5. Scroll to **Service Settings**
6. Update **Root Directory** from `backend` to `services/backend`
7. Save the changes
8. Trigger a new deployment

## Verification

After applying the fix:
- Railway should successfully find the `railpack.json` at `services/backend/railpack.json`
- The build will use Python 3.12 as specified in the railpack configuration
- The service will install dependencies from `services/backend/requirements.txt`
- The health check endpoint will be available at `/api/health`

## Alternative: CLI Fix

If you have Railway CLI installed, you can update the configuration:

```bash
# Navigate to the backend service directory
cd services/backend

# Link this directory as the Railway service root
railway up
```

Or use Railway CLI to set the root directory:

```bash
railway service --name monkey-coder-backend
railway variables set ROOT_DIR=services/backend
```

## Expected Build Behavior After Fix

Once the root directory is corrected, Railway will:

1. Find `services/backend/railpack.json`
2. Detect Python 3.12 provider
3. Create virtual environment at `/app/.venv`
4. Install dependencies from `requirements.txt`
5. Start the service with: `/app/.venv/bin/python -m uvicorn monkey_coder.app.main:app --host 0.0.0.0 --port $PORT`

## Related Services

Make sure the ML service (`monkey-coder-ml`) also has the correct root directory:
- **Root Directory**: `services/ml`
