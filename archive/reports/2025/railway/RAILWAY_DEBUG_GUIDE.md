# Railway Deployment Debug Guide

## Overview

This guide provides comprehensive Railway deployment debugging tools and procedures for the Monkey Coder monorepo. It integrates Railway best practices with MCP (Model Context Protocol) tools for automated validation and issue resolution.

## Quick Start

### Run Debug Tools

```bash
# Shell-based debug tool (no dependencies)
bash scripts/railway-debug.sh --verbose

# Python MCP debug tool (enhanced features)
python3 scripts/railway-mcp-debug.py --verbose

# Service-specific debugging
bash scripts/railway-debug.sh --service monkey-coder
python3 scripts/railway-mcp-debug.py --service monkey-coder-backend

# With auto-fix attempt
bash scripts/railway-debug.sh --fix
python3 scripts/railway-mcp-debug.py --fix
```

## Debug Tools

### 1. Shell Debug Script (`railway-debug.sh`)

**Purpose**: Quick validation without Python dependencies

**Features**:
- Validates all railpack.json files
- Checks for build system conflicts
- Verifies PORT and host binding
- Validates health check configuration
- Generates Railway CLI fix commands

**Output**: Console output with color-coded status

### 2. Python MCP Debug Tool (`railway-mcp-debug.py`)

**Purpose**: Comprehensive debugging with MCP integration

**Features**:
- All features from shell script
- MCP framework integration (when available)
- JSON report generation
- Structured issue tracking
- Automated recommendations
- Integration with Railway deployment manager

**Output**:
- Console output with detailed status
- JSON report: `railway-debug-report.json`

### 3. Existing Validation Scripts

**`railway-validation.sh`**: Runtime environment validation
**`validate-railway-config.sh`**: Configuration file validation
**`fix-railway-services.sh`**: Interactive service fix wizard

## Railway Best Practices Checklist

### Issue 1: Build System Conflicts ✓

**Problem**: Multiple build configurations competing (Dockerfile, railway.toml, nixpacks.toml)

**Solution**:
- ✅ Use only `railpack.json` files (3 files for 3 services)
- ✅ Remove/rename competing files
- ✅ Railway reads railpack.json from repo root

**Validation**:
```bash
# Check for competing files
ls -la Dockerfile railway.toml nixpacks.toml 2>/dev/null
```

### Issue 2: PORT Binding Failures ✓

**Problem**: Apps hardcoding ports or not using $PORT

**Solution**:
- ✅ All start commands use `$PORT` variable
- ✅ Applications bind to `0.0.0.0` not localhost
- ✅ Never hardcode port numbers

**Current Configuration**:
```json
// railpack.json (Frontend)
"startCommand": "yarn workspace @monkey-coder/web start --hostname 0.0.0.0 --port $PORT"

// railpack-backend.json
"startCommand": ".venv/bin/python -m uvicorn monkey_coder.app.main:app --host 0.0.0.0 --port $PORT"

// railpack-ml.json
"startCommand": ".venv/bin/python -m uvicorn services.ml.ml_server:app --host 0.0.0.0 --port $PORT"
```

### Issue 3: Health Check Configuration ✓

**Problem**: Missing or misconfigured health check endpoints

**Solution**:
- ✅ All services have `/api/health` endpoint
- ✅ Health check timeouts configured:
  - Frontend: 300s
  - Backend: 300s
  - ML: 600s (longer due to model loading)

**Validation**:
```bash
# Test health endpoints
curl https://monkey-coder.up.railway.app/api/health
curl https://monkey-coder-backend-production.up.railway.app/api/health
```

### Issue 4: Reference Variable Mistakes ✓

**Problem**: Incorrect Railway variable references

**Solution**:
- ✅ Use `RAILWAY_PUBLIC_DOMAIN` for external URLs
- ✅ Use `RAILWAY_PRIVATE_DOMAIN` for internal communication
- ✅ Never reference PORT of another service

**Required Environment Variables**:

**Frontend (monkey-coder)**:
```bash
NODE_ENV=production
NEXT_OUTPUT_EXPORT=true
NEXT_TELEMETRY_DISABLED=1
NEXT_PUBLIC_APP_URL=https://coder.fastmonkey.au
NEXT_PUBLIC_API_URL=https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}
```

**Backend (monkey-coder-backend)**:
```bash
PYTHON_ENV=production
PYTHONPATH=/app:/app/packages/core
ML_SERVICE_URL=http://${{monkey-coder-ml.RAILWAY_PRIVATE_DOMAIN}}
# Plus API keys: OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.
```

**ML (monkey-coder-ml)**:
```bash
PYTHON_ENV=production
PYTHONPATH=/app:/app/services/ml
TRANSFORMERS_CACHE=/app/.cache/huggingface
CUDA_VISIBLE_DEVICES=0
```

### Issue 5: Monorepo Service Configuration ⚠️ CRITICAL

**Problem**: Services configured with subdirectory root paths

**Solution**:
- ⚠️ **CRITICAL**: ALL services MUST use root directory `/`
- Railway reads railpack.json from repo root only
- Yarn workspaces require execution from repo root
- Service separation via config files, NOT directories

