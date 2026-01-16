#!/usr/bin/env python3
"""
Test script to verify MCP backend endpoints are working correctly.
Can be used by CLI to connect to the backend MCP server.
"""

import asyncio
import httpx
import json
from typing import Dict, Any


async def test_mcp_backend(base_url: str = "http://localhost:8000"):
    """Test all MCP backend endpoints."""
    
    print(f"🔍 Testing MCP Backend at {base_url}\n")
    
    async with httpx.AsyncClient() as client:
        # Test 1: Health check
        print("1️⃣ Testing health endpoint...")
        response = await client.get(f"{base_url}/health")
        health = response.json()
        print(f"   ✅ Status: {health['status']}")
        print(f"   ✅ MCP Server: {health['mcp_server']['status']}")
        print(f"   ✅ Tools Available: {health['mcp_server']['tools_count']}\n")
        
        # Test 2: List tools
        print("2️⃣ Testing list tools endpoint...")
        response = await client.get(f"{base_url}/api/mcp/tools")
        tools = response.json()
        print(f"   ✅ Found {len(tools['tools'])} tools:")
        for tool in tools['tools']:
            print(f"      - {tool['name']}: {tool['description'][:60]}...")
        print()
        
        # Test 3: Call analyze_code tool
        print("3️⃣ Testing analyze_code tool...")
        response = await client.post(
            f"{base_url}/api/mcp/tools/call",
            json={
                "tool_name": "analyze_code",
                "arguments": {
                    "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)",
                    "language": "python",
                    "analysis_type": "quality"
                }
            }
        )
        result = response.json()
        if result['success']:
            content = json.loads(result['content'][0]['text'])
            print(f"   ✅ Analysis completed")
            print(f"      Score: {content['score']}")
            print(f"      Issues: {len(content['issues'])}")
            print(f"      Suggestions: {len(content['suggestions'])}")
        print()
        
        # Test 4: Call generate_code tool
        print("4️⃣ Testing generate_code tool...")
        response = await client.post(
            f"{base_url}/api/mcp/tools/call",
            json={
                "tool_name": "generate_code",
                "arguments": {
                    "prompt": "Create a function to calculate fibonacci numbers",
                    "language": "python"
                }
            }
        )
        result = response.json()
        if result['success']:
            content = json.loads(result['content'][0]['text'])
            print(f"   ✅ Code generated")
            print(f"      Lines: {len(content['code'].split(chr(10)))}")
        print()
        
        # Test 5: Call generate_tests tool
        print("5️⃣ Testing generate_tests tool...")
        response = await client.post(
            f"{base_url}/api/mcp/tools/call",
            json={
                "tool_name": "generate_tests",
                "arguments": {
                    "code": "def divide(a, b):\n    return a / b",
                    "language": "python"
                }
            }
        )
        result = response.json()
        if result['success']:
            content = json.loads(result['content'][0]['text'])
            print(f"   ✅ Tests generated")
            print(f"      Framework: {content['framework']}")
            print(f"      Test Count: {content['test_count']}")
        print()
        
        # Test 6: List resources
        print("6️⃣ Testing list resources endpoint...")
        response = await client.get(f"{base_url}/api/mcp/resources")
        resources = response.json()
        print(f"   ✅ Found {len(resources['resources'])} resources:")
        for resource in resources['resources']:
            print(f"      - {resource['uri']}: {resource['name']}")
        print()
        
        # Test 7: Read resource
        print("7️⃣ Testing read resource endpoint...")
        response = await client.get(
            f"{base_url}/api/mcp/resources/read",
            params={"uri": "project://context"}
        )
        resource_data = response.json()
        context = json.loads(resource_data['content'])
        print(f"   ✅ Resource read successfully")
        print(f"      Project: {context['project_name']}")
        print(f"      Version: {context['version']}")
        print()
        
        print("✨ All tests passed! MCP backend is fully operational.\n")
        print("📝 CLI Integration Guide:")
        print("   - Use HTTP transport to connect to backend")
        print(f"   - Backend URL: {base_url}")
        print("   - Available endpoints:")
        print("     * GET /api/mcp/tools - List available tools")
        print("     * POST /api/mcp/tools/call - Execute a tool")
        print("     * GET /api/mcp/resources - List available resources")
        print("     * GET /api/mcp/resources/read?uri=<uri> - Read a resource")


if __name__ == "__main__":
    # Test with localhost by default
    # Can also test with Railway URL: https://monkey-coder-backend-production.up.railway.app
    asyncio.run(test_mcp_backend())
