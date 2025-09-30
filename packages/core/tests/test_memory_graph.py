"""
Tests for the memory graph system and specialized agents.

Tests cover:
1. Core memory graph operations (CRUD, queries, traversal)
2. IngestorAgent entity/relationship extraction
3. PlannerAgent graph-only reasoning
4. Multi-hop reasoning scenarios
5. CRM7 deployment example integration
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from monkey_coder.agents.memory_graph import (
    MemoryGraph, Node, Edge, QueryResult,
    missing_env_vars_for_service, related_incidents_for_service
)
from monkey_coder.agents.base_agent import AgentContext
from monkey_coder.agents.ingestor_agent import IngestorAgent
from monkey_coder.agents.planner_agent import PlannerAgent


class TestMemoryGraph:
    """Test core memory graph functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.graph = MemoryGraph()
    
    def test_node_creation_and_retrieval(self):
        """Test basic node operations"""
        node = Node(id="test:1", type="TestType", props={"name": "test"})
        
        assert self.graph.add_node(node) == True
        retrieved = self.graph.get_node("test:1")
        
        assert retrieved is not None
        assert retrieved.id == "test:1"
        assert retrieved.type == "TestType"
        assert retrieved.props["name"] == "test"
    
    def test_edge_creation_and_retrieval(self):
        """Test basic edge operations"""
        # Create nodes first
        node1 = Node(id="node:1", type="Type1", props={})
        node2 = Node(id="node:2", type="Type2", props={})
        
        self.graph.add_node(node1)
        self.graph.add_node(node2)
        
        # Create edge
        edge = Edge(type="CONNECTS", from_id="node:1", to_id="node:2")
        
        assert self.graph.add_edge(edge) == True
        
        # Test retrieval
        outgoing = self.graph.get_edges_from("node:1")
        incoming = self.graph.get_edges_to("node:2")
        
        assert len(outgoing) == 1
        assert len(incoming) == 1
        assert outgoing[0].type == "CONNECTS"
        assert incoming[0].type == "CONNECTS"
    
    def test_neighbors_query(self):
        """Test neighbor queries"""
        # Create test graph: A -> B -> C
        nodes = [
            Node(id="a", type="Type", props={"name": "A"}),
            Node(id="b", type="Type", props={"name": "B"}), 
            Node(id="c", type="Type", props={"name": "C"})
        ]
        
        for node in nodes:
            self.graph.add_node(node)
        
        edges = [
            Edge(type="CONNECTS", from_id="a", to_id="b"),
            Edge(type="CONNECTS", from_id="b", to_id="c")
        ]
        
        for edge in edges:
            self.graph.add_edge(edge)
        
        # Test outgoing neighbors
        neighbors_a = self.graph.neighbors("a", direction="out")
        assert len(neighbors_a) == 1
        assert neighbors_a[0].id == "b"
        
        # Test incoming neighbors
        neighbors_c = self.graph.neighbors("c", direction="in")
        assert len(neighbors_c) == 1
        assert neighbors_c[0].id == "b"
    
    def test_subgraph_query(self):
        """Test subgraph queries within N hops"""
        # Create test graph: A -> B -> C -> D
        nodes = [
            Node(id=f"node:{i}", type="Service", props={"name": f"service{i}"})
            for i in range(4)
        ]
        
        for node in nodes:
            self.graph.add_node(node)
        
        edges = [
            Edge(type="DEPENDS_ON", from_id="node:0", to_id="node:1"),
            Edge(type="DEPENDS_ON", from_id="node:1", to_id="node:2"),
            Edge(type="DEPENDS_ON", from_id="node:2", to_id="node:3")
        ]
        
        for edge in edges:
            self.graph.add_edge(edge)
        
        # Query subgraph within 2 hops from node:0
        result = self.graph.query_subgraph("node:0", max_hops=2)
        
        # Should include nodes 0, 1, 2 (but not 3)
        node_ids = [node.id for node in result.nodes]
        assert "node:0" in node_ids
        assert "node:1" in node_ids
        assert "node:2" in node_ids
        assert len(result.nodes) == 3
        assert len(result.edges) == 2
    
    def test_path_finding(self):
        """Test finding paths between nodes"""
        # Create test graph with multiple paths
        nodes = [Node(id=f"n{i}", type="Node", props={}) for i in range(5)]
        for node in nodes:
            self.graph.add_node(node)
        
        # Create paths: n0->n1->n2->n4 and n0->n3->n4
        edges = [
            Edge(type="PATH", from_id="n0", to_id="n1"),
            Edge(type="PATH", from_id="n1", to_id="n2"),
            Edge(type="PATH", from_id="n2", to_id="n4"),
            Edge(type="PATH", from_id="n0", to_id="n3"),
            Edge(type="PATH", from_id="n3", to_id="n4")
        ]
        
        for edge in edges:
            self.graph.add_edge(edge)
        
        paths = self.graph.find_paths("n0", "n4")
        
        assert len(paths) == 2  # Two possible paths
        assert ["n0", "n1", "n2", "n4"] in paths
        assert ["n0", "n3", "n4"] in paths
    
    def test_node_removal(self):
        """Test node removal and cascade deletion"""
        # Create nodes and edges
        node1 = Node(id="n1", type="Node", props={})
        node2 = Node(id="n2", type="Node", props={})
        
        self.graph.add_node(node1)
        self.graph.add_node(node2)
        
        edge = Edge(type="CONNECTS", from_id="n1", to_id="n2")
        self.graph.add_edge(edge)
        
        # Remove node1
        assert self.graph.remove_node("n1") == True
        
        # Check node and edges are removed
        assert self.graph.get_node("n1") is None
        assert len(self.graph.get_edges_to("n2")) == 0
        assert self.graph.get_node("n2") is not None  # n2 should still exist


