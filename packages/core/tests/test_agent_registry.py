"""
Tests for Agent Registry module.

Validates the Microsoft Agent Framework-inspired agent discovery and registration system.
"""

import pytest
from datetime import datetime

from monkey_coder.core.agent_registry import (
    AgentRegistry,
    AgentCapability,
    AgentCapabilityType,
    AgentMetadata,
    AgentStatus,
    get_agent_registry
)


class TestAgentRegistry:
    """Test suite for AgentRegistry."""
    
    @pytest.fixture
    def registry(self):
        """Create a fresh agent registry for each test."""
        return AgentRegistry()
    
    @pytest.fixture
    def sample_capabilities(self):
        """Sample agent capabilities."""
        return [
            AgentCapability(
                type=AgentCapabilityType.CODE_GENERATION,
                proficiency_level=0.9,
                supported_languages=["python", "javascript", "typescript"],
                supported_frameworks=["fastapi", "react", "nextjs"]
            ),
            AgentCapability(
                type=AgentCapabilityType.CODE_REVIEW,
                proficiency_level=0.85,
                supported_languages=["python", "javascript"]
            )
        ]
    
    def test_register_agent(self, registry, sample_capabilities):
        """Test basic agent registration."""
        agent_id = registry.register_agent(
            name="code-generator",
            version="1.0.0",
            description="AI code generation agent",
            capabilities=sample_capabilities,
            tags={"coding", "generation"}
        )
        
        assert agent_id is not None
        assert agent_id.startswith("agent_")
        
        # Verify agent is in registry
        agent = registry.get_agent(agent_id)
        assert agent is not None
        assert agent.name == "code-generator"
        assert agent.version == "1.0.0"
        assert agent.status == AgentStatus.ACTIVE
        assert len(agent.capabilities) == 2
        assert agent.tags == {"coding", "generation"}
    
    def test_register_duplicate_agent_updates(self, registry, sample_capabilities):
        """Test that registering duplicate agent updates metadata."""
        # Register first time
        agent_id_1 = registry.register_agent(
            name="test-agent",
            version="1.0.0",
            description="Test agent v1",
            capabilities=sample_capabilities
        )
        
        # Register again with same name/version
        agent_id_2 = registry.register_agent(
            name="test-agent",
            version="1.0.0",
            description="Test agent v1 updated",
            capabilities=sample_capabilities
        )
        
        # Should return same agent ID
        assert agent_id_1 == agent_id_2
        
        # Description should be updated
        agent = registry.get_agent(agent_id_1)
        assert agent.description == "Test agent v1 updated"
    
    def test_unregister_agent(self, registry, sample_capabilities):
        """Test agent unregistration."""
        agent_id = registry.register_agent(
            name="test-agent",
            version="1.0.0",
            description="Test agent",
            capabilities=sample_capabilities
        )
        
        # Verify agent exists
        assert registry.get_agent(agent_id) is not None
        
        # Unregister
        result = registry.unregister_agent(agent_id)
        assert result is True
        
        # Verify agent is removed
        assert registry.get_agent(agent_id) is None
        
        # Try to unregister again
        result = registry.unregister_agent(agent_id)
        assert result is False
    
    def test_list_agents(self, registry, sample_capabilities):
        """Test listing agents with filters."""
        # Register multiple agents
        agent1_id = registry.register_agent(
            name="agent-1",
            version="1.0.0",
            description="Agent 1",
            capabilities=sample_capabilities,
            tags={"frontend", "react"}
        )
        
        agent2_id = registry.register_agent(
            name="agent-2",
            version="1.0.0",
            description="Agent 2",
            capabilities=[sample_capabilities[0]],
            tags={"backend", "python"}
        )
        
        # List all agents
        all_agents = registry.list_agents()
        assert len(all_agents) == 2
        
        # Filter by capability
        code_gen_agents = registry.list_agents(
            capability=AgentCapabilityType.CODE_GENERATION
        )
        assert len(code_gen_agents) == 2
        
        code_review_agents = registry.list_agents(
            capability=AgentCapabilityType.CODE_REVIEW
        )
        assert len(code_review_agents) == 1
        assert code_review_agents[0].agent_id == agent1_id
        
        # Filter by tags
        frontend_agents = registry.list_agents(tags={"frontend"})
        assert len(frontend_agents) == 1
        assert frontend_agents[0].agent_id == agent1_id
        
        # Filter by status
        active_agents = registry.list_agents(status=AgentStatus.ACTIVE)
        assert len(active_agents) == 2
        
        inactive_agents = registry.list_agents(status=AgentStatus.INACTIVE)
        assert len(inactive_agents) == 0
    
    def test_find_agents_by_capability(self, registry):
        """Test finding agents by capability with detailed filtering."""
        # Register agents with different proficiency levels
        registry.register_agent(
            name="expert-agent",
            version="1.0.0",
            description="Expert coding agent",
            capabilities=[
                AgentCapability(
                    type=AgentCapabilityType.CODE_GENERATION,
                    proficiency_level=0.95,
                    supported_languages=["python", "rust"]
                )
            ]
        )
        
        registry.register_agent(
            name="intermediate-agent",
            version="1.0.0",
            description="Intermediate coding agent",
            capabilities=[
                AgentCapability(
                    type=AgentCapabilityType.CODE_GENERATION,
                    proficiency_level=0.7,
                    supported_languages=["python", "javascript"]
                )
            ]
        )
        
        registry.register_agent(
            name="beginner-agent",
            version="1.0.0",
            description="Beginner coding agent",
            capabilities=[
                AgentCapability(
                    type=AgentCapabilityType.CODE_GENERATION,
                    proficiency_level=0.5,
                    supported_languages=["javascript"]
                )
            ]
        )
        
        # Find all code generation agents
        all_agents = registry.find_agents_by_capability(
            AgentCapabilityType.CODE_GENERATION
        )
        assert len(all_agents) == 3
        # Should be sorted by proficiency (descending)
        assert all_agents[0].name == "expert-agent"
        assert all_agents[1].name == "intermediate-agent"
        assert all_agents[2].name == "beginner-agent"
        
        # Find agents with minimum proficiency
        expert_agents = registry.find_agents_by_capability(
            AgentCapabilityType.CODE_GENERATION,
            min_proficiency=0.8
        )
        assert len(expert_agents) == 1
        assert expert_agents[0].name == "expert-agent"
        
        # Find agents supporting specific language
        python_agents = registry.find_agents_by_capability(
            AgentCapabilityType.CODE_GENERATION,
            languages=["python"]
        )
        assert len(python_agents) == 2
        assert python_agents[0].name == "expert-agent"
        assert python_agents[1].name == "intermediate-agent"
        
        rust_agents = registry.find_agents_by_capability(
            AgentCapabilityType.CODE_GENERATION,
            languages=["rust"]
        )
        assert len(rust_agents) == 1
        assert rust_agents[0].name == "expert-agent"
    
    def test_find_best_agent_for_task(self, registry):
        """Test finding best agent for multi-capability tasks."""
        # Register specialist agents
        registry.register_agent(
            name="fullstack-agent",
            version="1.0.0",
            description="Full-stack development agent",
            capabilities=[
                AgentCapability(
                    type=AgentCapabilityType.CODE_GENERATION,
                    proficiency_level=0.9,
                    supported_languages=["python", "javascript"]
                ),
                AgentCapability(
                    type=AgentCapabilityType.CODE_REVIEW,
                    proficiency_level=0.85
                ),
                AgentCapability(
                    type=AgentCapabilityType.TESTING,
                    proficiency_level=0.8
                )
            ],
            tags={"fullstack", "experienced"}
        )
        
        registry.register_agent(
            name="backend-specialist",
            version="1.0.0",
            description="Backend specialist",
            capabilities=[
                AgentCapability(
                    type=AgentCapabilityType.CODE_GENERATION,
                    proficiency_level=0.95,
                    supported_languages=["python", "go"]
                ),
                AgentCapability(
                    type=AgentCapabilityType.CODE_REVIEW,
                    proficiency_level=0.9
                )
            ],
            tags={"backend", "expert"}
        )
        
        # Find best agent for task requiring code generation + review
        best_agent = registry.find_best_agent_for_task(
            required_capabilities=[
                AgentCapabilityType.CODE_GENERATION,
                AgentCapabilityType.CODE_REVIEW
            ],
            languages=["python"]
        )
        
        assert best_agent is not None
        # Backend specialist should win due to higher proficiency
        assert best_agent.name == "backend-specialist"
        
        # Find best agent for task requiring all three capabilities
        best_agent = registry.find_best_agent_for_task(
            required_capabilities=[
                AgentCapabilityType.CODE_GENERATION,
                AgentCapabilityType.CODE_REVIEW,
                AgentCapabilityType.TESTING
            ]
        )
        
        assert best_agent is not None
        # Only fullstack agent has all three
        assert best_agent.name == "fullstack-agent"
        
        # Find best agent with preferred tags
        best_agent = registry.find_best_agent_for_task(
            required_capabilities=[
                AgentCapabilityType.CODE_GENERATION,
                AgentCapabilityType.CODE_REVIEW
            ],
            preferred_tags={"fullstack"}
        )
        
        # Should prefer fullstack due to tag match
        assert best_agent is not None
        assert best_agent.name == "fullstack-agent"
    
    def test_update_agent_health(self, registry, sample_capabilities):
        """Test updating agent health metrics."""
        agent_id = registry.register_agent(
            name="test-agent",
            version="1.0.0",
            description="Test agent",
            capabilities=sample_capabilities
        )
        
        # Update health
        registry.update_agent_health(
            agent_id=agent_id,
            health_score=0.75,
            status=AgentStatus.DEGRADED
        )
        
        agent = registry.get_agent(agent_id)
        assert agent.health_score == 0.75
        assert agent.status == AgentStatus.DEGRADED
        assert agent.last_health_check is not None
    
    def test_record_execution(self, registry, sample_capabilities):
        """Test recording execution metrics."""
        agent_id = registry.register_agent(
            name="test-agent",
            version="1.0.0",
            description="Test agent",
            capabilities=sample_capabilities
        )
        
        # Record successful executions
        for i in range(10):
            registry.record_execution(
                agent_id=agent_id,
                success=True,
                response_time=1.0 + i * 0.1
            )
        
        agent = registry.get_agent(agent_id)
        assert agent.total_executions == 10
        assert agent.failed_executions == 0
        assert agent.success_rate == 1.0
        assert agent.average_response_time > 0
        
        # Record some failures
        for _ in range(5):
            registry.record_execution(
                agent_id=agent_id,
                success=False,
                response_time=2.0
            )
        
        agent = registry.get_agent(agent_id)
        assert agent.total_executions == 15
        assert agent.failed_executions == 5
        assert agent.success_rate == pytest.approx(10 / 15, rel=0.01)
    
    def test_get_registry_stats(self, registry, sample_capabilities):
        """Test getting registry statistics."""
        # Register some agents
        for i in range(3):
            registry.register_agent(
                name=f"agent-{i}",
                version="1.0.0",
                description=f"Agent {i}",
                capabilities=sample_capabilities,
                tags={f"tag-{i}"}
            )
        
        stats = registry.get_registry_stats()
        
        assert stats["total_agents"] == 3
        assert stats["active_agents"] == 3
        assert stats["capabilities_covered"] >= 2
        assert stats["total_tags"] >= 3
        assert stats["average_success_rate"] == 1.0  # No executions yet
    
    def test_global_registry_singleton(self):
        """Test that get_agent_registry returns singleton."""
        registry1 = get_agent_registry()
        registry2 = get_agent_registry()
        
        assert registry1 is registry2


