# Deployment Guide

> 📖 **For Railway deployment**, see [../RAILWAY_DEPLOYMENT.md](../RAILWAY_DEPLOYMENT.md) - the authoritative guide with complete Railway configuration, environment variables, and troubleshooting.

## Deployment Overview

Monkey Coder can be deployed in various environments with different architectures:

### Railway Deployment (Recommended)

Monkey Coder supports **two deployment architectures** on Railway:
1. **Single-Service Deployment** (Simplified): Python backend + Next.js frontend in one service
2. **Multi-Service Deployment** (Production): Separate backend, frontend, and ML services

Choose based on your needs:
- **Single-service**: Easier setup, lower cost, suitable for development/testing
- **Multi-service**: Better scalability, independent scaling, production-ready

**Documentation**:
- [RAILWAY_DEPLOYMENT.md](../RAILWAY_DEPLOYMENT.md) - Authoritative configuration guide
- [deployment/railway-optimization.md](deployment/railway-optimization.md) - Performance monitoring and optimization
- [deployment/railway-architecture.md](deployment/railway-architecture.md) - Architecture diagrams
- [deployment/railway-services-setup.md](deployment/railway-services-setup.md) - Service setup details

### Architecture Options

#### Option 1: Single-Service (Simplified)
```text
┌─────────────────┐         ┌─────────────────────────┐         ┌──────────────┐
│                 │         │                         │         │              │
│  CLI/SDK Users  │────────▶│    Railway Service     │────────▶│ AI Providers │
│                 │         │  (Python + Next.js)    │         │              │
└─────────────────┘         └─────────────────────────┘         └──────────────┘
```
**Config**: Root `railpack.json`

#### Option 2: Multi-Service (Production)
```text
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│             │     │              │     │             │     │              │
│ CLI/SDK/Web │────▶│   Frontend   │────▶│   Backend   │────▶│ AI Providers │
│    Users    │     │  (Next.js)   │     │  (FastAPI)  │     │              │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
                                              │
                                              ▼
                                         ┌─────────────┐
                                         │  ML Service │
                                         │  (Python)   │
                                         └─────────────┘
```
**Config**: Separate `services/*/railpack.json` files

> **Recommended**: Start with single-service for development, migrate to multi-service for production scaling.

### Railway Configuration

#### Single-Service Configuration (Root `railpack.json`)

The root `railpack.json` provides a simplified deployment with combined backend and frontend:

```json
{
  "$schema": "https://schema.railpack.com",
  "version": "1",
  "metadata": {
    "name": "monkey-coder-frontend",
    "description": "Next.js frontend - deploys from repo root"
  },
  "build": {
    "provider": "node",
    "packages": {
      "node": "20"
    },
    "cache": {
      "paths": [
        "node_modules",
        ".yarn/cache",
        "packages/web/.next",
        "packages/web/out"
      ]
    }
  },
  "deploy": {
    "startCommand": "yarn workspace @monkey-coder/web start --hostname 0.0.0.0 --port $PORT",
    "healthCheckPath": "/api/health",
    "healthCheckTimeout": 300
  }
}
```

**Key Points**:
- Uses Node.js provider for Next.js frontend
- Leverages Railway's cache for faster rebuilds
- Binds to `0.0.0.0` (required for Railway)
- Uses `$PORT` environment variable (auto-injected by Railway)

#### Multi-Service Configuration (Production)

For production scaling, use separate service configurations:

**Backend Service** (`services/backend/railpack.json`):
```json
{
  "metadata": {
    "name": "monkey-coder-backend"
  },
  "build": {
    "provider": "python",
    "packages": {
      "python": "3.12"
    }
  },
  "deploy": {
    "startCommand": "/app/.venv/bin/python -m uvicorn monkey_coder.app.main:app --host 0.0.0.0 --port $PORT",
    "healthCheckPath": "/api/health",
    "env": {
      "ML_SERVICE_URL": "http://${{monkey-coder-ml.RAILWAY_PRIVATE_DOMAIN}}"
    }
  }
}
```

**Frontend Service** (`railpack.json`):
```json
{
  "metadata": {
    "name": "monkey-coder-frontend"
  },
  "build": {
    "provider": "node"
  },
  "deploy": {
    "startCommand": "yarn workspace @monkey-coder/web start --hostname 0.0.0.0 --port $PORT",
    "healthCheckPath": "/api/health",
    "env": {
      "NEXT_PUBLIC_API_URL": "https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}"
    }
  }
}
```

