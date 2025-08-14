#!/usr/bin/env python3
"""
Use Monkey Coder to fix the website display issue.
The backend API is showing at https://coder.fastmonkey.au/ instead of the frontend.
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

async def fix_website_display():
    """Use Monkey Coder to fix the website display issue."""
    registry = ProviderRegistry()
    await registry.initialize_all()
    executor = AgentExecutor(registry)
    
    print("=" * 60)
    print("MONKEY CODER: FIXING WEBSITE DISPLAY")
    print("=" * 60)
    
    # Read current railpack.json to understand deployment
    railpack_content = read_file('railpack.json')
    
    # Read the main FastAPI app to understand static file serving
    main_app_path = 'packages/core/monkey_coder/app/main.py'
    if Path(main_app_path).exists():
        main_app_content = read_file(main_app_path)
    else:
        main_app_content = "File not found"
    
    # Get Monkey Coder to analyze and fix the issue
    result = await executor.execute_agent_task(
        agent_type='devops',
        prompt=f"""Fix the website display issue at https://coder.fastmonkey.au/

PROBLEM:
- The main URL shows the backend API instead of the frontend website
- Users see FastAPI docs/API endpoints instead of the Next.js frontend
- The frontend should be displayed at the root URL

CURRENT CONFIGURATION:
railpack.json:
{railpack_content}

FastAPI main.py static serving (relevant parts):
{main_app_content[:2000]}...

REQUIREMENTS:
1. The Next.js frontend (packages/web) should be served at the root URL /
2. The API should be accessible at /api/* endpoints
3. FastAPI docs should be at /docs (not root)
4. Static assets must be properly served
5. Must work with Railway deployment using railpack.json

Generate the complete fix to:
1. Update FastAPI routing to serve frontend at root
2. Move API endpoints to /api prefix
3. Configure static file serving correctly
4. Update railpack.json if needed for proper frontend build
5. Ensure the Next.js build output is correctly served

Provide complete, production-ready code changes that fix this issue.""",
        provider='openai',
        model='gpt-4.1',
        max_tokens=4000
    )
    
    if result.get('status') == 'completed':
        solution = result.get('output', '')
        
        print("\n" + "=" * 60)
        print("SOLUTION:")
        print("=" * 60)
        print(solution)
        
        # Extract and save the fixes
        if '```python' in solution:
            # Extract Python code for FastAPI changes
            python_start = solution.find('```python')
            python_end = solution.find('```', python_start + 9)
            if python_end > python_start:
                python_code = solution[python_start + 9:python_end].strip()
                write_file('fix_fastapi_routing.py', python_code)
                print("\n✅ FastAPI routing fix saved to fix_fastapi_routing.py")
        
        if '```json' in solution:
            # Extract JSON for railpack updates
            json_start = solution.find('```json')
            json_end = solution.find('```', json_start + 7)
            if json_end > json_start:
                json_code = solution[json_start + 7:json_end].strip()
                write_file('railpack_frontend_fix.json', json_code)
                print("✅ Railpack fix saved to railpack_frontend_fix.json")
        
        return solution
    else:
        raise Exception(f"Fix failed: {result.get('error')}")

async def verify_static_files():
    """Verify that static files are built and in the right place."""
    print("\n" + "=" * 60)
    print("VERIFYING STATIC FILES:")
    print("=" * 60)
    
    # Check if Next.js build exists
    web_out_path = Path('packages/web/out')
    web_dist_path = Path('packages/web/.next')
    
    if web_out_path.exists():
        print(f"✅ Static export found at {web_out_path}")
        # List some files
        files = list(web_out_path.glob('*'))[:5]
        for f in files:
            print(f"   - {f.name}")
    else:
        print(f"❌ No static export at {web_out_path}")
        print("   Run: cd packages/web && yarn build && yarn export")
    
    if web_dist_path.exists():
        print(f"✅ Next.js build found at {web_dist_path}")
    else:
        print(f"⚠️  No Next.js build at {web_dist_path}")

async def main():
    try:
        # Verify static files first
        await verify_static_files()
        
        # Get Monkey Coder to fix the issue
        solution = await fix_website_display()
        
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("1. Review the generated fixes")
        print("2. Apply fix_fastapi_routing.py to packages/core/monkey_coder/app/main.py")
        print("3. Update railpack.json if needed")
        print("4. Ensure Next.js is built: cd packages/web && yarn build && yarn export")
        print("5. Commit and push: git add -A && git commit -m 'fix: Serve frontend at root URL' && git push")
        print("6. Monitor Railway deployment")
        print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())