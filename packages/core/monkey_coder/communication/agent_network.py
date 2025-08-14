"""
Inter-Agent Communication Network for Coordinated Execution.

This module implements a sophisticated communication network that enables
agents to share information, coordinate actions, and achieve collective
intelligence similar to a well-coordinated orchestra.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Any, Optional, Set, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from collections import defaultdict, deque
import numpy as np

logger = logging.getLogger(__name__)

class MessageType(str, Enum):
    """Types of messages agents can exchange."""
    BROADCAST = "broadcast"  # Message to all agents
    UNICAST = "unicast"  # Message to specific agent
    MULTICAST = "multicast"  # Message to group of agents
    REQUEST = "request"  # Request for information/action
    RESPONSE = "response"  # Response to request
    NOTIFICATION = "notification"  # Status update
    COORDINATION = "coordination"  # Coordination directive
    SYNCHRONIZATION = "synchronization"  # Sync signal

class MessagePriority(str, Enum):
    """Message priority levels."""
    CRITICAL = "critical"  # Must be processed immediately
    HIGH = "high"  # Process as soon as possible
    NORMAL = "normal"  # Regular processing
    LOW = "low"  # Process when idle

@dataclass
class Message:
    """Represents a message in the communication network."""
    message_id: str = field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:8]}")
    sender: str = ""
    recipients: List[str] = field(default_factory=list)
    type: MessageType = MessageType.BROADCAST
    priority: MessagePriority = MessagePriority.NORMAL
    content: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    ttl: int = 10  # Time to live (hops)
    requires_ack: bool = False
    correlation_id: Optional[str] = None  # For request-response correlation

@dataclass
class AgentProfile:
    """Profile of an agent in the network."""
    agent_id: str
    agent_type: str  # developer, reviewer, architect, etc.
    capabilities: List[str] = field(default_factory=list)
    status: str = "idle"  # idle, busy, offline
    current_task: Optional[str] = None
    message_queue: deque = field(default_factory=lambda: deque(maxlen=100))
    subscriptions: Set[str] = field(default_factory=set)  # Topics subscribed to
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    
    @property
    def is_available(self) -> bool:
        """Check if agent is available for tasks."""
        return self.status in ["idle", "listening"]

@dataclass
class CommunicationChannel:
    """Communication channel between agents."""
    channel_id: str = field(default_factory=lambda: f"ch_{uuid.uuid4().hex[:8]}")
    participants: Set[str] = field(default_factory=set)
    channel_type: str = "direct"  # direct, group, broadcast
    bandwidth: float = 1.0  # Relative bandwidth (0.0 to 1.0)
    latency: float = 0.01  # Simulated latency in seconds
    reliability: float = 0.99  # Message delivery probability
    message_history: deque = field(default_factory=lambda: deque(maxlen=50))
    
    def can_transmit(self) -> bool:
        """Check if channel can transmit."""
        return np.random.random() < self.reliability

class ProtocolHandler:
    """Handles communication protocols between agents."""
    
    def __init__(self):
        """Initialize protocol handler."""
        self.protocols: Dict[str, Callable] = {
            'consensus': self._handle_consensus,
            'negotiation': self._handle_negotiation,
            'coordination': self._handle_coordination,
            'knowledge_sharing': self._handle_knowledge_sharing,
            'task_delegation': self._handle_task_delegation
        }
        
    async def execute_protocol(
        self,
        protocol_name: str,
        participants: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a communication protocol."""
        if protocol_name not in self.protocols:
            return {'error': f'Unknown protocol: {protocol_name}'}
        
        handler = self.protocols[protocol_name]
        return await handler(participants, context)
    
    async def _handle_consensus(
        self,
        participants: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle consensus protocol."""
        # Implement voting or agreement mechanism
        votes = {}
        proposal = context.get('proposal', {})
        
        for participant in participants:
            # Simulate voting (in practice, would query agents)
            vote = np.random.choice(['agree', 'disagree', 'abstain'], p=[0.6, 0.3, 0.1])
            votes[participant] = vote
        
        # Determine consensus
        agree_count = sum(1 for v in votes.values() if v == 'agree')
        consensus_reached = agree_count > len(participants) / 2
        
        return {
            'consensus': consensus_reached,
            'votes': votes,
            'proposal': proposal
        }
    
    async def _handle_negotiation(
        self,
        participants: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle negotiation protocol."""
        # Implement resource negotiation
        resource = context.get('resource', 'unknown')
        bids = {}
        
        for participant in participants:
            # Simulate bidding
            bid = np.random.uniform(0.1, 1.0)
            bids[participant] = bid
        
        # Determine winner
        winner = max(bids, key=bids.get)
        
        return {
            'resource': resource,
            'winner': winner,
            'bids': bids
        }
    
    async def _handle_coordination(
        self,
        participants: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle coordination protocol."""
        # Implement task coordination
        task = context.get('task', {})
        assignments = {}
        
        # Distribute subtasks
        subtasks = task.get('subtasks', [])
        for i, subtask in enumerate(subtasks):
            assigned_to = participants[i % len(participants)]
            assignments[subtask] = assigned_to
        
        return {
            'task': task,
            'assignments': assignments,
            'coordination_plan': 'distributed'
        }
    
    async def _handle_knowledge_sharing(
        self,
        participants: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle knowledge sharing protocol."""
        knowledge = context.get('knowledge', {})
        shared_knowledge = {}
        
        # Simulate knowledge exchange
        for participant in participants:
            # Each agent contributes knowledge
            contribution = {
                'source': participant,
                'data': f"knowledge_from_{participant}",
                'confidence': np.random.uniform(0.5, 1.0)
            }
            shared_knowledge[participant] = contribution
        
        return {
            'shared_knowledge': shared_knowledge,
            'integration_complete': True
        }
    
    async def _handle_task_delegation(
        self,
        participants: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle task delegation protocol."""
        task = context.get('task', {})
        delegations = []
        
        # Delegate based on capabilities (simplified)
        for participant in participants:
            delegation = {
                'agent': participant,
                'subtask': f"subtask_for_{participant}",
                'priority': np.random.choice(['high', 'normal', 'low']),
                'deadline': 'asap'
            }
            delegations.append(delegation)
        
        return {
            'task': task,
            'delegations': delegations
        }

class InterAgentNetwork:
    """
    Inter-agent communication network for coordinated execution.
    
    Implements a sophisticated communication infrastructure that enables
    agents to collaborate effectively like a well-coordinated team.
    """
    
    def __init__(self, enable_protocols: bool = True):
        """
        Initialize the communication network.
        
        Args:
            enable_protocols: Whether to enable communication protocols
        """
        self.agents: Dict[str, AgentProfile] = {}
        self.channels: Dict[str, CommunicationChannel] = {}
        self.message_bus: deque = deque()
        self.protocol_handler = ProtocolHandler() if enable_protocols else None
        
        # Network topology
        self.topology: Dict[str, Set[str]] = defaultdict(set)  # agent -> connected agents
        
        # Topic subscriptions for pub/sub
        self.topics: Dict[str, Set[str]] = defaultdict(set)  # topic -> subscribers
        
        # Message routing table
        self.routing_table: Dict[str, List[str]] = {}  # destination -> path
        
        # Network metrics
        self.message_count = 0
        self.successful_deliveries = 0
        self.failed_deliveries = 0
        
        # Running state
        self.is_running = False
        self.message_processor_task = None
    
    def register_agent(
        self,
        agent_id: str,
        agent_type: str,
        capabilities: List[str] = None
    ) -> AgentProfile:
        """Register an agent in the network."""
        agent = AgentProfile(
            agent_id=agent_id,
            agent_type=agent_type,
            capabilities=capabilities or []
        )
        
        self.agents[agent_id] = agent
        logger.info(f"Agent {agent_id} registered in network")
        
        return agent
    
    def create_channel(
        self,
        participants: List[str],
        channel_type: str = "direct"
    ) -> str:
        """Create a communication channel."""
        # Validate participants
        for participant in participants:
            if participant not in self.agents:
                raise ValueError(f"Agent {participant} not registered")
        
        channel = CommunicationChannel(
            participants=set(participants),
            channel_type=channel_type
        )
        
        self.channels[channel.channel_id] = channel
        
        # Update topology
        if channel_type == "direct" and len(participants) == 2:
            p1, p2 = participants
            self.topology[p1].add(p2)
            self.topology[p2].add(p1)
        elif channel_type == "group":
            for p1 in participants:
                for p2 in participants:
                    if p1 != p2:
                        self.topology[p1].add(p2)
        
        logger.info(f"Channel {channel.channel_id} created for {participants}")
        return channel.channel_id
    
    def subscribe_to_topic(self, agent_id: str, topic: str):
        """Subscribe an agent to a topic."""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not registered")
        
        self.topics[topic].add(agent_id)
        self.agents[agent_id].subscriptions.add(topic)
        
        logger.info(f"Agent {agent_id} subscribed to topic {topic}")
    
    async def send_message(
        self,
        sender: str,
        content: Any,
        recipients: Optional[List[str]] = None,
        type: MessageType = MessageType.BROADCAST,
        priority: MessagePriority = MessagePriority.NORMAL,
        requires_ack: bool = False
    ) -> str:
        """
        Send a message through the network.
        
        Args:
            sender: Sender agent ID
            content: Message content
            recipients: List of recipient agent IDs (None for broadcast)
            type: Message type
            priority: Message priority
            requires_ack: Whether acknowledgment is required
            
        Returns:
            Message ID
        """
        if sender not in self.agents:
            raise ValueError(f"Sender {sender} not registered")
        
        # Create message
        message = Message(
            sender=sender,
            recipients=recipients or [],
            type=type,
            priority=priority,
            content=content,
            requires_ack=requires_ack
        )
        
        # Add to message bus
        self.message_bus.append(message)
        self.message_count += 1
        
        # Process immediately if high priority
        if priority == MessagePriority.CRITICAL:
            await self._process_message(message)
        
        logger.debug(f"Message {message.message_id} sent from {sender}")
        return message.message_id
    
    async def request_response(
        self,
        sender: str,
        recipient: str,
        request: Dict[str, Any],
        timeout: float = 5.0
    ) -> Optional[Dict[str, Any]]:
        """
        Send a request and wait for response.
        
        Args:
            sender: Sender agent ID
            recipient: Recipient agent ID
            request: Request content
            timeout: Response timeout in seconds
            
        Returns:
            Response content or None if timeout
        """
        # Create request message
        request_id = await self.send_message(
            sender=sender,
            content=request,
            recipients=[recipient],
            type=MessageType.REQUEST,
            priority=MessagePriority.HIGH,
            requires_ack=True
        )
        
        # Wait for response
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < timeout:
            # Check for response in recipient's queue
            agent = self.agents.get(recipient)
            if agent:
                for msg in agent.message_queue:
                    if (msg.type == MessageType.RESPONSE and
                        msg.correlation_id == request_id):
                        return msg.content
            
            await asyncio.sleep(0.1)
        
        logger.warning(f"Request {request_id} timed out")
        return None
    
    async def broadcast(
        self,
        sender: str,
        content: Any,
        topic: Optional[str] = None
    ):
        """
        Broadcast a message to all agents or topic subscribers.
        
        Args:
            sender: Sender agent ID
            content: Message content
            topic: Optional topic for pub/sub
        """
        if topic:
            # Send to topic subscribers
            recipients = list(self.topics.get(topic, []))
        else:
            # Send to all agents except sender
            recipients = [a for a in self.agents.keys() if a != sender]
        
        await self.send_message(
            sender=sender,
            content=content,
            recipients=recipients,
            type=MessageType.BROADCAST,
            priority=MessagePriority.NORMAL
        )
    
    async def coordinate_task(
        self,
        coordinator: str,
        task: Dict[str, Any],
        participants: List[str]
    ) -> Dict[str, Any]:
        """
        Coordinate a task among multiple agents.
        
        Args:
            coordinator: Coordinating agent ID
            task: Task description
            participants: Participating agent IDs
            
        Returns:
            Coordination result
        """
        if not self.protocol_handler:
            return {'error': 'Protocols not enabled'}
        
        # Send coordination message
        coordination_msg = {
            'task': task,
            'coordinator': coordinator,
            'participants': participants
        }
        
        await self.send_message(
            sender=coordinator,
            content=coordination_msg,
            recipients=participants,
            type=MessageType.COORDINATION,
            priority=MessagePriority.HIGH
        )
        
        # Execute coordination protocol
        result = await self.protocol_handler.execute_protocol(
            'coordination',
            participants,
            {'task': task}
        )
        
        # Notify participants of assignments
        for participant, assignment in result.get('assignments', {}).items():
            await self.send_message(
                sender=coordinator,
                content={'assignment': assignment},
                recipients=[participant],
                type=MessageType.NOTIFICATION,
                priority=MessagePriority.NORMAL
            )
        
        return result
    
    async def achieve_consensus(
        self,
        initiator: str,
        proposal: Dict[str, Any],
        participants: List[str]
    ) -> Dict[str, Any]:
        """
        Achieve consensus among agents.
        
        Args:
            initiator: Initiating agent ID
            proposal: Proposal to reach consensus on
            participants: Participating agent IDs
            
        Returns:
            Consensus result
        """
        if not self.protocol_handler:
            return {'error': 'Protocols not enabled'}
        
        # Execute consensus protocol
        result = await self.protocol_handler.execute_protocol(
            'consensus',
            participants,
            {'proposal': proposal}
        )
        
        # Broadcast result
        await self.broadcast(
            sender=initiator,
            content={'consensus_result': result}
        )
        
        return result
    
    async def share_knowledge(
        self,
        agent_id: str,
        knowledge: Dict[str, Any],
        recipients: Optional[List[str]] = None
    ):
        """
        Share knowledge between agents.
        
        Args:
            agent_id: Sharing agent ID
            knowledge: Knowledge to share
            recipients: Optional specific recipients
        """
        if not recipients:
            # Share with all connected agents
            recipients = list(self.topology.get(agent_id, set()))
        
        # Package knowledge
        knowledge_package = {
            'source': agent_id,
            'knowledge': knowledge,
            'timestamp': datetime.now().isoformat()
        }
        
        await self.send_message(
            sender=agent_id,
            content=knowledge_package,
            recipients=recipients,
            type=MessageType.NOTIFICATION,
            priority=MessagePriority.NORMAL
        )
    
    async def synchronize_agents(self, agents: List[str]):
        """
        Synchronize a group of agents.
        
        Args:
            agents: List of agent IDs to synchronize
        """
        sync_signal = {
            'type': 'sync',
            'timestamp': datetime.now().isoformat(),
            'agents': agents
        }
        
        # Send sync signal to all agents
        for agent in agents:
            await self.send_message(
                sender='network',
                content=sync_signal,
                recipients=[agent],
                type=MessageType.SYNCHRONIZATION,
                priority=MessagePriority.HIGH
            )
        
        # Wait for all agents to acknowledge
        acks = set()
        timeout = 5.0
        start_time = asyncio.get_event_loop().time()
        
        while len(acks) < len(agents):
            if asyncio.get_event_loop().time() - start_time > timeout:
                logger.warning(f"Synchronization timeout, received {len(acks)}/{len(agents)} acks")
                break
            
            # Check for acknowledgments
            for agent_id in agents:
                agent = self.agents.get(agent_id)
                if agent and agent_id not in acks:
                    # Check if agent acknowledged (simplified)
                    if agent.status == 'synchronized':
                        acks.add(agent_id)
            
            await asyncio.sleep(0.1)
        
        logger.info(f"Synchronized {len(acks)}/{len(agents)} agents")
    
    async def _process_message(self, message: Message):
        """Process a single message."""
        # Route message to recipients
        if message.type == MessageType.BROADCAST:
            recipients = message.recipients or [a for a in self.agents.keys() if a != message.sender]
        else:
            recipients = message.recipients
        
        for recipient_id in recipients:
            recipient = self.agents.get(recipient_id)
            if recipient:
                # Check channel availability
                channel = self._find_channel(message.sender, recipient_id)
                
                if channel and channel.can_transmit():
                    # Simulate latency
                    await asyncio.sleep(channel.latency)
                    
                    # Deliver message
                    recipient.message_queue.append(message)
                    channel.message_history.append(message)
                    self.successful_deliveries += 1
                    
                    logger.debug(f"Message {message.message_id} delivered to {recipient_id}")
                else:
                    self.failed_deliveries += 1
                    logger.warning(f"Failed to deliver message {message.message_id} to {recipient_id}")
    
    async def _message_processor(self):
        """Background task to process messages."""
        while self.is_running:
            try:
                # Process messages by priority
                if self.message_bus:
                    # Sort by priority
                    sorted_messages = sorted(
                        self.message_bus,
                        key=lambda m: {
                            MessagePriority.CRITICAL: 0,
                            MessagePriority.HIGH: 1,
                            MessagePriority.NORMAL: 2,
                            MessagePriority.LOW: 3
                        }[m.priority]
                    )
                    
                    # Process highest priority message
                    if sorted_messages:
                        message = sorted_messages[0]
                        self.message_bus.remove(message)
                        await self._process_message(message)
                
                await asyncio.sleep(0.01)  # Small delay to prevent CPU spinning
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    def _find_channel(self, agent1: str, agent2: str) -> Optional[CommunicationChannel]:
        """Find channel between two agents."""
        for channel in self.channels.values():
            if agent1 in channel.participants and agent2 in channel.participants:
                return channel
        return None
    
    async def start(self):
        """Start the communication network."""
        self.is_running = True
        self.message_processor_task = asyncio.create_task(self._message_processor())
        logger.info("Inter-agent communication network started")
    
    async def stop(self):
        """Stop the communication network."""
        self.is_running = False
        if self.message_processor_task:
            self.message_processor_task.cancel()
            try:
                await self.message_processor_task
            except asyncio.CancelledError:
                pass
        logger.info("Inter-agent communication network stopped")
    
    def get_network_metrics(self) -> Dict[str, Any]:
        """Get network metrics and statistics."""
        active_agents = sum(1 for a in self.agents.values() if a.is_available)
        
        return {
            'total_agents': len(self.agents),
            'active_agents': active_agents,
            'total_channels': len(self.channels),
            'total_messages': self.message_count,
            'successful_deliveries': self.successful_deliveries,
            'failed_deliveries': self.failed_deliveries,
            'delivery_rate': self.successful_deliveries / max(self.message_count, 1),
            'topics': len(self.topics),
            'total_subscriptions': sum(len(subs) for subs in self.topics.values())
        }
    
    def visualize_network(self) -> str:
        """Generate ASCII visualization of network topology."""
        lines = []
        lines.append("Inter-Agent Network Topology")
        lines.append("=" * 40)
        
        for agent_id, connections in self.topology.items():
            agent = self.agents.get(agent_id)
            if agent:
                status = "●" if agent.is_available else "○"
                lines.append(f"{status} {agent_id} ({agent.agent_type})")
                
                for connected in connections:
                    lines.append(f"  └─> {connected}")
        
        lines.append("-" * 40)
        lines.append(f"Messages: {self.message_count} | Delivered: {self.successful_deliveries}")
        
        return "\n".join(lines)