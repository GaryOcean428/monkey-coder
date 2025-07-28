#!/usr/bin/env python3
"""Test Sentry integration after deployment"""
import requests  # type: ignore[import]
import os

# Test endpoint that should trigger Sentry
def test_error_tracking():
    base_url = os.getenv("RAILWAY_PUBLIC_URL", "https://monkey-coder.up.railway.app")
    
    # Test normal request
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test API docs
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"✅ API docs: {response.status_code}")
    except Exception as e:
        print(f"❌ API docs failed: {e}")
    
    # Test error endpoint (if available) to verify Sentry captures
    try:
        response = requests.get(f"{base_url}/test-error")
        print(f"✅ Error test: {response.status_code}")
    except Exception:
        print("ℹ️  Error endpoint not available (expected)")
    
    print("\n📊 Next Steps:")
    print("1. Check Railway logs for 'Sentry configured for core in production environment'")
    print("2. Verify no ModuleNotFoundError in Railway logs")
    print("3. Check your Sentry dashboard for incoming events")
    print("4. Configure the Railway environment variables from RAILWAY_SENTRY_CONFIG.md")

if __name__ == "__main__":
    test_error_tracking()
