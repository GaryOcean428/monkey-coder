"""Training Pipeline for DQN Agent.

This module implements the training pipeline for the Deep Q-Network agent,
including batch processing, epsilon-greedy exploration, and reward calculation
based on routing success.
"""

import logging
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from monkey_coder.quantum.dqn_agent import DQNAgent
from monkey_coder.quantum.experience_buffer import ExperienceBuffer

logger = logging.getLogger(__name__)


@dataclass
class TrainingConfig:
    """Configuration for training pipeline."""

    batch_size: int = 32
    epsilon: float = 1.0
    epsilon_min: float = 0.01
    epsilon_decay: float = 0.995
    learning_rate: float = 0.001
    discount_factor: float = 0.95
    target_update_frequency: int = 100
    save_frequency: int = 500
    max_episodes: int = 1000


class RoutingRewardCalculator:
    """Calculate rewards for routing decisions."""

    @staticmethod
    def calculate_reward(
        success: bool,
        response_time: float,
        cost: float,
        quality_score: float,
        target_time: float = 0.1
    ) -> float:
        """Calculate reward based on routing performance.

        Args:
            success: Whether the routing was successful
            response_time: Time taken for routing decision (seconds)
            cost: Cost of the routing decision
            quality_score: Quality score of the result (0-1)
            target_time: Target response time in seconds

        Returns:
            Calculated reward value
        """
        if not success:
            return -10.0  # Heavy penalty for failure

        # Base reward for success
        reward = 5.0

        # Time bonus/penalty
        if response_time < target_time:
            time_bonus = (target_time - response_time) / target_time * 2.0
            reward += time_bonus
        else:
            time_penalty = min((response_time - target_time) / target_time * 3.0, 5.0)
            reward -= time_penalty

        # Quality bonus
        quality_bonus = quality_score * 3.0
        reward += quality_bonus

        # Cost penalty (normalized)
        cost_penalty = min(cost * 0.5, 2.0)
        reward -= cost_penalty

        return np.clip(reward, -10.0, 10.0)


