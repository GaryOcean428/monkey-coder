#!/usr/bin/env python3
"""
Test script to verify environment variable loading
"""
import os
import sys
from pathlib import Path

# Add the packages directory to the path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "core"))

from monkey_coder.config.env_config import get_config

def test_environment_loading():
    """Test if environment variables are loaded correctly"""
    print("Testing environment variable loading...")

    # Load configuration
    config = get_config(env_file=".env.local")

    # Check AI provider keys
    ai_keys = {
        "OpenAI": bool(config.ai_providers.openai_api_key),
        "Anthropic": bool(config.ai_providers.anthropic_api_key),
        "Google": bool(config.ai_providers.google_api_key),
        "Groq": bool(config.ai_providers.groq_api_key),
        "Grok": bool(config.ai_providers.grok_api_key)
    }

    print("\nAI Provider Configuration:")
    for provider, has_key in ai_keys.items():
        status = "✅ Configured" if has_key else "❌ Missing"
        print(f"  {provider}: {status}")

    # Get configuration summary
    summary = config.get_config_summary()
    print(f"\nConfiguration Summary:")
    print(f"  Environment: {summary['environment']}")
    print(f"  Debug: {summary['debug']}")
    print(f"  AI Providers: {summary['ai_providers']}")

    # Validate configuration
    validation = config.validate_required_config()
    if validation['missing']:
        print(f"\n❌ Missing Configuration:")
        for item in validation['missing']:
            print(f"  - {item}")
    else:
        print(f"\n✅ All required configuration present")

    if validation['warnings']:
        print(f"\n⚠️  Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")

    return ai_keys

if __name__ == "__main__":
    test_environment_loading()
