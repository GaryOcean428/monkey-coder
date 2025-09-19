#!/bin/bash

# Railway Build Simulation Test
# This script simulates the key parts of the railpack.json build process
# to verify our fixes work correctly

set -e

echo "🚂 Railway Build Simulation Test"
echo "================================"

cd "$(dirname "$0")"

# Clean previous build to simulate fresh deployment
echo "🧹 Cleaning previous builds..."
rm -rf packages/web/out || true
rm -rf /tmp/test_app_out || true

# Simulate Railway environment variables
export NEXT_OUTPUT_EXPORT=true
export NODE_ENV=production
export NEXT_TELEMETRY_DISABLED=1
export NEXTAUTH_URL=${NEXTAUTH_URL:-https://coder.fastmonkey.au}
export NEXTAUTH_SECRET=${NEXTAUTH_SECRET:-railway-build-secret-$(date +%s)}
export NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-https://coder.fastmonkey.au}
export NEXT_PUBLIC_APP_URL=${NEXT_PUBLIC_APP_URL:-https://coder.fastmonkey.au}
export DATABASE_URL=${DATABASE_URL:-postgresql://railway.internal:5432/railway}

echo "🌍 Environment variables set"

# Test frontend build process (similar to railpack.json)
echo "🏗️ Building frontend with comprehensive environment setup..."
BUILD_SUCCESS=false

echo "Attempting yarn workspace build..."
if yarn workspace @monkey-coder/web run export; then
    BUILD_SUCCESS=true
    echo "✅ Workspace export succeeded"
else
    echo "⚠️ Workspace export failed, trying alternative method..."
    cd packages/web
    if yarn install --frozen-lockfile && yarn run export; then
        BUILD_SUCCESS=true
        echo "✅ Direct export succeeded"
    else
        echo "⚠️ Alternative export failed, trying simple build..."
        if yarn run build; then
            echo "Build completed, checking for .next directory..."
            if [ -d .next ]; then
                echo "Copying .next to out directory..."
                mkdir -p out && cp -r .next/* out/ 2>/dev/null || true
                BUILD_SUCCESS=true
                echo "✅ Build conversion succeeded"
            fi
        else
            echo "❌ All build methods failed"
        fi
    fi
    cd ../..
fi

echo "Build success status: $BUILD_SUCCESS"

# Test verification process (similar to railpack.json)
echo "🔍 Verifying frontend build integrity (relaxed mode)..."
FRONTEND_VALID=false

if [ -f packages/web/out/index.html ]; then
    FRONTEND_HASH=$(sha256sum packages/web/out/index.html | awk '{print $1}')
    echo "✅ Frontend verification passed: index.html present"
    echo "🔐 index.html sha256: ${FRONTEND_HASH}"
    FRONTEND_VALID=true
    
    # Check for assets directory (either _next or static)
    if [ -d packages/web/out/_next ]; then
        echo "✅ Next.js _next directory found"
    elif [ -d packages/web/out/static ]; then
        echo "✅ Static assets directory found"
    else
        echo "⚠️ No asset directory found, but continuing (may be a simple static site)"
    fi
    
    # Copy to fallback paths (simulate /app/out copy)
    mkdir -p /tmp/test_app_out
    cp -r packages/web/out/* /tmp/test_app_out/ 2>/dev/null || true
    echo "📁 Copied build to /tmp/test_app_out (simulating /app/out fallback path)"
else
    echo "⚠️ Frontend verification found no index.html"
    echo "    Expected: packages/web/out/index.html"
    echo "    Continuing with API-only deployment (server will create fallback)"
fi

# Test results
echo ""
echo "📊 Test Results Summary"
echo "====================="
echo "Build Success: $BUILD_SUCCESS"
echo "Frontend Valid: $FRONTEND_VALID"

if [ "$FRONTEND_VALID" = "true" ]; then
    FILES_COUNT=$(find packages/web/out -type f | wc -l)
    echo "Files created: $FILES_COUNT"
    echo "Sample files:"
    ls -la packages/web/out/ | head -5
    
    echo ""
    echo "Fallback copy verification:"
    FALLBACK_FILES=$(find /tmp/test_app_out -type f | wc -l 2>/dev/null || echo "0")
    echo "Fallback files: $FALLBACK_FILES"
fi

if [ "$FRONTEND_VALID" = "true" ]; then
    echo "🎉 SUCCESS: Railway deployment simulation passed!"
    echo "   Frontend build process completed successfully"
    echo "   Files are properly placed for server to find them"
    exit 0
else
    echo "❌ FAILURE: Railway deployment simulation failed"
    echo "   Frontend build process did not complete successfully"
    exit 1
fi