class TrainingPipeline:
    """Training pipeline for DQN agent."""

    def __init__(
        self,
        agent: DQNAgent,
        experience_buffer: ExperienceBuffer,
        config: Optional[TrainingConfig] = None
    ):
        """Initialize training pipeline.

        Args:
            agent: DQN agent to train
            experience_buffer: Experience replay buffer
            config: Training configuration
        """
        self.agent = agent
        self.experience_buffer = experience_buffer
        self.config = config or TrainingConfig()
        self.reward_calculator = RoutingRewardCalculator()

        self.epsilon = self.config.epsilon
        self.training_step = 0
        self.episode = 0

        # Training metrics
        self.episode_rewards: List[float] = []
        self.episode_losses: List[float] = []
        self.success_rate_history: List[float] = []

    def select_action_epsilon_greedy(
        self,
        state: np.ndarray,
        available_actions: List[int]
    ) -> int:
        """Select action using epsilon-greedy strategy.

        Args:
            state: Current state
            available_actions: List of available action indices

        Returns:
            Selected action index
        """
        if random.random() < self.epsilon:
            # Exploration: random action
            return random.choice(available_actions)
        else:
            # Exploitation: best action from Q-network
            q_values = self.agent.predict(state)

            # Mask unavailable actions
            masked_q_values = np.full_like(q_values, -np.inf)
            for action in available_actions:
                masked_q_values[action] = q_values[action]

            return int(np.argmax(masked_q_values))

    def train_batch(self) -> Optional[float]:
        """Train on a batch of experiences.

        Returns:
            Average loss for the batch, or None if buffer too small
        """
        if len(self.experience_buffer) < self.config.batch_size:
            return None

        # Sample batch from experience buffer
        batch = self.experience_buffer.sample(self.config.batch_size)

        states = np.array([exp['state'] for exp in batch])
        actions = np.array([exp['action'] for exp in batch])
        rewards = np.array([exp['reward'] for exp in batch])
        next_states = np.array([exp['next_state'] for exp in batch])
        dones = np.array([exp['done'] for exp in batch])

        # Calculate target Q-values
        current_q_values = self.agent.predict_batch(states)
        next_q_values = self.agent.predict_batch(next_states)

        target_q_values = current_q_values.copy()

        for i in range(self.config.batch_size):
            if dones[i]:
                target_q_values[i][actions[i]] = rewards[i]
            else:
                target_q_values[i][actions[i]] = (
                    rewards[i] +
                    self.config.discount_factor * np.max(next_q_values[i])
                )

        # Train the agent
        loss = self.agent.train_on_batch(states, target_q_values)

        # Update target network periodically
        self.training_step += 1
        if self.training_step % self.config.target_update_frequency == 0:
            self.agent.update_target_network()

        return loss

    def decay_epsilon(self):
        """Decay epsilon for exploration-exploitation balance."""
        self.epsilon = max(
            self.config.epsilon_min,
            self.epsilon * self.config.epsilon_decay
        )

    def run_episode(
        self,
        initial_state: np.ndarray,
        environment_step_func,
        max_steps: int = 100
    ) -> Dict[str, Any]:
        """Run a single training episode.

        Args:
            initial_state: Initial state for the episode
            environment_step_func: Function to step through environment
            max_steps: Maximum steps per episode

        Returns:
            Episode statistics
        """
        state = initial_state
        episode_reward = 0.0
        episode_losses = []
        steps = 0
        successes = 0

        for step in range(max_steps):
            # Select action
            available_actions = environment_step_func.get_available_actions(state)
            action = self.select_action_epsilon_greedy(state, available_actions)

            # Execute action in environment
            next_state, reward, done, info = environment_step_func(state, action)

            # Store experience
            self.experience_buffer.add({
                'state': state,
                'action': action,
                'reward': reward,
                'next_state': next_state,
                'done': done
            })

            # Train on batch
            loss = self.train_batch()
            if loss is not None:
                episode_losses.append(loss)

            # Update metrics
            episode_reward += reward
            if info.get('success', False):
                successes += 1

            state = next_state
            steps += 1

            if done:
                break

        # Decay epsilon
        self.decay_epsilon()

        # Update episode counter
        self.episode += 1

        # Save model periodically
        if self.episode % self.config.save_frequency == 0:
            self.agent.save_model(f"dqn_model_episode_{self.episode}.h5")

        # Calculate statistics
        avg_loss = np.mean(episode_losses) if episode_losses else 0.0
        success_rate = successes / steps if steps > 0 else 0.0

        # Store metrics
        self.episode_rewards.append(episode_reward)
        self.episode_losses.append(avg_loss)
        self.success_rate_history.append(success_rate)

        return {
            'episode': self.episode,
            'reward': episode_reward,
            'avg_loss': avg_loss,
            'steps': steps,
            'success_rate': success_rate,
            'epsilon': self.epsilon
        }

    def train(
        self,
        environment_func,
        episodes: Optional[int] = None
    ) -> Dict[str, Any]:
        """Run full training loop.

        Args:
            environment_func: Function to create environment
            episodes: Number of episodes to train (overrides config)

        Returns:
            Training statistics
        """
        episodes = episodes or self.config.max_episodes

        logger.info(f"Starting training for {episodes} episodes")

        for episode in range(episodes):
            # Create environment for this episode
            env = environment_func()
            initial_state = env.reset()

            # Run episode
            stats = self.run_episode(
                initial_state,
                env.step,
                max_steps=100
            )

            # Log progress
            if episode % 10 == 0:
                logger.info(
                    f"Episode {episode}: "
                    f"Reward={stats['reward']:.2f}, "
                    f"Loss={stats['avg_loss']:.4f}, "
                    f"Success={stats['success_rate']:.2%}, "
                    f"Epsilon={stats['epsilon']:.3f}"
                )

            # Check for convergence
            if self.is_converged():
                logger.info(f"Training converged at episode {episode}")
                break

        return self.get_training_summary()

    def is_converged(self, window: int = 100, threshold: float = 0.95) -> bool:
        """Check if training has converged.

        Args:
            window: Window size for checking convergence
            threshold: Success rate threshold for convergence

        Returns:
            True if converged, False otherwise
        """
        if len(self.success_rate_history) < window:
            return False

        recent_success_rate = np.mean(self.success_rate_history[-window:])
        return recent_success_rate >= threshold

    def get_training_summary(self) -> Dict[str, Any]:
        """Get summary of training results.

        Returns:
            Training summary statistics
        """
        return {
            'total_episodes': self.episode,
            'final_epsilon': self.epsilon,
            'avg_reward': np.mean(self.episode_rewards[-100:]) if self.episode_rewards else 0.0,
            'avg_loss': np.mean(self.episode_losses[-100:]) if self.episode_losses else 0.0,
            'final_success_rate': np.mean(self.success_rate_history[-100:]) if self.success_rate_history else 0.0,
            'converged': self.is_converged(),
            'training_steps': self.training_step
        }
