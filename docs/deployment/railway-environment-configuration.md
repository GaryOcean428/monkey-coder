# Railway Environment Variables Configuration Summary

**Repository:** GaryOcean428/monkey-coder  
**Last Updated:** 2026-02-13  
**Status:** ✅ Configuration Guide

---

## Executive Summary

This document summarizes the Railway environment variable configuration for the monkey-coder services. The configuration follows Railway best practices for internal networking, secrets management, and service discovery.

## Services Overview

### 1. **monkey-coder-sandbox**
- **Purpose:** Secure containerized environment for code execution and browser automation
- **Build:** Dockerfile at `services/sandbox/Dockerfile`
- **Health Check:** `/health`
- **New Variables:** 5

### 2. **monkey-coder-backend** (Core API)
- **Purpose:** Main FastAPI backend service that orchestrates agents
- **Build:** `services/backend/railpack.json`
- **Health Check:** `/api/health`
- **New Variables:** 5

### 3. **monkey-coder** (Frontend)
- **Purpose:** Next.js web interface
- **Build:** `services/frontend/railpack.json`
- **Health Check:** `/`
- **New Variables:** 3 (verification/update)

### 4. **monkey-coder-ml**
- **Purpose:** ML service with transformer models
- **Build:** `services/ml/railpack.json`
- **Health Check:** `/api/health`
- **Changes:** None (already configured)

---

## Environment Variables by Service

### monkey-coder-sandbox Service

| Variable | Value | Purpose |
|----------|-------|---------|
| `SANDBOX_TOKEN_SECRET` | `<generate-with-openssl-rand-hex-32>` | Authentication secret for API access |
| `SANDBOX_ALLOW_ORIGINS` | `https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}` | CORS allowed origins |
| `SANDBOX_ALLOW_ORIGIN_REGEX` | `^https?://([a-z0-9-]+\.)*railway\.app$` | CORS regex pattern |
| `LOG_LEVEL` | `info` | Logging verbosity |
| `PYTHONUNBUFFERED` | `1` | Python output buffering |

**Security Notes:**
- ✅ PORT auto-injected by Railway (service already binds to 0.0.0.0:$PORT)
- ✅ SANDBOX_TOKEN_SECRET must be 64-character hex (use `openssl rand -hex 32`)
- ✅ Uses Railway reference variables for CORS configuration

---

### monkey-coder-backend Service

| Variable | Value | Purpose |
|----------|-------|---------|
| `SANDBOX_SERVICE_URL` | `http://${{monkey-coder-sandbox.RAILWAY_PRIVATE_DOMAIN}}` | Sandbox service internal URL |
| `SANDBOX_TOKEN_SECRET` | `<same-as-sandbox-service>` | Authentication secret (must match sandbox) |
| `PYTHON_ENV` | `production` | Python environment mode |
| `PYTHONUNBUFFERED` | `1` | Python output buffering |
| `LOG_LEVEL` | `info` | Logging verbosity |

**Security Notes:**
- ✅ Uses RAILWAY_PRIVATE_DOMAIN for internal communication (zero egress cost)
- ✅ SANDBOX_TOKEN_SECRET must exactly match sandbox service value
- ✅ No hardcoded hostnames or ports

---

### monkey-coder Service (Frontend)

| Variable | Value | Purpose |
|----------|-------|---------|
| `NEXT_PUBLIC_API_URL` | `https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}` | Backend API public URL |
| `NODE_ENV` | `production` | Node.js environment mode |
| `NEXT_TELEMETRY_DISABLED` | `1` | Disable Next.js telemetry |

**Security Notes:**
- ✅ Uses RAILWAY_PUBLIC_DOMAIN for browser-accessible API URL
- ✅ NO sandbox secrets (verified secure)
- ✅ Only NEXT_PUBLIC_* variables exposed to browser

---

## Configuration Methods

Three methods are provided to apply these configurations:

### Method 1: Railway Dashboard (Recommended for Manual Setup)

1. Navigate to https://railway.app/
2. Select AetherOS project (ID: <your-project-id>)
3. For each service, go to Variables tab
4. Add variables as specified above
5. Click Deploy to apply changes

**Pros:** Visual interface, easy to verify  
**Cons:** Manual process, time-consuming for multiple variables

---

### Method 2: Railway CLI Script (Recommended for Automation)

```bash
# Install Railway CLI if not already installed
npm install -g @railway/cli

# Login to Railway
railway login

# Link to AetherOS project
railway link 9n

# Run configuration script

# Or dry-run first
```

**Features:**
- ✅ Automatically generates secure SANDBOX_TOKEN_SECRET
- ✅ Applies all variables in correct order
- ✅ Dry-run mode for preview
- ✅ Color-coded output with status
- ✅ Comprehensive error handling

**Pros:** Fast, automated, reproducible  
**Cons:** Requires Railway CLI installation

---

### Method 3: Railway API Script (Advanced)

```bash
# Get Railway API token from https://railway.app/account/tokens
export RAILWAY_API_TOKEN=your_token_here

# Install dependencies
pip install requests

# Run configuration script

# Or dry-run first
```

