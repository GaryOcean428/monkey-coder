# Railway Environment Variables Configuration Guide

**Repository:** GaryOcean428/monkey-coder  
**Last Updated:** 2026-02-13

## Overview

This document provides a comprehensive guide for configuring Railway environment variables for the monkey-coder services. Follow Railway best practices for internal networking and secrets management.

## Services Overview

The monkey-coder platform consists of the following Railway services:

1. **monkey-coder-sandbox** - Secure code execution and browser automation service
2. **monkey-coder-backend** (or **monkey-coder-core**) - Core API service
3. **monkey-coder** - Next.js frontend web interface
4. **monkey-coder-ml** - ML service with transformer models

## Configuration by Service

### 1. monkey-coder-sandbox Service

**Purpose:** Secure containerized environment for code execution and browser automation.

**Build Configuration:** Uses Dockerfile at `services/sandbox/Dockerfile`

**Required Environment Variables:**

```bash
# Port binding (Railway auto-injects this - DO NOT set manually)
# The service code already binds to 0.0.0.0:$PORT correctly

# Authentication Secret (CRITICAL - Generate secure random token)
SANDBOX_TOKEN_SECRET=<generate-with-openssl-rand-hex-32>

# CORS Configuration (optional but recommended)
SANDBOX_ALLOW_ORIGINS=https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}
SANDBOX_ALLOW_ORIGIN_REGEX=^https?://([a-z0-9-]+\.)*railway\.app$

# Resource Limits (optional hardening)
MEMORY_LIMIT=512m
CPU_LIMIT=0.5
NETWORK_RATE_LIMIT=10mbps

# Health Check Configuration
HEALTH_CHECK_PATH=/health

# Logging
LOG_LEVEL=info
PYTHONUNBUFFERED=1
```

**Health Check Endpoint:** `/health` (already configured in Dockerfile)

**Notes:**
- The service correctly uses `PORT` environment variable and binds to `0.0.0.0`
- SANDBOX_TOKEN_SECRET must be a cryptographically secure 64-character hex string
- Generate with: `openssl rand -hex 32`

---

### 2. monkey-coder-backend Service (Core API)

**Purpose:** Main FastAPI backend service that orchestrates agents and communicates with sandbox.

**Build Configuration:** Uses `services/backend/railpack.json`

**Required Environment Variables:**

```bash
# Sandbox Service Connection (CRITICAL)
# Use Railway reference variable to sandbox's PRIVATE domain for internal communication
SANDBOX_SERVICE_URL=http://${{monkey-coder-sandbox.RAILWAY_PRIVATE_DOMAIN}}

# Sandbox Authentication (CRITICAL - Must match sandbox service)
SANDBOX_TOKEN_SECRET=<same-value-as-sandbox-service>

# ML Service Connection (already configured)
ML_SERVICE_URL=http://${{monkey-coder-ml.RAILWAY_PRIVATE_DOMAIN}}

# Database and Redis (already configured via Railway plugins)
DATABASE_URL=${{PostgreSQL.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}

# Authentication Secrets (already configured)
JWT_SECRET_KEY=${{JWT_SECRET_KEY}}
NEXTAUTH_SECRET=${{NEXTAUTH_SECRET}}

# AI Provider Keys (already configured)
OPENAI_API_KEY=${{OPENAI_API_KEY}}
ANTHROPIC_API_KEY=${{ANTHROPIC_API_KEY}}

# Application URLs
NEXT_PUBLIC_APP_URL=https://${{monkey-coder.RAILWAY_PUBLIC_DOMAIN}}
PUBLIC_APP_URL=https://${{monkey-coder.RAILWAY_PUBLIC_DOMAIN}}

# CORS Configuration
CORS_ORIGINS=https://${{monkey-coder.RAILWAY_PUBLIC_DOMAIN}}

# Environment
PYTHON_ENV=production
PYTHONUNBUFFERED=1
LOG_LEVEL=info
```

**Health Check Endpoint:** `/api/health` (configured in railpack.json)

**Notes:**
- Uses RAILWAY_PRIVATE_DOMAIN for internal service-to-service communication (zero egress cost)
- SANDBOX_TOKEN_SECRET must exactly match the sandbox service value
- Never expose sandbox credentials to frontend

---

### 3. monkey-coder Service (Frontend)

**Purpose:** Next.js web interface for the application.

**Build Configuration:** Uses `services/frontend/railpack.json`

**Required Environment Variables:**