**Railway Dashboard Configuration** (for EACH service):

```
Settings → Service:
  ├─ Root Directory: / (or leave BLANK)
  ├─ Build Command: LEAVE BLANK (uses railpack.json)
  └─ Start Command: LEAVE BLANK (uses railpack.json)

Settings → Config as Code:
  └─ Path: [railpack.json | railpack-backend.json | railpack-ml.json]
```

## Common Deployment Issues

### Issue: "can't cd to packages/web"

**Cause**: Service root directory set to subdirectory
**Fix**: Set root directory to `/` or blank

### Issue: "yarn: command not found"

**Cause**: Corepack not enabled
**Fix**: Ensure railpack.json has proper corepack commands

### Issue: "Module not found" in Python

**Cause**: PYTHONPATH not configured
**Fix**: Set PYTHONPATH in environment variables

### Issue: Health check failing

**Cause**:
- Application not starting
- Health endpoint not implemented
- Wrong health check path

**Fix**:
1. Check application logs
2. Verify health endpoint returns 200
3. Confirm health check path in railpack.json

## Railway CLI Quick Reference

```bash
# Project management
railway link                              # Link to Railway project
railway service                           # Select service
railway status                            # Check project status

# Service configuration
railway service update --root-directory / # Fix root directory
railway variables --service <name>        # List variables
railway variables set KEY=VALUE           # Set variable

# Deployment
railway up                                # Deploy current service
railway up --service <name>               # Deploy specific service

# Monitoring
railway logs --service <name>             # View logs
railway logs --service <name> --follow    # Follow logs
railway logs --service <name> --build     # Build logs
```

## Debug Workflow

### Step 1: Initial Validation

```bash
# Run debug tools
python3 scripts/railway-mcp-debug.py --verbose
bash scripts/railway-debug.sh --verbose

# Review output for critical issues
```

### Step 2: Fix Configuration Issues

```bash
# Fix competing build files
git mv Dockerfile Dockerfile.disabled
git mv railway.toml railway.toml.disabled

# Validate railpack files
jq empty railpack.json
jq empty railpack-backend.json
jq empty railpack-ml.json
```

### Step 3: Update Railway Dashboard

For EACH service:
1. Navigate to Railway Dashboard → Service Settings
2. Set Root Directory: `/` (or blank)
3. Clear Build Command field
4. Clear Start Command field
5. Set Config Path to appropriate railpack file
6. Verify environment variables

### Step 4: Deploy and Monitor

```bash
# Deploy services
railway up --service monkey-coder
railway up --service monkey-coder-backend
railway up --service monkey-coder-ml

# Monitor deployment
railway logs --service monkey-coder --follow

# Check health endpoints
curl https://coder.fastmonkey.au/api/health
curl https://monkey-coder-backend-production.up.railway.app/api/health
```

## MCP Integration

When Python dependencies are installed, the debug tools can leverage MCP framework features:

### MCP Railway Tools

```python
from monkey_coder.mcp.railway_deployment_tool import MCPRailwayTool

# Initialize tool
railway_tool = MCPRailwayTool(project_root)

# Validate deployment
results = railway_tool.validate_railway_deployment(verbose=True)

# Get recommendations
recommendations = railway_tool.get_railway_deployment_recommendations()

# Monitor deployment
status = railway_tool.monitor_railway_deployment(check_health=True)
```

### Available MCP Tools

1. **validate_railway_deployment**: Comprehensive validation
2. **fix_railway_deployment_issues**: Automated issue fixing
3. **monitor_railway_deployment**: Real-time monitoring
4. **get_railway_deployment_recommendations**: Best practice recommendations

## Troubleshooting

### Debug Tool Not Working

**Symptom**: Debug script fails or shows errors

**Solutions**:
1. Check Python version: `python3 --version` (requires 3.12+)
2. Check Node.js version: `node --version` (requires 20+)
3. Install Railway CLI: `npm install -g @railway/cli`
4. Run from project root directory

### Railway CLI Not Authenticating

**Symptom**: "Not authenticated" errors

**Solutions**:
1. Run `railway login`
2. Run `railway link` to link project
3. Verify token: `railway whoami`

### MCP Features Not Available

**Symptom**: "MCP framework not available" warnings

**Solutions**:
1. This is normal if Python dependencies aren't installed
2. Debug tools work without MCP (reduced features)
3. To enable MCP: Install requirements.txt

## Documentation References

- **RAILWAY_DEPLOYMENT.md**: Authoritative deployment guide
- **RAILWAY_CRISIS_RESOLUTION.md**: Emergency fix instructions
- **CLAUDE.md**: Railway deployment section with cheat sheet
- **scripts/fix-railway-services.sh**: Interactive fix wizard
- **docs/deployment/railway-services-setup.md**: MCP services setup

## Support

For deployment issues:
1. Run debug tools and review output
2. Check Railway logs: `railway logs --service <name>`
3. Verify configuration against this guide
4. Consult RAILWAY_DEPLOYMENT.md for detailed instructions
5. Review past PRs for similar issues

---

**Last Updated**: 2025-01-16  
**Version**: 1.0  
**Maintainer**: Monkey Coder DevOps Team
