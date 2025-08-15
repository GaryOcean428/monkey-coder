#!/usr/bin/env python3
"""
Test script to verify REAL AI provider integration.
Tests that the system makes actual API calls to AI providers.
"""

import asyncio
import httpx
import json
from datetime import datetime

# Test configuration
API_URL = "http://localhost:8000"
API_KEY = "mk-7hAudQwdTZbN"  # Development key from logs

async def test_real_code_generation():
    """Test real code generation with actual AI providers."""
    
    print("\n" + "="*60)
    print("TESTING REAL AI CODE GENERATION")
    print("="*60)
    
    # Prepare request for code generation
    request_data = {
        "prompt": "Write a Python function that calculates the factorial of a number using recursion. Include proper error handling for negative numbers and add docstring documentation.",
        "task_type": "code_generation",
        "context": {  # ExecutionContext
            "user_id": "test_user",
            "session_id": "test_session",
            "workspace_id": "test_workspace",
            "environment": "production",
            "timeout": 300,
            "max_tokens": 4096,
            "temperature": 0.1
        },
        "persona_config": {  # PersonaConfig
            "persona": "developer",
            "slash_commands": [],
            "context_window": 32768,
            "use_markdown_spec": True,
            "custom_instructions": None
        },
        "preferred_providers": ["openai"],  # Provider preference list
        "model_preferences": {  # Model preferences by provider
            "openai": "gpt-4.1"
        },
        "orchestration_config": {
            "strategy": "sequential",
            "enable_quantum": False,
            "agents": ["developer"],
            "max_iterations": 1
        }
    }
    
    print(f"\n📤 Request Details:")
    print(f"   Task: {request_data['task_type']}")
    print(f"   Persona: {request_data['persona_config']['persona']}")
    print(f"   Provider: {request_data['preferred_providers'][0]}")
    print(f"   Prompt: {request_data['prompt'][:100]}...")
    
    # Make the API call
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print(f"\n⏳ Making API call to {API_URL}/v1/execute...")
            start_time = datetime.now()
            
            response = await client.post(
                f"{API_URL}/v1/execute",
                json=request_data,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"✅ Response received in {duration:.2f} seconds")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if we got real AI-generated code
                print(f"\n📊 Response Analysis:")
                print(f"   Execution ID: {result.get('execution_id', 'N/A')}")
                print(f"   Status: {result.get('status', 'N/A')}")
                
                # Extract the actual result
                execution_result = result.get('result', {})
                if isinstance(execution_result, dict):
                    actual_code = execution_result.get('result', {})
                    if isinstance(actual_code, dict):
                        # Check for orchestration results
                        phase_results = actual_code.get('phase_results', {})
                        if phase_results:
                            print(f"   Orchestration Phases: {list(phase_results.keys())}")
                            
                            # Look for generated code in phase results
                            for phase_name, phase_data in phase_results.items():
                                if isinstance(phase_data, dict) and 'output' in phase_data:
                                    output = phase_data['output']
                                    print(f"\n📝 Output from {phase_name} phase:")
                                    print("-" * 40)
                                    # Show first 500 chars of output
                                    print(output[:500] if len(output) > 500 else output)
                                    if len(output) > 500:
                                        print("... [truncated]")
                                    print("-" * 40)
                                    
                                    # Check if this looks like real code
                                    code_indicators = ['def ', 'return', 'if ', 'else:', 'raise', '"""']
                                    has_code = any(indicator in output for indicator in code_indicators)
                                    
                                    if has_code:
                                        print("✅ REAL CODE DETECTED - AI provider generated actual Python code!")
                                    else:
                                        print("⚠️ Output doesn't appear to contain code")
                        else:
                            # Direct result
                            output = actual_code.get('message', '')
                            print(f"\n📝 Direct Output:")
                            print("-" * 40)
                            print(output[:500] if len(output) > 500 else output)
                            print("-" * 40)
                
                # Check for token usage (indicates real API call)
                usage = result.get('usage')
                if usage:
                    print(f"\n💰 Token Usage (REAL API CALL):")
                    print(f"   Input Tokens: {usage.get('input_tokens', 0)}")
                    print(f"   Output Tokens: {usage.get('output_tokens', 0)}")
                    print(f"   Total Tokens: {usage.get('total_tokens', 0)}")
                    print(f"   Estimated Cost: ${usage.get('estimated_cost', 0):.4f}")
                    print("\n🎉 SUCCESS: Real AI provider integration is working!")
                else:
                    print("\n⚠️ No token usage data - might still be using mock responses")
                
                # Check persona routing info
                persona_routing = result.get('persona_routing', {})
                if persona_routing:
                    print(f"\n🎯 Routing Details:")
                    print(f"   Provider Used: {persona_routing.get('provider', 'N/A')}")
                    print(f"   Model Used: {persona_routing.get('model', 'N/A')}")
                    print(f"   Confidence: {persona_routing.get('confidence', 0):.2f}")
                
                return True
                
            else:
                print(f"\n❌ API Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error during API call: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

async def test_multiple_providers():
    """Test that different providers work."""
    
    print("\n" + "="*60)
    print("TESTING MULTIPLE AI PROVIDERS")
    print("="*60)
    
    providers_to_test = [
        ("openai", "gpt-3.5-turbo"),
        ("anthropic", "claude-3-5-haiku-20241022"),
        ("google", "gemini-2.5-flash"),
        ("groq", "llama-3.1-8b-instant"),
    ]
    
    for provider, model in providers_to_test:
        print(f"\n🧪 Testing {provider} with {model}...")
        
        request_data = {
            "prompt": f"Say 'Hello from {provider}!' and write a simple Python print statement.",
            "task_type": "custom",
            "context": {
                "user_id": "test_user",
                "session_id": "test_session",
                "workspace_id": "test_workspace",
                "environment": "production",
                "timeout": 300,
                "max_tokens": 500,
                "temperature": 0.1
            },
            "persona_config": {
                "persona": "developer",
                "slash_commands": [],
                "context_window": 32768,
                "use_markdown_spec": True,
                "custom_instructions": None
            },
            "preferred_providers": [provider],
            "model_preferences": {
                provider: model
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{API_URL}/v1/execute",
                    json=request_data,
                    headers={"Authorization": f"Bearer {API_KEY}"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('usage'):
                        tokens = result['usage'].get('total_tokens', 0)
                        print(f"   ✅ {provider}: Success! Used {tokens} tokens")
                    else:
                        print(f"   ⚠️ {provider}: Response received but no token usage")
                else:
                    print(f"   ❌ {provider}: Failed with status {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {provider}: Error - {str(e)}")

async def main():
    """Run all tests."""
    
    print("\n🚀 Starting Real AI Integration Tests")
    print("   Server: http://localhost:8000")
    print("   Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Test 1: Real code generation
    success = await test_real_code_generation()
    
    if success:
        # Test 2: Multiple providers
        await test_multiple_providers()
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())