class TestSpecializedQueries:
    """Test specialized query functions"""
    
    def setup_method(self):
        """Setup CRM7-like test graph"""
        self.graph = MemoryGraph()
        
        # Create service
        service = Node(id="service:crm7", type="Service", props={"name": "crm7"})
        self.graph.add_node(service)
        
        # Create environment variables
        env_vars = [
            Node(id="envvar:supabase_url", type="EnvVar", 
                 props={"key": "SUPABASE_URL", "present": False}),
            Node(id="envvar:supabase_key", type="EnvVar", 
                 props={"key": "SUPABASE_ANON_KEY", "present": True}),
        ]
        
        for var in env_vars:
            self.graph.add_node(var)
        
        # Create requirements
        requirements = [
            Edge(type="SERVICE_REQUIRES_ENVVAR", from_id="service:crm7", to_id="envvar:supabase_url"),
            Edge(type="SERVICE_REQUIRES_ENVVAR", from_id="service:crm7", to_id="envvar:supabase_key")
        ]
        
        for req in requirements:
            self.graph.add_edge(req)
        
        # Create incident
        incident = Node(id="incident:inc101", type="Incident", 
                       props={"description": "Missing SUPABASE_URL", "severity": "high"})
        self.graph.add_node(incident)
        
        # Link incident to service
        self.graph.add_edge(Edge(type="INCIDENT_IMPACTS_SERVICE", 
                                from_id="incident:inc101", to_id="service:crm7"))
    
    def test_missing_env_vars_query(self):
        """Test finding missing environment variables"""
        missing = missing_env_vars_for_service(self.graph, "service:crm7")
        
        assert len(missing) == 1
        assert missing[0].props["key"] == "SUPABASE_URL"
        assert missing[0].props["present"] == False
    
    def test_related_incidents_query(self):
        """Test finding related incidents"""
        incidents = related_incidents_for_service(self.graph, "service:crm7")
        
        assert len(incidents) == 1
        assert incidents[0].props["description"] == "Missing SUPABASE_URL"


@pytest.mark.asyncio
class TestIngestorAgent:
    """Test IngestorAgent functionality"""
    
    async def test_agent_initialization(self):
        """Test agent can be initialized"""
        agent = IngestorAgent()
        await agent.initialize()
        
        assert agent.name == "ingestor"
        assert len(agent.extraction_patterns) > 0
    
    async def test_service_env_extraction(self):
        """Test extraction of service environment requirements"""
        agent = IngestorAgent()
        await agent.initialize()
        
        context = AgentContext(
            task_id="test_001",
            user_id="test_user", 
            session_id="test_session"
        )
        
        text = "crm7 on Vercel requires SUPABASE_URL and SUPABASE_ANON_KEY"
        
        result = await agent.process(text, context)
        
        assert result["extracted_entities"] >= 3  # Service + 2 env vars
        assert result["extracted_relationships"] >= 2  # 2 requirements
        
        # Check entities were added to graph
        services = agent.get_entities_by_type("Service")
        env_vars = agent.get_entities_by_type("EnvVar")
        
        assert len(services) >= 1
        assert len(env_vars) >= 2
        
        # Check relationships
        crm7_service = None
        for service in services:
            if "crm7" in service.props.get("name", "").lower():
                crm7_service = service
                break
        
        assert crm7_service is not None
        related_envs = agent.get_related_entities(crm7_service.id, "SERVICE_REQUIRES_ENVVAR")
        assert len(related_envs) >= 2
    
    async def test_incident_extraction(self):
        """Test extraction of incidents"""
        agent = IngestorAgent()
        await agent.initialize()
        
        context = AgentContext(
            task_id="test_002",
            user_id="test_user",
            session_id="test_session" 
        )
        
        text = "Deploy failed with error: missing SUPABASE_URL configuration"
        
        result = await agent.process(text, context)
        
        incidents = agent.get_entities_by_type("Incident")
        assert len(incidents) >= 1
        
        # Check incident properties
        incident = incidents[0]
        assert "missing" in incident.props.get("description", "").lower()


