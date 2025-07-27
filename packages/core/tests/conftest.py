"""
Pytest configuration and fixtures for the routing system tests.
"""

import pytest
import sys
import os
from pathlib import Path

# Add the package root to the Python path
package_root = Path(__file__).parent.parent
sys.path.insert(0, str(package_root))

# Test configuration
pytest_plugins = []


@pytest.fixture
def sample_prompts():
    """Fixture providing sample prompts for testing."""
    return {
        "trivial": "Hello world",
        "simple": "Write a function to add two numbers",
        "moderate": "Create a user authentication system with login and logout",
        "complex": "Design a distributed microservices architecture with scalability and performance optimization",
        "critical": "Implement a comprehensive machine learning pipeline with distributed training, neural network optimization, concurrent processing, async I/O, performance profiling, security hardening, and threading",
        "debug": "Fix this error: TypeError: 'int' object is not callable",
        "security": "Audit this authentication system for vulnerabilities",
        "architecture": "Design the overall system architecture",
        "performance": "Optimize the performance of this algorithm",
        "documentation": "Document this API endpoint",
    }


@pytest.fixture
def slash_commands():
    """Fixture providing slash command test cases."""
    return {
        "/dev": "developer",
        "/arch": "architect", 
        "/security": "security_analyst",
        "/test": "tester",
        "/docs": "technical_writer",
        "/review": "reviewer",
        "/perf": "performance_expert",
    }


@pytest.fixture
def expected_models():
    """Fixture providing expected model selections for different scenarios."""
    return {
        "cost_effective": ["gpt-4o-mini", "claude-3-5-haiku-20241022"],
        "high_capability": ["gpt-4o", "claude-3-5-sonnet-20241022", "o1-preview"],
        "reasoning_focused": ["o1-preview", "gpt-4o", "claude-3-5-sonnet-20241022"],
        "fast_response": ["gpt-4o-mini", "claude-3-5-haiku-20241022", "gemini-2.0-flash-exp"],
    }


# Configure pytest markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "routing: mark test as routing system test"
    )
    config.addinivalue_line(
        "markers", "complexity: mark test as complexity analysis test"
    )
    config.addinivalue_line(
        "markers", "persona: mark test as persona selection test"
    )
