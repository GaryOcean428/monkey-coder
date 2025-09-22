# Comprehensive Railway Deployment Compliance Fix

## Goal
Apply all Railway Deployment Master Cheat Sheet standards to ensure 100% compliance and eliminate deployment pitfalls.

## Critical Issues to Fix

### 🔴 Priority 1: railpack.json Structure Compliance

**Issue**: Current railpack.json doesn't follow the recommended template structure from Railway cheat sheet.

**Action Required**: Restructure railpack.json to match exact Railway standards:

```json
{
  "version": "1",
  "metadata": {
    "name": "monkey-coder"
  },
  "build": {
    "provider": "python",
    "packages": {
      "python": "3.12",
      "node": "20"
    },
    "cache": {
      "paths": [
        "/app/venv/lib/python3.12/site-packages",
        "/root/.cache/yarn",
        "node_modules",
        "packages/web/.next"
      ]
    },
    "steps": {
      "install": {
        "commands": [
          "echo '🐒 Starting Monkey Coder build process...'",
          "/app/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel",
          "/app/venv/bin/pip install --no-cache-dir -r requirements-deploy.txt",
          "cd packages/core && /app/venv/bin/pip install --no-cache-dir -e ."
        ]
      },
      "build": {
        "commands": [
          "corepack enable",
          "corepack prepare yarn@4.9.2 --activate",
          "yarn install --immutable || yarn install",
          "export NEXT_OUTPUT_EXPORT=true",
          "export NODE_ENV=production",
          "export NEXTAUTH_URL=${NEXTAUTH_URL:-}",
          "export NEXTAUTH_SECRET=${NEXTAUTH_SECRET:-}",
          "yarn workspace @monkey-coder/web run export || echo 'Frontend build failed - continuing with API-only'"
        ]
      }
    }
  },
  "deploy": {
    "startCommand": "/app/start_server.sh",
    "healthCheckPath": "/health",
    "healthCheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3,
    "environment": {
      "VIRTUAL_ENV": "/app/venv",
      "PATH": "/app/venv/bin:$PATH",
      "PYTHONPATH": "/app:/app/packages/core",
      "ENABLE_A2A_SERVER": "true",
      "A2A_PORT": "7702"
    }
  }
}
```

### 🔴 Priority 2: Fix SDK Localhost References

**Issue**: Hardcoded localhost URLs in SDK examples violate Railway standards.

**Files to Fix**:
1. `packages/sdk/examples/python/main.py`
2. `packages/sdk/examples/bun/index.ts`  
3. `packages/sdk/src/index.ts`

**Replace**:
```python
# ❌ WRONG
base_url=os.getenv('MONKEY_CODER_BASE_URL', 'http://localhost:8000')

# ✅ CORRECT
base_url=os.getenv('MONKEY_CODER_BASE_URL', f"https://{os.getenv('RAILWAY_PUBLIC_DOMAIN', 'localhost:8000')}")
```

```typescript
// ❌ WRONG  
baseURL: process.env.MONKEY_CODER_BASE_URL || 'http://localhost:8000'

// ✅ CORRECT
baseURL: process.env.MONKEY_CODER_BASE_URL || 
  (process.env.RAILWAY_PUBLIC_DOMAIN ? `https://${process.env.RAILWAY_PUBLIC_DOMAIN}` : 'http://localhost:8000')
```

### 🔴 Priority 3: Implement Pre-deployment Validation

**Issue**: Missing automated validation hooks recommended in cheat sheet.

**Action Required**: Create validation automation:

1. **Pre-push Git Hook** (`/.git/hooks/pre-push`):
```bash
#!/bin/bash
set -e

echo "🔍 Pre-deployment validation..."

# 1. Check for conflicting build configs
if ls -la | grep -E "(Dockerfile|railway\.toml|nixpacks\.toml)" | grep -v railpack.json; then
  echo "❌ Conflicting build files found"
  exit 1
fi

# 2. Validate railpack.json syntax
if ! jq '.' railpack.json > /dev/null 2>&1; then
  echo "❌ Invalid railpack.json syntax"
  exit 1
fi

