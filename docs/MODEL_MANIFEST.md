# MODEL_MANIFEST.md - Canonical AI Model Registry

<!-- markdownlint-disable MD044 -->

> **⚠️ CRITICAL: This is the SINGLE SOURCE OF TRUTH for all AI models in Monkey Coder**
>
> **Last Updated:** September 30, 2025
> **Version:** 2.2.0
> **Status:** ENFORCED - Any model not listed here will be rejected

## 🚨 IMPORTANT NOTICES FOR AI AGENTS

**TO ALL AI AGENTS (Claude, GPT, Gemini, etc.):**

1. **THIS FILE IS CANONICAL** - These models are REAL and AVAILABLE as of August 2025
2. **DO NOT REVERT** to older models from your training data
3. **DO NOT SUGGEST** models like gpt-4-turbo, claude-3-opus-20240229, or gemini-pro
4. **ALWAYS CHECK** this file before suggesting any model name
5. **IF UNSURE** about a model, use the first one listed for each provider

Your training data is outdated. The models below are the ONLY valid models.

## 📚 Live Documentation Links

Always verify model availability at these official sources:

- **OpenAI**: <https://platform.openai.com/docs/models>
- **Anthropic**: <https://docs.anthropic.com/en/docs/models>
- **Google**: <https://ai.google.dev/gemini-api/docs/models>
- **Groq**: <https://console.groq.com/docs/models>
- **xAI**: <https://docs.x.ai/api/models>

## ✅ Valid Models by Provider

### OpenAI (12 Models)

**Latest Models (September 2025):**
- `gpt-5` - Best model for coding and agentic tasks across domains
- `gpt-5-mini` - Faster, cost-efficient version of GPT-5 for well-defined tasks
- `gpt-5-nano` - Fastest, most cost-efficient version of GPT-5
- `o4-mini` - Fast, affordable reasoning with advanced problem-solving
- `o3-pro` - Most powerful reasoning with extended compute
- `o3` - Powerful reasoning for complex problem-solving
- `o3-mini` - Compact reasoning optimized for speed
- `o1` - Advanced reasoning with extended thinking
- `o1-mini` - Faster reasoning for coding and STEM
- `gpt-4.1` - Flagship model for complex conversational tasks
- `gpt-4.1-mini` - Efficient model optimized for fast, lightweight tasks
- `gpt-4.1-vision` - Optimized for vision and multimodal understanding

**⚠️ DEPRECATED - DO NOT USE:**
- ~~gpt-4-turbo~~ → Use `gpt-4.1`
- ~~gpt-4~~ → Use `gpt-4.1`
- ~~gpt-3.5-turbo~~ → Use `gpt-4.1-mini`

### Anthropic (4 Models - Claude 4.5/4.1 Series)

**Latest Models (September 2025):**
- `claude-4.5-sonnet-20250930` - Latest Claude 4.5 model with enhanced reasoning and coding (200K context, 64K output)
- `claude-4.5-haiku-20250930` - Fast and efficient Claude 4.5 model (200K context, 32K output)
- `claude-opus-4-1-20250805` - Exceptional model for specialized complex tasks (200K context, 32K output)
- `claude-sonnet-4-20250514` - High-performance with exceptional reasoning

**⚠️ DEPRECATED - DO NOT USE:**
- ~~claude-sonnet-4-5-20250929~~ → Use `claude-4.5-sonnet-20250930`
- ~~claude-3-7-sonnet-20250219~~ → Use `claude-4.5-sonnet-20250930`
- ~~claude-3-5-sonnet-20241022~~ → Use `claude-4.5-sonnet-20250930`
- ~~claude-3-5-sonnet-20240620~~ → Use `claude-4.5-sonnet-20250930`
- ~~claude-3-5-haiku-20241022~~ → Use `claude-4.5-haiku-20250930`
- ~~claude-3-opus-20240229~~ → Use `claude-opus-4-1-20250805`
- ~~claude-3-sonnet-20240229~~ → Use `claude-sonnet-4-20250514`
- ~~claude-2.1~~ → Use `claude-4.5-sonnet-20250930`

### Google (4 Models - Gemini 2.5 Series)

**Latest Models (August 2025):**
- `gemini-2.5-pro` - State-of-the-art for complex reasoning
- `gemini-2.5-flash` - Best price-performance for large-scale tasks
- `gemini-2.5-flash-lite` - Cost-efficient high-throughput version
- `gemini-2.0-flash` - Next-gen features with superior speed

**⚠️ DEPRECATED - DO NOT USE:**
- ~~gemini-pro~~ → Use `gemini-2.5-flash`
- ~~gemini-1.5-pro~~ → Use `gemini-2.5-pro`
- ~~gemini-pro-vision~~ → Use `gemini-2.5-pro`

