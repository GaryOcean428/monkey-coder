[← Back to Roadmap Index](../roadmap.md)

## Technical Architecture

### Core Components

```text
monkey-coder/
├── packages/
│   ├── core/                 # Python core engine
│   │   ├── monkey_coder/
│   │   │   ├── agents/       # Multi-agent system
│   │   │   ├── quantum/      # Quantum execution
│   │   │   ├── mcp/         # MCP integration
│   │   │   ├── providers/    # AI provider adapters
│   │   │   └── utils/        # Model validation
│   │   └── tests/
│   ├── cli/                  # TypeScript CLI
│   │   └── src/
│   │       ├── commands/     # CLI commands
│   │       └── mcp/         # MCP management
│   └── sdk/                  # Multi-language SDKs
│       ├── src/TypeScript/
│       └── src/Python/
```
