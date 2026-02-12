"""
Pytest configuration and fixtures for the routing system tests.
"""

import pytest
import sys
from pathlib import Path

# Add the package root to the Python path
package_root = Path(__file__).parent.parent
sys.path.insert(0, str(package_root))

# (pytest_plugins moved to project root conftest to satisfy pytest deprecation)


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
        "cost_effective": ["gpt-4.1-mini", "claude-3.5-haiku"],
        "high_capability": ["gpt-4.1", "claude-4-opus", "claude-4-sonnet"],
        "reasoning_focused": ["gpt-4.1", "claude-4-opus", "claude-4-sonnet"],
        "fast_response": ["gpt-4.1-mini", "claude-haiku-4-5", "gemini-2.5-flash"],
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


# pytest.ini configuration
def pytest_addoption(parser):
    parser.addini("asyncio_mode", "auto")
