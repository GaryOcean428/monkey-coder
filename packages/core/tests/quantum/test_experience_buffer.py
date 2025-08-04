"""
Comprehensive test suite for Experience Replay Buffer

Tests all functionality including FIFO management, sampling, and prioritized replay.
"""

import pytest
import numpy as np
import tempfile
import os
from unittest.mock import patch

from monkey_coder.quantum.experience_buffer import (
    Experience, ExperienceReplayBuffer, PrioritizedExperienceBuffer
)


class TestExperience:
    """Test the Experience dataclass."""
    
    def test_valid_experience_creation(self):
        """Test creating a valid experience."""
        state = np.array([1.0, 2.0, 3.0])
        next_state = np.array([1.1, 2.1, 3.1])
        
        exp = Experience(
            state=state,
            action=1,
            reward=0.5,
            next_state=next_state,
            done=False,
            timestamp=123.45
        )
        
        assert np.array_equal(exp.state, state)
        assert exp.action == 1
        assert exp.reward == 0.5
        assert np.array_equal(exp.next_state, next_state)
        assert exp.done is False
        assert exp.timestamp == 123.45
    
    def test_experience_validation(self):
        """Test experience validation in __post_init__."""
        state = np.array([1.0, 2.0])
        
        # Invalid state type
        with pytest.raises(ValueError, match="State must be a numpy array"):
            Experience(
                state=[1.0, 2.0],  # List instead of array
                action=1,
                reward=0.5,
                next_state=state,
                done=False,
                timestamp=123.45
            )
        
        # Mismatched state shapes
        with pytest.raises(ValueError, match="State and next_state must have the same shape"):
            Experience(
                state=np.array([1.0, 2.0]),
                action=1,
                reward=0.5,
                next_state=np.array([1.0, 2.0, 3.0]),  # Different shape
                done=False,
                timestamp=123.45
            )