**Features:**
- ✅ Uses Railway GraphQL API directly
- ✅ Programmatic configuration
- ✅ Works in CI/CD pipelines
- ✅ No Railway CLI dependency

**Pros:** API-based, CI/CD friendly  
**Cons:** Requires API token, Python setup

---

## Security Architecture

### Internal Communication Flow

```
┌─────────────────┐
│   Frontend      │
│ (monkey-coder)  │
└────────┬────────┘
         │ HTTPS (PUBLIC)
         │ NEXT_PUBLIC_API_URL
         ▼
┌─────────────────┐
│    Backend      │  HTTP (PRIVATE)        ┌─────────────────┐
│ (monkey-coder-  │◄──────────────────────►│      ML         │
│    backend)     │  ML_SERVICE_URL        │ (monkey-coder-  │
└────────┬────────┘                        │     ml)         │
         │ HTTP (PRIVATE)                  └─────────────────┘
         │ SANDBOX_SERVICE_URL
         │ + SANDBOX_TOKEN_SECRET
         ▼
┌─────────────────┐
│    Sandbox      │
│ (monkey-coder-  │
│    sandbox)     │
└─────────────────┘
```

### Security Principles Applied

✅ **Principle 1: Internal Communication via Private Networks**
- Backend → Sandbox: Uses `RAILWAY_PRIVATE_DOMAIN`
- Backend → ML: Uses `RAILWAY_PRIVATE_DOMAIN`
- Benefits: Zero egress costs, lower latency, not exposed to internet

✅ **Principle 2: Public Communication via Public Domains**
- Frontend → Backend: Uses `RAILWAY_PUBLIC_DOMAIN`
- External webhooks → Services: Uses `RAILWAY_PUBLIC_DOMAIN`
- Benefits: Browser-accessible, proper HTTPS certificates

✅ **Principle 3: Secret Management**
- SANDBOX_TOKEN_SECRET generated with cryptographic RNG
- Same secret shared only between sandbox and backend
- Never exposed in frontend or logs
- 64-character hex format (256-bit entropy)

✅ **Principle 4: Service Discovery**
- No hardcoded hostnames or ports
- Railway reference variables (`${{service.RAILWAY_*_DOMAIN}}`)
- Automatically updated when services are redeployed

✅ **Principle 5: Least Privilege**
- Frontend has NO access to sandbox
- Frontend only knows backend public URL
- Sandbox only accessible via authenticated backend

---

## Verification Steps

After applying the configuration:

### 1. Verify Variables Are Set

```bash
# Check each service
railway variables --service monkey-coder-sandbox
railway variables --service monkey-coder-backend
railway variables --service monkey-coder
```

**Expected Output:**
- All variables listed above should appear
- SANDBOX_TOKEN_SECRET should match in sandbox and backend

---

### 2. Redeploy Services

```bash
# Redeploy in order (dependencies first)
railway redeploy --service monkey-coder-sandbox
railway redeploy --service monkey-coder-backend
railway redeploy --service monkey-coder
```

**Expected:** Services rebuild and restart with new variables

---

### 3. Check Health Endpoints

```bash
# Get service URLs from Railway dashboard, then:

# Check sandbox health
curl https://<sandbox-domain>.railway.app/health

# Check backend health
curl https://<backend-domain>.railway.app/api/health

# Check frontend
curl https://<frontend-domain>.railway.app/
```

**Expected Status:** All return 200 OK with `{"status": "healthy"}`

---

### 4. Monitor Service Logs

```bash
# Watch logs in real-time
railway logs --service monkey-coder-sandbox --follow
railway logs --service monkey-coder-backend --follow
```

**Look for:**
- ✅ "Sandbox Service started successfully"
- ✅ "Connected to sandbox service"
- ✅ No authentication errors
- ❌ NO connection refused errors
- ❌ NO 401 unauthorized errors

---

### 5. Test Sandbox Execution

From backend service, test sandbox connectivity:

```python
# This should work after configuration
from monkey_coder.sandbox_client import SandboxClient

client = SandboxClient()
result = await client.execute_code(
    code='print("Hello from sandbox!")',
    execution_id="test-001"
)
print(result)
```

**Expected:** Successful code execution with output

---

## Troubleshooting

### Issue: Backend cannot connect to sandbox

**Symptoms:**
- Connection refused errors
- Timeout errors in backend logs

**Solutions:**
1. ✓ Verify `SANDBOX_SERVICE_URL` uses `RAILWAY_PRIVATE_DOMAIN`
2. ✓ Check both services are in same Railway project
3. ✓ Verify Railway private networking is enabled (automatic)
4. ✓ Check sandbox service is healthy: `railway logs --service monkey-coder-sandbox`

---

### Issue: Sandbox returns 401 Unauthorized

**Symptoms:**
- Authentication errors when backend calls sandbox
- "Invalid token" in sandbox logs

