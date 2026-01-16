"""
FastMCP Server Implementation for Monkey Coder Tools
Provides AI-powered code tools via Model Context Protocol
"""

from typing import Any, Dict, Optional
from mcp.server.fastmcp import FastMCP


# Initialize FastMCP server with stateless HTTP support
mcp = FastMCP("MonkeyCoderTools", stateless_http=True)


@mcp.tool()
async def analyze_code(
    code: str,
    language: str = "python",
    analysis_type: str = "quality"
) -> dict:
    """Analyze code for quality, security, or performance issues.
    
    Args:
        code: The source code to analyze
        language: Programming language (python, typescript, javascript, etc.)
        analysis_type: Type of analysis (quality, security, performance)
    
    Returns:
        Analysis results with issues and suggestions
    """
    from monkey_coder.analyzer import CodeAnalyzer
    analyzer = CodeAnalyzer()
    return await analyzer.analyze(code, language, analysis_type)


@mcp.tool()
async def generate_code(
    prompt: str,
    language: str = "python",
    context: str | None = None
) -> dict:
    """Generate code based on a natural language prompt.
    
    Args:
        prompt: Description of what code to generate
        language: Target programming language
        context: Optional existing code context
    
    Returns:
        Generated code with explanation
    """
    from monkey_coder.generator import CodeGenerator
    generator = CodeGenerator()
    return await generator.generate(prompt, language, context)


@mcp.tool()
async def generate_tests(
    code: str,
    language: str = "python",
    framework: str | None = None
) -> dict:
    """Generate unit tests for the provided code.
    
    Args:
        code: Source code to generate tests for
        language: Programming language
        framework: Test framework (pytest, jest, vitest, etc.)
    
    Returns:
        Generated test code
    """
    from monkey_coder.services.test_generator import TestGenerator
    generator = TestGenerator()
    return await generator.generate(code, language, framework)


@mcp.tool()
async def refactor_code(
    code: str,
    instructions: str,
    language: str = "python"
) -> dict:
    """Refactor code according to instructions.
    
    Args:
        code: Original source code
        instructions: Refactoring instructions
        language: Programming language
    
    Returns:
        Refactored code with diff
    """
    from monkey_coder.services.refactor import CodeRefactorer
    refactorer = CodeRefactorer()
    return await refactorer.refactor(code, instructions, language)


@mcp.tool()
async def explain_code(
    code: str,
    language: str = "python",
    detail_level: str = "medium"
) -> dict:
    """Explain what code does in natural language.
    
    Args:
        code: Source code to explain
        language: Programming language
        detail_level: Level of detail (brief, medium, detailed)
    
    Returns:
        Natural language explanation
    """
    from monkey_coder.services.explainer import CodeExplainer
    explainer = CodeExplainer()
    return await explainer.explain(code, language, detail_level)


# Resources for context
@mcp.resource("project://context")
async def get_project_context() -> str:
    """Get current project context and configuration."""
    import os
    import json
    
    context = {
        "project_name": "Monkey Coder",
        "version": "1.2.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "available_tools": [
            "analyze_code",
            "generate_code",
            "generate_tests",
            "refactor_code",
            "explain_code"
        ]
    }
    
    return json.dumps(context, indent=2)


@mcp.resource("project://status")
async def get_project_status() -> str:
    """Get current project status and health."""
    import json
    from datetime import datetime
    
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "mcp_version": "1.25.0",
        "tools_available": 5,
        "resources_available": 2
    }
    
    return json.dumps(status, indent=2)
