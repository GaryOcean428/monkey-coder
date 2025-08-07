"""
Tests for Neural Network Architecture implementation.

This module tests the Q-network and target Q-network creation, training, and management
functionality required for DQN-based quantum routing.
"""

import pytest
import numpy as np
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

from monkey_coder.quantum.neural_networks import (
    QNetworkArchitecture,
    DQNNetworkManager,
    create_dqn_networks,
    _ensure_tensorflow
)


class TestTensorFlowImport:
    """Test TensorFlow import and lazy loading."""
    
    def test_ensure_tensorflow_success(self):
        """Test successful TensorFlow import."""
        # This test will pass if TensorFlow is available
        try:
            _ensure_tensorflow()
            assert True  # If no exception, import was successful
        except ImportError:
            pytest.skip("TensorFlow not available in test environment")
    
    def test_ensure_tensorflow_failure(self):
        """Test handling of TensorFlow import failure."""
        with patch('builtins.__import__', side_effect=ImportError("No module named tensorflow")):
            with pytest.raises(ImportError, match="TensorFlow is required"):
                _ensure_tensorflow()


class TestQNetworkArchitecture:
    """Test cases for Q-Network architecture factory."""
    
    @pytest.fixture
    def mock_tensorflow(self):
        """Mock TensorFlow components for testing."""
        with patch('monkey_coder.quantum.neural_networks.tf') as mock_tf, \
             patch('monkey_coder.quantum.neural_networks.Sequential') as mock_sequential, \
             patch('monkey_coder.quantum.neural_networks.Dense') as mock_dense, \
             patch('monkey_coder.quantum.neural_networks.Dropout') as mock_dropout, \
             patch('monkey_coder.quantum.neural_networks.BatchNormalization') as mock_bn, \
             patch('monkey_coder.quantum.neural_networks.Adam') as mock_adam, \
             patch('monkey_coder.quantum.neural_networks.Huber') as mock_huber:
            
            # Configure mock model
            mock_model = Mock()
            mock_model.count_params.return_value = 1000
            mock_sequential.return_value = mock_model
            
            # Configure mock optimizer and loss
            mock_adam.return_value = Mock()
            mock_huber.return_value = Mock()
            
            yield {
                'tf': mock_tf,
                'Sequential': mock_sequential,
                'Dense': mock_dense,
                'Dropout': mock_dropout,
                'BatchNormalization': mock_bn,
                'Adam': mock_adam,
                'Huber': mock_huber,
                'model': mock_model
            }
    
    def test_create_standard_dqn(self, mock_tensorflow):
        """Test creation of standard DQN architecture."""
        with patch('monkey_coder.quantum.neural_networks._ensure_tensorflow'):
            model = QNetworkArchitecture.create_standard_dqn(
                state_size=21,
                action_size=12,
                learning_rate=0.001,
                hidden_layers=(128, 64),
                dropout_rate=0.1,
                use_batch_norm=True
            )
            
            # Verify model was created and configured
            mock_tensorflow['Sequential'].assert_called_once_with(name="standard_dqn")
            assert mock_tensorflow['model'].add.call_count >= 3  # Input, hidden, output layers
            mock_tensorflow['model'].compile.assert_called_once()
    
    def test_create_deep_dqn(self, mock_tensorflow):
        """Test creation of deep DQN architecture."""
        with patch('monkey_coder.quantum.neural_networks._ensure_tensorflow'):
            model = QNetworkArchitecture.create_deep_dqn(
                state_size=21,
                action_size=12,
                learning_rate=0.0005,
                hidden_layers=(256, 128, 64, 32),
                dropout_rate=0.2,
                use_batch_norm=True
            )
            
            # Verify deep model was created
            mock_tensorflow['Sequential'].assert_called_once_with(name="deep_dqn")
            assert mock_tensorflow['model'].add.call_count >= 5  # More layers for deep network
            mock_tensorflow['model'].compile.assert_called_once()
    
    def test_create_lightweight_dqn(self, mock_tensorflow):
        """Test creation of lightweight DQN architecture."""
        with patch('monkey_coder.quantum.neural_networks._ensure_tensorflow'):
            model = QNetworkArchitecture.create_lightweight_dqn(
                state_size=21,
                action_size=12,
                learning_rate=0.002,
                hidden_layers=(64, 32),
                dropout_rate=0.05
            )
            
            # Verify lightweight model was created
            mock_tensorflow['Sequential'].assert_called_once_with(name="lightweight_dqn")
            assert mock_tensorflow['model'].add.call_count >= 3  # Fewer layers
            mock_tensorflow['model'].compile.assert_called_once()
    
    def test_standard_dqn_without_batch_norm(self, mock_tensorflow):
        """Test standard DQN creation without batch normalization."""
        with patch('monkey_coder.quantum.neural_networks._ensure_tensorflow'):
            model = QNetworkArchitecture.create_standard_dqn(
                state_size=21,
                action_size=12,
                use_batch_norm=False
            )
            
            # BatchNormalization should not be added
            mock_tensorflow['BatchNormalization'].assert_not_called()
    
    def test_standard_dqn_without_dropout(self, mock_tensorflow):
        """Test standard DQN creation without dropout."""
        with patch('monkey_coder.quantum.neural_networks._ensure_tensorflow'):
            model = QNetworkArchitecture.create_standard_dqn(
                state_size=21,
                action_size=12,
                dropout_rate=0.0
            )
            
            # Dropout layers should not be added when rate is 0
            mock_tensorflow['Dropout'].assert_not_called()


