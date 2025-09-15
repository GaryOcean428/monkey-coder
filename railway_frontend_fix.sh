#!/bin/bash
# Railway Frontend Fix Script
# This script ensures the frontend is properly built and served in Railway production

set -e  # Exit on any error

echo "🚀 Railway Frontend Fix Script Starting..."
echo "   Current working directory: $(pwd)"
echo "   Environment: ${RAILWAY_ENVIRONMENT:-unknown}"
echo "   Public domain: ${RAILWAY_PUBLIC_DOMAIN:-unknown}"

# Step 1: Check current directory structure
echo ""
echo "📂 Checking current directory structure..."
ls -la | head -20

# Step 2: Verify package.json and web directory exist
if [ ! -f "package.json" ]; then
    echo "❌ ERROR: package.json not found in current directory"
    echo "   This script must be run from the repository root"
    exit 1
fi

if [ ! -d "packages/web" ]; then
    echo "❌ ERROR: packages/web directory not found"
    echo "   Expected structure: packages/web/"
    exit 1
fi

echo "✅ Repository structure verified"

# Step 3: Setup environment variables with Railway defaults
echo ""
echo "🔧 Setting up environment variables..."

# Base URL from Railway or fallback
if [ -n "$RAILWAY_PUBLIC_DOMAIN" ]; then
    BASE_URL="https://$RAILWAY_PUBLIC_DOMAIN"
elif [ -n "$NEXT_PUBLIC_API_URL" ]; then
    BASE_URL="$NEXT_PUBLIC_API_URL"
else
    BASE_URL="https://coder.fastmonkey.au"
fi

export NEXT_OUTPUT_EXPORT=true
export NODE_ENV=production
export NEXT_TELEMETRY_DISABLED=1
export NEXTAUTH_URL="${NEXTAUTH_URL:-$BASE_URL}"
export NEXTAUTH_SECRET="${NEXTAUTH_SECRET:-railway-fix-secret-$(date +%s)}"
export NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-$BASE_URL}"
export NEXT_PUBLIC_APP_URL="${NEXT_PUBLIC_APP_URL:-$BASE_URL}"
export DATABASE_URL="${DATABASE_URL:-postgresql://railway.internal:5432/railway}"
export STRIPE_PUBLIC_KEY="${STRIPE_PUBLIC_KEY:-pk_test_placeholder}"
export STRIPE_SECRET_KEY="${STRIPE_SECRET_KEY:-sk_test_placeholder}"
export STRIPE_WEBHOOK_SECRET="${STRIPE_WEBHOOK_SECRET:-whsec_placeholder}"

echo "✅ Environment configured with BASE_URL: $BASE_URL"

# Step 4: Setup Yarn package manager
echo ""
echo "📦 Setting up Yarn package manager..."
if command -v corepack >/dev/null 2>&1; then
    echo "   Enabling corepack..."
    corepack enable
    echo "   Preparing Yarn 4.9.2..."
    corepack prepare yarn@4.9.2 --activate
    echo "✅ Yarn setup completed"
else
    echo "⚠️ Corepack not available, trying npm install -g yarn"
    npm install -g yarn@4.9.2 || echo "⚠️ Yarn installation failed"
fi

# Step 5: Install dependencies
echo ""
echo "📦 Installing dependencies..."
echo "   Running: yarn install"
if yarn install --immutable; then
    echo "✅ Dependencies installed (immutable mode)"
elif yarn install; then
    echo "✅ Dependencies installed (standard mode)"
else
    echo "❌ ERROR: Failed to install dependencies"
    exit 1
fi

# Step 6: Build frontend with multiple fallback methods
echo ""
echo "🏗️ Building frontend..."

# Method 1: Workspace export
echo "   Method 1: Trying workspace export..."
if yarn workspace @monkey-coder/web run export; then
    echo "✅ Workspace export succeeded"
    BUILD_SUCCESS=true
