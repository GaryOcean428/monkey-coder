# Monkey-Coder A2A Agent Documentation

## Overview

The Monkey-Coder A2A (Agent-to-Agent) Agent is a specialized Deep Agent that provides code generation, repository analysis, and testing capabilities through a standardized A2A interface with Model Context Protocol (MCP) integration.

## Features

### Core Capabilities
- **Code Generation**: Generate high-quality code from natural language specifications
- **Repository Analysis**: Analyze codebases for structure, issues, and improvements
- **Test Execution**: Run tests across multiple frameworks with intelligent detection
- **MCP Integration**: Seamless filesystem and GitHub operations through MCP protocol
- **Quantum Execution**: Advanced execution patterns for optimal results

### A2A Skills

#### 1. generate_code
Generate code implementing a feature specification with context awareness.

**Parameters:**
- `spec` (required): Feature specification or description
- `context` (optional): Additional context including:
  - `language`: Programming language (python, javascript, typescript, etc.)
  - `style`: Code style preference (clean, comprehensive, optimized)
  - `files`: Related files for context

**Example:**
```python
result = await client.call_skill(
    skill_name="generate_code",
    parameters={
        "spec": "Create a function that validates email addresses",
        "context": {
            "language": "python",
            "style": "clean"
        }
    }
)
```

#### 2. analyze_repo
Analyze a repository or module for various aspects of code quality and structure.

**Parameters:**
- `repo_path` (required): Path to repository or module
- `analysis_type` (optional): Type of analysis
  - `structure`: Architecture and organization analysis
  - `issues`: Potential problems and code smells
  - `improvements`: Optimization and enhancement suggestions
  - `comprehensive`: Complete analysis (default)

**Example:**
```python
result = await client.call_skill(
    skill_name="analyze_repo",
    parameters={
        "repo_path": "./src",
        "analysis_type": "comprehensive"
    }
)
```

#### 3. run_tests
Execute tests with automatic framework detection and comprehensive reporting.

**Parameters:**
- `path` (required): Path to test files or directory
- `test_framework` (optional): Framework to use
  - `pytest`: Python pytest framework
  - `unittest`: Python unittest framework
  - `jest`: JavaScript/TypeScript Jest framework
  - `auto`: Automatic detection (default)
- `options` (optional): Additional test options
  - `coverage`: Enable coverage reporting
  - `verbose`: Enable verbose output

**Example:**
```python
result = await client.call_skill(
    skill_name="run_tests",
    parameters={
        "path": "./tests",
        "test_framework": "pytest",
        "options": {
            "coverage": true,
            "verbose": true
        }
    }
)
```

## Architecture

### A2A Server Integration
The A2A server (`monkey_coder/a2a_server.py`) integrates with the main FastAPI application and provides:

- Configurable port (default: 7702)
- Automatic MCP client initialization
- Skill registration and management
- Error handling and logging
- Graceful startup and shutdown

### MCP Integration
The agent uses MCP (Model Context Protocol) for external operations:

- **Filesystem MCP**: File reading, writing, and directory operations
- **GitHub MCP**: Repository management and version control operations
- Automatic connection management and error handling

### Agent Components

```text
MonkeyCoderA2AAgent
├── CodeGeneratorAgent (quantum execution)
├── CodeAnalyzerAgent (comprehensive analysis)
├── MCP Clients
│   ├── Filesystem Client
│   └── GitHub Client (optional)
└── A2A Server
    ├── Skill Registration
    ├── Parameter Validation
    └── Error Handling
```

## Deployment

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENABLE_A2A_SERVER` | Enable A2A server | `true` | No |
| `A2A_PORT` | A2A server port | `7702` | No |
| `GITHUB_TOKEN` | GitHub token for MCP | - | No |
| `OPENAI_API_KEY` | OpenAI API key | - | Yes* |
| `ANTHROPIC_API_KEY` | Anthropic API key | - | Yes* |

*At least one AI provider API key is required.

### Railway Deployment

The agent is configured for Railway deployment through `railpack.json`:

```json
{
  "environment": {
    "ENABLE_A2A_SERVER": "true",
    "A2A_PORT": "7702"
  }
}
```

### Docker Deployment

```dockerfile
ENV ENABLE_A2A_SERVER=true
ENV A2A_PORT=7702
EXPOSE 7702
```

## Usage Examples

### Starting the A2A Server

The A2A server starts automatically with the main application when `ENABLE_A2A_SERVER=true`.

For standalone operation:
```bash
python packages/core/start_a2a_server.py
```

### Agent Discovery

Get agent capabilities via HTTP:
```bash
curl http://localhost:8000/.well-known/agent.json
```

### Using Example Clients

#### Demo Client (Full Demonstration)
```bash
cd examples/a2a
pythondemo_client.py
```

#### Simple Client (Command Line)
```bash
cd examples/a2a

