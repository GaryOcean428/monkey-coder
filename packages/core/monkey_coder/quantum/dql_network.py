"""
Deep Q-Learning Network (DQL) for advanced routing decisions.

This module implements a neural network-based Q-learning system that learns
optimal routing strategies through experience replay and deep learning.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
import json
import logging
from pathlib import Path
from collections import deque
import random

logger = logging.getLogger(__name__)

class DQN(nn.Module):
    """Deep Q-Network for routing decisions."""
    
    def __init__(
        self,
        input_dim: int = 19,  # State vector dimension
        hidden_dims: List[int] = None,
        output_dim: int = 1980,  # Number of possible actions
        dropout_rate: float = 0.1
    ):
        """
        Initialize DQN architecture.
        
        Args:
            input_dim: Dimension of state vector
            hidden_dims: List of hidden layer dimensions
            output_dim: Number of possible actions
            dropout_rate: Dropout rate for regularization
        """
        super(DQN, self).__init__()
        
        if hidden_dims is None:
            hidden_dims = [256, 512, 256, 128]
        
        # Build network layers
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.BatchNorm1d(hidden_dim))
            layers.append(nn.Dropout(dropout_rate))
            prev_dim = hidden_dim
        
        # Output layer
        layers.append(nn.Linear(prev_dim, output_dim))
        
        self.network = nn.Sequential(*layers)
        
        # Dueling network architecture components
        self.value_stream = nn.Sequential(
            nn.Linear(hidden_dims[-1], 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )
        
        self.advantage_stream = nn.Sequential(
            nn.Linear(hidden_dims[-1], 128),
            nn.ReLU(),
            nn.Linear(128, output_dim)
        )
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize network weights using Xavier initialization."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the network.
        
        Args:
            x: State tensor
            
        Returns:
            Q-values for all actions
        """
        # Get features from main network
        features = x
        for layer in self.network[:-1]:  # All layers except the last
            features = layer(features)
        
        # Dueling architecture: V(s) + A(s,a) - mean(A(s,a))
        value = self.value_stream(features)
        advantage = self.advantage_stream(features)
        
        # Combine value and advantage (dueling DQN formula)
        q_values = value + (advantage - advantage.mean(dim=1, keepdim=True))
        
        return q_values

@dataclass
class Transition:
    """Represents a state transition for experience replay."""
    state: np.ndarray
    action: int
    reward: float
    next_state: Optional[np.ndarray]
    done: bool

class PrioritizedReplayBuffer:
    """Prioritized experience replay buffer for DQL."""
    
    def __init__(self, capacity: int = 100000, alpha: float = 0.6, beta: float = 0.4):
        """
        Initialize prioritized replay buffer.
        
        Args:
            capacity: Maximum buffer size
            alpha: Priority exponent (0 = uniform, 1 = full prioritization)
            beta: Importance sampling exponent
        """
        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta
        self.beta_increment = 0.00001
        
        self.buffer = deque(maxlen=capacity)
        self.priorities = deque(maxlen=capacity)
        self.position = 0
        self.max_priority = 1.0
    
    def add(self, transition: Transition, priority: Optional[float] = None):
        """Add a transition to the buffer with priority."""
        if priority is None:
            priority = self.max_priority
        
        self.buffer.append(transition)
        self.priorities.append(priority)
        
        # Update max priority
        self.max_priority = max(self.max_priority, priority)
    
    def sample(self, batch_size: int) -> Tuple[List[Transition], np.ndarray, np.ndarray]:
        """
        Sample a batch of transitions with importance sampling weights.
        
        Returns:
            Tuple of (transitions, weights, indices)
        """
        if len(self.buffer) < batch_size:
            batch_size = len(self.buffer)
        
        # Calculate sampling probabilities
        priorities = np.array(self.priorities, dtype=np.float32)
        probs = priorities ** self.alpha
        probs /= probs.sum()
        
        # Sample indices
        indices = np.random.choice(len(self.buffer), batch_size, p=probs)
        
        # Calculate importance sampling weights
        total = len(self.buffer)
        weights = (total * probs[indices]) ** (-self.beta)
        weights /= weights.max()  # Normalize
        
        # Get transitions
        transitions = [self.buffer[idx] for idx in indices]
        
        # Increment beta
        self.beta = min(1.0, self.beta + self.beta_increment)
        
        return transitions, weights, indices
    
    def update_priorities(self, indices: np.ndarray, priorities: np.ndarray):
        """Update priorities for sampled transitions."""
        for idx, priority in zip(indices, priorities):
            self.priorities[idx] = priority
            self.max_priority = max(self.max_priority, priority)
    
    def __len__(self):
        return len(self.buffer)

