"""
Neural Network Architecture for DQN Agent.

This module implements the Q-network and target Q-network models for the DQN routing agent,
using TensorFlow/Keras with optimized architectures for routing decision learning.

Based on proven patterns from deep reinforcement learning and adapted for the
Monkey Coder quantum routing requirements.
"""

import logging
from typing import Optional, Tuple, Dict, Any

import numpy as np

logger = logging.getLogger(__name__)

# Lazy import TensorFlow to avoid dependency issues during testing
tf = None
Sequential = None
Dense = None
Dropout = None
BatchNormalization = None
Adam = None
Huber = None

def _ensure_tensorflow():
    """Lazy import TensorFlow components to avoid issues during testing."""
    global tf, Sequential, Dense, Dropout, BatchNormalization, Adam, Huber
    
    if tf is None:
        try:
            import tensorflow as tf
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
            from tensorflow.keras.optimizers import Adam
            from tensorflow.keras.losses import Huber
            
            # Set TensorFlow to be less verbose
            tf.get_logger().setLevel('ERROR')
            
        except ImportError as e:
            logger.error(f"TensorFlow not available: {e}")
            raise ImportError(
                "TensorFlow is required for neural network functionality. "
                "Install with: pip install tensorflow"
            ) from e


class QNetworkArchitecture:
    """
    Q-Network architecture factory for different routing complexity levels.
    
    Provides different neural network architectures optimized for various
    routing complexity scenarios and performance requirements.
    """
    
    @staticmethod
    def create_standard_dqn(
        state_size: int,
        action_size: int,
        learning_rate: float = 0.001,
        hidden_layers: Tuple[int, ...] = (128, 64),
        dropout_rate: float = 0.1,
        use_batch_norm: bool = True
    ) -> "tf.keras.Model":
        """
        Create standard DQN architecture for routing decisions.
        
        Args:
            state_size: Size of input state vector
            action_size: Number of possible actions
            learning_rate: Learning rate for optimizer
            hidden_layers: Tuple of hidden layer sizes
            dropout_rate: Dropout rate for regularization
            use_batch_norm: Whether to use batch normalization
            
        Returns:
            Compiled Keras model
        """
        _ensure_tensorflow()
        
        model = Sequential(name="standard_dqn")
        
        # Input layer
        model.add(Dense(
            hidden_layers[0],
            input_dim=state_size,
            activation='relu',
            name='input_layer'
        ))
        
        if use_batch_norm:
            model.add(BatchNormalization(name='input_batch_norm'))
        
        if dropout_rate > 0:
            model.add(Dropout(dropout_rate, name='input_dropout'))
        
        # Hidden layers
        for i, layer_size in enumerate(hidden_layers[1:], 1):
            model.add(Dense(
                layer_size,
                activation='relu',
                name=f'hidden_layer_{i}'
            ))
            
            if use_batch_norm:
                model.add(BatchNormalization(name=f'hidden_batch_norm_{i}'))
            
            if dropout_rate > 0:
                model.add(Dropout(dropout_rate, name=f'hidden_dropout_{i}'))
        
        # Output layer (Q-values for each action)
        model.add(Dense(
            action_size,
            activation='linear',  # Linear activation for Q-values
            name='output_layer'
        ))
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=learning_rate),
            loss=Huber(),  # Huber loss is more stable than MSE for Q-learning
            metrics=['mae']
        )
        
        logger.info(f"Created standard DQN with {model.count_params()} parameters")
        return model
    
    @staticmethod
    def create_deep_dqn(
        state_size: int,
        action_size: int,
        learning_rate: float = 0.0005,
        hidden_layers: Tuple[int, ...] = (256, 128, 64, 32),
        dropout_rate: float = 0.2,
        use_batch_norm: bool = True
    ) -> "tf.keras.Model":
        """
        Create deeper DQN architecture for complex routing decisions.
        
        Args:
            state_size: Size of input state vector
            action_size: Number of possible actions
            learning_rate: Learning rate for optimizer
            hidden_layers: Tuple of hidden layer sizes
            dropout_rate: Dropout rate for regularization
            use_batch_norm: Whether to use batch normalization
            
        Returns:
            Compiled Keras model
        """
        _ensure_tensorflow()
        
        model = Sequential(name="deep_dqn")
        
        # Input layer with larger capacity
        model.add(Dense(
            hidden_layers[0],
            input_dim=state_size,
            activation='relu',
            name='input_layer'
        ))
        
        if use_batch_norm:
            model.add(BatchNormalization(name='input_batch_norm'))
        
        if dropout_rate > 0:
            model.add(Dropout(dropout_rate, name='input_dropout'))
        
        # Multiple hidden layers with decreasing size
        for i, layer_size in enumerate(hidden_layers[1:], 1):
            model.add(Dense(
                layer_size,
                activation='relu',
                name=f'hidden_layer_{i}'
            ))
            
            if use_batch_norm:
                model.add(BatchNormalization(name=f'hidden_batch_norm_{i}'))
            
            if dropout_rate > 0:
                model.add(Dropout(dropout_rate, name=f'hidden_dropout_{i}'))
        
        # Output layer
        model.add(Dense(
            action_size,
            activation='linear',
            name='output_layer'
        ))
        
        # Compile with lower learning rate for stability
        model.compile(
            optimizer=Adam(learning_rate=learning_rate),
            loss=Huber(),
            metrics=['mae']
        )
        
        logger.info(f"Created deep DQN with {model.count_params()} parameters")
        return model
    
    @staticmethod
    def create_lightweight_dqn(
        state_size: int,
        action_size: int,
        learning_rate: float = 0.002,
        hidden_layers: Tuple[int, ...] = (64, 32),
        dropout_rate: float = 0.05
    ) -> "tf.keras.Model":
        """
        Create lightweight DQN architecture for fast routing decisions.
        
        Args:
            state_size: Size of input state vector
            action_size: Number of possible actions
            learning_rate: Learning rate for optimizer
            hidden_layers: Tuple of hidden layer sizes
            dropout_rate: Dropout rate for regularization
            
        Returns:
            Compiled Keras model
        """
        _ensure_tensorflow()
        
        model = Sequential(name="lightweight_dqn")
        
        # Smaller architecture for speed
        for i, layer_size in enumerate(hidden_layers):
            if i == 0:
                model.add(Dense(
                    layer_size,
                    input_dim=state_size,
                    activation='relu',
                    name=f'layer_{i}'
                ))
            else:
                model.add(Dense(
                    layer_size,
                    activation='relu',
                    name=f'layer_{i}'
                ))
            
            if dropout_rate > 0:
                model.add(Dropout(dropout_rate, name=f'dropout_{i}'))
        
        # Output layer
        model.add(Dense(
            action_size,
            activation='linear',
            name='output_layer'
        ))
        
        # Compile with higher learning rate for faster convergence
        model.compile(
            optimizer=Adam(learning_rate=learning_rate),
            loss=Huber(),
            metrics=['mae']
        )
        
        logger.info(f"Created lightweight DQN with {model.count_params()} parameters")
        return model


