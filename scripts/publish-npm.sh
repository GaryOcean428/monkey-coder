#!/bin/bash
# Publish Monkey Coder CLI to npm

set -e

echo "🐒 Publishing Monkey Coder CLI to npm..."

# Set npm token
echo "//registry.npmjs.org/:_authToken=${NPM_ACCESS_TOKEN}" > ~/.npmrc

# Change to CLI package directory
cd packages/cli

# Build the package
echo "📦 Building CLI package..."
yarn build

# Update version if needed (optional - can be done manually)
# npm version patch

# Publish to npm
echo "🚀 Publishing to npm..."
npm publish --access public

echo "✅ Successfully published to npm!"
echo "📦 Install with: npm install -g @monkey-coder/cli"
echo "🚀 Run with: monkey --help"

# Clean up
rm -f ~/.npmrc

echo "🎉 Done!"
