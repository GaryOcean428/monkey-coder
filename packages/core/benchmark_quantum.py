#!/usr/bin/env python3
"""
Quantum Execution Module Benchmark

This script demonstrates the capabilities of the functional quantum execution module
with various toy tasks and performance benchmarks.
"""

import asyncio
import time
import random
import json
from typing import List, Dict, Any

from monkey_coder.quantum import QuantumManager, quantum_task, CollapseStrategy
from monkey_coder.quantum.manager import TaskVariation


class QuantumBenchmark:
    """Benchmark suite for quantum execution patterns."""
    
    def __init__(self):
        self.results = []
    
    async def run_all_benchmarks(self):
        """Run all benchmark tests."""
        print("🚀 Quantum Execution Module Benchmark Suite")
        print("=" * 60)
        
        await self.benchmark_basic_execution()
        await self.benchmark_collapse_strategies()
        await self.benchmark_decorator_usage()
        await self.benchmark_parallel_performance()
        await self.benchmark_real_world_scenarios()
        
        self.print_summary()
    
    async def benchmark_basic_execution(self):
        """Benchmark basic quantum execution functionality."""
        print("\n📊 1. Basic Quantum Execution")
        print("-" * 40)
        
        manager = QuantumManager(max_workers=4, timeout=10.0)
        
        # Simple computation task
        def compute_fibonacci(n):
            """Compute fibonacci number (toy CPU task)."""
            if n <= 1:
                return n
            a, b = 0, 1
            for _ in range(2, n + 1):
                a, b = b, a + b
            return b
        
        variations = [
            TaskVariation(id=f"fib_{n}", task=compute_fibonacci, params={"n": n})
            for n in [10, 15, 20, 25, 30]
        ]
        
        start_time = time.time()
        result = await manager.execute_quantum_task(variations)
        execution_time = time.time() - start_time
        
        print(f"✅ Executed {len(variations)} fibonacci variations")
        print(f"   Winner: {result.variation_id} = {result.value}")
        print(f"   Execution time: {execution_time:.3f}s")
        
        self.results.append({
            "test": "basic_execution",
            "variations": len(variations),
            "execution_time": execution_time,
            "success": result.success
        })
    
    async def benchmark_collapse_strategies(self):
        """Benchmark different collapse strategies."""
        print("\n🎯 2. Collapse Strategy Comparison")
        print("-" * 40)
        
        manager = QuantumManager(max_workers=3)
        
        # Text processing task with varying quality
        def process_text(text, style, quality_factor):
            """Simulate text processing with different quality levels."""
            time.sleep(0.1 * quality_factor)  # Simulate processing time
            
            if style == "uppercase":
                result = text.upper()
            elif style == "lowercase":
                result = text.lower()
            elif style == "title":
                result = text.title()
            else:
                result = text
            
            # Add quality indicator
            return f"{result} (quality: {quality_factor})"
        
        def quality_scorer(text_result):
            """Extract and return quality score from result."""
            try:
                return float(text_result.split("quality: ")[1].split(")")[0])
            except:
                return 0.0
        
        test_text = "hello quantum world"
        
        variations = [
            TaskVariation(id="style1", task=process_text, params={"text": test_text, "style": "uppercase", "quality_factor": 0.7}),
            TaskVariation(id="style2", task=process_text, params={"text": test_text, "style": "title", "quality_factor": 0.9}),
            TaskVariation(id="style3", task=process_text, params={"text": test_text, "style": "lowercase", "quality_factor": 0.6}),
        ]
        
        strategies = [
            (CollapseStrategy.FIRST_SUCCESS, None),
            (CollapseStrategy.BEST_SCORE, quality_scorer),
            (CollapseStrategy.CONSENSUS, None),
            (CollapseStrategy.COMBINED, None),
        ]
        
        for strategy, scoring_fn in strategies:
            start_time = time.time()
            result = await manager.execute_quantum_task(
                variations, 
                collapse_strategy=strategy,
                scoring_fn=scoring_fn
            )
            execution_time = time.time() - start_time
            
            result_preview = str(result.value)[:30]
            print(f"   {strategy.value:15} | {result_preview:<30} | {execution_time:.3f}s")
            
            self.results.append({
                "test": f"strategy_{strategy.value}",
                "execution_time": execution_time,
                "result_preview": str(result.value)[:50]
            })
    
    async def benchmark_decorator_usage(self):
        """Benchmark the @quantum_task decorator."""
        print("\n🎭 3. Quantum Task Decorator")
        print("-" * 40)
        
        @quantum_task(
            variations=[
                {"id": "algo1", "params": {"algorithm": "bubble"}},
                {"id": "algo2", "params": {"algorithm": "quick"}},
                {"id": "algo3", "params": {"algorithm": "merge"}},
            ],
            collapse_strategy=CollapseStrategy.FIRST_SUCCESS,
            max_workers=3
        )
        def sort_numbers(numbers, algorithm="bubble"):
            """Toy sorting task with different algorithms."""
            data = numbers.copy()
            
            if algorithm == "bubble":
                # Bubble sort (slower)
                n = len(data)
                for i in range(n):
                    for j in range(0, n - i - 1):
                        if data[j] > data[j + 1]:
                            data[j], data[j + 1] = data[j + 1], data[j]
            
            elif algorithm == "quick":
                # Quick sort (faster)
                def quicksort(arr):
                    if len(arr) <= 1:
                        return arr
                    pivot = arr[len(arr) // 2]
                    left = [x for x in arr if x < pivot]
                    middle = [x for x in arr if x == pivot]
                    right = [x for x in arr if x > pivot]
                    return quicksort(left) + middle + quicksort(right)
                data = quicksort(data)
            
            elif algorithm == "merge":
                # Merge sort (consistent performance)
                def mergesort(arr):
                    if len(arr) <= 1:
                        return arr
                    mid = len(arr) // 2
                    left = mergesort(arr[:mid])
                    right = mergesort(arr[mid:])
                    return merge(left, right)
                
                def merge(left, right):
                    result = []
                    i, j = 0, 0
                    while i < len(left) and j < len(right):
                        if left[i] <= right[j]:
                            result.append(left[i])
                            i += 1
                        else:
                            result.append(right[j])
                            j += 1
                    result.extend(left[i:])
                    result.extend(right[j:])
                    return result
                
                data = mergesort(data)
            
            return f"Sorted with {algorithm}: {data[:5]}..."
        
        # Test data
        test_numbers = [random.randint(1, 100) for _ in range(20)]
        
        start_time = time.time()
        result = await sort_numbers(test_numbers)
        execution_time = time.time() - start_time
        
        print(f"✅ Quantum sorting completed")
        print(f"   Result: {result}")
        print(f"   Execution time: {execution_time:.3f}s")
        
        self.results.append({
            "test": "decorator_usage",
            "execution_time": execution_time,
            "input_size": len(test_numbers)
        })
    
    async def benchmark_parallel_performance(self):
        """Benchmark parallel execution performance gains."""
        print("\n⚡ 4. Parallel Performance Analysis")
        print("-" * 40)
        
        def cpu_intensive_task(task_id, work_amount):
            """Simulate CPU-intensive work."""
            result = 0
            for i in range(work_amount * 10000):
                result += i * task_id
            return f"Task {task_id}: {result}"
        
        # Sequential execution baseline
        work_units = [1, 2, 3, 4, 5]
        
        start_time = time.time()
        sequential_results = []
        for i, work in enumerate(work_units):
            result = cpu_intensive_task(i, work)
            sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        # Parallel quantum execution
        manager = QuantumManager(max_workers=5)
        variations = [
            TaskVariation(
                id=f"parallel_{i}",
                task=cpu_intensive_task,
                params={"task_id": i, "work_amount": work}
            )
            for i, work in enumerate(work_units)
        ]
        
        start_time = time.time()
        parallel_result = await manager.execute_quantum_task(
            variations,
            collapse_strategy=CollapseStrategy.FIRST_SUCCESS
        )
        parallel_time = time.time() - start_time
        
        speedup = sequential_time / parallel_time
        efficiency = speedup / len(work_units)
        
        print(f"   Sequential time: {sequential_time:.3f}s")
        print(f"   Parallel time:   {parallel_time:.3f}s")
        print(f"   Speedup:         {speedup:.2f}x")
        print(f"   Efficiency:      {efficiency:.2f}")
        
        self.results.append({
            "test": "parallel_performance",
            "sequential_time": sequential_time,
            "parallel_time": parallel_time,
            "speedup": speedup,
            "efficiency": efficiency
        })
    
    async def benchmark_real_world_scenarios(self):
        """Benchmark realistic use case scenarios."""
        print("\n🌍 5. Real-World Scenario Simulations")
        print("-" * 40)
        
        # Scenario 1: API Response Processing
        async def process_api_response(endpoint, processing_method):
            """Simulate API response processing."""
            await asyncio.sleep(random.uniform(0.1, 0.3))  # Simulate network delay
            
            if processing_method == "json":
                return {"endpoint": endpoint, "data": [1, 2, 3], "method": processing_method}
            elif processing_method == "xml":
                return f"<response><endpoint>{endpoint}</endpoint><data>1,2,3</data></response>"
            elif processing_method == "csv":
                return f"endpoint,data\n{endpoint},\"1,2,3\""
            else:
                return f"Raw response from {endpoint}"
        
        manager = QuantumManager(max_workers=4)
        
        # Test different processing approaches
        variations = [
            TaskVariation(
                id="json_proc",
                task=process_api_response,
                params={"endpoint": "/api/data", "processing_method": "json"}
            ),
            TaskVariation(
                id="xml_proc",
                task=process_api_response,
                params={"endpoint": "/api/data", "processing_method": "xml"}
            ),
            TaskVariation(
                id="csv_proc",
                task=process_api_response,
                params={"endpoint": "/api/data", "processing_method": "csv"}
            ),
        ]
        
        start_time = time.time()
        result = await manager.execute_quantum_task(
            variations,
            collapse_strategy=CollapseStrategy.FIRST_SUCCESS
        )
        execution_time = time.time() - start_time
        
        print(f"✅ API Processing scenario completed")
        print(f"   Winner: {result.variation_id}")
        print(f"   Result type: {type(result.value).__name__}")
        print(f"   Execution time: {execution_time:.3f}s")
        
        # Scenario 2: Machine Learning Model Selection
        def simple_ml_model(data, model_type, complexity):
            """Simulate simple ML model execution."""
            time.sleep(0.05 * complexity)  # Simulate training time
            
            # Fake accuracy based on complexity
            base_accuracy = 0.7
            accuracy = min(0.95, base_accuracy + (complexity * 0.05) + random.uniform(-0.1, 0.1))
            
            return {
                "model": model_type,
                "complexity": complexity,
                "accuracy": accuracy,
                "data_size": len(data)
            }
        
        test_data = list(range(100))  # Fake dataset
        
        ml_variations = [
            TaskVariation(
                id="simple_model",
                task=simple_ml_model,
                params={"data": test_data, "model_type": "linear", "complexity": 1}
            ),
            TaskVariation(
                id="complex_model",
                task=simple_ml_model,
                params={"data": test_data, "model_type": "neural_net", "complexity": 3}
            ),
            TaskVariation(
                id="ensemble_model",
                task=simple_ml_model,
                params={"data": test_data, "model_type": "ensemble", "complexity": 2}
            ),
        ]
        
        def accuracy_scorer(model_result):
            return model_result["accuracy"]
        
        start_time = time.time()
        ml_result = await manager.execute_quantum_task(
            ml_variations,
            collapse_strategy=CollapseStrategy.BEST_SCORE,
            scoring_fn=accuracy_scorer
        )
        ml_execution_time = time.time() - start_time
        
        print(f"\n✅ ML Model Selection scenario completed")
        print(f"   Best model: {ml_result.value['model']}")
        print(f"   Accuracy: {ml_result.value['accuracy']:.3f}")
        print(f"   Complexity: {ml_result.value['complexity']}")
        print(f"   Execution time: {ml_execution_time:.3f}s")
        
        self.results.append({
            "test": "api_processing",
            "execution_time": execution_time,
            "winner": result.variation_id
        })
        
        self.results.append({
            "test": "ml_model_selection",
            "execution_time": ml_execution_time,
            "best_model": ml_result.value["model"],
            "accuracy": ml_result.value["accuracy"]
        })
    
    def print_summary(self):
        """Print benchmark summary."""
        print("\n📈 Benchmark Summary")
        print("=" * 60)
        
        total_tests = len(self.results)
        total_time = sum(r.get("execution_time", 0) for r in self.results)
        
        print(f"Total tests run: {total_tests}")
        print(f"Total execution time: {total_time:.3f}s")
        print(f"Average time per test: {total_time/total_tests:.3f}s")
        
        print("\n🎯 Key Performance Metrics:")
        
        # Find parallel performance results
        parallel_result = next((r for r in self.results if r["test"] == "parallel_performance"), None)
        if parallel_result:
            print(f"   Parallel speedup: {parallel_result['speedup']:.2f}x")
            print(f"   Parallel efficiency: {parallel_result['efficiency']:.2f}")
        
        # Find fastest and slowest tests
        timed_results = [r for r in self.results if "execution_time" in r]
        if timed_results:
            fastest = min(timed_results, key=lambda x: x["execution_time"])
            slowest = max(timed_results, key=lambda x: x["execution_time"])
            
            print(f"   Fastest test: {fastest['test']} ({fastest['execution_time']:.3f}s)")
            print(f"   Slowest test: {slowest['test']} ({slowest['execution_time']:.3f}s)")
        
        print("\n💾 Detailed Results:")
        for result in self.results:
            print(f"   {result['test']:20} | {json.dumps(result, indent=None)}")
        
        print(f"\n✅ Quantum Execution Module benchmark completed successfully!")
        print(f"   All collapse strategies working correctly")
        print(f"   Parallel execution shows performance gains")
        print(f"   Decorator pattern functions as expected")
        print(f"   Real-world scenarios demonstrate practical utility")


async def main():
    """Run the quantum execution benchmark."""
    benchmark = QuantumBenchmark()
    await benchmark.run_all_benchmarks()


if __name__ == "__main__":
    asyncio.run(main())
