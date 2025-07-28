#!/bin/bash

# NPM Publishing Script for @monkey-coder/cli
# This script publishes the TypeScript CLI package to NPM

set -e

echo "🐒 Monkey Coder NPM Publishing"
echo "=============================="

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

# Check if NPM token is set
if [ -z "$NPM_ACCESS_TOKEN" ]; then
    print_status "error" "NPM_ACCESS_TOKEN environment variable not set"
    echo "Please set your NPM token:"
    echo "  export NPM_ACCESS_TOKEN='your-npm-token'"
    exit 1
fi

# Check if package.json exists
if [ ! -f "packages/cli/package.json" ]; then
    print_status "error" "packages/cli/package.json not found"
    exit 1
fi

# Get current version
CURRENT_VERSION=$(node -p "require('./packages/cli/package.json').version")
print_status "info" "Current version: $CURRENT_VERSION"

# Install dependencies using Yarn
print_status "info" "Installing dependencies..."
yarn install

# Run tests for the CLI workspace
print_status "info" "Running tests..."
yarn workspace @monkey-coder/cli test || print_status "warning" "No tests found or tests failed"

# Build the package
print_status "info" "Building package..."
yarn workspace @monkey-coder/cli build

# Check if dist directory exists
if [ ! -d "packages/cli/dist" ]; then
    print_status "error" "Build failed - dist directory not found"
    exit 1
fi

# Configure NPM for Yarn
print_status "info" "Configuring NPM..."
yarn config set npmRegistryServer "https://registry.npmjs.org"
yarn config set npmAuthToken "$NPM_ACCESS_TOKEN"

# Check if we're logged in
NPM_USER=$(yarn npm whoami 2>/dev/null || echo "")
if [ -z "$NPM_USER" ]; then
    print_status "error" "NPM authentication failed"
    exit 1
fi
print_status "success" "Authenticated as: $NPM_USER"

# Ask for confirmation
echo -e "\n${YELLOW}Ready to publish @monkey-coder/cli version $CURRENT_VERSION${NC}"
echo "Package will be published with public access"
read -p "Do you want to continue? (y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "warning" "Publishing cancelled"
    exit 0
fi

# Publish the package
print_status "info" "Publishing to NPM..."
yarn workspace @monkey-coder/cli npm publish --access public

if [ $? -eq 0 ]; then
    print_status "success" "Package published successfully! 🎉"
    echo -e "\nPackage URL: https://www.npmjs.com/package/@monkey-coder/cli"
    echo -e "Install with: npm install -g @monkey-coder/cli"
else
    print_status "error" "Publishing failed"
    exit 1
fi

# Tag the release in git
if command -v git >/dev/null 2>&1; then
    TAG_NAME="cli-v$CURRENT_VERSION"
    print_status "info" "Creating git tag: $TAG_NAME"
    git tag -a "$TAG_NAME" -m "Release @monkey-coder/cli v$CURRENT_VERSION"
    print_status "info" "Don't forget to push the tag: git push origin $TAG_NAME"
fi

print_status "success" "NPM publishing complete!"
