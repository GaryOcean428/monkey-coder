"""
Quantum-Enhanced Advanced Router with 112-dimensional state representation.

This module extends the AdvancedRouter with quantum routing capabilities:
- 112-dimensional state vector analysis
- AdvancedStateEncoder integration
- DQN-compatible routing decisions
- Enhanced complexity assessment using multi-dimensional features
- Backward compatibility with existing routing interfaces
"""

import logging
import numpy as np
from typing import Any, Dict, List, Tuple
from datetime import datetime
from dataclasses import dataclass

from .routing import AdvancedRouter, RoutingDecision, ComplexityLevel, ModelCapabilities
from ..monitoring.quantum_performance import routing_timer, inc_strategy
from ..cache.routing_cache import RoutingDecisionCache
from ..models import ExecuteRequest, PersonaType, ProviderType
from ..quantum.state_encoder import (
    TaskContextProfile,
    ProviderPerformanceHistory,
    UserPreferences,
    ResourceConstraints,
    ContextComplexity,
    create_state_encoder
)
from ..quantum.router_integration import DQNRouterBridge, EnhancedRoutingDecision

logger = logging.getLogger(__name__)


@dataclass
class QuantumRoutingMetrics:
    """Metrics for quantum routing performance analysis."""
    state_vector_dimensions: int
    encoding_time_ms: float
    routing_time_ms: float
    confidence_score: float
    complexity_accuracy: float
    provider_match_score: float
    quantum_coherence: float


