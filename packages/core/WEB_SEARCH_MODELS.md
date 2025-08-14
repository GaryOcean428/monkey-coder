# Web Search Support by Model

## Overview

This document lists which AI models support web search capabilities in the Monkey Coder system, based on the MODEL_MANIFEST.md specifications.

## Models with Web Search Support

### Anthropic Claude Models
All modern Claude models support web search through search result injection:

- **Claude 3.5 Sonnet** (`claude-3-5-sonnet-*`)
  - `claude-3-5-sonnet-20241022`
  - `claude-3-5-sonnet-20240620`
- **Claude 3.5 Haiku** (`claude-3-5-haiku-*`)
  - `claude-3-5-haiku-20241022`
- **Claude 3.7 Sonnet** (`claude-3-7-sonnet-*`)
  - `claude-3-7-sonnet-20250219`
- **Claude 4 Opus** (`claude-opus-4-*`)
  - `claude-opus-4-20250514`
- **Claude 4 Sonnet** (`claude-sonnet-4-*`)
  - `claude-sonnet-4-20250514`
- **Claude 4.1 Opus** (`claude-opus-4-1-*`)
  - `claude-opus-4-1-20250805`

**Implementation**: Anthropic models use search result injection rather than a tools array. Search results are added to the context.

### OpenAI Models (Including Groq-Hosted)
Modern OpenAI models support web search through the `web_search_preview` tool:

#### Native OpenAI Models
- **GPT-4.1 Family**
  - `gpt-4.1`
  - `gpt-4.1-mini`
  - `gpt-4.1-vision`
- **O-Series Models** (Reasoning models with extended thinking)
  - `o4-mini`
  - `o3-pro`
  - `o3`
  - `o3-mini`
  - `o1`
  - `o1-mini`

#### OpenAI Models Hosted on Groq
These are OpenAI-compatible models running on Groq's hardware:
- Same models as above when accessed through Groq provider
- Use Groq's `web_search` tool format instead of OpenAI's format

**Implementation**: Use `web_search_preview` tool with location context.

### Groq Models
Models hosted on Groq infrastructure support web search:

#### Llama Models
- **Llama 3.3** (`llama-3.3-70b-versatile`)
- **Llama 4 Preview Models**
  - `meta-llama/llama-4-maverick-17b-128e-instruct`
  - `meta-llama/llama-4-scout-17b-16e-instruct`

#### Specialized Models on Groq
- **Qwen 3** (`qwen/qwen3-32b`) - Advanced reasoning and multilingual
- **Kimi K2** (`moonshotai/kimi-k2-instruct`) - Advanced MoE model

**Implementation**: Use Groq's `web_search` tool with `enabled: true`.

### xAI Grok Models
Grok models support live web search:

- **Grok 4** (`grok-4-latest`, `grok-4`)
- **Grok 3** (`grok-3`, `grok-3-mini`, `grok-3-fast`)

**Implementation**: Use `live_search` tool for real-time information.

## Models WITHOUT Web Search Support

### Google Gemini Models
Currently, Gemini models don't have direct web search tool support in our implementation:
- `gemini-2.5-pro`
- `gemini-2.5-flash`
- `gemini-2.5-flash-lite`
- `gemini-2.0-flash`

*Note: Google has different search integration mechanisms that could be implemented separately.*

### Legacy OpenAI Models
Older GPT models don't support web search:
- `gpt-4-turbo`
- `gpt-4`
- `gpt-3.5-turbo`

## Implementation Details

### Tool Configuration by Provider

```python
# Anthropic (Claude 3.5+, 3.7, 4, 4.1)
tools = [{
    "type": "search_result_injection",
    "enabled": True
}]

# OpenAI (GPT-4.1, O-series)
tools = [{
    "type": "web_search_preview",
    "user_location": {
        "type": "approximate",
        "country": "US"
    },
    "search_context_size": "high"
}]

# Groq (Llama 3.3+, Qwen, Kimi)
tools = [{
    "type": "web_search",
    "enabled": True
}]

# xAI/Grok (Grok 3, 4)
tools = [{
    "type": "live_search",
    "enabled": True
}]
```

### Model Detection Logic

The enhanced agent executor checks model names to determine web search support:

```python
def _get_tools_for_provider(self, provider: str, model: Optional[str] = None):
    if provider == "anthropic":
        # Check for Claude 3.5+, 3.7, 4, 4.1
        if any(v in model for v in ["claude-3-5", "claude-3-7", "claude-4", "claude-opus-4"]):
            return search_tools
            
    elif provider == "openai":
        # Check for GPT-4.1, O-series
        if any(v in model for v in ["gpt-4.1", "o4", "o3", "o1"]):
            return search_tools
            
    elif provider == "groq":
        # Check for Llama 3.3+, Qwen, Kimi
        if any(v in model for v in ["llama-3.3", "llama-4", "qwen", "kimi"]):
            return search_tools
            
    elif provider == "grok":
        # Check for Grok 3, 4
        if any(v in model for v in ["grok-3", "grok-4"]):
            return search_tools
```

## Usage Examples

### With Web Search Enabled Model
```python
# Claude 4.1 with web search
result = await executor.execute_agent_task(
    agent_type="developer",
    prompt="What's the latest React version?",
    provider="anthropic",
    model="claude-opus-4-1-20250805",
    enable_web_search=True  # Will work!
)
```

### With Non-Web Search Model
```python
# Gemini (no web search support)
result = await executor.execute_agent_task(
    agent_type="developer",
    prompt="What's the latest React version?",
    provider="google",
    model="gemini-2.5-pro",
    enable_web_search=True  # Will be ignored
)
```

## Summary

**Total Models with Web Search**: ~30 models
- Anthropic: 6+ models (Claude 3.5+, 3.7, 4, 4.1)
- OpenAI: 9+ models (GPT-4.1, O-series)
- Groq: 6+ models (Llama 3.3+, Qwen, Kimi)
- xAI/Grok: 6+ models (Grok 3, 4)

**Models without Web Search**: ~7 models
- Google Gemini: 4 models
- Legacy OpenAI: 3+ models

This enables the Monkey Coder system to provide current, accurate information for the majority of its supported models.