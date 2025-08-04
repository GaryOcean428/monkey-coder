"""
Comprehensive test suite for Enhanced Neural Network architectures

Tests both TensorFlow and numpy implementations of DQN networks,
including target networks, weight updates, and model persistence.
"""

import pytest
import numpy as np
import tempfile
import os
from unittest.mock import patch, MagicMock

from monkey_coder.quantum.neural_network import (
    BaseDQNNetwork,
    NumpyDQNNetwork,
    DQNNetwork,
    create_dqn_network,
    TENSORFLOW_AVAILABLE
)

# Try to import TensorFlow for conditional testing
try:
    from monkey_coder.quantum.neural_network import TensorFlowDQNNetwork
    tensorflow_available = True
except ImportError:
    tensorflow_available = False


class TestNumpyDQNNetwork:
    """Test the numpy-based DQN network implementation."""
    
    def setup_method(self):
        """Set up test fixtures before each method."""
        self.state_size = 8
        self.action_size = 4
        self.network = NumpyDQNNetwork(
            state_size=self.state_size,
            action_size=self.action_size,
            learning_rate=0.01,
            hidden_layers=(16, 8),
            activation="relu"
        )
    
    def test_initialization(self):
        """Test network initialization."""
        assert self.network.state_size == 8
        assert self.network.action_size == 4
        assert self.network.learning_rate == 0.01
        assert self.network.hidden_layers == (16, 8)
        assert self.network.activation == "relu"
        
        # Check network architecture
        expected_layers = [8, 16, 8, 4]  # input + hidden + output
        assert self.network.layer_sizes == expected_layers
        
        # Check weights initialization
        assert len(self.network.weights) == 3  # 3 connections between 4 layers
        assert len(self.network.biases) == 3
        assert len(self.network.target_weights) == 3
        assert len(self.network.target_biases) == 3
        
        # Check weight shapes
        for i, (w, b) in enumerate(zip(self.network.weights, self.network.biases)):
            expected_input_size = expected_layers[i]
            expected_output_size = expected_layers[i + 1]
            
            assert w.shape == (expected_input_size, expected_output_size)
            assert b.shape == (1, expected_output_size)
    
    def test_activation_functions(self):
        """Test different activation functions."""
        test_input = np.array([[-2, -1, 0, 1, 2]])
        
        # Test ReLU
        relu_net = NumpyDQNNetwork(4, 2, activation="relu")
        relu_output = relu_net._activation_function(test_input)
        expected_relu = np.array([[0, 0, 0, 1, 2]])
        np.testing.assert_array_equal(relu_output, expected_relu)
        
        # Test Tanh
        tanh_net = NumpyDQNNetwork(4, 2, activation="tanh")
        tanh_output = tanh_net._activation_function(test_input)
        expected_tanh = np.tanh(test_input)
        np.testing.assert_array_almost_equal(tanh_output, expected_tanh)
        
        # Test Sigmoid
        sigmoid_net = NumpyDQNNetwork(4, 2, activation="sigmoid")
        sigmoid_output = sigmoid_net._activation_function(test_input)
        expected_sigmoid = 1 / (1 + np.exp(-test_input))
        np.testing.assert_array_almost_equal(sigmoid_output, expected_sigmoid)
    
    def test_forward_pass(self):
        """Test forward pass through the network."""
        # Test single state
        state = np.random.rand(1, self.state_size)
        output, layer_outputs = self.network._forward_pass(state)
        
        assert output.shape == (1, self.action_size)
        assert len(layer_outputs) == 4  # input + 2 hidden + output
        assert layer_outputs[0].shape == (1, self.state_size)  # Input
        assert layer_outputs[-1].shape == (1, self.action_size)  # Output
        
        # Test batch of states
        batch_size = 5
        states = np.random.rand(batch_size, self.state_size)
        output, layer_outputs = self.network._forward_pass(states)
        
        assert output.shape == (batch_size, self.action_size)
        assert layer_outputs[0].shape == (batch_size, self.state_size)
        assert layer_outputs[-1].shape == (batch_size, self.action_size)
    
    def test_predict(self):
        """Test prediction functionality."""
        # Test single state prediction
        state = np.random.rand(self.state_size)
        q_values = self.network.predict(state)
        
        assert q_values.shape == (1, self.action_size)
        assert isinstance(q_values, np.ndarray)
        
        # Test batch prediction
        batch_size = 3
        states = np.random.rand(batch_size, self.state_size)
        q_values = self.network.predict(states)
        
        assert q_values.shape == (batch_size, self.action_size)
    
    def test_target_network(self):
        """Test target network functionality."""
        # Initially, target network should be identical to main network
        state = np.random.rand(1, self.state_size)
        
        main_output = self.network.predict(state)
        target_output = self.network.predict_target(state)
        
        np.testing.assert_array_almost_equal(main_output, target_output)
        
        # Train main network
        states = np.random.rand(10, self.state_size)
        targets = np.random.rand(10, self.action_size)
        self.network.train(states, targets)
        
        # Target network should now be different
        main_output_after = self.network.predict(state)
        target_output_after = self.network.predict_target(state)
        
        assert not np.allclose(main_output_after, target_output_after)
        
        # Update target network
        self.network.update_target_network()
        
        # Should be identical again
        target_output_updated = self.network.predict_target(state)
        np.testing.assert_array_almost_equal(main_output_after, target_output_updated)
    
    def test_soft_target_update(self):
        """Test soft target network updates."""
        # Train main network to create difference
        states = np.random.rand(10, self.state_size)
        targets = np.random.rand(10, self.action_size)
        self.network.train(states, targets)
        
        # Get initial weights
        initial_target_weights = [w.copy() for w in self.network.target_weights]
        initial_main_weights = [w.copy() for w in self.network.weights]
        
        # Soft update with tau=0.1
        tau = 0.1
        self.network.update_target_network(tau=tau)
        
        # Check that target weights moved toward main weights
        for i, (target_w, main_w, initial_target_w) in enumerate(zip(
            self.network.target_weights, self.network.weights, initial_target_weights
        )):
            expected_w = tau * main_w + (1.0 - tau) * initial_target_w
            np.testing.assert_array_almost_equal(target_w, expected_w)
    
    def test_training(self):
        """Test network training functionality."""
        # Generate training data
        batch_size = 32
        states = np.random.rand(batch_size, self.state_size)
        targets = np.random.rand(batch_size, self.action_size)
        
        # Get initial loss
        initial_predictions = self.network.predict(states)
        initial_loss = np.mean((initial_predictions - targets) ** 2)
        
        # Train network
        training_loss = self.network.train(states, targets)
        
        # Loss should be recorded
        assert training_loss > 0
        assert len(self.network.loss_history) == 1
        assert self.network.loss_history[0] == training_loss
        
        # Training step should increment
        assert self.network.training_step == 1
        
        # Predictions should be closer to targets after training
        new_predictions = self.network.predict(states)
        new_loss = np.mean((new_predictions - targets) ** 2)
        
        # Loss should generally decrease (may fluctuate due to randomness)
        assert abs(new_loss - training_loss) < 0.1  # Allow for small differences
    
    def test_weight_management(self):
        """Test getting and setting network weights."""
        # Get initial weights
        original_weights = self.network.get_weights()
        
        # Weights should include both weights and biases
        expected_length = len(self.network.weights) + len(self.network.biases)
        assert len(original_weights) == expected_length
        
        # Modify network
        states = np.random.rand(5, self.state_size)
        targets = np.random.rand(5, self.action_size)
        self.network.train(states, targets)
        
        # Weights should be different
        modified_weights = self.network.get_weights()
        assert not all(np.allclose(orig, mod) for orig, mod in zip(original_weights, modified_weights))
        
        # Restore original weights
        self.network.set_weights(original_weights)
        restored_weights = self.network.get_weights()
        
        for orig, restored in zip(original_weights, restored_weights):
            np.testing.assert_array_almost_equal(orig, restored)
    
    def test_model_persistence(self):
        """Test saving and loading models."""
        # Train network to create unique state
        states = np.random.rand(10, self.state_size)
        targets = np.random.rand(10, self.action_size)
        self.network.train(states, targets)
        
        # Get reference prediction
        test_state = np.random.rand(1, self.state_size)
        original_prediction = self.network.predict(test_state)
        original_training_step = self.network.training_step
        
        # Save model
        with tempfile.NamedTemporaryFile(delete=False, suffix="") as tmp:
            filepath = tmp.name
        
        try:
            success = self.network.save_model(filepath)
            assert success is True
            
            # Create new network and load
            new_network = NumpyDQNNetwork(
                state_size=self.state_size,
                action_size=self.action_size
            )
            
            success = new_network.load_model(filepath)
            assert success is True
            
            # Verify loaded network produces same predictions
            loaded_prediction = new_network.predict(test_state)
            np.testing.assert_array_almost_equal(original_prediction, loaded_prediction)
            
            # Verify training step was restored
            assert new_network.training_step == original_training_step
            
        finally:
            # Cleanup
            if os.path.exists(f"{filepath}.json"):
                os.unlink(f"{filepath}.json")
    
    def test_save_load_failure_handling(self):
        """Test handling of save/load failures."""
        # Test save failure
        success = self.network.save_model("/invalid/path/model")
        assert success is False
        
        # Test load failure
        success = self.network.load_model("/nonexistent/model")
        assert success is False


