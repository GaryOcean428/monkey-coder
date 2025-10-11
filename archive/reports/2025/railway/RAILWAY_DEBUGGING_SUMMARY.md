# Railway Debugging Summary - Complete Overview

## Executive Summary

This document provides a comprehensive overview of Railway deployment debugging tools and processes for the Monkey Coder monorepo. All configuration files have been validated and are Railway-ready. The primary remaining step is Railway Dashboard configuration.

## 🎯 Current Status

### Configuration Validation Results ✅

All railpack.json files validated successfully:

| Configuration | Status | Provider | PORT Binding | Host Binding | Health Check |
|--------------|--------|----------|--------------|--------------|--------------|
| railpack.json | ✅ Valid | Node.js | ✓ $PORT | ✓ 0.0.0.0 | ✓ /api/health (300s) |
| railpack-backend.json | ✅ Valid | Python | ✓ $PORT | ✓ 0.0.0.0 | ✓ /api/health (300s) |
| railpack-ml.json | ✅ Valid | Python | ✓ $PORT | ✓ 0.0.0.0 | ✓ /api/health (600s) |

**Railway Best Practices Compliance:**
- ✅ Issue 1: Build System Conflicts - RESOLVED (no competing files)
- ✅ Issue 2: PORT Binding - COMPLIANT (all use $PORT)
- ✅ Issue 3: Health Checks - CONFIGURED (all services)
- ✅ Issue 4: Reference Variables - DOCUMENTED (see below)
- ⚠️ Issue 5: Root Directory - REQUIRES DASHBOARD CONFIGURATION

## 🛠️ Debug Tools Available

### 1. Shell Debug Script
**File**: `scripts/railway-debug.sh`  
**Purpose**: Quick validation without Python dependencies  
**Usage**:
```bash
bash scripts/railway-debug.sh [--service SERVICE] [--fix] [--verbose]
```

**Features**:
- Validates all railpack.json files
- Checks for build system conflicts
- Verifies PORT and host binding
- Validates health check configuration
- Color-coded console output
- Generates Railway CLI fix commands

### 2. Python MCP Debug Tool
**File**: `scripts/railway-mcp-debug.py`  
**Purpose**: Comprehensive debugging with MCP integration  
**Usage**:
```bash
python3 scripts/railway-mcp-debug.py [--service SERVICE] [--fix] [--verbose] [--output FILE]
```

**Features**:
- All shell script features
- MCP framework integration (when available)
- JSON report generation
- Structured issue tracking
- Automated recommendations
- Integration with Railway deployment manager

**Output**:
- Console: Detailed validation results with color coding
- File: `railway-debug-report.json` (configurable)

### 3. Existing Validation Tools

| Tool | Purpose |
|------|---------|
| `railway-validation.sh` | Runtime environment validation |
| `validate-railway-config.sh` | Configuration file validation |
| `fix-railway-services.sh` | Interactive service fix wizard |
| `railway_path_verification.sh` | Path verification utility |
| `mcp-railway-deployment-manager.py` | MCP deployment manager |

## 📚 Documentation Structure

### Quick Reference
- **RAILWAY_DEBUG_QUICK_START.md** - Immediate action guide
  - Quick commands
  - Current status
  - Dashboard configuration checklist
  - Common issues

### Comprehensive Guide
- **RAILWAY_DEBUG_GUIDE.md** - Complete debugging documentation
  - All debug tools
  - Best practices checklist
  - Common issues and solutions
  - Railway CLI reference
  - MCP integration

### Authoritative Configuration
- **RAILWAY_DEPLOYMENT.md** - Official deployment guide
  - Monorepo architecture explanation
  - Service configuration requirements
  - Troubleshooting guide
  - Success indicators

### Emergency Fixes
- **RAILWAY_CRISIS_RESOLUTION.md** - Emergency procedures
  - Crisis identification
  - Quick fix commands
  - Recovery procedures

### MCP Services
- **docs/deployment/railway-services-setup.md** - MCP services guide
  - Environment variables
  - Service setup
  - Validation checklist

## 🚨 Critical Action Required: Railway Dashboard Configuration

### Required for ALL THREE Services

#### 1. Root Directory Setting ⚠️ CRITICAL
```
Railway Dashboard → Service → Settings → Service
  Root Directory: /
  (or leave BLANK)
```

**Why**: Railway must operate from repository root where:
- railpack.json files are located
- Yarn workspaces require root execution
- package.json and yarn.lock are present

