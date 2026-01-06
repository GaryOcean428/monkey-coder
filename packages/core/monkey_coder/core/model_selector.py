"""
Intelligent Model Selection Strategy for Monkey Coder.

This module provides automatic model selection based on:
- Task type (editing, refactoring, documentation, etc.)
- Context size requirements
- Cost optimization preferences
- Performance requirements
- Capability requirements

Model Selection Matrix:
- Quick edits: Claude Opus 4.5 (low effort)
- Standard coding: GPT-5.2
- Complex refactors: Claude Opus 4.5 (high effort)
- Large codebases: Gemini 3 Pro (1M context)
- Documentation: Gemini 3 Pro + grounding
- Algorithm design: Gemini 3 Pro + code execution
- Agentic workflows: GPT-5.2-Codex
- Cost-sensitive: Qwen3-Coder
"""

import logging
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class TaskType(str, Enum):
    """Types of tasks for model selection."""
    EDIT = "edit"
    REFACTOR = "refactor"
    DOCUMENTATION = "documentation"
    ALGORITHM = "algorithm"
    DEBUG = "debug"
    REVIEW = "review"
    AGENT = "agent"
    CHAT = "chat"
    PLANNING = "planning"
    TESTING = "testing"


class PerformanceTier(str, Enum):
    """Performance tier preferences."""
    FASTEST = "fastest"
    BALANCED = "balanced"
    QUALITY = "quality"
    COST_OPTIMIZED = "cost_optimized"


@dataclass
class ModelSelection:
    """Selected model with reasoning."""
    model: str
    provider: str
    reasoning: str
    fallback_models: List[str]
    estimated_cost: Optional[float] = None
    config: Optional[Dict[str, Any]] = None


