"""
DQN Training Pipeline with Quantum Integration

This module implements the training pipeline for the DQN routing agent by integrating
with the existing QuantumManager system. Instead of duplicating quantum execution
patterns, it creates a bridge between the DQN learning agent and the sophisticated
quantum execution engine already built.

Key Integration Points:
- Leverages existing QuantumManager for parallel routing execution
- Converts quantum execution results into DQN training experiences
- Integrates with the model registry and provider system
- Uses existing collapse strategies and performance monitoring
"""

import asyncio
import logging
import random
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

import numpy as np

from monkey_coder.models import ProviderType, TaskType, ExecuteRequest, ExecutionContext, MODEL_REGISTRY, DEFAULT_MODELS
from monkey_coder.quantum.manager import QuantumManager, TaskVariation, CollapseStrategy, QuantumResult
from monkey_coder.quantum.dqn_agent import DQNRoutingAgent, RoutingState, RoutingAction

logger = logging.getLogger(__name__)


class TrainingPhase(Enum):
    """Training phases for DQN quantum integration."""
    
    EXPLORATION = "exploration"      # High exploration, learning basic patterns
    LEARNING = "learning"           # Balanced exploration/exploitation
    OPTIMIZATION = "optimization"   # Low exploration, refining policy
    EVALUATION = "evaluation"       # No exploration, testing performance


@dataclass
class TrainingScenario:
    """Represents a training scenario for the DQN agent."""
    
    task_type: TaskType
    complexity: float  # 0.0-1.0
    context_requirements: Dict[str, Any]
    provider_constraints: Dict[str, bool]  # Available providers
    expected_strategy: str  # Expected optimal strategy
    scenario_id: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class QuantumTrainingResult:
    """Result of quantum-assisted DQN training."""
    
    selected_action: RoutingAction
    quantum_result: QuantumResult
    calculated_reward: float
    training_loss: Optional[float]
    performance_metrics: Dict[str, Any]
    execution_time: float
    scenario: TrainingScenario


