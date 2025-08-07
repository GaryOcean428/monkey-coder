"""
Performance validation tests for Experience Replay Buffer.

These tests validate that the buffer meets the specification requirements:
- Maintains performance under 1000+ concurrent operations
- Efficient memory usage
- Sub-millisecond operation times for individual operations
"""

import pytest
import time
import threading
import concurrent.futures
import numpy as np
from typing import List

from monkey_coder.quantum.experience_buffer import Experience, ExperienceBuffer


class TestExperienceBufferPerformance:
    """Performance and load testing for Experience Replay Buffer."""

    def test_single_operation_performance(self):
        """Test individual operations complete in sub-millisecond time."""
        buffer = ExperienceBuffer(max_size=10000)
        
        # Pre-fill buffer for sampling tests
        for i in range(1000):
            experience = Experience(
                state=np.array([i]),
                action=i,
                reward=float(i),
                next_state=np.array([i+1]),
                done=False
            )
            buffer.add_experience(experience)
        
        # Test add_experience performance
        experience = Experience(
            state=np.array([9999]),
            action=9999,
            reward=9999.0,
            next_state=np.array([10000]),
            done=False
        )
        
        start_time = time.perf_counter()
        buffer.add_experience(experience)
        add_time = time.perf_counter() - start_time
        
        # Test sample_batch performance
        start_time = time.perf_counter()
        batch = buffer.sample_batch(batch_size=32)
        sample_time = time.perf_counter() - start_time
        
        # Performance requirements (very generous for reliability)
        assert add_time < 0.001, f"add_experience took {add_time:.6f}s, should be < 1ms"
        assert sample_time < 0.010, f"sample_batch took {sample_time:.6f}s, should be < 10ms"
        assert len(batch) == 32

    def test_concurrent_load_1000_operations(self):
        """Test buffer maintains performance under 1000+ concurrent operations."""
        buffer = ExperienceBuffer(max_size=2000)
        num_threads = 50
        operations_per_thread = 20  # Total: 1000 operations
        
        results = {'adds': [], 'samples': [], 'errors': []}
        
        def worker_add_operations(thread_id: int):
            """Worker that performs add operations."""
            try:
                for i in range(operations_per_thread):
                    experience = Experience(
                        state=np.array([thread_id, i]),
                        action=thread_id * 1000 + i,
                        reward=float(thread_id + i),
                        next_state=np.array([thread_id, i+1]),
                        done=False
                    )
                    start_time = time.perf_counter()
                    buffer.add_experience(experience)
                    operation_time = time.perf_counter() - start_time
                    results['adds'].append(operation_time)
            except Exception as e:
                results['errors'].append(f"Add worker {thread_id}: {e}")
        
        def worker_sample_operations():
            """Worker that performs sample operations."""
            try:
                # Wait a bit for some data to be added
                time.sleep(0.01)
                
                for _ in range(operations_per_thread):
                    if buffer.size() >= 10:  # Only sample if enough data
                        start_time = time.perf_counter()
                        batch = buffer.sample_batch(batch_size=10)
                        operation_time = time.perf_counter() - start_time
                        results['samples'].append(operation_time)
            except Exception as e:
                results['errors'].append(f"Sample worker: {e}")
        
        # Start threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads + 5) as executor:
            # Submit add workers
            add_futures = [
                executor.submit(worker_add_operations, i) 
                for i in range(num_threads)
            ]
            
            # Submit sample workers
            sample_futures = [
                executor.submit(worker_sample_operations) 
                for _ in range(5)
            ]
            
            # Wait for completion
            concurrent.futures.wait(add_futures + sample_futures)
        
        # Validate results
        assert len(results['errors']) == 0, f"Errors occurred: {results['errors']}"
        assert len(results['adds']) == num_threads * operations_per_thread
        
        # Performance validation
        avg_add_time = sum(results['adds']) / len(results['adds'])
        if results['samples']:
            avg_sample_time = sum(results['samples']) / len(results['samples'])
            assert avg_sample_time < 0.050, f"Average sample time {avg_sample_time:.6f}s too high"
        
        assert avg_add_time < 0.010, f"Average add time {avg_add_time:.6f}s too high"
        assert buffer.size() <= buffer.max_size  # Should not exceed capacity

    def test_memory_usage_under_load(self):
        """Test memory usage remains reasonable under high load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        buffer = ExperienceBuffer(max_size=5000)
        
        # Fill buffer with large experiences
        for i in range(10000):  # More than buffer capacity
            large_state = np.random.random(100)  # 100-element state vector
            experience = Experience(
                state=large_state,
                action=i % 10,
                reward=np.random.random(),
                next_state=np.random.random(100),
                done=i % 100 == 0
            )
            buffer.add_experience(experience)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory should not grow excessively (allowing 100MB increase)
        assert memory_increase < 100, f"Memory increased by {memory_increase:.1f}MB, should be < 100MB"
        assert buffer.size() == buffer.max_size  # Should be at capacity

    def test_throughput_requirements(self):
        """Test buffer can handle required throughput for quantum routing."""
        buffer = ExperienceBuffer(max_size=10000)
        
        # Pre-fill buffer
        for i in range(1000):
            experience = Experience(
                state=np.array([i]),
                action=i,
                reward=float(i),
                next_state=np.array([i+1]),
                done=False
            )
            buffer.add_experience(experience)
        
        # Test throughput: Should handle 100 operations per second minimum
        num_operations = 100
        batch_size = 32
        
        start_time = time.perf_counter()
        for _ in range(num_operations):
            batch = buffer.sample_batch(batch_size)
            assert len(batch) == batch_size
        
        total_time = time.perf_counter() - start_time
        ops_per_second = num_operations / total_time
        
        # Should easily handle 100 ops/second (quantum routing requirement)
        assert ops_per_second > 100, f"Throughput {ops_per_second:.1f} ops/s, should be > 100 ops/s"

    def test_scalability_with_large_buffers(self):
        """Test performance scales reasonably with large buffer sizes."""
        small_buffer = ExperienceBuffer(max_size=1000)
        large_buffer = ExperienceBuffer(max_size=50000)
        
        # Fill both buffers
        for i in range(1000):
            experience = Experience(
                state=np.array([i]),
                action=i,
                reward=float(i),
                next_state=np.array([i+1]),
                done=False
            )
            small_buffer.add_experience(experience)
        
        for i in range(10000):
            experience = Experience(
                state=np.array([i]),
                action=i,
                reward=float(i),
                next_state=np.array([i+1]),
                done=False
            )
            large_buffer.add_experience(experience)
        
        # Test sampling performance
        start_time = time.perf_counter()
        small_batch = small_buffer.sample_batch(100)
        small_time = time.perf_counter() - start_time
        
        start_time = time.perf_counter()
        large_batch = large_buffer.sample_batch(100)
        large_time = time.perf_counter() - start_time
        
        # Large buffer shouldn't be significantly slower
        assert len(small_batch) == 100
        assert len(large_batch) == 100
        assert large_time < small_time * 10, f"Large buffer too slow: {large_time:.6f}s vs {small_time:.6f}s"

    def test_concurrent_add_sample_stress(self):
        """Stress test with concurrent adds and samples."""
        buffer = ExperienceBuffer(max_size=1000)
        duration_seconds = 2.0
        results = {'add_count': 0, 'sample_count': 0, 'errors': []}
        stop_event = threading.Event()
        
        def add_worker():
            """Continuously add experiences."""
            i = 0
            while not stop_event.is_set():
                try:
                    experience = Experience(
                        state=np.array([i]),
                        action=i % 10,
                        reward=float(i),
                        next_state=np.array([i+1]),
                        done=False
                    )
                    buffer.add_experience(experience)
                    results['add_count'] += 1
                    i += 1
                except Exception as e:
                    results['errors'].append(f"Add: {e}")
        
        def sample_worker():
            """Continuously sample experiences."""
            while not stop_event.is_set():
                try:
                    if buffer.size() >= 10:
                        batch = buffer.sample_batch(5)
                        if len(batch) == 5:
                            results['sample_count'] += 1
                except Exception as e:
                    results['errors'].append(f"Sample: {e}")
                time.sleep(0.001)  # Small delay to allow adds
        
        # Start workers
        add_thread = threading.Thread(target=add_worker)
        sample_thread = threading.Thread(target=sample_worker)
        
        start_time = time.perf_counter()
        add_thread.start()
        sample_thread.start()
        
        # Run for specified duration
        time.sleep(duration_seconds)
        stop_event.set()
        
        add_thread.join()
        sample_thread.join()
        
        elapsed_time = time.perf_counter() - start_time
        
        # Validate results
        assert len(results['errors']) == 0, f"Errors: {results['errors']}"
        
        add_rate = results['add_count'] / elapsed_time
        sample_rate = results['sample_count'] / elapsed_time
        
        # Should achieve reasonable throughput under stress
        assert add_rate > 100, f"Add rate {add_rate:.1f}/s too low"
        assert sample_rate > 10, f"Sample rate {sample_rate:.1f}/s too low"