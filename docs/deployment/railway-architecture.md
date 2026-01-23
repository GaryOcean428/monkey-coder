# Railway Deployment Architecture

## Overview

Monkey Coder uses **Railway's railpack system** for deployment, not traditional Docker. This document clarifies the deployment architecture and resolves confusion about Docker usage.

## Railway Deployment Model

### How Railway Works

Railway uses a multi-layer approach:
1. **Configuration**: `railpack.json` defines the build and deployment
2. **Internal Containerization**: Railway automatically creates Docker containers from railpack config
3. **No Dockerfile Required**: Railway handles containerization internally

```text
Developer writes: railpack.json
        ↓
Railway reads: railpack.json configuration  
        ↓
Railway creates: Internal Docker container
        ↓
Railway deploys: Containerized application
```

### Why `.dockerignore` Exists

Even though there's no root `Dockerfile`, Railway still uses Docker internally. The `.dockerignore` file:
- Controls what files are copied into Railway's internal Docker build
- Excludes build artifacts like `.venv/`, `node_modules/`, etc.
- Is **required** for Railway deployments

## Current Configuration

### Primary Build Config: `railpack.json`

```json
{
  "$schema": "https://schema.railpack.com",
  "version": "1",
  "build": {
    "provider": "python",
    "packages": {
      "python": "3.12.11"
    }
  },
  "deploy": {
    "startCommand": "/app/.venv/bin/python /app/run_server.py",
    "healthCheckPath": "/health"
  }
}
```

### What's NOT Used for Deployment

- ❌ Root `Dockerfile` (doesn't exist)
- ❌ `railway.toml` (not present)
- ❌ `nixpacks.toml` (not present)
- ❌ Docker Compose files

### What IS Used for Deployment

- ✅ `railpack.json` (primary build configuration)
- ✅ `.dockerignore` (controls Railway's internal Docker build)
- ✅ `requirements.txt` (Python dependencies)
- ✅ `run_server.py` (application entrypoint)

## Docker References in Repository

### Active Docker Usage

1. **`services/sandbox/Dockerfile`**
   - **Purpose**: Optional containerized sandbox execution service
   - **Status**: Separate optional service, not main deployment
   - **Usage**: E2B/BrowserBase integration for code execution and browser automation
   - **Railway Config**: `services/sandbox/railpack.json` (uses Dockerfile)
   - **Required**: ⚠️ NO - Optional enhancement for cloud-based execution
   - **Alternative**: CLI has built-in local Docker sandbox via `dockerode`
   - **Deploy When**: 
     - Need browser automation for web users
     - Require cloud-based code execution API
     - Backend needs remote sandbox without local Docker
   - **Deploy Guide**: See `docs/deployment/sandbox-service-deployment-guide.md`

### Legacy/Development Docker Scripts

1. **`scripts/build-docker.sh`**
   - **Purpose**: Local Docker testing (legacy)
   - **Status**: Not used for Railway deployment
   - **Alternative**: Use Railway CLI for testing

2. **`scripts/verify-build.sh`**
   - **Purpose**: Build verification including Docker checks
   - **Status**: Docker portions are optional
   - **Note**: Checks Docker availability but doesn't require it

## Deployment Workflow

### Railway Deployment (Production)

```bash
# 1. Validate configuration
./scripts/railway-build-validation.sh

# 2. Deploy to Railway
railway deploy
```

### Local Development

```bash
# Option 1: Direct Python (recommended)
python run_server.py

# Option 2: Railway CLI (tests Railway environment)
railway run python run_server.py
```

### Testing Railway Configuration Locally

```bash
# Simulate Railway build environment
railway run --service monkey-coder-api python run_server.py
```

## Common Misconceptions

### ❌ Misconception: "This project uses Docker"
**Reality**: This project uses Railway's railpack system, which internally uses Docker but doesn't require a Dockerfile.

### ❌ Misconception: "Need to create a Dockerfile"
**Reality**: Railway automatically creates containers from `railpack.json`. Adding a Dockerfile would override railpack and cause conflicts.

### ❌ Misconception: ".dockerignore is unnecessary"
**Reality**: Railway's internal Docker build process uses `.dockerignore` to exclude files, even without a root Dockerfile.

### ❌ Misconception: "Docker scripts are required"
**Reality**: Docker scripts in `scripts/` are legacy/testing tools, not required for deployment.

## Troubleshooting

### Build Failures

If you see "competing build configurations":
1. Ensure only `railpack.json` exists (no `Dockerfile`, `railway.toml`, etc. in root)
2. Run: `./scripts/railway-build-validation.sh`

### "Command not found" Errors

Check that `railpack.json` uses the correct virtual environment:
```json
{
  "deploy": {
    "startCommand": "/app/.venv/bin/python /app/run_server.py"
  }
}
```

### Port Binding Issues

Ensure server binds to `0.0.0.0` and uses `process.env.PORT`:
- ✅ `host="0.0.0.0"`
- ✅ `port=int(os.getenv("PORT", 8000))`

## Summary

- **Deployment Method**: Railway railpack (not Docker)
- **Configuration File**: `railpack.json` (not Dockerfile)
- **Container Creation**: Handled automatically by Railway
- **Docker Scripts**: Legacy/testing tools, not required for deployment
- **`.dockerignore`**: Required for Railway's internal build process
