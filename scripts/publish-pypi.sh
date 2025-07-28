#!/bin/bash
# Publish Monkey Coder Core and SDK to PyPI

set -e

# Check if PYPI_TOKEN is set
if [ -z "$PYPI_TOKEN" ]; then
    echo "❌ Error: PYPI_TOKEN environment variable is not set"
    echo "Please set: export PYPI_TOKEN='your-token'"
    exit 1
fi

echo "🐒 Publishing Monkey Coder packages to PyPI..."

# Install publishing dependencies
pip install --upgrade build twine

# Clean up any previous builds
echo "🧹 Cleaning up previous builds..."
rm -rf packages/core/dist packages/core/build packages/core/*.egg-info
rm -rf packages/sdk/src/python/dist packages/sdk/src/python/build packages/sdk/src/python/*.egg-info

# Publish Core Package
echo "📦 Building and publishing core package..."
cd packages/core
python -m build
echo "📤 Uploading monkey-coder-core to PyPI..."
python -m twine upload dist/* -u __token__ -p "${PYPI_TOKEN}" --verbose
cd ../..

# Publish SDK Package (Python)
echo "📦 Building and publishing Python SDK package..."
cd packages/sdk/src/python
python -m build
echo "📤 Uploading monkey-coder-sdk to PyPI..."
python -m twine upload dist/* -u __token__ -p "${PYPI_TOKEN}" --verbose
cd ../../../..

echo "✅ Successfully published to PyPI!"
echo "📦 Install core with: pip install monkey-coder-core"
echo "📦 Install SDK with: pip install monkey-coder-sdk"
echo "🚀 Run with: monkey-coder --help"

echo "🎉 Done!"
