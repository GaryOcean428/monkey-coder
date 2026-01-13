# Railway UV Virtual Environment Fix

## Issue Summary
**Problem**: Build failure on Railway deployment due to UV module not being available in isolated virtual environment.

**Root Cause**: Virtual environments (venv) are isolated by design and don't inherit packages from the parent Python installation. When using `python -m uv venv /app/.venv` to create a venv, and then trying to run `/app/.venv/bin/python -m uv`, the command fails because the venv's Python doesn't have the `uv` module installed.

**Evidence Chain**:
1. `pip install --upgrade uv` → Build Python has uv ✓
2. `python -m uv venv /app/.venv` → Creates clean venv ✓
3. `/app/.venv/bin/python -m uv pip install ...` → ModuleNotFoundError ✗

## Solution Applied

### Changed Commands in `services/backend/railpack.json`

**Before (Failed Approach)**:
```json
"commands": [
  "pip install --upgrade uv",
  "python -m uv venv /app/.venv",
  "/app/.venv/bin/python -m uv pip install -r requirements-deploy.txt",
  "/app/.venv/bin/python -m uv pip install --no-cache-dir git+https://..."
]
```

**After (Working Solution)**:
```json
"commands": [
  "pip install --upgrade uv",
  "uv venv /app/.venv",
  "uv pip install --python /app/.venv/bin/python -r requirements-deploy.txt",
  "uv pip install --python /app/.venv/bin/python --no-cache-dir git+https://..."
]
```

### Key Changes

1. **Use UV Binary Instead of Module**: 
   - Changed from `python -m uv` to direct `uv` command
   - The `uv` binary is installed to the build Python's PATH by pip
   - More reliable PATH resolution in Railway's build context

2. **Install into Venv via --python Flag**:
   - Use `uv pip install --python /app/.venv/bin/python`
   - The `--python` flag tells UV to install packages into the target Python's site-packages
   - Build Python's UV remains available while packages go into the venv

## Technical Details

### Why This Works

1. **Build Stage**:
   - `pip install uv` → Installs UV binary to build Python (Railway Python 3.13 provider)
   - UV binary available in PATH (managed by Railway's Python provider)
   - Binary added to PATH automatically

2. **Venv Creation**:
   - `uv venv /app/.venv` → Creates isolated virtual environment
   - Venv contains only default packages (pip, setuptools, wheel)
   - No UV module in venv's site-packages

3. **Package Installation**:
   - `uv pip install --python /app/.venv/bin/python -r requirements.txt`
   - Build Python's UV binary executes the command
   - `--python` flag directs installation to venv's site-packages
   - Zero redundant package installs

4. **Runtime Stage**:
   - `/app/.venv` copied to runtime environment
   - All required packages available in venv
   - `/app/.venv/bin/python -m uvicorn` works correctly

### UV Documentation Reference

According to [UV official documentation](https://docs.astral.sh/uv/pip/environments/) (verified as of January 2026):

> "You can use `--python` with `uv pip install` to install packages directly into the environment tied to a specific Python interpreter:
> ```bash
> uv pip install --python /path/to/python some-package
> ```
> This enables direct installation into arbitrary Python environments, not just those managed by uv."

## Verification Steps

### 1. JSON Syntax Validation
```bash
python3 -m json.tool services/backend/railpack.json > /dev/null
echo $?  # Should output 0
```

### 2. Check Railway Build Logs
Expected output sequence:
```
✓ pip install --upgrade uv        (~2s)
✓ curl -fsSL ... requirements...   (~1s)
✓ test -f requirements...          (~100ms)
✓ uv venv /app/.venv               (~700ms)
✓ uv pip install --python ...      (~3-80s)
✓ Build complete
```

### 3. Runtime Verification
```bash
# Health check
curl -I https://monkey-coder-backend-production.up.railway.app/api/health

# Expected: HTTP/1.1 200 OK

# Test API endpoint
curl https://monkey-coder-backend-production.up.railway.app/api/v1/models/available

# Expected: JSON response with available models
```

## Related Files

- **Configuration**: `services/backend/railpack.json`
- **Dependencies**: `services/backend/requirements-deploy.txt`
- **Build Logs**: Railway deployment 92df606 and later

## Commit History

- **Commit**: `92df606` - "Fix: Use UV binary instead of Python module"
- **Date**: 2026-01-13T07:26:04Z
- **Author**: GaryOcean <81794144+GaryOcean428@users.noreply.github.com>

## Additional Notes

- This fix follows Railway's native pattern for multi-stage builds
- No redundant UV installations required
- Build time reduced by eliminating failed attempts
- Pattern applicable to other Railway deployments with similar venv isolation issues

## References

- [UV Documentation - Using environments](https://docs.astral.sh/uv/pip/environments/)
- [UV Documentation - Installing Python](https://docs.astral.sh/uv/guides/install-python/)
- [Railway Build Configuration](https://docs.railway.app/reference/config-as-code)
