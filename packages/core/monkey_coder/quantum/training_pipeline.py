"""
Training Pipeline for DQN Routing Agent

This module implements the training pipeline that coordinates the DQN agent,
experience replay buffer, and neural networks to learn optimal routing decisions.
Implements batch processing, epsilon-greedy exploration, and reward calculation.
"""

import logging
import numpy as np
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .dqn_agent import DQNRoutingAgent, RoutingState, RoutingAction
from .experience_buffer import ExperienceReplayBuffer, PrioritizedExperienceBuffer, Experience
from .neural_network import create_dqn_network, DQNNetwork
from ..models import ProviderType

logger = logging.getLogger(__name__)


class TrainingMode(Enum):
    """Training mode configurations."""
    STANDARD = "standard"  # Standard experience replay
    PRIORITIZED = "prioritized"  # Prioritized experience replay
    ONLINE = "online"  # Online learning without experience buffer


@dataclass
class TrainingConfig:
    """Configuration for training pipeline."""

    # Training hyperparameters
    batch_size: int = 32
    learning_rate: float = 0.001
    discount_factor: float = 0.99

    # Exploration parameters
    initial_epsilon: float = 1.0
    min_epsilon: float = 0.01
    epsilon_decay: float = 0.995

    # Target network updates
    target_update_frequency: int = 100  # Steps
    soft_update_tau: float = 0.01  # For soft updates

    # Experience replay
    buffer_size: int = 10000
    min_buffer_size: int = 1000
    training_mode: TrainingMode = TrainingMode.STANDARD

    # Training schedule
    max_episodes: int = 1000
    max_steps_per_episode: int = 100
    training_frequency: int = 4  # Train every N steps

    # Performance tracking
    evaluation_frequency: int = 50  # Episodes
    performance_window: int = 100  # Episode window for averaging

    # Early stopping
    target_performance: float = 0.9  # Success rate target
    patience: int = 100  # Episodes without improvement


@dataclass
class TrainingMetrics:
    """Metrics collected during training."""

    episode: int = 0
    step: int = 0

    # Performance metrics
    episode_reward: float = 0.0
    episode_success: bool = False
    routing_accuracy: float = 0.0

    # Training metrics
    loss: float = 0.0
    epsilon: float = 1.0
    q_value_mean: float = 0.0

    # Timing metrics
    episode_time: float = 0.0
    training_time: float = 0.0

    # Buffer metrics
    buffer_size: int = 0
    buffer_utilization: float = 0.0


