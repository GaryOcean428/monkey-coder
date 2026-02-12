"""
TRM-Enhanced Quantum Router

This module extends QuantumAdvancedRouter with TRM-inspired iterative refinement
for adaptive, efficient routing decisions with learned halting.
"""

import logging
import numpy as np
from typing import Any, Dict, Optional, Tuple
from datetime import datetime

from ..core.quantum_routing import QuantumAdvancedRouter, QuantumRoutingMetrics
from ..core.routing import RoutingDecision
from ..models import ExecuteRequest, ProviderType
from .trm_refinement import TRMRefinementModule, TRMConfig, create_trm_module

logger = logging.getLogger(__name__)


class TRMRouter(QuantumAdvancedRouter):
    """
    TRM-enhanced quantum router with iterative refinement and learned halting.
    
    Extends QuantumAdvancedRouter by:
    - Replacing single-step DQN decisions with iterative TRM refinement
    - Adding adaptive computation via learned halting
    - Providing intermediate predictions for A/B testing
    - Enabling dynamic collapse strategies
    """
    
    def __init__(
        self,
        encoding_strategy: str = "comprehensive",
        enable_quantum_features: bool = True,
        fallback_to_basic: bool = True,
        trm_config: Optional[TRMConfig] = None,
        enable_trm: bool = True
    ):
        """
        Initialize TRM-enhanced router.
        
        Args:
            encoding_strategy: State encoding strategy
            enable_quantum_features: Enable quantum routing features
            fallback_to_basic: Fallback to basic routing on errors
            trm_config: Configuration for TRM refinement
            enable_trm: Whether to enable TRM refinement
        """
        super().__init__(
            encoding_strategy=encoding_strategy,
            enable_quantum_features=enable_quantum_features,
            fallback_to_basic=fallback_to_basic
        )
        
        self.enable_trm = enable_trm
        
        if self.enable_trm:
            # Initialize TRM refinement module
            if trm_config is None:
                # Default config matches 112-dim state vector
                trm_config = TRMConfig(
                    latent_dim=112,
                    answer_dim=64,
                    max_inner_steps=5,
                    max_outer_steps=3,
                    halt_threshold=0.8,
                    random_seed=42
                )
            
            self.trm_module = TRMRefinementModule(trm_config)
            logger.info("Initialized TRM-enhanced router")
        else:
            self.trm_module = None
            logger.info("TRM refinement disabled, using standard quantum routing")
        
        # TRM-specific tracking
        self.trm_routing_history: list = []
        self.trm_feedback_buffer: list = []
    
    def _quantum_route_request(
        self,
        request: ExecuteRequest,
        start_time: datetime
    ) -> RoutingDecision:
        """
        Perform quantum-enhanced routing with optional TRM refinement.
        
        Overrides parent method to add TRM refinement loop.
        """
        if not self.enable_trm or self.trm_module is None:
            # Fall back to standard quantum routing
            return super()._quantum_route_request(request, start_time)
        
        # Phase 1: Generate initial 112-dimensional state representation
        encoding_start = datetime.now()
        state_vector = self._generate_quantum_state_vector(request)
        encoding_time = (datetime.now() - encoding_start).total_seconds() * 1000
        
        # Phase 2: TRM iterative refinement
        refinement_start = datetime.now()
        
        # Initialize answer embedding with provider logits
        initial_answer = self._initialize_answer_embedding(request)
        
        # Prepare attention context
        attention_context = self._prepare_attention_context(request, state_vector)
        
        # Perform TRM refinement
        final_state, final_answer, refinement_steps = self.trm_module.refine(
            initial_state=state_vector,
            initial_answer=initial_answer,
            context={'attention_context': attention_context}
        )
        
        refinement_time = (datetime.now() - refinement_start).total_seconds() * 1000
        
        # Phase 3: Extract routing decision from refined state
        routing_decision = self._extract_routing_decision(
            request, final_state, final_answer, refinement_steps
        )
        
        # Phase 4: Enhanced decision with TRM metadata
        enhanced_decision = self._create_trm_enhanced_decision(
            routing_decision, final_state, final_answer,
            refinement_steps, encoding_time, refinement_time
        )
        
        # Store for learning
        self.trm_routing_history.append({
            'request': request,
            'decision': enhanced_decision,
            'refinement_steps': refinement_steps,
            'timestamp': datetime.now()
        })
        
        logger.info(
            f"TRM routing completed in {len(refinement_steps)} steps, "
            f"provider={routing_decision.provider.value}, "
            f"confidence={routing_decision.confidence:.3f}"
        )
        
        return routing_decision
    
    def _initialize_answer_embedding(self, request: ExecuteRequest) -> np.ndarray:
        """
        Initialize answer embedding with provider preference logits.
        
        Args:
            request: Execution request
            
        Returns:
            Initial answer embedding (provider logits)
        """
        # Get available providers
        providers = list(ProviderType)
        num_providers = len(providers)
        
        # Initialize with uniform distribution
        answer_dim = self.trm_module.config.answer_dim
        answer = np.zeros(answer_dim)
        
        # Fill first N positions with provider logits (N = number of providers)
        if answer_dim >= num_providers:
            # Uniform initialization
            answer[:num_providers] = 1.0 / num_providers
            
            # Adjust based on request context if available
            if hasattr(request, 'preferred_providers') and request.preferred_providers:
                for i, provider in enumerate(providers):
                    if provider in request.preferred_providers:
                        answer[i] = 0.5  # Higher initial preference
        
        return answer
    
    def _prepare_attention_context(
        self,
        request: ExecuteRequest,
        state_vector: np.ndarray
    ) -> list:
        """
        Prepare attention context from historical routing decisions.
        
        Args:
            request: Execution request
            state_vector: Current state vector
            
        Returns:
            List of context vectors for attention
        """
        attention_contexts = []
        
        # Add recent successful routing decisions as context
        if self.quantum_routing_history:
            # Get last 5 successful routings
            recent_successes = [
                h for h in self.quantum_routing_history[-10:]
                if h.original_decision.confidence > 0.7
            ][-5:]
            
            for history_item in recent_successes:
                if history_item.state_vector is not None:
                    attention_contexts.append(history_item.state_vector)
        
        # Add current state as self-attention
        attention_contexts.append(state_vector)
        
        return attention_contexts
    
    def _extract_routing_decision(
        self,
        request: ExecuteRequest,
        final_state: np.ndarray,
        final_answer: np.ndarray,
        refinement_steps: list
    ) -> RoutingDecision:
        """
        Extract routing decision from refined TRM state and answer.
        
        Args:
            request: Original request
            final_state: Final latent state from TRM
            final_answer: Final answer embedding from TRM
            refinement_steps: List of refinement steps
            
        Returns:
            RoutingDecision extracted from TRM outputs
        """
        # Enhanced complexity analysis using final state
        complexity_analysis = self._analyze_quantum_complexity(final_state, request)
        
        # Enhanced context analysis
        context_analysis = self._analyze_quantum_context(final_state, request)
        
        # Provider performance analysis
        provider_analysis = self._analyze_provider_performance(final_state, request)
        
        # Resource constraint analysis
        resource_analysis = self._analyze_resource_constraints(final_state, request)
        
        # Extract provider selection from answer embedding
        providers = list(ProviderType)
        num_providers = len(providers)
        
        if len(final_answer) >= num_providers:
            # Use first N positions as provider logits
            provider_logits = final_answer[:num_providers]
            
            # Softmax to get probabilities
            exp_logits = np.exp(provider_logits - np.max(provider_logits))
            provider_probs = exp_logits / np.sum(exp_logits)
            
            # Select provider (with exploration)
            final_confidence = refinement_steps[-1].confidence if refinement_steps else 0.5
            
            if final_confidence > 0.8:
                # High confidence: select best provider
                selected_provider_idx = np.argmax(provider_probs)
            else:
                # Lower confidence: sample from distribution
                selected_provider_idx = np.random.choice(
                    len(providers),
                    p=provider_probs
                )
            
            provider = providers[selected_provider_idx]
        else:
            # Fallback to default provider selection
            provider = ProviderType.OPENAI
        
        # Make final routing decision using parent class logic
        # but with TRM-refined state
        model_scores = self._score_models_with_quantum_features(
            self._calculate_enhanced_capability_requirements(
                request, complexity_analysis, context_analysis,
                self._select_persona(
                    request,
                    self._parse_slash_commands(request.prompt),
                    context_analysis["context_type"]
                ),
                final_state
            ),
            provider_analysis,
            resource_analysis
        )
        
        # Filter to selected provider's models
        provider_models = {
            (p, m): score for (p, m), score in model_scores.items()
            if p == provider
        }
        
        if provider_models:
            # Select best model for chosen provider
            (_, model), score = max(provider_models.items(), key=lambda x: x[1])
        else:
            # Fallback
            model = "gpt-4.1-mini" if provider == ProviderType.OPENAI else "claude-sonnet-4-5"
            score = 0.8
        
        # Calculate final confidence from TRM
        if refinement_steps:
            final_step = refinement_steps[-1]
            confidence = final_step.confidence
            halt_prob = final_step.halt_probability
        else:
            confidence = 0.5
            halt_prob = 0.0
        
        # Create routing decision
        decision = RoutingDecision(
            provider=provider,
            model=model,
            persona=self._select_persona(
                request,
                self._parse_slash_commands(request.prompt),
                context_analysis["context_type"]
            ),
            complexity_score=complexity_analysis["complexity_score"],
            context_score=context_analysis["context_score"],
            capability_score=score,
            confidence=confidence,
            reasoning=self._generate_trm_reasoning(
                complexity_analysis, context_analysis, provider, model,
                refinement_steps
            ),
            metadata={
                "timestamp": datetime.utcnow().isoformat(),
                "trm_routing": True,
                "trm_steps": len(refinement_steps),
                "trm_halt_probability": halt_prob,
                "trm_final_confidence": confidence,
                "state_vector_dimensions": len(final_state),
                "encoding_strategy": self.encoding_strategy,
                "slash_command": self._parse_slash_commands(request.prompt),
                "context_type": context_analysis["context_type"].value,
                "complexity_level": complexity_analysis["complexity_level"].value,
                "refinement_cycles": {
                    "inner": sum(1 for s in refinement_steps if s.cycle_type == 'inner'),
                    "outer": sum(1 for s in refinement_steps if s.cycle_type == 'outer')
                }
            }
        )
        
        return decision
    
    def _generate_trm_reasoning(
        self,
        complexity_analysis: Dict[str, Any],
        context_analysis: Dict[str, Any],
        provider: ProviderType,
        model: str,
        refinement_steps: list
    ) -> str:
        """Generate reasoning for TRM-enhanced routing decision."""
        base_reasoning = self._generate_quantum_reasoning(
            complexity_analysis,
            context_analysis,
            self._select_persona(
                None,
                None,
                context_analysis["context_type"]
            ),
            provider,
            model
        )
        
        # Add TRM-specific reasoning
        num_steps = len(refinement_steps)
        final_confidence = refinement_steps[-1].confidence if refinement_steps else 0.5
        
        if num_steps < 3:
            efficiency_note = "High efficiency with early halting"
        elif num_steps < 6:
            efficiency_note = "Balanced refinement process"
        else:
            efficiency_note = "Deep refinement for complex case"
        
        trm_reasoning = (
            f" TRM refinement: {num_steps} steps, "
            f"confidence={final_confidence:.2f}. {efficiency_note}."
        )
        
        return base_reasoning + trm_reasoning
    
    def _create_trm_enhanced_decision(
        self,
        routing_decision: RoutingDecision,
        final_state: np.ndarray,
        final_answer: np.ndarray,
        refinement_steps: list,
        encoding_time_ms: float,
        refinement_time_ms: float
    ) -> RoutingDecision:
        """Create enhanced routing decision with TRM metadata."""
        # Add TRM-specific metrics to metadata
        routing_decision.metadata.update({
            "trm_metrics": {
                "encoding_time_ms": encoding_time_ms,
                "refinement_time_ms": refinement_time_ms,
                "total_time_ms": encoding_time_ms + refinement_time_ms,
                "final_state_norm": float(np.linalg.norm(final_state)),
                "final_answer_norm": float(np.linalg.norm(final_answer)),
                "halt_efficiency": refinement_steps[-1].halt_probability if refinement_steps else 0.0
            }
        })
        
        return routing_decision
    
    def learn_from_outcome(
        self,
        request: ExecuteRequest,
        decision: RoutingDecision,
        actual_quality: float,
        actual_latency: float
    ):
        """
        Learn from routing outcome to improve TRM refinement.
        
        Args:
            request: Original request
            decision: Routing decision made
            actual_quality: Actual quality achieved (0-1)
            actual_latency: Actual latency in seconds
        """
        if not self.enable_trm or self.trm_module is None:
            return
        
        # Find corresponding TRM history entry
        for history_item in reversed(self.trm_routing_history):
            if history_item['decision'].metadata.get('timestamp') == decision.metadata.get('timestamp'):
                refinement_steps = history_item['refinement_steps']
                
                # Compute target outcome (weighted quality and latency)
                target_outcome = 0.7 * actual_quality + 0.3 * (1.0 - min(actual_latency / 10.0, 1.0))
                
                # Compute actual outcome from decision confidence
                actual_outcome = decision.confidence
                
                # Apply feedback to TRM
                self.trm_module.learn_from_feedback(
                    refinement_steps,
                    actual_outcome,
                    target_outcome
                )
                
                logger.debug(
                    f"Applied TRM feedback: quality={actual_quality:.2f}, "
                    f"latency={actual_latency:.2f}s, target={target_outcome:.2f}"
                )
                break
    
    def get_trm_statistics(self) -> Dict[str, Any]:
        """Get TRM-specific routing statistics."""
        base_stats = self.get_quantum_routing_statistics()
        
        if not self.enable_trm or self.trm_module is None:
            return base_stats
        
        # Add TRM metrics
        trm_metrics = self.trm_module.get_metrics()
        
        base_stats.update({
            "trm_enabled": True,
            "trm_metrics": trm_metrics,
            "trm_total_routings": len(self.trm_routing_history),
            "trm_avg_steps": trm_metrics.get("avg_steps_to_halt", 0.0),
            "trm_halt_accuracy": trm_metrics.get("halt_accuracy", 0.0)
        })
        
        return base_stats
    
    def enable_trm_routing(self, config: Optional[TRMConfig] = None):
        """Enable TRM refinement routing."""
        self.enable_trm = True
        
        if self.trm_module is None:
            if config is None:
                config = TRMConfig(latent_dim=112, random_seed=42)
            self.trm_module = TRMRefinementModule(config)
        
        logger.info("TRM routing enabled")
    
    def disable_trm_routing(self):
        """Disable TRM refinement and use standard quantum routing."""
        self.enable_trm = False
        logger.info("TRM routing disabled")


def create_trm_router(
    encoding_strategy: str = "comprehensive",
    max_inner_steps: int = 5,
    max_outer_steps: int = 3,
    halt_threshold: float = 0.8,
    random_seed: Optional[int] = 42
) -> TRMRouter:
    """
    Factory function to create TRM-enhanced router.
    
    Args:
        encoding_strategy: State encoding strategy
        max_inner_steps: Maximum inner refinement cycles
        max_outer_steps: Maximum outer answer updates
        halt_threshold: Confidence threshold for halting
        random_seed: Random seed for reproducibility
        
    Returns:
        Configured TRMRouter
    """
    trm_config = TRMConfig(
        latent_dim=112,
        answer_dim=64,
        max_inner_steps=max_inner_steps,
        max_outer_steps=max_outer_steps,
        halt_threshold=halt_threshold,
        random_seed=random_seed
    )
    
    return TRMRouter(
        encoding_strategy=encoding_strategy,
        enable_quantum_features=True,
        fallback_to_basic=True,
        trm_config=trm_config,
        enable_trm=True
    )