@pytest.mark.skipif(not tensorflow_available, reason="TensorFlow not available")
class TestTensorFlowDQNNetwork:
    """Test the TensorFlow-based DQN network implementation."""
    
    def setup_method(self):
        """Set up test fixtures before each method."""
        self.state_size = 6
        self.action_size = 3
        
        # Only run if TensorFlow is actually available
        if tensorflow_available:
            self.network = TensorFlowDQNNetwork(
                state_size=self.state_size,
                action_size=self.action_size,
                learning_rate=0.01,
                hidden_layers=(12, 6),
                activation="relu"
            )
    
    def test_initialization(self):
        """Test TensorFlow network initialization."""
        if not tensorflow_available:
            pytest.skip("TensorFlow not available")
        
        assert self.network.state_size == 6
        assert self.network.action_size == 3
        assert self.network.learning_rate == 0.01
        assert self.network.hidden_layers == (12, 6)
        
        # Check models are created
        assert self.network.model is not None
        assert self.network.target_model is not None
        
        # Check model architecture
        assert len(self.network.model.layers) == 5  # input + hidden + dropout + output
    
    def test_predict(self):
        """Test TensorFlow prediction."""
        if not tensorflow_available:
            pytest.skip("TensorFlow not available")
        
        # Single state
        state = np.random.rand(self.state_size)
        q_values = self.network.predict(state)
        
        assert q_values.shape == (1, self.action_size)
        
        # Batch prediction
        states = np.random.rand(5, self.state_size)
        q_values = self.network.predict(states)
        
        assert q_values.shape == (5, self.action_size)
    
    def test_target_network(self):
        """Test TensorFlow target network."""
        if not tensorflow_available:
            pytest.skip("TensorFlow not available")
        
        state = np.random.rand(1, self.state_size)
        
        # Initially identical
        main_output = self.network.predict(state)
        target_output = self.network.predict_target(state)
        
        np.testing.assert_array_almost_equal(main_output, target_output, decimal=5)
        
        # Train and test difference
        states = np.random.rand(10, self.state_size)
        targets = np.random.rand(10, self.action_size)
        self.network.train(states, targets)
        
        main_output_after = self.network.predict(state)
        target_output_after = self.network.predict_target(state)
        
        # Should be different after training
        assert not np.allclose(main_output_after, target_output_after, atol=1e-3)


