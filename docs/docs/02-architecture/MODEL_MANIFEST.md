# MODEL_MANIFEST.md - Canonical AI Model Registry

<!-- markdownlint-disable MD044 -->

> **CRITICAL: This is the SINGLE SOURCE OF TRUTH for all AI models in Monkey Coder**
>
> **Last Updated:** February 12, 2026
> **Version:** 3.0.0
> **Canonical JSON:** `artifacts/model_manifest.json`
> **Status:** ENFORCED - Any model not listed here will be rejected

## Live Documentation Links

Always verify model availability at these official sources:

- **OpenAI**: <https://developers.openai.com/api/docs/models>
- **Anthropic**: <https://platform.claude.com/docs/en/about-claude/models/overview>
- **Google**: <https://ai.google.dev/gemini-api/docs/models>
- **Groq**: <https://console.groq.com/docs/models>
- **xAI**: <https://docs.x.ai/docs/models>

## Valid Models by Provider

### OpenAI (20 Models)

**GPT-5.x Series (Latest):**

- `gpt-5.2` - Best model for coding and agentic tasks across industries (400K context, 128K output)
- `gpt-5.2-codex` - Agentic coding specialist with context compaction (400K context, 128K output)
- `gpt-5.2-pro` - Smarter and more precise responses (400K context, 128K output)
- `gpt-5.3-codex` - Latest Codex model, 25% faster than GPT-5.2-Codex (400K context, 128K output)
- `gpt-5.1` - Flagship GPT with 400K context and advanced reasoning
- `gpt-5` - Previous flagship with multimodal capabilities (200K context)
- `gpt-5-mini` - Faster, cost-efficient version of GPT-5
- `gpt-5-nano` - Fastest, most cost-efficient version of GPT-5

**GPT-4.1 Series (Production):**

- `gpt-4.1` - Smartest non-reasoning model (200K context)
- `gpt-4.1-mini` - Smaller, faster version of GPT-4.1 (1M context)
- `gpt-4.1-nano` - Fastest, most cost-efficient GPT-4.1 (1M context)

**Reasoning Models:**

- `o3-pro` - Version of o3 with more compute for better responses
- `o3` - Reasoning model for complex tasks
- `o3-mini` - Small model alternative to o3
- `o4-mini` - Fast, cost-efficient reasoning model
- `o3-deep-research` - Most powerful deep research model
- `o4-mini-deep-research` - Faster, more affordable deep research

**Open-Weight Models:**

- `gpt-oss-120b` - Most powerful open-weight model (Apache 2.0)
- `gpt-oss-20b` - Medium-sized open-weight model for low latency (Apache 2.0)

**DEPRECATED - DO NOT USE:**

- ~~gpt-4o~~ → Use `gpt-4.1`
- ~~gpt-4o-mini~~ → Use `gpt-4.1-mini`
- ~~gpt-4-turbo~~ → Use `gpt-4.1`
- ~~gpt-4~~ → Use `gpt-4.1`
- ~~gpt-3.5-turbo~~ → Use `gpt-4.1-nano`
- ~~o1-mini~~ → Use `o4-mini` (explicitly deprecated by OpenAI)
- ~~o1-preview~~ → Use `o3`

### Anthropic (5 Models - Claude 4.5/4.6 Series)

**Latest Models (February 2026):**

- `claude-opus-4-6` - Most intelligent model with adaptive thinking, 128K output, 1M context beta (DEFAULT)
- `claude-opus-4-5` - Premium model combining maximum intelligence with practical performance (alias: `claude-opus-4-5-20251101`)
- `claude-sonnet-4-5` - Smart model for complex agents and coding with computer use (alias: `claude-sonnet-4-5-20250929`)
- `claude-haiku-4-5` - Fastest model with near-frontier intelligence (alias: `claude-haiku-4-5-20251001`)

**DEPRECATED - DO NOT USE:**

