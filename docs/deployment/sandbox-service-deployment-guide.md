# Sandbox Service Deployment Guide

## Executive Summary

The `services/sandbox` Dockerfile is designed for **optional cloud-based code execution and browser automation**. It does **NOT** need its own Railway deployment for typical installations.

## Architecture Overview

### Two Separate Sandbox Implementations

The Monkey Coder project has **two independent sandboxing systems**:

#### 1. CLI Local Docker Execution (Primary)
- **Location**: `packages/cli/src/sandbox/`
- **Technology**: Direct Docker integration via `dockerode`
- **Execution Modes**: 
  - `none` - Direct process spawn (development only)
  - `spawn` - Isolated process execution (default)
  - `docker` - Full Docker containerization (maximum security)
- **Fallback Strategy**: Automatic fallback from `docker` → `spawn` if Docker unavailable
- **Dependencies**: None (completely self-contained)
- **Use Case**: Command-line interface, local development, CI/CD pipelines

#### 2. Remote Sandbox Service (Optional)
- **Location**: `services/sandbox/`
- **Technology**: FastAPI + E2B + BrowserBase + Playwright
- **Features**:
  - E2B code execution sandboxes
  - BrowserBase browser automation
  - Centralized resource monitoring
  - Multi-tenant execution management
- **Dependencies**: Requires E2B and BrowserBase API keys
- **Use Case**: Web applications, cloud-based execution, enterprise deployments

### Key Architectural Decision

**The CLI does NOT use the remote sandbox service.** This was confirmed by:
1. Zero imports of `SandboxClient` in CLI TypeScript code
2. CLI implements its own `SandboxExecutor` with local Docker
3. No environment variable references to `SANDBOX_SERVICE_URL` in CLI

## When to Deploy services/sandbox to Railway

### ✅ Deploy When:

1. **Web Application Execution Requirements**
   - You need browser automation via BrowserBase
   - You require remote code execution from web clients
   - You want centralized sandbox resource management

2. **Multi-User Cloud Platform**
   - Offering code execution as a service
   - Multiple users sharing sandbox infrastructure
   - Need resource quotas and monitoring per user

3. **No Local Docker Available**
   - Backend API service runs in Railway without Docker-in-Docker
   - Cannot use local Docker for security reasons
   - Prefer managed sandbox infrastructure

### ❌ Do NOT Deploy When:

1. **CLI-Only Deployment**
   - Users only use `monkey` CLI commands
   - Local Docker is available and preferred
   - No web interface for code execution

2. **Simple Backend API**
   - API doesn't execute untrusted code
   - No browser automation requirements
   - Resource constraints (sandbox service requires separate compute)

3. **Cost Sensitivity**
   - Each Railway service incurs separate costs
   - Local Docker execution is more cost-effective
   - Limited usage doesn't justify standalone service

## Railway Deployment Configuration

If you decide the sandbox service is needed, here's the configuration:

### Create railpack.json

**File**: `services/sandbox/railpack.json`

```json
{
  "$schema": "https://schema.railpack.com",
  "version": "1",
  "metadata": {
    "name": "monkey-coder-sandbox",
    "description": "Isolated sandbox execution service with E2B and BrowserBase"
  },
  "build": {
    "provider": "docker",
    "dockerfile": "Dockerfile",
    "buildArgs": {
      "PORT": "$PORT"
    }
  },
  "deploy": {
    "startCommand": "/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf",
    "healthCheckPath": "/health",
    "healthCheckTimeout": 120,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3,
    "variables": {
      "SANDBOX_MODE": "1",
      "PYTHONUNBUFFERED": "1",
      "LOG_LEVEL": "info"
    }
  }
}
```

### Required Environment Variables

Set these in Railway dashboard for the sandbox service:

```bash
# Security
SANDBOX_TOKEN_SECRET=<generate-secure-random-secret>

# CORS Configuration
SANDBOX_ALLOW_ORIGINS=https://your-frontend.railway.app
SANDBOX_ALLOW_ORIGIN_REGEX=^https?://([a-z0-9-]+\.)*railway\.app$

# E2B Integration (optional - for code execution)
E2B_API_KEY=<your-e2b-api-key>

# BrowserBase Integration (optional - for browser automation)
BROWSERBASE_API_KEY=<your-browserbase-api-key>
BROWSERBASE_PROJECT_ID=<your-browserbase-project-id>

# Resource Limits
SANDBOX_MAX_MEMORY_MB=512
SANDBOX_MAX_CPU_PERCENT=50.0
SANDBOX_MAX_DISK_MB=1024
SANDBOX_MAX_NETWORK_MBPS=10.0
```

### Connect Backend Service to Sandbox

If deploying sandbox service, update backend's railpack.json environment:

