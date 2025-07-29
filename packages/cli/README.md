# Monkey Coder CLI

A powerful command-line interface for the Monkey Coder AI-powered code generation and analysis platform.

## Features

- 🚀 **Code Implementation**: Generate code based on natural language requirements
- 🔍 **Code Analysis**: Analyze code for quality, security, and performance issues  
- 🏗️  **Architecture Building**: Design and build robust code architectures
- 🧪 **Test Generation**: Automatically generate comprehensive unit tests
- 📊 **Streaming Output**: Real-time progress updates with Server-Sent Events
- ⚙️  **Configuration Management**: Persistent settings and preferences
- 🎭 **Multiple Personas**: Choose from different AI personas (developer, architect, reviewer, tester, etc.)
- 🔌 **Provider Support**: Support for multiple AI providers (OpenAI, Anthropic, Google, Qwen)

## Installation

```bash
# Install globally
npm install -g monkey-coder-cli

# Or use yarn
yarn global add monkey-coder-cli
```

## Quick Start

1. **Set up your API configuration:**
```bash
monkey-coder config set apiKey "your-api-key-here"
monkey-coder config set baseUrl "https://your-monkey-coder-api.com"
```

2. **Check server health:**
```bash
monkey-coder health
```

3. **Generate some code:**
```bash
monkey-coder implement "Create a TypeScript function that validates email addresses" --output email-validator.ts
```

## Commands

### `implement`
Generate code implementation based on requirements.

```bash
monkey-coder implement <prompt> [files...] [options]

# Examples:
monkey-coder implement "Create a React component for user authentication"
monkey-coder implement "Add error handling to this API" src/api.ts --output src/api-fixed.ts
monkey-coder implement "Convert this to TypeScript" legacy.js --language typescript --stream
```

**Options:**
- `-o, --output <file>` - Output file path
- `-l, --language <lang>` - Target programming language
- `-p, --persona <persona>` - AI persona to use (default: developer)
- `--model <model>` - AI model to use
- `--provider <provider>` - AI provider to use
- `-t, --temperature <temp>` - Model temperature (0.0-2.0)
- `--timeout <seconds>` - Request timeout in seconds
- `--stream` - Enable streaming output

### `analyze`
Analyze code for quality, security, and performance issues.

```bash
monkey-coder analyze <files...> [options]

# Examples:
monkey-coder analyze src/**/*.ts --type security
monkey-coder analyze app.py --type performance --output performance-report.md
monkey-coder analyze src/ --persona security_analyst --stream
```

**Options:**
- `-t, --type <type>` - Analysis type (quality, security, performance)
- `-p, --persona <persona>` - AI persona to use (default: reviewer)
- `-o, --output <file>` - Output file path for analysis report
- `--model <model>` - AI model to use
- `--provider <provider>` - AI provider to use
- `--stream` - Enable streaming output

### `build`
Build and optimize code architecture.

```bash
monkey-coder build <prompt> [files...] [options]

# Examples:
monkey-coder build "Design a microservices architecture for e-commerce"
monkey-coder build "Refactor this monolith into modules" src/ --output refactored/
monkey-coder build "Add caching layer" --persona architect --stream
```

**Options:**
- `-o, --output <dir>` - Output directory for built files
- `-p, --persona <persona>` - AI persona to use (default: architect)
- `--model <model>` - AI model to use
- `--provider <provider>` - AI provider to use
- `--stream` - Enable streaming output

### `test`
Generate tests for code files.

```bash
monkey-coder test <files...> [options]

# Examples:
monkey-coder test src/utils.ts --framework jest
monkey-coder test src/**/*.py --output tests/ --framework pytest
monkey-coder test app.js --persona tester --stream
```

**Options:**
- `-o, --output <dir>` - Output directory for test files
- `-f, --framework <framework>` - Testing framework to use
- `-p, --persona <persona>` - AI persona to use (default: tester)
- `--model <model>` - AI model to use
- `--provider <provider>` - AI provider to use
- `--stream` - Enable streaming output

