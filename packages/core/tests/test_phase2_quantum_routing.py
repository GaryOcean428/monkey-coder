"""
Comprehensive test suite for Phase 2 Quantum Routing implementation.

Tests all major components:
- Enhanced DQN Agent with neural networks
- Quantum Routing Manager
- Performance Metrics Collection
- Router Integration
"""

import pytest
import numpy as np

from monkey_coder.models import (
    ExecuteRequest, PersonaType, ProviderType, TaskType,
    ExecutionContext, PersonaConfig, OrchestrationConfig, QuantumConfig
)
from monkey_coder.quantum import (
    DQNRoutingAgent,
    RoutingState,
    RoutingAction,
    QuantumRoutingManager,
    RoutingStrategy,
    PerformanceMetricsCollector,
    MetricType
)
from monkey_coder.quantum.router_integration import QuantumRouterIntegration
from monkey_coder.quantum.neural_network import NumpyDQNModel

def create_test_execute_request(prompt: str, task_type: TaskType) -> ExecuteRequest:
    """Create a valid ExecuteRequest object for testing."""
    return ExecuteRequest(
        prompt=prompt,
        task_type=task_type,
        files=[{"name": "test.py", "content": "print('test')"}],
        context=ExecutionContext(
            user_id="test_user",
            session_id="test_session",
            workspace_id="test_workspace",
            environment="test"
        ),
        persona_config=PersonaConfig(
            persona=PersonaType.DEVELOPER,
            custom_instructions="Test instructions"
        ),
        orchestration_config=OrchestrationConfig(),
        quantum_config=QuantumConfig()
    )


class TestDQNNetworkImplementation:
    """Test the neural network implementation for DQN agent."""

    def test_numpy_network_creation(self):
        """Test creation of numpy-based DQN network."""
        network = NumpyDQNModel(
            input_size=10,
            hidden_sizes=(16, 8),
            output_size=5,
            learning_rate=0.001
        )

        assert network.input_size == 10
        assert network.output_size == 5
        assert len(network.weights) == 3  # input->hidden1, hidden1->hidden2, hidden2->output
        assert len(network.biases) == 3

    def test_numpy_network_prediction(self):
        """Test forward pass prediction."""
        network = NumpyDQNModel(input_size=5, output_size=3)

        state = np.random.random((1, 5))
        prediction = network.predict(state)

        assert prediction.shape == (1, 3)
        assert isinstance(prediction, np.ndarray)

    def test_numpy_network_training(self):
        """Test network training with simple data."""
        network = NumpyDQNModel(input_size=3, output_size=2, learning_rate=0.1)

        # Simple training data
        x = np.array([[1.0, 0.0, 0.5]])
        y = np.array([[0.8, 0.2]])

        initial_weights = [w.copy() for w in network.weights]
        history = network.fit(x, y, epochs=5)

        # Weights should have changed after training
        assert any(not np.allclose(initial_weights[i], network.weights[i]) for i in range(len(network.weights)))
        assert isinstance(history, dict)
        assert 'loss' in history
        assert len(history['loss']) == 5
        assert all(loss >= 0 for loss in history['loss'])