class DQNNetworkManager:
    """
    Manager for DQN neural networks with target network support.
    
    Handles creation, initialization, and management of both main Q-network
    and target Q-network for stable DQN training.
    """
    
    def __init__(
        self,
        state_size: int,
        action_size: int,
        architecture: str = "standard",
        learning_rate: float = 0.001,
        **kwargs
    ):
        """
        Initialize DQN network manager.
        
        Args:
            state_size: Size of input state vector
            action_size: Number of possible actions
            architecture: Architecture type ("standard", "deep", "lightweight")
            learning_rate: Learning rate for optimizer
            **kwargs: Additional arguments for network creation
        """
        self.state_size = state_size
        self.action_size = action_size
        self.architecture = architecture
        self.learning_rate = learning_rate
        self.network_kwargs = kwargs
        
        self.q_network = None
        self.target_q_network = None
        
        logger.info(f"Initialized DQN network manager with {architecture} architecture")
    
    def create_networks(self) -> Tuple["tf.keras.Model", "tf.keras.Model"]:
        """
        Create both main Q-network and target Q-network.
        
        Returns:
            Tuple of (q_network, target_q_network)
        """
        _ensure_tensorflow()
        
        # Select architecture factory method
        architecture_map = {
            "standard": QNetworkArchitecture.create_standard_dqn,
            "deep": QNetworkArchitecture.create_deep_dqn,
            "lightweight": QNetworkArchitecture.create_lightweight_dqn,
        }
        
        if self.architecture not in architecture_map:
            logger.warning(f"Unknown architecture '{self.architecture}', using 'standard'")
            self.architecture = "standard"
        
        create_network = architecture_map[self.architecture]
        
        # Create main Q-network
        self.q_network = create_network(
            state_size=self.state_size,
            action_size=self.action_size,
            learning_rate=self.learning_rate,
            **self.network_kwargs
        )
        
        # Create target Q-network with same architecture
        self.target_q_network = create_network(
            state_size=self.state_size,
            action_size=self.action_size,
            learning_rate=self.learning_rate,
            **self.network_kwargs
        )
        
        # Initialize target network with same weights as main network
        self.update_target_network()
        
        logger.info("Created Q-network and target Q-network")
        return self.q_network, self.target_q_network
    
    def update_target_network(self) -> None:
        """Update target network weights from main Q-network."""
        if self.q_network is None or self.target_q_network is None:
            logger.error("Networks not initialized, cannot update target network")
            return
        
        self.target_q_network.set_weights(self.q_network.get_weights())
        logger.debug("Updated target network weights")
    
    def soft_update_target_network(self, tau: float = 0.005) -> None:
        """
        Perform soft update of target network weights.
        
        Args:
            tau: Update rate (0 = no update, 1 = full update)
        """
        if self.q_network is None or self.target_q_network is None:
            logger.error("Networks not initialized, cannot update target network")
            return
        
        q_weights = self.q_network.get_weights()
        target_weights = self.target_q_network.get_weights()
        
        # Soft update: target = tau * q_network + (1 - tau) * target
        updated_weights = []
        for q_weight, target_weight in zip(q_weights, target_weights):
            updated_weight = tau * q_weight + (1 - tau) * target_weight
            updated_weights.append(updated_weight)
        
        self.target_q_network.set_weights(updated_weights)
        logger.debug(f"Soft updated target network with tau={tau}")
    
    def predict_q_values(self, state: np.ndarray) -> np.ndarray:
        """
        Predict Q-values for given state using main network.
        
        Args:
            state: State vector or batch of state vectors
            
        Returns:
            Q-values for each action
        """
        if self.q_network is None:
            raise RuntimeError("Q-network not initialized")
        
        if len(state.shape) == 1:
            state = state.reshape(1, -1)
        
        return self.q_network.predict(state)
    
    def predict_target_q_values(self, state: np.ndarray) -> np.ndarray:
        """
        Predict Q-values for given state using target network.
        
        Args:
            state: State vector or batch of state vectors
            
        Returns:
            Q-values for each action
        """
        if self.target_q_network is None:
            raise RuntimeError("Target Q-network not initialized")
        
        if len(state.shape) == 1:
            state = state.reshape(1, -1)
        
        return self.target_q_network.predict(state)
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        Get information about the neural networks.
        
        Returns:
            Dictionary with network information
        """
        info = {
            "architecture": self.architecture,
            "state_size": self.state_size,
            "action_size": self.action_size,
            "learning_rate": self.learning_rate,
            "networks_initialized": self.q_network is not None,
        }
        
        if self.q_network is not None:
            info.update({
                "total_parameters": self.q_network.count_params(),
                "trainable_parameters": sum([tf.size(w).numpy() for w in self.q_network.trainable_weights]),
                "layers": len(self.q_network.layers),
                "optimizer": self.q_network.optimizer.__class__.__name__,
                "loss_function": self.q_network.loss.name if hasattr(self.q_network.loss, 'name') else str(self.q_network.loss),
            })
        
        return info
    
    def save_networks(self, filepath: str) -> None:
        """
        Save both networks to disk.
        
        Args:
            filepath: Base path for saving (without extension)
        """
        if self.q_network is None or self.target_q_network is None:
            logger.error("Networks not initialized, cannot save")
            return
        
        try:
            self.q_network.save_weights(f"{filepath}_q_network.h5")
            self.target_q_network.save_weights(f"{filepath}_target_network.h5")
            logger.info(f"Saved networks to {filepath}_*.h5")
        except Exception as e:
            logger.error(f"Failed to save networks: {e}")
    
    def load_networks(self, filepath: str) -> bool:
        """
        Load both networks from disk.
        
        Args:
            filepath: Base path for loading (without extension)
            
        Returns:
            True if successful, False otherwise
        """
        if self.q_network is None or self.target_q_network is None:
            logger.error("Networks not initialized, cannot load")
            return False
        
        try:
            self.q_network.load_weights(f"{filepath}_q_network.h5")
            self.target_q_network.load_weights(f"{filepath}_target_network.h5")
            logger.info(f"Loaded networks from {filepath}_*.h5")
            return True
        except Exception as e:
            logger.error(f"Failed to load networks: {e}")
            return False


# Convenience function for easy network creation
def create_dqn_networks(
    state_size: int,
    action_size: int,
    architecture: str = "standard",
    learning_rate: float = 0.001,
    **kwargs
) -> Tuple["tf.keras.Model", "tf.keras.Model"]:
    """
    Convenience function to create DQN networks.
    
    Args:
        state_size: Size of input state vector
        action_size: Number of possible actions
        architecture: Architecture type ("standard", "deep", "lightweight")
        learning_rate: Learning rate for optimizer
        **kwargs: Additional arguments for network creation
        
    Returns:
        Tuple of (q_network, target_q_network)
    """
    manager = DQNNetworkManager(
        state_size=state_size,
        action_size=action_size,
        architecture=architecture,
        learning_rate=learning_rate,
        **kwargs
    )
    return manager.create_networks()
