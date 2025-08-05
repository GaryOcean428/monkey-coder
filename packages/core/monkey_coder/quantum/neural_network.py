"""
Neural Network Implementation for DQN Agent

This module provides the neural network architecture for the Deep Q-Network
agent used in quantum routing. It supports both TensorFlow/Keras and a
NumPy fallback implementation for maximum compatibility.
"""

import logging
from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    # Only import for type checking when TensorFlow is available
    try:
        from tensorflow import keras
    except ImportError:
        keras = None

logger = logging.getLogger(__name__)

# Try to import TensorFlow, but don't fail if not available
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models, optimizers
    TENSORFLOW_AVAILABLE = True
    logger.info("TensorFlow/Keras is available for neural network implementation")
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logger.warning("TensorFlow/Keras not available, using NumPy fallback implementation")


class NumPyNeuralNetwork:
    """
    NumPy fallback implementation of a neural network for DQN.

    This provides a simple feedforward neural network using only NumPy,
    serving as a fallback when TensorFlow is not available.
    """

    def __init__(
        self,
        input_size: int,
        hidden_sizes: Tuple[int, ...] = (128, 128),
        output_size: int = 1,
        learning_rate: float = 0.001
    ):
        """
        Initialize the NumPy neural network.

        Args:
            input_size: Size of the input layer
            hidden_sizes: Tuple of hidden layer sizes
            output_size: Size of the output layer
            learning_rate: Learning rate for training
        """
        self.input_size = input_size
        self.hidden_sizes = hidden_sizes
        self.output_size = output_size
        self.learning_rate = learning_rate

        # Initialize network architecture
        self.layer_sizes = [input_size] + list(hidden_sizes) + [output_size]
        self.weights = []
        self.biases = []

        # Initialize weights and biases
        np.random.seed(42)  # For reproducible results
        for i in range(len(self.layer_sizes) - 1):
            # Xavier/Glorot initialization
            scale = np.sqrt(2.0 / (self.layer_sizes[i] + self.layer_sizes[i + 1]))
            weight_matrix = np.random.randn(self.layer_sizes[i], self.layer_sizes[i + 1]) * scale
            bias_vector = np.zeros((1, self.layer_sizes[i + 1]))

            self.weights.append(weight_matrix)
            self.biases.append(bias_vector)

        logger.info(f"Initialized NumPy neural network: {self.layer_sizes}")

    def relu(self, x: np.ndarray) -> np.ndarray:
        """ReLU activation function."""
        return np.maximum(0, x)

    def relu_derivative(self, x: np.ndarray) -> np.ndarray:
        """Derivative of ReLU activation function."""
        return (x > 0).astype(float)

    def forward(self, x: np.ndarray) -> Tuple[np.ndarray, list]:
        """
        Forward pass through the network.

        Args:
            x: Input data

        Returns:
            Tuple of (output, activations) where activations includes
            all intermediate layer outputs for backpropagation
        """
        activations = [x]
        current_input = x

        # Forward through hidden layers
        for i in range(len(self.weights) - 1):
            z = np.dot(current_input, self.weights[i]) + self.biases[i]
            current_input = self.relu(z)
            activations.append(current_input)

        # Output layer (no activation for Q-values)
        z = np.dot(current_input, self.weights[-1]) + self.biases[-1]
        activations.append(z)

        return z, activations

    def predict(self, x: np.ndarray, verbose: int = 0) -> np.ndarray:
        """
        Make predictions with the network.

        Args:
            x: Input data
            verbose: Verbosity level (for compatibility with Keras)

        Returns:
            Network predictions
        """
        output, _ = self.forward(x)
        return output

    def fit(self, x: np.ndarray, y: np.ndarray, epochs: int = 1, verbose: int = 0) -> Dict[str, list]:
        """
        Train the network using backpropagation.

        Args:
            x: Training input data
            y: Training target data
            epochs: Number of training epochs
            verbose: Verbosity level

        Returns:
            Dictionary with training history (for compatibility with Keras)
        """
        losses = []

        for epoch in range(epochs):
            total_loss = 0

            # Mini-batch training (process each sample individually)
            for i in range(len(x)):
                sample_x = x[i:i+1]  # Keep as 2D array
                sample_y = y[i:i+1]

                # Forward pass
                output, activations = self.forward(sample_x)

                # Calculate loss (MSE)
                loss = np.mean((output - sample_y) ** 2)
                total_loss += loss

                # Backward pass
                # Output layer error
                error = output - sample_y
                delta = error

                # Backpropagate through layers
                for layer_idx in range(len(self.weights) - 1, -1, -1):
                    if layer_idx == len(self.weights) - 1:
                        # Output layer
                        dW = np.dot(activations[layer_idx].T, delta)
                        dB = np.sum(delta, axis=0, keepdims=True)
                    else:
                        # Hidden layer
                        delta = np.dot(delta, self.weights[layer_idx + 1].T) * \
                               self.relu_derivative(activations[layer_idx + 1])
                        dW = np.dot(activations[layer_idx].T, delta)
                        dB = np.sum(delta, axis=0, keepdims=True)

                    # Update weights and biases
                    self.weights[layer_idx] -= self.learning_rate * dW
                    self.biases[layer_idx] -= self.learning_rate * dB

            avg_loss = total_loss / len(x)
            losses.append(avg_loss)

            if verbose > 0:
                logger.info(f"Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.6f}")

        # Return history in Keras-compatible format
        return {'loss': losses}

    def get_weights(self) -> list:
        """Get network weights and biases."""
        weights_and_biases = []
        for i in range(len(self.weights)):
            weights_and_biases.append(self.weights[i])
            weights_and_biases.append(self.biases[i])
        return weights_and_biases

    def set_weights(self, weights: list) -> None:
        """Set network weights and biases."""
        idx = 0
        for i in range(len(self.weights)):
            self.weights[i] = weights[idx]
            self.biases[i] = weights[idx + 1]
            idx += 2

    def summary(self) -> str:
        """Get a summary of the network architecture."""
        summary_lines = [f"NumPy Neural Network Summary:"]
        summary_lines.append(f"Input layer: {self.input_size} units")

        for i, size in enumerate(self.hidden_sizes):
            summary_lines.append(f"Hidden layer {i+1}: {size} units (ReLU)")

        summary_lines.append(f"Output layer: {self.output_size} units (linear)")

        total_params = sum(
            w.size + b.size for w, b in zip(self.weights, self.biases)
        )
        summary_lines.append(f"Total parameters: {total_params:,}")

        return "\n".join(summary_lines)


