#!/bin/bash
# Master script to publish all Monkey Coder packages

set -e

echo "🐒 Monkey Coder Package Publisher"
echo "================================="

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "📋 Loading environment variables from .env..."
    export $(grep -v '^#' .env | xargs)
fi

# Check if tokens are set
if [ -z "$PYPI_TOKEN" ]; then
    echo "❌ Error: PYPI_TOKEN not found in environment"
    echo "Please ensure it's set in your .env file or environment"
    exit 1
fi

if [ -z "$NPM_ACCESS_TOKEN" ]; then
    echo "❌ Error: NPM_ACCESS_TOKEN not found in environment"
    echo "Please ensure it's set in your .env file or environment"
    exit 1
fi

echo "✅ All required tokens found"
echo ""

# Run validation first
echo "🔍 Running package validation..."
./scripts/validate-packages.sh
if [ $? -ne 0 ]; then
    echo "❌ Package validation failed. Please fix the issues before publishing."
    exit 1
fi

echo ""
echo "📦 Package validation passed! Ready to publish."
echo ""

# Ask for confirmation
read -p "Do you want to publish all packages? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Publishing cancelled."
    exit 1
fi

echo ""
echo "🐍 Publishing Python packages to PyPI..."
./scripts/publish-pypi.sh
if [ $? -ne 0 ]; then
    echo "❌ PyPI publishing failed."
    exit 1
fi

echo ""
echo "📦 Publishing npm packages..."
./scripts/publish-npm.sh
if [ $? -ne 0 ]; then
    echo "❌ npm publishing failed."
    exit 1
fi

echo ""
echo "🎉 All packages published successfully!"
echo ""
echo "📋 Installation commands:"
echo "  Python:"
echo "    pip install monkey-coder-core"
echo "    pip install monkey-coder-sdk"
echo ""
echo "  npm:"
echo "    npm install -g monkey-coder-cli"
echo "    npm install @monkey-coder/sdk"
echo ""
echo "✨ Happy coding with Monkey Coder!"
