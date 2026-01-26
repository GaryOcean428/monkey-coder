# Monorepo Restructuring Summary

## Overview

This document summarizes the monorepo restructuring that aligns Monkey Coder with industry best practices for separating reusable libraries from deployable applications.

## Changes Made

### 1. Directory Structure

**Before:**
```
packages/
├── cli/              # CLI tool (published)
├── core/             # Backend + published library (CONFUSING)
├── sdk/              # SDK (published)
└── web/              # Frontend application (deployed)

services/
├── backend/          # Empty placeholder
├── ml/               # ML service
└── sandbox/          # Sandbox service
```

**After:**
```
packages/
├── cli/              # CLI tool (published to npm)
├── core/             # Python library ONLY (published to PyPI)
├── sdk/              # Client SDK (published to npm/PyPI)
├── shared-types/     # Shared TypeScript types (NEW)
└── shared-utils/     # Shared utility functions (NEW)

services/
├── frontend/         # Next.js application (MOVED from packages/web)
├── backend/          # FastAPI backend (uses packages/core library)
├── ml/               # ML inference service
└── sandbox/          # Code execution sandbox
```

### 2. Key Architectural Changes

#### Packages (Reusable Libraries)
- **packages/core** - Remains as published Python library (PyPI: monkey-coder-core)
- **packages/cli** - Remains as published CLI tool (npm: monkey-coder-cli)
- **packages/sdk** - Remains as published SDK (npm: monkey-coder-sdk)
- **packages/shared-types** - NEW: Shared TypeScript types
- **packages/shared-utils** - NEW: Shared utility functions

#### Services (Deployable Applications)
- **services/frontend** - Moved from packages/web, renamed to @monkey-coder/frontend
- **services/backend** - Properly configured to import from packages/core
- **services/ml** - ML inference microservice
- **services/sandbox** - Code execution sandbox

### 3. Configuration Updates

#### Root package.json
- Updated workspace scripts to reference `@monkey-coder/frontend` instead of `@monkey-coder/web`
- Updated build, test, lint, and dev scripts
- Added new shared packages to workspaces

#### tsconfig.json
- Updated project references to point to services/frontend
- Added references to shared-types and shared-utils

#### railpack.json Files
- **services/frontend/railpack.json** - Updated workspace commands
- **services/backend/railpack.json** - Properly imports packages/core library
- **packages/core/railpack.json** - REMOVED (no longer a deployed service)

#### .gitignore
- Added services/frontend/.next/ and services/frontend/out/
- Properly ignores build artifacts for all services

### 4. Documentation Updates

#### README.md
- Updated monorepo structure diagram
- Updated all references from packages/web to services/frontend
- Updated workspace command examples

#### AGENTS.md
- Updated all path references throughout
- Updated build and development commands

#### CONTRIBUTING.md
- Added new "Monorepo Structure Guidelines" section
- Updated commit message scopes (web → frontend, added backend, shared)
- Provided clear guidance on where to add new code

## Railway Deployment Updates Required

### Service Configuration Changes

#### Frontend Service (monkey-coder)
**Railway Dashboard Settings:**
1. Navigate to: Railway → Project → monkey-coder service → Settings
2. Update **Root Directory**: `services/frontend` (was: `packages/web`)
3. **Build Command**: Automatically detected from railpack.json
4. **Start Command**: Automatically detected from railpack.json
5. Click **Deploy**

#### Backend Service (monkey-coder-backend)
**Railway Dashboard Settings:**
1. Navigate to: Railway → Project → monkey-coder-backend service → Settings
2. Update **Root Directory**: Leave as current OR update if needed
3. Verify railpack.json configuration is correct
4. Click **Deploy**

### Environment Variables
No changes required to environment variables.

### Verification Steps

After deployment, verify:

```bash
# Check frontend
curl -f https://coder.fastmonkey.au && echo "✅ Frontend OK"

# Check backend
curl -f https://coder.fastmonkey.au/api/health && echo "✅ Backend OK"
```

## Local Development Changes

### Installation
```bash
# Enable Corepack and install dependencies
corepack enable
corepack prepare yarn@4.9.2 --activate
yarn install
```

### Build Commands
```bash
# Build all TypeScript packages
yarn build

# Build specific services
yarn workspace @monkey-coder/frontend build
yarn workspace @monkey-coder/shared-types build
yarn workspace @monkey-coder/shared-utils build

# Build Python core package
yarn build:core  # or: cd packages/core && python -m build
```

### Development Commands
```bash
# Start frontend development server
yarn workspace @monkey-coder/frontend dev

# Start backend development server (requires Python deps)
cd packages/core
python -m uvicorn monkey_coder.app.main:app --reload
```

### Testing Commands
```bash
# Run all tests
yarn test

# Test specific services
yarn workspace @monkey-coder/frontend test
yarn workspace @monkey-coder/cli test

# Test Python core
cd packages/core && pytest
```

## Benefits of This Structure

### 1. Clear Separation of Concerns
- **Packages** = Reusable, importable code
- **Services** = Deployable applications

### 2. Better Dependency Management
- Services can import from packages
- Packages remain independent
- No circular dependencies

### 3. Improved Railway Compatibility
- Each service has clear build configuration
- Root directory per service is obvious
- No confusion about what's deployed vs published

### 4. Scalability
- Easy to add new services
- Shared code goes in packages/shared-*
- Published packages remain in packages/

### 5. Developer Experience
- Clear guidelines on where to add code
- Intuitive structure for new contributors
- Follows industry best practices

## Migration Checklist

For developers with existing checkouts:

- [ ] Pull latest changes: `git pull origin main`
- [ ] Update dependencies: `yarn install`
- [ ] Update any local scripts referencing packages/web → services/frontend
- [ ] Update any imports from @monkey-coder/web → @monkey-coder/frontend
- [ ] Rebuild: `yarn build`
- [ ] Run tests: `yarn test`

## Troubleshooting

### Build Errors
```bash
# Clean and rebuild
yarn clean:all
yarn install
yarn build
```

### TypeScript Errors
```bash
# Check TypeScript project references
cat tsconfig.json
# Ensure references point to correct paths
```

### Workspace Errors
```bash
# List all workspaces
yarn workspaces list

# Should show:
# - packages/cli
# - packages/sdk
# - packages/shared-types
# - packages/shared-utils
# - services/frontend
```

### Railway Deployment Issues
1. Check Root Directory is set correctly in Railway Dashboard
2. Verify railpack.json exists in service directory
3. Check Railway logs for build errors
4. Ensure environment variables are set

## Additional Resources

- [AGENTS.md](./AGENTS.md) - Comprehensive development guide
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guidelines with monorepo structure section
- [Railway Documentation](https://docs.railway.app/) - Railway deployment guide

## Questions?

If you encounter issues with the restructuring:
1. Check this document first
2. Review AGENTS.md for detailed setup
3. Open an issue on GitHub with the `restructuring` label
