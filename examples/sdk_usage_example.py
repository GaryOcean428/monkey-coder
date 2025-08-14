#!/usr/bin/env python3
"""
Example of using Monkey Coder as an installed SDK.

First install:
    pip install monkey-coder-core

Then run this script!
"""

import asyncio
import os
from pathlib import Path

# This is how you'd import after installing via pip
try:
    # If installed via pip
    from monkey_coder import MonkeyCoder
    from monkey_coder.filesystem import read_file, write_file, analyze_project_structure
except ImportError:
    # Fallback for local development
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / 'packages' / 'core'))
    from monkey_coder.core.agent_executor import AgentExecutor as MonkeyCoder
    from monkey_coder.filesystem import read_file, write_file, analyze_project_structure
    from monkey_coder.providers import ProviderRegistry
    from dotenv import load_dotenv
    
    # Load environment for local dev
    env_path = Path(__file__).parent.parent / 'packages' / 'core' / '.env.local'
    if env_path.exists():
        load_dotenv(env_path)


async def example_usage():
    """Example of using Monkey Coder SDK."""
    
    print("=" * 60)
    print("MONKEY CODER SDK EXAMPLE")
    print("=" * 60)
    
    # For installed version, you'd initialize like this:
    # monkey = MonkeyCoder(api_key="YOUR_API_KEY")
    
    # For local development:
    from monkey_coder.providers import ProviderRegistry
    registry = ProviderRegistry()
    await registry.initialize_all()
    monkey = MonkeyCoder(registry)
    
    # Example 1: Generate a function
    print("\n1. Generating a Python function...")
    result = await monkey.execute_agent_task(
        agent_type='developer',
        prompt="""Create a Python function that:
        1. Calculates compound interest
        2. Includes proper type hints
        3. Has comprehensive docstring
        4. Handles edge cases""",
        provider='openai',
        model='gpt-4.1',
        max_tokens=1500
    )
    
    if result['status'] == 'completed':
        code = result['output']
        print("✅ Generated code:")
        print("-" * 40)
        print(code[:500] + "..." if len(code) > 500 else code)
        
        # Save using the filesystem module
        write_file("generated_compound_interest.py", code)
        print("\n✅ Saved to generated_compound_interest.py")
    
    # Example 2: Analyze project structure
    print("\n2. Analyzing project structure...")
    structure = analyze_project_structure(".")
    print(f"✅ Project Analysis:")
    print(f"   Type: {structure['project_type']}")
    print(f"   Framework: {structure['framework']}")
    print(f"   Files: {len(structure['details']['files'])}")
    
    # Example 3: Code review
    print("\n3. Reviewing code...")
    sample_code = """
def calculate_average(numbers):
    total = 0
    for n in numbers:
        total += n
    return total / len(numbers)
"""
    
    review_result = await monkey.execute_agent_task(
        agent_type='reviewer',
        prompt=f"Review this code and suggest improvements:\n```python\n{sample_code}\n```",
        provider='anthropic',
        model='claude-3-5-sonnet-20241022',
        max_tokens=1000
    )
    
    if review_result['status'] == 'completed':
        print("✅ Code Review:")
        print("-" * 40)
        review = review_result['output']
        print(review[:500] + "..." if len(review) > 500 else review)
    
    # Example 4: Generate tests
    print("\n4. Generating tests...")
    test_result = await monkey.execute_agent_task(
        agent_type='tester',
        prompt=f"Generate pytest unit tests for:\n```python\n{sample_code}\n```",
        provider='openai',
        model='gpt-4.1',
        max_tokens=1000
    )
    
    if test_result['status'] == 'completed':
        tests = test_result['output']
        print("✅ Generated Tests:")
        print("-" * 40)
        print(tests[:500] + "..." if len(tests) > 500 else tests)
        
        write_file("test_generated.py", tests)
        print("\n✅ Saved tests to test_generated.py")
    
    print("\n" + "=" * 60)
    print("SDK EXAMPLE COMPLETE!")
    print("=" * 60)
    print("\nTo use this in your own projects:")
    print("1. Install: pip install monkey-coder-core")
    print("2. Import: from monkey_coder import MonkeyCoder")
    print("3. Initialize: monkey = MonkeyCoder(api_key='YOUR_KEY')")
    print("4. Use: result = await monkey.implement('your prompt')")


if __name__ == "__main__":
    asyncio.run(example_usage())