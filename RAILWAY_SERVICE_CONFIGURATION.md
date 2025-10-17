# Railway Service Configuration Guide

> **⚠️ OUTDATED - SEE UPDATED GUIDE**
>
> This document references deprecated root-level `railpack-*.json` files and `RAILWAY_CONFIG_FILE` variables.
>
> **For current, accurate configuration, see:**
> - [docs/deployment/railway-configuration.md](docs/deployment/railway-configuration.md) - Complete guide
>
> **Archived:** 2025-10-16
>
> This file is preserved for historical reference only.

---

**Last Updated:** 2025-10-13 (Archived 2025-10-16)
**Project:** AetherOS Monkey Coder
**Environment:** Production

## 🎯 Quick Start

```bash
# Option 1: Automated Update (Recommended)
python scripts/railway-service-config-updater.py --dry-run  # Preview changes
python scripts/railway-service-config-updater.py             # Apply changes

# Option 2: Generate Commands for Manual Execution
python scripts/railway-service-config-updater.py --generate-commands
bash railway-update-commands.sh

# Option 3: Update Specific Service
python scripts/railway-service-config-updater.py --service monkey-coder-backend
```

## 📋 Service Reference

### Service IDs (AetherOS Project)

| Service Name | Service ID | Config File | Purpose |
|--------------|------------|-------------|---------|
| `monkey-coder` | `ccc58ca2-1f4b-4086-beb6-2321ac7dab40` | `railpack.json` | Next.js Frontend |
| `monkey-coder-backend` | `6af98d25-621b-4a2d-bbcb-7acb314fbfed` | `railpack-backend.json` | FastAPI Backend |
| `monkey-coder-ml` | `07ef6ac7-e412-4a24-a0dc-74e301413eaa` | `railpack-ml.json` | ML Inference |

## 🔧 Configuration by Service

### 1. Frontend Service (monkey-coder)

**Service ID:** `ccc58ca2-1f4b-4086-beb6-2321ac7dab40`

#### Required Variables

```bash
railway variables set --service ccc58ca2-1f4b-4086-beb6-2321ac7dab40 \
  RAILWAY_CONFIG_FILE=railpack.json \
  NODE_ENV=production \
  NEXT_OUTPUT_EXPORT=true \
  NEXT_TELEMETRY_DISABLED=1 \
  NEXT_PUBLIC_APP_URL="https://coder.fastmonkey.au" \
  NEXT_PUBLIC_API_URL="https://monkey-coder-backend-production.up.railway.app"
```

#### Service Settings

- **Root Directory:** `/` (or blank)
- **Build Command:** (blank - handled by railpack.json)
- **Start Command:** (blank - handled by railpack.json)
- **Config Path:** `railpack.json`
- **Health Check Path:** `/`
- **Health Check Timeout:** 300 seconds

---

### 2. Backend Service (monkey-coder-backend)

**Service ID:** `6af98d25-621b-4a2d-bbcb-7acb314fbfed`

#### Critical Secrets (Set First)

```bash
# Generate secure secrets
JWT_SECRET=$(openssl rand -hex 32)
NEXTAUTH_SECRET=$(openssl rand -hex 32)

# Set critical secrets
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  JWT_SECRET_KEY="$JWT_SECRET" \
  NEXTAUTH_SECRET="$NEXTAUTH_SECRET" \
  OPENAI_API_KEY="sk-..." \
  ANTHROPIC_API_KEY="sk-ant-..."
```

#### Required Variables

```bash
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  RAILWAY_CONFIG_FILE=railpack-backend.json \
  ENV=production \
  NODE_ENV=production \
  PYTHON_ENV=production \
  LOG_LEVEL=info \
  NEXT_PUBLIC_APP_URL="https://coder.fastmonkey.au" \
  PUBLIC_APP_URL="https://coder.fastmonkey.au" \
  NEXT_PUBLIC_API_URL="https://monkey-coder-backend-production.up.railway.app" \
  CORS_ORIGINS="https://coder.fastmonkey.au" \
  TRUSTED_HOSTS="coder.fastmonkey.au,*.railway.app,*.railway.internal" \
  ENABLE_SECURITY_HEADERS=true \
  ENABLE_CORS=true \
  HEALTH_CHECK_PATH="/api/health" \
  ENABLE_HEALTH_CHECKS=true
```

#### Optional Variables (Production Features)

