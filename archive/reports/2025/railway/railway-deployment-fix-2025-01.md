# Railway Deployment Fix - Python 3.12 Standardization

## Date: January 15, 2025

## Issue Summary

The Monkey Coder service on Railway experienced deployment failures due to two critical issues:

1. **Python Version Incompatibility**: Railway's update to Python 3.13 broke compatibility with PyTorch 2.3.0, which lacks Python 3.13 wheels. We standardized on Python 3.12 for better compatibility and stability.

2. **Code Quality**: Initial reports indicated an IndentationError in run_server.py at line 423, though this was resolved in the refactored version.

## Resolution Applied

### 1. Python Version Pinning

**File: `railpack.json`**
- Standardized Python version to `3.12.11` for Railway compatibility
- Updated cache paths to `/app/venv/lib/python3.12/site-packages`

```json
"packages": {
  "python": "3.12",
  "node": "20"
}
```

### 2. PyTorch Dependency Update

**File: `requirements.txt`**
- Updated PyTorch from `2.3.0` to `2.8.0+cpu` for Python 3.12 compatibility
- Added explicit CPU index URL for PyTorch: `--extra-index-url https://download.pytorch.org/whl/cpu`

```txt
# PyTorch CPU index for deployment compatibility (Python 3.12 support)
--extra-index-url https://download.pytorch.org/whl/cpu
torch==2.8.0+cpu
```

### 3. Enhanced Server Runner

**File: `run_server.py`**
- Completely refactored for better error handling and organization
- Added configuration management via `ServerConfig` class
- Implemented robust frontend build management with fallback strategies
- Added signal handling for graceful shutdowns
- Improved logging and system information collection

Key improvements:
- Port validation with proper range checking (1-65535)
- Environment-aware configuration (production vs development)
- Multiple frontend build strategies with fallback HTML
- MCP environment manager integration with error handling

### 4. Robust Startup Script

**File: `start_server.sh`**
- Created comprehensive startup script with error handling
- Virtual environment activation with multiple fallback paths
- PyTorch verification at startup
- Environment-specific configuration (Railway vs local)
- Frontend build status checking

Features:
- Python version verification
- PyTorch installation validation
- Dynamic worker count configuration
- Railway environment detection
- Graceful fallback mechanisms

## Validation Steps

1. **Python Compilation Check**:
```bash
python -m py_compile run_server.py
# Result: ✅ Successful compilation, no syntax errors
```

2. **Dependency Compatibility**:
```bash
# Verify PyTorch 2.8.0 supports Python 3.12
python -c "import torch; print(f'PyTorch {torch.__version__}')"
```

3. **Railway Configuration**:
- Python 3.12 explicitly specified in railpack.json
- Health check endpoint configured at `/health`
- Timeout increased to 300 seconds for ML model initialization

## Environment Variables

The deployment now properly handles these environment variables:

- `PORT`: Dynamic port binding (Railway provides this)
- `RAILWAY_ENVIRONMENT`: Environment detection
- `LOG_LEVEL`: Configurable logging (default: info)
- `WORKERS`: Uvicorn worker count (default: 1)
- `SERVE_FRONTEND`: Frontend serving toggle (default: true)

## Health Check Configuration

```json
"deploy": {
  "healthCheckPath": "/health",
  "healthCheckTimeout": 300,
  "restartPolicyType": "ON_FAILURE",
  "restartPolicyMaxRetries": 3
}
```

## Long-term Improvements

### Implemented
1. ✅ Explicit Python version pinning
2. ✅ PyTorch CPU-optimized builds
3. ✅ Robust error handling
4. ✅ Multiple fallback strategies
5. ✅ Comprehensive logging

### Recommended Future Actions
1. Set up GitHub Actions for dependency compatibility testing
2. Implement semantic versioning for Python dependencies
3. Create automated Railway deployment pipeline
4. Add monitoring for deployment health metrics
5. Consider using Poetry for deterministic dependency resolution

## Testing Commands

```bash
# Local testing
./start_server.sh

# Railway deployment
railway up --service monkey-coder --environment production

# Verify deployment
curl -I https://coder.fastmonkey.au/health
```

## Prevention Measures

1. **Version Locking**: Always specify exact runtime versions in railpack.json
2. **Compatibility Testing**: Test with multiple Python versions in CI/CD
3. **Dependency Monitoring**: Regular updates with compatibility checks
4. **Build Caching**: Utilize Railway's cache for faster deployments
5. **Health Monitoring**: Implement comprehensive health check endpoints

## References

- [PyTorch Python 3.12 Support](https://github.com/pytorch/pytorch/releases)
- [Railway Railpack Documentation](https://docs.railway.app/reference/railpack)
- [Python Packaging Best Practices](https://packaging.python.org/en/latest/)

---

*This document serves as a reference for the January 2025 Railway deployment fix addressing Python version standardization to 3.12 for improved compatibility and deployment stability.*