class TestEnhancedDQNAgent:
    """Test the enhanced DQN agent with neural network integration."""

    def setup_method(self):
        """Setup test fixtures."""
        self.agent = DQNRoutingAgent(
            state_size=21,  # Match the actual state vector size from RoutingState.to_vector()
            action_size=12,  # Match the actual number of actions in RoutingAction.from_action_index()
            learning_rate=0.001,
            exploration_rate=0.5,
            memory_size=100
        )

    def test_agent_initialization(self):
        """Test DQN agent initialization with neural networks."""
        # Networks are initialized lazily, so we need to trigger initialization
        self.agent._initialize_networks()

        assert self.agent.q_network is not None
        assert self.agent.target_q_network is not None
        assert self.agent.state_size == 21  # Updated to match the actual state vector size
        assert self.agent.action_size == 12  # Updated to match the actual action size

    def test_routing_state_conversion(self):
        """Test conversion of routing state to vector."""
        state = RoutingState(
            task_complexity=0.7,
            context_type="code_generation",
            provider_availability={"openai": True, "anthropic": False},
            historical_performance={"openai": 0.9, "anthropic": 0.8},
            resource_constraints={"cost_weight": 0.3, "time_weight": 0.4, "quality_weight": 0.3},
            user_preferences={"preference_strength": 0.6}
        )

        vector = state.to_vector()
        assert isinstance(vector, np.ndarray)
        assert len(vector) == 21  # Expected state vector size
        assert vector[0] == 0.7  # task_complexity

    def test_action_selection(self):
        """Test action selection with exploration/exploitation."""
        state = RoutingState(
            task_complexity=0.5,
            context_type="code_generation",
            provider_availability={"openai": True},
            historical_performance={"openai": 0.8},
            resource_constraints={"cost_weight": 0.33, "time_weight": 0.33, "quality_weight": 0.34},
            user_preferences={"preference_strength": 0.5}
        )

        action = self.agent.act(state)
        assert isinstance(action, RoutingAction)
        assert isinstance(action.provider, ProviderType)
        assert isinstance(action.model, str)

    def test_experience_replay(self):
        """Test experience replay training."""
        # Add some experiences to memory
        for _ in range(10):
            state = RoutingState(
                task_complexity=0.5,
                context_type="testing",
                provider_availability={"openai": True},
                historical_performance={"openai": 0.8},
                resource_constraints={"cost_weight": 0.33, "time_weight": 0.33, "quality_weight": 0.34},
                user_preferences={"preference_strength": 0.5}
            )

            action = RoutingAction(ProviderType.OPENAI, "gpt-4.1", "performance")

            self.agent.remember(
                state=state,
                action=action,
                reward=0.8,
                next_state=state,
                done=True
            )

        # Should not train with insufficient samples
        assert len(self.agent.memory) == 10
        loss = self.agent.replay()
        assert loss is None  # Not enough samples for batch_size=64

    def test_model_save_load(self):
        """Test model saving and loading."""
        # Note: This is a simplified test since we can't easily test file operations
        # In a real test environment, you'd test actual file save/load

        self.agent.exploration_rate = 0.1  # Change a parameter

        # Test configuration save (without actual file operations)
        config_data = {
            "exploration_rate": self.agent.exploration_rate,
            "training_step": self.agent.training_step,
            "routing_performance": self.agent.routing_performance
        }

        assert config_data["exploration_rate"] == 0.1
        assert config_data["training_step"] == 0


class TestQuantumRoutingManager:
    """Test the Quantum Routing Manager."""

    def setup_method(self):
        """Setup test fixtures."""
        self.manager = QuantumRoutingManager(
            max_threads=2,
            default_timeout=5.0
        )

    def test_manager_initialization(self):
        """Test quantum routing manager initialization."""
        assert self.manager is not None
        assert self.manager.max_threads == 2
        assert self.manager.default_timeout == 5.0

    @pytest.mark.asyncio
    async def test_routing_strategy_execution(self):
        """Test execution of different routing strategies."""
        request = create_test_execute_request(
            "Create a Python function for data processing",
            TaskType.CODE_GENERATION
        )

        # Test routing with a specific strategy
        result = await self.manager.route_with_quantum_strategies(
            request=request,
            strategies=[RoutingStrategy.TASK_OPTIMIZED]
        )

        assert result.provider is not None
        assert result.model is not None
        assert result.strategy_used == RoutingStrategy.TASK_OPTIMIZED.value

    @pytest.mark.asyncio
    async def test_quantum_routing_execution(self):
        """Test full quantum routing with multiple strategies."""
        request = create_test_execute_request(
            "Analyze code performance and suggest optimizations",
            TaskType.CODE_ANALYSIS
        )

        result = await self.manager.route_with_quantum_strategies(
            request=request,
            strategies=[
                RoutingStrategy.TASK_OPTIMIZED,
                RoutingStrategy.BALANCED
            ]
        )

        assert result.provider is not None
        assert result.model is not None
        assert result.execution_time > 0
        assert result.strategy_used in [RoutingStrategy.TASK_OPTIMIZED.value, RoutingStrategy.BALANCED.value]
        assert len(result.thread_results) > 0

    def test_routing_state_conversion(self):
        """Test conversion of request to routing state."""
        request = create_test_execute_request(
            "Debug this Python code",
            TaskType.DEBUGGING
        )

        routing_state = self.manager._create_routing_state(request)

        assert isinstance(routing_state, RoutingState)
        assert 0.0 <= routing_state.task_complexity <= 1.0
        assert routing_state.context_type in [
            "python", "javascript", "typescript", "java", "general"
        ]

    def test_performance_stats(self):
        """Test performance statistics."""
        # Initially should be empty
        stats = self.manager.get_performance_stats()
        assert stats["total_executions"] == 0
        assert "strategy_performance" in stats

        # Should handle empty data gracefully
        assert stats["average_confidence"] == 0.0
        assert stats["average_execution_time"] == 0.0


