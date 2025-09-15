# Railway Frontend Fix Implementation Guide

## Problem Summary
The Railway deployment was showing the API fallback page instead of the Next.js frontend because static frontend assets weren't being built during deployment.

## Root Cause
- Frontend build directory (`packages/web/out`) missing at runtime
- Railway either not using `railpack.json` or frontend build failing during deployment  
- FastAPI backend falling back to API-only HTML page

## Solution Implemented

### 🔧 Three-Layer Fix Strategy

#### 1. Enhanced Build Process (`railpack.json`)
**What Changed**: Added comprehensive environment variable setup and detailed logging
```json
{
  "build": {
    "commands": [
      "export NEXT_OUTPUT_EXPORT=true",
      "export NEXTAUTH_URL=${NEXTAUTH_URL:-https://coder.fastmonkey.au}",
      "yarn workspace @monkey-coder/web run export && echo '✅ Frontend build completed successfully' || echo '⚠️ Frontend build failed, runtime fallback will be used'"
    ]
  }
}
```

#### 2. Runtime Fallback (`run_server.py`)
**What Changed**: Added frontend building capability at server startup
- Detects missing frontend assets
- Automatically rebuilds frontend if missing
- Comprehensive error handling and logging
- Falls back gracefully to API-only mode if build fails

#### 3. Alternative Unified Mode (`run_unified.js`) 
**What Changed**: Production-ready multi-process deployment
- Runs Python backend and Next.js server simultaneously
- Health checks and graceful shutdown
- Process restart capabilities

## 🚀 Railway Deployment Instructions

### Step 1: Verify Railway Configuration
1. **In Railway Dashboard**:
   - Go to your `monkey-coder` service settings
   - Ensure **Build Method** is set to **Railpack** (not Nixpacks)
   - If using Nixpacks, switch to Railpack

### Step 2: Set Environment Variables
**Add these variables in Railway's Environment tab**:

```bash
# Required for Next.js build
NEXTAUTH_URL=https://coder.fastmonkey.au
NEXTAUTH_SECRET=your-production-secret-here
NEXT_PUBLIC_API_URL=https://coder.fastmonkey.au  
NEXT_PUBLIC_APP_URL=https://coder.fastmonkey.au

# Optional (can be empty)
DATABASE_URL=
```

### Step 3: Deploy with Enhanced Configuration

**Option A: Default Enhanced Mode (Recommended)**
- Use current `railpack.json` configuration 
- Start command: `python run_server.py`
- **Benefits**: Runtime fallback + static serving optimization

**Option B: Unified Multi-Process Mode**  
- Change Railway start command to: `node run_unified.js`
- **Benefits**: Separate frontend and backend processes

### Step 4: Verify Deployment
1. **Check build logs** for:
   ```
   ✅ Frontend build completed successfully
   ```
2. **Access your domain**: Should show Next.js frontend, not API page
3. **Check health endpoint**: `https://coder.fastmonkey.au/health`

## 🔍 Troubleshooting

### If Frontend Still Missing
1. **Check Railway logs** during build phase
2. **Look for**: `⚠️ Frontend build failed, runtime fallback will be used`
3. **Server will attempt rebuild** at startup (check logs)

### Common Issues & Solutions

**Issue**: "Module not found: uvicorn"
**Solution**: Ensure Railway is using Railpack, not Nixpacks

**Issue**: "NEXTAUTH_SECRET missing"  
**Solution**: Set environment variables in Railway dashboard

**Issue**: "Build timeout"
**Solution**: Frontend will rebuild at runtime automatically

### Manual Testing
```bash
# Test locally
NEXT_OUTPUT_EXPORT=true yarn workspace @monkey-coder/web run export
ls packages/web/out/  # Should show index.html and other files
```

## 📁 Files Modified

- ✅ `run_server.py` - Runtime frontend building with fallbacks
- ✅ `run_unified.js` - Production multi-process deployment
- ✅ `railpack.json` - Enhanced build logging and environment setup  
- ✅ `.env.railway.frontend` - Environment variable template

## 🎯 Expected Results

**Before Fix**: API fallback page with text "Monkey Coder API"
**After Fix**: Full Next.js frontend with dashboard, authentication, etc.

The implementation provides multiple fallback layers to ensure frontend availability even if initial build fails, while maintaining full API functionality.