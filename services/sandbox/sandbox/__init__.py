"""
Monkey Coder Sandbox Service

Secure containerized environment for code execution and browser automation.
"""

__version__ = "1.0.0"
__author__ = "GaryOcean428"
__email__ = "gary@ocean428.dev"

from .main import app
from .e2b_integration import E2BSandboxManager
from .browserbase_integration import BrowserBaseSandboxManager
from .security import SecurityManager
from .monitoring import ResourceMonitor, SandboxMetrics

__all__ = [
    "app",
    "E2BSandboxManager", 
    "BrowserBaseSandboxManager",
    "SecurityManager",
    "ResourceMonitor",
    "SandboxMetrics"
]
