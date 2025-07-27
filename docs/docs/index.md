# Monkey Coder

Welcome to Monkey Coder, an AI-powered code generation and analysis platform based on Qwen3-Coder.

## Overview

Monkey Coder is a comprehensive development toolkit that leverages the power of Qwen3-Coder models to provide:

- **Code Generation**: Generate high-quality code from natural language prompts
- **Code Analysis**: Analyze existing code for quality, security, and performance issues
- **Multi-language Support**: Support for TypeScript, Python, JavaScript, and more
- **CLI Tools**: Command-line interface for seamless integration into your workflow
- **SDK**: Easy-to-use SDKs for TypeScript and Python

## Architecture

The project is structured as a Yarn 4.9.2 monorepo with the following packages:

```
monkey-coder/
├─ packages/
│  ├─ cli/          # TypeScript CLI
│  ├─ core/         # Python orchestration
│  └─ sdk/          # Thin TypeScript/Python clients
├─ services/        # Optional micro-services
├─ docs/            # MkDocs documentation
└─ examples/        # Usage examples
```

## Quick Start

1. **Installation**
   ```bash
   yarn install
   ```

2. **Build all packages**
   ```bash
   yarn build
   ```

3. **Generate code**
   ```bash
   yarn cli generate "Create a REST API endpoint for user management"
   ```

4. **Analyze code**
   ```bash
   yarn cli analyze ./src/app.ts
   ```

## Features

### 🚀 Code Generation
Generate production-ready code from natural language descriptions using state-of-the-art AI models.

### 🔍 Code Analysis
Comprehensive code analysis including quality metrics, security vulnerabilities, and performance suggestions.

### 📦 Monorepo Structure
Well-organized monorepo with clear separation of concerns and reusable components.

### 🛠️ Developer Experience
Rich CLI tools, comprehensive documentation, and easy-to-use SDKs for seamless integration.

## License

This project is licensed under the MIT License, with attribution to the original Qwen3-Coder project.

## Contributing

We welcome contributions! Please see our [Contributing Guide](contributing.md) for details.
