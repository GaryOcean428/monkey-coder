"""Smoke tests for model registry and alias normalization.

These tests ensure the runtime `MODEL_REGISTRY` stays aligned with the
canonical `MODEL_MANIFEST.md` and that legacy identifiers normalize to the
approved canonical names.
"""

from monkey_coder.models import (
    ProviderType,
    get_available_models,
    MODEL_ALIASES,
    resolve_model,
)


def test_openai_models_presence():
    """OpenAI registry should include expected flagship and reasoning models."""
    models = get_available_models(ProviderType.OPENAI)[ProviderType.OPENAI.value]
    assert "gpt-4.1-vision" in models
    assert "o3-mini" in models


def test_anthropic_models_presence():
    """Anthropic registry should include Claude 4.5 Sonnet and Opus 4.1."""
    models = get_available_models(ProviderType.ANTHROPIC)[ProviderType.ANTHROPIC.value]
    assert "claude-sonnet-4-5-20250929" in models
    assert "claude-opus-4-1-20250805" in models


def test_google_models_presence():
    """Google registry should include Gemini 2.5/2.0 canonical model IDs."""
    models = get_available_models(ProviderType.GOOGLE)[ProviderType.GOOGLE.value]
    assert "gemini-2.5-pro" in models
    assert "gemini-2.5-flash" in models
    assert "gemini-2.5-flash-lite" in models
    assert "gemini-2.0-flash" in models


def test_grok_models_presence():
    """xAI registry should include Grok 4 and specialized Grok code model."""
    models = get_available_models(ProviderType.GROK)[ProviderType.GROK.value]
    assert "grok-4" in models
    assert "grok-code-fast-1" in models


def test_google_aliases_normalize():
    """Legacy Google prefixed IDs should normalize to canonical names."""
    # Ensure legacy prefixed IDs normalize to canonical names
    assert MODEL_ALIASES.get("models/gemini-2.5-flash") == "gemini-2.5-flash"
    assert MODEL_ALIASES.get("models/gemini-2.5-flash-lite") == "gemini-2.5-flash-lite"
    assert MODEL_ALIASES.get("models/gemini-2.0-flash") == "gemini-2.0-flash"

    # And resolve_model maps them
    assert resolve_model("models/gemini-2.5-flash", ProviderType.GOOGLE) == "gemini-2.5-flash"
    assert (
        resolve_model("models/gemini-2.5-flash-lite", ProviderType.GOOGLE)
        == "gemini-2.5-flash-lite"
    )
    assert resolve_model("models/gemini-2.0-flash", ProviderType.GOOGLE) == "gemini-2.0-flash"
