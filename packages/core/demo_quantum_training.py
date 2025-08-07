#!/usr/bin/env python3
"""
Quantum DQN Training Pipeline Demonstration

This script demonstrates the quantum-integrated DQN training system
that combines the existing QuantumManager with DQN reinforcement learning
for intelligent AI model routing decisions.
"""

import asyncio
import json
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import our quantum training pipeline
from monkey_coder.quantum import (
    create_quantum_dqn_trainer,
    TrainingPhase,
    TrainingScenario
)
from monkey_coder.models import TaskType


async def demonstrate_quantum_training():
    """Demonstrate the quantum DQN training pipeline."""
    
    print("🚀 Quantum DQN Training Pipeline Demonstration")
    print("=" * 60)
    
    # Create quantum-integrated DQN trainer
    print("\n📦 Creating Quantum DQN Trainer...")
    trainer = create_quantum_dqn_trainer(
        state_size=21,      # DQN state space size
        action_size=12,     # Number of routing actions
        learning_rate=0.001,
        max_workers=2,      # Quantum execution workers
        training_batch_size=3
    )
    
    print(f"✅ Created trainer with DQN agent (state_size=21, action_size=12)")
    print(f"   Quantum Manager: {trainer.quantum_manager.__class__.__name__}")
    print(f"   Training Phase: {trainer.training_phase.value}")
    print(f"   Training Step: {trainer.training_step}")
    
    # Display initial metrics
    print("\n📊 Initial Metrics:")
    initial_metrics = trainer.get_training_metrics()
    print(f"   DQN Exploration Rate: {initial_metrics['dqn_metrics']['exploration_rate']:.3f}")
    print(f"   DQN Memory Utilization: {initial_metrics['dqn_metrics']['memory_utilization']:.3f}")
    print(f"   Training Phase: {initial_metrics['training_phase']}")
    
    # Generate sample training scenarios
    print("\n🎯 Generating Training Scenarios...")
    scenario_generator = trainer.scenario_generator
    
    scenarios = scenario_generator.generate_scenarios(5, TrainingPhase.EXPLORATION)
    print(f"✅ Generated {len(scenarios)} training scenarios:")
    
    for i, scenario in enumerate(scenarios):
        print(f"   {i+1}. {scenario.task_type.value} (complexity: {scenario.complexity:.2f}, "
              f"strategy: {scenario.expected_strategy})")
    
    # Mock quantum execution for demonstration (since we don't have actual AI providers)
    print("\n⚛️  Setting up Mock Quantum Execution...")
    
    async def mock_quantum_execution(variations, **kwargs):
        """Mock quantum execution for demonstration."""
        await asyncio.sleep(0.1)  # Simulate execution time
        
        # Simulate realistic results based on provider
        primary_variation = variations[0]
        provider = primary_variation.params.get("provider")
        model = primary_variation.params.get("model")
        strategy = primary_variation.params.get("strategy")
        
        # Simulate provider-specific performance
        quality_scores = {
            "openai": 0.85,
            "anthropic": 0.90,
            "google": 0.80,
            "groq": 0.75,
            "grok": 0.70
        }
        
        base_quality = quality_scores.get(provider.value if hasattr(provider, 'value') else str(provider), 0.75)
        
        # Add strategy bonus
        strategy_bonus = {
            "performance": 0.1,
            "balanced": 0.05,
            "task_optimized": 0.08,
            "cost_efficient": -0.05
        }.get(strategy, 0.0)
        
        final_quality = min(1.0, base_quality + strategy_bonus)
        
        from monkey_coder.quantum.manager import QuantumResult
        
        return QuantumResult(
            value={
                "success": True,
                "execution_time": 1.5,
                "quality_score": final_quality,
                "cost_efficiency": 0.7,
                "provider": provider.value if hasattr(provider, 'value') else str(provider),
                "model": model,
                "strategy": strategy
            },
            success=True,
            execution_time=1.5
        )
    
    # Replace quantum manager's execute method with our mock
    trainer.quantum_manager.execute_quantum_task = mock_quantum_execution
    
    # Demonstrate single training step
    print("\n🎓 Running Single Training Step...")
    sample_scenario = scenarios[0]
    training_result = await trainer.train_routing_decision(sample_scenario)
    
    print(f"✅ Training Result:")
    print(f"   Selected Action: {training_result.selected_action.provider.value}:"
          f"{training_result.selected_action.model} ({training_result.selected_action.strategy})")
    print(f"   Calculated Reward: {training_result.calculated_reward:.3f}")
    loss_str = f"{training_result.training_loss:.4f}" if training_result.training_loss is not None else "N/A"
    print(f"   Training Loss: {loss_str}")
    print(f"   Execution Time: {training_result.execution_time:.3f}s")
    
    # Demonstrate batch training
    print("\n📚 Running Batch Training...")
    batch_results = await trainer.train_batch(3)
    
    print(f"✅ Batch Training Complete:")
    print(f"   Scenarios Processed: {len(batch_results)}")
    
    if batch_results:
        avg_reward = sum(r.calculated_reward for r in batch_results) / len(batch_results)
        success_rate = sum(1 for r in batch_results if r.calculated_reward > 0) / len(batch_results)
        
        print(f"   Average Reward: {avg_reward:.3f}")
        print(f"   Success Rate: {success_rate:.1%}")
        
        print(f"\n   Detailed Results:")
        for i, result in enumerate(batch_results):
            print(f"     {i+1}. {result.selected_action.provider.value}:"
                  f"{result.selected_action.model} -> reward: {result.calculated_reward:.3f}")
    
    # Show final metrics
    print("\n📊 Final Training Metrics:")
    final_metrics = trainer.get_training_metrics()
    
    print(f"   Training Steps: {final_metrics['training_step']}")
    print(f"   Training Phase: {final_metrics['training_phase']}")
    print(f"   DQN Exploration Rate: {final_metrics['dqn_metrics']['exploration_rate']:.3f}")
    print(f"   DQN Memory Utilization: {final_metrics['dqn_metrics']['memory_utilization']:.3f}")
    
    if final_metrics['performance_history']:
        latest_perf = final_metrics['performance_history'][-1]
        print(f"   Latest Performance: {latest_perf['avg_reward']:.3f} avg reward, "
              f"{latest_perf['success_rate']:.1%} success rate")
    
    # Show provider performance tracking
    if final_metrics['provider_performance']:
        print(f"\n🏆 Provider Performance Tracking:")
        for provider_key, scores in final_metrics['provider_performance'].items():
            if scores:  # Only show providers with data
                avg_score = sum(scores) / len(scores) if isinstance(scores, list) else scores
                print(f"   {provider_key}: {avg_score:.3f} average performance")
    
    print("\n✨ Quantum DQN Training Demonstration Complete!")
    print("\n💡 Key Features Demonstrated:")
    print("   ✅ Quantum-DQN Integration: Existing QuantumManager + New DQN Learning")
    print("   ✅ Smart Training Scenarios: Realistic routing situations for training")
    print("   ✅ Reward Calculation: Quality, speed, cost efficiency feedback")
    print("   ✅ Experience Collection: Automated DQN memory management")
    print("   ✅ Performance Tracking: Provider and model effectiveness monitoring")
    print("   ✅ Phase Management: Automatic progression through training phases")


