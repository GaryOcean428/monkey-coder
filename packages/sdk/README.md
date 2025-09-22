# Monkey Coder SDK

The official TypeScript/JavaScript and Python SDK for [Monkey Coder](https://monkeycoder.dev) - an AI-powered code generation and analysis platform.

## Features

🚀 **Multiple Runtime Support**: Works with Node.js, Bun, Deno, and Python  
🔐 **Authentication**: Built-in API key management and token handling  
🔄 **Automatic Retries**: Exponential backoff with configurable retry logic  
📡 **Streaming Support**: Real-time execution progress with Server-Sent Events  
🎯 **Type Safety**: Full TypeScript definitions and Python type hints  
⚡ **Performance**: Optimized for speed and efficiency  
🛠️ **Developer Experience**: Rich error handling and debugging tools  

## Quick Start

### TypeScript/JavaScript

```bash
# Install via npm
npm install @monkey-coder/sdk

# Install via yarn
yarn add @monkey-coder/sdk

# Install via pnpm
pnpm add @monkey-coder/sdk
```

```typescript
import { MonkeyCoderClient, createCodeGenerationRequest } from '@monkey-coder/sdk';

const client = new MonkeyCoderClient({
  baseURL: 'https://api.monkeycoder.dev',
  apiKey: 'your-api-key',
  retries: 3
});

// Generate code
const request = createCodeGenerationRequest(
  'Create a REST API server with authentication',
  'user-123'
);

const response = await client.execute(request);
console.log(response.result?.result);
```

### Python

```bash
# Install via pip
pip install monkey-coder-sdk
```

```python
from monkey_coder_sdk import MonkeyCoderClient, create_code_generation_request

client = MonkeyCoderClient({
    'base_url': 'https://api.monkeycoder.dev',
    'api_key': 'your-api-key',
    'retries': 3
})

# Generate code
request = create_code_generation_request(
    prompt='Create a REST API server with authentication',
    user_id='user-123'
)

response = client.execute(request)
print(response.result.result)
```

## Documentation

### TypeScript/JavaScript API

#### `MonkeyCoderClient`

The main client class for interacting with the Monkey Coder API.

```typescript
interface MonkeyCoderClientConfig {
  baseURL?: string;           // API base URL
  apiKey?: string;           // API key for authentication
  timeout?: number;          // Request timeout in ms (default: 300000)
  retries?: number;          // Number of retries (default: 3)
  retryDelay?: number;       // Initial retry delay in ms (default: 1000)
  maxRetryDelay?: number;    // Maximum retry delay in ms (default: 10000)
  retryCondition?: (error: AxiosError) => boolean;
  onRetry?: (retryCount: number, error: AxiosError) => void;
}
```

#### Core Methods

```typescript
// Health check
await client.health(): Promise<HealthResponse>

// Execute task
await client.execute(request: ExecuteRequest): Promise<ExecuteResponse>

// Execute with streaming
await client.executeStream(
  request: ExecuteRequest, 
  onEvent: (event: StreamEvent) => void
): Promise<ExecuteResponse>

// Get usage metrics
await client.getUsage(params?: UsageRequest): Promise<any>

// List providers and models
await client.listProviders(): Promise<Record<string, any>>
await client.listModels(provider?: ProviderType): Promise<Record<string, any>>

// Debug routing decisions
await client.debugRouting(request: ExecuteRequest): Promise<Record<string, any>>
```

#### Helper Functions

```typescript
// Create basic execute request
createExecuteRequest(
  taskType: TaskType,
  prompt: string,
  context: ExecutionContext,
  persona?: PersonaType,
  options?: Partial<ExecuteRequest>
): ExecuteRequest

// Create code generation request
createCodeGenerationRequest(
  prompt: string,
  userId: string,
  options?: Partial<ExecuteRequest>
): ExecuteRequest

// Create code review request
createCodeReviewRequest(
  prompt: string,
  userId: string,
  files: Array<{ path: string; content: string; type?: string }>,
  options?: Partial<ExecuteRequest>
): ExecuteRequest
```

### Python API

#### `MonkeyCoderClient`

```python
@dataclass
class MonkeyCoderClientConfig:
    base_url: str = "https://your-domain.railway.app"  # Use your Railway deployment URL
    api_key: Optional[str] = None
    timeout: float = 300.0
    retries: int = 3
    retry_delay: float = 1.0
    max_retry_delay: float = 10.0
    retry_condition: Optional[Callable[[Exception], bool]] = None
    on_retry: Optional[Callable[[int, Exception], None]] = None
```

#### Core Methods

```python
# Health check
client.health() -> HealthResponse

# Execute task
client.execute(request: ExecuteRequest) -> ExecuteResponse

# Execute with streaming
client.execute_stream(
    request: ExecuteRequest, 
    on_event: Callable[[StreamEvent], None]
) -> None

# Get usage metrics
client.get_usage(usage_request: UsageRequest) -> Dict

# List providers and models
client.list_providers() -> Dict
client.list_models(provider: Optional[ProviderType] = None) -> Dict

# Debug routing decisions
client.debug_routing(request: ExecuteRequest) -> Dict
```

#### Helper Functions

```python
# Create basic execute request
create_execute_request(
    task_type: TaskType,
    prompt: str,
    context: ExecutionContext,
    persona: PersonaType = PersonaType.DEVELOPER,
    **kwargs
) -> ExecuteRequest

# Create code generation request
create_code_generation_request(
    prompt: str,
    user_id: str,
    language: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: int = 4096,
    **kwargs
) -> ExecuteRequest

# Specialized request creators
create_code_review_request(...)
create_documentation_request(...)
create_security_analysis_request(...)
create_testing_request(...)
create_performance_optimization_request(...)
```

## Examples

### Streaming Execution

```typescript
await client.executeStream(request, (event) => {
  switch (event.type) {
    case 'start':
      console.log('🚀 Starting execution...');
      break;
    case 'progress':
      console.log(`📊 ${event.progress?.percentage}% - ${event.progress?.step}`);
      break;
    case 'complete':
      console.log('✅ Execution completed');
      console.log(event.data?.result?.result);
      break;
    case 'error':
      console.error('❌ Error:', event.error?.message);
      break;
  }
});
```

### Error Handling

```typescript
try {
  const response = await client.execute(request);
} catch (error) {
  if (error instanceof MonkeyCoderError) {
    console.error('API Error:', error.message);
    console.error('Status Code:', error.statusCode);
    console.error('Error Code:', error.code);
  }
}
```

### Configuration Management

```typescript
// Update API key dynamically
client.setApiKey('new-api-key');

// Update base URL
client.setBaseURL('https://api-staging.monkeycoder.dev');

// Custom retry logic
const client = new MonkeyCoderClient({
  retryCondition: (error) => error.response?.status >= 500,
  onRetry: (retryCount, error) => {
    console.log(`Retry ${retryCount}: ${error.message}`);
  }
});
```

## Task Types

- `code_generation` - Generate new code from prompts
- `code_analysis` - Analyze existing code for issues
- `code_review` - Review code for quality and best practices
- `documentation` - Generate documentation from code
- `testing` - Create unit tests for code
- `debugging` - Debug and fix code issues
- `refactoring` - Refactor and optimize code
- `custom` - Custom tasks with specific requirements

## Personas

- `developer` - General development tasks
- `architect` - System design and architecture
- `reviewer` - Code review and quality assessment
- `security_analyst` - Security analysis and vulnerability scanning
- `performance_expert` - Performance optimization
- `tester` - Test generation and quality assurance
- `technical_writer` - Documentation and technical writing
- `custom` - Custom persona with specific instructions

## Runtime Examples

### Node.js
```bash
cd examples/node
npm install
node index.js
```

### Bun
```bash
cd examples/bun
bun install
bun run index.ts
```

### Deno
```bash
cd examples/deno
deno run --allow-net index.ts
```

### Python
```bash
cd examples/python
pip install -r requirements.txt
python main.py
```

## Advanced Configuration

### Multi-Agent Configuration

```typescript
const monkey1Config: Monkey1Config = {
  agent_count: 5,
  coordination_strategy: 'collaborative',
  consensus_threshold: 0.8,
  enable_reflection: true,
  max_iterations: 10
};
```

### Quantum Execution Configuration

```typescript
const gary8dConfig: Gary8DConfig = {
  parallel_futures: true,
  collapse_strategy: 'weighted_average',
  quantum_coherence: 0.9,
  execution_branches: 5,
  uncertainty_threshold: 0.05
};
```

## Error Codes

- `NO_RESPONSE` - No response from server
- `REQUEST_ERROR` - Request configuration error
- `STREAM_INCOMPLETE` - Streaming ended without completion
- `EXECUTION_ERROR` - Task execution failed
- `PROVIDER_ERROR` - AI provider error
- `VALIDATION_ERROR` - Request validation failed

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@monkeycoder.dev
- 💬 Discord: [Join our community](https://discord.gg/monkeycoder)
- 📖 Documentation: https://docs.monkeycoder.dev
- 🐛 Issues: [GitHub Issues](https://github.com/monkey-coder/sdk/issues)
