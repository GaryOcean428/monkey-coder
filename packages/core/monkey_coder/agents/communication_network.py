"""
Inter-Agent Communication Network for Coordinated Execution.

This module implements a sophisticated communication network that enables
agents to share information, coordinate actions, and collectively solve
complex problems through collaborative intelligence.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Any, Optional, Set, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict, deque
import json
import numpy as np

logger = logging.getLogger(__name__)

class MessageType(str, Enum):
    """Types of messages in the communication network."""
    BROADCAST = "broadcast"  # Send to all agents
    UNICAST = "unicast"  # Send to specific agent
    MULTICAST = "multicast"  # Send to group of agents
    REQUEST = "request"  # Request information
    RESPONSE = "response"  # Response to request
    NOTIFICATION = "notification"  # Notify about state change
    COORDINATION = "coordination"  # Coordinate actions
    CONSENSUS = "consensus"  # Reach agreement
    HEARTBEAT = "heartbeat"  # Keep-alive signal

class MessagePriority(str, Enum):
    """Message priority levels."""
    CRITICAL = "critical"  # Immediate processing required
    HIGH = "high"  # High priority
    NORMAL = "normal"  # Standard priority
    LOW = "low"  # Low priority
    BACKGROUND = "background"  # Process when idle

@dataclass
class Message:
    """Represents a message in the communication network."""
    message_id: str = field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:8]}")
    sender: str = ""
    recipients: List[str] = field(default_factory=list)
    message_type: MessageType = MessageType.NOTIFICATION
    priority: MessagePriority = MessagePriority.NORMAL
    content: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    ttl: int = 60  # Time to live in seconds
    requires_ack: bool = False
    ack_received: Set[str] = field(default_factory=set)
    
    def is_expired(self) -> bool:
        """Check if message has expired."""
        age = (datetime.now() - self.timestamp).total_seconds()
        return age > self.ttl

@dataclass
class AgentProfile:
    """Profile of an agent in the network."""
    agent_id: str
    agent_type: str  # coder, reviewer, architect, tester, etc.
    capabilities: List[str] = field(default_factory=list)
    current_task: Optional[str] = None
    status: str = "idle"  # idle, busy, blocked, offline
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    message_queue: deque = field(default_factory=lambda: deque(maxlen=100))
    subscriptions: Set[str] = field(default_factory=set)  # Topics subscribed to
    reputation: float = 1.0  # Trust/reputation score
    last_heartbeat: datetime = field(default_factory=datetime.now)
    
    def update_heartbeat(self):
        """Update last heartbeat timestamp."""
        self.last_heartbeat = datetime.now()
    
    def is_responsive(self, timeout: int = 30) -> bool:
        """Check if agent is responsive."""
        age = (datetime.now() - self.last_heartbeat).total_seconds()
        return age < timeout

class CommunicationProtocol:
    """Defines communication protocols between agents."""
    
    @staticmethod
    async def handshake(sender: str, receiver: str) -> bool:
        """Establish communication handshake."""
        # Simple handshake protocol
        return True
    
    @staticmethod
    def validate_message(message: Message) -> bool:
        """Validate message format and content."""
        if not message.sender:
            return False
        if message.is_expired():
            return False
        if not message.content:
            return False
        return True

class ConsensusAlgorithm:
    """Consensus algorithms for multi-agent agreement."""
    
    def __init__(self):
        """Initialize consensus algorithm."""
        self.proposals: Dict[str, Dict[str, Any]] = {}
        self.votes: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.consensus_threshold = 0.66  # 2/3 majority
    
    def propose(self, proposal_id: str, proposer: str, content: Any):
        """Submit a proposal for consensus."""
        self.proposals[proposal_id] = {
            'proposer': proposer,
            'content': content,
            'timestamp': datetime.now(),
            'status': 'pending'
        }
    
    def vote(self, proposal_id: str, voter: str, vote: bool, weight: float = 1.0):
        """Cast a vote on a proposal."""
        if proposal_id in self.proposals:
            self.votes[proposal_id][voter] = {
                'vote': vote,
                'weight': weight,
                'timestamp': datetime.now()
            }
    
    def check_consensus(self, proposal_id: str, total_agents: int) -> Optional[bool]:
        """Check if consensus has been reached."""
        if proposal_id not in self.proposals:
            return None
        
        votes = self.votes.get(proposal_id, {})
        if not votes:
            return None
        
        # Calculate weighted votes
        yes_weight = sum(v['weight'] for v in votes.values() if v['vote'])
        no_weight = sum(v['weight'] for v in votes.values() if not v['vote'])
        total_weight = sum(v['weight'] for v in votes.values())
        
        # Check if enough agents have voted
        if len(votes) < total_agents * 0.5:  # Need at least 50% participation
            return None
        
        # Check consensus
        if yes_weight / total_weight >= self.consensus_threshold:
            self.proposals[proposal_id]['status'] = 'accepted'
            return True
        elif no_weight / total_weight > (1 - self.consensus_threshold):
            self.proposals[proposal_id]['status'] = 'rejected'
            return False
        
        return None  # No consensus yet

class CollaborativeIntelligence:
    """Enables collective problem-solving through agent collaboration."""
    
    def __init__(self):
        """Initialize collaborative intelligence."""
        self.shared_knowledge: Dict[str, Any] = {}
        self.problem_decomposition: Dict[str, List[str]] = {}
        self.solution_synthesis: Dict[str, List[Any]] = defaultdict(list)
        self.collective_memory: deque = deque(maxlen=1000)
    
    def share_knowledge(self, agent_id: str, knowledge_key: str, knowledge_value: Any):
        """Share knowledge with the collective."""
        if knowledge_key not in self.shared_knowledge:
            self.shared_knowledge[knowledge_key] = {}
        
        self.shared_knowledge[knowledge_key][agent_id] = {
            'value': knowledge_value,
            'timestamp': datetime.now(),
            'confidence': 0.8  # Default confidence
        }
    
    def get_collective_knowledge(self, knowledge_key: str) -> Any:
        """Get collective knowledge on a topic."""
        if knowledge_key not in self.shared_knowledge:
            return None
        
        # Aggregate knowledge from multiple agents
        knowledge_entries = self.shared_knowledge[knowledge_key]
        
        if not knowledge_entries:
            return None
        
        # Simple aggregation - could be more sophisticated
        # Return the most recent high-confidence entry
        best_entry = max(
            knowledge_entries.values(),
            key=lambda x: x['confidence'] * (1 / (datetime.now() - x['timestamp']).total_seconds())
        )
        
        return best_entry['value']
    
    def decompose_problem(self, problem_id: str, subtasks: List[str]):
        """Decompose a problem into subtasks."""
        self.problem_decomposition[problem_id] = subtasks
    
    def contribute_solution(self, problem_id: str, agent_id: str, partial_solution: Any):
        """Contribute a partial solution to a problem."""
        self.solution_synthesis[problem_id].append({
            'agent_id': agent_id,
            'solution': partial_solution,
            'timestamp': datetime.now()
        })
    
    def synthesize_solution(self, problem_id: str) -> Any:
        """Synthesize complete solution from partial solutions."""
        if problem_id not in self.solution_synthesis:
            return None
        
        partial_solutions = self.solution_synthesis[problem_id]
        
        if not partial_solutions:
            return None
        
        # Combine partial solutions
        # This is simplified - actual implementation would be more sophisticated
        combined = {
            'problem_id': problem_id,
            'contributors': [s['agent_id'] for s in partial_solutions],
            'solutions': [s['solution'] for s in partial_solutions],
            'synthesis_time': datetime.now()
        }
        
        return combined

class InterAgentCommunicationNetwork:
    """
    Sophisticated inter-agent communication network for coordinated execution.
    
    Enables agents to communicate, coordinate, share knowledge, and collectively
    solve problems through various communication patterns and protocols.
    """
    
    def __init__(self, enable_consensus: bool = True):
        """
        Initialize the communication network.
        
        Args:
            enable_consensus: Whether to enable consensus mechanisms
        """
        # Agent registry
        self.agents: Dict[str, AgentProfile] = {}
        self.agent_groups: Dict[str, Set[str]] = defaultdict(set)
        
        # Communication infrastructure
        self.message_bus: deque = deque(maxlen=10000)
        self.message_handlers: Dict[MessageType, List[Callable]] = defaultdict(list)
        self.topic_subscriptions: Dict[str, Set[str]] = defaultdict(set)
        
        # Consensus and collaboration
        self.enable_consensus = enable_consensus
        self.consensus_algorithm = ConsensusAlgorithm() if enable_consensus else None
        self.collaborative_intelligence = CollaborativeIntelligence()
        
        # Network metrics
        self.total_messages = 0
        self.delivered_messages = 0
        self.network_latency: List[float] = []
        
        # Communication patterns
        self.communication_patterns = {
            'request_response': self._handle_request_response,
            'publish_subscribe': self._handle_publish_subscribe,
            'pipeline': self._handle_pipeline,
            'scatter_gather': self._handle_scatter_gather
        }
    
    def register_agent(
        self,
        agent_id: str,
        agent_type: str,
        capabilities: List[str] = None
    ) -> AgentProfile:
        """
        Register an agent in the network.
        
        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent
            capabilities: List of agent capabilities
            
        Returns:
            AgentProfile
        """
        profile = AgentProfile(
            agent_id=agent_id,
            agent_type=agent_type,
            capabilities=capabilities or []
        )
        
        self.agents[agent_id] = profile
        self.agent_groups[agent_type].add(agent_id)
        
        logger.info(f"Registered agent {agent_id} of type {agent_type}")
        
        return profile
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent from the network."""
        if agent_id in self.agents:
            profile = self.agents[agent_id]
            self.agent_groups[profile.agent_type].discard(agent_id)
            del self.agents[agent_id]
            
            logger.info(f"Unregistered agent {agent_id}")
    
    async def send_message(
        self,
        sender: str,
        recipients: List[str],
        content: Any,
        message_type: MessageType = MessageType.NOTIFICATION,
        priority: MessagePriority = MessagePriority.NORMAL,
        requires_ack: bool = False
    ) -> str:
        """
        Send a message through the network.
        
        Args:
            sender: Sender agent ID
            recipients: List of recipient agent IDs
            content: Message content
            message_type: Type of message
            priority: Message priority
            requires_ack: Whether acknowledgment is required
            
        Returns:
            Message ID
        """
        message = Message(
            sender=sender,
            recipients=recipients,
            message_type=message_type,
            priority=priority,
            content=content,
            requires_ack=requires_ack
        )
        
        # Validate message
        if not CommunicationProtocol.validate_message(message):
            raise ValueError("Invalid message format")
        
        # Add to message bus
        self.message_bus.append(message)
        self.total_messages += 1
        
        # Process message
        await self._process_message(message)
        
        return message.message_id
    
    async def broadcast(
        self,
        sender: str,
        content: Any,
        exclude: List[str] = None
    ) -> str:
        """
        Broadcast message to all agents.
        
        Args:
            sender: Sender agent ID
            content: Message content
            exclude: Agents to exclude from broadcast
            
        Returns:
            Message ID
        """
        exclude = exclude or []
        recipients = [aid for aid in self.agents.keys() if aid != sender and aid not in exclude]
        
        return await self.send_message(
            sender=sender,
            recipients=recipients,
            content=content,
            message_type=MessageType.BROADCAST
        )
    
    async def request_response(
        self,
        requester: str,
        responder: str,
        request: Any,
        timeout: int = 30
    ) -> Optional[Any]:
        """
        Request-response pattern.
        
        Args:
            requester: Requesting agent ID
            responder: Responding agent ID
            request: Request content
            timeout: Response timeout in seconds
            
        Returns:
            Response or None if timeout
        """
        # Send request
        request_id = await self.send_message(
            sender=requester,
            recipients=[responder],
            content={'request': request, 'request_id': uuid.uuid4().hex},
            message_type=MessageType.REQUEST,
            requires_ack=True
        )
        
        # Wait for response
        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < timeout:
            # Check for response in agent's queue
            if requester in self.agents:
                agent = self.agents[requester]
                for msg in agent.message_queue:
                    if msg.message_type == MessageType.RESPONSE:
                        if msg.content.get('request_id') == request_id:
                            return msg.content.get('response')
            
            await asyncio.sleep(0.1)
        
        return None  # Timeout
    
    def subscribe_to_topic(self, agent_id: str, topic: str):
        """Subscribe an agent to a topic."""
        if agent_id in self.agents:
            self.agents[agent_id].subscriptions.add(topic)
            self.topic_subscriptions[topic].add(agent_id)
    
    def unsubscribe_from_topic(self, agent_id: str, topic: str):
        """Unsubscribe an agent from a topic."""
        if agent_id in self.agents:
            self.agents[agent_id].subscriptions.discard(topic)
            self.topic_subscriptions[topic].discard(agent_id)
    
    async def publish_to_topic(self, topic: str, content: Any, publisher: str):
        """Publish message to a topic."""
        subscribers = self.topic_subscriptions.get(topic, set())
        
        if subscribers:
            await self.send_message(
                sender=publisher,
                recipients=list(subscribers),
                content={'topic': topic, 'data': content},
                message_type=MessageType.MULTICAST
            )
    
    async def reach_consensus(
        self,
        proposal: Any,
        proposer: str,
        voters: List[str],
        timeout: int = 60
    ) -> Optional[bool]:
        """
        Reach consensus among agents.
        
        Args:
            proposal: Proposal content
            proposer: Proposing agent ID
            voters: List of voting agent IDs
            timeout: Consensus timeout in seconds
            
        Returns:
            True if accepted, False if rejected, None if no consensus
        """
        if not self.enable_consensus or not self.consensus_algorithm:
            return None
        
        proposal_id = f"proposal_{uuid.uuid4().hex[:8]}"
        
        # Submit proposal
        self.consensus_algorithm.propose(proposal_id, proposer, proposal)
        
        # Request votes
        await self.send_message(
            sender=proposer,
            recipients=voters,
            content={'proposal_id': proposal_id, 'proposal': proposal},
            message_type=MessageType.CONSENSUS,
            priority=MessagePriority.HIGH
        )
        
        # Wait for consensus
        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < timeout:
            result = self.consensus_algorithm.check_consensus(proposal_id, len(voters))
            if result is not None:
                return result
            
            await asyncio.sleep(0.5)
        
        return None  # No consensus reached
    
    async def coordinate_task(
        self,
        task_id: str,
        coordinator: str,
        workers: List[str],
        task_description: Any
    ) -> Dict[str, Any]:
        """
        Coordinate a task among multiple agents.
        
        Args:
            task_id: Task identifier
            coordinator: Coordinating agent ID
            workers: List of worker agent IDs
            task_description: Task details
            
        Returns:
            Coordination result
        """
        # Decompose task
        subtasks = self._decompose_task(task_description)
        self.collaborative_intelligence.decompose_problem(task_id, subtasks)
        
        # Assign subtasks to workers
        assignments = {}
        for i, worker in enumerate(workers):
            if i < len(subtasks):
                assignments[worker] = subtasks[i]
                
                # Send assignment
                await self.send_message(
                    sender=coordinator,
                    recipients=[worker],
                    content={
                        'task_id': task_id,
                        'subtask': subtasks[i],
                        'index': i
                    },
                    message_type=MessageType.COORDINATION,
                    priority=MessagePriority.HIGH
                )
        
        return {
            'task_id': task_id,
            'assignments': assignments,
            'status': 'coordinated'
        }
    
    def _decompose_task(self, task_description: Any) -> List[str]:
        """Decompose task into subtasks."""
        # Simplified decomposition
        if isinstance(task_description, dict):
            return list(task_description.get('subtasks', ['default_task']))
        return ['subtask_1', 'subtask_2', 'subtask_3']
    
    async def _process_message(self, message: Message):
        """Process a message through the network."""
        # Update latency metrics
        processing_start = datetime.now()
        
        # Deliver to recipients
        for recipient_id in message.recipients:
            if recipient_id in self.agents:
                agent = self.agents[recipient_id]
                
                # Add to agent's queue based on priority
                if message.priority == MessagePriority.CRITICAL:
                    agent.message_queue.appendleft(message)
                else:
                    agent.message_queue.append(message)
                
                self.delivered_messages += 1
                
                # Send acknowledgment if required
                if message.requires_ack:
                    message.ack_received.add(recipient_id)
        
        # Execute message handlers
        handlers = self.message_handlers.get(message.message_type, [])
        for handler in handlers:
            await handler(message)
        
        # Update latency
        processing_time = (datetime.now() - processing_start).total_seconds()
        self.network_latency.append(processing_time)
    
    async def _handle_request_response(self, message: Message):
        """Handle request-response pattern."""
        # Implementation would process request and generate response
        pass
    
    async def _handle_publish_subscribe(self, message: Message):
        """Handle publish-subscribe pattern."""
        # Implementation would route to subscribers
        pass
    
    async def _handle_pipeline(self, message: Message):
        """Handle pipeline pattern."""
        # Implementation would process through pipeline stages
        pass
    
    async def _handle_scatter_gather(self, message: Message):
        """Handle scatter-gather pattern."""
        # Implementation would scatter work and gather results
        pass
    
    def register_message_handler(self, message_type: MessageType, handler: Callable):
        """Register a handler for a message type."""
        self.message_handlers[message_type].append(handler)
    
    def get_network_metrics(self) -> Dict[str, Any]:
        """Get network performance metrics."""
        active_agents = sum(1 for a in self.agents.values() if a.is_responsive())
        
        return {
            'total_agents': len(self.agents),
            'active_agents': active_agents,
            'total_messages': self.total_messages,
            'delivered_messages': self.delivered_messages,
            'delivery_rate': self.delivered_messages / max(self.total_messages, 1),
            'average_latency': np.mean(self.network_latency) if self.network_latency else 0,
            'topics': len(self.topic_subscriptions),
            'pending_messages': len(self.message_bus),
            'shared_knowledge_items': len(self.collaborative_intelligence.shared_knowledge)
        }
    
    async def heartbeat_check(self):
        """Check agent heartbeats and update status."""
        for agent_id, agent in self.agents.items():
            if not agent.is_responsive(timeout=60):
                agent.status = "offline"
                logger.warning(f"Agent {agent_id} is offline")
    
    def visualize_network(self) -> str:
        """Generate ASCII visualization of network state."""
        lines = []
        lines.append("Inter-Agent Communication Network")
        lines.append("=" * 50)
        
        # Agent status
        lines.append("\nAgent Status:")
        for agent_id, agent in list(self.agents.items())[:10]:
            status_icon = "🟢" if agent.is_responsive() else "🔴"
            lines.append(f"  {status_icon} {agent_id}: {agent.status} ({agent.agent_type})")
        
        # Communication metrics
        lines.append(f"\nNetwork Metrics:")
        lines.append(f"  Messages: {self.delivered_messages}/{self.total_messages}")
        lines.append(f"  Delivery Rate: {self.delivered_messages/max(self.total_messages,1):.1%}")
        
        if self.network_latency:
            lines.append(f"  Avg Latency: {np.mean(self.network_latency)*1000:.1f}ms")
        
        # Collaboration metrics
        lines.append(f"\nCollaboration:")
        lines.append(f"  Shared Knowledge: {len(self.collaborative_intelligence.shared_knowledge)} items")
        lines.append(f"  Active Problems: {len(self.collaborative_intelligence.problem_decomposition)}")
        
        return "\n".join(lines)