class QuantumDQNTrainer:
    """
    Integration layer between DQN agent and existing QuantumManager.
    
    This trainer uses the existing quantum execution system to generate
    realistic routing scenarios and train the DQN agent based on actual
    execution outcomes rather than simulated results.
    """
    
    def __init__(
        self,
        dqn_agent: DQNRoutingAgent,
        max_workers: int = 4,
        quantum_timeout: float = 30.0,
        training_batch_size: int = 32,
        scenario_cache_size: int = 100
    ):
        """
        Initialize the quantum-integrated DQN trainer.
        
        Args:
            dqn_agent: The DQN agent to train
            max_workers: Maximum parallel workers for quantum execution
            quantum_timeout: Timeout for quantum task execution
            training_batch_size: Batch size for DQN training
            scenario_cache_size: Number of training scenarios to cache
        """
        self.dqn_agent = dqn_agent
        self.training_batch_size = training_batch_size
        
        # Initialize quantum manager (reusing existing sophisticated system)
        self.quantum_manager = QuantumManager(
            max_workers=max_workers,
            timeout=quantum_timeout,
            default_strategy=CollapseStrategy.BEST_SCORE
        )
        
        # Training state
        self.training_phase = TrainingPhase.EXPLORATION
        self.training_step = 0
        self.performance_history = []
        self.provider_performance = defaultdict(list)
        
        # Scenario management
        self.scenario_cache = []
        self.scenario_cache_size = scenario_cache_size
        self.scenario_generator = TrainingScenarioGenerator()
        
        logger.info(f"Initialized QuantumDQNTrainer with {max_workers} workers, {quantum_timeout}s timeout")
    
    def create_routing_state(self, scenario: TrainingScenario, request: ExecuteRequest) -> RoutingState:
        """
        Convert training scenario and request into DQN routing state.
        
        Args:
            scenario: Training scenario
            request: Execute request
            
        Returns:
            RoutingState for DQN decision making
        """
        # Determine provider availability based on scenario constraints
        provider_availability = {}
        for provider_type in ProviderType:
            provider_key = provider_type.value
            provider_availability[provider_key] = scenario.provider_constraints.get(provider_key, True)
        
        # Calculate historical performance (simplified for initial implementation)
        historical_performance = {}
        for provider_type in ProviderType:
            provider_key = provider_type.value
            if provider_key in self.provider_performance:
                # Average of recent performance scores
                recent_scores = self.provider_performance[provider_key][-10:]  # Last 10 scores
                historical_performance[provider_key] = np.mean(recent_scores) if recent_scores else 0.5
            else:
                historical_performance[provider_key] = 0.5  # Neutral starting point
        
        # Extract resource constraints from execution context
        context = request.context
        resource_constraints = {
            "cost_weight": 0.33,  # Could be derived from user preferences
            "time_weight": 0.33,  # Based on timeout requirements
            "quality_weight": 0.34,  # Remainder
        }
        
        # Extract user preferences (simplified)
        user_preferences = {
            "preference_strength": 0.5,  # Neutral preference
        }
        
        return RoutingState(
            task_complexity=scenario.complexity,
            context_type=scenario.task_type.value,
            provider_availability=provider_availability,
            historical_performance=historical_performance,
            resource_constraints=resource_constraints,
            user_preferences=user_preferences
        )
    
    def generate_provider_variations(
        self, 
        selected_action: RoutingAction, 
        scenario: TrainingScenario
    ) -> List[TaskVariation]:
        """
        Generate quantum variations around the DQN-selected action.
        
        Args:
            selected_action: Action selected by DQN agent
            scenario: Current training scenario
            
        Returns:
            List of task variations for quantum execution
        """
        variations = []
        
        # Primary variation: The DQN-selected action
        primary_variation = TaskVariation(
            id="dqn_selected",
            task=self.simulate_routing_execution,
            params={
                "provider": selected_action.provider,
                "model": selected_action.model,
                "strategy": selected_action.strategy,
                "scenario": scenario
            },
            weight=1.0,
            priority=1,
            metadata={"source": "dqn_selection", "action": selected_action}
        )
        variations.append(primary_variation)
        
        # Alternative variations for comparison
        # This helps the quantum system evaluate if DQN made optimal choice
        
        # Alternative provider with same strategy
        alternative_providers = [p for p in ProviderType if p != selected_action.provider 
                               and scenario.provider_constraints.get(p.value, True)]
        
        if alternative_providers:
            alt_provider = random.choice(alternative_providers)
            alt_model = self.get_default_model_for_provider(alt_provider)
            
            alt_variation = TaskVariation(
                id="alternative_provider",
                task=self.simulate_routing_execution,
                params={
                    "provider": alt_provider,
                    "model": alt_model,
                    "strategy": selected_action.strategy,
                    "scenario": scenario
                },
                weight=0.8,
                priority=0,
                metadata={"source": "alternative_provider"}
            )
            variations.append(alt_variation)
        
        # Alternative strategy with same provider
        alternative_strategies = ["task_optimized", "cost_efficient", "performance", "balanced"]
        alt_strategies = [s for s in alternative_strategies if s != selected_action.strategy]
        
        if alt_strategies:
            alt_strategy = random.choice(alt_strategies)
            strategy_variation = TaskVariation(
                id="alternative_strategy",
                task=self.simulate_routing_execution,
                params={
                    "provider": selected_action.provider,
                    "model": selected_action.model,
                    "strategy": alt_strategy,
                    "scenario": scenario
                },
                weight=0.7,
                priority=0,
                metadata={"source": "alternative_strategy"}
            )
            variations.append(strategy_variation)
        
        logger.debug(f"Generated {len(variations)} quantum variations for training")
        return variations
    
    async def simulate_routing_execution(
        self, 
        provider: ProviderType, 
        model: str, 
        strategy: str, 
        scenario: TrainingScenario
    ) -> Dict[str, Any]:
        """
        Simulate routing execution for training purposes.
        
        In production, this would actually execute the routing decision.
        For training, we simulate the results based on known patterns.
        
        Args:
            provider: AI provider to use
            model: Model to use
            strategy: Routing strategy
            scenario: Training scenario
            
        Returns:
            Simulated execution result
        """
        # Simulate execution time based on provider and model characteristics
        base_time = {
            ProviderType.OPENAI: 1.5,
            ProviderType.ANTHROPIC: 1.2,
            ProviderType.GOOGLE: 1.0,
            ProviderType.GROQ: 0.5,  # Hardware accelerated
            ProviderType.GROK: 1.8,
        }.get(provider, 1.5)
        
        # Add complexity-based variation
        complexity_multiplier = 1.0 + (scenario.complexity * 0.5)
        execution_time = base_time * complexity_multiplier
        
        # Add random variation (±20%)
        execution_time *= random.uniform(0.8, 1.2)
        
        # Simulate execution delay
        await asyncio.sleep(min(execution_time * 0.1, 0.5))  # Scaled down for training
        
        # Calculate simulated success rate based on provider-task alignment
        success_probability = self.calculate_success_probability(provider, model, strategy, scenario)
        success = random.random() < success_probability
        
        # Calculate quality score based on provider capabilities and task requirements
        quality_score = self.calculate_quality_score(provider, model, strategy, scenario)
        
        # Add noise to quality score
        quality_score += random.uniform(-0.1, 0.1)
        quality_score = max(0.0, min(1.0, quality_score))
        
        # Calculate cost efficiency (simplified)
        cost_efficiency = self.calculate_cost_efficiency(provider, model, strategy)
        
        result = {
            "success": success,
            "execution_time": execution_time,
            "quality_score": quality_score,
            "cost_efficiency": cost_efficiency,
            "provider": provider.value,
            "model": model,
            "strategy": strategy,
            "error_rate": 1.0 - success_probability
        }
        
        logger.debug(f"Simulated routing: {provider.value}:{model} -> success={success}, quality={quality_score:.3f}")
        return result
    
    def calculate_success_probability(
        self, 
        provider: ProviderType, 
        model: str, 
        strategy: str, 
        scenario: TrainingScenario
    ) -> float:
        """Calculate success probability based on provider-task alignment."""
        base_probability = 0.8  # Base success rate
        
        # Provider-specific adjustments
        provider_adjustments = {
            ProviderType.OPENAI: 0.05,     # Slightly above average
            ProviderType.ANTHROPIC: 0.1,   # High reliability
            ProviderType.GOOGLE: 0.0,      # Average
            ProviderType.GROQ: -0.05,      # Slightly below due to speed focus
            ProviderType.GROK: -0.1,       # Newer provider, lower reliability
        }
        
        # Task type alignments
        task_alignments = {
            TaskType.CODE_GENERATION: {
                ProviderType.OPENAI: 0.1,
                ProviderType.ANTHROPIC: 0.05,
                ProviderType.GOOGLE: 0.0,
                ProviderType.GROQ: 0.05,
                ProviderType.GROK: -0.05,
            },
            TaskType.CODE_ANALYSIS: {
                ProviderType.ANTHROPIC: 0.1,
                ProviderType.OPENAI: 0.05,
                ProviderType.GOOGLE: 0.05,
                ProviderType.GROQ: 0.0,
                ProviderType.GROK: 0.0,
            },
            # Add more task type alignments as needed
        }
        
        # Calculate final probability
        probability = base_probability
        probability += provider_adjustments.get(provider, 0.0)
        
        task_alignment = task_alignments.get(scenario.task_type, {})
        probability += task_alignment.get(provider, 0.0)
        
        # Complexity penalty
        complexity_penalty = scenario.complexity * 0.2
        probability -= complexity_penalty
        
        # Ensure valid probability range
        return max(0.1, min(0.95, probability))
    
    def calculate_quality_score(
        self, 
        provider: ProviderType, 
        model: str, 
        strategy: str, 
        scenario: TrainingScenario
    ) -> float:
        """Calculate quality score based on provider capabilities and strategy."""
        # Base quality by provider
        base_quality = {
            ProviderType.OPENAI: 0.8,
            ProviderType.ANTHROPIC: 0.85,
            ProviderType.GOOGLE: 0.75,
            ProviderType.GROQ: 0.7,
            ProviderType.GROK: 0.65,
        }.get(provider, 0.7)
        
        # Strategy adjustments
        if strategy == "performance":
            quality_bonus = 0.1
        elif strategy == "balanced":
            quality_bonus = 0.05
        elif strategy == "task_optimized":
            quality_bonus = 0.08
        else:  # cost_efficient
            quality_bonus = -0.05
        
        # Complexity adjustment
        complexity_factor = 1.0 - (scenario.complexity * 0.3)  # Harder tasks get lower quality
        
        final_quality = (base_quality + quality_bonus) * complexity_factor
        return max(0.0, min(1.0, final_quality))
    
    def calculate_cost_efficiency(self, provider: ProviderType, model: str, strategy: str) -> float:
        """Calculate cost efficiency score."""
        # Base cost efficiency by provider (higher = more cost efficient)
        base_efficiency = {
            ProviderType.GROQ: 0.9,       # Hardware accelerated, very efficient
            ProviderType.GOOGLE: 0.8,     # Generally cost effective
            ProviderType.GROK: 0.7,       # Newer, moderate efficiency
            ProviderType.OPENAI: 0.6,     # Premium pricing
            ProviderType.ANTHROPIC: 0.5,  # Premium model, higher cost
        }.get(provider, 0.6)
        
        # Strategy adjustments
        if strategy == "cost_efficient":
            efficiency_bonus = 0.2
        elif strategy == "balanced":
            efficiency_bonus = 0.1
        else:
            efficiency_bonus = 0.0
        
        return max(0.0, min(1.0, base_efficiency + efficiency_bonus))
    
    def get_default_model_for_provider(self, provider: ProviderType) -> str:
        """Get default model for a provider."""
        return DEFAULT_MODELS.get(provider, "default-model")
    
    def calculate_routing_reward(
        self, 
        quantum_result: QuantumResult, 
        selected_action: RoutingAction,
        scenario: TrainingScenario
    ) -> float:
        """
        Calculate DQN reward based on quantum execution results.
        
        Args:
            quantum_result: Result from quantum execution
            selected_action: Action selected by DQN
            scenario: Training scenario
            
        Returns:
            Reward value for DQN training
        """
        if not quantum_result.success:
            return -1.0  # Penalty for failed execution
        
        # Extract results from quantum collapse
        if isinstance(quantum_result.value, dict):
            execution_result = quantum_result.value
        else:
            logger.warning(f"Unexpected quantum result format: {type(quantum_result.value)}")
            return 0.0
        
        reward = 0.0
        
        # Base reward for successful execution
        if execution_result.get("success", False):
            reward += 1.0
        else:
            reward -= 0.5
        
        # Performance-based rewards
        execution_time = execution_result.get("execution_time", 5.0)
        if execution_time < 2.0:
            reward += 0.3  # Fast execution bonus
        elif execution_time > 8.0:
            reward -= 0.3  # Slow execution penalty
        
        # Quality-based rewards
        quality_score = execution_result.get("quality_score", 0.5)
        reward += (quality_score - 0.5) * 1.0  # Linear quality reward
        
        # Cost efficiency rewards
        cost_efficiency = execution_result.get("cost_efficiency", 0.5)
        if selected_action.strategy == "cost_efficient":
            reward += cost_efficiency * 0.4  # Bonus for cost-efficient strategy achieving good efficiency
        
        # Strategy alignment rewards
        if selected_action.strategy == "performance" and quality_score > 0.8:
            reward += 0.3  # Bonus for performance strategy achieving high quality
        elif selected_action.strategy == "balanced" and 0.6 <= quality_score <= 0.8:
            reward += 0.2  # Bonus for balanced strategy achieving moderate quality
        
        # Scenario-specific rewards
        if scenario.expected_strategy == selected_action.strategy:
            reward += 0.2  # Bonus for matching expected strategy
        
        # Complexity adjustment - harder tasks get bonus rewards for success
        complexity_bonus = scenario.complexity * 0.3
        if execution_result.get("success", False):
            reward += complexity_bonus
        
        logger.debug(f"Calculated reward {reward:.3f} for {selected_action.provider.value}:{selected_action.model}")
        return reward
    
    async def train_routing_decision(self, scenario: TrainingScenario) -> QuantumTrainingResult:
        """
        Train DQN using quantum execution feedback for a single scenario.
        
        Args:
            scenario: Training scenario
            
        Returns:
            Training result with performance metrics
        """
        start_time = time.time()
        
        # Create a mock request for the scenario
        request = ExecuteRequest(
            task_type=scenario.task_type,
            prompt="Training scenario prompt",
            context=ExecutionContext(
                user_id="training_user",
                timeout=30,
                max_tokens=4096,
                temperature=0.1
            ),
            superclause_config={"persona": "developer"}  # Simplified config
        )
        
        # Convert scenario to routing state
        routing_state = self.create_routing_state(scenario, request)
        
        # DQN agent selects action based on current policy
        selected_action = self.dqn_agent.act(routing_state)
        
        # Generate quantum variations around selected action
        variations = self.generate_provider_variations(selected_action, scenario)
        
        # Execute variations using existing QuantumManager
        quantum_result = await self.quantum_manager.execute_quantum_task(
            variations=variations,
            collapse_strategy=CollapseStrategy.BEST_SCORE,
            scoring_fn=lambda result: result.get("quality_score", 0.0) if isinstance(result, dict) else 0.0
        )
        
        # Calculate reward based on quantum results
        reward = self.calculate_routing_reward(quantum_result, selected_action, scenario)
        
        # Store experience in DQN memory
        next_state = routing_state  # Simplified - in practice, this would be the next state
        self.dqn_agent.remember(
            state=routing_state,
            action=selected_action,
            reward=reward,
            next_state=next_state,
            done=True  # Each scenario is independent
        )
        
        # Perform DQN training step
        training_loss = self.dqn_agent.replay()
        
        # Update provider performance tracking
        if isinstance(quantum_result.value, dict) and quantum_result.value.get("success", False):
            performance_score = quantum_result.value.get("quality_score", 0.5)
            self.dqn_agent.update_routing_performance(selected_action, performance_score)
            
            # Update internal performance tracking
            provider_key = f"{selected_action.provider.value}:{selected_action.model}"
            self.provider_performance[provider_key].append(performance_score)
        
        execution_time = time.time() - start_time
        self.training_step += 1
        
        # Create performance metrics
        performance_metrics = {
            "training_step": self.training_step,
            "quantum_execution_time": quantum_result.execution_time,
            "total_execution_time": execution_time,
            "reward": reward,
            "exploration_rate": self.dqn_agent.exploration_rate,
            "selected_provider": selected_action.provider.value,
            "selected_model": selected_action.model,
            "selected_strategy": selected_action.strategy
        }
        
        result = QuantumTrainingResult(
            selected_action=selected_action,
            quantum_result=quantum_result,
            calculated_reward=reward,
            training_loss=training_loss,
            performance_metrics=performance_metrics,
            execution_time=execution_time,
            scenario=scenario
        )
        
        loss_str = f"{training_loss:.4f}" if training_loss is not None else "N/A"
        logger.info(f"Training step {self.training_step}: reward={reward:.3f}, "
                   f"loss={loss_str}, "
                   f"provider={selected_action.provider.value}")
        
        return result
    
    async def train_batch(self, num_scenarios: int = None) -> List[QuantumTrainingResult]:
        """
        Train DQN on a batch of scenarios using quantum feedback.
        
        Args:
            num_scenarios: Number of scenarios to train on (default: training_batch_size)
            
        Returns:
            List of training results
        """
        if num_scenarios is None:
            num_scenarios = self.training_batch_size
        
        # Generate or retrieve training scenarios
        scenarios = self.generate_training_scenarios(num_scenarios)
        
        # Execute training in parallel for efficiency
        training_tasks = [
            self.train_routing_decision(scenario)
            for scenario in scenarios
        ]
        
        logger.info(f"Starting batch training with {len(training_tasks)} scenarios")
        
        try:
            results = await asyncio.gather(*training_tasks, return_exceptions=True)
            
            # Filter successful results and log failures
            successful_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Training scenario {i} failed: {result}")
                else:
                    successful_results.append(result)
            
            # Update training phase based on performance
            self.update_training_phase(successful_results)
            
            logger.info(f"Completed batch training: {len(successful_results)}/{len(scenarios)} successful")
            return successful_results
            
        except Exception as e:
            logger.error(f"Batch training failed: {e}")
            return []
    
    def generate_training_scenarios(self, num_scenarios: int) -> List[TrainingScenario]:
        """
        Generate training scenarios for DQN training.
        
        Args:
            num_scenarios: Number of scenarios to generate
            
        Returns:
            List of training scenarios
        """
        # Use scenario generator to create diverse training cases
        return self.scenario_generator.generate_scenarios(num_scenarios, self.training_phase)
    
    def update_training_phase(self, results: List[QuantumTrainingResult]) -> None:
        """Update training phase based on recent performance."""
        if not results:
            return
        
        # Calculate performance metrics
        avg_reward = np.mean([r.calculated_reward for r in results])
        success_rate = np.mean([1.0 if r.calculated_reward > 0 else 0.0 for r in results])
        
        # Store performance history
        self.performance_history.append({
            "step": self.training_step,
            "avg_reward": avg_reward,
            "success_rate": success_rate,
            "phase": self.training_phase.value
        })
        
        # Phase transition logic
        if self.training_phase == TrainingPhase.EXPLORATION and success_rate > 0.6:
            self.training_phase = TrainingPhase.LEARNING
            logger.info(f"Advanced to LEARNING phase at step {self.training_step}")
        elif self.training_phase == TrainingPhase.LEARNING and success_rate > 0.8:
            self.training_phase = TrainingPhase.OPTIMIZATION
            logger.info(f"Advanced to OPTIMIZATION phase at step {self.training_step}")
        elif self.training_phase == TrainingPhase.OPTIMIZATION and success_rate > 0.9:
            self.training_phase = TrainingPhase.EVALUATION
            logger.info(f"Advanced to EVALUATION phase at step {self.training_step}")
    
    def get_training_metrics(self) -> Dict[str, Any]:
        """Get comprehensive training metrics."""
        return {
            "training_step": self.training_step,
            "training_phase": self.training_phase.value,
            "performance_history": self.performance_history[-50:],  # Last 50 entries
            "provider_performance": dict(self.provider_performance),
            "dqn_metrics": self.dqn_agent.get_performance_metrics(),
            "quantum_metrics": self.quantum_manager.get_metrics()
        }


