"""
DQN Router Integration with Existing AdvancedRouter

This module bridges the existing Gary8D-inspired AdvancedRouter with the new 
AdvancedStateEncoder for quantum routing capabilities. It maintains backward 
compatibility while adding sophisticated state encoding for DQN training.
"""

import logging
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass

from ..core.routing import AdvancedRouter, RoutingDecision, ComplexityLevel, ContextType
from ..models import ExecuteRequest, ProviderType, TaskType
from .state_encoder import (
    AdvancedStateEncoder,
    TaskContextProfile,
    ProviderPerformanceHistory,
    UserPreferences,
    ResourceConstraints,
    ContextComplexity,
    create_state_encoder
)
from .dqn_agent import DQNRoutingAgent, RoutingState, RoutingAction

logger = logging.getLogger(__name__)


@dataclass
class EnhancedRoutingDecision:
    """Extended routing decision with DQN state information."""
    
    original_decision: RoutingDecision
    state_vector: Any  # np.ndarray
    state_dimensions: int
    encoding_metadata: Dict[str, Any]


class DQNRouterBridge:
    """
    Bridge between AdvancedRouter and DQN routing capabilities.
    
    This class enhances the existing router with:
    - 112-dimensional state encoding
    - DQN-compatible state representation
    - Training data collection
    - Backward compatibility
    """
    
    def __init__(
        self,
        use_advanced_encoding: bool = True,
        encoding_strategy: str = "comprehensive",
        collect_training_data: bool = False
    ):
        """
        Initialize the DQN router bridge.
        
        Args:
            use_advanced_encoding: Whether to use 112-dimensional encoding
            encoding_strategy: Strategy for state encoder ("minimal", "standard", "comprehensive")
            collect_training_data: Whether to collect data for DQN training
        """
        self.use_advanced_encoding = use_advanced_encoding
        self.collect_training_data = collect_training_data
        
        # Initialize existing router
        self.advanced_router = AdvancedRouter()
        
        # Initialize state encoder if using advanced encoding
        if use_advanced_encoding:
            self.state_encoder = create_state_encoder(encoding_strategy)
            logger.info(f"Initialized DQN router bridge with {encoding_strategy} encoding")
        else:
            self.state_encoder = None
            logger.info("Initialized DQN router bridge with basic encoding")
        
        # Training data collection
        self.training_data = []
        self.performance_history = {}  # Provider performance tracking
        
    def route_request(self, request: ExecuteRequest) -> EnhancedRoutingDecision:
        """
        Route request with enhanced state encoding capabilities.
        
        Args:
            request: The execution request to route
            
        Returns:
            Enhanced routing decision with state information
        """
        # Get traditional routing decision first
        original_decision = self.advanced_router.route_request(request)
        
        if not self.use_advanced_encoding:
            # Fallback to basic state representation
            state_vector = self._create_basic_state_vector(request, original_decision)
            return EnhancedRoutingDecision(
                original_decision=original_decision,
                state_vector=state_vector,
                state_dimensions=len(state_vector),
                encoding_metadata={"encoding_type": "basic"}
            )
        
        # Create advanced state representation
        state_vector, encoding_metadata = self._create_advanced_state_vector(
            request, original_decision
        )
        
        # Collect training data if enabled
        if self.collect_training_data:
            self._collect_training_sample(
                request, original_decision, state_vector, encoding_metadata
            )
        
        return EnhancedRoutingDecision(
            original_decision=original_decision,
            state_vector=state_vector,
            state_dimensions=self.state_encoder.state_size,
            encoding_metadata=encoding_metadata
        )
    
    def _create_advanced_state_vector(
        self, 
        request: ExecuteRequest, 
        decision: RoutingDecision
    ) -> Tuple[Any, Dict[str, Any]]:
        """Create advanced 112-dimensional state vector."""
        
        # Convert AdvancedRouter analysis to AdvancedStateEncoder format
        task_context = self._convert_to_task_context_profile(request, decision)
        provider_history = self._get_provider_performance_history()
        user_preferences = self._extract_user_preferences(request)
        resource_constraints = self._extract_resource_constraints(request)
        provider_availability = self._get_provider_availability()
        
        # Generate state vector using advanced encoder
        state_vector = self.state_encoder.encode_state(
            task_context=task_context,
            provider_history=provider_history,
            user_preferences=user_preferences,
            resource_constraints=resource_constraints,
            provider_availability=provider_availability
        )
        
        encoding_metadata = {
            "encoding_type": "advanced",
            "dimensions": self.state_encoder.state_size,
            "complexity_category": task_context.complexity_category.value,
            "task_type": task_context.task_type.value,
            "temporal_features_enabled": self.state_encoder.enable_temporal_features,
            "personalization_enabled": self.state_encoder.enable_user_personalization,
            "dynamic_weighting_enabled": self.state_encoder.enable_dynamic_weighting
        }
        
        return state_vector, encoding_metadata
    
    def _create_basic_state_vector(
        self, 
        request: ExecuteRequest, 
        decision: RoutingDecision
    ) -> Any:
        """Create basic state vector compatible with original DQN implementation."""
        # Create basic RoutingState for backward compatibility
        routing_state = RoutingState(
            task_complexity=decision.complexity_score,
            context_type=self._map_context_to_string(request),
            provider_availability=self._get_basic_provider_availability(),
            historical_performance=self._get_basic_historical_performance(),
            resource_constraints={
                "cost_weight": 0.33,
                "time_weight": 0.33,
                "quality_weight": 0.34
            },
            user_preferences={"preference_strength": 0.5}
        )
        
        return routing_state.to_vector()
    
    def _convert_to_task_context_profile(
        self, 
        request: ExecuteRequest, 
        decision: RoutingDecision
    ) -> TaskContextProfile:
        """Convert ExecuteRequest and RoutingDecision to TaskContextProfile."""
        
        # Map complexity level to category
        complexity_mapping = {
            ComplexityLevel.TRIVIAL: ContextComplexity.SIMPLE,
            ComplexityLevel.SIMPLE: ContextComplexity.SIMPLE,
            ComplexityLevel.MODERATE: ContextComplexity.MODERATE,
            ComplexityLevel.COMPLEX: ContextComplexity.COMPLEX,
            ComplexityLevel.CRITICAL: ContextComplexity.CRITICAL
        }
        
        # Extract complexity level from metadata or classify from score
        complexity_level = decision.metadata.get("complexity_level")
        if isinstance(complexity_level, str):
            complexity_level = ComplexityLevel(complexity_level)
        else:
            # Fallback: classify from score
            if decision.complexity_score >= 0.8:
                complexity_level = ComplexityLevel.CRITICAL
            elif decision.complexity_score >= 0.6:
                complexity_level = ComplexityLevel.COMPLEX
            elif decision.complexity_score >= 0.4:
                complexity_level = ComplexityLevel.MODERATE
            elif decision.complexity_score >= 0.2:
                complexity_level = ComplexityLevel.SIMPLE
            else:
                complexity_level = ComplexityLevel.TRIVIAL
        
        complexity_category = complexity_mapping[complexity_level]
        
        # Extract domain requirements from prompt analysis
        domain_requirements = self.state_encoder._extract_domain_requirements(
            request.prompt, request.task_type
        )
        
        # Determine context flags
        is_production = getattr(request.context, 'is_production', False)
        requires_reasoning = self.state_encoder._requires_reasoning(
            request.prompt, request.task_type
        )
        requires_creativity = self.state_encoder._requires_creativity(
            request.prompt, request.task_type
        )
        
        return TaskContextProfile(
            task_type=request.task_type,
            estimated_complexity=decision.complexity_score,
            complexity_category=complexity_category,
            domain_requirements=domain_requirements,
            quality_threshold=0.8,  # Could be extracted from request context
            latency_requirement=getattr(request.context, 'timeout', 30.0),
            cost_sensitivity=0.5,   # Could be user-configurable
            is_production=is_production,
            requires_reasoning=requires_reasoning,
            requires_creativity=requires_creativity
        )
    
    def _get_provider_performance_history(self) -> Dict[ProviderType, ProviderPerformanceHistory]:
        """Get provider performance history for all providers."""
        history = {}
        
        for provider in ProviderType:
            if provider.value in self.performance_history:
                # Use tracked performance data
                perf_data = self.performance_history[provider.value]
                history[provider] = ProviderPerformanceHistory(
                    recent_success_rate=perf_data.get("success_rate", 0.85),
                    recent_avg_latency=perf_data.get("avg_latency", 2.0),
                    recent_avg_quality=perf_data.get("avg_quality", 0.8),
                    long_term_reputation=perf_data.get("reputation", 0.85),
                    total_interactions=perf_data.get("interactions", 100)
                )
            else:
                # Use default performance metrics
                history[provider] = ProviderPerformanceHistory()
        
        return history
    
    def _extract_user_preferences(self, request: ExecuteRequest) -> UserPreferences:
        """Extract user preferences from request."""
        preferences = UserPreferences()
        
        # Check for preferred providers in request
        preferred_providers = getattr(request, 'preferred_providers', [])
        for provider in preferred_providers:
            if isinstance(provider, ProviderType):
                preferences.provider_preference_scores[provider] = 0.8
        
        # Extract other preferences from context if available
        context = request.context
        if hasattr(context, 'quality_threshold'):
            # Infer quality vs speed preference from quality threshold
            if context.quality_threshold > 0.8:
                preferences.quality_vs_speed_preference = 0.8  # Quality priority
            else:
                preferences.quality_vs_speed_preference = 0.3  # Speed priority
        
        return preferences
    
    def _extract_resource_constraints(self, request: ExecuteRequest) -> ResourceConstraints:
        """Extract resource constraints from request."""
        context = request.context
        
        return ResourceConstraints(
            max_latency_seconds=getattr(context, 'timeout', None),
            min_quality_threshold=getattr(context, 'quality_threshold', None),
            is_premium_user=getattr(context, 'is_premium_user', False),
            billing_tier=getattr(context, 'billing_tier', "standard")
        )
    
    def _get_provider_availability(self) -> Dict[ProviderType, bool]:
        """Get current provider availability."""
        # In real implementation, this would check actual provider status
        # For now, assume all providers are available
        return {provider: True for provider in ProviderType}
    
    def _get_basic_provider_availability(self) -> Dict[str, bool]:
        """Get basic provider availability for backward compatibility."""
        return {provider.value: True for provider in ProviderType}
    
    def _get_basic_historical_performance(self) -> Dict[str, float]:
        """Get basic historical performance for backward compatibility."""
        performance = {}
        for provider in ProviderType:
            if provider.value in self.performance_history:
                performance[provider.value] = self.performance_history[provider.value].get("reputation", 0.8)
            else:
                performance[provider.value] = 0.8  # Default performance
        return performance
    
    def _map_context_to_string(self, request: ExecuteRequest) -> str:
        """Map TaskType to context string for backward compatibility."""
        mapping = {
            TaskType.CODE_GENERATION: "code_generation",
            TaskType.CODE_ANALYSIS: "analysis", 
            TaskType.DEBUGGING: "debugging",
            TaskType.DOCUMENTATION: "documentation",
            TaskType.TESTING: "testing",
            TaskType.REFACTORING: "refactoring"
        }
        return mapping.get(request.task_type, "general")
    
    def _collect_training_sample(
        self,
        request: ExecuteRequest,
        decision: RoutingDecision, 
        state_vector: Any,
        encoding_metadata: Dict[str, Any]
    ) -> None:
        """Collect sample for DQN training."""
        training_sample = {
            "timestamp": decision.metadata.get("timestamp"),
            "request_type": request.task_type.value,
            "state_vector": state_vector.tolist() if hasattr(state_vector, 'tolist') else state_vector,
            "selected_provider": decision.provider.value,
            "selected_model": decision.model,
            "selected_persona": decision.persona.value,
            "confidence": decision.confidence,
            "complexity_score": decision.complexity_score,
            "context_score": decision.context_score,
            "capability_score": decision.capability_score,
            "encoding_metadata": encoding_metadata
        }
        
        self.training_data.append(training_sample)
        
        # Limit training data size to prevent memory issues
        if len(self.training_data) > 1000:
            self.training_data = self.training_data[-1000:]
        
        logger.debug(f"Collected training sample: {decision.provider.value}/{decision.model}")
    
    def update_provider_performance(
        self, 
        provider: ProviderType, 
        performance_metrics: Dict[str, float]
    ) -> None:
        """Update provider performance tracking."""
        provider_key = provider.value
        
        if provider_key not in self.performance_history:
            self.performance_history[provider_key] = {}
        
        # Update with exponential moving average
        alpha = 0.2  # Learning rate
        current = self.performance_history[provider_key]
        
        for metric, value in performance_metrics.items():
            if metric in current:
                current[metric] = (1 - alpha) * current[metric] + alpha * value
            else:
                current[metric] = value
        
        # Track interaction count
        current["interactions"] = current.get("interactions", 0) + 1
        
        logger.debug(f"Updated performance for {provider.value}: {performance_metrics}")
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing and training statistics."""
        return {
            "total_routes": len(self.training_data),
            "encoding_type": "advanced" if self.use_advanced_encoding else "basic",
            "state_dimensions": self.state_encoder.state_size if self.state_encoder else 21,
            "training_data_collected": len(self.training_data),
            "provider_performance_tracked": len(self.performance_history),
            "advanced_router_history": len(self.advanced_router.routing_history)
        }
    
    def create_dqn_agent(
        self, 
        learning_rate: float = 0.001,
        **kwargs
    ) -> DQNRoutingAgent:
        """Create DQN agent compatible with this router's state encoding."""
        state_size = self.state_encoder.state_size if self.state_encoder else 21
        action_size = 12  # Number of routing actions
        
        agent = DQNRoutingAgent(
            state_size=state_size,
            action_size=action_size,
            learning_rate=learning_rate,
            **kwargs
        )
        
        # Initialize networks for training
        agent.initialize_networks()
        
        logger.info(f"Created DQN agent with {state_size}D state space")
        return agent
    
    def convert_decision_to_routing_action(self, decision: RoutingDecision) -> RoutingAction:
        """Convert RoutingDecision to DQN RoutingAction."""
        # Determine strategy based on decision characteristics
        if decision.capability_score > 0.9:
            strategy = "performance"
        elif decision.complexity_score < 0.4:
            strategy = "cost_efficient"
        elif decision.confidence > 0.8:
            strategy = "task_optimized"
        else:
            strategy = "balanced"
        
        return RoutingAction(
            provider=decision.provider,
            model=decision.model,
            strategy=strategy
        )


# Convenience function for easy integration
def create_dqn_router_bridge(
    encoding_strategy: str = "comprehensive",
    collect_training_data: bool = False,
    **kwargs
) -> DQNRouterBridge:
    """
    Create DQN router bridge with standard configuration.
    
    Args:
        encoding_strategy: State encoding strategy ("minimal", "standard", "comprehensive")
        collect_training_data: Whether to collect training data
        **kwargs: Additional arguments for DQNRouterBridge
        
    Returns:
        Configured DQNRouterBridge instance
    """
    return DQNRouterBridge(
        use_advanced_encoding=True,
        encoding_strategy=encoding_strategy,
        collect_training_data=collect_training_data,
        **kwargs
    )