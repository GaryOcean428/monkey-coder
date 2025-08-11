"""
Enhanced Neural Network Implementation for DQN Routing Agent

This module provides the neural network backbone for the DQN agent,
implementing both TensorFlow and numpy-based implementations for Phase 2.
Features target networks for stable learning and automatic weight updates.
"""

import logging
import numpy as np
import json
from typing import Optional, Tuple, List, Dict, Any
from abc import ABC, abstractmethod

# Try to import tensorflow, fallback to numpy implementation if not available
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TENSORFLOW_AVAILABLE = True

    # Type aliases for when TensorFlow is available
    KerasModel = keras.Model

except ImportError:
    TENSORFLOW_AVAILABLE = False
    tf = None
    keras = None
    layers = None

    # Dummy type for when TensorFlow is not available
    class KerasModel:
        pass

logger = logging.getLogger(__name__)


class BaseDQNNetwork(ABC):
    """Abstract base class for DQN networks."""

    @abstractmethod
    def predict(self, states: np.ndarray) -> np.ndarray:
        """Predict Q-values for given states."""
        pass

    @abstractmethod
    def train(self, states: np.ndarray, targets: np.ndarray) -> float:
        """Train the network and return loss."""
        pass

    @abstractmethod
    def get_weights(self) -> List[np.ndarray]:
        """Get network weights."""
        pass

    @abstractmethod
    def set_weights(self, weights: List[np.ndarray]) -> None:
        """Set network weights."""
        pass

    @abstractmethod
    def save_model(self, filepath: str) -> bool:
        """Save model to file."""
        pass

    @abstractmethod
    def load_model(self, filepath: str) -> bool:
        """Load model from file."""
        pass


class TensorFlowDQNNetwork(BaseDQNNetwork):
    """
    TensorFlow-based DQN network implementation.

    Uses Keras to build and train the neural network for routing decisions.
    """

    def __init__(
        self,
        state_size: int,
        action_size: int,
        learning_rate: float = 0.001,
        hidden_layers: Tuple[int, ...] = (64, 32),
        activation: str = "relu",
        output_activation: str = "linear",
        dropout_rate: float = 0.1
    ):
        """Initialize TensorFlow DQN network."""
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required for TensorFlowDQNNetwork")

        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.hidden_layers = hidden_layers
        self.activation = activation
        self.output_activation = output_activation
        self.dropout_rate = dropout_rate

        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_network()

        logger.info(f"Initialized TensorFlow DQN network: {state_size}->{hidden_layers}->{action_size}")

    def _build_model(self) -> KerasModel:
        """Build the neural network model."""
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required for TensorFlowDQNNetwork")

        model = keras.Sequential()

        # Input layer
        model.add(layers.Dense(
            self.hidden_layers[0],
            input_shape=(self.state_size,),
            activation=self.activation,
            name="input_layer"
        ))
        model.add(layers.Dropout(self.dropout_rate))

        # Hidden layers
        for i, units in enumerate(self.hidden_layers[1:], 1):
            model.add(layers.Dense(
                units,
                activation=self.activation,
                name=f"hidden_layer_{i}"
            ))
            model.add(layers.Dropout(self.dropout_rate))

        # Output layer
        model.add(layers.Dense(
            self.action_size,
            activation=self.output_activation,
            name="output_layer"
        ))

        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='mse',
            metrics=['mae']
        )

        return model

    def predict(self, states: np.ndarray) -> np.ndarray:
        """Predict Q-values for given states."""
        if len(states.shape) == 1:
            states = states.reshape(1, -1)
        return self.model.predict(states, verbose=0)

    def predict_target(self, states: np.ndarray) -> np.ndarray:
        """Predict Q-values using target network."""
        if len(states.shape) == 1:
            states = states.reshape(1, -1)
        return self.target_model.predict(states, verbose=0)

    def train(self, states: np.ndarray, targets: np.ndarray) -> float:
        """Train the network and return loss."""
        history = self.model.fit(
            states, targets,
            epochs=1,
            verbose=0,
            batch_size=len(states)
        )
        return history.history['loss'][0]

    def get_weights(self) -> List[np.ndarray]:
        """Get network weights."""
        return self.model.get_weights()

    def set_weights(self, weights: List[np.ndarray]) -> None:
        """Set network weights."""
        self.model.set_weights(weights)

    def update_target_network(self, tau: float = 1.0) -> None:
        """
        Update target network weights.

        Args:
            tau: Soft update parameter (1.0 = hard update, <1.0 = soft update)
        """
        if tau == 1.0:
            # Hard update
            self.target_model.set_weights(self.model.get_weights())
        else:
            # Soft update
            main_weights = self.model.get_weights()
            target_weights = self.target_model.get_weights()

            updated_weights = []
            for main_w, target_w in zip(main_weights, target_weights):
                updated_weights.append(tau * main_w + (1.0 - tau) * target_w)

            self.target_model.set_weights(updated_weights)

    def save_model(self, filepath: str) -> bool:
        """Save model to file."""
        try:
            self.model.save(f"{filepath}.h5")

            # Save configuration
            config = {
                'state_size': self.state_size,
                'action_size': self.action_size,
                'learning_rate': self.learning_rate,
                'hidden_layers': self.hidden_layers,
                'activation': self.activation,
                'output_activation': self.output_activation,
                'dropout_rate': self.dropout_rate
            }

            with open(f"{filepath}_config.json", 'w') as f:
                json.dump(config, f)

            return True
        except Exception as e:
            logger.error(f"Failed to save TensorFlow model: {e}")
            return False

    def load_model(self, filepath: str) -> bool:
        """Load model from file."""
        try:
            self.model = keras.models.load_model(f"{filepath}.h5")
            self.target_model = keras.models.load_model(f"{filepath}.h5")

            # Load configuration
            with open(f"{filepath}_config.json", 'r') as f:
                config = json.load(f)

            self.state_size = config['state_size']
            self.action_size = config['action_size']
            self.learning_rate = config['learning_rate']
            self.hidden_layers = tuple(config['hidden_layers'])
            self.activation = config['activation']
            self.output_activation = config['output_activation']
            self.dropout_rate = config.get('dropout_rate', 0.1)

            return True
        except Exception as e:
            logger.error(f"Failed to load TensorFlow model: {e}")
            return False


