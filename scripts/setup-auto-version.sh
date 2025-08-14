#!/bin/bash

# Setup script for automatic version bumping

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Setting up automatic version bumping...${NC}"

# Set git hooks path
git config core.hooksPath .githooks

echo -e "${GREEN}✅ Git hooks configured!${NC}"
echo ""
echo "Automatic version bumping is now enabled!"
echo ""
echo "How it works:"
echo "  • Every commit will auto-increment patch versions"
echo "  • Changed packages get version bumps automatically"
echo "  • Add [skip version] to commit message to skip"
echo "  • Add [skip ci] to skip GitHub publishing"
echo ""
echo "Examples:"
echo "  git commit -m 'feat: add new feature'           # Auto-bumps version"
echo "  git commit -m 'docs: update README [skip ci]'   # No version bump or publish"
echo "  git commit -m 'fix: typo [skip version]'        # No version bump"
echo ""
echo -e "${YELLOW}Note: You can manually set versions before committing if needed${NC}"