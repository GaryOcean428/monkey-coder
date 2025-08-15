# Multi-Service Railway Deployment Guide

This guide documents the implementation of the multi-service deployment strategy for the monkey-coder monorepo on Railway.

## Architecture Overview

The deployment uses Railway's multi-service configuration to separate the Python backend and Next.js frontend into independent services while maintaining inter-service communication.

### Services

1. **Backend Service** (`monkey-coder-api`)
   - Python 3.12 FastAPI application
   - Health check: `/health`
   - Serves API endpoints and static files

2. **Frontend Service** (`monkey-coder-web`)
   - Next.js 15 application
   - Health check: `/api/health`
   - Communicates with backend via Railway reference variables

## Configuration Files

### Root Configuration (`railpack.json`)

```json
{
  "$schema": "https://schema.railpack.com",
  "version": "1",
  "metadata": {
    "name": "monkey-coder-monorepo"
  },
  "services": {
    "backend": {
      "root": "./",
      "build": {
        "provider": "python",
        "packages": { "python": "3.12" },
        "steps": {
          "install": {
            "commands": [
              "pip install -r requirements.txt",
              "cd packages/core && pip install -e ."
            ]
          }
        },
        "secrets": ["RAILWAY_ENVIRONMENT", "PYTHONPATH"]
      },
      "deploy": {
        "startCommand": "python run_server.py",
        "healthCheckPath": "/health",
        "healthCheckTimeout": 300,
        "inputs": [{ "step": "install" }]
      }
    },
    "frontend": {
      "root": "./packages/web",
      "build": {
        "provider": "node",
        "packages": { "node": "20" },
        "steps": {
          "install": {
            "commands": [
              "corepack enable",
              "corepack prepare yarn@stable --activate",
              "cd /app && yarn install --frozen-lockfile"
            ]
          },
          "build": {
            "commands": [
              "cd /app/packages/web && RAILWAY_ENVIRONMENT=production yarn build"
            ]
          }
        },
        "secrets": ["RAILWAY_ENVIRONMENT"]
      },
      "deploy": {
        "startCommand": "yarn start",
        "healthCheckPath": "/api/health",
        "healthCheckTimeout": 300,
        "inputs": [{ "step": "build" }],
        "environment": {
          "NEXT_PUBLIC_API_URL": "https://${{backend.RAILWAY_PUBLIC_DOMAIN}}"
        }
      }
    }
  }
}
```

### Frontend Service Configuration (`packages/web/railpack.json`)

This file provides standalone deployment configuration for the frontend service:

```json
{
  "$schema": "https://schema.railpack.com",
  "version": "1",
  "metadata": {
    "name": "monkey-coder-web"
  },
  "build": {
    "provider": "node",
    "steps": {
      "install": {
        "commands": [
          "corepack enable",
          "corepack prepare yarn@stable --activate",
          "yarn install --frozen-lockfile"
        ]
      },
      "build": {
        "commands": ["yarn build"]
      }
    }
  },
  "deploy": {
    "startCommand": "yarn start",
    "healthCheckPath": "/api/health",
    "healthCheckTimeout": 300,
    "inputs": [{ "step": "build" }]
  }
}
```

## Environment Variable Optimization

The deployment minimizes build-time environment variables to reduce buildkit memory pressure:

### Build-Time Variables (Minimal Set)
- `RAILWAY_ENVIRONMENT` - For build logic branching
- `PYTHONPATH` - For Python module resolution

### Runtime-Only Variables (Not Exposed to BuildKit)
- AI Provider API Keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.)
- Authentication secrets (`JWT_SECRET_KEY`)
- Database credentials (`DATABASE_URL`, `REDIS_URL`)
- Monitoring keys (`SENTRY_DSN`)

## Inter-Service Communication

Services communicate using Railway's reference variables:

```bash
# Frontend to Backend API calls
NEXT_PUBLIC_API_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}
```

This ensures automatic service discovery and eliminates hardcoded URLs.

## Health Check Endpoints

### Backend Health Check (`/health`)
The Python FastAPI server provides a health endpoint that checks:
- Service status
- Database connectivity
- AI provider availability

### Frontend Health Check (`/api/health`)
The Next.js application provides a health endpoint that returns:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "service": "monkey-coder-web",
  "version": "0.1.0",
  "environment": "production"
}
```

## Deployment Process

### Step 1: Repository Setup
1. Ensure all dependencies are installed: `yarn install`
2. Build the Python core package: `cd packages/core && pip install -e .`
3. Validate configuration: `./scripts/validate-deployment.sh`

### Step 2: Railway Service Creation
1. Create backend service pointing to repository root
2. Create frontend service pointing to `packages/web/`
3. Set environment variables for each service

### Step 3: Environment Configuration

#### Backend Service Variables
```bash
# Required
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
JWT_SECRET_KEY=...

# Optional
GROQ_API_KEY=gsk_...
SENTRY_DSN=https://...
LOG_LEVEL=INFO
```

#### Frontend Service Variables
```bash
# Automatically configured by Railway
NEXT_PUBLIC_API_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}

# Optional
NEXT_PUBLIC_ENVIRONMENT=production
```

### Step 4: Deployment Validation
Run the validation script to ensure readiness:
```bash
./scripts/validate-deployment.sh
```

## Build Optimization Features

1. **Explicit Secrets Management**: Only essential variables exposed to build context
2. **Minimal Build Dependencies**: Separate build-time vs runtime requirements
3. **Cache Optimization**: Proper layer caching for both Python and Node.js builds
4. **Memory Pressure Reduction**: Eliminated 70+ environment variable overhead

## Monitoring and Troubleshooting

### Logs
- Backend logs: JSON structured with Sentry integration
- Frontend logs: Next.js standard output
- Health checks: Automatic Railway monitoring

### Common Issues
1. **Build Failures**: Check build logs for dependency issues
2. **Health Check Failures**: Verify service startup and port binding
3. **Inter-Service Communication**: Ensure Railway reference variables are set

### Debugging Commands
```bash
# Validate configuration
./scripts/validate-deployment.sh

# Check environment variables
./scripts/filter_build_vars.sh

# Test local builds
cd packages/web && RAILWAY_ENVIRONMENT=production yarn build
python -c "from packages.core.monkey_coder.core import orchestrator"
```

## Performance Metrics

### Build Performance
- Reduced build environment variables from 70+ to <10
- Eliminated buildkit solver crashes
- Improved build cache utilization

### Runtime Performance
- Independent service scaling
- Optimized resource allocation
- Health check monitoring

## Migration from Unified Deployment

For projects migrating from the unified deployment (`run_unified.js`):

1. The unified deployment continues to work for local development
2. Railway deployment uses multi-service architecture
3. Environment detection automatically selects the correct mode
4. No breaking changes to existing functionality

## Validation Tools

The repository includes comprehensive validation tools:

- `scripts/validate-deployment.sh` - Full deployment readiness check
- `scripts/filter_build_vars.sh` - Environment variable audit
- Health check endpoints for monitoring
- JSON schema validation for configurations

## Support

For deployment issues:
1. Run validation scripts
2. Check Railway logs
3. Verify environment variables
4. Test health endpoints

This architecture provides a robust, scalable deployment strategy that eliminates the buildkit conflicts while maintaining all existing functionality.