def create_dqn_network(
    state_size: int,
    action_size: int,
    learning_rate: float = 0.001,
    hidden_layers: Tuple[int, ...] = (128, 128)
) -> Any:
    """
    Create a Deep Q-Network neural network.

    This function creates a neural network suitable for DQN training,
    with TensorFlow/Keras as the preferred implementation and NumPy as fallback.

    Args:
        state_size: Size of the state input vector
        action_size: Number of possible actions (output size)
        learning_rate: Learning rate for optimization
        hidden_layers: Tuple specifying hidden layer sizes

    Returns:
        Neural network model compatible with the DQN agent interface
    """
    logger.info(f"Creating DQN network: state_size={state_size}, action_size={action_size}")

    if TENSORFLOW_AVAILABLE:
        return _create_tensorflow_network(state_size, action_size, learning_rate, hidden_layers)
    else:
        return _create_numpy_network(state_size, action_size, learning_rate, hidden_layers)


def _create_tensorflow_network(
    state_size: int,
    action_size: int,
    learning_rate: float,
    hidden_layers: Tuple[int, ...]
) -> Any:
    """Create TensorFlow/Keras DQN network."""

    # Build the model
    model = keras.Sequential()

    # Input layer
    model.add(layers.Input(shape=(state_size,)))

    # Hidden layers
    for i, units in enumerate(hidden_layers):
        model.add(layers.Dense(
            units=units,
            activation='relu',
            kernel_initializer='he_normal',
            name=f'hidden_{i+1}'
        ))
        # Add dropout for regularization
        model.add(layers.Dropout(0.2, name=f'dropout_{i+1}'))

    # Output layer (linear activation for Q-values)
    model.add(layers.Dense(
        action_size,
        activation='linear',
        kernel_initializer='he_normal',
        name='output'
    ))

    # Compile the model
    optimizer = optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss='mse',  # Mean Squared Error for Q-learning
        metrics=['mae']  # Mean Absolute Error for monitoring
    )

    logger.info(f"Created TensorFlow/Keras model with {model.count_params():,} parameters")
    model.summary(print_fn=logger.info)

    return model


def _create_numpy_network(
    state_size: int,
    action_size: int,
    learning_rate: float,
    hidden_layers: Tuple[int, ...]
) -> NumPyNeuralNetwork:
    """Create NumPy fallback DQN network."""

    network = NumPyNeuralNetwork(
        input_size=state_size,
        hidden_sizes=hidden_layers,
        output_size=action_size,
        learning_rate=learning_rate
    )

    logger.info(network.summary())

    return network


def validate_network_compatibility() -> Dict[str, Any]:
    """
    Validate neural network implementation and return compatibility info.

    Returns:
        Dictionary with compatibility information
    """
    compatibility_info = {
        'tensorflow_available': TENSORFLOW_AVAILABLE,
        'tensorflow_version': None,
        'fallback_available': True,
        'recommended_implementation': 'tensorflow' if TENSORFLOW_AVAILABLE else 'numpy',
        'performance_note': None
    }

    if TENSORFLOW_AVAILABLE:
        compatibility_info['tensorflow_version'] = tf.__version__
        compatibility_info['performance_note'] = (
            "TensorFlow/Keras provides GPU acceleration and optimized performance"
        )
    else:
        compatibility_info['performance_note'] = (
            "NumPy fallback provides basic functionality but limited performance"
        )
        logger.warning("TensorFlow not available - using NumPy fallback for neural networks")

    return compatibility_info


# Export compatibility info for external use
NETWORK_COMPATIBILITY = validate_network_compatibility()
