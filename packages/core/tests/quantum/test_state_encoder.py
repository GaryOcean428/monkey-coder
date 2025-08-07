"""
Tests for Advanced State Encoder for Quantum Routing

This module tests the comprehensive state representation system that enhances
the basic DQN routing state with sophisticated encoding strategies for
improved learning and decision-making accuracy.
"""

import pytest
import numpy as np
import time
from typing import Dict, Set
from unittest.mock import Mock, patch

from monkey_coder.models import ProviderType, TaskType
from monkey_coder.quantum.state_encoder import (
    AdvancedStateEncoder,
    TaskContextProfile,
    ProviderPerformanceHistory, 
    UserPreferences,
    ResourceConstraints,
    ContextComplexity,
    TimeWindow,
    create_state_encoder
)


class TestTaskContextProfile:
    """Test task context profile data structure."""
    
    def test_task_context_creation(self):
        """Test creating task context profile."""
        profile = TaskContextProfile(
            task_type=TaskType.CODE_GENERATION,
            estimated_complexity=0.7,
            complexity_category=ContextComplexity.COMPLEX,
            domain_requirements={"programming", "analysis"},
            quality_threshold=0.8,
            latency_requirement=15.0,
            cost_sensitivity=0.3,
            is_production=True,
            requires_reasoning=True,
            requires_creativity=False
        )
        
        assert profile.task_type == TaskType.CODE_GENERATION
        assert profile.estimated_complexity == 0.7
        assert profile.complexity_category == ContextComplexity.COMPLEX
        assert profile.domain_requirements == {"programming", "analysis"}
        assert profile.quality_threshold == 0.8
        assert profile.latency_requirement == 15.0
        assert profile.cost_sensitivity == 0.3
        assert profile.is_production is True
        assert profile.requires_reasoning is True
        assert profile.requires_creativity is False
    
    def test_task_context_defaults(self):
        """Test task context with default values."""
        profile = TaskContextProfile(
            task_type=TaskType.DEBUGGING,
            estimated_complexity=0.5,
            complexity_category=ContextComplexity.MODERATE,
            domain_requirements={"debugging"}
        )
        
        assert profile.quality_threshold == 0.7  # Default
        assert profile.latency_requirement == 30.0  # Default
        assert profile.cost_sensitivity == 0.5  # Default
        assert profile.is_production is False  # Default
        assert profile.requires_reasoning is False  # Default
        assert profile.requires_creativity is False  # Default
        assert profile.requires_accuracy is True  # Default


class TestProviderPerformanceHistory:
    """Test provider performance history."""
    
    def test_performance_history_creation(self):
        """Test creating provider performance history."""
        history = ProviderPerformanceHistory(
            recent_success_rate=0.9,
            recent_avg_latency=1.5,
            recent_avg_quality=0.85,
            recent_cost_efficiency=0.8,
            long_term_reputation=0.9,
            total_interactions=500
        )
        
        assert history.recent_success_rate == 0.9
        assert history.recent_avg_latency == 1.5
        assert history.recent_avg_quality == 0.85
        assert history.recent_cost_efficiency == 0.8
        assert history.long_term_reputation == 0.9
        assert history.total_interactions == 500
    
    def test_performance_vector_generation(self):
        """Test performance history vector generation."""
        history = ProviderPerformanceHistory(
            recent_success_rate=0.9,
            recent_avg_latency=2.0,
            recent_avg_quality=0.8,
            total_interactions=1000
        )
        
        vector = history.get_performance_vector()
        
        assert isinstance(vector, np.ndarray)
        assert len(vector) == 11  # Expected number of performance metrics
        assert vector.dtype == np.float32
        assert 0.0 <= vector[0] <= 1.0  # Success rate should be normalized
        assert vector[1] == 0.2  # Latency normalized (2.0 / 10.0)
        assert vector[2] == 0.8  # Quality score
        assert vector[-1] == 1.0  # Experience normalized (min(1000/1000, 1.0))
    
    def test_domain_expertise_tracking(self):
        """Test domain-specific expertise tracking."""
        history = ProviderPerformanceHistory()
        history.domain_expertise = {
            "programming": 0.9,
            "analysis": 0.7,
            "creative": 0.5
        }
        history.complexity_performance = {
            ContextComplexity.SIMPLE: 0.95,
            ContextComplexity.COMPLEX: 0.75
        }
        
        assert history.domain_expertise["programming"] == 0.9
        assert history.complexity_performance[ContextComplexity.SIMPLE] == 0.95


