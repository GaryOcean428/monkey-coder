"""
Experience Replay Buffer for DQN Agent

This module implements a configurable memory buffer for experience replay,
supporting FIFO management and automatic cleanup as specified in T2.1.2.
"""

import random
import logging
from collections import deque
from dataclasses import dataclass
from typing import List, Tuple, Optional, Any
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Experience:
    """Represents a single experience tuple for DQN training."""

    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    done: bool
    timestamp: float

    def __post_init__(self):
        """Validate experience data after initialization."""
        if not isinstance(self.state, np.ndarray):
            raise ValueError("State must be a numpy array")
        if not isinstance(self.next_state, np.ndarray):
            raise ValueError("Next state must be a numpy array")
        if self.state.shape != self.next_state.shape:
            raise ValueError("State and next_state must have the same shape")


class ExperienceReplayBuffer:
    """
    Configurable memory buffer for experience replay with FIFO management.

    Supports automatic cleanup and efficient sampling for DQN training.
    """

    def __init__(self,
                 capacity: int = 2000,
                 min_size: int = 100,
                 cleanup_threshold: float = 0.9):
        """
        Initialize the experience replay buffer.

        Args:
            capacity: Maximum number of experiences to store (default: 2000)
            min_size: Minimum experiences before sampling is allowed
            cleanup_threshold: Trigger cleanup when buffer is this full (0.0-1.0)
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        if min_size < 0 or min_size > capacity:
            raise ValueError("min_size must be between 0 and capacity")
        if not 0.0 <= cleanup_threshold <= 1.0:
            raise ValueError("cleanup_threshold must be between 0.0 and 1.0")

        self.capacity = capacity
        self.min_size = min_size
        self.cleanup_threshold = cleanup_threshold

        # Use deque for efficient FIFO operations
        self._buffer: deque = deque(maxlen=capacity)

        # Statistics
        self._total_added = 0
        self._total_sampled = 0
        self._cleanup_count = 0

        logger.info(f"Initialized ExperienceReplayBuffer with capacity={capacity}")

    def add(self, experience: Experience) -> None:
        """
        Add a new experience to the buffer.

        Args:
            experience: Experience tuple to add
        """
        if not isinstance(experience, Experience):
            raise TypeError("experience must be an Experience object")

        # Add to buffer (automatically removes oldest if at capacity)
        self._buffer.append(experience)
        self._total_added += 1

        # Trigger cleanup if necessary
        if len(self._buffer) >= self.capacity * self.cleanup_threshold:
            self._maybe_cleanup()

    def sample(self, batch_size: int) -> List[Experience]:
        """
        Sample a random batch of experiences.

        Args:
            batch_size: Number of experiences to sample

        Returns:
            List of randomly sampled experiences

        Raises:
            ValueError: If batch_size is invalid or insufficient experiences
        """
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")

        if len(self._buffer) < self.min_size:
            raise ValueError(f"Insufficient experiences: {len(self._buffer)} < {self.min_size}")

        if batch_size > len(self._buffer):
            raise ValueError(f"batch_size ({batch_size}) > buffer size ({len(self._buffer)})")

        # Random sampling without replacement
        batch = random.sample(list(self._buffer), batch_size)
        self._total_sampled += batch_size

        return batch

    def sample_recent(self, batch_size: int, recent_fraction: float = 0.1) -> List[Experience]:
        """
        Sample experiences with bias toward recent experiences.

        Args:
            batch_size: Number of experiences to sample
            recent_fraction: Fraction of samples to take from recent experiences

        Returns:
            List of sampled experiences with recent bias
        """
        if not 0.0 <= recent_fraction <= 1.0:
            raise ValueError("recent_fraction must be between 0.0 and 1.0")

        if len(self._buffer) < self.min_size:
            raise ValueError(f"Insufficient experiences: {len(self._buffer)} < {self.min_size}")

        # Calculate split
        recent_count = int(batch_size * recent_fraction)
        random_count = batch_size - recent_count

        # Get recent experiences (last 20% of buffer)
        recent_start = max(0, len(self._buffer) - int(len(self._buffer) * 0.2))
        recent_experiences = list(self._buffer)[recent_start:]

        # Sample components
        batch = []

        if recent_count > 0 and recent_experiences:
            batch.extend(random.sample(recent_experiences,
                                     min(recent_count, len(recent_experiences))))

        if random_count > 0:
            remaining_needed = batch_size - len(batch)
            if remaining_needed > 0:
                batch.extend(random.sample(list(self._buffer), remaining_needed))

        self._total_sampled += len(batch)
        return batch

    def get_batch_arrays(self, batch: List[Experience]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Convert a batch of experiences to numpy arrays for training.

        Args:
            batch: List of Experience objects

        Returns:
            Tuple of (states, actions, rewards, next_states, dones) as numpy arrays
        """
        if not batch:
            raise ValueError("Batch cannot be empty")

        states = np.array([exp.state for exp in batch])
        actions = np.array([exp.action for exp in batch])
        rewards = np.array([exp.reward for exp in batch])
        next_states = np.array([exp.next_state for exp in batch])
        dones = np.array([exp.done for exp in batch])

        return states, actions, rewards, next_states, dones

    def clear(self) -> None:
        """Clear all experiences from the buffer."""
        self._buffer.clear()
        logger.info("Experience buffer cleared")

    def _maybe_cleanup(self) -> None:
        """
        Perform automatic cleanup if needed.

        Removes oldest experiences to free up space and maintain performance.
        """
        # Only cleanup if we exceed the threshold, not when we're exactly at it
        if len(self._buffer) > self.capacity * self.cleanup_threshold:
            # Remove oldest 10% of experiences
            cleanup_count = max(1, int(self.capacity * 0.1))

            for _ in range(cleanup_count):
                if self._buffer:
                    self._buffer.popleft()

            self._cleanup_count += 1
            logger.debug(f"Cleaned up {cleanup_count} old experiences")

    def get_statistics(self) -> dict:
        """
        Get buffer statistics and performance metrics.

        Returns:
            Dictionary with buffer statistics
        """
        return {
            'size': len(self._buffer),
            'capacity': self.capacity,
            'utilization': len(self._buffer) / self.capacity,
            'total_added': self._total_added,
            'total_sampled': self._total_sampled,
            'cleanup_count': self._cleanup_count,
            'min_size': self.min_size,
            'ready_for_sampling': len(self._buffer) >= self.min_size
        }

    def save_buffer(self, filepath: str) -> bool:
        """
        Save buffer contents to file.

        Args:
            filepath: Path to save buffer data

        Returns:
            True if successful, False otherwise
        """
        try:
            import pickle

            buffer_data = {
                'experiences': list(self._buffer),
                'capacity': self.capacity,
                'min_size': self.min_size,
                'cleanup_threshold': self.cleanup_threshold,
                'stats': self.get_statistics()
            }

            with open(filepath, 'wb') as f:
                pickle.dump(buffer_data, f)

            logger.info(f"Buffer saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to save buffer: {e}")
            return False

    def load_buffer(self, filepath: str) -> bool:
        """
        Load buffer contents from file.

        Args:
            filepath: Path to load buffer data from

        Returns:
            True if successful, False otherwise
        """
        try:
            import pickle

            with open(filepath, 'rb') as f:
                buffer_data = pickle.load(f)

            # Restore configuration
            self.capacity = buffer_data.get('capacity', self.capacity)
            self.min_size = buffer_data.get('min_size', self.min_size)
            self.cleanup_threshold = buffer_data.get('cleanup_threshold', self.cleanup_threshold)

            # Restore experiences
            self._buffer = deque(buffer_data['experiences'], maxlen=self.capacity)

            # Update statistics
            old_stats = buffer_data.get('stats', {})
            self._total_added = old_stats.get('total_added', len(self._buffer))
            self._total_sampled = old_stats.get('total_sampled', 0)
            self._cleanup_count = old_stats.get('cleanup_count', 0)

            logger.info(f"Buffer loaded from {filepath} with {len(self._buffer)} experiences")
            return True

        except Exception as e:
            logger.error(f"Failed to load buffer: {e}")
            return False

    def __len__(self) -> int:
        """Return the current number of experiences in the buffer."""
        return len(self._buffer)

    def __repr__(self) -> str:
        """Return string representation of the buffer."""
        return (f"ExperienceReplayBuffer(size={len(self._buffer)}, "
                f"capacity={self.capacity}, utilization={len(self._buffer)/self.capacity:.1%})")


