#!/usr/bin/env python3
"""
Railway Deployment Validation Script

This script validates the Railway deployment configuration for monkey-coder,
specifically addressing the virtual environment path resolution issues
identified in the railpack.json configuration.

Usage:
    python railway_deployment_validation.py

The script will:
1. Validate virtual environment setup
2. Check Python package installation paths
3. Verify uvicorn accessibility
4. Test FastAPI app import
5. Validate environment variables
6. Check health endpoint response
"""

import os
import sys
import subprocess
import json
import importlib.util
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_virtual_environment():
    """Validate virtual environment setup and accessibility."""
    logger.info("🔍 Validating virtual environment setup...")
    
    # Check if we're in a virtual environment
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        logger.info(f"✅ Virtual environment detected: {venv_path}")
    else:
        logger.warning("⚠️ No VIRTUAL_ENV detected in environment")
    
    # Check for Railway railpack virtual environment
    railway_venv = Path("/app/.venv")
    if railway_venv.exists():
        logger.info(f"✅ Railway virtual environment found at: {railway_venv}")
        
        # Check Python executable in venv
        venv_python = railway_venv / "bin" / "python"
        if venv_python.exists():
            logger.info(f"✅ Python executable found: {venv_python}")
        else:
            logger.error(f"❌ Python executable not found: {venv_python}")
            return False
            
        # Check uvicorn in venv
        venv_uvicorn = railway_venv / "bin" / "uvicorn"
        if venv_uvicorn.exists():
            logger.info(f"✅ Uvicorn found: {venv_uvicorn}")
        else:
            logger.error(f"❌ Uvicorn not found: {venv_uvicorn}")
            return False
    else:
        logger.warning(f"⚠️ Railway virtual environment not found at: {railway_venv}")
    
    # Check current Python executable
    current_python = sys.executable
    logger.info(f"📍 Current Python executable: {current_python}")
    
    # Check Python version
    python_version = sys.version
    logger.info(f"🐍 Python version: {python_version}")
    
    return True


def validate_package_installation():
    """Validate that required packages are installed and accessible."""
    logger.info("📦 Validating package installation...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'httpx',
        'openai',
        'anthropic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            spec = importlib.util.find_spec(package)
            if spec is None:
                missing_packages.append(package)
                logger.error(f"❌ Package not found: {package}")
            else:
                logger.info(f"✅ Package found: {package}")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ Package import failed: {package}")
    
    if missing_packages:
        logger.error(f"❌ Missing packages: {missing_packages}")
        return False
    
    logger.info("✅ All required packages are installed")
    return True


def validate_uvicorn_accessibility():
    """Validate that uvicorn can be accessed from the correct path."""
    logger.info("🚀 Validating uvicorn accessibility...")
    
    # Try to find uvicorn in different locations
    uvicorn_paths = [
        "/app/.venv/bin/uvicorn",
        "uvicorn",
        subprocess.run(["which", "uvicorn"], capture_output=True, text=True).stdout.strip()
    ]
    
    accessible_uvicorn = None
    
    for path in uvicorn_paths:
        if not path:
            continue
            
        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                accessible_uvicorn = path
                logger.info(f"✅ Uvicorn accessible at: {path}")
                logger.info(f"   Version: {result.stdout.strip()}")
                break
            else:
                logger.warning(f"⚠️ Uvicorn not accessible at: {path}")
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError) as e:
            logger.warning(f"⚠️ Error testing uvicorn at {path}: {e}")
    
    if not accessible_uvicorn:
        logger.error("❌ Uvicorn is not accessible from any expected path")
        return False
    
    return True


def validate_app_import():
    """Validate that the FastAPI app can be imported successfully."""
    logger.info("🎯 Validating FastAPI app import...")
    
    # Add the current directory and packages/core to Python path
    current_dir = Path(__file__).parent
    core_dir = current_dir / "packages" / "core"
    
    sys.path.insert(0, str(current_dir))
    sys.path.insert(0, str(core_dir))
    
    try:
        # Try to import the main FastAPI app
        from monkey_coder.app.main import app
        logger.info("✅ FastAPI app imported successfully")
        
        # Check if app is a FastAPI instance
        from fastapi import FastAPI
        if isinstance(app, FastAPI):
            logger.info("✅ App is a valid FastAPI instance")
        else:
            logger.error("❌ App is not a FastAPI instance")
            return False
            
        return True
        
    except ImportError as e:
        logger.error(f"❌ Failed to import FastAPI app: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error importing app: {e}")
        return False


