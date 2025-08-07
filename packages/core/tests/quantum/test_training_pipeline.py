"""
Tests for Quantum-Integrated DQN Training Pipeline

This module tests the integration between the DQN agent and the existing
QuantumManager system, validating the training pipeline that leverages
quantum execution results for reinforcement learning.
"""

import asyncio
import pytest
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from monkey_coder.models import ProviderType, TaskType, ExecuteRequest, ExecutionContext
from monkey_coder.quantum.manager import QuantumResult, CollapseStrategy
from monkey_coder.quantum.dqn_agent import DQNRoutingAgent, RoutingState, RoutingAction
from monkey_coder.quantum.training_pipeline import (
    QuantumDQNTrainer,
    TrainingScenario,
    TrainingPhase,
    QuantumTrainingResult,
    TrainingScenarioGenerator,
    create_quantum_dqn_trainer
)


class TestTrainingScenario:
    """Test training scenario data structure."""
    
    def test_training_scenario_creation(self):
        """Test creating a training scenario."""
        scenario = TrainingScenario(
            task_type=TaskType.CODE_GENERATION,
            complexity=0.7,
            context_requirements={"timeout": 30, "max_tokens": 4096},
            provider_constraints={"openai": True, "anthropic": False},
            expected_strategy="performance",
            scenario_id="test_scenario_1"
        )
        
        assert scenario.task_type == TaskType.CODE_GENERATION
        assert scenario.complexity == 0.7
        assert scenario.context_requirements["timeout"] == 30
        assert scenario.provider_constraints["openai"] is True
        assert scenario.expected_strategy == "performance"
        assert scenario.scenario_id == "test_scenario_1"
        assert scenario.metadata is None
    
    def test_training_scenario_with_metadata(self):
        """Test training scenario with metadata."""
        metadata = {"source": "test", "priority": "high"}
        scenario = TrainingScenario(
            task_type=TaskType.DEBUGGING,
            complexity=0.5,
            context_requirements={},
            provider_constraints={},
            expected_strategy="task_optimized",
            scenario_id="test_scenario_2",
            metadata=metadata
        )
        
        assert scenario.metadata == metadata
        assert scenario.metadata["source"] == "test"


