# Monkey Coder Installation & Usage Guide

## 🚀 Installation Options

### Option 1: Install CLI Globally (npm)

```bash
# Install the CLI globally
yarn global add monkey-coder-cli

# Or with npm
npm install -g monkey-coder-cli

# Verify installation
monkey --version
```

### Option 2: Install Python SDK (PyPI)

```bash
# Install the Python SDK
pip install monkey-coder-core

# Or with poetry
poetry add monkey-coder-core
```

### Option 3: Local Development Installation

```bash
# Clone the repository
git clone https://github.com/GaryOcean428/monkey-coder.git
cd monkey-coder

# Install dependencies
yarn install

# Build all packages
yarn build

# Link CLI globally for development
cd packages/cli
npm link

# Now you can use 'monkey' command globally
monkey --help
```

## 📦 Using the CLI

Once installed, you can use the `monkey` command globally:

### Basic Commands

```bash
# Get help
monkey --help

# Check version
monkey --version

# Authenticate (first time setup)
monkey auth login --email your@email.com --password yourpassword

# Or use API key directly
monkey auth login --api-key YOUR_API_KEY

# Check authentication status
monkey auth status
```

### Code Generation Commands

```bash
# Generate code
monkey implement "Create a React component for user authentication"

# Analyze existing code
monkey analyze "Review this function for security issues" --file ./src/auth.js

# Build a complete feature
monkey build "Create a REST API for todo management"

# Generate tests
monkey test "Generate unit tests for user service" --file ./src/userService.js

# Start interactive chat
monkey chat
```

### Advanced Options

```bash
# Use specific AI provider
monkey implement "Create a Python class" --provider anthropic

# Use specific model
monkey implement "Build a function" --model gpt-4.1

# Set maximum tokens
monkey implement "Complex task" --max-tokens 8000

# Use different persona
monkey implement "System design" --persona architect

# Enable streaming (when available)
monkey implement "Generate code" --stream

# Output to file
monkey implement "Create module" --output ./generated.py
```

## 🐍 Using the Python SDK

### Installation

```python
pip install monkey-coder-core
```

### Basic Usage

```python
from monkey_coder import MonkeyCoder

# Initialize the SDK
monkey = MonkeyCoder(api_key="YOUR_API_KEY")

# Generate code
result = await monkey.implement(
    prompt="Create a Python function to validate email addresses",
    provider="openai",
    model="gpt-4.1"
)

print(result.code)
```

### Advanced Usage

```python
import asyncio
from monkey_coder import MonkeyCoder
from monkey_coder.filesystem import read_file, write_file

async def main():
    # Initialize with configuration
    monkey = MonkeyCoder(
        api_key="YOUR_API_KEY",
        default_provider="openai",
        default_model="gpt-4.1"
    )
    
    # Generate a complete module
    result = await monkey.build(
        requirements="Create a task queue system with priority support",
        agent_type="architect"
    )
    
    # Save the generated code
    write_file("task_queue.py", result.code)
    
    # Analyze existing code
    existing_code = read_file("my_module.py")
    analysis = await monkey.analyze(
        code=existing_code,
        focus="security and performance"
    )
    
    print(analysis.recommendations)
    
    # Generate tests
    tests = await monkey.test(
        code=existing_code,
        framework="pytest"
    )
    
    write_file("test_my_module.py", tests.code)

asyncio.run(main())
```

### Using File Operations

The filesystem module that Monkey Coder generated for itself is also available:

```python
from monkey_coder.filesystem import (
    read_file,
    write_file,
    analyze_project_structure
)

# Read a file
content = read_file("src/main.py")

# Write a file with backup
write_file("output.py", generated_code, create_backup=True)

# Analyze project
structure = analyze_project_structure(".")
print(f"Project type: {structure['project_type']}")
print(f"Framework: {structure['framework']}")
```

### Using Different Agents

```python
from monkey_coder import MonkeyCoder

monkey = MonkeyCoder(api_key="YOUR_API_KEY")

# Developer agent for implementation
code = await monkey.execute_agent(
    agent_type="developer",
    prompt="Implement a binary search algorithm"
)

# Reviewer agent for code review
review = await monkey.execute_agent(
    agent_type="reviewer",
    prompt=f"Review this code:\n{code}"
)

# Architect agent for system design
design = await monkey.execute_agent(
    agent_type="architect",
    prompt="Design a microservices architecture for e-commerce"
)

# Security agent for vulnerability analysis
security = await monkey.execute_agent(
    agent_type="security",
    prompt=f"Check this code for vulnerabilities:\n{code}"
)
```

## 📚 TypeScript/JavaScript SDK

### Installation

```bash
yarn add monkey-coder-sdk
# or
npm install monkey-coder-sdk
```

### Usage

```typescript
import { MonkeyCoder } from 'monkey-coder-sdk';

// Initialize the SDK
const monkey = new MonkeyCoder({
  apiKey: 'YOUR_API_KEY',
  baseUrl: 'https://api.monkey-coder.com' // optional
});

// Generate code
const result = await monkey.implement({
  prompt: 'Create a TypeScript function to debounce API calls',
  provider: 'openai',
  model: 'gpt-4.1'
});

console.log(result.code);

// Analyze code
const analysis = await monkey.analyze({
  code: myCode,
  focus: 'performance'
});

// Stream responses
const stream = await monkey.implement({
  prompt: 'Create a complex system',
  stream: true
});

for await (const chunk of stream) {
  process.stdout.write(chunk);
}
```

## 🔧 Configuration

### CLI Configuration

The CLI stores configuration in `~/.monkey-coder/config.json`:

```json
{
  "apiKey": "YOUR_API_KEY",
  "defaultProvider": "openai",
  "defaultModel": "gpt-4.1",
  "defaultPersona": "developer"
}
```

### Environment Variables

You can also use environment variables:

```bash
export MONKEY_CODER_API_KEY="YOUR_API_KEY"
export OPENAI_API_KEY="YOUR_OPENAI_KEY"
export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_KEY"
```

## 🎯 Quick Start Examples

### 1. Generate a REST API

```bash
monkey build "Create a REST API for user management with authentication"
```

### 2. Improve Existing Code

```bash
monkey analyze "Improve this code for better performance" --file ./slow_function.py
```

### 3. Generate Tests

```bash
monkey test "Create comprehensive unit tests" --file ./my_module.py
```

### 4. Interactive Development

```bash
monkey chat
> Help me build a React component for data visualization
> Now add sorting functionality
> Generate tests for this component
```

## 📝 Publishing Status

- **CLI Package**: `monkey-coder-cli` v1.4.0 (ready to publish to npm)
- **Python SDK**: `monkey-coder-core` v1.1.1 (published to PyPI)
- **TypeScript SDK**: `monkey-coder-sdk` v1.0.0 (ready to publish)

## 🚦 Current Status

- ✅ Real AI Integration (OpenAI, Anthropic, Google, etc.)
- ✅ File Operations (generated by Monkey Coder itself!)
- ✅ Multi-Agent Orchestration
- ✅ Quantum-Inspired Routing
- 🚧 Streaming Support (in progress)
- 🚧 Context Management (in progress)

## 🤝 Support

- Documentation: https://docs.monkey-coder.com
- GitHub: https://github.com/GaryOcean428/monkey-coder
- Issues: https://github.com/GaryOcean428/monkey-coder/issues

## 🎉 Fun Fact

The filesystem module used by Monkey Coder was generated by Monkey Coder itself using GPT-4.1 - a true demonstration of self-improvement capability!
