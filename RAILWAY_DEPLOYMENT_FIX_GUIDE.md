# 🚂 Railway Deployment Fix Guide
## Monkey Coder Project - October 2025

---

## 🔍 **Issue Summary**

Your Railway deployment has **3 services** configured:
- ✅ `monkey-coder-backend` - **Working** (Python FastAPI)
- ✅ `monkey-coder-ml` - **Configured correctly** (Python ML service)
- ❌ `monkey-coder` (frontend) - **FIXED** (Next.js static export now properly configured)

### **Root Cause (Now Fixed)**
The frontend service was trying to run `next start` on a static export, which is impossible. When Next.js builds with `output: 'export'`, it creates static HTML/CSS/JS files that need a **static file server**, not the Next.js server.

**Fix Applied:** Changed startCommand to use `serve` package for serving static files.

---

## 🎯 **What Was Changed**

### 1. **railpack.json** - Updated
```json
{
  "deploy": {
    "startCommand": "serve -s packages/web/out -l $PORT -c serve.json"
  }
}
```

### 2. **serve.json** - Created
New configuration file for the static file server with:
- SPA routing (all routes → index.html)
- Cache headers (1 hour general, 1 year for static assets)
- Security headers (XSS protection, frame options)

### 3. **validate_deployment.sh** - Created
Validation script to check deployment readiness before pushing.

---

## 🚀 **Deployment Instructions**

### **Immediate Steps**

The fixes have been applied directly to your repository. Now deploy:

```bash
# 1. Pull the latest changes
git pull origin main

# 2. Run validation (optional but recommended)
chmod +x validate_deployment.sh
./validate_deployment.sh

# 3. Railway will auto-deploy on push, or manually trigger
railway up

# 4. Monitor deployment
railway logs --service monkey-coder --tail
```

---

## 🧪 **Testing the Deployment**

### **Local Testing**

Before relying on Railway deployment:

```bash
# 1. Build the frontend
yarn workspace @monkey-coder/web build

# 2. Test serving locally
npx serve -s packages/web/out -l 3000

# 3. Open browser to http://localhost:3000
```

### **Railway Testing**

After deployment:

```bash
# Check health endpoints
curl https://monkey-coder.up.railway.app/
curl https://monkey-coder-backend.up.railway.app/api/health
curl https://monkey-coder-ml.up.railway.app/api/health

# View logs
railway logs --service monkey-coder
railway logs --service monkey-coder-backend
railway logs --service monkey-coder-ml
```

---

## 📊 **Railway Service Configuration**

### **Current Setup**

| Service Name | Purpose | railpack.json | Status |
|-------------|---------|---------------|--------|
| `monkey-coder` | Frontend (Next.js static) | `railpack.json` | ✅ Fixed |
| `monkey-coder-backend` | API Server (FastAPI) | `railpack-backend.json` | ✅ Working |
| `monkey-coder-ml` | ML Inference | `railpack-ml.json` | ✅ Working |

### **Environment Variables**

Set these in Railway dashboard:

**Frontend Service:**
```bash
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}
NEXT_TELEMETRY_DISABLED=1
```

**Backend Service:**
```bash
PYTHON_ENV=production
ALLOWED_ORIGINS=https://${{monkey-coder.RAILWAY_PUBLIC_DOMAIN}}
CORS_ORIGINS=https://${{monkey-coder.RAILWAY_PUBLIC_DOMAIN}}
```

**ML Service:**
```bash
PYTHON_ENV=production
ML_MODEL_PATH=/app/.cache/huggingface
TRANSFORMERS_CACHE=/app/.cache/huggingface
```

---

## 🔧 **Understanding the Fix**

### **Before (Broken)**

```json
{
  "build": {
    "env": {
      "NEXT_OUTPUT_EXPORT": "true"  // Creates static export
    }
  },
  "deploy": {
    "startCommand": "next start"  // Tries to run server ❌
  }
}
```

**Problem:** `next start` requires a Node.js server build (`.next/` directory), but we're creating a static export (`out/` directory).

### **After (Fixed)**

```json
{
  "build": {
    "commands": [
      "yarn workspace @monkey-coder/web build",
      "yarn global add serve@14.2.4"  // Install static server
    ],
    "env": {
      "NEXT_OUTPUT_EXPORT": "true"  // Still creates static export
    }
  },
  "deploy": {
    "startCommand": "serve -s packages/web/out -l $PORT"  // Serve static files ✅
  }
}
```