class TestQuantumDQNTrainer:
    """Test the quantum-integrated DQN trainer."""
    
    @pytest.fixture
    def mock_dqn_agent(self):
        """Mock DQN agent for testing."""
        agent = Mock(spec=DQNRoutingAgent)
        agent.state_size = 21
        agent.action_size = 12
        agent.exploration_rate = 0.5
        agent.act.return_value = RoutingAction(
            provider=ProviderType.OPENAI,
            model="gpt-4.1",
            strategy="performance"
        )
        agent.remember = Mock()
        agent.replay.return_value = 0.05  # Mock training loss
        agent.update_routing_performance = Mock()
        agent.get_performance_metrics.return_value = {
            "exploration_rate": 0.5,
            "training_steps": 10,
            "memory_utilization": 0.3
        }
        return agent
    
    @pytest.fixture
    def trainer(self, mock_dqn_agent):
        """Create quantum DQN trainer for testing."""
        with patch('monkey_coder.quantum.training_pipeline.QuantumManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.get_metrics.return_value = {"executions": []}
            mock_manager_class.return_value = mock_manager
            
            trainer = QuantumDQNTrainer(
                dqn_agent=mock_dqn_agent,
                max_workers=2,
                quantum_timeout=10.0,
                training_batch_size=4
            )
            return trainer
    
    @pytest.fixture
    def sample_scenario(self):
        """Create a sample training scenario."""
        return TrainingScenario(
            task_type=TaskType.CODE_GENERATION,
            complexity=0.6,
            context_requirements={"timeout": 30, "max_tokens": 4096},
            provider_constraints={"openai": True, "anthropic": True, "google": True},
            expected_strategy="performance",
            scenario_id="test_scenario"
        )
    
    def test_trainer_initialization(self, mock_dqn_agent):
        """Test trainer initialization."""
        with patch('monkey_coder.quantum.training_pipeline.QuantumManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.get_metrics.return_value = {"executions": []}
            mock_manager_class.return_value = mock_manager
            
            trainer = QuantumDQNTrainer(
                dqn_agent=mock_dqn_agent,
                max_workers=3,
                quantum_timeout=20.0,
                training_batch_size=8
            )
            
            assert trainer.dqn_agent == mock_dqn_agent
            assert trainer.training_batch_size == 8
            assert trainer.training_phase == TrainingPhase.EXPLORATION
            assert trainer.training_step == 0
            assert len(trainer.performance_history) == 0
            
            # Verify quantum manager was created with correct parameters
            mock_manager_class.assert_called_once_with(
                max_workers=3,
                timeout=20.0,
                default_strategy=CollapseStrategy.BEST_SCORE
            )
    
    def test_create_routing_state(self, trainer, sample_scenario):
        """Test conversion of scenario to routing state."""
        request = ExecuteRequest(
            task_type=TaskType.CODE_GENERATION,
            prompt="Test prompt",
            context=ExecutionContext(
                user_id="test_user",
                timeout=30,
                max_tokens=4096,
                temperature=0.1
            ),
            superclause_config={"persona": "developer"}
        )
        
        routing_state = trainer.create_routing_state(sample_scenario, request)
        
        assert isinstance(routing_state, RoutingState)
        assert routing_state.task_complexity == 0.6
        assert routing_state.context_type == "code_generation"
        assert "openai" in routing_state.provider_availability
        assert routing_state.provider_availability["openai"] is True
        assert "anthropic" in routing_state.historical_performance
        assert 0.0 <= routing_state.historical_performance["anthropic"] <= 1.0
        assert routing_state.resource_constraints["cost_weight"] == 0.33
        assert routing_state.user_preferences["preference_strength"] == 0.5
    
    def test_generate_provider_variations(self, trainer, sample_scenario):
        """Test generation of provider variations for quantum execution."""
        selected_action = RoutingAction(
            provider=ProviderType.OPENAI,
            model="gpt-4.1",
            strategy="performance"
        )
        
        variations = trainer.generate_provider_variations(selected_action, sample_scenario)
        
        # Should have at least the primary variation
        assert len(variations) >= 1
        
        # Check primary variation
        primary_var = variations[0]
        assert primary_var.id == "dqn_selected"
        assert primary_var.weight == 1.0
        assert primary_var.priority == 1
        assert primary_var.params["provider"] == ProviderType.OPENAI
        assert primary_var.params["model"] == "gpt-4.1"
        assert primary_var.params["strategy"] == "performance"
        assert primary_var.metadata["source"] == "dqn_selection"
    
    @pytest.mark.asyncio
    async def test_simulate_routing_execution(self, trainer, sample_scenario):
        """Test simulation of routing execution."""
        result = await trainer.simulate_routing_execution(
            provider=ProviderType.OPENAI,
            model="gpt-4.1",
            strategy="performance",
            scenario=sample_scenario
        )
        
        # Validate result structure
        assert isinstance(result, dict)
        assert "success" in result
        assert "execution_time" in result
        assert "quality_score" in result
        assert "cost_efficiency" in result
        assert "provider" in result
        assert "model" in result
        assert "strategy" in result
        
        # Validate result values
        assert isinstance(result["success"], bool)
        assert result["execution_time"] > 0
        assert 0.0 <= result["quality_score"] <= 1.0
        assert 0.0 <= result["cost_efficiency"] <= 1.0
        assert result["provider"] == "openai"
        assert result["model"] == "gpt-4.1"
        assert result["strategy"] == "performance"
    
    def test_calculate_success_probability(self, trainer, sample_scenario):
        """Test success probability calculation."""
        prob = trainer.calculate_success_probability(
            provider=ProviderType.ANTHROPIC,
            model="claude-opus-4-20250514",
            strategy="performance",
            scenario=sample_scenario
        )
        
        assert 0.1 <= prob <= 0.95
        
        # Test with different providers
        openai_prob = trainer.calculate_success_probability(
            ProviderType.OPENAI, "gpt-4.1", "performance", sample_scenario
        )
        groq_prob = trainer.calculate_success_probability(
            ProviderType.GROQ, "llama-3.3-70b-versatile", "performance", sample_scenario
        )
        
        # Anthropic should have higher probability than Groq for most tasks
        assert prob >= groq_prob
    
    def test_calculate_quality_score(self, trainer, sample_scenario):
        """Test quality score calculation."""
        score = trainer.calculate_quality_score(
            provider=ProviderType.ANTHROPIC,
            model="claude-opus-4-20250514",
            strategy="performance",
            scenario=sample_scenario
        )
        
        assert 0.0 <= score <= 1.0
        
        # Performance strategy should generally give higher quality
        perf_score = trainer.calculate_quality_score(
            ProviderType.ANTHROPIC, "claude-opus-4-20250514", "performance", sample_scenario
        )
        cost_score = trainer.calculate_quality_score(
            ProviderType.ANTHROPIC, "claude-opus-4-20250514", "cost_efficient", sample_scenario
        )
        
        assert perf_score >= cost_score
    
    def test_calculate_cost_efficiency(self, trainer):
        """Test cost efficiency calculation."""
        # Groq should be most cost efficient
        groq_efficiency = trainer.calculate_cost_efficiency(
            ProviderType.GROQ, "llama-3.3-70b-versatile", "cost_efficient"
        )
        
        # Anthropic should be least cost efficient
        anthropic_efficiency = trainer.calculate_cost_efficiency(
            ProviderType.ANTHROPIC, "claude-opus-4-20250514", "performance"
        )
        
        assert 0.0 <= groq_efficiency <= 1.0
        assert 0.0 <= anthropic_efficiency <= 1.0
        assert groq_efficiency >= anthropic_efficiency
    
    def test_calculate_routing_reward(self, trainer, sample_scenario):
        """Test reward calculation from quantum results."""
        # Mock successful quantum result
        quantum_result = QuantumResult(
            value={
                "success": True,
                "execution_time": 1.5,
                "quality_score": 0.8,
                "cost_efficiency": 0.7
            },
            success=True,
            execution_time=1.5
        )
        
        selected_action = RoutingAction(
            provider=ProviderType.OPENAI,
            model="gpt-4.1",
            strategy="performance"
        )
        
        reward = trainer.calculate_routing_reward(quantum_result, selected_action, sample_scenario)
        
        # Should be positive reward for successful execution with good quality
        assert reward > 0
        
        # Test failed execution
        failed_result = QuantumResult(
            value={"success": False},
            success=False
        )
        
        failed_reward = trainer.calculate_routing_reward(failed_result, selected_action, sample_scenario)
        assert failed_reward < 0
    
    @pytest.mark.asyncio
    async def test_train_routing_decision(self, trainer, sample_scenario):
        """Test training on a single routing decision."""
        # Mock quantum manager execution
        mock_quantum_result = QuantumResult(
            value={
                "success": True,
                "execution_time": 2.0,
                "quality_score": 0.75,
                "cost_efficiency": 0.6
            },
            success=True,
            execution_time=2.0
        )
        
        trainer.quantum_manager.execute_quantum_task = AsyncMock(return_value=mock_quantum_result)
        
        result = await trainer.train_routing_decision(sample_scenario)
        
        # Verify result structure
        assert isinstance(result, QuantumTrainingResult)
        assert result.selected_action.provider == ProviderType.OPENAI
        assert result.quantum_result == mock_quantum_result
        assert isinstance(result.calculated_reward, float)
        assert result.training_loss == 0.05  # From mock
        assert result.execution_time > 0
        assert result.scenario == sample_scenario
        
        # Verify DQN agent interactions
        trainer.dqn_agent.act.assert_called_once()
        trainer.dqn_agent.remember.assert_called_once()
        trainer.dqn_agent.replay.assert_called_once()
        trainer.dqn_agent.update_routing_performance.assert_called_once()
        
        # Verify quantum manager was called
        trainer.quantum_manager.execute_quantum_task.assert_called_once()
        call_args = trainer.quantum_manager.execute_quantum_task.call_args
        assert call_args[1]["collapse_strategy"] == CollapseStrategy.BEST_SCORE
    
    @pytest.mark.asyncio
    async def test_train_batch(self, trainer):
        """Test batch training functionality."""
        # Mock scenario generation
        trainer.generate_training_scenarios = Mock(return_value=[
            TrainingScenario(
                task_type=TaskType.CODE_GENERATION,
                complexity=0.5,
                context_requirements={},
                provider_constraints={"openai": True},
                expected_strategy="performance",
                scenario_id=f"batch_scenario_{i}"
            ) for i in range(3)
        ])
        
        # Mock training function
        async def mock_train_routing_decision(scenario):
            return QuantumTrainingResult(
                selected_action=RoutingAction(ProviderType.OPENAI, "gpt-4.1", "performance"),
                quantum_result=QuantumResult(value={"success": True}, success=True),
                calculated_reward=0.5,
                training_loss=0.05,
                performance_metrics={},
                execution_time=1.0,
                scenario=scenario
            )
        
        trainer.train_routing_decision = mock_train_routing_decision
        
        results = await trainer.train_batch(3)
        
        assert len(results) == 3
        assert all(isinstance(r, QuantumTrainingResult) for r in results)
        assert trainer.training_step > 0  # Should have incremented
    
    def test_update_training_phase(self, trainer):
        """Test training phase updates based on performance."""
        # Mock results with good performance
        good_results = [
            QuantumTrainingResult(
                selected_action=RoutingAction(ProviderType.OPENAI, "gpt-4.1", "performance"),
                quantum_result=QuantumResult(value={"success": True}, success=True),
                calculated_reward=0.8,  # Good reward
                training_loss=0.05,
                performance_metrics={},
                execution_time=1.0,
                scenario=Mock()
            ) for _ in range(10)
        ]
        
        # Start in exploration phase
        assert trainer.training_phase == TrainingPhase.EXPLORATION
        
        # Update with good results (success rate > 0.6)
        trainer.update_training_phase(good_results)
        
        # Should advance to learning phase
        assert trainer.training_phase == TrainingPhase.LEARNING
        assert len(trainer.performance_history) > 0
        
        # Create excellent results for further advancement
        excellent_results = [
            QuantumTrainingResult(
                selected_action=RoutingAction(ProviderType.OPENAI, "gpt-4.1", "performance"),
                quantum_result=QuantumResult(value={"success": True}, success=True),
                calculated_reward=1.0,  # Excellent reward
                training_loss=0.02,
                performance_metrics={},
                execution_time=1.0,
                scenario=Mock()
            ) for _ in range(10)
        ]
        
        trainer.update_training_phase(excellent_results)
        assert trainer.training_phase == TrainingPhase.OPTIMIZATION
    
    def test_get_training_metrics(self, trainer):
        """Test training metrics collection."""
        # Add some mock performance history
        trainer.performance_history = [
            {"step": 1, "avg_reward": 0.5, "success_rate": 0.7, "phase": "exploration"},
            {"step": 2, "avg_reward": 0.6, "success_rate": 0.8, "phase": "learning"}
        ]
        
        trainer.provider_performance["openai:gpt-4.1"] = [0.8, 0.7, 0.9]
        
        metrics = trainer.get_training_metrics()
        
        assert "training_step" in metrics
        assert "training_phase" in metrics
        assert "performance_history" in metrics
        assert "provider_performance" in metrics
        assert "dqn_metrics" in metrics
        assert "quantum_metrics" in metrics
        
        assert metrics["training_phase"] == TrainingPhase.EXPLORATION.value
        assert len(metrics["performance_history"]) == 2
        assert "openai:gpt-4.1" in metrics["provider_performance"]


class TestTrainingScenarioGenerator:
    """Test training scenario generation."""
    
    @pytest.fixture
    def generator(self):
        """Create scenario generator for testing."""
        return TrainingScenarioGenerator()
    
    def test_generator_initialization(self, generator):
        """Test scenario generator initialization."""
        assert isinstance(generator.scenario_templates, list)
        assert len(generator.scenario_templates) > 0
        
        # Check template structure
        template = generator.scenario_templates[0]
        assert "task_type" in template
        assert "complexity_range" in template
        assert "expected_strategy" in template
        assert "provider_constraints" in template
    
    def test_generate_scenarios_exploration(self, generator):
        """Test scenario generation for exploration phase."""
        scenarios = generator.generate_scenarios(5, TrainingPhase.EXPLORATION)
        
        assert len(scenarios) == 5
        assert all(isinstance(s, TrainingScenario) for s in scenarios)
        assert all(hasattr(s, "task_type") for s in scenarios)
        assert all(hasattr(s, "complexity") for s in scenarios)
        assert all(hasattr(s, "expected_strategy") for s in scenarios)
        
        # Exploration phase should have lower average complexity
        avg_complexity = np.mean([s.complexity for s in scenarios])
        assert avg_complexity < 0.7  # Should be relatively simple
    
    def test_generate_scenarios_evaluation(self, generator):
        """Test scenario generation for evaluation phase."""
        scenarios = generator.generate_scenarios(5, TrainingPhase.EVALUATION)
        
        assert len(scenarios) == 5
        
        # Evaluation phase should have higher average complexity
        avg_complexity = np.mean([s.complexity for s in scenarios])
        assert avg_complexity > 0.4  # Should be more challenging
    
    def test_scenario_diversity(self, generator):
        """Test that generated scenarios are diverse."""
        scenarios = generator.generate_scenarios(20, TrainingPhase.LEARNING)
        
        # Should have diverse task types
        task_types = [s.task_type for s in scenarios]
        unique_task_types = set(task_types)
        assert len(unique_task_types) > 1
        
        # Should have diverse strategies
        strategies = [s.expected_strategy for s in scenarios]
        unique_strategies = set(strategies)
        assert len(unique_strategies) > 1
        
        # Should have diverse complexities
        complexities = [s.complexity for s in scenarios]
        assert max(complexities) > min(complexities) + 0.2  # At least 0.2 spread


class TestConvenienceFunctions:
    """Test convenience functions for trainer creation."""
    
    def test_create_quantum_dqn_trainer(self):
        """Test convenience function for creating trainer."""
        with patch('monkey_coder.quantum.training_pipeline.DQNRoutingAgent') as mock_agent_class, \
             patch('monkey_coder.quantum.training_pipeline.QuantumDQNTrainer') as mock_trainer_class:
            
            mock_agent = Mock()
            mock_agent.initialize_networks = Mock()
            mock_agent_class.return_value = mock_agent
            
            mock_trainer = Mock()
            mock_trainer_class.return_value = mock_trainer
            
            result = create_quantum_dqn_trainer(
                state_size=25,
                action_size=15,
                learning_rate=0.002,
                max_workers=6
            )
            
            # Verify agent creation
            mock_agent_class.assert_called_once_with(
                state_size=25,
                action_size=15,
                learning_rate=0.002
            )
            mock_agent.initialize_networks.assert_called_once()
            
            # Verify trainer creation
            mock_trainer_class.assert_called_once_with(mock_agent, max_workers=6)
            
            assert result == mock_trainer


class TestTrainingIntegration:
    """Integration tests for quantum training pipeline."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_training_flow(self):
        """Test complete end-to-end training flow."""
        # Create real components (with mocked neural networks)
        with patch('monkey_coder.quantum.dqn_agent.DQNNetworkManager') as mock_network_manager:
            # Mock network manager
            mock_manager = Mock()
            mock_manager.create_networks.return_value = (Mock(), Mock())
            mock_manager.update_target_network = Mock()
            mock_network_manager.return_value = mock_manager
            
            # Create DQN agent
            dqn_agent = DQNRoutingAgent(state_size=21, action_size=12)
            dqn_agent.initialize_networks()
            
            # Create trainer
            trainer = QuantumDQNTrainer(
                dqn_agent=dqn_agent,
                max_workers=2,
                training_batch_size=2
            )
            
            # Mock quantum manager execution
            async def mock_execute_quantum_task(variations, **kwargs):
                return QuantumResult(
                    value={
                        "success": True,
                        "execution_time": 1.0,
                        "quality_score": 0.8,
                        "cost_efficiency": 0.7
                    },
                    success=True,
                    execution_time=1.0
                )
            
            trainer.quantum_manager.execute_quantum_task = mock_execute_quantum_task
            
            # Run training batch
            results = await trainer.train_batch(2)
            
            # Verify results
            assert len(results) == 2
            assert all(isinstance(r, QuantumTrainingResult) for r in results)
            assert all(r.calculated_reward > 0 for r in results)  # Should be positive rewards
            
            # Verify training progression
            assert trainer.training_step == 2  # Should have trained on 2 scenarios
            assert len(trainer.performance_history) > 0
    
    def test_realistic_scenario_generation(self):
        """Test that generated scenarios are realistic."""
        generator = TrainingScenarioGenerator()
        scenarios = generator.generate_scenarios(10, TrainingPhase.LEARNING)
        
        for scenario in scenarios:
            # Validate scenario realism
            assert 0.0 <= scenario.complexity <= 1.0
            assert isinstance(scenario.task_type, TaskType)
            assert scenario.expected_strategy in ["performance", "cost_efficient", "balanced", "task_optimized"]
            assert isinstance(scenario.provider_constraints, dict)
            assert isinstance(scenario.context_requirements, dict)
            assert scenario.scenario_id is not None
    
    def test_reward_calculation_sensitivity(self):
        """Test reward calculation sensitivity to different outcomes."""
        trainer = QuantumDQNTrainer(Mock(), max_workers=1)
        scenario = TrainingScenario(
            task_type=TaskType.CODE_GENERATION,
            complexity=0.5,
            context_requirements={},
            provider_constraints={},
            expected_strategy="performance",
            scenario_id="test"
        )
        
        action = RoutingAction(ProviderType.OPENAI, "gpt-4.1", "performance")
        
        # Test high-quality result
        high_quality_result = QuantumResult(
            value={
                "success": True,
                "execution_time": 1.0,
                "quality_score": 0.9,
                "cost_efficiency": 0.8
            },
            success=True
        )
        
        # Test low-quality result
        low_quality_result = QuantumResult(
            value={
                "success": True,
                "execution_time": 5.0,
                "quality_score": 0.3,
                "cost_efficiency": 0.4
            },
            success=True
        )
        
        high_reward = trainer.calculate_routing_reward(high_quality_result, action, scenario)
        low_reward = trainer.calculate_routing_reward(low_quality_result, action, scenario)
        
        # High quality should get better reward
        assert high_reward > low_reward
        assert high_reward > 1.0  # Should be significantly positive
        assert low_reward < high_reward  # But may still be positive due to success


class TestTrainingPerformance:
    """Performance tests for training pipeline."""
    
    @pytest.mark.asyncio
    async def test_batch_training_performance(self):
        """Test that batch training completes within reasonable time."""
        import time
        
        # Create lightweight trainer for performance testing
        with patch('monkey_coder.quantum.training_pipeline.QuantumManager'):
            mock_agent = Mock(spec=DQNRoutingAgent)
            mock_agent.act.return_value = RoutingAction(ProviderType.OPENAI, "gpt-4.1", "performance")
            mock_agent.remember = Mock()
            mock_agent.replay.return_value = 0.05
            mock_agent.update_routing_performance = Mock()
            mock_agent.get_performance_metrics.return_value = {}
            
            trainer = QuantumDQNTrainer(mock_agent, max_workers=4, training_batch_size=10)
            
            # Mock fast quantum execution
            async def fast_quantum_execution(variations, **kwargs):
                await asyncio.sleep(0.01)  # Minimal delay
                return QuantumResult(
                    value={"success": True, "quality_score": 0.8},
                    success=True,
                    execution_time=0.01
                )
            
            trainer.quantum_manager.execute_quantum_task = fast_quantum_execution
            
            # Measure batch training time
            start_time = time.perf_counter()
            results = await trainer.train_batch(10)
            training_time = time.perf_counter() - start_time
            
            # Should complete batch training quickly
            assert training_time < 2.0  # Should take less than 2 seconds for 10 scenarios
            assert len(results) == 10
    
    def test_memory_usage_scaling(self):
        """Test that memory usage scales reasonably with training scenarios."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create multiple trainers to test memory scaling
        trainers = []
        for i in range(5):
            with patch('monkey_coder.quantum.training_pipeline.QuantumManager'):
                mock_agent = Mock(spec=DQNRoutingAgent)
                trainer = QuantumDQNTrainer(mock_agent, max_workers=2)
                trainers.append(trainer)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for 5 trainers)
        assert memory_increase < 100, f"Memory increased by {memory_increase:.1f}MB"
        
        # Cleanup
        del trainers