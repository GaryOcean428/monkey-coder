#!/usr/bin/env python3
"""
Comprehensive Backend API Smoke Tests for Monkey Coder

Tests all FastAPI endpoints to ensure they're accessible and return expected responses.
This smoke test focuses on route availability and basic functionality without deep integration testing.
"""

import asyncio
import httpx
import json
import os
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TestResult:
    """Result of a single API test."""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    success: bool
    error: Optional[str] = None


class BackendSmokeTest:
    """Backend API smoke test runner."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.client: Optional[httpx.AsyncClient] = None
        self.results: list[TestResult] = []
        
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def test_endpoint(
        self, 
        endpoint: str, 
        method: str = "GET", 
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 200
    ) -> TestResult:
        """Test a single API endpoint."""
        full_url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = await self.client.get(full_url, headers=headers)
            elif method.upper() == "POST":
                response = await self.client.post(full_url, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = time.time() - start_time
            success = response.status_code == expected_status
            
            result = TestResult(
                endpoint=endpoint,
                method=method,
                status_code=response.status_code,
                response_time=response_time,
                success=success,
                error=None if success else f"Expected {expected_status}, got {response.status_code}"
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            result = TestResult(
                endpoint=endpoint,
                method=method,
                status_code=0,
                response_time=response_time,
                success=False,
                error=str(e)
            )
            
        self.results.append(result)
        return result
    
    async def run_health_checks(self):
        """Test all health check endpoints."""
        print("🔍 Testing Health Check Endpoints...")
        
        health_endpoints = [
            "/health",
            "/healthz", 
            "/health/comprehensive",
            "/health/readiness"
        ]
        
        for endpoint in health_endpoints:
            result = await self.test_endpoint(endpoint)
            status = "✅" if result.success else "❌"
            print(f"  {status} {endpoint} - {result.status_code} ({result.response_time:.3f}s)")
    
    async def run_metrics_checks(self):
        """Test metrics endpoints."""
        print("📊 Testing Metrics Endpoints...")
        
        metrics_endpoints = [
            "/metrics",
            "/metrics/performance", 
            "/metrics/cache"
        ]
        
        for endpoint in metrics_endpoints:
            result = await self.test_endpoint(endpoint)
            status = "✅" if result.success else "❌"
            print(f"  {status} {endpoint} - {result.status_code} ({result.response_time:.3f}s)")
    
    async def run_api_v1_checks(self):
        """Test API v1 endpoints (without authentication)."""
        print("🔌 Testing API v1 Endpoints...")
        
        # Test endpoints that should work without auth
        public_endpoints = [
            ("/api/v1/cache/stats", "GET"),
            ("/api/v1/production/validate", "GET"),
            ("/api/v1/providers", "GET"),
            ("/api/v1/models", "GET")
        ]
        
        for endpoint, method in public_endpoints:
            result = await self.test_endpoint(endpoint, method)
            status = "✅" if result.success else "❌"
            print(f"  {status} {method} {endpoint} - {result.status_code} ({result.response_time:.3f}s)")
    
    async def run_auth_endpoint_checks(self):
        """Test authentication endpoints (expecting 401/422 for invalid requests)."""
        print("🔐 Testing Auth Endpoints...")
        
        # Test auth endpoints with invalid data (should return 401/422)
        auth_tests = [
            ("/api/v1/auth/status", "GET", None, 401),  # No auth token
            ("/api/v1/auth/login", "POST", {"email": "invalid", "password": "invalid"}, 422),  # Invalid format
            ("/api/v1/auth/logout", "POST", None, 401),  # No auth token
            ("/api/v1/auth/refresh", "POST", {"refresh_token": "invalid"}, 422)  # Invalid token
        ]
        
        for endpoint, method, data, expected_status in auth_tests:
            result = await self.test_endpoint(endpoint, method, data, expected_status=expected_status)
            status = "✅" if result.success else "❌"
            print(f"  {status} {method} {endpoint} - {result.status_code} ({result.response_time:.3f}s)")
    
    async def run_protected_endpoint_checks(self):
        """Test protected endpoints (should return 401 without auth)."""
        print("🛡️ Testing Protected Endpoints...")
        
        protected_endpoints = [
            ("/api/v1/execute", "POST"),
            ("/api/v1/billing/usage", "GET"),
            ("/api/v1/billing/portal", "POST")
        ]
        
        for endpoint, method in protected_endpoints:
            result = await self.test_endpoint(endpoint, method, expected_status=401)
            status = "✅" if result.success else "❌"
            print(f"  {status} {method} {endpoint} - {result.status_code} ({result.response_time:.3f}s)")
    
    async def run_all_tests(self):
        """Run comprehensive smoke tests."""
        print("🚀 Starting Backend API Smoke Tests")
        print("=" * 50)
        
        await self.run_health_checks()
        await self.run_metrics_checks()
        await self.run_api_v1_checks()
        await self.run_auth_endpoint_checks()
        await self.run_protected_endpoint_checks()
        
        # Summary
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - successful_tests
        avg_response_time = sum(r.response_time for r in self.results) / total_tests if total_tests > 0 else 0
        
        print("\n" + "=" * 50)
        print("📋 Test Summary")
        print(f"  Total Tests: {total_tests}")
        print(f"  ✅ Successful: {successful_tests}")
        print(f"  ❌ Failed: {failed_tests}")
        print(f"  ⏱️ Average Response Time: {avg_response_time:.3f}s")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.results:
                if not result.success:
                    print(f"  - {result.method} {result.endpoint}: {result.error}")
        
        return successful_tests == total_tests


async def main():
    """Main test runner."""
    base_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    async with BackendSmokeTest(base_url) as tester:
        success = await tester.run_all_tests()
        if not success:
            exit(1)


if __name__ == "__main__":
    asyncio.run(main())