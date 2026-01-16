"""
MCP Tools REST API Router
Provides REST wrapper for MCP tools for backward compatibility
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List


router = APIRouter(prefix="/api/mcp", tags=["mcp"])


class ToolCallRequest(BaseModel):
    """Request model for tool execution"""
    tool_name: str
    arguments: Dict[str, Any]


class ToolCallResponse(BaseModel):
    """Response model for tool execution"""
    success: bool
    content: List[Dict[str, Any]]
    is_error: bool = False


class ToolInfo(BaseModel):
    """Information about a tool"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


class ResourceInfo(BaseModel):
    """Information about a resource"""
    uri: str
    name: str
    description: str
    mimeType: str


@router.get("/tools")
async def list_tools() -> Dict[str, List[ToolInfo]]:
    """List all available MCP tools."""
    from monkey_coder.mcp.server import mcp
    
    try:
        tools_list = await mcp.list_tools()
        
        # Convert MCP tools to our response format
        tools = []
        for tool in tools_list:
            tools.append(ToolInfo(
                name=tool.name,
                description=tool.description or "",
                inputSchema=tool.inputSchema or {}
            ))
        
        return {"tools": tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")


@router.post("/tools/call")
async def call_tool(request: ToolCallRequest) -> ToolCallResponse:
    """Execute an MCP tool."""
    from monkey_coder.mcp.server import mcp
    
    try:
        result_list = await mcp.call_tool(request.tool_name, request.arguments)
        
        # Convert result to response format
        content = []
        for item in result_list:
            if hasattr(item, 'text'):
                content.append({"type": "text", "text": item.text})
            elif hasattr(item, 'type'):
                content.append({"type": item.type, "data": str(item)})
            else:
                content.append({"type": "unknown", "data": str(item)})
        
        return ToolCallResponse(
            success=True,
            content=content,
            is_error=False
        )
    except Exception as e:
        return ToolCallResponse(
            success=False,
            content=[{"type": "error", "text": str(e)}],
            is_error=True
        )


@router.get("/resources")
async def list_resources() -> Dict[str, List[ResourceInfo]]:
    """List all available MCP resources."""
    from monkey_coder.mcp.server import mcp
    
    try:
        resources_list = await mcp.list_resources()
        
        # Convert MCP resources to our response format
        resources = []
        for resource in resources_list:
            resources.append(ResourceInfo(
                uri=str(resource.uri),  # Convert AnyUrl to string
                name=resource.name or str(resource.uri),
                description=resource.description or "",
                mimeType=resource.mimeType or "text/plain"
            ))
        
        return {"resources": resources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list resources: {str(e)}")


@router.get("/resources/read")
async def read_resource(uri: str) -> Dict[str, Any]:
    """Read an MCP resource by URI."""
    from monkey_coder.mcp.server import mcp
    
    try:
        content_list = await mcp.read_resource(uri)
        
        # Extract content
        content = ""
        mime_type = "text/plain"
        for item in content_list:
            if hasattr(item, 'content'):
                content += str(item.content)
            if hasattr(item, 'mime_type'):
                mime_type = item.mime_type
        
        return {
            "uri": uri,
            "content": content,
            "mime_type": mime_type
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Resource not found: {str(e)}")


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check for MCP server."""
    from monkey_coder.mcp.server import mcp
    from datetime import datetime
    
    try:
        # Test that MCP server is responsive
        tools_list = await mcp.list_tools()
        tool_count = len(tools_list)
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "mcp_server": "operational",
            "tools_available": tool_count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "mcp_server": "error",
            "error": str(e)
        }
