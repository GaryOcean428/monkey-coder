#!/usr/bin/env python3
"""
Test Railway backend service configuration for deployment readiness.
This test validates that all required files exist in the correct locations
for Railway's isolated service build context.
"""

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_backend_service_requirements_file():
    """Verify requirements-deploy.txt exists in backend service directory."""
    backend_dir = Path("services/backend")
    requirements_file = backend_dir / "requirements-deploy.txt"
    
    assert backend_dir.exists(), f"Backend service directory not found: {backend_dir}"
    assert requirements_file.exists(), (
        f"requirements-deploy.txt missing from {backend_dir}. "
        f"Railway builds services in isolation and cannot access root-level files."
    )
    
    logger.info(f"✅ {requirements_file} exists")
    return True


def test_backend_railpack_json_valid():
    """Verify railpack.json is valid JSON and properly configured."""
    backend_dir = Path("services/backend")
    railpack_file = backend_dir / "railpack.json"
    
    assert railpack_file.exists(), f"railpack.json not found in {backend_dir}"
    
    # Validate JSON syntax
    with open(railpack_file, 'r') as f:
        config = json.load(f)
    
    # Validate schema reference
    assert "$schema" in config, "railpack.json missing $schema field"
    assert config["$schema"] == "https://schema.railpack.com", "Invalid schema URL"
    
    # Validate provider
    assert config.get("provider") == "python", "Invalid provider, should be 'python'"
    
    # Validate Python version
    packages = config.get("packages", {})
    assert "python" in packages, "Python version not specified in packages"
    assert packages["python"] == "3.12", "Python version should be 3.12"
    
    # Validate install steps reference requirements-deploy.txt
    steps = config.get("steps", {})
    install = steps.get("install", {})
    commands = install.get("commands", [])
    
    has_requirements_deploy = any(
        "requirements-deploy.txt" in cmd for cmd in commands
    )
    assert has_requirements_deploy, (
        "railpack.json install commands must reference requirements-deploy.txt"
    )
    
    logger.info(f"✅ {railpack_file} is valid and properly configured")
    return True


def test_backend_packages_core_accessible():
    """Verify packages/core is accessible from backend service directory."""
    backend_dir = Path("services/backend")
    core_package = Path("packages/core")
    
    # Check that relative path from backend to core exists
    relative_core = backend_dir / "../../packages/core"
    resolved_path = relative_core.resolve()
    
    assert resolved_path.exists(), (
        f"packages/core not accessible from backend service. "
        f"Expected path: {resolved_path}"
    )
    
    # Check that pyproject.toml exists (indicating it's a valid Python package)
    pyproject = resolved_path / "pyproject.toml"
    assert pyproject.exists(), (
        f"packages/core/pyproject.toml not found. "
        f"Core package may not be properly configured."
    )
    
    logger.info(f"✅ packages/core is accessible from backend service")
    return True


def main():
    """Run all Railway backend configuration tests."""
    logger.info("🚂 Railway Backend Service Configuration Tests")
    logger.info("=" * 70)
    
    tests = [
        ("Requirements File", test_backend_service_requirements_file),
        ("railpack.json Config", test_backend_railpack_json_valid),
        ("Core Package Access", test_backend_packages_core_accessible),
    ]
    
    results = []
    for name, test_func in tests:
        logger.info(f"\nTesting: {name}")
        try:
            test_func()
            results.append((name, True, None))
        except AssertionError as e:
            logger.error(f"❌ FAILED: {e}")
            results.append((name, False, str(e)))
        except Exception as e:
            logger.error(f"❌ ERROR: {e}")
            results.append((name, False, str(e)))
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY:")
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, error in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"  {status}: {name}")
        if error:
            logger.info(f"    Error: {error}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 All Railway backend configuration tests passed!")
        logger.info("The backend service is ready for Railway deployment.")
        return True
    else:
        logger.error("\n🚨 Some tests failed. Fix the issues before deploying.")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
