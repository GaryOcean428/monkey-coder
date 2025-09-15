#!/usr/bin/env python3
"""
Railway Environment Configuration Setup
Automates the setup of required environment variables for Railway deployment.
"""

import os
import sys
import logging
import json
import secrets
import string
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class EnvironmentVariable:
    """Represents a required environment variable with metadata."""
    name: str
    description: str
    required: bool = True
    default_value: Optional[str] = None
    secret: bool = False
    validation_pattern: Optional[str] = None
    category: str = "general"

class RailwayEnvironmentSetup:
    """Railway deployment environment configuration manager."""
    
    def __init__(self):
        self.required_variables = self._define_required_variables()
        self.validation_results = []
        
    def _define_required_variables(self) -> List[EnvironmentVariable]:
        """Define all required environment variables for production deployment."""
        return [
            # Core Application Settings
            EnvironmentVariable(
                name="NODE_ENV",
                description="Node.js environment",
                default_value="production",
                category="core"
            ),
            EnvironmentVariable(
                name="PYTHON_ENV", 
                description="Python environment",
                default_value="production",
                category="core"
            ),
            EnvironmentVariable(
                name="RAILWAY_ENVIRONMENT",
                description="Railway deployment environment",
                default_value="production",
                category="railway"
            ),
            
            # Authentication & Security
            EnvironmentVariable(
                name="JWT_SECRET_KEY",
                description="JWT signing secret key",
                secret=True,
                category="security"
            ),
            EnvironmentVariable(
                name="NEXTAUTH_SECRET",
                description="NextAuth.js encryption secret",
                secret=True,
                category="security"
            ),
            EnvironmentVariable(
                name="NEXTAUTH_URL",
                description="NextAuth.js application URL",
                default_value="https://coder.fastmonkey.au",
                category="frontend"
            ),
            
            # Frontend Configuration
            EnvironmentVariable(
                name="NEXT_PUBLIC_API_URL",
                description="Public API URL for frontend",
                default_value="https://coder.fastmonkey.au",
                category="frontend"
            ),
            EnvironmentVariable(
                name="NEXT_PUBLIC_APP_URL",
                description="Public application URL",
                default_value="https://coder.fastmonkey.au",
                category="frontend"
            ),
            EnvironmentVariable(
                name="NEXT_OUTPUT_EXPORT",
                description="Enable Next.js static export",
                default_value="true",
                category="frontend"
            ),
            EnvironmentVariable(
                name="NEXT_TELEMETRY_DISABLED",
                description="Disable Next.js telemetry",
                default_value="1",
                category="frontend"
            ),
            
            # AI Provider Keys (Optional but recommended)
            EnvironmentVariable(
                name="OPENAI_API_KEY",
                description="OpenAI API key for GPT models",
                required=False,
                secret=True,
                category="ai_providers"
            ),
            EnvironmentVariable(
                name="ANTHROPIC_API_KEY",
                description="Anthropic API key for Claude models",
                required=False,
                secret=True,
                category="ai_providers"
            ),
            EnvironmentVariable(
                name="GOOGLE_API_KEY",
                description="Google AI API key",
                required=False,
                secret=True,
                category="ai_providers"
            ),
            EnvironmentVariable(
                name="GROQ_API_KEY",
                description="Groq API key for fast inference",
                required=False,
                secret=True,
                category="ai_providers"
            ),
            
            # Database Configuration
            EnvironmentVariable(
                name="DATABASE_URL",
                description="PostgreSQL database URL",
                default_value="postgresql://railway.internal:5432/railway",
                secret=True,
                category="database"
            ),
            
            # Stripe Configuration (Optional)
            EnvironmentVariable(
                name="STRIPE_PUBLIC_KEY",
                description="Stripe publishable key",
                required=False,
                default_value="pk_test_placeholder",
                category="payments"
            ),
            EnvironmentVariable(
                name="STRIPE_SECRET_KEY",
                description="Stripe secret key",
                required=False,
                secret=True,
                default_value="sk_test_placeholder",
                category="payments"
            ),
            EnvironmentVariable(
                name="STRIPE_WEBHOOK_SECRET",
                description="Stripe webhook secret",
                required=False,
                secret=True,
                default_value="whsec_placeholder",
                category="payments"
            ),
            
            # Monitoring (Optional)
            EnvironmentVariable(
                name="SENTRY_DSN",
                description="Sentry error tracking DSN",
                required=False,
                secret=True,
                category="monitoring"
            ),
        ]
    
    def generate_secure_secret(self, length: int = 32) -> str:
        """Generate a cryptographically secure random string."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def validate_current_environment(self) -> Dict[str, Any]:
        """Validate the current environment variables."""
        results = {
            "configured": 0,
            "missing_required": [],
            "missing_optional": [],
            "using_defaults": [],
            "secrets_needed": [],
            "validation_errors": []
        }
        
        for var in self.required_variables:
            current_value = os.getenv(var.name)
            
            if current_value:
                results["configured"] += 1
                logger.info(f"✅ {var.name}: Configured")
            elif var.required:
                results["missing_required"].append(var.name)
                if var.secret:
                    results["secrets_needed"].append(var.name)
                logger.warning(f"❌ {var.name}: Missing (Required)")
            else:
                results["missing_optional"].append(var.name)
                if var.secret:
                    results["secrets_needed"].append(var.name)
                logger.info(f"⚠️  {var.name}: Missing (Optional)")
            
            # Check for default values
            if not current_value and var.default_value:
                results["using_defaults"].append({
                    "name": var.name,
                    "default": var.default_value
                })
                
        return results
    
    def generate_env_file(self, output_path: str = ".env.railway.complete") -> None:
        """Generate a complete .env file with all required variables."""
        env_content = []
        env_content.append("# Railway Deployment Environment Variables")
        env_content.append("# Generated by railway_environment_setup.py")
        env_content.append("# Copy these to Railway's Environment Variables tab\n")
        
        # Group by category
        categories = {}
        for var in self.required_variables:
            if var.category not in categories:
                categories[var.category] = []
            categories[var.category].append(var)
        
        for category, vars_in_category in categories.items():
            env_content.append(f"# {category.upper()} Configuration")
            
            for var in vars_in_category:
                current_value = os.getenv(var.name)
                
                if current_value:
                    # Use existing value (but mask secrets)
                    if var.secret and len(current_value) > 8:
                        display_value = current_value[:4] + "..." + current_value[-4:]
                        env_content.append(f"# {var.name}={display_value} # (configured)")
                    else:
                        env_content.append(f"{var.name}={current_value}")
                elif var.default_value:
                    env_content.append(f"{var.name}={var.default_value}")
                elif var.secret:
                    # Generate secure default for secrets
                    secret_value = self.generate_secure_secret()
                    env_content.append(f"{var.name}={secret_value}")
                else:
                    env_content.append(f"# {var.name}=  # {var.description}")
                
                if var.description:
                    env_content.append(f"# {var.description}")
                    
            env_content.append("")  # Blank line between categories
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write('\n'.join(env_content))
        
        logger.info(f"✅ Environment file generated: {output_path}")
        logger.info(f"   Copy the contents to Railway's Environment Variables tab")
    
    def generate_railway_setup_script(self, output_path: str = "railway_env_setup.sh") -> None:
        """Generate a shell script to set Railway environment variables."""
        script_content = [
            "#!/bin/bash",
            "# Railway Environment Variables Setup Script",
            "# Run this script with Railway CLI to configure all environment variables",
            "",
            "set -e",
            "",
            "echo '🚀 Setting up Railway environment variables...'",
            "echo 'Make sure you have Railway CLI installed and are logged in'",
            "echo 'Run: railway login'",
            "echo 'Run: railway link'",
            "echo ''",
            "",
            "# Check if Railway CLI is available",
            "if ! command -v railway &> /dev/null; then",
            "    echo '❌ Railway CLI not found. Install it first:'",
            "    echo '   npm install -g @railway/cli'",
            "    exit 1",
            "fi",
            "",
        ]
        
        # Add environment variable setup commands
        for var in self.required_variables:
            current_value = os.getenv(var.name)
            
            if current_value:
                if var.secret and len(current_value) > 8:
                    script_content.append(f"# {var.name} is already configured")
                else:
                    script_content.append(f'railway variables set {var.name}="{current_value}"')
            elif var.default_value:
                script_content.append(f'railway variables set {var.name}="{var.default_value}"')
            elif var.secret:
                secret_value = self.generate_secure_secret()
                script_content.append(f'railway variables set {var.name}="{secret_value}"')
            else:
                script_content.append(f'# railway variables set {var.name}="YOUR_VALUE_HERE"  # {var.description}')
        
        script_content.extend([
            "",
            "echo '✅ Environment variables setup completed!'",
            "echo 'Now redeploy your service:'",
            "echo '   railway redeploy'",
        ])
        
        # Write script
        with open(output_path, 'w') as f:
            f.write('\n'.join(script_content))
        
        # Make executable
        os.chmod(output_path, 0o755)
        
        logger.info(f"✅ Railway setup script generated: {output_path}")
        logger.info(f"   Run: ./{output_path}")
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate a comprehensive validation report."""
        validation = self.validate_current_environment()
        
        report = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "status": "ready" if not validation["missing_required"] else "needs_setup",
            "summary": {
                "total_variables": len(self.required_variables),
                "configured": validation["configured"],
                "missing_required": len(validation["missing_required"]),
                "missing_optional": len(validation["missing_optional"]),
                "secrets_needed": len(validation["secrets_needed"])
            },
            "missing_required": validation["missing_required"],
            "missing_optional": validation["missing_optional"],
            "secrets_needed": validation["secrets_needed"],
            "recommendations": []
        }
        
        # Add recommendations
        if validation["missing_required"]:
            report["recommendations"].append({
                "priority": "high",
                "action": "Set required environment variables",
                "variables": validation["missing_required"]
            })
        
        if validation["secrets_needed"]:
            report["recommendations"].append({
                "priority": "high", 
                "action": "Configure API keys and secrets",
                "variables": validation["secrets_needed"]
            })
        
        ai_vars = [os.getenv(v.name) for v in self.required_variables if v.category == "ai_providers"]
        if not any(var and var.startswith(("sk-", "anthropic-", "gsk_", "grok-")) for var in ai_vars):
            report["recommendations"].append({
                "priority": "medium",
                "action": "Configure at least one AI provider API key",
                "note": "App will work but AI features will be limited"
            })
        
        return report

