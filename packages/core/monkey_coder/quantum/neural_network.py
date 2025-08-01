"""
Neural Network Implementation for DQN Routing Agent

This module provides the neural network backbone for the DQN agent,
implementing the actual deep learning components needed for Phase 2.
"""

import logging
import numpy as np
from typing import Optional, Tuple

# Try to import tensorflow, fallback to basic implementation if not available
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    tf = None
    keras = None
    layers = None

logger = logging.getLogger(__name__)


class DQNNetwork:
    """
    Deep Q-Network for routing decisions.
    
    Implements a neural network that maps routing states to Q-values
    for each possible action (provider/model combination).
    """
    
    def __init__(
        self,
        state_size: int,
        action_size: int,
        learning_rate: float = 0.001,
        hidden_layers: Tuple[int, ...] = (64, 32),
        activation: str = "relu",
        output_activation: str = "linear"
    ):
        """
        Initialize the DQN network.
        
        Args:
            state_size: Dimension of the state space
            action_size: Number of possible actions
            learning_rate: Learning rate for training
            hidden_layers: Tuple of hidden layer sizes
            activation: Activation function for hidden layers
            output_activation: Activation function for output layer
        """
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.hidden_layers = hidden_layers
        self.activation = activation
        self.output_activation = output_activation
        
        if TENSORFLOW_AVAILABLE:
            self.model = self._build_tensorflow_model()
            logger.info(f"Initialized TensorFlow DQN network: {state_size} -> {hidden_layers} -> {action_size}")
        else:
            self.model = self._build_numpy_model()
            logger.warning("TensorFlow not available, using numpy-based fallback network")
    
    def _build_tensorflow_model(self) -> keras.Model:
        """Build the neural network using TensorFlow/Keras."""
        model = keras.Sequential()
        
        # Input layer
        model.add(layers.Dense(
            self.hidden_layers[0],
            input_shape=(self.state_size,),
            activation=self.activation,
            name="input_layer"
        ))
        
        # Hidden layers
        for i, units in enumerate(self.hidden_layers[1:], 1):
            model.add(layers.Dense(
                units,
                activation=self.activation,
                name=f"hidden_layer_{i}"
            ))
        
        # Output layer (Q-values for each action)
        model.add(layers.Dense(
            self.action_size,
            activation=self.output_activation,
            name="output_layer"
        ))
        
        # Compile the model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def _build_numpy_model(self) -> "NumpyDQNModel":
        """Build a simple numpy-based model as fallback."""
        return NumpyDQNModel(
            state_size=self.state_size,
            action_size=self.action_size,
            hidden_layers=self.hidden_layers,
            learning_rate=self.learning_rate
        )
    
    def predict(self, state: np.ndarray, verbose: int = 0) -> np.ndarray:
        """
        Predict Q-values for given state(s).
        
        Args:
            state: State vector(s) to predict Q-values for
            verbose: Verbosity level for prediction
            
        Returns:
            Q-values for each action
        """
        if TENSORFLOW_AVAILABLE:
            return self.model.predict(state, verbose=verbose)
        else:
            return self.model.predict(state)
    
    def fit(
        self,
        x: np.ndarray,
        y: np.ndarray,
        epochs: int = 1,
        verbose: int = 0,
        batch_size: Optional[int] = None
    ) -> dict:
        """
        Train the network on given data.
        
        Args:
            x: Input states
            y: Target Q-values
            epochs: Number of training epochs
            verbose: Verbosity level
            batch_size: Batch size for training
            
        Returns:
            Training history
        """
        if TENSORFLOW_AVAILABLE:
            history = self.model.fit(
                x, y,
                epochs=epochs,
                verbose=verbose,
                batch_size=batch_size
            )
            return history
        else:
            loss = self.model.fit(x, y, epochs=epochs)
            return {"history": {"loss": [loss]}}
    
    def get_weights(self) -> list:
        """Get model weights."""
        if TENSORFLOW_AVAILABLE:
            return self.model.get_weights()
        else:
            return self.model.get_weights()
    
    def set_weights(self, weights: list) -> None:
        """Set model weights."""
        if TENSORFLOW_AVAILABLE:
            self.model.set_weights(weights)
        else:
            self.model.set_weights(weights)
    
    def save_weights(self, filepath: str) -> None:
        """Save model weights to file."""
        if TENSORFLOW_AVAILABLE:
            self.model.save_weights(filepath)
        else:
            self.model.save_weights(filepath)
    
    def load_weights(self, filepath: str) -> None:
        """Load model weights from file."""
        if TENSORFLOW_AVAILABLE:
            self.model.load_weights(filepath)
        else:
            self.model.load_weights(filepath)


