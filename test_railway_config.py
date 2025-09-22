#!/usr/bin/env python3
"""
Simplified Railway Configuration Test

This script tests core Railway deployment configuration without
requiring all dependencies to be installed.
"""

import os
import sys
import json
from pathlib import Path

def test_railpack_configuration():
    """Test railpack.json configuration comprehensively."""
    print("📋 Testing railpack.json configuration...")
    
    script_dir = Path(__file__).parent
    railpack_path = script_dir / "railpack.json"
    
    if not railpack_path.exists():
        print("❌ railpack.json not found")
        return False
    
    try:
        with open(railpack_path) as f:
            config = json.load(f)
        
        # Validate critical elements
        checks = [
            ("build.provider", "python"),
            ("build.packages.python", "3.12"),
            ("build.packages.node", "20"),
            ("deploy.startCommand", "/app/.venv/bin/python /app/run_server.py"),
            ("deploy.healthCheckPath", "/health"),
            ("deploy.environment.VIRTUAL_ENV", "/app/.venv"),
            ("deploy.environment.PATH", "/app/.venv/bin:$PATH"),
            ("deploy.environment.PYTHONPATH", "/app:/app/packages/core"),
        ]
        
        all_passed = True
        for check_path, expected_value in checks:
            keys = check_path.split('.')
            current = config
            try:
                for key in keys:
                    current = current[key]
                
                if current == expected_value:
                    print(f"✅ {check_path} = {current}")
                else:
                    print(f"❌ {check_path} = {current}, expected: {expected_value}")
                    all_passed = False
            except KeyError:
                print(f"❌ Missing configuration: {check_path}")
                all_passed = False
        
        # Check build commands for virtual environment usage
        build_commands = config.get("build", {}).get("steps", {}).get("install", {}).get("commands", [])
        venv_commands = [cmd for cmd in build_commands if "/app/.venv/bin" in str(cmd)]
        
        print(f"\n🔧 Virtual environment commands found: {len(venv_commands)}")
        for cmd in venv_commands[:3]:  # Show first 3
            print(f"   • {cmd}")
        
        if len(venv_commands) >= 3:
            print("✅ Sufficient virtual environment usage in build commands")
        else:
            print("⚠️ Limited virtual environment usage in build commands")
        
        # Check cache configuration
        cache_paths = config.get("build", {}).get("cache", {}).get("paths", [])
        print(f"\n💾 Cache paths configured: {len(cache_paths)}")
        for path in cache_paths:
            print(f"   • {path}")
        
        if "/app/.venv/lib/python3.12/site-packages" in cache_paths:
            print("✅ Python packages cache configured")
        else:
            print("⚠️ Python packages cache not configured")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Failed to validate railpack.json: {e}")
        return False

def test_start_script():
    """Test the start script configuration."""
    print("\n🚀 Testing start script...")
    
    script_dir = Path(__file__).parent
    start_script_path = script_dir / "railpack.json"
    
    try:
        with open(start_script_path) as f:
            config = json.load(f)
        
        start_command = config.get("deploy", {}).get("startCommand", "")
        
        if start_command == "/app/.venv/bin/python /app/run_server.py":
            print("✅ Start command correctly configured: /app/.venv/bin/python /app/run_server.py")
            return True
        else:
            print(f"❌ Incorrect start command: {start_command}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test start script: {e}")
        return False

def test_environment_variables():
    """Test environment variable configuration."""
    print("\n🔧 Testing environment variables...")
    
    script_dir = Path(__file__).parent
    railpack_path = script_dir / "railpack.json"
    
    try:
        with open(railpack_path) as f:
            config = json.load(f)
        
        env_vars = config.get("deploy", {}).get("environment", {})
        
        required_vars = {
            "VIRTUAL_ENV": "/app/.venv",
            "PATH": "/app/.venv/bin:$PATH",
            "PYTHONPATH": "/app:/app/packages/core"
        }
        
        all_passed = True
        for var_name, expected_value in required_vars.items():
            if var_name in env_vars:
                actual_value = env_vars[var_name]
                if actual_value == expected_value:
                    print(f"✅ {var_name} = {actual_value}")
                else:
                    print(f"⚠️ {var_name} = {actual_value}, expected: {expected_value}")
                    all_passed = False
            else:
                print(f"❌ Missing environment variable: {var_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Failed to test environment variables: {e}")
        return False

def test_health_check_config():
    """Test health check configuration."""
    print("\n🩺 Testing health check configuration...")
    
    script_dir = Path(__file__).parent
    railpack_path = script_dir / "railpack.json"
    
    try:
        with open(railpack_path) as f:
            config = json.load(f)
        
        health_path = config.get("deploy", {}).get("healthCheckPath", "")
        health_timeout = config.get("deploy", {}).get("healthCheckTimeout", 0)
        
        if health_path == "/health":
            print("✅ Health check path correctly configured: /health")
        else:
            print(f"❌ Incorrect health check path: {health_path}")
            return False
        
        if health_timeout >= 300:
            print(f"✅ Health check timeout adequate: {health_timeout}s")
        else:
            print(f"⚠️ Health check timeout may be too short: {health_timeout}s")
        
        # Check restart policy
        restart_policy = config.get("deploy", {}).get("restartPolicyType", "")
        if restart_policy == "ON_FAILURE":
            print("✅ Restart policy configured: ON_FAILURE")
        else:
            print(f"⚠️ Restart policy: {restart_policy}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test health check config: {e}")
        return False

def main():
    """Run comprehensive Railway configuration tests."""
    print("🐒 Railway Configuration Validation for Monkey Coder")
    print("=====================================================")
    
    tests = [
        ("Railpack Configuration", test_railpack_configuration),
        ("Start Script", test_start_script),
        ("Environment Variables", test_environment_variables),
        ("Health Check Config", test_health_check_config),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running test: {test_name}")
        print("─" * 50)
        
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"🎯 Configuration Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All configuration tests passed! Railway deployment config is optimal")
        return 0
    else:
        print("❌ Some tests failed. Please review configuration")
        return 1

if __name__ == "__main__":
    exit(main())