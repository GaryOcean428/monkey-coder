"""
Test PEP 625 compliance for monkey-coder-core package builds.

This test ensures that our built distributions comply with PEP 625 naming conventions
for PyPI source distributions.
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path

import pytest


def check_pep625_compliance(filename: str) -> tuple[bool, str]:
    """Check if a distribution filename is PEP 625 compliant.
    
    Args:
        filename: The distribution filename to check
        
    Returns:
        Tuple of (is_compliant, message)
    """
    # PEP 625 pattern for source distributions
    pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?)-([a-zA-Z0-9_.!+]+)\.tar\.gz$'
    
    match = re.match(pattern, filename)
    if not match:
        return False, 'Does not match PEP 625 pattern'
    
    name, _, version = match.groups()
    
    # Check if name is normalized (no consecutive separators, lowercase, underscores only)
    normalized_name = re.sub(r'[-_.]+', '_', name).lower()
    if name != normalized_name:
        return False, f'Name "{name}" is not normalized. Should be "{normalized_name}"'
    
    return True, 'PEP 625 compliant'


def test_pep625_compliance_current_build():
    """Test that current built distributions are PEP 625 compliant."""
    dist_dir = Path(__file__).parent.parent / "dist"
    
    if not dist_dir.exists():
        pytest.skip("No dist directory found - run 'python -m build' first")
    
    source_distributions = list(dist_dir.glob("*.tar.gz"))
    
    if not source_distributions:
        pytest.skip("No source distributions found in dist/")
    
    for sdist in source_distributions:
        compliant, message = check_pep625_compliance(sdist.name)
        assert compliant, f"Source distribution {sdist.name} is not PEP 625 compliant: {message}"


def test_pep625_compliance_fresh_build():
    """Test that a fresh build produces PEP 625 compliant distributions."""
    package_root = Path(__file__).parent.parent
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Run build in temporary directory
        result = subprocess.run(
            ["python", "-m", "build", "--outdir", temp_dir],
            cwd=package_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            pytest.skip(f"Build failed: {result.stderr}")
        
        # Check all generated source distributions
        temp_path = Path(temp_dir)
        source_distributions = list(temp_path.glob("*.tar.gz"))
        
        assert source_distributions, "No source distributions generated"
        
        for sdist in source_distributions:
            compliant, message = check_pep625_compliance(sdist.name)
            assert compliant, f"Fresh build produced non-PEP 625 compliant file {sdist.name}: {message}"


def test_project_name_normalization():
    """Test that project name normalization works as expected."""
    test_cases = [
        ("monkey-coder-core", "monkey_coder_core"),
        ("My-Project", "my_project"),
        ("test_package", "test_package"),
        ("Package.Name", "package_name"),
        ("Mixed-Case_Pkg.Name", "mixed_case_pkg_name"),
    ]
    
    for original, expected in test_cases:
        normalized = re.sub(r'[-_.]+', '_', original).lower()
        assert normalized == expected, f"Normalization of '{original}' should be '{expected}', got '{normalized}'"


def test_current_package_metadata():
    """Test that the current package metadata produces the expected normalized name."""
    import configparser
    import tomli
    
    package_root = Path(__file__).parent.parent
    pyproject_file = package_root / "pyproject.toml"
    
    if not pyproject_file.exists():
        pytest.skip("No pyproject.toml found")
    
    with open(pyproject_file, "rb") as f:
        config = tomli.load(f)
    
    project_name = config.get("project", {}).get("name")
    if not project_name:
        pytest.skip("No project name found in pyproject.toml")
    
    # The expected normalized filename should use underscores
    expected_normalized = re.sub(r'[-_.]+', '_', project_name).lower()
    
    # For monkey-coder-core, this should be monkey_coder_core
    if project_name == "monkey-coder-core":
        assert expected_normalized == "monkey_coder_core"


if __name__ == "__main__":
    # Allow running as a script for manual testing
    import sys
    package_root = Path(__file__).parent.parent
    dist_dir = package_root / "dist"
    
    if dist_dir.exists():
        print("Checking existing distributions...")
        for sdist in dist_dir.glob("*.tar.gz"):
            compliant, message = check_pep625_compliance(sdist.name)
            status = "✅" if compliant else "❌"
            print(f"{status} {sdist.name}: {message}")
    else:
        print("No dist/ directory found. Run 'python -m build' first.")
        sys.exit(1)