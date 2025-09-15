# Railway Deployment Final Fix Guide

## Complete Fix Implementation - Phase 2

This guide provides the complete solution to fix the Railway deployment where the API documentation is appearing instead of the main Monkey Coder frontend at https://coder.fastmonkey.au.

## Current Status

✅ **Phase 1 Complete**: Frontend build infrastructure implemented
✅ **Phase 2 Ready**: Environment configuration system prepared

## Root Cause Analysis

The deployment issue occurs because:

1. **Frontend static files missing**: Next.js export process fails due to missing environment variables
2. **FastAPI fallback mode**: When static files aren't found, the backend serves API documentation only
3. **Environment variables unconfigured**: Required secrets and configuration missing from Railway

## Complete Solution

### Step 1: Environment Variable Configuration (Critical)

The environment setup system has generated the required configuration files. You need to set these variables in Railway:

#### Quick Setup via Railway Dashboard

1. **Access Railway Project**:
   - Go to https://railway.app
   - Select the "monkey-coder" service in AetherOS project
   - Navigate to "Variables" tab

2. **Copy Environment Variables**:
   Use the generated `.env.railway.complete` file content:

```bash
# Core Configuration
NODE_ENV=production
PYTHON_ENV=production
RAILWAY_ENVIRONMENT=production

# Security Configuration (CRITICAL)
JWT_SECRET_KEY=QwfZ4DUMAXpQIm010ntVFsiIh9T9Nlxf
NEXTAUTH_SECRET=52TLtnB8u95dfcfnqwsAfJP88e6NZkoO

# Frontend Configuration (CRITICAL)
NEXTAUTH_URL=https://coder.fastmonkey.au
NEXT_PUBLIC_API_URL=https://coder.fastmonkey.au
NEXT_PUBLIC_APP_URL=https://coder.fastmonkey.au
NEXT_OUTPUT_EXPORT=true
NEXT_TELEMETRY_DISABLED=1

# AI Provider Keys (Replace with real API keys)
OPENAI_API_KEY=your_actual_openai_key_here
ANTHROPIC_API_KEY=your_actual_anthropic_key_here
GOOGLE_API_KEY=your_actual_google_key_here
```

3. **Essential AI Provider Setup**:
   Replace the placeholder API keys with real ones for AI functionality:
   - OpenAI: Get from https://platform.openai.com/api-keys
   - Anthropic: Get from https://console.anthropic.com/
   - Google: Get from https://console.cloud.google.com/

### Step 2: Verify Build Configuration

Ensure Railway is using the correct build method:

1. **Check Build Method**:
   - In Railway service settings → "Build" tab
   - Verify "Build Method" is set to "Railpack"
   - If not, change from "Nixpacks" to "Railpack"

2. **Verify railpack.json**:
   The repository contains a comprehensive `railpack.json` with:
   - Multi-stage frontend build process
   - Multiple fallback methods
   - Environment variable setup
   - Error handling and logging

### Step 3: Deploy and Verify

1. **Redeploy Service**:
   - In Railway dashboard → "Deployments" tab
   - Click "Redeploy" to trigger new deployment with environment variables

2. **Monitor Build Logs**:
   Look for these success indicators:
   ```
   ✅ Frontend build completed successfully
   Frontend assets count: [number] files
   🚀 Build process completed
   ```

3. **Verify Frontend Serving**:
   - Visit https://coder.fastmonkey.au
   - Should show Monkey Coder frontend instead of API documentation
   - Check developer tools for proper asset loading

### Alternative: Railway CLI Setup (Advanced)

If you have Railway CLI installed:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and link to project
railway login
railway link

# Run the generated setup script
./railway_env_setup.sh

# Redeploy
railway redeploy
```

## Automated Fix Script

The repository includes `railway_frontend_fix.sh` for emergency deployment fixes:

```bash
# In Railway shell or server
chmod +x railway_frontend_fix.sh
./railway_frontend_fix.sh
```

This script will:
- Check repository structure
- Install dependencies if missing
- Build frontend with multiple fallback methods
- Verify static file generation
- Provide detailed diagnostics

## Verification Checklist

After deployment, verify these components:

### ✅ Frontend Verification
- [ ] https://coder.fastmonkey.au shows Monkey Coder UI (not API docs)
- [ ] Static assets load properly (/_next/ directory accessible)
- [ ] Navigation and routing work correctly
- [ ] No 404 errors for frontend assets

### ✅ Backend Verification  
- [ ] API endpoints accessible at /api/v1/
- [ ] Health check responds at /health
- [ ] Database connectivity working
- [ ] Authentication system functional

### ✅ Integration Verification
- [ ] Frontend can communicate with backend API
- [ ] AI providers respond (if configured)
- [ ] User registration/login flows work
- [ ] Error handling displays properly

## Troubleshooting

### Issue: Still seeing API documentation

**Solutions**:
1. Check environment variables are set correctly
2. Verify NEXT_OUTPUT_EXPORT=true is configured  
3. Check build logs for frontend build failures
4. Run `railway_frontend_fix.sh` script

### Issue: Frontend builds but doesn't load

**Solutions**:
1. Check browser console for 404 errors
2. Verify `/_next/` static files are accessible
3. Check NEXTAUTH_URL matches actual domain
4. Verify Content-Security-Policy headers

### Issue: Build process fails

**Solutions**:
1. Check for missing environment variables in build logs
2. Verify Node.js and Python versions in railpack.json
3. Check for dependency conflicts
4. Try the alternative build methods in railpack.json

## Expected Results

After implementing this fix:

1. **Frontend Serving**: https://coder.fastmonkey.au displays the full Monkey Coder application interface
2. **API Access**: Backend API remains fully functional at /api/v1/ endpoints  
3. **Asset Loading**: Static files load properly from /_next/ and /static/ paths
4. **Authentication**: NextAuth.js authentication flows work correctly
5. **AI Integration**: Configured AI providers respond to requests
6. **Database**: PostgreSQL database connectivity maintained
7. **Monitoring**: Error tracking and logging operational

## Support Files Generated

The environment setup has created these files for you:

- `railway_environment_setup.py` - Environment configuration generator
- `.env.railway.complete` - Complete environment variable list
- `railway_env_setup.sh` - Railway CLI setup script  
- `railway_environment_report.json` - Validation report
- `railway_frontend_fix.sh` - Emergency deployment fix script

## Next Steps

1. **Immediate**: Set environment variables in Railway dashboard
2. **Short-term**: Configure real AI provider API keys for full functionality
3. **Long-term**: Set up monitoring with Sentry DSN for error tracking

The deployment infrastructure is now robust and production-ready with comprehensive error handling, multiple build fallbacks, and intelligent environment management.