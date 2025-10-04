# Next.js 15 Best Practices - Monkey Coder

## Overview

This document outlines Next.js 15 best practices for the Monkey Coder project, with special attention to common pitfalls and breaking changes from Next.js 14.

## Critical Issues in Next.js 15

### 1. RegExp Literal Issues

**Problem**: Next.js 15 has stricter parsing of regular expressions, causing build failures with certain regex patterns.

**Reference**: https://github.com/Arcane-Fly/disco/pull/132

**Common Error**:
```
Error: Invalid regular expression: /(?:^|[\s\n])([\w-]+)(?=[\s\n]|$)/g: Invalid group
```

#### ❌ Problematic Patterns

```javascript
// Issue: Lookbehind/lookahead assertions can cause problems
const pattern1 = /(?:^|[\s\n])([\w-]+)(?=[\s\n]|$)/g;

// Issue: Complex character classes with escapes
const pattern2 = /[\\\/\-\_\s]/g;

// Issue: Unicode property escapes without proper flags
const pattern3 = /\p{Emoji}/g;  // Missing 'u' flag
```

#### ✅ Recommended Patterns

```javascript
// Use explicit string matching
const pattern1 = /(^|[\s\n])([\w-]+)([\s\n]|$)/g;

// Simplify character classes
const pattern2 = /[\\/\-_\s]/g;  // Remove unnecessary escapes

// Add proper Unicode flag
const pattern3 = /\p{Emoji}/gu;  // Add 'u' flag

// Or use RegExp constructor for complex patterns
const pattern4 = new RegExp('(?:^|[\\s\\n])([\\w-]+)(?=[\\s\\n]|$)', 'g');
```

### 2. Current Codebase Status

#### ✅ Next.js Configuration (GOOD)

Our `next.config.mjs` is clean and follows best practices:

```javascript
// packages/web/next.config.mjs
export default (phase) => {
  const isDev = phase === PHASE_DEVELOPMENT_SERVER
  return {
    reactStrictMode: true,
    output: 'export',
    trailingSlash: true,
    images: {
      unoptimized: true,
      domains: ['localhost', 'coder.fastmonkey.au', 'monkey-coder.up.railway.app'],
    },
    // No problematic regex patterns
  }
}
```

#### ⚠️ Areas to Monitor

Files containing regex patterns that should be reviewed:
- `packages/web/src/components/ui/password-strength.tsx`
- `packages/web/src/components/ui/input.tsx`
- Any custom validation logic

### 3. Next.js 15 Breaking Changes

#### Output Configuration

```javascript
// ✅ CORRECT - For Railway deployment
export default {
  output: 'export',  // Static export
  trailingSlash: true,
  images: {
    unoptimized: true  // Required for static export
  }
}
```

#### Image Optimization

```javascript
// ❌ WRONG - Will fail in static export
export default {
  images: {
    domains: ['example.com']  // Not supported in export mode
  }
}

// ✅ CORRECT - For static export
export default {
  images: {
    unoptimized: true,
    domains: ['example.com']  // OK if for dev mode only
  }
}
```

#### API Routes

```javascript
// ⚠️ NOT AVAILABLE in 'export' mode
// API routes are not supported with static export
// Use external API (our backend service)

// ✅ CORRECT - Proxy during development
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`
    }
  ]
}
```

### 4. Deployment Best Practices

#### Railway-Specific Configuration

```javascript
// packages/web/next.config.mjs
export default {
  // Static export for Railway
  output: 'export',
  trailingSlash: true,
  
  // Required for static export
  images: {
    unoptimized: true
  },
  
  // Webpack configuration
  webpack: (config, { isServer, dev }) => {
    // Path aliases
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(process.cwd(), 'src'),
    }
    
    // Production optimizations
    if (!dev && !isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        module: false,
      }
    }
    
    return config
  }
}
```

### 5. Performance Optimizations

#### Bundle Size Management

```javascript
// next.config.mjs
export default {
  experimental: {
    optimizeCss: false,  // Reduce inline styles
    externalDir: true    // Monorepo support
  },
  
  // Webpack optimizations
  webpack: (config, { dev }) => {
    if (!dev) {
      // Production optimizations
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            default: false,
            vendors: false,
            // Vendor chunk
            vendor: {
              name: 'vendor',
              chunks: 'all',
              test: /node_modules/,
              priority: 20
            },
            // Common chunk
            common: {
              name: 'common',
              minChunks: 2,
              chunks: 'all',
              priority: 10,
              reuseExistingChunk: true,
              enforce: true
            }
          }
        }
      }
    }
    return config
  }
}
```

### 6. Environment Variables

#### Proper Configuration

```javascript
// ✅ CORRECT - Runtime environment variables
export default {
  env: {
    // Available at build time and runtime
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
  }
}
```

#### Railway Environment Variables

Required for monkey-coder frontend:
```bash
NODE_ENV=production
NEXT_OUTPUT_EXPORT=true
NEXT_TELEMETRY_DISABLED=1
NEXT_PUBLIC_APP_URL=https://coder.fastmonkey.au
NEXT_PUBLIC_API_URL=https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}
```

### 7. Testing for Next.js 15 Issues

#### Pre-Deployment Checklist

```bash
# 1. Clean build test
rm -rf .next out
yarn build

