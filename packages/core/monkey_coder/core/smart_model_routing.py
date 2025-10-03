"""
Smart Model Routing - Right-sized AI Model Selection

This module implements intelligent task classification and tiered model routing
to optimize for speed, cost, and reliability. Based on the principle of using
the right-sized AI model for the job.

Key Features:
- Task classification (TRIVIAL, ROUTINE, HARD, HIGH_STAKES)
- Tiered model selection (A=mini, B=pro-mid, C=frontier)
- Automatic escalation with fallback chains
- Input/output validation and guardrails
- Response caching and learning
- Cost-benefit optimization

Reference: Smart Model Routing Playbook
"""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)


class TaskLabel(str, Enum):
    """Task classification labels for routing decisions."""
    TRIVIAL = "TRIVIAL"      # Keyword lookup, extraction, classification, short paraphrase
    ROUTINE = "ROUTINE"      # Multi-step rewrite, basic code fix, structured generation
    HARD = "HARD"           # Reasoning, multi-hop research, complex coding
    HIGH_STAKES = "HIGH_STAKES"  # Legal/medical/financial, PII handling, irreversible actions


class ModelTier(str, Enum):
    """Model tiers by cost and capability."""
    A = "A"  # Cheap/fast: small/mini models for trivial + routine
    B = "B"  # Mid: strong mid-size for reasoning + light tool use
    C = "C"  # Premium: frontier models for hard/high-stakes


@dataclass
class TaskClassification:
    """Result of task classification."""
    label: TaskLabel
    confidence: float
    reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelSelection:
    """Selected model and tier for task execution."""
    tier: ModelTier
    provider: str
    model: str
    temperature: float
    max_tokens: int
    json_mode: bool
    reasoning: str
    estimated_cost: float


