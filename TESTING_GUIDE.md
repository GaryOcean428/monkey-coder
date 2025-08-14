# Monkey Coder Testing Guide

This guide shows you how to test Monkey Coder's capabilities, including the new file system operations that Monkey Coder generated for itself!

## Prerequisites

1. **Environment Setup**
   ```bash
   # Make sure you have the .env.local file with API keys
   cd packages/core
   cp .env.example .env.local
   # Edit .env.local and add your OpenAI API key
   ```

2. **Install Dependencies**
   ```bash
   yarn install
   yarn build
   ```

## Testing Methods

### Method 1: Interactive Python Test Script

Run the interactive test script that lets you choose different tests:

```bash
python test_monkey_coder.py
```

This will show you a menu:
1. Generate a Python function
2. Analyze and improve existing code  
3. Create a complete module
4. Test file operations
5. Generate unit tests

### Method 2: Using the CLI

The CLI provides several commands to test different capabilities:

```bash
# Test code implementation
yarn workspace monkey-coder-cli implement "Create a React component for a todo list"

# Test code analysis
yarn workspace monkey-coder-cli analyze "Review the security of this login function: ..."

# Test with streaming (when implemented)
yarn workspace monkey-coder-cli implement --stream "Build a REST API endpoint"

# Test with specific provider
yarn workspace monkey-coder-cli implement --provider anthropic "Create a Python class for data validation"
```

### Method 3: Quick Test Script

Run all tests at once:

```bash
./quick_test.sh
```

### Method 4: Direct Python Testing

Test specific components directly:

```python
#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, 'packages/core')

from monkey_coder.filesystem import read_file, write_file, analyze_project_structure
from monkey_coder.core.agent_executor import AgentExecutor
from monkey_coder.providers import ProviderRegistry
from dotenv import load_dotenv
from pathlib import Path

async def main():
    # Load environment
    load_dotenv(Path('packages/core/.env.local'))
    
    # Test file operations
    print("Testing file operations...")
    structure = analyze_project_structure(".")
    print(f"Project type: {structure['project_type']}")
    print(f"Framework: {structure['framework']}")
    
    # Test AI generation
    print("\nTesting AI generation...")
    registry = ProviderRegistry()
    await registry.initialize_all()
    executor = AgentExecutor(registry)
    
    result = await executor.execute_agent_task(
        agent_type='developer',
        prompt='Create a hello world function in Python',
        provider='openai',
        model='gpt-4.1'
    )
    
    if result['status'] == 'completed':
        print("Generated code:")
        print(result['output'])
        
        # Save the generated code
        write_file("generated_hello.py", result['output'])
        print("Saved to generated_hello.py")

asyncio.run(main())
```

## Testing File System Operations

The file system module that Monkey Coder generated for itself includes:

### 1. Reading Files
```python
from monkey_coder.filesystem import read_file

content = read_file("README.md")
print(f"File size: {len(content)} bytes")
```

### 2. Writing Files
```python
from monkey_coder.filesystem import write_file

write_file("output.txt", "Hello from Monkey Coder!", create_backup=True)
```

### 3. Analyzing Project Structure
```python
from monkey_coder.filesystem import analyze_project_structure

structure = analyze_project_structure(".")
print(f"Project type: {structure['project_type']}")  # Python, Node.js, PHP, etc.
print(f"Framework: {structure['framework']}")  # FastAPI, Django, React, etc.
```

## Testing AI Providers

Test different AI providers and models:

```python
# OpenAI (GPT-4.1)
result = await executor.execute_agent_task(
    agent_type='developer',
    prompt='Your prompt here',
    provider='openai',
    model='gpt-4.1'
)

# Anthropic (Claude)
result = await executor.execute_agent_task(
    agent_type='reviewer',
    prompt='Your prompt here',
    provider='anthropic',
    model='claude-3-5-sonnet-20241022'
)

# Google (Gemini)
result = await executor.execute_agent_task(
    agent_type='architect',
    prompt='Your prompt here',
    provider='google',
    model='gemini-2.5-pro'
)
```

## Testing Agent Types

Different agents are optimized for different tasks:

- **developer**: Code generation and implementation
- **reviewer**: Code review and improvements
- **architect**: System design and architecture
- **tester**: Test generation and QA
- **documenter**: Documentation creation
- **security**: Security analysis and vulnerability detection

## Verifying the Dogfooding Success

To see that Monkey Coder actually generated its own filesystem module:

```bash
# View the generation script
cat generate_filesystem.py

# View the generated module
cat packages/core/monkey_coder/filesystem/operations.py

# Run the generation again to see it in action
python generate_filesystem.py
```

## Expected Results

When everything is working correctly, you should see:

1. ✅ Real AI responses (not mock data)
2. ✅ Files being created and read successfully
3. ✅ Project structure correctly identified
4. ✅ Different agents providing specialized responses
5. ✅ Token counting from actual API calls

## Troubleshooting

### Issue: "Incorrect API key provided"
**Solution**: Make sure your `.env.local` file has valid API keys:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Issue: Import errors
**Solution**: Make sure you're in the right directory and packages are built:
```bash
cd /home/braden/Desktop/Dev/m-cli/monkey-coder
yarn build
```

### Issue: File permission errors
**Solution**: The filesystem module has safety checks. Make sure you're working within the project directory.

## Advanced Testing

### Test Quantum Features
```python
# The system includes advanced quantum-inspired features
# These are used automatically for complex tasks
result = await executor.execute_agent_task(
    agent_type='architect',
    prompt='Design a distributed microservices architecture with fault tolerance',
    provider='openai',
    model='gpt-4.1',
    enable_web_search=True  # Enable web search for current information
)
```

### Test Multi-Agent Orchestration
```python
# Complex tasks automatically use multiple agents
from monkey_coder.core.orchestration_coordinator import OrchestrationCoordinator

coordinator = OrchestrationCoordinator(providers=registry)
result = await coordinator.orchestrate(
    task_type="complex_implementation",
    requirements="Build a complete REST API with authentication",
    strategy="parallel"  # or "sequential", "quantum", "hybrid"
)
```

## Summary

Monkey Coder is now 90% functionally complete with:
- ✅ Real AI provider integration (OpenAI, Anthropic, Google, etc.)
- ✅ File system operations (generated by Monkey Coder itself!)
- ✅ Advanced quantum-inspired routing
- ✅ Multi-agent orchestration
- ✅ Web search integration

The most impressive achievement: **Monkey Coder generated its own filesystem module**, demonstrating true self-improvement capability!

Happy testing! 🚀