#!/usr/bin/env bash
# Audit environment variables to separate build-time vs runtime-only usage.
# Usage: ./scripts/filter_build_vars.sh

set -euo pipefail

echo "=== Essential Build-Time Variables (consider keeping at build) ==="
echo "DATABASE_URL     - only if running migrations at build time (not recommended)"
echo "REDIS_URL        - only if build performs connectivity checks (avoid if possible)"
echo "RAILWAY_ENVIRONMENT - if your build logic branches by environment (rare)"
echo "PYTHONPATH       - for module resolution during build if needed"
echo

echo "=== Runtime-Only Variables (should NOT be passed to BuildKit) ==="
env | grep -E "_KEY=|_TOKEN=|_SECRET=|_API=|STRIPE_|OPENAI_|ANTHROPIC_|AWS_|GCP_|GOOGLE_|AZURE_" | cut -d= -f1 | sort -u || true
echo

echo "Total env vars: $(env | wc -l | awk '{print $1}')"
echo "Sensitive-pattern matches (to keep runtime-only): $(env | grep -E '_KEY=|_TOKEN=|_SECRET=|_API=|STRIPE_|OPENAI_|ANTHROPIC_|AWS_|GCP_|GOOGLE_|AZURE_' | wc -l | awk '{print $1}')"
echo
echo "Note:"
echo "- railpack.json now uses an explicit secrets list to prevent auto-propagation of ALL service variables to BuildKit."
echo "- Keep build-time secrets to an absolute minimum (ideally zero)."