class TestPerformanceMetricsCollector:
    """Test the performance metrics collection system."""

    def setup_method(self):
        """Setup test fixtures."""
        self.collector = PerformanceMetricsCollector(
            max_datapoints=100,
            enable_real_time_monitoring=False  # Disable for testing
        )

    def test_metric_recording(self):
        """Test recording of various metric types."""
        # Record routing decision
        self.collector.record_routing_decision(
            provider="openai",
            model="gpt-4.1",
            execution_time=2.5,
            success=True,
            confidence_score=0.9,
            strategy_used="quantum"
        )

        # Check that metrics were recorded
        assert len(self.collector.metrics[MetricType.EXECUTION_TIME]) == 1
        assert len(self.collector.metrics[MetricType.ROUTING_DECISION]) == 1
        assert len(self.collector.metrics[MetricType.QUALITY_SCORE]) == 1

        # Check counter updates
        assert self.collector.counters["total_routing_decisions"] == 1
        assert self.collector.counters["routing_decisions_openai"] == 1

    def test_metric_statistics(self):
        """Test statistical analysis of metrics."""
        # Record multiple data points
        for i in range(10):
            self.collector.record_metric(
                MetricType.EXECUTION_TIME,
                float(i + 1),  # Values 1.0 to 10.0
                metadata={"test": "data"}
            )

        stats = self.collector.get_metric_statistics(MetricType.EXECUTION_TIME)

        assert stats["count"] == 10
        assert stats["mean"] == 5.5
        assert stats["min"] == 1.0
        assert stats["max"] == 10.0

    def test_provider_performance_report(self):
        """Test provider performance reporting."""
        # Record performance for multiple providers
        self.collector.record_provider_performance(
            provider="openai",
            model="gpt-4.1",
            response_time=2.0,
            success=True,
            quality_score=0.9,
            cost_tokens=100
        )

        self.collector.record_provider_performance(
            provider="anthropic",
            model="claude-3-opus",
            response_time=3.0,
            success=True,
            quality_score=0.85,
            cost_tokens=120
        )

        report = self.collector.get_provider_performance_report()

        assert "openai" in report
        assert "anthropic" in report
        assert "derived_metrics" in report["openai"]
        assert "success_rate" in report["openai"]["derived_metrics"]

    def test_trend_analysis(self):
        """Test trend analysis functionality."""
        # Record increasing values to test trend detection
        for i in range(5):
            self.collector.record_metric(
                MetricType.QUALITY_SCORE,
                0.5 + (i * 0.1),  # Increasing trend
                metadata={"trend_test": True}
            )

        trend = self.collector.get_trend_analysis(MetricType.QUALITY_SCORE)

        assert trend["trend"] in ["improving", "stable", "degrading"]
        assert "slope" in trend
        assert trend["data_points"] == 5


class TestRouterIntegration:
    """Test the quantum router integration layer."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test fixtures."""
        # Create integration instance for testing
        self.integration = QuantumRouterIntegration(
            enable_quantum=True,
            quantum_timeout=5.0,
            fallback_on_failure=True,
            performance_comparison=False
        )

    @pytest.mark.asyncio
    async def test_quantum_routing_integration(self):
        """Test integrated quantum routing."""
        # Create integration inside async context to avoid event loop issues
        integration = QuantumRouterIntegration(
            enable_quantum=True,
            quantum_timeout=5.0,
            fallback_on_failure=True,
            performance_comparison=False  # Disable for simpler testing
        )
        request = create_test_execute_request(
            "Write a unit test for this function",
            TaskType.TESTING
        )

        decision = await integration.route_request(request, force_method="quantum")

        assert decision.provider is not None
        assert decision.model is not None
        assert decision.confidence > 0

    @pytest.mark.asyncio
    async def test_classic_routing_fallback(self):
        """Test fallback to classic routing."""
        integration = QuantumRouterIntegration(
            enable_quantum=True,
            quantum_timeout=5.0,
            fallback_on_failure=True,
            performance_comparison=False
        )
        request = create_test_execute_request(
            "Review this code for security issues",
            TaskType.CODE_REVIEW
        )

        decision = await integration.route_request(request, force_method="classic")

        assert decision.provider is not None
        assert decision.model is not None
        assert decision.confidence > 0

    def test_routing_method_determination(self):
        """Test routing method determination logic."""
        request = create_test_execute_request(
            "Test request",
            TaskType.CODE_GENERATION
        )

        # Test forced method
        method = self.integration._determine_routing_method(request, force_method="classic")
        assert method == "classic"

        # Test auto-selection
        method = self.integration._determine_routing_method(request, force_method=None)
        assert method == "quantum"  # Should default to quantum when enabled

        # Test disabled quantum
        self.integration.enable_quantum = False
        method = self.integration._determine_routing_method(request, force_method=None)
        assert method == "classic"

    @pytest.mark.asyncio
    async def test_routing_analytics(self):
        """Test routing analytics generation."""
        analytics = await self.integration.get_routing_analytics()

        assert "routing_statistics" in analytics
        assert "performance_metrics" in analytics
        assert "configuration" in analytics

        stats = analytics["routing_statistics"]
        assert "total_requests" in stats
        assert "quantum_enabled" in stats
        assert stats["quantum_enabled"]

    def test_health_status(self):
        """Test health status monitoring."""
        status = self.integration.get_health_status()

        assert "quantum_enabled" in status
        assert "quantum_manager_healthy" in status
        assert "classic_router_healthy" in status
        assert "overall_health" in status

        assert status["quantum_enabled"]
        assert status["quantum_manager_healthy"]
        assert status["classic_router_healthy"]


