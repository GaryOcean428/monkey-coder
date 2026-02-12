"""
Canonical Model Manifest Loader — Single Source of Truth.

This module loads ``artifacts/model_manifest.json`` and exposes every
piece of model metadata the rest of the codebase needs.  **No other file
should hardcode model IDs, pricing, capabilities, or deprecation info.**

Usage::

    from monkey_coder.manifest import (
        get_models,              # all active models
        get_models_for_provider, # e.g. get_models_for_provider("openai")
        get_model,               # single model by ID
        get_default_model,       # default model for a provider
        get_deprecated_models,   # deprecation → replacement mapping
        get_aliases,             # alias → canonical ID mapping
        is_valid_model,          # bool check
        resolve_model,           # alias / deprecated → canonical
        PROVIDER_DEFAULTS,       # dict[str, str]
    )
"""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Locate the manifest JSON
# ---------------------------------------------------------------------------
_MANIFEST_SEARCH_PATHS = [
    Path(__file__).resolve().parents[3] / "artifacts" / "model_manifest.json",
    Path(__file__).resolve().parents[4] / "artifacts" / "model_manifest.json",
    Path.cwd() / "artifacts" / "model_manifest.json",
]

_manifest_path: Path | None = None
for _p in _MANIFEST_SEARCH_PATHS:
    if _p.exists():
        _manifest_path = _p
        break

if _manifest_path is None:
    logger.warning(
        "model_manifest.json not found in any expected location. "
        "Searched: %s",
        [str(p) for p in _MANIFEST_SEARCH_PATHS],
    )


# ---------------------------------------------------------------------------
# Raw loader (cached)
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _load_raw() -> dict[str, Any]:
    """Load and cache the raw manifest JSON."""
    if _manifest_path is None:
        logger.error("Cannot load manifest — file not found")
        return {"models": [], "deprecations": []}
    with open(_manifest_path, encoding="utf-8") as fh:
        data: dict[str, Any] = json.load(fh)
    logger.info("Loaded %d models from %s", len(data.get("models", [])), _manifest_path)
    return data


def reload() -> None:
    """Force-reload the manifest (e.g. after hot-editing the JSON)."""
    _load_raw.cache_clear()
    _build_indexes.cache_clear()
    logger.info("Manifest cache cleared — will reload on next access")


