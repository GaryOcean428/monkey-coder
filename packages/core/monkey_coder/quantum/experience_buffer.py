"""
Experience Replay Buffer for DQN Agent.

This module implements a thread-safe, FIFO-managed experience replay buffer for storing
and sampling experiences during reinforcement learning training. The buffer supports
configurable capacity with automatic cleanup and efficient random sampling.

Based on the Monkey Coder Phase 2 quantum routing requirements.
"""

import random
import threading
from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, List, Union

import numpy as np


@dataclass
class Experience:
    """
    Represents a single experience tuple for reinforcement learning.
    
    An experience contains the state transition information needed for Q-learning:
    - Current state before action
    - Action taken in that state
    - Reward received after action
    - Next state after action
    - Terminal flag indicating if episode ended
    """
    state: np.ndarray
    action: Union[int, np.ndarray]
    reward: float
    next_state: np.ndarray
    done: bool


class BufferFullError(Exception):
    """Raised when attempting to add to a full buffer with strict capacity."""
    pass


class BufferEmptyError(Exception):
    """Raised when attempting to sample from an empty buffer."""
    pass


class ExperienceBuffer:
    """
    Thread-safe experience replay buffer with FIFO management.
    
    Implements a circular buffer for storing experiences with efficient random sampling
    for DQN training. Supports configurable capacity with automatic old experience
    removal when full.
    
    Key Features:
    - FIFO management with automatic cleanup
    - Thread-safe operations for concurrent access
    - Efficient random sampling without replacement
    - Configurable buffer size with memory optimization
    - Performance optimized for high-throughput scenarios
    
    Example:
        >>> buffer = ExperienceBuffer(max_size=1000)
        >>> experience = Experience(
        ...     state=np.array([1, 2, 3]),
        ...     action=0,
        ...     reward=1.0,
        ...     next_state=np.array([2, 3, 4]),
        ...     done=False
        ... )
        >>> buffer.add_experience(experience)
        >>> batch = buffer.sample_batch(batch_size=32)
    """
    
    def __init__(self, max_size: int = 2000):
        """
        Initialize experience replay buffer.
        
        Args:
            max_size: Maximum number of experiences to store (default: 2000)
                     When exceeded, oldest experiences are automatically removed
        
        Raises:
            ValueError: If max_size is not a positive integer
        """
        if max_size <= 0:
            raise ValueError("Buffer max_size must be a positive integer")
        
        self.max_size = max_size
        self._buffer: Deque[Experience] = deque(maxlen=max_size)
        self._lock = threading.RLock()  # Reentrant lock for nested operations
        
    def add_experience(self, experience: Experience) -> None:
        """
        Add a new experience to the buffer.
        
        Thread-safe operation that adds experience to the buffer. If buffer is at
        capacity, the oldest experience is automatically removed (FIFO).
        
        Args:
            experience: Experience tuple containing (state, action, reward, next_state, done)
        
        Raises:
            TypeError: If experience is not an Experience instance
        """
        if not isinstance(experience, Experience):
            raise TypeError("experience must be an Experience instance")
        
        with self._lock:
            self._buffer.append(experience)
    
    def sample_batch(self, batch_size: int) -> List[Experience]:
        """
        Sample a random batch of experiences from the buffer.
        
        Thread-safe operation that returns a list of randomly selected experiences
        without replacement. Useful for training neural networks with varied data.
        
        Args:
            batch_size: Number of experiences to sample
            
        Returns:
            List of randomly selected Experience objects
            
        Raises:
            BufferEmptyError: If buffer is empty
            ValueError: If batch_size exceeds buffer size or is not positive
        """
        if batch_size <= 0:
            raise ValueError("Batch size must be positive")
        
        with self._lock:
            if self.is_empty():
                raise BufferEmptyError("Cannot sample from empty buffer")
            
            if batch_size > len(self._buffer):
                raise ValueError(
                    f"Batch size {batch_size} exceeds buffer size {len(self._buffer)}"
                )
            
            # Use random.sample for efficient sampling without replacement
            return random.sample(list(self._buffer), batch_size)
    
    def clear(self) -> None:
        """
        Clear all experiences from the buffer.
        
        Thread-safe operation that removes all stored experiences and resets
        the buffer to empty state.
        """
        with self._lock:
            self._buffer.clear()
    
    def size(self) -> int:
        """
        Get current number of experiences in buffer.
        
        Returns:
            Current buffer size (number of stored experiences)
        """
        with self._lock:
            return len(self._buffer)
    
    def is_empty(self) -> bool:
        """
        Check if buffer is empty.
        
        Returns:
            True if buffer contains no experiences, False otherwise
        """
        with self._lock:
            return len(self._buffer) == 0
    
    def is_full(self) -> bool:
        """
        Check if buffer is at capacity.
        
        Returns:
            True if buffer is at maximum capacity, False otherwise
        """
        with self._lock:
            return len(self._buffer) == self.max_size
    
    def get_statistics(self) -> dict:
        """
        Get buffer usage statistics.
        
        Returns:
            Dictionary containing buffer statistics:
            - size: Current number of experiences
            - max_size: Maximum buffer capacity
            - utilization: Percentage of buffer used (0.0-1.0)
            - is_empty: Whether buffer is empty
            - is_full: Whether buffer is at capacity
        """
        with self._lock:
            current_size = len(self._buffer)
            return {
                "size": current_size,
                "max_size": self.max_size,
                "utilization": current_size / self.max_size if self.max_size > 0 else 0.0,
                "is_empty": current_size == 0,
                "is_full": current_size == self.max_size,
            }
    
    def __len__(self) -> int:
        """Return current buffer size."""
        return self.size()
    
    def __repr__(self) -> str:
        """Return string representation of buffer."""
        return f"ExperienceBuffer(size={self.size()}, max_size={self.max_size})"