"""
Test suite for Enhanced DQN Agent

This module tests the DQN routing agent implementation,
ensuring it follows the patterns from monkey1 and meets
the requirements for quantum routing.
"""

import json
import tempfile
import unittest
from unittest.mock import Mock, patch

import numpy as np
import pytest

from monkey_coder.models import ProviderType
from monkey_coder.quantum.dqn_agent import (
    DQNRoutingAgent,
    RoutingAction,
    RoutingState,
)


class TestRoutingState(unittest.TestCase):
    """Test cases for RoutingState."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_state = RoutingState(
            task_complexity=0.7,
            context_type="code_generation",
            provider_availability={
                "openai": True,
                "anthropic": True,
                "google": False,
                "groq": True,
                "grok": False,
            },
            historical_performance={
                "openai": 0.8,
                "anthropic": 0.9,
                "groq": 0.6,
            },
            resource_constraints={
                "cost_weight": 0.3,
                "time_weight": 0.2,
                "quality_weight": 0.5,
            },
            user_preferences={
                "preference_strength": 0.8,
            },
        )
    
    def test_to_vector_correct_size(self):
        """Test that state vector has correct size."""
        vector = self.sample_state.to_vector()
        expected_size = 21  # As defined in DQNRoutingAgent
        self.assertEqual(len(vector), expected_size)
        self.assertIsInstance(vector, np.ndarray)
        self.assertEqual(vector.dtype, np.float32)
    
    def test_to_vector_task_complexity(self):
        """Test that task complexity is correctly encoded."""
        vector = self.sample_state.to_vector()
        self.assertEqual(vector[0], 0.7)  # First element should be task_complexity
    
    def test_to_vector_context_type_encoding(self):
        """Test that context type is correctly one-hot encoded."""
        vector = self.sample_state.to_vector()
        # code_generation should be at index 1
        self.assertEqual(vector[1], 1.0)
        # Other context types should be 0
        self.assertEqual(vector[2], 0.0)  # analysis
        self.assertEqual(vector[3], 0.0)  # debugging
    
    def test_to_vector_provider_availability(self):
        """Test that provider availability is correctly encoded."""
        vector = self.sample_state.to_vector()
        # Provider availability starts at index 11
        providers = ["openai", "anthropic", "google", "groq", "grok"]
        for i, provider in enumerate(providers):
            expected = 1.0 if self.sample_state.provider_availability.get(provider) else 0.0
            self.assertEqual(vector[11 + i], expected)
    
    def test_to_vector_different_context_types(self):
        """Test vector encoding for different context types."""
        context_types = [
            "analysis", "debugging", "documentation", "testing",
            "planning", "research", "creative", "reasoning", "general"
        ]
        
        for i, context_type in enumerate(context_types):
            state = RoutingState(
                task_complexity=0.5,
                context_type=context_type,
                provider_availability={},
                historical_performance={},
                resource_constraints={},
                user_preferences={},
            )
            vector = state.to_vector()
            # Check that the correct context type is encoded as 1.0
            self.assertEqual(vector[2 + i], 1.0)  # analysis starts at index 2


class TestRoutingAction(unittest.TestCase):
    """Test cases for RoutingAction."""
    
    def test_from_action_index_valid_indices(self):
        """Test conversion from valid action indices."""
        # Test first action (OpenAI performance)
        action = RoutingAction.from_action_index(0)
        self.assertEqual(action.provider, ProviderType.OPENAI)
        self.assertEqual(action.model, "chatgpt-4.1")
        self.assertEqual(action.strategy, "performance")
        
        # Test Anthropic balanced action
        action = RoutingAction.from_action_index(4)
        self.assertEqual(action.provider, ProviderType.ANTHROPIC)
        self.assertEqual(action.model, "claude-4.5-sonnet-20250930")
        self.assertEqual(action.strategy, "balanced")
    
    def test_from_action_index_invalid_index(self):
        """Test conversion from invalid action index (should default to first action)."""
        action = RoutingAction.from_action_index(999)
        self.assertEqual(action.provider, ProviderType.OPENAI)
        self.assertEqual(action.model, "chatgpt-4.1")
        self.assertEqual(action.strategy, "performance")
    
    def test_to_action_index_roundtrip(self):
        """Test that action index conversion is consistent."""
        for i in range(12):  # Test all valid action indices
            action = RoutingAction.from_action_index(i)
            converted_index = action.to_action_index()
            self.assertEqual(converted_index, i)
    
    def test_to_action_index_unknown_action(self):
        """Test conversion of unknown action (should default to 0)."""
        action = RoutingAction(
            provider=ProviderType.OPENAI,
            model="unknown-model",
            strategy="unknown-strategy"
        )
        index = action.to_action_index()
        self.assertEqual(index, 0)


class TestDQNRoutingAgent(unittest.TestCase):
    """Test cases for DQNRoutingAgent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = DQNRoutingAgent(
            state_size=21,
            action_size=12,
            learning_rate=0.001,
            memory_size=100,  # Smaller for testing
            batch_size=32,
        )
        
        self.sample_state = RoutingState(
            task_complexity=0.5,
            context_type="code_generation",
            provider_availability={"openai": True, "anthropic": True},
            historical_performance={"openai": 0.8},
            resource_constraints={"cost_weight": 0.33, "time_weight": 0.33, "quality_weight": 0.34},
            user_preferences={"preference_strength": 0.7},
        )
    
    def test_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.state_size, 21)
        self.assertEqual(self.agent.action_size, 12)
        self.assertEqual(self.agent.learning_rate, 0.001)
        self.assertEqual(self.agent.exploration_rate, 1.0)
        self.assertEqual(len(self.agent.memory), 0)
        self.assertIsNone(self.agent.q_network)  # Not initialized yet
        self.assertEqual(self.agent.training_step, 0)
    
    def test_remember(self):
        """Test experience storage in replay buffer."""
        action = RoutingAction(ProviderType.OPENAI, "chatgpt-4.1", "performance")
        next_state = RoutingState(
            task_complexity=0.6,
            context_type="code_generation",
            provider_availability={"openai": True},
            historical_performance={},
            resource_constraints={},
            user_preferences={},
        )
        
        initial_memory_size = len(self.agent.memory)
        self.agent.remember(self.sample_state, action, 1.0, next_state, False)
        
        self.assertEqual(len(self.agent.memory), initial_memory_size + 1)
        
        # Check that experience is stored correctly
        experience = self.agent.memory[-1]
        self.assertEqual(len(experience), 5)  # state, action, reward, next_state, done
        self.assertIsInstance(experience[0], np.ndarray)  # state vector
        self.assertIsInstance(experience[1], int)  # action index
        self.assertEqual(experience[2], 1.0)  # reward
        self.assertIsInstance(experience[3], np.ndarray)  # next state vector
        self.assertFalse(experience[4])  # done flag
    
    def test_act_exploration(self):
        """Test action selection during exploration phase."""
        # With exploration_rate = 1.0, should always explore
        action = self.agent.act(self.sample_state)
        self.assertIsInstance(action, RoutingAction)
        self.assertIn(action.provider, [p for p in ProviderType])
        self.assertIsInstance(action.model, str)
        self.assertIsInstance(action.strategy, str)
    
    def test_act_exploitation_without_network(self):
        """Test action selection during exploitation phase without neural network."""
        # Set exploration rate to 0 to force exploitation
        self.agent.exploration_rate = 0.0
        
        action = self.agent.act(self.sample_state)
        # Should still return a valid action even without network (fallback to random)
        self.assertIsInstance(action, RoutingAction)
    
    def test_calculate_reward_successful_routing(self):
        """Test reward calculation for successful routing."""
        action = RoutingAction(ProviderType.ANTHROPIC, "claude-sonnet-4-5-20250929", "balanced")
        routing_result = {"success": True}
        execution_metrics = {
            "response_time": 2.0,
            "quality_score": 0.8,
            "cost_efficiency": 0.7,
        }
        
        reward = self.agent.calculate_reward(action, routing_result, execution_metrics)
        self.assertGreater(reward, 0.0)  # Should be positive for successful routing
    
    def test_calculate_reward_failed_routing(self):
        """Test reward calculation for failed routing."""
        action = RoutingAction(ProviderType.OPENAI, "chatgpt-4.1", "performance")
        routing_result = {"success": False}
        execution_metrics = {
            "response_time": 15.0,  # Slow response
            "quality_score": 0.3,   # Low quality
            "cost_efficiency": 0.2, # Poor cost efficiency
        }
        
        reward = self.agent.calculate_reward(action, routing_result, execution_metrics)
        self.assertLess(reward, 0.0)  # Should be negative for failed routing
    
    def test_calculate_reward_performance_bonuses(self):
        """Test that performance bonuses are applied correctly."""
        action = RoutingAction(ProviderType.ANTHROPIC, "claude-3-7-sonnet-20250219", "performance")
        routing_result = {"success": True}
        execution_metrics = {
            "response_time": 0.5,   # Fast response (should get bonus)
            "quality_score": 0.9,   # High quality (should get bonus)
            "cost_efficiency": 0.8,
        }
        
        reward = self.agent.calculate_reward(action, routing_result, execution_metrics)
        
        # Calculate expected bonuses
        expected_base = 1.0  # Success
        expected_speed_bonus = 0.3  # Fast response
        expected_quality_bonus = (0.9 - 0.5) * 0.5  # Quality above average
        expected_strategy_bonus = 0.2  # Performance strategy with high quality
        
        expected_min = expected_base + expected_speed_bonus + expected_quality_bonus + expected_strategy_bonus
        self.assertGreaterEqual(reward, expected_min)
    
    def test_replay_insufficient_memory(self):
        """Test replay when there's insufficient memory."""
        # With empty memory, replay should return None
        loss = self.agent.replay()
        self.assertIsNone(loss)
        
        # Add some experiences but not enough for batch_size
        action = RoutingAction(ProviderType.OPENAI, "chatgpt-4.1", "performance")
        for _ in range(self.agent.batch_size - 1):
            self.agent.remember(self.sample_state, action, 0.5, self.sample_state, False)
        
        loss = self.agent.replay()
        self.assertIsNone(loss)
    
    def test_replay_without_network(self):
        """Test replay when neural network is not initialized."""
        # Fill memory with enough experiences
        action = RoutingAction(ProviderType.OPENAI, "chatgpt-4.1", "performance")
        for _ in range(self.agent.batch_size):
            self.agent.remember(self.sample_state, action, 0.5, self.sample_state, False)
        
        # Replay should return None when network is not initialized
        loss = self.agent.replay()
        self.assertIsNone(loss)
    
    def test_update_routing_performance(self):
        """Test updating routing performance tracking."""
        action = RoutingAction(ProviderType.ANTHROPIC, "claude-sonnet-4-5-20250929", "balanced")
        provider_key = f"{action.provider}:{action.model}"
        
        # First update
        self.agent.update_routing_performance(action, 0.8)
        self.assertEqual(self.agent.routing_performance[provider_key], 0.8)
        
        # Second update (should be weighted average)
        self.agent.update_routing_performance(action, 0.6)
        expected = 0.8 * 0.8 + 0.2 * 0.6  # 0.8 * old + 0.2 * new
        self.assertAlmostEqual(self.agent.routing_performance[provider_key], expected, places=3)
    
    def test_get_performance_metrics(self):
        """Test getting performance metrics."""
        metrics = self.agent.get_performance_metrics()
        
        required_keys = [
            "exploration_rate", "training_steps", "memory_utilization",
            "routing_performance", "recent_training_loss",
            "action_space_size", "state_space_size"
        ]
        
        for key in required_keys:
            self.assertIn(key, metrics)
        
        self.assertEqual(metrics["action_space_size"], 12)
        self.assertEqual(metrics["state_space_size"], 21)
        self.assertEqual(metrics["training_steps"], 0)
        self.assertIsInstance(metrics["memory_utilization"], float)
    
    def test_save_and_load_model(self):
        """Test saving and loading model configuration."""
        # Update some agent state
        self.agent.exploration_rate = 0.5
        self.agent.training_step = 100
        self.agent.routing_performance = {"openai:chatgpt-4.1": 0.8}
        self.agent.training_history = [{"step": 1, "loss": 0.5}]
        
        with tempfile.NamedTemporaryFile(delete=False, suffix="") as tmp:
            filepath = tmp.name
        
        try:
            # Save model (should succeed even without neural network)
            self.agent.save_model(filepath)
            
            # Create new agent and load
            new_agent = DQNRoutingAgent()
            success = new_agent.load_model(filepath)
            
            self.assertTrue(success)
            self.assertEqual(new_agent.exploration_rate, 0.5)
            self.assertEqual(new_agent.training_step, 100)
            self.assertEqual(new_agent.routing_performance, {"openai:chatgpt-4.1": 0.8})
            self.assertEqual(len(new_agent.training_history), 1)
            
        finally:
            # Clean up temp files
            import os
            try:
                os.unlink(f"{filepath}_config.json")
            except FileNotFoundError:
                pass
    
    def test_memory_buffer_max_size(self):
        """Test that memory buffer respects max size."""
        action = RoutingAction(ProviderType.OPENAI, "chatgpt-4.1", "performance")
        
        # Fill memory beyond max size
        for i in range(self.agent.memory.maxlen + 10):
            self.agent.remember(self.sample_state, action, float(i), self.sample_state, False)
        
        # Memory should not exceed max size
        self.assertEqual(len(self.agent.memory), self.agent.memory.maxlen)
        
        # Should contain only the most recent experiences
        latest_experience = self.agent.memory[-1]
        self.assertEqual(latest_experience[2], float(self.agent.memory.maxlen + 10 - 1))  # Latest reward


