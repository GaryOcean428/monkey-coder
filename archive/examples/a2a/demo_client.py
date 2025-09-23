#!/usr/bin/env python3
"""
Example A2A client for demonstrating Monkey-Coder Agent capabilities

This script shows how to interact with the Monkey-Coder A2A server
to generate code, analyze repositories, and run tests.
"""

import asyncio
import logging
import json
from python_a2a import A2AClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_code_generation():
    """Demonstrate code generation skill"""
    print("\n" + "="*50)
    print("🐒 CODE GENERATION DEMO")
    print("="*50)
    
    try:
        # Connect to Monkey-Coder A2A server
        client = A2AClient(host="localhost", port=7702)
        await client.connect()
        
        # Generate a Python function
        print("\n📝 Generating Python factorial function...")
        result = await client.call_skill(
            skill_name="generate_code",
            parameters={
                "spec": "Create a function that calculates the factorial of a number with error handling",
                "context": {
                    "language": "python",
                    "style": "clean",
                    "include_tests": True
                }
            }
        )
        
        print("✅ Generated code:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        
        # Generate a JavaScript function
        print("\n📝 Generating JavaScript validation function...")
        result = await client.call_skill(
            skill_name="generate_code",
            parameters={
                "spec": "Create a function that validates an email address using regex",
                "context": {
                    "language": "javascript",
                    "style": "modern",
                    "framework": "node.js"
                }
            }
        )
        
        print("✅ Generated code:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        
        await client.disconnect()
        
    except Exception as e:
        logger.error(f"Code generation demo failed: {e}")


async def demo_repo_analysis():
    """Demonstrate repository analysis skill"""
    print("\n" + "="*50)
    print("🔍 REPOSITORY ANALYSIS DEMO")
    print("="*50)
    
    try:
        # Connect to Monkey-Coder A2A server
        client = A2AClient(host="localhost", port=7702)
        await client.connect()
        
        # Analyze current repository structure
        print("\n📊 Analyzing repository structure...")
        result = await client.call_skill(
            skill_name="analyze_repo",
            parameters={
                "repo_path": ".",
                "analysis_type": "structure"
            }
        )
        
        print("✅ Structure Analysis:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        
        # Analyze for potential issues
        print("\n🔎 Analyzing for potential issues...")
        result = await client.call_skill(
            skill_name="analyze_repo",
            parameters={
                "repo_path": "./packages/core",
                "analysis_type": "issues"
            }
        )
        
        print("✅ Issues Analysis:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        
        # Get improvement suggestions
        print("\n💡 Getting improvement suggestions...")
        result = await client.call_skill(
            skill_name="analyze_repo",
            parameters={
                "repo_path": "./packages/core",
                "analysis_type": "improvements"
            }
        )
        
        print("✅ Improvement Suggestions:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        
        await client.disconnect()
        
    except Exception as e:
        logger.error(f"Repository analysis demo failed: {e}")


async def demo_test_execution():
    """Demonstrate test execution skill"""
    print("\n" + "="*50)
    print("🧪 TEST EXECUTION DEMO")
    print("="*50)
    
    try:
        # Connect to Monkey-Coder A2A server
        client = A2AClient(host="localhost", port=7702)
        await client.connect()
        
        # Run Python tests
        print("\n🐍 Running Python tests...")
        result = await client.call_skill(
            skill_name="run_tests",
            parameters={
                "path": "./packages/core/tests",
                "test_framework": "pytest",
                "options": {
                    "coverage": True,
                    "verbose": True
                }
            }
        )
        
        print("✅ Test Results:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        
        # Auto-detect and run tests
        print("\n🔍 Auto-detecting test framework...")
        result = await client.call_skill(
            skill_name="run_tests",
            parameters={
                "path": "./packages/core/tests/agents",
                "test_framework": "auto"
            }
        )
        
        print("✅ Auto-detected Test Results:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        
        await client.disconnect()
        
    except Exception as e:
        logger.error(f"Test execution demo failed: {e}")


async def demo_agent_discovery():
    """Demonstrate agent discovery and capabilities"""
    print("\n" + "="*50)
    print("🤖 AGENT DISCOVERY DEMO")
    print("="*50)
    
    try:
        # Get agent card via HTTP
        import httpx
        
        print("\n📋 Fetching agent card...")
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get("http://localhost:8000/.well-known/agent.json")
            
            if response.status_code == 200:
                agent_card = response.json()
                
                print("✅ Agent Card Retrieved:")
                print("-" * 40)
                print(f"Name: {agent_card.get('name')}")
                print(f"Version: {agent_card.get('version')}")
                print(f"Status: {agent_card.get('status')}")
                
                print("\nSkills:")
                for skill in agent_card.get('skills', []):
                    print(f"  • {skill['name']}: {skill['description']}")
                
                print("\nCapabilities:")
                for cap in agent_card.get('capabilities', []):
                    print(f"  • {cap}")
                
                a2a_server = agent_card.get('a2a_server', {})
                print(f"\nA2A Server: {a2a_server.get('status')} on port {a2a_server.get('port')}")
                
                if a2a_server.get('mcp_clients'):
                    print(f"MCP Clients: {', '.join(a2a_server['mcp_clients'])}")
                
                print("-" * 40)
            else:
                print(f"❌ Failed to fetch agent card: {response.status_code}")
        
    except Exception as e:
        logger.error(f"Agent discovery demo failed: {e}")


async def demo_complete_workflow():
    """Demonstrate a complete development workflow"""
    print("\n" + "="*50)
    print("🚀 COMPLETE WORKFLOW DEMO")
    print("="*50)
    
    try:
        # Connect to Monkey-Coder A2A server
        client = A2AClient(host="localhost", port=7702)
        await client.connect()
        
        # Step 1: Generate code
        print("\n📝 Step 1: Generate a utility function...")
        code_result = await client.call_skill(
            skill_name="generate_code",
            parameters={
                "spec": "Create a utility function that validates and formats phone numbers",
                "context": {
                    "language": "python",
                    "style": "comprehensive"
                }
            }
        )
        
        print("✅ Code generated successfully!")
        
        # Step 2: Analyze the generated code structure
        print("\n🔍 Step 2: Analyze repository after code generation...")
        analysis_result = await client.call_skill(
            skill_name="analyze_repo",
            parameters={
                "repo_path": ".",
                "analysis_type": "comprehensive"
            }
        )
        
        print("✅ Analysis completed successfully!")
        
        # Step 3: Run tests to verify everything works
        print("\n🧪 Step 3: Run tests to verify functionality...")
        test_result = await client.call_skill(
            skill_name="run_tests",
            parameters={
                "path": "./tests",
                "test_framework": "auto"
            }
        )
        
        print("✅ Tests executed successfully!")
        
        print("\n🎉 Complete workflow demonstration finished!")
        print("The Monkey-Coder Agent successfully:")
        print("  ✓ Generated code based on specification")
        print("  ✓ Analyzed repository structure and quality")
        print("  ✓ Executed tests to verify functionality")
        
        await client.disconnect()
        
    except Exception as e:
        logger.error(f"Complete workflow demo failed: {e}")


async def main():
    """Main demo function"""
    print("🐒 MONKEY-CODER A2A AGENT DEMONSTRATION")
    print("=" * 60)
    print("This demo showcases the capabilities of the Monkey-Coder A2A Agent")
    print("Make sure the Monkey-Coder server is running before starting!")
    print("=" * 60)
    
    # Run all demonstrations
    await demo_agent_discovery()
    await demo_code_generation()
    await demo_repo_analysis()
    await demo_test_execution()
    await demo_complete_workflow()
    
    print("\n🎯 DEMONSTRATION COMPLETE!")
    print("The Monkey-Coder A2A Agent is ready for production use.")


if __name__ == "__main__":
    asyncio.run(main())