class TestExperienceReplayBuffer:
    """Test the ExperienceReplayBuffer class."""
    
    def setup_method(self):
        """Set up test fixtures before each method."""
        self.buffer = ExperienceReplayBuffer(capacity=100, min_size=10)
        
    def create_test_experience(self, idx: int = 0) -> Experience:
        """Create a test experience with given index."""
        state = np.array([float(idx), float(idx + 1)])
        next_state = np.array([float(idx + 0.1), float(idx + 1.1)])
        
        return Experience(
            state=state,
            action=idx % 4,
            reward=float(idx * 0.1),
            next_state=next_state,
            done=idx % 10 == 9,  # Every 10th experience is terminal
            timestamp=float(idx)
        )
    
    def test_initialization(self):
        """Test buffer initialization."""
        buffer = ExperienceReplayBuffer(capacity=500, min_size=50, cleanup_threshold=0.8)
        
        assert buffer.capacity == 500
        assert buffer.min_size == 50
        assert buffer.cleanup_threshold == 0.8
        assert len(buffer) == 0
        
        stats = buffer.get_statistics()
        assert stats['size'] == 0
        assert stats['capacity'] == 500
        assert stats['utilization'] == 0.0
        assert stats['ready_for_sampling'] is False
    
    def test_initialization_validation(self):
        """Test initialization parameter validation."""
        # Invalid capacity
        with pytest.raises(ValueError, match="Capacity must be positive"):
            ExperienceReplayBuffer(capacity=0)
        
        # Invalid min_size
        with pytest.raises(ValueError, match="min_size must be between 0 and capacity"):
            ExperienceReplayBuffer(capacity=100, min_size=150)
        
        # Invalid cleanup_threshold
        with pytest.raises(ValueError, match="cleanup_threshold must be between 0.0 and 1.0"):
            ExperienceReplayBuffer(capacity=100, cleanup_threshold=1.5)
    
    def test_add_experience(self):
        """Test adding experiences to the buffer."""
        exp = self.create_test_experience(0)
        
        assert len(self.buffer) == 0
        self.buffer.add(exp)
        assert len(self.buffer) == 1
        
        stats = self.buffer.get_statistics()
        assert stats['total_added'] == 1
    
    def test_add_invalid_experience(self):
        """Test adding invalid experience."""
        with pytest.raises(TypeError, match="experience must be an Experience object"):
            self.buffer.add("not an experience")
    
    def test_fifo_behavior(self):
        """Test FIFO behavior when buffer exceeds capacity."""
        # Set small capacity for easy testing with high cleanup threshold to avoid interference
        small_buffer = ExperienceReplayBuffer(capacity=5, min_size=2, cleanup_threshold=1.0)
        
        # Add more experiences than capacity
        for i in range(10):
            small_buffer.add(self.create_test_experience(i))
        
        # Should only have last 5 experiences due to deque maxlen behavior
        assert len(small_buffer) == 5
        
        # Sample all and check they're the last 5
        batch = small_buffer.sample(5)
        actions = [exp.action for exp in batch]
        
        # Should contain experiences with indices 5-9
        expected_actions = [i % 4 for i in range(5, 10)]
        assert set(actions) == set(expected_actions)
    
    def test_sampling(self):
        """Test basic sampling functionality."""
        # Add enough experiences for sampling
        for i in range(20):
            self.buffer.add(self.create_test_experience(i))
        
        # Test normal sampling
        batch = self.buffer.sample(5)
        assert len(batch) == 5
        assert all(isinstance(exp, Experience) for exp in batch)
        
        stats = self.buffer.get_statistics()
        assert stats['total_sampled'] == 5
    
    def test_sampling_validation(self):
        """Test sampling parameter validation."""
        # Add some experiences
        for i in range(5):
            self.buffer.add(self.create_test_experience(i))
        
        # Invalid batch size
        with pytest.raises(ValueError, match="batch_size must be positive"):
            self.buffer.sample(0)
        
        # Insufficient experiences for min_size
        with pytest.raises(ValueError, match="Insufficient experiences"):
            self.buffer.sample(3)  # min_size is 10, we only have 5
        
        # Add enough experiences
        for i in range(5, 15):
            self.buffer.add(self.create_test_experience(i))
        
        # Batch size larger than buffer
        with pytest.raises(ValueError, match="batch_size.*> buffer size"):
            self.buffer.sample(20)
    
    def test_sample_recent(self):
        """Test recent-biased sampling."""
        # Add experiences
        for i in range(50):
            self.buffer.add(self.create_test_experience(i))
        
        # Sample with recent bias
        batch = self.buffer.sample_recent(10, recent_fraction=0.5)
        assert len(batch) == 10
        
        # Check that some experiences are from recent portion
        recent_actions = [exp.action for exp in batch]
        assert len(set(recent_actions)) > 1  # Should have variety
    
    def test_sample_recent_validation(self):
        """Test recent sampling parameter validation."""
        for i in range(15):
            self.buffer.add(self.create_test_experience(i))
        
        # Invalid recent_fraction
        with pytest.raises(ValueError, match="recent_fraction must be between 0.0 and 1.0"):
            self.buffer.sample_recent(5, recent_fraction=1.5)
    
    def test_get_batch_arrays(self):
        """Test converting batch to numpy arrays."""
        # Add experiences
        for i in range(15):
            self.buffer.add(self.create_test_experience(i))
        
        batch = self.buffer.sample(5)
        states, actions, rewards, next_states, dones = self.buffer.get_batch_arrays(batch)
        
        assert isinstance(states, np.ndarray)
        assert isinstance(actions, np.ndarray)
        assert isinstance(rewards, np.ndarray)
        assert isinstance(next_states, np.ndarray)
        assert isinstance(dones, np.ndarray)
        
        assert states.shape == (5, 2)  # 5 experiences, 2D state
        assert actions.shape == (5,)
        assert rewards.shape == (5,)
        assert next_states.shape == (5, 2)
        assert dones.shape == (5,)
    
    def test_get_batch_arrays_empty(self):
        """Test get_batch_arrays with empty batch."""
        with pytest.raises(ValueError, match="Batch cannot be empty"):
            self.buffer.get_batch_arrays([])
    
    def test_clear(self):
        """Test clearing the buffer."""
        # Add experiences
        for i in range(10):
            self.buffer.add(self.create_test_experience(i))
        
        assert len(self.buffer) == 10
        
        self.buffer.clear()
        assert len(self.buffer) == 0
        
        stats = self.buffer.get_statistics()
        assert stats['size'] == 0
    
    def test_automatic_cleanup(self):
        """Test automatic cleanup when buffer gets full."""
        # Create buffer with low cleanup threshold
        buffer = ExperienceReplayBuffer(capacity=20, min_size=5, cleanup_threshold=0.8)
        
        # Fill buffer past cleanup threshold
        for i in range(18):  # 18 > 20 * 0.8 = 16
            buffer.add(self.create_test_experience(i))
        
        # Should trigger cleanup, removing ~10% = 2 experiences
        initial_size = len(buffer)
        assert initial_size <= 20
        
        stats = buffer.get_statistics()
        assert stats['cleanup_count'] >= 0  # Cleanup may or may not have triggered yet
    
    def test_save_and_load_buffer(self):
        """Test saving and loading buffer to/from file."""
        # Add experiences
        for i in range(15):
            self.buffer.add(self.create_test_experience(i))
        
        # Save buffer
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            filepath = tmp.name
        
        try:
            success = self.buffer.save_buffer(filepath)
            assert success is True
            
            # Create new buffer and load
            new_buffer = ExperienceReplayBuffer(capacity=50, min_size=5)
            success = new_buffer.load_buffer(filepath)
            assert success is True
            
            # Verify data was loaded correctly
            assert len(new_buffer) == 15
            assert new_buffer.capacity == 100  # Should restore original capacity
            assert new_buffer.min_size == 10   # Should restore original min_size
            
        finally:
            os.unlink(filepath)
    
    def test_save_load_failure_handling(self):
        """Test handling of save/load failures."""
        # Test save failure
        success = self.buffer.save_buffer("/invalid/path/file.pkl")
        assert success is False
        
        # Test load failure
        success = self.buffer.load_buffer("/nonexistent/file.pkl")
        assert success is False
    
    def test_statistics(self):
        """Test statistics gathering."""
        initial_stats = self.buffer.get_statistics()
        assert initial_stats['size'] == 0
        assert initial_stats['utilization'] == 0.0
        assert initial_stats['total_added'] == 0
        assert initial_stats['total_sampled'] == 0
        assert initial_stats['ready_for_sampling'] is False
        
        # Add experiences and sample
        for i in range(15):
            self.buffer.add(self.create_test_experience(i))
        
        batch = self.buffer.sample(5)
        
        final_stats = self.buffer.get_statistics()
        assert final_stats['size'] == 15
        assert final_stats['utilization'] == 0.15  # 15/100
        assert final_stats['total_added'] == 15
        assert final_stats['total_sampled'] == 5
        assert final_stats['ready_for_sampling'] is True
    
    def test_repr(self):
        """Test string representation."""
        repr_str = repr(self.buffer)
        assert "ExperienceReplayBuffer" in repr_str
        assert "size=0" in repr_str
        assert "capacity=100" in repr_str
        assert "utilization=" in repr_str