@pytest.mark.asyncio 
class TestPlannerAgent:
    """Test PlannerAgent functionality"""
    
    async def setup_method(self):
        """Setup planner with test data"""
        self.planner = PlannerAgent()
        await self.planner.initialize()
        
        # Add test entities to memory graph
        service = self.planner.add_entity("Service", {"name": "crm7"})
        env_missing = self.planner.add_entity("EnvVar", {"key": "SUPABASE_URL", "present": False})
        env_present = self.planner.add_entity("EnvVar", {"key": "STRIPE_KEY", "present": True})
        incident = self.planner.add_entity("Incident", 
                                         {"description": "Config error", "severity": "high"})
        
        # Add relationships
        self.planner.add_relationship(service, env_missing, "SERVICE_REQUIRES_ENVVAR")
        self.planner.add_relationship(service, env_present, "SERVICE_REQUIRES_ENVVAR")
        self.planner.add_relationship(incident, service, "INCIDENT_IMPACTS_SERVICE")
    
    async def test_rollout_risk_analysis(self):
        """Test rollout risk analysis"""
        context = AgentContext(
            task_id="test_003",
            user_id="test_user",
            session_id="test_session"
        )
        
        result = await self.planner.process("What's blocking crm7 rollout?", context)
        
        assert result["analysis_type"] == "rollout_risks"
        assert result["total_risks"] > 0
        assert result["rollout_status"] in ["blocked", "ready"]
    
    async def test_deployment_readiness(self):
        """Test deployment readiness check"""
        context = AgentContext(
            task_id="test_004", 
            user_id="test_user",
            session_id="test_session"
        )
        
        result = await self.planner.process("Is crm7 ready for deployment?", context)
        
        assert result["analysis_type"] == "deployment_readiness"
        assert "readiness_percentage" in result
        assert "service_readiness" in result
    
    async def test_graph_only_constraint(self):
        """Test that planner only uses graph data"""
        context = AgentContext(
            task_id="test_005",
            user_id="test_user", 
            session_id="test_session"
        )
        
        # The planner should not have access to raw text
        # All analysis should come from graph structure
        result = await self.planner.process("Analyze deployment", context)
        
        # All results should reference graph entities/relationships
        assert result["query_metadata"]["reasoning_source"] == "graph_only"


@pytest.mark.asyncio
class TestEndToEndScenario:
    """Test complete end-to-end memory graph workflow"""
    
    async def test_crm7_deployment_scenario(self):
        """Test the complete CRM7 deployment analysis scenario"""
        # Initialize agents
        ingestor = IngestorAgent()
        planner = PlannerAgent()
        
        await ingestor.initialize()
        await planner.initialize()
        
        context = AgentContext(
            task_id="e2e_crm7",
            user_id="demo_user",
            session_id="demo_session"
        )
        
        # Step 1: Ingest deployment information
        deployment_text = """
        crm7 service requires SUPABASE_URL and STRIPE_KEY for deployment.
        Recent incident: Service outage due to missing SUPABASE_URL.
        STRIPE_KEY=pk_test_12345 is already configured.
        """
        
        ingest_result = await ingestor.process(deployment_text, context)
        assert ingest_result["extracted_entities"] > 0
        assert ingest_result["extracted_relationships"] > 0
        
        # Step 2: Share graph with planner (in practice via shared storage)
        planner.memory.graph = ingestor.memory.graph
        
        # Step 3: Analyze rollout readiness
        analysis = await planner.process("What's blocking crm7 rollout?", context)
        
        assert analysis["analysis_type"] == "rollout_risks"
        assert len(analysis["risks"]) > 0
        
        # Should identify missing SUPABASE_URL as a risk
        missing_var_risks = [r for r in analysis["risks"] 
                           if r.get("type") == "missing_environment_variables"]
        assert len(missing_var_risks) > 0
        
        # Step 4: Fix the issue
        supabase_nodes = [n for n in planner.get_entities_by_type("EnvVar")
                         if "SUPABASE_URL" in n.props.get("key", "")]
        for node in supabase_nodes:
            node.props["present"] = True
        
        # Step 5: Re-analyze
        updated_analysis = await planner.process("Is crm7 ready for deployment?", context)
        
        # Should show improved readiness
        assert updated_analysis["analysis_type"] == "deployment_readiness"
        # Readiness should be higher after fixing the issue