class TestUserPreferences:
    """Test user preferences system."""
    
    def test_user_preferences_creation(self):
        """Test creating user preferences."""
        preferences = UserPreferences(
            provider_preference_scores={
                ProviderType.OPENAI: 0.8,
                ProviderType.ANTHROPIC: 0.9
            },
            quality_vs_speed_preference=0.7,
            cost_sensitivity=0.3,
            risk_tolerance=0.6
        )
        
        assert preferences.provider_preference_scores[ProviderType.OPENAI] == 0.8
        assert preferences.provider_preference_scores[ProviderType.ANTHROPIC] == 0.9
        assert preferences.quality_vs_speed_preference == 0.7
        assert preferences.cost_sensitivity == 0.3
        assert preferences.risk_tolerance == 0.6
    
    def test_preference_vector_generation(self):
        """Test user preference vector generation."""
        preferences = UserPreferences(
            provider_preference_scores={
                ProviderType.OPENAI: 0.8,
                ProviderType.ANTHROPIC: 0.9,
                ProviderType.GOOGLE: 0.6
            },
            quality_vs_speed_preference=0.7,
            personalization_strength=0.5
        )
        
        vector = preferences.get_preference_vector()
        
        assert isinstance(vector, np.ndarray)
        assert len(vector) == 13  # 5 providers + 4 strategies + 4 other preferences
        assert vector.dtype == np.float32
        
        # Check provider preferences
        assert vector[0] == 0.8  # OpenAI preference
        assert vector[1] == 0.9  # Anthropic preference  
        assert vector[2] == 0.6  # Google preference
        
        # Check other preferences
        assert vector[-4] == 0.7  # Quality vs speed
        assert vector[-1] == 0.5  # Personalization strength
    
    def test_default_strategy_preferences(self):
        """Test default strategy preferences are balanced."""
        preferences = UserPreferences()
        
        for strategy, weight in preferences.preferred_strategies.items():
            assert weight == 0.25  # Should be equally weighted by default


class TestResourceConstraints:
    """Test resource constraints system."""
    
    def test_resource_constraints_creation(self):
        """Test creating resource constraints."""
        constraints = ResourceConstraints(
            max_cost_per_request=5.0,
            max_latency_seconds=10.0,
            min_quality_threshold=0.8,
            is_premium_user=True,
            billing_tier="premium"
        )
        
        assert constraints.max_cost_per_request == 5.0
        assert constraints.max_latency_seconds == 10.0
        assert constraints.min_quality_threshold == 0.8
        assert constraints.is_premium_user is True
        assert constraints.billing_tier == "premium"
    
    def test_constraint_vector_generation(self):
        """Test resource constraint vector generation."""
        constraints = ResourceConstraints(
            max_cost_per_request=10.0,
            max_latency_seconds=30.0,
            min_quality_threshold=0.9,
            is_premium_user=True,
            billing_tier="enterprise"
        )
        
        vector = constraints.get_constraint_vector()
        
        assert isinstance(vector, np.ndarray)
        assert len(vector) == 10  # Expected constraint features
        assert vector.dtype == np.float32
        
        assert vector[0] == 1.0  # Max cost normalized (10.0 / 10.0)
        assert vector[1] == 0.5  # Max latency normalized (30.0 / 60.0)
        assert vector[2] == 0.9  # Min quality threshold
        assert vector[7] == 1.0  # Is premium user
        assert vector[9] == 1.0  # Enterprise billing tier
    
    def test_billing_tier_encoding(self):
        """Test billing tier encoding."""
        for tier, expected in [
            ("free", 0.0),
            ("standard", 0.33),
            ("premium", 0.66), 
            ("enterprise", 1.0)
        ]:
            constraints = ResourceConstraints(billing_tier=tier)
            vector = constraints.get_constraint_vector()
            assert abs(vector[9] - expected) < 0.01  # Allow small floating point error


