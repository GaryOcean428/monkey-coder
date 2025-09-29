#!/bin/bash

# Monkey Coder Package Publishing Script
# This script publishes updated packages to npm and PyPI

set -e

echo "🐒 Monkey Coder Package Publishing Script"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [[ ! -f "package.json" ]] || [[ ! "$(cat package.json | grep -o '"name": "monkey-coder"')" ]]; then
    echo "❌ Error: Must be run from the monkey-coder repository root"
    exit 1
fi

echo "📋 Package Update Summary:"
echo "• monkey-coder-cli (NPM): v1.5.0 (enhanced CLI UX)"
echo "• monkey-coder-sdk (NPM): v1.3.6 (needs update from v1.3.4)"
echo "• monkey-coder-core (PyPI): v1.2.0 (enhanced backend API)"
echo "• monkey-coder-sdk (PyPI): v1.1.0 (needs update from v1.0.1)"
echo ""

# Confirm with user
read -p "🤔 Do you want to proceed with publishing? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Publishing cancelled"
    exit 1
fi

echo "🔧 Setting up publishing environment..."

# Install publishing tools if needed
if ! command -v twine &> /dev/null; then
    echo "📦 Installing Python publishing tools..."
    pip install --user build twine
fi

# Build all packages first
echo "🏗️  Building all packages..."
yarn build

# Test packages
echo "🧪 Running tests..."
yarn test

echo "📦 Publishing packages..."
echo ""

# 1. Publish NPM packages that need updates
echo "🚀 Publishing NPM packages..."

echo "📤 Publishing monkey-coder-sdk v1.3.6..."
cd packages/sdk
yarn build:ts
if npm publish --access public --dry-run; then
    npm publish --access public
    echo "✅ monkey-coder-sdk v1.3.6 published to npm"
else
    echo "❌ Failed to publish monkey-coder-sdk"
    exit 1
fi
cd ../..

# monkey-coder-cli is already up to date, skip it
echo "📤 Publishing monkey-coder-cli v1.5.0 (enhanced UX)..."
cd packages/cli
yarn build
if npm publish --access public --dry-run; then
    npm publish --access public
    echo "✅ monkey-coder-cli v1.5.0 published to npm"
else
    echo "❌ Failed to publish monkey-coder-cli"
    exit 1
fi
cd ../..

echo ""

# 2. Publish Python packages
echo "🚀 Publishing Python packages..."

echo "📤 Publishing monkey-coder-core v1.2.0..."
cd packages/core
rm -rf dist/  # Clean previous builds
python -m build
if twine check dist/*; then
    twine upload dist/*
    echo "✅ monkey-coder-core v1.2.0 published to PyPI"
else
    echo "❌ Failed to publish monkey-coder-core"
    exit 1
fi
cd ../..

echo "📤 Publishing monkey-coder-sdk (Python) v1.1.0..."
cd packages/sdk/src/python
rm -rf dist/  # Clean previous builds
python -m build
if twine check dist/*; then
    twine upload dist/*
    echo "✅ monkey-coder-sdk (Python) v1.1.0 published to PyPI"
else
    echo "❌ Failed to publish monkey-coder-sdk (Python)"
    exit 1
fi
cd ../../../..

echo ""
echo "🎉 All packages published successfully!"
echo ""

# Verification
echo "🔍 Verifying published packages..."
echo "You can verify the publications at:"
echo "• npm: https://www.npmjs.com/package/monkey-coder-sdk"
echo "• PyPI: https://pypi.org/project/monkey-coder-core/"
echo "• PyPI: https://pypi.org/project/monkey-coder-sdk/"
echo ""

echo "📋 Post-publishing checklist:"
echo "• ✅ Packages built and tested successfully"
echo "• ✅ NPM package monkey-coder-cli v1.5.0 published"
echo "• ✅ NPM package monkey-coder-sdk v1.3.6 published"
echo "• ✅ PyPI package monkey-coder-core v1.2.0 published"
echo "• ✅ PyPI package monkey-coder-sdk v1.1.0 published"
echo ""

echo "🎯 All monkey-coder packages are now up to date!"