```bash
# API URL (PUBLIC domain for browser-to-backend communication)
NEXT_PUBLIC_API_URL=https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}

# Application URL (self-reference)
NEXT_PUBLIC_APP_URL=https://${{monkey-coder.RAILWAY_PUBLIC_DOMAIN}}

# Supabase Configuration (if using OAuth)
NEXT_PUBLIC_SUPABASE_URL=${{NEXT_PUBLIC_SUPABASE_URL}}
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=${{NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY}}

# Build Configuration
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
```

**Health Check Endpoint:** `/` (root path serves the application)

**Security Notes:**
- ✅ NO sandbox secrets or tokens in frontend service
- ✅ Uses PUBLIC domain for API URL (browser-accessible)
- ✅ Only NEXT_PUBLIC_* variables are exposed to browser
- ❌ Never set SANDBOX_TOKEN_SECRET in frontend

---

### 4. monkey-coder-ml Service

**Purpose:** ML service with transformer models and GPU support.

**Build Configuration:** Uses `services/ml/railpack.json`

**Environment Variables:** (Already configured - no changes needed)

```bash
LOG_LEVEL=info
HEALTH_CHECK_PATH=/api/health
PYTHONPATH=/app
CUDA_VISIBLE_DEVICES=0
TRANSFORMERS_CACHE=/app/.cache/huggingface
PYTHON_ENV=production
```

---

## Security Best Practices

### 1. Secret Generation

Generate the SANDBOX_TOKEN_SECRET using a cryptographically secure random generator:

```bash
# Generate a secure 64-character hex token
openssl rand -hex 32

# Example output: f3a8b9c2d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1
```

### 2. Railway Reference Variables

Always use Railway's built-in reference variables for service discovery:

✅ **Correct:**
```bash
SANDBOX_SERVICE_URL=http://${{monkey-coder-sandbox.RAILWAY_PRIVATE_DOMAIN}}
NEXT_PUBLIC_API_URL=https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}
```

❌ **Incorrect:**
```bash
SANDBOX_SERVICE_URL=http://monkey-coder-sandbox:8001
NEXT_PUBLIC_API_URL=https://api.example.com
```

### 3. Public vs Private Domains

**Use RAILWAY_PRIVATE_DOMAIN for:**
- Internal service-to-service communication
- Backend → Sandbox communication
- Backend → ML communication
- No egress costs, lower latency

**Use RAILWAY_PUBLIC_DOMAIN for:**
- Browser → Backend communication (frontend variables)
- External webhooks
- Public API endpoints

### 4. No Secrets in Frontend

Frontend environment variables prefixed with `NEXT_PUBLIC_` are bundled into the JavaScript and exposed to browsers. **Never** set secrets in frontend:

❌ **Never do this:**
```bash
NEXT_PUBLIC_SANDBOX_TOKEN=xxx  # EXPOSED TO BROWSERS!
NEXT_PUBLIC_JWT_SECRET=xxx     # SECURITY BREACH!
```

---

## Application Steps

### Option 1: Railway Dashboard (Recommended)

1. Navigate to Railway Dashboard: https://railway.app/
2. Select the **your project** project (ID: 9n)
3. For each service listed above:
   - Click on the service name
   - Go to **Variables** tab
   - Click **+ New Variable**
   - Add each variable from the configuration above
   - Click **Deploy** to apply changes

### Option 2: Railway CLI

```bash
# Login to Railway
railway login

# Link to Railway project
railway link <your-project-id>

# Set variables for sandbox service
railway variables set \
  --service monkey-coder-sandbox \
  SANDBOX_TOKEN_SECRET=$(openssl rand -hex 32) \
  SANDBOX_ALLOW_ORIGINS='https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}' \
  SANDBOX_ALLOW_ORIGIN_REGEX='^https?://([a-z0-9-]+\.)*railway\.app$' \
  LOG_LEVEL=info \
  PYTHONUNBUFFERED=1

# Set variables for backend service
railway variables set \
  --service monkey-coder-backend \
  SANDBOX_SERVICE_URL='http://${{monkey-coder-sandbox.RAILWAY_PRIVATE_DOMAIN}}' \
  SANDBOX_TOKEN_SECRET=<copy-from-sandbox-service> \
  PYTHON_ENV=production \
  PYTHONUNBUFFERED=1 \
  LOG_LEVEL=info

# Set variables for frontend service (verify existing)
railway variables set \
  --service monkey-coder \
  NEXT_PUBLIC_API_URL='https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}' \
  NODE_ENV=production \
  NEXT_TELEMETRY_DISABLED=1

# Verify variables
railway variables --service monkey-coder-sandbox
railway variables --service monkey-coder-backend
railway variables --service monkey-coder
```