```bash
# Redis Session Management
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  SESSION_BACKEND=redis \
  RATE_LIMIT_BACKEND=redis

# Email Service (Resend)
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  RESEND_API_KEY="re_..." \
  NOTIFICATION_EMAIL_FROM="noreply@fastmonkey.au" \
  EMAIL_PROVIDER=resend

# Additional AI Providers
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  GOOGLE_API_KEY="..." \
  GROQ_API_KEY="..." \
  XAI_API_KEY="..."

# Error Tracking
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  SENTRY_DSN="https://...@sentry.io/..."
```

#### Service Settings

- **Root Directory:** `/` (or blank)
- **Build Command:** (blank - handled by railpack-backend.json)
- **Start Command:** (blank - handled by railpack-backend.json)
- **Config Path:** `railpack-backend.json`
- **Health Check Path:** `/api/health`
- **Health Check Timeout:** 300 seconds

---

### 3. ML Service (monkey-coder-ml)

**Service ID:** `07ef6ac7-e412-4a24-a0dc-74e301413eaa`

#### Required Variables

```bash
railway variables set --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa \
  RAILWAY_CONFIG_FILE=railpack-ml.json \
  ENV=production \
  NODE_ENV=production \
  PYTHON_ENV=production \
  LOG_LEVEL=info \
  TRANSFORMERS_CACHE="/app/.cache/huggingface" \
  HEALTH_CHECK_PATH="/api/health"
```

#### Optional Variables

```bash
railway variables set --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa \
  CUDA_VISIBLE_DEVICES=0
```

#### Service Settings

- **Root Directory:** `/` (or blank)
- **Build Command:** (blank - handled by railpack-ml.json)
- **Start Command:** (blank - handled by railpack-ml.json)
- **Config Path:** `railpack-ml.json`
- **Health Check Path:** `/api/health`
- **Health Check Timeout:** 600 seconds (first build takes 25+ minutes)

---

## 🚀 Deployment Workflow

### Step 1: Verify Service Configuration

```bash
# Check current configuration for each service
railway service --service ccc58ca2-1f4b-4086-beb6-2321ac7dab40
railway service --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed
railway service --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa

# Verify variables
railway variables --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed
```

### Step 2: Update Configuration

```bash
# Automated update (dry-run first)
python scripts/railway-service-config-updater.py --dry-run
python scripts/railway-service-config-updater.py

# Or use generated script
python scripts/railway-service-config-updater.py --generate-commands
bash railway-update-commands.sh
```

### Step 3: Set Critical Secrets

```bash
# Backend secrets (REQUIRED)
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  JWT_SECRET_KEY="$(openssl rand -hex 32)" \
  NEXTAUTH_SECRET="$(openssl rand -hex 32)" \
  OPENAI_API_KEY="sk-your-openai-key" \
  ANTHROPIC_API_KEY="sk-ant-your-anthropic-key"
```

### Step 4: Add Railway Plugins

```bash
# Add PostgreSQL database
railway add --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed postgresql

# Add Redis cache (optional but recommended)
railway add --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed redis
```

### Step 5: Deploy Services

```bash
# Deploy all services
railway redeploy --service ccc58ca2-1f4b-4086-beb6-2321ac7dab40
railway redeploy --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed
railway redeploy --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa

# Or trigger from GitHub push
git push origin main
```

### Step 6: Verify Deployment

```bash
# Check deployment status
railway logs --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed --tail

# Test health endpoints
curl https://coder.fastmonkey.au/
curl https://monkey-coder-backend-production.up.railway.app/api/health
curl https://monkey-coder-backend-production.up.railway.app/health/readiness
```

---

## 🔍 Verification Commands

### Check Service Configuration

```bash
# List all services in project
railway status

# Check specific service details
railway service --service <SERVICE_ID>

# List environment variables
railway variables --service <SERVICE_ID>

# Check for problematic overrides (should be empty)
railway variables --service <SERVICE_ID> | grep -E "(NIXPACK_|BUILD_|INSTALL_)"
```

### Validate Health Endpoints

```bash
# Frontend health check
curl -I https://coder.fastmonkey.au/

# Backend health checks
curl https://monkey-coder-backend-production.up.railway.app/health
curl https://monkey-coder-backend-production.up.railway.app/api/health
curl https://monkey-coder-backend-production.up.railway.app/health/readiness
curl https://monkey-coder-backend-production.up.railway.app/health/comprehensive

# ML service health check
curl https://monkey-coder-ml-production.up.railway.app/api/health
```

