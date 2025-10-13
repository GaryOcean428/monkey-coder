# Railway Production Deployment Checklist

This checklist ensures all Railway services are properly configured for production deployment with no build failures and all production features enabled.

## Pre-Deployment Checklist

### Phase 1: Build System Validation ✅

- [x] **Lockfile Stability**
  - Yarn 4.9.2 is activated via Corepack
  - `yarn.lock` is committed and stable
  - `yarn install --immutable --check-cache` passes locally
  - No `YN0028` errors when running immutable install

- [x] **Railpack Configuration**
  - All three railpack configs use `yarn install --immutable`
  - `railpack.json` (frontend) - ✅ Verified
  - `railpack-backend.json` (API) - ✅ Verified
  - `railpack-ml.json` (ML) - ✅ Verified
  - No competing build configs (Dockerfile, railway.toml, etc.)

- [ ] **Railway Service Configuration**
  ```bash
  # For each service, verify:
  railway service --service <service-id>
  # Check:
  # - Root Directory: / or blank
  # - Build Command: blank (let railpack handle)
  # - Start Command: blank (let railpack handle)
  # - Config Path: correct railpack file
  ```

### Phase 2: Environment Variables

#### Critical Secrets (Deployment Fails Without These)

- [ ] **JWT_SECRET_KEY** - Generate: `openssl rand -hex 32`
- [ ] **NEXTAUTH_SECRET** - Generate: `openssl rand -hex 32`
- [ ] **DATABASE_URL** - Auto-provided by Railway PostgreSQL plugin
- [ ] **OPENAI_API_KEY** or **ANTHROPIC_API_KEY** - At least one required

#### Production Features

- [ ] **Redis Configuration**
  ```bash
  railway variables set --service <backend-service-id> \
    REDIS_URL="redis://..." \
    SESSION_BACKEND="redis" \
    RATE_LIMIT_BACKEND="redis"
  ```

- [ ] **Email Service (Resend)**
  ```bash
  railway variables set --service <backend-service-id> \
    RESEND_API_KEY="re_..." \
    NOTIFICATION_EMAIL_FROM="noreply@fastmonkey.au" \
    EMAIL_PROVIDER="resend" \
    SMTP_ENABLED="true"
  ```
  - Domain verified in Resend dashboard: https://resend.com/domains

- [ ] **OAuth Providers**
  
  **Google OAuth Setup:**
  1. Go to: https://console.cloud.google.com/apis/credentials
  2. Create OAuth 2.0 Client ID
  3. Add callback: `https://coder.fastmonkey.au/api/v1/auth/oauth/google/callback`
  4. Set in Railway:
  ```bash
  railway variables set --service <backend-service-id> \
    GOOGLE_OAUTH_CLIENT_ID="....apps.googleusercontent.com" \
    GOOGLE_OAUTH_CLIENT_SECRET="..."
  ```

  **GitHub OAuth Setup:**
  1. Go to: https://github.com/settings/developers
  2. Create New OAuth App
  3. Add callback: `https://coder.fastmonkey.au/api/v1/auth/oauth/github/callback`
  4. Set in Railway:
  ```bash
  railway variables set --service <backend-service-id> \
    GITHUB_OAUTH_CLIENT_ID="..." \
    GITHUB_OAUTH_CLIENT_SECRET="..."
  ```

  **OAuth Base Configuration:**
  ```bash
  railway variables set --service <backend-service-id> \
    OAUTH_REDIRECT_BASE="https://coder.fastmonkey.au/api/v1/auth/oauth" \
    OAUTH_STATE_SECRET="$(openssl rand -hex 32)"
  ```

- [ ] **Application URLs**
  ```bash
  railway variables set --service <backend-service-id> \
    NEXT_PUBLIC_APP_URL="https://coder.fastmonkey.au" \
    NEXT_PUBLIC_API_URL="https://monkey-coder-backend-production.up.railway.app" \
    PUBLIC_APP_URL="https://coder.fastmonkey.au"
  ```

#### Recommended Variables

- [ ] **Email Notifications**
  ```bash
  railway variables set --service <backend-service-id> \
    ADMIN_NOTIFICATION_EMAILS="admin@fastmonkey.au" \
    ENQUIRY_NOTIFICATION_EMAILS="enquiries@fastmonkey.au" \
    ROLLBACK_NOTIFICATION_EMAILS="ops@fastmonkey.au"
  ```

- [ ] **Error Tracking (Sentry)**
  ```bash
  railway variables set --service <backend-service-id> \
    SENTRY_DSN="https://...@sentry.io/..." \
    SENTRY_ENVIRONMENT="production"
  ```

