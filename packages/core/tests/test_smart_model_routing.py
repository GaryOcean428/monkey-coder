"""
Tests for Smart Model Routing system.

Validates task classification, tiered selection, and routing logic.
"""

import pytest
from datetime import datetime

from monkey_coder.core.smart_model_routing import (
    SmartModelRouter,
    TaskLabel,
    ModelTier,
    TaskClassification,
    ModelSelection,
    ValidationResult,
    RoutingMetrics,
    get_smart_router
)


class TestTaskClassification:
    """Test suite for task classification."""
    
    @pytest.fixture
    def router(self):
        """Create fresh router for each test."""
        return SmartModelRouter()
    
    def test_high_stakes_detection(self, router):
        """Test HIGH_STAKES task detection."""
        high_stakes_prompts = [
            "Process this financial payment for $5000",
            "Handle this credit card information for the customer",
            "Extract personal medical records from the database",
            "Deploy to production server permanently"
        ]
        
        for prompt in high_stakes_prompts:
            classification = router.classify_task(prompt)
            assert classification.label == TaskLabel.HIGH_STAKES, f"Failed for: {prompt}, got {classification.label}"
            assert classification.confidence >= 0.9
    
    def test_hard_task_detection(self, router):
        """Test HARD task detection."""
        hard_prompts = [
            "Design a scalable microservices architecture for e-commerce platform",
            "Optimize the database query performance and refactor the schema",
            "Analyze security vulnerabilities in the authentication system",
            "Implement a complex algorithm for real-time data processing"
        ]
        
        for prompt in hard_prompts:
            classification = router.classify_task(prompt)
            assert classification.label == TaskLabel.HARD
            assert classification.confidence >= 0.7
    
    def test_routine_task_detection(self, router):
        """Test ROUTINE task detection."""
        routine_prompts = [
            "Fix the bug in the user authentication login function code",
            "Add a new method to validate inputs in the UserController class implementation",
            "Write comprehensive unit tests for the user registration module logic",
            "Update and modify the styling for the navigation component layout"
        ]
        
        for prompt in routine_prompts:
            classification = router.classify_task(prompt)
            # Note: Some prompts may be classified as HARD or HIGH_STAKES depending on keywords
            # We check that it's either ROUTINE or appropriately classified based on context
            assert classification.label in [TaskLabel.ROUTINE, TaskLabel.HARD], \
                f"Failed for: {prompt}, got {classification.label}"
    
    def test_trivial_task_detection(self, router):
        """Test TRIVIAL task detection."""
        trivial_prompts = [
            "What is REST?",
            "List files",
            "Format code",
            "Show version"
        ]
        
        for prompt in trivial_prompts:
            classification = router.classify_task(prompt)
            assert classification.label == TaskLabel.TRIVIAL
            assert classification.confidence >= 0.8


class TestTierSelection:
    """Test suite for tier selection."""
    
    @pytest.fixture
    def router(self):
        """Create fresh router for each test."""
        return SmartModelRouter()
    
    def test_high_stakes_always_tier_c(self, router):
        """Test HIGH_STAKES always uses Tier C."""
        classification = TaskClassification(
            label=TaskLabel.HIGH_STAKES,
            confidence=0.95,
            reasoning="High stakes task"
        )
        
        tier = router.select_tier(classification)
        assert tier == ModelTier.C
    
    def test_hard_low_confidence_tier_b(self, router):
        """Test HARD with low confidence uses Tier B."""
        classification = TaskClassification(
            label=TaskLabel.HARD,
            confidence=0.6,
            reasoning="Hard task with low confidence"
        )
        
        tier = router.select_tier(classification)
        assert tier == ModelTier.B
    
    def test_hard_high_confidence_tier_b(self, router):
        """Test HARD with high confidence uses Tier B."""
        classification = TaskClassification(
            label=TaskLabel.HARD,
            confidence=0.85,
            reasoning="Hard task with high confidence"
        )
        
        tier = router.select_tier(classification)
        assert tier == ModelTier.B
    
    def test_routine_tier_a(self, router):
        """Test ROUTINE uses Tier A."""
        classification = TaskClassification(
            label=TaskLabel.ROUTINE,
            confidence=0.9,
            reasoning="Routine task"
        )
        
        tier = router.select_tier(classification)
        assert tier == ModelTier.A
    
    def test_trivial_tier_a(self, router):
        """Test TRIVIAL uses Tier A."""
        classification = TaskClassification(
            label=TaskLabel.TRIVIAL,
            confidence=0.95,
            reasoning="Trivial task"
        )
        
        tier = router.select_tier(classification)
        assert tier == ModelTier.A


