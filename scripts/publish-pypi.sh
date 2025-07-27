#!/bin/bash
# Publish Monkey Coder Core and SDK to PyPI

set -e

echo "🐒 Publishing Monkey Coder packages to PyPI..."

# Install publishing dependencies
pip install --upgrade build twine

# Publish Core Package
echo "📦 Building and publishing core package..."
cd packages/core
python -m build
python -m twine upload dist/* -u __token__ -p "${PYPI_TOKEN}"
cd ../..

# Publish SDK Package
echo "📦 Building and publishing SDK package..."
cd packages/sdk
python -m build
python -m twine upload dist/* -u __token__ -p "${PYPI_TOKEN}"
cd ../..

echo "✅ Successfully published to PyPI!"
echo "📦 Install core with: pip install monkey-coder-core"
echo "📦 Install SDK with: pip install monkey-coder-sdk"
echo "🚀 Run with: monkey-coder --help"

echo "🎉 Done!"
