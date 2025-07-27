#!/usr/bin/env python3
"""
Example: Using Quantum Tasks in Agent Systems

This example demonstrates how to integrate the functional quantum execution module
with agent-based systems for improved performance and reliability.
"""

import asyncio
import logging
from typing import Dict, List, Any

from monkey_coder.quantum import quantum_task, CollapseStrategy, QuantumManager
from monkey_coder.quantum.manager import TaskVariation

# Setup logging to see quantum execution details
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeGeneratorAgent:
    """Example agent that generates code using quantum execution patterns."""
    
    def __init__(self, name: str):
        self.name = name
        self.quantum_manager = QuantumManager(max_workers=3, timeout=15.0)
    
    @quantum_task(
        variations=[
            {"id": "pythonic", "params": {"style": "pythonic", "verbosity": "concise"}},
            {"id": "verbose", "params": {"style": "explicit", "verbosity": "detailed"}},
            {"id": "functional", "params": {"style": "functional", "verbosity": "balanced"}},
        ],
        collapse_strategy=CollapseStrategy.BEST_SCORE,
        scoring_fn=lambda code: len(code.split('\n'))  # Prefer more detailed code
    )
    async def generate_function(self, func_name: str, description: str, style: str = "pythonic", verbosity: str = "balanced"):
        """Generate a Python function with different coding styles."""
        
        if style == "pythonic":
            if verbosity == "concise":
                template = f'''def {func_name}():\n    """{description}"""\n    pass  # TODO: Implement'''
            else:
                template = f'''def {func_name}():\n    """\n    {description}\n    \n    Returns:\n        TODO: Define return type\n    """\n    pass  # TODO: Implement functionality'''
        
        elif style == "explicit":
            template = f'''def {func_name}() -> None:\n    """\n    Function: {func_name}\n    Description: {description}\n    \n    Args:\n        None\n    \n    Returns:\n        None: This function returns nothing\n    \n    Raises:\n        NotImplementedError: Function not yet implemented\n    """\n    raise NotImplementedError("Function {func_name} not yet implemented")'''
        
        elif style == "functional":
            template = f'''from typing import Callable, Any\n\ndef {func_name}() -> Callable[[], Any]:\n    """{description}"""\n    \n    def inner_implementation() -> Any:\n        # TODO: Add implementation\n        return None\n    \n    return inner_implementation'''
        
        else:
            template = f'def {func_name}():\n    """{description}"""\n    pass'
        
        return template
    
    async def generate_class_with_quantum_methods(self, class_name: str, methods: List[str]):
        """Generate a class with methods created using quantum execution."""
        
        logger.info(f"🏗️  {self.name} generating class {class_name} with {len(methods)} methods")
        
        # Generate each method in parallel using quantum execution
        method_variations = []
        
        for i, method_name in enumerate(methods):
            method_variations.append(
                TaskVariation(
                    id=f"method_{method_name}",
                    task=self._generate_single_method,
                    params={
                        "method_name": method_name,
                        "class_context": class_name,
                        "complexity": i % 3 + 1  # Vary complexity
                    }
                )
            )
        
        # Execute all method generations in parallel
        result = await self.quantum_manager.execute_quantum_task(
            method_variations,
            collapse_strategy=CollapseStrategy.COMBINED
        )
        
        if result.success:
            methods_code = result.value["primary"]
            alternatives = result.value.get("alternatives", [])
            
            class_template = f'''class {class_name}:
    """Generated class with quantum-optimized methods."""
    
    def __init__(self):
        """Initialize {class_name} instance."""
        pass

{methods_code}
'''
            
            logger.info(f"✅ {self.name} successfully generated class {class_name}")
            return {
                "class_code": class_template,
                "primary_implementation": methods_code,
                "alternative_implementations": alternatives,
                "generation_time": result.execution_time
            }
        else:
            logger.error(f"❌ {self.name} failed to generate class {class_name}: {result.error}")
            return None
    
    async def _generate_single_method(self, method_name: str, class_context: str, complexity: int):
        """Generate a single method with specified complexity."""
        
        if complexity == 1:  # Simple method
            return f'''    def {method_name}(self):
        """Simple {method_name} method for {class_context}."""
        return f"Called {method_name} on {{self.__class__.__name__}}"'''
        
        elif complexity == 2:  # Medium complexity method
            return f'''    def {method_name}(self, *args, **kwargs):
        """
        {method_name} method for {class_context}.
        
        Args:
            *args: Variable positional arguments
            **kwargs: Variable keyword arguments
            
        Returns:
            dict: Result dictionary with method info
        """
        return {{
            "method": "{method_name}",
            "class": "{class_context}",
            "args": args,
            "kwargs": kwargs,
            "timestamp": __import__("time").time()
        }}'''
        
        else:  # Complex method
            return f'''    async def {method_name}(self, data: Any = None, callback: Optional[Callable] = None):
        """
        Advanced asynchronous {method_name} method for {class_context}.
        
        Args:
            data: Input data to process
            callback: Optional callback function to execute
            
        Returns:
            Any: Processed result
            
        Raises:
            ValueError: If data processing fails
        """
        try:
            await asyncio.sleep(0.1)  # Simulate async work
            
            result = {{
                "method": "{method_name}",
                "class": "{class_context}",
                "data": data,
                "processed": True
            }}
            
            if callback:
                result = await callback(result) if asyncio.iscoroutinefunction(callback) else callback(result)
            
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to process in {method_name}: {{e}}")'''