# ---------------------------------------------------------------------------
# Indexes built once from the raw data
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _build_indexes() -> dict[str, Any]:
    raw = _load_raw()
    models_list: list[dict[str, Any]] = raw.get("models", [])

    by_id: dict[str, dict[str, Any]] = {}
    by_provider: dict[str, list[dict[str, Any]]] = {}
    aliases: dict[str, str] = {}
    deprecated: dict[str, dict[str, Any]] = {}

    for m in models_list:
        mid = m["id"]
        provider = m.get("provider", "unknown")
        by_id[mid] = m
        by_provider.setdefault(provider, []).append(m)

        # If the entry carries an ``alias_for`` key, it means *this* id is
        # the short alias and the value is the dated canonical form.
        # We store the reverse too so callers can look up either direction.
        if "alias_for" in m:
            aliases[mid] = m["alias_for"]

    for dep in raw.get("deprecations", []):
        dep_id = dep["id"]
        replacements = dep.get("replacement_ids", [])
        deprecated[dep_id] = {
            "replacement": replacements[0] if replacements else None,
            "replacements": replacements,
            "note": dep.get("note", ""),
        }

    return {
        "by_id": by_id,
        "by_provider": by_provider,
        "aliases": aliases,
        "deprecated": deprecated,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_models() -> dict[str, dict[str, Any]]:
    """Return *all* models keyed by ID."""
    return _build_indexes()["by_id"]


def get_models_for_provider(provider: str) -> list[dict[str, Any]]:
    """Return models for a given provider name (e.g. ``"openai"``)."""
    return _build_indexes()["by_provider"].get(provider, [])


def get_model_ids_for_provider(provider: str) -> list[str]:
    """Return just the model IDs for a provider."""
    return [m["id"] for m in get_models_for_provider(provider)]


def get_model(model_id: str) -> dict[str, Any] | None:
    """Look up a single model by its canonical ID."""
    return _build_indexes()["by_id"].get(model_id)


def get_aliases() -> dict[str, str]:
    """Return alias → canonical-ID mapping derived from ``alias_for`` fields."""
    return _build_indexes()["aliases"]


def get_deprecated_models() -> dict[str, dict[str, Any]]:
    """Return deprecated-ID → replacement info mapping."""
    return _build_indexes()["deprecated"]


def is_valid_model(model_id: str) -> bool:
    """Return ``True`` if *model_id* exists in the manifest (active or alias)."""
    idx = _build_indexes()
    return model_id in idx["by_id"]


def is_deprecated(model_id: str) -> bool:
    """Return ``True`` if *model_id* appears in the deprecations list."""
    return model_id in _build_indexes()["deprecated"]


def resolve_model(model_id: str) -> str:
    """Resolve an alias or deprecated ID to its current canonical model.

    Resolution order:
    1. If *model_id* exists as an active model, return it as-is.
    2. If *model_id* is a known alias, return the canonical form.
    3. If *model_id* is deprecated, return the first replacement.
    4. Otherwise return *model_id* unchanged (caller decides how to fail).
    """
    idx = _build_indexes()

    # 1. Already canonical
    if model_id in idx["by_id"]:
        return model_id

    # 2. Alias
    if model_id in idx["aliases"]:
        return idx["aliases"][model_id]

    # 3. Deprecated
    dep = idx["deprecated"].get(model_id)
    if dep and dep.get("replacement"):
        return dep["replacement"]

    # 4. Wildcard deprecations (e.g. "claude-3-5-sonnet-*")
    for pattern, dep_info in idx["deprecated"].items():
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            if model_id.startswith(prefix) and dep_info.get("replacement"):
                return dep_info["replacement"]

    return model_id


# ---------------------------------------------------------------------------
# Provider defaults — the "best current model" per provider
# ---------------------------------------------------------------------------
PROVIDER_DEFAULTS: dict[str, str] = {
    "openai": "gpt-5.2",
    "anthropic": "claude-opus-4-6",
    "google": "gemini-2.5-pro",
    "groq": "llama-3.3-70b-versatile",
    "xai": "grok-4",
}


def get_default_model(provider: str) -> str:
    """Return the default model ID for *provider*."""
    return PROVIDER_DEFAULTS.get(provider, PROVIDER_DEFAULTS.get("openai", "gpt-5.2"))


# ---------------------------------------------------------------------------
# Convenience: pricing helpers
# ---------------------------------------------------------------------------

def get_pricing(model_id: str) -> dict[str, float] | None:
    """Return ``{"input": …, "output": …}`` per-1M-token pricing, or None."""
    m = get_model(model_id)
    if m is None:
        return None
    return {
        "input": float(m.get("cost_input", 0)),
        "output": float(m.get("cost_output", 0)),
    }


def get_context_limit(model_id: str) -> int | None:
    """Return the context window size for *model_id*."""
    m = get_model(model_id)
    return m.get("context_limit") if m else None


def get_capabilities(model_id: str) -> list[str]:
    """Return the capability tags for *model_id*."""
    m = get_model(model_id)
    return m.get("capabilities", []) if m else []


# ---------------------------------------------------------------------------
# Startup validation (optional — call from app entrypoint)
# ---------------------------------------------------------------------------

def validate_manifest() -> bool:
    """Quick sanity-check that the manifest loaded correctly."""
    models = get_models()
    if not models:
        logger.error("Manifest validation FAILED — no models loaded")
        return False

    # Verify every default actually exists
    ok = True
    for provider, default_id in PROVIDER_DEFAULTS.items():
        if default_id not in models:
            logger.error(
                "Default model %r for provider %r is missing from manifest",
                default_id,
                provider,
            )
            ok = False

    count = len(models)
    providers = {m.get("provider") for m in models.values()}
    logger.info(
        "Manifest OK — %d models across %d providers (%s)",
        count,
        len(providers),
        ", ".join(sorted(providers)),
    )
    return ok
