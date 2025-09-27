#!/usr/bin/env python3
"""
Railway MCP Services Manager

This tool uses Railway MCP integration to set up all required services
for the Monkey Coder platform, including:
- PostgreSQL Database
- Redis Cache/Message Broker
- Environment variable configuration
- Service cross-referencing and connectivity

Based on the Railway Deployment Master Cheat Sheet requirements.
"""

import os
import sys
import json
import subprocess
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ServiceConfig:
    """Railway service configuration."""
    name: str
    type: str  # postgres, redis, web
    variables: Dict[str, str]
    required: bool = True

@dataclass
class DeploymentResult:
    """Result of Railway deployment operations."""
    success: bool
    service_name: str
    message: str
    variables: Dict[str, str] = None

class RailwayServicesManager:
    """
    Railway MCP Services Manager
    
    Manages Railway services and environment variables with cross-referencing
    following Railway deployment best practices.
    """
    
    def __init__(self):
        self.project_name = "monkey-coder"
        self.services_config = self._load_services_config()
        self.deployment_results: List[DeploymentResult] = []
        
    def _load_services_config(self) -> List[ServiceConfig]:
        """Load required services configuration for Monkey Coder."""
        return [
            ServiceConfig(
                name="monkey-coder-api",
                type="web",
                variables={
                    "PYTHON_VERSION": "3.12.11",
                    "NODE_ENV": "production",
                    "PYTHON_ENV": "production",
                    "LOG_LEVEL": "info",
                    "HEALTH_CHECK_PATH": "/health",
                    "HEALTH_CHECK_TIMEOUT": "300",
                    "CORS_ORIGINS": "https://${{RAILWAY_PUBLIC_DOMAIN}}",
                    "NEXTAUTH_URL": "https://${{RAILWAY_PUBLIC_DOMAIN}}",
                    "NEXT_PUBLIC_API_URL": "https://${{RAILWAY_PUBLIC_DOMAIN}}",
                    "NEXT_PUBLIC_APP_URL": "https://${{RAILWAY_PUBLIC_DOMAIN}}",
                },
                required=True
            ),
            ServiceConfig(
                name="monkey-coder-postgres",
                type="postgres",
                variables={
                    "POSTGRES_DB": "monkey_coder",
                    "POSTGRES_USER": "monkey_coder",
                    "POSTGRES_PASSWORD": "${{POSTGRES_PASSWORD}}"
                },
                required=True
            ),
            ServiceConfig(
                name="monkey-coder-redis",
                type="redis",
                variables={
                    "REDIS_URL": "redis://:${{REDIS_PASSWORD}}@${{RAILWAY_PRIVATE_DOMAIN}}:6379"
                },
                required=True
            )
        ]
    
    def check_railway_cli(self) -> bool:
        """Check if Railway CLI is available and authenticated."""
        try:
            result = subprocess.run(['railway', 'whoami'], 
                                  capture_output=True, text=True, check=True)
            logger.info(f"✅ Railway CLI authenticated as: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError:
            logger.error("❌ Railway CLI not authenticated. Run 'railway login'")
            return False
        except FileNotFoundError:
            logger.error("❌ Railway CLI not found. Install from https://railway.app/cli")
            return False
    
    def check_existing_services(self) -> Dict[str, Any]:
        """Check what services already exist in the Railway project."""
        try:
            result = subprocess.run(['railway', 'status', '--json'], 
                                  capture_output=True, text=True, check=True)
            services_data = json.loads(result.stdout)
            logger.info("📋 Current Railway services:")
            
            existing_services = {}
            if 'services' in services_data:
                for service in services_data['services']:
                    service_name = service.get('name', 'Unknown')
                    service_type = service.get('type', 'Unknown')
                    existing_services[service_name] = service
                    logger.info(f"  • {service_name} ({service_type})")
            
            return existing_services
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            logger.warning(f"⚠️  Could not fetch existing services: {e}")
            return {}
    
    def create_postgres_service(self) -> DeploymentResult:
        """Create PostgreSQL database service."""
        logger.info("🐘 Setting up PostgreSQL database...")
        
        try:
            # Create PostgreSQL service
            result = subprocess.run([
                'railway', 'add', '--name', 'monkey-coder-postgres', 'postgres'
            ], capture_output=True, text=True, check=True)
            
            logger.info("✅ PostgreSQL service created")
            
            # Get database connection details
            db_result = subprocess.run([
                'railway', 'variables', '--service', 'monkey-coder-postgres', '--json'
            ], capture_output=True, text=True, check=True)
            
            db_vars = json.loads(db_result.stdout)
            database_url = db_vars.get('DATABASE_URL', '')
            
            return DeploymentResult(
                success=True,
                service_name="monkey-coder-postgres",
                message="PostgreSQL service created successfully",
                variables={"DATABASE_URL": database_url}
            )
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to create PostgreSQL service: {e.stderr}")
            return DeploymentResult(
                success=False,
                service_name="monkey-coder-postgres",
                message=f"Failed to create PostgreSQL service: {e.stderr}"
            )
    
    def create_redis_service(self) -> DeploymentResult:
        """Create Redis cache/message broker service."""
        logger.info("🗄️  Setting up Redis cache...")
        
        try:
            # Create Redis service
            result = subprocess.run([
                'railway', 'add', '--name', 'monkey-coder-redis', 'redis'
            ], capture_output=True, text=True, check=True)
            
            logger.info("✅ Redis service created")
            
            # Get Redis connection details
            redis_result = subprocess.run([
                'railway', 'variables', '--service', 'monkey-coder-redis', '--json'
            ], capture_output=True, text=True, check=True)
            
            redis_vars = json.loads(redis_result.stdout)
            redis_url = redis_vars.get('REDIS_URL', '')
            
            return DeploymentResult(
                success=True,
                service_name="monkey-coder-redis",
                message="Redis service created successfully",
                variables={"REDIS_URL": redis_url}
            )
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to create Redis service: {e.stderr}")
            return DeploymentResult(
                success=False,
                service_name="monkey-coder-redis",
                message=f"Failed to create Redis service: {e.stderr}"
            )
    
    def configure_main_service_variables(self, db_url: str, redis_url: str) -> DeploymentResult:
        """Configure environment variables for the main API service."""
        logger.info("⚙️  Configuring main service environment variables...")
        
        try:
            # Environment variables with Railway references
            variables = {
                "DATABASE_URL": db_url,
                "REDIS_URL": redis_url,
                "CORS_ORIGINS": "https://${{RAILWAY_PUBLIC_DOMAIN}}",
                "NEXTAUTH_URL": "https://${{RAILWAY_PUBLIC_DOMAIN}}",
                "NEXT_PUBLIC_API_URL": "https://${{RAILWAY_PUBLIC_DOMAIN}}",
                "NEXT_PUBLIC_APP_URL": "https://${{RAILWAY_PUBLIC_DOMAIN}}",
                "RAILWAY_STATIC_URL": "${{RAILWAY_PUBLIC_DOMAIN}}",
                "HEALTH_CHECK_PATH": "/health",
                "HEALTH_CHECK_TIMEOUT": "300",
                "NODE_ENV": "production",
                "PYTHON_ENV": "production",
                "LOG_LEVEL": "info"
            }
            
            # Set each variable
            for key, value in variables.items():
                subprocess.run([
                    'railway', 'variables', 'set', f'{key}={value}'
                ], check=True)
                logger.info(f"  ✅ Set {key}")
            
            return DeploymentResult(
                success=True,
                service_name="monkey-coder-api",
                message="Environment variables configured successfully",
                variables=variables
            )
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to configure environment variables: {e.stderr}")
            return DeploymentResult(
                success=False,
                service_name="monkey-coder-api",
                message=f"Failed to configure environment variables: {e.stderr}"
            )
    
    def create_railway_variables_script(self) -> None:
        """Create a script to easily manage Railway variables locally."""
        script_content = '''#!/bin/bash

# Railway Variables Management Script
# Generated by Railway MCP Services Manager

echo "🚂 Railway Variables Manager"
echo "=========================="

case "$1" in
  "list")
    echo "📋 Listing all variables:"
    railway variables
    ;;
  "set-api-keys")
    echo "🔑 Setting up API keys..."
    echo "Enter your API keys (press Enter to skip):"
    
    read -p "OpenAI API Key: " OPENAI_KEY
    if [ ! -z "$OPENAI_KEY" ]; then
      railway variables set "OPENAI_API_KEY=$OPENAI_KEY"
    fi
    
    read -p "Anthropic API Key: " ANTHROPIC_KEY
    if [ ! -z "$ANTHROPIC_KEY" ]; then
      railway variables set "ANTHROPIC_API_KEY=$ANTHROPIC_KEY"
    fi
    
    read -p "Google API Key: " GOOGLE_KEY
    if [ ! -z "$GOOGLE_KEY" ]; then
      railway variables set "GOOGLE_API_KEY=$GOOGLE_KEY"
    fi
    
    read -p "Groq API Key: " GROQ_KEY
    if [ ! -z "$GROQ_KEY" ]; then
      railway variables set "GROQ_API_KEY=$GROQ_KEY"
    fi
    ;;
  "set-secrets")
    echo "🔐 Setting up security secrets..."
    JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(64))")
    NEXTAUTH_SECRET=$(openssl rand -base64 32)
    
    railway variables set "JWT_SECRET_KEY=$JWT_SECRET"
    railway variables set "NEXTAUTH_SECRET=$NEXTAUTH_SECRET"
    echo "✅ Security secrets generated and set"
    ;;
  "validate")
    echo "✅ Validating deployment configuration..."
    railway run python scripts/validate-deployment-model.sh
    ;;
  "deploy")
    echo "🚀 Deploying to Railway..."
    railway deploy
    ;;
  *)
    echo "Usage: $0 {list|set-api-keys|set-secrets|validate|deploy}"
    echo ""
    echo "Commands:"
    echo "  list         - List all environment variables"
    echo "  set-api-keys - Interactively set AI provider API keys"
    echo "  set-secrets  - Generate and set security secrets"
    echo "  validate     - Validate deployment configuration"
    echo "  deploy       - Deploy to Railway"
    ;;
esac
'''
        
        script_path = Path("railway_vars_manager.sh")
        script_path.write_text(script_content)
        script_path.chmod(0o755)
        logger.info(f"✅ Created Railway variables manager: {script_path}")
    
    def generate_deployment_summary(self) -> Dict[str, Any]:
        """Generate a comprehensive deployment summary."""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "project": self.project_name,
            "services_deployed": len([r for r in self.deployment_results if r.success]),
            "services_failed": len([r for r in self.deployment_results if not r.success]),
            "deployment_results": [
                {
                    "service": r.service_name,
                    "status": "success" if r.success else "failed",
                    "message": r.message,
                    "variables": r.variables or {}
                }
                for r in self.deployment_results
            ],
            "next_steps": [
                "Set API keys using: ./railway_vars_manager.sh set-api-keys",
                "Generate security secrets using: ./railway_vars_manager.sh set-secrets",
                "Validate deployment using: ./railway_vars_manager.sh validate",
                "Deploy using: ./railway_vars_manager.sh deploy",
                "Monitor deployment at: https://railway.app/dashboard"
            ]
        }
        
        # Save summary
        summary_file = Path("railway_deployment_summary.json")
        summary_file.write_text(json.dumps(summary, indent=2))
        logger.info(f"📋 Deployment summary saved to: {summary_file}")
        
        return summary
    
    async def setup_all_services(self) -> bool:
        """Set up all required Railway services."""
        logger.info("🚀 Setting up Railway services for Monkey Coder...")
        
        # Check prerequisites
        if not self.check_railway_cli():
            return False
        
        # Check existing services
        existing_services = self.check_existing_services()
        
        # Set up PostgreSQL
        if "monkey-coder-postgres" not in existing_services:
            postgres_result = self.create_postgres_service()
            self.deployment_results.append(postgres_result)
        else:
            logger.info("✅ PostgreSQL service already exists")
            postgres_result = DeploymentResult(
                success=True,
                service_name="monkey-coder-postgres",
                message="PostgreSQL service already exists"
            )
        
        # Set up Redis
        if "monkey-coder-redis" not in existing_services:
            redis_result = self.create_redis_service()
            self.deployment_results.append(redis_result)
        else:
            logger.info("✅ Redis service already exists")
            redis_result = DeploymentResult(
                success=True,
                service_name="monkey-coder-redis",
                message="Redis service already exists"
            )
        
        # Configure main service variables if services are ready
        if postgres_result.success and redis_result.success:
            # Get actual connection URLs
            db_url = "${DATABASE_URL}"  # Railway will populate this
            redis_url = "${REDIS_URL}"   # Railway will populate this
            
            var_result = self.configure_main_service_variables(db_url, redis_url)
            self.deployment_results.append(var_result)
        
        # Create management scripts
        self.create_railway_variables_script()
        
        # Generate summary
        summary = self.generate_deployment_summary()
        
        # Print results
        self.print_deployment_results()
        
        return all(r.success for r in self.deployment_results)
    
    def print_deployment_results(self):
        """Print a formatted summary of deployment results."""
        print("\n" + "="*60)
        print("🚂 Railway Services Setup Complete")
        print("="*60)
        
        success_count = len([r for r in self.deployment_results if r.success])
        total_count = len(self.deployment_results)
        
        print(f"\n📊 Results: {success_count}/{total_count} services configured successfully")
        
        for result in self.deployment_results:
            status_icon = "✅" if result.success else "❌"
            print(f"\n{status_icon} {result.service_name}")
            print(f"   {result.message}")
            
            if result.variables:
                print("   Variables configured:")
                for key, value in result.variables.items():
                    # Mask sensitive values
                    masked_value = value if not any(secret in key.lower() for secret in ['key', 'secret', 'password', 'token']) else '***MASKED***'
                    print(f"     • {key}={masked_value}")
        
        print(f"\n🔧 Next Steps:")
        print(f"1. Set your API keys: ./railway_vars_manager.sh set-api-keys")
        print(f"2. Generate secrets: ./railway_vars_manager.sh set-secrets")
        print(f"3. Validate config: ./railway_vars_manager.sh validate")
        print(f"4. Deploy: ./railway_vars_manager.sh deploy")
        
        print(f"\n📋 Full summary saved to: railway_deployment_summary.json")

def main():
    """Main entry point."""
    manager = RailwayServicesManager()
    
    try:
        success = asyncio.run(manager.setup_all_services())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()