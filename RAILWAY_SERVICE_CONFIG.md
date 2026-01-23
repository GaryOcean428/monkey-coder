# Railway Service Configuration

## Critical Fix Applied

**Issue**: The root `railway.toml` was overriding service-specific `railpack.json` files, causing the backend service to try running the `serve` command (Node.js) instead of `uvicorn` (Python).

**Solution**: Removed `railway.toml` to ensure Railway uses the correct `railpack.json` for each service.

---

## Service Configuration in Railway Dashboard

Each service must be configured to use its own `railpack.json` file. Configure the **Root Directory** setting for each service:

### 1. Frontend Service (`monkey-coder`)

**Settings → Service Settings:**
- **Root Directory**: `/` (or leave blank)
- **Railpack Config**: `/railpack.json` (auto-detected)

**Expected Behavior:**
- Uses Node.js 20
- Runs: `serve -s packages/web/out -l $PORT -c serve.json`
- Health check: `/`

### 2. Backend Service (`monkey-coder-backend`)

**Settings → Service Settings:**
- **Root Directory**: `/services/backend`
- **Railpack Config**: `/services/backend/railpack.json` (auto-detected)

**Expected Behavior:**
- Uses Python 3.12
- Runs: `/app/.venv/bin/python -m uvicorn monkey_coder.app.main:app --host 0.0.0.0 --port $PORT`
- Health check: `/api/health`

**Environment Variables Required:**
```bash
LOG_LEVEL=info
HEALTH_CHECK_PATH=/api/health
PYTHONPATH=/app:/app/packages/core
ML_SERVICE_URL=http://${{monkey-coder-ml.RAILWAY_PRIVATE_DOMAIN}}
```

### 3. ML Service (`monkey-coder-ml`)

**Settings → Service Settings:**
- **Root Directory**: `/services/ml`
- **Railpack Config**: `/services/ml/railpack.json` (auto-detected)

**Expected Behavior:**
- Uses Python 3.12
- Runs: `/app/.venv/bin/python -m uvicorn services.ml.ml_server:app --host 0.0.0.0 --port $PORT`
- Health check: `/api/health`

**Environment Variables Required:**
```bash
LOG_LEVEL=info
HEALTH_CHECK_PATH=/api/health
PYTHONPATH=/app:/app/services/ml
CUDA_VISIBLE_DEVICES=0
TRANSFORMERS_CACHE=/app/.cache/huggingface
```

---

## Build Config Priority

Railway honors configs in this order (from the cheat sheet):
1. **Dockerfile** (highest priority)
2. **railpack.json**
3. **railway.*** (railway.toml, railway.json)
4. **Nixpacks** (auto-detection, lowest priority)

**Best Practice**: Use only **one** build config method. We've chosen **railpack.json** for all services.

---

## Verification Steps

After updating Railway service settings:

1. **Trigger new deployment** for each service
2. **Check build logs** for correct provider detection:
   - Frontend: "Detected Node.js"
   - Backend/ML: "Detected Python"
3. **Check deploy logs** for correct start command
4. **Test health endpoints**:
   ```bash
   curl https://monkey-coder.up.railway.app/
   curl https://monkey-coder-backend-production.up.railway.app/api/health
   curl https://monkey-coder-ml.up.railway.app/api/health
   ```

---

## Troubleshooting

### Service still trying to run wrong command

**Cause**: Root directory not set correctly in Railway dashboard.

**Fix**: Go to Service Settings → Root Directory → Set to correct path for that service.

### "No such file or directory" errors

**Cause**: Start command uses wrong path or virtualenv not found.

**Fix**: Verify `railpack.json` uses absolute paths (`/app/.venv/bin/python`).

### Health check timeout

**Cause**: Service not binding to `0.0.0.0` or wrong port.

**Fix**: Ensure code binds to `0.0.0.0` and uses `$PORT` environment variable.

---

## Files to Keep vs Remove

### ✅ Keep (Active Configs)
- `/railpack.json` (frontend)
- `/services/backend/railpack.json` (backend)
- `/services/ml/railpack.json` (ML)

### ❌ Removed (Conflicts)
- ~~`/railway.toml`~~ (was overriding railpack.json)
- No `nixpacks.toml` files (except sandbox service if needed)
- No root `Dockerfile` (except for specific services)

### 4. Sandbox Service (`monkey-coder-sandbox`) - OPTIONAL

**Status**: ⚠️ Optional - Deploy only if needed for cloud-based execution

**Settings → Service Settings:**
- **Root Directory**: `/services/sandbox`
- **Railpack Config**: `/services/sandbox/railpack.json` (uses Dockerfile)

**Expected Behavior:**
- Uses Docker with Python 3.12
- Runs: `/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf`
- Health check: `/health`

**When to Deploy:**
- Need browser automation via BrowserBase for web users
- Require cloud-based code execution API endpoint
- Backend needs remote sandbox without local Docker access
- Building multi-tenant sandbox management platform

**When NOT to Deploy:**
- CLI-only deployment (CLI has local Docker sandbox)
- No browser automation requirements
- Backend doesn't execute untrusted code
- Cost-sensitive deployment

**Environment Variables Required:**
```bash
SANDBOX_TOKEN_SECRET=<secure-random-secret>
SANDBOX_ALLOW_ORIGINS=https://your-frontend.railway.app
SANDBOX_ALLOW_ORIGIN_REGEX=^https?://([a-z0-9-]+\.)*railway\.app$

# Optional: For E2B code execution
E2B_API_KEY=<your-e2b-api-key>

# Optional: For BrowserBase browser automation
BROWSERBASE_API_KEY=<your-browserbase-api-key>
BROWSERBASE_PROJECT_ID=<your-browserbase-project-id>

# Resource limits
SANDBOX_MAX_MEMORY_MB=512
SANDBOX_MAX_CPU_PERCENT=50.0
SANDBOX_MODE=1
```

**Backend Integration (if deployed):**
Add to backend service environment variables:
```bash
SANDBOX_SERVICE_URL=http://${{monkey-coder-sandbox.RAILWAY_PRIVATE_DOMAIN}}
SANDBOX_TOKEN_SECRET=${{monkey-coder-sandbox.SANDBOX_TOKEN_SECRET}}
```

---

## Service Deployment Decision Matrix

| Service | Required | Purpose | Cost Impact |
|---------|----------|---------|-------------|
| **Frontend** | ✅ Yes | Web UI | Base |
| **Backend** | ✅ Yes | API orchestration | Base |
| **ML** | ✅ Yes | Model inference | Base |
| **Sandbox** | ⚠️ Optional | Cloud execution | +25-50% |

**Recommendation**: Start with 3 core services (frontend, backend, ml). Add sandbox service only if you need browser automation or cloud-based code execution API.

---

## Reference Documentation

- **Detailed deployment guide**: `docs/production-deployment-guide.md`
- **Railway architecture**: `docs/deployment/railway-architecture.md`
- **Sandbox deployment guide**: `docs/deployment/sandbox-service-deployment-guide.md`
- **Service configuration**: `docs/deployment/railway-configuration.md`
- **Optimization tips**: `docs/deployment/railway-optimization.md`
