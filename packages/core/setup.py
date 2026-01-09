"""
Setup script for monkey-coder-core package.

This file provides setuptools compatibility for editable installs (-e flag).
Modern builds use pyproject.toml (PEP 517/518), but this ensures compatibility
with uv pip and Railway deployment.
"""
from setuptools import setup

# All configuration is in pyproject.toml
# This file just enables editable installs
setup()