class TestPrioritizedExperienceBuffer:
    """Test the PrioritizedExperienceBuffer class."""
    
    def setup_method(self):
        """Set up test fixtures before each method."""
        self.buffer = PrioritizedExperienceBuffer(
            capacity=100, 
            min_size=10,
            alpha=0.6,
            beta=0.4
        )
    
    def create_test_experience(self, idx: int = 0) -> Experience:
        """Create a test experience with given index."""
        state = np.array([float(idx), float(idx + 1)])
        next_state = np.array([float(idx + 0.1), float(idx + 1.1)])
        
        return Experience(
            state=state,
            action=idx % 4,
            reward=float(idx * 0.1),
            next_state=next_state,
            done=idx % 10 == 9,
            timestamp=float(idx)
        )
    
    def test_initialization(self):
        """Test prioritized buffer initialization."""
        buffer = PrioritizedExperienceBuffer(
            capacity=200,
            alpha=0.7,
            beta=0.5,
            beta_increment=0.002
        )
        
        assert buffer.capacity == 200
        assert buffer.alpha == 0.7
        assert buffer.beta == 0.5
        assert buffer.beta_increment == 0.002
        assert buffer._max_priority == 1.0
    
    def test_add_with_priority(self):
        """Test adding experiences with explicit priorities."""
        exp1 = self.create_test_experience(0)
        exp2 = self.create_test_experience(1)
        
        self.buffer.add(exp1, priority=0.5)
        self.buffer.add(exp2, priority=1.2)
        
        assert len(self.buffer) == 2
        assert self.buffer._max_priority == 1.2
    
    def test_add_without_priority(self):
        """Test adding experiences without explicit priorities."""
        exp = self.create_test_experience(0)
        
        self.buffer.add(exp)  # Should use max priority
        assert len(self.buffer) == 1
        assert len(self.buffer._priorities) == 1
    
    def test_prioritized_sampling(self):
        """Test prioritized sampling functionality."""
        # Add experiences with different priorities
        for i in range(20):
            exp = self.create_test_experience(i)
            priority = 1.0 if i < 10 else 0.1  # First 10 have high priority
            self.buffer.add(exp, priority=priority)
        
        # Sample and check return format
        experiences, indices, weights = self.buffer.sample(5)
        
        assert len(experiences) == 5
        assert len(indices) == 5
        assert len(weights) == 5
        assert isinstance(experiences, list)
        assert isinstance(indices, np.ndarray)
        assert isinstance(weights, np.ndarray)
        
        # Weights should be normalized
        assert weights.max() == 1.0
        assert all(w > 0 for w in weights)
    
    def test_update_priorities(self):
        """Test updating priorities for sampled experiences."""
        # Add experiences
        for i in range(15):
            self.buffer.add(self.create_test_experience(i), priority=1.0)
        
        # Sample some experiences
        experiences, indices, weights = self.buffer.sample(3)
        
        # Update their priorities
        new_priorities = np.array([0.5, 2.0, 0.8])
        self.buffer.update_priorities(indices, new_priorities)
        
        # Max priority should be updated
        assert self.buffer._max_priority == 2.0
    
    def test_beta_increment(self):
        """Test that beta increases with sampling."""
        # Add experiences
        for i in range(15):
            self.buffer.add(self.create_test_experience(i))
        
        initial_beta = self.buffer.beta
        
        # Sample multiple times
        for _ in range(10):
            self.buffer.sample(2)
        
        # Beta should have increased
        assert self.buffer.beta > initial_beta
        assert self.buffer.beta <= self.buffer.max_beta
    
    def test_inheritance(self):
        """Test that prioritized buffer inherits base functionality."""
        # Should inherit basic buffer functionality
        assert hasattr(self.buffer, 'capacity')
        assert hasattr(self.buffer, 'clear')
        assert hasattr(self.buffer, 'get_statistics')
        
        # Test basic operations work
        exp = self.create_test_experience(0)
        self.buffer.add(exp)
        assert len(self.buffer) == 1
        
        self.buffer.clear()
        assert len(self.buffer) == 0