class TestDQNAgentIntegration(unittest.TestCase):
    """Integration tests for DQN agent."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.agent = DQNRoutingAgent(memory_size=50, batch_size=16)
        
        self.sample_state = RoutingState(
            task_complexity=0.5,
            context_type="code_generation",
            provider_availability={"openai": True, "anthropic": True},
            historical_performance={"openai": 0.8},
            resource_constraints={"cost_weight": 0.33, "time_weight": 0.33, "quality_weight": 0.34},
            user_preferences={"preference_strength": 0.7},
        )
    
    def test_complete_training_episode(self):
        """Test a complete training episode without neural network."""
        states = []
        actions = []
        rewards = []
        
        # Simulate a routing episode
        for step in range(10):
            state = RoutingState(
                task_complexity=0.5 + step * 0.05,
                context_type="code_generation",
                provider_availability={"openai": True, "anthropic": True},
                historical_performance={},
                resource_constraints={},
                user_preferences={},
            )
            
            action = self.agent.act(state)
            
            # Simulate reward calculation
            routing_result = {"success": step % 3 != 0}  # Some successes, some failures
            execution_metrics = {
                "response_time": 1.0 + step * 0.2,
                "quality_score": 0.5 + step * 0.03,
                "cost_efficiency": 0.6,
            }
            
            reward = self.agent.calculate_reward(action, routing_result, execution_metrics)
            
            states.append(state)
            actions.append(action)
            rewards.append(reward)
            
            # Store experience
            if step > 0:
                self.agent.remember(
                    states[step-1], actions[step-1], rewards[step-1],
                    state, step == 9  # Last step is done
                )
            
            # Update performance tracking
            performance_score = 1.0 if routing_result["success"] else 0.0
            self.agent.update_routing_performance(action, performance_score)
        
        # Check that experiences were stored
        self.assertEqual(len(self.agent.memory), 9)  # 10 steps - 1 (no experience for first step)
        
        # Check that performance tracking was updated
        self.assertGreater(len(self.agent.routing_performance), 0)
        
        # Try replay (should handle gracefully without neural network)
        loss = self.agent.replay()
        # Should return None since we don't have neural network yet
        self.assertIsNone(loss)
    
    def test_exploration_decay(self):
        """Test that exploration rate decays over time during training."""
        initial_exploration = self.agent.exploration_rate
        
        # Fill memory and trigger multiple replay calls
        action = RoutingAction(ProviderType.OPENAI, "chatgpt-4.1", "performance")
        for i in range(50):
            self.agent.remember(self.sample_state, action, 0.5, self.sample_state, False)
        
        # Mock neural networks to enable replay
        self.agent.q_network = Mock()
        self.agent.target_q_network = Mock()
        self.agent.q_network.predict.return_value = np.array([[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]])
        self.agent.target_q_network.predict.return_value = np.array([[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]])
        self.agent.q_network.train.return_value = 0.1
        self.agent.q_network.get_weights.return_value = "mock_weights"
        
        # Perform multiple replay steps
        for _ in range(10):
            self.agent.replay()
        
        # Exploration rate should have decayed
        self.assertLess(self.agent.exploration_rate, initial_exploration)
        self.assertGreaterEqual(self.agent.exploration_rate, self.agent.exploration_min)


if __name__ == "__main__":
    unittest.main()