class ModelSelector:
    """
    Intelligent model selector based on task requirements.
    """

    # Model capabilities matrix
    MODEL_CAPABILITIES: Dict[str, Dict[str, Any]] = {
        "claude-opus-4-5": {
            "provider": "anthropic",
            "max_context": 200_000,
            "strengths": ["editing", "refactoring", "debugging", "swe_bench"],
            "best_for": ["edit", "refactor", "debug", "review"],
            "input_cost": 5.00,
            "output_cost": 25.00,
            "swe_bench_score": 80.9,
            "speed": "fast",
            "effort_control": True,
        },
        "gpt-5.2": {
            "provider": "openai",
            "max_context": 400_000,
            "strengths": ["reasoning", "coding", "balance"],
            "best_for": ["chat", "refactor", "planning"],
            "input_cost": 1.75,
            "output_cost": 14.00,
            "swe_bench_score": 75.0,
            "speed": "medium",
            "reasoning_control": True,
        },
        "gpt-5.2-pro": {
            "provider": "openai",
            "max_context": 400_000,
            "strengths": ["deep_reasoning", "architecture", "planning"],
            "best_for": ["planning", "refactor"],
            "input_cost": 21.00,
            "output_cost": 168.00,
            "swe_bench_score": 80.0,
            "speed": "slow",
            "reasoning_control": True,
        },
        "gpt-5.2-codex": {
            "provider": "openai",
            "max_context": 400_000,
            "strengths": ["agentic_coding", "context_compaction"],
            "best_for": ["agent", "refactor"],
            "input_cost": 2.50,
            "output_cost": 15.00,
            "swe_bench_score": 85.0,
            "speed": "medium",
            "agentic": True,
        },
        "gemini-3-pro": {
            "provider": "google",
            "max_context": 1_048_576,  # 1M tokens
            "strengths": ["large_context", "grounding", "code_execution", "multimodal"],
            "best_for": ["documentation", "algorithm", "review"],
            "input_cost": 2.00,
            "output_cost": 12.00,
            "swe_bench_score": 72.0,
            "speed": "medium",
            "thinking_control": True,
            "code_execution": True,
            "search_grounding": True,
        },
        "qwen3-coder-480b": {
            "provider": "groq",
            "max_context": 256_000,
            "strengths": ["cost_efficiency", "speed"],
            "best_for": ["edit", "chat"],
            "input_cost": 0.59,
            "output_cost": 0.79,
            "swe_bench_score": 68.0,
            "speed": "fastest",
        },
        "claude-sonnet-4.5": {
            "provider": "anthropic",
            "max_context": 200_000,
            "strengths": ["balance", "speed", "quality"],
            "best_for": ["chat", "edit", "review"],
            "input_cost": 3.00,
            "output_cost": 15.00,
            "swe_bench_score": 77.2,
            "speed": "fast",
        },
    }

    def __init__(self):
        """Initialize the model selector."""
        self.selection_history: List[ModelSelection] = []

    def select_model(
        self,
        task_type: TaskType,
        context_size: int = 0,
        performance_tier: PerformanceTier = PerformanceTier.BALANCED,
        required_capabilities: Optional[List[str]] = None,
        budget_constraint: Optional[float] = None,
    ) -> ModelSelection:
        """
        Select the optimal model for the given task.

        Args:
            task_type: Type of task to perform
            context_size: Size of context in tokens
            performance_tier: Performance preference
            required_capabilities: Required model capabilities
            budget_constraint: Maximum cost per 1M tokens

        Returns:
            ModelSelection with chosen model and configuration
        """
        required_capabilities = required_capabilities or []

        # Handle large context requirements
        if context_size > 200_000:
            logger.info(f"Large context ({context_size} tokens) - selecting Gemini 3 Pro")
            return ModelSelection(
                model="gemini-3-pro",
                provider="google",
                reasoning="1M context window required for large codebase",
                fallback_models=["gpt-5.2"],
                config={"thinking_level": "mid"},
            )

        # Task-specific selection
        selection = self._select_by_task(
            task_type,
            performance_tier,
            required_capabilities,
            budget_constraint
        )

        self.selection_history.append(selection)
        logger.info(
            f"Selected {selection.model} for {task_type.value}: {selection.reasoning}"
        )

        return selection

    def _select_by_task(
        self,
        task_type: TaskType,
        performance_tier: PerformanceTier,
        required_capabilities: List[str],
        budget_constraint: Optional[float],
    ) -> ModelSelection:
        """Select model based on task type."""

        # Cost-optimized tier
        if performance_tier == PerformanceTier.COST_OPTIMIZED:
            return ModelSelection(
                model="qwen3-coder-480b",
                provider="groq",
                reasoning="Cost-optimized tier selected",
                fallback_models=["claude-sonnet-4.5"],
                estimated_cost=0.69,
            )

        # Fastest tier
        if performance_tier == PerformanceTier.FASTEST:
            if task_type == TaskType.EDIT:
                return ModelSelection(
                    model="claude-opus-4-5",
                    provider="anthropic",
                    reasoning="Fastest editing with low effort",
                    fallback_models=["qwen3-coder-480b"],
                    config={"effort": "low"},
                    estimated_cost=15.00,
                )
            return ModelSelection(
                model="qwen3-coder-480b",
                provider="groq",
                reasoning="Fastest general performance",
                fallback_models=["claude-sonnet-4.5"],
                estimated_cost=0.69,
            )

        # Task-specific selection matrix
        task_matrix = {
            TaskType.EDIT: ModelSelection(
                model="claude-opus-4-5",
                provider="anthropic",
                reasoning="80.9% SWE-bench score, optimized for edits",
                fallback_models=["claude-sonnet-4.5", "gpt-5.2"],
                config={"effort": "medium"},
                estimated_cost=15.00,
            ),
            TaskType.REFACTOR: ModelSelection(
                model="claude-opus-4-5" if performance_tier == PerformanceTier.QUALITY else "gpt-5.2",
                provider="anthropic" if performance_tier == PerformanceTier.QUALITY else "openai",
                reasoning="Complex refactoring requires highest capability",
                fallback_models=["gpt-5.2-pro", "claude-opus-4-5"],
                config={"effort": "high"} if performance_tier == PerformanceTier.QUALITY else {"effort": "medium"},
                estimated_cost=30.00 if performance_tier == PerformanceTier.QUALITY else 7.88,
            ),
            TaskType.DOCUMENTATION: ModelSelection(
                model="gemini-3-pro",
                provider="google",
                reasoning="Search grounding for accurate documentation",
                fallback_models=["gpt-5.2"],
                config={"thinking_level": "hi", "enable_grounding": True},
                estimated_cost=7.00,
            ),
            TaskType.ALGORITHM: ModelSelection(
                model="gemini-3-pro",
                provider="google",
                reasoning="Code execution sandbox for testing algorithms",
                fallback_models=["gpt-5.2-pro"],
                config={"thinking_level": "hi", "enable_code_execution": True},
                estimated_cost=7.00,
            ),
            TaskType.DEBUG: ModelSelection(
                model="claude-opus-4-5",
                provider="anthropic",
                reasoning="Strong debugging with high effort reasoning",
                fallback_models=["gpt-5.2"],
                config={"effort": "high", "extended_thinking": True},
                estimated_cost=30.00,
            ),
            TaskType.REVIEW: ModelSelection(
                model="claude-opus-4-5",
                provider="anthropic",
                reasoning="Excellent code review with balanced effort",
                fallback_models=["gemini-3-pro", "gpt-5.2"],
                config={"effort": "medium"},
                estimated_cost=15.00,
            ),
            TaskType.AGENT: ModelSelection(
                model="gpt-5.2-codex",
                provider="openai",
                reasoning="Purpose-built for agentic coding workflows",
                fallback_models=["claude-opus-4-5"],
                config={"effort": "medium"},
                estimated_cost=8.75,
            ),
            TaskType.CHAT: ModelSelection(
                model="gpt-5.2",
                provider="openai",
                reasoning="Best balance of cost and performance",
                fallback_models=["claude-sonnet-4.5"],
                config={"effort": "medium"},
                estimated_cost=7.88,
            ),
            TaskType.PLANNING: ModelSelection(
                model="gpt-5.2-pro" if performance_tier == PerformanceTier.QUALITY else "gpt-5.2",
                provider="openai",
                reasoning="Deep reasoning for architectural planning",
                fallback_models=["claude-opus-4-5"],
                config={"effort": "xhigh"} if performance_tier == PerformanceTier.QUALITY else {"effort": "high"},
                estimated_cost=94.50 if performance_tier == PerformanceTier.QUALITY else 7.88,
            ),
            TaskType.TESTING: ModelSelection(
                model="gpt-5.2",
                provider="openai",
                reasoning="Good test generation capabilities",
                fallback_models=["gemini-3-pro"],
                config={"effort": "medium"},
                estimated_cost=7.88,
            ),
        }

        selection = task_matrix.get(task_type)
        if not selection:
            # Default fallback
            selection = ModelSelection(
                model="gpt-5.2",
                provider="openai",
                reasoning=f"Default selection for {task_type.value}",
                fallback_models=["claude-sonnet-4.5"],
                estimated_cost=7.88,
            )

        # Check required capabilities
        if required_capabilities:
            model_caps = self.MODEL_CAPABILITIES.get(selection.model, {})
            model_strengths = model_caps.get("strengths", [])
            
            missing_caps = [cap for cap in required_capabilities if cap not in model_strengths]
            if missing_caps:
                logger.warning(
                    f"Model {selection.model} missing capabilities: {missing_caps}. "
                    f"Consider using a fallback model."
                )

        # Check budget constraint
        if budget_constraint and selection.estimated_cost:
            if selection.estimated_cost > budget_constraint:
                # Select cheaper alternative
                logger.warning(
                    f"Selected model exceeds budget ({selection.estimated_cost} > {budget_constraint}). "
                    f"Selecting cost-optimized model."
                )
                return ModelSelection(
                    model="qwen3-coder-480b",
                    provider="groq",
                    reasoning="Budget constraint applied",
                    fallback_models=["claude-sonnet-4.5"],
                    estimated_cost=0.69,
                )

        return selection

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        return self.MODEL_CAPABILITIES.get(model, {})

    def list_available_models(self) -> List[str]:
        """List all available models."""
        return list(self.MODEL_CAPABILITIES.keys())

    def get_selection_history(self) -> List[ModelSelection]:
        """Get history of model selections."""
        return self.selection_history
