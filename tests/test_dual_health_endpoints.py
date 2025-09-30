#!/usr/bin/env python3
"""
Integration test to verify /health and /api/health return identical JSON payloads.
Run this test when the backend server is running.
"""
import asyncio
import sys

import aiohttp


async def test_dual_health_endpoints(base_url: str = "http://localhost:8000") -> bool:
    """Test that /health and /api/health return identical JSON payloads."""
    print("🔄 Testing dual health endpoint consistency...")

    try:
        async with aiohttp.ClientSession() as session:
            # Get responses from both endpoints
            async with session.get(f"{base_url}/health") as resp1:
                if resp1.status != 200:
                    print(f"  ❌ /health returned status {resp1.status}")
                    return False
                health_json = await resp1.json()

            async with session.get(f"{base_url}/api/health") as resp2:
                if resp2.status != 200:
                    print(f"  ❌ /api/health returned status {resp2.status}")
                    return False
                api_health_json = await resp2.json()

        # Compare JSON payloads (excluding timestamp fields that may differ slightly)
        health_compare = {k: v for k, v in health_json.items() if k != 'timestamp'}
        api_health_compare = {k: v for k, v in api_health_json.items() if k != 'timestamp'}

        if health_compare == api_health_compare:
            print("  ✅ /health and /api/health return identical payloads")
            print(f"    Status: {health_json.get('status', 'unknown')}")
            print(f"    Version: {health_json.get('version', 'unknown')}")
            print(f"    Components: {len(health_json.get('components', {}))}")
            return True
        else:
            print("  ❌ /health and /api/health payloads differ")
            print(f"    /health keys: {set(health_compare.keys())}")
            print(f"    /api/health keys: {set(api_health_compare.keys())}")

            # Show detailed diff
            for key in health_compare.keys() | api_health_compare.keys():
                health_val = health_compare.get(key, "<missing>")
                api_health_val = api_health_compare.get(key, "<missing>")
                if health_val != api_health_val:
                    print(f"    {key}: /health={health_val}, /api/health={api_health_val}")
            return False

    except aiohttp.ClientConnectorError:
        print(f"  ❌ Could not connect to {base_url}")
        print("  💡 Make sure the backend server is running:")
        print("     cd packages/core && python run_server.py")
        return False
    except Exception as e:
        print(f"  ❌ Dual health consistency test failed: {e}")
        return False


async def main():
    """Main test runner."""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

    print("🚀 Dual Health Endpoint Consistency Test")
    print("=" * 50)

    success = await test_dual_health_endpoints(base_url)

    print("=" * 50)
    if success:
        print("✅ Test PASSED: Both endpoints return identical payloads")
        sys.exit(0)
    else:
        print("❌ Test FAILED: Endpoints do not return identical payloads")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
