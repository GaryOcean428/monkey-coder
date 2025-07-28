# Monkey Coder

```text
    🐵 
   /||\   
  / || \  
 /  ||  \ 
🍌 CODE 🍌
```

## AI-Powered Code Generation and Analysis Platform

![Monkey Coder Logo](assets/finalmonkey.png)

## Overview

Monkey Coder is a comprehensive AI-powered code generation and analysis platform designed to
enhance developer productivity with intelligent automation:

- 🚀 **TypeScript CLI** for seamless integration into your workflow
- 🐍 **Python Core** for AI model orchestration and processing
- 📦 **SDK Libraries** for easy integration into your applications
- 🛠️ **Monorepo Architecture** with yarn 4.9.2 workspaces
- 📚 **Comprehensive Documentation** with MkDocs
- 🤖 **Multi-Agent System** with MCP (Model Context Protocol) support
- 🔧 **Advanced Code Analysis** with security, performance, and quality insights

## Monorepo Structure

```text
monkey-coder/
├─ packages/
│  ├─ cli/              # TypeScript CLI tools
│  ├─ core/             # Python orchestration engine
│  └─ sdk/              # TypeScript/Python client SDKs
├─ services/            # Optional microservices
├─ docs/                # MkDocs documentation
├─ examples/            # Usage examples (from original repo)
├─ qwencoder-eval/      # Evaluation benchmarks (from original repo)
└─ demo/                # Demo applications (from original repo)
```

## Introduction

Monkey Coder is an advanced AI-powered development platform that brings intelligent code generation,
analysis, and multi-agent orchestration to your development workflow. Built with modern TypeScript
and Python architectures, Monkey Coder provides:

💻 **Intelligent Code Generation**: Generate high-quality code from natural language
descriptions across multiple programming languages

🔍 **Advanced Code Analysis**: Comprehensive analysis covering security vulnerabilities,
performance bottlenecks, and code quality metrics

🤖 **Multi-Agent Architecture**: Leverage multiple specialized AI agents working together to
solve complex development tasks

🔧 **Developer-First Tools**: CLI interfaces, SDK libraries, and integrations designed for
seamless workflow integration

## Key Features

1. ✨ **Multi-Language Support**: Generate and analyze code across popular programming
   languages including Python, TypeScript, JavaScript, Go, Rust, and more
2. ✨ **Context-Aware Analysis**: Understand your entire codebase context for more accurate
   suggestions and analysis
3. ✨ **MCP Integration**: Built-in Model Context Protocol support for advanced agent
   communication and task orchestration
4. ✨ **Enterprise Ready**: Comprehensive error tracking, authentication, and usage monitoring
   with Sentry integration

## Getting Started

### Prerequisites

- **Node.js** 18+ and **yarn** 4.9.2
- **Python** 3.8+ with pip
- **Git** for cloning and version control

### Package Installation

Our packages are now published and available for installation:

#### Python Packages (Published on PyPI)

```bash
# Install the core package with multi-agent and MCP support
pip install monkey-coder-core

# Install the Python SDK for API integration
pip install monkey-coder-sdk
```

### npm Package (Ready to Publish)

```bash
# Will be available after publishing
npm install -g monkey-coder-cli
```

### Development Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/GaryOcean428/monkey-coder.git
   cd monkey-coder
   ```

2. **Install dependencies**:

   ```bash
   yarn install
   ```

3. **Build all packages**:

   ```bash
   yarn build
   ```

## Published Packages

### 🐍 Python Packages

#### monkey-coder-core (v1.0.3)

- **PyPI**: [https://pypi.org/project/monkey-coder-core/1.0.3/](https://pypi.org/project/monkey-coder-core/1.0.3/)
- **Features**:
  - Multi-agent orchestration system
  - MCP (Model Context Protocol) integration
  - Quantum task execution framework
  - Built-in MCP servers (filesystem, GitHub, browser, database)
  - Model validation and compliance
  - Sentry error tracking

#### monkey-coder-sdk (v1.0.1)

- **PyPI**: [https://pypi.org/project/monkey-coder-sdk/1.0.1/](https://pypi.org/project/monkey-coder-sdk/1.0.1/)
- **Features**:
  - Python SDK for Monkey Coder API
  - Client authentication
  - API helpers and types
  - Request/response handling

### 📦 npm Package

#### monkey-coder-cli (v1.0.0)
- **Status**: Ready to publish
- **Features**:
  - Complete CLI interface
  - Authentication system (login/logout/status)
  - Usage tracking and billing
  - MCP server management commands
  - Streaming support
  - Interactive chat mode

### CLI Tools

The Monkey Coder CLI provides powerful commands for code generation and analysis:

#### Generate Code

```bash
# Generate TypeScript code
yarn cli generate "Create a REST API endpoint for user management" --language TypeScript

