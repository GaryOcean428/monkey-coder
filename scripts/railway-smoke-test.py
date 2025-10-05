#!/usr/bin/env python3
"""
Railway Deployment Smoke Test Suite

Comprehensive smoke testing for Railway deployments with health checks,
endpoint validation, and service communication testing.

Usage:
    python scripts/railway-smoke-test.py [--services SERVICES] [--timeout TIMEOUT]
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from urllib.parse import urljoin

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "core"))


@dataclass
class ServiceEndpoint:
    """Railway service endpoint configuration."""
    name: str
    url: str
    health_path: str = "/api/health"
    timeout: int = 10
    required: bool = True


@dataclass
class TestResult:
    """Test execution result."""
    test_name: str
    service: str
    status: str  # "pass", "fail", "skip"
    duration_ms: float
    message: str
    timestamp: str = ""
    details: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class RailwaySmokeTest:
    """Comprehensive smoke test suite for Railway deployments."""
    
    def __init__(self, timeout: int = 30, verbose: bool = False, base_url: Optional[str] = None):
        self.timeout = timeout
        self.verbose = verbose
        self.base_url = base_url
        self.results: List[TestResult] = []
        self.services = self._load_service_endpoints()
        
    def _load_service_endpoints(self) -> List[ServiceEndpoint]:
        """Load service endpoints from environment or defaults."""
        services = []
        
        # Try to load from environment or use provided base_url
        base_url = self.base_url or os.getenv("RAILWAY_BASE_URL", "https://monkey-coder.up.railway.app")
        backend_url = os.getenv("BACKEND_URL", "https://monkey-coder-backend-production.up.railway.app")
        
        # Frontend service
        services.append(ServiceEndpoint(
            name="frontend",
            url=base_url,
            health_path="/api/health",
            timeout=10,
            required=True
        ))
        
        # Backend service
        services.append(ServiceEndpoint(
            name="backend",
            url=backend_url,
            health_path="/api/health",
            timeout=10,
            required=True
        ))
        
        # ML service (optional - may not always be deployed)
        ml_url = os.getenv("ML_SERVICE_URL")
        if ml_url:
            services.append(ServiceEndpoint(
                name="ml",
                url=ml_url,
                health_path="/api/health",
                timeout=30,  # Longer timeout for ML service
                required=False
            ))
        
        return services
    
    def print_header(self):
        """Print test suite header."""
        print("\n" + "="*75)
        print("║" + " "*73 + "║")
        print("║" + "     Railway Deployment Smoke Test Suite".center(73) + "║")
        print("║" + " "*73 + "║")
        print("="*75 + "\n")
    
    def test_health_endpoint(self, service: ServiceEndpoint) -> TestResult:
        """Test service health endpoint."""
        test_name = f"Health Check - {service.name}"
        start_time = time.time()
        
        try:
            health_url = urljoin(service.url, service.health_path)
            
            if self.verbose:
                print(f"  Testing {health_url}...")
            
            response = requests.get(
                health_url,
                timeout=service.timeout,
                headers={"User-Agent": "Railway-Smoke-Test/1.0"}
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return TestResult(
                        test_name=test_name,
                        service=service.name,
                        status="pass",
                        duration_ms=duration_ms,
                        message=f"✓ Health check passed ({duration_ms:.0f}ms)",
                        details={"response": data, "status_code": 200}
                    )
                except json.JSONDecodeError:
                    return TestResult(
                        test_name=test_name,
                        service=service.name,
                        status="pass",
                        duration_ms=duration_ms,
                        message=f"✓ Health check passed (non-JSON response, {duration_ms:.0f}ms)",
                        details={"status_code": 200}
                    )
            else:
                return TestResult(
                    test_name=test_name,
                    service=service.name,
                    status="fail",
                    duration_ms=duration_ms,
                    message=f"✗ Health check failed: HTTP {response.status_code}",
                    details={"status_code": response.status_code}
                )
                
        except requests.Timeout:
            duration_ms = (time.time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                service=service.name,
                status="fail",
                duration_ms=duration_ms,
                message=f"✗ Timeout after {duration_ms:.0f}ms",
                details={"error": "timeout"}
            )
        except requests.ConnectionError as e:
            duration_ms = (time.time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                service=service.name,
                status="fail" if service.required else "skip",
                duration_ms=duration_ms,
                message=f"✗ Connection failed: {str(e)[:50]}",
                details={"error": "connection_error"}
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                service=service.name,
                status="fail",
                duration_ms=duration_ms,
                message=f"✗ Unexpected error: {str(e)[:50]}",
                details={"error": str(e)}
            )
    
    def test_response_time(self, service: ServiceEndpoint, threshold_ms: int = 2000) -> TestResult:
        """Test service response time."""
        test_name = f"Response Time - {service.name}"
        start_time = time.time()
        
        try:
            health_url = urljoin(service.url, service.health_path)
            response = requests.get(health_url, timeout=service.timeout)
            duration_ms = (time.time() - start_time) * 1000
            
            if duration_ms < threshold_ms:
                return TestResult(
                    test_name=test_name,
                    service=service.name,
                    status="pass",
                    duration_ms=duration_ms,
                    message=f"✓ Response time: {duration_ms:.0f}ms (< {threshold_ms}ms)",
                    details={"threshold_ms": threshold_ms}
                )
            else:
                return TestResult(
                    test_name=test_name,
                    service=service.name,
                    status="fail",
                    duration_ms=duration_ms,
                    message=f"⚠ Slow response: {duration_ms:.0f}ms (> {threshold_ms}ms)",
                    details={"threshold_ms": threshold_ms}
                )
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                service=service.name,
                status="skip",
                duration_ms=duration_ms,
                message=f"Skip: {str(e)[:50]}",
                details={"error": str(e)}
            )
    
    def test_cors_headers(self, service: ServiceEndpoint) -> TestResult:
        """Test CORS configuration."""
        test_name = f"CORS Headers - {service.name}"
        start_time = time.time()
        
        try:
            health_url = urljoin(service.url, service.health_path)
            response = requests.options(
                health_url,
                timeout=service.timeout,
                headers={
                    "Origin": "https://coder.fastmonkey.au",
                    "Access-Control-Request-Method": "GET"
                }
            )
            duration_ms = (time.time() - start_time) * 1000
            
            has_cors = "Access-Control-Allow-Origin" in response.headers
            
            if has_cors:
                return TestResult(
                    test_name=test_name,
                    service=service.name,
                    status="pass",
                    duration_ms=duration_ms,
                    message="✓ CORS headers present",
                    details={"cors_origin": response.headers.get("Access-Control-Allow-Origin")}
                )
            else:
                return TestResult(
                    test_name=test_name,
                    service=service.name,
                    status="pass",  # Not critical
                    duration_ms=duration_ms,
                    message="⚠ No CORS headers (may be intentional)",
                    details={}
                )
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                service=service.name,
                status="skip",
                duration_ms=duration_ms,
                message=f"Skip: {str(e)[:50]}",
                details={"error": str(e)}
            )
    
    def test_ssl_certificate(self, service: ServiceEndpoint) -> TestResult:
        """Test SSL certificate validity."""
        test_name = f"SSL Certificate - {service.name}"
        start_time = time.time()
        
        try:
            if not service.url.startswith("https://"):
                return TestResult(
                    test_name=test_name,
                    service=service.name,
                    status="skip",
                    duration_ms=0,
                    message="Skip: Not HTTPS",
                    details={}
                )
            
            response = requests.get(
                urljoin(service.url, service.health_path),
                timeout=service.timeout,
                verify=True  # Will fail if cert is invalid
            )
            duration_ms = (time.time() - start_time) * 1000
            
            return TestResult(
                test_name=test_name,
                service=service.name,
                status="pass",
                duration_ms=duration_ms,
                message="✓ Valid SSL certificate",
                details={}
            )
            
        except requests.exceptions.SSLError as e:
            duration_ms = (time.time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                service=service.name,
                status="fail",
                duration_ms=duration_ms,
                message=f"✗ SSL certificate error: {str(e)[:50]}",
                details={"error": "ssl_error"}
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                service=service.name,
                status="skip",
                duration_ms=duration_ms,
                message=f"Skip: {str(e)[:50]}",
                details={"error": str(e)}
            )
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all smoke tests."""
        self.print_header()
        
        print("📋 Testing Services:")
        for service in self.services:
            print(f"  - {service.name}: {service.url}")
        print()
        
        # Run tests for each service
        for service in self.services:
            print(f"\n🔍 Testing {service.name} ({service.url})")
            print("-" * 75)
            
            # Health check (critical)
            result = self.test_health_endpoint(service)
            self.results.append(result)
            print(f"  {result.message}")
            
            # Only run additional tests if health check passed
            if result.status == "pass":
                # Response time
                result = self.test_response_time(service)
                self.results.append(result)
                print(f"  {result.message}")
                
                # CORS headers
                result = self.test_cors_headers(service)
                self.results.append(result)
                print(f"  {result.message}")
                
                # SSL certificate
                result = self.test_ssl_certificate(service)
                self.results.append(result)
                print(f"  {result.message}")
        
        # Generate summary
        return self.generate_summary()
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate test summary."""
        print("\n" + "="*75)
        print("📊 Test Summary")
        print("="*75 + "\n")
        
        passed = sum(1 for r in self.results if r.status == "pass")
        failed = sum(1 for r in self.results if r.status == "fail")
        skipped = sum(1 for r in self.results if r.status == "skip")
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"  ✓ Passed: {passed}")
        print(f"  ✗ Failed: {failed}")
        print(f"  ⊘ Skipped: {skipped}")
        print()
        
        # Show failures
        if failed > 0:
            print("❌ Failed Tests:")
            for result in self.results:
                if result.status == "fail":
                    print(f"  - {result.test_name}: {result.message}")
            print()
        
        # Calculate success rate
        success_rate = (passed / (passed + failed) * 100) if (passed + failed) > 0 else 0
        
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed == 0:
            print("✅ All critical tests passed!")
        else:
            print("❌ Some tests failed - review failures above")
        
        print("="*75 + "\n")
        
        # Calculate total duration
        total_duration = sum(r.duration_ms for r in self.results)
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "success_rate": success_rate,
                "duration_ms": total_duration
            },
            "tests": [asdict(r) for r in self.results]
        }
        
        return summary
    
    def save_report(self, summary: Dict[str, Any], output_file: str = "railway-smoke-test-report.json"):
        """Save test report to file."""
        output_path = PROJECT_ROOT / output_file
        
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"💾 Report saved to: {output_path}")
        return output_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Railway Deployment Smoke Test Suite"
    )
    parser.add_argument(
        "--base-url",
        help="Base URL for deployment to test (e.g., https://coder.fastmonkey.au)"
    )
    parser.add_argument(
        "--services",
        help="Comma-separated list of services to test (default: all)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--output",
        default="railway-smoke-test-report.json",
        help="Output file for test report"
    )
    
    args = parser.parse_args()
    
    # Create smoke test instance
    smoke_test = RailwaySmokeTest(
        timeout=args.timeout, 
        verbose=args.verbose,
        base_url=args.base_url
    )
    
    # Filter services if specified
    if args.services:
        service_names = [s.strip() for s in args.services.split(",")]
        smoke_test.services = [
            s for s in smoke_test.services 
            if s.name in service_names
        ]
    
    # Run tests
    summary = smoke_test.run_all_tests()
    
    # Save report
    smoke_test.save_report(summary, args.output)
    
    # Exit with error if tests failed
    if summary["failed"] > 0:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
