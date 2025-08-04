# Model Update Summary

## Models Updated

Based on the requirements to use only modern models, the following updates have been made:

### OpenAI Models

- ✅ `gpt-4.1` - Latest flagship model with 1M token context
- ✅ `gpt-4.1-mini` - Efficient model for lightweight tasks
- ❌ Removed `gpt-4.1-turbo` (doesn't exist)

### Anthropic Models

- ✅ `claude-4-opus` - High capability Claude 4 variant
- ✅ `claude-4-sonnet` - Balanced Claude 4 variant
- ✅ `claude-3.7-sonnet` - Recent 3.x generation
- ✅ `claude-3.5-sonnet` - Stable 3.5 release
- ✅ `claude-3.5-haiku` - Fast variant
- ❌ Removed standalone `claude-4` (must specify opus or sonnet)

### Google Models

- ✅ `gemini-2.5-pro` - Latest pro model
- ✅ `gemini-2.5-flash` - Fast variant
- ✅ `gemini-2.0-pro` - Previous generation pro
- ✅ `gemini-2.0-flash` - Previous generation fast

### Qwen Models

- ✅ `qwen-coder-3-32b` - Largest Qwen Coder 3
- ✅ `qwen-coder-3-14b` - Medium size
- ✅ `qwen-coder-3-7b` - Standard size
- ✅ `qwen-coder-3-1.5b` - Small size
- ❌ Removed all `qwen4` models (don't exist yet)

### Grok Models

- ✅ `grok-4-latest` - Latest generation with automatic updates
- ✅ `grok-3` - Previous generation
- ❌ Removed turbo variants

### Moonshot Models

- ✅ `kimi-k2` - Single K2 model variant
- ❌ Removed size variants (32b, 14b, 7b)

## Files Updated

1. **packages/core/monkey_coder/models.py** [PROTECTED FILE - NO FUTURE MODIFICATIONS ALLOWED]
   - Updated `MODEL_REGISTRY` with correct model names
   - Added GROK and MOONSHOT to `ProviderType` enum
   - **WARNING**: This file is now STRICTLY PROTECTED and must not be modified without explicit approval

2. **packages/core/monkey_coder/providers/openai_adapter.py**
   - Updated `VALIDATED_MODELS` to include only gpt-4.1 and gpt-4.1-mini
   - Updated health check to use `gpt-4.1-mini` instead of outdated models
   - Removed references to non-existent gpt-4.1-turbo

## Validation

All model names have been validated against the Context7 MCP documentation to ensure they represent
actual available models from each provider.