class RoutingEnvironmentSimulator:
    """
    Simulates a routing environment for training the DQN agent.

    This provides synthetic routing scenarios for the agent to learn from,
    including success/failure feedback and performance metrics.
    """

    def __init__(self, state_size: int = 21, action_size: int = 12):
        """Initialize the routing environment simulator."""
        self.state_size = state_size
        self.action_size = action_size

        # Environment state
        self.current_state = None
        self.step_count = 0
        self.episode_success = False

        # Provider performance profiles (simulated)
        self.provider_performance = {
            ProviderType.OPENAI: {"base_success": 0.85, "latency": 1.2, "cost": 0.03},
            ProviderType.ANTHROPIC: {"base_success": 0.82, "latency": 1.5, "cost": 0.04},
            ProviderType.GOOGLE: {"base_success": 0.78, "latency": 0.8, "cost": 0.02},
            ProviderType.GROQ: {"base_success": 0.75, "latency": 0.3, "cost": 0.01},
        }

        # Task complexity profiles
        self.task_profiles = {
            "simple": {"complexity": 0.2, "optimal_provider": ProviderType.GROQ},
            "medium": {"complexity": 0.5, "optimal_provider": ProviderType.GOOGLE},
            "complex": {"complexity": 0.8, "optimal_provider": ProviderType.OPENAI},
            "creative": {"complexity": 0.9, "optimal_provider": ProviderType.ANTHROPIC},
        }

    def reset(self) -> RoutingState:
        """Reset environment and return initial state."""
        self.step_count = 0
        self.episode_success = False

        # Generate random task scenario
        task_type = np.random.choice(list(self.task_profiles.keys()))
        task_profile = self.task_profiles[task_type]

        # Create routing state
        self.current_state = RoutingState(
            task_complexity=task_profile["complexity"] + np.random.normal(0, 0.1),
            context_type=task_type,
            provider_availability={
                "openai": np.random.rand() > 0.05,  # 95% uptime
                "anthropic": np.random.rand() > 0.08,  # 92% uptime
                "google": np.random.rand() > 0.03,  # 97% uptime
                "groq": np.random.rand() > 0.02,  # 98% uptime
            },
            historical_performance={
                provider.value: perf["base_success"] + np.random.normal(0, 0.05)
                for provider, perf in self.provider_performance.items()
            },
            resource_constraints={
                "max_cost": np.random.uniform(0.01, 0.10),
                "max_latency": np.random.uniform(0.5, 3.0),
                "quality_threshold": np.random.uniform(0.7, 0.95),
            },
            user_preferences={
                "cost_weight": np.random.rand(),
                "speed_weight": np.random.rand(),
                "quality_weight": np.random.rand(),
            }
        )

        return self.current_state

    def step(self, action: RoutingAction) -> Tuple[RoutingState, float, bool, Dict]:
        """
        Execute action and return next state, reward, done, info.

        Args:
            action: Routing action taken by agent

        Returns:
            Tuple of (next_state, reward, done, info)
        """
        self.step_count += 1

        # Calculate reward based on routing decision
        reward = self._calculate_reward(action)

        # Determine if episode is done
        done = bool(self.step_count >= 10 or reward > 0.8)  # Convert numpy bool to Python bool

        if reward > 0.8:
            self.episode_success = True

        # Generate next state (small perturbation of current state)
        next_state = self._generate_next_state(action)

        provider_key = action.provider.value if hasattr(action.provider, "value") else str(action.provider)

        info = {
            "step_count": self.step_count,
            "episode_success": self.episode_success,
            "action_provider": provider_key,
            "action_model": action.model,
            "reward_components": self._get_reward_components(action),
        }

        self.current_state = next_state
        return next_state, reward, done, info

    def _calculate_reward(self, action: RoutingAction) -> float:
        """Calculate reward for the given action."""
        if self.current_state is None:
            return 0.0

        # Get provider performance
        provider_perf = self.provider_performance.get(action.provider, {})
        base_success = provider_perf.get("base_success", 0.5)
        latency = provider_perf.get("latency", 1.0)
        cost = provider_perf.get("cost", 0.02)

        # Task complexity matching
        task_complexity = self.current_state.task_complexity
        complexity_match = 1.0 - abs(task_complexity - base_success)

        # Resource constraint satisfaction
        constraints = self.current_state.resource_constraints
        cost_satisfaction = 1.0 if cost <= constraints.get("max_cost", 0.1) else 0.5
        latency_satisfaction = 1.0 if latency <= constraints.get("max_latency", 2.0) else 0.7

        # Provider availability
        provider_key = action.provider.value if hasattr(action.provider, 'value') else str(action.provider)
        provider_available = self.current_state.provider_availability.get(
            provider_key, True
        )
        availability_penalty = 1.0 if provider_available else 0.1

        # Strategy alignment
        strategy_bonus = self._get_strategy_bonus(action)

        # Combine components
        reward = (
            0.4 * complexity_match +
            0.2 * cost_satisfaction +
            0.2 * latency_satisfaction +
            0.1 * strategy_bonus +
            0.1 * availability_penalty
        )

        # Add noise to make learning more realistic
        reward += np.random.normal(0, 0.05)

        return np.clip(reward, 0.0, 1.0)

    def _get_strategy_bonus(self, action: RoutingAction) -> float:
        """Calculate bonus based on strategy alignment."""
        strategy_bonuses = {
            "performance": 0.8 if action.provider in [ProviderType.OPENAI, ProviderType.ANTHROPIC] else 0.5,
            "cost_efficient": 0.8 if action.provider in [ProviderType.GROQ, ProviderType.GOOGLE] else 0.4,
            "balanced": 0.7,  # Always decent bonus for balanced strategy
        }

        return strategy_bonuses.get(action.strategy, 0.5)

    def _generate_next_state(self, action: RoutingAction) -> RoutingState:
        """Generate next state based on current state and action."""
        if self.current_state is None:
            return self.reset()

        # Small perturbations to create state transitions
        new_state = RoutingState(
            task_complexity=np.clip(
                self.current_state.task_complexity + np.random.normal(0, 0.02),
                0.0, 1.0
            ),
            context_type=self.current_state.context_type,
            provider_availability={
                k: v and (np.random.rand() > 0.01)  # Small chance of provider going down
                for k, v in self.current_state.provider_availability.items()
            },
            historical_performance={
                k: np.clip(v + np.random.normal(0, 0.01), 0.0, 1.0)
                for k, v in self.current_state.historical_performance.items()
            },
            resource_constraints=self.current_state.resource_constraints,
            user_preferences=self.current_state.user_preferences
        )

        return new_state

    def _get_reward_components(self, action: RoutingAction) -> Dict[str, float]:
        """Get detailed reward components for analysis."""
        if self.current_state is None:
            return {}

        provider_perf = self.provider_performance.get(action.provider, {})

        return {
            "complexity_match": 1.0 - abs(
                self.current_state.task_complexity - provider_perf.get("base_success", 0.5)
            ),
            "cost_efficiency": provider_perf.get("cost", 0.02),
            "latency": provider_perf.get("latency", 1.0),
            "availability": self.current_state.provider_availability.get(
                action.provider.value, True
            ),
        }