class TestingAgent:
    """Agent that creates tests using quantum execution for comprehensive coverage."""
    
    def __init__(self, name: str):
        self.name = name
    
    @quantum_task(
        variations=[
            {"id": "basic_tests", "params": {"test_style": "basic", "coverage": "minimal"}},
            {"id": "comprehensive_tests", "params": {"test_style": "comprehensive", "coverage": "extensive"}},
            {"id": "property_tests", "params": {"test_style": "property_based", "coverage": "thorough"}},
        ],
        collapse_strategy=CollapseStrategy.CONSENSUS,
        max_workers=3
    )
    async def generate_test_suite(self, target_class: str, methods: List[str], test_style: str = "basic", coverage: str = "minimal"):
        """Generate test suite with different testing approaches."""
        
        logger.info(f"🧪 {self.name} generating {test_style} tests for {target_class}")
        
        if test_style == "basic":
            test_template = f'''import unittest
from {target_class.lower()} import {target_class}

class Test{target_class}(unittest.TestCase):
    """Basic tests for {target_class}."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.instance = {target_class}()
'''
            
            for method in methods:
                test_template += f'''
    def test_{method}(self):
        """Test {method} method."""
        result = self.instance.{method}()
        self.assertIsNotNone(result)
'''
        
        elif test_style == "comprehensive":
            test_template = f'''import unittest
import asyncio
from unittest.mock import Mock, patch
from {target_class.lower()} import {target_class}

class Test{target_class}(unittest.TestCase):
    """Comprehensive tests for {target_class}."""
    
    def setUp(self):
        """Set up test fixtures with mocks."""
        self.instance = {target_class}()
        self.mock_data = {{"test": "data"}}
    
    def tearDown(self):
        """Clean up after tests."""
        pass
'''
            
            for method in methods:
                test_template += f'''
    def test_{method}_success_case(self):
        """Test {method} success scenario."""
        result = self.instance.{method}()
        self.assertIsNotNone(result)
        
    def test_{method}_edge_cases(self):
        """Test {method} edge cases."""
        # Test with None
        result = self.instance.{method}()
        self.assertIsNotNone(result)
        
    @patch('time.time')
    def test_{method}_with_mock(self, mock_time):
        """Test {method} with mocked dependencies."""
        mock_time.return_value = 1234567890
        result = self.instance.{method}()
        self.assertIsNotNone(result)
'''
        
        else:  # property_based
            test_template = f'''import unittest
from hypothesis import given, strategies as st
from {target_class.lower()} import {target_class}

class Test{target_class}Property(unittest.TestCase):
    """Property-based tests for {target_class}."""
    
    def setUp(self):
        """Set up test instance."""
        self.instance = {target_class}()
'''
            
            for method in methods:
                test_template += f'''
    @given(st.text(), st.integers())
    def test_{method}_property(self, text_data, int_data):
        """Property-based test for {method}."""
        # Property: method should always return something
        result = self.instance.{method}()
        self.assertIsNotNone(result)
'''
        
        test_template += '''
if __name__ == '__main__':
    unittest.main()
'''
        
        return {
            "test_code": test_template,
            "test_style": test_style,
            "coverage": coverage,
            "method_count": len(methods)
        }