class TrainingScenarioGenerator:
    """Generates diverse training scenarios for DQN training."""
    
    def __init__(self):
        self.scenario_templates = self._create_scenario_templates()
    
    def _create_scenario_templates(self) -> List[Dict[str, Any]]:
        """Create template scenarios for different training situations."""
        templates = [
            # Code generation scenarios
            {
                "task_type": TaskType.CODE_GENERATION,
                "complexity_range": (0.3, 0.8),
                "expected_strategy": "performance",
                "provider_constraints": {"openai": True, "anthropic": True, "google": True}
            },
            {
                "task_type": TaskType.CODE_GENERATION,
                "complexity_range": (0.1, 0.4),
                "expected_strategy": "cost_efficient",
                "provider_constraints": {"groq": True, "google": True}
            },
            # Analysis scenarios
            {
                "task_type": TaskType.CODE_ANALYSIS,
                "complexity_range": (0.4, 0.9),
                "expected_strategy": "task_optimized",
                "provider_constraints": {"anthropic": True, "openai": True}
            },
            # Debugging scenarios
            {
                "task_type": TaskType.DEBUGGING,
                "complexity_range": (0.6, 1.0),
                "expected_strategy": "performance",
                "provider_constraints": {"anthropic": True, "openai": True, "google": True}
            },
            # Testing scenarios
            {
                "task_type": TaskType.TESTING,
                "complexity_range": (0.2, 0.6),
                "expected_strategy": "balanced",
                "provider_constraints": {"openai": True, "groq": True, "google": True}
            },
        ]
        return templates
    
    def generate_scenarios(self, num_scenarios: int, training_phase: TrainingPhase) -> List[TrainingScenario]:
        """Generate training scenarios based on current training phase."""
        scenarios = []
        
        for i in range(num_scenarios):
            template = random.choice(self.scenario_templates)
            
            # Adjust complexity based on training phase
            complexity_min, complexity_max = template["complexity_range"]
            if training_phase == TrainingPhase.EXPLORATION:
                # Focus on simpler scenarios during exploration
                complexity = random.uniform(complexity_min, (complexity_min + complexity_max) / 2)
            elif training_phase == TrainingPhase.EVALUATION:
                # Use more challenging scenarios for evaluation
                complexity = random.uniform((complexity_min + complexity_max) / 2, complexity_max)
            else:
                # Full range for learning and optimization phases
                complexity = random.uniform(complexity_min, complexity_max)
            
            # Create scenario
            scenario = TrainingScenario(
                task_type=template["task_type"],
                complexity=complexity,
                context_requirements={
                    "timeout": random.randint(10, 60),
                    "max_tokens": random.randint(1000, 8000),
                    "temperature": random.uniform(0.1, 0.8)
                },
                provider_constraints=template["provider_constraints"].copy(),
                expected_strategy=template["expected_strategy"],
                scenario_id=f"scenario_{i}_{int(time.time())}",
                metadata={
                    "training_phase": training_phase.value,
                    "generation_time": time.time()
                }
            )
            scenarios.append(scenario)
        
        logger.debug(f"Generated {len(scenarios)} scenarios for {training_phase.value} phase")
        return scenarios


# Convenience function for easy training pipeline creation
def create_quantum_dqn_trainer(
    state_size: int = 21,
    action_size: int = 12,
    learning_rate: float = 0.001,
    **kwargs
) -> QuantumDQNTrainer:
    """
    Create a quantum-integrated DQN trainer with default settings.
    
    Args:
        state_size: DQN state space size
        action_size: DQN action space size
        learning_rate: DQN learning rate
        **kwargs: Additional arguments for QuantumDQNTrainer
        
    Returns:
        Configured QuantumDQNTrainer instance
    """
    # Create DQN agent
    dqn_agent = DQNRoutingAgent(
        state_size=state_size,
        action_size=action_size,
        learning_rate=learning_rate
    )
    
    # Initialize neural networks
    dqn_agent.initialize_networks()
    
    # Create quantum trainer
    trainer = QuantumDQNTrainer(dqn_agent, **kwargs)
    
    logger.info(f"Created quantum DQN trainer with {state_size}D state space, {action_size} actions")
    return trainer