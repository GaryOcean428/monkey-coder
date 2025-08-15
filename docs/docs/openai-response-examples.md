---
id: openai-response-examples
title: OpenAI Response Examples
sidebar_label: OpenAI Response Examples
---

# OpenAI Response Examples

This document provides comprehensive examples of OpenAI client response patterns for different model variants. These examples demonstrate the various configurations and capabilities available across different model tiers.

:::info
The GPT-5 model examples shown below are conceptual templates for future OpenAI models. Please refer to the Models Manifest for currently supported models.
:::

## Overview

The OpenAI API supports various response configurations depending on the model type and intended use case. This guide covers three main model categories with their optimal configurations:

- **Chat Latest Models**: High-performance models for complex reasoning
- **Mini Models**: Balanced models for general-purpose tasks
- **Nano Models**: Lightweight models for simple tasks

## Python Examples

### GPT-5 Chat Latest (High Performance)

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5-chat-latest",
    input=[
        {
            "role": "system",
            "content": [
                {
                    "type": "input_text",
                    "text": "insert utility model system prompt."
                }
            ]
        }
    ],
    text={},
    reasoning={},
    tools=[],
    temperature=2,
    max_output_tokens=16384,
    top_p=1,
    store=True
)
```

**Configuration Details:**
- **Temperature**: `2` - Maximum creativity and variation
- **Max Tokens**: `16384` - Large response capacity
- **Top P**: `1` - Full vocabulary consideration
- **Store**: `True` - Response storage enabled

**Use Cases:**
- Complex reasoning tasks
- Creative content generation
- Advanced problem solving
- Large-scale analysis

### GPT-5 Mini (Balanced Performance)

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5-mini",
    input=[
        {
            "role": "developer",
            "content": [
                {
                    "type": "input_text",
                    "text": "insert utility model system prompt."
                }
            ]
        }
    ],
    text={
        "format": {
            "type": "text"
        },
        "verbosity": "high"
    },
    reasoning={
        "effort": "high",
        "summary": "auto"
    },
    tools=[],
    store=True
)
```

**Configuration Details:**
- **Text Format**: Structured text output with high verbosity
- **Reasoning Effort**: `high` - Enhanced reasoning capabilities
- **Summary**: `auto` - Automatic response summarization
- **Store**: `True` - Response storage enabled

**Use Cases:**
- Development tasks
- Code generation and analysis
- Technical documentation
- API integration

### GPT-5 Nano (Lightweight Performance)

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5-nano",
    input=[
        {
            "role": "developer",
            "content": [
                {
                    "type": "input_text",
                    "text": "insert utility model system prompt."
                }
            ]
        }
    ],
    text={
        "format": {
            "type": "text"
        },
        "verbosity": "low"
    },
    reasoning={
        "effort": "minimal",
        "summary": "detailed"
    },
    tools=[],
    store=True
)
```

**Configuration Details:**
- **Text Format**: Structured text output with low verbosity
- **Reasoning Effort**: `minimal` - Efficient processing
- **Summary**: `detailed` - Comprehensive response summaries
- **Store**: `True` - Response storage enabled

**Use Cases:**
- Quick responses
- Simple queries
- Rapid prototyping
- Resource-constrained environments

## TypeScript/JavaScript Examples

For frontend developers using Node.js or browser environments:

### GPT-5 Chat Latest (TypeScript)

```typescript
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

async function generateHighPerformanceResponse() {
  const response = await client.responses.create({
    model: 'gpt-5-chat-latest',
    input: [
      {
        role: 'system',
        content: [
          {
            type: 'input_text',
            text: 'insert utility model system prompt.',
          },
        ],
      },
    ],
    text: {},
    reasoning: {},
    tools: [],
    temperature: 2,
    max_output_tokens: 16384,
    top_p: 1,
    store: true,
  });

  return response;
}
```

### GPT-5 Mini (TypeScript)

```typescript
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

async function generateBalancedResponse() {
  const response = await client.responses.create({
    model: 'gpt-5-mini',
    input: [
      {
        role: 'developer',
        content: [
          {
            type: 'input_text',
            text: 'insert utility model system prompt.',
          },
        ],
      },
    ],
    text: {
      format: {
        type: 'text',
      },
      verbosity: 'high',
    },
    reasoning: {
      effort: 'high',
      summary: 'auto',
    },
    tools: [],
    store: true,
  });

  return response;
}
```

### GPT-5 Nano (TypeScript)

```typescript
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