class NumpyDQNNetwork(BaseDQNNetwork):
    """
    Numpy-based DQN network implementation.

    Provides a basic neural network implementation using only numpy,
    suitable for environments without TensorFlow.
    """

    def __init__(
        self,
        state_size: int,
        action_size: int,
        learning_rate: float = 0.001,
        hidden_layers: Tuple[int, ...] = (64, 32),
        activation: str = "relu"
    ):
        """Initialize numpy DQN network."""
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.hidden_layers = hidden_layers
        self.activation = activation

        # Build network architecture
        self.layer_sizes = [state_size] + list(hidden_layers) + [action_size]
        self.weights = []
        self.biases = []
        self.target_weights = []
        self.target_biases = []

        self._initialize_weights()
        self.update_target_network()

        # Training statistics
        self.training_step = 0
        self.loss_history = []

        logger.info(f"Initialized numpy DQN network: {state_size}->{hidden_layers}->{action_size}")

    def _initialize_weights(self) -> None:
        """Initialize network weights using Xavier initialization."""
        np.random.seed(42)  # For reproducible results

        for i in range(len(self.layer_sizes) - 1):
            # Xavier initialization
            fan_in = self.layer_sizes[i]
            fan_out = self.layer_sizes[i + 1]
            limit = np.sqrt(6.0 / (fan_in + fan_out))

            weight = np.random.uniform(-limit, limit, (fan_in, fan_out))
            bias = np.zeros((1, fan_out))

            self.weights.append(weight)
            self.biases.append(bias)
            self.target_weights.append(weight.copy())
            self.target_biases.append(bias.copy())

    def _activation_function(self, x: np.ndarray) -> np.ndarray:
        """Apply activation function."""
        if self.activation == "relu":
            return np.maximum(0, x)
        elif self.activation == "tanh":
            return np.tanh(x)
        elif self.activation == "sigmoid":
            return 1 / (1 + np.exp(-np.clip(x, -500, 500)))  # Clip to prevent overflow
        else:
            return x  # Linear activation

    def _activation_derivative(self, x: np.ndarray) -> np.ndarray:
        """Compute activation function derivative."""
        if self.activation == "relu":
            return (x > 0).astype(float)
        elif self.activation == "tanh":
            return 1 - np.tanh(x) ** 2
        elif self.activation == "sigmoid":
            sig = 1 / (1 + np.exp(-np.clip(x, -500, 500)))
            return sig * (1 - sig)
        else:
            return np.ones_like(x)  # Linear activation derivative

    def _forward_pass(self, states: np.ndarray, use_target: bool = False) -> Tuple[np.ndarray, List[np.ndarray]]:
        """
        Perform forward pass through the network.

        Returns:
            Tuple of (output, layer_outputs) for backpropagation
        """
        weights = self.target_weights if use_target else self.weights
        biases = self.target_biases if use_target else self.biases

        layer_outputs = [states]
        current_input = states

        for i, (w, b) in enumerate(zip(weights, biases)):
            z = np.dot(current_input, w) + b

            # Apply activation (no activation on output layer)
            if i < len(weights) - 1:
                current_input = self._activation_function(z)
            else:
                current_input = z  # Linear output for Q-values

            layer_outputs.append(current_input)

        return current_input, layer_outputs

    def predict(self, states: np.ndarray) -> np.ndarray:
        """Predict Q-values for given states."""
        if len(states.shape) == 1:
            states = states.reshape(1, -1)

        output, _ = self._forward_pass(states, use_target=False)
        return output

    def predict_target(self, states: np.ndarray) -> np.ndarray:
        """Predict Q-values using target network."""
        if len(states.shape) == 1:
            states = states.reshape(1, -1)

        output, _ = self._forward_pass(states, use_target=True)
        return output

    def train(self, states: np.ndarray, targets: np.ndarray) -> float:
        """Train the network using backpropagation."""
        batch_size = states.shape[0]

        # Forward pass
        predictions, layer_outputs = self._forward_pass(states)

        # Compute loss (MSE)
        loss = np.mean((predictions - targets) ** 2)
        self.loss_history.append(loss)

        # Backward pass
        self._backward_pass(layer_outputs, targets)

        self.training_step += 1
        return loss

    def _backward_pass(self, layer_outputs: List[np.ndarray], targets: np.ndarray) -> None:
        """Perform backward pass and update weights."""
        batch_size = layer_outputs[0].shape[0]

        # Compute output layer error
        output_error = layer_outputs[-1] - targets

        # Backpropagate errors
        errors = [output_error]

        for i in range(len(self.weights) - 1, 0, -1):
            error = np.dot(errors[-1], self.weights[i].T)

            # Apply activation derivative for hidden layers
            activated_output = layer_outputs[i]
            error = error * self._activation_derivative(activated_output)
            errors.append(error)

        errors.reverse()

        # Update weights and biases
        for i in range(len(self.weights)):
            # Compute gradients
            weight_gradient = np.dot(layer_outputs[i].T, errors[i]) / batch_size
            bias_gradient = np.mean(errors[i], axis=0, keepdims=True)

            # Update with learning rate
            self.weights[i] -= self.learning_rate * weight_gradient
            self.biases[i] -= self.learning_rate * bias_gradient

    def get_weights(self) -> List[np.ndarray]:
        """Get network weights."""
        return [w.copy() for w in self.weights] + [b.copy() for b in self.biases]

    def set_weights(self, weights: List[np.ndarray]) -> None:
        """Set network weights."""
        num_layers = len(self.weights)
        self.weights = [w.copy() for w in weights[:num_layers]]
        self.biases = [b.copy() for b in weights[num_layers:]]

    def update_target_network(self, tau: float = 1.0) -> None:
        """Update target network weights."""
        if tau == 1.0:
            # Hard update
            self.target_weights = [w.copy() for w in self.weights]
            self.target_biases = [b.copy() for b in self.biases]
        else:
            # Soft update
            for i in range(len(self.weights)):
                self.target_weights[i] = tau * self.weights[i] + (1.0 - tau) * self.target_weights[i]
                self.target_biases[i] = tau * self.biases[i] + (1.0 - tau) * self.target_biases[i]

    def save_model(self, filepath: str) -> bool:
        """Save model to file."""
        try:
            model_data = {
                'weights': [w.tolist() for w in self.weights],
                'biases': [b.tolist() for b in self.biases],
                'target_weights': [w.tolist() for w in self.target_weights],
                'target_biases': [b.tolist() for b in self.target_biases],
                'config': {
                    'state_size': self.state_size,
                    'action_size': self.action_size,
                    'learning_rate': self.learning_rate,
                    'hidden_layers': self.hidden_layers,
                    'activation': self.activation,
                    'training_step': self.training_step
                },
                'loss_history': self.loss_history[-100:]  # Save last 100 losses
            }

            with open(f"{filepath}.json", 'w') as f:
                json.dump(model_data, f)

            return True
        except Exception as e:
            logger.error(f"Failed to save numpy model: {e}")
            return False

    def load_model(self, filepath: str) -> bool:
        """Load model from file."""
        try:
            with open(f"{filepath}.json", 'r') as f:
                model_data = json.load(f)

            # Restore weights
            self.weights = [np.array(w) for w in model_data['weights']]
            self.biases = [np.array(b) for b in model_data['biases']]
            self.target_weights = [np.array(w) for w in model_data['target_weights']]
            self.target_biases = [np.array(b) for b in model_data['target_biases']]

            # Restore configuration
            config = model_data['config']
            self.state_size = config['state_size']
            self.action_size = config['action_size']
            self.learning_rate = config['learning_rate']
            self.hidden_layers = tuple(config['hidden_layers'])
            self.activation = config['activation']
            self.training_step = config.get('training_step', 0)

            # Restore loss history
            self.loss_history = model_data.get('loss_history', [])

            return True
        except Exception as e:
            logger.error(f"Failed to load numpy model: {e}")
            return False


