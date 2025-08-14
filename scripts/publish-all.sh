#!/bin/bash

# Monkey Coder - Package Version Checker and Publishing Helper
# This script checks versions and helps publish packages

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Function to print colored messages
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Main execution
echo "======================================"
echo "  Monkey Coder Package Version Check"
echo "======================================"
echo ""

log_info "Checking local versions..."
echo ""
echo "Local Versions:"
echo "  CLI (npm):        $(grep '"version"' $ROOT_DIR/packages/cli/package.json | cut -d'"' -f4)"
echo "  SDK (npm):        $(grep '"version"' $ROOT_DIR/packages/sdk/package.json | cut -d'"' -f4)"
echo "  Core (PyPI):      $(grep '^version = ' $ROOT_DIR/packages/core/pyproject.toml | cut -d'"' -f2)"
echo "  SDK Python:       $(grep 'version=' $ROOT_DIR/packages/sdk/src/python/setup.py | head -1 | sed 's/.*version="\([^"]*\)".*/\1/')"

echo ""
log_info "Checking published versions..."
echo ""
echo "Published Versions:"
echo "  CLI (npm):        $(npm view monkey-coder-cli version 2>/dev/null || echo 'Not published')"
echo "  SDK (npm):        $(npm view monkey-coder-sdk version 2>/dev/null || echo 'Not published')"
echo "  Core (PyPI):      $(pip index versions monkey-coder-core 2>/dev/null | head -1 | sed 's/.*(\([^)]*\)).*/\1/' || echo 'Not published')"
echo "  SDK (PyPI):       $(pip index versions monkey-coder-sdk 2>/dev/null | head -1 | sed 's/.*(\([^)]*\)).*/\1/' || echo 'Not published')"

echo ""
echo "======================================"
log_success "Version check complete!"
echo ""
echo "Publishing Instructions:"
echo ""
echo "1. For npm packages:"
echo "   cd packages/cli && npm publish"
echo "   cd packages/sdk && npm publish"
echo ""
echo "2. For PyPI packages:"
echo "   cd packages/core && python -m build && twine upload dist/*"
echo "   cd packages/sdk/src/python && python setup.py sdist bdist_wheel && twine upload dist/*"
echo "======================================"