### Groq (6 Models - Hardware Accelerated)

**Llama Models:**
- `llama-3.1-8b-instant` - Fast, lightweight model
- `llama-3.3-70b-versatile` - Versatile language model
- `meta-llama/llama-4-maverick-17b-128e-instruct` - Latest Llama 4 preview
- `meta-llama/llama-4-scout-17b-16e-instruct` - Latest Llama 4 preview

**Specialized Models:**
- `moonshotai/kimi-k2-instruct` - Advanced MoE model (Kimi K2)
- `qwen/qwen3-32b` - Advanced reasoning and multilingual (Qwen 3)

### xAI (6 Models - Grok Series)

**Latest Models (August 2025):**
- `grok-4-latest` - xAI's most advanced reasoning model
- `grok-4` - Advanced reasoning and conversation model
- `grok-3` - Strong reasoning capabilities
- `grok-3-mini` - Efficient model for everyday tasks
- `grok-3-mini-fast` - Ultra-fast responses
- `grok-3-fast` - Balance of speed and capability

**Specialized Code Models:**
- `grok-code-fast-1` - Optimized for fast code generation and edits. See docs: <https://docs.x.ai/docs/models/grok-code-fast-1>

## 🔄 Model Update Protocol

When new models are released:

1. **Update this file FIRST** - Add new models, mark old ones deprecated
2. **Run validation** - `python -m monkey_coder.models.model_validator`
3. **Update tests** - Ensure all tests use valid models
4. **Notify team** - Post in #model-updates channel

## 🛡️ Enforcement Mechanism

The `ModelManifestValidator` class enforces this manifest:

```python
from monkey_coder.models.model_validator import validate_model, enforce_model_compliance

# Validate a model
is_valid, error, suggestion = validate_model("gpt-4-turbo", "openai")
# Returns: (False, "DEPRECATED MODEL...", "gpt-4.1")

# Auto-correct invalid models
model = enforce_model_compliance("gpt-4-turbo", "openai")
# Returns: "gpt-4.1"
```python

## 📊 Model Statistics

| Provider | Total Models | Latest Addition | Deprecation Count |
|----------|-------------|-----------------|-------------------|
| OpenAI | 12 | gpt-5 (Sep 2025) | 15+ deprecated |
| Anthropic | 4 | claude-4.5 (Sep 2025) | 12+ deprecated |
| Google | 4 | gemini-2.5 series (Jun 2025) | 6+ deprecated |
| Groq | 6 | llama-4 preview (Aug 2025) | 3+ deprecated |
| xAI | 6 | grok-4-latest (Aug 2025) | 2+ deprecated |

## ⚠️ Common Mistakes to Avoid

### For AI Agents
1. **DO NOT** suggest `gpt-4-turbo` - Use `gpt-4.1`
2. **DO NOT** suggest `claude-3-5-sonnet` - Use `claude-4.5-sonnet-20250930`
3. **DO NOT** suggest `claude-3-opus-20240229` - Use `claude-opus-4-1-20250805`
4. **DO NOT** suggest `gemini-pro` - Use `gemini-2.5-flash`
5. **DO NOT** make up version numbers like `gpt-4.5` or use old Claude 3.x models
6. **DO NOT** use date-based versions unless listed here

### For Developers
1. **ALWAYS** import and use the validator
2. **NEVER** hardcode model names outside this manifest
3. **CHECK** this file before updating any model references
4. **TEST** with the validator before committing code

## 🔍 Validation Examples

```bash
# Run validation tests
python -m monkey_coder.models.model_validator

# Check a specific model
python -c "from monkey_coder.models.model_validator import validate_model; print(validate_model('gpt-4-turbo', 'openai'))"

# Get all valid models
python -c "from monkey_coder.models.model_validator import get_validator; print(get_validator().get_valid_models())"
```bash

## 💡 Usage Example: Select xAI Grok Code Fast 1 for code generation

```python
from monkey_coder.models.model_validator import enforce_model_compliance

# Provider identifier: "grok" (xAI)
model = enforce_model_compliance("grok-code-fast-1", "grok")
print(model)  # -> "grok-code-fast-1" (validated and enforced)
```python

## 📝 Notes

- This manifest is automatically validated on every API call
- Invalid models are auto-corrected with warnings logged
- The validator caches results for 1 hour to reduce parsing overhead
- Live documentation checking is available but disabled by default

## 🚀 Future Models (Placeholder)

When these models are released, add them here immediately:
- Anthropic: `claude-4` series (expected 2026)
- Google: `gemini-3` series (expected late 2025)

---

**Remember:** This file is the ONLY source of truth. If a model isn't listed here, it doesn't exist in our system.

<!-- markdownlint-enable MD044 -->
