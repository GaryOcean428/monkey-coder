---
id: migration-guide
title: Migration Guide - Qwen3-Coder to Monkey Coder
---

# Migration Guide: Qwen3-Coder to Monkey Coder

This guide will help you migrate from Qwen3-Coder to Monkey Coder, highlighting the key differences, improvements, and steps needed for a smooth transition.

## Overview

Monkey Coder is built on the foundation of Qwen3-Coder but extends it with additional features, better tooling, and improved user experience. The migration process is designed to be straightforward while providing enhanced capabilities.

## Key Differences

### Architecture Changes

| Aspect | Qwen3-Coder | Monkey Coder |
|--------|-------------|--------------|
| **Structure** | Single package | Monorepo with workspace support |
| **Package Manager** | npm/pip | Yarn 4.9.2 |
| **Language Support** | Python-first | TypeScript + Python |
| **CLI Interface** | Basic commands | Rich CLI with interactive features |
| **Documentation** | Markdown files | Interactive Docusaurus site |

### New Features in Monkey Coder

- **Quantum Tasks**: Advanced AI-powered development operations
- **WebContainer Integration**: Interactive code execution in docs
- **Enhanced Analysis**: Multi-dimensional code analysis
- **Team Collaboration**: Built-in collaboration features
- **API Gateway**: RESTful API for integrations
- **Usage Analytics**: Detailed usage tracking and insights

## Migration Steps

### 1. Environment Setup

First, ensure you have the required tools:

```bash
# Install Yarn 4.9.2 (if not already installed)
npm install -g yarn

# Verify version
yarn --version  # Should show 4.9.2 or higher
```

### 2. Project Structure Migration

If migrating an existing Qwen3-Coder project:

```bash
# Backup your existing project
cp -r qwen3-coder-project qwen3-coder-project-backup

# Clone Monkey Coder
git clone https://github.com/GaryOcean428/monkey-coder.git
cd monkey-coder

# Install dependencies
yarn install
```

### 3. Configuration Migration

#### API Keys and Environment Variables

Monkey Coder uses a unified environment configuration:

```bash
# .env (create this file)
MONKEY_CODER_API_KEY=your_api_key_here
QWEN_MODEL_PATH=./models/qwen3-coder
QUANTUM_ENABLED=true
ANALYTICS_ENABLED=true
```

#### Model Configuration

Update your model configuration:

```javascript
// monkey-coder.config.js
module.exports = {
  model: {
    name: 'qwen3-coder',
    version: 'latest',
    quantization: 'int8',
    maxTokens: 4096
  },
  quantum: {
    enabled: true,
    depth: 8,
    parallelProcessing: true
  },
  generation: {
    temperature: 0.7,
    topP: 0.9,
    maxLength: 2048
  }
};
```

### 4. Code Migration

#### Command Line Interface

Update your existing command usage:

```bash
# Qwen3-Coder (old)
python -m qwen3_coder generate "Create a function"
python -m qwen3_coder analyze file.py

# Monkey Coder (new)
yarn cli generate "Create a function"
yarn cli analyze file.py

# Or using the full path
./packages/cli/bin/monkey-coder generate "Create a function"
```

#### API Integration

If you were using the Python API directly:

```python
# Qwen3-Coder (old)
from qwen3_coder import QwenCoder

coder = QwenCoder(model_path='./models')
result = coder.generate("Create a REST API")
```

```typescript
// Monkey Coder (new)
import { MonkeyCoder } from '@monkey-coder/sdk';

const coder = new MonkeyCoder({
  apiKey: process.env.MONKEY_CODER_API_KEY
});

const result = await coder.generate("Create a REST API");
```

### 5. Advanced Features Migration

#### Quantum Tasks (New Feature)

Leverage new quantum computing capabilities:

```bash
# Generate optimized code using quantum algorithms
yarn cli quantum-generate --type="optimization" --prompt="Optimize database queries"

# Perform quantum analysis
yarn cli quantum-analyze --file="complex-algorithm.ts" --depth="maximum"
```

#### WebContainer Integration (New Feature)

Add interactive code execution to your documentation:

```jsx
import { MonkeyCoderREPL } from '@monkey-coder/web-container';

<MonkeyCoderREPL 
  language="typescript"
  initialCode="console.log('Hello from Monkey Coder!');"
  showConsole={true}
/>
```

## Breaking Changes

### Command Structure

- `qwen3-coder` → `yarn cli` or `monkey-coder`
- Model loading is now automatic
- Configuration files use different format

### API Endpoints

| Qwen3-Coder | Monkey Coder |
|-------------|--------------|
| `/api/generate` | `/api/v1/generate` |
| `/api/analyze` | `/api/v1/analyze` |
| N/A | `/api/v1/quantum/generate` |
| N/A | `/api/v1/quantum/analyze` |

### Dependencies

Remove old Qwen3-Coder dependencies and use Monkey Coder packages:

```json
// package.json - Remove these
{
  "dependencies": {
    "qwen3-coder": "^1.0.0",
    "qwen-tokenizer": "^0.5.0"
  }
}

// package.json - Add these
{
  "dependencies": {
    "@monkey-coder/sdk": "^1.0.0",
    "@monkey-coder/cli": "^1.0.0"
  }
}
```

## Testing Your Migration

After migration, verify everything works:

```bash
# Test basic generation
yarn cli generate "Create a simple function"

# Test analysis
yarn cli analyze ./src/example.ts

# Test quantum features
yarn cli quantum-generate --type="optimization" --prompt="Optimize this algorithm"

# Run the development server
yarn dev
```

## Troubleshooting

### Common Issues

1. **Yarn version mismatch**: Ensure you're using Yarn 4.9.2
2. **Missing API keys**: Check your `.env` file configuration
3. **Model loading errors**: Verify model paths in configuration
4. **Port conflicts**: Check if ports 3000-3002 are available

### Getting Help

- **Documentation**: Check our comprehensive Docusaurus site
- **GitHub Issues**: Report bugs or ask questions
- **Community**: Join our discussions for community support
- **Enterprise Support**: Available for Team and Enterprise tiers

## Migration Checklist

- [ ] Environment setup (Yarn 4.9.2)
- [ ] Project cloned and dependencies installed
- [ ] Environment variables configured
- [ ] Model configuration updated
- [ ] Command usage updated
- [ ] API integration migrated
- [ ] Advanced features implemented
- [ ] Testing completed
- [ ] Documentation updated
- [ ] Team training completed (if applicable)

## Next Steps

After successful migration:

1. **Explore Quantum Tasks**: Try advanced AI-powered features
2. **Set up Analytics**: Monitor usage and performance
3. **Integrate WebContainer**: Add interactive examples to docs
4. **Team Onboarding**: Train team members on new features
5. **Performance Optimization**: Use new optimization features

Welcome to the enhanced world of Monkey Coder! 🐒✨
