"""
Model Context Protocol (MCP) integration for Monkey Coder
Provides tools and resources from external servers
"""

from .client import MCPClient, MCPTool, MCPResource
from .server_manager import MCPServerManager, MCPServerConfig
from .registry import MCPServerRegistry

try:
    from .server import mcp
    __all__ = [
        "MCPClient",
        "MCPTool",
        "MCPResource",
        "MCPServerManager",
        "MCPServerConfig",
        "MCPServerRegistry",
        "mcp",
    ]
except ImportError:
    # MCP server not available (fastmcp not installed)
    __all__ = [
        "MCPClient",
        "MCPTool",
        "MCPResource",
        "MCPServerManager",
        "MCPServerConfig",
        "MCPServerRegistry",
    ]
