"""
Model Validator - Single Source of Truth for AI Models

This module ensures that ONLY models defined in MODEL_MANIFEST.md are used.
It provides real-time validation against provider documentation and prevents
AI agents from reverting to outdated models.

CRITICAL: This is the ONLY place where model names should be validated.
All other code MUST use this validator to ensure model compliance.
"""

import os
import re
import json
import hashlib
import logging
from typing import Any, Dict, List, Optional, Set, Tuple
import aiohttp
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class ModelManifestValidator:
    """
    Enforces MODEL_MANIFEST.md as the canonical source of truth for all AI models.

    This validator:
    1. Parses MODEL_MANIFEST.md for the official model list
    2. Validates all model usage against this list
    3. Optionally checks provider documentation for model availability
    4. Caches validation results with TTL
    5. Provides clear error messages when outdated models are used
    """

    # Provider documentation URLs for live validation
    PROVIDER_DOCS = {
        "openai": "https://platform.openai.com/docs/models",
        "anthropic": "https://docs.anthropic.com/en/docs/models",
        "google": "https://ai.google.dev/gemini-api/docs/models",
        "groq": "https://console.groq.com/docs/models",
        "xai": "https://docs.x.ai/api/models"
    }

    # Known deprecated models that AI agents keep suggesting
    DEPRECATED_MODELS = {
        # OpenAI deprecated
        "gpt-4-turbo", "gpt-4-turbo-preview", "gpt-4-0125-preview",
        "gpt-4-1106-preview", "gpt-4-vision-preview",
        "gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106", "gpt-3.5-turbo",
        "text-davinci-003", "text-davinci-002",
        "gpt-4o", "gpt-4o-mini", "gpt-4",
        "o1", "o1-mini", "o1-preview",
        "codex-mini-latest",

        # Anthropic deprecated
        "claude-2.1", "claude-2.0", "claude-instant-1.2",
        "claude-3-opus-20240229", "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-3-5-sonnet-20241022", "claude-3-5-sonnet-20240620",
        "claude-3-5-haiku-20241022", "claude-3-7-sonnet-20250219",
        "claude-opus-4-20250514", "claude-sonnet-4-20250514",
        "claude-opus-4-1-20250805",

        # Google deprecated
        "gemini-1.0-pro", "gemini-1.5-pro-001",
        "gemini-pro", "gemini-pro-vision",
        "gemini-2.0-flash", "gemini-2.0-flash-lite",
        "palm-2", "bard",

        # xAI deprecated
        "grok-4-latest", "grok-3-fast", "grok-3-mini-fast", "grok-2",

        # Common AI hallucinations
        "gpt-5-turbo", "claude-4",
        "gpt-4.5", "gemini-1.75"
    }

    def __init__(self, manifest_path: Optional[str] = None, enable_live_validation: bool = False):
        """
        Initialize the validator.

        Args:
            manifest_path: Path to MODEL_MANIFEST.md (auto-detects if not provided)
            enable_live_validation: Whether to check provider docs in real-time
        """
        self.manifest_path = manifest_path or self._find_manifest()
        self.enable_live_validation = enable_live_validation
        self._model_cache: Dict[str, Set[str]] = {}
        self._cache_time: Optional[datetime] = None
        self._cache_ttl = timedelta(hours=1)  # Refresh cache every hour
        self._manifest_hash: Optional[str] = None

    def _find_manifest(self) -> str:
        """Find MODEL_MANIFEST.md in the project structure, preferring docs/ if present."""
        root_candidate = Path(__file__).resolve().parents[4]
        candidates = [
            # Prefer docs folder in current working dir or repo root
            Path("docs") / "MODEL_MANIFEST.md",
            root_candidate / "docs" / "MODEL_MANIFEST.md",
            # Fallbacks
            Path("MODEL_MANIFEST.md"),
            root_candidate / "MODEL_MANIFEST.md",
        ]

        for path in candidates:
            if path.exists():
                logger.info(f"Found MODEL_MANIFEST at: {path}")
                return str(path.resolve())

        raise FileNotFoundError(
            "MODEL_MANIFEST.md not found! This file is REQUIRED for model validation. "
            "Please add docs/MODEL_MANIFEST.md or MODEL_MANIFEST.md to the repository."
        )

    def _parse_manifest(self) -> Dict[str, Set[str]]:
        """
        Parse MODEL_MANIFEST.md to extract the canonical model list.

        Returns:
            Dict mapping provider names to sets of valid model names
        """
        with open(self.manifest_path, 'r') as f:
            content = f.read()

        # Calculate hash to detect changes
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if content_hash != self._manifest_hash:
            logger.info("MODEL_MANIFEST.md has changed, refreshing cache")
            self._manifest_hash = content_hash
            self._model_cache.clear()

        models = {
            "openai": set(),
            "anthropic": set(),
            "google": set(),
            "groq": set(),
            "xai": set()
        }

        current_provider = None
        in_model_section = False

        for line in content.split('\n'):
            line = line.strip()

            # Detect provider sections
            if '## OpenAI' in line or '### OpenAI' in line:
                current_provider = 'openai'
                in_model_section = True
            elif '## Anthropic' in line or '### Anthropic' in line:
                current_provider = 'anthropic'
                in_model_section = True
            elif '## Google' in line or '### Google' in line:
                current_provider = 'google'
                in_model_section = True
            elif '## Groq' in line or '### Groq' in line:
                current_provider = 'groq'
                in_model_section = True
            elif '## xAI' in line or '### xAI' in line:
                current_provider = 'xai'
                in_model_section = True
            elif line.startswith('#'):
                # New section, reset
                in_model_section = False
                current_provider = None

            # Extract model names
            if in_model_section and current_provider and line.startswith('- `'):
                # Parse model name from markdown list
                match = re.search(r'`([^`]+)`', line)
                if match:
                    model_name = match.group(1)
                    models[current_provider].add(model_name)
                    logger.debug(f"Found {current_provider} model: {model_name}")

        return models

    def get_valid_models(self, provider: Optional[str] = None, force_refresh: bool = False) -> Dict[str, Set[str]]:
        """
        Get the list of valid models from MODEL_MANIFEST.md.

        Args:
            provider: Optional provider to filter by
            force_refresh: Force cache refresh

        Returns:
            Dictionary of provider -> set of valid model names
        """
        # Serve from cache if valid
        if (
            not force_refresh
            and self._model_cache
            and self._cache_time is not None
            and datetime.now() - self._cache_time < self._cache_ttl
        ):
            if provider:
                return {provider: self._model_cache.get(provider, set())}
            return self._model_cache

        # Refresh cache by parsing the manifest
        self._model_cache = self._parse_manifest()
        self._cache_time = datetime.now()

        if provider:
            return {provider: self._model_cache.get(provider, set())}
        return self._model_cache

    def validate_model(self, model: str, provider: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate a model name against MODEL_MANIFEST.md.

        Args:
            model: The model name to validate
            provider: The provider name

        Returns:
            Tuple of (is_valid, error_message, suggested_alternative)
        """
        valid_models = self.get_valid_models(provider)
        provider_models = valid_models.get(provider, set())

        # Check if model is valid
        if model in provider_models:
            return True, None, None

        # Check if it's a known deprecated model
        if model in self.DEPRECATED_MODELS:
            suggestion = self._suggest_alternative(model, provider, provider_models)
            error = (
                f"❌ DEPRECATED MODEL: '{model}' is outdated and no longer available.\n"
                f"This model was deprecated and should not be used.\n"
                f"✅ Suggested alternative: {suggestion}\n"
                f"📚 Valid {provider} models from MODEL_MANIFEST.md:\n" +
                "\n".join(f"  - {m}" for m in sorted(provider_models)[:5])
            )
            return False, error, suggestion

        # Unknown model
        suggestion = self._suggest_alternative(model, provider, provider_models)
        error = (
            f"❌ INVALID MODEL: '{model}' is not in MODEL_MANIFEST.md.\n"
            f"This model is not recognized as a valid {provider} model.\n"
            f"✅ Suggested alternative: {suggestion}\n"
            f"📚 Valid {provider} models from MODEL_MANIFEST.md:\n" +
            "\n".join(f"  - {m}" for m in sorted(provider_models)[:5])
        )
        return False, error, suggestion

    def _suggest_alternative(self, invalid_model: str, provider: str, valid_models: Set[str]) -> str:
        """
        Suggest an alternative model based on the invalid model name.

        Args:
            invalid_model: The invalid model name
            provider: The provider name
            valid_models: Set of valid models for this provider

        Returns:
            Suggested alternative model name
        """
        # Provider-specific suggestions
        if provider == "openai":
            if "o1" in invalid_model or "o3" in invalid_model or "o4" in invalid_model:
                return "o3"  # Latest reasoning model
            elif "gpt-4" in invalid_model:
                return "gpt-4.1"  # Latest GPT-4
            elif "gpt-3.5" in invalid_model or "turbo" in invalid_model:
                return "gpt-4.1-nano"  # Fast, affordable
            return "gpt-5.2"  # Default to latest

        elif provider == "anthropic":
            if "opus" in invalid_model:
                return "claude-opus-4-6"  # Latest Opus
            elif "sonnet" in invalid_model:
                return "claude-sonnet-4-5"  # Latest Sonnet
            elif "haiku" in invalid_model:
                return "claude-haiku-4-5"  # Latest Haiku
            return "claude-sonnet-4-5"  # Default

        elif provider == "google":
            if "flash-lite" in invalid_model:
                return "gemini-2.5-flash-lite"
            elif "flash" in invalid_model:
                return "gemini-2.5-flash"
            elif "pro" in invalid_model:
                return "gemini-2.5-pro"
            return "gemini-2.5-flash"  # Default to Flash

        elif provider == "groq":
            if "llama" in invalid_model:
                return "llama-3.3-70b-versatile"
            return "llama-3.3-70b-versatile"  # Default

        elif provider == "xai":
            return "grok-4"  # Latest Grok

        # Fallback: return first valid model
        return sorted(valid_models)[0] if valid_models else "unknown"

    async def check_provider_docs(self, provider: str) -> Optional[List[str]]:
        """
        Check provider documentation for latest model list (optional).

        Args:
            provider: Provider name to check

        Returns:
            List of models found in docs, or None if check fails
        """
        if not self.enable_live_validation:
            return None

        url = self.PROVIDER_DOCS.get(provider)
        if not url:
            return None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        await response.text()
                        # Parse models from docs (provider-specific parsing needed)
                        logger.info(f"Successfully fetched {provider} docs from {url}")
                        # This would need provider-specific parsing logic
                        return None
        except Exception as e:
            logger.warning(f"Could not fetch {provider} docs: {e}")
            return None

    def enforce_compliance(self, model: str, provider: str) -> str:
        """
        Enforce MODEL_MANIFEST.md compliance by replacing invalid models.

        Args:
            model: Requested model name
            provider: Provider name

        Returns:
            Valid model name (original if valid, replacement if not)
        """
        is_valid, error, suggestion = self.validate_model(model, provider)

        if is_valid:
            return model

        # Log the violation
        logger.error(f"MODEL COMPLIANCE VIOLATION: {error}")

        # Return suggested alternative
        suggestion_str = suggestion or "unknown"
        logger.info(f"AUTO-CORRECTING: '{model}' -> '{suggestion_str}'")
        return suggestion_str

    def get_manifest_info(self) -> Dict[str, Any]:
        """
        Get information about the MODEL_MANIFEST.md file.

        Returns:
            Dictionary with manifest metadata
        """
        stat = os.stat(self.manifest_path)
        models = self.get_valid_models()

        return {
            "path": self.manifest_path,
            "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "size": stat.st_size,
            "hash": self._manifest_hash,
            "total_models": sum(len(m) for m in models.values()),
            "providers": list(models.keys()),
            "model_counts": {k: len(v) for k, v in models.items()},
            "cache_time": self._cache_time.isoformat() if self._cache_time else None,
            "documentation_urls": self.PROVIDER_DOCS
        }


# Global singleton instance
_validator_instance: Optional[ModelManifestValidator] = None


def get_validator() -> ModelManifestValidator:
    """Get the global validator instance."""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = ModelManifestValidator()
    return _validator_instance


def validate_model(model: str, provider: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Convenience function to validate a model.

    Args:
        model: Model name to validate
        provider: Provider name

    Returns:
        Tuple of (is_valid, error_message, suggested_alternative)
    """
    return get_validator().validate_model(model, provider)


def enforce_model_compliance(model: str, provider: str) -> str:
    """
    Convenience function to enforce model compliance.

    Args:
        model: Requested model name
        provider: Provider name

    Returns:
        Valid model name (original if valid, replacement if not)
    """
    return get_validator().enforce_compliance(model, provider)


# Example usage and testing
if __name__ == "__main__":

    # Test the validator
    validator = ModelManifestValidator()

    # Test cases
    test_cases = [
        ("gpt-4-turbo", "openai"),  # Deprecated
        ("gpt-5.2", "openai"),  # Valid
        ("claude-3-opus-20240229", "anthropic"),  # Deprecated
        ("claude-opus-4-6", "anthropic"),  # Valid
        ("gemini-pro", "google"),  # Deprecated
        ("gemini-2.5-flash", "google"),  # Valid
        ("grok-4", "xai"),  # Valid
        ("llama-3.3-70b-versatile", "groq"),  # Valid
    ]

    print("MODEL VALIDATION TEST RESULTS")
    print("=" * 60)

    for model, provider in test_cases:
        is_valid, error, suggestion = validator.validate_model(model, provider)
        print(f"\nModel: {model} ({provider})")
        if not is_valid:
            print(f"Suggestion: {suggestion}")
            print(error)

    print("\n" + "=" * 60)
    print("MANIFEST INFO")
    print(json.dumps(validator.get_manifest_info(), indent=2))