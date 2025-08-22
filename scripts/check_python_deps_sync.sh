#!/usr/bin/env bash
set -euo pipefail

# Simple dependency drift detector between pyproject.toml (uv authoritative) and requirements.txt
# Usage: ./scripts/check_python_deps_sync.sh [--fix]
# If --fix is passed, regenerates requirements.txt from uv export.

PROJECT_ROOT=$(dirname "$(dirname "${BASH_SOURCE[0]}")")
cd "$PROJECT_ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: uv not installed. Install via: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 2
fi

TMP_REQ=$(mktemp)
trap 'rm -f "$TMP_REQ"' EXIT

# Export current lock / resolution to pinned requirements
# Include PyTorch CPU index for torch dependencies with +cpu suffix
uv pip compile pyproject.toml --extra-index-url https://download.pytorch.org/whl/cpu --quiet -o "$TMP_REQ" || {
  echo "Failed to compile dependencies via uv" >&2
  exit 3
}

# Normalize the header comment to avoid false diffs due to temp file paths
sed -i 's|#    uv pip compile pyproject.toml.*|#    uv pip compile pyproject.toml|' "$TMP_REQ"

if ! diff -u requirements.txt "$TMP_REQ" >/dev/null 2>&1; then
  echo "Dependency drift detected between pyproject.toml and requirements.txt" >&2
  if [[ ${1:-} == "--fix" ]]; then
    mv "$TMP_REQ" requirements.txt
    echo "requirements.txt updated from pyproject.toml"
    exit 0
  else
    echo "Run ./scripts/check_python_deps_sync.sh --fix to update requirements.txt" >&2
    # Show brief diff but limit to first 100 lines
    diff -u requirements.txt "$TMP_REQ" | head -n 100
    exit 1
  fi
else
  echo "Dependencies are in sync."
fi