# Generate code
python simple_client.py generate "Create a sorting algorithm" --language python

# Analyze repository
python simple_client.py analyze ./src --type comprehensive

# Run tests
python simple_client.py test ./tests--framework pytest
```

### Python A2A Client

```python
import asyncio
from python_a2a import A2AClient

async def example():
    client = A2AClient(host="localhost", port=7702)
    await client.connect()
    
    try:
        # Generate code
        result = await client.call_skill(
            skill_name="generate_code",
            parameters={
                "spec": "Create a binary search function",
                "context": {"language": "python", "style": "clean"}
            }
        )
        print("Generated code:", result)
        
    finally:
        await client.disconnect()

asyncio.run(example())
```

## Testing

### Running Tests

```bash
# Run all A2A tests
pytest packages/core/tests/agents/test_monkey_coder_a2a.py -v

# Run specific test
pytest packages/core/tests/agents/test_monkey_coder_a2a.py::TestMonkeyCoderA2AAgent::test_generate_code_skill -v

# Run with coverage
pytest packages/core/tests/agents/test_monkey_coder_a2a.py--cov=monkey_coder.a2a_server
```

### Test Coverage

The test suite covers:
- Agent initialization and lifecycle
- All three skills (generate_code, analyze_repo, run_tests)
- MCP client integration
- Error handling and edge cases
- Agent card functionality
- HTTP endpoint integration

## Monitoring and Observability

### Health Checks

- Main application health: `GET /health`
- Agent card status: `GET /.well-known/agent.json`
- A2A server status included in agent card response

### Logging

A2A operations are logged with structured information:
- Skill execution timing
- MCP operations
- Error conditions
- Performance metrics

### Metrics

Key metrics tracked:
- Skill execution count and duration
- MCP operation success/failure rates
- Error rates by skill type
- Resource utilization

## Development

### Adding New Skills

1. Define skill function with `@skill` decorator:
```python
@skill(name="my_skill")
async def my_skill(self, param1: str, param2: int = 10) -> str:
    # Implementation
    return result
```

2. Register skill in `_register_skills()` method
3. Add parameter schema to agent card
4. Create tests for the new skill

### Extending MCP Integration

1. Add new MCP server configuration
2. Update `_initialize_mcp_clients()` method
3. Use MCP tools in skill implementations
4. Add error handling for MCP operations

### Custom Prompt Templates

Create new templates in `prompts/` directory:
```markdown
# My Custom Template

{parameter1}
{parameter2}

Instructions...
```

## Troubleshooting

### Common Issues

1. **A2A Server Won't Start**
   - Check port availability
   - Verify dependencies installed
   - Check logs for initialization errors

2. **MCP Connection Failures**
   - Verify MCP servers are available
   - Check GitHub token if using GitHub MCP
   - Review MCP server logs

3. **Skill Execution Errors**
   - Validate input parameters
   - Check AI provider API keys
   - Review error logs

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python packages/core/start_a2a_server.py
```

### Health Diagnostics

Check system status:
```bash
curl http://localhost:8000/.well-known/agent.json | jq '.a2a_server'
```

## Security Considerations

- A2A server binds to localhost by default
- API keys are required for AI operations
- GitHub token is optional but recommended for full functionality
- All external requests are validated and sanitized
- Error messages don't expose sensitive information

## Performance Optimization

- Skills use quantum execution for optimal results
- MCP clients are reused across requests
- Prompt templates are cached
- Background tasks handle long-running operations
- Graceful degradation when services are unavailable

## License

This implementation follows the same license as the Monkey-Coder project.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review test examples
3. Open an issue in the project repository
