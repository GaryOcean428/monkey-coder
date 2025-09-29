# Functional Quantum Execution Module

A quantum-inspired execution framework for parallel task processing with intelligent result selection strategies.

## Overview

The Functional Quantum Execution Module implements quantum computing principles for classical task execution:

- **Superposition**: Multiple task variations executed in parallel
- **Entanglement**: Task dependencies and relationships
- **Collapse**: Selection of optimal results based on configurable strategies

## Features

### ✨ Core Capabilities

- **Task Variations Generator**: Automatically generate variations of tasks with different parameters
- **Async Parallel Execution**: Execute tasks concurrently using `anyio` for structured concurrency
- **Multiple Collapse Strategies**: Choose how to select final results from parallel executions
- **Decorator Pattern**: Easy-to-use `@quantum_task` decorator for seamless integration
- **Performance Monitoring**: Built-in metrics tracking and performance analysis

### 🎯 Collapse Strategies

1. **FIRST_SUCCESS**: Return the first successful result (fastest execution)
2. **BEST_SCORE**: Return the result with the highest score using a custom scoring function
3. **CONSENSUS**: Return the most common result among variations
4. **COMBINED**: Intelligently combine multiple results into a composite output

## Quick Start

### Basic Usage

```python
import asyncio
from monkey_coder.quantum import QuantumManager, CollapseStrategy
from monkey_coder.quantum.manager import TaskVariation

async def main():
    manager = QuantumManager(max_workers=4)
    
    def compute_result(method, data):
        if method == "fast":
            return sum(data)
        elif method == "accurate":
            return sum(x * 1.1 for x in data)  # More accurate calculation
        else:
            return sum(data) / len(data)  # Average
    
    variations = [
        TaskVariation("fast", compute_result, {"method": "fast", "data": [1, 2, 3, 4, 5]}),
        TaskVariation("accurate", compute_result, {"method": "accurate", "data": [1, 2, 3, 4, 5]}),
        TaskVariation("average", compute_result, {"method": "average", "data": [1, 2, 3, 4, 5]}),
    ]
    
    result = await manager.execute_quantum_task(
        variations,
        collapse_strategy=CollapseStrategy.FIRST_SUCCESS
    )
    
    print(f"Result: {result.value}")
    print(f"Winner: {result.variation_id}")
    print(f"Execution time: {result.execution_time:.3f}s")

asyncio.run(main())
```python

### Using the Decorator

```python
from monkey_coder.quantum import quantum_task, CollapseStrategy

@quantum_task(
    variations=[
        {"id": "method1", "params": {"algorithm": "quick"}},
        {"id": "method2", "params": {"algorithm": "merge"}},
        {"id": "method3", "params": {"algorithm": "bubble"}},
    ],
    collapse_strategy=CollapseStrategy.FIRST_SUCCESS,
    max_workers=3,
    timeout=10.0
)
async def sort_data(data, algorithm="quick"):
    """Sort data using different algorithms."""
    if algorithm == "quick":
        return sorted(data)  # Fast for most cases
    elif algorithm == "merge":
        # Implement merge sort logic
        return sorted(data)
    elif algorithm == "bubble":
        # Implement bubble sort logic
        return sorted(data)

# Usage
async def main():
    result = await sort_data([3, 1, 4, 1, 5, 9, 2, 6])
    print(f"Sorted: {result}")

asyncio.run(main())
```python

### Advanced Usage with Custom Scoring

```python
@quantum_task(
    variations=[
        {"id": "brief", "params": {"style": "brief"}},
        {"id": "detailed", "params": {"style": "detailed"}},
        {"id": "comprehensive", "params": {"style": "comprehensive"}},
    ],
    collapse_strategy=CollapseStrategy.BEST_SCORE,
    scoring_fn=lambda text: len(text.split())  # Prefer more detailed text
)
async def generate_report(data, style="brief"):
    """Generate reports with different levels of detail."""
    if style == "brief":
        return f"Report: {len(data)} items processed."
    elif style == "detailed":
        return f"Detailed Report: Processed {len(data)} items with average value {sum(data)/len(data):.2f}."
    else:
        return f"Comprehensive Report: Analyzed {len(data)} data points. Average: {sum(data)/len(data):.2f}, Min: {min(data)}, Max: {max(data)}, Total: {sum(data)}."

# Usage
async def main():
    data = [1, 5, 3, 8, 2, 9, 4, 6, 7]
    report = await generate_report(data)
    print(report)

asyncio.run(main())
```python

## Architecture

### Core Components

```text
quantum/
├── __init__.py           # Module exports
├── manager.py            # Main quantum execution logic
└── README.md            # This documentation
```

### Class Hierarchy