class TestAdvancedStateEncoder:
    """Test the advanced state encoder."""
    
    @pytest.fixture
    def encoder(self):
        """Create standard state encoder for testing."""
        return AdvancedStateEncoder(
            enable_temporal_features=True,
            enable_user_personalization=True,
            enable_dynamic_weighting=True
        )
    
    @pytest.fixture
    def minimal_encoder(self):
        """Create minimal state encoder for testing."""
        return AdvancedStateEncoder(
            enable_temporal_features=False,
            enable_user_personalization=False,
            enable_dynamic_weighting=False
        )
    
    @pytest.fixture
    def sample_task_context(self):
        """Create sample task context."""
        return TaskContextProfile(
            task_type=TaskType.CODE_GENERATION,
            estimated_complexity=0.6,
            complexity_category=ContextComplexity.MODERATE,
            domain_requirements={"programming"},
            quality_threshold=0.8,
            latency_requirement=20.0,
            is_production=True,
            requires_reasoning=True
        )
    
    @pytest.fixture  
    def sample_provider_history(self):
        """Create sample provider history."""
        history = {}
        for provider in ProviderType:
            history[provider] = ProviderPerformanceHistory(
                recent_success_rate=0.85,
                recent_avg_quality=0.8,
                long_term_reputation=0.82,
                total_interactions=200
            )
        return history
    
    @pytest.fixture
    def sample_user_preferences(self):
        """Create sample user preferences."""
        return UserPreferences(
            provider_preference_scores={
                ProviderType.OPENAI: 0.8,
                ProviderType.ANTHROPIC: 0.9
            },
            quality_vs_speed_preference=0.7
        )
    
    @pytest.fixture
    def sample_resource_constraints(self):
        """Create sample resource constraints."""
        return ResourceConstraints(
            max_latency_seconds=25.0,
            min_quality_threshold=0.75,
            is_premium_user=True
        )
    
    @pytest.fixture
    def sample_provider_availability(self):
        """Create sample provider availability."""
        return {
            ProviderType.OPENAI: True,
            ProviderType.ANTHROPIC: True,
            ProviderType.GOOGLE: True,
            ProviderType.GROQ: False,  # Simulate unavailable provider
            ProviderType.GROK: True
        }
    
    def test_encoder_initialization(self, encoder):
        """Test encoder initialization."""
        assert encoder.enable_temporal_features is True
        assert encoder.enable_user_personalization is True
        assert encoder.enable_dynamic_weighting is True
        assert encoder.base_dimensions == 15
        assert encoder.provider_dimensions == 60  # 5 providers × (1 availability + 11 metrics)
        assert encoder.preference_dimensions == 13
        assert encoder.constraint_dimensions == 10
        assert encoder.temporal_dimensions == 8
        assert encoder.context_dimensions == 6
        assert encoder.total_dimensions == 112  # Sum of all dimensions
    
    def test_minimal_encoder_dimensions(self, minimal_encoder):
        """Test minimal encoder has correct dimensions."""
        assert minimal_encoder.enable_temporal_features is False
        assert minimal_encoder.enable_user_personalization is False
        assert minimal_encoder.temporal_dimensions == 0
        assert minimal_encoder.total_dimensions == 104  # Without temporal features (8 dimensions)
    
    def test_encode_state_full(
        self, 
        encoder,
        sample_task_context,
        sample_provider_history,
        sample_user_preferences,
        sample_resource_constraints,
        sample_provider_availability
    ):
        """Test complete state encoding."""
        state_vector = encoder.encode_state(
            task_context=sample_task_context,
            provider_history=sample_provider_history,
            user_preferences=sample_user_preferences,
            resource_constraints=sample_resource_constraints,
            provider_availability=sample_provider_availability
        )
        
        assert isinstance(state_vector, np.ndarray)
        assert len(state_vector) == encoder.total_dimensions
        assert state_vector.dtype == np.float32
        assert np.all(np.isfinite(state_vector))  # No NaN or inf values
        
        # Check value ranges are reasonable
        assert np.all(state_vector >= -2.0)  # No extremely negative values
        assert np.all(state_vector <= 2.0)   # No extremely positive values
    
    def test_encode_task_context(self, encoder, sample_task_context):
        """Test task context encoding."""
        features = encoder._encode_task_context(sample_task_context)
        
        assert len(features) == encoder.base_dimensions
        assert features[0] == 0.6  # Complexity
        assert features[1] == 0.0  # Not simple
        assert features[2] == 1.0  # Is moderate
        assert features[3] == 0.0  # Not complex
        assert features[4] == 0.0  # Not critical
        assert features[5] == 1.0  # Is code generation
        assert features[9] == 0.8  # Quality threshold
        assert features[12] == 1.0  # Requires reasoning
        assert features[14] == 1.0  # Is production
    
    def test_encode_provider_history(
        self, 
        encoder, 
        sample_provider_history,
        sample_provider_availability
    ):
        """Test provider history encoding."""
        features = encoder._encode_provider_history(
            sample_provider_history, 
            sample_provider_availability
        )
        
        assert len(features) == encoder.provider_dimensions
        
        # Check first provider (OpenAI) - should be available
        assert features[0] == 1.0  # Available
        # Next 11 features should be performance metrics
        assert 0.0 <= features[1] <= 1.0  # Success rate
        assert 0.0 <= features[2] <= 1.0  # Normalized latency
        
        # Check unavailable provider (Groq) - index 4 * 12 = 48
        groq_start = 4 * 12  # Groq is 5th provider (0-indexed: 4), 12 features per provider
        assert features[groq_start] == 0.0  # Not available
        # Should have neutral values for performance
        for i in range(1, 12):
            assert features[groq_start + i] == 0.5
    
    def test_encode_temporal_context(self, encoder, sample_task_context):
        """Test temporal context encoding."""
        features = encoder._encode_temporal_context(sample_task_context)
        
        assert len(features) == encoder.temporal_dimensions
        assert all(isinstance(f, np.floating) for f in features)
        
        # Check cyclical encodings are in valid range
        assert -1.0 <= features[4] <= 1.0  # sin(hour)
        assert -1.0 <= features[5] <= 1.0  # cos(hour)
        assert -1.0 <= features[6] <= 1.0  # sin(day)
        assert -1.0 <= features[7] <= 1.0  # cos(day)
    
    def test_encode_contextual_factors(
        self, 
        encoder,
        sample_task_context,
        sample_provider_availability
    ):
        """Test contextual factors encoding."""
        features = encoder._encode_contextual_factors(
            sample_task_context,
            sample_provider_availability
        )
        
        assert len(features) == encoder.context_dimensions
        
        # Provider availability ratio: 4/5 = 0.8 (Groq is unavailable)
        assert abs(features[0] - 0.8) < 0.01
        
        # Domain complexity: 1 domain / 5 max = 0.2
        assert abs(features[1] - 0.2) < 0.01
        
        # Non-linear complexity: 0.6^2 = 0.36
        assert abs(features[3] - 0.36) < 0.01
    
    def test_create_routing_state_convenience(self, encoder):
        """Test convenience method for creating routing state."""
        provider_availability = {provider: True for provider in ProviderType}
        
        state_vector = encoder.create_routing_state(
            task_type=TaskType.CODE_ANALYSIS,
            prompt="Analyze this code for potential security vulnerabilities",
            complexity=0.8,
            context_requirements={
                "timeout": 45.0,
                "quality_threshold": 0.9,
                "is_production": True
            },
            provider_availability=provider_availability
        )
        
        assert isinstance(state_vector, np.ndarray)
        assert len(state_vector) == encoder.total_dimensions
        assert np.all(np.isfinite(state_vector))
    
    def test_domain_requirement_extraction(self, encoder):
        """Test domain requirement extraction from prompts."""
        test_cases = [
            ("Write a creative story about robots", {"creative"}),
            ("Analyze the performance of this algorithm", {"analysis"}),
            ("Calculate the fibonacci sequence", {"mathematical"}),
            ("Debug this Python function", {"programming", "debugging"}),
            ("Explain why this logic is flawed", {"reasoning", "analysis"})
        ]
        
        for prompt, expected_domains in test_cases:
            domains = encoder._extract_domain_requirements(prompt, TaskType.CODE_GENERATION)
            assert domains.intersection(expected_domains), f"Failed for prompt: {prompt}"
    
    def test_complexity_category_estimation(self, encoder):
        """Test complexity category estimation."""
        test_cases = [
            (0.1, ContextComplexity.SIMPLE),
            (0.3, ContextComplexity.MODERATE),
            (0.6, ContextComplexity.COMPLEX),
            (0.9, ContextComplexity.CRITICAL)
        ]
        
        for complexity, expected_category in test_cases:
            category = encoder._estimate_complexity_category(complexity)
            assert category == expected_category
    
    def test_reasoning_detection(self, encoder):
        """Test reasoning requirement detection."""
        reasoning_prompts = [
            ("Explain why this code is inefficient", True),
            ("Analyze the root cause of this bug", True), 
            ("How does this algorithm work?", True),
            ("Create a simple hello world program", False),
            ("Format this JSON data", False)
        ]
        
        for prompt, expected in reasoning_prompts:
            result = encoder._requires_reasoning(prompt, TaskType.CODE_ANALYSIS)
            assert result == expected, f"Failed for prompt: {prompt}"
    
    def test_creativity_detection(self, encoder):
        """Test creativity requirement detection."""
        creativity_prompts = [
            ("Design a creative solution for this problem", True),
            ("Generate innovative ideas for this feature", True),
            ("Brainstorm different approaches", True),
            ("Fix this bug", False),
            ("Optimize this function", False)
        ]
        
        for prompt, expected in creativity_prompts:
            result = encoder._requires_creativity(prompt, TaskType.CODE_GENERATION)
            assert result == expected, f"Failed for prompt: {prompt}"
    
    def test_dynamic_weighting(
        self, 
        encoder,
        sample_task_context,
        sample_provider_history,
        sample_user_preferences,
        sample_resource_constraints,
        sample_provider_availability
    ):
        """Test dynamic weighting application."""
        # Create production task with high accuracy requirements
        production_context = TaskContextProfile(
            task_type=TaskType.CODE_GENERATION,
            estimated_complexity=0.7,
            complexity_category=ContextComplexity.COMPLEX,
            domain_requirements={"programming"},
            is_production=True,
            requires_accuracy=True,
            quality_threshold=0.9,
            latency_requirement=8.0  # Time-sensitive
        )
        
        # Encode without dynamic weighting
        encoder_no_weighting = AdvancedStateEncoder(enable_dynamic_weighting=False)
        state_no_weight = encoder_no_weighting.encode_state(
            task_context=production_context,
            provider_history=sample_provider_history,
            user_preferences=sample_user_preferences,
            resource_constraints=sample_resource_constraints,
            provider_availability=sample_provider_availability
        )
        
        # Encode with dynamic weighting
        state_with_weight = encoder.encode_state(
            task_context=production_context,
            provider_history=sample_provider_history,
            user_preferences=sample_user_preferences,
            resource_constraints=sample_resource_constraints,
            provider_availability=sample_provider_availability
        )
        
        # Values should be different due to weighting
        assert not np.array_equal(state_no_weight, state_with_weight)
        
        # Provider performance features should be boosted (multiplied by 1.2)
        provider_start = encoder.base_dimensions
        provider_end = provider_start + encoder.provider_dimensions
        
        # Some provider features should be larger in weighted version
        weighted_provider_features = state_with_weight[provider_start:provider_end]
        unweighted_provider_features = state_no_weight[provider_start:provider_end]
        
        # At least some features should be boosted
        boosted_count = np.sum(weighted_provider_features > unweighted_provider_features)
        assert boosted_count > 0
    
    def test_state_size_property(self, encoder):
        """Test state size property."""
        assert encoder.state_size == encoder.total_dimensions
    
    def test_feature_names_generation(self, encoder):
        """Test feature names generation."""
        feature_names = encoder.get_feature_names()
        
        assert len(feature_names) == encoder.total_dimensions
        assert all(isinstance(name, str) for name in feature_names)
        
        # Check for expected feature categories
        name_str = " ".join(feature_names)
        assert "task_complexity" in name_str
        assert "openai_available" in name_str
        assert "pref_openai" in name_str
        assert "cost_weight" in name_str
        assert "time_of_day" in name_str  # Temporal feature


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_create_state_encoder_strategies(self):
        """Test state encoder creation with different strategies."""
        strategies = ["minimal", "basic", "standard", "comprehensive"]
        
        for strategy in strategies:
            encoder = create_state_encoder(strategy)
            assert isinstance(encoder, AdvancedStateEncoder)
            
            if strategy == "minimal":
                assert not encoder.enable_temporal_features
                assert not encoder.enable_user_personalization
                assert not encoder.enable_dynamic_weighting
            elif strategy == "comprehensive":
                assert encoder.enable_temporal_features
                assert encoder.enable_user_personalization
                assert encoder.enable_dynamic_weighting
    
    def test_create_state_encoder_custom_args(self):
        """Test state encoder creation with custom arguments."""
        encoder = create_state_encoder(
            encoding_strategy="standard",
            context_window_size=20
        )
        
        assert encoder.context_window_size == 20
        assert encoder.enable_temporal_features is True
        assert encoder.enable_user_personalization is True
        assert encoder.enable_dynamic_weighting is False


