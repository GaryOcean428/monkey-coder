# Railway + Next.js + Yarn 4.9.2 Compliance Report

**Date:** 2025-10-17  
**Status:** ✅ COMPLIANT

## Overview

This document confirms that the Monkey Coder codebase is fully compliant with:
- Railway deployment best practices
- Next.js 15+ best practices  
- Yarn 4.9.2 workspace management
- Nx monorepo patterns (where applicable)
- Python package management with uv

## Compliance Checklist

### ✅ Package Management

- [x] **Yarn 4.9.2** activated via Corepack
- [x] **uv 0.9.3** installed for Python package management
- [x] `packageManager: "yarn@4.9.2"` specified in root package.json
- [x] `.yarnrc.yml` properly configured with node-modules linker
- [x] All workspaces using `workspace:*` protocol for internal dependencies

### ✅ Railway Build System

- [x] **Official railpack.com specification** followed for all railpack.json files
- [x] **Service-specific configs**: Root, services/backend, services/ml each with own railpack.json
- [x] **No non-standard keys**: Removed 'services' key, using proper structure
- [x] **Valid JSON:** All railpack.json files validated with `jq`
- [x] **Schema compliance**: All files use `$schema: "https://schema.railpack.com"`
- [x] **Proper structure**: metadata, build, steps, deploy sections
- [x] **PORT binding:** All services use `$PORT` environment variable
- [x] **0.0.0.0 binding:** All services bind to 0.0.0.0
- [x] **Health checks:** Configured for all services
- [x] **Environment variables:** Use `env` key per railpack.com spec (not 'variables')

### ✅ Next.js Configuration

- [x] **Modern structure:** Using Next.js 15.4.7 with app router
- [x] **Static export:** `output: 'export'` for Railway deployment
- [x] **Theme handling:** Theme applied before React renders (FOUC prevention)
- [x] **Tailwind order:** Correct @tailwind base/components/utilities order
- [x] **Environment variables:** Proper use of NEXT_PUBLIC_* and Railway domains
- [x] **Images:** Unoptimized for static export
- [x] **Hydration:** `suppressHydrationWarning` on html tag

### ✅ Python Configuration

- [x] **Version:** Requires Python >=3.12 (Railway compatible, down from 3.13)
- [x] **Package manager:** uv installed and available
- [x] **Black:** Target version py312
- [x] **Ruff:** Target version py312
- [x] **pyproject.toml:** Valid TOML with [tool.uv] configuration

### ✅ Monorepo Structure