**Solutions:**
1. ✓ Verify `SANDBOX_TOKEN_SECRET` matches in both services
2. ✓ Check token wasn't regenerated in one service only
3. ✓ Review sandbox security.py for token validation logic
4. ✓ Test token generation: `openssl rand -hex 32`

---

### Issue: Frontend cannot reach backend

**Symptoms:**
- Network errors in browser console
- CORS errors

**Solutions:**
1. ✓ Verify `NEXT_PUBLIC_API_URL` uses `RAILWAY_PUBLIC_DOMAIN`
2. ✓ Check `CORS_ORIGINS` in backend includes frontend domain
3. ✓ Verify backend service is deployed and healthy
4. ✓ Check browser network tab for actual error

---

### Issue: Variables not taking effect

**Symptoms:**
- Services using default/old values
- Variables visible in dashboard but not in logs

**Solutions:**
1. ✓ Redeploy service after setting variables
2. ✓ Check Railway deployment logs for variable injection
3. ✓ Verify variable names match exactly (case-sensitive)
4. ✓ Clear Railway build cache if needed

---

## Files Created/Modified

### New Files

1. **`docs/deployment/railway-aetheros-config.md`**
   - Comprehensive configuration documentation
   - Step-by-step instructions
   - Troubleshooting guide

   - Bash script for Railway CLI configuration
   - Automated setup with dry-run mode
   - Color-coded output

   - Python script for Railway API configuration
   - GraphQL-based automation
   - CI/CD friendly

4. **`RAILWAY_CONFIG_SUMMARY.md`** (this file)
   - Executive summary
   - Quick reference
   - Verification checklist

### Modified Files

1. **`.env.railway.example`**
   - Updated sandbox variable documentation
   - Added SANDBOX_ALLOW_ORIGINS example
   - Enhanced comments

---

## Configuration Checklist

Use this checklist to verify the configuration:

### Pre-Configuration
- [ ] Railway CLI installed (`npm install -g @railway/cli`)
- [ ] Logged into Railway (`railway login`)
- [ ] Project linked (`railway link 9n`)
- [ ] Generated SANDBOX_TOKEN_SECRET (`openssl rand -hex 32`)

### Configuration Applied
- [ ] monkey-coder-sandbox variables set (5 variables)
- [ ] monkey-coder-backend variables set (5 variables)
- [ ] monkey-coder (frontend) variables set (3 variables)
- [ ] All variables verified in Railway Dashboard

### Deployment
- [ ] Services redeployed (sandbox, backend, frontend)
- [ ] All services show "healthy" status
- [ ] No deployment errors in logs

### Verification
- [ ] Health endpoints return 200 OK
- [ ] Backend logs show sandbox connection
- [ ] No authentication errors in logs
- [ ] Frontend can reach backend API

### Security Audit
- [ ] SANDBOX_TOKEN_SECRET is 64-character hex
- [ ] Same token in sandbox and backend
- [ ] NO sandbox secrets in frontend
- [ ] All internal URLs use RAILWAY_PRIVATE_DOMAIN
- [ ] All browser URLs use RAILWAY_PUBLIC_DOMAIN

---

## Next Steps

1. **Choose Configuration Method**
   - For one-time setup: Use Railway Dashboard
   - For automation: Use Railway CLI script
   - For CI/CD: Use Railway API script

2. **Apply Configuration**
   - Follow instructions for chosen method
   - Run dry-run first to preview changes
   - Apply actual configuration

3. **Verify Deployment**
   - Complete verification checklist
   - Monitor service logs
   - Test functionality

4. **Document Project-Specific Details**
   - Save generated SANDBOX_TOKEN_SECRET securely
   - Note actual service URLs
   - Update team documentation

---

## Support Resources

- **Railway Documentation:** https://docs.railway.com/
- **Railway Variables Guide:** https://docs.railway.com/reference/variables
- **Railway Private Networking:** https://docs.railway.com/reference/private-networking
- **Repository Documentation:** `docs/deployment/`

---

## Appendix: Variable Reference Quick Table

| Service | Variable | Type | Source |
|---------|----------|------|--------|
| sandbox | SANDBOX_TOKEN_SECRET | Secret | Generated |
| sandbox | SANDBOX_ALLOW_ORIGINS | Config | Reference Var |
| sandbox | SANDBOX_ALLOW_ORIGIN_REGEX | Config | Static |
| sandbox | LOG_LEVEL | Config | Static |
| sandbox | PYTHONUNBUFFERED | Config | Static |
| backend | SANDBOX_SERVICE_URL | Reference | Private Domain |
| backend | SANDBOX_TOKEN_SECRET | Secret | From Sandbox |
| backend | PYTHON_ENV | Config | Static |
| backend | PYTHONUNBUFFERED | Config | Static |
| backend | LOG_LEVEL | Config | Static |
| frontend | NEXT_PUBLIC_API_URL | Reference | Public Domain |
| frontend | NODE_ENV | Config | Static |
| frontend | NEXT_TELEMETRY_DISABLED | Config | Static |

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-12  
**Status:** Ready for Implementation