def main():
    """Main execution function."""
    setup = RailwayEnvironmentSetup()
    
    print("🐒 Railway Environment Setup for Monkey Coder")
    print("=" * 50)
    
    # Validate current environment
    validation = setup.validate_current_environment()
    
    print(f"\n📊 Current Environment Status:")
    print(f"   Configured: {validation['configured']}")
    print(f"   Missing Required: {len(validation['missing_required'])}")
    print(f"   Missing Optional: {len(validation['missing_optional'])}")
    print(f"   Secrets Needed: {len(validation['secrets_needed'])}")
    
    # Generate files
    print(f"\n🔧 Generating setup files...")
    setup.generate_env_file()
    setup.generate_railway_setup_script()
    
    # Generate validation report
    report = setup.generate_validation_report()
    with open("railway_environment_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Setup files generated:")
    print(f"   📄 .env.railway.complete - Copy to Railway Environment Variables")
    print(f"   🚀 railway_env_setup.sh - Run with Railway CLI")
    print(f"   📊 railway_environment_report.json - Validation report")
    
    if validation['missing_required']:
        print(f"\n⚠️  Missing required variables:")
        for var in validation['missing_required']:
            print(f"   - {var}")
    
    print(f"\n🚀 Next steps:")
    print(f"   1. Copy .env.railway.complete contents to Railway Environment Variables tab")
    print(f"   2. Or run: ./railway_env_setup.sh (requires Railway CLI)")
    print(f"   3. Redeploy the service in Railway")
    print(f"   4. Verify deployment at https://coder.fastmonkey.au")

if __name__ == "__main__":
    main()