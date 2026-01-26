# Monorepo Structure Quick Reference

## Visual Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Monkey Coder Monorepo                     │
└─────────────────────────────────────────────────────────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
        ┌────────▼────────┐     ┌───────▼────────┐
        │    packages/     │     │   services/     │
        │   (Libraries)    │     │  (Applications) │
        └─────────────────┘     └────────────────┘
                 │                       │
    ┌────────────┼────────────┐         │
    │            │            │         │
┌───▼───┐  ┌────▼────┐  ┌────▼────┐   │
│  cli  │  │  core   │  │   sdk   │   │
│ (npm) │  │ (PyPI)  │  │(npm/PyPI)│  │
└───────┘  └────┬────┘  └─────────┘   │
                │                       │
    ┌───────────┼───────────┐          │
    │           │           │          │
┌───▼───────┐  ┌▼──────────┐          │
│shared-types│  │shared-utils│         │
│  (private) │  │  (private)  │        │
└────────────┘  └─────────────┘        │
                                        │
                            ┌───────────┼───────────┐
                            │           │           │
                      ┌─────▼─────┐ ┌──▼──────┐ ┌─▼────────┐
                      │  frontend │ │ backend │ │    ml    │
                      │ (Railway) │ │(Railway)│ │(Railway) │
                      └───────────┘ └────┬────┘ └──────────┘
                                         │
                                    ┌────▼────┐
                                    │ sandbox │
                                    │(Railway)│
                                    └─────────┘
```

## Dependency Flow

```
services/frontend  ──imports──> packages/shared-types
                                packages/shared-utils
                                packages/sdk

services/backend   ──imports──> packages/core (PyPI library)
                                packages/shared-utils

services/ml        ──imports──> packages/core (PyPI library)

packages/core      ──published to──> PyPI (monkey-coder-core)
packages/cli       ──published to──> npm (monkey-coder-cli)
packages/sdk       ──published to──> npm/PyPI (monkey-coder-sdk)
```

## Railway Deployment Mapping

| Service Name           | Root Directory      | Config File     | Purpose              |
|------------------------|---------------------|-----------------|----------------------|
| monkey-coder           | services/frontend   | railpack.json   | Next.js frontend     |
| monkey-coder-backend   | services/backend    | railpack.json   | FastAPI backend      |
| monkey-coder-ml        | services/ml         | railpack.json   | ML inference         |
| monkey-coder-sandbox   | services/sandbox    | Dockerfile      | Code execution       |

## Package Publishing

| Package              | Registry | Package Name           | Published | Deployed |
|----------------------|----------|------------------------|-----------|----------|
| packages/cli         | npm      | monkey-coder-cli       | ✅        | ❌       |
| packages/core        | PyPI     | monkey-coder-core      | ✅        | ❌       |
| packages/sdk         | npm/PyPI | monkey-coder-sdk       | ✅        | ❌       |
| packages/shared-*    | -        | @monkey-coder/shared-* | ❌        | ❌       |
| services/frontend    | -        | @monkey-coder/frontend | ❌        | ✅       |
| services/backend     | -        | -                      | ❌        | ✅       |
| services/ml          | -        | -                      | ❌        | ✅       |
| services/sandbox     | -        | -                      | ❌        | ✅       |

## Decision Matrix: Where Does New Code Go?

| What You're Building                          | Where It Goes              | Why                                    |
|-----------------------------------------------|----------------------------|----------------------------------------|
| Shared TypeScript type definitions            | packages/shared-types      | Used by multiple services              |
| Shared utility function                       | packages/shared-utils      | Reusable across services               |
| New API endpoint                              | services/backend           | Part of backend service                |
| Backend logic using FastAPI                   | services/backend           | Imports from packages/core             |
| Core AI/ML orchestration logic                | packages/core              | Published library, imported by backend |
| New UI component                              | services/frontend          | Part of frontend application           |
| New page/route in frontend                    | services/frontend          | Part of Next.js app                    |
| CLI command                                   | packages/cli               | Published CLI tool                     |
| New microservice                              | services/<name>            | New deployable service                 |
| SDK client method                             | packages/sdk               | Published client library               |

## Common Tasks

### Adding a New Service
```bash
# 1. Create service directory
mkdir -p services/new-service

# 2. Add railpack.json or Dockerfile
# (See existing services for examples)

# 3. Update Railway Dashboard
# Add new service, set root directory to services/new-service
```

### Adding Shared Code
```bash
# For TypeScript types
echo "export interface NewType { ... }" >> packages/shared-types/api.ts

# For utilities
echo "export function newUtil() { ... }" >> packages/shared-utils/index.ts

# Import in service
import { NewType } from '@monkey-coder/shared-types';
import { newUtil } from '@monkey-coder/shared-utils';
```

### Publishing a Package
```bash
# NPM packages
yarn workspace monkey-coder-cli publish --access public

# Python packages
cd packages/core
python -m build
python -m twine upload dist/*
```

## Quick Commands

```bash
# Install dependencies
yarn install

# Build all
yarn build

# Build specific service
yarn workspace @monkey-coder/frontend build

# Test all
yarn test

# Test specific service
yarn workspace @monkey-coder/frontend test

# Dev mode
yarn workspace @monkey-coder/frontend dev

# Lint
yarn lint

# Format
yarn format
```

## Migration Path (Old → New)

| Old Path            | New Path              | Status    |
|---------------------|-----------------------|-----------|
| packages/web        | services/frontend     | ✅ MOVED  |
| @monkey-coder/web   | @monkey-coder/frontend| ✅ RENAMED|
| packages/core       | packages/core         | ✅ STAYED |
| packages/cli        | packages/cli          | ✅ STAYED |
| packages/sdk        | packages/sdk          | ✅ STAYED |
| services/backend    | services/backend      | ✅ STAYED |

## Key Principles

1. **packages/** = Code that can be imported by services
2. **services/** = Code that runs as separate processes
3. **Packages can be published** to npm/PyPI
4. **Services are deployed** to Railway
5. **No circular dependencies** (services import from packages, not vice versa)

---

For detailed information, see [MONOREPO_RESTRUCTURING.md](./MONOREPO_RESTRUCTURING.md)
