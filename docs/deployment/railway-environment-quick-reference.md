# Railway Environment Configuration Quick Reference

**Repository:** GaryOcean428/monkey-coder

## 🚀 Quick Start

```bash
# 1. Login and link to your Railway project
railway login
railway link <your-project-id>

# 2. Configure environment variables manually or via Railway Dashboard
# See detailed guide: docs/deployment/railway-environment-setup-guide.md

# 3. Verify
railway variables --service monkey-coder-sandbox
railway variables --service monkey-coder-backend

# 4. Deploy
railway redeploy --service monkey-coder-sandbox
railway redeploy --service monkey-coder-backend
railway redeploy --service monkey-coder

# 5. Check health
curl https://<sandbox-domain>/health
curl https://<backend-domain>/api/health
```

---

## 📋 Environment Variables Matrix

| Service | Variable | Value | Type |
|---------|----------|-------|------|
| **sandbox** | `SANDBOX_TOKEN_SECRET` | `openssl rand -hex 32` | Secret |
| **sandbox** | `SANDBOX_ALLOW_ORIGINS` | `https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}` | Config |
| **sandbox** | `SANDBOX_ALLOW_ORIGIN_REGEX` | `^https?://([a-z0-9-]+\.)*railway\.app$` | Config |
| **sandbox** | `LOG_LEVEL` | `info` | Config |
| **sandbox** | `PYTHONUNBUFFERED` | `1` | Config |
| **backend** | `SANDBOX_SERVICE_URL` | `http://${{monkey-coder-sandbox.RAILWAY_PRIVATE_DOMAIN}}` | Reference |
| **backend** | `SANDBOX_TOKEN_SECRET` | *same as sandbox* | Secret |
| **backend** | `PYTHON_ENV` | `production` | Config |
| **backend** | `PYTHONUNBUFFERED` | `1` | Config |
| **backend** | `LOG_LEVEL` | `info` | Config |
| **frontend** | `NEXT_PUBLIC_API_URL` | `https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}` | Reference |
| **frontend** | `NODE_ENV` | `production` | Config |
| **frontend** | `NEXT_TELEMETRY_DISABLED` | `1` | Config |

---

## 🔒 Security Checklist

- [ ] `SANDBOX_TOKEN_SECRET` is 64-char hex (use `openssl rand -hex 32`)
- [ ] Same token in both sandbox and backend
- [ ] NO sandbox secrets in frontend
- [ ] Internal URLs use `RAILWAY_PRIVATE_DOMAIN`
- [ ] Browser URLs use `RAILWAY_PUBLIC_DOMAIN`
- [ ] Health checks working on all services

---

## 🔍 Verification Commands

```bash
# Check variables
railway variables --service monkey-coder-sandbox | grep SANDBOX_TOKEN_SECRET
railway variables --service monkey-coder-backend | grep SANDBOX_TOKEN_SECRET

# Compare tokens (should be identical)
diff <(railway variables --service monkey-coder-sandbox | grep SANDBOX_TOKEN_SECRET) \
     <(railway variables --service monkey-coder-backend | grep SANDBOX_TOKEN_SECRET)

# Test health endpoints
curl -f https://<sandbox-domain>/health && echo "✓ Sandbox healthy"
curl -f https://<backend-domain>/api/health && echo "✓ Backend healthy"
curl -f https://<frontend-domain>/ && echo "✓ Frontend healthy"

# Check logs
railway logs --service monkey-coder-sandbox --tail 50
railway logs --service monkey-coder-backend --tail 50
```

---

## 🐛 Common Issues & Quick Fixes

### Backend can't connect to sandbox
```bash
# Check SANDBOX_SERVICE_URL uses PRIVATE domain
railway variables --service monkey-coder-backend | grep SANDBOX_SERVICE_URL

# Should output:
# SANDBOX_SERVICE_URL=http://${{monkey-coder-sandbox.RAILWAY_PRIVATE_DOMAIN}}
```

### Sandbox returns 401 Unauthorized
```bash
# Verify tokens match
railway variables --service monkey-coder-sandbox | grep SECRET
railway variables --service monkey-coder-backend | grep SECRET

# If different, regenerate and set both:
TOKEN=$(openssl rand -hex 32)
railway variables set --service monkey-coder-sandbox SANDBOX_TOKEN_SECRET=$TOKEN
railway variables set --service monkey-coder-backend SANDBOX_TOKEN_SECRET=$TOKEN
```

### Frontend can't reach backend
```bash
# Check frontend uses PUBLIC domain
railway variables --service monkey-coder | grep NEXT_PUBLIC_API_URL

# Should output:
# NEXT_PUBLIC_API_URL=https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}

# Check CORS in backend
railway variables --service monkey-coder-backend | grep CORS_ORIGINS
```

---

## 📚 Documentation Links

- **Comprehensive Guide:** `docs/deployment/railway-aetheros-config.md`
- **Executive Summary:** `docs/deployment/railway-environment-configuration.md`
- **Scripts README:** `scripts/README_RAILWAY_TOOLS.md`
- **Environment Template:** `.env.railway.example`

---

## 🎯 Service Architecture

```
┌──────────────────┐
│    Browser       │
└────────┬─────────┘
         │ HTTPS (PUBLIC)
         │ NEXT_PUBLIC_API_URL
         ▼
┌──────────────────┐
│    Frontend      │
│  (monkey-coder)  │
└──────────────────┘
         │ HTTPS (PUBLIC)
         ▼
┌──────────────────┐     HTTP (PRIVATE)      ┌──────────────────┐
│    Backend       │◄────────────────────────►│   ML Service     │
│ (monkey-coder-   │  ML_SERVICE_URL          │ (monkey-coder-   │
│   backend)       │                          │     ml)          │
└────────┬─────────┘                          └──────────────────┘
         │ HTTP (PRIVATE)
         │ SANDBOX_SERVICE_URL
         │ + SANDBOX_TOKEN_SECRET
         ▼
┌──────────────────┐
│    Sandbox       │
│ (monkey-coder-   │
│   sandbox)       │
└──────────────────┘
```

**Legend:**
- **PUBLIC**: Accessible from internet (browser, webhooks)
- **PRIVATE**: Internal Railway network only (zero egress cost)
- **Auth**: Requires SANDBOX_TOKEN_SECRET authentication

---

## 💾 Backup Current Config (Before Changes)

```bash
# Export current variables to file
railway variables --service monkey-coder-sandbox > backup-sandbox-vars.txt
railway variables --service monkey-coder-backend > backup-backend-vars.txt
railway variables --service monkey-coder > backup-frontend-vars.txt

# Include timestamp
date >> backup-vars-$(date +%Y%m%d-%H%M%S).log
```

---

## 🔄 Rollback Procedure

```bash
# If something goes wrong, rollback deployment
railway rollback --service monkey-coder-sandbox
railway rollback --service monkey-coder-backend

# Or use Railway Dashboard:
# Project → Service → Deployments → Select previous → Rollback
```

---

## 📞 Support

- **Railway Docs:** https://docs.railway.com/
- **Railway Status:** https://railway.statuspage.io/
- **Issue Tracker:** https://github.com/GaryOcean428/monkey-coder/issues

---

**Last Updated:** 2026-02-12 | **Version:** 1.0
