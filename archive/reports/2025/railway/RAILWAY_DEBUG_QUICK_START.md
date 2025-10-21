# Railway Deployment Debug - Quick Start

## 🚨 Quick Debug Commands

```bash
# Run comprehensive debug (recommended)
python3 scripts/railway-mcp-debug.py --verbose

# Or use shell script (no Python dependencies needed)
bash scripts/railway-debug.sh --verbose

# Service-specific debugging
python3 scripts/railway-mcp-debug.py --service monkey-coder
bash scripts/railway-debug.sh --service monkey-coder-backend
```

## ✅ Current Status

Based on latest validation:
- ✓ All railpack.json files valid and properly configured
- ✓ PORT binding correct ($PORT variable used)
- ✓ Host binding correct (0.0.0.0)
- ✓ Health checks configured (/api/health)
- ✓ No competing build files
- ✅ **Configuration is Railway-ready!**

## ⚠️ Railway Dashboard Configuration Required

**CRITICAL**: For ALL three services in Railway Dashboard:

### Step 1: Root Directory
```
Settings → Service → Root Directory: /
(or leave BLANK)
```

### Step 2: Build/Start Commands
```
Settings → Service:
  - Build Command: LEAVE BLANK
  - Start Command: LEAVE BLANK
```

### Step 3: Config Path
```
Settings → Config as Code → Path:
  - monkey-coder: railpack.json
  - monkey-coder-backend: railpack-backend.json (or set SERVICE_TYPE=backend)
  - monkey-coder-ml: railpack-ml.json (or set SERVICE_TYPE=ml)
```

## 🔧 Required Environment Variables

### Frontend (monkey-coder)
```bash
NODE_ENV=production
NEXT_OUTPUT_EXPORT=true
NEXT_TELEMETRY_DISABLED=1
NEXT_PUBLIC_APP_URL=https://coder.fastmonkey.au
NEXT_PUBLIC_API_URL=https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}
```

### Backend (monkey-coder-backend)
```bash
PYTHON_ENV=production
PYTHONPATH=/app:/app/packages/core
ML_SERVICE_URL=http://${{monkey-coder-ml.RAILWAY_PRIVATE_DOMAIN}}
# Plus: OPENAI_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY, etc.
```

### ML (monkey-coder-ml)
```bash
PYTHON_ENV=production
PYTHONPATH=/app:/app/services/ml
TRANSFORMERS_CACHE=/app/.cache/huggingface
CUDA_VISIBLE_DEVICES=0
```

## 🚀 Deploy Commands

```bash
# Link to project (first time only)
railway link

# Deploy services
railway up --service monkey-coder
railway up --service monkey-coder-backend
railway up --service monkey-coder-ml

# Monitor logs
railway logs --service monkey-coder --follow
```

## 🔍 Verify Deployment

```bash
# Check health endpoints
curl https://coder.fastmonkey.au/api/health
curl https://monkey-coder-backend-production.up.railway.app/api/health

# Expected: 200 OK with JSON response
```

## 📚 Full Documentation

- **RAILWAY_DEBUG_GUIDE.md** - Complete debugging guide
- **RAILWAY_DEPLOYMENT.md** - Authoritative deployment configuration
- **RAILWAY_CRISIS_RESOLUTION.md** - Emergency fix instructions
- **scripts/fix-railway-services.sh** - Interactive fix wizard

## 🐛 Common Issues

### Issue: "can't cd to packages/web"
**Fix**: Set Root Directory to `/` in Railway Dashboard

### Issue: Health check failing
**Fix**:
1. Check logs: `railway logs --service <name>`
2. Verify application starts correctly
3. Test health endpoint locally

### Issue: Service can't communicate with other services
**Fix**:
1. Verify environment variables use `RAILWAY_PUBLIC_DOMAIN` or `RAILWAY_PRIVATE_DOMAIN`
2. Check variable references: `railway variables --service <name>`

## 🆘 Need Help?

1. Run debug tool: `python3 scripts/railway-mcp-debug.py --verbose`
2. Review output for critical issues
3. Check Railway logs: `railway logs --service <name>`
4. Consult full documentation above

---

**Quick Reference** | **Version 1.0** | **Last Updated: 2025-01-16**