async def demonstrate_quantum_agents():
    """Demonstrate quantum execution in agent systems."""
    
    print("🤖 Quantum Agent System Demonstration")
    print("=" * 50)
    
    # Create agents
    code_agent = CodeGeneratorAgent("CodeBot")
    test_agent = TestingAgent("TestBot")
    
    # Demonstrate single quantum task
    print("\n📝 1. Single Quantum Task - Function Generation")
    print("-" * 45)
    
    function_code = await code_agent.generate_function(
        func_name="process_data",
        description="Process input data and return structured results"
    )
    
    print("Generated function:")
    print(function_code)
    
    # Demonstrate complex quantum workflow
    print("\n🏗️  2. Complex Quantum Workflow - Class Generation")
    print("-" * 45)
    
    class_methods = ["initialize", "process", "validate", "cleanup", "export"]
    
    class_result = await code_agent.generate_class_with_quantum_methods(
        class_name="DataProcessor",
        methods=class_methods
    )
    
    if class_result:
        print(f"✅ Generated class in {class_result['generation_time']:.3f}s")
        print(f"📦 Primary implementation with {len(class_methods)} methods")
        print(f"🔄 {len(class_result['alternative_implementations'])} alternative implementations available")
        
        # Show a preview of the generated class
        preview = class_result['class_code'][:500] + "..." if len(class_result['class_code']) > 500 else class_result['class_code']
        print(f"\nClass preview:\n{preview}")
    
    # Demonstrate test generation with quantum execution
    print("\n🧪 3. Quantum Test Generation")
    print("-" * 30)
    
    test_result = await test_agent.generate_test_suite(
        target_class="DataProcessor",
        methods=class_methods
    )
    
    print(f"✅ Generated {test_result['test_style']} test suite")
    print(f"📊 Coverage level: {test_result['coverage']}")
    print(f"🎯 Testing {test_result['method_count']} methods")
    
    # Show test preview
    test_preview = test_result['test_code'][:400] + "..." if len(test_result['test_code']) > 400 else test_result['test_code']
    print(f"\nTest preview:\n{test_preview}")
    
    # Demonstrate parallel agent coordination
    print("\n🤝 4. Parallel Agent Coordination")
    print("-" * 35)
    
    # Run multiple agents in parallel using quantum patterns
    manager = QuantumManager(max_workers=2)
    
    coordination_variations = [
        TaskVariation(
            id="code_generation",
            task=code_agent.generate_function,
            params={
                "func_name": "analyze_results",
                "description": "Analyze processing results and generate report"
            }
        ),
        TaskVariation(
            id="test_generation",
            task=test_agent.generate_test_suite,
            params={
                "target_class": "ResultAnalyzer",
                "methods": ["analyze", "report"]
            }
        )
    ]
    
    coordination_result = await manager.execute_quantum_task(
        coordination_variations,
        collapse_strategy=CollapseStrategy.COMBINED
    )
    
    if coordination_result.success:
        print("✅ Parallel agent coordination successful")
        print(f"⚡ Combined execution completed in {coordination_result.execution_time:.3f}s")
        print(f"🎯 Primary result: {type(coordination_result.value['primary']).__name__}")
        print(f"🔄 {len(coordination_result.value['alternatives'])} alternative results")
    
    print("\n🎯 Quantum Agent Demonstration Summary")
    print("=" * 40)
    print("✅ Single quantum tasks: Function generation with style variations")
    print("✅ Complex workflows: Parallel method generation with quantum collapse")
    print("✅ Multi-agent systems: Test generation with consensus strategies")
    print("✅ Agent coordination: Parallel execution with combined results")
    print("\n💡 The quantum execution module enables:")
    print("   • Parallel exploration of solution variations")
    print("   • Intelligent result selection strategies")
    print("   • Improved agent system performance")
    print("   • Fault-tolerant execution patterns")


if __name__ == "__main__":
    asyncio.run(demonstrate_quantum_agents())
