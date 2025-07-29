#!/usr/bin/env bash
set -euo pipefail

REPO="GaryOcean428/monkey-coder"
ENV_NAME="copilot"   # <— replace with your environment name
ENV_FILE=".env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "❌ $ENV_FILE not found!"
  exit 1
fi

while IFS='=' read -r KEY VALUE; do
  # Skip blank lines or comments
  [[ -z "$KEY" ]] && continue
  [[ "$KEY" == \#* ]] && continue

  echo "Uploading secret: $KEY to environment: $ENV_NAME"
  echo -n "$VALUE" | gh secret set "$KEY" --repo "$REPO" --env "$ENV_NAME"
done < "$ENV_FILE"

echo "✅ All environment secrets uploaded successfully."
