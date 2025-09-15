#!/usr/bin/env python3
"""
Test Railway App Startup Validation

This script tests that the FastAPI application can start properly
and validates the health endpoint functionality without requiring
full Railway environment setup.
"""

import os
import sys
import asyncio
import json
import uvicorn
import multiprocessing
import time
import requests
from pathlib import Path

# Add package path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir / "packages" / "core"))

def test_app_import():
    """Test that the FastAPI app can be imported successfully."""
    print("🔍 Testing FastAPI app import...")
    try:
        from monkey_coder.app.main import app
        print("✅ FastAPI app imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import FastAPI app: {e}")
        return False

def test_health_endpoint_logic():
    """Test the health endpoint logic without starting the server."""
    print("🩺 Testing health endpoint logic...")
    try:
        from monkey_coder.app.main import health_check
        
        # Mock the health check function in a test context
        import asyncio
        async def run_health_check():
            try:
                response = await health_check()
                print(f"✅ Health check response: {response.status}")
                return True
            except Exception as e:
                print(f"❌ Health check failed: {e}")
                return False
        
        # Run the async health check
        result = asyncio.run(run_health_check())
        return result
    except Exception as e:
        print(f"❌ Failed to test health endpoint: {e}")
        return False

def start_test_server():
    """Start a test server to validate full functionality."""
    print("🚀 Starting test server for validation...")
    
    # Set required environment variables for testing
    os.environ['PORT'] = '8001'
    os.environ['PYTHONPATH'] = str(script_dir)
    
    try:
        from monkey_coder.app.main import app
        
        # Start server in test mode
        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=8001,
            log_level="info",
            access_log=False
        )
        server = uvicorn.Server(config)
        
        def run_server():
            asyncio.run(server.serve())
        
        # Start server in background process
        process = multiprocessing.Process(target=run_server)
        process.start()
        
        # Give server time to start
        time.sleep(3)
        
        # Test health endpoint
        try:
            response = requests.get("http://127.0.0.1:8001/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health endpoint returned: {health_data['status']}")
                success = True
            else:
                print(f"❌ Health endpoint returned status: {response.status_code}")
                success = False
        except Exception as e:
            print(f"❌ Failed to reach health endpoint: {e}")
            success = False
        
        # Clean up
        process.terminate()
        process.join()
        
        return success
        
    except Exception as e:
        print(f"❌ Failed to start test server: {e}")
        return False

def validate_railpack_configuration():
    """Validate the railpack.json configuration comprehensively."""
    print("📋 Validating railpack.json configuration...")
    
    railpack_path = script_dir / "railpack.json"
    if not railpack_path.exists():
        print("❌ railpack.json not found")
        return False
    
    try:
        with open(railpack_path) as f:
            config = json.load(f)
        
        # Validate critical configuration elements
        checks = [
            ("provider", "python"),
            ("packages.python", "3.13"),
            ("packages.node", "20"),
            ("deploy.startCommand", "/app/start_server.sh"),
            ("deploy.healthCheckPath", "/health"),
            ("deploy.environment.VIRTUAL_ENV", "/app/venv"),
        ]
        
        for check_path, expected_value in checks:
            keys = check_path.split('.')
            current = config
            for key in keys:
                if key not in current:
                    print(f"❌ Missing configuration: {check_path}")
                    return False
                current = current[key]
            
            if current != expected_value:
                print(f"❌ Incorrect configuration: {check_path} = {current}, expected: {expected_value}")
                return False
            else:
                print(f"✅ Configuration valid: {check_path} = {current}")
        
        # Validate build cache paths
        cache_paths = config.get("build", {}).get("cache", {}).get("paths", [])
        required_cache_paths = ["/app/venv/lib/python3.13/site-packages", "node_modules"]
        for path in required_cache_paths:
            if path not in cache_paths:
                print(f"⚠️ Missing cache path: {path}")
            else:
                print(f"✅ Cache path configured: {path}")
        
        print("✅ railpack.json configuration validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Failed to validate railpack.json: {e}")
        return False

def main():
    """Run comprehensive Railway deployment readiness tests."""
    print("🐒 Railway App Startup Validation for Monkey Coder")
    print("==================================================")
    
    tests = [
        ("FastAPI App Import", test_app_import),
        ("Health Endpoint Logic", test_health_endpoint_logic),
        ("Railpack Configuration", validate_railpack_configuration),
        ("Full Server Test", start_test_server),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running test: {test_name}")
        print("─" * 40)
        
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! App is ready for Railway deployment")
        return 0
    else:
        print("❌ Some tests failed. Please address issues before deployment")
        return 1

if __name__ == "__main__":
    exit(main())