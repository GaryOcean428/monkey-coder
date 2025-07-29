#!/usr/bin/env python3
"""
Package Structure Validation Script

Validates that all required Python package files exist to prevent
import failures during Railway deployment.
"""

import os
import sys
from pathlib import Path

def validate_package_structure():
    """Validate Python package structure for Monkey Coder."""
    
    # Required __init__.py files for package structure
    required_init_files = [
        'packages/core/monkey_coder/__init__.py',
        'packages/core/monkey_coder/config/__init__.py',
        'packages/core/monkey_coder/core/__init__.py',
        'packages/core/monkey_coder/app/__init__.py',
        'packages/core/monkey_coder/agents/__init__.py',
        'packages/core/monkey_coder/auth/__init__.py',
        'packages/core/monkey_coder/billing/__init__.py',
        'packages/core/monkey_coder/database/__init__.py',
        'packages/core/monkey_coder/logging_utils/__init__.py',
        'packages/core/monkey_coder/mcp/__init__.py',
        'packages/core/monkey_coder/pricing/__init__.py',
        'packages/core/monkey_coder/providers/__init__.py',
        'packages/core/monkey_coder/quantum/__init__.py',
        'packages/core/monkey_coder/utils/__init__.py'
    ]
    
    # Required module files
    required_modules = [
        'packages/core/monkey_coder/config/env_config.py',
        'packages/core/monkey_coder/app/main.py',
        'packages/core/monkey_coder/core/orchestrator.py',
        'packages/core/monkey_coder/core/orchestration_coordinator.py'
    ]
    
    missing_files = []
    
    # Check __init__.py files
    print("Validating Python package structure...")
    for init_file in required_init_files:
        if not os.path.exists(init_file):
            missing_files.append(init_file)
            print(f"❌ MISSING: {init_file}")
        else:
            print(f"✅ OK: {init_file}")
    
    # Check required modules
    print("\nValidating required modules...")
    for module_file in required_modules:
        if not os.path.exists(module_file):
            missing_files.append(module_file)
            print(f"❌ MISSING: {module_file}")
        else:
            print(f"✅ OK: {module_file}")
    
    # Test critical imports
    print("\nTesting critical imports...")
    try:
        sys.path.insert(0, 'packages/core')
        from monkey_coder.config.env_config import get_config
        print("✅ SUCCESS: monkey_coder.config.env_config import works")
    except ImportError as e:
        print(f"❌ IMPORT FAILED: {e}")
        missing_files.append("IMPORT_TEST_FAILED")
    
    # Summary
    if missing_files:
        print(f"\n❌ VALIDATION FAILED: {len(missing_files)} issues found")
        for f in missing_files:
            print(f"  - {f}")
        return False
    else:
        print("\n✅ VALIDATION PASSED: All package files found")
        return True

if __name__ == "__main__":
    success = validate_package_structure()
    sys.exit(0 if success else 1)