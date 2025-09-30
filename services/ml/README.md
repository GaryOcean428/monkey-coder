# ML Inference Service

## ⚠️ Important: Service Purpose

This service is for **LOCAL model inference** only. It handles ML workloads that require torch/transformers.

**This is NOT for production AI API calls.** For production AI requests, the backend service directly calls the providers listed in `MODEL_MANIFEST.md`:

### Production AI Providers (See MODEL_MANIFEST.md)

**Use these for code generation, chat, and analysis:**
- **OpenAI**: gpt-5, gpt-4.1, o3, o3-mini, gpt-4.1-mini
- **Anthropic**: claude-opus-4-1-20250805, claude-sonnet-4-20250514
- **Google**: gemini-2.5-pro, gemini-2.5-flash
- **Groq**: llama-3.3-70b-versatile, qwen/qwen3-32b
- **xAI**: grok-4-latest, grok-code-fast-1 (optimized for code)

### What This ML Service IS For

1. **Local embeddings** - For semantic search and similarity
2. **Custom fine-tuned models** - If you train your own models
3. **Offline inference** - When API calls aren't suitable
4. **Special ML tasks** - Vector operations, clustering, etc.

### What This ML Service is NOT For

❌ Regular code generation (use grok-code-fast-1 or gpt-5)
❌ Chat completions (use claude-opus-4-1 or gpt-4.1)
❌ Code analysis (use o3-mini or claude-sonnet-4)

## Architecture

```
User Request
    ↓
Backend API
    ├─→ Production AI Providers (OpenAI, Anthropic, etc.) [MOST REQUESTS]
    └─→ ML Service (this service) [RARE - only for local inference]
```

## Why Separate Service?

The ML service includes **2.5GB+ of dependencies** (torch, CUDA, transformers). Keeping it separate means:

1. **Backend deploys in 2 minutes** (no ML deps)
2. **ML service only rebuilds when needed** (~25 min first time, then cached)
3. **Better memory isolation** (ML can use 4-8GB independently)
4. **Can scale to zero** when not in use

## Current Status

**Stub Implementation** - Currently returns placeholder responses.

To implement actual local inference:
1. Choose specific models to load (e.g., sentence-transformers for embeddings)
2. Load models in startup event handler
3. Implement inference endpoints
4. Update backend to route appropriate requests here

## Configuration

See `railpack.json` for deployment config.
See `requirements.txt` for dependencies (torch, transformers, etc.).