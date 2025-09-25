# Deployment Guide

## Railway Deployment

Monkey Coder is configured for single-service deployment on Railway using `railpack.json`.

### Architecture

```
┌─────────────────┐         ┌─────────────────────────┐         ┌──────────────┐
│                 │         │                         │         │              │
│  CLI/SDK Users  │────────▶│    Railway Service     │────────▶│ AI Providers │
│                 │         │  (Python + Next.js)    │         │              │
└─────────────────┘         └─────────────────────────┘         └──────────────┘
```

### Railway Configuration (`railpack.json`)

The project uses a simplified deployment configuration with runtime frontend building:

```json
{
  "$schema": "https://schema.railpack.com",
  "version": "1",
  "metadata": {
    "name": "monkey-coder",
    "description": "AI-powered code generation and analysis platform"
  },
  "build": {
    "provider": "python",
    "packages": {
      "python": "3.12.11",
      "node": "20"
    },
    "steps": {
      "install": {
        "commands": [
          "python -m venv /app/.venv",
          "/app/.venv/bin/pip install --upgrade pip setuptools wheel",
          "/app/.venv/bin/pip install -r requirements.txt",
          "corepack enable && corepack prepare yarn@4.9.2 --activate",
          "yarn install --frozen-lockfile"
        ]
      },
      "build": {
        "commands": [
          "yarn workspace @monkey-coder/web export"
        ]
      }
    },
    "env": {
      "NODE_ENV": "production",
      "PYTHON_ENV": "production"
    }
  },
  "deploy": {
    "startCommand": "/app/.venv/bin/python /app/run_server.py",
    "healthCheckPath": "/health",
    "healthCheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3,
    "env": {
      "NODE_ENV": "production"
    }
  }
}
```

**Note**: Frontend building is handled automatically at runtime by `run_server.py` which:
- Checks if `packages/web/out` directory exists
- Installs Yarn 4.9.2 and dependencies if needed
- Builds the Next.js frontend using `yarn workspace @monkey-coder/web export`
- Continues with server startup even if frontend build fails (with warnings)

### Pre-Deployment Validation

Before deploying, run the comprehensive validation script to ensure Railway deployment best practices:

```bash
# Validate Railway deployment readiness
./scripts/railway-cheatsheet-validation.sh

# Or use yarn script
yarn railway:validate
```

This validation checks:
- ✅ Single build system (no competing configurations)
- ✅ Health check endpoint configuration
- ✅ Proper PORT environment variable usage
- ✅ Host binding to 0.0.0.0
- ✅ Railway reference variable support
- ✅ JSON syntax validation

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
- Python 3.13
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

### Common Issues

1. **Port Binding**: Ensure binding to `0.0.0.0:$PORT`
2. **Build Failures**: Check Node.js/Python versions match requirements
3. **Module Not Found**: Run `yarn install --immutable`
4. **Constraint Violations**: Run `yarn constraints --fix`

### Debug Commands

```bash
# Check Railway logs
railway logs

# Test locally with Railway env
railway run yarn dev

# Validate railpack.json
cat railpack.json | jq '.'
```

## Security

- All API keys stored as Railway environment variables
- HTTPS enforced for all production traffic
- Automated security scanning via `yarn npm audit`
- Sentry integration for error tracking