def demonstrate_training_scenario_generation():
    """Demonstrate the training scenario generation system."""
    
    print("\n🎯 Training Scenario Generation Demonstration")
    print("=" * 50)
    
    from monkey_coder.quantum.training_pipeline import TrainingScenarioGenerator
    
    generator = TrainingScenarioGenerator()
    
    # Generate scenarios for different phases
    phases = [TrainingPhase.EXPLORATION, TrainingPhase.LEARNING, TrainingPhase.EVALUATION]
    
    for phase in phases:
        print(f"\n📋 {phase.value.title()} Phase Scenarios:")
        scenarios = generator.generate_scenarios(3, phase)
        
        for i, scenario in enumerate(scenarios):
            print(f"   {i+1}. Type: {scenario.task_type.value}")
            print(f"      Complexity: {scenario.complexity:.2f}")
            print(f"      Expected Strategy: {scenario.expected_strategy}")
            print(f"      Providers: {list(scenario.provider_constraints.keys())}")


def demonstrate_quantum_integration():
    """Demonstrate how our system integrates with existing quantum patterns."""
    
    print("\n⚛️  Quantum Integration Architecture")
    print("=" * 40)
    
    print("\n🔧 Integration Points:")
    print("   📦 Existing QuantumManager -> Parallel routing execution")
    print("   🧠 New DQN Agent        -> Learning from execution results") 
    print("   🔄 Integration Layer    -> Bridges quantum execution with DQN learning")
    print("   🎯 Training Pipeline    -> Systematic learning from realistic scenarios")
    
    print("\n🏗️  Architecture Flow:")
    print("   1. DQN Agent selects routing action based on current policy")
    print("   2. Generate quantum variations around selected action")
    print("   3. Execute variations using existing QuantumManager")
    print("   4. Calculate reward based on quantum execution results")
    print("   5. Store experience and train DQN with quantum feedback")
    print("   6. Update provider performance tracking")
    print("   7. Progress through training phases automatically")
    
    print("\n💡 Key Benefits:")
    print("   ✅ Leverages existing sophisticated quantum execution system")
    print("   ✅ No code duplication - builds on proven patterns")
    print("   ✅ Realistic training data from actual quantum execution")
    print("   ✅ Automatic learning from provider performance outcomes")
    print("   ✅ Progressive training phases with automatic advancement")


if __name__ == "__main__":
    print("🌟 Monkey Coder Quantum DQN Training System")
    print("Building intelligent AI routing through quantum-integrated reinforcement learning")
    print("=" * 80)
    
    # Run demonstrations
    try:
        # Show architecture integration
        demonstrate_quantum_integration()
        
        # Show scenario generation
        demonstrate_training_scenario_generation()
        
        # Run main training demonstration
        asyncio.run(demonstrate_quantum_training())
        
        print(f"\n🎉 All demonstrations completed successfully!")
        print("The quantum DQN training pipeline is ready for integration with the routing system.")
        
    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        import traceback
        traceback.print_exc()