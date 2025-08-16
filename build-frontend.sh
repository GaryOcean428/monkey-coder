#!/bin/bash

# Build frontend for deployment
echo "🚀 Building frontend for deployment..."

# Enable Yarn 4.9.2
echo "📦 Enabling Yarn 4.9.2..."
corepack enable
corepack prepare yarn@4.9.2 --activate

# Install dependencies
echo "📦 Installing dependencies..."
yarn install

# Build and export the Next.js frontend
echo "🏗️ Building Next.js frontend..."
yarn workspace @monkey-coder/web export

# Verify the build
if [ -d "packages/web/out" ]; then
  echo "✅ Frontend build complete!"
  echo "📁 Build output:"
  ls -la packages/web/out/ | head -10
else
  echo "❌ Frontend build failed - output directory not found"
  exit 1
fi