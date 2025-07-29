# Unified Deployment Instructions

This guide explains how to deploy the unified Monkey Coder service (frontend + backend) to Railway using the existing service ID: `ccc58ca2-1f4b-4086-beb6-2321ac7dab40`.

## 🎯 Overview

The unified deployment combines:
- **Next.js Frontend**: Built as static files and served by FastAPI
- **Python Backend**: FastAPI with quantum routing and AI orchestration
- **Single Service**: Reduced costs and simplified management

## 📋 Pre-Deployment Checklist

### 1. Test Locally (Optional but Recommended)
```bash
# Run the test script to validate everything works
./test-unified-deployment.sh
```

### 2. Commit Changes
```bash
git add .
git commit -m "feat: implement unified deployment with FastAPI serving Next.js frontend

- Add multi-stage Dockerfile.unified for building both frontend and backend
- Configure Next.js for static export with FastAPI StaticFiles
- Update railpack.json to use Docker provider
- Consolidate frontend and backend into single service for cost optimization"
```

### 3. Push to Repository
```bash
git push origin main
```

## 🚀 Railway Deployment Steps

### Step 1: Access Your Railway Service
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Navigate to your project
3. Select the `monkey-coder` service (ID: `ccc58ca2-1f4b-4086-beb6-2321ac7dab40`)

### Step 2: Update Service Configuration
1. Go to **Settings** tab
2. Under **Source**, ensure it's connected to your GitHub repository
3. Under **Build**, verify it's using the root directory (`/`)
4. Railway should automatically detect the `railpack.json` configuration

### Step 3: Verify Environment Variables
Ensure these environment variables are set:
```
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key  
GOOGLE_API_KEY=your_google_key
SENTRY_DSN=your_sentry_dsn (optional)
PORT=8000 (automatically set by Railway)
```

### Step 4: Deploy
1. Click **Deploy** or push new changes to trigger automatic deployment
2. Monitor the build logs for any issues
3. Wait for deployment to complete (typically 3-5 minutes)

## ✅ Post-Deployment Verification

### 1. Health Check
Test the backend health endpoint:
```bash
curl https://monkey-coder.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-29T...",
  "components": {
    "orchestrator": "active",
    "quantum_executor": "active",
    "persona_router": "active",
    "provider_registry": "active"
  }
}
```

### 2. Frontend Access
Visit the frontend:
```
https://monkey-coder.up.railway.app/
```

You should see the Next.js frontend served by FastAPI.

### 3. API Endpoints
Test API functionality:
```bash
# List providers (requires API key)
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://monkey-coder.up.railway.app/v1/providers

# Check API documentation
open https://monkey-coder.up.railway.app/docs
```

## 🔧 Troubleshooting

### Build Issues
If the build fails:
1. Check Railway build logs
2. Verify `Dockerfile.unified` syntax
3. Ensure all dependencies are correctly specified

### Static Files Not Loading
If frontend doesn't load:
1. Verify `packages/web/out` directory is created during build
2. Check FastAPI logs for static file serving errors
3. Ensure Next.js export configuration is correct

### API Not Working
If backend API fails:
1. Check environment variables are set
2. Verify database connections (PostgreSQL/Redis)
3. Review application logs in Railway dashboard

## 💰 Cost Benefits

This unified deployment provides:
- **~50% cost reduction** compared to separate frontend/backend services
- **Simplified management** with single service monitoring
- **Unified health checks and logging**
- **Reduced inter-service communication overhead**

## 🔄 Rolling Back

If you need to roll back:
1. In Railway dashboard, go to **Deployments**
2. Select a previous successful deployment
3. Click **Redeploy**

## 📊 Monitoring

Monitor your unified service:
- **Railway Dashboard**: View logs, metrics, and health status
- **Sentry**: Error tracking and performance monitoring
- **Health Endpoint**: `/health` for uptime monitoring
- **Metrics Endpoint**: `/metrics` for Prometheus scraping

## 🎉 Next Steps

After successful deployment:
1. Update DNS records if using custom domain
2. Test all critical user workflows
3. Monitor performance and error rates
4. Consider setting up automated health checks
5. Update CI/CD pipelines if needed

Your unified Monkey Coder service is now running at:
**https://monkey-coder.up.railway.app**