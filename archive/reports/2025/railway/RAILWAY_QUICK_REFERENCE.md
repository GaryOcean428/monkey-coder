# Railway Deployment Quick Reference

## ✅ Validation Status

This repository follows all Railway deployment best practices from the AI Agent Cheatsheet:

- **Build System**: Single railpack.json configuration (no conflicts)
- **Health Checks**: `/health` endpoint properly configured and implemented
- **Port Binding**: Uses `process.env.PORT` with 0.0.0.0 host binding
- **Railway Integration**: Proper Railway reference variables

## 🚀 Quick Commands

```bash
# Validate Railway deployment readiness
./scripts/railway-cheatsheet-validation.sh

# Test railpack.json syntax and structure
./scripts/railway-build-validation.sh

# Deploy to Railway (if Railway CLI is installed)
railway up
```

## 📋 railpack.json Structure

The project uses the recommended Railway deployment structure:

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
      "install": [...],
      "build": [...]
    }
  },
  "deploy": {
    "startCommand": "/app/.venv/bin/python /app/run_server.py",
    "healthCheckPath": "/health",
    "healthCheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

## 🔍 Key Implementation Details

- **Health Endpoint**: Implemented in `packages/core/monkey_coder/app/main.py` at `/health` and `/healthz`
- **Server Configuration**: `run_server.py` properly binds to `0.0.0.0:$PORT`
- **Frontend Build**: Next.js static export integrated in build process
- **Environment**: Production-ready with proper error handling

## 🎯 Deployment Readiness Checklist

- [x] Single build configuration (railpack.json only)
- [x] Health check endpoint implemented and configured
- [x] PORT environment variable usage
- [x] Host binding to 0.0.0.0
- [x] Railway reference variables support
- [x] No hardcoded ports in start commands
- [x] JSON syntax validation
- [x] Comprehensive error handling

## 🛠️ Troubleshooting

If deployment fails:

1. Run validation: `./scripts/railway-cheatsheet-validation.sh`
2. Check Railway logs for specific error messages
3. Verify environment variables are set correctly
4. Ensure Railway service has sufficient resources

## 📚 References

- [Railway Documentation](https://docs.railway.app/)
- [Railpack Configuration](https://railpack.com/)
- Original cheatsheet implementation in this repository