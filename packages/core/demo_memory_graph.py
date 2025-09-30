#!/usr/bin/env python3
"""
Memory Graph Demo Script

This script demonstrates the memory graph system with a practical CRM7 example:
1. Agent A (IngestorAgent) extracts entities/relations from deployment text
2. Agent B (PlannerAgent) answers questions using only graph queries
3. Shows multi-hop reasoning and decision traceability

Run this script to see the 20-minute mini-experiment in action.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

# Import our agents and types
from monkey_coder.agents.base_agent import AgentContext
from monkey_coder.agents.ingestor_agent import IngestorAgent
from monkey_coder.agents.planner_agent import PlannerAgent
from monkey_coder.agents.memory_graph import MemoryGraph, Node, Edge


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_results(title: str, results: Dict[str, Any]):
    """Print formatted results"""
    print(f"\n--- {title} ---")
    print(json.dumps(results, indent=2, default=str))


async def demo_memory_graph():
    """Run the complete memory graph demo"""
    
    print_section("Memory Graph Demo: CRM7 Deployment Analysis")
    
    # Initialize agents
    ingestor = IngestorAgent()
    planner = PlannerAgent()
    
    await ingestor.initialize()
    await planner.initialize()
    
    # Create shared context
    context = AgentContext(
        task_id="demo_crm7_001",
        user_id="demo_user",
        session_id="demo_session",
        metadata={"demo": True, "scenario": "crm7_deployment"}
    )
    
    print_section("STEP 1: Agent A (Ingestor) - Extract from Source Text")
    
    # Sample deployment text (mimics README or deploy log)
    deployment_text = """
    CRM7 Application Deployment Guide
    
    The crm7 service on Vercel requires the following environment variables:
    - SUPABASE_URL for database connection
    - SUPABASE_ANON_KEY for authentication
    - STRIPE_PUBLISHABLE_KEY for payments
    
    Recent deployment log:
    Deploy crm7 failed with error: missing SUPABASE_URL
    
    Historical incidents:
    - INC-101: Service outage due to missing SUPABASE_URL configuration
    - INC-102: Authentication failures caused by incorrect SUPABASE_ANON_KEY
    
    Environment configuration:
    STRIPE_PUBLISHABLE_KEY=pk_test_12345abcdef
    DATABASE_URL=postgresql://localhost/crm7_dev
    """
    
    print("📄 Source Text:")
    print(deployment_text)
    
    # Agent A processes the text
    extraction_result = await ingestor.process(deployment_text, context)
    print_results("Extraction Results", extraction_result)
    
    # Show what was added to the graph
    graph_stats = ingestor.get_memory_graph_stats()
    print_results("Memory Graph Statistics", graph_stats)
    
    print_section("STEP 2: Add Additional Relationships")
    
    # Add incident relationships manually (Agent A could also extract these)
    # First, add the specific incidents
    inc101_id = ingestor.add_entity(
        "Incident", 
        {"description": "Service outage due to missing SUPABASE_URL", "severity": "high"},
        entity_id="incident:inc-101"
    )
    
    # Add incident relationships
    ingestor.add_relationship(
        from_entity_id="incident:inc-101",
        to_entity_id="service:crm7",
        relationship_type="INCIDENT_IMPACTS_SERVICE",
        properties={"severity": "high", "date": "2025-01-01"}
    )
    
    ingestor.add_relationship(
        from_entity_id="incident:inc-101", 
        to_entity_id="envvar:supabase_url",
        relationship_type="INCIDENT_CAUSED_BY_ENVVAR",
        properties={"root_cause": "missing_configuration"}
    )
    
    print("✅ Added incident relationships")
    
    # Now share the memory graph with Agent B
    # In practice, this would be done through shared memory or database
    planner.memory.graph = ingestor.memory.graph
    
    print_section("STEP 3: Agent B (Planner) - Graph-Only Reasoning")
    
    # Query 1: What's blocking crm7 rollout?
    print("\n🤔 Question 1: What's blocking crm7 rollout?")
    rollout_analysis = await planner.process("What's blocking crm7 rollout?", context)
    print_results("Rollout Risk Analysis", rollout_analysis)
    
    # Query 2: Which incidents are related to current rollout risks?
    print("\n🤔 Question 2: Which incidents are related to current rollout risks?")
    incident_analysis = await planner.process("Which incidents are related to current rollout risks?", context)
    print_results("Incident Impact Analysis", incident_analysis)
    
    # Query 3: Check deployment readiness
    print("\n🤔 Question 3: Is crm7 ready for deployment?")
    readiness_analysis = await planner.process("Is crm7 ready for deployment?", context)
    print_results("Deployment Readiness Check", readiness_analysis)
    
    print_section("STEP 4: Multi-Hop Reasoning Example")
    
    # Show multi-hop reasoning: CRM7 -> missing env var -> historical incident
    crm7_node = None
    for node in planner.get_entities_by_type("Service"):
        if "crm7" in node.props.get("name", "").lower():
            crm7_node = node
            break
    
    if crm7_node:
        print(f"🔍 Analyzing connections from service: {crm7_node.id}")
        
        # Get subgraph within 2 hops
        subgraph = planner.query_memory_graph(crm7_node.id, max_hops=2)
        
        print(f"📊 Found {len(subgraph.nodes)} connected entities and {len(subgraph.edges)} relationships")
        
        # Show the reasoning path
        print("\n🧠 Multi-hop reasoning paths:")
        for node in subgraph.nodes[:5]:  # Show first 5 nodes
            print(f"   • {node.type}: {node.props.get('name', node.props.get('key', node.id))}")
        
        for edge in subgraph.edges[:5]:  # Show first 5 edges
            print(f"   → {edge.type}: {edge.from_id} → {edge.to_id}")
    
    print_section("STEP 5: Fix Issues and Re-analyze")
    
    # Simulate fixing the missing environment variable
    print("🔧 Simulating fix: Adding missing SUPABASE_URL...")
    
    # Mark SUPABASE_URL as present
    supabase_url_nodes = [n for n in planner.get_entities_by_type("EnvVar") 
                         if "supabase_url" in n.props.get("key", "").lower()]
    
    for node in supabase_url_nodes:
        node.props["present"] = True
        print(f"   ✅ Marked {node.props.get('key')} as present")
    
    # Re-check deployment readiness
    print("\n🔄 Re-checking deployment readiness after fix...")
    updated_readiness = await planner.process("Is crm7 ready for deployment?", context)
    print_results("Updated Deployment Readiness", updated_readiness)
    
    print_section("STEP 6: Graph Analysis Summary")
    
    # Show final graph statistics
    final_stats = planner.get_memory_graph_stats()
    print_results("Final Graph Statistics", final_stats)
    
    # Show capabilities
    capabilities = planner.get_planning_capabilities()
    print_results("Planner Capabilities", capabilities)
    
    print_section("DEMO COMPLETE")
    
    print("""