```json
{
  "deploy": {
    "variables": {
      "SANDBOX_SERVICE_URL": "http://${{monkey-coder-sandbox.RAILWAY_PRIVATE_DOMAIN}}",
      "SANDBOX_TOKEN_SECRET": "${{monkey-coder-sandbox.SANDBOX_TOKEN_SECRET}}"
    }
  }
}
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Monkey Coder Platform                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐              ┌────────────────────┐   │
│  │   CLI Package   │              │  Backend Service   │   │
│  │   (TypeScript)  │              │     (Python)       │   │
│  └────────┬────────┘              └─────────┬──────────┘   │
│           │                                 │              │
│           │ Local Docker                    │              │
│           │ (dockerode)                     │              │
│           │                                 │              │
│           ▼                                 ▼              │
│  ┌─────────────────┐              ┌────────────────────┐   │
│  │ SandboxExecutor │              │  SandboxClient     │   │
│  │  - docker mode  │              │  (HTTP client)     │   │
│  │  - spawn mode   │              └─────────┬──────────┘   │
│  │  - none mode    │                        │              │
│  └─────────────────┘                        │              │
│           │                                 │              │
│           │                                 │ Optional     │
│           │                                 ▼              │
│           │                        ┌────────────────────┐  │
│           │                        │ Sandbox Service    │  │
│           │                        │ (FastAPI)          │  │
│           │                        │  - E2B integration │  │
│           │                        │  - BrowserBase     │  │
│           │                        │  - Playwright      │  │
│           │                        └────────────────────┘  │
│           │                                                │
│           └─────────────── Independent ───────────────────┘
```

## Current Railway Deployment Status

### Existing Services

The project currently deploys **3 services** to Railway:

1. **Frontend** (`services/frontend/railpack.json`)
   - Next.js web application
   - Static site serving
   - Health check: `/`

2. **Backend** (`services/backend/railpack.json`)
   - Python FastAPI orchestration
   - AI model integration
   - Health check: `/api/health`

3. **ML Service** (`services/ml/railpack.json`)
   - Machine learning inference
   - Model serving
   - Health check: `/api/health`

### Sandbox Service Status

- **Configuration**: Has Dockerfile, NO railpack.json
- **Railway Deployment**: ❌ NOT deployed
- **Required**: ❌ NO (optional enhancement)

## Recommendation

### For Most Deployments: Do NOT Deploy

**Rationale:**
1. CLI provides complete sandboxing via local Docker
2. Backend API doesn't require remote sandbox for core functionality
3. Additional Railway service increases costs
4. E2B/BrowserBase require separate API subscriptions
5. Local Docker execution is more performant

### When to Consider Deployment

Deploy the sandbox service ONLY if you need:
- Browser automation for web users
- Cloud-based code execution API
- Centralized multi-tenant sandbox management
- Backend runs without local Docker access

## Testing Sandbox Integration

### Test CLI Local Docker (Primary Path)

```bash
# Check Docker availability
docker ps

# Test CLI sandbox modes
cd packages/cli

# Test spawn mode (default)
yarn build
node dist/cli.js agent --task "echo Hello World"

# Test docker mode
node dist/cli.js agent --docker --task "echo Hello Docker"

# Should see: Automatic fallback if Docker unavailable
```

### Test Backend Sandbox Client (Optional)

```bash
# Only if deploying sandbox service

# Start sandbox service locally
cd services/sandbox
python -m pip install -r requirements.txt
python -m sandbox.main

# In another terminal, test backend integration
cd packages/core
python -c "
from monkey_coder.sandbox_client import SandboxClient
import asyncio

async def test():
    client = SandboxClient()
    health = await client.health_check()
    print(f'Sandbox service healthy: {health}')

asyncio.run(test())
"
```

## Migration Path (If Needed)

If you later decide to deploy the sandbox service:

1. **Create railpack.json** in `services/sandbox/`
2. **Add Railway service** via Railway dashboard
3. **Configure environment variables** (listed above)
4. **Update backend service** to reference `SANDBOX_SERVICE_URL`
5. **Test health endpoint**: `https://sandbox-service.railway.app/health`
6. **Monitor resource usage** via `/sandbox/metrics`

## Security Considerations

### Local Docker (CLI)
- ✅ Runs in user's environment
- ✅ User controls Docker daemon security
- ✅ No network exposure
- ⚠️ Requires Docker installation

### Remote Sandbox Service
- ✅ Centralized security policies
- ✅ Network isolation via Railway
- ✅ Resource quotas enforced
- ⚠️ Requires proper authentication
- ⚠️ Token management complexity
- ⚠️ Network latency overhead

## Conclusion

**The Dockerfile in `services/sandbox/` is for an optional cloud-based execution service.** 

- ✅ **CLI users**: Already have complete sandboxing via local Docker
- ✅ **Backend API**: Functions without sandbox service
- ⚠️ **Deploy separately ONLY if**: You need browser automation or cloud-based code execution as a service

For most deployments, the existing 3 Railway services (frontend, backend, ml) are sufficient. The sandbox service is an **optional enhancement** for specific use cases, not a core requirement.

## Related Documentation

- [Railway Architecture](./railway-architecture.md)
- [Railway Service Configuration](../../RAILWAY_SERVICE_CONFIG.md)
- [CLI Sandbox Execution](../../packages/cli/SANDBOX_EXECUTION.md)
- [Sandbox Implementation Summary](../../IMPLEMENTATION_SUMMARY_SANDBOX.md)