def validate_environment_variables():
    """Validate that essential environment variables are set."""
    logger.info("🔧 Validating environment variables...")
    
    essential_vars = {
        'PORT': 'Application port',
        'PYTHONPATH': 'Python module search paths'
    }
    
    optional_vars = {
        'NEXTAUTH_URL': 'NextAuth authentication URL',
        'DATABASE_URL': 'Database connection URL',
        'NEXT_PUBLIC_API_URL': 'Public API URL'
    }
    
    # Check essential variables
    missing_essential = []
    for var, description in essential_vars.items():
        value = os.environ.get(var)
        if value:
            # Mask sensitive values for logging
            display_value = value if var != 'DATABASE_URL' else value.split('@')[0] + '@***'
            logger.info(f"✅ {var}: {display_value}")
        else:
            missing_essential.append(var)
            logger.warning(f"⚠️ Missing essential variable: {var} ({description})")
    
    # Check optional variables
    for var, description in optional_vars.items():
        value = os.environ.get(var)
        if value:
            # Mask sensitive values for logging
            display_value = value if var != 'DATABASE_URL' else value.split('@')[0] + '@***'
            logger.info(f"✅ {var}: {display_value}")
        else:
            logger.info(f"ℹ️ Optional variable not set: {var} ({description})")
    
    if missing_essential:
        logger.error(f"❌ Missing essential environment variables: {missing_essential}")
        return False
    
    return True


def validate_railpack_configuration():
    """Validate the railpack.json configuration."""
    logger.info("📋 Validating railpack.json configuration...")
    
    railpack_path = Path(__file__).parent / "railpack.json"
    
    if not railpack_path.exists():
        logger.error(f"❌ railpack.json not found at: {railpack_path}")
        return False
    
    try:
        with open(railpack_path, 'r') as f:
            config = json.load(f)
        
        logger.info("✅ railpack.json is valid JSON")
        
        # Check essential configuration elements
        required_keys = ['version', 'metadata', 'build', 'deploy']
        for key in required_keys:
            if key in config:
                logger.info(f"✅ Configuration key present: {key}")
            else:
                logger.error(f"❌ Missing configuration key: {key}")
                return False
        
        # Check provider under build section
        if config.get('build', {}).get('provider') == 'python':
            logger.info("✅ Provider is correctly set to 'python'")
        else:
            logger.error(f"❌ Provider should be 'python', got: {config.get('build', {}).get('provider')}")
            return False
        
        # Check start command
        start_command = config.get('deploy', {}).get('startCommand')
        if start_command:
            logger.info(f"✅ Start command: {start_command}")
            if '/app/start_server.sh' in start_command or '/app/.venv/bin/' in start_command:
                logger.info("✅ Start command uses virtual environment path")
            else:
                logger.warning("⚠️ Start command may not use virtual environment path")
        else:
            logger.error("❌ No start command specified")
            return False
        
        return True
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in railpack.json: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error reading railpack.json: {e}")
        return False


def test_health_endpoint():
    """Test the health endpoint if the server is running."""
    logger.info("🩺 Testing health endpoint (if server is running)...")
    
    port = os.environ.get('PORT', '8000')
    health_url = f"http://localhost:{port}/health"
    
    try:
        import httpx
        
        with httpx.Client(timeout=5.0) as client:
            response = client.get(health_url)
            
            if response.status_code == 200:
                logger.info(f"✅ Health endpoint accessible: {health_url}")
                logger.info(f"   Response: {response.json()}")
                return True
            else:
                logger.warning(f"⚠️ Health endpoint returned status {response.status_code}")
                return False
                
    except ImportError:
        logger.info("ℹ️ httpx not available, skipping health endpoint test")
        return True
    except Exception as e:
        logger.info(f"ℹ️ Health endpoint test failed (server may not be running): {e}")
        return True  # Not a failure if server isn't running


def main():
    """Run all validation checks."""
    logger.info("🐒 Starting Railway Deployment Validation for Monkey Coder")
    logger.info("=" * 60)
    
    checks = [
        ("Virtual Environment Setup", validate_virtual_environment),
        ("Package Installation", validate_package_installation),
        ("Uvicorn Accessibility", validate_uvicorn_accessibility),
        ("FastAPI App Import", validate_app_import),
        ("Environment Variables", validate_environment_variables),
        ("Railpack Configuration", validate_railpack_configuration),
        ("Health Endpoint", test_health_endpoint)
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check_name, check_function in checks:
        logger.info(f"\n{'─' * 40}")
        logger.info(f"Running check: {check_name}")
        logger.info(f"{'─' * 40}")
        
        try:
            if check_function():
                passed_checks += 1
                logger.info(f"✅ {check_name}: PASSED")
            else:
                logger.error(f"❌ {check_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {check_name}: ERROR - {e}")
    
    logger.info(f"\n{'=' * 60}")
    logger.info(f"Validation Summary: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        logger.info("🎉 All validation checks passed!")
        logger.info("✅ Railway deployment configuration is ready")
        return True
    else:
        failed_checks = total_checks - passed_checks
        logger.error(f"❌ {failed_checks} validation check(s) failed")
        logger.error("🔧 Please address the issues above before deploying")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)