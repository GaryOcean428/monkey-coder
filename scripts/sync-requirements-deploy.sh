#!/usr/bin/env bash
# Sync requirements-deploy.txt from root to services/backend
# This ensures Railway backend deployments have access to the requirements file.

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT=$(dirname "$(dirname "${BASH_SOURCE[0]}")")
cd "$PROJECT_ROOT"

ROOT_REQ="requirements-deploy.txt"
BACKEND_REQ="services/backend/requirements-deploy.txt"

echo "📋 Syncing requirements-deploy.txt to services/backend..."

if [[ ! -f "$ROOT_REQ" ]]; then
    echo "❌ ERROR: $ROOT_REQ not found!" >&2
    exit 1
fi

# Create backup if target exists
if [[ -f "$BACKEND_REQ" ]]; then
    BACKUP="${BACKEND_REQ}.backup"
    cp "$BACKEND_REQ" "$BACKUP"
    echo -e "${YELLOW}ℹ️  Backup created: $BACKUP${NC}"
fi

# Copy file
cp "$ROOT_REQ" "$BACKEND_REQ"
echo -e "${GREEN}✅ Successfully synced $ROOT_REQ → $BACKEND_REQ${NC}"

# Verify the copy
if diff -q "$ROOT_REQ" "$BACKEND_REQ" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Verification successful - files are identical${NC}"
    
    # Show git status
    if git diff --quiet "$BACKEND_REQ" 2>/dev/null; then
        echo "ℹ️  No changes detected (files were already in sync)"
    else
        echo ""
        echo "📝 Changes detected. To commit:"
        echo "   git add $BACKEND_REQ"
        echo "   git commit -m 'Sync backend requirements-deploy.txt'"
    fi
else
    echo "❌ ERROR: Verification failed - copy was unsuccessful" >&2
    exit 1
fi