# Generate Python code with output file
yarn cli generate "Implement a binary search algorithm" --language Python --output search.py
```

#### Analyze Code

```bash
# Analyze code quality
yarn cli analyze ./src/app.ts --type quality

# Security analysis
yarn cli analyze ./src/app.ts --type security

# Performance analysis
yarn cli analyze ./src/app.ts --type performance
```

#### Available Commands

- `generate <prompt>` - Generate code from natural language
- `analyze <file>` - Analyze existing code
- `--help` - Show help information

### Splash Screen

The CLI now features a splash screen to enhance the user experience.

![Monkey Coder Splash](assets/splash.png)

This splash screen is enabled by default. To opt out, you can use one of the following methods:

- **Environment Variable**: Set `MONKEY_CODER_NO_SPLASH=1`
- **Command-Line Flag**: Use the `--no-splash` flag with any command.

### Using the SDK

#### TypeScript/JavaScript

```typescript
import { MonkeyCoderClient } from '@monkey-coder/sdk';

const client = new MonkeyCoderClient('http://localhost:8000');

// Generate code
const result = await client.generateCode({
  prompt: 'Create a React component',
  language: 'TypeScript',
});

console.log(result.code);
```

#### Python

```python
from monkey_coder_core import CodeGenerator

generator = CodeGenerator()
code = generator.generate('Create a Flask API endpoint')
print(code)
```

## Use Cases

Monkey Coder excels in various development scenarios:

### Code Generation

Generate high-quality code from natural language descriptions:

```bash
# Generate a REST API endpoint
monkey-coder generate "Create a FastAPI endpoint for user authentication with JWT tokens"

# Generate React components
monkey-coder generate "Create a responsive navigation component with mobile menu"

# Generate database models
monkey-coder generate "Create SQLAlchemy models for a blog with posts, users, and comments"
```

### Code Analysis

Comprehensive analysis of your codebase:

```bash
# Security analysis
monkey-coder analyze --type security ./src/

# Performance analysis  
monkey-coder analyze --type performance ./src/API/

# Code quality analysis
monkey-coder analyze --type quality ./src/components/
```

### Multi-Agent Orchestration

Leverage multiple AI agents for complex tasks:

```python
from monkey_coder_core import AgentOrchestrator

orchestrator = AgentOrchestrator()

# Deploy multiple agents for a complex refactoring task
result = orchestrator.coordinate_agents([
    "code_analyzer",
    "security_auditor", 
    "performance_optimizer"
], task="Optimize the user authentication system")
```

### MCP Integration

Seamless integration with Model Context Protocol:

```python
from monkey_coder_core import MCPClient

# Connect to MCP servers for enhanced capabilities
mcp_client = MCPClient()
mcp_client.connect("filesystem")
mcp_client.connect("GitHub")

# Use MCP for context-aware code generation
result = mcp_client.generate_with_context(
    prompt="Refactor this function",
    context={"file": "src/utils.py", "repository": "my-project"}
)
```

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=GaryOcean428/monkey-coder&type=Date)](https://star-history.com/#GaryOcean428/monkey-coder&Date)

## Citation

If you find Monkey Coder helpful in your work, please consider citing:

```bibtex
@software{monkey_coder,
  title={Monkey Coder: AI-Powered Code Generation and Analysis Platform},
  author={GaryOcean428},
  year={2025},
  url={https://github.com/GaryOcean428/monkey-coder},
  note={Open-source AI development toolkit}
}
```

## Contact Us

Have questions or want to contribute to Monkey Coder?

- 🐛 **Issues**: [GitHub Issues](https://github.com/GaryOcean428/monkey-coder/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/GaryOcean428/monkey-coder/discussions)
- 📧 **Email**: Contact the maintainers through GitHub

We welcome contributions, bug reports, and feature requests!

---

[↑ Back to Top ↑](#monkey-coder)
