# Railway Service Configuration - Quick Reference

## ⚠️ DEPRECATED - See RAILWAY_FIX_INSTRUCTIONS.md

**This document contains INCORRECT configuration that caused 100% deployment failure.**

**The instructions below set `rootDirectory` to subdirectories which breaks Yarn workspaces!**

**Use instead**: `RAILWAY_FIX_INSTRUCTIONS.md` or `RAILWAY_DEPLOYMENT.md`

---

## ⚡ TL;DR (CORRECTED)

Update all 3 services to use root directory:

| Service | Root Dir | Config | Build Time |
|---------|----------|--------|------------|
| `monkey-coder` | `/` | `railpack.json` | ~2 min |
| `monkey-coder-backend` | `/` | `railpack-backend.json` | ~2 min |
| `monkey-coder-ml` | `/` | `railpack-ml.json` | ~25 min |

---

## ⚡ Old TL;DR (INCORRECT - DO NOT USE)

~~Update 2 existing services, create 1 new service:~~

| Service | Status | Root Dir (WRONG) | Config | Build Time |
|---------|--------|----------|--------|------------|
| `monkey-coder` | UPDATE | ~~`services/frontend`~~ | `railpack.json` | ~2 min |
| `monkey-coder-backend` | UPDATE | ~~`services/backend`~~ | `railpack.json` | ~2 min |
| `monkey-coder-ml` | CREATE | ~~`services/ml`~~ | `railpack.json` | ~25 min |

---

## 🎯 Step 1: Update monkey-coder (Frontend)

**Railway Dashboard:**
```
Service: monkey-coder
Settings → Service:
  ├─ Root Directory: services/frontend
  └─ Config Path: railpack.json

Settings → Variables:
  └─ Add: NEXT_PUBLIC_API_URL=https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}

Then: Trigger Redeploy
```

**Expected:** ~2 minute build, serves at `coder.fastmonkey.au`

---

## 🎯 Step 2: Update monkey-coder-backend

**Railway Dashboard:**
```
Service: monkey-coder-backend
Settings → Service:
  ├─ Root Directory: services/backend
  └─ Config Path: railpack.json

Settings → Variables:
  └─ Add: ML_SERVICE_URL=http://${{monkey-coder-ml.RAILWAY_PRIVATE_DOMAIN}}

  (Keep all existing vars: DATABASE_URL, REDIS_URL, API keys, etc.)

Then: Trigger Redeploy
```

**Expected:** ~2 minute build (no torch/CUDA)

---

## 🎯 Step 3: Create monkey-coder-ml (New)

**Railway Dashboard:**
```
New Service Button → From GitHub Repo

Service Name: monkey-coder-ml
Root Directory: services/ml
Config Path: railpack.json

Settings → Variables:
  ├─ PYTHON_ENV=production
  ├─ TRANSFORMERS_CACHE=/app/.cache/huggingface
  └─ CUDA_VISIBLE_DEVICES=0

Settings → Storage → Add Volume:
  ├─ Mount Path: /app/.cache
  └─ Size: 10GB (for model weights and torch cache)

Then: Deploy
```

**Expected:** ~25 minute build (2.5GB torch/CUDA downloads)

---

## ✅ Verification

After all 3 services deploy:

```bash
# Frontend
curl https://coder.fastmonkey.au

# Backend API
curl https://monkey-coder-backend-production.up.railway.app/health

# ML Service (internal only)
# Backend will proxy requests to: monkey-coder-ml.railway.internal
```

---

## 🔄 Service Communication

```
User Request
    ↓
monkey-coder (Frontend)
    ↓ API calls
monkey-coder-backend (API)
    ↓ ML requests
monkey-coder-ml (Internal)
```

---

## 📊 Resource Allocation

| Service | Memory | CPU | Public |
|---------|--------|-----|--------|
| monkey-coder | 512MB | Low | ✅ coder.fastmonkey.au |
| monkey-coder-backend | 1GB | Low | ✅ (API endpoint) |
| monkey-coder-ml | 4-8GB | High | ❌ (internal only) |

---

## 🚨 Common Issues

### "Root directory not found"
- Make sure you typed `services/frontend` not `/services/frontend`
- Railway paths are relative to repo root

### "Build failed: yarn not found"
- Frontend service: Check railpack.json has `corepack enable` in install commands
- Backend service: Should use Python, not Node

### "ML service timeout"
- First build takes 25+ minutes - this is normal
- Railway may show "Application failed to respond" during build
- Wait for build logs to show "Successfully installed torch..."

---

## 📝 Rollback Plan

If something breaks:

1. Change Root Directory back to `/` on affected service
2. Change Config Path back to `railpack.json` (root)
3. Redeploy

The root railpack.json still works for monolithic setup.