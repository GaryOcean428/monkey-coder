#!/usr/bin/env python3
"""
Deployment validation script for Monkey Coder Core.

This script validates that the Python package structure is correct
and all imports work properly for Railway deployment.
"""

import sys
import os
from pathlib import Path

def validate_package_structure():
    """Validate the Python package structure."""
    print("🔍 Validating package structure...")
    
    # Check if we're in the right directory
    core_dir = Path(__file__).parent
    if not (core_dir / "monkey_coder").exists():
        print("❌ monkey_coder package not found")
        return False
    
    # Check required __init__.py files
    required_init_files = [
        "monkey_coder/__init__.py",
        "monkey_coder/config/__init__.py",
        "monkey_coder/pricing/__init__.py",
        "monkey_coder/app/__init__.py",
        "monkey_coder/core/__init__.py",
        "monkey_coder/database/__init__.py",
    ]
    
    for init_file in required_init_files:
        if not (core_dir / init_file).exists():
            print(f"❌ Missing {init_file}")
            return False
    
    print("✅ All __init__.py files present")
    return True

def validate_imports():
    """Validate that all imports work correctly."""
    print("🔍 Validating imports...")
    
    try:
        # Test config import (the main issue)
        from monkey_coder.config import config
        print("✅ monkey_coder.config import successful")
        
        # Test pricing import
        from monkey_coder.pricing.models import ModelPricing
        print("✅ monkey_coder.pricing.models import successful")
        
        # Test main app import
        from monkey_coder.app.main import app
        print("✅ monkey_coder.app.main import successful")
        
        # Test config module
        from monkey_coder.config.env_config import get_config
        print("✅ monkey_coder.config.env_config import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def validate_config_access():
    """Validate config object access."""
    print("🔍 Validating config object access...")
    
    try:
        from monkey_coder.config import config
        
        # Test config object properties
        print(f"✅ Config STORAGE: {type(config.STORAGE)}")
        print(f"✅ Config API_HOST: {config.API_HOST}")
        print(f"✅ Config API_PORT: {config.API_PORT}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config access error: {e}")
        return False

def validate_railway_compatibility():
    """Validate Railway deployment compatibility."""
    print("🔍 Validating Railway compatibility...")
    
    # Check for PORT environment variable handling
    from monkey_coder.config import config
    
    # Railway uses PORT env var
    port = int(os.getenv("PORT", config.API_PORT))
    host = os.getenv("HOST", config.API_HOST)
    
    print(f"✅ Railway port: {port}")
    print(f"✅ Railway host: {host}")
    
    # Check for Railway-specific paths
    data_dir = Path("/data")
    if data_dir.exists():
        print("✅ Railway /data volume detected")
    else:
        print("⚠️ Railway /data volume not detected (development mode)")
    
    return True

def validate_environment():
    """Validate the environment setup."""
    print("🔍 Validating environment...")
    
    # Check Python path
    python_path = os.getenv("PYTHONPATH", "")
    print(f"✅ PYTHONPATH: {python_path}")
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"✅ Current directory: {current_dir}")
    
    # Check if we can import as module
    try:
        import monkey_coder.app.main
        print("✅ Module import successful")
    except ImportError as e:
        print(f"❌ Module import failed: {e}")
        return False
    
    return True

def main():
    """Main validation function."""
    print("🚀 Monkey Coder Core Deployment Validation")
    print("=" * 50)
    
    validations = [
        ("Package Structure", validate_package_structure),
        ("Import Validation", validate_imports),
        ("Config Access", validate_config_access),
        ("Railway Compatibility", validate_railway_compatibility),
        ("Environment Setup", validate_environment),
    ]
    
    all_passed = True
    
    for name, validator in validations:
        print(f"\n{name}:")
        if not validator():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All validations passed! Ready for Railway deployment.")
        return 0
    else:
        print("❌ Some validations failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