@dataclass
class ValidationResult:
    """Result of output validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RoutingMetrics:
    """Metrics for routing performance tracking."""
    tier: ModelTier
    label: TaskLabel
    success: bool
    attempts: int
    cost: float
    latency_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


class SmartModelRouter:
    """
    Smart model routing with task classification and tiered selection.
    
    Implements cost-benefit optimization with automatic escalation and
    fallback chains for reliability.
    """
    
    def __init__(self):
        self.response_cache: Dict[str, Any] = {}
        self.metrics_history: List[RoutingMetrics] = []
        self.tier_success_rates: Dict[ModelTier, float] = {
            ModelTier.A: 1.0,
            ModelTier.B: 1.0,
            ModelTier.C: 1.0
        }
        
        # Tier to model mapping (configurable)
        self.tier_models = {
            ModelTier.A: [
                ("openai", "gpt-4.1-mini"),
                ("anthropic", "claude-haiku-4-20250730"),
                ("google", "gemini-2.5-flash")
            ],
            ModelTier.B: [
                ("openai", "gpt-4.1"),
                ("anthropic", "claude-sonnet-4-20250514"),
                ("google", "gemini-2.5-pro")
            ],
            ModelTier.C: [
                ("openai", "o1"),
                ("anthropic", "claude-opus-4-1-20250805"),
                ("anthropic", "claude-4.5-sonnet-20250930")
            ]
        }
        
        logger.info("SmartModelRouter initialized with tiered model selection")
    
    def classify_task(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> TaskClassification:
        """
        Classify task into TRIVIAL, ROUTINE, HARD, or HIGH_STAKES.
        
        Args:
            prompt: Task prompt/description
            context: Additional context for classification
            
        Returns:
            TaskClassification with label and confidence
        """
        prompt_lower = prompt.lower()
        context = context or {}
        
        # HIGH_STAKES detection (highest priority)
        high_stakes_indicators = [
            r'(legal|medical|financial|payment|pii|personal\s+data|ssn|credit\s+card)',
            r'(delete|remove|drop|truncate)\s+(database|table|user|account)',
            r'(production|live|prod)\s+(deploy|release|update)',
            r'(irreversible|permanent|critical)'
        ]
        
        for pattern in high_stakes_indicators:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                return TaskClassification(
                    label=TaskLabel.HIGH_STAKES,
                    confidence=0.95,
                    reasoning="Detected high-stakes indicators: sensitive data or irreversible actions",
                    metadata={"pattern": pattern}
                )
        
        # HARD task detection
        hard_indicators = [
            r'(architect|design|optimize|complex|algorithm|reasoning|multi-hop)',
            r'(refactor|restructure|migrate|scale)',
            r'(security|vulnerability|threat|exploit)',
            r'(performance|optimization|bottleneck)'
        ]
        
        hard_matches = sum(1 for pattern in hard_indicators if re.search(pattern, prompt_lower, re.IGNORECASE))
        if hard_matches >= 1 or len(prompt.split()) > 100:
            return TaskClassification(
                label=TaskLabel.HARD,
                confidence=0.8,
                reasoning=f"Complex task detected with {hard_matches} complexity indicators",
                metadata={"matches": hard_matches, "length": len(prompt.split())}
            )
        
        # ROUTINE task detection
        routine_indicators = [
            r'(fix|debug|update|modify|change|add|remove)',
            r'(implement|create|write|generate)\s+(function|class|method|component)',
            r'(test|validate|check|verify)',
            r'(format|lint|style|cleanup)'
        ]
        
        routine_matches = sum(1 for pattern in routine_indicators if re.search(pattern, prompt_lower, re.IGNORECASE))
        if routine_matches >= 1 and len(prompt.split()) > 5:
            return TaskClassification(
                label=TaskLabel.ROUTINE,
                confidence=0.85,
                reasoning=f"Routine development task with {routine_matches} indicators",
                metadata={"matches": routine_matches}
            )
        
        # TRIVIAL by default (short, simple tasks)
        return TaskClassification(
            label=TaskLabel.TRIVIAL,
            confidence=0.9,
            reasoning="Simple, short task suitable for lightweight model",
            metadata={"length": len(prompt.split())}
        )
    
    def select_tier(
        self,
        classification: TaskClassification,
        context: Optional[Dict[str, Any]] = None
    ) -> ModelTier:
        """
        Select appropriate model tier based on classification.
        
        Policy:
        - HIGH_STAKES -> C (always use frontier models)
        - HARD with low confidence -> B (escalate if validator fails)
        - HARD with high confidence -> B
        - TRIVIAL or ROUTINE -> A (escalate only if validator fails twice)
        
        Args:
            classification: Task classification result
            context: Additional context for tier selection
            
        Returns:
            Selected model tier
        """
        label = classification.label
        confidence = classification.confidence
        
        # HIGH_STAKES always uses premium tier
        if label == TaskLabel.HIGH_STAKES:
            logger.info("HIGH_STAKES task detected, using Tier C (frontier)")
            return ModelTier.C
        
        # HARD tasks use mid or premium tier based on confidence
        if label == TaskLabel.HARD:
            if confidence < 0.7:
                logger.info("HARD task with low confidence, starting with Tier B (will escalate on failure)")
                return ModelTier.B
            else:
                logger.info("HARD task with high confidence, using Tier B")
                return ModelTier.B
        
        # TRIVIAL and ROUTINE use cheap tier
        logger.info(f"{label.value} task detected, using Tier A (cheap/fast)")
        return ModelTier.A
    
    def get_model_config(
        self,
        tier: ModelTier,
        label: TaskLabel,
        provider_preference: Optional[str] = None
    ) -> ModelSelection:
        """
        Get model configuration for tier and task label.
        
        Args:
            tier: Model tier to use
            label: Task label for knob configuration
            provider_preference: Preferred provider (if available)
            
        Returns:
            ModelSelection with provider, model, and parameters
        """
        # Select provider and model from tier
        available_models = self.tier_models[tier]
        
        # Prefer specified provider if available
        if provider_preference:
            for provider, model in available_models:
                if provider == provider_preference:
                    selected_provider = provider
                    selected_model = model
                    break
            else:
                # Provider not available in tier, use first option
                selected_provider, selected_model = available_models[0]
        else:
            # Use first available option (can be enhanced with load balancing)
            selected_provider, selected_model = available_models[0]
        
        # Configure knobs based on task label
        if label in [TaskLabel.TRIVIAL, TaskLabel.ROUTINE]:
            # Low temperature, tight tokens, JSON mode for structured output
            temperature = 0.1
            max_tokens = 1000 if label == TaskLabel.TRIVIAL else 2000
            json_mode = True
        elif label == TaskLabel.HARD:
            # Moderate temperature, more tokens, chain-of-thought
            temperature = 0.3
            max_tokens = 4000
            json_mode = False
        else:  # HIGH_STAKES
            # Strict settings, longer output, citations required
            temperature = 0.2
            max_tokens = 8000
            json_mode = True
        
        # Estimate cost (simplified)
        cost_per_1k_tokens = {
            ModelTier.A: 0.0001,
            ModelTier.B: 0.001,
            ModelTier.C: 0.01
        }
        estimated_cost = (max_tokens / 1000) * cost_per_1k_tokens[tier]
        
        return ModelSelection(
            tier=tier,
            provider=selected_provider,
            model=selected_model,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=json_mode,
            reasoning=f"Tier {tier.value} model for {label.value} task",
            estimated_cost=estimated_cost
        )
    
    def guard_input(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, List[str]]:
        """
        Apply input guardrails before model invocation.
        
        - Redact secrets/PII
        - Apply length caps
        - Schema validation
        
        Args:
            input_text: Raw input text
            context: Additional context
            
        Returns:
            Tuple of (guarded_text, warnings)
        """
        warnings = []
        guarded_text = input_text
        
        # Redact potential secrets
        secret_patterns = [
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),  # Email
            (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),  # SSN
            (r'\b(?:\d{4}[-\s]?){3}\d{4}\b', '[CREDIT_CARD]'),  # Credit card
            (r'\b[A-Za-z0-9]{20,}\b', '[API_KEY]')  # API keys (long alphanumeric)
        ]
        
        for pattern, replacement in secret_patterns:
            matches = re.findall(pattern, guarded_text)
            if matches:
                guarded_text = re.sub(pattern, replacement, guarded_text)
                warnings.append(f"Redacted {len(matches)} potential secrets")
        
        # Apply length cap (configurable)
        max_length = 10000  # characters
        if len(guarded_text) > max_length:
            original_length = len(guarded_text)
            guarded_text = guarded_text[:max_length]
            warnings.append(f"Truncated input from {original_length} to {max_length} characters")
        
        if warnings:
            logger.warning(f"Input guardrails applied: {warnings}")
        
        return guarded_text, warnings
    
    def validate_output(
        self,
        output: Any,
        label: TaskLabel,
        expected_schema: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate model output before returning to user.
        
        - Schema validation
        - Content checks (banned words, required fields)
        - Domain-specific validation
        
        Args:
            output: Model output to validate
            label: Task label for validation rules
            expected_schema: Optional JSON schema for validation
            
        Returns:
            ValidationResult with validity and errors
        """
        errors = []
        warnings = []
        
        # Basic validation: output must exist
        if output is None or (isinstance(output, str) and len(output.strip()) == 0):
            errors.append("Empty output from model")
            return ValidationResult(is_valid=False, errors=errors)
        
        # Schema validation (if provided)
        if expected_schema:
            # Simplified schema check (can be enhanced with jsonschema library)
            if isinstance(output, dict):
                required_fields = expected_schema.get("required", [])
                for field in required_fields:
                    if field not in output:
                        errors.append(f"Missing required field: {field}")
        
        # Content checks for HIGH_STAKES
        if label == TaskLabel.HIGH_STAKES:
            # Check for disclaimer/citation
            if isinstance(output, str):
                if "disclaimer" not in output.lower() and "citation" not in output.lower() and "note" not in output.lower():
                    warnings.append("HIGH_STAKES task output should include disclaimer or citation")
        
        # Banned content check (simplified)
        banned_patterns = [
            r'(execute|run|eval)\s*\(',  # Dangerous code execution
            r'rm\s+-rf',  # Dangerous system commands
        ]
        
        output_str = str(output)
        for pattern in banned_patterns:
            if re.search(pattern, output_str, re.IGNORECASE):
                errors.append(f"Output contains banned pattern: {pattern}")
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            logger.warning(f"Output validation failed: {errors}")
        elif warnings:
            logger.info(f"Output validation warnings: {warnings}")
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
    
    def cache_key(
        self,
        input_text: str,
        tier: ModelTier,
        label: TaskLabel,
        policy: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate cache key for response caching.
        
        Args:
            input_text: Input prompt
            tier: Model tier
            label: Task label
            policy: Additional policy parameters
            
        Returns:
            Cache key string
        """
        cache_data = f"{input_text}|{tier.value}|{label.value}|{policy or {}}"
        return hashlib.sha256(cache_data.encode()).hexdigest()
    
    def check_cache(self, cache_key: str) -> Optional[Any]:
        """Check if response is cached."""
        return self.response_cache.get(cache_key)
    
    def store_cache(
        self,
        cache_key: str,
        response: Any,
        ttl_hours: int = 24
    ):
        """Store response in cache with TTL."""
        self.response_cache[cache_key] = {
            "response": response,
            "cached_at": datetime.utcnow(),
            "ttl_hours": ttl_hours
        }
    
    def record_metrics(self, metrics: RoutingMetrics):
        """Record routing metrics for learning."""
        self.metrics_history.append(metrics)
        
        # Update tier success rates (exponential moving average)
        alpha = 0.1
        current_rate = self.tier_success_rates[metrics.tier]
        new_observation = 1.0 if metrics.success else 0.0
        self.tier_success_rates[metrics.tier] = (
            alpha * new_observation + (1 - alpha) * current_rate
        )
        
        logger.debug(
            f"Recorded metrics: tier={metrics.tier.value}, "
            f"success={metrics.success}, cost=${metrics.cost:.4f}"
        )
    
    def get_success_rate(self, tier: ModelTier, window_hours: int = 24) -> float:
        """Get recent success rate for a tier."""
        cutoff = datetime.utcnow() - timedelta(hours=window_hours)
        recent_metrics = [
            m for m in self.metrics_history
            if m.tier == tier and m.timestamp > cutoff
        ]
        
        if not recent_metrics:
            return self.tier_success_rates[tier]
        
        successes = sum(1 for m in recent_metrics if m.success)
        return successes / len(recent_metrics)
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics for monitoring."""
        stats = {
            "total_requests": len(self.metrics_history),
            "cache_size": len(self.response_cache),
            "tier_success_rates": {
                tier.value: rate
                for tier, rate in self.tier_success_rates.items()
            }
        }
        
        # Calculate metrics by tier
        for tier in ModelTier:
            tier_metrics = [m for m in self.metrics_history if m.tier == tier]
            if tier_metrics:
                stats[f"{tier.value}_count"] = len(tier_metrics)
                stats[f"{tier.value}_avg_cost"] = sum(m.cost for m in tier_metrics) / len(tier_metrics)
                stats[f"{tier.value}_avg_latency"] = sum(m.latency_ms for m in tier_metrics) / len(tier_metrics)
        
        return stats


# Global router instance (singleton)
_global_router: Optional[SmartModelRouter] = None


def get_smart_router() -> SmartModelRouter:
    """Get or create the global smart router instance."""
    global _global_router
    if _global_router is None:
        _global_router = SmartModelRouter()
    return _global_router