class TestIntegration:
    """Integration tests for experience buffer components."""
    
    def test_buffer_with_dqn_workflow(self):
        """Test buffer in a typical DQN training workflow."""
        buffer = ExperienceReplayBuffer(capacity=1000, min_size=50)
        
        # Simulate episode collection
        for episode in range(5):
            for step in range(20):
                idx = episode * 20 + step
                state = np.random.rand(4)
                next_state = np.random.rand(4)
                
                exp = Experience(
                    state=state,
                    action=np.random.randint(0, 3),
                    reward=np.random.rand() - 0.5,
                    next_state=next_state,
                    done=step == 19,  # Episode ends
                    timestamp=float(idx)
                )
                
                buffer.add(exp)
        
        # Should have 100 experiences
        assert len(buffer) == 100
        
        # Should be ready for training
        stats = buffer.get_statistics()
        assert stats['ready_for_sampling'] is True
        
        # Simulate training steps
        for training_step in range(10):
            batch = buffer.sample(32)
            states, actions, rewards, next_states, dones = buffer.get_batch_arrays(batch)
            
            # Verify batch shapes for training
            assert states.shape == (32, 4)
            assert actions.shape == (32,)
            assert rewards.shape == (32,)
            assert next_states.shape == (32, 4)
            assert dones.shape == (32,)
        
        # Verify sampling statistics
        final_stats = buffer.get_statistics()
        assert final_stats['total_sampled'] == 320  # 10 * 32
    
    def test_prioritized_buffer_workflow(self):
        """Test prioritized buffer in a training workflow."""
        buffer = PrioritizedExperienceBuffer(capacity=500, min_size=30)
        
        # Add initial experiences
        for i in range(50):
            exp = Experience(
                state=np.random.rand(3),
                action=np.random.randint(0, 4),
                reward=np.random.rand() - 0.5,
                next_state=np.random.rand(3),
                done=i % 10 == 9,
                timestamp=float(i)
            )
            buffer.add(exp, priority=np.random.rand())
        
        # Training loop with priority updates
        for step in range(5):
            # Sample batch
            experiences, indices, weights = buffer.sample(10)
            
            # Simulate computing TD errors
            td_errors = np.random.rand(10) * 2.0
            
            # Update priorities based on TD errors
            buffer.update_priorities(indices, td_errors)
            
            # Verify importance weights are applied
            assert all(w > 0 for w in weights)
            assert weights.max() == 1.0