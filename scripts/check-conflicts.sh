#!/usr/bin/env bash
# Simple merge conflict marker detector. Exit 1 if any markers found.
set -euo pipefail

markers='<<<<<<< HEAD|=======|>>>>>>> '
if grep -R -n -E "$markers" . --exclude-dir=.git --exclude=check-conflicts.sh; then
  echo "Merge conflict markers detected. Resolve before committing." >&2
  exit 1
else
  echo "No merge conflict markers detected."
fi
