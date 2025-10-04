#!/usr/bin/env python3
"""
Railway Service Updater

This script uses the Railway MCP to directly update Railway services
prefixed with 'monkey-coder'. It provides automated service configuration
updates following best practices.

Usage:
    python scripts/railway-service-updater.py [--service SERVICE] [--dry-run]
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "core"))


@dataclass
class ServiceConfig:
    """Railway service configuration."""
    name: str
    root_directory: str = "/"
    build_command: Optional[str] = None
    start_command: Optional[str] = None
    config_path: Optional[str] = None
    environment_variables: Dict[str, str] = None
    
    def __post_init__(self):
        if self.environment_variables is None:
            self.environment_variables = {}


class RailwayServiceUpdater:
    """Update Railway services using Railway CLI and MCP."""
    
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.project_root = PROJECT_ROOT
        self.railway_available = self._check_railway_cli()
        
    def _check_railway_cli(self) -> bool:
        """Check if Railway CLI is available."""
        try:
            result = subprocess.run(
                ['railway', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"✓ Railway CLI available: {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        print("⚠ Railway CLI not available")
        print("  Install with: npm install -g @railway/cli")
        return False
    
    def _run_railway_command(self, command: List[str], service: Optional[str] = None) -> bool:
        """Run a Railway CLI command."""
        if self.dry_run:
            print(f"[DRY RUN] Would execute: railway {' '.join(command)}")
            if service:
                print(f"           for service: {service}")
            return True
        
        if not self.railway_available:
            print(f"✗ Cannot execute: Railway CLI not available")
            return False
        
        try:
            # Validate command to prevent injection
            if not all(isinstance(arg, str) for arg in command):
                print("✗ Invalid command arguments")
                return False
            
            # Build command without shell for security
            if service:
                # Execute two separate commands sequentially
                # First select the service
                service_cmd = ['railway', 'service', service]
                service_result = subprocess.run(
                    service_cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    shell=False
                )
                if service_result.returncode != 0:
                    print(f"✗ Failed to select service: {service}")
                    if service_result.stderr:
                        print(f"  Error: {service_result.stderr}")
                    return False
            
            # Execute the main command
            full_command = ['railway'] + command
            
            if self.verbose:
                print(f"Executing: {' '.join(full_command)}")
            
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=30,
                shell=False
            )
            
            if result.returncode == 0:
                print(f"✓ Success: {' '.join(command)}")
                if self.verbose and result.stdout:
                    print(f"  Output: {result.stdout}")
                return True
            else:
                print(f"✗ Failed: {' '.join(command)}")
                if result.stderr:
                    print(f"  Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"✗ Timeout: {' '.join(command)}")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def get_service_configs(self) -> List[ServiceConfig]:
        """Get configuration for all monkey-coder services."""
        return [
            ServiceConfig(
                name="monkey-coder",
                root_directory="/",
                build_command="",  # Let railpack.json handle
                start_command="",  # Let railpack.json handle
                config_path="railpack.json",
                environment_variables={
                    "NODE_ENV": "production",
                    "NEXT_OUTPUT_EXPORT": "true",
                    "NEXT_TELEMETRY_DISABLED": "1",
                    "NEXT_PUBLIC_APP_URL": "https://coder.fastmonkey.au",
                    "NEXT_PUBLIC_API_URL": "https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}"
                }
            ),
            ServiceConfig(
                name="monkey-coder-backend",
                root_directory="/",
                build_command="",  # Let railpack.json handle
                start_command="",  # Let railpack.json handle
                config_path="railpack-backend.json",
                environment_variables={
                    "PYTHON_ENV": "production",
                    "PYTHONPATH": "/app:/app/packages/core",
                    "ML_SERVICE_URL": "http://${{monkey-coder-ml.RAILWAY_PRIVATE_DOMAIN}}"
                }
            ),
            ServiceConfig(
                name="monkey-coder-ml",
                root_directory="/",
                build_command="",  # Let railpack.json handle
                start_command="",  # Let railpack.json handle
                config_path="railpack-ml.json",
                environment_variables={
                    "PYTHON_ENV": "production",
                    "PYTHONPATH": "/app:/app/services/ml",
                    "TRANSFORMERS_CACHE": "/app/.cache/huggingface",
                    "CUDA_VISIBLE_DEVICES": "0"
                }
            )
        ]
    
    def update_service(self, config: ServiceConfig) -> bool:
        """Update a single Railway service."""
        print(f"\n🔧 Updating service: {config.name}")
        print("-" * 60)
        
        success = True
        
        # Update root directory
        if config.root_directory:
            print(f"Setting root directory to: {config.root_directory}")
            cmd = ['service', 'update', '--root-directory', config.root_directory]
            if not self._run_railway_command(cmd, config.name):
                success = False
        
        # Clear build command (let railpack.json handle)
        if config.build_command == "":
            print("Clearing build command (using railpack.json)")
            if not self.dry_run:
                print("  Note: Clear build command manually in Railway Dashboard")
        
        # Clear start command (let railpack.json handle)
        if config.start_command == "":
            print("Clearing start command (using railpack.json)")
            if not self.dry_run:
                print("  Note: Clear start command manually in Railway Dashboard")
        
        # Set environment variables
        if config.environment_variables:
            print(f"Setting {len(config.environment_variables)} environment variables")
            for key, value in config.environment_variables.items():
                cmd = ['variables', 'set', f'{key}={value}']
                if not self._run_railway_command(cmd, config.name):
                    success = False
        
        return success
    
    def update_all_services(self) -> Dict[str, bool]:
        """Update all monkey-coder services."""
        print("\n" + "="*60)
        print("Railway Service Updater")
        print("="*60)
        
        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - No actual changes will be made\n")
        
        configs = self.get_service_configs()
        results = {}
        
        for config in configs:
            results[config.name] = self.update_service(config)
        
        # Print summary
        print("\n" + "="*60)
        print("Update Summary")
        print("="*60)
        
        for service, success in results.items():
            status = "✓" if success else "✗"
            print(f"{status} {service}")
        
        if self.dry_run:
            print("\n⚠️  This was a DRY RUN - No actual changes were made")
            print("    Remove --dry-run to apply changes")
        
        return results
    
    def generate_update_script(self, output_file: str = "railway-update-services.sh") -> Path:
        """Generate a shell script for manual service updates."""
        output_path = self.project_root / output_file
        
        configs = self.get_service_configs()
        
        script_content = '''#!/bin/bash
#
# Railway Service Update Script
# Generated automatically - updates all monkey-coder services
#
# Usage: bash railway-update-services.sh
#

set -e

echo "======================================"
echo "Railway Service Updater"
echo "======================================"
echo ""

# Check Railway CLI
if ! command -v railway &> /dev/null; then
    echo "✗ Railway CLI not found!"
    echo "  Install with: npm install -g @railway/cli"
    exit 1
fi

echo "✓ Railway CLI available"
echo ""

'''
        
        for config in configs:
            script_content += f'''
# Update {config.name}
echo "🔧 Updating {config.name}..."
railway service {config.name}

# Set root directory
railway service update --root-directory {config.root_directory}

# Set environment variables
'''
            for key, value in config.environment_variables.items():
                # Escape single quotes in values
                escaped_value = value.replace("'", "'\\''")
                script_content += f"railway variables set '{key}={escaped_value}'\n"
            
            script_content += f'''
echo "✓ {config.name} updated"
echo ""

'''
        
        script_content += '''
echo "======================================"
echo "Update Complete"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. In Railway Dashboard, clear Build/Start commands for each service"
echo "2. Set Config Path to appropriate railpack file"
echo "3. Trigger redeploy: railway up --service <name>"
echo ""
'''
        
        with open(output_path, 'w') as f:
            f.write(script_content)
        
        # Make executable
        output_path.chmod(0o755)
        
        print(f"\n📝 Generated update script: {output_path}")
        return output_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Railway Service Updater - Update monkey-coder services"
    )
    parser.add_argument(
        "--service",
        help="Update specific service only (e.g., monkey-coder, monkey-coder-backend)"
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
        "--generate-script",
        action="store_true",
        help="Generate shell script for manual updates"
    )
    
    args = parser.parse_args()
    
    # Create updater
    updater = RailwayServiceUpdater(dry_run=args.dry_run, verbose=args.verbose)
    
    # Generate script if requested
    if args.generate_script:
        updater.generate_update_script()
        return
    
    # Update services
    if args.service:
        # Update specific service
        configs = [c for c in updater.get_service_configs() if c.name == args.service]
        if not configs:
            print(f"✗ Service not found: {args.service}")
            print(f"  Available services: {', '.join(c.name for c in updater.get_service_configs())}")
            sys.exit(1)
        
        updater.update_service(configs[0])
    else:
        # Update all services
        results = updater.update_all_services()
        
        # Exit with error if any updates failed
        if not all(results.values()):
            sys.exit(1)


if __name__ == "__main__":
    main()