class PrioritizedExperienceBuffer(ExperienceReplayBuffer):
    """
    Extension of ExperienceReplayBuffer with prioritized sampling.

    Implements importance sampling based on TD error for more efficient learning.
    """

    def __init__(self,
                 capacity: int = 2000,
                 min_size: int = 100,
                 cleanup_threshold: float = 0.9,
                 alpha: float = 0.6,
                 beta: float = 0.4,
                 beta_increment: float = 0.001):
        """
        Initialize prioritized experience replay buffer.

        Args:
            alpha: Prioritization exponent (0 = uniform, 1 = full prioritization)
            beta: Importance sampling exponent (0 = no correction, 1 = full correction)
            beta_increment: Amount to increment beta per sample
        """
        super().__init__(capacity, min_size, cleanup_threshold)

        self.alpha = alpha
        self.beta = beta
        self.beta_increment = beta_increment
        self.max_beta = 1.0

        # Priority storage (parallel to buffer)
        self._priorities: deque = deque(maxlen=capacity)
        self._max_priority = 1.0

    def add(self, experience: Experience, priority: Optional[float] = None) -> None:
        """
        Add experience with priority.

        Args:
            experience: Experience to add
            priority: Priority value (defaults to max priority)
        """
        # Normalize to float for type safety (avoid Optional comparisons)
        prio: float = float(self._max_priority) if priority is None else float(priority)

        super().add(experience)
        self._priorities.append(prio)

        if prio > self._max_priority:
            self._max_priority = prio


    def sample(self, batch_size: int) -> Tuple[List[Experience], np.ndarray, np.ndarray]:
        """
        Sample experiences using prioritized sampling.

        Returns:
            Tuple of (experiences, indices, importance_weights)
        """
        if len(self._buffer) < self.min_size:
            raise ValueError(f"Insufficient experiences: {len(self._buffer)} < {self.min_size}")

        # Calculate sampling probabilities
        priorities = np.array(self._priorities)
        probabilities = priorities ** self.alpha
        probabilities /= probabilities.sum()

        # Sample indices
        indices = np.random.choice(len(self._buffer), batch_size, p=probabilities)

        # Get experiences
        experiences = [self._buffer[i] for i in indices]

        # Calculate importance weights
        total_samples = len(self._buffer)
        weights = (total_samples * probabilities[indices]) ** (-self.beta)
        weights /= weights.max()  # Normalize by max weight

        # Update beta
        self.beta = min(self.max_beta, self.beta + self.beta_increment)

        self._total_sampled += batch_size

        return experiences, indices, weights

    def update_priorities(self, indices: np.ndarray, priorities: np.ndarray) -> None:
        """
        Update priorities for sampled experiences.

        Args:
            indices: Indices of experiences to update
            priorities: New priority values
        """
        for idx, priority in zip(indices, priorities):
            if 0 <= idx < len(self._priorities):
                self._priorities[idx] = priority
                if priority > self._max_priority:
                    self._max_priority = priority

# Backward compatibility wrapper for legacy imports and args
class ExperienceBuffer(ExperienceReplayBuffer):
    """
    Backward-compatible ExperienceBuffer.

    Tests refer to ExperienceBuffer(max_size=...), so this wrapper maps
    max_size -> capacity and preserves other semantics.
    """

    def __init__(self, max_size: int = 2000, min_size: int = 100, cleanup_threshold: float = 0.9):
        super().__init__(capacity=max_size, min_size=min_size, cleanup_threshold=cleanup_threshold)