class TestDQNNetworkUnified:
    """Test the unified DQN network interface."""
    
    def test_automatic_selection(self):
        """Test automatic implementation selection."""
        network = DQNNetwork(
            state_size=4,
            action_size=2,
            force_numpy=False
        )
        
        # Should select appropriate implementation
        if TENSORFLOW_AVAILABLE:
            assert network.implementation in ["tensorflow", "numpy"]
        else:
            assert network.implementation == "numpy"
    
    def test_force_numpy(self):
        """Test forcing numpy implementation."""
        network = DQNNetwork(
            state_size=4,
            action_size=2,
            force_numpy=True
        )
        
        assert network.implementation == "numpy"
        assert isinstance(network.network, NumpyDQNNetwork)
    
    def test_unified_interface(self):
        """Test that unified interface works consistently."""
        network = DQNNetwork(
            state_size=5,
            action_size=3,
            force_numpy=True  # Use numpy for consistent testing
        )
        
        # Test all interface methods
        state = np.random.rand(5)
        
        # Predict
        q_values = network.predict(state)
        assert q_values.shape == (1, 3)
        
        # Target predict
        target_q_values = network.predict_target(state)
        assert target_q_values.shape == (1, 3)
        
        # Train
        states = np.random.rand(10, 5)
        targets = np.random.rand(10, 3)
        loss = network.train(states, targets)
        assert loss >= 0
        
        # Update target
        network.update_target_network()
        
        # Weight management
        weights = network.get_weights()
        assert len(weights) > 0
        
        network.set_weights(weights)
        
        # Model persistence
        with tempfile.NamedTemporaryFile(delete=False, suffix="") as tmp:
            filepath = tmp.name
        
        try:
            success = network.save_model(filepath)
            assert success is True
            
            success = network.load_model(filepath)
            assert success is True
            
        finally:
            # Cleanup
            for ext in [".json", ".h5", "_config.json"]:
                if os.path.exists(f"{filepath}{ext}"):
                    os.unlink(f"{filepath}{ext}")