else
    echo "⚠️ Workspace export failed, trying alternative methods..."
    BUILD_SUCCESS=false
    
    # Method 2: Direct export in web directory
    echo "   Method 2: Trying direct export..."
    cd packages/web
    if yarn run export; then
        echo "✅ Direct export succeeded"
        BUILD_SUCCESS=true
        cd ../..
    else
        echo "⚠️ Direct export failed, trying simple build..."
        
        # Method 3: Simple build + manual copy
        echo "   Method 3: Trying simple build..."
        if yarn run build; then
            echo "✅ Simple build succeeded"
            
            # Check if we need to copy .next to out
            if [ -d ".next" ] && [ ! -d "out" ]; then
                echo "   Copying .next to out directory..."
                cp -r .next out 2>/dev/null || {
                    echo "   Creating out directory manually..."
                    mkdir -p out
                    # Copy essential files
                    [ -f ".next/index.html" ] && cp .next/index.html out/ 2>/dev/null
                    [ -d ".next/static" ] && cp -r .next/static out/ 2>/dev/null
                    [ -d ".next/_next" ] && cp -r .next/_next out/ 2>/dev/null
                }
            fi
            BUILD_SUCCESS=true
        else
            echo "❌ All build methods failed"
        fi
        cd ../..
    fi
fi

# Step 7: Verify build output
echo ""
echo "🔍 Verifying build output..."
OUT_DIR="packages/web/out"
if [ -d "$OUT_DIR" ] && [ "$(ls -A $OUT_DIR 2>/dev/null)" ]; then
    FILE_COUNT=$(find $OUT_DIR -type f | wc -l)
    HTML_COUNT=$(find $OUT_DIR -name "*.html" | wc -l)
    echo "✅ Build output verified:"
    echo "   Directory: $OUT_DIR"
    echo "   Total files: $FILE_COUNT"
    echo "   HTML files: $HTML_COUNT"
    echo "   Contents preview:"
    ls -la $OUT_DIR | head -10
    
    # Check for critical files
    if [ -f "$OUT_DIR/index.html" ]; then
        INDEX_SIZE=$(stat -f%z "$OUT_DIR/index.html" 2>/dev/null || stat -c%s "$OUT_DIR/index.html" 2>/dev/null || echo "unknown")
        echo "   ✅ index.html found (${INDEX_SIZE} bytes)"
    else
        echo "   ⚠️ index.html not found"
    fi
    
    FRONTEND_READY=true
else
    echo "❌ No build output found in $OUT_DIR"
    FRONTEND_READY=false
fi

# Step 8: Test if Python server can find the frontend
echo ""
echo "🧪 Testing frontend detection..."
python3 -c "
import os
from pathlib import Path

# Check static directory locations (same as run_server.py)
static_dir_options = [
    Path('/app/packages/web/out'),
    Path('/app/out'),
    Path.cwd() / 'packages' / 'web' / 'out',
    Path.cwd() / 'out',
]

found = False
for option in static_dir_options:
    if option.exists():
        print(f'✅ Frontend found at: {option}')
        file_count = len(list(option.glob('*')))
        print(f'   Contains {file_count} files')
        found = True
        break

if not found:
    print('❌ Frontend not found in any expected location')
    print('Expected locations:')
    for option in static_dir_options:
        print(f'  - {option} (exists: {option.exists()})')
"

# Step 9: Summary and next steps
echo ""
echo "📋 Railway Frontend Fix Summary"
echo "================================"
echo "Build Success: ${BUILD_SUCCESS:-false}"
echo "Frontend Ready: ${FRONTEND_READY:-false}"
echo "Base URL: $BASE_URL"
echo "Environment: ${RAILWAY_ENVIRONMENT:-unknown}"
echo ""

if [ "$FRONTEND_READY" = "true" ]; then
    echo "✅ SUCCESS: Frontend should now be available!"
    echo ""
    echo "Next steps:"
    echo "1. Restart your Railway service to pick up the new frontend"
    echo "2. Visit your Railway domain to verify the frontend loads"
    echo "3. Check Railway service logs for any runtime issues"
    echo ""
    echo "If the frontend still doesn't appear:"
    echo "- Verify Railway is using railpack.json (not Nixpacks)"
    echo "- Check Railway environment variables are set correctly"
    echo "- Ensure the Railway service restart picked up the new files"
else
    echo "❌ PARTIAL SUCCESS: Build completed but frontend may not be ready"
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Check the build logs above for specific errors"
    echo "2. Verify all required environment variables are set in Railway"
    echo "3. Try running the build manually in the Railway service shell"
    echo "4. Consider using the unified deployment (run_unified.js) instead"
fi

echo ""
echo "🔧 For Railway deployment troubleshooting:"
echo "   - Railway Dashboard: Check build logs and environment variables"
echo "   - Health Check: $BASE_URL/health"
echo "   - API Docs: $BASE_URL/api/docs"
echo "   - Runtime Logs: railway logs"
echo ""
echo "Railway Frontend Fix Script Completed"