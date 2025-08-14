#!/usr/bin/env python3
"""
Fix railpack.json with a simpler, more compatible configuration.
"""

import json
import sys
from pathlib import Path

# Create a minimal, working railpack.json
railpack = {
    "version": "1",
    "build": {
        "builder": "nixpacks"
    },
    "deploy": {
        "startCommand": "cd packages/core && python -m uvicorn monkey_coder.app.main:app --host 0.0.0.0 --port ${PORT:-8000}",
        "restartPolicyType": "ON_FAILURE",
        "restartPolicyMaxRetries": 3
    }
}

# Save the new railpack.json
with open('railpack.json', 'w') as f:
    json.dump(railpack, f, indent=2)

print("✅ Created simplified railpack.json")
print("\nNew configuration uses nixpacks auto-detection:")
print("- Will auto-detect Python and install requirements.txt")
print("- Will auto-detect Node.js and run yarn build")
print("- Simplified start command")
print("\nThis should work better with Railway's build system.")