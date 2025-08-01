"""
Quantum Routing Manager - Phase 2 Core Component

This module implements the advanced quantum routing engine that orchestrates
multiple routing strategies in parallel, uses DQN learning for optimal decisions,
and provides comprehensive metrics and performance tracking.

Key Features:
- Multi-strategy parallel routing execution
- DQN-based learning and adaptation
- Comprehensive performance metrics
- Redis-based caching system
- Real-time routing analytics
"""

import asyncio
import logging
import time
import json
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor

from ..models import ExecuteRequest, ProviderType
from .manager import QuantumManager, TaskVariation, CollapseStrategy, QuantumResult
from .dqn_agent import DQNRoutingAgent, RoutingState, RoutingAction
from ..core.routing import AdvancedRouter, RoutingDecision

# Try to import redis for caching
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Available routing strategies for quantum execution."""
    
    TASK_OPTIMIZED = "task_optimized"      # Optimize for task-specific performance
    COST_EFFICIENT = "cost_efficient"     # Minimize cost while maintaining quality
    PERFORMANCE_FOCUSED = "performance"   # Maximum quality regardless of cost
    BALANCED = "balanced"                  # Balance between cost, speed, and quality
    LEARNING_OPTIMIZED = "learning"       # Use DQN learning for optimization


@dataclass
class QuantumRoutingResult:
    """Result from quantum routing execution with comprehensive metrics."""
    
    primary_decision: RoutingDecision
    alternative_decisions: List[RoutingDecision]
    execution_time: float
    strategy_used: RoutingStrategy
    confidence_score: float
    learning_applied: bool
    cache_hit: bool
    performance_metrics: Dict[str, Any]
    collapse_strategy: CollapseStrategy
    parallel_executions: int


@dataclass
class RoutingMetrics:
    """Comprehensive routing performance metrics."""
    
    total_requests: int
    cache_hit_rate: float
    average_response_time: float
    strategy_performance: Dict[str, float]
    provider_success_rates: Dict[str, float]
    learning_accuracy: float
    cost_efficiency: float
    quality_scores: List[float]
    timestamp: float


class QuantumRoutingManager:
    """
    Advanced Quantum Routing Manager for Phase 2.
    
    Orchestrates multiple routing strategies in parallel, applies machine learning
    for optimal decision making, and provides comprehensive analytics.
    """
    
    def __init__(
        self,
        max_workers: int = 6,
        enable_learning: bool = True,
        enable_caching: bool = True,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        cache_ttl: int = 3600,  # 1 hour
        quantum_timeout: float = 30.0
    ):
        """
        Initialize the Quantum Routing Manager.
        
        Args:
            max_workers: Maximum parallel workers for quantum execution
            enable_learning: Whether to enable DQN learning
            enable_caching: Whether to enable Redis caching
            redis_host: Redis server host
            redis_port: Redis server port
            cache_ttl: Cache time-to-live in seconds
            quantum_timeout: Timeout for quantum execution
        """
        self.max_workers = max_workers
        self.enable_learning = enable_learning
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        self.quantum_timeout = quantum_timeout
        
        # Initialize core components
        self.quantum_manager = QuantumManager(
            max_workers=max_workers,
            timeout=quantum_timeout,
            default_strategy=CollapseStrategy.BEST_SCORE
        )
        
        self.advanced_router = AdvancedRouter()
        
        # Initialize DQN agent for learning
        if self.enable_learning:
            self.dqn_agent = DQNRoutingAgent(
                state_size=21,  # From RoutingState.to_vector()
                action_size=12,  # Number of routing actions
                learning_rate=0.001,
                exploration_rate=0.3,  # Start with moderate exploration
                memory_size=5000,
                batch_size=64
            )
        else:
            self.dqn_agent = None
        
        # Initialize Redis cache
        self.redis_client = None
        if self.enable_caching and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Connected to Redis cache")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                self.redis_client = None
        
        # Performance tracking
        self.metrics = RoutingMetrics(
            total_requests=0,
            cache_hit_rate=0.0,
            average_response_time=0.0,
            strategy_performance={},
            provider_success_rates={},
            learning_accuracy=0.0,
            cost_efficiency=0.0,
            quality_scores=[],
            timestamp=time.time()
        )
        
        self.request_history = []
        self.performance_history = []
        
        logger.info("Initialized Quantum Routing Manager")
    
    async def route_with_quantum_strategies(
        self,
        request: ExecuteRequest,
        strategies: Optional[List[RoutingStrategy]] = None,
        collapse_strategy: CollapseStrategy = CollapseStrategy.BEST_SCORE
    ) -> QuantumRoutingResult:
        """
        Route request using quantum strategies with parallel execution.
        
        Args:
            request: The execution request to route
            strategies: List of routing strategies to execute in parallel
            collapse_strategy: Strategy for collapsing parallel results
            
        Returns:
            Quantum routing result with primary decision and alternatives
        """
        start_time = time.time()
        cache_hit = False
        
        # Check cache first
        cache_key = self._generate_cache_key(request)
        cached_result = await self._get_cached_result(cache_key)
        
        if cached_result:
            cache_hit = True
            logger.debug(f"Cache hit for request: {cache_key}")
            # Update cache hit metrics
            self._update_cache_metrics(True)
            return cached_result
        
        # Default strategies if none provided
        if strategies is None:
            strategies = [
                RoutingStrategy.TASK_OPTIMIZED,
                RoutingStrategy.PERFORMANCE_FOCUSED,
                RoutingStrategy.BALANCED
            ]
            
            # Add learning strategy if DQN is enabled
            if self.enable_learning and self.dqn_agent:
                strategies.append(RoutingStrategy.LEARNING_OPTIMIZED)
        
        # Create task variations for parallel execution
        routing_variations = []
        
        for i, strategy in enumerate(strategies):
            variation = TaskVariation(
                id=f"route_{strategy.value}",
                task=self._execute_routing_strategy,
                params={
                    "request": request,
                    "strategy": strategy
                },
                priority=self._get_strategy_priority(strategy),
                metadata={"strategy": strategy.value}
            )
            routing_variations.append(variation)
        
        # Execute routing strategies in quantum parallel mode
        quantum_result = await self.quantum_manager.execute_quantum_task(
            variations=routing_variations,
            collapse_strategy=collapse_strategy,
            scoring_fn=self._score_routing_decision
        )
        
        # Process quantum result
        if quantum_result.success:
            primary_decision = quantum_result.value
            
            # Get alternative decisions from combined result
            alternatives = []
            if hasattr(quantum_result, 'metadata') and quantum_result.metadata:
                alternatives = quantum_result.metadata.get('alternatives', [])
            
            # Apply learning if enabled
            learning_applied = False
            if self.enable_learning and self.dqn_agent:
                await self._apply_learning(request, primary_decision, quantum_result)
                learning_applied = True
            
            # Create comprehensive result
            result = QuantumRoutingResult(
                primary_decision=primary_decision,
                alternative_decisions=alternatives,
                execution_time=time.time() - start_time,
                strategy_used=self._determine_winning_strategy(quantum_result),
                confidence_score=quantum_result.score,
                learning_applied=learning_applied,
                cache_hit=cache_hit,
                performance_metrics=self._extract_performance_metrics(quantum_result),
                collapse_strategy=collapse_strategy,
                parallel_executions=len(strategies)
            )
            
            # Cache the result
            await self._cache_result(cache_key, result)
            
            # Update metrics
            self._update_routing_metrics(result)
            
            logger.info(f"Quantum routing completed: {primary_decision.provider.value}/{primary_decision.model} in {result.execution_time:.3f}s")
            return result
        
        else:
            # Fallback to standard routing if quantum execution fails
            logger.warning("Quantum routing failed, falling back to standard routing")
            fallback_decision = self.advanced_router.route_request(request)
            
            return QuantumRoutingResult(
                primary_decision=fallback_decision,
                alternative_decisions=[],
                execution_time=time.time() - start_time,
                strategy_used=RoutingStrategy.BALANCED,
                confidence_score=0.5,  # Lower confidence for fallback
                learning_applied=False,
                cache_hit=cache_hit,
                performance_metrics={},
                collapse_strategy=collapse_strategy,
                parallel_executions=0
            )
    
    async def _execute_routing_strategy(
        self,
        request: ExecuteRequest,
        strategy: RoutingStrategy
    ) -> RoutingDecision:
        """Execute a specific routing strategy."""
        
        if strategy == RoutingStrategy.LEARNING_OPTIMIZED and self.dqn_agent:
            return await self._execute_dqn_routing(request)
        
        elif strategy == RoutingStrategy.TASK_OPTIMIZED:
            return self._execute_task_optimized_routing(request)
        
        elif strategy == RoutingStrategy.COST_EFFICIENT:
            return self._execute_cost_efficient_routing(request)
        
        elif strategy == RoutingStrategy.PERFORMANCE_FOCUSED:
            return self._execute_performance_focused_routing(request)
        
        elif strategy == RoutingStrategy.BALANCED:
            return self.advanced_router.route_request(request)
        
        else:
            # Default fallback
            return self.advanced_router.route_request(request)
    
    async def _execute_dqn_routing(self, request: ExecuteRequest) -> RoutingDecision:
        """Execute routing using DQN agent."""
        
        # Convert request to routing state
        routing_state = self._request_to_routing_state(request)
        
        # Get action from DQN agent
        action = self.dqn_agent.act(routing_state)
        
        # Convert action to routing decision
        decision = RoutingDecision(
            provider=action.provider,
            model=action.model,
            persona=request.persona_config.persona if hasattr(request, 'persona_config') and request.persona_config else None,
            complexity_score=routing_state.task_complexity,
            context_score=0.8,  # Assume high context relevance from DQN
            capability_score=0.9,  # Assume high capability match from learning
            confidence=max(0.7, 1.0 - self.dqn_agent.exploration_rate),  # Higher confidence as exploration decreases
            reasoning=f"DQN agent selected {action.provider.value}/{action.model} using {action.strategy} strategy",
            metadata={
                "dqn_strategy": action.strategy,
                "exploration_rate": self.dqn_agent.exploration_rate,
                "training_steps": self.dqn_agent.training_step
            }
        )
        
        return decision
    
    def _execute_task_optimized_routing(self, request: ExecuteRequest) -> RoutingDecision:
        """Execute task-specific optimized routing."""
        
        # Get base decision from advanced router
        base_decision = self.advanced_router.route_request(request)
        
        # Apply task-specific optimizations
        if hasattr(request, 'task_type'):
            if request.task_type.value in ['code_generation', 'implementation']:
                # Prefer coding-specialized models
                if base_decision.provider == ProviderType.GROQ:
                    base_decision.model = "llama-3.3-70b-versatile"
                elif base_decision.provider == ProviderType.OPENAI:
                    base_decision.model = "gpt-4.1"
            
            elif request.task_type.value in ['analysis', 'reasoning']:
                # Prefer reasoning-optimized models
                if base_decision.provider == ProviderType.OPENAI:
                    base_decision.model = "o1"
                elif base_decision.provider == ProviderType.ANTHROPIC:
                    base_decision.model = "claude-opus-4-20250514"
        
        # Update reasoning
        base_decision.reasoning += " (task-optimized)"
        base_decision.confidence = min(1.0, base_decision.confidence * 1.1)
        
        return base_decision
    
    def _execute_cost_efficient_routing(self, request: ExecuteRequest) -> RoutingDecision:
        """Execute cost-efficient routing strategy."""
        
        # Get base decision from advanced router
        base_decision = self.advanced_router.route_request(request)
        
        # Apply cost optimization
        cost_efficient_models = {
            ProviderType.OPENAI: "gpt-4.1-mini",
            ProviderType.ANTHROPIC: "claude-3-5-haiku-20241022",
            ProviderType.GOOGLE: "models/gemini-2.0-flash",
            ProviderType.GROQ: "llama-3.1-8b-instant",
            ProviderType.GROK: "grok-3-mini"
        }
        
        if base_decision.provider in cost_efficient_models:
            base_decision.model = cost_efficient_models[base_decision.provider]
        
        # Prefer Groq for cost efficiency (fast hardware)
        if base_decision.complexity_score < 0.7:  # For simpler tasks
            base_decision.provider = ProviderType.GROQ
            base_decision.model = "llama-3.1-8b-instant"
        
        # Update reasoning
        base_decision.reasoning += " (cost-optimized)"
        
        return base_decision
    
    def _execute_performance_focused_routing(self, request: ExecuteRequest) -> RoutingDecision:
        """Execute performance-focused routing strategy."""
        
        # Get base decision from advanced router
        base_decision = self.advanced_router.route_request(request)
        
        # Apply performance optimization
        performance_models = {
            ProviderType.OPENAI: "gpt-4.1",
            ProviderType.ANTHROPIC: "claude-opus-4-20250514",
            ProviderType.GOOGLE: "models/gemini-2.5-pro",
            ProviderType.GROQ: "llama-3.3-70b-versatile",
            ProviderType.GROK: "grok-4-latest"
        }
        
        if base_decision.provider in performance_models:
            base_decision.model = performance_models[base_decision.provider]
        
        # Boost confidence for performance-focused selection
        base_decision.confidence = min(1.0, base_decision.confidence * 1.2)
        base_decision.reasoning += " (performance-optimized)"
        
        return base_decision
    
    def _score_routing_decision(self, decision: RoutingDecision) -> float:
        """Score a routing decision for quantum collapse strategy."""
        
        score = 0.0
        
        # Base score from decision confidence
        score += decision.confidence * 0.4
        
        # Score based on capability match
        score += decision.capability_score * 0.3
        
        # Score based on context relevance
        score += decision.context_score * 0.2
        
        # Bonus for recent good performance of this provider/model combination
        provider_key = f"{decision.provider.value}:{decision.model}"
        historical_performance = self.metrics.provider_success_rates.get(provider_key, 0.5)
        score += historical_performance * 0.1
        
        return score
    
    def _request_to_routing_state(self, request: ExecuteRequest) -> RoutingState:
        """Convert execution request to routing state for DQN."""
        
        # Analyze request complexity
        complexity_score, _ = self.advanced_router.scoring_manager.get_complexity_score(request)
        
        # Determine context type
        context_type, _ = self.advanced_router.scoring_manager.get_context_classification(request)
        
        # Get provider availability (assume all available for now)
        provider_availability = {
            "openai": True,
            "anthropic": True,
            "google": True,
            "groq": True,
            "grok": True
        }
        
        # Get historical performance
        historical_performance = dict(self.metrics.provider_success_rates)
        
        # Resource constraints from request or defaults
        resource_constraints = {
            "cost_weight": 0.33,
            "time_weight": 0.33,
            "quality_weight": 0.34
        }
        
        # User preferences (simplified)
        user_preferences = {"preference_strength": 0.5}
        
        return RoutingState(
            task_complexity=complexity_score,
            context_type=context_type.value,
            provider_availability=provider_availability,
            historical_performance=historical_performance,
            resource_constraints=resource_constraints,
            user_preferences=user_preferences
        )
    
    async def _apply_learning(
        self,
        request: ExecuteRequest,
        decision: RoutingDecision,
        quantum_result: QuantumResult
    ):
        """Apply DQN learning based on routing outcome."""
        
        if not self.dqn_agent:
            return
        
        # Convert request to state
        current_state = self._request_to_routing_state(request)
        
        # Create action from decision
        action = RoutingAction(
            provider=decision.provider,
            model=decision.model,
            strategy="quantum_selected"
        )
        
        # Calculate reward based on quantum result performance
        reward = self._calculate_learning_reward(decision, quantum_result)
        
        # For learning, we assume the next state is similar (simplified)
        next_state = current_state
        
        # Store experience in DQN
        self.dqn_agent.remember(
            state=current_state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=True  # Each routing is a complete episode
        )
        
        # Train the DQN if we have enough experiences
        loss = self.dqn_agent.replay()
        if loss is not None:
            logger.debug(f"DQN training loss: {loss:.4f}")
    
    def _calculate_learning_reward(
        self,
        decision: RoutingDecision,
        quantum_result: QuantumResult
    ) -> float:
        """Calculate reward for DQN learning."""
        
        reward = 0.0
        
        # Base reward for successful routing
        if quantum_result.success:
            reward += 1.0
        else:
            return -0.5  # Penalty for failure
        
        # Reward based on decision confidence
        reward += decision.confidence * 0.3
        
        # Reward based on capability score
        reward += decision.capability_score * 0.2
        
        # Reward based on execution speed (faster is better)
        if quantum_result.execution_time < 2.0:
            reward += 0.2
        elif quantum_result.execution_time > 10.0:
            reward -= 0.2
        
        # Bonus for high-quality decisions
        if decision.confidence > 0.8 and decision.capability_score > 0.8:
            reward += 0.3
        
        return reward
    
    def _generate_cache_key(self, request: ExecuteRequest) -> str:
        """Generate cache key for routing request."""
        
        key_components = [
            str(hash(request.prompt)),
            request.task_type.value if hasattr(request, 'task_type') else "unknown",
            request.persona_config.persona.value if hasattr(request, 'persona_config') and request.persona_config else "developer"
        ]
        
        return f"routing:{':'.join(key_components)}"
    
    async def _get_cached_result(self, cache_key: str) -> Optional[QuantumRoutingResult]:
        """Get cached routing result."""
        
        if not self.redis_client:
            return None
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                result_dict = json.loads(cached_data)
                # Note: This is simplified - in production you'd want proper deserialization
                logger.debug(f"Cache hit: {cache_key}")
                return result_dict  # Simplified return
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
        
        return None
    
    async def _cache_result(self, cache_key: str, result: QuantumRoutingResult):
        """Cache routing result."""
        
        if not self.redis_client:
            return
        
        try:
            # Convert result to JSON (simplified)
            result_dict = asdict(result)
            # Note: This needs proper serialization handling for complex objects
            cached_data = json.dumps(result_dict, default=str)
            
            self.redis_client.setex(cache_key, self.cache_ttl, cached_data)
            logger.debug(f"Cached result: {cache_key}")
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
    
    def _get_strategy_priority(self, strategy: RoutingStrategy) -> int:
        """Get priority for routing strategy (higher = more important)."""
        
        priorities = {
            RoutingStrategy.LEARNING_OPTIMIZED: 10,
            RoutingStrategy.PERFORMANCE_FOCUSED: 8,
            RoutingStrategy.TASK_OPTIMIZED: 7,
            RoutingStrategy.BALANCED: 5,
            RoutingStrategy.COST_EFFICIENT: 3
        }
        
        return priorities.get(strategy, 1)
    
    def _determine_winning_strategy(self, quantum_result: QuantumResult) -> RoutingStrategy:
        """Determine which strategy won in quantum execution."""
        
        if hasattr(quantum_result, 'metadata') and quantum_result.metadata:
            strategy_name = quantum_result.metadata.get('strategy', 'balanced')
            try:
                return RoutingStrategy(strategy_name)
            except ValueError:
                pass
        
        return RoutingStrategy.BALANCED
    
    def _extract_performance_metrics(self, quantum_result: QuantumResult) -> Dict[str, Any]:
        """Extract performance metrics from quantum result."""
        
        return {
            "execution_time": quantum_result.execution_time,
            "score": quantum_result.score,
            "success": quantum_result.success,
            "variation_id": quantum_result.variation_id,
            "metadata": quantum_result.metadata or {}
        }
    
    def _update_cache_metrics(self, cache_hit: bool):
        """Update cache hit rate metrics."""
        
        # Simple running average calculation
        current_hits = self.metrics.cache_hit_rate * self.metrics.total_requests
        
        if cache_hit:
            current_hits += 1
        
        self.metrics.total_requests += 1
        self.metrics.cache_hit_rate = current_hits / self.metrics.total_requests
    
    def _update_routing_metrics(self, result: QuantumRoutingResult):
        """Update comprehensive routing metrics."""
        
        # Update request count
        self.metrics.total_requests += 1
        
        # Update average response time
        current_total_time = self.metrics.average_response_time * (self.metrics.total_requests - 1)
        self.metrics.average_response_time = (current_total_time + result.execution_time) / self.metrics.total_requests
        
        # Update strategy performance
        strategy_key = result.strategy_used.value
        if strategy_key not in self.metrics.strategy_performance:
            self.metrics.strategy_performance[strategy_key] = 0.0
        
        # Running average of strategy performance
        current_perf = self.metrics.strategy_performance[strategy_key]
        self.metrics.strategy_performance[strategy_key] = (current_perf * 0.8) + (result.confidence_score * 0.2)
        
        # Update provider success rates
        provider_key = f"{result.primary_decision.provider.value}:{result.primary_decision.model}"
        if provider_key not in self.metrics.provider_success_rates:
            self.metrics.provider_success_rates[provider_key] = 0.0
        
        success_score = 1.0 if result.confidence_score > 0.7 else 0.5
        current_rate = self.metrics.provider_success_rates[provider_key]
        self.metrics.provider_success_rates[provider_key] = (current_rate * 0.9) + (success_score * 0.1)
        
        # Update quality scores
        self.metrics.quality_scores.append(result.confidence_score)
        if len(self.metrics.quality_scores) > 100:  # Keep last 100 scores
            self.metrics.quality_scores = self.metrics.quality_scores[-100:]
        
        # Update timestamp
        self.metrics.timestamp = time.time()
    
    def get_routing_analytics(self) -> Dict[str, Any]:
        """Get comprehensive routing analytics."""
        
        return {
            "metrics": asdict(self.metrics),
            "dqn_performance": self.dqn_agent.get_performance_metrics() if self.dqn_agent else None,
            "quantum_metrics": self.quantum_manager.get_metrics(),
            "cache_status": {
                "enabled": self.enable_caching,
                "connected": self.redis_client is not None,
                "hit_rate": self.metrics.cache_hit_rate
            },
            "learning_status": {
                "enabled": self.enable_learning,
                "training_steps": self.dqn_agent.training_step if self.dqn_agent else 0,
                "exploration_rate": self.dqn_agent.exploration_rate if self.dqn_agent else 0.0
            }
        }
    
    async def optimize_routing_parameters(self):
        """Optimize routing parameters based on historical performance."""
        
        if not self.dqn_agent or len(self.dqn_agent.memory) < 100:
            return
        
        # Train the DQN with recent experiences
        for _ in range(10):  # Multiple training iterations
            loss = self.dqn_agent.replay()
            if loss is None:
                break
        
        logger.info("Optimized routing parameters using DQN training")
    
    async def save_routing_model(self, filepath: str):
        """Save the trained routing model."""
        
        if self.dqn_agent:
            self.dqn_agent.save_model(filepath)
            logger.info(f"Saved routing model to {filepath}")
    
    async def load_routing_model(self, filepath: str) -> bool:
        """Load a trained routing model."""
        
        if self.dqn_agent:
            success = self.dqn_agent.load_model(filepath)
            if success:
                logger.info(f"Loaded routing model from {filepath}")
            return success
        
        return False