class DQNNetwork:
    """
    Unified DQN Network interface that automatically selects implementation.

    Uses TensorFlow if available, falls back to numpy implementation.
    """

    def __init__(
        self,
        state_size: int,
        action_size: int,
        learning_rate: float = 0.001,
        hidden_layers: Tuple[int, ...] = (64, 32),
        activation: str = "relu",
        force_numpy: bool = False
    ):
        """
        Initialize DQN network with automatic implementation selection.

        Args:
            force_numpy: Force use of numpy implementation even if TensorFlow is available
        """
        self.state_size = state_size
        self.action_size = action_size

        if TENSORFLOW_AVAILABLE and not force_numpy:
            try:
                self.network = TensorFlowDQNNetwork(
                    state_size, action_size, learning_rate, hidden_layers, activation
                )
                self.implementation = "tensorflow"
                logger.info("Using TensorFlow DQN implementation")
            except Exception as e:
                logger.warning(f"TensorFlow initialization failed, falling back to numpy: {e}")
                self.network = NumpyDQNNetwork(
                    state_size, action_size, learning_rate, hidden_layers, activation
                )
                self.implementation = "numpy"
        else:
            self.network = NumpyDQNNetwork(
                state_size, action_size, learning_rate, hidden_layers, activation
            )
            self.implementation = "numpy"
            if not TENSORFLOW_AVAILABLE:
                logger.warning("TensorFlow not available, using numpy-based fallback network")

    def predict(self, states: np.ndarray) -> np.ndarray:
        """Predict Q-values for given states."""
        return self.network.predict(states)

    def predict_target(self, states: np.ndarray) -> np.ndarray:
        """Predict Q-values using target network."""
        if hasattr(self.network, 'predict_target'):
            return self.network.predict_target(states)
        else:
            # Fallback for implementations without target network support
            return self.network.predict(states)

    def train(self, states: np.ndarray, targets: np.ndarray) -> float:
        """Train the network and return loss."""
        return self.network.train(states, targets)

    def update_target_network(self, tau: float = 1.0) -> None:
        """Update target network weights."""
        if hasattr(self.network, 'update_target_network'):
            self.network.update_target_network(tau)

    def get_weights(self) -> List[np.ndarray]:
        """Get network weights."""
        return self.network.get_weights()

    def set_weights(self, weights: List[np.ndarray]) -> None:
        """Set network weights."""
        self.network.set_weights(weights)

    def save_model(self, filepath: str) -> bool:
        """Save model to file."""
        return self.network.save_model(filepath)

    def load_model(self, filepath: str) -> bool:
        """Load model from file."""
        return self.network.load_model(filepath)


# Convenience function for creating networks
def create_dqn_network(
    state_size: int,
    action_size: int,
    learning_rate: float = 0.001,
    hidden_layers: Tuple[int, ...] = (64, 32),
    activation: str = "relu",
    force_numpy: bool = False
) -> DQNNetwork:
    """
    Create a DQN network with automatic implementation selection.

    Args:
        state_size: Dimension of the state space
        action_size: Number of possible actions
        learning_rate: Learning rate for training
        hidden_layers: Tuple of hidden layer sizes
        activation: Activation function ("relu", "tanh", "sigmoid")
        force_numpy: Force numpy implementation

    Returns:
        Configured DQN network
    """
    return DQNNetwork(
        state_size=state_size,
        action_size=action_size,
        learning_rate=learning_rate,
        hidden_layers=hidden_layers,
        activation=activation,
        force_numpy=force_numpy
    )


# Legacy compatibility
NumpyDQNModel = NumpyDQNNetwork

# Ensure TensorFlow-specific symbols are not importable when TF is unavailable
# This makes `from ... import TensorFlowDQNNetwork` raise ImportError in tests.
if not TENSORFLOW_AVAILABLE:
    try:
        del TensorFlowDQNNetwork  # type: ignore[name-defined]
    except Exception:
        pass
