#!/usr/bin/env python3
"""
Test Monkey Coder's capabilities including file system operations.
Run this to see Monkey Coder in action!
"""

import asyncio
import sys
from pathlib import Path

# Add packages/core to path
sys.path.insert(0, 'packages/core')

from monkey_coder.core.agent_executor import AgentExecutor
from monkey_coder.providers import ProviderRegistry
from monkey_coder.filesystem import read_file, write_file, analyze_project_structure
from dotenv import load_dotenv

# Load environment
env_path = Path('packages/core/.env.local')
if env_path.exists():
    load_dotenv(env_path)
    print(f'✅ Loaded {env_path}')

async def test_monkey_coder():
    """Test different Monkey Coder capabilities."""
    
    print("=" * 60)
    print("MONKEY CODER TEST SUITE")
    print("=" * 60)
    
    # Initialize Monkey Coder
    registry = ProviderRegistry()
    await registry.initialize_all()
    executor = AgentExecutor(registry)
    
    # Test options
    print("\nChoose a test to run:")
    print("1. Generate a Python function")
    print("2. Analyze and improve existing code")
    print("3. Create a complete module")
    print("4. Test file operations")
    print("5. Generate unit tests")
    
    choice = "1"  # Default choice for automated testing
    
    if choice == "1":
        # Generate a Python function
        print("\n🚀 Generating a Python function...")
        result = await executor.execute_agent_task(
            agent_type='developer',
            prompt="""Create a Python function that:
1. Calculates the Fibonacci sequence
2. Uses memoization for optimization
3. Includes proper type hints and docstring
4. Handles edge cases""",
            provider='openai',
            model='gpt-4.1',
            max_tokens=1500
        )
        
        if result.get('status') == 'completed':
            code = result.get('output', '')
            print("\n✅ Generated code:")
            print("-" * 40)
            print(code)
            
            # Save to file
            write_file("generated_fibonacci.py", code)
            print("\n✅ Saved to generated_fibonacci.py")
    
    elif choice == "2":
        # Analyze and improve code
        test_code = '''
def calc(x, y, op):
    if op == "+":
        return x + y
    elif op == "-":
        return x - y
    elif op == "*":
        return x * y
    elif op == "/":
        return x / y
'''
        
        print("\n🔍 Analyzing and improving code...")
        print("Original code:")
        print(test_code)
        
        result = await executor.execute_agent_task(
            agent_type='reviewer',
            prompt=f"""Review and improve this code:

```python
{test_code}
```

Provide an improved version with:
1. Better naming
2. Error handling
3. Type hints
4. Documentation
5. More pythonic approach""",
            provider='anthropic',
            model='claude-3-5-sonnet-20241022',
            max_tokens=2000
        )
        
        if result.get('status') == 'completed':
            improved = result.get('output', '')
            print("\n✅ Improved code:")
            print("-" * 40)
            print(improved)
            
            write_file("improved_calculator.py", improved)
            print("\n✅ Saved to improved_calculator.py")
    
    elif choice == "3":
        # Create a complete module
        print("\n🏗️ Creating a complete module...")
        result = await executor.execute_agent_task(
            agent_type='architect',
            prompt="""Design and implement a simple task queue module with:
1. Task class with priority
2. Queue class with add/remove operations
3. Priority-based execution
4. Error handling
5. Async support
6. Complete with tests""",
            provider='openai',
            model='gpt-4.1',
            max_tokens=4000
        )
        
        if result.get('status') == 'completed':
            module_code = result.get('output', '')
            print("\n✅ Generated module:")
            print("-" * 40)
            print(module_code[:1000] + "..." if len(module_code) > 1000 else module_code)
            
            write_file("task_queue_module.py", module_code)
            print("\n✅ Saved to task_queue_module.py")
    
    elif choice == "4":
        # Test file operations
        print("\n📁 Testing file operations...")
        
        # Analyze project structure
        structure = analyze_project_structure(".")
        print(f"\nProject Analysis:")
        print(f"  Type: {structure['project_type']}")
        print(f"  Framework: {structure['framework']}")
        print(f"  Files: {len(structure['details']['files'])}")
        print(f"  Directories: {len(structure['details']['directories'])}")
        
        # Read a file
        readme_content = read_file("README.md")
        print(f"\n📄 README.md size: {len(readme_content)} bytes")
        print(f"   First line: {readme_content.split(chr(10))[0]}")
        
        # Write a test file
        test_content = """# Test File
Created by Monkey Coder file system test.
This demonstrates the file operations working correctly.
"""
        write_file("test_file_ops.md", test_content)
        print("\n✅ Created test_file_ops.md")
        
        # Read it back
        verify = read_file("test_file_ops.md")
        if verify == test_content:
            print("✅ Verified: File write/read working correctly!")
    
    elif choice == "5":
        # Generate unit tests
        print("\n🧪 Generating unit tests...")
        
        # First read an existing file to test
        sample_code = """
def add_numbers(a: int, b: int) -> int:
    return a + b

def multiply_numbers(a: float, b: float) -> float:
    return a * b

class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, value):
        self.result += value
        return self.result
"""
        
        result = await executor.execute_agent_task(
            agent_type='tester',
            prompt=f"""Generate comprehensive pytest unit tests for this code:

```python
{sample_code}
```

Include:
1. Edge cases
2. Error scenarios  
3. Fixtures if needed
4. Parametrized tests
5. Clear test names""",
            provider='openai',
            model='gpt-4.1',
            max_tokens=2000
        )
        
        if result.get('status') == 'completed':
            tests = result.get('output', '')
            print("\n✅ Generated tests:")
            print("-" * 40)
            print(tests)
            
            write_file("test_generated.py", tests)
            print("\n✅ Saved to test_generated.py")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_monkey_coder())