async function generateLightweightResponse() {
  const response = await client.responses.create({
    model: 'gpt-5-nano',
    input: [
      {
        role: 'developer',
        content: [
          {
            type: 'input_text',
            text: 'insert utility model system prompt.',
          },
        ],
      },
    ],
    text: {
      format: {
        type: 'text',
      },
      verbosity: 'low',
    },
    reasoning: {
      effort: 'minimal',
      summary: 'detailed',
    },
    tools: [],
    store: true,
  });

  return response;
}
```

## Configuration Reference

### Model Comparison

| Model | Performance | Token Limit | Best For |
|-------|-------------|-------------|----------|
| `gpt-5-chat-latest` | Highest | 16384 | Complex reasoning, creative tasks |
| `gpt-5-mini` | Balanced | Variable | Development, general purpose |
| `gpt-5-nano` | Efficient | Variable | Quick responses, simple tasks |

### Parameter Guide

#### Temperature Settings
- **0-0.5**: Focused, deterministic responses
- **0.6-1.2**: Balanced creativity and consistency
- **1.3-2.0**: High creativity and variation

#### Reasoning Configuration
- **effort**: `minimal`, `low`, `medium`, `high`, `maximum`
- **summary**: `none`, `brief`, `auto`, `detailed`

#### Text Format Options
- **type**: `text`, `markdown`, `json`, `xml`
- **verbosity**: `minimal`, `low`, `medium`, `high`, `verbose`

## Error Handling

### Python Error Handling

```python
from openai import OpenAI
import openai

client = OpenAI()

try:
    response = client.responses.create(
        model="gpt-5-mini",
        input=[{"role": "user", "content": [{"type": "input_text", "text": "Hello"}]}],
        text={"verbosity": "high"},
        reasoning={"effort": "high"},
        store=True
    )
except openai.APIError as e:
    print(f"OpenAI API error: {e}")
except openai.RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except openai.AuthenticationError as e:
    print(f"Authentication failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### TypeScript Error Handling

```typescript
import OpenAI from 'openai';

const client = new OpenAI();

async function handleResponse() {
  try {
    const response = await client.responses.create({
      model: 'gpt-5-mini',
      input: [{ role: 'user', content: [{ type: 'input_text', text: 'Hello' }] }],
      text: { verbosity: 'high' },
      reasoning: { effort: 'high' },
      store: true,
    });

    return response;
  } catch (error) {
    if (error instanceof OpenAI.APIError) {
      console.error('OpenAI API error:', error.message);
    } else if (error instanceof OpenAI.RateLimitError) {
      console.error('Rate limit exceeded:', error.message);
    } else if (error instanceof OpenAI.AuthenticationError) {
      console.error('Authentication failed:', error.message);
    } else {
      console.error('Unexpected error:', error);
    }
    throw error;
  }
}
```

## Integration Examples

### React Frontend Integration

```tsx
import React, { useState } from 'react';
import OpenAI from 'openai';

const OpenAIChat: React.FC = () => {
  const [response, setResponse] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const generateResponse = async (prompt: string) => {
    setLoading(true);
    try {
      const client = new OpenAI({
        apiKey: process.env.REACT_APP_OPENAI_API_KEY,
        dangerouslyAllowBrowser: true, // Only for demo purposes
      });

      const result = await client.responses.create({
        model: 'gpt-5-mini',
        input: [
          {
            role: 'user',
            content: [{ type: 'input_text', text: prompt }],
          },
        ],
        text: { verbosity: 'medium' },
        reasoning: { effort: 'medium' },
        store: true,
      });

      setResponse(result.choices[0]?.message?.content || '');
    } catch (error) {
      console.error('Error generating response:', error);
      setResponse('Error generating response');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={() => generateResponse('Hello, world!')}>
        {loading ? 'Generating...' : 'Generate Response'}
      </button>
      {response && <div>{response}</div>}
    </div>
  );
};

export default OpenAIChat;
```

### Node.js Backend Integration

```javascript
const express = require('express');
const OpenAI = require('openai');

const app = express();
const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

app.use(express.json());

app.post('/api/generate', async (req, res) => {
  try {
    const { prompt, model = 'gpt-5-mini' } = req.body;

    const response = await client.responses.create({
      model,
      input: [
        {
          role: 'user',
          content: [{ type: 'input_text', text: prompt }],
        },
      ],
      text: { verbosity: 'medium' },
      reasoning: { effort: 'medium' },
      store: true,
    });

    res.json({
      success: true,
      response: response.choices[0]?.message?.content,
    });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

## Best Practices

### Performance Optimization

1. **Choose the Right Model**: Use nano for simple tasks, mini for balanced needs, latest for complex reasoning
2. **Optimize Parameters**: Adjust temperature and reasoning effort based on use case
3. **Implement Caching**: Cache responses for repeated queries
4. **Use Streaming**: Enable streaming for real-time applications

### Security Considerations

1. **API Key Management**: Store API keys securely using environment variables
2. **Input Validation**: Validate and sanitize user inputs
3. **Rate Limiting**: Implement client-side rate limiting
4. **Error Handling**: Properly handle and log errors without exposing sensitive data

### Cost Management

1. **Model Selection**: Use the most cost-effective model for your needs
2. **Token Optimization**: Minimize unnecessary tokens in prompts and responses
3. **Response Caching**: Cache responses to reduce API calls
4. **Monitoring**: Track usage and costs regularly

## Related Resources

- [Model Manifest](pathname:///monkey-coder/MODEL_MANIFEST.md) - Current supported models
- [Quick Start Guide](./quick-start.md) - Getting started with Monkey Coder
- [Migration Guide](./migration-guide.md) - Upgrading and migration information

:::tip
For production applications, always refer to the official OpenAI documentation and use the currently supported models listed in the Models Manifest.
:::