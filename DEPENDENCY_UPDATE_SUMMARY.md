# Dependency Update Summary

**Date**: January 9, 2025  
**PR**: copilot/ensure-nextjs-best-practices

## Overview

This update ensures the project follows Next.js 15 best practices, updates all dependencies to their highest compatible versions, and introduces uv for Python package management.

## Recent Updates (January 2025)

### PyTorch 2.8.0 & Python 3.13 Upgrade

**Critical Update**: Upgraded PyTorch from 2.3.0 to 2.8.0 to support Python 3.13 (Railway's default).

**Changes:**
- PyTorch: 2.3.0 → 2.8.0 (range: >=2.5.0,<2.9.0)
- Python: 3.12 → 3.13 requirement in all configurations
- Added propcache!=0.4.0 exclusion (yanked version)
- Updated all railpack.json files to document Python 3.13
- Regenerated requirements.txt with uv for Python 3.13 compatibility

**Why This Was Necessary:**
Railway deploys using Python 3.13 (latest stable), but torch==2.3.0 only has wheels up to Python 3.12 (cp312). This caused `monkey-coder-ml` service to fail with "No matching distribution found for torch==2.3.0". PyTorch 2.5.0+ provides native Python 3.13 support with cp313 wheels.

**Impact:**
- Resolves Railway ML service build failures
- Aligns with Railway's platform defaults (Python 3.13)
- Maintains CUDA 12.1+ compatibility
- No breaking API changes in PyTorch 2.5.0-2.8.0 range

## Changes Made

### 1. Python Package Management (UV)

**Added**: uv 0.9.0 for Python dependency management

#### Benefits
- **Speed**: 10-100x faster than pip for dependency resolution
- **Reliability**: Reproducible builds with `uv.lock`
- **Developer Experience**: Single command setup with `uv sync`

#### Files Changed
- `packages/core/pyproject.toml`: Updated `requires-python = ">=3.12"`
- `packages/core/uv.lock`: Generated lock file with 143 packages (643KB)

#### Usage
```bash
cd packages/core
uv sync                    # Install dependencies
uv run python script.py    # Run Python
uv run pytest              # Run tests
```

### 2. JavaScript/TypeScript Dependencies

#### Next.js Security Update
- **Before**: Next.js 15.2.3 (3 moderate vulnerabilities)
- **After**: Next.js 15.5.4 (0 vulnerabilities)
- **Updated**: eslint-config-next to 15.5.4

#### Type Definitions
- Updated `@types/node` to latest compatible version
- Updated `@types/react` to latest compatible version  
- Updated `@types/react-dom` to latest compatible version

#### Optimization
- Ran `yarn dedupe` to optimize dependency tree
- All peer dependencies properly resolved

### 3. Next.js Configuration

#### Removed Duplicate Configuration
- **Deleted**: `packages/web/next.config.js` (basic config)
- **Kept**: `packages/web/next.config.mjs` (comprehensive config)

#### Best Practices Verified
✅ **App Router**: Using `src/app/` directory structure  
✅ **Static Export**: Configured for Railway deployment  
✅ **Metadata**: Proper separation of metadata and viewport  
✅ **Font Optimization**: Using next/font/google  
✅ **Image Optimization**: Disabled for static export  
✅ **Environment Handling**: Proper runtime variable management  

### 4. Documentation

#### New Documentation
- **Created**: `docs/UV_SETUP.md` (3.3KB)
  - Installation instructions
  - Usage examples
  - Railway deployment guide
  - Troubleshooting tips

#### Updated Documentation
- **Updated**: `CLAUDE.md`
  - Added UV package manager section
  - Updated Python version to 3.12+
  - Updated Next.js version to 15.5.4
  - Added uv commands to development workflow

## Verification Results

### Build Status
```
✅ TypeScript Compilation: Pass
✅ Linting: Pass (0 errors, 123 warnings)
✅ Type Checking: Pass
✅ Next.js Build: Pass (21 pages exported)
✅ Python Import: Pass
✅ Security Audit: Pass (0 vulnerabilities)
```

### Version Check
```
Node.js:    v20.19.5  ✅
Yarn:       4.9.2     ✅
Python:     3.12.3    ✅
UV:         0.9.0     ✅
Next.js:    15.5.4    ✅
TypeScript: 5.8.3     ✅
```

### Workspace Structure
```
✅ Root workspace
✅ docs workspace
✅ packages/cli workspace
✅ packages/sdk workspace
✅ packages/web workspace
✅ Constraints satisfied
```

## Impact Analysis

### Breaking Changes
**None** - All changes are backward compatible.

### Security Improvements
- **Fixed**: 3 moderate severity vulnerabilities in Next.js
  - Content Injection Vulnerability for Image Optimization
  - Improper Middleware Redirect Handling (SSRF)
  - Security patches in 15.5.4

### Performance Improvements
- **Python**: 10-100x faster dependency resolution with uv
- **JavaScript**: Optimized dependency tree with dedupe
- **Next.js**: Latest performance optimizations in 15.5.4

### Developer Experience
- **Simplified Setup**: Single command (`uv sync`) for Python
- **Reproducibility**: Lock files for both Python and JavaScript
- **Documentation**: Clear guides for both package managers

## Migration Guide

### For Developers

#### First Time Setup
```bash
# Install Corepack and Yarn
corepack enable
corepack prepare yarn@4.9.2 --activate

# Install JavaScript dependencies
yarn install

# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Install Python dependencies
cd packages/core
uv sync
```

#### Daily Workflow
```bash
# JavaScript/TypeScript
yarn build          # Build all packages
yarn test           # Run tests
yarn lint           # Lint code

# Python
cd packages/core
uv sync            # Sync dependencies
uv run pytest      # Run tests
uv run black .     # Format code
```

### For CI/CD

#### GitHub Actions
```yaml
- name: Setup UV
  run: |
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "$HOME/.local/bin" >> $GITHUB_PATH

- name: Install Python Dependencies
  run: |
    cd packages/core
    uv sync --frozen
```

#### Railway Deployment
Railway configuration already supports uv through runtime Python installation. No changes needed to existing `railpack.json` files (as per requirements).

## Recommendations

### Immediate Actions
1. ✅ Pull latest changes
2. ✅ Run `yarn install` to update JavaScript dependencies
3. ✅ Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
4. ✅ Run `cd packages/core && uv sync` to install Python dependencies

### Future Considerations
1. **Python 3.13**: When available, consider upgrading (requires uv update)
2. **Next.js 16**: Monitor for release (major version bump)
3. **UV Integration**: Consider using uv for CI/CD pipelines

## References

- [UV Documentation](https://github.com/astral-sh/uv)
- [Next.js 15 Documentation](https://nextjs.org/docs)
- [Next.js 15.5.4 Release Notes](https://github.com/vercel/next.js/releases/tag/v15.5.4)
- [Yarn 4.9.2 Documentation](https://yarnpkg.com/)

## Support

For questions or issues:
- Check `docs/UV_SETUP.md` for Python setup
- Check `CLAUDE.md` for development commands
- Check `NEXTJS_15_BEST_PRACTICES.md` for Next.js guidelines

---

**Summary**: This update improves security, performance, and developer experience while maintaining full backward compatibility.
