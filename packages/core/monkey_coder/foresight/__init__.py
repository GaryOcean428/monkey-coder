"""
Foresight and Predictive Intelligence Module.

This module provides advanced foresight capabilities including:
- Predictive analysis and outcome modeling
- Imaginative extrapolation of possibilities
- Quantum-enhanced decision making
- Multi-modal context analysis
- Cross-project pattern learning

Key Components:
- PredictiveForesightEngine: Core foresight analysis
- QuantumForesight: Quantum-enhanced predictions
- ImaginativeEngine: Creative possibility generation
"""

from .predictive_engine import (
    PredictiveForesightEngine,
    ForesightType,
    ForesightContext,
    Prediction,
    ProbabilityNode
)

__all__ = [
    "PredictiveForesightEngine",
    "ForesightType",
    "ForesightContext",
    "Prediction",
    "ProbabilityNode"
]

# Claude 4.5 Model Specifications for Foresight Engine
CLAUDE_45_FORESIGHT_CONFIG = {
    "claude-4.5-sonnet-20250930": {
        "context_window": 200000,
        "output_tokens": 64000,
        "foresight_capabilities": {
            "logical_analysis": 0.95,
            "imaginative_extrapolation": 0.90,
            "probabilistic_reasoning": 0.88,
            "temporal_prediction": 0.85,
            "causal_analysis": 0.92,
            "emergent_pattern_detection": 0.87
        },
        "optimal_for": [
            "complex_architectural_foresight",
            "multi_step_reasoning",
            "creative_problem_solving",
            "long_term_planning"
        ]
    },
    "claude-4.5-haiku-20250930": {
        "context_window": 200000,
        "output_tokens": 32000,
        "foresight_capabilities": {
            "logical_analysis": 0.85,
            "imaginative_extrapolation": 0.80,
            "probabilistic_reasoning": 0.82,
            "temporal_prediction": 0.78,
            "causal_analysis": 0.83,
            "emergent_pattern_detection": 0.79
        },
        "optimal_for": [
            "rapid_foresight_analysis",
            "quick_outcome_prediction",
            "tactical_planning",
            "immediate_decision_support"
        ]
    },
    "claude-opus-4-1-20250805": {
        "context_window": 200000,
        "output_tokens": 32000,
        "foresight_capabilities": {
            "logical_analysis": 0.98,
            "imaginative_extrapolation": 0.95,
            "probabilistic_reasoning": 0.93,
            "temporal_prediction": 0.90,
            "causal_analysis": 0.96,
            "emergent_pattern_detection": 0.92
        },
        "optimal_for": [
            "specialized_domain_foresight",
            "high_stakes_predictions",
            "novel_approach_generation",
            "strategic_planning"
        ]
    },
    "claude-sonnet-4-20250514": {
        "context_window": 200000,
        "output_tokens": 32000,
        "foresight_capabilities": {
            "logical_analysis": 0.93,
            "imaginative_extrapolation": 0.88,
            "probabilistic_reasoning": 0.90,
            "temporal_prediction": 0.86,
            "causal_analysis": 0.91,
            "emergent_pattern_detection": 0.85
        },
        "optimal_for": [
            "balanced_foresight_analysis",
            "general_purpose_prediction",
            "architectural_planning",
            "cross_domain_analysis"
        ]
    }
}

# Foresight Model Selection Logic
def select_optimal_claude_model_for_foresight(
    foresight_type: ForesightType,
    complexity_level: float = 0.5,
    speed_requirement: str = "balanced"  # "fast", "balanced", "thorough"
) -> str:
    """
    Select optimal Claude 4.5 model for foresight analysis.

    Args:
        foresight_type: Type of foresight analysis needed
        complexity_level: Task complexity (0.0-1.0)
        speed_requirement: Speed vs quality preference

    Returns:
        Optimal Claude model identifier
    """
    if speed_requirement == "fast" or complexity_level < 0.3:
        return "claude-4.5-haiku-20250930"

    if complexity_level > 0.9 or foresight_type == ForesightType.IMAGINATIVE:
        return "claude-opus-4-1-20250805"

    if foresight_type in [ForesightType.LOGICAL, ForesightType.CAUSAL]:
        return "claude-4.5-sonnet-20250930"

    return "claude-sonnet-4-20250514"  # Balanced default