# 3. Verify health endpoint exists
if ! grep -r "/health" packages/core/monkey_coder/app/main.py > /dev/null; then
  echo "❌ Health endpoint not found"
  exit 1
fi

# 4. Test build locally
if ! yarn build > /dev/null 2>&1; then
  echo "❌ Build failed"
  exit 1
fi

echo "✅ Pre-deployment validation passed"
```

2. **Validation Script** (`/scripts/validate-railway-compliance.sh`):
```bash
#!/bin/bash
# Railway Compliance Validator

echo "🚀 Railway Deployment Compliance Check"
echo "======================================="

ERRORS=0

# Check railpack.json structure
if ! jq '.version' railpack.json > /dev/null 2>&1; then
  echo "❌ railpack.json missing 'version' field"
  ERRORS=$((ERRORS + 1))
fi

if ! jq '.metadata.name' railpack.json > /dev/null 2>&1; then
  echo "❌ railpack.json missing 'metadata.name' field"  
  ERRORS=$((ERRORS + 1))
fi

# Check for localhost references
if grep -r "localhost:8000" packages/sdk/ > /dev/null; then
  echo "❌ Found hardcoded localhost references in SDK"
  ERRORS=$((ERRORS + 1))
fi

# Validate PORT usage
if ! grep -r "process.env.PORT" run_server.py > /dev/null; then
  echo "❌ Server not using process.env.PORT"
  ERRORS=$((ERRORS + 1))
fi

if [ $ERRORS -eq 0 ]; then
  echo "✅ All compliance checks passed"
  exit 0
else
  echo "❌ $ERRORS compliance issues found"
  exit 1
fi
```

### 🟡 Priority 4: Enhance Frontend CSS Configuration

**Issue**: Verify CSS import order and theme initialization follow cheat sheet standards.

**Action Required**: Check and fix if needed:

1. **CSS Import Order** in `packages/web/src/globals.css`:
```css
/* ✅ CORRECT ORDER */
@tailwind base;
@tailwind components; 
@tailwind utilities;

/* Critical theme styles */
.dark {
  color-scheme: dark;
}
```

2. **Theme Initialization** (if using React):
```javascript
// Apply theme BEFORE React renders
document.documentElement.className = localStorage.getItem('theme') || 'dark';
```

3. **Vite/Next.js Config** for Railway:
```javascript
export default defineConfig({
  base: './',  // Relative paths for Railway
  build: {
    outDir: 'out',
    assetsDir: 'assets',
    cssCodeSplit: false  // Ensure CSS is bundled
  }
});
```

## Implementation Steps

1. **Backup current railpack.json**: `cp railpack.json railpack.json.backup`

2. **Apply railpack.json restructure**: Replace with compliant structure

3. **Fix SDK localhost references**: Update all SDK files to use Railway domain variables

4. **Create validation scripts**: Add pre-push hook and compliance validator

5. **Verify frontend configuration**: Ensure CSS and theme setup follows standards

6. **Test locally**: 
   ```bash
   ./scripts/validate-railway-compliance.sh
   yarn build && yarn test
   ```

7. **Deploy and verify**: Ensure all Railway deployment standards are met

## Success Criteria

- [ ] railpack.json follows exact Railway template structure
- [ ] No hardcoded localhost URLs in any code
- [ ] Automated validation prevents deployment issues
- [ ] Frontend CSS loads properly without FOUC
- [ ] All Railway cheat sheet standards implemented
- [ ] Local and Railway deployment both work correctly

## Files to Modify

1. `railpack.json` - Restructure to Railway standards
2. `packages/sdk/examples/python/main.py` - Fix localhost URL
3. `packages/sdk/examples/bun/index.ts` - Fix localhost URL  
4. `packages/sdk/src/index.ts` - Fix localhost URL
5. `.git/hooks/pre-push` - Add validation hook
6. `scripts/validate-railway-compliance.sh` - Create compliance validator
7. `packages/web/src/globals.css` - Verify CSS order (if needed)
8. `packages/web/next.config.mjs` - Verify Vite config (if needed)

This comprehensive fix ensures 100% compliance with Railway Deployment Master Cheat Sheet standards and eliminates all identified deployment pitfalls.