**Solution:** Use `serve` package to serve the static files from `out/` directory.

---

## 🆘 **Troubleshooting**

### **Frontend Still Not Loading**

1. **Check build logs:**
   ```bash
   railway logs --service monkey-coder --deployment <deployment-id>
   ```

2. **Verify static files exist:**
   ```bash
   railway run ls -la packages/web/out
   ```

3. **Look for these success indicators:**
   ```
   ✅ "Accepting connections at http://0.0.0.0:XXXX"
   ✅ "serve: Running on port XXXX"
   ✅ Build contains: yarn global add serve
   ```

### **Common Issues**

| Issue | Cause | Solution |
|-------|-------|----------|
| 404 on all routes | SPA routing not working | Check `serve.json` exists and has rewrites |
| CSS not loading | Wrong public path | Verify `trailingSlash: true` in next.config.js |
| API calls fail | CORS not configured | Add CORS middleware to FastAPI backend |
| Build succeeds, deploy fails | `serve` not installed | Check build logs for "yarn global add serve" |

### **Backend CORS Configuration**

If frontend can't connect to backend API:

```python
# packages/core/monkey_coder/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000"),
        os.environ.get("FRONTEND_URL", "http://localhost:3000")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📋 **Deployment Checklist**

Use this before every deployment:

- [x] All `railpack.json` files are valid JSON ✅
- [x] No conflicting build configs (Dockerfile, railway.toml) ✅
- [x] Frontend uses `serve` for static files ✅
- [x] `serve.json` exists with SPA routing ✅
- [x] All services bind to `0.0.0.0:$PORT` ✅
- [x] Health check endpoints exist ✅
- [ ] Environment variables configured in Railway
- [ ] CORS configured for cross-origin requests
- [ ] Test build locally before pushing
- [ ] Monitor deployment logs after push

---

## 🎉 **Success Indicators**

Your deployment is successful when:

1. ✅ Frontend loads at `https://monkey-coder.up.railway.app`
2. ✅ API responds at `https://monkey-coder-backend.up.railway.app/api/health`
3. ✅ ML service health check passes
4. ✅ No CORS errors in browser console
5. ✅ All Railway services show "Active" status
6. ✅ Build logs show "yarn global add serve" succeeded
7. ✅ Deploy logs show "Accepting connections at http://0.0.0.0:XXXX"

---

## 📚 **Additional Resources**

- [Railway Documentation](https://docs.railway.com)
- [Next.js Static Export](https://nextjs.org/docs/app/building-your-application/deploying/static-exports)
- [Serve Package](https://github.com/vercel/serve)
- [FastAPI Static Files](https://fastapi.tiangolo.com/tutorial/static-files/)
- [Railway CLI Reference](https://docs.railway.com/reference/cli-api)

---

## 💡 **Key Learnings**

### **Next.js Output Modes**

1. **Server Mode** (default):
   - Builds: `.next/` directory
   - Runs: `next start`
   - Requires: Node.js runtime

2. **Static Export** (your configuration):
   - Builds: `out/` directory
   - Runs: Static file server (`serve`, `nginx`, etc.)
   - Requires: ANY web server

**Remember:** You can't use `next start` with static exports!

### **Railway Best Practices**

1. Always use `process.env.PORT` - Railway assigns ports dynamically
2. Bind to `0.0.0.0` - Never `localhost` or `127.0.0.1`
3. Include health check endpoints - Railway monitors these
4. Use `serve.json` for static file server configuration
5. Test locally with Railway CLI: `railway run`

---

## 🔄 **Maintenance**

### **Updating Dependencies**

```bash
# Update Next.js
yarn workspace @monkey-coder/web add next@latest

# Update serve
yarn global add serve@latest

# Update Python dependencies
pip install -r requirements.txt --upgrade
```

### **Monitoring**

```bash
# Real-time logs
railway logs --tail

# Specific service
railway logs --service monkey-coder-backend --tail

# Deployment status
railway status

# List all services
railway service
```

---

**Last Updated:** October 8, 2025  
**Deployment Target:** Railway.app  
**Project:** Monkey Coder (AetherOS)  
**Status:** ✅ Fixed and Ready to Deploy
