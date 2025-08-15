#!/usr/bin/env python3
"""
Use Monkey Coder to implement the OpenAI adapter - simple strategy version.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import time

sys.path.insert(0, str(Path(__file__).parent / "packages" / "core"))
load_dotenv(".env.local")

from monkey_coder.providers import ProviderRegistry
from monkey_coder.models import ExecuteRequest, PersonaConfig, ExecutionContext, TaskType, PersonaType
from monkey_coder.core.orchestration_coordinator import OrchestrationCoordinator, OrchestrationStrategy


async def implement_openai_adapter():
    """Have Monkey Coder implement the OpenAI adapter for unified SDK."""
    
    print("\n" + "="*80)
    print("🐵 MONKEY CODER: Implementing OpenAI Adapter (Simple Strategy)")
    print("="*80)
    
    # Initialize system
    print("\n📦 Initializing Monkey Coder...")
    registry = ProviderRegistry()
    await registry.initialize_all()
    
    # Use OrchestrationCoordinator directly with simple strategy
    coordinator = OrchestrationCoordinator(provider_registry=registry)
    
    # Create the implementation task
    prompt = """
You are implementing the OpenAI adapter for the Monkey Coder Unified AI SDK.

CONTEXT:
- Base interface is already defined in packages/sdk/unified/base.py
- This adapter should implement the UnifiedProvider interface for OpenAI
- Location: packages/sdk/unified/openai_adapter.py

REQUIREMENTS:
1. Import the base classes from base.py
2. Implement all abstract methods (complete, stream, health_check)
3. Use the official OpenAI Python SDK
4. Handle errors gracefully with proper exceptions
5. Map OpenAI-specific response format to UnifiedResponse
6. Support both streaming and non-streaming responses
7. Include comprehensive logging

IMPLEMENTATION:
Create a production-ready OpenAI adapter that:
- Initializes with API key
- Handles model selection (gpt-4, gpt-3.5-turbo, etc.)
- Properly maps messages format
- Implements token counting
- Handles rate limiting and retries
- Provides detailed error messages

Generate the complete openai_adapter.py file with all necessary imports, error handling, and documentation.
"""
    
    request = ExecuteRequest(
        prompt=prompt,
        task_type=TaskType.CODE_GENERATION,
        persona="developer",
        context=ExecutionContext(
            user_id="monkey_openai_adapter",
            project_path="/home/braden/Desktop/Dev/m-cli/monkey-coder",
            language="python"
        ),
        persona_config=PersonaConfig(
            persona="developer",
            confidence_threshold=0.8
        )
    )
    
    print("\n🚀 Executing OpenAI adapter implementation...")
    start_time = time.time()
    
    try:
        # Use simple strategy explicitly
        response = await coordinator.coordinate_execution(
            request=request,
            strategy_hint=OrchestrationStrategy.SIMPLE
        )
        
        execution_time = time.time() - start_time
        
        # Convert response
        if hasattr(response, 'model_dump'):
            result = response.model_dump()
        else:
            result = response
        
        if result and result.get("status") == "completed":
            print(f"\n✅ Implementation completed in {execution_time:.2f}s")
            
            # Extract code
            code_result = None
            if result.get("result"):
                if isinstance(result["result"], dict):
                    code_result = result["result"].get("result", {}).get("code", "")
                else:
                    code_result = str(result["result"])
            
            if code_result and ("class " in code_result or "import " in code_result):
                # Extract Python code from markdown if present
                if "```python" in code_result:
                    code_parts = code_result.split("```python")
                    if len(code_parts) > 1:
                        code_only = code_parts[1].split("```")[0]
                    else:
                        code_only = code_result
                else:
                    code_only = code_result
                
                # Save to file
                adapter_file = Path("/home/braden/Desktop/Dev/m-cli/monkey-coder/packages/sdk/unified/openai_adapter.py")
                adapter_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Fix escaped newlines if present
                code_only = code_only.replace('\\n', '\n')
                
                with open(adapter_file, "w") as f:
                    f.write(code_only.strip())
                
                print(f"✅ Saved OpenAI adapter to: {adapter_file}")
                
                # Show preview
                print("\n📄 Generated Code Preview (first 50 lines):")
                print("-"*80)
                lines = code_only.strip().split('\n')[:50]
                for i, line in enumerate(lines, 1):
                    print(f"{i:3} | {line}")
                if len(code_only.strip().split('\n')) > 50:
                    print("... [truncated]")
                print("-"*80)
                
                return True
            else:
                print("⚠️ Response doesn't contain implementation")
                print(f"Result type: {type(code_result)}")
                print(f"Result preview: {str(code_result)[:500] if code_result else 'No result'}")
                return False
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await registry.cleanup_all()


async def test_adapter():
    """Test the generated OpenAI adapter."""
    print("\n" + "="*80)
    print("🧪 Testing Generated OpenAI Adapter")
    print("="*80)
    
    adapter_file = Path("/home/braden/Desktop/Dev/m-cli/monkey-coder/packages/sdk/unified/openai_adapter.py")
    
    if not adapter_file.exists():
        print("❌ Adapter file not found")
        return False
    
    try:
        # Try to import
        sys.path.insert(0, str(adapter_file.parent.parent))
        from unified.openai_adapter import OpenAIAdapter
        from unified.base import UnifiedRequest
        
        print("✅ Successfully imported OpenAIAdapter")
        
        # Basic instantiation test
        adapter = OpenAIAdapter(api_key=os.getenv("OPENAI_API_KEY"))
        print("✅ Created OpenAIAdapter instance")
        
        # Test health check
        health = await adapter.health_check()
        print(f"✅ Health check: {health}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


async def main():
    """Main orchestrator."""
    print("🐵 Monkey Coder: OpenAI Adapter Implementation (Simple Strategy)")
    print("="*80)
    
    # Implement adapter
    success = await implement_openai_adapter()
    
    if success:
        # Test it
        await asyncio.sleep(1)
        test_success = await test_adapter()
        
        if test_success:
            print("\n🎉 SUCCESS: OpenAI adapter fully implemented and tested!")
        else:
            print("\n⚠️ Adapter needs refinement")
    else:
        print("\n❌ Failed to generate adapter")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)