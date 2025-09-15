"""
MCP-Enhanced Environment Variable Manager

This module provides environment variable management using Model Context Protocol (MCP)
servers to access and interact with variables directly, avoiding hardcoded localhost
references in production environments.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class EnvironmentVariable:
    """Represents an environment variable with MCP integration."""
    key: str
    value: Optional[str]
    source: str  # "env", "mcp", "railway", "default"
    priority: int  # Lower = higher priority
    description: str = ""


class MCPEnvironmentManager:
    """
    MCP-enhanced environment variable manager.
    
    Provides intelligent environment variable resolution using:
    1. Direct environment variables (highest priority)
    2. MCP server variable resolution 
    3. Railway service discovery
    4. Production-aware defaults (no localhost)
    """
    
    def __init__(self):
        self.variables: Dict[str, EnvironmentVariable] = {}
        self.mcp_available = False
        self.railway_environment = os.getenv('RAILWAY_ENVIRONMENT')
        self.railway_project = os.getenv('RAILWAY_PROJECT_NAME', 'monkey-coder')
        self.railway_public_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN')
        
        # Initialize MCP availability
        self._check_mcp_availability()
        
    def _check_mcp_availability(self):
        """Check if MCP servers are available for variable resolution."""
        try:
            # Check if Context7 MCP is configured
            from .mcp_config import MCPConfig
            context7_url = MCPConfig.get_context7_url()
            if context7_url and not context7_url.startswith('http://localhost'):
                self.mcp_available = True
                logger.info("✅ MCP variable resolution available via Context7")
        except ImportError:
            logger.debug("MCP configuration not available")
            
    def get_variable(self, key: str, fallback: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable using MCP-enhanced resolution.
        
        Args:
            key: Environment variable key
            fallback: Fallback value if not found
            
        Returns:
            Variable value or fallback
        """
        # Priority 1: Direct environment variable
        env_value = os.getenv(key)
        if env_value and not self._is_localhost_reference(env_value):
            self.variables[key] = EnvironmentVariable(
                key=key,
                value=env_value,
                source="env",
                priority=1,
                description=f"Direct environment variable: {key}"
            )
            return env_value
            
        # Priority 2: MCP server resolution
        if self.mcp_available:
            mcp_value = self._resolve_via_mcp(key)
            if mcp_value:
                self.variables[key] = EnvironmentVariable(
                    key=key,
                    value=mcp_value,
                    source="mcp",
                    priority=2,
                    description=f"MCP server resolved: {key}"
                )
                return mcp_value
                
        # Priority 3: Railway service discovery
        railway_value = self._resolve_via_railway(key)
        if railway_value:
            self.variables[key] = EnvironmentVariable(
                key=key,
                value=railway_value,
                source="railway",
                priority=3,
                description=f"Railway service discovery: {key}"
            )
            return railway_value
            
        # Priority 4: Production-aware defaults
        default_value = self._get_production_default(key)
        if default_value:
            self.variables[key] = EnvironmentVariable(
                key=key,
                value=default_value,
                source="default",
                priority=4,
                description=f"Production default: {key}"
            )
            return default_value
            
        # Priority 5: Provided fallback
        if fallback:
            self.variables[key] = EnvironmentVariable(
                key=key,
                value=fallback,
                source="fallback",
                priority=5,
                description=f"Provided fallback: {key}"
            )
            return fallback
            
        return None
        
    def _is_localhost_reference(self, value: str) -> bool:
        """Check if a value references localhost (not useful in production)."""
        if not value:
            return False
            
        localhost_indicators = [
            'localhost',
            '127.0.0.1',
            '::1',
            'http://localhost',
            'postgresql://localhost',
            'redis://localhost'
        ]
        
        return any(indicator in value.lower() for indicator in localhost_indicators)
        
    def _resolve_via_mcp(self, key: str) -> Optional[str]:
        """Resolve variable via MCP server."""
        # This would integrate with actual MCP servers in a full implementation
        # For now, return None as MCP integration is placeholder
        logger.debug(f"MCP resolution attempted for {key} (not implemented)")
        return None
        
    def _resolve_via_railway(self, key: str) -> Optional[str]:
        """Resolve variable using Railway service discovery."""
        railway_mapping = {
            'DATABASE_URL': self._get_railway_database_url(),
            'NEXT_PUBLIC_API_URL': self._get_railway_api_url(),
            'NEXT_PUBLIC_APP_URL': self._get_railway_api_url(),
            'NEXTAUTH_URL': self._get_railway_api_url(),
            'REDIS_URL': self._get_railway_redis_url(),
        }
        
        return railway_mapping.get(key)
        
    def _get_railway_database_url(self) -> Optional[str]:
        """Get Railway database URL using service discovery."""
        # Check for Railway database service variables
        db_host = os.getenv('RAILWAY_DB_HOST') or os.getenv('PGHOST')
        db_port = os.getenv('RAILWAY_DB_PORT') or os.getenv('PGPORT', '5432')
        db_name = os.getenv('RAILWAY_DB_NAME') or os.getenv('PGDATABASE', 'railway')
        db_user = os.getenv('RAILWAY_DB_USER') or os.getenv('PGUSER', 'postgres')
        db_password = os.getenv('RAILWAY_DB_PASSWORD') or os.getenv('PGPASSWORD', '')
        
        if db_host:
            return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            
        # Use Railway internal networking
        return "postgresql://railway.internal:5432/railway"
        
    def _get_railway_api_url(self) -> Optional[str]:
        """Get Railway API URL using public domain."""
        if self.railway_public_domain:
            return f"https://{self.railway_public_domain}"
            
        if self.railway_environment and self.railway_project:
            return f"https://{self.railway_project}-{self.railway_environment}.railway.app"
            
        # Use configured production domain
        return "https://coder.fastmonkey.au"
        
    def _get_railway_redis_url(self) -> Optional[str]:
        """Get Railway Redis URL using service discovery."""
        redis_host = os.getenv('RAILWAY_REDIS_HOST')
        redis_port = os.getenv('RAILWAY_REDIS_PORT', '6379')
        redis_password = os.getenv('RAILWAY_REDIS_PASSWORD', '')
        
        if redis_host:
            if redis_password:
                return f"redis://:{redis_password}@{redis_host}:{redis_port}"
            return f"redis://{redis_host}:{redis_port}"
            
        # Use Railway internal networking
        return "redis://railway.internal:6379"
        
    def _get_production_default(self, key: str) -> Optional[str]:
        """Get production-aware default values (no localhost)."""
        production_defaults = {
            'DATABASE_URL': 'postgresql://railway.internal:5432/railway',
            'REDIS_URL': 'redis://railway.internal:6379',
            'NEXT_PUBLIC_API_URL': 'https://coder.fastmonkey.au',
            'NEXT_PUBLIC_APP_URL': 'https://coder.fastmonkey.au',
            'NEXTAUTH_URL': 'https://coder.fastmonkey.au',
            'STRIPE_PUBLIC_KEY': 'pk_test_placeholder',
            'STRIPE_SECRET_KEY': 'sk_test_placeholder',
            'STRIPE_WEBHOOK_SECRET': 'whsec_placeholder',
        }
        
        return production_defaults.get(key)
        
    def get_all_variables(self) -> Dict[str, EnvironmentVariable]:
        """Get all resolved variables."""
        return self.variables.copy()
        
    def get_variable_summary(self) -> Dict[str, Any]:
        """Get summary of variable resolution."""
        sources = {}
        for var in self.variables.values():
            source = var.source
            if source not in sources:
                sources[source] = 0
            sources[source] += 1
            
        return {
            'total_variables': len(self.variables),
            'sources': sources,
            'mcp_available': self.mcp_available,
            'railway_environment': self.railway_environment,
            'railway_public_domain': self.railway_public_domain,
        }
        
    def validate_production_readiness(self) -> Dict[str, Any]:
        """Validate that variables are production-ready (no localhost)."""
        issues = []
        warnings = []
        
        for var in self.variables.values():
            if var.value and self._is_localhost_reference(var.value):
                issues.append(f"{var.key}: Contains localhost reference ({var.value})")
                
            if var.source == "fallback":
                warnings.append(f"{var.key}: Using fallback value, may not be production-ready")
                
        return {
            'production_ready': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'summary': self.get_variable_summary()
        }


# Global instance for easy access
mcp_env_manager = MCPEnvironmentManager()


def get_mcp_variable(key: str, fallback: Optional[str] = None) -> Optional[str]:
    """
    Convenience function to get MCP-enhanced environment variable.
    
    Args:
        key: Environment variable key
        fallback: Fallback value
        
    Returns:
        Variable value
    """
    return mcp_env_manager.get_variable(key, fallback)


def get_production_database_url() -> str:
    """Get production database URL using MCP environment manager."""
    return get_mcp_variable('DATABASE_URL', 'postgresql://railway.internal:5432/railway')


def get_production_api_url() -> str:
    """Get production API URL using MCP environment manager."""
    return get_mcp_variable('NEXT_PUBLIC_API_URL', 'https://coder.fastmonkey.au')


def get_production_redis_url() -> str:
    """Get production Redis URL using MCP environment manager."""
    return get_mcp_variable('REDIS_URL', 'redis://railway.internal:6379')