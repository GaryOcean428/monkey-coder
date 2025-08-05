"""
Experience Replay Buffer for DQN Agent

This module implements an experience replay buffer with FIFO management,
automatic cleanup, and support for (state, action, reward, next_state, done) tuples.
Following proven patterns from monkey1 and adapted for Monkey Coder's quantum routing.
"""

import logging
import random
from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Experience:
    """
    Represents a single experience tuple for reinforcement learning.

    Attributes:
        state: The state vector when the action was taken
        action: The action index that was taken
        reward: The reward received after taking the action
        next_state: The resulting state vector after taking the action
        done: Whether the episode ended after this action
        timestamp: When this experience was recorded (for aging)
        priority: Priority score for prioritized experience replay (future enhancement)
    """

    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    done: bool
    timestamp: float
    priority: float = 1.0

    def to_tuple(self) -> Tuple[np.ndarray, int, float, np.ndarray, bool]:
        """Convert experience to tuple format for compatibility."""
        return (self.state, self.action, self.reward, self.next_state, self.done)


class ExperienceBuffer:
    """
    Experience replay buffer with FIFO management and advanced features.

    This buffer stores experiences for the DQN agent to learn from, providing
    several key benefits:
    - Breaks correlation between consecutive experiences
    - Enables batch learning for efficiency
    - Allows reuse of valuable experiences
    - Supports prioritized sampling (future enhancement)
    """

    def __init__(
        self,
        max_size: int = 2000,
        min_size_for_sampling: int = 32,
        auto_cleanup_threshold: float = 0.9,
        enable_priority_sampling: bool = False,
        random_seed: Optional[int] = None,
    ):
        """
        Initialize the experience replay buffer.

        Args:
            max_size: Maximum number of experiences to store
            min_size_for_sampling: Minimum experiences needed before sampling
            auto_cleanup_threshold: When buffer reaches this % of max_size, auto-cleanup old experiences
            enable_priority_sampling: Whether to enable prioritized experience replay
            random_seed: Random seed for reproducible sampling
        """
        self.max_size = max_size
        self.min_size_for_sampling = min_size_for_sampling
        self.auto_cleanup_threshold = auto_cleanup_threshold
        self.enable_priority_sampling = enable_priority_sampling

        # Use deque for efficient FIFO operations (no maxlen to allow auto-cleanup control)
        self._buffer: Deque[Experience] = deque()

        # Statistics tracking
        self._total_experiences_added = 0
        self._total_experiences_sampled = 0
        self._cleanup_count = 0

        # Performance metrics
        self._average_reward = 0.0
        self._reward_history = deque(maxlen=1000)  # Track recent rewards

        # Auto-cleanup tracking to prevent multiple triggers
        self._last_cleanup_size = 0

        # Set random seed if provided
        if random_seed is not None:
            random.seed(random_seed)
            np.random.seed(random_seed)

        logger.info(f"Initialized ExperienceBuffer: max_size={max_size}, "
                   f"min_sampling_size={min_size_for_sampling}, "
                   f"auto_cleanup_threshold={auto_cleanup_threshold}")

    def add(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        priority: Optional[float] = None,
    ) -> None:
        """
        Add a new experience to the buffer.

        Args:
            state: State vector when action was taken
            action: Action index that was taken
            reward: Reward received after taking the action
            next_state: Resulting state vector
            done: Whether episode ended after this action
            priority: Optional priority score for sampling
        """
        import time

        experience = Experience(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done,
            timestamp=time.time(),
            priority=priority if priority is not None else 1.0
        )

        self._buffer.append(experience)
        self._total_experiences_added += 1

        # Check if we need to make space (auto-cleanup) when buffer crosses the threshold
        current_size = len(self._buffer)
        threshold = int(self.max_size * self.auto_cleanup_threshold)

        # Only trigger auto-cleanup if we just crossed the threshold and haven't cleaned at this threshold before
        if current_size > threshold and current_size > 0 and threshold != self._last_cleanup_size:
            self._auto_cleanup()
            self._last_cleanup_size = threshold  # Remember we cleaned at this threshold

        # Enforce max_size limit after adding and cleanup
        while len(self._buffer) > self.max_size:
            self._buffer.popleft()

        # Update reward statistics
        self._reward_history.append(reward)
        self._average_reward = np.mean(list(self._reward_history))

        logger.debug(f"Added experience: action={action}, reward={reward:.3f}, "
                    f"buffer_size={len(self._buffer)}/{self.max_size}")

    def sample(self, batch_size: int) -> Optional[List[Tuple[np.ndarray, int, float, np.ndarray, bool]]]:
        """
        Sample a batch of experiences from the buffer.

        Args:
            batch_size: Number of experiences to sample

        Returns:
            List of experience tuples, or None if insufficient experiences
        """
        if len(self._buffer) < self.min_size_for_sampling:
            logger.debug(f"Insufficient experiences for sampling: "
                        f"{len(self._buffer)} < {self.min_size_for_sampling}")
            return None

        if batch_size > len(self._buffer):
            batch_size = len(self._buffer)
            logger.debug(f"Reduced batch size to {batch_size} due to limited experiences")

        if self.enable_priority_sampling:
            # Prioritized experience replay (future enhancement)
            experiences = self._sample_prioritized(batch_size)
        else:
            # Uniform random sampling
            experiences = random.sample(list(self._buffer), batch_size)

        # Convert to tuple format for compatibility with existing DQN code
        batch = [exp.to_tuple() for exp in experiences]
        self._total_experiences_sampled += batch_size

        logger.debug(f"Sampled batch of {len(batch)} experiences")
        return batch

    def _sample_prioritized(self, batch_size: int) -> List[Experience]:
        """
        Sample experiences using prioritized experience replay.

        Args:
            batch_size: Number of experiences to sample

        Returns:
            List of sampled experiences
        """
        # Calculate sampling probabilities based on priorities
        priorities = np.array([exp.priority for exp in self._buffer])

        # Add small epsilon to avoid zero probabilities
        priorities = priorities + 1e-6

        # Calculate sampling probabilities
        probabilities = priorities / priorities.sum()

        # Sample indices based on probabilities
        indices = np.random.choice(len(self._buffer), size=batch_size, p=probabilities)

        return [self._buffer[i] for i in indices]

    def _auto_cleanup(self) -> None:
        """
        Automatically clean up old experiences when buffer is nearly full.
        Uses FIFO approach but can be enhanced with more sophisticated strategies.
        """
        if not self._buffer:
            return

        # Calculate how many experiences to remove to get to 70% of max_size
        current_size = len(self._buffer)
        target_size = int(self.max_size * 0.7)
        experiences_to_remove = current_size - target_size

        if experiences_to_remove > 0:
            # Remove oldest experiences (FIFO)
            for _ in range(experiences_to_remove):
                if self._buffer:
                    self._buffer.popleft()

            self._cleanup_count += 1
            logger.info(f"Auto-cleanup: removed {experiences_to_remove} old experiences, "
                       f"buffer size now {len(self._buffer)}")

    def update_priorities(self, indices: List[int], priorities: List[float]) -> None:
        """
        Update priorities for specific experiences (for prioritized experience replay).

        Args:
            indices: List of experience indices to update
            priorities: List of new priority values
        """
        if not self.enable_priority_sampling:
            logger.warning("Priority sampling not enabled, ignoring priority updates")
            return

        if len(indices) != len(priorities):
            logger.error("Mismatch between indices and priorities length")
            return

        for idx, priority in zip(indices, priorities):
            if 0 <= idx < len(self._buffer):
                # Convert to list for modification (deque doesn't support direct indexing)
                buffer_list = list(self._buffer)
                buffer_list[idx].priority = priority
                self._buffer = deque(buffer_list, maxlen=self.max_size)

        logger.debug(f"Updated priorities for {len(indices)} experiences")

    def get_recent_experiences(self, count: int = 10) -> List[Experience]:
        """
        Get the most recent experiences added to the buffer.

        Args:
            count: Number of recent experiences to return

        Returns:
            List of most recent experiences
        """
        recent_count = min(count, len(self._buffer))
        return list(self._buffer)[-recent_count:]

    def get_experiences_by_reward(self, threshold: float, top_n: int = 10) -> List[Experience]:
        """
        Get experiences with rewards above a certain threshold.

        Args:
            threshold: Minimum reward threshold
            top_n: Maximum number of experiences to return

        Returns:
            List of high-reward experiences
        """
        high_reward_experiences = [exp for exp in self._buffer if exp.reward >= threshold]

        # Sort by reward (descending) and return top N
        high_reward_experiences.sort(key=lambda x: x.reward, reverse=True)
        return high_reward_experiences[:top_n]

    def clear(self) -> None:
        """Clear all experiences from the buffer."""
        self._buffer.clear()
        self._reward_history.clear()
        self._average_reward = 0.0
        self._last_cleanup_size = 0  # Reset cleanup tracking
        logger.info("Cleared experience buffer")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the buffer.

        Returns:
            Dictionary containing buffer statistics
        """
        if not self._buffer:
            return {
                "size": 0,
                "max_size": self.max_size,
                "utilization": 0.0,
                "total_added": self._total_experiences_added,
                "total_sampled": self._total_experiences_sampled,
                "cleanup_count": self._cleanup_count,
                "average_reward": 0.0,
                "can_sample": False,
            }

        # Calculate reward statistics
        rewards = [exp.reward for exp in self._buffer]
        reward_stats = {
            "average": np.mean(rewards),
            "min": np.min(rewards),
            "max": np.max(rewards),
            "std": np.std(rewards),
        }

        # Calculate action distribution
        actions = [exp.action for exp in self._buffer]
        unique_actions, action_counts = np.unique(actions, return_counts=True)
        action_distribution = dict(zip(unique_actions, action_counts))

        # Calculate age statistics (in seconds)
        import time
        current_time = time.time()
        ages = [current_time - exp.timestamp for exp in self._buffer]
        age_stats = {
            "average_age": np.mean(ages),
            "min_age": np.min(ages),
            "max_age": np.max(ages),
        }

        return {
            "size": len(self._buffer),
            "max_size": self.max_size,
            "utilization": len(self._buffer) / self.max_size,
            "total_added": self._total_experiences_added,
            "total_sampled": self._total_experiences_sampled,
            "cleanup_count": self._cleanup_count,
            "reward_statistics": reward_stats,
            "action_distribution": action_distribution,
            "age_statistics": age_stats,
            "can_sample": len(self._buffer) >= self.min_size_for_sampling,
            "priority_sampling_enabled": self.enable_priority_sampling,
        }

    def save_to_file(self, filepath: str) -> bool:
        """
        Save buffer contents to a file.

        Args:
            filepath: Path to save the buffer

        Returns:
            True if successful, False otherwise
        """
        try:
            import pickle

            # Convert deque to list for serialization
            buffer_data = {
                "buffer": list(self._buffer),
                "max_size": self.max_size,
                "min_size_for_sampling": self.min_size_for_sampling,
                "auto_cleanup_threshold": self.auto_cleanup_threshold,
                "enable_priority_sampling": self.enable_priority_sampling,
                "total_experiences_added": self._total_experiences_added,
                "total_experiences_sampled": self._total_experiences_sampled,
                "cleanup_count": self._cleanup_count,
                "average_reward": self._average_reward,
                "reward_history": list(self._reward_history),
            }

            with open(filepath, 'wb') as f:
                pickle.dump(buffer_data, f)

            logger.info(f"Saved experience buffer to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to save experience buffer: {e}")
            return False

    def load_from_file(self, filepath: str) -> bool:
        """
        Load buffer contents from a file.

        Args:
            filepath: Path to load the buffer from

        Returns:
            True if successful, False otherwise
        """
        try:
            import pickle

            with open(filepath, 'rb') as f:
                buffer_data = pickle.load(f)

            # Restore buffer state
            self._buffer = deque(buffer_data["buffer"], maxlen=self.max_size)
            self.max_size = buffer_data.get("max_size", self.max_size)
            self.min_size_for_sampling = buffer_data.get("min_size_for_sampling", self.min_size_for_sampling)
            self.auto_cleanup_threshold = buffer_data.get("auto_cleanup_threshold", self.auto_cleanup_threshold)
            self.enable_priority_sampling = buffer_data.get("enable_priority_sampling", self.enable_priority_sampling)
            self._total_experiences_added = buffer_data.get("total_experiences_added", 0)
            self._total_experiences_sampled = buffer_data.get("total_experiences_sampled", 0)
            self._cleanup_count = buffer_data.get("cleanup_count", 0)
            self._average_reward = buffer_data.get("average_reward", 0.0)
            self._reward_history = deque(buffer_data.get("reward_history", []), maxlen=1000)

            logger.info(f"Loaded experience buffer from {filepath}: {len(self._buffer)} experiences")
            return True

        except Exception as e:
            logger.error(f"Failed to load experience buffer: {e}")
            return False

    def __len__(self) -> int:
        """Return the current number of experiences in the buffer."""
        return len(self._buffer)

    def __bool__(self) -> bool:
        """Return True if buffer contains experiences, False otherwise."""
        return len(self._buffer) > 0

    def __repr__(self) -> str:
        """Return string representation of the buffer."""
        return (f"ExperienceBuffer(size={len(self._buffer)}/{self.max_size}, "
                f"can_sample={len(self._buffer) >= self.min_size_for_sampling})")
