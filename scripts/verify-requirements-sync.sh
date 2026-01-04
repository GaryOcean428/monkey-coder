#!/usr/bin/env bash
# Verify that requirements-deploy.txt is in sync between root and services/backend
# This prevents Railway deployment failures due to missing or outdated requirements files.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT=$(dirname "$(dirname "${BASH_SOURCE[0]}")")
cd "$PROJECT_ROOT"

ROOT_REQ="requirements-deploy.txt"
BACKEND_REQ="services/backend/requirements-deploy.txt"

echo "🔍 Verifying requirements-deploy.txt sync..."

# Check if both files exist
if [[ ! -f "$ROOT_REQ" ]]; then
    echo -e "${RED}❌ ERROR: $ROOT_REQ not found!${NC}" >&2
    exit 1
fi

if [[ ! -f "$BACKEND_REQ" ]]; then
    echo -e "${RED}❌ ERROR: $BACKEND_REQ not found!${NC}" >&2
    echo -e "${YELLOW}💡 Run: cp $ROOT_REQ $BACKEND_REQ${NC}" >&2
    exit 1
fi

# Check if files are identical
if diff -q "$ROOT_REQ" "$BACKEND_REQ" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Requirements files are in sync${NC}"
    exit 0
else
    echo -e "${RED}❌ ERROR: Requirements files are OUT OF SYNC!${NC}" >&2
    echo "" >&2
    echo "Differences found between:" >&2
    echo "  - $ROOT_REQ" >&2
    echo "  - $BACKEND_REQ" >&2
    echo "" >&2
    echo -e "${YELLOW}To fix this, run:${NC}" >&2
    echo "  cp $ROOT_REQ $BACKEND_REQ" >&2
    echo "" >&2
    echo "Then commit the updated file:" >&2
    echo "  git add $BACKEND_REQ" >&2
    echo "  git commit -m 'Sync backend requirements-deploy.txt'" >&2
    echo "" >&2
    echo "Showing diff:" >&2
    diff -u "$ROOT_REQ" "$BACKEND_REQ" | head -50 || true
    exit 1
fi