class NumpyDQNModel:
    """
    Simple numpy-based DQN implementation as fallback when TensorFlow is not available.
    
    This provides basic neural network functionality using only numpy,
    allowing the system to work even without TensorFlow installed.
    """
    
    def __init__(
        self,
        state_size: int,
        action_size: int,
        hidden_layers: Tuple[int, ...] = (64, 32),
        learning_rate: float = 0.001
    ):
        """Initialize the numpy-based model."""
        self.state_size = state_size
        self.action_size = action_size
        self.hidden_layers = hidden_layers
        self.learning_rate = learning_rate
        
        # Initialize weights and biases
        self.weights = []
        self.biases = []
        
        # Input to first hidden layer
        layer_sizes = [state_size] + list(hidden_layers) + [action_size]
        
        for i in range(len(layer_sizes) - 1):
            # Xavier initialization
            weight_shape = (layer_sizes[i], layer_sizes[i + 1])
            fan_in = layer_sizes[i]
            fan_out = layer_sizes[i + 1]
            limit = np.sqrt(6.0 / (fan_in + fan_out))
            
            weights = np.random.uniform(-limit, limit, weight_shape)
            bias = np.zeros(layer_sizes[i + 1])
            
            self.weights.append(weights)
            self.biases.append(bias)
        
        logger.info(f"Initialized numpy DQN model with {len(self.weights)} layers")
    
    def _relu(self, x: np.ndarray) -> np.ndarray:
        """ReLU activation function."""
        return np.maximum(0, x)
    
    def _relu_derivative(self, x: np.ndarray) -> np.ndarray:
        """Derivative of ReLU activation."""
        return (x > 0).astype(float)
    
    def predict(self, state: np.ndarray) -> np.ndarray:
        """Forward pass through the network."""
        x = state
        
        # Forward pass through hidden layers
        for i in range(len(self.weights) - 1):
            x = np.dot(x, self.weights[i]) + self.biases[i]
            x = self._relu(x)
        
        # Output layer (no activation)
        x = np.dot(x, self.weights[-1]) + self.biases[-1]
        
        return x
    
    def fit(self, x: np.ndarray, y: np.ndarray, epochs: int = 1) -> float:
        """Train the network using simple gradient descent."""
        total_loss = 0.0
        
        for epoch in range(epochs):
            # Forward pass
            activations = [x]
            z_values = []
            
            current = x
            for i in range(len(self.weights)):
                z = np.dot(current, self.weights[i]) + self.biases[i]
                z_values.append(z)
                
                if i < len(self.weights) - 1:  # Hidden layers
                    current = self._relu(z)
                else:  # Output layer
                    current = z
                
                activations.append(current)
            
            # Compute loss (MSE)
            output = activations[-1]
            loss = np.mean((output - y) ** 2)
            total_loss += loss
            
            # Backward pass
            delta = 2 * (output - y) / len(y)  # MSE derivative
            
            # Backpropagate through layers
            for i in reversed(range(len(self.weights))):
                # Update weights and biases
                self.weights[i] -= self.learning_rate * np.dot(activations[i].T, delta)
                self.biases[i] -= self.learning_rate * np.mean(delta, axis=0)
                
                if i > 0:  # Not the first layer
                    # Propagate delta to previous layer
                    delta = np.dot(delta, self.weights[i].T)
                    # Apply derivative of activation (ReLU)
                    delta *= self._relu_derivative(z_values[i - 1])
        
        return total_loss / epochs
    
    def get_weights(self) -> list:
        """Get model weights."""
        return self.weights + self.biases
    
    def set_weights(self, weights: list) -> None:
        """Set model weights."""
        num_weight_matrices = len(self.weights)
        self.weights = weights[:num_weight_matrices]
        self.biases = weights[num_weight_matrices:]
    
    def save_weights(self, filepath: str) -> None:
        """Save weights to numpy file."""
        weights_data = {
            'weights': self.weights,
            'biases': self.biases,
            'state_size': self.state_size,
            'action_size': self.action_size,
            'hidden_layers': self.hidden_layers
        }
        np.savez(filepath, **weights_data)
        logger.info(f"Saved numpy model weights to {filepath}")
    
    def load_weights(self, filepath: str) -> None:
        """Load weights from numpy file."""
        try:
            weights_data = np.load(filepath, allow_pickle=True)
            self.weights = weights_data['weights'].tolist()
            self.biases = weights_data['biases'].tolist()
            logger.info(f"Loaded numpy model weights from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load numpy weights: {e}")
            raise


def create_dqn_network(
    state_size: int,
    action_size: int,
    **kwargs
) -> DQNNetwork:
    """
    Factory function to create a DQN network.
    
    Args:
        state_size: Dimension of the state space
        action_size: Number of possible actions
        **kwargs: Additional parameters for network configuration
        
    Returns:
        Configured DQN network
    """
    return DQNNetwork(state_size, action_size, **kwargs)