class TestAgentCapability:
    """Test suite for AgentCapability."""
    
    def test_capability_creation(self):
        """Test creating agent capability."""
        capability = AgentCapability(
            type=AgentCapabilityType.CODE_GENERATION,
            proficiency_level=0.9,
            supported_languages=["python", "rust"],
            supported_frameworks=["fastapi", "actix"],
            metadata={"model": "gpt-4"}
        )
        
        assert capability.type == AgentCapabilityType.CODE_GENERATION
        assert capability.proficiency_level == 0.9
        assert len(capability.supported_languages) == 2
        assert len(capability.supported_frameworks) == 2
        assert capability.metadata["model"] == "gpt-4"
    
    def test_capability_defaults(self):
        """Test capability default values."""
        capability = AgentCapability(
            type=AgentCapabilityType.TESTING
        )
        
        assert capability.proficiency_level == 1.0
        assert capability.supported_languages == []
        assert capability.supported_frameworks == []
        assert capability.metadata == {}


class TestAgentMetadata:
    """Test suite for AgentMetadata."""
    
    def test_metadata_creation(self):
        """Test creating agent metadata."""
        metadata = AgentMetadata(
            agent_id="test-123",
            name="test-agent",
            version="1.0.0",
            description="Test agent",
            capabilities=[
                AgentCapability(type=AgentCapabilityType.CODE_GENERATION)
            ]
        )
        
        assert metadata.agent_id == "test-123"
        assert metadata.name == "test-agent"
        assert metadata.status == AgentStatus.INACTIVE  # Default
        assert metadata.is_local is True  # Default
        assert metadata.health_score == 1.0  # Default
        assert metadata.success_rate == 1.0  # Default
        assert isinstance(metadata.registered_at, datetime)