# 2. Check for regex issues
grep -r "new RegExp\|\/.*\/[gimuy]" src/ | grep -v "node_modules"

# 3. Verify static export
ls -la out/
cat out/_next/static/chunks/*.js | grep -i "regexp\|lookahead\|lookbehind"

# 4. Test production build locally
npx serve out -p 3000

# 5. Check bundle sizes
du -h out/_next/static/chunks/*.js
```

### 8. Migration Guide (Next.js 14 → 15)

#### Step 1: Update Dependencies

```bash
# Update Next.js
yarn workspace @monkey-coder/web add next@15.2.3 react@18.2.0 react-dom@18.2.0

# Update TypeScript types
yarn workspace @monkey-coder/web add -D @types/react@18.2.0 @types/react-dom@18.2.0
```

#### Step 2: Update Configuration

```javascript
// Remove deprecated options
export default {
  // ❌ REMOVE these if present
  // target: 'serverless',  // Deprecated
  // experimental.amp,      // Deprecated
  
  // ✅ ADD these
  reactStrictMode: true,
  output: 'export'
}
```

#### Step 3: Fix Regex Patterns

```bash
# Find all regex patterns
grep -rn "new RegExp\|\/.*\/[gimuy]" src/

# Test each pattern
node -e "console.log(/your-pattern/.test('test-string'))"
```

#### Step 4: Test Build

```bash
# Clean build
yarn workspace @monkey-coder/web build

# Check for warnings
cat .next/build-warnings.txt

# Verify output
ls -la packages/web/out/
```

### 9. Common Issues & Solutions

#### Issue: Build fails with regex error

```bash
# Solution: Check all regex patterns
grep -rn "new RegExp" packages/web/src/

# Update problematic patterns
# Before: /(?<=^|[\s\n])([\w-]+)(?=[\s\n]|$)/g
# After:  /(^|[\s\n])([\w-]+)([\s\n]|$)/g
```

#### Issue: Static export fails

```bash
# Solution: Ensure proper configuration
# packages/web/next.config.mjs
export default {
  output: 'export',
  images: {
    unoptimized: true  // Required!
  }
}
```

#### Issue: Images not loading

```bash
# Solution: Use unoptimized images
<Image 
  src="/image.png"
  alt="Description"
  width={500}
  height={300}
  unoptimized={true}  // For static export
/>
```

### 10. Recommended Patterns

#### Dynamic Imports

```javascript
// ✅ CORRECT - Code splitting
const DynamicComponent = dynamic(
  () => import('../components/HeavyComponent'),
  {
    loading: () => <p>Loading...</p>,
    ssr: false  // Disable SSR if needed
  }
)
```

#### Client-Side Only Code

```javascript
// ✅ CORRECT - Client-side only
'use client'

import { useEffect, useState } from 'react'

export default function ClientComponent() {
  const [data, setData] = useState(null)
  
  useEffect(() => {
    // Client-side only code
    fetch('/api/data').then(/* ... */)
  }, [])
  
  return <div>{/* ... */}</div>
}
```

### 11. Monitoring & Debugging

#### Build Analysis

```bash
# Analyze bundle
ANALYZE=true yarn build

# Check bundle sizes
yarn workspace @monkey-coder/web build --profile

# Monitor build performance
time yarn workspace @monkey-coder/web build
```

#### Runtime Debugging

```javascript
// Add debug logging
if (process.env.NODE_ENV === 'development') {
  console.log('Debug info:', {
    version: process.env.NEXT_PUBLIC_VERSION,
    api: process.env.NEXT_PUBLIC_API_URL
  })
}
```

## Summary

### ✅ Current Status

- Next.js 15.2.3 installed
- Clean configuration without problematic regex patterns
- Static export configured for Railway
- Image optimization properly disabled
- Development proxy working correctly

### ⚠️ Watch Out For

- New regex patterns in validation logic
- Complex lookbehind/lookahead assertions
- Unicode property escapes without flags
- Dynamic imports in static export mode

### 📋 Action Items

1. ✅ Audit all regex patterns in codebase
2. ✅ Ensure static export configuration is correct
3. ✅ Test build process regularly
4. ⏱️ Add regex validation to CI/CD
5. ⏱️ Document any new regex patterns

## References

- [Next.js 15 Documentation](https://nextjs.org/docs)
- [Next.js 15 Migration Guide](https://nextjs.org/docs/upgrading)
- [Regex Issue Example](https://github.com/Arcane-Fly/disco/pull/132)
- [Railway Deployment Best Practices](./RAILWAY_DEPLOYMENT.md)

---

**Last Updated**: 2025-10-03  
**Next.js Version**: 15.2.3  
**Status**: Production Ready
