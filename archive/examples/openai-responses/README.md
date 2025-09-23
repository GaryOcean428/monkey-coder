# OpenAI Response Examples

This directory contains practical examples for integrating OpenAI response patterns in both Python and TypeScript/JavaScript applications.

## Overview

The examples demonstrate three conceptual GPT-5 model configurations:

- **GPT-5 Chat Latest**: High-performance model for complex reasoning
- **GPT-5 Mini**: Balanced model for general development tasks
- **GPT-5 Nano**: Lightweight model for simple tasks

> **Note**: These examples use conceptual GPT-5 models for demonstration purposes. Please refer to the [Model Manifest](../../docs/MODEL_MANIFEST.md) for currently supported models.

## Files

### Python Implementation
- `openai_response_examples.py` - Complete Python implementation with sync/async support

### TypeScript/JavaScript Implementation
- `openai-response-examples.ts` - TypeScript implementation with React hooks and Express middleware

## Usage

### Python

```bash
# Install dependencies
pip install openai python-dotenv

# Set environment variable
export OPENAI_API_KEY="your-api-key"

# Run examples
python openai_response_examples.py
```

### TypeScript/JavaScript

```bash
# Install dependencies
npm install openai dotenv

# Set environment variable
export OPENAI_API_KEY="your-api-key"

# Run with Node.js
node openai-response-examples.js

# Or with TypeScript
ts-node openai-response-examples.ts
```

## Key Features

### Python Features
- Synchronous and asynchronous support
- Comprehensive error handling
- Mock responses for demonstration
- Dataclass-based configuration

### TypeScript/JavaScript Features
- React hook integration for frontend
- Express middleware for backend
- Streaming response support
- Batch processing capabilities

## Configuration Examples

### GPT-5 Chat Latest
- Temperature: 2 (maximum creativity)
- Max tokens: 16384
- Top P: 1 (full vocabulary)
- Best for: Complex reasoning, creative tasks

### GPT-5 Mini
- High verbosity text output
- High reasoning effort with auto summary
- Best for: Development tasks, code generation

### GPT-5 Nano
- Low verbosity output
- Minimal reasoning effort with detailed summary
- Best for: Quick responses, simple tasks

## Integration Patterns

### Frontend (React)
```typescript
const { generateResponse, loading, error } = useOpenAIResponses();

const handleGenerate = async () => {
  const result = await generateResponse('mini', 'Generate a function');
  console.log(result);
};
```

### Backend (Express)
```javascript
const middleware = createOpenAIMiddleware();

app.post('/api/generate', middleware.generateResponse);
app.post('/api/stream', middleware.streamResponse);
```

### Python Async
```python
examples = OpenAIResponseExamples()
response = await examples.create_async_response('mini', 'Your prompt here')
```

## Error Handling

Both implementations include comprehensive error handling for:
- API authentication errors
- Rate limiting
- Network issues
- Invalid model configurations

## Best Practices

1. **Environment Variables**: Always use environment variables for API keys
2. **Error Handling**: Implement proper error handling for production use
3. **Rate Limiting**: Consider implementing client-side rate limiting
4. **Model Selection**: Choose the appropriate model based on task complexity
5. **Caching**: Implement response caching for repeated queries

## Related Documentation

- [OpenAI Response Examples Documentation](../../docs/docs/openai-response-examples.md)
- [Model Manifest](../../docs/MODEL_MANIFEST.md)
- [Quick Start Guide](../../docs/docs/quick-start.md)