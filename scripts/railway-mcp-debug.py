#!/usr/bin/env python3
"""
Railway MCP Debug Tool - Comprehensive Railway deployment debugging using MCP framework

This tool provides Railway deployment debugging with MCP integration,
following all Railway best practices from the deployment documentation.

Usage:
    python scripts/railway-mcp-debug.py [--service SERVICE] [--fix] [--verbose]

Options:
    --service SERVICE    Debug specific service (monkey-coder, monkey-coder-backend, monkey-coder-ml)
    --fix               Attempt to automatically fix detected issues
    --verbose           Enable verbose output
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "core"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# Try to import MCP components
try:
    from monkey_coder.mcp.railway_deployment_tool import MCPRailwayTool
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: MCP framework not available: {e}")
    MCP_AVAILABLE = False

# Try to import deployment manager
try:
    from mcp_railway_deployment_manager import RailwayDeploymentManager
    DEPLOYMENT_MANAGER_AVAILABLE = True
except ImportError:
    DEPLOYMENT_MANAGER_AVAILABLE = False


class RailwayDebugger:
    """Comprehensive Railway deployment debugger."""
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.issues: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.successes: List[Dict[str, Any]] = []
        
        # Initialize MCP tool if available
        self.mcp_tool = None
        if MCP_AVAILABLE:
            try:
                self.mcp_tool = MCPRailwayTool(project_root)
                print("✅ MCP Railway tool initialized")
            except Exception as e:
                print(f"⚠️  MCP tool initialization failed: {e}")
        
        # Initialize deployment manager if available
        self.deployment_manager = None
        if DEPLOYMENT_MANAGER_AVAILABLE:
            try:
                self.deployment_manager = RailwayDeploymentManager(project_root, verbose)
                print("✅ Railway deployment manager initialized")
            except Exception as e:
                print(f"⚠️  Deployment manager initialization failed: {e}")
    
    def print_header(self):
        """Print debug tool header."""
        print("\n" + "="*75)
        print("║" + " "*73 + "║")
        print("║" + "     Railway Deployment MCP Debug Tool".center(73) + "║")
        print("║" + " "*73 + "║")
        print("║" + "  Comprehensive Railway debugging with MCP integration".center(73) + "║")
        print("║" + " "*73 + "║")
        print("="*75 + "\n")
    
    def validate_railpack_files(self) -> Dict[str, Any]:
        """Validate all railpack.json files."""
        print("\n📋 Validating Railpack Configuration Files")
        print("-" * 75)
        
        railpack_files = [
            ("railpack.json", "Frontend (monkey-coder)"),
            ("railpack-backend.json", "Backend (monkey-coder-backend)"),
            ("railpack-ml.json", "ML Service (monkey-coder-ml)")
        ]
        
        results = {}
        
        for filename, service_name in railpack_files:
            filepath = self.project_root / filename
            print(f"\n🔍 Checking {filename} ({service_name})...")
            
            if not filepath.exists():
                self.issues.append({
                    "type": "missing_file",
                    "file": filename,
                    "message": f"{filename} not found"
                })
                print(f"  ✗ File not found: {filepath}")
                continue
            
            try:
                with open(filepath, 'r') as f:
                    config = json.load(f)
                
                # Validate JSON structure
                print(f"  ✓ Valid JSON syntax")
                
                # Check critical fields
                provider = config.get("build", {}).get("provider", "unknown")
                start_cmd = config.get("deploy", {}).get("startCommand", "")
                health_path = config.get("deploy", {}).get("healthCheckPath", "")
                health_timeout = config.get("deploy", {}).get("healthCheckTimeout", 0)
                
                print(f"  Provider: {provider}")
                print(f"  Start Command: {start_cmd[:60]}...")
                print(f"  Health Check: {health_path} (timeout: {health_timeout}s)")
                
                # Validate PORT binding
                if "$PORT" in start_cmd:
                    print(f"  ✓ Uses $PORT variable")
                    self.successes.append({
                        "type": "port_binding",
                        "file": filename,
                        "message": "Uses $PORT variable"
                    })
                else:
                    print(f"  ✗ Missing $PORT variable - CRITICAL!")
                    self.issues.append({
                        "type": "port_binding",
                        "file": filename,
                        "severity": "critical",
                        "message": "Start command must use $PORT"
                    })
                
                # Validate host binding
                if "0.0.0.0" in start_cmd:
                    print(f"  ✓ Binds to 0.0.0.0")
                    self.successes.append({
                        "type": "host_binding",
                        "file": filename,
                        "message": "Binds to 0.0.0.0"
                    })
                else:
                    print(f"  ⚠ Not explicitly binding to 0.0.0.0")
                    self.warnings.append({
                        "type": "host_binding",
                        "file": filename,
                        "message": "Should explicitly bind to 0.0.0.0"
                    })
                
                # Validate health check
                if health_path:
                    print(f"  ✓ Health check configured")
                    self.successes.append({
                        "type": "health_check",
                        "file": filename,
                        "message": f"Health check at {health_path}"
                    })
                else:
                    print(f"  ✗ Health check missing - CRITICAL!")
                    self.issues.append({
                        "type": "health_check",
                        "file": filename,
                        "severity": "critical",
                        "message": "Health check endpoint required"
                    })
                
                results[filename] = {
                    "valid": True,
                    "provider": provider,
                    "start_command": start_cmd,
                    "health_path": health_path
                }
                
            except json.JSONDecodeError as e:
                print(f"  ✗ Invalid JSON: {e}")
                self.issues.append({
                    "type": "invalid_json",
                    "file": filename,
                    "severity": "critical",
                    "message": f"Invalid JSON: {e}"
                })
                results[filename] = {"valid": False, "error": str(e)}
            except Exception as e:
                print(f"  ✗ Error: {e}")
                self.issues.append({
                    "type": "validation_error",
                    "file": filename,
                    "message": str(e)
                })
                results[filename] = {"valid": False, "error": str(e)}
        
        return results
    
    def check_competing_files(self) -> List[str]:
        """Check for competing build configuration files."""
        print("\n🔧 Checking for Build System Conflicts")
        print("-" * 75)
        
        competing_files = ["Dockerfile", "railway.toml", "nixpacks.toml"]
        found_files = []
        
        for filename in competing_files:
            filepath = self.project_root / filename
            if filepath.exists():
                print(f"  ⚠ Found competing file: {filename}")
                found_files.append(filename)
                self.warnings.append({
                    "type": "competing_file",
                    "file": filename,
                    "message": f"May override railpack.json: {filename}"
                })
        
        if not found_files:
            print("  ✓ No competing build files detected")
            self.successes.append({
                "type": "build_config",
                "message": "Only railpack.json files exist"
            })
        
        return found_files
    
    def check_railway_best_practices(self) -> Dict[str, Any]:
        """Check Railway deployment best practices."""
        print("\n✅ Railway Best Practices Checklist")
        print("-" * 75)
        
        practices = {
            "1. Build System Conflicts": len(self.check_competing_files()) == 0,
            "2. PORT Binding": all(
                issue["type"] != "port_binding" 
                for issue in self.issues
            ),
            "3. Host Binding (0.0.0.0)": all(
                issue["type"] != "host_binding" 
                for issue in self.issues
            ),
            "4. Health Check Configuration": all(
                issue["type"] != "health_check" 
                for issue in self.issues
            ),
        }
        
        print("\nBest Practices Status:")
        for practice, passing in practices.items():
            status = "✓" if passing else "✗"
            print(f"  {status} {practice}")
        
        return practices
    
    def run_mcp_validation(self) -> Optional[Dict[str, Any]]:
        """Run MCP tool validation if available."""
        if not self.mcp_tool:
            print("\n⚠️  MCP tool not available for validation")
            return None
        
        print("\n🔌 Running MCP Railway Validation")
        print("-" * 75)
        
        try:
            results = self.mcp_tool.validate_railway_deployment(
                project_path=str(self.project_root),
                verbose=self.verbose
            )
            
            if results.get("error"):
                print(f"  ✗ MCP validation error: {results['error']}")
                return results
            
            print(f"  Status: {results.get('overall_status', 'unknown')}")
            print(f"  Critical Issues: {results.get('critical_checks', 0)}")
            print(f"  Warnings: {results.get('warning_checks', 0)}")
            
            return results
        except Exception as e:
            print(f"  ✗ MCP validation failed: {e}")
            return {"error": str(e)}
    
    def get_recommendations(self) -> List[str]:
        """Get deployment recommendations."""
        print("\n📊 Deployment Recommendations")
        print("-" * 75)
        
        recommendations = []
        
        # Based on detected issues
        if any(issue["type"] == "port_binding" for issue in self.issues):
            recommendations.append(
                "Fix PORT binding: Ensure all start commands use $PORT"
            )
        
        if any(issue["type"] == "health_check" for issue in self.issues):
            recommendations.append(
                "Configure health checks: Add healthCheckPath to railpack.json"
            )
        
        if any(warning["type"] == "competing_file" for warning in self.warnings):
            recommendations.append(
                "Remove competing build files: Rename or delete Dockerfile, railway.toml"
            )
        
        # Railway-specific recommendations
        recommendations.extend([
            "Set Root Directory to '/' in Railway Dashboard for ALL services",
            "Clear manual Build/Start commands in Railway Dashboard",
            "Configure environment variables for service references",
            "Use RAILWAY_PUBLIC_DOMAIN for external URLs",
            "Use RAILWAY_PRIVATE_DOMAIN for internal service communication"
        ])
        
        # Print recommendations
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        return recommendations
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate debug summary."""
        print("\n" + "="*75)
        print("📊 Debug Summary")
        print("="*75)
        
        critical_count = len([i for i in self.issues if i.get("severity") == "critical"])
        warnings_count = len(self.warnings)
        successes_count = len(self.successes)
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "critical_issues": critical_count,
            "warnings_count": warnings_count,
            "successes": successes_count,
            "issues": self.issues,
            "warnings": self.warnings
        }
        
        print(f"\nCritical Issues: {summary['critical_issues']}")
        print(f"Warnings: {summary['warnings_count']}")
        print(f"Successful Checks: {summary['successes']}")
        
        if summary['critical_issues'] > 0:
            print(f"\n❌ Deployment NOT ready - {summary['critical_issues']} critical issue(s)")
        elif summary['warnings_count'] > 0:
            print(f"\n⚠️  Deployment ready with {summary['warnings_count']} warning(s)")
        else:
            print("\n✅ Deployment configuration looks good!")
        
        print("\n" + "="*75)
        
        return summary
    
    def save_report(self, summary: Dict[str, Any], output_file: str = "railway-debug-report.json"):
        """Save debug report to file."""
        output_path = self.project_root / output_file
        
        report = {
            "summary": summary,
            "timestamp": datetime.now().isoformat(),
            "mcp_available": MCP_AVAILABLE,
            "deployment_manager_available": DEPLOYMENT_MANAGER_AVAILABLE
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Report saved to: {output_path}")
        return output_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Railway MCP Debug Tool - Comprehensive Railway deployment debugging"
    )
    parser.add_argument(
        "--service",
        help="Debug specific service (monkey-coder, monkey-coder-backend, monkey-coder-ml)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to automatically fix detected issues"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--output",
        default="railway-debug-report.json",
        help="Output file for debug report (default: railway-debug-report.json)"
    )
    
    args = parser.parse_args()
    
    # Create debugger instance
    debugger = RailwayDebugger(PROJECT_ROOT, verbose=args.verbose)
    
    # Print header
    debugger.print_header()
    
    # Run validation steps
    railpack_results = debugger.validate_railpack_files()
    competing_files = debugger.check_competing_files()
    best_practices = debugger.check_railway_best_practices()
    
    # Run MCP validation if available
    mcp_results = debugger.run_mcp_validation()
    
    # Get recommendations
    recommendations = debugger.get_recommendations()
    
    # Generate and save summary
    summary = debugger.generate_summary()
    debugger.save_report(summary, args.output)
    
    # Print next steps
    print("\n📚 Documentation:")
    print("  RAILWAY_DEPLOYMENT.md        - Authoritative deployment guide")
    print("  RAILWAY_CRISIS_RESOLUTION.md - Emergency fix instructions")
    print("  scripts/fix-railway-services.sh - Interactive fix script")
    print("  scripts/railway-debug.sh        - Shell script debug tool")
    
    print("\n🛠️  Useful Commands:")
    print("  railway link                              # Link to project")
    print("  railway service update --root-directory / # Fix root directory")
    print("  railway variables --service <name>        # Check variables")
    print("  railway logs --service <name>             # View logs")
    
    # Exit with error if critical issues found
    if summary['critical_issues'] > 0:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
