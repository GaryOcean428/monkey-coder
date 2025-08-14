# Model Compliance System Documentation

## The Problem

AI agents (including Claude, GPT, and others) consistently revert to outdated model names from their training data, causing constant issues:

- Using `gpt-4-turbo` instead of `gpt-4.1`
- Suggesting `claude-3-opus-20240229` instead of `claude-opus-4-20250514`
- Referencing `gemini-pro` instead of `gemini-2.5-flash`

This happens because:
1. AI training data is frozen at a point in time
2. Models are released faster than AI agents are retrained
3. There's no way for AI agents to know what models currently exist

## The Solution

We've implemented a comprehensive model compliance system with multiple layers of protection:

### 1. MODEL_MANIFEST.md - Single Source of Truth

The `MODEL_MANIFEST.md` file is the canonical list of all valid models. It includes:
- Current valid models for each provider
- Deprecated model mappings
- Live documentation links
- Clear instructions for AI agents

### 2. Context7 Integration - Real-Time Updates

Context7 MCP server provides real-time documentation about available models:

```python
from monkey_coder.config.mcp_config import MCPConfig

# Hardcoded Context7 configuration
CONTEXT7_URL = "https://mcp.context7.com/mcp"
```

This allows us to:
- Query current model availability in real-time
- Detect newly released models automatically
- Validate against official documentation

### 3. Model Validator - Enforcement Layer

The `ModelManifestValidator` class enforces compliance:

```python
from monkey_coder.models.model_validator import enforce_model_compliance

# Automatically corrects invalid models
model = enforce_model_compliance("gpt-4-turbo", "openai")
# Returns: "gpt-4.1"
```

### 4. Pre-Commit Hooks - Prevention

The `.githooks/pre-commit-model-check` script prevents committing invalid models:

```bash
# Runs automatically on git commit
python scripts/model_compliance_monitor.py --git

# Auto-fix violations
python scripts/model_compliance_monitor.py --fix
```

### 5. Base Provider Integration

All provider adapters inherit from `BaseProvider` which automatically validates models:

```python
class BaseProvider(ABC):
    def validate_and_fix_model(self, model: str) -> str:
        """Auto-corrects invalid model names."""
        return enforce_model_compliance(model, self.provider_type)
```

## How It Works

### Flow Diagram

```
User Request with Model Name
           ↓
    BaseProvider.generate_completion()
           ↓
    validate_and_fix_model()
           ↓
    ┌──────────────┐
    │ Is Valid?    │
    └──────────────┘
         ↓     ↓
        Yes    No
         ↓     ↓
      Use   Context7 Check (if available)
         ↓     ↓
            Fallback to MODEL_MANIFEST.md
               ↓
          Auto-correct to valid model
               ↓
          Log warning
               ↓
     Proceed with valid model
```

### Validation Priority

1. **Context7** (if available) - Real-time documentation
2. **MODEL_MANIFEST.md** - Local canonical list
3. **Auto-correction** - Replace with suggested alternative

## Configuration

### Settings (.claude/settings.json)

```json
{
  "model_compliance": {
    "enforce": true,
    "use_context7": true,
    "auto_fix": true
  },
  "mcp": {
    "servers": {
      "context7": {
        "url": "https://mcp.context7.com/mcp"
      }
    }
  }
}
```

### Environment Variables

```bash
# Override Context7 URL (for testing)
export CONTEXT7_URL="https://custom.context7.com/mcp"

# Disable Context7 (use local validation only)
export DISABLE_CONTEXT7=true
```

## Usage Examples

### For Developers

```python
# Import the validators
from monkey_coder.models.model_validator import validate_model
from monkey_coder.models.context7_validator import HybridModelValidator

# Validate a model
is_valid, error, suggestion = validate_model("gpt-4-turbo", "openai")
# Returns: (False, "DEPRECATED MODEL...", "gpt-4.1")

# Use hybrid validation (Context7 + local)
validator = HybridModelValidator()
is_valid, error, suggestion = await validator.validate_model("gemini-pro", "google")
```

### For AI Agents

**IMPORTANT INSTRUCTIONS FOR AI AGENTS:**

1. **ALWAYS** check `MODEL_MANIFEST.md` before suggesting any model
2. **NEVER** use these deprecated models:
   - `gpt-4-turbo` → Use `gpt-4.1`
   - `claude-3-opus-20240229` → Use `claude-opus-4-20250514`
   - `gemini-pro` → Use `gemini-2.5-flash`
3. **IF UNSURE**, use the first model listed for each provider
4. **REMEMBER** your training data is outdated - trust the manifest

### Command Line Tools

```bash
# Check entire codebase for violations
python scripts/model_compliance_monitor.py

# Check only staged files (for pre-commit)
python scripts/model_compliance_monitor.py --git

# Auto-fix violations
python scripts/model_compliance_monitor.py --fix

# Output as JSON (for CI/CD)
python scripts/model_compliance_monitor.py --json --ci
```

## Monitoring and Metrics

The system tracks:
- Model usage frequency
- Deprecation attempt rate
- Auto-correction frequency
- Context7 availability

Access metrics via:
```python
from monkey_coder.models.model_validator import get_validator

validator = get_validator()
info = validator.get_manifest_info()
print(info)
```

## Troubleshooting

### Common Issues

#### 1. Context7 Timeout
**Symptom:** Slow model validation
**Solution:** Reduce timeout or disable Context7:
```python
# Reduce timeout
validator = Context7ModelValidator(timeout_seconds=1)

# Disable Context7
export DISABLE_CONTEXT7=true
```

#### 2. MODEL_MANIFEST.md Not Found
**Symptom:** FileNotFoundError
**Solution:** Ensure file exists in project root or specify path:
```python
validator = ModelManifestValidator(manifest_path="/path/to/MODEL_MANIFEST.md")
```

#### 3. Auto-Correction Loop
**Symptom:** Model keeps getting corrected
**Solution:** Update your code to use the correct model name

## Best Practices

1. **Update Regularly**: Run `python scripts/sync_manifest.py` weekly
2. **Test Locally**: Use pre-commit hooks to catch issues early
3. **Monitor Logs**: Check for repeated correction patterns
4. **Document Changes**: Update MODEL_MANIFEST.md when new models release
5. **Trust the System**: Let auto-correction handle edge cases

## Future Enhancements

- [ ] Automatic MODEL_MANIFEST.md updates from Context7
- [ ] Model performance benchmarking
- [ ] Cost optimization based on model selection
- [ ] Version pinning for reproducibility
- [ ] Model capability matching

## Contributing

To add support for a new provider:

1. Add provider section to `MODEL_MANIFEST.md`
2. Update `PROVIDER_DOCS` in `model_validator.py`
3. Add provider-specific logic to `_suggest_alternative()`
4. Test with `python scripts/model_compliance_monitor.py`
5. Submit PR with test cases

## Summary

This multi-layered approach ensures:
- ✅ No deprecated models in production
- ✅ Automatic correction of AI agent mistakes
- ✅ Real-time validation against documentation
- ✅ Clear audit trail of model usage
- ✅ Future-proof as new models release

The system is designed to be invisible when everything works correctly, but provides clear guidance when issues arise.