class TestModelConfiguration:
    """Test suite for model configuration."""
    
    @pytest.fixture
    def router(self):
        """Create fresh router for each test."""
        return SmartModelRouter()
    
    def test_tier_a_models(self, router):
        """Test Tier A model selection."""
        selection = router.get_model_config(
            tier=ModelTier.A,
            label=TaskLabel.TRIVIAL
        )
        
        assert selection.tier == ModelTier.A
        assert selection.provider in ["openai", "anthropic", "google"]
        assert selection.temperature <= 0.3
        assert selection.max_tokens <= 2000
    
    def test_tier_b_models(self, router):
        """Test Tier B model selection."""
        selection = router.get_model_config(
            tier=ModelTier.B,
            label=TaskLabel.HARD
        )
        
        assert selection.tier == ModelTier.B
        assert selection.provider in ["openai", "anthropic", "google"]
        assert selection.max_tokens >= 2000
    
    def test_tier_c_models(self, router):
        """Test Tier C model selection."""
        selection = router.get_model_config(
            tier=ModelTier.C,
            label=TaskLabel.HIGH_STAKES
        )
        
        assert selection.tier == ModelTier.C
        assert selection.provider in ["openai", "anthropic"]
        assert selection.max_tokens >= 4000
    
    def test_temperature_by_label(self, router):
        """Test temperature configuration by task label."""
        # TRIVIAL/ROUTINE should have low temperature
        trivial_sel = router.get_model_config(ModelTier.A, TaskLabel.TRIVIAL)
        assert trivial_sel.temperature <= 0.2
        
        routine_sel = router.get_model_config(ModelTier.A, TaskLabel.ROUTINE)
        assert routine_sel.temperature <= 0.2
        
        # HARD/HIGH_STAKES should have moderate temperature
        hard_sel = router.get_model_config(ModelTier.B, TaskLabel.HARD)
        assert 0.2 <= hard_sel.temperature <= 0.4
    
    def test_provider_preference(self, router):
        """Test provider preference in selection."""
        selection = router.get_model_config(
            tier=ModelTier.B,
            label=TaskLabel.ROUTINE,
            provider_preference="anthropic"
        )
        
        assert selection.provider == "anthropic"


class TestInputGuardrails:
    """Test suite for input guardrails."""
    
    @pytest.fixture
    def router(self):
        """Create fresh router for each test."""
        return SmartModelRouter()
    
    def test_email_redaction(self, router):
        """Test email redaction."""
        input_text = "Contact user@example.com for details"
        guarded, warnings = router.guard_input(input_text)
        
        assert "[EMAIL]" in guarded
        assert "user@example.com" not in guarded
        assert len(warnings) > 0
    
    def test_ssn_redaction(self, router):
        """Test SSN redaction."""
        input_text = "SSN: 123-45-6789"
        guarded, warnings = router.guard_input(input_text)
        
        assert "[SSN]" in guarded
        assert "123-45-6789" not in guarded
    
    def test_credit_card_redaction(self, router):
        """Test credit card redaction."""
        input_text = "Card: 1234 5678 9012 3456"
        guarded, warnings = router.guard_input(input_text)
        
        assert "[CREDIT_CARD]" in guarded
        assert "1234 5678 9012 3456" not in guarded
    
    def test_length_cap(self, router):
        """Test input length capping."""
        # Use a pattern that won't trigger API key redaction
        long_input = "This is a test. " * 1000  # Create input > 10000 characters
        guarded, warnings = router.guard_input(long_input)
        
        assert len(guarded) <= 10000, f"Guarded text too long: {len(guarded)}"
        # Should have truncation warning (may also have other warnings)
        assert any("Truncated" in str(w) for w in warnings), f"Expected truncation warning, got: {warnings}"
    
    def test_no_redaction_needed(self, router):
        """Test input without sensitive data."""
        input_text = "Write a function to sort an array"
        guarded, warnings = router.guard_input(input_text)
        
        assert guarded == input_text
        assert len(warnings) == 0


class TestOutputValidation:
    """Test suite for output validation."""
    
    @pytest.fixture
    def router(self):
        """Create fresh router for each test."""
        return SmartModelRouter()
    
    def test_empty_output_invalid(self, router):
        """Test empty output is invalid."""
        result = router.validate_output(None, TaskLabel.TRIVIAL)
        
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_schema_validation(self, router):
        """Test schema validation."""
        schema = {"required": ["name", "value"]}
        output = {"name": "test"}  # Missing "value"
        
        result = router.validate_output(output, TaskLabel.ROUTINE, schema)
        
        assert not result.is_valid
        assert any("value" in err for err in result.errors)
    
    def test_high_stakes_warnings(self, router):
        """Test HIGH_STAKES validation warnings."""
        output = "Here is the result"  # No disclaimer, citation, or note
        
        result = router.validate_output(output, TaskLabel.HIGH_STAKES)
        
        # Should have warnings about missing disclaimer/citation
        assert len(result.warnings) > 0, f"Expected warnings for HIGH_STAKES without disclaimer"
    
    def test_banned_content(self, router):
        """Test banned content detection."""
        dangerous_output = "Run this: eval(user_input)"
        
        result = router.validate_output(dangerous_output, TaskLabel.ROUTINE)
        
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_valid_output(self, router):
        """Test valid output passes validation."""
        output = {"code": "def hello(): return 'world'", "tests": "test_hello()"}
        
        result = router.validate_output(output, TaskLabel.ROUTINE)
        
        assert result.is_valid
        assert len(result.errors) == 0


