"""
Compliance facade for MODEL_MANIFEST.md enforcement.

This module avoids the Python package/module name conflict between
`monkey_coder/models.py` (module) and `monkey_coder/models/` (package)
by loading the canonical validator implementation from its file path.

Public API:
- validate_model(model, provider) -> (bool, error, suggestion)
- enforce_model_compliance(model, provider) -> str
- get_validator() -> ModelManifestValidator instance
- ModelManifestValidator (export alias)
- DEPRECATED_MODELS (export alias)
"""

from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
# No typing imports needed here

_loaded = False
_validator_mod = None  # type: ignore[var-annotated]
_validator_instance = None  # type: ignore[var-annotated]


def _load_validator_module():
    global _loaded, _validator_mod
    if _loaded and _validator_mod is not None:
        return _validator_mod

    path = Path(__file__).parent / "models" / "model_validator.py"
    if not path.exists():
        raise FileNotFoundError(f"model_validator.py not found at {path}")

    loader = SourceFileLoader("monkey_coder_model_validator", str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise ImportError("Could not create spec for model_validator")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    _validator_mod = module
    _loaded = True
    return module


essential_exports = ("ModelManifestValidator", "DEPRECATED_MODELS")


def get_validator():
    """Get a singleton validator instance from the loaded module."""
    global _validator_instance
    if _validator_instance is not None:
        return _validator_instance
    mod = _load_validator_module()
    _validator_instance = mod.ModelManifestValidator()  # type: ignore[attr-defined]
    return _validator_instance


def validate_model(model: str, provider: str):
    """Validate a model name against the manifest."""
    validator = get_validator()
    return validator.validate_model(model, provider)


def enforce_model_compliance(model: str, provider: str) -> str:
    """Return a compliant model name (auto-correct when needed)."""
    validator = get_validator()
    return validator.enforce_compliance(model, provider)


# Re-exports for backwards compatibility with existing imports in scripts/docs
mod = _load_validator_module()
ModelManifestValidator = getattr(mod, "ModelManifestValidator")
DEPRECATED_MODELS = getattr(mod, "DEPRECATED_MODELS", set())