class TestDQNNetworkManager:
    """Test cases for DQN Network Manager."""
    
    @pytest.fixture
    def mock_networks(self):
        """Mock Q-network and target network."""
        q_network = Mock()
        target_network = Mock()
        
        # Configure network methods
        q_network.count_params.return_value = 1000
        q_network.predict.return_value = np.array([[0.1, 0.2, 0.3, 0.4]])
        q_network.get_weights.return_value = [np.array([1, 2, 3])]
        q_network.trainable_weights = [Mock()]
        q_network.layers = [Mock(), Mock(), Mock()]
        q_network.optimizer = Mock()
        q_network.optimizer.__class__.__name__ = "Adam"
        q_network.loss = Mock()
        q_network.loss.name = "huber"
        
        target_network.predict.return_value = np.array([[0.15, 0.25, 0.35, 0.45]])
        target_network.get_weights.return_value = [np.array([1, 2, 3])]
        target_network.set_weights = Mock()
        
        return q_network, target_network
    
    @pytest.fixture
    def network_manager(self):
        """Create network manager for testing."""
        return DQNNetworkManager(
            state_size=21,
            action_size=12,
            architecture="standard",
            learning_rate=0.001
        )
    
    def test_network_manager_initialization(self, network_manager):
        """Test network manager initialization."""
        assert network_manager.state_size == 21
        assert network_manager.action_size == 12
        assert network_manager.architecture == "standard"
        assert network_manager.learning_rate == 0.001
        assert network_manager.q_network is None
        assert network_manager.target_q_network is None
    
    def test_create_networks_standard(self, network_manager, mock_networks):
        """Test creation of standard architecture networks."""
        q_network, target_network = mock_networks
        
        with patch('monkey_coder.quantum.neural_networks._ensure_tensorflow'), \
             patch.object(QNetworkArchitecture, 'create_standard_dqn') as mock_create, \
             patch.object(network_manager, 'update_target_network') as mock_update:
            mock_create.side_effect = [q_network, target_network]  # Return different networks
            
            result = network_manager.create_networks()
            
            # Verify networks were created
            assert mock_create.call_count == 2  # Called for both networks
            assert result == (q_network, target_network)  # Returns tuple
            assert network_manager.q_network == q_network
            assert network_manager.target_q_network == target_network
            mock_update.assert_called_once()  # Target network should be updated
    
    def test_create_networks_unknown_architecture(self, mock_networks):
        """Test handling of unknown architecture."""
        q_network, target_network = mock_networks
        manager = DQNNetworkManager(
            state_size=21,
            action_size=12,
            architecture="unknown",
            learning_rate=0.001
        )
        
        with patch('monkey_coder.quantum.neural_networks._ensure_tensorflow'), \
             patch.object(QNetworkArchitecture, 'create_standard_dqn') as mock_create, \
             patch.object(manager, 'update_target_network') as mock_update:
            mock_create.side_effect = [q_network, target_network]
            
            manager.create_networks()
            
            # Should fallback to standard architecture
            assert manager.architecture == "standard"
            assert mock_create.call_count == 2
    
    def test_update_target_network(self, network_manager, mock_networks):
        """Test target network weight update."""
        q_network, target_network = mock_networks
        network_manager.q_network = q_network
        network_manager.target_q_network = target_network
        
        network_manager.update_target_network()
        
        # Verify weights were copied
        q_network.get_weights.assert_called_once()
        # Use ANY matcher to avoid numpy array comparison issues in mock
        from unittest.mock import ANY
        target_network.set_weights.assert_called_once_with(ANY)
    
    def test_update_target_network_not_initialized(self, network_manager):
        """Test target network update when networks not initialized."""
        network_manager.update_target_network()
        
        # Should handle gracefully when networks are None
        assert network_manager.q_network is None
        assert network_manager.target_q_network is None
    
    def test_soft_update_target_network(self, network_manager, mock_networks):
        """Test soft update of target network."""
        q_network, target_network = mock_networks
        network_manager.q_network = q_network
        network_manager.target_q_network = target_network
        
        # Configure weights for soft update
        q_weights = [np.array([1.0, 2.0, 3.0])]
        target_weights = [np.array([0.5, 1.0, 1.5])]
        
        q_network.get_weights.return_value = q_weights
        target_network.get_weights.return_value = target_weights
        
        network_manager.soft_update_target_network(tau=0.1)
        
        # Verify soft update was applied
        q_network.get_weights.assert_called_once()
        target_network.get_weights.assert_called_once()
        target_network.set_weights.assert_called_once()
        
        # Check that the call was made with updated weights
        call_args = target_network.set_weights.call_args[0][0]
        assert len(call_args) == 1  # One weight array
    
    def test_predict_q_values(self, network_manager, mock_networks):
        """Test Q-value prediction."""
        q_network, _ = mock_networks
        network_manager.q_network = q_network
        
        state = np.array([1, 2, 3, 4])
        result = network_manager.predict_q_values(state)
        
        # Verify prediction was called with reshaped state
        q_network.predict.assert_called_once()
        call_args = q_network.predict.call_args[0][0]
        assert call_args.shape == (1, 4)  # Should be reshaped to batch
        
        # Verify result
        assert np.array_equal(result, np.array([[0.1, 0.2, 0.3, 0.4]]))
    
    def test_predict_q_values_batch(self, network_manager, mock_networks):
        """Test Q-value prediction with batch input."""
        q_network, _ = mock_networks
        network_manager.q_network = q_network
        
        state_batch = np.array([[1, 2, 3, 4], [5, 6, 7, 8]])
        result = network_manager.predict_q_values(state_batch)
        
        # Should not reshape if already batch
        q_network.predict.assert_called_once()
        call_args = q_network.predict.call_args[0][0]
        assert call_args.shape == (2, 4)
    
    def test_predict_q_values_not_initialized(self, network_manager):
        """Test Q-value prediction when network not initialized."""
        state = np.array([1, 2, 3, 4])
        
        with pytest.raises(RuntimeError, match="Q-network not initialized"):
            network_manager.predict_q_values(state)
    
    def test_predict_target_q_values(self, network_manager, mock_networks):
        """Test target Q-value prediction."""
        _, target_network = mock_networks
        network_manager.target_q_network = target_network
        
        state = np.array([1, 2, 3, 4])
        result = network_manager.predict_target_q_values(state)
        
        # Verify prediction was called
        target_network.predict.assert_called_once()
        assert np.array_equal(result, np.array([[0.15, 0.25, 0.35, 0.45]]))
    
    def test_predict_target_q_values_not_initialized(self, network_manager):
        """Test target Q-value prediction when network not initialized."""
        state = np.array([1, 2, 3, 4])
        
        with pytest.raises(RuntimeError, match="Target Q-network not initialized"):
            network_manager.predict_target_q_values(state)
    
    def test_get_network_info(self, network_manager, mock_networks):
        """Test network information retrieval."""
        q_network, target_network = mock_networks
        
        # Test without networks initialized
        info = network_manager.get_network_info()
        assert info["networks_initialized"] is False
        assert info["architecture"] == "standard"
        assert info["state_size"] == 21
        assert info["action_size"] == 12
        
        # Test with networks initialized
        network_manager.q_network = q_network
        network_manager.target_q_network = target_network
        
        with patch('monkey_coder.quantum.neural_networks.tf') as mock_tf:
            mock_tf.size.return_value.numpy.return_value = 100
            
            info = network_manager.get_network_info()
            assert info["networks_initialized"] is True
            assert info["total_parameters"] == 1000
            assert info["layers"] == 3
            assert info["optimizer"] == "Adam"
    
    def test_save_networks(self, network_manager, mock_networks):
        """Test saving networks to disk."""
        q_network, target_network = mock_networks
        network_manager.q_network = q_network
        network_manager.target_q_network = target_network
        
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_network")
            network_manager.save_networks(filepath)
            
            # Verify save_weights was called for both networks
            q_network.save_weights.assert_called_once_with(f"{filepath}_q_network.h5")
            target_network.save_weights.assert_called_once_with(f"{filepath}_target_network.h5")
    
    def test_save_networks_not_initialized(self, network_manager):
        """Test saving networks when not initialized."""
        network_manager.save_networks("test_path")
        
        # Should handle gracefully when networks are None
        assert network_manager.q_network is None
        assert network_manager.target_q_network is None
    
    def test_load_networks(self, network_manager, mock_networks):
        """Test loading networks from disk."""
        q_network, target_network = mock_networks
        network_manager.q_network = q_network
        network_manager.target_q_network = target_network
        
        filepath = "test_network"
        result = network_manager.load_networks(filepath)
        
        # Verify load_weights was called for both networks
        q_network.load_weights.assert_called_once_with(f"{filepath}_q_network.h5")
        target_network.load_weights.assert_called_once_with(f"{filepath}_target_network.h5")
        assert result is True
    
    def test_load_networks_not_initialized(self, network_manager):
        """Test loading networks when not initialized."""
        result = network_manager.load_networks("test_path")
        
        # Should return False when networks are None
        assert result is False
    
    def test_load_networks_file_error(self, network_manager, mock_networks):
        """Test loading networks with file error."""
        q_network, target_network = mock_networks
        network_manager.q_network = q_network
        network_manager.target_q_network = target_network
        
        # Configure load_weights to raise exception
        q_network.load_weights.side_effect = FileNotFoundError("File not found")
        
        result = network_manager.load_networks("nonexistent_path")
        assert result is False


