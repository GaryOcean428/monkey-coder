#!/bin/bash
# Python package build wrapper with error handling

set -e

CORE_DIR="packages/core"

echo "🐍 Building Python packages..."

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "Using uv for faster builds..."
    cd "${CORE_DIR}"
    uv build
else
    echo "Using standard Python build..."
    cd "${CORE_DIR}"
    python -m build
fi

cd -

echo "✅ Python build complete"
ls -lh "${CORE_DIR}/dist/"