**ML Service** (`services/ml/railpack.json`):
```json
{
  "metadata": {
    "name": "monkey-coder-ml"
  },
  "build": {
    "provider": "python",
    "packages": {
      "python": "3.12"
    }
  },
  "deploy": {
    "startCommand": "/app/.venv/bin/python -m uvicorn monkey_coder.ml.main:app --host 0.0.0.0 --port $PORT",
    "healthCheckPath": "/health"
  }
}
```

**Railway Best Practices**:
- ✅ **Use Railway Reference Variables**: `${{service.RAILWAY_PUBLIC_DOMAIN}}` for service-to-service communication
- ✅ **Never Hardcode Ports**: Always use `$PORT` environment variable
- ✅ **Bind to 0.0.0.0**: Not `localhost` or `127.0.0.1`
- ✅ **Health Check Endpoints**: Required for Railway health monitoring
- ✅ **Private vs Public Domains**: Use `RAILWAY_PRIVATE_DOMAIN` for internal communication (faster, more secure)

> See [docs/deployment/railway-services-separation.md](./deployment/railway-services-separation.md) for complete multi-service setup guide.

### Railway Deployment Best Practices

**Critical Requirements** (Based on [Railway Official Documentation](https://docs.railway.app/)):

1. **PORT Binding** ([Railway Docs: PORT Variable](https://docs.railway.app/guides/public-networking#port-variable))
   - Railway injects `$PORT` environment variable
   - Your app MUST bind to `0.0.0.0:$PORT`
   - ❌ Never hardcode ports
   - ❌ Never bind to `localhost` or `127.0.0.1`

2. **Health Checks** ([Railway Docs: Health Checks](https://docs.railway.app/reference/healthchecks))
   - Required for production deployments
   - Must return HTTP 200 status
   - Configure `healthCheckPath` in railpack.json
   - Default timeout: 300 seconds

3. **Service References** ([Railway Docs: Reference Variables](https://docs.railway.app/guides/variables#reference-variables))
   - Use `${{serviceName.RAILWAY_PUBLIC_DOMAIN}}` for external access
   - Use `${{serviceName.RAILWAY_PRIVATE_DOMAIN}}` for internal service-to-service communication
   - ❌ Never reference `${{serviceName.PORT}}` (not available)

4. **Build Configuration Priority** ([Railway Docs: Build Configurations](https://docs.railway.app/guides/builds))
   - Dockerfile (if present) - highest priority
   - railpack.json (recommended for this project)
   - railway.json/railway.toml
   - Nixpacks auto-detection - lowest priority
   - ⚠️ Remove competing configs to avoid build conflicts

5. **Virtual Environment Paths** (Python-specific)
   - Railway uses `/app` as working directory
   - Virtual environments: `/app/.venv/bin/python`
   - Ensure startCommand uses full paths

### Pre-Deployment Validation

Before deploying, run the comprehensive validation script:

```bash
# Validate Railway deployment readiness
./scripts/railway-cheatsheet-validation.sh

# Or use yarn script
yarn railway:validate
```

This validation checks:
- ✅ Single build system (no competing configurations like Dockerfile + railpack.json)
- ✅ Health check endpoint configuration and response
- ✅ Proper PORT environment variable usage (not hardcoded)
- ✅ Host binding to 0.0.0.0 (not localhost)
- ✅ Railway reference variable syntax
- ✅ JSON syntax validation for railpack.json files

### Deployment Steps

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy to Railway"
   git push origin main
   ```

2. **Deploy via Railway CLI**:
   ```bash
   railway up
   ```

3. **Or use GitHub Integration**:
   - Connect your GitHub repo to Railway
   - Automatic deployments on push to main

### Environment Variables

Set these in Railway dashboard:

```bash
# Required
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GOOGLE_API_KEY=your_key

# Optional
SENTRY_DSN=your_sentry_dsn
LOG_LEVEL=INFO
JSON_LOGS=true
PERFORMANCE_LOGS=true
```

### Health Monitoring

The service exposes health endpoints:

- `/health` - Basic health check
- `/healthz` - Kubernetes-style health check  
- `/v1/capabilities` - Detailed system capabilities

### Performance Optimizations

- **JSON Structured Logging**: Better log processing in Railway
- **Performance Metrics**: Tracks API call latency
- **Global Yarn Cache**: 30-50% faster builds
- **Hardlinks**: Reduced deployment size

## Local Development

### Prerequisites

- Node.js 20+
- Python 3.12
- Yarn 4.9.2 (via Corepack)

### Setup

```bash
# Enable Yarn
corepack enable
corepack prepare yarn@4.9.2 --activate

# Install dependencies
yarn install

# Verify constraints
yarn constraints

# Build packages
yarn build

# Start backend
cd packages/core
python -m monkey_coder.app.main

# Optional: Start frontend
yarn workspace @monkey-coder/web dev
```

### Testing Production Build Locally

```bash
# Build for production
yarn build
yarn workspace @monkey-coder/web build

# Run with Railway environment
railway run python run_server.py
```

## Continuous Deployment

### GitHub Actions

The project includes automated publishing workflows:

- **Auto-publish on push to main**: Updates npm and PyPI packages
- **Version management**: Automatic version bumping
- **Security scanning**: Automated vulnerability checks

### Package Publishing

Published packages:
- `monkey-coder-cli` (npm)
- `monkey-coder-core` (PyPI)
- `monkey-coder-sdk` (PyPI)

## Troubleshooting

### Common Railway Issues

#### 1. "Application Failed to Respond" / Health Check Failures

**Symptoms**:
- Deployment shows "Crashed" or "Unhealthy"
- Health check timeout errors

**Solutions**:
```bash
# Check if app binds to correct host/port
grep -r "0\.0\.0\.0" packages/
grep -r "process.env.PORT\|os.getenv.*PORT" packages/

# Verify health endpoint exists
curl http://localhost:8000/health  # Local test

# Check Railway logs for binding errors
railway logs --service monkey-coder-backend
```

**Common Causes**:
- ❌ Binding to `localhost` instead of `0.0.0.0`
- ❌ Hardcoded port instead of using `$PORT`
- ❌ Health endpoint not returning 200 status
- ❌ Application crashes before health check completes

#### 2. Build System Conflicts

**Symptoms**:
- "Nixpacks build failed"
- "Multiple build configurations detected"
- "ERROR: failed to exec pid1"

**Solutions**:
```bash
# Check for competing configurations
ls -la | grep -E "(Dockerfile|railway\.toml|nixpacks\.toml|railpack\.json)"

# Should only see railpack.json (and service-specific ones)
# Remove any Dockerfile, railway.toml, or nixpacks.toml in root

# Validate railpack.json syntax
cat railpack.json | jq '.'
```

**Railway Build Priority** (highest to lowest):
1. Dockerfile ← Remove if using railpack
2. railpack.json ← Use this
3. railway.json/railway.toml ← Remove if using railpack
4. Nixpacks auto-detection ← Fallback

#### 3. Service Reference Errors

**Symptoms**:
- "serviceA.PORT does not resolve"
- "Variable reference failed"
- Backend URL returns 404

**Solutions**:
```bash
# ❌ WRONG - Cannot reference PORT
BACKEND_URL=${{backend.PORT}}

# ✅ CORRECT - Use PUBLIC_DOMAIN
BACKEND_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}

# ✅ CORRECT - Use PRIVATE_DOMAIN for internal calls
INTERNAL_API=http://${{backend.RAILWAY_PRIVATE_DOMAIN}}
```

#### 4. Dependency Installation Failures

**Solutions**:
```bash
# Python: Ensure requirements.txt is up to date
pip freeze > requirements.txt

# Node: Use frozen lockfile
yarn install --frozen-lockfile

# Check for drift (Python deps)
./scripts/check_python_deps_sync.sh

# Fix workspace constraints (Node)
yarn constraints --fix
```

#### 5. Performance Issues / Slow Builds

**Solutions**:
```bash
# Enable caching in railpack.json
{
  "build": {
    "cache": {
      "paths": [
        "node_modules",
        ".yarn/cache",
        ".venv"
      ]
    }
  }
}

# Check build times
railway logs --service your-service | grep "Build time"

# Use Railway's cache clearing command
railway run --service your-service railway cache:clear
```

### Debug Commands

```bash
# Check Railway logs with timestamps
railway logs --timestamps

# Test locally with Railway environment
railway run yarn dev
railway run python run_server.py

# Validate railpack.json syntax
cat railpack.json | jq '.' > /dev/null && echo "✅ Valid JSON"

# Check environment variables in Railway
railway run env | grep -E "(PORT|HOST|RAILWAY)"

# Test health endpoint locally
curl -I http://localhost:8000/health

# Check system resource limits
ulimit -a

# Verify build commands work locally
cd packages/web && yarn build
cd packages/core && pip install -r requirements.txt
```

### Getting Help

1. **Railway Logs**: Check deployment logs for specific errors
2. **Validation Script**: Run `./scripts/railway-cheatsheet-validation.sh`
3. **Railway Docs**: [docs.railway.app](https://docs.railway.app/)
4. **Project Issues**: Open an issue with Railway logs attached

## Security

- All API keys stored as Railway environment variables
- HTTPS enforced for all production traffic
- Automated security scanning via `yarn npm audit`
- Sentry integration for error tracking