class TestConvenienceFunctions:
    """Test convenience functions for network creation."""
    
    def test_create_dqn_networks(self):
        """Test convenience function for creating DQN networks."""
        with patch('monkey_coder.quantum.neural_networks.DQNNetworkManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.create_networks.return_value = ("q_net", "target_net")
            mock_manager_class.return_value = mock_manager
            
            result = create_dqn_networks(
                state_size=21,
                action_size=12,
                architecture="deep",
                learning_rate=0.002
            )
            
            # Verify manager was created and networks were created
            mock_manager_class.assert_called_once_with(
                state_size=21,
                action_size=12,
                architecture="deep",
                learning_rate=0.002
            )
            mock_manager.create_networks.assert_called_once()
            assert result == ("q_net", "target_net")


class TestNetworkIntegration:
    """Integration tests for neural network functionality."""
    
    def test_network_prediction_shape(self):
        """Test that network predictions have correct shape."""
        try:
            _ensure_tensorflow()
        except ImportError:
            pytest.skip("TensorFlow not available")
        
        # Create actual networks
        q_network, target_network = create_dqn_networks(
            state_size=21,
            action_size=12,
            architecture="lightweight"  # Use lightweight for faster testing
        )
        
        # Test prediction shapes
        test_state = np.random.random((1, 21))
        q_values = q_network.predict(test_state, verbose=0)
        target_q_values = target_network.predict(test_state, verbose=0)
        
        assert q_values.shape == (1, 12)
        assert target_q_values.shape == (1, 12)
    
    def test_network_training_step(self):
        """Test single training step on network."""
        try:
            _ensure_tensorflow()
        except ImportError:
            pytest.skip("TensorFlow not available")
        
        # Create networks
        q_network, _ = create_dqn_networks(
            state_size=21,
            action_size=12,
            architecture="lightweight"
        )
        
        # Prepare training data
        states = np.random.random((32, 21))
        targets = np.random.random((32, 12))
        
        # Perform training step
        history = q_network.fit(states, targets, epochs=1, verbose=0)
        
        # Verify training occurred
        assert 'loss' in history.history
        assert len(history.history['loss']) == 1
        assert isinstance(history.history['loss'][0], (int, float))
    
    def test_network_weight_copying(self):
        """Test weight copying between networks."""
        try:
            _ensure_tensorflow()
        except ImportError:
            pytest.skip("TensorFlow not available")
        
        # Create networks
        manager = DQNNetworkManager(
            state_size=21,
            action_size=12,
            architecture="lightweight"
        )
        q_network, target_network = manager.create_networks()
        
        # Get initial weights
        initial_q_weights = q_network.get_weights()
        initial_target_weights = target_network.get_weights()
        
        # Verify weights are the same initially (due to initialization)
        for q_w, t_w in zip(initial_q_weights, initial_target_weights):
            assert np.allclose(q_w, t_w)
        
        # Train Q-network to change its weights
        states = np.random.random((10, 21))
        targets = np.random.random((10, 12))
        q_network.fit(states, targets, epochs=1, verbose=0)
        
        # Get updated weights
        updated_q_weights = q_network.get_weights()
        
        # Verify Q-network weights changed
        weights_changed = False
        for initial, updated in zip(initial_q_weights, updated_q_weights):
            if not np.allclose(initial, updated):
                weights_changed = True
                break
        
        assert weights_changed, "Q-network weights should have changed after training"
        
        # Update target network
        manager.update_target_network()
        
        # Verify target network now has Q-network weights
        final_target_weights = target_network.get_weights()
        for q_w, t_w in zip(updated_q_weights, final_target_weights):
            assert np.allclose(q_w, t_w)


class TestNetworkPerformance:
    """Performance tests for neural network operations."""
    
    def test_prediction_performance(self):
        """Test prediction performance meets requirements."""
        try:
            _ensure_tensorflow()
        except ImportError:
            pytest.skip("TensorFlow not available")
        
        import time
        
        # Create lightweight network for performance testing
        q_network, _ = create_dqn_networks(
            state_size=21,
            action_size=12,
            architecture="lightweight"
        )
        
        # Test batch prediction performance
        batch_size = 100
        test_states = np.random.random((batch_size, 21))
        
        start_time = time.perf_counter()
        predictions = q_network.predict(test_states, verbose=0)
        prediction_time = time.perf_counter() - start_time
        
        # Performance requirements
        assert predictions.shape == (batch_size, 12)
        assert prediction_time < 1.0  # Should predict 100 states in < 1 second
    
    def test_memory_efficiency(self):
        """Test memory usage remains reasonable."""
        try:
            _ensure_tensorflow()
        except ImportError:
            pytest.skip("TensorFlow not available")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create multiple networks to test memory usage
        networks = []
        for _ in range(5):
            q_net, target_net = create_dqn_networks(
                state_size=21,
                action_size=12,
                architecture="standard"
            )
            networks.append((q_net, target_net))
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory should not increase excessively (allowing 200MB for 10 networks)
        assert memory_increase < 200, f"Memory increased by {memory_increase:.1f}MB"
        
        # Cleanup
        del networks