- [ ] **Security Configuration**
  ```bash
  railway variables set --service <backend-service-id> \
    ENV="production" \
    NODE_ENV="production" \
    PYTHON_ENV="production" \
    CORS_ORIGINS="https://coder.fastmonkey.au" \
    TRUSTED_HOSTS="coder.fastmonkey.au,*.railway.app" \
    ENABLE_SECURITY_HEADERS="true"
  ```

### Phase 3: Railway Plugins

- [ ] **PostgreSQL Plugin**
  - Add to project: `railway add postgresql`
  - Verify DATABASE_URL is auto-populated
  - Check connection: `railway run --service <backend-service-id> "python -c 'import os; print(os.getenv(\"DATABASE_URL\"))'"

- [ ] **Redis Plugin (Recommended)**
  - Add to project: `railway add redis`
  - Verify REDIS_URL is auto-populated
  - Test connection:
  ```bash
  railway run --service <backend-service-id> "python -c 'import redis; r=redis.from_url(os.getenv(\"REDIS_URL\")); print(r.ping())'"
  ```

### Phase 4: Service Configuration

#### Frontend Service (monkey-coder)

- [ ] Root Directory: `/` or blank
- [ ] Build Command: blank
- [ ] Start Command: blank
- [ ] Config Path: `railpack.json`
- [ ] Environment Variables:
  - `RAILWAY_CONFIG_FILE=railpack.json`
  - `NEXT_PUBLIC_API_URL` (backend URL)

#### Backend Service (monkey-coder-backend)

- [ ] Root Directory: `/` or blank
- [ ] Build Command: blank
- [ ] Start Command: blank
- [ ] Config Path: `railpack-backend.json`
- [ ] Environment Variables:
  - `RAILWAY_CONFIG_FILE=railpack-backend.json`
  - All critical secrets configured
  - All production features configured

#### ML Service (monkey-coder-ml)

- [ ] Root Directory: `/` or blank
- [ ] Build Command: blank
- [ ] Start Command: blank
- [ ] Config Path: `railpack-ml.json`
- [ ] Environment Variables:
  - `RAILWAY_CONFIG_FILE=railpack-ml.json`
- [ ] Health Check Timeout: 600 seconds (first build takes 25+ minutes)

## Deployment Process

### Step 1: Verify Local Build

```bash
# 1. Clean and rebuild
rm -rf node_modules .yarn/cache
yarn install --immutable --check-cache

# 2. Verify no lockfile changes
git status yarn.lock
# Should show: nothing to commit, working tree clean

# 3. Test Python backend
cd packages/core
pip install -r requirements.txt
# Should complete without errors
```

### Step 2: Deploy Services

```bash
# After all environment variables are set:

# Deploy frontend
railway redeploy --service ccc58ca2-1f4b-4086-beb6-2321ac7dab40

# Deploy backend
railway redeploy --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed

# Deploy ML
railway redeploy --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa

# Monitor logs
railway logs --service monkey-coder-backend --tail
```

### Step 3: Verify Deployment

#### Build Success Signals

Look for these in logs:
```
✅ yarn install --immutable
✅ ➤ YN0000: · Done with warnings in X.XXs
✅ No YN0028 error
✅ Build succeeds
✅ Health check passed
```

#### Health Check Validation

```bash
# Basic health
curl https://coder.fastmonkey.au/api/health
# Expected: {"status": "healthy", "version": "2.0.0", ...}

# Readiness check (includes Redis, email, OAuth status)
curl https://monkey-coder-backend-production.up.railway.app/health/readiness | jq
# Expected: {"status": "ready", "checks": {...all services}}

# Comprehensive health
curl https://monkey-coder-backend-production.up.railway.app/health/comprehensive | jq
# Expected: {"status": "healthy", "components": {...}}
```

#### Feature Verification

```bash
# OAuth Configuration Status
curl https://monkey-coder-backend-production.up.railway.app/api/v1/auth/oauth/google/initiate | jq .degraded
# Expected: false (not true)

# Redis Connection
railway run --service <backend-service-id> \
  "python -c 'import redis; r=redis.from_url(os.getenv(\"REDIS_URL\")); print(r.ping())'"
# Expected: True

# Email Configuration
curl -H "Authorization: Bearer <your-api-key>" \
  https://monkey-coder-backend-production.up.railway.app/api/v1/enquiry/status | jq
# Expected: {"status": "active", "configuration": {"resend_configured": true, ...}}
```

## Post-Deployment Monitoring

### Immediate Checks (First 5 Minutes)

- [ ] All services showing "DEPLOYED" status in Railway dashboard
- [ ] No error spikes in logs
- [ ] Health endpoints returning 200 OK
- [ ] Frontend loads correctly at `https://coder.fastmonkey.au`
- [ ] Backend API responds at `/api/health`

