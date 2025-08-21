#!/usr/bin/env bash
set -euo pipefail

# verify_docs.sh
# Fast documentation hygiene checks for ADR and roadmap markdown.
# 1. Detect hard tab characters
# 2. Detect multiple H1 headings per file
# 3. Optionally run markdownlint if available
# 4. Summarize findings and exit non-zero on violations
#
# Usage:
#   scripts/verify_docs.sh [--fix]
# --fix currently only removes trailing spaces; future hooks may expand.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
DOC_DIRS=("$ROOT_DIR/docs/adr" "$ROOT_DIR/docs/roadmap")
EXIT_CODE=0
FIX=0

if [[ ${1:-} == "--fix" ]]; then
  FIX=1
fi

echo "[verify_docs] Scanning documentation hygiene..."

declare -a TAB_VIOLATIONS
declare -a H1_VIOLATIONS

for dir in "${DOC_DIRS[@]}"; do
  [[ -d "$dir" ]] || continue
  while IFS= read -r -d '' file; do
    rel="${file#$ROOT_DIR/}"
    if grep -P "\t" -q "$file"; then
      TAB_VIOLATIONS+=("$rel")
    fi
    # Count H1 lines starting with '# ' (avoid code fences by naive approach first)
    h1_count=$(grep -E '^# ' "$file" | wc -l | tr -d ' ')
    if [[ $h1_count -gt 1 ]]; then
      H1_VIOLATIONS+=("$rel:$h1_count")
    fi
    # Optional light fix: remove trailing spaces
    if [[ $FIX -eq 1 ]]; then
      sed -i 's/[[:space:]]\+$//' "$file"
    fi
  done < <(find "$dir" -type f -name '*.md' -print0)
done

if [[ ${#TAB_VIOLATIONS[@]} -gt 0 ]]; then
  echo "[verify_docs] Tab character violations detected in:" >&2
  printf '  - %s\n' "${TAB_VIOLATIONS[@]}" >&2
  EXIT_CODE=1
fi

if [[ ${#H1_VIOLATIONS[@]} -gt 0 ]]; then
  echo "[verify_docs] Multiple H1 headings detected:" >&2
  printf '  - %s (count)\n' "${H1_VIOLATIONS[@]}" >&2
  EXIT_CODE=1
fi

# Run markdownlint if installed locally (npx or yarn). Non-blocking if absent.
if command -v npx >/dev/null 2>&1; then
  if npx --yes markdownlint --version >/dev/null 2>&1; then
    echo "[verify_docs] Running markdownlint (informational)..."
    if ! npx --yes markdownlint "docs/adr/**/*.md" "docs/roadmap/**/*.md"; then
      echo "[verify_docs] markdownlint reported issues (does not alter exit unless other violations present)." >&2
      # Optionally set EXIT_CODE=1 here if you want lint to fail pipeline.
    fi
  fi
fi

echo "[verify_docs] Summary:"
if [[ $EXIT_CODE -eq 0 ]]; then
  echo "  No blocking documentation hygiene issues detected."
else
  echo "  Blocking issues found. See above."
fi

exit $EXIT_CODE
