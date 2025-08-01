"""
Monkey Coder Agent System
Multi-agent architecture with quantum execution capabilities and communication protocol
"""

from .base_agent import BaseAgent, AgentCapability, AgentContext
from .orchestrator import AgentOrchestrator, AgentTask, AgentResult
from .communication import (
    AgentCommunicationProtocol, MessageBus, InMemoryMessageBus,
    AgentMessage, MessageType, MessagePriority,
    CollaborationRequest, CollaborationResponse,
    initialize_communication, get_communication_protocol, shutdown_communication
)
from .specialized import (
    CodeGeneratorAgent, FrontendAgent, BackendAgent, 
    DevOpsAgent, SecurityAgent
)

__all__ = [
    # Base components
    "BaseAgent",
    "AgentCapability", 
    "AgentContext",
    "AgentOrchestrator",
    "AgentTask",
    "AgentResult",
    
    # Communication protocol
    "AgentCommunicationProtocol",
    "MessageBus",
    "InMemoryMessageBus",
    "AgentMessage",
    "MessageType",
    "MessagePriority",
    "CollaborationRequest",
    "CollaborationResponse",
    "initialize_communication",
    "get_communication_protocol",
    "shutdown_communication",
    
    # Specialized agents
    "CodeGeneratorAgent",
    "FrontendAgent",
    "BackendAgent", 
    "DevOpsAgent",
    "SecurityAgent",
]
