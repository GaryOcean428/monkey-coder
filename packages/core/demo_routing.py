#!/usr/bin/env python3
"""
Demonstration script for the AdvancedRouter system.

This script shows how the Gary8D-inspired AdvancedRouter works with:
- Complexity analysis and scoring
- Context-aware model selection
- SuperClaude persona integration
- Slash-command parsing
"""

import json
from monkey_coder.models import (
    ExecuteRequest,
    TaskType,
    PersonaType,
    ExecutionContext,
    SuperClaudeConfig,
)
from monkey_coder.core.routing import AdvancedRouter


def demonstrate_routing():
    """Demonstrate the AdvancedRouter with various sample prompts."""
    
    # Initialize the router
    router = AdvancedRouter()
    
    # Create context for requests
    context = ExecutionContext(user_id="demo_user")
    superclause_config = SuperClaudeConfig(persona=PersonaType.DEVELOPER)
    
    # Sample prompts demonstrating different complexity levels and contexts
    sample_prompts = [
        {
            "name": "Simple Function",
            "prompt": "Write a Python function to add two numbers",
            "task_type": TaskType.CODE_GENERATION,
        },
        {
            "name": "Architecture with Slash Command",
            "prompt": "/arch Design a scalable microservices architecture for a social media platform with performance optimization",
            "task_type": TaskType.CUSTOM,
        },
        {
            "name": "Security Audit",
            "prompt": "/security Audit this authentication system for vulnerabilities and implement secure session management",
            "task_type": TaskType.CODE_REVIEW,
        },
        {
            "name": "Complex ML Pipeline",
            "prompt": "Implement a comprehensive machine learning pipeline with distributed training, neural network optimization, concurrent processing, and performance profiling",
            "task_type": TaskType.CODE_GENERATION,
            "files": [{"name": f"model_{i}.py", "content": "ml code"} for i in range(5)]
        },
        {
            "name": "Simple Debug",
            "prompt": "Fix this error: TypeError: 'int' object is not callable",
            "task_type": TaskType.DEBUGGING,
        },
        {
            "name": "Documentation Task",
            "prompt": "/docs Document this REST API endpoint with examples and parameter descriptions",
            "task_type": TaskType.DOCUMENTATION,
        }
    ]
    
    print("🚀 AdvancedRouter Demonstration")
    print("=" * 50)
    
    for i, sample in enumerate(sample_prompts, 1):
        print(f"\n{i}. {sample['name']}")
        print("-" * 30)
        
        # Create request
        request = ExecuteRequest(
            prompt=sample["prompt"],
            task_type=sample["task_type"],
            context=context,
            superclause_config=superclause_config,
            files=sample.get("files", [])
        )
        
        # Get routing decision
        decision = router.route_request(request)
        
        # Display results
        print(f"📝 Prompt: {sample['prompt'][:60]}{'...' if len(sample['prompt']) > 60 else ''}")
        print(f"🎯 Selected Model: {decision.provider.value}/{decision.model}")
        print(f"👤 Persona: {decision.persona.value}")
        print(f"🧮 Complexity: {decision.complexity_score:.2f} ({decision.metadata['complexity_level']})")
        print(f"🎯 Context: {decision.metadata['context_type']}")
        print(f"⚡ Capability: {decision.capability_score:.2f}")
        print(f"🎪 Confidence: {decision.confidence:.2f}")
        print(f"💭 Reasoning: {decision.reasoning}")
        
        if decision.metadata.get("slash_command"):
            print(f"⚡ Slash Command: /{decision.metadata['slash_command']}")


if __name__ == "__main__":
    try:
        demonstrate_routing()
        
        print("\n\n✅ AdvancedRouter demonstration completed successfully!")
        print("🎯 Key Features Demonstrated:")
        print("  • Complexity analysis and classification")
        print("  • Context-aware model selection")
        print("  • SuperClaude persona integration")
        print("  • Slash-command parsing and routing")
        print("  • Cost-performance optimization")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
