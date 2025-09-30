#!/usr/bin/env python3
"""
Test script to verify Claude 4.5 models are properly integrated.
This tests the MODEL_MANIFEST.md parsing, model validation, and alias resolution.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'packages', 'core'))

from monkey_coder.models.model_validator import ModelManifestValidator, validate_model, enforce_model_compliance
from monkey_coder.models import MODEL_REGISTRY, MODEL_ALIASES, DEFAULT_MODELS, ProviderType


def test_claude_45_integration():
    """Test Claude 4.5 model integration."""
    print("🧪 Testing Claude 4.5 Model Integration")
    print("=" * 50)

    # Test 1: Check if Claude 4.5 models are in the registry
    print("\n1. Testing MODEL_REGISTRY...")
    anthropic_models = MODEL_REGISTRY[ProviderType.ANTHROPIC]
    claude_45_models = [m for m in anthropic_models if "4.5" in m]

    expected_45_models = [
        "claude-4.5-sonnet-20250930",
        "claude-4.5-haiku-20250930"
    ]

    for model in expected_45_models:
        if model in anthropic_models:
            print(f"  ✅ {model} found in MODEL_REGISTRY")
        else:
            print(f"  ❌ {model} MISSING from MODEL_REGISTRY")

    # Test 2: Check default model
    print("\n2. Testing DEFAULT_MODELS...")
    default_anthropic = DEFAULT_MODELS[ProviderType.ANTHROPIC]
    if "4.5" in default_anthropic:
        print(f"  ✅ Default Anthropic model uses Claude 4.5: {default_anthropic}")
    else:
        print(f"  ❌ Default Anthropic model not Claude 4.5: {default_anthropic}")

    # Test 3: Test alias resolution
    print("\n3. Testing MODEL_ALIASES...")
    test_aliases = {
        "claude-3-5-sonnet-20241022": "claude-4.5-sonnet-20250930",
        "claude-3-5-haiku-20241022": "claude-4.5-haiku-20250930",
        "claude-sonnet-4-5-20250929": "claude-4.5-sonnet-20250930",
    }

    for old_model, expected_new in test_aliases.items():
        if old_model in MODEL_ALIASES:
            actual_new = MODEL_ALIASES[old_model]
            if actual_new == expected_new:
                print(f"  ✅ {old_model} -> {actual_new}")
            else:
                print(f"  ❌ {old_model} -> {actual_new} (expected {expected_new})")
        else:
            print(f"  ❌ Alias missing: {old_model}")

    # Test 4: Test model validator
    print("\n4. Testing ModelManifestValidator...")
    try:
        validator = ModelManifestValidator()

        # Test valid Claude 4.5 models
        for model in expected_45_models:
            is_valid, error, suggestion = validator.validate_model(model, "anthropic")
            if is_valid:
                print(f"  ✅ {model} validated successfully")
            else:
                print(f"  ❌ {model} validation failed: {error}")

        # Test deprecated model handling
        deprecated_models = [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-sonnet-4-5-20250929"
        ]

        for model in deprecated_models:
            is_valid, error, suggestion = validator.validate_model(model, "anthropic")
            if not is_valid and "4.5" in suggestion:
                print(f"  ✅ {model} deprecated -> suggests {suggestion}")
            else:
                print(f"  ❌ {model} handling incorrect. Valid: {is_valid}, Suggestion: {suggestion}")

    except Exception as e:
        print(f"  ❌ Validator test failed: {e}")

    # Test 5: Test enforcement compliance
    print("\n5. Testing enforce_model_compliance...")
    test_cases = [
        ("claude-3-5-sonnet-20241022", "claude-4.5-sonnet-20250930"),
        ("claude-3-5-haiku-20241022", "claude-4.5-haiku-20250930"),
        ("claude-4.5-sonnet-20250930", "claude-4.5-sonnet-20250930"),  # Should stay the same
    ]

    for input_model, expected_output in test_cases:
        try:
            result = enforce_model_compliance(input_model, "anthropic")
            if result == expected_output:
                print(f"  ✅ {input_model} -> {result}")
            else:
                print(f"  ❌ {input_model} -> {result} (expected {expected_output})")
        except Exception as e:
            print(f"  ❌ Enforcement failed for {input_model}: {e}")

    print("\n" + "=" * 50)
    print("✅ Claude 4.5 integration test completed!")


if __name__ == "__main__":
    test_claude_45_integration()