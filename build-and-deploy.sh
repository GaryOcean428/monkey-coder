#!/bin/bash
# Build and Deploy Script for Railway
# Handles both frontend build and backend preparation

set -e  # Exit on error

echo "🚀 Starting unified build process..."

# 1. Install Node dependencies using Yarn
echo "📦 Installing Node.js dependencies..."
corepack enable
corepack prepare yarn@4.9.2 --activate
yarn install --immutable

# 2. Build the Next.js frontend
echo "🏗️ Building Next.js frontend..."
cd packages/web
yarn build
cd ../..

# 3. Verify frontend build
if [ -d "packages/web/out" ]; then
    echo "✅ Frontend build successful!"
    echo "   Found $(find packages/web/out -type f | wc -l) files"
    ls -la packages/web/out/ | head -10
else
    echo "❌ Frontend build failed - directory not found!"
    exit 1
fi

# 4. Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt
cd packages/core
pip install --no-cache-dir -e .
cd ../..

# 5. Run database migrations
echo "🗄️ Running database migrations..."
python -c "from monkey_coder.database import run_migrations; import asyncio; asyncio.run(run_migrations())" || echo "⚠️ Migrations skipped"

echo "✅ Build process complete!"
echo "   Frontend: packages/web/out/"
echo "   Backend: Ready to start"
