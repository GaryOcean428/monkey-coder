# 🚨 Railway Deployment Fix - Quick Instructions

## What's Wrong?

Your Railway services are currently configured with:
- ❌ Root Directory: `services/frontend`, `services/backend`, `services/ml`
- ❌ Manual build commands that try to `cd packages/web` from wrong directory
- ❌ Result: **100% deployment failure** with error: `can't cd to packages/web`

## Why This Fails

Railway reads `railpack.json` from **repository root**, but services execute in **subdirectories** where:
- Yarn workspace commands don't work (no `package.json` or `node_modules`)
- Path `packages/web` doesn't exist relative to `services/frontend/`
- Python imports fail because package structure is broken

## The Fix (3 Steps)

### Step 1: Fix Frontend Service (monkey-coder)

**Option A: Railway CLI**
```bash
railway link
railway service  # Select: monkey-coder
railway service update --root-directory /
railway up
```

**Option B: Railway Dashboard**
1. Go to: https://railway.app/project/[your-project]
2. Click on `monkey-coder` service
3. Settings → Service → Root Directory: Change to `/`
4. Settings → Config as Code → Path: `railpack.json`
5. Save and redeploy

### Step 2: Fix Backend Service (monkey-coder-backend)

**Option A: Railway CLI**
```bash
railway service  # Select: monkey-coder-backend
railway service update --root-directory /
```

**Option B: Railway Dashboard**
1. Click on `monkey-coder-backend` service
2. Settings → Service → Root Directory: Change to `/`
3. Settings → Config as Code → Path: `railpack-backend.json`
4. Save and redeploy

### Step 3: Fix ML Service (monkey-coder-ml)

**Option A: Railway CLI**
```bash
railway service  # Select: monkey-coder-ml
railway service update --root-directory /
```

**Option B: Railway Dashboard**
1. Click on `monkey-coder-ml` service
2. Settings → Service → Root Directory: Change to `/`
3. Settings → Config as Code → Path: `railpack-ml.json`
4. Save and redeploy

## Verify It Works

After redeployment, check:

```bash
# Frontend health check
curl https://coder.fastmonkey.au/api/health

# Backend health check
curl https://[your-backend-domain]/api/health

# Expected: Both return 200 OK with JSON
```

**Check deployment logs:**
```bash
railway logs --service monkey-coder

# You should see:
# ✓ Using config file 'railpack.json'
# ✓ Running: yarn install --immutable (from /app)
# ✓ Running: yarn workspace @monkey-coder/web build
# ✓ Server started on 0.0.0.0:$PORT
```

## Environment Variables Checklist

### Frontend (monkey-coder)
- [x] `NODE_ENV=production`
- [x] `NEXT_OUTPUT_EXPORT=true`
- [x] `NEXT_TELEMETRY_DISABLED=1`
- [x] `NEXT_PUBLIC_APP_URL=https://coder.fastmonkey.au`
- [x] `NEXT_PUBLIC_API_URL=https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}`

### Backend (monkey-coder-backend)
- [x] `PYTHON_ENV=production`
- [x] `ML_SERVICE_URL=http://${{monkey-coder-ml.RAILWAY_PRIVATE_DOMAIN}}`
- [x] All API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)

### ML (monkey-coder-ml)
- [x] `PYTHON_ENV=production`
- [x] `TRANSFORMERS_CACHE=/app/.cache/huggingface`

## Common Questions

**Q: Why not use services/frontend/railpack.json?**  
A: Railway ALWAYS reads railpack.json from repository root, regardless of `rootDirectory` setting. Service-specific configs are ignored.

**Q: What if I want isolated service configs?**  
A: Use different config files at root level:
- Frontend: `railpack.json` (default)
- Backend: `railpack-backend.json`
- ML: `railpack-ml.json`

Set the config path in Railway Dashboard under "Config as Code".

**Q: Can I keep rootDirectory as services/frontend?**  
A: No - this breaks Yarn workspace commands. Workspaces MUST run from repo root where `package.json` exists.

**Q: How long will deployments take?**  
A: 
- Frontend: 2-3 minutes
- Backend: ~2 minutes
- ML: 25+ minutes (first time), 5 minutes (cached)

## Troubleshooting

### Error: "yarn: command not found"
**Fix**: Ensure railpack.json includes Corepack setup:
```json
"install": {
  "commands": [
    "corepack enable",
    "corepack prepare yarn@4.9.2 --activate",
    "yarn install --immutable"
  ]
}
```

### Error: "Module not found: monkey_coder"
**Fix**: Backend needs correct PYTHONPATH:
```bash
railway variables set PYTHONPATH=/app:/app/packages/core
```

### Error: "Health check failed"
**Fix**: Verify service binds to `0.0.0.0:$PORT`, not `localhost`:
```python
uvicorn.run(app, host="0.0.0.0", port=os.getenv("PORT"))
```

## Need More Help?

- **Detailed Guide**: See `RAILWAY_DEPLOYMENT.md`
- **Automated Script**: Run `bash scripts/fix-railway-services.sh`
- **Railway Docs**: https://docs.railway.com/guides/monorepo

## What Changed in This PR

1. ✅ Updated root `railpack.json` for optimal frontend deployment
2. ✅ Created `railpack-backend.json` for Python backend service
3. ✅ Created `railpack-ml.json` for ML inference service
4. ✅ Added deprecation warnings to service-specific configs
5. ✅ Created comprehensive documentation and fix scripts

**Status**: Ready to deploy - just update Railway service configurations as documented above.
