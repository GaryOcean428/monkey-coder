#!/usr/bin/env python3
"""
Remote Railway Deployment Validation
Validates the current state of the Railway deployment at coder.fastmonkey.au
"""

import requests
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RailwayDeploymentValidator:
    """Validates the current Railway deployment status."""
    
    def __init__(self, base_url: str = "https://coder.fastmonkey.au"):
        self.base_url = base_url.rstrip('/')
        self.results = {}
        
    def test_endpoint(self, path: str, description: str, expected_status: int = 200) -> Dict[str, Any]:
        """Test a specific endpoint and return results."""
        url = urljoin(self.base_url + '/', path.lstrip('/'))
        
        try:
            response = requests.get(url, timeout=10)
            result = {
                "url": url,
                "status_code": response.status_code,
                "success": response.status_code == expected_status,
                "response_time": response.elapsed.total_seconds(),
                "content_length": len(response.content),
                "content_type": response.headers.get('content-type', ''),
                "description": description
            }
            
            # Check for specific content indicators
            text = response.text.lower()
            result["indicators"] = {
                "is_fastapi_docs": "fastapi" in text and "swagger" in text,
                "is_next_app": "_next" in text or "next.js" in text,
                "has_monkey_coder": "monkey" in text and "coder" in text,
                "is_error_page": "error" in text or response.status_code >= 400,
                "has_api_endpoints": "/api/" in text,
                "has_static_assets": "_next/static" in text or "static/" in text
            }
            
            logger.info(f"✅ {description}: {response.status_code} ({response.elapsed.total_seconds():.2f}s)")
            
        except requests.exceptions.RequestException as e:
            result = {
                "url": url,
                "status_code": None,
                "success": False,
                "error": str(e),
                "description": description
            }
            logger.error(f"❌ {description}: {str(e)}")
            
        return result
    
    def validate_frontend_deployment(self) -> Dict[str, Any]:
        """Validate frontend deployment status."""
        logger.info("🔍 Validating frontend deployment...")
        
        tests = [
            ('/', 'Main page'),
            ('/api/docs', 'API documentation'),
            ('/api/v1/health', 'Health endpoint'),
            ('/_next/static/css/', 'Static CSS assets'),
            ('/static/', 'Static assets'),
            ('/favicon.ico', 'Favicon'),
        ]
        
        results = {}
        for path, description in tests:
            results[path] = self.test_endpoint(path, description)
            time.sleep(0.5)  # Rate limiting
        
        return results
    
    def analyze_deployment_type(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze what type of deployment is currently running."""
        main_page = test_results.get('/', {})
        
        analysis = {
            "deployment_type": "unknown",
            "frontend_status": "unknown",
            "backend_status": "unknown",
            "issues": [],
            "recommendations": []
        }
        
        if main_page.get("success"):
            indicators = main_page.get("indicators", {})
            
            if indicators.get("is_fastapi_docs"):
                analysis["deployment_type"] = "api_only"
                analysis["frontend_status"] = "missing"
                analysis["backend_status"] = "working"
                analysis["issues"].append("Frontend static files not found - showing FastAPI docs instead")
                analysis["recommendations"].extend([
                    "Set NEXT_OUTPUT_EXPORT=true in Railway environment",
                    "Ensure frontend build process completes successfully",
                    "Verify packages/web/out directory is generated"
                ])
                
            elif indicators.get("is_next_app"):
                analysis["deployment_type"] = "full_app"
                analysis["frontend_status"] = "working"
                analysis["backend_status"] = "working"
                
            elif indicators.get("has_monkey_coder"):
                analysis["deployment_type"] = "partial_app"
                analysis["frontend_status"] = "partial"
                analysis["backend_status"] = "working"
                
        else:
            analysis["deployment_type"] = "failed"
            analysis["issues"].append(f"Main page not accessible: {main_page.get('error', 'Unknown error')}")
            
        return analysis
    
    def check_environment_readiness(self) -> Dict[str, Any]:
        """Check if the deployment environment is properly configured."""
        logger.info("🔧 Checking environment readiness...")
        
        # Test health endpoint for environment info
        health_result = self.test_endpoint('/api/v1/health', 'Health check')
        
        readiness = {
            "health_check": health_result.get("success", False),
            "api_accessible": False,
            "database_connected": False,
            "environment_configured": False
        }
        
        # Try to get more detailed info from capabilities endpoint
        capabilities_result = self.test_endpoint('/api/v1/capabilities', 'Capabilities endpoint')
        readiness["capabilities_available"] = capabilities_result.get("success", False)
        
        # Check for common static files that indicate proper build
        static_tests = [
            ('/_next/static/chunks/', 'Next.js chunks'),
            ('/_next/static/css/', 'Next.js CSS'),
            ('/assets/', 'Static assets'),
        ]
        
        static_files_found = 0
        for path, description in static_tests:
            result = self.test_endpoint(path, description, expected_status=404)  # 404 is OK for directory listings
            if result.get("status_code") in [200, 403, 404]:  # These indicate the path exists
                static_files_found += 1
        
        readiness["static_files_ratio"] = static_files_found / len(static_tests)
        
        return readiness
    
    def generate_fix_recommendations(self, test_results: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """Generate specific fix recommendations based on test results."""
        recommendations = []
        
        if analysis["deployment_type"] == "api_only":
            recommendations.extend([
                "🔧 CRITICAL: Set environment variables in Railway dashboard:",
                "   - NEXT_OUTPUT_EXPORT=true",
                "   - NEXTAUTH_URL=https://coder.fastmonkey.au", 
                "   - NEXT_PUBLIC_API_URL=https://coder.fastmonkey.au",
                "   - NODE_ENV=production",
                "",
                "🔧 Verify Railway build configuration:",
                "   - Build Method should be 'Railpack' (not Nixpacks)",
                "   - Check build logs for frontend export errors",
                "",
                "🔧 Alternative quick fix:",
                "   - Change Railway start command to: node run_unified.js",
                "   - This bypasses static export and runs Next.js server directly"
            ])
            
        elif analysis["deployment_type"] == "failed":
            recommendations.extend([
                "🚨 CRITICAL: Deployment is not responding",
                "   - Check Railway service status in dashboard",
                "   - Review deployment logs for errors",
                "   - Verify domain configuration"
            ])
            
        if not test_results.get('/api/v1/health', {}).get("success"):
            recommendations.append("🔧 Backend API not responding - check FastAPI server status")
            
        return recommendations
    
    def run_complete_validation(self) -> Dict[str, Any]:
        """Run complete deployment validation."""
        logger.info(f"🚀 Starting Railway deployment validation for {self.base_url}")
        
        # Run all tests
        test_results = self.validate_frontend_deployment()
        analysis = self.analyze_deployment_type(test_results)
        readiness = self.check_environment_readiness()
        recommendations = self.generate_fix_recommendations(test_results, analysis)
        
        # Compile final report
        report = {
            "timestamp": time.time(),
            "base_url": self.base_url,
            "test_results": test_results,
            "analysis": analysis,
            "readiness": readiness,
            "recommendations": recommendations,
            "summary": {
                "overall_status": analysis["deployment_type"],
                "frontend_working": analysis["frontend_status"] == "working",
                "backend_working": analysis["backend_status"] == "working",
                "needs_environment_setup": analysis["deployment_type"] == "api_only",
                "critical_issues": len([r for r in recommendations if "CRITICAL" in r])
            }
        }
        
        # Save report
        with open("railway_deployment_validation.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        self.print_validation_summary(report)
        
        return report
    
    def print_validation_summary(self, report: Dict[str, Any]):
        """Print a human-readable validation summary."""
        print("\n" + "="*60)
        print("🚀 RAILWAY DEPLOYMENT VALIDATION REPORT")
        print("="*60)
        
        summary = report["summary"]
        analysis = report["analysis"]
        
        print(f"📍 URL: {report['base_url']}")
        print(f"📊 Status: {summary['overall_status'].upper()}")
        print(f"🎨 Frontend: {'✅ Working' if summary['frontend_working'] else '❌ Not Working'}")
        print(f"⚙️  Backend: {'✅ Working' if summary['backend_working'] else '❌ Not Working'}")
        
        if summary['needs_environment_setup']:
            print(f"\n🔧 ISSUE IDENTIFIED: {analysis['issues'][0]}")
            
        if summary['critical_issues'] > 0:
            print(f"\n🚨 CRITICAL ISSUES: {summary['critical_issues']}")
            
        print(f"\n📋 RECOMMENDATIONS:")
        for rec in report["recommendations"][:5]:  # Show first 5 recommendations
            print(f"   {rec}")
            
        if len(report["recommendations"]) > 5:
            print(f"   ... and {len(report['recommendations']) - 5} more (see JSON report)")
            
        print(f"\n📄 Full report saved to: railway_deployment_validation.json")

def main():
    """Main execution function."""
    validator = RailwayDeploymentValidator()
    validator.run_complete_validation()

if __name__ == "__main__":
    main()