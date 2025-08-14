#!/usr/bin/env python3
"""
Use Monkey Coder to debug and fix Railway deployment issues.
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

async def debug_deployment():
    """Use Monkey Coder to debug Railway deployment."""
    registry = ProviderRegistry()
    await registry.initialize_all()
    executor = AgentExecutor(registry)
    
    print("=" * 60)
    print("MONKEY CODER DEBUGGING RAILWAY DEPLOYMENT")
    print("=" * 60)
    
    # Read current railpack.json
    railpack_content = read_file('railpack.json')
    
    # Analyze the error
    result = await executor.execute_agent_task(
        agent_type='devops',
        prompt=f"""Debug this Railway deployment failure. The build is failing with these errors:

ERROR OUTPUT:
```
runtime.goexit
/usr/local/go/src/runtime/asm_amd64.s:1700
github.com/moby/buildkit/solver.(*edge).execOp
/src/solver/edge.go:966
```

This appears to be a BuildKit/Docker build failure during the railpack build process.

Current railpack.json:
```json
{railpack_content}
```

The error suggests the build process is failing during execution. Common issues:
1. Missing files or directories referenced in inputs
2. Commands failing due to missing dependencies
3. Memory or resource constraints
4. Syntax errors in railpack.json
5. Incompatible Docker image versions

Please provide:
1. A fixed railpack.json that addresses potential issues
2. Any additional files needed for the build
3. Explanation of what was wrong

Focus on:
- Ensuring all input paths exist
- Using correct Docker base images
- Proper command execution order
- Resource allocation
- Syntax validation""",
        provider='openai',
        model='gpt-4.1',
        max_tokens=4000
    )
    
    if result.get('status') == 'completed':
        solution = result.get('output', '')
        
        # Extract the fixed railpack.json if present
        if '```json' in solution:
            start = solution.find('```json') + 7
            end = solution.find('```', start)
            if end > start:
                fixed_json = solution[start:end].strip()
                
                # Save the fixed railpack.json
                backup_path = 'railpack.json.backup'
                write_file(backup_path, railpack_content)
                write_file('railpack.json', fixed_json)
                print(f"\n✅ Saved fixed railpack.json (backup at {backup_path})")
        
        print("\n" + "=" * 60)
        print("DIAGNOSIS AND SOLUTION:")
        print("=" * 60)
        print(solution)
        
        return solution
    else:
        raise Exception(f"Debug failed: {result.get('error')}")

async def create_missing_files():
    """Create any missing files needed for deployment."""
    executor = AgentExecutor(ProviderRegistry())
    
    # Check if requirements.txt exists at root
    if not Path('requirements.txt').exists():
        print("\n⚠️ Missing requirements.txt at root, creating...")
        
        result = await executor.execute_agent_task(
            agent_type='devops',
            prompt="""Create a requirements.txt file for the Railway deployment that includes:
1. All dependencies from packages/core/requirements.txt
2. Additional deployment dependencies like uvicorn
3. Proper versions for production stability

Base it on typical FastAPI deployment requirements.""",
            provider='openai',
            model='gpt-4.1',
            max_tokens=1000
        )
        
        if result.get('status') == 'completed':
            content = result.get('output', '')
            if 'fastapi' in content.lower():
                write_file('requirements.txt', content)
                print("✅ Created requirements.txt")

async def main():
    try:
        # Debug the deployment
        solution = await debug_deployment()
        
        # Create missing files
        await create_missing_files()
        
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("1. Review the changes to railpack.json")
        print("2. Commit and push: git add -A && git commit -m 'fix: Railway deployment issues' && git push")
        print("3. Monitor Railway build logs")
        print("4. If it still fails, run this script again with updated error messages")
        print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())