"""
Agent Registry Module

Implements Microsoft Agent Framework's agent discovery and registration pattern.
Maintains metadata about available agents for intelligent routing and orchestration.

References:
- https://microsoft.github.io/multi-agent-reference-architecture/docs/reference-architecture/Reference-Architecture.html
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent health and availability status."""
    
    ACTIVE = "active"           # Agent is running and available
    INACTIVE = "inactive"       # Agent is registered but not active
    DEGRADED = "degraded"       # Agent is active but experiencing issues
    MAINTENANCE = "maintenance" # Agent is in maintenance mode
    FAILED = "failed"          # Agent has failed and needs attention


class AgentCapabilityType(Enum):
    """Standard agent capability types following Microsoft Agent Framework patterns."""
    
    # Code-related capabilities
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    CODE_REVIEW = "code_review"
    CODE_REFACTORING = "refactoring"
    
    # Testing capabilities
    TESTING = "testing"
    TEST_GENERATION = "test_generation"
    
    # Documentation capabilities
    DOCUMENTATION = "documentation"
    API_DOCUMENTATION = "api_documentation"
    
    # Architecture and design
    ARCHITECTURE_DESIGN = "architecture_design"
    SYSTEM_DESIGN = "system_design"
    
    # Security
    SECURITY_ANALYSIS = "security_analysis"
    VULNERABILITY_SCANNING = "vulnerability_scanning"
    
    # Performance
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    
    # DevOps
    DEVOPS = "devops"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    
    # Specialized
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    
    # General
    PLANNING = "planning"
    COLLABORATION = "collaboration"