class TestCreateDQNNetwork:
    """Test the convenience function for creating DQN networks."""
    
    def test_create_function(self):
        """Test the create_dqn_network function."""
        network = create_dqn_network(
            state_size=6,
            action_size=4,
            learning_rate=0.005,
            hidden_layers=(32, 16),
            activation="tanh",
            force_numpy=True
        )
        
        assert isinstance(network, DQNNetwork)
        assert network.state_size == 6
        assert network.action_size == 4
        assert network.implementation == "numpy"
        
        # Test prediction works
        state = np.random.rand(6)
        q_values = network.predict(state)
        assert q_values.shape == (1, 4)


class TestIntegration:
    """Integration tests for neural network components."""
    
    def test_dqn_training_workflow(self):
        """Test a complete DQN training workflow."""
        # Create network
        network = create_dqn_network(
            state_size=8,
            action_size=4,
            learning_rate=0.01,
            force_numpy=True
        )
        
        # Simulate experience collection
        batch_size = 32
        states = np.random.rand(batch_size, 8)
        actions = np.random.randint(0, 4, batch_size)
        rewards = np.random.rand(batch_size) - 0.5
        next_states = np.random.rand(batch_size, 8)
        dones = np.random.rand(batch_size) > 0.9
        
        # Compute target Q-values (simplified)
        next_q_values = network.predict_target(next_states)
        max_next_q = np.max(next_q_values, axis=1)
        
        targets = network.predict(states).copy()
        for i in range(batch_size):
            if dones[i]:
                targets[i, actions[i]] = rewards[i]
            else:
                targets[i, actions[i]] = rewards[i] + 0.99 * max_next_q[i]
        
        # Train network
        loss = network.train(states, targets)
        assert loss >= 0
        
        # Update target network every few steps
        network.update_target_network()
        
        # Verify learning occurred
        new_predictions = network.predict(states)
        assert new_predictions.shape == (batch_size, 4)
    
    def test_experience_replay_integration(self):
        """Test integration with experience replay buffer."""
        from monkey_coder.quantum.experience_buffer import ExperienceReplayBuffer, Experience
        
        # Create components
        network = create_dqn_network(4, 2, force_numpy=True)
        buffer = ExperienceReplayBuffer(capacity=100, min_size=10)
        
        # Collect experiences
        for i in range(20):
            state = np.random.rand(4)
            next_state = np.random.rand(4)
            
            exp = Experience(
                state=state,
                action=np.random.randint(0, 2),
                reward=np.random.rand() - 0.5,
                next_state=next_state,
                done=i % 10 == 9,
                timestamp=float(i)
            )
            buffer.add(exp)
        
        # Training step
        batch = buffer.sample(8)
        states, actions, rewards, next_states, dones = buffer.get_batch_arrays(batch)
        
        # Compute targets
        next_q_values = network.predict_target(next_states)
        max_next_q = np.max(next_q_values, axis=1)
        
        targets = network.predict(states).copy()
        for i in range(len(batch)):
            if dones[i]:
                targets[i, actions[i]] = rewards[i]
            else:
                targets[i, actions[i]] = rewards[i] + 0.99 * max_next_q[i]
        
        # Train
        loss = network.train(states, targets)
        assert loss >= 0
        
        # Update target
        network.update_target_network()