class QuantumAdvancedRouter(AdvancedRouter):
    """
    Enhanced AdvancedRouter with 112-dimensional state representation.

    Extends the base AdvancedRouter with:
    - Advanced state encoding (112 dimensions vs basic routing)
    - Multi-dimensional complexity analysis
    - Enhanced provider performance tracking
    - User preference learning
    - Resource constraint awareness
    - Quantum-inspired decision making
    """

    def __init__(self,
                 encoding_strategy: str = "comprehensive",
                 enable_quantum_features: bool = True,
                 fallback_to_basic: bool = True):
        """
        Initialize quantum-enhanced router.

        Args:
            encoding_strategy: State encoding strategy (minimal, basic, standard, comprehensive)
            enable_quantum_features: Enable advanced quantum routing features
            fallback_to_basic: Fallback to basic routing if quantum features fail
        """
        super().__init__()

        self.encoding_strategy = encoding_strategy
        self.enable_quantum_features = enable_quantum_features
        self.fallback_to_basic = fallback_to_basic

        # Initialize quantum routing components
        if self.enable_quantum_features:
            self.state_encoder = create_state_encoder(encoding_strategy)
            self.dqn_bridge = DQNRouterBridge(
                use_advanced_encoding=True,
                encoding_strategy=encoding_strategy,
                collect_training_data=True
            )
        else:
            self.state_encoder = None
            self.dqn_bridge = None

        # Enhanced tracking
        self.quantum_routing_history: List[EnhancedRoutingDecision] = []
        self.performance_metrics: List[QuantumRoutingMetrics] = []
        self.state_vector_cache: Dict[str, np.ndarray] = {}
    logger.info(f"Initialized QuantumAdvancedRouter with {self.encoding_strategy} encoding")
    # Simple in-memory routing decision cache (Phase1)
    self._routing_cache = RoutingDecisionCache()

    def route_request(self, request: ExecuteRequest) -> RoutingDecision:
        """
        Enhanced routing with 112-dimensional state representation.

        Args:
            request: The execution request to route

        Returns:
            RoutingDecision with quantum-enhanced analysis
        """
        start_time = datetime.now()
        # Metrics: time entire routing decision path
        with routing_timer():
            # Attempt cache lookup (best-effort; no cache key if missing fields)
            try:
                complexity_probe = self._analyze_complexity(request)
                complexity_bucket = (
                    "critical" if complexity_probe >= 0.8 else
                    "complex" if complexity_probe >= 0.6 else
                    "moderate" if complexity_probe >= 0.4 else
                    "simple" if complexity_probe >= 0.2 else
                    "trivial"
                )
                if cached := self._routing_cache.get(
                    request.prompt, "unknown", complexity_bucket
                ):
                    return cached
            except Exception:  # pragma: no cover
                pass
            decision = self._route_request_with_metrics(request, start_time)
            try:
                context_type = decision.metadata.get("context_type")
                complexity_level = decision.metadata.get("complexity_level")

                # Validate context_type and complexity_level
                if not isinstance(context_type, str) or not context_type:
                    # Fallback: use a hash of the prompt to reduce collisions
                    import hashlib
                    context_type = f"unknown_{hashlib.md5(request.prompt.encode()).hexdigest()[:8]}"
                if not isinstance(complexity_level, str) or not complexity_level:
                    # Fallback: use a hash of the prompt to reduce collisions
                    import hashlib
                    complexity_level = f"unknown_{hashlib.sha1(request.prompt.encode()).hexdigest()[:8]}"

                self._routing_cache.set(request.prompt, context_type, complexity_level, decision)
            except Exception:  # pragma: no cover
                pass
            return decision

    def _route_request_with_metrics(self, request: ExecuteRequest, start_time: datetime) -> RoutingDecision:
        """Internal helper so context manager exits before fallback handling returns."""

        try:
            if self.enable_quantum_features and self.state_encoder:
                # Use quantum-enhanced routing
                return self._quantum_route_request(request, start_time)
            else:
                # Fallback to basic routing
                logger.info("Using basic routing (quantum features disabled)")
                return super().route_request(request)

        except Exception as e:
            logger.error(f"Quantum routing failed: {e}")

            if self.fallback_to_basic:
                logger.info("Falling back to basic routing")
                return super().route_request(request)
            else:
                raise

    def _quantum_route_request(self, request: ExecuteRequest, start_time: datetime) -> RoutingDecision:
        """Perform quantum-enhanced routing with 112-dimensional analysis."""

        # Phase 1: Generate 112-dimensional state representation
        encoding_start = datetime.now()
        state_vector = self._generate_quantum_state_vector(request)
        encoding_time = (datetime.now() - encoding_start).total_seconds() * 1000

        # Phase 2: Enhanced complexity analysis using state vector
        complexity_analysis = self._analyze_quantum_complexity(state_vector, request)

        # Phase 3: Multi-dimensional context scoring
        context_analysis = self._analyze_quantum_context(state_vector, request)

        # Phase 4: Provider performance-aware selection
        provider_analysis = self._analyze_provider_performance(state_vector, request)

        # Phase 5: Resource constraint optimization
        resource_analysis = self._analyze_resource_constraints(state_vector, request)

        # Phase 6: Quantum-inspired final decision
        routing_decision = self._make_quantum_routing_decision(
            request, state_vector, complexity_analysis, context_analysis,
            provider_analysis, resource_analysis
        )

        # Metrics: record chosen strategy/model signature (provider+model)
        try:
            strategy_label = f"{routing_decision.provider.value}:{routing_decision.model}"
            inc_strategy(strategy_label)
        except Exception:  # pragma: no cover - metrics should not break routing
            pass

        # Phase 7: Enhanced decision with quantum metadata
        enhanced_decision = self._create_enhanced_decision(
            routing_decision, state_vector, request, start_time, encoding_time
        )

        # Store for learning and analysis
        self.quantum_routing_history.append(enhanced_decision)

        # Update performance tracking
        if self.dqn_bridge:
            self.dqn_bridge.update_provider_performance(
                routing_decision.provider,
                {
                    "success_rate": 0.95,  # This would be updated based on actual outcomes
                    "avg_quality": routing_decision.confidence,
                    "avg_latency": (datetime.now() - start_time).total_seconds(),
                    "reputation": routing_decision.capability_score
                }
            )

        logger.info(f"Quantum routing completed: {routing_decision.provider.value}/{routing_decision.model}")
        return routing_decision

    def _generate_quantum_state_vector(self, request: ExecuteRequest) -> np.ndarray:
        """Generate 112-dimensional state vector for the request."""

        # Check cache first
        cache_key = f"{request.prompt[:50]}_{request.task_type.value}"
        if cache_key in self.state_vector_cache:
            return self.state_vector_cache[cache_key]

        # Get basic routing decision for context
        basic_decision = super().route_request(request)

        # Convert to components needed by state encoder
        task_context = self._convert_to_task_context_profile(request, basic_decision)
        provider_history = self._get_provider_performance_history()
        user_preferences = self._extract_user_preferences(request)
        resource_constraints = self._extract_resource_constraints(request)

        # Generate state vector using advanced encoder
        state_vector = self.state_encoder.encode_state(
            task_context=task_context,
            provider_history=provider_history,
            user_preferences=user_preferences,
            resource_constraints=resource_constraints
        )

        # Cache for future use
        self.state_vector_cache[cache_key] = state_vector

        return state_vector

    def _analyze_quantum_complexity(self, state_vector: np.ndarray, request: ExecuteRequest) -> Dict[str, Any]:
        """Enhanced complexity analysis using state vector features."""

        # Extract complexity-related features from state vector
        # The first several dimensions contain complexity information
        task_complexity = float(state_vector[0])  # Overall complexity
        domain_complexity = np.mean(state_vector[1:6])  # Domain-specific complexity
        reasoning_complexity = float(state_vector[6]) if len(state_vector) > 6 else 0.0

        # Combine with traditional analysis
        traditional_complexity = super()._analyze_complexity(request)

        # Weighted combination of quantum and traditional complexity
        quantum_weight = 0.7
        traditional_weight = 0.3

        final_complexity = (
            quantum_weight * task_complexity +
            traditional_weight * traditional_complexity
        )

        # Determine complexity category based on enhanced analysis
        if final_complexity < 0.2:
            complexity_level = ComplexityLevel.TRIVIAL
        elif final_complexity < 0.4:
            complexity_level = ComplexityLevel.SIMPLE
        elif final_complexity < 0.6:
            complexity_level = ComplexityLevel.MODERATE
        elif final_complexity < 0.8:
            complexity_level = ComplexityLevel.COMPLEX
        else:
            complexity_level = ComplexityLevel.CRITICAL

        return {
            "complexity_score": final_complexity,
            "complexity_level": complexity_level,
            "task_complexity": task_complexity,
            "domain_complexity": domain_complexity,
            "reasoning_complexity": reasoning_complexity,
            "traditional_complexity": traditional_complexity,
            "quantum_features_used": True
        }

    def _analyze_quantum_context(self, state_vector: np.ndarray, request: ExecuteRequest) -> Dict[str, Any]:
        """Enhanced context analysis using multi-dimensional features."""

        # Extract context features from state vector
        context_features = state_vector[10:20] if len(state_vector) > 20 else state_vector[7:10]

        # Get traditional context analysis
        traditional_context = super()._extract_context_type(request)
        traditional_score = super()._score_context_match(request, traditional_context)

        # Enhanced context scoring using quantum features
        quantum_context_score = float(np.mean(context_features))

        # Combine scores
        final_context_score = 0.6 * quantum_context_score + 0.4 * traditional_score

        return {
            "context_type": traditional_context,
            "context_score": final_context_score,
            "quantum_context_score": quantum_context_score,
            "traditional_context_score": traditional_score,
            "context_features": context_features.tolist()
        }

    def _analyze_provider_performance(self, state_vector: np.ndarray, request: ExecuteRequest) -> Dict[str, Any]:
        """Analyze provider performance using historical data from state vector."""

        # Extract provider performance features (dimensions vary by encoding strategy)
        perf_start_idx = 30 if len(state_vector) > 50 else 15
        perf_end_idx = perf_start_idx + 20

        provider_features = state_vector[perf_start_idx:perf_end_idx] if len(state_vector) > perf_end_idx else []

        # Get performance data from DQN bridge if available
        performance_data = {}
        if self.dqn_bridge:
            for provider in ProviderType:
                provider_key = provider.value
                if provider_key in self.dqn_bridge.performance_history:
                    perf = self.dqn_bridge.performance_history[provider_key]
                    performance_data[provider] = {
                        "success_rate": perf.get("success_rate", 0.8),
                        "avg_latency": perf.get("avg_latency", 2.0),
                        "avg_quality": perf.get("avg_quality", 0.8),
                        "reputation": perf.get("reputation", 0.8)
                    }

        return {
            "provider_performance_data": performance_data,
            "provider_features": provider_features.tolist() if len(provider_features) > 0 else [],
            "quantum_provider_analysis": len(provider_features) > 0
        }

    def _analyze_resource_constraints(self, state_vector: np.ndarray, request: ExecuteRequest) -> Dict[str, Any]:
        """Analyze resource constraints from state vector and request context."""

        # Extract resource constraint features
        resource_start_idx = 60 if len(state_vector) > 80 else 25
        resource_end_idx = resource_start_idx + 10

        resource_features = state_vector[resource_start_idx:resource_end_idx] if len(state_vector) > resource_end_idx else []

        # Default resource constraints
        default_constraints = {
            "max_latency_seconds": 30.0,
            "min_quality_threshold": 0.8,
            "cost_sensitivity": 0.5,
            "is_premium_user": False,
            "billing_tier": "standard"
        }

        # Extract from request context if available
        request_constraints = {}
        if hasattr(request, 'context') and request.context:
            if hasattr(request.context, 'timeout'):
                request_constraints["max_latency_seconds"] = float(request.context.timeout)
            if hasattr(request.context, 'quality_threshold'):
                request_constraints["min_quality_threshold"] = float(request.context.quality_threshold)
            if hasattr(request.context, 'is_premium_user'):
                request_constraints["is_premium_user"] = bool(request.context.is_premium_user)

        # Combine default and request constraints
        final_constraints = {**default_constraints, **request_constraints}

        return {
            "resource_constraints": final_constraints,
            "resource_features": resource_features.tolist() if len(resource_features) > 0 else [],
            "has_custom_constraints": len(request_constraints) > 0
        }

    def _make_quantum_routing_decision(self,
                                     request: ExecuteRequest,
                                     state_vector: np.ndarray,
                                     complexity_analysis: Dict[str, Any],
                                     context_analysis: Dict[str, Any],
                                     provider_analysis: Dict[str, Any],
                                     resource_analysis: Dict[str, Any]) -> RoutingDecision:
        """Make final routing decision using quantum-enhanced analysis."""

        # Use traditional persona selection (can be enhanced later)
        slash_command = self._parse_slash_commands(request.prompt)
        persona = self._select_persona(request, slash_command, context_analysis["context_type"])

        # Enhanced capability requirements using quantum features
        capability_requirements = self._calculate_enhanced_capability_requirements(
            request, complexity_analysis, context_analysis, persona, state_vector
        )

        # Enhanced model scoring using provider performance data
        model_scores = self._score_models_with_quantum_features(
            capability_requirements, provider_analysis, resource_analysis
        )

        # Select optimal model with quantum-enhanced logic
        provider, model = self._select_optimal_model_quantum(
            model_scores, complexity_analysis, context_analysis, resource_analysis
        )

        # Enhanced confidence calculation
        confidence = self._calculate_quantum_confidence(
            complexity_analysis["complexity_score"],
            context_analysis["context_score"],
            model_scores.get((provider, model), 0.8),
            state_vector
        )

        # Create routing decision with enhanced metadata
        decision = RoutingDecision(
            provider=provider,
            model=model,
            persona=persona,
            complexity_score=complexity_analysis["complexity_score"],
            context_score=context_analysis["context_score"],
            capability_score=model_scores.get((provider, model), 0.8),
            confidence=confidence,
            reasoning=self._generate_quantum_reasoning(
                complexity_analysis, context_analysis, persona, provider, model
            ),
            metadata={
                "timestamp": datetime.utcnow().isoformat(),
                "quantum_routing": True,
                "state_vector_dimensions": len(state_vector),
                "encoding_strategy": self.encoding_strategy,
                "slash_command": slash_command,
                "context_type": context_analysis["context_type"].value,
                "complexity_level": complexity_analysis["complexity_level"].value,
                "quantum_features": {
                    "task_complexity": complexity_analysis["task_complexity"],
                    "domain_complexity": complexity_analysis["domain_complexity"],
                    "reasoning_complexity": complexity_analysis["reasoning_complexity"],
                    "quantum_context_score": context_analysis["quantum_context_score"],
                    "provider_performance_used": len(provider_analysis["provider_performance_data"]) > 0,
                    "resource_constraints_applied": resource_analysis["has_custom_constraints"]
                },
                "model_scores": model_scores,
            }
        )

        return decision

    def _calculate_enhanced_capability_requirements(self,
                                                  request: ExecuteRequest,
                                                  complexity_analysis: Dict[str, Any],
                                                  context_analysis: Dict[str, Any],
                                                  persona: PersonaType,
                                                  state_vector: np.ndarray) -> Dict[str, float]:
        """Calculate capability requirements using quantum features."""

        # Start with traditional requirements
        traditional_requirements = self._calculate_capability_requirements(
            request, complexity_analysis["complexity_level"],
            context_analysis["context_type"], persona
        )

        # Enhanced requirements using quantum features
        task_complexity = complexity_analysis["task_complexity"]
        reasoning_complexity = complexity_analysis["reasoning_complexity"]

        # Adjust requirements based on quantum analysis
        enhanced_requirements = traditional_requirements.copy()

        # Increase reasoning requirement for complex tasks
        if reasoning_complexity > 0.6:
            enhanced_requirements["reasoning"] = min(1.0, enhanced_requirements.get("reasoning", 0.5) + 0.2)

        # Increase code generation requirement for complex domain tasks
        if complexity_analysis["domain_complexity"] > 0.7:
            enhanced_requirements["code_generation"] = min(1.0, enhanced_requirements.get("code_generation", 0.5) + 0.15)

        # Context window requirements based on prompt length and complexity
        prompt_length = len(request.prompt)
        if prompt_length > 1000 or task_complexity > 0.8:
            enhanced_requirements["context_window"] = 100000  # Large context needed
        elif prompt_length > 500 or task_complexity > 0.6:
            enhanced_requirements["context_window"] = 50000   # Medium context needed
        else:
            enhanced_requirements["context_window"] = 8000    # Standard context sufficient

        return enhanced_requirements

    def _score_models_with_quantum_features(self,
                                          capability_requirements: Dict[str, float],
                                          provider_analysis: Dict[str, Any],
                                          resource_analysis: Dict[str, Any]) -> Dict[Tuple[ProviderType, str], float]:
        """Score models using quantum-enhanced analysis."""

        # Start with traditional model scoring
        model_scores = self._score_models(capability_requirements)

        # Enhance scores using provider performance data
        performance_data = provider_analysis.get("provider_performance_data", {})
        resource_constraints = resource_analysis.get("resource_constraints", {})

        for (provider, model), base_score in model_scores.items():
            enhanced_score = base_score

            # Apply provider performance adjustments
            if provider in performance_data:
                perf = performance_data[provider]
                success_rate_bonus = perf["success_rate"] * 0.1  # Up to 10% bonus
                quality_bonus = perf["avg_quality"] * 0.1       # Up to 10% bonus
                latency_penalty = min(perf["avg_latency"] / 10.0, 0.1)  # Up to 10% penalty

                enhanced_score += success_rate_bonus + quality_bonus - latency_penalty

            # Apply resource constraint adjustments
            if resource_constraints.get("is_premium_user", False):
                enhanced_score += 0.05  # 5% bonus for premium users

            max_latency = resource_constraints.get("max_latency_seconds", 30.0)
            if max_latency < 5.0:  # Very tight latency requirements
                if "fast" in self.model_capabilities.get((provider, model), ModelCapabilities(
                    code_generation=0.5, reasoning=0.5, context_window=8000,
                    latency_ms=2000, cost_per_token=0.001, reliability=0.8,
                    specializations=[]
                )).specializations:
                    enhanced_score += 0.15  # Bonus for fast models when speed is critical

            model_scores[(provider, model)] = max(0.0, min(1.0, enhanced_score))

        return model_scores

    def _select_optimal_model_quantum(self,
                                    model_scores: Dict[Tuple[ProviderType, str], float],
                                    complexity_analysis: Dict[str, Any],
                                    context_analysis: Dict[str, Any],
                                    resource_analysis: Dict[str, Any]) -> Tuple[ProviderType, str]:
        """Select optimal model using quantum-enhanced selection logic."""

        if not model_scores:
            return ProviderType.OPENAI, "gpt-4.1-mini"

        # Get resource constraints
        resource_constraints = resource_analysis.get("resource_constraints", {})
        complexity_score = complexity_analysis["complexity_score"]

        # Filter models based on constraints
        filtered_scores = {}
        for (provider, model), score in model_scores.items():
            model_caps = self.model_capabilities.get((provider, model))
            if not model_caps:
                continue

            # Check latency constraints
            max_latency = resource_constraints.get("max_latency_seconds", 30.0) * 1000  # Convert to ms
            if model_caps.latency_ms > max_latency:
                continue

            # Check quality constraints
            min_quality = resource_constraints.get("min_quality_threshold", 0.8)
            estimated_quality = (model_caps.code_generation + model_caps.reasoning) / 2
            if estimated_quality < min_quality:
                continue

            filtered_scores[(provider, model)] = score

        # Fallback to all models if filtering was too restrictive
        if not filtered_scores:
            filtered_scores = model_scores

        # Select best model with quantum-inspired randomness for exploration
        if complexity_score > 0.8:  # For very complex tasks, prefer highest scoring model
            best_model = max(filtered_scores.items(), key=lambda x: x[1])
        else:
            # Add some exploration for moderate complexity tasks
            sorted_models = sorted(filtered_scores.items(), key=lambda x: x[1], reverse=True)
            top_3 = sorted_models[:3]  # Consider top 3 models

            if len(top_3) > 1 and np.random.random() < 0.1:  # 10% chance to explore
                # Select randomly from top models (quantum-inspired exploration)
                best_model = np.random.choice(top_3)
            else:
                best_model = sorted_models[0]

        return best_model[0]

    def _calculate_quantum_confidence(self,
                                    complexity_score: float,
                                    context_score: float,
                                    capability_score: float,
                                    state_vector: np.ndarray) -> float:
        """Calculate confidence using quantum features."""

        # Base confidence from traditional method
        base_confidence = super()._calculate_confidence(complexity_score, context_score, capability_score)

        # Quantum confidence adjustments using state vector coherence
        state_coherence = float(np.std(state_vector))  # Lower std = more coherent state
        coherence_bonus = max(0, (0.5 - state_coherence) * 0.2)  # Up to 20% bonus for coherent states

        # Confidence penalty for very complex tasks
        complexity_penalty = complexity_score * 0.1 if complexity_score > 0.8 else 0

        final_confidence = base_confidence + coherence_bonus - complexity_penalty
        return max(0.1, min(1.0, final_confidence))

    def _generate_quantum_reasoning(self,
                                  complexity_analysis: Dict[str, Any],
                                  context_analysis: Dict[str, Any],
                                  persona: PersonaType,
                                  provider: ProviderType,
                                  model: str) -> str:
        """Generate reasoning for quantum-enhanced routing decision."""

        complexity_level = complexity_analysis["complexity_level"]
        context_type = context_analysis["context_type"]
        quantum_complexity = complexity_analysis["task_complexity"]

        base_reasoning = super()._generate_reasoning(
            complexity_level, context_type, persona, provider, model
        )

        quantum_additions = []

        if quantum_complexity > 0.8:
            quantum_additions.append("high quantum complexity analysis")

        if complexity_analysis.get("reasoning_complexity", 0) > 0.6:
            quantum_additions.append("enhanced reasoning requirements")

        if complexity_analysis.get("domain_complexity", 0) > 0.7:
            quantum_additions.append("domain-specific complexity factors")

        if quantum_additions:
            quantum_reasoning = " Enhanced with: " + ", ".join(quantum_additions) + "."
            return base_reasoning + quantum_reasoning

        return base_reasoning + " (quantum-enhanced analysis)"

    def _create_enhanced_decision(self,
                                routing_decision: RoutingDecision,
                                state_vector: np.ndarray,
                                request: ExecuteRequest,
                                start_time: datetime,
                                encoding_time_ms: float) -> EnhancedRoutingDecision:
        """Create enhanced routing decision with quantum metadata."""

        total_time_ms = (datetime.now() - start_time).total_seconds() * 1000

        enhanced_decision = EnhancedRoutingDecision(
            original_decision=routing_decision,
            state_vector=state_vector,
            state_dimensions=len(state_vector),
            encoding_metadata={
                "encoding_type": "advanced",
                "encoding_strategy": self.encoding_strategy,
                "dimensions": len(state_vector),
                "task_type": request.task_type.value,
                "complexity_category": routing_decision.metadata.get("complexity_level", "moderate"),
                "temporal_features_enabled": self.state_encoder.enable_temporal_features if self.state_encoder else False,
                "personalization_enabled": self.state_encoder.enable_user_personalization if self.state_encoder else False,
                "dynamic_weighting_enabled": self.state_encoder.enable_dynamic_weighting if self.state_encoder else False,
                "encoding_time_ms": encoding_time_ms,
                "total_routing_time_ms": total_time_ms,
                "quantum_features_used": True
            }
        )

        return enhanced_decision

    def _convert_to_task_context_profile(self, request: ExecuteRequest, routing_decision: RoutingDecision) -> TaskContextProfile:
        """Convert request and routing decision to TaskContextProfile."""

        # Map complexity score to ContextComplexity enum
        complexity_score = routing_decision.complexity_score
        if complexity_score < 0.2:
            complexity_category = ContextComplexity.SIMPLE
        elif complexity_score < 0.6:
            complexity_category = ContextComplexity.MODERATE
        else:
            complexity_category = ContextComplexity.COMPLEX

        # Extract domain requirements from prompt
        prompt_lower = request.prompt.lower()
        domain_requirements = []

        if any(word in prompt_lower for word in ['code', 'function', 'class', 'implement']):
            domain_requirements.append("programming")
        if any(word in prompt_lower for word in ['api', 'service', 'endpoint']):
            domain_requirements.append("api_development")
        if any(word in prompt_lower for word in ['database', 'sql', 'query']):
            domain_requirements.append("database")
        if any(word in prompt_lower for word in ['ui', 'interface', 'frontend']):
            domain_requirements.append("frontend")
        if any(word in prompt_lower for word in ['test', 'testing', 'spec']):
            domain_requirements.append("testing")

        if not domain_requirements:
            domain_requirements = ["general"]

        # Determine if task requires reasoning
        reasoning_keywords = ['analyze', 'design', 'architecture', 'algorithm', 'optimize', 'debug']
        requires_reasoning = any(keyword in prompt_lower for keyword in reasoning_keywords)

        return TaskContextProfile(
            task_type=request.task_type,
            estimated_complexity=complexity_score,
            complexity_category=complexity_category,
            domain_requirements=domain_requirements,
            requires_reasoning=requires_reasoning,
            context_length=len(request.prompt),
            estimated_tokens=len(request.prompt.split()) * 4  # Rough token estimate
        )

    def _get_provider_performance_history(self) -> Dict[ProviderType, ProviderPerformanceHistory]:
        """Get provider performance history for state encoding."""

        history = {}

        for provider in ProviderType:
            if self.dqn_bridge and provider.value in self.dqn_bridge.performance_history:
                perf = self.dqn_bridge.performance_history[provider.value]
                history[provider] = ProviderPerformanceHistory(
                    recent_success_rate=perf.get("success_rate", 0.8),
                    recent_avg_latency=perf.get("avg_latency", 2.0),
                    recent_avg_quality=perf.get("avg_quality", 0.8),
                    long_term_reputation=perf.get("reputation", 0.8),
                    total_interactions=perf.get("interactions", 100)
                )
            else:
                # Default performance history
                history[provider] = ProviderPerformanceHistory(
                    recent_success_rate=0.85,
                    recent_avg_latency=2.0,
                    recent_avg_quality=0.80,
                    long_term_reputation=0.85,
                    total_interactions=50
                )

        return history

    def _extract_user_preferences(self, request: ExecuteRequest) -> UserPreferences:
        """Extract user preferences from request."""

        preferences = UserPreferences()

        # Extract preferred providers if available
        if hasattr(request, 'preferred_providers') and request.preferred_providers:
            for provider in request.preferred_providers:
                if provider in preferences.provider_preference_scores:
                    preferences.provider_preference_scores[provider] = 0.9

        # Extract quality vs speed preference from context
        if hasattr(request, 'context') and request.context:
            if hasattr(request.context, 'quality_threshold'):
                quality_threshold = request.context.quality_threshold
                if quality_threshold > 0.9:
                    preferences.quality_vs_speed_preference = 0.9  # Strong quality preference
                elif quality_threshold < 0.7:
                    preferences.quality_vs_speed_preference = 0.3  # Speed preference
                else:
                    preferences.quality_vs_speed_preference = 0.6  # Balanced

        return preferences

    def _extract_resource_constraints(self, request: ExecuteRequest) -> ResourceConstraints:
        """Extract resource constraints from request."""

        constraints = ResourceConstraints()

        if hasattr(request, 'context') and request.context:
            if hasattr(request.context, 'timeout'):
                constraints.max_latency_seconds = float(request.context.timeout)
            if hasattr(request.context, 'quality_threshold'):
                constraints.min_quality_threshold = float(request.context.quality_threshold)
            if hasattr(request.context, 'is_premium_user'):
                constraints.is_premium_user = bool(request.context.is_premium_user)
            if hasattr(request.context, 'billing_tier'):
                constraints.billing_tier = str(request.context.billing_tier)

        return constraints

    def get_quantum_routing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive routing statistics including quantum features."""

        base_stats = {
            "total_quantum_routes": len(self.quantum_routing_history),
            "total_traditional_routes": len(self.routing_history) - len(self.quantum_routing_history),
            "encoding_strategy": self.encoding_strategy,
            "quantum_features_enabled": self.enable_quantum_features,
            "state_vector_dimensions": 112 if self.state_encoder else 0,
        }

        if self.quantum_routing_history:
            # Calculate quantum routing statistics
            complexity_scores = [d.original_decision.complexity_score for d in self.quantum_routing_history]
            confidence_scores = [d.original_decision.confidence for d in self.quantum_routing_history]

            base_stats.update({
                "avg_complexity_score": float(np.mean(complexity_scores)),
                "avg_confidence_score": float(np.mean(confidence_scores)),
                "complexity_std": float(np.std(complexity_scores)),
                "confidence_std": float(np.std(confidence_scores)),
                "quantum_routing_success_rate": 1.0,  # This would be updated based on actual outcomes
            })

        if self.dqn_bridge:
            bridge_stats = self.dqn_bridge.get_routing_statistics()
            base_stats.update({
                "dqn_bridge_stats": bridge_stats
            })

        return base_stats

    def enable_quantum_routing(self, encoding_strategy: str = "comprehensive"):
        """Enable quantum routing features."""
        if not self.enable_quantum_features:
            self.enable_quantum_features = True
            self.encoding_strategy = encoding_strategy
            self.state_encoder = create_state_encoder(encoding_strategy)
            self.dqn_bridge = DQNRouterBridge(
                use_advanced_encoding=True,
                encoding_strategy=encoding_strategy,
                collect_training_data=True
            )
            logger.info(f"Quantum routing enabled with {encoding_strategy} encoding")

    def disable_quantum_routing(self):
        """Disable quantum routing features and fallback to basic routing."""
        self.enable_quantum_features = False
        self.state_encoder = None
        self.dqn_bridge = None
        logger.info("Quantum routing disabled, using basic routing")


# Factory function for creating quantum router instances
def create_quantum_router(encoding_strategy: str = "comprehensive",
                         enable_quantum_features: bool = True,
                         fallback_to_basic: bool = True) -> QuantumAdvancedRouter:
    """
    Factory function to create QuantumAdvancedRouter instances.

    Args:
        encoding_strategy: State encoding strategy (minimal, basic, standard, comprehensive)
        enable_quantum_features: Enable quantum routing features
        fallback_to_basic: Fallback to basic routing on errors

    Returns:
        Configured QuantumAdvancedRouter instance
    """
    return QuantumAdvancedRouter(
        encoding_strategy=encoding_strategy,
        enable_quantum_features=enable_quantum_features,
        fallback_to_basic=fallback_to_basic
    )