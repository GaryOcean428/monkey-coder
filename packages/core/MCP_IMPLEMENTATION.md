# MCP Backend Implementation

## Overview

This implementation provides a complete MCP (Model Context Protocol) server backend using FastMCP, exposing AI-powered code tools that the CLI can call remotely via HTTP transport.

## Architecture

### Core Components

1. **FastMCP Server** (`monkey_coder/mcp/server.py`)
   - Stateless HTTP support enabled
   - 5 AI-powered tools
   - 2 resource endpoints
   - Mounted at `/mcp` for SSE transport

2. **REST API Wrapper** (`monkey_coder/app/routes/mcp.py`)
   - Backward-compatible REST endpoints
   - Tool listing and execution
   - Resource discovery and reading
   - Health checks

3. **Service Layer** (`monkey_coder/services/`)
   - `TestGenerator` - Generate unit tests
   - `CodeRefactorer` - Refactor code per instructions
   - `CodeExplainer` - Explain code in natural language
   - `CodeAnalyzer` - Analyze code quality/security (updated with async)
   - `CodeGenerator` - Generate code from prompts (updated with async)

## Available Tools

### 1. analyze_code
Analyze code for quality, security, or performance issues.

**Arguments:**
- `code` (str, required) - Source code to analyze
- `language` (str, default: "python") - Programming language
- `analysis_type` (str, default: "quality") - Type of analysis

**Returns:**
```json
{
  "code": "...",
  "language": "python",
  "analysis_type": "quality",
  "score": 0.8,
  "issues": [...],
  "suggestions": [...]
}
```

### 2. generate_code
Generate code based on natural language prompt.

**Arguments:**
- `prompt` (str, required) - Description of code to generate
- `language` (str, default: "python") - Target programming language
- `context` (str, optional) - Existing code context

**Returns:**
```json
{
  "code": "...",
  "prompt": "...",
  "language": "python",
  "explanation": "...",
  "context_used": false
}
```

### 3. generate_tests
Generate unit tests for provided code.

**Arguments:**
- `code` (str, required) - Source code to test
- `language` (str, default: "python") - Programming language
- `framework` (str, optional) - Test framework (auto-detected if not provided)

**Returns:**
```json
{
  "test_code": "...",
  "framework": "pytest",
  "language": "python",
  "estimated_coverage": 0.8,
  "test_count": 5
}
```

### 4. refactor_code
Refactor code according to instructions.

**Arguments:**
- `code` (str, required) - Original source code
- `instructions` (str, required) - Refactoring instructions
- `language` (str, default: "python") - Programming language

**Returns:**
```json
{
  "original_code": "...",
  "refactored_code": "...",
  "diff": "...",
  "instructions": "...",
  "language": "python",
  "changes_summary": "Added 5 lines, removed 2 lines"
}
```

### 5. explain_code
Explain what code does in natural language.

**Arguments:**
- `code` (str, required) - Source code to explain
- `language` (str, default: "python") - Programming language
- `detail_level` (str, default: "medium") - Level of detail (brief, medium, detailed)

**Returns:**
```json
{
  "code": "...",
  "explanation": "...",
  "language": "python",
  "detail_level": "medium",
  "components": {
    "functions": ["add", "subtract"],
    "classes": ["Calculator"],
    "imports": ["import math"]
  },
  "complexity": "low"
}
```

## Resources

### project://context
Get current project context and configuration.

**Returns:**
```json
{
  "project_name": "Monkey Coder",
  "version": "1.2.0",
  "environment": "production",
  "available_tools": [...]
}
```

### project://status
Get current project status and health.

**Returns:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-16T10:17:16.718137",
  "mcp_version": "1.25.0",
  "tools_available": 5,
  "resources_available": 2
}
```

## API Endpoints

### Health Check
```bash
GET /health
GET /api/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-16T10:17:16.718137",
  "service": "monkey-coder-api",
  "mcp_server": {
    "status": "operational",
    "tools_count": 5
  }
}
```

### List Tools
```bash
GET /api/mcp/tools
```

Response:
```json
{
  "tools": [
    {
      "name": "analyze_code",
      "description": "...",
      "inputSchema": {...}
    },
    ...
  ]
}
```

### Call Tool
```bash
POST /api/mcp/tools/call
Content-Type: application/json

