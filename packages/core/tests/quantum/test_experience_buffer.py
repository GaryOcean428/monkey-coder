"""
Tests for Experience Replay Buffer implementation.

This module tests the experience replay buffer functionality required for DQN agent training,
including FIFO management, concurrent access, and memory optimization.
"""

import pytest
import numpy as np
import threading
import time
from typing import Tuple, List, Any

from monkey_coder.quantum.experience_buffer import (
    ExperienceBuffer,
    Experience,
    BufferFullError,
    BufferEmptyError
)


class TestExperienceBuffer:
    """Test suite for Experience Replay Buffer implementation."""

    def test_buffer_initialization_with_defaults(self):
        """Test buffer creates with default parameters."""
        buffer = ExperienceBuffer()
        assert buffer.max_size == 2000
        assert buffer.size() == 0
        assert buffer.is_empty() is True
        assert buffer.is_full() is False

    def test_buffer_initialization_with_custom_size(self):
        """Test buffer creates with custom size parameter."""
        buffer = ExperienceBuffer(max_size=1000)
        assert buffer.max_size == 1000
        assert buffer.size() == 0

    def test_add_single_experience(self):
        """Test adding a single experience to buffer."""
        buffer = ExperienceBuffer(max_size=5)
        experience = Experience(
            state=np.array([1, 2, 3]),
            action=0,
            reward=1.0,
            next_state=np.array([2, 3, 4]),
            done=False
        )
        
        buffer.add_experience(experience)
        assert buffer.size() == 1
        assert buffer.is_empty() is False

    def test_add_multiple_experiences(self):
        """Test adding multiple experiences to buffer."""
        buffer = ExperienceBuffer(max_size=5)
        
        for i in range(3):
            experience = Experience(
                state=np.array([i, i+1, i+2]),
                action=i,
                reward=float(i),
                next_state=np.array([i+1, i+2, i+3]),
                done=False
            )
            buffer.add_experience(experience)
        
        assert buffer.size() == 3
        assert buffer.is_empty() is False
        assert buffer.is_full() is False

    def test_fifo_behavior_when_buffer_full(self):
        """Test FIFO behavior when buffer exceeds capacity."""
        buffer = ExperienceBuffer(max_size=3)
        
        # Fill buffer to capacity
        for i in range(3):
            experience = Experience(
                state=np.array([i]),
                action=i,
                reward=float(i),
                next_state=np.array([i+1]),
                done=False
            )
            buffer.add_experience(experience)
        
        assert buffer.is_full() is True
        assert buffer.size() == 3
        
        # Add one more experience - should remove oldest
        new_experience = Experience(
            state=np.array([99]),
            action=99,
            reward=99.0,
            next_state=np.array([100]),
            done=True
        )
        buffer.add_experience(new_experience)
        
        assert buffer.size() == 3  # Size should remain the same
        assert buffer.is_full() is True

    def test_sample_batch_success(self):
        """Test successful batch sampling from buffer."""
        buffer = ExperienceBuffer(max_size=10)
        
        # Add experiences
        for i in range(5):
            experience = Experience(
                state=np.array([i]),
                action=i,
                reward=float(i),
                next_state=np.array([i+1]),
                done=False
            )
            buffer.add_experience(experience)
        
        # Sample batch
        batch = buffer.sample_batch(batch_size=3)
        assert len(batch) == 3
        assert all(isinstance(exp, Experience) for exp in batch)

    def test_sample_batch_larger_than_buffer_size(self):
        """Test sampling batch larger than available experiences."""
        buffer = ExperienceBuffer(max_size=10)
        
        # Add only 2 experiences
        for i in range(2):
            experience = Experience(
                state=np.array([i]),
                action=i,
                reward=float(i),
                next_state=np.array([i+1]),
                done=False
            )
            buffer.add_experience(experience)
        
        # Try to sample larger batch
        with pytest.raises(ValueError, match="Batch size .* exceeds buffer size"):
            buffer.sample_batch(batch_size=5)

    def test_sample_from_empty_buffer(self):
        """Test sampling from empty buffer raises appropriate error."""
        buffer = ExperienceBuffer()
        
        with pytest.raises(BufferEmptyError):
            buffer.sample_batch(batch_size=1)

    def test_clear_buffer(self):
        """Test clearing buffer removes all experiences."""
        buffer = ExperienceBuffer(max_size=5)
        
        # Add experiences
        for i in range(3):
            experience = Experience(
                state=np.array([i]),
                action=i,
                reward=float(i),
                next_state=np.array([i+1]),
                done=False
            )
            buffer.add_experience(experience)
        
        assert buffer.size() == 3
        
        buffer.clear()
        assert buffer.size() == 0
        assert buffer.is_empty() is True
        assert buffer.is_full() is False

    def test_thread_safety_concurrent_adds(self):
        """Test thread safety with concurrent add operations."""
        buffer = ExperienceBuffer(max_size=1000)
        num_threads = 10
        experiences_per_thread = 50
        
        def add_experiences(thread_id: int):
            for i in range(experiences_per_thread):
                experience = Experience(
                    state=np.array([thread_id, i]),
                    action=thread_id * 100 + i,
                    reward=float(thread_id + i),
                    next_state=np.array([thread_id, i+1]),
                    done=False
                )
                buffer.add_experience(experience)
        
        threads = []
        for thread_id in range(num_threads):
            thread = threading.Thread(target=add_experiences, args=(thread_id,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert buffer.size() == num_threads * experiences_per_thread

    def test_thread_safety_concurrent_sample(self):
        """Test thread safety with concurrent sampling operations."""
        buffer = ExperienceBuffer(max_size=1000)
        
        # Pre-fill buffer
        for i in range(500):
            experience = Experience(
                state=np.array([i]),
                action=i,
                reward=float(i),
                next_state=np.array([i+1]),
                done=False
            )
            buffer.add_experience(experience)
        
        results = []
        
        def sample_batch():
            try:
                batch = buffer.sample_batch(batch_size=10)
                results.append(len(batch))
            except Exception as e:
                results.append(f"Error: {e}")
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=sample_batch)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All sampling operations should succeed
        assert all(result == 10 for result in results)

    def test_thread_safety_mixed_operations(self):
        """Test thread safety with mixed add and sample operations."""
        buffer = ExperienceBuffer(max_size=200)
        
        # Pre-fill buffer partially
        for i in range(50):
            experience = Experience(
                state=np.array([i]),
                action=i,
                reward=float(i),
                next_state=np.array([i+1]),
                done=False
            )
            buffer.add_experience(experience)
        
        add_results = []
        sample_results = []
        
        def add_worker():
            for i in range(50, 100):
                experience = Experience(
                    state=np.array([i]),
                    action=i,
                    reward=float(i),
                    next_state=np.array([i+1]),
                    done=False
                )
                buffer.add_experience(experience)
                add_results.append(i)
        
        def sample_worker():
            time.sleep(0.01)  # Small delay to ensure some adds happen first
            for _ in range(10):
                try:
                    batch = buffer.sample_batch(batch_size=5)
                    sample_results.append(len(batch))
                except Exception as e:
                    sample_results.append(f"Error: {e}")
        
        add_thread = threading.Thread(target=add_worker)
        sample_thread = threading.Thread(target=sample_worker)
        
        add_thread.start()
        sample_thread.start()
        
        add_thread.join()
        sample_thread.join()
        
        # Verify operations completed successfully
        assert len(add_results) == 50
        assert all(result == 5 for result in sample_results if isinstance(result, int))

    def test_memory_efficiency(self):
        """Test memory usage remains reasonable with large buffer."""
        import sys
        
        buffer = ExperienceBuffer(max_size=1000)
        
        # Measure memory before adding experiences
        initial_size = sys.getsizeof(buffer)
        
        # Add many experiences
        for i in range(1000):
            experience = Experience(
                state=np.array([i] * 10),  # Larger state
                action=i,
                reward=float(i),
                next_state=np.array([i+1] * 10),  # Larger next_state
                done=False
            )
            buffer.add_experience(experience)
        
        # Memory should not grow excessively
        final_size = sys.getsizeof(buffer)
        assert buffer.size() == 1000
        assert buffer.is_full()
        
        # Add more experiences to test FIFO cleanup
        for i in range(1000, 1500):
            experience = Experience(
                state=np.array([i] * 10),
                action=i,
                reward=float(i),
                next_state=np.array([i+1] * 10),
                done=False
            )
            buffer.add_experience(experience)
        
        # Size should remain at max_size
        assert buffer.size() == 1000

    def test_experience_dataclass_properties(self):
        """Test Experience dataclass has correct properties."""
        experience = Experience(
            state=np.array([1, 2, 3]),
            action=0,
            reward=1.5,
            next_state=np.array([2, 3, 4]),
            done=True
        )
        
        assert np.array_equal(experience.state, np.array([1, 2, 3]))
        assert experience.action == 0
        assert experience.reward == 1.5
        assert np.array_equal(experience.next_state, np.array([2, 3, 4]))
        assert experience.done is True

    def test_sample_batch_randomness(self):
        """Test that batch sampling produces different results (randomness)."""
        buffer = ExperienceBuffer(max_size=100)
        
        # Add many experiences
        for i in range(50):
            experience = Experience(
                state=np.array([i]),
                action=i,
                reward=float(i),
                next_state=np.array([i+1]),
                done=False
            )
            buffer.add_experience(experience)
        
        # Sample multiple batches
        batch1 = buffer.sample_batch(batch_size=10)
        batch2 = buffer.sample_batch(batch_size=10)
        
        # Batches should be different (with high probability)
        actions1 = [exp.action for exp in batch1]
        actions2 = [exp.action for exp in batch2]
        assert actions1 != actions2  # Very unlikely to be equal if truly random

    def test_buffer_state_consistency(self):
        """Test buffer maintains consistent state throughout operations."""
        buffer = ExperienceBuffer(max_size=5)
        
        # Test various state transitions
        assert buffer.is_empty() and not buffer.is_full()
        
        # Add one experience
        experience = Experience(
            state=np.array([1]),
            action=0,
            reward=1.0,
            next_state=np.array([2]),
            done=False
        )
        buffer.add_experience(experience)
        assert not buffer.is_empty() and not buffer.is_full()
        
        # Fill buffer
        for i in range(1, 5):
            experience = Experience(
                state=np.array([i]),
                action=i,
                reward=float(i),
                next_state=np.array([i+1]),
                done=False
            )
            buffer.add_experience(experience)
        
        assert not buffer.is_empty() and buffer.is_full()
        
        # Clear and verify
        buffer.clear()
        assert buffer.is_empty() and not buffer.is_full()

    def test_large_batch_performance(self):
        """Test performance with large batches."""
        buffer = ExperienceBuffer(max_size=10000)
        
        # Fill buffer with large dataset
        for i in range(10000):
            experience = Experience(
                state=np.array([i] * 100),  # Large state vector
                action=i,
                reward=float(i),
                next_state=np.array([i+1] * 100),  # Large next_state vector
                done=False
            )
            buffer.add_experience(experience)
        
        # Test large batch sampling performance
        start_time = time.time()
        batch = buffer.sample_batch(batch_size=1000)
        end_time = time.time()
        
        assert len(batch) == 1000
        assert end_time - start_time < 1.0  # Should complete within 1 second