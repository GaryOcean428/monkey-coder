# Railway Configuration Quick Start Guide

> **⚠️ OUTDATED - SEE UPDATED GUIDE**
>
> This document references deprecated root-level `railpack-*.json` files and automation scripts.
>
> **For current, accurate quick start, see:**
> - [docs/deployment/railway-configuration.md](docs/deployment/railway-configuration.md) - Complete guide with quick start
>
> **Archived:** 2025-10-16

---

This guide will help you quickly set up and configure your Railway services for the AetherOS Monkey Coder project.

## 🎯 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Railway CLI**: Install the CLI tool
3. **Project Access**: Ensure you have access to the AetherOS Railway project

### Install Railway CLI

```bash
# Option 1: Using npm (recommended)
npm install -g @railway/cli

# Option 2: Using Homebrew (macOS)
brew install railway

# Option 3: Using curl (Linux/macOS)
curl -fsSL https://railway.app/install.sh | sh

# Verify installation
railway --version
```

### Login to Railway

```bash
railway login
```

This will open a browser window for authentication.

---

## 🚀 Quick Configuration (3 Steps)

### Step 1: Preview Configuration Changes

Before making any changes, preview what will be configured:

```bash
cd /path/to/monkey-coder
python scripts/railway-service-config-updater.py --dry-run
```

**What this does:**
- Shows all variables that will be set for each service
- Identifies critical secrets that need manual configuration
- Displays service IDs and configuration files
- No actual changes are made

**Expected output:**
```
✓ Railway CLI available
🚂 Railway Service Configuration Updater
⚠️  DRY RUN MODE - No actual changes will be made

🔧 Updating Service: monkey-coder
  Service ID: ccc58ca2-1f4b-4086-beb6-2321ac7dab40
  [DRY RUN] Would set RAILWAY_CONFIG_FILE=railpack.json
  [DRY RUN] Would set NODE_ENV=production
  ...
```

### Step 2: Apply Configuration

Once you've reviewed the changes, apply them:

```bash
python scripts/railway-service-config-updater.py
```

**What this does:**
- Sets all required environment variables for each service
- Configures service settings
- Generates a summary report
- Identifies critical secrets that need to be set manually

**Expected output:**
```
✓ Railway CLI available
🚂 Railway Service Configuration Updater

🔧 Updating Service: monkey-coder
  ✓ Set RAILWAY_CONFIG_FILE=railpack.json
  ✓ Set NODE_ENV=production
  ...

⚠️  IMPORTANT: Set critical secrets manually
```

### Step 3: Set Critical Secrets

The script will identify secrets that need to be set manually. Set them using Railway CLI:

```bash
# Generate secure secrets
JWT_SECRET=$(openssl rand -hex 32)
NEXTAUTH_SECRET=$(openssl rand -hex 32)

# Set secrets for backend service
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed \
  JWT_SECRET_KEY="$JWT_SECRET" \
  NEXTAUTH_SECRET="$NEXTAUTH_SECRET" \
  OPENAI_API_KEY="sk-your-openai-key" \
  ANTHROPIC_API_KEY="sk-ant-your-anthropic-key"
```

---

## ✅ Verify Configuration

After configuration, verify everything is set correctly:

```bash
# Run verification
python scripts/verify-railway-config.py

# Generate JSON report
python scripts/verify-railway-config.py --json > compliance-report.json
```

**Expected output:**
```
🚂 Railway Configuration Verification

🔍 Verifying Service: monkey-coder
  ✓ railpack_exists: Railpack config exists
  ✓ railpack_structure: Valid structure
  ✓ health_check_config: Health check configured
  ✓ critical_secrets: All secrets set

✅ CONFIGURATION FULLY COMPLIANT
```

---

## 🔄 Alternative: Manual Configuration

If you prefer to review and execute commands manually:

### Generate Command Script

```bash
python scripts/railway-service-config-updater.py --generate-commands
```

This creates `railway-update-commands.sh` with all configuration commands.

### Review and Execute

```bash
# Review the generated script
cat railway-update-commands.sh

# Execute it (or run commands individually)
bash railway-update-commands.sh
```

---

## 📊 Service Configuration Reference

### Frontend Service (monkey-coder)

**Service ID:** `ccc58ca2-1f4b-4086-beb6-2321ac7dab40`

**Required Variables:**
- `RAILWAY_CONFIG_FILE=railpack.json`
- `NODE_ENV=production`
- `NEXT_OUTPUT_EXPORT=true`
- `NEXT_TELEMETRY_DISABLED=1`
- `NEXT_PUBLIC_APP_URL=https://coder.fastmonkey.au`
- `NEXT_PUBLIC_API_URL=https://monkey-coder-backend-production.up.railway.app`

