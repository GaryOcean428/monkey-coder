"""
Test suite for Experience Replay Buffer

This module tests the experience replay buffer implementation,
ensuring it follows proven multi-agent patterns and meets
the requirements for quantum routing DQN training.
"""

import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from monkey_coder.quantum.experience_buffer import Experience, ExperienceBuffer


class TestExperience(unittest.TestCase):
    """Test cases for Experience dataclass."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_state = np.array([0.1, 0.2, 0.3, 0.4, 0.5], dtype=np.float32)
        self.sample_next_state = np.array([0.2, 0.3, 0.4, 0.5, 0.6], dtype=np.float32)

        self.experience = Experience(
            state=self.sample_state,
            action=2,
            reward=1.5,
            next_state=self.sample_next_state,
            done=False,
            timestamp=1234567890.0,
            priority=1.0
        )

    def test_experience_creation(self):
        """Test that Experience is created correctly."""
        self.assertEqual(self.experience.action, 2)
        self.assertEqual(self.experience.reward, 1.5)
        self.assertFalse(self.experience.done)
        self.assertEqual(self.experience.priority, 1.0)
        self.assertEqual(self.experience.timestamp, 1234567890.0)
        np.testing.assert_array_equal(self.experience.state, self.sample_state)
        np.testing.assert_array_equal(self.experience.next_state, self.sample_next_state)

    def test_experience_to_tuple(self):
        """Test conversion to tuple format."""
        tuple_exp = self.experience.to_tuple()

        self.assertIsInstance(tuple_exp, tuple)
        self.assertEqual(len(tuple_exp), 5)

        state, action, reward, next_state, done = tuple_exp
        np.testing.assert_array_equal(state, self.sample_state)
        self.assertEqual(action, 2)
        self.assertEqual(reward, 1.5)
        np.testing.assert_array_equal(next_state, self.sample_next_state)
        self.assertFalse(done)

    def test_experience_default_priority(self):
        """Test default priority value."""
        exp = Experience(
            state=self.sample_state,
            action=1,
            reward=0.5,
            next_state=self.sample_next_state,
            done=True,
            timestamp=1234567890.0
        )
        self.assertEqual(exp.priority, 1.0)  # Default value


class TestExperienceBuffer(unittest.TestCase):
    """Test cases for ExperienceBuffer."""

    def setUp(self):
        """Set up test fixtures."""
        self.buffer = ExperienceBuffer(
            max_size=100,
            min_size_for_sampling=10,
            auto_cleanup_threshold=0.9,
            enable_priority_sampling=False,
            random_seed=42
        )

        self.sample_state = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        self.sample_next_state = np.array([0.2, 0.3, 0.4], dtype=np.float32)

    def test_buffer_initialization(self):
        """Test buffer initialization with default parameters."""
        buffer = ExperienceBuffer()

        self.assertEqual(buffer.max_size, 2000)  # Default
        self.assertEqual(buffer.min_size_for_sampling, 32)  # Default
        self.assertEqual(buffer.auto_cleanup_threshold, 0.9)  # Default
        self.assertFalse(buffer.enable_priority_sampling)
        self.assertEqual(len(buffer), 0)
        self.assertFalse(buffer)

    def test_buffer_initialization_custom_params(self):
        """Test buffer initialization with custom parameters."""
        buffer = ExperienceBuffer(
            max_size=500,
            min_size_for_sampling=20,
            auto_cleanup_threshold=0.8,
            enable_priority_sampling=True,
            random_seed=123
        )

        self.assertEqual(buffer.max_size, 500)
        self.assertEqual(buffer.min_size_for_sampling, 20)
        self.assertEqual(buffer.auto_cleanup_threshold, 0.8)
        self.assertTrue(buffer.enable_priority_sampling)

    def test_add_experience(self):
        """Test adding experiences to buffer."""
        initial_size = len(self.buffer)

        self.buffer.add(
            state=self.sample_state,
            action=1,
            reward=0.5,
            next_state=self.sample_next_state,
            done=False
        )

        self.assertEqual(len(self.buffer), initial_size + 1)
        self.assertTrue(self.buffer)
        self.assertEqual(self.buffer._total_experiences_added, 1)

    def test_add_multiple_experiences(self):
        """Test adding multiple experiences."""
        for i in range(5):
            state = np.array([i * 0.1, i * 0.2, i * 0.3], dtype=np.float32)
            next_state = np.array([(i + 1) * 0.1, (i + 1) * 0.2, (i + 1) * 0.3], dtype=np.float32)

            self.buffer.add(
                state=state,
                action=i,
                reward=float(i) * 0.1,
                next_state=next_state,
                done=(i == 4)  # Last experience is done
            )

        self.assertEqual(len(self.buffer), 5)
        self.assertEqual(self.buffer._total_experiences_added, 5)

    def test_add_experience_with_priority(self):
        """Test adding experience with custom priority."""
        self.buffer.add(
            state=self.sample_state,
            action=1,
            reward=0.5,
            next_state=self.sample_next_state,
            done=False,
            priority=2.5
        )

        experience = self.buffer._buffer[0]
        self.assertEqual(experience.priority, 2.5)

    def test_sample_insufficient_experiences(self):
        """Test sampling when buffer has insufficient experiences."""
        # Add fewer experiences than min_size_for_sampling
        for i in range(5):  # Less than min_size_for_sampling=10
            self.buffer.add(
                state=self.sample_state,
                action=i,
                reward=0.1,
                next_state=self.sample_next_state,
                done=False
            )

        batch = self.buffer.sample(batch_size=5)
        self.assertIsNone(batch)

    def test_sample_sufficient_experiences(self):
        """Test sampling when buffer has sufficient experiences."""
        # Add enough experiences for sampling
        for i in range(15):  # More than min_size_for_sampling=10
            state = np.array([i * 0.1, i * 0.2, i * 0.3], dtype=np.float32)
            next_state = np.array([(i + 1) * 0.1, (i + 1) * 0.2, (i + 1) * 0.3], dtype=np.float32)

            self.buffer.add(
                state=state,
                action=i,
                reward=float(i) * 0.1,
                next_state=next_state,
                done=False
            )

        batch = self.buffer.sample(batch_size=5)

        self.assertIsNotNone(batch)
        assert batch is not None  # Type assertion for mypy
        self.assertEqual(len(batch), 5)

        # Check that all experiences are valid tuples
        for experience in batch:
            self.assertIsInstance(experience, tuple)
            self.assertEqual(len(experience), 5)
            state, action, reward, next_state, done = experience
            self.assertIsInstance(state, np.ndarray)
            self.assertIsInstance(action, (int, np.integer))
            self.assertIsInstance(reward, (float, np.floating))
            self.assertIsInstance(next_state, np.ndarray)
            self.assertIsInstance(done, bool)

    def test_sample_batch_size_larger_than_buffer(self):
        """Test sampling when batch size is larger than buffer."""
        # Add fewer experiences than requested batch size but enough for sampling
        for i in range(15):  # More than min_size_for_sampling=10 but less than batch_size=20
            self.buffer.add(
                state=self.sample_state,
                action=i,
                reward=0.1,
                next_state=self.sample_next_state,
                done=False
            )

        # Should reduce batch size to buffer size
        batch = self.buffer.sample(batch_size=20)
        self.assertIsNotNone(batch)
        assert batch is not None  # Type assertion for mypy
        self.assertEqual(len(batch), 15)

    def test_auto_cleanup(self):
        """Test automatic cleanup when buffer is nearly full."""
        # Create a small buffer for easier testing
        small_buffer = ExperienceBuffer(
            max_size=10,
            min_size_for_sampling=3,
            auto_cleanup_threshold=0.8  # Cleanup at 80% = 8 experiences
        )

        # Add experiences up to cleanup threshold
        for i in range(8):
            state = np.array([i * 0.1], dtype=np.float32)
            next_state = np.array([(i + 1) * 0.1], dtype=np.float32)
            small_buffer.add(
                state=state,
                action=i,
                reward=0.1,
                next_state=next_state,
                done=False
            )

        # Should trigger cleanup on next add
        state = np.array([0.9], dtype=np.float32)
        next_state = np.array([1.0], dtype=np.float32)
        small_buffer.add(
            state=state,
            action=8,
            reward=0.1,
            next_state=next_state,
            done=False
        )

        # Buffer should be cleaned up to 70% of max_size = 7 experiences
        self.assertEqual(len(small_buffer), 7)
        self.assertEqual(small_buffer._cleanup_count, 1)

        # Should contain the most recent experiences
        latest_experience = small_buffer._buffer[-1]
        np.testing.assert_array_equal(latest_experience.state, state)
        self.assertEqual(latest_experience.action, 8)

    def test_update_priorities_disabled(self):
        """Test priority updates when priority sampling is disabled."""
        self.buffer.add(
            state=self.sample_state,
            action=1,
            reward=0.5,
            next_state=self.sample_next_state,
            done=False
        )

        # Should log warning but not crash
        with patch('monkey_coder.quantum.experience_buffer.logger') as mock_logger:
            self.buffer.update_priorities([0], [2.0])
            mock_logger.warning.assert_called_once_with("Priority sampling not enabled, ignoring priority updates")

    def test_update_priorities_enabled(self):
        """Test priority updates when priority sampling is enabled."""
        buffer = ExperienceBuffer(enable_priority_sampling=True)

        # Add multiple experiences
        for i in range(3):
            state = np.array([i * 0.1], dtype=np.float32)
            next_state = np.array([(i + 1) * 0.1], dtype=np.float32)
            buffer.add(
                state=state,
                action=i,
                reward=0.1,
                next_state=next_state,
                done=False
            )

        # Update priorities
        buffer.update_priorities([0, 2], [2.0, 3.0])

        # Check that priorities were updated
        self.assertEqual(buffer._buffer[0].priority, 2.0)
        self.assertEqual(buffer._buffer[2].priority, 3.0)
        # Middle experience should keep default priority
        self.assertEqual(buffer._buffer[1].priority, 1.0)

    def test_update_priorities_invalid_indices(self):
        """Test priority updates with invalid indices."""
        buffer = ExperienceBuffer(enable_priority_sampling=True)

        buffer.add(
            state=self.sample_state,
            action=1,
            reward=0.5,
            next_state=self.sample_next_state,
            done=False
        )

        with patch('monkey_coder.quantum.experience_buffer.logger') as mock_logger:
            buffer.update_priorities([0, 1], [2.0])  # Mismatched lengths
            mock_logger.error.assert_called_once_with("Mismatch between indices and priorities length")

    def test_get_recent_experiences(self):
        """Test getting recent experiences."""
        # Add multiple experiences
        for i in range(15):
            state = np.array([i * 0.1], dtype=np.float32)
            next_state = np.array([(i + 1) * 0.1], dtype=np.float32)
            self.buffer.add(
                state=state,
                action=i,
                reward=float(i) * 0.1,
                next_state=next_state,
                done=False
            )

        recent = self.buffer.get_recent_experiences(count=5)
        self.assertEqual(len(recent), 5)

        # Should be the most recent experiences (highest action numbers)
        for i, exp in enumerate(recent):
            self.assertEqual(exp.action, 10 + i)  # Last 5 actions: 10, 11, 12, 13, 14

    def test_get_recent_experiences_buffer_smaller_than_count(self):
        """Test getting recent experiences when buffer is smaller than requested count."""
        # Add only 3 experiences
        for i in range(3):
            self.buffer.add(
                state=self.sample_state,
                action=i,
                reward=0.1,
                next_state=self.sample_next_state,
                done=False
            )

        recent = self.buffer.get_recent_experiences(count=10)
        self.assertEqual(len(recent), 3)  # Should return all experiences

    def test_get_experiences_by_reward(self):
        """Test getting experiences by reward threshold."""
        # Add experiences with different rewards
        rewards = [0.1, 0.5, 0.8, 1.2, 0.3, 0.9, 1.5]
        for i, reward in enumerate(rewards):
            state = np.array([i * 0.1], dtype=np.float32)
            next_state = np.array([(i + 1) * 0.1], dtype=np.float32)
            self.buffer.add(
                state=state,
                action=i,
                reward=reward,
                next_state=next_state,
                done=False
            )

        high_reward_experiences = self.buffer.get_experiences_by_reward(threshold=0.7, top_n=3)

        # Should return experiences with reward >= 0.7, sorted by reward (descending)
        self.assertEqual(len(high_reward_experiences), 3)
        self.assertEqual(high_reward_experiences[0].reward, 1.5)  # Highest
        self.assertEqual(high_reward_experiences[1].reward, 1.2)
        self.assertEqual(high_reward_experiences[2].reward, 0.9)

    def test_get_experiences_by_reward_no_matches(self):
        """Test getting experiences by reward when none match threshold."""
        for i in range(5):
            self.buffer.add(
                state=self.sample_state,
                action=i,
                reward=0.1,  # All low rewards
                next_state=self.sample_next_state,
                done=False
            )

        high_reward_experiences = self.buffer.get_experiences_by_reward(threshold=0.5, top_n=3)
        self.assertEqual(len(high_reward_experiences), 0)

    def test_clear_buffer(self):
        """Test clearing the buffer."""
        # Add some experiences
        for i in range(5):
            self.buffer.add(
                state=self.sample_state,
                action=i,
                reward=0.1,
                next_state=self.sample_next_state,
                done=False
            )

        self.assertEqual(len(self.buffer), 5)
        self.assertTrue(self.buffer)

        self.buffer.clear()

        self.assertEqual(len(self.buffer), 0)
        self.assertFalse(self.buffer)
        self.assertEqual(self.buffer._average_reward, 0.0)
        self.assertEqual(len(self.buffer._reward_history), 0)

    def test_get_statistics_empty_buffer(self):
        """Test getting statistics for empty buffer."""
        stats = self.buffer.get_statistics()

        expected_keys = [
            "size", "max_size", "utilization", "total_added", "total_sampled",
            "cleanup_count", "average_reward", "can_sample"
        ]

        for key in expected_keys:
            self.assertIn(key, stats)

        self.assertEqual(stats["size"], 0)
        self.assertEqual(stats["utilization"], 0.0)
        self.assertEqual(stats["average_reward"], 0.0)
        self.assertFalse(stats["can_sample"])

    def test_get_statistics_populated_buffer(self):
        """Test getting statistics for populated buffer."""
        # Add experiences with known properties
        for i in range(20):
            state = np.array([i * 0.1], dtype=np.float32)
            next_state = np.array([(i + 1) * 0.1], dtype=np.float32)
            self.buffer.add(
                state=state,
                action=i % 5,  # Cycle through actions 0-4
                reward=float(i) * 0.1,
                next_state=next_state,
                done=False
            )

        stats = self.buffer.get_statistics()

        self.assertEqual(stats["size"], 20)
        self.assertEqual(stats["utilization"], 20 / 100)  # 20/100 = 0.2
        self.assertEqual(stats["total_added"], 20)
        self.assertTrue(stats["can_sample"])

        # Check reward statistics
        reward_stats = stats["reward_statistics"]
        self.assertAlmostEqual(reward_stats["average"], 0.95)  # Average of 0.0 to 1.9
        self.assertEqual(reward_stats["min"], 0.0)
        self.assertAlmostEqual(reward_stats["max"], 1.9)  # Use assertAlmostEqual for float comparison

        # Check action distribution
        action_dist = stats["action_distribution"]
        self.assertEqual(len(action_dist), 5)  # Actions 0-4
        for action in range(5):
            self.assertEqual(action_dist[action], 4)  # Each action appears 4 times

        # Check age statistics
        age_stats = stats["age_statistics"]
        self.assertGreater(age_stats["average_age"], 0)
        self.assertGreater(age_stats["max_age"], 0)

    def test_save_and_load_buffer(self):
        """Test saving and loading buffer to/from file."""
        # Add some experiences
        for i in range(10):
            state = np.array([i * 0.1, i * 0.2], dtype=np.float32)
            next_state = np.array([(i + 1) * 0.1, (i + 1) * 0.2], dtype=np.float32)
            self.buffer.add(
                state=state,
                action=i,
                reward=float(i) * 0.1,
                next_state=next_state,
                done=(i == 9)
            )

        original_stats = self.buffer.get_statistics()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pkl") as tmp:
            filepath = tmp.name

        try:
            # Save buffer
            success = self.buffer.save_to_file(filepath)
            self.assertTrue(success)

            # Create new buffer and load
            new_buffer = ExperienceBuffer()
            success = new_buffer.load_from_file(filepath)
            self.assertTrue(success)

            # Check that buffer was loaded correctly
            self.assertEqual(len(new_buffer), len(self.buffer))
            self.assertEqual(new_buffer.max_size, self.buffer.max_size)
            self.assertEqual(new_buffer._total_experiences_added, self.buffer._total_experiences_added)

            # Check that experiences are identical
            for i, (orig_exp, loaded_exp) in enumerate(zip(self.buffer._buffer, new_buffer._buffer)):
                np.testing.assert_array_equal(orig_exp.state, loaded_exp.state)
                np.testing.assert_array_equal(orig_exp.next_state, loaded_exp.next_state)
                self.assertEqual(orig_exp.action, loaded_exp.action)
                self.assertAlmostEqual(orig_exp.reward, loaded_exp.reward)
                self.assertEqual(orig_exp.done, loaded_exp.done)
                self.assertEqual(orig_exp.priority, loaded_exp.priority)

            # Check statistics
            loaded_stats = new_buffer.get_statistics()
            self.assertEqual(loaded_stats["size"], original_stats["size"])
            self.assertEqual(loaded_stats["total_added"], original_stats["total_added"])

        finally:
            # Clean up
            import os
            try:
                os.unlink(filepath)
            except FileNotFoundError:
                pass

    def test_save_and_load_nonexistent_file(self):
        """Test loading from non-existent file."""
        success = self.buffer.load_from_file("/nonexistent/file.pkl")
        self.assertFalse(success)

    def test_buffer_repr(self):
        """Test buffer string representation."""
        # Empty buffer
        self.assertEqual(
            repr(self.buffer),
            "ExperienceBuffer(size=0/100, can_sample=False)"
        )

        # Add some experiences (but not enough for sampling)
        for i in range(5):  # Less than min_size_for_sampling=10
            self.buffer.add(
                state=self.sample_state,
                action=i,
                reward=0.1,
                next_state=self.sample_next_state,
                done=False
            )

        self.assertEqual(
            repr(self.buffer),
            "ExperienceBuffer(size=5/100, can_sample=False)"
        )

        # Add enough experiences for sampling
        for i in range(5, 15):  # Total 15, which is >= min_size_for_sampling=10
            state = np.array([i * 0.1], dtype=np.float32)
            next_state = np.array([(i + 1) * 0.1], dtype=np.float32)
            self.buffer.add(
                state=state,
                action=i,
                reward=0.1,
                next_state=next_state,
                done=False
            )

        self.assertEqual(
            repr(self.buffer),
            "ExperienceBuffer(size=15/100, can_sample=True)"
        )

    def test_buffer_max_size_enforcement(self):
        """Test that buffer respects max_size limit."""
        # Fill buffer beyond max_size
        for i in range(150):  # More than max_size=100
            state = np.array([i * 0.01], dtype=np.float32)
            next_state = np.array([(i + 1) * 0.01], dtype=np.float32)
            self.buffer.add(
                state=state,
                action=i,
                reward=0.01,
                next_state=next_state,
                done=False
            )

        # Buffer should not exceed max_size
        self.assertEqual(len(self.buffer), 100)

        # Should contain the most recent experiences
        latest_experience = self.buffer._buffer[-1]
        self.assertEqual(latest_experience.action, 149)  # Last action added


class TestExperienceBufferIntegration(unittest.TestCase):
    """Integration tests for ExperienceBuffer with realistic usage patterns."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.buffer = ExperienceBuffer(
            max_size=50,
            min_size_for_sampling=10,
            auto_cleanup_threshold=0.8
        )

    def test_realistic_training_scenario(self):
        """Test buffer behavior in a realistic training scenario."""
        # Simulate a training episode with multiple experiences
        episode_rewards = []

        for episode in range(3):
            episode_states = []
            episode_actions = []

            # Generate episode experiences
            for step in range(20):
                state = np.array([episode * 0.1, step * 0.05], dtype=np.float32)
                action = step % 5  # Cycle through actions
                reward = 0.1 + (step * 0.05) + (episode * 0.02)  # Increasing reward
                next_state = np.array([episode * 0.1, (step + 1) * 0.05], dtype=np.float32)
                done = (step == 19)  # Last step of episode

                self.buffer.add(
                    state=state,
                    action=action,
                    reward=reward,
                    next_state=next_state,
                    done=done
                )

                episode_states.append(state)
                episode_actions.append(action)

                if done:
                    episode_rewards.append(reward)

        # Check buffer statistics
        stats = self.buffer.get_statistics()
        # Buffer should have auto-cleaned when it reached 40 experiences (80% of 50)
        # and been reduced to 35 experiences (70% of 50), then continued adding
        # but max_size is 50, so final size should be 50
        self.assertEqual(stats["size"], 50)  # max_size=50
        self.assertEqual(stats["total_added"], 60)
        self.assertTrue(stats["can_sample"])

        # Test sampling
        batch = self.buffer.sample(batch_size=16)
        self.assertIsNotNone(batch)
        assert batch is not None  # Type assertion for mypy
        self.assertEqual(len(batch), 16)

        # Verify batch contents
        for experience in batch:
            state, action, reward, next_state, done = experience
            self.assertIsInstance(state, np.ndarray)
            self.assertIsInstance(action, (int, np.integer))
            self.assertIsInstance(reward, (float, np.floating))
            self.assertIsInstance(next_state, np.ndarray)
            self.assertIsInstance(done, bool)
            self.assertEqual(len(state), 2)  # State dimension
            self.assertEqual(len(next_state), 2)  # Next state dimension

        # Test getting high-reward experiences
        high_reward_experiences = self.buffer.get_experiences_by_reward(threshold=0.8, top_n=5)
        self.assertGreater(len(high_reward_experiences), 0)

        # All high-reward experiences should have reward >= 0.8
        for exp in high_reward_experiences:
            self.assertGreaterEqual(exp.reward, 0.8)

        # Test getting recent experiences
        recent_experiences = self.buffer.get_recent_experiences(count=10)
        self.assertEqual(len(recent_experiences), 10)

        # Recent experiences should be from the end of the last episode
        for exp in recent_experiences:
            self.assertGreaterEqual(exp.action, 0)
            self.assertLessEqual(exp.action, 4)  # Actions cycle 0-4

    def test_buffer_performance_with_large_data(self):
        """Test buffer performance with larger amounts of data."""
        import time

        # Add many experiences quickly
        start_time = time.time()

        for i in range(1000):
            state = np.random.rand(10).astype(np.float32)  # 10-dimensional state
            action = i % 12  # 12 possible actions
            reward = np.random.random()  # Random reward
            next_state = np.random.rand(10).astype(np.float32)
            done = (i % 50 == 49)  # Episode ends every 50 steps

            self.buffer.add(
                state=state,
                action=action,
                reward=reward,
                next_state=next_state,
                done=done
            )

        add_time = time.time() - start_time

        # Check that buffer respects max_size
        self.assertEqual(len(self.buffer), 50)  # max_size=50

        # Test sampling performance
        start_time = time.time()
        for _ in range(100):  # Sample 100 times
            batch = self.buffer.sample(batch_size=16)
            self.assertIsNotNone(batch)
            assert batch is not None  # Type assertion for mypy
            self.assertEqual(len(batch), 16)

        sample_time = time.time() - start_time

        # Performance should be reasonable (these are loose bounds)
        self.assertLess(add_time, 1.0)  # Should add 1000 experiences in < 1 second
        self.assertLess(sample_time, 1.0)  # Should sample 100 batches in < 1 second

        # Check statistics
        stats = self.buffer.get_statistics()
        self.assertEqual(stats["size"], 50)
        self.assertEqual(stats["total_added"], 1000)
        self.assertEqual(stats["total_sampled"], 1600)  # 100 batches * 16 samples
        self.assertGreater(stats["cleanup_count"], 0)  # Should have done cleanup

        # Check reward statistics
        reward_stats = stats["reward_statistics"]
        self.assertGreaterEqual(reward_stats["average"], 0.0)
        self.assertLessEqual(reward_stats["average"], 1.0)
        self.assertGreaterEqual(reward_stats["min"], 0.0)
        self.assertLessEqual(reward_stats["max"], 1.0)


if __name__ == "__main__":
    unittest.main()