#### 2. Clear Manual Overrides
```
Railway Dashboard → Service → Settings → Service
  Build Command: LEAVE BLANK
  Start Command: LEAVE BLANK
```

**Why**: Manual commands override railpack.json configuration

#### 3. Config Path
```
Railway Dashboard → Service → Settings → Config as Code
  Path: [see below]
```

**Service-Specific Config Paths**:
- `monkey-coder` (Frontend): `railpack.json`
- `monkey-coder-backend`: `railpack-backend.json`
- `monkey-coder-ml`: `railpack-ml.json`

**Alternative**: Use single `railpack.json` with `SERVICE_TYPE` environment variable

## 🔧 Environment Variables Configuration

### Frontend Service (monkey-coder)
```bash
NODE_ENV=production
NEXT_OUTPUT_EXPORT=true
NEXT_TELEMETRY_DISABLED=1
NEXT_PUBLIC_APP_URL=https://coder.fastmonkey.au
NEXT_PUBLIC_API_URL=https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}
```

### Backend Service (monkey-coder-backend)
```bash
PYTHON_ENV=production
PYTHONPATH=/app:/app/packages/core
ML_SERVICE_URL=http://${{monkey-coder-ml.RAILWAY_PRIVATE_DOMAIN}}

# API Keys (required)
OPENAI_API_KEY=<your-key>
ANTHROPIC_API_KEY=<your-key>
GROQ_API_KEY=<your-key>
GOOGLE_API_KEY=<your-key>
XAI_API_KEY=<your-key>

# Database (Railway provides)
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
```

### ML Service (monkey-coder-ml)
```bash
PYTHON_ENV=production
PYTHONPATH=/app:/app/services/ml
TRANSFORMERS_CACHE=/app/.cache/huggingface
CUDA_VISIBLE_DEVICES=0
```

## 📊 Deployment Workflow

### Step 1: Pre-Deployment Validation
```bash
# Run debug tools
python3 scripts/railway-mcp-debug.py --verbose
bash scripts/railway-debug.sh --verbose

# Review output - should show 0 critical issues
```

### Step 2: Railway Dashboard Configuration
For each service (monkey-coder, monkey-coder-backend, monkey-coder-ml):

1. Navigate to Railway Dashboard
2. Select service
3. Go to Settings → Service
4. Set Root Directory: `/` (or blank)
5. Clear Build Command
6. Clear Start Command
7. Go to Settings → Config as Code
8. Set Config Path to appropriate railpack file
9. Go to Settings → Variables
10. Configure required environment variables

### Step 3: Deploy Services
```bash
# Ensure Railway CLI is installed and authenticated
railway link

# Deploy services (one at a time recommended)
railway up --service monkey-coder
railway up --service monkey-coder-backend
railway up --service monkey-coder-ml
```

### Step 4: Monitor Deployment
```bash
# Watch logs
railway logs --service monkey-coder --follow
railway logs --service monkey-coder-backend --follow
railway logs --service monkey-coder-ml --follow

# Check for success indicators:
# - "Using config file 'railpack.json'"
# - "Running from /app"
# - "yarn workspace commands succeed" (frontend)
# - "uvicorn starts successfully" (backend/ML)
# - "Health check passed: /api/health"
```

### Step 5: Verify Deployment
```bash
# Test health endpoints
curl https://coder.fastmonkey.au/api/health
curl https://monkey-coder-backend-production.up.railway.app/api/health

# Expected: 200 OK with JSON response
```

## 🐛 Common Issues and Solutions

### Issue: "can't cd to packages/web"
**Symptom**: Build fails with directory not found  
**Cause**: Root directory set to subdirectory  
**Solution**: Set root directory to `/` in Railway Dashboard  
**Prevention**: Use debug tools to validate configuration

### Issue: "yarn: command not found"
**Symptom**: Build fails to find Yarn  
**Cause**: Corepack not enabled properly  
**Solution**: Ensure railpack.json includes corepack enable commands  
**Validation**: All current railpack files include proper corepack setup ✓

### Issue: "Module not found" (Python)
**Symptom**: Python import errors  
**Cause**: PYTHONPATH not configured  
**Solution**: Set PYTHONPATH environment variable  
**Validation**: All railpack files configure PYTHONPATH ✓

### Issue: Health check failing
**Symptom**: Service shows unhealthy in Railway  
**Cause**: Multiple possible causes  
**Solution**:
1. Check application logs
2. Verify health endpoint returns 200
3. Confirm health check path matches railpack.json
4. Check health check timeout (ML needs 600s)

