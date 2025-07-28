#!/usr/bin/env python3
"""
Railway Deployment Validation Script

This script validates that all Railway deployment optimizations are working correctly.
Run this script before deploying to Railway to ensure everything is configured properly.
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add the packages/core directory to Python path
script_dir = Path(__file__).parent
core_dir = script_dir / "packages" / "core"
sys.path.insert(0, str(core_dir))

# Set up test environment
os.environ.update({
    'JSON_LOGS': 'true',
    'LOG_LEVEL': 'INFO',
    'PERFORMANCE_LOGS': 'true',
    'RAILWAY_ENVIRONMENT': 'test'
})

def test_import_structure():
    """Test that all key modules can be imported without errors."""
    print("Testing import structure...")
    
    try:
        # Test logging utilities
        from monkey_coder.logging_utils import setup_logging, monitor_api_calls
        print("✅ Logging utilities import successful")
        
        # Test configuration
        from monkey_coder.config import config
        print("✅ Configuration import successful")
        
        # Test providers
        from monkey_coder.providers import ProviderRegistry
        from monkey_coder.providers.qwen_adapter import QwenProvider
        from monkey_coder.providers.openai_adapter import OpenAIProvider
        print("✅ Provider imports successful")
        
        # Test FastAPI app
        from monkey_coder.app.main import app
        print("✅ FastAPI application import successful")
        
        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_json_logging():
    """Test that JSON logging is working correctly."""
    print("\nTesting JSON logging...")
    
    try:
        from monkey_coder.logging_utils import setup_logging, get_performance_logger
        
        # Capture log output
        import io
        log_stream = io.StringIO()
        
        # Configure logging to write to our stream
        setup_logging()
        
        # Get a logger and test it
        perf_logger = get_performance_logger("test")
        
        # Log a test message
        perf_logger.logger.info(
            "Test log message",
            extra={'extra_fields': {
                'test_metric': 'json_logging_test',
                'value': 123
            }}
        )
        
        print("✅ JSON logging configured successfully")
        return True
    except Exception as e:
        print(f"❌ JSON logging test failed: {e}")
        return False

def test_performance_monitoring():
    """Test that performance monitoring decorators work."""
    print("\nTesting performance monitoring...")
    
    try:
        from monkey_coder.logging_utils import monitor_api_calls
        
        @monitor_api_calls("test_function")
        async def test_async_function():
            await asyncio.sleep(0.1)  # Simulate work
            return "success"
        
        @monitor_api_calls("test_sync_function")
        def test_sync_function():
            time.sleep(0.05)  # Simulate work
            return "success"
        
        # Test async function
        result = asyncio.run(test_async_function())
        assert result == "success"
        
        # Test sync function
        result = test_sync_function()
        assert result == "success"
        
        print("✅ Performance monitoring decorators working")
        return True
    except Exception as e:
        print(f"❌ Performance monitoring test failed: {e}")
        return False

async def test_fastapi_health():
    """Test that the FastAPI health endpoint works."""
    print("\nTesting FastAPI health endpoint...")
    
    try:
        from fastapi.testclient import TestClient
        from monkey_coder.app.main import app
        
        with TestClient(app) as client:
            response = client.get("/health")
            
            if response.status_code != 200:
                print(f"❌ Health endpoint returned {response.status_code}")
                return False
            
            data = response.json()
            
            # Validate response structure
            required_fields = ["status", "version", "timestamp", "components"]
            for field in required_fields:
                if field not in data:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            if data["status"] != "healthy":
                print(f"❌ Health status is {data['status']}, expected 'healthy'")
                return False
            
            # Check components
            expected_components = [
                "orchestrator", "quantum_executor", 
                "persona_router", "provider_registry"
            ]
            for component in expected_components:
                if component not in data["components"]:
                    print(f"❌ Missing component: {component}")
                    return False
                if data["components"][component] != "active":
                    print(f"❌ Component {component} not active")
                    return False
            
            print("✅ Health endpoint working correctly")
            print(f"   Status: {data['status']}")
            print(f"   Components: {list(data['components'].keys())}")
            return True
            
    except Exception as e:
        print(f"❌ FastAPI health test failed: {e}")
        return False

def test_qwen_integration():
    """Test that Qwen agent integration works without warnings."""
    print("\nTesting Qwen integration...")
    
    try:
        # Capture warnings
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            from monkey_coder.providers.qwen_adapter import QwenProvider
            
            # Check if QwenAgent is available
            provider = QwenProvider("test-key")
            
            # Look for qwen-agent related warnings
            qwen_warnings = [warning for warning in w 
                           if "Qwen Agent" in str(warning.message)]
            
            if qwen_warnings:
                print(f"❌ Qwen warnings detected: {[str(w.message) for w in qwen_warnings]}")
                return False
            
            print("✅ Qwen integration working without warnings")
            return True
            
    except Exception as e:
        print(f"❌ Qwen integration test failed: {e}")
        return False

def test_railway_config():
    """Test that Railway configuration is valid."""
    print("\nTesting Railway configuration...")
    
    try:
        import json
        
        # Load and validate railpack.json
        railpack_path = script_dir / "railpack.json"
        with open(railpack_path, "r") as f:
            config = json.load(f)
        
        # Check required fields
        if "healthcheck" not in config:
            print("❌ Missing healthcheck configuration")
            return False
        
        if config["healthcheck"]["path"] != "/health":
            print("❌ Incorrect healthcheck path")
            return False
        
        if "environments" not in config:
            print("❌ Missing environments configuration")
            return False
        
        if "production" not in config["environments"]:
            print("❌ Missing production environment")
            return False
        
        prod_env = config["environments"]["production"]
        if "env" not in prod_env:
            print("❌ Missing production environment variables")
            return False
        
        required_env_vars = ["LOG_LEVEL", "JSON_LOGS", "PERFORMANCE_LOGS"]
        for var in required_env_vars:
            if var not in prod_env["env"]:
                print(f"❌ Missing environment variable: {var}")
                return False
        
        print("✅ Railway configuration valid")
        print(f"   Health check: {config['healthcheck']['path']}")
        print(f"   Environment vars: {list(prod_env['env'].keys())}")
        return True
        
    except Exception as e:
        print(f"❌ Railway config test failed: {e}")
        return False

def main():
    """Run all validation tests."""
    print("🚀 Railway Deployment Validation")
    print("=" * 50)
    
    tests = [
        test_import_structure,
        test_json_logging,
        test_performance_monitoring,
        lambda: asyncio.run(test_fastapi_health()),
        test_qwen_integration,
        test_railway_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for Railway deployment.")
        return 0
    else:
        print("❌ Some tests failed. Please fix issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())