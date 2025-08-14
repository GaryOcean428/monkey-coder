#!/usr/bin/env python3
"""
Use Monkey Coder to fix Railway deployment issues.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
import sys
sys.path.insert(0, 'packages/core')

from monkey_coder.core.agent_executor import AgentExecutor
from monkey_coder.providers import ProviderRegistry
from monkey_coder.filesystem import write_file, read_file

# Load environment
env_path = Path('packages/core/.env.local')
if env_path.exists():
    load_dotenv(env_path)
    print(f'Loaded {env_path}')

async def fix_railway_deployment():
    """Use Monkey Coder to fix Railway deployment."""
    registry = ProviderRegistry()
    await registry.initialize_all()
    executor = AgentExecutor(registry)
    
    print("=" * 60)
    print("MONKEY CODER FIXING RAILWAY DEPLOYMENT")
    print("=" * 60)
    
    # Read the error log
    error_log = """
    The build is failing with:
    - pip: command not found
    - Railway is using nixpacks auto-detection instead of railpack.json steps
    - The build command runs: cd packages/web && yarn install && yarn build && cd ../../ && pip install -r requirements.txt
    - This fails because pip is not available in the Node.js container
    
    Current railpack.json has separate python and web steps but Railway is ignoring them.
    """
    
    # Get Monkey Coder to fix it
    result = await executor.execute_agent_task(
        agent_type='devops',
        prompt=f"""Fix this Railway deployment issue. The problem is Railway is using nixpacks auto-detection and ignoring our railpack.json steps configuration.

ERROR: {error_log}

The issue is that Railway is not respecting the multi-step build process in railpack.json. It's trying to run pip in a Node.js container.

Create a fixed railpack.json that:
1. Forces Railway to use the railpack build system, not nixpacks auto-detection
2. Properly separates Python and Node.js build steps
3. Uses a multi-stage approach with proper base images
4. Ensures pip is available when needed
5. Must be compatible with Railway's railpack specification

The railpack.json must:
- Use proper "steps" configuration with separate python and web builds
- Use "deploy" section that combines both outputs
- Ensure Python environment is available for the start command
- Be syntactically valid JSON without comments

Focus on making Railway respect the multi-step build process.""",
        provider='openai',
        model='gpt-4.1',
        max_tokens=3000
    )
    
    if result.get('status') == 'completed':
        solution = result.get('output', '')
        
        # Extract the fixed railpack.json
        if '```json' in solution:
            start = solution.find('```json') + 7
            end = solution.find('```', start)
            if end > start:
                fixed_json = solution[start:end].strip()
                
                # Save the fixed railpack.json
                write_file('railpack.json', fixed_json)
                print(f"\n✅ Fixed railpack.json created")
        
        print("\n" + "=" * 60)
        print("SOLUTION:")
        print("=" * 60)
        print(solution)
        
        return solution
    else:
        raise Exception(f"Fix failed: {result.get('error')}")

async def main():
    try:
        solution = await fix_railway_deployment()
        
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("1. Review the fixed railpack.json")
        print("2. Commit and push: git add railpack.json && git commit -m 'fix: Railway multi-step build' && git push")
        print("3. Monitor Railway build logs")
        print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())