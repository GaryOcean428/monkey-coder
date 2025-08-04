"""
Quantum Routing Engine - Phase 2 Implementation

This module implements the advanced quantum routing capabilities for the Monkey Coder
platform, providing intelligent AI model selection using Deep Q-Network (DQN)
algorithms, multi-strategy parallel execution, comprehensive performance metrics,
and Redis-based caching for optimal routing decisions.

Phase 2 Features:
- Enhanced DQN Agent with neural network implementation
- Experience Replay Buffer with prioritized sampling
- Quantum Routing Manager with multi-strategy execution
- Comprehensive performance metrics and analytics
- Real-time monitoring and alerting
- Redis-based intelligent caching system

Built on proven multi-agent patterns and adapted for the
Monkey Coder platform's specific routing requirements.
"""

# Core quantum execution components
from .manager import (
    QuantumManager,
    TaskVariation,
    CollapseStrategy,
    QuantumResult,
    quantum_task
)

# Phase 2: Enhanced DQN components
from .dqn_agent import (
    DQNRoutingAgent,
    RoutingAction,
    RoutingState
)

from .experience_buffer import (
    Experience,
    ExperienceReplayBuffer,
    PrioritizedExperienceBuffer
)

from .neural_network import (
    DQNNetwork,
    NumpyDQNModel,
    create_dqn_network
)

# Phase 2: Quantum Routing Manager
from .quantum_routing_manager import (
    QuantumRoutingManager,
    RoutingStrategy,
    QuantumRoutingResult,
    RoutingMetrics
)

# Phase 2: Performance Metrics System
from .performance_metrics import (
    PerformanceMetricsCollector,
    MetricType,
    MetricDataPoint,
    PerformanceAlert
)

__all__ = [
    # Core quantum execution
    "QuantumManager",
    "TaskVariation", 
    "CollapseStrategy",
    "QuantumResult",
    "quantum_task",
    
    # DQN components
    "DQNRoutingAgent",
    "RoutingAction", 
    "RoutingState",
    
    # Experience replay components
    "Experience",
    "ExperienceReplayBuffer", 
    "PrioritizedExperienceBuffer",
    
    # Neural network components
    "DQNNetwork",
    "NumpyDQNModel",
    "create_dqn_network",
    
    # Quantum routing manager
    "QuantumRoutingManager",
    "RoutingStrategy",
    "QuantumRoutingResult",
    "RoutingMetrics",
    
    # Performance metrics
    "PerformanceMetricsCollector",
    "MetricType",
    "MetricDataPoint",
    "PerformanceAlert",
]

__version__ = "2.0.0"  # Phase 2 implementation