- **QuantumManager**: Main orchestrator for quantum execution
- **TaskVariation**: Represents a single task variation
- **QuantumResult**: Container for execution results
- **CollapseStrategy**: Enum defining result selection strategies

### Key Methods

#### QuantumManager

- `execute_quantum_task()`: Execute variations and collapse results
- `generate_variations()`: Create task variations from configurations
- `get_metrics()`: Retrieve performance metrics

#### Decorators

- `@quantum_task`: Transform functions to use quantum execution patterns

## Integration with Agent Systems

The quantum module is designed to integrate seamlessly with agent-based systems:

```python
class CodeGeneratorAgent:
    def __init__(self):
        self.quantum_manager = QuantumManager(max_workers=3)
    
    @quantum_task(
        variations=[
            {"id": "pythonic", "params": {"style": "pythonic"}},
            {"id": "verbose", "params": {"style": "verbose"}},
            {"id": "functional", "params": {"style": "functional"}},
        ],
        collapse_strategy=CollapseStrategy.BEST_SCORE,
        scoring_fn=lambda code: len(code.split('\n'))  # Prefer more lines
    )
    async def generate_code(self, description, style="pythonic"):
        # Generate code based on style
        return f"# {style.title()} style\n# {description}\npass"
    
    async def create_multiple_functions(self, functions):
        """Generate multiple functions in parallel."""
        variations = []
        
        for func_name, desc in functions.items():
            variations.append(TaskVariation(
                id=f"func_{func_name}",
                task=self.generate_code,
                params={"description": desc}
            ))
        
        result = await self.quantum_manager.execute_quantum_task(
            variations,
            collapse_strategy=CollapseStrategy.COMBINED
        )
        
        return result
```

## Performance Characteristics

### Parallel Execution Benefits

- **CPU-bound tasks**: Significant speedup with multiple workers
- **I/O-bound tasks**: Excellent concurrency with async/await
- **Mixed workloads**: Intelligent scheduling and resource utilization

### Collapse Strategy Performance

- **FIRST_SUCCESS**: Fastest for time-critical applications
- **BEST_SCORE**: Best quality results with custom optimization
- **CONSENSUS**: Most reliable for consistency requirements
- **COMBINED**: Most comprehensive for analysis tasks

## Best Practices

### 1. Choose Appropriate Strategies

```python
# For speed-critical applications
collapse_strategy=CollapseStrategy.FIRST_SUCCESS

# For quality optimization
collapse_strategy=CollapseStrategy.BEST_SCORE
scoring_fn=lambda result: calculate_quality_score(result)

# For reliability
collapse_strategy=CollapseStrategy.CONSENSUS

# For comprehensive analysis
collapse_strategy=CollapseStrategy.COMBINED
```

### 2. Configure Worker Count

```python
# CPU-bound tasks: match CPU cores
manager = QuantumManager(max_workers=os.cpu_count())

# I/O-bound tasks: can exceed CPU cores
manager = QuantumManager(max_workers=20)

# Memory-constrained: limit workers
manager = QuantumManager(max_workers=2)
```

### 3. Handle Errors Gracefully

```python
try:
    result = await manager.execute_quantum_task(variations)
    if not result.success:
        logger.error(f"Task failed: {result.error}")
        # Handle failure case
except Exception as e:
    logger.error(f"Quantum execution error: {e}")
    # Fallback logic
```

### 4. Monitor Performance

```python
manager = QuantumManager(max_workers=4)

# Execute tasks...

metrics = manager.get_metrics()
for execution in metrics['executions']:
    print(f"Strategy: {execution['strategy']}")
    print(f"Time: {execution['execution_time']:.3f}s")
    print(f"Success: {execution['success']}")
```

## Testing

The module includes comprehensive tests covering:

- Basic quantum execution patterns
- All collapse strategies
- Decorator functionality
- Error handling scenarios
- Performance benchmarks
- Integration patterns

Run tests with:

```bash
pytest tests/test_quantum.py -v
```

Run benchmarks with:

```bash
python benchmark_quantum.py
```

## Dependencies

- **anyio**: Structured concurrency (preferred)
- **asyncio**: Fallback async framework
- **concurrent.futures**: Thread pool execution
- **typing**: Type hints support

## Future Enhancements

- **Adaptive Strategies**: Dynamic strategy selection based on performance
- **Resource Monitoring**: CPU, memory, and network usage tracking
- **Result Caching**: Intelligent caching of expensive computations
- **Load Balancing**: Dynamic worker allocation across tasks
- **Quantum Entanglement**: Task dependency management and coordination

## Examples

See the following files for complete examples:

- `benchmark_quantum.py`: Comprehensive performance benchmarks
- `example_quantum_agents.py`: Agent system integration examples

## License

This module is part of the Monkey Coder project and follows the same license terms.