class DQLRouter:
    """Deep Q-Learning based routing system."""
    
    def __init__(
        self,
        state_dim: int = 19,
        action_dim: int = 1980,
        learning_rate: float = 0.0001,
        gamma: float = 0.99,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
        target_update_freq: int = 1000,
        save_path: Optional[str] = None,
        device: Optional[str] = None
    ):
        """
        Initialize DQL router.
        
        Args:
            state_dim: Dimension of state vector
            action_dim: Number of possible actions
            learning_rate: Learning rate for optimizer
            gamma: Discount factor
            epsilon: Initial exploration rate
            epsilon_decay: Epsilon decay rate
            epsilon_min: Minimum epsilon value
            target_update_freq: Frequency of target network updates
            save_path: Path to save/load model
            device: Device to run on (cuda/cpu)
        """
        # Set device
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        logger.info(f"DQL Router using device: {self.device}")
        
        # Initialize networks
        self.q_network = DQN(state_dim, output_dim=action_dim).to(self.device)
        self.target_network = DQN(state_dim, output_dim=action_dim).to(self.device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()
        
        # Optimizer
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        self.scheduler = optim.lr_scheduler.StepLR(self.optimizer, step_size=10000, gamma=0.9)
        
        # Hyperparameters
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.target_update_freq = target_update_freq
        
        # Experience replay
        self.replay_buffer = PrioritizedReplayBuffer()
        self.batch_size = 32
        
        # Training metrics
        self.training_step = 0
        self.episode = 0
        self.losses = []
        self.rewards = []
        
        # Save/load path
        self.save_path = Path(save_path) if save_path else Path("data/dql/model.pth")
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing model if available
        self.load_model()
    
    def select_action(self, state: np.ndarray, explore: bool = True) -> int:
        """
        Select action using epsilon-greedy strategy with neural network.
        
        Args:
            state: State vector
            explore: Whether to use exploration
            
        Returns:
            Action index
        """
        # Epsilon-greedy exploration
        if explore and random.random() < self.epsilon:
            return random.randint(0, self.q_network.advantage_stream[-1].out_features - 1)
        
        # Exploitation: use network to select action
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.q_network(state_tensor)
            action = q_values.argmax(dim=1).item()
        
        return action
    
    def train_step(self):
        """Perform one training step."""
        if len(self.replay_buffer) < self.batch_size:
            return
        
        # Sample batch with prioritized replay
        transitions, weights, indices = self.replay_buffer.sample(self.batch_size)
        
        # Convert to tensors
        states = torch.FloatTensor([t.state for t in transitions]).to(self.device)
        actions = torch.LongTensor([t.action for t in transitions]).to(self.device)
        rewards = torch.FloatTensor([t.reward for t in transitions]).to(self.device)
        next_states = torch.FloatTensor([
            t.next_state if t.next_state is not None else np.zeros_like(t.state)
            for t in transitions
        ]).to(self.device)
        dones = torch.FloatTensor([t.done for t in transitions]).to(self.device)
        weights = torch.FloatTensor(weights).to(self.device)
        
        # Current Q values
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        
        # Double DQN: use online network to select action, target network to evaluate
        with torch.no_grad():
            next_actions = self.q_network(next_states).argmax(dim=1)
            next_q_values = self.target_network(next_states).gather(1, next_actions.unsqueeze(1))
            target_q_values = rewards.unsqueeze(1) + (1 - dones.unsqueeze(1)) * self.gamma * next_q_values
        
        # Calculate TD error for prioritized replay
        td_errors = torch.abs(current_q_values - target_q_values).detach().cpu().numpy()
        
        # Update priorities
        self.replay_buffer.update_priorities(indices, td_errors.squeeze() + 1e-6)
        
        # Calculate weighted loss
        loss = (weights.unsqueeze(1) * F.mse_loss(current_q_values, target_q_values, reduction='none')).mean()
        
        # Backpropagation
        self.optimizer.zero_grad()
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), max_norm=10)
        
        self.optimizer.step()
        self.scheduler.step()
        
        # Update target network
        if self.training_step % self.target_update_freq == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())
            logger.info(f"Target network updated at step {self.training_step}")
        
        # Update epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        # Track metrics
        self.losses.append(loss.item())
        self.training_step += 1
    
    def add_experience(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: Optional[np.ndarray],
        done: bool
    ):
        """Add experience to replay buffer."""
        transition = Transition(state, action, reward, next_state, done)
        
        # Calculate initial priority based on expected TD error
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            if next_state is not None:
                next_state_tensor = torch.FloatTensor(next_state).unsqueeze(0).to(self.device)
                current_q = self.q_network(state_tensor)[0, action].item()
                next_q = self.target_network(next_state_tensor).max(dim=1)[0].item()
                td_error = abs(reward + self.gamma * next_q * (1 - done) - current_q)
            else:
                td_error = abs(reward)
        
        priority = td_error + 1e-6
        self.replay_buffer.add(transition, priority)
    
    def save_model(self):
        """Save model and training state."""
        try:
            checkpoint = {
                'q_network_state': self.q_network.state_dict(),
                'target_network_state': self.target_network.state_dict(),
                'optimizer_state': self.optimizer.state_dict(),
                'scheduler_state': self.scheduler.state_dict(),
                'epsilon': self.epsilon,
                'training_step': self.training_step,
                'episode': self.episode,
                'losses': self.losses[-1000:],  # Keep last 1000 losses
                'rewards': self.rewards[-1000:]  # Keep last 1000 rewards
            }
            
            torch.save(checkpoint, self.save_path)
            logger.info(f"Model saved to {self.save_path}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def load_model(self):
        """Load model and training state."""
        if not self.save_path.exists():
            logger.info("No saved model found, starting fresh")
            return
        
        try:
            checkpoint = torch.load(self.save_path, map_location=self.device)
            
            self.q_network.load_state_dict(checkpoint['q_network_state'])
            self.target_network.load_state_dict(checkpoint['target_network_state'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state'])
            self.scheduler.load_state_dict(checkpoint['scheduler_state'])
            self.epsilon = checkpoint.get('epsilon', self.epsilon)
            self.training_step = checkpoint.get('training_step', 0)
            self.episode = checkpoint.get('episode', 0)
            self.losses = checkpoint.get('losses', [])
            self.rewards = checkpoint.get('rewards', [])
            
            logger.info(f"Model loaded from {self.save_path}")
            logger.info(f"Resumed at step {self.training_step}, epsilon={self.epsilon:.3f}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get training statistics."""
        return {
            'training_step': self.training_step,
            'episode': self.episode,
            'epsilon': self.epsilon,
            'buffer_size': len(self.replay_buffer),
            'avg_loss': np.mean(self.losses[-100:]) if self.losses else 0,
            'avg_reward': np.mean(self.rewards[-100:]) if self.rewards else 0,
            'learning_rate': self.optimizer.param_groups[0]['lr'],
            'device': str(self.device)
        }