### `config`
Manage CLI configuration.

```bash
# Set configuration values
monkey-coder config set <key> <value>
monkey-coder config set apiKey "sk-..."
monkey-coder config set defaultPersona "architect"

# Get configuration values
monkey-coder config get apiKey
monkey-coder config get baseUrl

# List all configuration
monkey-coder config list

# Reset to defaults
monkey-coder config reset
```

### `health`
Check API server health.

```bash
monkey-coder health
```

## Configuration

The CLI supports configuration through:

1. **Configuration file** (`~/.config/monkey-coder/config.json`)
2. **Environment variables**
3. **Command-line options**

### Configuration Keys

- `apiKey` - Your API key for authentication
- `baseUrl` - Base URL for the API (default: http://localhost:8000)
- `defaultPersona` - Default AI persona (default: developer)
- `defaultModel` - Default AI model (default: gpt-4)
- `defaultProvider` - Default AI provider (default: openai)
- `defaultTemperature` - Default model temperature (default: 0.1)
- `defaultTimeout` - Default request timeout (default: 300)

### Environment Variables

- `MONKEY_CODER_API_KEY` - API key
- `MONKEY_CODER_API_URL` - Base URL for the API

## AI Personas

Choose different AI personas for specialized tasks:

- **developer** - General purpose coding and implementation
- **architect** - System design and architecture planning
- **reviewer** - Code review and quality analysis
- **security_analyst** - Security-focused analysis and recommendations
- **performance_expert** - Performance optimization and analysis
- **tester** - Test generation and quality assurance
- **technical_writer** - Documentation and explanation

## Streaming Output

Enable real-time progress updates with the `--stream` flag:

```bash
monkey-coder implement "Build a REST API" --stream
```

This provides:
- Real-time progress updates
- Step-by-step execution feedback
- Interactive spinner animations
- Immediate error reporting

## Examples

### Generate a Complete Feature
```bash
# Generate a user authentication system
monkey-coder implement "Create a complete user authentication system with login, register, and JWT tokens" \
  --language typescript \
  --persona developer \
  --output auth-system.ts \
  --stream
```

### Analyze Code Security
```bash
# Security analysis of multiple files
monkey-coder analyze src/**/*.js \
  --type security \
  --persona security_analyst \
  --output security-report.md \
  --stream
```

### Build System Architecture
```bash
# Design microservices architecture
monkey-coder build "Design a scalable microservices architecture for a social media platform" \
  --persona architect \
  --output architecture/ \
  --stream
```

### Generate Tests
```bash
# Generate comprehensive tests
monkey-coder test src/api/users.ts src/api/auth.ts \
  --framework jest \
  --output tests/ \
  --persona tester \
  --stream
```

## Error Handling

The CLI provides comprehensive error handling:

- **Network errors** - Connection issues with the API server
- **Authentication errors** - Invalid API keys or permissions
- **File errors** - Missing files or permission issues
- **Validation errors** - Invalid command arguments or options
- **API errors** - Server-side processing errors

All errors are displayed with clear, actionable messages.

## Cross-Platform Support

The CLI works on:
- ✅ Windows (PowerShell, Command Prompt)
- ✅ macOS (Terminal, iTerm)
- ✅ Linux (Bash, Zsh, Fish)

## Development

### Building from Source

```bash
# Clone the repository
git clone https://github.com/your-org/monkey-coder.git
cd monkey-coder/packages/cli

# Install dependencies
yarn install

# Build the project
yarn build

# Link for local development
yarn link
```

### Testing

```bash
# Run tests
yarn test

# Run tests in watch mode
yarn test:watch

# Run tests with coverage
yarn test:coverage
```

## License

MIT License - see [LICENSE](../../LICENSE) for details.

## Support

- 📚 Documentation: [https://docs.monkey-coder.dev](https://docs.monkey-coder.dev)
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/monkey-coder/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-org/monkey-coder/discussions)