@dataclass
class AgentCapability:
    """Represents a specific capability an agent provides."""
    
    type: AgentCapabilityType
    proficiency_level: float = 1.0  # 0.0 to 1.0
    supported_languages: List[str] = field(default_factory=list)
    supported_frameworks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMetadata:
    """
    Metadata about a registered agent.
    
    Follows Microsoft Agent Framework's agent registry pattern for
    maintaining agent information for discovery and routing.
    """
    
    agent_id: str
    name: str
    version: str
    description: str
    capabilities: List[AgentCapability]
    
    # Status and health
    status: AgentStatus = AgentStatus.INACTIVE
    last_health_check: Optional[datetime] = None
    health_score: float = 1.0  # 0.0 to 1.0
    
    # Service information
    endpoint: Optional[str] = None  # For microservice deployments
    is_local: bool = True           # True if in-process, False if remote
    
    # Performance metrics
    average_response_time: float = 0.0  # seconds
    success_rate: float = 1.0           # 0.0 to 1.0
    total_executions: int = 0
    failed_executions: int = 0
    
    # Resource requirements
    estimated_tokens_per_request: int = 1000
    estimated_cost_per_request: float = 0.01
    max_concurrent_requests: int = 10
    
    # Registration info
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    # Tags for discovery
    tags: Set[str] = field(default_factory=set)
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentRegistry:
    """
    Central registry for agent discovery and management.
    
    Implements Microsoft Agent Framework's agent registry pattern,
    enabling dynamic agent discovery, health monitoring, and intelligent routing.
    
    Reference: https://microsoft.github.io/multi-agent-reference-architecture/
    """
    
    def __init__(self):
        self._agents: Dict[str, AgentMetadata] = {}
        self._capabilities_index: Dict[AgentCapabilityType, List[str]] = {}
        self._tags_index: Dict[str, List[str]] = {}
        logger.info("AgentRegistry initialized")
    
    def register_agent(
        self,
        name: str,
        version: str,
        description: str,
        capabilities: List[AgentCapability],
        endpoint: Optional[str] = None,
        is_local: bool = True,
        tags: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register a new agent or update existing agent metadata.
        
        Args:
            name: Agent name
            version: Agent version (semantic versioning recommended)
            description: Human-readable agent description
            capabilities: List of agent capabilities
            endpoint: Service endpoint (for remote agents)
            is_local: Whether agent is in-process or remote
            tags: Tags for discovery
            metadata: Additional metadata
            
        Returns:
            Agent ID
        """
        # Check if agent already registered
        existing_agent = self._find_agent_by_name_version(name, version)
        if existing_agent:
            agent_id = existing_agent.agent_id
            logger.info(f"Updating existing agent: {name} v{version} ({agent_id})")
        else:
            agent_id = f"agent_{uuid4().hex[:12]}"
            logger.info(f"Registering new agent: {name} v{version} ({agent_id})")
        
        agent_metadata = AgentMetadata(
            agent_id=agent_id,
            name=name,
            version=version,
            description=description,
            capabilities=capabilities,
            endpoint=endpoint,
            is_local=is_local,
            tags=tags or set(),
            metadata=metadata or {},
            status=AgentStatus.ACTIVE,
            last_updated=datetime.utcnow()
        )
        
        # Store agent
        self._agents[agent_id] = agent_metadata
        
        # Update capability index
        for capability in capabilities:
            if capability.type not in self._capabilities_index:
                self._capabilities_index[capability.type] = []
            if agent_id not in self._capabilities_index[capability.type]:
                self._capabilities_index[capability.type].append(agent_id)
        
        # Update tags index
        for tag in agent_metadata.tags:
            if tag not in self._tags_index:
                self._tags_index[tag] = []
            if agent_id not in self._tags_index[tag]:
                self._tags_index[tag].append(agent_id)
        
        logger.info(
            f"Agent registered: {name} v{version} with "
            f"{len(capabilities)} capabilities and {len(agent_metadata.tags)} tags"
        )
        
        return agent_id
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the registry.
        
        Args:
            agent_id: Agent ID to unregister
            
        Returns:
            True if agent was unregistered, False if not found
        """
        if agent_id not in self._agents:
            logger.warning(f"Attempted to unregister unknown agent: {agent_id}")
            return False
        
        agent = self._agents[agent_id]
        
        # Remove from capability index
        for capability in agent.capabilities:
            if capability.type in self._capabilities_index:
                self._capabilities_index[capability.type] = [
                    aid for aid in self._capabilities_index[capability.type]
                    if aid != agent_id
                ]
        
        # Remove from tags index
        for tag in agent.tags:
            if tag in self._tags_index:
                self._tags_index[tag] = [
                    aid for aid in self._tags_index[tag]
                    if aid != agent_id
                ]
        
        # Remove agent
        del self._agents[agent_id]
        
        logger.info(f"Agent unregistered: {agent.name} v{agent.version} ({agent_id})")
        return True
    
    def get_agent(self, agent_id: str) -> Optional[AgentMetadata]:
        """Get agent metadata by ID."""
        return self._agents.get(agent_id)
    
    def list_agents(
        self,
        status: Optional[AgentStatus] = None,
        capability: Optional[AgentCapabilityType] = None,
        tags: Optional[Set[str]] = None
    ) -> List[AgentMetadata]:
        """
        List agents with optional filtering.
        
        Args:
            status: Filter by agent status
            capability: Filter by capability type
            tags: Filter by tags (agents must have all specified tags)
            
        Returns:
            List of matching agent metadata
        """
        agents = list(self._agents.values())
        
        # Filter by status
        if status:
            agents = [a for a in agents if a.status == status]
        
        # Filter by capability
        if capability:
            capable_agent_ids = set(self._capabilities_index.get(capability, []))
            agents = [a for a in agents if a.agent_id in capable_agent_ids]
        
        # Filter by tags
        if tags:
            agents = [a for a in agents if tags.issubset(a.tags)]
        
        return agents
    
    def find_agents_by_capability(
        self,
        capability: AgentCapabilityType,
        min_proficiency: float = 0.0,
        languages: Optional[List[str]] = None,
        status: AgentStatus = AgentStatus.ACTIVE
    ) -> List[AgentMetadata]:
        """
        Find agents by capability with filtering.
        
        Args:
            capability: Required capability type
            min_proficiency: Minimum proficiency level (0.0 to 1.0)
            languages: Required programming languages
            status: Required agent status
            
        Returns:
            List of matching agents sorted by proficiency
        """
        agent_ids = self._capabilities_index.get(capability, [])
        matching_agents = []
        
        for agent_id in agent_ids:
            agent = self._agents.get(agent_id)
            if not agent or agent.status != status:
                continue
            
            # Find matching capability
            for cap in agent.capabilities:
                if cap.type != capability:
                    continue
                
                # Check proficiency
                if cap.proficiency_level < min_proficiency:
                    continue
                
                # Check languages
                if languages:
                    if not cap.supported_languages:
                        continue
                    if not any(lang in cap.supported_languages for lang in languages):
                        continue
                
                matching_agents.append(agent)
                break
        
        # Sort by proficiency level (descending)
        matching_agents.sort(
            key=lambda a: max(
                c.proficiency_level for c in a.capabilities
                if c.type == capability
            ),
            reverse=True
        )
        
        return matching_agents
    
    def find_best_agent_for_task(
        self,
        required_capabilities: List[AgentCapabilityType],
        preferred_tags: Optional[Set[str]] = None,
        languages: Optional[List[str]] = None
    ) -> Optional[AgentMetadata]:
        """
        Find the best agent for a task requiring multiple capabilities.
        
        Uses a scoring algorithm to rank agents based on:
        - Capability coverage
        - Proficiency levels
        - Health score
        - Success rate
        - Tag matches
        
        Args:
            required_capabilities: List of required capabilities
            preferred_tags: Preferred tags (bonus points)
            languages: Required programming languages
            
        Returns:
            Best matching agent or None if no suitable agent found
        """
        scores: Dict[str, float] = {}
        
        for agent in self._agents.values():
            if agent.status != AgentStatus.ACTIVE:
                continue
            
            score = 0.0
            matched_capabilities = 0
            
            # Check each required capability
            for required_cap in required_capabilities:
                for cap in agent.capabilities:
                    if cap.type != required_cap:
                        continue
                    
                    # Check language compatibility
                    if languages and cap.supported_languages:
                        if not any(lang in cap.supported_languages for lang in languages):
                            continue
                    
                    matched_capabilities += 1
                    score += cap.proficiency_level * 10  # Weight: 0-10 per capability
                    break
            
            # Must have all required capabilities
            if matched_capabilities < len(required_capabilities):
                continue
            
            # Add health score (weight: 0-5)
            score += agent.health_score * 5
            
            # Add success rate (weight: 0-5)
            score += agent.success_rate * 5
            
            # Add tag bonus (weight: 0-3)
            if preferred_tags and agent.tags:
                tag_match_ratio = len(preferred_tags & agent.tags) / len(preferred_tags)
                score += tag_match_ratio * 3
            
            # Penalize slow agents slightly
            if agent.average_response_time > 10.0:
                score -= 2
            
            scores[agent.agent_id] = score
        
        if not scores:
            return None
        
        # Return agent with highest score
        best_agent_id = max(scores.keys(), key=lambda aid: scores[aid])
        return self._agents[best_agent_id]
    
    def update_agent_health(
        self,
        agent_id: str,
        health_score: float,
        status: Optional[AgentStatus] = None
    ):
        """
        Update agent health metrics.
        
        Args:
            agent_id: Agent ID
            health_score: Health score (0.0 to 1.0)
            status: New agent status
        """
        agent = self._agents.get(agent_id)
        if not agent:
            logger.warning(f"Attempted to update health for unknown agent: {agent_id}")
            return
        
        agent.health_score = max(0.0, min(1.0, health_score))
        agent.last_health_check = datetime.utcnow()
        
        if status:
            agent.status = status
        
        logger.debug(f"Updated health for {agent.name}: score={health_score:.2f}, status={agent.status.value}")
    
    def record_execution(
        self,
        agent_id: str,
        success: bool,
        response_time: float
    ):
        """
        Record agent execution metrics.
        
        Args:
            agent_id: Agent ID
            success: Whether execution was successful
            response_time: Execution time in seconds
        """
        agent = self._agents.get(agent_id)
        if not agent:
            logger.warning(f"Attempted to record execution for unknown agent: {agent_id}")
            return
        
        agent.total_executions += 1
        if not success:
            agent.failed_executions += 1
        
        # Update success rate
        agent.success_rate = (
            (agent.total_executions - agent.failed_executions) / agent.total_executions
        )
        
        # Update average response time (exponential moving average)
        alpha = 0.3  # Weight for new observation
        if agent.average_response_time == 0.0:
            agent.average_response_time = response_time
        else:
            agent.average_response_time = (
                alpha * response_time + (1 - alpha) * agent.average_response_time
            )
        
        agent.last_updated = datetime.utcnow()
        
        logger.debug(
            f"Recorded execution for {agent.name}: "
            f"success={success}, time={response_time:.2f}s, "
            f"success_rate={agent.success_rate:.2%}"
        )
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        active_agents = [a for a in self._agents.values() if a.status == AgentStatus.ACTIVE]
        
        return {
            "total_agents": len(self._agents),
            "active_agents": len(active_agents),
            "capabilities_covered": len(self._capabilities_index),
            "total_tags": len(self._tags_index),
            "average_success_rate": (
                sum(a.success_rate for a in active_agents) / len(active_agents)
                if active_agents else 0.0
            ),
            "total_executions": sum(a.total_executions for a in self._agents.values()),
            "failed_executions": sum(a.failed_executions for a in self._agents.values())
        }
    
    def _find_agent_by_name_version(
        self,
        name: str,
        version: str
    ) -> Optional[AgentMetadata]:
        """Find agent by name and version."""
        for agent in self._agents.values():
            if agent.name == name and agent.version == version:
                return agent
        return None


# Global registry instance (singleton pattern)
_global_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """Get or create the global agent registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = AgentRegistry()
    return _global_registry
