#!/usr/bin/env python3
"""
MCP-Enhanced Railway Deployment Validator

This script uses the Model Context Protocol (MCP) framework to provide
comprehensive Railway deployment validation and automatic fix suggestions
following the Railway Deployment Master Cheat Sheet.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
from enum import Enum

# Add the core package to path for MCP imports
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "core"))

try:
    from monkey_coder.config.env_config import EnvironmentConfig
    from monkey_coder.core.orchestration_coordinator import OrchestrationCoordinator
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP framework not available, running in standalone mode")


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    CRITICAL = "critical"  # Will cause deployment failure
    WARNING = "warning"   # May cause issues but not failure
    INFO = "info"        # Best practice recommendations


@dataclass
class ValidationIssue:
    """Represents a Railway deployment validation issue."""
    severity: ValidationSeverity
    category: str
    description: str
    fix_command: Optional[str] = None
    file_path: Optional[str] = None


class RailwayValidationOrchestrator:
    """Enhanced Railway validator using MCP orchestration patterns."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logging.getLogger(self.__class__.__name__)
        self.issues: List[ValidationIssue] = []
        
        # Initialize MCP components if available
        if MCP_AVAILABLE:
            try:
                self.env_config = EnvironmentConfig()
                self.coordinator = OrchestrationCoordinator()
                self.mcp_enabled = True
            except Exception as e:
                self.logger.warning(f"MCP initialization failed: {e}")
                self.mcp_enabled = False
        else:
            self.mcp_enabled = False

    def validate_build_system_conflicts(self) -> None:
        """
        Validate ISSUE 1: Build System Conflicts
        Ensures only railpack.json exists as build configuration.
        """
        competing_files = []
        root_files = {
            "Dockerfile": self.project_root / "Dockerfile",
            "railway.toml": self.project_root / "railway.toml", 
            "railway.json": self.project_root / "railway.json",
            "nixpacks.toml": self.project_root / "nixpacks.toml"
        }
        
        for name, path in root_files.items():
            # Skip Dockerfiles in services directory
            if name == "Dockerfile" and not path.exists():
                continue
            if path.exists() and not (name == "Dockerfile" and "services" in str(path)):
                competing_files.append(name)
        
        if competing_files:
            self.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="Build System Conflicts",
                description=f"Found competing build files: {', '.join(competing_files)}",
                fix_command=f"rm {' '.join(competing_files)}"
            ))
        
        # Validate railpack.json exists and is valid
        railpack_path = self.project_root / "railpack.json"
        if not railpack_path.exists():
            self.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="Build System Conflicts", 
                description="railpack.json not found",
                fix_command="Create railpack.json with proper Railway configuration"
            ))
        else:
            try:
                with open(railpack_path) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                self.issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category="Build System Conflicts",
                    description=f"railpack.json has invalid JSON: {e}",
                    file_path=str(railpack_path)
                ))

    def validate_port_binding(self) -> None:
        """
        Validate ISSUE 2: PORT Binding Failures
        Ensures proper use of process.env.PORT and 0.0.0.0 binding.
        """
        # Check for hardcoded ports in main application files
        main_files = [
            "run_server.py",
            "packages/core/monkey_coder/app/main.py"
        ]
        
        hardcoded_port_patterns = [
            r"app\.listen\(\d+\)",  # Express hardcoded ports
            r"host.*=.*['\"]127\.0\.0\.1['\"]",  # localhost binding
            r"host.*=.*['\"]localhost['\"]",     # localhost binding
        ]
        
        for file_path in main_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    content = full_path.read_text()
                    
                    # Check for proper PORT usage
                    if "process.env.PORT" not in content and "os.environ" in content and "PORT" not in content:
                        self.issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            category="PORT Binding",
                            description=f"File {file_path} should use environment PORT variable",
                            file_path=str(full_path)
                        ))
                    
                    # Check for proper host binding
                    if "127.0.0.1" in content or "localhost" in content:
                        # Filter out comments and example code
                        lines = content.split('\n')
                        problem_lines = [
                            i for i, line in enumerate(lines, 1)
                            if ("127.0.0.1" in line or "localhost" in line)
                            and not line.strip().startswith('#')
                            and "example" not in line.lower()
                        ]
                        
                        if problem_lines:
                            self.issues.append(ValidationIssue(
                                severity=ValidationSeverity.WARNING,
                                category="PORT Binding",
                                description=f"File {file_path} should bind to 0.0.0.0, not localhost/127.0.0.1",
                                file_path=str(full_path)
                            ))
                            
                except Exception as e:
                    self.logger.warning(f"Could not read {file_path}: {e}")

    def validate_health_check_config(self) -> None:
        """
        Validate ISSUE 5: Health Check Configuration
        Ensures health endpoint exists and is properly configured.
        """
        # Check railpack.json health check configuration
        railpack_path = self.project_root / "railpack.json"
        if railpack_path.exists():
            try:
                with open(railpack_path) as f:
                    config = json.load(f)
                
                health_path = config.get("deploy", {}).get("healthCheckPath")
                if not health_path:
                    self.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category="Health Check",
                        description="No healthCheckPath configured in railpack.json"
                    ))
                elif not health_path.startswith("/"):
                    self.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category="Health Check",
                        description="healthCheckPath should start with /"
                    ))
                    
            except Exception as e:
                self.logger.warning(f"Could not validate railpack.json health config: {e}")
        
        # Check if health endpoint is implemented
        main_py = self.project_root / "packages/core/monkey_coder/app/main.py"
        if main_py.exists():
            try:
                content = main_py.read_text()
                if "/health" not in content:
                    self.issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        category="Health Check",
                        description="Health endpoint not implemented in main.py",
                        file_path=str(main_py)
                    ))
            except Exception as e:
                self.logger.warning(f"Could not check health endpoint implementation: {e}")

    def validate_monorepo_structure(self) -> None:
        """
        Validate ISSUE 6: Monorepo Service Confusion
        Ensures proper monorepo configuration if applicable.
        """
        # Check if this is a monorepo with multiple services
        has_packages = (self.project_root / "packages").exists()
        has_services = (self.project_root / "services").exists()
        
        if has_packages or has_services:
            railpack_path = self.project_root / "railpack.json"
            if railpack_path.exists():
                try:
                    with open(railpack_path) as f:
                        config = json.load(f)
                    
                    # For monorepos, check if services are properly configured
                    if "services" not in config and has_services:
                        self.issues.append(ValidationIssue(
                            severity=ValidationSeverity.INFO,
                            category="Monorepo Structure",
                            description="Consider using services configuration for multiple services"
                        ))
                        
                except Exception as e:
                    self.logger.warning(f"Could not validate monorepo structure: {e}")

    def validate_reference_variables(self) -> None:
        """
        Validate ISSUE 4: Reference Variable Mistakes
        Check for proper Railway variable references.
        """
        # Look for common reference variable mistakes in config files
        config_files = [
            "railpack.json",
            ".env.example", 
            "railway_vars_cli.sh"
        ]
        
        for file_name in config_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                try:
                    content = file_path.read_text()
                    
                    # Check for invalid port references
                    if "{{" in content and ".PORT}}" in content:
                        self.issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            category="Reference Variables",
                            description=f"File {file_name} contains invalid PORT reference - use RAILWAY_PUBLIC_DOMAIN instead",
                            file_path=str(file_path)
                        ))
                        
                except Exception as e:
                    self.logger.warning(f"Could not check reference variables in {file_name}: {e}")

    def validate_railway_compliance(self) -> Dict[str, Any]:
        """
        Run comprehensive Railway deployment validation.
        Returns validation results with MCP orchestration if available.
        """
        self.logger.info("🔍 Starting comprehensive Railway deployment validation...")
        
        # Clear previous issues
        self.issues.clear()
        
        # Run all validation checks
        validation_checks = [
            ("Build System Conflicts", self.validate_build_system_conflicts),
            ("PORT Binding", self.validate_port_binding), 
            ("Health Check Configuration", self.validate_health_check_config),
            ("Monorepo Structure", self.validate_monorepo_structure),
            ("Reference Variables", self.validate_reference_variables)
        ]
        
        for check_name, check_func in validation_checks:
            try:
                self.logger.info(f"Running {check_name} validation...")
                check_func()
            except Exception as e:
                self.logger.error(f"Validation check {check_name} failed: {e}")
                self.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="Validation Error",
                    description=f"Could not complete {check_name} validation: {e}"
                ))
        
        # Use MCP orchestration for advanced analysis if available
        if self.mcp_enabled:
            try:
                mcp_analysis = self._run_mcp_analysis()
            except Exception as e:
                self.logger.warning(f"MCP analysis failed: {e}")
                mcp_analysis = {}
        else:
            mcp_analysis = {}
        
        # Compile results
        critical_issues = [i for i in self.issues if i.severity == ValidationSeverity.CRITICAL]
        warning_issues = [i for i in self.issues if i.severity == ValidationSeverity.WARNING]
        info_issues = [i for i in self.issues if i.severity == ValidationSeverity.INFO]
        
        results = {
            "railway_compliant": len(critical_issues) == 0,
            "total_issues": len(self.issues),
            "critical_issues": len(critical_issues),
            "warning_issues": len(warning_issues), 
            "info_issues": len(info_issues),
            "issues": [
                {
                    "severity": issue.severity.value,
                    "category": issue.category,
                    "description": issue.description,
                    "fix_command": issue.fix_command,
                    "file_path": issue.file_path
                }
                for issue in self.issues
            ],
            "mcp_analysis": mcp_analysis,
            "deployment_ready": len(critical_issues) == 0
        }
        
        return results

    def _run_mcp_analysis(self) -> Dict[str, Any]:
        """Run MCP-enhanced analysis using orchestration patterns."""
        if not self.mcp_enabled:
            return {}
        
        try:
            # Use MCP orchestration for advanced deployment readiness analysis
            analysis_context = {
                "project_root": str(self.project_root),
                "validation_issues": len(self.issues),
                "environment": "railway_deployment"
            }
            
            # This would integrate with the full MCP system for advanced analysis
            # For now, return a basic analysis structure
            return {
                "orchestration_available": True,
                "environment_config": self.env_config is not None,
                "coordinator_active": self.coordinator is not None,
                "analysis_timestamp": "2025-01-27T22:22:22Z",
                "recommendations": [
                    "Consider using MCP orchestration for deployment automation",
                    "Environment configuration is available for enhanced validation"
                ]
            }
            
        except Exception as e:
            self.logger.warning(f"MCP analysis error: {e}")
            return {"error": str(e)}

    def generate_fix_script(self) -> str:
        """Generate a shell script to automatically fix Railway deployment issues."""
        script_lines = [
            "#!/bin/bash",
            "# Auto-generated Railway Deployment Fix Script",
            "# Generated by MCP Railway Validator",
            "",
            "set -e",
            "echo '🔧 Applying Railway deployment fixes...'",
            ""
        ]
        
        for issue in self.issues:
            if issue.fix_command and issue.severity == ValidationSeverity.CRITICAL:
                script_lines.extend([
                    f"# Fix: {issue.description}",
                    issue.fix_command,
                    ""
                ])
        
        script_lines.extend([
            "echo '✅ Railway deployment fixes applied!'",
            "echo 'Run validation again to verify fixes.'"
        ])
        
        return "\n".join(script_lines)

    def print_validation_report(self, results: Dict[str, Any]) -> None:
        """Print a formatted validation report."""
        print("\n" + "="*60)
        print("🚀 MCP-Enhanced Railway Deployment Validation Report")
        print("="*60)
        
        if results["railway_compliant"]:
            print("✅ RAILWAY DEPLOYMENT READY")
        else:
            print("❌ DEPLOYMENT ISSUES DETECTED")
        
        print(f"\nIssue Summary:")
        print(f"  Critical: {results['critical_issues']}")
        print(f"  Warnings: {results['warning_issues']}")
        print(f"  Info: {results['info_issues']}")
        
        if results["issues"]:
            print(f"\nDetailed Issues:")
            for issue in results["issues"]:
                severity_icon = {
                    "critical": "❌",
                    "warning": "⚠️", 
                    "info": "ℹ️"
                }[issue["severity"]]
                
                print(f"\n{severity_icon} {issue['category']}: {issue['description']}")
                if issue["fix_command"]:
                    print(f"   Fix: {issue['fix_command']}")
                if issue["file_path"]:
                    print(f"   File: {issue['file_path']}")
        
        if results.get("mcp_analysis", {}).get("orchestration_available"):
            print(f"\n🔌 MCP Orchestration: Available")
            for rec in results["mcp_analysis"].get("recommendations", []):
                print(f"   • {rec}")
        
        print("\n" + "="*60)


def main():
    """Main entry point for MCP Railway validator."""
    logging.basicConfig(level=logging.INFO)
    
    # Find project root
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    
    # Initialize validator with MCP integration
    validator = RailwayValidationOrchestrator(project_root)
    
    # Run comprehensive validation
    results = validator.validate_railway_compliance()
    
    # Print report
    validator.print_validation_report(results)
    
    # Generate fix script for critical issues
    if results["critical_issues"] > 0:
        fix_script = validator.generate_fix_script()
        fix_script_path = project_root / "fix-railway-deployment.sh"
        fix_script_path.write_text(fix_script)
        fix_script_path.chmod(0o755)
        print(f"\n🔧 Generated fix script: {fix_script_path}")
        print("   Run it with: ./fix-railway-deployment.sh")
    
    # Exit with error code if critical issues found
    sys.exit(0 if results["deployment_ready"] else 1)


if __name__ == "__main__":
    main()