class DQNTrainingPipeline:
    """
    Complete training pipeline for the DQN routing agent.

    Coordinates the DQN agent, experience buffer, neural networks, and environment
    to implement a complete reinforcement learning training loop.
    """

    def __init__(self, config: TrainingConfig):
        """Initialize the training pipeline."""
        self.config = config

        # Initialize components
        self.agent = DQNRoutingAgent(
            state_size=21,  # From RoutingState.to_vector()
            action_size=12,  # Number of provider/model combinations
            learning_rate=config.learning_rate,
            exploration_rate=config.initial_epsilon,
            discount_factor=config.discount_factor
        )

        # Ensure agent has a working Q-network (numpy fallback)
        from .neural_network import create_dqn_network
        self.agent.q_network = create_dqn_network(
            state_size=21,
            action_size=12,
            learning_rate=config.learning_rate,
            force_numpy=True
        )

        # Initialize experience buffer
        if config.training_mode == TrainingMode.PRIORITIZED:
            self.experience_buffer = PrioritizedExperienceBuffer(
                capacity=config.buffer_size,
                min_size=config.min_buffer_size
            )
        else:
            self.experience_buffer = ExperienceReplayBuffer(
                capacity=config.buffer_size,
                min_size=config.min_buffer_size
            )

        # Initialize environment
        self.environment = RoutingEnvironmentSimulator()

        # Training state
        self.current_episode = 0
        self.current_step = 0
        self.training_metrics = []
        self.best_performance = 0.0
        self.episodes_without_improvement = 0

        # Performance tracking
        self.episode_rewards = []
        self.episode_successes = []
        self.training_losses = []

        logger.info(f"Initialized DQN training pipeline with {config.training_mode.value} mode")

    def train(self) -> List[TrainingMetrics]:
        """
        Run the complete training process.

        Returns:
            List of training metrics collected during training
        """
        logger.info(f"Starting DQN training for {self.config.max_episodes} episodes")

        start_time = time.time()

        for episode in range(self.config.max_episodes):
            episode_metrics = self._run_episode(episode)
            self.training_metrics.append(episode_metrics)

            # Update exploration rate
            self._update_epsilon()

            # Update target network periodically
            if self.current_step % self.config.target_update_frequency == 0:
                self.agent.q_network.update_target_network(tau=self.config.soft_update_tau)

            # Evaluate performance periodically
            if episode % self.config.evaluation_frequency == 0:
                self._evaluate_performance(episode)

            # Check for early stopping
            if self._should_stop_early():
                logger.info(f"Early stopping at episode {episode}")
                break

            # Log progress
            if episode % 50 == 0:
                recent_reward = np.mean(self.episode_rewards[-50:]) if self.episode_rewards else 0
                recent_success = np.mean(self.episode_successes[-50:]) if self.episode_successes else 0
                logger.info(
                    f"Episode {episode}: avg_reward={recent_reward:.3f}, "
                    f"success_rate={recent_success:.3f}, epsilon={self.agent.exploration_rate:.3f}"
                )

        total_time = time.time() - start_time
        logger.info(f"Training completed in {total_time:.2f} seconds")

        return self.training_metrics

    def _run_episode(self, episode: int) -> TrainingMetrics:
        """Run a single training episode."""
        episode_start_time = time.time()

        # Reset environment
        state = self.environment.reset()

        episode_reward = 0.0
        episode_success = False
        training_time = 0.0
        step_count = 0

        for step in range(self.config.max_steps_per_episode):
            step_start_time = time.time()

            # Agent selects action
            action = self.agent.act(state)

            # Environment executes action
            next_state, reward, done, info = self.environment.step(action)

            # Store experience
            experience = Experience(
                state=state.to_vector(),
                action=action.to_action_index(),
                reward=reward,
                next_state=next_state.to_vector(),
                done=done,
                timestamp=time.time()
            )

            self.experience_buffer.add(experience)

            # Train agent if enough experiences
            loss = 0.0
            if (len(self.experience_buffer) >= self.config.min_buffer_size and
                self.current_step % self.config.training_frequency == 0):

                train_start = time.time()
                loss = self._train_agent()
                training_time += time.time() - train_start

            # Update state and metrics
            state = next_state
            episode_reward += reward
            step_count += 1
            self.current_step += 1

            if done:
                episode_success = info.get("episode_success", False)
                break

        # Update tracking
        self.episode_rewards.append(episode_reward)
        self.episode_successes.append(episode_success)

        episode_time = time.time() - episode_start_time

        # Create metrics
        metrics = TrainingMetrics(
            episode=episode,
            step=self.current_step,
            episode_reward=episode_reward,
            episode_success=episode_success,
            routing_accuracy=self._calculate_routing_accuracy(),
            loss=self.training_losses[-1] if self.training_losses else 0.0,
            epsilon=self.agent.exploration_rate,
            q_value_mean=self._calculate_mean_q_value(state),
            episode_time=episode_time,
            training_time=training_time,
            buffer_size=len(self.experience_buffer),
            buffer_utilization=len(self.experience_buffer) / self.config.buffer_size
        )

        return metrics

    def _train_agent(self) -> float:
        """Train the agent using experience replay."""
        # Sample batch from experience buffer
        if isinstance(self.experience_buffer, PrioritizedExperienceBuffer):
            experiences, indices, weights = self.experience_buffer.sample(self.config.batch_size)
        else:
            experiences = self.experience_buffer.sample(self.config.batch_size)
            indices = None
            weights = None

        # Convert to arrays
        states, actions, rewards, next_states, dones = self.experience_buffer.get_batch_arrays(experiences)

        # Compute target Q-values
        next_q_values = self.agent.q_network.predict_target(next_states)
        max_next_q = np.max(next_q_values, axis=1)

        # Compute targets
        targets = self.agent.q_network.predict(states).copy()

        for i in range(len(experiences)):
            if dones[i]:
                targets[i, actions[i]] = rewards[i]
            else:
                targets[i, actions[i]] = rewards[i] + self.config.discount_factor * max_next_q[i]

        # Apply importance sampling weights if using prioritized replay
        if weights is not None:
            # Scale targets by importance weights
            for i in range(len(experiences)):
                targets[i] *= weights[i]

        # Train network
        loss = self.agent.q_network.train(states, targets)
        self.training_losses.append(loss)

        # Update priorities if using prioritized replay
        if isinstance(self.experience_buffer, PrioritizedExperienceBuffer) and indices is not None:
            # Calculate TD errors as new priorities
            current_q_values = self.agent.q_network.predict(states)
            td_errors = np.abs(targets - current_q_values)
            td_errors_max = np.max(td_errors, axis=1)

            self.experience_buffer.update_priorities(indices, td_errors_max)

        return loss

    def _update_epsilon(self):
        """Update exploration rate using epsilon decay."""
        if self.agent.exploration_rate > self.config.min_epsilon:
            self.agent.exploration_rate *= self.config.epsilon_decay
            self.agent.exploration_rate = max(self.agent.exploration_rate, self.config.min_epsilon)

    def _calculate_routing_accuracy(self) -> float:
        """Calculate routing accuracy over recent episodes."""
        if not self.episode_successes:
            return 0.0

        window_size = min(self.config.performance_window, len(self.episode_successes))
        recent_successes = self.episode_successes[-window_size:]

        return np.mean(recent_successes)

    def _calculate_mean_q_value(self, state: RoutingState) -> float:
        """Calculate mean Q-value for the current state."""
        state_vector = state.to_vector().reshape(1, -1)
        q_values = self.agent.q_network.predict(state_vector)
        return np.mean(q_values)

    def _evaluate_performance(self, episode: int):
        """Evaluate current performance and update best performance."""
        current_accuracy = self._calculate_routing_accuracy()

        if current_accuracy > self.best_performance:
            self.best_performance = current_accuracy
            self.episodes_without_improvement = 0
            logger.info(f"New best performance: {current_accuracy:.3f} at episode {episode}")
        else:
            self.episodes_without_improvement += self.config.evaluation_frequency

    def _should_stop_early(self) -> bool:
        """Check if training should stop early."""
        # Check if target performance reached
        current_accuracy = self._calculate_routing_accuracy()
        if current_accuracy >= self.config.target_performance:
            return True

        # Check patience for improvement
        if self.episodes_without_improvement >= self.config.patience:
            return True

        return False

    def save_checkpoint(self, filepath: str) -> bool:
        """Save training checkpoint."""
        try:
            checkpoint_data = {
                "episode": self.current_episode,
                "step": self.current_step,
                "best_performance": self.best_performance,
                "episodes_without_improvement": self.episodes_without_improvement,
                "config": {
                    **self.config.__dict__,
                    "training_mode": self.config.training_mode.value  # Convert enum to string
                },
                "episode_rewards": self.episode_rewards,
                "episode_successes": self.episode_successes,
                "training_losses": self.training_losses
            }

            # Save agent
            agent_path = f"{filepath}_agent"
            self.agent.save_model(agent_path)

            # Save buffer
            buffer_path = f"{filepath}_buffer"
            self.experience_buffer.save_buffer(buffer_path)

            # Save checkpoint data
            import json
            with open(f"{filepath}.json", 'w') as f:
                json.dump(checkpoint_data, f)

            logger.info(f"Checkpoint saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            return False

    def load_checkpoint(self, filepath: str) -> bool:
        """Load training checkpoint."""
        try:
            # Load checkpoint data
            import json
            with open(f"{filepath}.json", 'r') as f:
                checkpoint_data = json.load(f)

            # Restore training state
            self.current_episode = checkpoint_data["episode"]
            self.current_step = checkpoint_data["step"]
            self.best_performance = checkpoint_data["best_performance"]
            self.episodes_without_improvement = checkpoint_data["episodes_without_improvement"]
            self.episode_rewards = checkpoint_data["episode_rewards"]
            self.episode_successes = checkpoint_data["episode_successes"]
            self.training_losses = checkpoint_data["training_losses"]

            # Load agent
            agent_path = f"{filepath}_agent"
            self.agent.load_model(agent_path)

            # Load buffer
            buffer_path = f"{filepath}_buffer"
            self.experience_buffer.load_buffer(buffer_path)

            logger.info(f"Checkpoint loaded from {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return False

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of training performance."""
        if not self.training_metrics:
            return {}

        recent_window = min(100, len(self.training_metrics))
        recent_metrics = self.training_metrics[-recent_window:]

        return {
            "total_episodes": len(self.training_metrics),
            "total_steps": self.current_step,
            "best_performance": self.best_performance,
            "final_epsilon": self.agent.exploration_rate,
            "recent_avg_reward": np.mean([m.episode_reward for m in recent_metrics]),
            "recent_success_rate": np.mean([m.episode_success for m in recent_metrics]),
            "recent_avg_loss": np.mean([m.loss for m in recent_metrics if m.loss > 0]),
            "buffer_utilization": len(self.experience_buffer) / self.config.buffer_size,
            "training_efficiency": np.mean([m.training_time for m in recent_metrics])
        }