- ~~claude-3-5-sonnet-*~~ → Use `claude-sonnet-4-5`
- ~~claude-3-5-haiku-*~~ → Use `claude-haiku-4-5`
- ~~claude-3-7-sonnet-*~~ → Use `claude-sonnet-4-5`
- ~~claude-opus-4-20250514~~ → Use `claude-opus-4-6`
- ~~claude-sonnet-4-20250514~~ → Use `claude-sonnet-4-5`
- ~~claude-opus-4-1-20250805~~ → Use `claude-opus-4-6`

### Google (6 Models - Gemini 2.5/3 Series)

**Gemini 3 (Preview):**

- `gemini-3-pro-preview` - Best for multimodal understanding, most powerful agentic model
- `gemini-3-flash-preview` - Most balanced model for speed, scale, and frontier intelligence
- `gemini-3-pro-image-preview` - Specialized for native image generation and editing

**Gemini 2.5 (Production):**

- `gemini-2.5-pro` - Advanced thinking model for complex reasoning (1M context)
- `gemini-2.5-flash` - Best price-performance for large-scale tasks (1M context)
- `gemini-2.5-flash-lite` - Fastest flash model for cost-efficiency and high throughput (1M context)

**DEPRECATED - DO NOT USE:**

- ~~gemini-2.0-flash~~ → Use `gemini-2.5-flash` (shutting down March 31, 2026)
- ~~gemini-1.5-pro~~ → Use `gemini-2.5-pro`
- ~~gemini-pro~~ → Use `gemini-2.5-flash`

### Groq (5 Models - Hardware Accelerated)

**Production Models:**

- `groq/compound` - AI system with built-in web search and code execution (~450 tps)
- `llama-3.3-70b-versatile` - Production-ready on Groq LPUs with ultra-fast inference (~280 tps)
- `llama-3.1-8b-instant` - Fast, lightweight production model (~750 tps)
- `gpt-oss-120b` - OpenAI open-weight 120B model on Groq (~500 tps)
- `gpt-oss-20b` - OpenAI open-weight 20B model on Groq

### xAI (8 Models - Grok Series)

**Grok 4.1 (Latest):**

- `grok-4.1-fast-reasoning` - Fast reasoning with 2M context window
- `grok-4.1-fast-non-reasoning` - Instant response for standard tasks (1M context)

**Grok 4 (Production):**

- `grok-4` - Reasoning model (no non-reasoning mode)

**Grok 3 (Production):**

- `grok-3` - Flagship model with vision and multimodal capabilities
- `grok-3-mini` - Smaller, faster version of Grok 3

**Specialized:**

- `grok-code-fast-1` - 314B MoE reasoning model optimized for agentic coding (256K context)

**DEPRECATED - DO NOT USE:**

- ~~grok-2~~ → Use `grok-3`
- ~~grok-4-latest~~ → Use `grok-4` (use canonical ID)

## Default Models

| Provider | Default Model | Rationale |
| -------- | ------------- | --------- |
| OpenAI | `gpt-5.2` | Latest flagship, best for coding |
| Anthropic | `claude-opus-4-6` | Latest and most capable per Anthropic docs |
| Google | `gemini-2.5-pro` | Best for complex reasoning |
| xAI | `grok-4` | Latest flagship |
| Groq | `llama-3.3-70b-versatile` | Best production model on Groq |

## Enforcement Mechanism

The `ModelManifestEnforcer` reads `artifacts/model_manifest.json` at startup:

```python
from monkey_coder.validators.enforce_manifest import ModelManifestEnforcer

enforcer = ModelManifestEnforcer()

# Validate a model
result = enforcer.validate_model("gpt-4-turbo")
# Returns: {"valid": False, "replacement": "gpt-4.1"}

# Auto-correct invalid models
model = enforcer.enforce_model("gpt-4-turbo")
# Returns: "gpt-4.1"
```

## Model Update Protocol

1. **Update `artifacts/model_manifest.json` FIRST** - add new models, update deprecations
2. **Update this file** to match the JSON
3. **Run validation** - `python -m monkey_coder.validators.enforce_manifest`
4. **Update tests** - ensure all tests use valid models

---

**This file mirrors `artifacts/model_manifest.json`. If they diverge, the JSON is authoritative.**

<!-- markdownlint-enable MD044 -->
