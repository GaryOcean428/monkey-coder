# Railway Service Settings - Quick Reference

This document provides the exact settings needed for each Railway service in the dashboard.

## 🚀 Automated Configuration (Recommended)

Use the automated configuration script for faster, error-free setup:

```bash
# Preview changes (dry-run)
python scripts/railway-service-config-updater.py --dry-run

# Apply configuration to all services
python scripts/railway-service-config-updater.py

# Generate shell script for manual execution
python scripts/railway-service-config-updater.py --generate-commands
bash railway-update-commands.sh
```

**See [RAILWAY_SERVICE_CONFIGURATION.md](./RAILWAY_SERVICE_CONFIGURATION.md) for complete guide.**

---

## Service IDs Reference

Based on the problem statement:
- **monkey-coder** (Frontend): `ccc58ca2-1f4b-4086-beb6-2321ac7dab40`
- **monkey-coder-backend** (API): `6af98d25-621b-4a2d-bbcb-7acb314fbfed`
- **monkey-coder-ml** (ML): `07ef6ac7-e412-4a24-a0dc-74e301413eaa`

---

## 1. Frontend Service: monkey-coder

### Settings → Service
```
Root Directory: /
  (or leave blank)

Custom Build Command: 
  (leave blank - railpack.json handles this)

Custom Start Command:
  (leave blank - railpack.json handles this)
```

### Settings → Config as Code
```
Config Path: railpack.json
```

### Environment Variables (Minimum)
```bash
railway variables set --service ccc58ca2-1f4b-4086-beb6-2321ac7dab40 \
  RAILWAY_CONFIG_FILE=railpack.json \
  NEXT_PUBLIC_API_URL="https://monkey-coder-backend-production.up.railway.app" \
  NEXT_PUBLIC_APP_URL="https://coder.fastmonkey.au" \
  NODE_ENV=production \
  NEXT_TELEMETRY_DISABLED=1
```

### Health Check
```
Path: /
Timeout: 300 seconds
```

---

## 2. Backend Service: monkey-coder-backend

### Settings → Service
```
Root Directory: /
  (or leave blank)

Custom Build Command:
  (leave blank - railpack-backend.json handles this)

Custom Start Command:
  (leave blank - railpack-backend.json handles this)
```

### Settings → Config as Code
```
Config Path: railpack-backend.json
```

### Environment Variables (Critical - Set First)
```bash
# CRITICAL SECRETS (generate these)
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  JWT_SECRET_KEY="$(openssl rand -hex 32)" \
  NEXTAUTH_SECRET="$(openssl rand -hex 32)" \
  RAILWAY_CONFIG_FILE=railpack-backend.json \
  ENV=production \
  NODE_ENV=production \
  PYTHON_ENV=production

# AI PROVIDERS (at least one required)
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  OPENAI_API_KEY="sk-..." \
  ANTHROPIC_API_KEY="sk-ant-..."

# DATABASE (auto-set by Railway PostgreSQL plugin)
# DATABASE_URL is automatically configured when you add the plugin
```

### Environment Variables (Production Features)
```bash
# REDIS (after adding Redis plugin)
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  SESSION_BACKEND=redis \
  RATE_LIMIT_BACKEND=redis

# EMAIL SERVICE (Resend)
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  RESEND_API_KEY="re_..." \
  NOTIFICATION_EMAIL_FROM="noreply@fastmonkey.au" \
  EMAIL_PROVIDER=resend \
  SMTP_ENABLED=true

# OAUTH - GOOGLE
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  GOOGLE_OAUTH_CLIENT_ID="...apps.googleusercontent.com" \
  GOOGLE_OAUTH_CLIENT_SECRET="..."

# OAUTH - GITHUB  
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  GITHUB_OAUTH_CLIENT_ID="..." \
  GITHUB_OAUTH_CLIENT_SECRET="..."

# OAUTH - CONFIGURATION
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  OAUTH_REDIRECT_BASE="https://coder.fastmonkey.au/api/v1/auth/oauth" \
  OAUTH_STATE_SECRET="$(openssl rand -hex 32)"

# APPLICATION URLS
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  NEXT_PUBLIC_APP_URL="https://coder.fastmonkey.au" \
  PUBLIC_APP_URL="https://coder.fastmonkey.au" \
  NEXT_PUBLIC_API_URL="https://monkey-coder-backend-production.up.railway.app"

# SECURITY
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  CORS_ORIGINS="https://coder.fastmonkey.au" \
  TRUSTED_HOSTS="coder.fastmonkey.au,*.railway.app,*.railway.internal" \
  ENABLE_SECURITY_HEADERS=true
```