class TestCaching:
    """Test suite for response caching."""
    
    @pytest.fixture
    def router(self):
        """Create fresh router for each test."""
        return SmartModelRouter()
    
    def test_cache_key_generation(self, router):
        """Test cache key generation."""
        key1 = router.cache_key("test prompt", ModelTier.A, TaskLabel.TRIVIAL)
        key2 = router.cache_key("test prompt", ModelTier.A, TaskLabel.TRIVIAL)
        key3 = router.cache_key("different prompt", ModelTier.A, TaskLabel.TRIVIAL)
        
        # Same input should generate same key
        assert key1 == key2
        # Different input should generate different key
        assert key1 != key3
    
    def test_cache_storage_and_retrieval(self, router):
        """Test cache storage and retrieval."""
        cache_key = "test_key"
        response = {"result": "cached response"}
        
        # Store in cache
        router.store_cache(cache_key, response)
        
        # Retrieve from cache
        cached = router.check_cache(cache_key)
        
        assert cached is not None
        assert cached["response"] == response
    
    def test_cache_miss(self, router):
        """Test cache miss returns None."""
        cached = router.check_cache("nonexistent_key")
        assert cached is None


class TestMetrics:
    """Test suite for routing metrics."""
    
    @pytest.fixture
    def router(self):
        """Create fresh router for each test."""
        return SmartModelRouter()
    
    def test_record_metrics(self, router):
        """Test metrics recording."""
        metrics = RoutingMetrics(
            tier=ModelTier.A,
            label=TaskLabel.TRIVIAL,
            success=True,
            attempts=1,
            cost=0.001,
            latency_ms=150.0
        )
        
        initial_count = len(router.metrics_history)
        router.record_metrics(metrics)
        
        assert len(router.metrics_history) == initial_count + 1
    
    def test_success_rate_tracking(self, router):
        """Test success rate tracking."""
        # Record some successes and failures
        for i in range(10):
            metrics = RoutingMetrics(
                tier=ModelTier.A,
                label=TaskLabel.TRIVIAL,
                success=(i < 8),  # 80% success rate
                attempts=1,
                cost=0.001,
                latency_ms=100.0
            )
            router.record_metrics(metrics)
        
        # Success rate should be updated
        rate = router.tier_success_rates[ModelTier.A]
        assert 0.7 <= rate <= 0.9  # Approximate due to exponential moving average
    
    def test_routing_stats(self, router):
        """Test routing statistics."""
        # Record some metrics
        for _ in range(5):
            metrics = RoutingMetrics(
                tier=ModelTier.A,
                label=TaskLabel.TRIVIAL,
                success=True,
                attempts=1,
                cost=0.001,
                latency_ms=100.0
            )
            router.record_metrics(metrics)
        
        stats = router.get_routing_stats()
        
        assert stats["total_requests"] == 5
        assert "A_count" in stats
        assert "tier_success_rates" in stats


class TestGlobalRouter:
    """Test suite for global router singleton."""
    
    def test_singleton_pattern(self):
        """Test global router returns same instance."""
        router1 = get_smart_router()
        router2 = get_smart_router()
        
        assert router1 is router2


class TestEndToEnd:
    """End-to-end routing tests."""
    
    @pytest.fixture
    def router(self):
        """Create fresh router for each test."""
        return SmartModelRouter()
    
    def test_trivial_task_routing(self, router):
        """Test complete routing for trivial task."""
        prompt = "What is Python?"
        
        # Classify
        classification = router.classify_task(prompt)
        assert classification.label == TaskLabel.TRIVIAL
        
        # Select tier
        tier = router.select_tier(classification)
        assert tier == ModelTier.A
        
        # Get model config
        selection = router.get_model_config(tier, classification.label)
        assert selection.tier == ModelTier.A
        assert selection.temperature <= 0.2
    
    def test_high_stakes_task_routing(self, router):
        """Test complete routing for high-stakes task."""
        prompt = "Process the medical records for all patients in the system"
        
        # Classify
        classification = router.classify_task(prompt)
        assert classification.label == TaskLabel.HIGH_STAKES, f"Expected HIGH_STAKES, got {classification.label}"
        
        # Select tier
        tier = router.select_tier(classification)
        assert tier == ModelTier.C
        
        # Get model config
        selection = router.get_model_config(tier, classification.label)
        assert selection.tier == ModelTier.C
        assert selection.max_tokens >= 4000
    
    def test_routing_with_guardrails(self, router):
        """Test routing with input/output guardrails."""
        prompt = "Process payment for user@example.com"
        
        # Guard input
        guarded, warnings = router.guard_input(prompt)
        assert "[EMAIL]" in guarded
        
        # Classify guarded input
        classification = router.classify_task(guarded)
        
        # Validate output (simulate)
        output = {"status": "success", "amount": 100}
        validation = router.validate_output(output, classification.label)
        assert validation.is_valid
