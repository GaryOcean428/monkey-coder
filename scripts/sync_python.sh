#!/usr/bin/env bash
# Sync Python dependencies using uv (https://github.com/astral-sh/uv)
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
fi

# Generate/refresh lock
uv pip compile pyproject.toml -o requirements.lock || true
# Sync environment
uv pip sync requirements.txt

echo "Python dependencies synchronized via uv."