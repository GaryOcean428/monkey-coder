# Railway Frontend Fix Guide

This guide provides step-by-step instructions to fix the Railway deployment where the API UI is appearing instead of the main frontend UI.

## Problem Summary

The Railway deployment at `https://coder.fastmonkey.au` is currently showing only the FastAPI backend documentation instead of the full Monkey Coder frontend application. This happens when:

1. The frontend static files are not built during deployment
2. The FastAPI backend falls back to serving API documentation instead of the frontend
3. Environment variables may be missing or incorrectly configured

## Root Causes

1. **Frontend Build Failure**: The Next.js export process fails during Railway deployment
2. **Missing Environment Variables**: Required variables for Next.js build are not set
3. **Build Method Mismatch**: Railway may be using Nixpacks instead of railpack.json
4. **Runtime Build Issues**: The fallback runtime build process is not working properly

## Fix Instructions

### Option 1: Quick Fix via Railway CLI (Recommended)

1. **Access Railway Service**
   ```bash
   # Install Railway CLI if not already installed
   npm install -g @railway/cli
   
   # Login to Railway
   railway login
   
   # Connect to your project
   railway link
   
   # Open shell in the running service
   railway shell
   ```

2. **Run the Fix Script**
   ```bash
   # In the Railway shell, run:
   chmod +x railway_frontend_fix.sh
   ./railway_frontend_fix.sh
   ```

3. **Restart the Service**
   ```bash
   # Exit the shell and restart the service
   railway service restart
   ```

### Option 2: Fix via Railway Dashboard

1. **Check Build Configuration**
   - Go to Railway dashboard → your project → monkey-coder service
   - Go to Settings → Build
   - Ensure "Build Method" is set to **Railpack** (not Nixpacks)
   - If not, change it and redeploy

2. **Verify Environment Variables**
   - Go to Variables tab
   - Ensure these variables are set:
     ```
     NEXTAUTH_URL=https://coder.fastmonkey.au
     NEXTAUTH_SECRET=your-secret-here
     NEXT_PUBLIC_API_URL=https://coder.fastmonkey.au
     NEXT_PUBLIC_APP_URL=https://coder.fastmonkey.au
     DATABASE_URL=your-database-url
     ```

3. **Force Rebuild**
   - Go to Deployments tab
   - Click "Redeploy" on the latest deployment
   - Monitor build logs for frontend build completion

### Option 3: Switch to Unified Deployment

If the static export continues to fail, switch to running both frontend and backend as separate processes:

1. **Update Start Command**
   - In Railway dashboard → Settings → Deploy
   - Change start command from `python run_server.py` to `node run_unified.js`

2. **Set Environment Variables**
   ```
   BACKEND_PORT=8000
   FRONTEND_START_DELAY=8000
   HEALTH_CHECK_RETRIES=30
   ```

3. **Redeploy the Service**

## Verification Steps

After applying any fix:

1. **Check Health Endpoint**
   ```bash
   curl https://coder.fastmonkey.au/health
   ```

2. **Verify Frontend Loads**
   - Visit `https://coder.fastmonkey.au` in browser
   - Should show Monkey Coder frontend, not API documentation

3. **Test API Endpoints**
   ```bash
   curl https://coder.fastmonkey.au/api/docs
   curl https://coder.fastmonkey.au/api/v1/capabilities
   ```

## Troubleshooting

### If Build Still Fails

1. **Check Railway Build Logs**
   - Railway dashboard → Deployments → latest deployment → View Logs
   - Look for Node.js/yarn errors during frontend build

2. **Common Issues**
   - Missing Node.js dependencies: Ensure `node: "20"` in railpack.json
   - Environment variable errors: Set all required Next.js variables
   - Memory/timeout issues: Frontend build takes significant resources

3. **Manual Build Test**
   ```bash
   # In Railway shell:
   cd packages/web
   NEXT_OUTPUT_EXPORT=true yarn run export
   ls -la out/  # Check if files were created
   ```

### If Frontend Loads but API Doesn't Work

1. **Check CORS Configuration**
   - Frontend and API must be on same domain
   - Verify `NEXT_PUBLIC_API_URL` matches deployment domain

2. **Authentication Issues**
   - Check `NEXTAUTH_URL` and `NEXTAUTH_SECRET` are set
   - Verify JWT configuration is working

## Expected Behavior After Fix

- **Frontend**: `https://coder.fastmonkey.au` shows the full Monkey Coder web interface
- **API Docs**: `https://coder.fastmonkey.au/api/docs` shows FastAPI documentation
- **Health Check**: `https://coder.fastmonkey.au/health` returns healthy status
- **Static Assets**: CSS, JS, and images load properly from the frontend

## Prevention

To prevent this issue in future deployments:

1. **Always Use railpack.json**: Ensure Railway uses Railpack build method
2. **Set All Environment Variables**: Use the provided .env.railway.template
3. **Test Frontend Build Locally**: Run `yarn workspace @monkey-coder/web run export` before deploying
4. **Monitor Deployment Logs**: Check for frontend build success in Railway logs
5. **Use Health Checks**: Monitor `/health` endpoint for service status

## Emergency Fallback

If all else fails, you can temporarily serve just the API:

1. **Disable Frontend Serving**
   ```
   SERVE_FRONTEND=false
   ```

2. **Deploy Frontend Separately**
   - Use Vercel/Netlify for frontend
   - Point `NEXT_PUBLIC_API_URL` to Railway backend
   - Update CORS settings to allow cross-origin requests

This ensures the API remains functional while frontend issues are resolved.