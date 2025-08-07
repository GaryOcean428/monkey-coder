"""
Tests for DQN Router Integration Bridge

This module tests the integration between the existing AdvancedRouter and the 
new AdvancedStateEncoder for quantum routing capabilities. It ensures backward
compatibility while validating the enhanced state encoding functionality.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch

from monkey_coder.models import ExecuteRequest, TaskType, ProviderType, PersonaType
from monkey_coder.core.routing import AdvancedRouter, RoutingDecision, ComplexityLevel, ContextType
from monkey_coder.quantum.router_integration import (
    DQNRouterBridge, 
    EnhancedRoutingDecision,
    create_dqn_router_bridge
)
from monkey_coder.quantum.state_encoder import (
    AdvancedStateEncoder,
    TaskContextProfile,
    ProviderPerformanceHistory,
    UserPreferences,
    ResourceConstraints,
    ContextComplexity
)
from monkey_coder.quantum.dqn_agent import DQNRoutingAgent, RoutingAction


class TestEnhancedRoutingDecision:
    """Test enhanced routing decision data structure."""
    
    def test_enhanced_routing_decision_creation(self):
        """Test creating enhanced routing decision."""
        original_decision = RoutingDecision(
            provider=ProviderType.OPENAI,
            model="gpt-4.1",
            persona=PersonaType.DEVELOPER,
            complexity_score=0.6,
            context_score=0.8,
            capability_score=0.9,
            confidence=0.85,
            reasoning="Test routing decision",
            metadata={"test": True}
        )
        
        state_vector = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)
        
        enhanced_decision = EnhancedRoutingDecision(
            original_decision=original_decision,
            state_vector=state_vector,
            state_dimensions=4,
            encoding_metadata={"encoding_type": "basic"}
        )
        
        assert enhanced_decision.original_decision == original_decision
        assert np.array_equal(enhanced_decision.state_vector, state_vector)
        assert enhanced_decision.state_dimensions == 4
        assert enhanced_decision.encoding_metadata["encoding_type"] == "basic"


class TestDQNRouterBridge:
    """Test the DQN router bridge functionality."""
    
    @pytest.fixture
    def sample_request(self):
        """Create sample execution request."""
        from monkey_coder.models import ExecutionContext, SuperClaudeConfig
        
        context = ExecutionContext(user_id="test-user-123", session_id="test-session-456")
        superclause_config = SuperClaudeConfig(
            persona=PersonaType.DEVELOPER
        )
        
        return ExecuteRequest(
            prompt="Create a REST API with authentication",
            task_type=TaskType.CODE_GENERATION,
            persona_config=None,
            context=context,
            superclause_config=superclause_config
        )
    
    @pytest.fixture
    def bridge_basic(self):
        """Create bridge with basic encoding."""
        return DQNRouterBridge(
            use_advanced_encoding=False,
            collect_training_data=False
        )
    
    @pytest.fixture  
    def bridge_advanced(self):
        """Create bridge with advanced encoding."""
        return DQNRouterBridge(
            use_advanced_encoding=True,
            encoding_strategy="comprehensive",
            collect_training_data=True
        )
    
    def test_bridge_initialization_basic(self, bridge_basic):
        """Test bridge initialization with basic encoding."""
        assert bridge_basic.use_advanced_encoding is False
        assert bridge_basic.collect_training_data is False
        assert bridge_basic.state_encoder is None
        assert isinstance(bridge_basic.advanced_router, AdvancedRouter)
        assert isinstance(bridge_basic.training_data, list)
        assert isinstance(bridge_basic.performance_history, dict)
    
    def test_bridge_initialization_advanced(self, bridge_advanced):
        """Test bridge initialization with advanced encoding."""
        assert bridge_advanced.use_advanced_encoding is True
        assert bridge_advanced.collect_training_data is True
        assert isinstance(bridge_advanced.state_encoder, AdvancedStateEncoder)
        assert isinstance(bridge_advanced.advanced_router, AdvancedRouter)
        assert bridge_advanced.state_encoder.enable_temporal_features is True
        assert bridge_advanced.state_encoder.enable_user_personalization is True
        assert bridge_advanced.state_encoder.enable_dynamic_weighting is True
    
    def test_route_request_basic(self, bridge_basic, sample_request):
        """Test routing with basic encoding."""
        enhanced_decision = bridge_basic.route_request(sample_request)
        
        assert isinstance(enhanced_decision, EnhancedRoutingDecision)
        assert enhanced_decision.encoding_metadata["encoding_type"] == "basic"
        assert enhanced_decision.state_dimensions == len(enhanced_decision.state_vector)
        assert enhanced_decision.original_decision.provider in ProviderType
        assert enhanced_decision.original_decision.persona in PersonaType
        
        # Should use basic state vector (21 dimensions)
        assert enhanced_decision.state_dimensions == 21
    
    def test_route_request_advanced(self, bridge_advanced, sample_request):
        """Test routing with advanced encoding."""
        enhanced_decision = bridge_advanced.route_request(sample_request)
        
        assert isinstance(enhanced_decision, EnhancedRoutingDecision)
        assert enhanced_decision.encoding_metadata["encoding_type"] == "advanced"
        assert enhanced_decision.state_dimensions == 112  # Advanced encoder dimensions
        assert np.all(np.isfinite(enhanced_decision.state_vector))
        
        # Check metadata contains advanced encoding information
        metadata = enhanced_decision.encoding_metadata
        assert "dimensions" in metadata
        assert "complexity_category" in metadata
        assert "task_type" in metadata
        assert metadata["temporal_features_enabled"] is True
        assert metadata["personalization_enabled"] is True
        assert metadata["dynamic_weighting_enabled"] is True
    
    def test_convert_to_task_context_profile(self, bridge_advanced, sample_request):
        """Test conversion from ExecuteRequest to TaskContextProfile."""
        # Create a mock routing decision
        mock_decision = RoutingDecision(
            provider=ProviderType.OPENAI,
            model="gpt-4.1",
            persona=PersonaType.DEVELOPER,
            complexity_score=0.7,
            context_score=0.8,
            capability_score=0.9,
            confidence=0.85,
            reasoning="Test decision",
            metadata={"complexity_level": "complex"}
        )
        
        task_context = bridge_advanced._convert_to_task_context_profile(
            sample_request, mock_decision
        )
        
        assert isinstance(task_context, TaskContextProfile)
        assert task_context.task_type == TaskType.CODE_GENERATION
        assert task_context.estimated_complexity == 0.7
        assert task_context.complexity_category == ContextComplexity.COMPLEX
        assert "programming" in task_context.domain_requirements
        assert task_context.requires_reasoning is False  # "Create" is not reasoning-heavy
    
    def test_get_provider_performance_history(self, bridge_advanced):
        """Test provider performance history retrieval."""
        # Update some performance data
        bridge_advanced.performance_history["openai"] = {
            "success_rate": 0.9,
            "avg_latency": 1.5,
            "avg_quality": 0.85,
            "reputation": 0.88,
            "interactions": 500
        }
        
        history = bridge_advanced._get_provider_performance_history()
        
        assert len(history) == len(ProviderType)
        assert ProviderType.OPENAI in history
        assert isinstance(history[ProviderType.OPENAI], ProviderPerformanceHistory)
        
        openai_history = history[ProviderType.OPENAI]
        assert openai_history.recent_success_rate == 0.9
        assert openai_history.recent_avg_latency == 1.5
        assert openai_history.recent_avg_quality == 0.85
        assert openai_history.long_term_reputation == 0.88
        assert openai_history.total_interactions == 500
    
    def test_extract_user_preferences(self, bridge_advanced, sample_request):
        """Test user preferences extraction."""
        # Add preferred providers to request
        sample_request.preferred_providers = [ProviderType.OPENAI, ProviderType.ANTHROPIC]
        
        # Update the context with additional attributes
        if hasattr(sample_request.context, 'quality_threshold'):
            sample_request.context.quality_threshold = 0.9
        else:
            # Create a mock for quality threshold if not available
            context_mock = Mock()
            context_mock.quality_threshold = 0.9
            sample_request.context = context_mock
        
        preferences = bridge_advanced._extract_user_preferences(sample_request)
        
        assert isinstance(preferences, UserPreferences)
        assert preferences.provider_preference_scores[ProviderType.OPENAI] == 0.8
        assert preferences.provider_preference_scores[ProviderType.ANTHROPIC] == 0.8
        assert preferences.quality_vs_speed_preference == 0.8  # High quality preference
    
    def test_extract_resource_constraints(self, bridge_advanced, sample_request):
        """Test resource constraints extraction."""
        # Create a mock context with the required attributes
        context_mock = Mock()
        context_mock.timeout = 15.0
        context_mock.quality_threshold = 0.85
        context_mock.is_premium_user = True
        context_mock.billing_tier = "premium"
        sample_request.context = context_mock
        
        constraints = bridge_advanced._extract_resource_constraints(sample_request)
        
        assert isinstance(constraints, ResourceConstraints)
        assert constraints.max_latency_seconds == 15.0
        assert constraints.min_quality_threshold == 0.85
        assert constraints.is_premium_user is True
        assert constraints.billing_tier == "premium"
    
    def test_provider_availability_mapping(self, bridge_advanced):
        """Test provider availability mapping."""
        availability = bridge_advanced._get_provider_availability()
        
        assert len(availability) == len(ProviderType)
        assert all(isinstance(available, bool) for available in availability.values())
        assert all(provider in ProviderType for provider in availability.keys())
    
    def test_training_data_collection(self, bridge_advanced, sample_request):
        """Test training data collection when enabled."""
        assert bridge_advanced.collect_training_data is True
        
        # Route a request to trigger training data collection
        enhanced_decision = bridge_advanced.route_request(sample_request)
        
        # Should have collected one training sample
        assert len(bridge_advanced.training_data) == 1
        
        training_sample = bridge_advanced.training_data[0]
        assert "timestamp" in training_sample
        assert "request_type" in training_sample
        assert "state_vector" in training_sample
        assert "selected_provider" in training_sample
        assert "selected_model" in training_sample
        assert "selected_persona" in training_sample
        assert "confidence" in training_sample
        assert "encoding_metadata" in training_sample
        
        # Verify state vector is properly serialized
        assert isinstance(training_sample["state_vector"], list)
        assert len(training_sample["state_vector"]) == 112
    
    def test_training_data_size_limit(self, bridge_advanced, sample_request):
        """Test training data size limit enforcement."""
        # Fill training data beyond limit
        for i in range(1050):  # Exceed 1000 limit
            bridge_advanced.route_request(sample_request)
        
        # Should be capped at 1000
        assert len(bridge_advanced.training_data) == 1000
    
    def test_update_provider_performance(self, bridge_advanced):
        """Test provider performance updates."""
        performance_metrics = {
            "success_rate": 0.95,
            "avg_latency": 1.2,
            "avg_quality": 0.9,
            "reputation": 0.92
        }
        
        bridge_advanced.update_provider_performance(
            ProviderType.ANTHROPIC, performance_metrics
        )
        
        provider_key = ProviderType.ANTHROPIC.value
        assert provider_key in bridge_advanced.performance_history
        
        stored_metrics = bridge_advanced.performance_history[provider_key]
        assert stored_metrics["success_rate"] == 0.95
        assert stored_metrics["avg_latency"] == 1.2
        assert stored_metrics["avg_quality"] == 0.9
        assert stored_metrics["reputation"] == 0.92
        assert stored_metrics["interactions"] == 1
    
    def test_performance_exponential_moving_average(self, bridge_advanced):
        """Test exponential moving average in performance updates."""
        provider = ProviderType.GOOGLE
        
        # First update
        bridge_advanced.update_provider_performance(provider, {"success_rate": 0.8})
        assert bridge_advanced.performance_history[provider.value]["success_rate"] == 0.8
        
        # Second update - should use EMA
        bridge_advanced.update_provider_performance(provider, {"success_rate": 1.0})
        
        # EMA calculation: (1-0.2) * 0.8 + 0.2 * 1.0 = 0.64 + 0.2 = 0.84
        expected = 0.8 * 0.8 + 0.2 * 1.0
        actual = bridge_advanced.performance_history[provider.value]["success_rate"]
        assert abs(actual - expected) < 0.01
    
    def test_get_routing_statistics(self, bridge_advanced, sample_request):
        """Test routing statistics retrieval."""
        # Generate some routing data
        bridge_advanced.route_request(sample_request)
        bridge_advanced.route_request(sample_request)
        
        stats = bridge_advanced.get_routing_statistics()
        
        assert isinstance(stats, dict)
        assert stats["total_routes"] == 2
        assert stats["encoding_type"] == "advanced"
        assert stats["state_dimensions"] == 112
        assert stats["training_data_collected"] == 2
        assert stats["provider_performance_tracked"] == 0  # No explicit updates yet
        assert "advanced_router_history" in stats
    
    def test_create_dqn_agent(self, bridge_advanced):
        """Test DQN agent creation."""
        agent = bridge_advanced.create_dqn_agent(learning_rate=0.002)
        
        assert isinstance(agent, DQNRoutingAgent)
        assert agent.state_size == 112  # Advanced state size
        assert agent.action_size == 12
        assert agent.learning_rate == 0.002
    
    def test_create_dqn_agent_basic_encoding(self, bridge_basic):
        """Test DQN agent creation with basic encoding."""
        agent = bridge_basic.create_dqn_agent()
        
        assert isinstance(agent, DQNRoutingAgent)
        assert agent.state_size == 21  # Basic state size
        assert agent.action_size == 12
    
    def test_convert_decision_to_routing_action(self, bridge_advanced):
        """Test conversion from RoutingDecision to RoutingAction."""
        decision = RoutingDecision(
            provider=ProviderType.ANTHROPIC,
            model="claude-4-sonnet",
            persona=PersonaType.ARCHITECT,
            complexity_score=0.7,
            context_score=0.8,
            capability_score=0.95,
            confidence=0.9,
            reasoning="High capability score",
            metadata={}
        )
        
        action = bridge_advanced.convert_decision_to_routing_action(decision)
        
        assert isinstance(action, RoutingAction)
        assert action.provider == ProviderType.ANTHROPIC
        assert action.model == "claude-4-sonnet"
        assert action.strategy == "performance"  # High capability score -> performance strategy
    
    def test_convert_decision_strategy_mapping(self, bridge_advanced):
        """Test strategy mapping in decision conversion."""
        test_cases = [
            # (capability_score, complexity_score, confidence, expected_strategy)
            (0.95, 0.7, 0.9, "performance"),     # High capability
            (0.6, 0.3, 0.8, "cost_efficient"),  # Low complexity
            (0.7, 0.6, 0.9, "task_optimized"),  # High confidence
            (0.6, 0.6, 0.6, "balanced"),        # Default case
        ]
        
        for capability, complexity, confidence, expected_strategy in test_cases:
            decision = RoutingDecision(
                provider=ProviderType.OPENAI,
                model="gpt-4.1",
                persona=PersonaType.DEVELOPER,
                complexity_score=complexity,
                context_score=0.7,
                capability_score=capability,
                confidence=confidence,
                reasoning="Test case",
                metadata={}
            )
            
            action = bridge_advanced.convert_decision_to_routing_action(decision)
            assert action.strategy == expected_strategy, f"Failed for scores: {capability}, {complexity}, {confidence}"
    
    def test_context_to_string_mapping(self, bridge_advanced, sample_request):
        """Test task type to context string mapping."""
        test_cases = [
            (TaskType.CODE_GENERATION, "code_generation"),
            (TaskType.CODE_ANALYSIS, "analysis"),
            (TaskType.DEBUGGING, "debugging"),
            (TaskType.DOCUMENTATION, "documentation"),
            (TaskType.TESTING, "testing"),
            (TaskType.REFACTORING, "refactoring"),
        ]
        
        for task_type, expected_context in test_cases:
            sample_request.task_type = task_type
            context_string = bridge_advanced._map_context_to_string(sample_request)
            assert context_string == expected_context
    
    def test_backward_compatibility_basic_state_vector(self, bridge_basic, sample_request):
        """Test backward compatibility with basic state vector creation."""
        enhanced_decision = bridge_basic.route_request(sample_request)
        
        # Should create basic state vector with expected structure
        state_vector = enhanced_decision.state_vector
        assert len(state_vector) == 21  # Expected basic vector size
        assert isinstance(state_vector, np.ndarray)
        assert state_vector.dtype == np.float32
        
        # Verify basic vector contains expected components
        assert 0.0 <= state_vector[0] <= 1.0  # Task complexity
        # Context type one-hot encoding should be present
        context_sum = np.sum(state_vector[1:11])
        assert context_sum == 1.0  # Exactly one context type should be active
    
    def test_missing_data_handling(self, bridge_advanced):
        """Test handling of missing data in requests."""
        from monkey_coder.models import ExecutionContext, SuperClaudeConfig
        
        context = ExecutionContext(user_id="test-user-minimal", session_id="test-session-minimal")
        superclause_config = SuperClaudeConfig(
            persona=PersonaType.DEVELOPER
        )
        
        minimal_request = ExecuteRequest(
            prompt="test",
            task_type=TaskType.CUSTOM,
            persona_config=None,
            context=context,
            superclause_config=superclause_config
        )
        
        # Should not raise exception
        enhanced_decision = bridge_advanced.route_request(minimal_request)
        
        assert isinstance(enhanced_decision, EnhancedRoutingDecision)
        assert enhanced_decision.state_dimensions == 112
        assert np.all(np.isfinite(enhanced_decision.state_vector))
    
    def test_different_encoding_strategies(self):
        """Test different encoding strategies."""
        strategies = ["minimal", "basic", "standard", "comprehensive"]
        
        for strategy in strategies:
            bridge = DQNRouterBridge(
                use_advanced_encoding=True,
                encoding_strategy=strategy,
                collect_training_data=False
            )
            
            assert isinstance(bridge.state_encoder, AdvancedStateEncoder)
            
            if strategy == "minimal":
                assert not bridge.state_encoder.enable_temporal_features
                assert not bridge.state_encoder.enable_user_personalization
                assert not bridge.state_encoder.enable_dynamic_weighting
            elif strategy == "comprehensive":
                assert bridge.state_encoder.enable_temporal_features
                assert bridge.state_encoder.enable_user_personalization
                assert bridge.state_encoder.enable_dynamic_weighting


class TestConvenienceFunctions:
    """Test convenience functions for easy integration."""
    
    def test_create_dqn_router_bridge_default(self):
        """Test default DQN router bridge creation."""
        bridge = create_dqn_router_bridge()
        
        assert isinstance(bridge, DQNRouterBridge)
        assert bridge.use_advanced_encoding is True
        assert bridge.collect_training_data is False
        assert bridge.state_encoder.enable_temporal_features is True
        assert bridge.state_encoder.enable_user_personalization is True
        assert bridge.state_encoder.enable_dynamic_weighting is True
    
    def test_create_dqn_router_bridge_custom_args(self):
        """Test DQN router bridge creation with custom arguments."""
        bridge = create_dqn_router_bridge(
            encoding_strategy="standard",
            collect_training_data=True
        )
        
        assert bridge.use_advanced_encoding is True
        assert bridge.collect_training_data is True
        assert bridge.state_encoder.enable_temporal_features is True
        assert bridge.state_encoder.enable_user_personalization is True
        assert bridge.state_encoder.enable_dynamic_weighting is False  # Standard strategy


class TestIntegrationWorkflows:
    """Test complete integration workflows."""
    
    @pytest.fixture
    def bridge(self):
        """Create bridge for integration testing."""
        return create_dqn_router_bridge(
            encoding_strategy="comprehensive",
            collect_training_data=True
        )
    
    def test_complete_routing_workflow(self, bridge):
        """Test complete routing workflow from request to training data."""
        from monkey_coder.models import ExecutionContext, SuperClaudeConfig
        
        context = ExecutionContext(user_id="test-user-workflow", session_id="test-session-workflow")
        superclause_config = SuperClaudeConfig(
            persona=PersonaType.ARCHITECT
        )
        
        request = ExecuteRequest(
            prompt="Build a microservice architecture with authentication and rate limiting",
            task_type=TaskType.CODE_GENERATION,
            persona_config=None,
            context=context,
            superclause_config=superclause_config
        )
        
        # Route the request
        enhanced_decision = bridge.route_request(request)
        
        # Verify enhanced decision
        assert isinstance(enhanced_decision, EnhancedRoutingDecision)
        assert enhanced_decision.state_dimensions == 112
        assert enhanced_decision.encoding_metadata["encoding_type"] == "advanced"
        
        # Verify training data was collected
        assert len(bridge.training_data) == 1
        training_sample = bridge.training_data[0]
        assert training_sample["request_type"] == TaskType.CODE_GENERATION.value
        assert len(training_sample["state_vector"]) == 112
        
        # Create DQN agent from bridge
        agent = bridge.create_dqn_agent()
        assert agent.state_size == 112
        
        # Convert routing decision to action
        action = bridge.convert_decision_to_routing_action(
            enhanced_decision.original_decision
        )
        assert isinstance(action, RoutingAction)
        
        # Update performance tracking
        bridge.update_provider_performance(
            enhanced_decision.original_decision.provider,
            {"success_rate": 0.9, "avg_quality": 0.85}
        )
        
        # Get routing statistics
        stats = bridge.get_routing_statistics()
        assert stats["total_routes"] == 1
        assert stats["training_data_collected"] == 1
        assert stats["provider_performance_tracked"] == 1
    
    def test_multiple_requests_performance_tracking(self, bridge):
        """Test performance tracking across multiple requests."""
        from monkey_coder.models import ExecutionContext, SuperClaudeConfig
        
        context1 = ExecutionContext(user_id="test-user-multi1", session_id="test-session-multi1")
        superclause_config1 = SuperClaudeConfig(
            persona=PersonaType.DEVELOPER
        )
        
        context2 = ExecutionContext(user_id="test-user-multi2", session_id="test-session-multi2")
        superclause_config2 = SuperClaudeConfig(
            persona=PersonaType.SECURITY_ANALYST  # Using available persona type instead of ANALYZER
        )
        
        context3 = ExecutionContext(user_id="test-user-multi3", session_id="test-session-multi3")
        superclause_config3 = SuperClaudeConfig(
            persona=PersonaType.REVIEWER
        )
        
        requests = [
            ExecuteRequest(
                prompt="Create a simple function",
                task_type=TaskType.CODE_GENERATION,
                persona_config=None,
                context=context1,
                superclause_config=superclause_config1
            ),
            ExecuteRequest(
                prompt="Debug this error",
                task_type=TaskType.DEBUGGING,
                persona_config=None,
                context=context2,
                superclause_config=superclause_config2
            ),
            ExecuteRequest(
                prompt="Analyze code quality",
                task_type=TaskType.CODE_ANALYSIS,
                persona_config=None,
                context=context3,
                superclause_config=superclause_config3
            )
        ]
        
        routing_decisions = []
        for request in requests:
            enhanced_decision = bridge.route_request(request)
            routing_decisions.append(enhanced_decision)
            
            # Simulate performance feedback
            bridge.update_provider_performance(
                enhanced_decision.original_decision.provider,
                {
                    "success_rate": 0.8 + np.random.rand() * 0.2,
                    "avg_quality": 0.7 + np.random.rand() * 0.3,
                    "avg_latency": 1.0 + np.random.rand() * 2.0
                }
            )
        
        # Verify all requests were processed
        assert len(routing_decisions) == 3
        assert len(bridge.training_data) == 3
        
        # Verify performance tracking
        stats = bridge.get_routing_statistics()
        assert stats["total_routes"] == 3
        assert stats["provider_performance_tracked"] >= 1  # At least one provider tracked
        
        # Verify different task types were handled
        task_types = [
            sample["request_type"] for sample in bridge.training_data
        ]
        assert TaskType.CODE_GENERATION.value in task_types
        assert TaskType.DEBUGGING.value in task_types
        assert TaskType.CODE_ANALYSIS.value in task_types
    
    def test_integration_with_different_complexities(self, bridge):
        """Test integration with requests of varying complexity."""
        from monkey_coder.models import ExecutionContext, SuperClaudeConfig
        
        complexity_prompts = [
            ("Hello world", TaskType.CODE_GENERATION),  # Simple
            ("Create a REST API with user authentication", TaskType.CODE_GENERATION),  # Moderate
            ("Build a distributed microservices architecture with event sourcing and CQRS", TaskType.CODE_GENERATION),  # Complex
        ]
        
        decisions = []
        for i, (prompt, task_type) in enumerate(complexity_prompts):
            context = ExecutionContext(user_id=f"test-user-complex{i}", session_id=f"test-session-complex{i}")
            
            # Use different persona types for variety
            persona_types = [PersonaType.DEVELOPER, PersonaType.ARCHITECT, PersonaType.PERFORMANCE_EXPERT]
            superclause_config = SuperClaudeConfig(
                persona=persona_types[i]
            )
            
            request = ExecuteRequest(
                prompt=prompt,
                task_type=task_type,
                persona_config=None,
                context=context,
                superclause_config=superclause_config
            )
            
            enhanced_decision = bridge.route_request(request)
            decisions.append(enhanced_decision)
        
        # Verify different complexity levels were captured
        complexity_scores = [
            d.original_decision.complexity_score for d in decisions
        ]
        
        # Verify that we get different complexity scores (the router analyzes differently)
        # The complexity is not necessarily increasing with prompt length
        assert len(set(complexity_scores)) > 1, f"Expected different complexity scores, got {complexity_scores}"
        assert all(0.0 <= score <= 1.0 for score in complexity_scores), f"Complexity scores should be between 0 and 1, got {complexity_scores}"
        
        # Verify state vectors capture complexity differences
        state_vectors = [d.state_vector for d in decisions]
        
        # First element of state vector should be complexity score
        state_complexities = [vec[0] for vec in state_vectors]
        assert len(set(state_complexities)) > 1, f"Expected different state complexity values, got {state_complexities}"
        assert all(0.0 <= complexity <= 1.0 for complexity in state_complexities), f"State complexities should be between 0 and 1, got {state_complexities}"