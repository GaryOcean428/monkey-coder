# Railway Backend Service Configuration

## Overview
This document explains the Railway backend service configuration and the importance of the `requirements-deploy.txt` file in the service directory.

## Problem Statement
Railway builds each service in an **isolated build context**. When deploying the `services/backend` service:
- Railway treats `services/backend/` as `/app` during the build
- Files outside this directory (e.g., at monorepo root) are not accessible
- The `railpack.json` configuration references `requirements-deploy.txt` which must exist in the service directory

## Solution
The `requirements-deploy.txt` file has been copied from the monorepo root to `services/backend/` to make it accessible during Railway builds.

### File Locations
```
monkey-coder/
├── requirements-deploy.txt           # Original file (monorepo root)
└── services/
    └── backend/
        ├── railpack.json              # References requirements-deploy.txt
        ├── requirements-deploy.txt    # Copy for Railway build context ✅
        └── requirements.txt           # Alternative lighter requirements
```

## Railway Build Process

### 1. Build Context
When Railway builds the backend service:
```bash
# Railway's view:
/app/                           # → services/backend/
/app/requirements-deploy.txt    # → services/backend/requirements-deploy.txt ✅
/app/railpack.json             # → services/backend/railpack.json
/app/../../packages/core       # → packages/core (accessible via relative path)
```

### 2. Install Steps (from railpack.json)
```json
{
  "steps": {
    "install": {
      "commands": [
        "pip install --upgrade uv",
        "python -m uv pip install -r requirements-deploy.txt",  // ← Needs local file
        "python -m uv pip install -e ../../packages/core",      // ← Relative path OK
        "python -c 'import monkey_coder; print(\"✅ Installed:\", monkey_coder.__file__)'"
      ]
    }
  }
}
```

### 3. Expected Output
```
✅ Installed: /app/.venv/lib/python3.12/site-packages/monkey_coder/__init__.py
```

## Validation

### Running Tests
```bash
# Run Railway backend configuration tests
python3 tests/integration/test_railway_backend_config.py
```

### Manual Verification
```bash
# 1. Check file exists
ls -l services/backend/requirements-deploy.txt

# 2. Verify it matches root version
diff requirements-deploy.txt services/backend/requirements-deploy.txt

# 3. Validate railpack.json
cd services/backend && cat railpack.json | python3 -m json.tool

# 4. Verify relative path to core package
ls -ld services/backend/../../packages/core
```

## Maintenance

### When to Update
Update `services/backend/requirements-deploy.txt` whenever:
1. New dependencies are added to the backend
2. Dependency versions are updated
3. The root `requirements-deploy.txt` changes

### Automated Sync Scripts

Two scripts are available to manage requirements file synchronization:

#### 1. Verify Sync Status
```bash
# Check if files are in sync
./scripts/verify-requirements-sync.sh
```
This script will:
- ✅ Verify both files exist
- ✅ Check if they're identical
- ❌ Exit with error if out of sync (with diff output)

#### 2. Sync Files
```bash
# Sync requirements-deploy.txt from root to services/backend
./scripts/sync-requirements-deploy.sh
```
This script will:
- 📋 Copy the root requirements-deploy.txt to services/backend/
- 💾 Create a backup of the existing backend file
- ✅ Verify the sync was successful
- 📝 Show git status and commit instructions

### Manual Sync (Alternative)
```bash
# Copy updated requirements from root to backend service
cp requirements-deploy.txt services/backend/requirements-deploy.txt
```

### Pre-Commit Integration
Add this to `.githooks/pre-commit` or `.husky/pre-commit`:
```bash
# Verify requirements-deploy.txt is in sync
./scripts/verify-requirements-sync.sh || exit 1
```

## Troubleshooting

### Build Fails with "No such file or directory"
```
Error: FileNotFoundError: requirements-deploy.txt
```
**Solution:** Ensure `services/backend/requirements-deploy.txt` exists
```bash
cp requirements-deploy.txt services/backend/requirements-deploy.txt
```

### Module Import Fails
```
ModuleNotFoundError: No module named 'monkey_coder'
```
**Solution:** Verify relative path to packages/core is correct and accessible
```bash
cd services/backend
ls -ld ../../packages/core  # Should exist
```

### railpack.json Schema Errors
```
Error: Invalid railpack.json configuration
```
**Solution:** Validate JSON syntax and schema compliance
```bash
cd services/backend
cat railpack.json | python3 -m json.tool  # Check JSON syntax
```

## Related Files
- `services/backend/railpack.json` - Railway build configuration
- `requirements-deploy.txt` - Root level requirements (source)
- `services/backend/requirements-deploy.txt` - Backend service copy (deployed)
- `tests/integration/test_railway_backend_config.py` - Configuration tests
- `packages/core/pyproject.toml` - Core package configuration

## References
- [Railway Documentation](https://docs.railway.app/)
- [Railpack Schema](https://schema.railpack.com)
- [Problem Statement](https://github.com/GaryOcean428/monkey-coder/issues/XXX)