class TestStateEncoderIntegration:
    """Integration tests for state encoder."""
    
    def test_state_encoder_with_missing_data(self):
        """Test encoder handles missing data gracefully."""
        encoder = AdvancedStateEncoder()
        
        # Create minimal context with missing data
        task_context = TaskContextProfile(
            task_type=TaskType.TESTING,
            estimated_complexity=0.4,
            complexity_category=ContextComplexity.MODERATE,
            domain_requirements=set()  # Empty domain requirements
        )
        
        provider_history = {
            ProviderType.OPENAI: ProviderPerformanceHistory(),
            # Missing some providers
        }
        
        user_preferences = UserPreferences()  # Default preferences
        resource_constraints = ResourceConstraints()  # Default constraints
        provider_availability = {ProviderType.OPENAI: True}  # Partial availability
        
        # Should not raise exception
        state_vector = encoder.encode_state(
            task_context=task_context,
            provider_history=provider_history,
            user_preferences=user_preferences,
            resource_constraints=resource_constraints,
            provider_availability=provider_availability
        )
        
        assert isinstance(state_vector, np.ndarray)
        assert len(state_vector) == encoder.total_dimensions
        assert np.all(np.isfinite(state_vector))
    
    def test_state_encoder_consistency(self):
        """Test encoder produces consistent results for same inputs."""
        encoder = AdvancedStateEncoder(enable_dynamic_weighting=False)  # Disable for consistency
        
        # Create fixed inputs
        task_context = TaskContextProfile(
            task_type=TaskType.CODE_GENERATION,
            estimated_complexity=0.5,
            complexity_category=ContextComplexity.MODERATE,
            domain_requirements={"programming"},
            time_of_day=0.5,  # Fixed time
            day_of_week=3     # Fixed day
        )
        
        provider_history = {provider: ProviderPerformanceHistory() for provider in ProviderType}
        user_preferences = UserPreferences()
        resource_constraints = ResourceConstraints()
        provider_availability = {provider: True for provider in ProviderType}
        
        # Encode multiple times
        state1 = encoder.encode_state(task_context, provider_history, user_preferences,
                                     resource_constraints, provider_availability)
        state2 = encoder.encode_state(task_context, provider_history, user_preferences,
                                     resource_constraints, provider_availability)
        
        # Should be identical
        np.testing.assert_array_equal(state1, state2)
    
    def test_performance_scaling(self):
        """Test encoder performance with different configurations."""
        import time
        
        # Test different encoder configurations
        configs = [
            ("minimal", {"enable_temporal_features": False, "enable_user_personalization": False}),
            ("standard", {"enable_temporal_features": True, "enable_user_personalization": True}),
            ("comprehensive", {"enable_dynamic_weighting": True})
        ]
        
        for config_name, config_args in configs:
            encoder = AdvancedStateEncoder(**config_args)
            
            # Simple context for performance test
            provider_availability = {provider: True for provider in ProviderType}
            
            start_time = time.perf_counter()
            
            # Encode 100 states
            for _ in range(100):
                encoder.create_routing_state(
                    task_type=TaskType.CODE_GENERATION,
                    prompt="Test prompt",
                    complexity=0.5,
                    context_requirements={},
                    provider_availability=provider_availability
                )
            
            encoding_time = time.perf_counter() - start_time
            
            # Should complete within reasonable time (< 1 second for 100 encodings)
            assert encoding_time < 1.0, f"{config_name} encoding took {encoding_time:.3f}s"
    
    def test_memory_usage(self):
        """Test encoder memory usage is reasonable."""
        # Create multiple encoders to test memory scaling
        encoders = []
        for i in range(10):
            encoder = AdvancedStateEncoder()
            encoders.append(encoder)
        
        # Memory usage should be reasonable for 10 encoders
        # This is mainly a smoke test to ensure no memory leaks
        assert len(encoders) == 10
        
        # Cleanup
        del encoders
    
    def test_edge_case_handling(self):
        """Test encoder handles edge cases."""
        encoder = AdvancedStateEncoder()
        
        # Test with extreme values
        extreme_context = TaskContextProfile(
            task_type=TaskType.CUSTOM,
            estimated_complexity=1.0,  # Maximum complexity
            complexity_category=ContextComplexity.CRITICAL,
            domain_requirements={"domain1", "domain2", "domain3", "domain4", "domain5", "domain6"},  # Many domains
            quality_threshold=1.0,     # Maximum quality
            latency_requirement=0.1,   # Very tight latency
            cost_sensitivity=1.0       # Maximum cost sensitivity
        )
        
        extreme_history = {}
        for provider in ProviderType:
            extreme_history[provider] = ProviderPerformanceHistory(
                recent_success_rate=1.0,
                recent_avg_latency=0.1,
                recent_avg_quality=1.0,
                total_interactions=10000
            )
        
        extreme_preferences = UserPreferences(
            provider_preference_scores={provider: 1.0 for provider in ProviderType},
            quality_vs_speed_preference=1.0,
            cost_sensitivity=1.0,
            risk_tolerance=0.0
        )
        
        extreme_constraints = ResourceConstraints(
            max_cost_per_request=0.01,  # Very low cost constraint
            max_latency_seconds=0.5,    # Very tight latency
            min_quality_threshold=0.99, # Very high quality requirement
            is_premium_user=True,
            billing_tier="enterprise"
        )
        
        provider_availability = {provider: True for provider in ProviderType}
        
        # Should handle extreme values without error
        state_vector = encoder.encode_state(
            task_context=extreme_context,
            provider_history=extreme_history,
            user_preferences=extreme_preferences,
            resource_constraints=extreme_constraints,
            provider_availability=provider_availability
        )
        
        assert isinstance(state_vector, np.ndarray)
        assert len(state_vector) == encoder.total_dimensions
        assert np.all(np.isfinite(state_vector))
        
        # Values should still be in reasonable ranges
        assert np.all(state_vector >= -5.0)
        assert np.all(state_vector <= 5.0)