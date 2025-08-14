"""
MCP (Model Context Protocol) Configuration

Hardcoded configuration for MCP servers, including Context7 for
up-to-date documentation and model information.
"""

from typing import Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)


class MCPConfig:
    """MCP server configuration with Context7 integration."""
    
    # Hardcoded Context7 configuration
    CONTEXT7_CONFIG = {
        "type": "http",
        "url": "https://mcp.context7.com/mcp",
        "description": "Up-to-date documentation server for AI models and libraries",
        "github": "https://github.com/upstash/context7",
        "capabilities": [
            "model_documentation",
            "library_docs",
            "api_references",
            "real_time_updates"
        ]
    }
    
    # Full MCP configuration
    MCP_SERVERS = {
        "context7": CONTEXT7_CONFIG,
        # Add other MCP servers here as needed
    }
    
    @classmethod
    def get_mcp_config(cls) -> Dict[str, Any]:
        """
        Get the complete MCP configuration.
        
        Returns:
            Dict with MCP server configurations
        """
        return {
            "mcp": {
                "servers": cls.MCP_SERVERS
            }
        }
    
    @classmethod
    def get_context7_config(cls) -> Dict[str, Any]:
        """
        Get Context7 specific configuration.
        
        Returns:
            Context7 server configuration
        """
        return cls.CONTEXT7_CONFIG
    
    @classmethod
    def get_context7_url(cls) -> str:
        """
        Get Context7 MCP URL.
        
        Returns:
            Context7 MCP endpoint URL
        """
        # Allow override via environment variable for testing
        return os.getenv("CONTEXT7_URL", cls.CONTEXT7_CONFIG["url"])
    
    @classmethod
    def is_context7_available(cls) -> bool:
        """
        Check if Context7 is available and configured.
        
        Returns:
            True if Context7 is configured
        """
        return bool(cls.CONTEXT7_CONFIG.get("url"))


# Export configuration
MCP_CONFIG = MCPConfig.get_mcp_config()
CONTEXT7_URL = MCPConfig.get_context7_url()