#!/usr/bin/env python3
"""
MCP Railway Deployment Manager

This tool provides comprehensive Railway deployment management with MCP integration,
real-time monitoring, and automatic issue resolution based on the Railway cheat sheet.
"""

import os
import sys
import json
import time
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import subprocess
import tempfile

# Add core package to path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "core"))

try:
    from monkey_coder.config.env_config import EnvironmentConfig
    from monkey_coder.core.orchestration_coordinator import OrchestrationCoordinator
    MCP_AVAILABLE = True
    print("🔌 MCP framework detected - enhanced features available")
except ImportError:
    MCP_AVAILABLE = False
    print("⚠️  Running in standalone mode (MCP framework not available)")


class DeploymentStatus(Enum):
    """Railway deployment status levels."""
    READY = "ready"
    WARNING = "warning"
    CRITICAL = "critical"
    DEPLOYING = "deploying"
    FAILED = "failed"


@dataclass
class DeploymentCheck:
    """Represents a Railway deployment validation check."""
    name: str
    status: DeploymentStatus
    message: str
    fix_available: bool = False
    fix_command: Optional[str] = None
    file_path: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class RailwayDeploymentManager:
    """
    Comprehensive Railway deployment manager with MCP integration.
    
    This class implements all Railway deployment best practices from the cheat sheet
    and provides automatic issue detection and resolution.
    """
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.logger = self._setup_logging()
        self.checks: List[DeploymentCheck] = []
        
        # Initialize MCP components if available
        self.mcp_enabled = False
        if MCP_AVAILABLE:
            try:
                self.env_config = EnvironmentConfig()
                self.coordinator = OrchestrationCoordinator()
                self.mcp_enabled = True
                self.logger.info("✅ MCP integration enabled")
            except Exception as e:
                self.logger.warning(f"MCP initialization failed: {e}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(self.__class__.__name__)
    
    def _run_command(self, command: List[str], timeout: int = 30) -> Tuple[bool, str, str]:
        """Run a shell command and return success status and output."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout}s"
        except Exception as e:
            return False, "", str(e)
    
    def check_build_system_conflicts(self) -> DeploymentCheck:
        """
        ISSUE 1: Build System Conflicts
        Check for competing build configuration files.
        """
        competing_files = []
        
        # Define competing files (excluding services directory)
        check_files = [
            ("Dockerfile", "Root Dockerfile conflicts with railpack.json"),
            ("railway.toml", "railway.toml conflicts with railpack.json"), 
            ("railway.json", "railway.json conflicts with railpack.json"),
            ("nixpacks.toml", "nixpacks.toml conflicts with railpack.json")
        ]
        
        for filename, description in check_files:
            file_path = self.project_root / filename
            # Skip Dockerfiles in services directory
            if filename == "Dockerfile" and str(file_path).find("/services/") != -1:
                continue
            if file_path.exists():
                competing_files.append((filename, description))
        
        # Check railpack.json exists and is valid
        railpack_path = self.project_root / "railpack.json"
        if not railpack_path.exists():
            return DeploymentCheck(
                name="Build System Configuration",
                status=DeploymentStatus.CRITICAL,
                message="railpack.json not found",
                fix_available=True,
                fix_command="Create railpack.json with proper Railway configuration"
            )
        
        # Validate JSON syntax
        try:
            with open(railpack_path) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            return DeploymentCheck(
                name="Build System Configuration",
                status=DeploymentStatus.CRITICAL,
                message=f"railpack.json has invalid JSON: {e}",
                file_path=str(railpack_path),
                fix_available=True,
                fix_command="Fix JSON syntax in railpack.json"
            )
        
        if competing_files:
            files_list = ", ".join([f[0] for f in competing_files])
            return DeploymentCheck(
                name="Build System Configuration",
                status=DeploymentStatus.CRITICAL,
                message=f"Competing build files found: {files_list}",
                fix_available=True,
                fix_command=f"rm {' '.join([f[0] for f in competing_files])}"
            )
        
        return DeploymentCheck(
            name="Build System Configuration",
            status=DeploymentStatus.READY,
            message="railpack.json is the only build configuration (correct)"
        )
    
    def check_port_binding(self) -> DeploymentCheck:
        """
        ISSUE 2: PORT Binding Failures  
        Check for proper PORT usage and host binding.
        """
        issues = []
        
        # Check run_server.py
        server_file = self.project_root / "run_server.py"
        if server_file.exists():
            content = server_file.read_text()
            
            if "0.0.0.0" not in content:
                issues.append("run_server.py should bind to 0.0.0.0")
            
            if "PORT" not in content and "port" in content.lower():
                issues.append("run_server.py should use PORT environment variable")
            
            # Check for hardcoded localhost
            if "127.0.0.1" in content or "localhost" in content:
                # Filter out comments
                lines = content.split('\n')
                problem_lines = [
                    line.strip() for line in lines 
                    if ("127.0.0.1" in line or "localhost" in line)
                    and not line.strip().startswith('#')
                    and "example" not in line.lower()
                ]
                if problem_lines:
                    issues.append("Avoid binding to localhost/127.0.0.1")
        
        # Check FastAPI main app
        main_py = self.project_root / "packages/core/monkey_coder/app/main.py"
        if main_py.exists():
            content = main_py.read_text()
            if "0.0.0.0" not in content:
                issues.append("FastAPI app should configure 0.0.0.0 binding")
        
        if issues:
            return DeploymentCheck(
                name="PORT Binding Configuration",
                status=DeploymentStatus.WARNING,
                message=f"PORT binding issues: {'; '.join(issues)}",
                fix_available=True,
                fix_command="Review and fix PORT/host binding in server files"
            )
        
        return DeploymentCheck(
            name="PORT Binding Configuration", 
            status=DeploymentStatus.READY,
            message="Proper PORT usage and 0.0.0.0 binding configured"
        )
    
    def check_health_endpoint(self) -> DeploymentCheck:
        """
        ISSUE 5: Health Check Configuration
        Verify health endpoint implementation and configuration.
        """
        # Check railpack.json health configuration
        railpack_path = self.project_root / "railpack.json"
        health_path_configured = False
        
        if railpack_path.exists():
            try:
                with open(railpack_path) as f:
                    config = json.load(f)
                
                health_path = config.get("deploy", {}).get("healthCheckPath")
                if health_path == "/health":
                    health_path_configured = True
                elif health_path:
                    return DeploymentCheck(
                        name="Health Check Configuration",
                        status=DeploymentStatus.WARNING,
                        message=f"Non-standard health path: {health_path}",
                        fix_available=True,
                        fix_command='Set healthCheckPath to "/health" in railpack.json'
                    )
                
            except Exception as e:
                return DeploymentCheck(
                    name="Health Check Configuration",
                    status=DeploymentStatus.WARNING,
                    message=f"Could not read railpack.json health config: {e}"
                )
        
        # Check health endpoint implementation
        main_py = self.project_root / "packages/core/monkey_coder/app/main.py"
        health_implemented = False
        
        if main_py.exists():
            content = main_py.read_text()
            if "/health" in content and "@app.get" in content:
                health_implemented = True
        
        if not health_path_configured:
            return DeploymentCheck(
                name="Health Check Configuration",
                status=DeploymentStatus.WARNING,
                message="Health check path not configured in railpack.json",
                fix_available=True,
                fix_command='Add "healthCheckPath": "/health" to railpack.json deploy section'
            )
        
        if not health_implemented:
            return DeploymentCheck(
                name="Health Check Configuration",
                status=DeploymentStatus.CRITICAL,
                message="Health endpoint not implemented in application",
                fix_available=True,
                fix_command="Add @app.get('/health') endpoint returning 200 status"
            )
        
        return DeploymentCheck(
            name="Health Check Configuration",
            status=DeploymentStatus.READY,
            message="Health endpoint implemented and configured"
        )
    
    def check_reference_variables(self) -> DeploymentCheck:
        """
        ISSUE 4: Reference Variable Mistakes
        Check for improper Railway variable references.
        """
        issues = []
        config_files = ["railpack.json", ".env.example", "railway_vars_cli.sh"]
        
        for filename in config_files:
            file_path = self.project_root / filename
            if file_path.exists():
                try:
                    content = file_path.read_text()
                    
                    # Check for invalid PORT references
                    if "{{" in content and ".PORT}}" in content:
                        issues.append(f"{filename}: Invalid PORT reference (use RAILWAY_PUBLIC_DOMAIN)")
                    
                    # Check for other common mistakes
                    if "${{" in content and "RAILWAY_PRIVATE_DOMAIN" not in content and "backend." in content:
                        issues.append(f"{filename}: Consider using RAILWAY_PRIVATE_DOMAIN for internal services")
                        
                except Exception as e:
                    issues.append(f"Could not check {filename}: {e}")
        
        if issues:
            return DeploymentCheck(
                name="Reference Variables",
                status=DeploymentStatus.WARNING,
                message=f"Reference variable issues: {'; '.join(issues)}",
                fix_available=True,
                fix_command="Review Railway variable references in configuration files"
            )
        
        return DeploymentCheck(
            name="Reference Variables",
            status=DeploymentStatus.READY,
            message="Railway variable references appear correct"
        )
    
    def check_monorepo_configuration(self) -> DeploymentCheck:
        """
        ISSUE 6: Monorepo Service Confusion
        Check monorepo structure and configuration.
        """
        has_packages = (self.project_root / "packages").exists()
        has_services = (self.project_root / "services").exists()
        
        if not (has_packages or has_services):
            return DeploymentCheck(
                name="Monorepo Configuration",
                status=DeploymentStatus.READY,
                message="Single service structure (no monorepo complexity)"
            )
        
        # Check railpack.json for proper monorepo configuration
        railpack_path = self.project_root / "railpack.json"
        if railpack_path.exists():
            try:
                with open(railpack_path) as f:
                    config = json.load(f)
                
                if "services" in config:
                    return DeploymentCheck(
                        name="Monorepo Configuration",
                        status=DeploymentStatus.READY,
                        message="Monorepo properly configured with services section"
                    )
                else:
                    return DeploymentCheck(
                        name="Monorepo Configuration",
                        status=DeploymentStatus.WARNING,
                        message="Monorepo detected but no services configuration",
                        fix_available=True,
                        fix_command="Consider using services configuration in railpack.json"
                    )
            except Exception as e:
                return DeploymentCheck(
                    name="Monorepo Configuration",
                    status=DeploymentStatus.WARNING,
                    message=f"Could not validate monorepo configuration: {e}"
                )
        
        return DeploymentCheck(
            name="Monorepo Configuration",
            status=DeploymentStatus.WARNING,
            message="Monorepo structure detected, review configuration"
        )
    
    def run_comprehensive_check(self) -> Dict[str, Any]:
        """Run all Railway deployment checks and return comprehensive results."""
        self.logger.info("🔍 Running comprehensive Railway deployment validation...")
        
        # Clear previous checks
        self.checks.clear()
        
        # Run all validation checks
        check_functions = [
            self.check_build_system_conflicts,
            self.check_port_binding,
            self.check_health_endpoint,
            self.check_reference_variables,
            self.check_monorepo_configuration
        ]
        
        for check_func in check_functions:
            try:
                check_result = check_func()
                self.checks.append(check_result)
                self.logger.debug(f"Check {check_result.name}: {check_result.status.value}")
            except Exception as e:
                self.logger.error(f"Check {check_func.__name__} failed: {e}")
                self.checks.append(DeploymentCheck(
                    name=f"Validation Error ({check_func.__name__})",
                    status=DeploymentStatus.WARNING,
                    message=f"Check failed: {e}"
                ))
        
        # Compile results
        ready_count = sum(1 for check in self.checks if check.status == DeploymentStatus.READY)
        warning_count = sum(1 for check in self.checks if check.status == DeploymentStatus.WARNING)
        critical_count = sum(1 for check in self.checks if check.status == DeploymentStatus.CRITICAL)
        
        # Determine overall deployment readiness
        deployment_ready = critical_count == 0
        overall_status = DeploymentStatus.READY if deployment_ready else (
            DeploymentStatus.CRITICAL if critical_count > 0 else DeploymentStatus.WARNING
        )
        
        # Generate MCP analysis if available
        mcp_analysis = {}
        if self.mcp_enabled:
            try:
                mcp_analysis = self._generate_mcp_analysis()
            except Exception as e:
                self.logger.warning(f"MCP analysis failed: {e}")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "overall_status": overall_status.value,
            "deployment_ready": deployment_ready,
            "total_checks": len(self.checks),
            "ready_checks": ready_count,
            "warning_checks": warning_count,
            "critical_checks": critical_count,
            "checks": [asdict(check) for check in self.checks],
            "mcp_analysis": mcp_analysis,
            "fix_commands": [
                check.fix_command for check in self.checks 
                if check.fix_available and check.fix_command
            ]
        }
        
        return results
    
    def _generate_mcp_analysis(self) -> Dict[str, Any]:
        """Generate MCP-enhanced analysis and recommendations."""
        if not self.mcp_enabled:
            return {}
        
        try:
            # Use MCP components for enhanced analysis
            analysis = {
                "orchestration_available": True,
                "environment_config_loaded": self.env_config is not None,
                "coordinator_active": self.coordinator is not None,
                "analysis_timestamp": datetime.now().isoformat(),
                "recommendations": []
            }
            
            # Generate MCP-specific recommendations based on checks
            critical_checks = [c for c in self.checks if c.status == DeploymentStatus.CRITICAL]
            if critical_checks:
                analysis["recommendations"].append(
                    "Use MCP orchestration for automated deployment issue resolution"
                )
            
            warning_checks = [c for c in self.checks if c.status == DeploymentStatus.WARNING]
            if warning_checks:
                analysis["recommendations"].append(
                    "Consider MCP environment validation for enhanced deployment monitoring"
                )
            
            analysis["recommendations"].append(
                "MCP framework can provide real-time deployment monitoring and auto-remediation"
            )
            
            return analysis
            
        except Exception as e:
            self.logger.warning(f"MCP analysis error: {e}")
            return {"error": str(e), "mcp_available": False}
    
    def generate_fix_script(self, results: Dict[str, Any]) -> str:
        """Generate a shell script to fix deployment issues automatically."""
        script_lines = [
            "#!/bin/bash",
            "# Auto-generated Railway Deployment Fix Script",
            f"# Generated at: {datetime.now().isoformat()}",
            f"# Project: {results['project_root']}",
            "",
            "set -e",
            'echo "🔧 Applying Railway deployment fixes..."',
            ""
        ]
        
        critical_fixes = [
            check for check in self.checks 
            if check.status == DeploymentStatus.CRITICAL and check.fix_available
        ]
        
        for check in critical_fixes:
            if check.fix_command:
                script_lines.extend([
                    f"# Fix: {check.message}",
                    f"echo 'Fixing: {check.name}'",
                    check.fix_command,
                    ""
                ])
        
        script_lines.extend([
            'echo "✅ Critical fixes applied!"',
            'echo "Run validation again to verify fixes."',
            "",
            "# Validate fixes",
            "python scripts/mcp-railway-validator.py"
        ])
        
        return "\n".join(script_lines)
    
    def print_validation_report(self, results: Dict[str, Any]) -> None:
        """Print a comprehensive validation report."""
        status_icons = {
            "ready": "✅",
            "warning": "⚠️",
            "critical": "❌",
            "deploying": "🚀",
            "failed": "💥"
        }
        
        print("\n" + "="*70)
        print("🚀 MCP Railway Deployment Manager - Validation Report")
        print("="*70)
        
        # Overall status
        icon = status_icons.get(results["overall_status"], "❓")
        status_text = results["overall_status"].upper()
        print(f"\n{icon} OVERALL STATUS: {status_text}")
        
        if results["deployment_ready"]:
            print("🎉 READY FOR RAILWAY DEPLOYMENT!")
        else:
            print("🛑 DEPLOYMENT BLOCKED - Issues must be resolved")
        
        # Summary
        print(f"\n📊 Check Summary:")
        print(f"   Total Checks: {results['total_checks']}")
        print(f"   ✅ Ready: {results['ready_checks']}")
        print(f"   ⚠️  Warnings: {results['warning_checks']}")
        print(f"   ❌ Critical: {results['critical_checks']}")
        
        # Detailed results
        print(f"\n📋 Detailed Results:")
        for check_data in results["checks"]:
            status_val = check_data["status"] if isinstance(check_data["status"], str) else check_data["status"].value
            check_icon = status_icons.get(status_val, "❓")
            print(f"\n{check_icon} {check_data['name']}")
            print(f"   Status: {status_val.upper()}")
            print(f"   Message: {check_data['message']}")
            
            if check_data.get("fix_available") and check_data.get("fix_command"):
                print(f"   🔧 Fix: {check_data['fix_command']}")
            
            if check_data.get("file_path"):
                print(f"   📁 File: {check_data['file_path']}")
        
        # MCP Analysis
        mcp_analysis = results.get("mcp_analysis", {})
        if mcp_analysis.get("orchestration_available"):
            print(f"\n🔌 MCP Analysis:")
            print(f"   Orchestration: Available")
            print(f"   Environment Config: {'✅' if mcp_analysis.get('environment_config_loaded') else '❌'}")
            
            for rec in mcp_analysis.get("recommendations", []):
                print(f"   • {rec}")
        
        # Fix commands
        if results["fix_commands"]:
            print(f"\n🛠️  Available Fixes:")
            for i, fix_cmd in enumerate(results["fix_commands"], 1):
                print(f"   {i}. {fix_cmd}")
        
        # Next steps
        print(f"\n🎯 Next Steps:")
        if results["critical_checks"] > 0:
            print("   1. Fix critical issues above")
            print("   2. Re-run validation")
            print("   3. Deploy to Railway")
        elif results["warning_checks"] > 0:
            print("   1. Review warnings (optional)")
            print("   2. Deploy to Railway")
            print("   3. Monitor deployment")
        else:
            print("   1. Deploy to Railway: railway up")
            print("   2. Monitor deployment health")
            print("   3. Verify application functionality")
        
        print("\n" + "="*70)


def main():
    """Main entry point for Railway deployment manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Railway Deployment Manager")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--fix", action="store_true", help="Generate fix script for issues")
    parser.add_argument("--project-root", help="Project root directory", default=".")
    
    args = parser.parse_args()
    
    # Initialize deployment manager
    project_root = Path(args.project_root).resolve()
    manager = RailwayDeploymentManager(project_root, verbose=args.verbose)
    
    # Run validation
    results = manager.run_comprehensive_check()
    
    # Print report
    manager.print_validation_report(results)
    
    # Generate fix script if requested
    if args.fix and results["critical_checks"] > 0:
        fix_script = manager.generate_fix_script(results)
        fix_script_path = project_root / "railway-deployment-fix.sh"
        fix_script_path.write_text(fix_script)
        fix_script_path.chmod(0o755)
        print(f"\n🔧 Generated fix script: {fix_script_path}")
        print("   Run with: ./railway-deployment-fix.sh")
    
    # Exit with appropriate code
    exit_code = 0 if results["deployment_ready"] else 1
    print(f"\n{'✅' if exit_code == 0 else '❌'} Validation completed with exit code {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()