### Monitor Logs

```bash
# Tail logs for specific service
railway logs --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed --tail

# View recent logs
railway logs --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed --since 1h

# Check for errors
railway logs --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed | grep -i error
```

---

## ⚠️ Common Issues & Solutions

### Issue: "Root directory not found"

**Solution:** Ensure Root Directory is set to `/` or blank, not a subdirectory.

```bash
railway service update --service <SERVICE_ID> --root-directory /
```

### Issue: "Build failed: yarn not found"

**Solution:** Verify railpack.json includes corepack setup in install commands.

### Issue: Environment variables not taking effect

**Solution:**
1. Clear build cache in Railway Dashboard
2. Redeploy the service
3. Verify variables with `railway variables --service <SERVICE_ID>`

### Issue: Health check timeout

**Solution:**
- Frontend/Backend: Increase timeout to 300 seconds
- ML Service: Increase timeout to 600 seconds (first build is slow)
- Verify health endpoint returns 200 status

### Issue: Database connection failed

**Solution:**
1. Verify PostgreSQL plugin is added
2. Check DATABASE_URL is automatically set
3. Ensure backend service can access database

---

## 📊 Configuration Checklist

Before deployment, verify:

- [ ] All three services have Root Directory set to `/` or blank
- [ ] All three services have Build/Start Commands blank (handled by railpack)
- [ ] Each service has correct `RAILWAY_CONFIG_FILE` variable set
- [ ] Backend has all CRITICAL secrets set (JWT_SECRET_KEY, NEXTAUTH_SECRET, API keys)
- [ ] PostgreSQL plugin added to backend service (DATABASE_URL auto-populated)
- [ ] Redis plugin added to backend service (optional but recommended)
- [ ] No NIXPACK_* or manual build override variables
- [ ] Health check paths configured correctly for each service
- [ ] CORS_ORIGINS includes your custom domain
- [ ] TRUSTED_HOSTS includes Railway domains

---

## 🛠️ Using the Configuration Updater Script

### Features

- ✅ Direct service ID targeting for precise updates
- ✅ Comprehensive environment variable management
- ✅ Dry-run mode for safe testing
- ✅ Automatic secret detection and masking
- ✅ Command generation for manual execution
- ✅ JSON summary export

### Usage Examples

```bash
# Preview changes (dry-run)
python scripts/railway-service-config-updater.py --dry-run

# Update all services
python scripts/railway-service-config-updater.py

# Update specific service
python scripts/railway-service-config-updater.py --service monkey-coder-backend

# Generate shell script for manual execution
python scripts/railway-service-config-updater.py --generate-commands

# Verbose output
python scripts/railway-service-config-updater.py --verbose

# Skip secret warnings
python scripts/railway-service-config-updater.py --skip-secrets
```

### Output Files

- `railway_update_summary.json` - JSON summary of all updates
- `railway-update-commands.sh` - Shell script with all commands

---

## 🔐 Security Best Practices

1. **Never commit secrets to git**
   - Use Railway Dashboard or CLI to set secrets
   - Keep `.env.railway.example` as template only

2. **Generate strong secrets**
   ```bash
   openssl rand -hex 32  # For JWT and auth secrets
   openssl rand -base64 64  # For longer secrets
   ```

3. **Rotate secrets regularly**
   - JWT secrets: Every 60-90 days
   - API keys: When compromised or annually
   - OAuth secrets: Per provider recommendation

4. **Use Railway's secret masking**
   - Secrets are automatically masked in logs
   - Never log secrets in application code

5. **Limit CORS origins**
   - Only include your production domains
   - Never use wildcard (*) in production

---

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Railway CLI Reference](https://docs.railway.app/develop/cli)
- [Railpack Configuration](https://docs.railway.app/deploy/config-as-code)
- [Railway Service Discovery](https://docs.railway.app/deploy/environments#railway-provided-variables)
- [Project README](/README.md)
- [Railway Deployment Guide](/RAILWAY_DEPLOYMENT.md)
- [Railway Production Checklist](/RAILWAY_PRODUCTION_CHECKLIST.md)

---

**Questions or Issues?**

- GitHub Issues: https://github.com/GaryOcean428/monkey-coder/issues
- Railway Support: https://railway.app/help
- Documentation: https://docs.monkey-coder.dev (when available)
