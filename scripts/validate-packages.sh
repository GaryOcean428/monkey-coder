#!/bin/bash

# Package validation script for Monkey Coder
# Validates both Python (PyPI) and TypeScript (NPM) packages before publishing

set -e

echo "🐒 Monkey Coder Package Validation"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ "$1" = "error" ]; then
        echo -e "${RED}❌ $2${NC}"
    elif [ "$1" = "success" ]; then
        echo -e "${GREEN}✅ $2${NC}"
    elif [ "$1" = "warning" ]; then
        echo -e "${YELLOW}⚠️  $2${NC}"
    else
        echo "$2"
    fi
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate Python package
validate_python_package() {
    echo -e "\n📦 Validating Python Package (monkey-coder-core)"
    echo "------------------------------------------------"
    
    cd packages/core
    
    # Check pyproject.toml exists
    if [ ! -f "pyproject.toml" ]; then
        print_status "error" "pyproject.toml not found"
        return 1
    fi
    print_status "success" "pyproject.toml found"
    
    # Check Python version
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_status "success" "Python version: $PYTHON_VERSION"
    else
        print_status "error" "Python 3 not found"
        return 1
    fi
    
    # Check package version
    # Try with tomllib (Python 3.11+) first, then tomli, then grep as fallback
    PACKAGE_VERSION=$(python3 -c "
try:
    import tomllib
    with open('pyproject.toml', 'rb') as f:
        data = tomllib.load(f)
    print(data['project']['version'])
except ImportError:
    try:
        import tomli
        with open('pyproject.toml', 'rb') as f:
            data = tomli.load(f)
        print(data['project']['version'])
    except ImportError:
        print('unknown')
" 2>/dev/null || echo "unknown")
    
    if [ "$PACKAGE_VERSION" = "unknown" ]; then
        # Fallback to grep
        PACKAGE_VERSION=$(grep -m1 '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/' 2>/dev/null || echo "unknown")
    fi
    
    if [ "$PACKAGE_VERSION" != "unknown" ]; then
        print_status "success" "Package version: $PACKAGE_VERSION"
    else
        print_status "warning" "Could not parse package version"
    fi
    
    # Check required files
    REQUIRED_FILES=("README.md" "LICENSE" "monkey_coder/__init__.py")
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            print_status "success" "Required file exists: $file"
        else
            print_status "error" "Required file missing: $file"
            return 1
        fi
    done
    
    # Check package structure
    REQUIRED_MODULES=("agents" "mcp" "core" "models.py" "utils")
    for module in "${REQUIRED_MODULES[@]}"; do
        if [ -e "monkey_coder/$module" ]; then
            print_status "success" "Module exists: monkey_coder/$module"
        else
            print_status "error" "Module missing: monkey_coder/$module"
            return 1
        fi
    done
    
    # Validate imports
    echo -e "\n🔍 Validating Python imports..."
    python3 ../../scripts/validate-imports.py
    if [ $? -eq 0 ]; then
        print_status "success" "All imports validated successfully"
    else
        print_status "error" "Import validation failed"
        return 1
    fi
    
    # Check if package can be built
    echo -e "\n🏗️  Testing package build..."
    if command_exists pip; then
        pip install --quiet build
        python3 -m build --wheel --outdir dist_test/ > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            print_status "success" "Package builds successfully"
            rm -rf dist_test/
        else
            print_status "error" "Package build failed"
            return 1
        fi
    else
        print_status "warning" "pip not found, skipping build test"
    fi
    
    # Check PyPI token
    if [ -n "$PYPI_TOKEN" ]; then
        print_status "success" "PyPI token is set"
    else
        print_status "warning" "PyPI token not found in environment"
    fi
    
    cd ../..
    return 0
}

# Function to validate TypeScript package
validate_typescript_package() {
    echo -e "\n📦 Validating TypeScript Package (@monkey-coder/cli)"
    echo "----------------------------------------------------"
    
    cd packages/cli
    
    # Check package.json exists
    if [ ! -f "package.json" ]; then
        print_status "error" "package.json not found"
        return 1
    fi
    print_status "success" "package.json found"
    
    # Check Node.js version
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_status "success" "Node.js version: $NODE_VERSION"
    else
        print_status "error" "Node.js not found"
        return 1
    fi
    
    # Check package version
    PACKAGE_VERSION=$(node -p "require('./package.json').version" 2>/dev/null || echo "unknown")
    if [ "$PACKAGE_VERSION" != "unknown" ]; then
        print_status "success" "Package version: $PACKAGE_VERSION"
    else
        print_status "warning" "Could not parse package version"
    fi
    
    # Check package name
    PACKAGE_NAME=$(node -p "require('./package.json').name" 2>/dev/null || echo "unknown")
    if [ "$PACKAGE_NAME" = "@monkey-coder/cli" ]; then
        print_status "success" "Package name: $PACKAGE_NAME"
    else
        print_status "error" "Package name should be @monkey-coder/cli, got: $PACKAGE_NAME"
        return 1
    fi
    
    # Check required files
    REQUIRED_FILES=("README.md" "tsconfig.json" "src/cli.ts")
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            print_status "success" "Required file exists: $file"
        else
            print_status "error" "Required file missing: $file"
            return 1
        fi
    done
    
    # Check TypeScript compilation
    echo -e "\n🔨 Testing TypeScript compilation..."
    if command_exists yarn; then
        yarn install --silent > /dev/null 2>&1
        yarn build > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            print_status "success" "TypeScript compiles successfully"
        else
            print_status "error" "TypeScript compilation failed"
            return 1
        fi
    else
        print_status "warning" "Yarn not found, skipping compilation test"
    fi
    
    # Check if dist directory was created
    if [ -d "dist" ]; then
        print_status "success" "Distribution directory created"
    else
        print_status "error" "Distribution directory not found"
        return 1
    fi
    
    # Check NPM token
    if [ -n "$NPM_ACCESS_TOKEN" ]; then
        print_status "success" "NPM token is set"
    else
        print_status "warning" "NPM token not found in environment"
    fi
    
    cd ../..
    return 0
}

# Function to check publishing readiness
check_publishing_readiness() {
    echo -e "\n🚀 Publishing Readiness Check"
    echo "-----------------------------"
    
    # Check git status
    if command_exists git; then
        if [ -z "$(git status --porcelain)" ]; then
            print_status "success" "Git working directory is clean"
        else
            print_status "warning" "Git working directory has uncommitted changes"
        fi
        
        # Check if on main branch
        CURRENT_BRANCH=$(git branch --show-current)
        if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
            print_status "success" "On main branch: $CURRENT_BRANCH"
        else
            print_status "warning" "Not on main branch: $CURRENT_BRANCH"
        fi
    fi
    
    # Check environment variables
    echo -e "\n🔐 Checking credentials..."
    if [ -f ".env" ]; then
        print_status "success" ".env file found"
    else
        print_status "warning" ".env file not found"
    fi
    
    # Summary
    echo -e "\n📊 Validation Summary"
    echo "--------------------"
    
    if [ $PYTHON_VALID -eq 0 ] && [ $TYPESCRIPT_VALID -eq 0 ]; then
        print_status "success" "Both packages are ready for publishing! 🎉"
        echo -e "\nTo publish:"
        echo "  Python:     ./scripts/publish-pypi.sh"
        echo "  TypeScript: ./scripts/publish-npm.sh"
    else
        print_status "error" "Some validation checks failed. Please fix the issues above."
        return 1
    fi
}

# Main execution
main() {
    # Validate Python package
    PYTHON_VALID=1
    validate_python_package
    PYTHON_VALID=$?
    
    # Validate TypeScript package
    TYPESCRIPT_VALID=1
    validate_typescript_package
    TYPESCRIPT_VALID=$?
    
    # Check overall readiness
    check_publishing_readiness
    
    exit $?
}

# Run main function
main
