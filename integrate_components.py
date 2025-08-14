#!/usr/bin/env python3
"""
Use Monkey Coder to generate integration code for all components.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
import sys
sys.path.insert(0, 'packages/core')

from monkey_coder.core.agent_executor import AgentExecutor
from monkey_coder.providers import ProviderRegistry
from monkey_coder.filesystem import write_file

# Load environment
env_path = Path('packages/core/.env.local')
if env_path.exists():
    load_dotenv(env_path)
    print(f'Loaded {env_path}')

async def generate_integration():
    """Use Monkey Coder to generate integration code."""
    registry = ProviderRegistry()
    await registry.initialize_all()
    executor = AgentExecutor(registry)
    
    print("=" * 60)
    print("MONKEY CODER GENERATING INTEGRATION CODE")
    print("=" * 60)
    
    # Generate integration endpoints
    result = await executor.execute_agent_task(
        agent_type='architect',
        prompt="""Create FastAPI endpoints that integrate the streaming, auth, and context management systems:

1. Streaming endpoint:
   - GET /v1/stream/{request_id}
   - Use EventSourceResponse from sse-starlette
   - Stream tokens from AI provider responses
   - Include proper error handling

2. Enhanced auth endpoints:
   - POST /v1/auth/login - Return JWT and API key
   - POST /v1/auth/refresh - Refresh JWT token
   - GET /v1/auth/status - Check auth status
   - POST /v1/auth/logout - Invalidate session

3. Context-aware execute endpoint:
   - POST /v1/execute - Existing endpoint
   - Add session_id parameter
   - Retrieve conversation context
   - Store response in context

4. Session management endpoints:
   - GET /v1/sessions - List user sessions
   - GET /v1/sessions/{session_id} - Get session history
   - DELETE /v1/sessions/{session_id} - Clear session

5. Integration code:
   - Import the generated modules
   - Add to FastAPI app routes
   - Include proper dependencies

Show the complete integration code for FastAPI main.py additions.
Focus on the endpoint definitions and router setup.""",
        provider='openai',
        model='gpt-4.1',
        max_tokens=3000
    )
    
    if result.get('status') == 'completed':
        code = result.get('output', '')
        
        # Extract Python code if wrapped in markdown
        if '```python' in code:
            start = code.find('```python') + 9
            end = code.find('```', start)
            if end > start:
                code = code[start:end].strip()
        
        # Save the integration code
        integration_path = Path('packages/core/monkey_coder/app/integration_endpoints.py')
        
        write_file(str(integration_path), code)
        print(f"\n✅ Generated integration endpoints: {integration_path}")
        print(f"   Size: {len(code)} bytes")
        
        return code
    else:
        raise Exception(f"Generation failed: {result.get('error')}")

async def main():
    try:
        code = await generate_integration()
        print("\n" + "=" * 60)
        print("SUCCESS! Monkey Coder has generated integration code!")
        print("=" * 60)
        
        # Show preview
        print("\nIntegration code preview:")
        print("-" * 40)
        lines = code.split('\n')[:40]
        for line in lines:
            print(line)
        if len(code.split('\n')) > 40:
            print("... (truncated)")
            
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("1. Add these endpoints to main.py")
        print("2. Test authentication flow")
        print("3. Test streaming responses")
        print("4. Deploy to production")
        print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())