### Backend Service (monkey-coder-backend)

**Service ID:** `6af98d25-621b-4a2d-bbcb-7acb314fbfed`

**Critical Secrets (Must Set Manually):**
- `JWT_SECRET_KEY` - Use: `openssl rand -hex 32`
- `NEXTAUTH_SECRET` - Use: `openssl rand -hex 32`
- `OPENAI_API_KEY` - Your OpenAI API key
- `ANTHROPIC_API_KEY` - Your Anthropic API key

**Required Variables:**
- `RAILWAY_CONFIG_FILE=railpack-backend.json`
- `ENV=production`
- `NODE_ENV=production`
- `PYTHON_ENV=production`
- `LOG_LEVEL=info`
- `CORS_ORIGINS=https://coder.fastmonkey.au`
- `TRUSTED_HOSTS=coder.fastmonkey.au,*.railway.app,*.railway.internal`
- `ENABLE_SECURITY_HEADERS=true`
- `HEALTH_CHECK_PATH=/api/health`

### ML Service (monkey-coder-ml)

**Service ID:** `07ef6ac7-e412-4a24-a0dc-74e301413eaa`

**Required Variables:**
- `RAILWAY_CONFIG_FILE=railpack-ml.json`
- `ENV=production`
- `NODE_ENV=production`
- `PYTHON_ENV=production`
- `LOG_LEVEL=info`
- `TRANSFORMERS_CACHE=/app/.cache/huggingface`
- `HEALTH_CHECK_PATH=/api/health`

---

## 🔍 Troubleshooting

### Railway CLI Not Found

**Error:** `railway: command not found`

**Solution:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Or use ephemeral version
yarn dlx @railway/cli@latest --version
```

### Not Authenticated

**Error:** `Not logged in. Run 'railway login' first.`

**Solution:**
```bash
railway login
```

### Service Not Found

**Error:** `Service not found`

**Solution:** Verify service IDs:
```bash
railway service list
```

### Variables Not Taking Effect

**Problem:** Changes not reflected after setting variables

**Solution:**
1. Verify variables are set:
   ```bash
   railway variables --service <SERVICE_ID>
   ```

2. Redeploy the service:
   ```bash
   railway redeploy --service <SERVICE_ID>
   ```

3. Check deployment logs:
   ```bash
   railway logs --service <SERVICE_ID> --tail
   ```

---

## 📚 Additional Resources

- **Complete Guide:** [RAILWAY_SERVICE_CONFIGURATION.md](../RAILWAY_SERVICE_CONFIGURATION.md)
- **Service Settings:** [RAILWAY_SERVICE_SETTINGS.md](../RAILWAY_SERVICE_SETTINGS.md)
- **Deployment Guide:** [RAILWAY_DEPLOYMENT.md](../RAILWAY_DEPLOYMENT.md)
- **Production Checklist:** [RAILWAY_PRODUCTION_CHECKLIST.md](../RAILWAY_PRODUCTION_CHECKLIST.md)

---

## 🎓 Next Steps

After configuration:

1. **Add Railway Plugins:**
   ```bash
   railway add --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed postgresql
   railway add --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed redis
   ```

2. **Deploy Services:**
   ```bash
   railway redeploy --service ccc58ca2-1f4b-4086-beb6-2321ac7dab40  # Frontend
   railway redeploy --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed  # Backend
   railway redeploy --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa  # ML
   ```

3. **Verify Deployment:**
   ```bash
   # Check health endpoints
   curl https://coder.fastmonkey.au/
   curl https://monkey-coder-backend-production.up.railway.app/api/health
   
   # Monitor logs
   railway logs --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed --tail
   ```

4. **Set Up Monitoring:**
   - Configure alerts in Railway Dashboard
   - Set up Sentry for error tracking (optional)
   - Configure email notifications

---

## 💡 Tips

- **Always use dry-run first** to preview changes
- **Keep secrets secure** - never commit them to git
- **Rotate secrets regularly** - every 60-90 days
- **Monitor deployment logs** - catch issues early
- **Use Railway Dashboard** - for quick visual checks
- **Verify configuration** - after each significant change

---

## 🆘 Getting Help

- **GitHub Issues:** [Report bugs or request features](https://github.com/GaryOcean428/monkey-coder/issues)
- **Railway Support:** [Railway Help Center](https://railway.app/help)
- **Documentation:** Check the [complete documentation](../README.md)

---

**Last Updated:** 2025-10-13  
**Project:** AetherOS Monkey Coder  
**Environment:** Production
