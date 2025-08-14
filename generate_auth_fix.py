#!/usr/bin/env python3
"""
Use Monkey Coder to fix the CLI-Backend authentication flow.
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

async def generate_auth_fix():
    """Use Monkey Coder to fix authentication flow."""
    registry = ProviderRegistry()
    await registry.initialize_all()
    executor = AgentExecutor(registry)
    
    print("=" * 60)
    print("MONKEY CODER FIXING AUTHENTICATION FLOW")
    print("=" * 60)
    
    # Generate auth fix for FastAPI backend
    result = await executor.execute_agent_task(
        agent_type='developer',
        prompt="""Create a complete Python authentication module for FastAPI that properly handles CLI authentication with these requirements:

1. JWT token generation and validation:
   - Generate JWT tokens with proper expiration
   - Validate tokens in protected endpoints
   - Include user info in token payload

2. API key management:
   - Generate unique API keys for users
   - Store and validate API keys
   - Support both Bearer token and API key auth

3. Login endpoint:
   - POST /auth/login with email/password
   - Return JWT token and API key
   - Include user info in response

4. Session management:
   - Track active sessions
   - Support token refresh
   - Logout endpoint to invalidate tokens

5. Authentication middleware:
   - Verify JWT tokens in headers
   - Support API key in headers
   - Return proper 401/403 errors

Include all imports, security best practices, and make it production-ready.
Use python-jose for JWT, passlib for password hashing, and FastAPI security utilities.""",
        provider='openai',
        model='gpt-4.1',
        max_tokens=4000
    )
    
    if result.get('status') == 'completed':
        code = result.get('output', '')
        
        # Extract Python code if wrapped in markdown
        if '```python' in code:
            start = code.find('```python') + 9
            end = code.find('```', start)
            if end > start:
                code = code[start:end].strip()
        
        # Save the auth implementation
        auth_path = Path('packages/core/monkey_coder/auth/auth_handler.py')
        auth_path.parent.mkdir(parents=True, exist_ok=True)
        
        write_file(str(auth_path), code)
        print(f"\n✅ Generated auth handler: {auth_path}")
        print(f"   Size: {len(code)} bytes")
        
        return code
    else:
        raise Exception(f"Generation failed: {result.get('error')}")

async def main():
    try:
        code = await generate_auth_fix()
        print("\n" + "=" * 60)
        print("SUCCESS! Monkey Coder has fixed authentication!")
        print("=" * 60)
        
        # Show preview
        print("\nGenerated code preview:")
        print("-" * 40)
        lines = code.split('\n')[:30]
        for line in lines:
            print(line)
        if len(code.split('\n')) > 30:
            print("... (truncated)")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())