### Option 3: Railway API (Advanced)

Use Railway's GraphQL API for programmatic configuration. See: https://docs.railway.com/reference/public-api

---

## Verification Steps

After applying the configuration:

### 1. Check Service Health

```bash
# Check sandbox service
curl https://<monkey-coder-sandbox-domain>.railway.app/health

# Check backend service
curl https://<monkey-coder-backend-domain>.railway.app/api/health

# Check frontend service
curl https://<monkey-coder-domain>.railway.app/
```

### 2. Verify Internal Connectivity

From the backend service logs, verify it can reach the sandbox:

```bash
railway logs --service monkey-coder-backend | grep -i sandbox
```

Expected log entries:
- "Connected to sandbox service"
- "Sandbox health check passed"

### 3. Test Sandbox Execution

Make an authenticated request from backend to sandbox:

```bash
# This should work from backend service
curl -X POST https://<sandbox-internal-url>/sandbox/execute \
  -H "Authorization: Bearer <sandbox-token>" \
  -H "Content-Type: application/json" \
  -d '{"sandbox_type": "code", "action": "execute", "code": "print(\"Hello\")"}'
```

### 4. Security Audit

- [ ] SANDBOX_TOKEN_SECRET is set in both sandbox and backend (same value)
- [ ] SANDBOX_TOKEN_SECRET is NOT set in frontend
- [ ] Backend uses RAILWAY_PRIVATE_DOMAIN for sandbox communication
- [ ] Frontend uses RAILWAY_PUBLIC_DOMAIN for API communication
- [ ] All secrets are generated with `openssl rand -hex 32`
- [ ] No hardcoded hostnames or ports in variables

---

## Troubleshooting

### Issue: Backend cannot connect to sandbox

**Symptoms:** Connection refused, timeout errors in backend logs

**Solutions:**
1. Verify SANDBOX_SERVICE_URL uses `RAILWAY_PRIVATE_DOMAIN`
2. Check both services are in the same Railway project
3. Verify Railway private networking is enabled (automatic)
4. Check sandbox service is healthy: `railway logs --service monkey-coder-sandbox`

### Issue: Sandbox returns 401 Unauthorized

**Symptoms:** Authentication errors when backend calls sandbox

**Solutions:**
1. Verify SANDBOX_TOKEN_SECRET matches in both services
2. Check token has not been regenerated in one service only
3. Review sandbox logs for token validation errors

### Issue: Frontend cannot reach backend

**Symptoms:** Network errors in browser console

**Solutions:**
1. Verify NEXT_PUBLIC_API_URL uses `RAILWAY_PUBLIC_DOMAIN` (not PRIVATE)
2. Check CORS_ORIGINS in backend includes frontend domain
3. Verify backend service is deployed and healthy

### Issue: Variables not taking effect

**Symptoms:** Services using default/old values

**Solutions:**
1. Redeploy the service after setting variables
2. Check Railway deployment logs for variable injection
3. Verify variable names match exactly (case-sensitive)

---

## Summary of Changes

### Variables Added/Updated:

**monkey-coder-sandbox:**
- ✅ SANDBOX_TOKEN_SECRET (new secret)
- ✅ SANDBOX_ALLOW_ORIGINS (new)
- ✅ SANDBOX_ALLOW_ORIGIN_REGEX (new)

**monkey-coder-backend:**
- ✅ SANDBOX_SERVICE_URL (new reference variable)
- ✅ SANDBOX_TOKEN_SECRET (new secret, matches sandbox)

**monkey-coder (frontend):**
- ✅ NEXT_PUBLIC_API_URL (verify existing configuration)
- ✅ No sandbox secrets (security verified)

**monkey-coder-ml:**
- ✅ No changes needed (already configured)

### Security Posture:

- ✅ All internal communication uses private domains
- ✅ Secrets are not hardcoded or exposed
- ✅ Frontend has no access to sandbox credentials
- ✅ Railway reference variables used throughout
- ✅ Authentication between services implemented

---

## References

- Railway Documentation: https://docs.railway.com/
- Railway Variables: https://docs.railway.com/reference/variables
- Railway Private Networking: https://docs.railway.com/reference/private-networking
- Railway Reference Variables: https://docs.railway.com/guides/variables#referencing-another-services-variable

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-12  
**Maintained By:** DevOps Team
