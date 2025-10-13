#!/usr/bin/env python3
"""
Railway Configuration Verification Script

This script verifies that Railway services are properly configured
according to the project standards and best practices.

Usage:
    python scripts/verify-railway-config.py [--service SERVICE] [--json]
    python scripts/verify-railway-config.py --check-all

Features:
- Verify environment variables are set
- Check service settings (root directory, config paths)
- Validate health check configuration
- Identify missing critical secrets
- Generate compliance report
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Service IDs for AetherOS project
SERVICE_IDS = {
    "monkey-coder": "ccc58ca2-1f4b-4086-beb6-2321ac7dab40",
    "monkey-coder-backend": "6af98d25-621b-4a2d-bbcb-7acb314fbfed",
    "monkey-coder-ml": "07ef6ac7-e412-4a24-a0dc-74e301413eaa"
}


@dataclass
class VerificationResult:
    """Verification result for a single check."""
    check_name: str
    status: str  # "pass", "fail", "warning", "skip"
    message: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class ServiceVerification:
    """Complete verification results for a service."""
    service_name: str
    service_id: str
    overall_status: str  # "pass", "fail", "warning"
    checks_passed: int = 0
    checks_failed: int = 0
    checks_warning: int = 0
    checks_skipped: int = 0
    results: List[VerificationResult] = field(default_factory=list)
    
    def add_result(self, result: VerificationResult):
        """Add a verification result and update counters."""
        self.results.append(result)
        if result.status == "pass":
            self.checks_passed += 1
        elif result.status == "fail":
            self.checks_failed += 1
        elif result.status == "warning":
            self.checks_warning += 1
        elif result.status == "skip":
            self.checks_skipped += 1
        
        # Update overall status
        if self.checks_failed > 0:
            self.overall_status = "fail"
        elif self.checks_warning > 0 and self.overall_status != "fail":
            self.overall_status = "warning"
        elif self.checks_passed > 0 and self.overall_status == "unknown":
            self.overall_status = "pass"


class RailwayConfigVerifier:
    """Verify Railway service configuration compliance."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.project_root = PROJECT_ROOT
        self.railway_available = self._check_railway_cli()
        
    def _check_railway_cli(self) -> bool:
        """Check if Railway CLI is available and authenticated."""
        try:
            result = subprocess.run(
                ['railway', '--version'],
                capture_output=True,
                text=True,
                timeout=5,
                shell=False
            )
            if result.returncode == 0:
                if self.verbose:
                    print(f"✓ Railway CLI available: {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        if self.verbose:
            print("⚠ Railway CLI not available - skipping CLI checks")
        return False
    
    def _run_railway_command(
        self, 
        command: List[str], 
        service_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Run a Railway CLI command and return result."""
        if not self.railway_available:
            return False, "Railway CLI not available"
        
        try:
            # Validate command arguments
            if not all(isinstance(arg, str) for arg in command):
                return False, "Invalid command arguments"
            
            # Build full command
            full_command = ['railway']
            if service_id:
                full_command.extend(['--service', service_id])
            full_command.extend(command)
            
            # Execute without shell for security
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=60,
                shell=False
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def get_required_variables(self, service_name: str) -> Dict[str, bool]:
        """
        Get required variables for a service.
        
        Returns:
            Dict mapping variable name to whether it's critical (True) or not (False)
        """
        common_vars = {
            "RAILWAY_CONFIG_FILE": False,
            "ENV": False,
            "NODE_ENV": False,
        }
        
        if service_name == "monkey-coder":
            return {
                **common_vars,
                "NEXT_OUTPUT_EXPORT": False,
                "NEXT_TELEMETRY_DISABLED": False,
                "NEXT_PUBLIC_APP_URL": False,
                "NEXT_PUBLIC_API_URL": False,
            }
        elif service_name == "monkey-coder-backend":
            return {
                **common_vars,
                "PYTHON_ENV": False,
                "LOG_LEVEL": False,
                "CORS_ORIGINS": False,
                "TRUSTED_HOSTS": False,
                "ENABLE_SECURITY_HEADERS": False,
                "HEALTH_CHECK_PATH": False,
                # Critical secrets
                "JWT_SECRET_KEY": True,
                "NEXTAUTH_SECRET": True,
                "OPENAI_API_KEY": True,
                "ANTHROPIC_API_KEY": True,
            }
        elif service_name == "monkey-coder-ml":
            return {
                **common_vars,
                "PYTHON_ENV": False,
                "LOG_LEVEL": False,
                "TRANSFORMERS_CACHE": False,
                "HEALTH_CHECK_PATH": False,
            }
        
        return {}
    
    def verify_environment_variables(
        self, 
        service_name: str, 
        service_id: str
    ) -> List[VerificationResult]:
        """Verify that required environment variables are set."""
        results = []
        
        # Check if Railway CLI is available
        if not self.railway_available:
            results.append(VerificationResult(
                check_name="environment_variables",
                status="skip",
                message="Railway CLI not available - cannot verify variables"
            ))
            return results
        
        # Get current variables
        success, output = self._run_railway_command(
            ['variables', 'list'],
            service_id=service_id
        )
        
        if not success:
            results.append(VerificationResult(
                check_name="environment_variables",
                status="fail",
                message=f"Failed to fetch variables: {output}"
            ))
            return results
        
        # Parse output to get set variables
        set_variables = set()
        for line in output.split('\n'):
            if '=' in line:
                var_name = line.split('=')[0].strip()
                set_variables.add(var_name)
        
        # Check required variables
        required_vars = self.get_required_variables(service_name)
        missing_vars = []
        missing_critical = []
        
        for var_name, is_critical in required_vars.items():
            if var_name not in set_variables:
                if is_critical:
                    missing_critical.append(var_name)
                else:
                    missing_vars.append(var_name)
        
        # Generate results
        if missing_critical:
            results.append(VerificationResult(
                check_name="critical_secrets",
                status="fail",
                message=f"Missing {len(missing_critical)} critical secrets",
                details={"missing": missing_critical}
            ))
        else:
            results.append(VerificationResult(
                check_name="critical_secrets",
                status="pass",
                message="All critical secrets are set"
            ))
        
        if missing_vars:
            results.append(VerificationResult(
                check_name="required_variables",
                status="warning",
                message=f"Missing {len(missing_vars)} recommended variables",
                details={"missing": missing_vars}
            ))
        else:
            results.append(VerificationResult(
                check_name="required_variables",
                status="pass",
                message="All required variables are set"
            ))
        
        return results
    
    def verify_railpack_config(self, service_name: str) -> List[VerificationResult]:
        """Verify that railpack configuration files exist and are valid."""
        results = []
        
        config_files = {
            "monkey-coder": "railpack.json",
            "monkey-coder-backend": "railpack-backend.json",
            "monkey-coder-ml": "railpack-ml.json"
        }
        
        config_file = config_files.get(service_name)
        if not config_file:
            results.append(VerificationResult(
                check_name="railpack_config",
                status="skip",
                message=f"Unknown service: {service_name}"
            ))
            return results
        
        config_path = self.project_root / config_file
        
        # Check if file exists
        if not config_path.exists():
            results.append(VerificationResult(
                check_name="railpack_exists",
                status="fail",
                message=f"Railpack config not found: {config_file}"
            ))
            return results
        
        results.append(VerificationResult(
            check_name="railpack_exists",
            status="pass",
            message=f"Railpack config exists: {config_file}"
        ))
        
        # Validate JSON
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check required fields
            required_fields = ['$schema', 'version', 'metadata', 'build', 'deploy']
            missing_fields = [f for f in required_fields if f not in config]
            
            if missing_fields:
                results.append(VerificationResult(
                    check_name="railpack_structure",
                    status="fail",
                    message=f"Missing required fields: {', '.join(missing_fields)}"
                ))
            else:
                results.append(VerificationResult(
                    check_name="railpack_structure",
                    status="pass",
                    message="Railpack config has valid structure"
                ))
            
            # Check health check configuration
            if 'deploy' in config and 'healthCheckPath' in config['deploy']:
                health_path = config['deploy']['healthCheckPath']
                results.append(VerificationResult(
                    check_name="health_check_config",
                    status="pass",
                    message=f"Health check configured: {health_path}",
                    details={"path": health_path}
                ))
            else:
                results.append(VerificationResult(
                    check_name="health_check_config",
                    status="warning",
                    message="No health check path configured in railpack"
                ))
                
        except json.JSONDecodeError as e:
            results.append(VerificationResult(
                check_name="railpack_json",
                status="fail",
                message=f"Invalid JSON in {config_file}: {e}"
            ))
        
        return results
    
    def verify_service(self, service_name: str) -> ServiceVerification:
        """Verify a single service configuration."""
        service_id = SERVICE_IDS.get(service_name)
        if not service_id:
            verification = ServiceVerification(
                service_name=service_name,
                service_id="unknown",
                overall_status="fail"
            )
            verification.add_result(VerificationResult(
                check_name="service_exists",
                status="fail",
                message=f"Unknown service: {service_name}"
            ))
            return verification
        
        verification = ServiceVerification(
            service_name=service_name,
            service_id=service_id,
            overall_status="unknown"
        )
        
        print(f"\n{'='*70}")
        print(f"🔍 Verifying Service: {service_name}")
        print(f"{'='*70}")
        print(f"Service ID: {service_id}")
        print()
        
        # Verify railpack configuration
        print("📋 Checking railpack configuration...")
        for result in self.verify_railpack_config(service_name):
            verification.add_result(result)
            self._print_result(result)
        
        # Verify environment variables
        print("\n📋 Checking environment variables...")
        for result in self.verify_environment_variables(service_name, service_id):
            verification.add_result(result)
            self._print_result(result)
        
        # Print summary
        print(f"\n{'─'*70}")
        status_icon = {
            "pass": "✅",
            "warning": "⚠️",
            "fail": "❌",
            "unknown": "❓"
        }.get(verification.overall_status, "❓")
        
        print(f"{status_icon} Overall Status: {verification.overall_status.upper()}")
        print(f"   Checks Passed: {verification.checks_passed}")
        print(f"   Checks Failed: {verification.checks_failed}")
        print(f"   Warnings: {verification.checks_warning}")
        print(f"   Skipped: {verification.checks_skipped}")
        
        return verification
    
    def _print_result(self, result: VerificationResult):
        """Print a verification result."""
        status_icons = {
            "pass": "✓",
            "fail": "✗",
            "warning": "⚠",
            "skip": "○"
        }
        icon = status_icons.get(result.status, "?")
        
        print(f"  {icon} {result.check_name}: {result.message}")
        
        if self.verbose and result.details:
            for key, value in result.details.items():
                print(f"      {key}: {value}")
    
    def verify_all_services(self) -> Dict[str, ServiceVerification]:
        """Verify all services."""
        print("\n" + "="*70)
        print("🚂 Railway Configuration Verification")
        print("="*70)
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        if not self.railway_available:
            print("\n⚠️  Railway CLI not available - limited verification")
        
        results = {}
        for service_name in SERVICE_IDS.keys():
            results[service_name] = self.verify_service(service_name)
        
        # Print overall summary
        print("\n" + "="*70)
        print("📊 Verification Summary")
        print("="*70)
        
        total_passed = sum(v.checks_passed for v in results.values())
        total_failed = sum(v.checks_failed for v in results.values())
        total_warnings = sum(v.checks_warning for v in results.values())
        
        for service_name, verification in results.items():
            status_icon = {
                "pass": "✅",
                "warning": "⚠️",
                "fail": "❌"
            }.get(verification.overall_status, "❓")
            
            print(f"\n{status_icon} {service_name}")
            print(f"   Status: {verification.overall_status.upper()}")
            print(f"   Checks: {verification.checks_passed} passed, "
                  f"{verification.checks_failed} failed, "
                  f"{verification.checks_warning} warnings")
        
        print(f"\n{'='*70}")
        print(f"Total Checks: {total_passed} passed, {total_failed} failed, {total_warnings} warnings")
        
        # Determine overall compliance
        if total_failed > 0:
            print("\n❌ CONFIGURATION NOT COMPLIANT - Fix failed checks")
        elif total_warnings > 0:
            print("\n⚠️  CONFIGURATION MOSTLY COMPLIANT - Review warnings")
        else:
            print("\n✅ CONFIGURATION FULLY COMPLIANT")
        
        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Railway Configuration Verification Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify all services
  python scripts/verify-railway-config.py
  
  # Verify specific service
  python scripts/verify-railway-config.py --service monkey-coder-backend
  
  # Generate JSON report
  python scripts/verify-railway-config.py --json > report.json
  
  # Verbose output
  python scripts/verify-railway-config.py --verbose
        """
    )
    parser.add_argument(
        "--service",
        choices=["monkey-coder", "monkey-coder-backend", "monkey-coder-ml"],
        help="Verify specific service only"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--check-all",
        action="store_true",
        help="Alias for verifying all services"
    )
    
    args = parser.parse_args()
    
    # Create verifier
    verifier = RailwayConfigVerifier(verbose=args.verbose)
    
    # Verify services
    if args.service:
        result = verifier.verify_service(args.service)
        results = {args.service: result}
    else:
        results = verifier.verify_all_services()
    
    # Output JSON if requested
    if args.json:
        json_output = {
            "timestamp": datetime.now().isoformat(),
            "services": {
                name: {
                    "service_id": v.service_id,
                    "overall_status": v.overall_status,
                    "checks_passed": v.checks_passed,
                    "checks_failed": v.checks_failed,
                    "checks_warning": v.checks_warning,
                    "results": [asdict(r) for r in v.results]
                }
                for name, v in results.items()
            }
        }
        print("\n" + json.dumps(json_output, indent=2))
    
    # Exit with error if any checks failed
    if any(v.overall_status == "fail" for v in results.values()):
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