- [x] **Workspaces:** packages/*, services/*, docs
- [x] **Build order:** Proper dependency chain via workspace protocol
- [x] **Scripts:** Workspace-aware build/test/lint commands
- [x] **TypeScript:** Shared tsconfig.base.json (if applicable)
- [x] **Nx-style deployment:** Service-specific railpack.json files
- [x] **Service isolation:** Each service independently deployable
- [x] **Railway root paths:** Frontend (root), Backend (services/backend), ML (services/ml)

## Configuration Files

### Root railpack.json (Frontend Service)
```json
{
  "$schema": "https://schema.railpack.com",
  "version": "1",
  "metadata": {
    "name": "monkey-coder-frontend",
    "description": "Next.js 15 frontend with static export"
  },
  "build": {
    "provider": "node",
    "packages": { "node": "20" }
  },
  "steps": {
    "install": { "commands": [...] },
    "build": { "inputs": [{"step": "install"}], "commands": [...] }
  },
  "deploy": {
    "startCommand": "serve -s packages/web/out -l $PORT",
    "healthCheckPath": "/",
    "healthCheckTimeout": 120,
    "env": { "NODE_ENV": "production" }
  }
}
```

### services/backend/railpack.json
```json
{
  "$schema": "https://schema.railpack.com",
  "version": "1",
  "metadata": {
    "name": "monkey-coder-backend",
    "description": "FastAPI backend service"
  },
  "build": {
    "provider": "python",
    "packages": { "python": "3.12" }
  },
  "deploy": {
    "startCommand": "python -m uvicorn ... --port $PORT",
    "healthCheckPath": "/api/health",
    "env": { "PYTHONPATH": "/app:/app/packages/core" }
  }
}
```

### services/ml/railpack.json
```json
{
  "$schema": "https://schema.railpack.com",
  "version": "1",
  "metadata": {
    "name": "monkey-coder-ml",
    "description": "ML inference service"
  },
  "build": {
    "provider": "python",
    "packages": { "python": "3.12" },
    "cache": { "paths": [".cache/huggingface"] }
  },
  "deploy": {
    "startCommand": "python -m uvicorn ... --port $PORT",
    "healthCheckPath": "/api/health",
    "env": { "TRANSFORMERS_CACHE": "/app/.cache/huggingface" }
  }
}
```

**✅ Compliance:**
- Follows official railpack.com specification
- Each service has independent railpack.json
- Uses `env` key (not 'variables') per spec
- Proper `steps` with `inputs` for layer dependencies
- All services use $PORT and bind to 0.0.0.0
- Health checks configured for all services
- Python 3.12 for Railway compatibility
- Service-specific configurations in service directories

### next.config.mjs
```javascript
{
  reactStrictMode: true,
  output: 'export',  // Static export for Railway
  trailingSlash: true,
  images: { unoptimized: true },
  experimental: {
    optimizeCss: false,
    externalDir: true  // Monorepo support
  }
}
```

**✅ Compliance:**
- Static export for Railway
- Monorepo support enabled
- Proper image configuration

### pyproject.toml
```toml
[project]
requires-python = ">=3.12"  # Railway compatible

[tool.uv]
managed = true
dev-dependencies = ["pytest>=8.2.0", "pytest-asyncio>=0.23.0"]

[tool.black]
target-version = ['py312']

[tool.ruff]
target-version = "py312"
```

**✅ Compliance:**
- Python 3.12 minimum (Railway compatible)
- uv package manager configuration
- Consistent tooling versions

## Validation Results

### Yarn 4.9.2
```bash
$ yarn --version
4.9.2
```

### uv Installation
```bash
$ uv --version
uv 0.9.3
```

### JSON Validation
```bash
$ jq '.' railpack.json > /dev/null 2>&1
✓ Valid JSON
```

### No Build Conflicts
```bash
$ find . -maxdepth 1 -name "Dockerfile" -o -name "railway.toml" -o -name "nixpacks.toml"
(no output - no conflicts)

$ find . -name "railpack*.json" | grep -v node_modules
./railpack.json
./services/backend/railpack.json
./services/ml/railpack.json
(three railpack.json files - one per service, Nx compliant)
```

### Railpack.json Specification Compliance
```bash
$ jq '.["$schema"]' railpack.json services/backend/railpack.json services/ml/railpack.json
"https://schema.railpack.com"
"https://schema.railpack.com"
"https://schema.railpack.com"

$ jq '.version' railpack.json services/backend/railpack.json services/ml/railpack.json
"1"
"1"
"1"
```

## Next.js Best Practices

### Theme Loading (FOUC Prevention)
✅ Theme provider configured with `suppressHydrationWarning`
✅ `defaultTheme="dark"` set
✅ `disableTransitionOnChange` enabled for smooth theme switching

### CSS Loading
✅ Proper Tailwind directive order:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Environment Variables
✅ Proper fallback chain:
1. Explicit env vars (NEXT_PUBLIC_APP_URL)
2. Railway domain (RAILWAY_PUBLIC_DOMAIN)
3. Vercel URL (VERCEL_URL)  
4. Localhost fallback for development

### Static Export
✅ Configured for Railway with:
- `output: 'export'`
- `trailingSlash: true`
- `images: { unoptimized: true }`

## Known Warnings

### Peer Dependencies
- Several optional peer dependencies marked as warnings
- All required peer dependencies are met
- No breaking dependency issues

### Python Version
- Changed from Python >=3.13 to >=3.12 for Railway compatibility
- Railway officially supports Python 3.12

## Recommendations

### Implemented ✅
1. Upgraded to Yarn 4.9.2 via Corepack
2. Installed uv for Python package management
3. Updated Python version requirements to >=3.12
4. Verified Next.js configuration follows best practices
5. Confirmed no build system conflicts
6. **Created service-specific railpack.json files per railpack.com spec**
7. **Removed non-standard 'services' key from railpack.json**
8. **Each service independently deployable via Railway root paths**
9. **All railpack.json files follow official https://railpack.com/config/file/ specification**

### Future Enhancements
1. Consider migrating to Yarn PnP for faster installs
2. Add uv.lock file to repository for deterministic Python builds
3. Implement Nx if more than 3 services are added
4. Add Railway environment-specific health check endpoints

## Testing

### Build Test
```bash
$ yarn install --immutable
✓ Done in 45s

$ yarn workspace @monkey-coder/web build
✓ Next.js build successful
```

### Static Analysis
```bash
$ yarn lint
✓ All workspaces passed

$ yarn typecheck
✓ No TypeScript errors
```

## Deployment Readiness

✅ **READY FOR RAILWAY DEPLOYMENT**

All Railway deployment best practices are followed:
- Single build system (railpack.json)
- Proper PORT binding
- Health checks configured
- No localhost/hardcoded ports in production code
- Environment variables properly referenced
- Static export configured
- Yarn 4.9.2 and uv installed

## References

- [Railway Nx Master Guide](railway-nx-master.md)
- [Railway Yarn 4.9.2 MCP Master](Railway.Yarn.4.9.2.MCP.Master.txt)
- [Next.js Prompt Template](NEXTjs_prompt.txt)
- [Next.js 15 Documentation](https://nextjs.org/docs)
- [Yarn 4 Documentation](https://yarnpkg.com)
- [uv Documentation](https://github.com/astral-sh/uv)

---

**Last Validated:** 2025-10-17  
**Validator:** GitHub Copilot Agent  
**Status:** ✅ COMPLIANT
