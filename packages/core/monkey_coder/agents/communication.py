"""
Agent Communication Protocol for Multi-Agent Coordination
Enables inter-agent messaging, coordination, and collaborative task execution
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Set
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages agents can exchange"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    COLLABORATION_REQUEST = "collaboration_request"
    COLLABORATION_RESPONSE = "collaboration_response"
    STATUS_UPDATE = "status_update"
    RESOURCE_SHARING = "resource_sharing"
    KNOWLEDGE_SHARING = "knowledge_sharing"
    COORDINATION = "coordination"
    ERROR_NOTIFICATION = "error_notification"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class AgentMessage:
    """Message structure for agent communication"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    recipient_id: str = ""  # Can be "*" for broadcast
    message_type: MessageType = MessageType.STATUS_UPDATE
    priority: MessagePriority = MessagePriority.NORMAL
    subject: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None  # For request-response correlation
    reply_to: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationRequest:
    """Request for collaboration between agents"""
    requesting_agent: str
    task_description: str
    required_capabilities: Set[str]
    preferred_agents: List[str] = field(default_factory=list)
    deadline: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationResponse:
    """Response to collaboration request"""
    responding_agent: str
    request_id: str
    accepted: bool
    confidence_score: float
    estimated_time: Optional[int] = None  # minutes
    resource_availability: Dict[str, Any] = field(default_factory=dict)
    conditions: List[str] = field(default_factory=list)
    alternative_suggestions: List[str] = field(default_factory=list)


class MessageBus(ABC):
    """Abstract message bus for agent communication"""
    
    @abstractmethod
    async def publish(self, message: AgentMessage) -> bool:
        """Publish a message to the bus"""
        pass
    
    @abstractmethod
    async def subscribe(self, agent_id: str, callback: Callable[[AgentMessage], None]) -> None:
        """Subscribe to messages for an agent"""
        pass
    
    @abstractmethod
    async def unsubscribe(self, agent_id: str) -> None:
        """Unsubscribe agent from message bus"""
        pass


