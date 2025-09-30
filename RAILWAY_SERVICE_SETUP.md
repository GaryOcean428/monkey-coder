# Railway 3-Service Architecture Setup

## Overview

Following the Gary8D-monorepo pattern, Monkey Coder is split into 3 services to optimize memory usage and build times:

1. **monkey-coder-frontend** - Next.js static site (Node.js)
2. **monkey-coder-backend** - FastAPI without ML (~2min build)
3. **monkey-coder-ml** - ML inference service (~25min build, scales independently)

## Service Configuration

### 1. Frontend Service (monkey-coder-frontend)

**Railway Dashboard Settings:**
- Service Name: `monkey-coder-frontend` (or keep as `monkey-coder`)
- Root Directory: `services/frontend`
- Config Path: `railpack.json`

**What it does:**
- Builds Next.js static export
- Serves via `npx serve`
- ~2-3 minute build time
- Minimal memory footprint

**Environment Variables:**
```bash
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}
```

---

### 2. Backend Service (monkey-coder-backend)

**Railway Dashboard Settings:**
- Service Name: `monkey-coder-backend`
- Root Directory: `services/backend`
- Config Path: `railpack.json`

**What it does:**
- FastAPI with lightweight dependencies only
- Routes requests to ML service when needed
- ~2 minute build time (no torch/CUDA)
- Low memory usage

**Environment Variables:**
```bash
PYTHON_ENV=production
ML_SERVICE_URL=http://${{monkey-coder-ml.RAILWAY_PRIVATE_DOMAIN}}
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
# Copy all API keys from current monkey-coder service
OPENAI_API_KEY=${{...}}
ANTHROPIC_API_KEY=${{...}}
GROQ_API_KEY=${{...}}
GOOGLE_API_KEY=${{...}}
XAI_API_KEY=${{...}}
```

**requirements.txt:**
- Located at `services/backend/requirements.txt`
- Contains only FastAPI, httpx, database drivers, AI SDKs
- **No torch, transformers, or CUDA**

---

### 3. ML Service (monkey-coder-ml)

**Railway Dashboard Settings:**
- Service Name: `monkey-coder-ml`
- Root Directory: `services/ml`
- Config Path: `railpack.json`

**What it does:**
- Handles ML inference (code generation, analysis)
- Loads torch, transformers, sentence-transformers
- ~25 minute build time (2.5GB+ dependencies)
- High memory usage (scales independently)

**Environment Variables:**
```bash
PYTHON_ENV=production
TRANSFORMERS_CACHE=/app/.cache/huggingface
CUDA_VISIBLE_DEVICES=0
```

**requirements.txt:**
- Located at `services/ml/requirements.txt`
- Contains torch==2.3.0, transformers, accelerate, all CUDA libs
- Total size: ~2.5GB

---

## Migration Steps

### Step 1: Update Existing Service (Frontend)

1. Go to Railway Dashboard → `monkey-coder` service
2. Settings → Service → Root Directory: `services/frontend`
3. Settings → Config as Code → Path: `railpack.json`
4. Settings → Environment Variables → Add `NEXT_PUBLIC_API_URL`
5. Trigger redeploy

### Step 2: Create Backend Service

1. Railway Dashboard → Add New Service
2. Name: `monkey-coder-backend`
3. Source: Same GitHub repo
4. Root Directory: `services/backend`
5. Config Path: `railpack.json`
6. Add all environment variables listed above
7. Deploy

### Step 3: Create ML Service

1. Railway Dashboard → Add New Service
2. Name: `monkey-coder-ml`
3. Source: Same GitHub repo
4. Root Directory: `services/ml`
5. Config Path: `railpack.json`
6. Add ML-specific environment variables
7. Deploy (will take ~25 minutes first time)

---

## Service Communication

```
User → Frontend (Static)
         ↓
      Backend API (FastAPI)
         ↓
      ML Service (Internal)
```

**Internal URLs:**
- Backend → ML: `http://monkey-coder-ml.railway.internal`
- Railway automatically provides: `${{service-name.RAILWAY_PRIVATE_DOMAIN}}`

**Public URLs:**
- Frontend: `https://coder.fastmonkey.au`
- Backend API: `https://monkey-coder-backend-production.up.railway.app`
- ML: Internal only (not exposed publicly)

---

## Build Time Comparison

| Service | Old (Monolithic) | New (Split) |
|---------|------------------|-------------|
| Frontend | 25+ min (full stack) | **2-3 min** |
| Backend | 25+ min (full stack) | **2 min** |
| ML | N/A | 25 min (once) |
| **Total** | 25+ min | **~30 min first time, 2-3 min subsequent** |

**Key Benefit:** Frontend and backend deploy in ~2 minutes. ML service scales independently and only rebuilds when ML dependencies change.

---

## Memory Usage

| Service | Memory | Scales |
|---------|--------|--------|
| Frontend | ~512MB | Horizontally |
| Backend | ~1GB | Horizontally |
| ML | ~4-8GB | Independently |

ML service can scale to 0 when not in use or scale up during high demand without affecting frontend/backend.

---

## Troubleshooting

### Backend can't find packages/core

**Fix:** Update `PYTHONPATH` in backend railpack.json:
```json
"env": {
  "PYTHONPATH": "/app:/app/../../packages/core"
}
```

### ML service timeout

**Expected:** First build takes 25+ minutes due to torch/CUDA downloads.
**Fix:** Increase healthCheckTimeout to 600 seconds in railpack.json.

### Frontend API calls failing

**Check:** Ensure `NEXT_PUBLIC_API_URL` points to backend service public domain.

---

## Rollback Plan

If 3-service setup has issues:

1. Keep using current `monkey-coder` service (monolithic)
2. Point Root Directory back to `/`
3. Keep using root `railpack.json`

The new services/ directory structure doesn't break the existing setup.