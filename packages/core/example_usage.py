#!/usr/bin/env python3
"""
Simple example demonstrating memory graph usage for deployment analysis.

This script shows how to:
1. Extract entities from deployment text using IngestorAgent
2. Query relationships using PlannerAgent 
3. Perform multi-hop reasoning for deployment decisions
"""

import asyncio
from monkey_coder.agents.ingestor_agent import IngestorAgent
from monkey_coder.agents.planner_agent import PlannerAgent
from monkey_coder.agents.base_agent import AgentContext


async def main():
    """Simple memory graph example"""
    
    # Initialize agents
    ingestor = IngestorAgent()
    planner = PlannerAgent()
    
    await ingestor.initialize()
    await planner.initialize()
    
    # Create context
    context = AgentContext("example", "user", "session")
    
    print("🔍 Extracting entities from deployment text...")
    
    # Extract from deployment description
    deployment_text = """
    The api-gateway service requires JWT_SECRET and DATABASE_URL.
    The user-service requires DATABASE_URL and REDIS_URL.
    
    Incident: API gateway failed due to missing JWT_SECRET.
    """
    
    # Agent A extracts entities and relationships
    result = await ingestor.process(deployment_text, context)
    print(f"✅ Extracted {result['extracted_entities']} entities and {result['extracted_relationships']} relationships")
    
    # Share graph with planner
    planner.memory.graph = ingestor.memory.graph
    
    print("\n🤔 Analyzing deployment risks...")
    
    # Agent B performs graph-only analysis
    analysis = await planner.process("What services need configuration?", context)
    
    print(f"📊 Analysis type: {analysis['analysis_type']}")
    
    # Handle different analysis types
    if 'total_risks' in analysis:
        print(f"🚨 Total risks found: {analysis['total_risks']}")
    elif 'services_analyzed' in analysis:
        print(f"🔍 Services analyzed: {analysis['services_analyzed']}")
    
    if 'recommendations' in analysis and analysis['recommendations']:
        print("\n💡 Recommendations:")
        for rec in analysis['recommendations'][:3]:  # Show first 3
            print(f"   • {rec}")
    
    # Show some analysis details
    if analysis['analysis_type'] == 'missing_dependencies':
        if 'dependencies' in analysis:
            print(f"\n📋 Dependencies found:")
            for dep in analysis['dependencies'][:2]:  # Show first 2
                service = dep.get('service', 'unknown')
                completion = dep.get('completion_percentage', 0)
                print(f"   • {service}: {completion:.1f}% ready")
    
    print("\n📈 Graph statistics:")
    stats = planner.get_memory_graph_stats()
    print(f"   • {stats['node_count']} entities")
    print(f"   • {stats['edge_count']} relationships")
    print(f"   • Entity types: {', '.join(stats['node_types'])}")


if __name__ == "__main__":
    asyncio.run(main())