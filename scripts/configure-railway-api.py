#!/usr/bin/env python3
"""
Railway API Configuration Script for AetherOS Project

This script uses the Railway GraphQL API to configure environment variables
for monkey-coder services in the AetherOS project.

Prerequisites:
    - Railway API token: export RAILWAY_API_TOKEN=<your-token>
    - Get token from: https://railway.app/account/tokens

Usage:
    export RAILWAY_API_TOKEN=your_token_here
    python scripts/configure-railway-api.py
    python scripts/configure-railway-api.py --dry-run  # Preview only
"""

import argparse
import json
import os
import secrets
import sys
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)


class RailwayAPI:
    """Railway GraphQL API client."""

    GRAPHQL_ENDPOINT = "https://backboard.railway.app/graphql/v2"

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    def execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute a GraphQL query."""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = requests.post(
            self.GRAPHQL_ENDPOINT,
            headers=self.headers,
            json=payload,
        )

        if response.status_code != 200:
            raise Exception(f"GraphQL request failed: {response.status_code} - {response.text}")

        result = response.json()
        if "errors" in result:
            raise Exception(f"GraphQL errors: {result['errors']}")

        return result.get("data", {})

    def get_project_services(self, project_id: str) -> List[Dict]:
        """Get all services in a project."""
        query = """
        query GetProjectServices($projectId: String!) {
            project(id: $projectId) {
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
        """
        data = self.execute_query(query, {"projectId": project_id})
        project = data.get("project", {})
        services = project.get("services", {}).get("edges", [])
        return [edge["node"] for edge in services]

    def set_service_variables(
        self,
        service_id: str,
        environment_id: str,
        variables: Dict[str, str],
    ) -> bool:
        """Set environment variables for a service."""
        query = """
        mutation UpsertVariables($input: VariableUpsertInput!) {
            variableUpsert(input: $input)
        }
        """

        for name, value in variables.items():
            input_data = {
                "projectId": "",  # Not needed when using serviceId
                "environmentId": environment_id,
                "serviceId": service_id,
                "name": name,
                "value": value,
            }

            try:
                self.execute_query(query, {"input": input_data})
                print(f"  ✓ Set {name}")
            except Exception as e:
                print(f"  ✗ Failed to set {name}: {e}")
                return False

        return True

    def get_environments(self, project_id: str) -> List[Dict]:
        """Get environments in a project."""
        query = """
        query GetEnvironments($projectId: String!) {
            project(id: $projectId) {
                environments {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        }
        """
        data = self.execute_query(query, {"projectId": project_id})
        environments = data.get("project", {}).get("environments", {}).get("edges", [])
        return [edge["node"] for edge in environments]


def generate_sandbox_token() -> str:
    """Generate a secure 64-character hex token."""
    return secrets.token_hex(32)


def get_service_config(sandbox_token: str) -> Dict[str, Dict[str, str]]:
    """Get configuration for each service."""
    return {
        "monkey-coder-sandbox": {
            "SANDBOX_TOKEN_SECRET": sandbox_token,
            "SANDBOX_ALLOW_ORIGINS": "https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}",
            "SANDBOX_ALLOW_ORIGIN_REGEX": r"^https?://([a-z0-9-]+\.)*railway\.app$",
            "LOG_LEVEL": "info",
            "PYTHONUNBUFFERED": "1",
        },
        "monkey-coder-backend": {
            "SANDBOX_SERVICE_URL": "http://${{monkey-coder-sandbox.RAILWAY_PRIVATE_DOMAIN}}",
            "SANDBOX_TOKEN_SECRET": sandbox_token,
            "PYTHON_ENV": "production",
            "PYTHONUNBUFFERED": "1",
            "LOG_LEVEL": "info",
        },
        "monkey-coder": {
            "NEXT_PUBLIC_API_URL": "https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}",
            "NODE_ENV": "production",
            "NEXT_TELEMETRY_DISABLED": "1",
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Configure Railway environment variables for AetherOS project"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them",
    )
    parser.add_argument(
        "--project-id",
        default="9n",
        help="Railway project ID (default: 9n)",
    )
    parser.add_argument(
        "--environment",
        default="production",
        help="Environment name (default: production)",
    )
    args = parser.parse_args()

    # Get API token
    api_token = os.getenv("RAILWAY_API_TOKEN")
    if not api_token:
        print("Error: RAILWAY_API_TOKEN environment variable not set")
        print("Get your token from: https://railway.app/account/tokens")
        print("\nUsage:")
        print("  export RAILWAY_API_TOKEN=your_token_here")
        print(f"  python {sys.argv[0]}")
        sys.exit(1)

    print("=" * 70)
    print("Railway Environment Configuration for AetherOS Project")
    print("=" * 70)
    print()

    if args.dry_run:
        print("⚠️  DRY RUN MODE - No changes will be applied")
        print()

    # Initialize API client
    api = RailwayAPI(api_token)

    # Generate secure token
    print("🔐 Generating secure SANDBOX_TOKEN_SECRET...")
    sandbox_token = generate_sandbox_token()
    print(f"   Generated: {sandbox_token[:8]}...(truncated)")
    print()

    # Get service configuration
    config = get_service_config(sandbox_token)

    print("📋 Configuration Plan:")
    print()
    for service_name, variables in config.items():
        print(f"Service: {service_name}")
        for var_name, var_value in variables.items():
            # Don't show full token value
            display_value = var_value
            if "SECRET" in var_name or "TOKEN" in var_name:
                display_value = f"{var_value[:8]}...(truncated)"
            print(f"  - {var_name}={display_value}")
        print()

    if args.dry_run:
        print("✓ Dry run complete. No changes were applied.")
        return

    # Confirm with user
    response = input("Apply these configurations? (yes/no): ")
    if response.lower() != "yes":
        print("Configuration cancelled by user.")
        return

    print()
    print("🚀 Applying configurations...")
    print()

    try:
        # Get project services
        print(f"📡 Fetching services from project {args.project_id}...")
        services = api.get_project_services(args.project_id)
        print(f"   Found {len(services)} services")
        print()

        # Get environment ID
        environments = api.get_environments(args.project_id)
        env_id = None
        for env in environments:
            if env["name"].lower() == args.environment.lower():
                env_id = env["id"]
                break

        if not env_id:
            print(f"Error: Environment '{args.environment}' not found")
            sys.exit(1)

        print(f"🌍 Using environment: {args.environment} (ID: {env_id})")
        print()

        # Apply configuration to each service
        for service in services:
            service_name = service["name"]
            service_id = service["id"]

            if service_name not in config:
                print(f"⏭️  Skipping {service_name} (no configuration)")
                continue

            print(f"⚙️  Configuring {service_name}...")
            variables = config[service_name]
            success = api.set_service_variables(service_id, env_id, variables)

            if success:
                print(f"   ✅ {service_name} configured successfully")
            else:
                print(f"   ❌ {service_name} configuration failed")
            print()

        print("=" * 70)
        print("✅ Configuration completed!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Verify variables in Railway Dashboard")
        print("  2. Redeploy services for changes to take effect")
        print("  3. Check service health and logs")
        print()
        print("For detailed documentation, see:")
        print("  docs/deployment/railway-aetheros-config.md")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
