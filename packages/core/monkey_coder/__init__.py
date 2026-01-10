"""
Monkey Coder Core - Python orchestration package

This package provides the core functionality for the Monkey Coder project,
including AI model integration, code generation, and analysis capabilities.
"""

__version__ = "1.2.0"

from .generator import CodeGenerator
from .analyzer import CodeAnalyzer

# Make quantum import optional for deployment (requires heavy ML dependencies)
try:
    from . import quantum
    __all__ = ["CodeGenerator", "CodeAnalyzer", "quantum"]
except ImportError:
    # Continue without quantum module if ML dependencies are not available
    # This allows deployment with lighter requirements-deploy.txt
    import warnings
    warnings.warn("Quantum module not available - ML dependencies not installed", ImportWarning)
    __all__ = ["CodeGenerator", "CodeAnalyzer"]
