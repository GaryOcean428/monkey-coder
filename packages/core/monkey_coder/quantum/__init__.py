"""
Quantum Routing Engine

This module implements the quantum routing capabilities for the Monkey Coder
platform, providing intelligent AI model selection using Deep Q-Network (DQN)
algorithms and multi-strategy parallel execution patterns.

Built on proven patterns from the monkey1 project and adapted for the
Monkey Coder platform's specific routing requirements.
"""

from .dqn_agent import DQNRoutingAgent, RoutingAction, RoutingState
from .experience_buffer import Experience, ExperienceBuffer, BufferFullError, BufferEmptyError
from .neural_networks import (
    QNetworkArchitecture,
    DQNNetworkManager,
    create_dqn_networks,
)
from .training_pipeline import (
    QuantumDQNTrainer,
    TrainingScenario,
    TrainingPhase,
    QuantumTrainingResult,
    TrainingScenarioGenerator,
    create_quantum_dqn_trainer,
)
from .state_encoder import (
    AdvancedStateEncoder,
    TaskContextProfile,
    ProviderPerformanceHistory,
    UserPreferences,
    ResourceConstraints,
    ContextComplexity,
    TimeWindow,
    create_state_encoder,
)

__all__ = [
    "DQNRoutingAgent",
    "RoutingAction", 
    "RoutingState",
    "Experience",
    "ExperienceBuffer",
    "BufferFullError",
    "BufferEmptyError",
    "QNetworkArchitecture",
    "DQNNetworkManager",
    "create_dqn_networks",
    "QuantumDQNTrainer",
    "TrainingScenario",
    "TrainingPhase",
    "QuantumTrainingResult", 
    "TrainingScenarioGenerator",
    "create_quantum_dqn_trainer",
    "AdvancedStateEncoder",
    "TaskContextProfile",
    "ProviderPerformanceHistory",
    "UserPreferences", 
    "ResourceConstraints",
    "ContextComplexity",
    "TimeWindow",
    "create_state_encoder",
]

__version__ = "1.0.0"