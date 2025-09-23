#!/usr/bin/env python3
"""
Simple A2A client example for quick testing

This script provides a simple command-line interface to test
individual skills of the Monkey-Coder A2A Agent.
"""

import asyncio
import argparse
from python_a2a import A2AClient


async def call_generate_code(spec, language="python", style="clean"):
    """Call the generate_code skill"""
    client = A2AClient(host="localhost", port=7702)
    await client.connect()
    
    try:
        result = await client.call_skill(
            skill_name="generate_code",
            parameters={
                "spec": spec,
                "context": {
                    "language": language,
                    "style": style
                }
            }
        )
        print("Generated Code:")
        print("-" * 40)
        print(result)
    finally:
        await client.disconnect()


async def call_analyze_repo(repo_path, analysis_type="comprehensive"):
    """Call the analyze_repo skill"""
    client = A2AClient(host="localhost", port=7702)
    await client.connect()
    
    try:
        result = await client.call_skill(
            skill_name="analyze_repo",
            parameters={
                "repo_path": repo_path,
                "analysis_type": analysis_type
            }
        )
        print("Repository Analysis:")
        print("-" * 40)
        print(result)
    finally:
        await client.disconnect()


async def call_run_tests(path, framework="auto"):
    """Call the run_tests skill"""
    client = A2AClient(host="localhost", port=7702)
    await client.connect()
    
    try:
        result = await client.call_skill(
            skill_name="run_tests",
            parameters={
                "path": path,
                "test_framework": framework
            }
        )
        print("Test Results:")
        print("-" * 40)
        print(result)
    finally:
        await client.disconnect()


def main():
    parser = argparse.ArgumentParser(
        description="Simple A2A client for Monkey-Coder Agent"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate code command
    gen_parser = subparsers.add_parser("generate", help="Generate code")
    gen_parser.add_argument("spec", help="Code specification")
    gen_parser.add_argument("--language", default="python", help="Programming language")
    gen_parser.add_argument("--style", default="clean", help="Code style")
    
    # Analyze repo command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze repository")
    analyze_parser.add_argument("path", help="Repository path")
    analyze_parser.add_argument("--type", dest="analysis_type", default="comprehensive",
                              choices=["structure", "issues", "improvements", "comprehensive"],
                              help="Analysis type")
    
    # Run tests command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("path", help="Test path")
    test_parser.add_argument("--framework", default="auto",
                           choices=["pytest", "unittest", "jest", "auto"],
                           help="Test framework")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        asyncio.run(call_generate_code(args.spec, args.language, args.style))
    elif args.command == "analyze":
        asyncio.run(call_analyze_repo(args.path, args.analysis_type))
    elif args.command == "test":
        asyncio.run(call_run_tests(args.path, args.framework))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()