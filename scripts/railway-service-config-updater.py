#!/usr/bin/env python3
"""
Railway Service Configuration Updater

This script directly updates Railway service configurations using Railway CLI
with specific service IDs for the AetherOS monkey-coder project.

Usage:
    python scripts/railway-service-config-updater.py [--service SERVICE] [--dry-run]
    python scripts/railway-service-config-updater.py --generate-commands

Features:
- Direct service ID targeting for precise updates
- Comprehensive environment variable management
- MCP-compatible operations
- Dry-run mode for safe testing
- Command generation for manual execution
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
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
class ServiceConfig:
    """Railway service configuration with all required variables."""
    name: str
    service_id: str
    config_file: str
    root_directory: str = "/"
    required_variables: Dict[str, str] = field(default_factory=dict)
    optional_variables: Dict[str, str] = field(default_factory=dict)
    critical_secrets: List[str] = field(default_factory=list)
    
    
class RailwayServiceConfigUpdater:
    """Update Railway services using Railway CLI with service IDs."""
    
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
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
                print(f"✓ Railway CLI available: {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        print("✗ Railway CLI not available")
        print("  Install with: npm install -g @railway/cli")
        print("  Or use ephemeral: yarn dlx @railway/cli@latest")
        return False
    
    def _run_railway_command(
        self, 
        command: List[str], 
        service_id: Optional[str] = None,
        capture_output: bool = True
    ) -> Tuple[bool, str]:
        """
        Run a Railway CLI command securely.
        
        Args:
            command: Command arguments (without 'railway' prefix)
            service_id: Optional service ID to target
            capture_output: Whether to capture command output
            
        Returns:
            Tuple of (success: bool, output: str)
        """
        if self.dry_run:
            cmd_str = f"railway {' '.join(command)}"
            if service_id:
                cmd_str = f"railway --service {service_id} {' '.join(command)}"
            print(f"[DRY RUN] Would execute: {cmd_str}")
            return True, ""
        
        if not self.railway_available:
            print("✗ Cannot execute: Railway CLI not available")
            return False, ""
        
        try:
            # Validate command arguments
            if not all(isinstance(arg, str) for arg in command):
                print("✗ Invalid command arguments")
                return False, ""
            
            # Build full command
            full_command = ['railway']
            if service_id:
                full_command.extend(['--service', service_id])
            full_command.extend(command)
            
            if self.verbose:
                print(f"Executing: {' '.join(full_command)}")
            
            # Execute without shell for security
            result = subprocess.run(
                full_command,
                capture_output=capture_output,
                text=True,
                timeout=60,
                shell=False
            )
            
            if result.returncode == 0:
                if self.verbose:
                    print(f"✓ Success: {' '.join(command)}")
                    if result.stdout:
                        print(f"  Output: {result.stdout.strip()}")
                return True, result.stdout
            else:
                print(f"✗ Failed: {' '.join(command)}")
                if result.stderr:
                    print(f"  Error: {result.stderr.strip()}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            print(f"✗ Timeout: {' '.join(command)}")
            return False, "Command timed out"
        except Exception as e:
            print(f"✗ Error: {e}")
            return False, str(e)
    
    def get_service_configs(self) -> List[ServiceConfig]:
        """Get configuration for all monkey-coder services with comprehensive variables."""
        return [
            ServiceConfig(
                name="monkey-coder",
                service_id=SERVICE_IDS["monkey-coder"],
                config_file="railpack.json",
                root_directory="/",
                required_variables={
                    "RAILWAY_CONFIG_FILE": "railpack.json",
                    "NODE_ENV": "production",
                    "NEXT_OUTPUT_EXPORT": "true",
                    "NEXT_TELEMETRY_DISABLED": "1",
                    "NEXT_PUBLIC_APP_URL": "https://coder.fastmonkey.au",
                    "NEXT_PUBLIC_API_URL": "https://monkey-coder-backend-production.up.railway.app"
                },
                optional_variables={
                    "NEXT_PUBLIC_ENV": "production"
                }
            ),
            ServiceConfig(
                name="monkey-coder-backend",
                service_id=SERVICE_IDS["monkey-coder-backend"],
                config_file="railpack-backend.json",
                root_directory="/",
                required_variables={
                    "RAILWAY_CONFIG_FILE": "railpack-backend.json",
                    "ENV": "production",
                    "NODE_ENV": "production",
                    "PYTHON_ENV": "production",
                    "LOG_LEVEL": "info",
                    "NEXT_PUBLIC_APP_URL": "https://coder.fastmonkey.au",
                    "PUBLIC_APP_URL": "https://coder.fastmonkey.au",
                    "NEXT_PUBLIC_API_URL": "https://monkey-coder-backend-production.up.railway.app",
                    "CORS_ORIGINS": "https://coder.fastmonkey.au",
                    "TRUSTED_HOSTS": "coder.fastmonkey.au,*.railway.app,*.railway.internal",
                    "ENABLE_SECURITY_HEADERS": "true",
                    "ENABLE_CORS": "true",
                    "HEALTH_CHECK_PATH": "/api/health",
                    "ENABLE_HEALTH_CHECKS": "true"
                },
                critical_secrets=[
                    "JWT_SECRET_KEY",
                    "NEXTAUTH_SECRET",
                    "OPENAI_API_KEY",
                    "ANTHROPIC_API_KEY"
                ],
                optional_variables={
                    "GOOGLE_API_KEY": "",
                    "GROQ_API_KEY": "",
                    "XAI_API_KEY": "",
                    "RESEND_API_KEY": "",
                    "NOTIFICATION_EMAIL_FROM": "noreply@fastmonkey.au",
                    "EMAIL_PROVIDER": "resend",
                    "SENTRY_DSN": "",
                    "SESSION_BACKEND": "redis",
                    "RATE_LIMIT_BACKEND": "redis"
                }
            ),
            ServiceConfig(
                name="monkey-coder-ml",
                service_id=SERVICE_IDS["monkey-coder-ml"],
                config_file="railpack-ml.json",
                root_directory="/",
                required_variables={
                    "RAILWAY_CONFIG_FILE": "railpack-ml.json",
                    "ENV": "production",
                    "NODE_ENV": "production",
                    "PYTHON_ENV": "production",
                    "LOG_LEVEL": "info",
                    "TRANSFORMERS_CACHE": "/app/.cache/huggingface",
                    "HEALTH_CHECK_PATH": "/api/health"
                },
                optional_variables={
                    "CUDA_VISIBLE_DEVICES": "0"
                }
            )
        ]
    
    def set_environment_variable(
        self, 
        service_id: str, 
        key: str, 
        value: str
    ) -> bool:
        """Set a single environment variable for a service."""
        # Validate inputs
        if not key or not isinstance(key, str):
            print(f"✗ Invalid variable key: {key}")
            return False
        
        # Escape value properly
        escaped_value = value.replace("'", "'\"'\"'")
        
        success, _ = self._run_railway_command(
            ['variables', 'set', f'{key}={value}'],
            service_id=service_id
        )
        
        if success:
            # Mask sensitive values in output
            display_value = value
            if any(secret in key.lower() for secret in ['key', 'secret', 'password', 'token']):
                display_value = '***MASKED***'
            print(f"  ✓ Set {key}={display_value}")
        
        return success
    
    def update_service(self, config: ServiceConfig, skip_secrets: bool = False) -> Dict[str, any]:
        """
        Update a single Railway service configuration.
        
        Returns:
            Dict with update results
        """
        print(f"\n{'='*70}")
        print(f"🔧 Updating Service: {config.name}")
        print(f"{'='*70}")
        print(f"Service ID: {config.service_id}")
        print(f"Config File: {config.config_file}")
        print(f"Root Directory: {config.root_directory}")
        print()
        
        results = {
            "service": config.name,
            "service_id": config.service_id,
            "success": True,
            "variables_set": 0,
            "variables_failed": 0,
            "missing_secrets": []
        }
        
        # Set required environment variables
        if config.required_variables:
            print(f"📋 Setting {len(config.required_variables)} required variables...")
            for key, value in config.required_variables.items():
                if self.set_environment_variable(config.service_id, key, value):
                    results["variables_set"] += 1
                else:
                    results["variables_failed"] += 1
                    results["success"] = False
        
        # Check for critical secrets (don't set, just warn if missing)
        if config.critical_secrets and not skip_secrets:
            print(f"\n⚠️  Critical secrets required (set manually):")
            for secret in config.critical_secrets:
                print(f"  • {secret}")
                results["missing_secrets"].append(secret)
        
        # Set optional variables (only if value is provided)
        if config.optional_variables:
            print(f"\n📋 Optional variables (set if needed):")
            for key, value in config.optional_variables.items():
                if value:  # Only set if value is not empty
                    if self.set_environment_variable(config.service_id, key, value):
                        results["variables_set"] += 1
                    else:
                        results["variables_failed"] += 1
                else:
                    print(f"  ○ {key} (not set)")
        
        print(f"\n✓ Service {config.name} configuration updated")
        print(f"  Variables set: {results['variables_set']}")
        if results["variables_failed"] > 0:
            print(f"  Variables failed: {results['variables_failed']}")
        if results["missing_secrets"]:
            print(f"  Critical secrets to set manually: {len(results['missing_secrets'])}")
        
        return results
    
    def update_all_services(self, skip_secrets: bool = False) -> Dict[str, any]:
        """Update all monkey-coder services."""
        print("\n" + "="*70)
        print("🚂 Railway Service Configuration Updater")
        print("="*70)
        print(f"Project: AetherOS Monkey Coder")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - No actual changes will be made\n")
        
        configs = self.get_service_configs()
        all_results = []
        
        for config in configs:
            result = self.update_service(config, skip_secrets=skip_secrets)
            all_results.append(result)
        
        # Print summary
        print("\n" + "="*70)
        print("📊 Update Summary")
        print("="*70)
        
        total_vars_set = sum(r["variables_set"] for r in all_results)
        total_vars_failed = sum(r["variables_failed"] for r in all_results)
        total_secrets = sum(len(r["missing_secrets"]) for r in all_results)
        
        for result in all_results:
            status = "✓" if result["success"] else "✗"
            print(f"\n{status} {result['service']}")
            print(f"   Service ID: {result['service_id']}")
            print(f"   Variables set: {result['variables_set']}")
            if result["variables_failed"] > 0:
                print(f"   Variables failed: {result['variables_failed']}")
            if result["missing_secrets"]:
                print(f"   Secrets to set: {', '.join(result['missing_secrets'])}")
        
        print(f"\n{'='*70}")
        print(f"Total variables set: {total_vars_set}")
        print(f"Total variables failed: {total_vars_failed}")
        print(f"Total secrets to set manually: {total_secrets}")
        
        if self.dry_run:
            print("\n⚠️  This was a DRY RUN - No actual changes were made")
            print("    Remove --dry-run to apply changes")
        
        if total_secrets > 0:
            print(f"\n⚠️  IMPORTANT: Set critical secrets manually:")
            print(f"    Use: railway variables set --service <SERVICE_ID> KEY=VALUE")
            print(f"    Or set in Railway Dashboard → Service → Variables")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_services": len(all_results),
            "total_variables_set": total_vars_set,
            "total_variables_failed": total_vars_failed,
            "total_secrets_needed": total_secrets,
            "results": all_results
        }
    
    def generate_commands_script(self, output_file: str = "railway-update-commands.sh") -> Path:
        """Generate shell script with all commands for manual execution."""
        output_path = self.project_root / output_file
        
        configs = self.get_service_configs()
        
        script_content = '''#!/bin/bash
#
# Railway Service Configuration Commands
# Generated: ''' + datetime.now().isoformat() + '''
#
# This script contains all commands to update Railway services
# for the AetherOS Monkey Coder project.
#
# Usage: 
#   1. Review the commands below
#   2. Execute manually or run: bash ''' + output_file + '''
#   3. Set critical secrets separately (marked with TODO)
#

set -e

echo "======================================"
echo "Railway Service Configuration Update"
echo "======================================"
echo ""

# Check Railway CLI
if ! command -v railway &> /dev/null; then
    echo "✗ Railway CLI not found!"
    echo "  Install with: npm install -g @railway/cli"
    echo "  Or use: yarn dlx @railway/cli@latest"
    exit 1
fi

echo "✓ Railway CLI available"
echo ""

'''
        
        for config in configs:
            script_content += f'''
# ============================================================================
# Service: {config.name}
# Service ID: {config.service_id}
# Config File: {config.config_file}
# ============================================================================

echo "🔧 Updating {config.name}..."
echo "  Service ID: {config.service_id}"

# Required Variables
'''
            for key, value in config.required_variables.items():
                escaped_value = value.replace('"', '\\"')
                script_content += f'railway variables set --service {config.service_id} "{key}={escaped_value}"\n'
            
            if config.critical_secrets:
                script_content += f'\n# Critical Secrets (SET THESE MANUALLY)\n'
                for secret in config.critical_secrets:
                    script_content += f'# TODO: railway variables set --service {config.service_id} "{secret}=YOUR_VALUE_HERE"\n'
            
            if config.optional_variables:
                script_content += f'\n# Optional Variables (uncomment if needed)\n'
                for key, value in config.optional_variables.items():
                    if value:
                        escaped_value = value.replace('"', '\\"')
                        script_content += f'# railway variables set --service {config.service_id} "{key}={escaped_value}"\n'
                    else:
                        script_content += f'# railway variables set --service {config.service_id} "{key}=YOUR_VALUE_HERE"\n'
            
            script_content += f'\necho "✓ {config.name} variables set"\necho ""\n'
        
        script_content += '''
echo "======================================"
echo "Configuration Update Complete"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Set critical secrets in Railway Dashboard"
echo "2. Verify: railway variables --service <SERVICE_ID>"
echo "3. Redeploy: railway up --service <SERVICE_ID>"
echo ""
'''
        
        with open(output_path, 'w') as f:
            f.write(script_content)
        
        output_path.chmod(0o755)
        
        print(f"\n✓ Generated commands script: {output_path}")
        print(f"  Execute with: bash {output_path}")
        
        return output_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Railway Service Configuration Updater for AetherOS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (safe preview)
  python scripts/railway-service-config-updater.py --dry-run
  
  # Update all services
  python scripts/railway-service-config-updater.py
  
  # Update specific service
  python scripts/railway-service-config-updater.py --service monkey-coder
  
  # Generate shell script for manual execution
  python scripts/railway-service-config-updater.py --generate-commands
  
  # Skip secret warnings
  python scripts/railway-service-config-updater.py --skip-secrets
        """
    )
    parser.add_argument(
        "--service",
        choices=["monkey-coder", "monkey-coder-backend", "monkey-coder-ml"],
        help="Update specific service only"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--generate-commands",
        action="store_true",
        help="Generate shell script with all commands"
    )
    parser.add_argument(
        "--skip-secrets",
        action="store_true",
        help="Skip critical secret warnings"
    )
    
    args = parser.parse_args()
    
    # Create updater
    updater = RailwayServiceConfigUpdater(dry_run=args.dry_run, verbose=args.verbose)
    
    # Generate commands script if requested
    if args.generate_commands:
        updater.generate_commands_script()
        return 0
    
    # Update services
    if args.service:
        # Update specific service
        configs = [c for c in updater.get_service_configs() if c.name == args.service]
        if not configs:
            print(f"✗ Service not found: {args.service}")
            return 1
        
        result = updater.update_service(configs[0], skip_secrets=args.skip_secrets)
        return 0 if result["success"] else 1
    else:
        # Update all services
        summary = updater.update_all_services(skip_secrets=args.skip_secrets)
        
        # Save summary to JSON
        summary_file = PROJECT_ROOT / "railway_update_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\n📋 Summary saved to: {summary_file}")
        
        # Exit with error if any updates failed
        if summary["total_variables_failed"] > 0:
            return 1
        
        return 0


if __name__ == "__main__":
    sys.exit(main())