{
  "tool_name": "explain_code",
  "arguments": {
    "code": "def add(a, b): return a + b",
    "language": "python"
  }
}
```

Response:
```json
{
  "success": true,
  "content": [
    {
      "type": "text",
      "text": "{...json result...}"
    }
  ],
  "is_error": false
}
```

### List Resources
```bash
GET /api/mcp/resources
```

Response:
```json
{
  "resources": [
    {
      "uri": "project://context",
      "name": "get_project_context",
      "description": "...",
      "mimeType": "text/plain"
    },
    ...
  ]
}
```

### Read Resource
```bash
GET /api/mcp/resources/read?uri=project://context
```

Response:
```json
{
  "uri": "project://context",
  "content": "{...json content...}",
  "mime_type": "text/plain"
}
```

### MCP Health
```bash
GET /api/mcp/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-16T10:17:16.718137",
  "mcp_server": "operational",
  "tools_available": 5
}
```

## CLI Integration

The CLI can connect to the MCP backend using HTTP transport:

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";

const transport = new SSEClientTransport(
  new URL("http://localhost:8000/mcp")
);
const client = new Client({ name: "monkey-cli", version: "1.0.0" }, {
  capabilities: {}
});

await client.connect(transport);

// List tools
const tools = await client.listTools();

// Call a tool
const result = await client.callTool({
  name: "analyze_code",
  arguments: {
    code: "def test(): pass",
    language: "python"
  }
});
```

## Testing

Run the comprehensive test suite:

```bash
cd packages/core
python test_mcp_backend.py
```

This tests:
- Health endpoint
- Tool listing
- Tool execution (all 5 tools)
- Resource listing
- Resource reading

## Deployment

### Local Development
```bash
cd packages/core
python -m uvicorn monkey_coder.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Railway Deployment
The MCP server is automatically deployed with the FastAPI application on Railway. No additional configuration needed.

Environment variables:
- `CORS_ORIGINS` - Configure allowed origins (default: "*")
- `ENVIRONMENT` - Set to "production" for production (default: "production")

### Testing Production
```bash
# Test Railway deployment
python test_mcp_backend.py
# When prompted, use: https://monkey-coder-backend-production.up.railway.app
```

## Dependencies

Added to `pyproject.toml` and `requirements.txt`:
```
mcp[cli]>=1.25.0
```

This includes:
- FastMCP server framework
- HTTP/SSE transport support
- Tool and resource decorators
- JSON-RPC protocol implementation

## Files Created/Modified

### New Files
- `packages/core/monkey_coder/mcp/server.py` - FastMCP server with tools
- `packages/core/monkey_coder/app/routes/mcp.py` - REST API wrapper
- `packages/core/monkey_coder/services/__init__.py` - Service exports
- `packages/core/monkey_coder/services/test_generator.py` - Test generation service
- `packages/core/monkey_coder/services/refactor.py` - Code refactoring service
- `packages/core/monkey_coder/services/explainer.py` - Code explanation service
- `packages/core/test_mcp_backend.py` - Comprehensive test suite

### Modified Files
- `packages/core/monkey_coder/app/main.py` - Mounted MCP server, added health check
- `packages/core/monkey_coder/mcp/__init__.py` - Export MCP server
- `packages/core/monkey_coder/analyzer.py` - Added async `analyze()` method
- `packages/core/monkey_coder/generator.py` - Added async `generate()` method
- `packages/core/pyproject.toml` - Added mcp dependency
- `packages/core/requirements.txt` - Added mcp dependency

## Status

✅ **Complete and Ready for Production**

All acceptance criteria met:
- [x] MCP server mounted at `/mcp` endpoint using Streamable HTTP transport
- [x] Tools available: `analyze_code`, `generate_code`, `generate_tests`, `refactor_code`, `explain_code`
- [x] REST wrapper at `/api/mcp/tools` for backward compatibility
- [x] CLI can connect to backend MCP server via SSE transport
- [x] Tool schemas exposed via `/api/mcp/tools` endpoint
- [x] Resources endpoint returns project context
- [x] Health check includes MCP server status

All tests passing ✨