🎉 Memory Graph Demo Summary:

✅ Agent A (Ingestor) successfully extracted:
   - Services, environment variables, and incidents from text
   - Relationships between entities (requirements, impacts)
   - Source traceability for all graph operations

✅ Agent B (Planner) demonstrated graph-only reasoning:
   - Identified rollout risks through missing dependencies
   - Found multi-hop connections (service → env var → incident)
   - Provided deployment recommendations based on graph structure
   - Updated analysis as graph data changed

🔑 Key Benefits Shown:
   - Composability: Agent A output became structured input for Agent B
   - Context compression: Agent B queried only relevant subgraphs
   - Traceability: All decisions were explainable through graph relationships
   - Multi-hop reasoning: Complex dependencies discovered automatically

📈 Next Steps:
   - Integrate with CRM7 parity roadmap (Features, Routes, Permissions)
   - Add deploy hygiene checks (Service-EnvVar-Secret-Incident)
   - Implement support flow analysis (Ticket-Customer-Plan-Module)
""")


async def run_quick_test():
    """Run a quick test to verify the system works"""
    print("🧪 Running quick verification test...")
    
    try:
        # Test basic graph operations
        from monkey_coder.agents.memory_graph import MemoryGraph, Node, Edge
        
        graph = MemoryGraph()
        
        # Add test entities
        service_node = Node(id="service:test", type="Service", props={"name": "test-service"})
        env_node = Node(id="envvar:test_key", type="EnvVar", props={"key": "TEST_KEY"})
        
        graph.add_node(service_node)
        graph.add_node(env_node)
        
        # Add relationship
        edge = Edge(type="SERVICE_REQUIRES_ENVVAR", from_id="service:test", to_id="envvar:test_key")
        graph.add_edge(edge)
        
        # Query graph
        neighbors = graph.neighbors("service:test")
        
        assert len(neighbors) == 1
        assert neighbors[0].id == "envvar:test_key"
        
        print("✅ Basic graph operations working")
        
        # Test agents
        ingestor = IngestorAgent()
        planner = PlannerAgent()
        
        await ingestor.initialize()
        await planner.initialize()
        
        print("✅ Agents initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Memory Graph Demo...")
    
    # Run verification first
    test_success = asyncio.run(run_quick_test())
    
    if test_success:
        print("\n" + "="*60)
        print("Starting full demo...")
        asyncio.run(demo_memory_graph())
    else:
        print("❌ Verification failed - cannot run demo")
        exit(1)