"""
Setup script for monkey-coder-core package.

This file provides setuptools compatibility for the package.
Modern builds use pyproject.toml (PEP 517/518), but this file
ensures compatibility with various pip/uv installation scenarios.
"""
from setuptools import setup

# All configuration is in pyproject.toml (PEP 517/518 compliant)
# This minimal setup.py provides setuptools compatibility
setup()