### Issue: Services can't communicate
**Symptom**: Backend can't reach ML service  
**Cause**: Environment variable misconfiguration  
**Solution**: Use Railway reference variables correctly:
- External: `RAILWAY_PUBLIC_DOMAIN`
- Internal: `RAILWAY_PRIVATE_DOMAIN`

## 🔍 Railway CLI Quick Reference

```bash
# Authentication & Project
railway login                             # Authenticate with Railway
railway link                              # Link to Railway project
railway whoami                            # Check authentication status

# Service Management
railway service                           # Interactive service selection
railway service update --root-directory / # Fix root directory
railway status                            # Check project status

# Environment Variables
railway variables --service <name>        # List variables
railway variables set KEY=VALUE           # Set variable
railway variables get KEY                 # Get specific variable

# Deployment
railway up                                # Deploy current service
railway up --service <name>               # Deploy specific service
railway redeploy --service <name>         # Force redeploy

# Monitoring
railway logs --service <name>             # View logs
railway logs --service <name> --follow    # Follow logs
railway logs --service <name> --build     # Build logs
railway logs --service <name> --deployment # Deployment logs
```

## 📈 Success Indicators

After proper configuration, expect to see:

### Frontend (monkey-coder)
- Build time: 2-3 minutes
- Corepack activates Yarn 4.9.2
- Yarn workspace install succeeds
- Next.js build completes
- Static export generated to `packages/web/out`
- Server starts on `0.0.0.0:$PORT`
- Health check passes at `/api/health`

### Backend (monkey-coder-backend)
- Build time: ~2 minutes
- Virtual environment created
- Python dependencies installed
- PYTHONPATH configured correctly
- Uvicorn starts FastAPI app
- Can communicate with ML service
- Health check passes at `/api/health`

### ML Service (monkey-coder-ml)
- First build: 25+ minutes (CUDA/PyTorch downloads ~2.5GB)
- Subsequent builds: ~5 minutes (cached)
- Virtual environment created
- ML dependencies installed (torch, transformers, etc.)
- Model cache configured at `/app/.cache/huggingface`
- Uvicorn starts ML inference service
- Health check passes at `/api/health`

## 🔐 Security Considerations

1. **Secrets Management**: Use Railway environment variables
2. **Service Communication**: Use `RAILWAY_PRIVATE_DOMAIN` for internal calls
3. **External Access**: Use `RAILWAY_PUBLIC_DOMAIN` for public URLs
4. **API Keys**: Never commit to repository
5. **HTTPS**: Railway provides automatic SSL
6. **Health Endpoints**: Ensure they don't expose sensitive information

## 📞 Support Resources

### Internal Documentation
- RAILWAY_DEBUG_QUICK_START.md - Quick start guide
- RAILWAY_DEBUG_GUIDE.md - Complete debugging guide
- RAILWAY_DEPLOYMENT.md - Authoritative deployment guide
- RAILWAY_CRISIS_RESOLUTION.md - Emergency procedures
- CLAUDE.md - Railway best practices section

### Debug Tools
- `scripts/railway-debug.sh` - Shell validation
- `scripts/railway-mcp-debug.py` - Python MCP tool
- `scripts/fix-railway-services.sh` - Interactive fix wizard
- `scripts/railway-validation.sh` - Runtime validation

### External Resources
- [Railway Documentation](https://docs.railway.com/)
- [Railpack Documentation](https://railpack.com/)
- [Yarn Workspaces](https://yarnpkg.com/features/workspaces)

## 🎯 Next Steps

1. **Immediate**: Configure Railway Dashboard for all three services
2. **Deploy**: Use `railway up` to deploy each service
3. **Verify**: Test health endpoints and service communication
4. **Monitor**: Watch logs for any issues
5. **Iterate**: Use debug tools to validate any configuration changes

## 📝 Maintenance

### Regular Validation
```bash
# Run before major deployments
python3 scripts/railway-mcp-debug.py --verbose

# Check for configuration drift
bash scripts/validate-railway-config.sh
```

### After Configuration Changes
1. Validate locally with debug tools
2. Test build with `railway up`
3. Monitor deployment logs
4. Verify health endpoints
5. Test service communication

### Updating Dependencies
```bash
# Frontend
yarn workspace @monkey-coder/web add <package>

# Backend/ML
# Update requirements.txt in appropriate location
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-16  
**Status**: Authoritative Summary  
**Maintainer**: Monkey Coder DevOps Team

**Configuration Status**: ✅ Railway-Ready (Dashboard configuration required)
