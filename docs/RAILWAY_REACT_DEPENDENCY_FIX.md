# Railway React Dependency Fix

## Problem

The `monkey-coder-backend` and `monkey-coder-ml` services were failing to build on Railway with errors about missing React peer dependencies:

```
@docusaurus/utils requires a peer of react but none was found in the package tree.
@docusaurus/utils requires a peer of react-dom but none was found in the package tree.
```

## Root Cause

Railway deploys from the monorepo root which contains:
- A `docs/` workspace with Docusaurus packages that have React as peer dependencies
- A root `package.json` with React dependencies
- Multiple service-specific `railpack.json` files

The backend and ML service railpack configurations only included Python packages, which meant:
1. Railway would not install Node.js or Yarn
2. When Railway's build system analyzed the monorepo structure, it couldn't resolve peer dependencies
3. The `yarn install --check-cache` validation failed because React wasn't available for Docusaurus

## Solution

Updated both `railpack-backend.json` and `railpack-ml.json` to:

### 1. Add Node.js 20 to packages

```json
"packages": {
  "python": "3.13",
  "node": "20"
}
```

### 2. Add Yarn installation step

```json
"steps": {
  "install-yarn": {
    "commands": [
      "echo '📦 Setting up Yarn for monorepo...'",
      "corepack enable",
      "corepack prepare yarn@4.9.2 --activate",
      "yarn install --immutable",
      "echo '✅ Yarn dependencies installed (including React for Docusaurus)'"
    ]
  },
  "install-python": {
    "commands": [
      // ... Python installation commands
    ],
    "inputs": [{"step": "install-yarn"}]
  }
}
```

### 3. Add Yarn cache paths

```json
"cache": {
  "paths": [
    "node_modules",
    ".yarn/cache",
    ".venv",
    "__pycache__",
    // ... other cache paths
  ]
}
```

## Why This Works

1. **Monorepo Architecture**: Railway reads from the repository root and sees all workspaces
2. **Peer Dependency Resolution**: With Node and Yarn properly set up, React is installed and hoisted
3. **Build Order**: Installing Yarn dependencies FIRST ensures all peer dependencies are satisfied before Python installation
4. **Cache Optimization**: Caching `node_modules` and `.yarn/cache` speeds up subsequent builds

## Consistency

This fix aligns all three Railway services to use the same pattern:

- ✅ `railpack.json` (frontend) - Already had Python 3.13 + Node 20
- ✅ `railpack-backend.json` (backend) - Now has Python 3.13 + Node 20
- ✅ `railpack-ml.json` (ML) - Now has Python 3.13 + Node 20

## Testing

Local validation confirms:
```bash
# Yarn setup works
corepack enable
corepack prepare yarn@4.9.2 --activate

# Dependencies install without errors
yarn install --immutable
# ✅ Done with warnings in 2s 171ms

# Configuration is valid
cat railpack-backend.json | jq '.'
# ✅ Valid JSON
```

## References

- Railway Deployment Guide: `/RAILWAY_DEPLOYMENT.md`
- Yarn Workspace Setup: `/.agent-os/product/yarn-workspace-setup.md`
- Issue: "Build failure for monkey-coder-backend service due to missing React peer dependencies"
