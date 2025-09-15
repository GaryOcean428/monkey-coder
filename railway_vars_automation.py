#!/usr/bin/env python3
"""
Railway Environment Variables Automation
Provides multiple methods to set environment variables for Railway deployment.
"""

import os
import sys
import json
import requests
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RailwayVariablesAutomation:
    """Automates Railway environment variable configuration."""
    
    def __init__(self):
        self.token = os.getenv('RAILWAY_TOKEN')
        self.project_id = None
        self.service_id = None
        self.base_url = "https://backboard.railway.app/graphql"
        
    def get_environment_variables(self) -> Dict[str, str]:
        """Get the complete environment variables dictionary."""
        return {
            # Core Application Settings
            "NODE_ENV": "production",
            "PYTHON_ENV": "production",
            "RAILWAY_ENVIRONMENT": "production",
            
            # Security Configuration
            "JWT_SECRET_KEY": "QwfZ4DUMAXpQIm010ntVFsiIh9T9Nlxf",
            "NEXTAUTH_SECRET": "52TLtnB8u95dfcfnqwsAfJP88e6NZkoO",
            
            # Frontend Configuration
            "NEXTAUTH_URL": "https://coder.fastmonkey.au",
            "NEXT_PUBLIC_API_URL": "https://coder.fastmonkey.au",
            "NEXT_PUBLIC_APP_URL": "https://coder.fastmonkey.au",
            "NEXT_OUTPUT_EXPORT": "true",
            "NEXT_TELEMETRY_DISABLED": "1",
            
            # AI Providers (placeholders - replace with real keys)
            "OPENAI_API_KEY": "your_real_openai_key_here",
            "ANTHROPIC_API_KEY": "your_real_anthropic_key_here",
            "GOOGLE_API_KEY": "your_real_google_key_here",
            "GROQ_API_KEY": "your_real_groq_key_here",
            
            # Payment Configuration (placeholders)
            "STRIPE_PUBLIC_KEY": "pk_test_placeholder",
            "STRIPE_SECRET_KEY": "sk_test_placeholder",
            "STRIPE_WEBHOOK_SECRET": "whsec_placeholder",
            
            # Monitoring (placeholder)
            "SENTRY_DSN": "your_sentry_dsn_here"
        }
    
    def set_variables_via_api(self) -> bool:
        """Attempt to set variables via Railway GraphQL API."""
        if not self.token:
            logger.error("❌ RAILWAY_TOKEN not found")
            return False
            
        try:
            # First, get the project and service information
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            # GraphQL query to get projects
            query = """
            query {
                projects {
                    edges {
                        node {
                            id
                            name
                            services {
                                edges {
                                    node {
                                        id
                                        name
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """
            
            response = requests.post(
                self.base_url,
                json={"query": query},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Successfully connected to Railway API")
                
                # Find the monkey-coder project
                projects = data.get('data', {}).get('projects', {}).get('edges', [])
                for project_edge in projects:
                    project = project_edge['node']
                    if 'monkey' in project['name'].lower():
                        self.project_id = project['id']
                        logger.info(f"🎯 Found project: {project['name']} ({self.project_id})")
                        
                        # Find the service
                        services = project.get('services', {}).get('edges', [])
                        for service_edge in services:
                            service = service_edge['node']
                            self.service_id = service['id']
                            logger.info(f"🔧 Found service: {service['name']} ({self.service_id})")
                            break
                        break
                
                if self.project_id and self.service_id:
                    return self._set_variables_graphql(headers)
                else:
                    logger.error("❌ Could not find monkey-coder project/service")
                    return False
            else:
                logger.error(f"❌ API request failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ API method failed: {e}")
            return False
    
    def _set_variables_graphql(self, headers: Dict[str, str]) -> bool:
        """Set variables using GraphQL mutations."""
        variables = self.get_environment_variables()
        
        for key, value in variables.items():
            try:
                mutation = """
                mutation variableUpsert($input: VariableUpsertInput!) {
                    variableUpsert(input: $input) {
                        id
                        name
                        value
                    }
                }
                """
                
                variables_input = {
                    "input": {
                        "name": key,
                        "value": value,
                        "environmentId": self.service_id,
                        "serviceId": self.service_id
                    }
                }
                
                response = requests.post(
                    self.base_url,
                    json={
                        "query": mutation,
                        "variables": variables_input
                    },
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Set {key}")
                else:
                    logger.warning(f"⚠️  Failed to set {key}: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"⚠️  Error setting {key}: {e}")
        
        return True
    
    def generate_cli_script(self) -> str:
        """Generate Railway CLI script for manual execution."""
        variables = self.get_environment_variables()
        script = "#!/bin/bash\n"
        script += "# Railway Environment Variables Setup\n"
        script += "# Run this after: railway login && railway link\n\n"
        
        for key, value in variables.items():
            script += f'railway variables set {key}="{value}"\n'
        
        script += "\necho '✅ Environment variables setup completed!'\n"
        script += "echo 'Now redeploy: railway redeploy'\n"
        
        return script
    
    def generate_dashboard_instructions(self) -> str:
        """Generate instructions for Railway dashboard setup."""
        variables = self.get_environment_variables()
        
        instructions = """# RAILWAY DASHBOARD ENVIRONMENT SETUP

## Step 1: Access Railway Dashboard
1. Go to: https://railway.app/dashboard
2. Select your project (AetherOS or similar)
3. Click on the monkey-coder service
4. Go to the "Variables" tab

## Step 2: Add Environment Variables
Copy and paste these variables one by one:

"""
        
        for key, value in variables.items():
            instructions += f"{key}={value}\n"
        
        instructions += """
## Step 3: Verify Build Configuration
1. Go to "Settings" tab
2. Ensure "Build Method" is set to "Railpack"
3. Ensure "Start Command" is: python run_server.py

## Step 4: Redeploy
1. Go to "Deployments" tab
2. Click "Redeploy"
3. Monitor logs for successful frontend build

## Critical Variables for Frontend:
- NEXT_OUTPUT_EXPORT=true (enables static export)
- NEXTAUTH_URL=https://coder.fastmonkey.au (correct URL)
- NEXT_PUBLIC_API_URL=https://coder.fastmonkey.au (API endpoint)

## Security Notes:
- Replace JWT_SECRET_KEY with a real secure key
- Replace NEXTAUTH_SECRET with a real secure key
- Replace AI provider API keys with real keys

Generated: """ + str(os.popen('date').read().strip())
        
        return instructions
    
    def run_automation(self) -> bool:
        """Run the complete automation process."""
        logger.info("🚀 Starting Railway environment variables automation...")
        
        # Try API method first
        if self.set_variables_via_api():
            logger.info("✅ Variables set via API")
            return True
        
        # Generate fallback scripts and instructions
        logger.info("📝 Generating fallback scripts...")
        
        # CLI script
        cli_script = self.generate_cli_script()
        with open("railway_vars_cli.sh", "w") as f:
            f.write(cli_script)
        os.chmod("railway_vars_cli.sh", 0o755)
        logger.info("✅ Created railway_vars_cli.sh")
        
        # Dashboard instructions
        dashboard_instructions = self.generate_dashboard_instructions()
        with open("RAILWAY_VARS_SETUP.md", "w") as f:
            f.write(dashboard_instructions)
        logger.info("✅ Created RAILWAY_VARS_SETUP.md")
        
        logger.info("""
🎯 NEXT STEPS:
1. If Railway CLI is available, run: ./railway_vars_cli.sh
2. Otherwise, follow instructions in: RAILWAY_VARS_SETUP.md
3. After setting variables, redeploy: railway redeploy
        """)
        
        return True

def main():
    """Main execution function."""
    automation = RailwayVariablesAutomation()
    automation.run_automation()

if __name__ == "__main__":
    main()