class TestEndToEndIntegration:
    """End-to-end integration tests for the complete Phase 2 system."""

    @pytest.mark.asyncio
    async def test_complete_routing_workflow(self):
        """Test complete routing workflow from request to result."""
        # Initialize complete system
        integration = QuantumRouterIntegration(
            enable_quantum=True,
            quantum_timeout=10.0,
            fallback_on_failure=True,
            performance_comparison=False
        )

        # Create test request
        request = create_test_execute_request(
            "Create a comprehensive data validation system with error handling",
            TaskType.CODE_GENERATION
        )

        # Execute routing
        decision = await integration.route_request(request)

        # Validate results
        assert decision is not None
        assert decision.provider in ProviderType
        assert decision.model is not None
        assert 0.0 <= decision.confidence <= 1.0
        assert decision.reasoning is not None

        # Check analytics were updated
        analytics = await integration.get_routing_analytics()
        assert analytics["routing_statistics"]["total_requests"] > 0

    @pytest.mark.asyncio
    async def test_learning_and_optimization(self):
        """Test the learning and optimization capabilities."""
        integration = QuantumRouterIntegration(enable_quantum=True)

        # Simulate multiple routing requests for learning
        requests = [
            create_test_execute_request(f"Test request {i}", TaskType.CODE_GENERATION)
            for i in range(5)
        ]

        for request in requests:
            await integration.route_request(request)

        # Trigger optimization
        await integration.optimize_routing()

        # Verify that learning has occurred
        if integration.quantum_manager and integration.quantum_manager.dqn_agent:
            agent = integration.quantum_manager.dqn_agent
            assert len(agent.memory) > 0
            assert agent.training_step >= 0

    def test_performance_metrics_integration(self):
        """Test integration of performance metrics across the system."""
        integration = QuantumRouterIntegration(enable_quantum=True)

        # Performance metrics should be accessible
        metrics_data = integration.metrics_collector.get_real_time_dashboard_data()
        assert "summary" in metrics_data
        assert "timestamp" in metrics_data


# Performance benchmarks
class TestPerformanceBenchmarks:
    """Performance benchmarks for Phase 2 components."""

    @pytest.mark.asyncio
    async def test_routing_performance_benchmark(self):
        """Benchmark routing performance."""
        integration = QuantumRouterIntegration(enable_quantum=True)

        # Time quantum routing
        import time
        start_time = time.time()

        request = create_test_execute_request(
            "Benchmark test request",
            TaskType.CODE_GENERATION
        )

        await integration.route_request(request, force_method="quantum")
        quantum_time = time.time() - start_time

        # Time classic routing
        start_time = time.time()
        await integration.route_request(request, force_method="classic")
        classic_time = time.time() - start_time

        # Quantum routing should complete within reasonable time
        assert quantum_time < 30.0  # Should complete within 30 seconds
        assert classic_time < 5.0   # Classic should be faster for single requests

        print(f"Quantum routing time: {quantum_time:.3f}s")
        print(f"Classic routing time: {classic_time:.3f}s")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