### Health Check
```
Path: /api/health
Timeout: 300 seconds
```

---

## 3. ML Service: monkey-coder-ml

### Settings → Service
```
Root Directory: /
  (or leave blank)

Custom Build Command:
  (leave blank - railpack-ml.json handles this)

Custom Start Command:
  (leave blank - railpack-ml.json handles this)
```

### Settings → Config as Code
```
Config Path: railpack-ml.json
```

### Environment Variables (Minimum)
```bash
railway variables set --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa \
  RAILWAY_CONFIG_FILE=railpack-ml.json \
  ENV=production \
  NODE_ENV=production \
  PYTHON_ENV=production \
  LOG_LEVEL=info
```

### Health Check
```
Path: /api/health
Timeout: 600 seconds
  (First build takes 25+ minutes due to ML dependencies)
```

---

## Verification Commands

After setting all variables and configurations:

### Check Service Configuration
```bash
# Frontend
railway service --service ccc58ca2-1f4b-4086-beb6-2321ac7dab40

# Backend
railway service --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed

# ML
railway service --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa
```

### Check Environment Variables
```bash
# Backend (shows all vars - NEVER share output with secrets!)
railway variables --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed

# Check specific variables (safe to share)
railway variables --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed | grep -E "(ENV|NODE_ENV|SESSION_BACKEND)"
```

### Check for Problematic Overrides
```bash
# Should return empty (no overrides)
railway vars --service ccc58ca2-1f4b-4086-beb6-2321ac7dab40 | grep -E "(RAILPACK_|BUILD_|INSTALL_|NIXPACK)"
railway vars --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed | grep -E "(RAILPACK_|BUILD_|INSTALL_|NIXPACK)"
railway vars --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa | grep -E "(RAILPACK_|BUILD_|INSTALL_|NIXPACK)"
```

---

## Common Mistakes to Avoid

### ❌ DON'T DO THESE

1. **Setting Custom Build/Start Commands**
   - Let railpack.json handle the build process
   - Manual commands override railpack configuration

2. **Setting Root Directory to Subdirectories**
   - Always use `/` or blank
   - Yarn workspace needs repository root

3. **Setting PORT Variable**
   - Railway automatically injects `$PORT`
   - Never set PORT manually

4. **Hardcoding Localhost URLs**
   - Always use Railway service references
   - Use `RAILWAY_PUBLIC_DOMAIN` and `RAILWAY_PRIVATE_DOMAIN`

5. **Setting NIXPACK_* Variables**
   - These override railpack.json
   - Remove any NIXPACK_* variables

### ✅ DO THESE

1. **Use Railway Plugins**
   - Add PostgreSQL plugin for DATABASE_URL
   - Add Redis plugin for REDIS_URL

2. **Set RAILWAY_CONFIG_FILE**
   - Each service needs its own railpack config
   - Frontend: `railpack.json`
   - Backend: `railpack-backend.json`
   - ML: `railpack-ml.json`

3. **Generate Strong Secrets**
   - Use `openssl rand -hex 32` for all secrets
   - Never reuse secrets across environments

4. **Test Locally First**
   - Run `yarn install --immutable --check-cache`
   - Should pass without errors

5. **Monitor Health Endpoints**
   - `/api/health` - Basic health
   - `/health/readiness` - Dependency status
   - `/health/comprehensive` - Full system status

---

## Deployment Process

1. **Set Environment Variables** (from above)
2. **Verify Settings** (Root Directory, Build/Start Commands blank)
3. **Add Railway Plugins** (PostgreSQL, Redis)
4. **Deploy Services**
   ```bash
   railway redeploy --service ccc58ca2-1f4b-4086-beb6-2321ac7dab40
   railway redeploy --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed
   railway redeploy --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa
   ```
5. **Monitor Logs**
   ```bash
   railway logs --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed --tail
   ```
6. **Verify Health**
   ```bash
   curl https://coder.fastmonkey.au/api/health
   curl https://monkey-coder-backend-production.up.railway.app/health/readiness
   ```

---

## Quick Checklist

Before deploying, verify:

- [ ] All three services have Root Directory set to `/` or blank
- [ ] All three services have Build/Start Commands blank
- [ ] Each service has correct `RAILWAY_CONFIG_FILE` set
- [ ] Backend has all CRITICAL secrets set
- [ ] PostgreSQL plugin added (DATABASE_URL auto-populated)
- [ ] Redis plugin added if using session persistence
- [ ] No NIXPACK_* or RAILPACK_* override variables
- [ ] Health check paths configured correctly

---

**Last Updated:** 2025-10-13
**Railway Project:** AetherOS
**Environment:** Production