class InMemoryMessageBus(MessageBus):
    """In-memory implementation of message bus for development/testing"""
    
    def __init__(self):
        self.subscribers: Dict[str, Callable[[AgentMessage], None]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_history: List[AgentMessage] = []
        self.running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the message bus"""
        if not self.running:
            self.running = True
            self._task = asyncio.create_task(self._process_messages())
            logger.info("Message bus started")
    
    async def stop(self):
        """Stop the message bus"""
        if self.running:
            self.running = False
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
            logger.info("Message bus stopped")
    
    async def publish(self, message: AgentMessage) -> bool:
        """Publish a message to the bus"""
        try:
            await self.message_queue.put(message)
            self.message_history.append(message)
            logger.debug(f"Message published: {message.id} from {message.sender_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return False
    
    async def subscribe(self, agent_id: str, callback: Callable[[AgentMessage], None]) -> None:
        """Subscribe to messages for an agent"""
        self.subscribers[agent_id] = callback
        logger.debug(f"Agent {agent_id} subscribed to message bus")
    
    async def unsubscribe(self, agent_id: str) -> None:
        """Unsubscribe agent from message bus"""
        if agent_id in self.subscribers:
            del self.subscribers[agent_id]
            logger.debug(f"Agent {agent_id} unsubscribed from message bus")
    
    async def _process_messages(self):
        """Process messages from the queue"""
        while self.running:
            try:
                # Wait for message with timeout to allow graceful shutdown
                message = await asyncio.wait_for(
                    self.message_queue.get(), 
                    timeout=1.0
                )
                await self._deliver_message(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    async def _deliver_message(self, message: AgentMessage):
        """Deliver message to appropriate subscribers"""
        # Check if message has expired
        if message.expires_at and datetime.now() > message.expires_at:
            logger.warning(f"Message {message.id} expired, discarding")
            return
        
        # Deliver to specific recipient or broadcast
        if message.recipient_id == "*":
            # Broadcast to all subscribers except sender
            for agent_id, callback in self.subscribers.items():
                if agent_id != message.sender_id:
                    try:
                        await self._safe_callback(callback, message)
                    except Exception as e:
                        logger.error(f"Error delivering message to {agent_id}: {e}")
        else:
            # Deliver to specific recipient
            if message.recipient_id in self.subscribers:
                try:
                    callback = self.subscribers[message.recipient_id]
                    await self._safe_callback(callback, message)
                except Exception as e:
                    logger.error(f"Error delivering message to {message.recipient_id}: {e}")
            else:
                logger.warning(f"No subscriber found for recipient {message.recipient_id}")
    
    async def _safe_callback(self, callback: Callable[[AgentMessage], None], message: AgentMessage):
        """Safely execute callback with error handling"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(message)
            else:
                callback(message)
        except Exception as e:
            logger.error(f"Callback execution failed: {e}")
    
    def get_message_history(self, agent_id: Optional[str] = None) -> List[AgentMessage]:
        """Get message history, optionally filtered by agent"""
        if agent_id:
            return [msg for msg in self.message_history 
                   if msg.sender_id == agent_id or msg.recipient_id == agent_id]
        return self.message_history.copy()


class AgentCommunicationProtocol:
    """Protocol handler for agent communication"""
    
    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self.pending_requests: Dict[str, CollaborationRequest] = {}
        self.active_collaborations: Dict[str, Dict[str, Any]] = {}
        self.knowledge_cache: Dict[str, Any] = {}
    
    async def request_collaboration(
        self, 
        requesting_agent: str,
        task_description: str,
        required_capabilities: Set[str],
        preferred_agents: List[str] = None,
        deadline: datetime = None
    ) -> str:
        """Request collaboration from other agents"""
        request_id = str(uuid.uuid4())
        
        collaboration_request = CollaborationRequest(
            requesting_agent=requesting_agent,
            task_description=task_description,
            required_capabilities=required_capabilities,
            preferred_agents=preferred_agents or [],
            deadline=deadline
        )
        
        self.pending_requests[request_id] = collaboration_request
        
        # Send collaboration request message
        message = AgentMessage(
            sender_id=requesting_agent,
            recipient_id="*" if not preferred_agents else ",".join(preferred_agents),
            message_type=MessageType.COLLABORATION_REQUEST,
            priority=MessagePriority.HIGH,
            subject=f"Collaboration Request: {task_description[:50]}...",
            content={
                "request_id": request_id,
                "task_description": task_description,
                "required_capabilities": list(required_capabilities),
                "preferred_agents": preferred_agents,
                "deadline": deadline.isoformat() if deadline else None
            },
            correlation_id=request_id
        )
        
        await self.message_bus.publish(message)
        logger.info(f"Collaboration request {request_id} sent by {requesting_agent}")
        
        return request_id
    
    async def respond_to_collaboration(
        self,
        responding_agent: str,
        request_id: str,
        accepted: bool,
        confidence_score: float,
        estimated_time: int = None,
        conditions: List[str] = None
    ) -> bool:
        """Respond to a collaboration request"""
        if request_id not in self.pending_requests:
            logger.warning(f"Unknown collaboration request: {request_id}")
            return False
        
        request = self.pending_requests[request_id]
        
        response = CollaborationResponse(
            responding_agent=responding_agent,
            request_id=request_id,
            accepted=accepted,
            confidence_score=confidence_score,
            estimated_time=estimated_time,
            conditions=conditions or []
        )
        
        # Send collaboration response message
        message = AgentMessage(
            sender_id=responding_agent,
            recipient_id=request.requesting_agent,
            message_type=MessageType.COLLABORATION_RESPONSE,
            priority=MessagePriority.HIGH,
            subject=f"Collaboration Response: {'Accepted' if accepted else 'Declined'}",
            content={
                "request_id": request_id,
                "accepted": accepted,
                "confidence_score": confidence_score,
                "estimated_time": estimated_time,
                "conditions": conditions
            },
            correlation_id=request_id
        )
        
        await self.message_bus.publish(message)
        logger.info(f"Collaboration response sent by {responding_agent}: {'Accepted' if accepted else 'Declined'}")
        
        return True
    
    async def share_knowledge(
        self,
        sender_agent: str,
        knowledge_type: str,
        knowledge_data: Dict[str, Any],
        recipients: List[str] = None
    ) -> bool:
        """Share knowledge between agents"""
        knowledge_id = str(uuid.uuid4())
        
        # Store in knowledge cache
        self.knowledge_cache[knowledge_id] = {
            "type": knowledge_type,
            "data": knowledge_data,
            "sender": sender_agent,
            "timestamp": datetime.now()
        }
        
        # Send knowledge sharing message
        message = AgentMessage(
            sender_id=sender_agent,
            recipient_id="*" if not recipients else ",".join(recipients),
            message_type=MessageType.KNOWLEDGE_SHARING,
            priority=MessagePriority.NORMAL,
            subject=f"Knowledge Sharing: {knowledge_type}",
            content={
                "knowledge_id": knowledge_id,
                "knowledge_type": knowledge_type,
                "knowledge_data": knowledge_data
            }
        )
        
        await self.message_bus.publish(message)
        logger.info(f"Knowledge shared by {sender_agent}: {knowledge_type}")
        
        return True
    
    async def coordinate_task(
        self,
        coordinator_agent: str,
        task_id: str,
        participating_agents: List[str],
        coordination_strategy: str,
        task_details: Dict[str, Any]
    ) -> bool:
        """Coordinate task execution among multiple agents"""
        coordination_id = str(uuid.uuid4())
        
        # Create coordination entry
        self.active_collaborations[coordination_id] = {
            "coordinator": coordinator_agent,
            "task_id": task_id,
            "participants": participating_agents,
            "strategy": coordination_strategy,
            "details": task_details,
            "status": "initiated",
            "started_at": datetime.now()
        }
        
        # Send coordination message to all participants
        message = AgentMessage(
            sender_id=coordinator_agent,
            recipient_id=",".join(participating_agents),
            message_type=MessageType.COORDINATION,
            priority=MessagePriority.HIGH,
            subject=f"Task Coordination: {task_id}",
            content={
                "coordination_id": coordination_id,
                "task_id": task_id,
                "strategy": coordination_strategy,
                "task_details": task_details,
                "participants": participating_agents
            }
        )
        
        await self.message_bus.publish(message)
        logger.info(f"Task coordination {coordination_id} initiated by {coordinator_agent}")
        
        return True
    
    async def send_status_update(
        self,
        sender_agent: str,
        status: str,
        details: Dict[str, Any] = None
    ) -> bool:
        """Send status update to other agents"""
        message = AgentMessage(
            sender_id=sender_agent,
            recipient_id="*",
            message_type=MessageType.STATUS_UPDATE,
            priority=MessagePriority.LOW,
            subject=f"Status Update: {status}",
            content={
                "status": status,
                "details": details or {},
                "timestamp": datetime.now().isoformat()
            }
        )
        
        await self.message_bus.publish(message)
        logger.debug(f"Status update sent by {sender_agent}: {status}")
        
        return True
    
    def get_pending_requests(self, agent_id: str = None) -> List[CollaborationRequest]:
        """Get pending collaboration requests"""
        if agent_id:
            return [req for req in self.pending_requests.values() 
                   if agent_id in req.preferred_agents or not req.preferred_agents]
        return list(self.pending_requests.values())
    
    def get_knowledge_cache(self, knowledge_type: str = None) -> List[Dict[str, Any]]:
        """Get cached knowledge, optionally filtered by type"""
        if knowledge_type:
            return [data for data in self.knowledge_cache.values() 
                   if data["type"] == knowledge_type]
        return list(self.knowledge_cache.values())
    
    def get_active_collaborations(self) -> List[Dict[str, Any]]:
        """Get currently active collaborations"""
        return list(self.active_collaborations.values())


# Global communication protocol instance
_communication_protocol: Optional[AgentCommunicationProtocol] = None
_message_bus: Optional[MessageBus] = None


async def initialize_communication() -> AgentCommunicationProtocol:
    """Initialize the global communication protocol"""
    global _communication_protocol, _message_bus
    
    if _communication_protocol is None:
        _message_bus = InMemoryMessageBus()
        await _message_bus.start()
        _communication_protocol = AgentCommunicationProtocol(_message_bus)
        logger.info("Agent communication protocol initialized")
    
    return _communication_protocol


async def get_communication_protocol() -> AgentCommunicationProtocol:
    """Get the global communication protocol instance"""
    global _communication_protocol
    
    if _communication_protocol is None:
        return await initialize_communication()
    
    return _communication_protocol


async def shutdown_communication():
    """Shutdown the global communication protocol"""
    global _communication_protocol, _message_bus
    
    if _message_bus:
        await _message_bus.stop()
        _message_bus = None
    
    _communication_protocol = None
    logger.info("Agent communication protocol shutdown")