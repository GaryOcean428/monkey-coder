"""
Context management system for multi-turn conversations.
Using in-memory implementation to avoid system dependencies.
"""

# Only import the simple manager that doesn't require SQLite
from .simple_manager import (
    SimpleContextManager,
    SimpleMessage,
    SimpleConversation,
    get_simple_context_manager,
)

# Create compatibility aliases
ContextManager = SimpleContextManager
Message = SimpleMessage
Session = SimpleConversation

__all__ = [
    "ContextManager",
    "Session", 
    "Message",
    "SimpleContextManager",
    "SimpleMessage",
    "SimpleConversation",
    "get_simple_context_manager",
]