### First Hour Monitoring

- [ ] Monitor error rates in Sentry (if configured)
- [ ] Check session persistence (Redis stats)
- [ ] Verify OAuth login flows work
- [ ] Test email delivery (send a test enquiry)
- [ ] Monitor memory usage and CPU

### Validation Commands

```bash
# Service status
railway status

# Real-time logs
railway logs --service monkey-coder-backend --tail

# Recent deployments
railway deployments list --service <service-id>

# Environment variables check
railway variables --service <service-id> | grep -E "(REDIS|OAUTH|EMAIL)"
```

## Rollback Procedures

### If Build Fails

```bash
# Immediate rollback
railway rollback --service <service-id>

# Or via Dashboard: Deployments → Click previous successful deployment → Redeploy
```

### If Redis Breaks Sessions

```bash
railway variables set SESSION_BACKEND=memory --service <backend-service-id>
railway redeploy --service <backend-service-id>
```

### If OAuth Breaks Authentication

```bash
# Temporarily disable OAuth (falls back to email/password)
railway variables unset GOOGLE_OAUTH_CLIENT_ID GITHUB_OAUTH_CLIENT_ID \
  --service <backend-service-id>
railway redeploy --service <backend-service-id>
```

### If Email Breaks Signup

```bash
# Temporarily disable production email (falls back to debug mode)
railway variables unset EMAIL_PROVIDER --service <backend-service-id>
railway redeploy --service <backend-service-id>
```

### Nuclear Option

```bash
# Rollback all services to last known good state
railway rollback --service ccc58ca2-1f4b-4086-beb6-2321ac7dab40
railway rollback --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed
railway rollback --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa
```

## Common Issues & Solutions

### YN0028: Lockfile Would Have Been Modified

**Cause:** Railway running `yarn install --check-cache` instead of `--immutable`

**Solution:**
1. Check for environment variable overrides:
   ```bash
   railway vars --service <service-id> | grep -E "(BUILD_|INSTALL_|NIXPACK)"
   ```
2. Remove any found overrides
3. Verify Custom Build Command is **empty** in Railway Dashboard
4. Ensure railpack config is correct

### Redis Connection Fails

**Cause:** REDIS_URL not configured or connection issues

**Solution:**
- System automatically falls back to in-memory sessions
- Check logs for "Session backend initialized: memory"
- Verify Redis plugin is added and healthy
- Test connection manually

### OAuth Returns "degraded": true

**Cause:** Missing OAuth credentials

**Solution:**
1. Verify CLIENT_ID and CLIENT_SECRET are set for provider
2. Check callback URLs match OAuth provider configuration
3. Ensure OAUTH_REDIRECT_BASE is correct
4. Test with: `curl .../api/v1/auth/oauth/google/initiate | jq .degraded`

### Email Not Sending

**Cause:** Resend not configured or domain not verified

**Solution:**
1. Check RESEND_API_KEY is set and valid
2. Verify domain in Resend dashboard: https://resend.com/domains
3. Check logs for "Email sent successfully" vs "DEV EMAIL"
4. Test with enquiry submission

## Success Criteria

✅ **Deployment is successful when:**

1. All three services show "DEPLOYED" status
2. Health checks return 200 OK:
   - `/api/health` → `{"status": "healthy"}`
   - `/health/readiness` → `{"status": "ready"}`
3. Build logs show:
   - `✅ yarn install --immutable`
   - `✅ Done with warnings in X.XXs`
   - No `YN0028` errors
4. Production features verified:
   - Redis: `"redis": "connected"` or graceful fallback
   - Email: `"email": "configured"`
   - OAuth: Not showing `"degraded": true`
5. No error spikes in first hour
6. Frontend accessible and API responding

## Support & Escalation

If issues persist after following this checklist:

1. **Collect Diagnostics:**
   ```bash
   railway logs --service <service-id> > deployment-logs.txt
   curl https://your-domain/health/comprehensive > health-status.json
   railway variables --service <service-id> > env-vars.txt  # Redact secrets!
   ```

2. **Check Railway Status:** https://status.railway.app/

3. **Railway Support:** If railpack-specific issues, open ticket mentioning:
   - Railpack version 0.8.0
   - YN0028 error with `--immutable` flag
   - Service IDs and project ID

4. **GitHub Issues:** For application-specific issues:
   - https://github.com/GaryOcean428/monkey-coder/issues

---

**Last Updated:** 2025-10-13
**Version:** 1.0.0
**Deployment Target:** Railway Production
