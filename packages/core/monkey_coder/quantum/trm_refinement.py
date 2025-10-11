"""
Tiny Recursive Model (TRM) Refinement Module

This module implements TRM-inspired iterative refinement with learned halting
for adaptive computation in quantum routing and foresight engines.

Based on the principles of:
- Small networks with iterative refinement
- Dynamic halting based on confidence
- Inner/outer cycle structure (H inner cycles, K outer steps)
- Attention masks for context management
"""

import logging
import random
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class TRMConfig:
    """Configuration for TRM refinement."""
    latent_dim: int = 112  # Dimension of latent state vector
    answer_dim: int = 64   # Dimension of answer embedding
    max_inner_steps: int = 5  # Maximum H inner cycles
    max_outer_steps: int = 3  # Maximum K outer cycles
    halt_threshold: float = 0.8  # Confidence threshold for halting
    learning_rate: float = 0.001
    gradient_clip: float = 1.0
    enable_attention: bool = True
    random_seed: Optional[int] = 42


@dataclass
class RefinementStep:
    """Records details of a single refinement step."""
    step_number: int
    cycle_type: str  # 'inner' or 'outer'
    latent_state: np.ndarray
    answer_embedding: np.ndarray
    halt_probability: float
    confidence: float
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class TRMRefinementModule:
    """
    TRM-inspired refinement module for iterative improvement of decisions.
    
    Implements:
    - Latent state (z) refinement through inner cycles
    - Answer embedding (y) updates through outer cycles
    - Learned halting head for adaptive computation
    - Attention mechanism for context management
    """
    
    def __init__(self, config: Optional[TRMConfig] = None):
        """
        Initialize TRM refinement module.
        
        Args:
            config: Configuration for TRM refinement
        """
        self.config = config or TRMConfig()
        
        # Set random seed for reproducibility
        if self.config.random_seed is not None:
            np.random.seed(self.config.random_seed)
            random.seed(self.config.random_seed)
        
        # Initialize simple MLP weights for refinement (in practice, would use PyTorch/TF)
        self.latent_refine_weights = self._init_weights(
            self.config.latent_dim * 2, self.config.latent_dim
        )
        self.answer_refine_weights = self._init_weights(
            self.config.latent_dim + self.config.answer_dim,
            self.config.answer_dim
        )
        self.halt_weights = self._init_weights(self.config.latent_dim, 1)
        
        # Attention weights if enabled
        if self.config.enable_attention:
            self.attention_weights = self._init_weights(
                self.config.latent_dim, self.config.latent_dim
            )
        
        # Tracking
        self.refinement_history: List[List[RefinementStep]] = []
        self.performance_metrics: Dict[str, Any] = {
            "total_refinements": 0,
            "avg_steps_to_halt": 0.0,
            "halt_accuracy": 0.0,
            "early_halt_count": 0,
            "max_steps_count": 0
        }
        
        logger.info(f"Initialized TRM refinement module with config: {self.config}")
    
    def _init_weights(self, input_dim: int, output_dim: int) -> np.ndarray:
        """Initialize network weights with Xavier initialization."""
        # Xavier/Glorot initialization for better convergence
        limit = np.sqrt(6.0 / (input_dim + output_dim))
        return np.random.uniform(-limit, limit, (input_dim, output_dim))
    
    def refine(
        self,
        initial_state: np.ndarray,
        initial_answer: Optional[np.ndarray] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, np.ndarray, List[RefinementStep]]:
        """
        Perform iterative refinement with learned halting.
        
        Args:
            initial_state: Initial latent state vector (z0)
            initial_answer: Initial answer embedding (y0), if None uses zeros
            context: Optional context for attention mechanism
            
        Returns:
            Tuple of (final_latent_state, final_answer_embedding, refinement_steps)
        """
        # Initialize latent state and answer
        z = initial_state.copy()
        
        if initial_answer is None:
            y = np.zeros(self.config.answer_dim)
        else:
            y = initial_answer.copy()
        
        steps: List[RefinementStep] = []
        total_inner_cycles = 0
        halted = False
        
        # Outer cycles (K steps)
        for outer_step in range(self.config.max_outer_steps):
            # Inner cycles (H refinement steps per outer cycle)
            for inner_step in range(self.config.max_inner_steps):
                total_inner_cycles += 1
                
                # Compute attention if enabled
                if self.config.enable_attention and context:
                    attention_context = self._compute_attention(z, context)
                    z_input = np.concatenate([z, attention_context])
                else:
                    # Self-attention: concatenate z with itself
                    z_input = np.concatenate([z, z])
                
                # Inner refinement: update latent state
                z_delta = self._forward_pass(z_input, self.latent_refine_weights)
                z = z + z_delta  # Residual connection
                
                # Clip gradients (simulate gradient clipping)
                z = np.clip(z, -self.config.gradient_clip, self.config.gradient_clip)
                
                # Compute halting probability
                halt_prob = self._compute_halt_probability(z)
                
                # Compute confidence from state coherence
                confidence = self._compute_confidence(z, y)
                
                # Record step
                step = RefinementStep(
                    step_number=total_inner_cycles,
                    cycle_type='inner',
                    latent_state=z.copy(),
                    answer_embedding=y.copy(),
                    halt_probability=halt_prob,
                    confidence=confidence
                )
                steps.append(step)
                
                # Check halting condition
                if halt_prob > self.config.halt_threshold:
                    halted = True
                    break
            
            if halted:
                break
            
            # Outer cycle: update answer embedding
            zy_input = np.concatenate([y, z])
            y_delta = self._forward_pass(zy_input, self.answer_refine_weights)
            y = y + y_delta  # Residual connection
            
            # Clip gradients
            y = np.clip(y, -self.config.gradient_clip, self.config.gradient_clip)
            
            # Record outer step
            step = RefinementStep(
                step_number=len(steps) + 1,
                cycle_type='outer',
                latent_state=z.copy(),
                answer_embedding=y.copy(),
                halt_probability=halt_prob,
                confidence=confidence
            )
            steps.append(step)
        
        # Update metrics
        self._update_metrics(steps, halted)
        
        # Store history
        self.refinement_history.append(steps)
        
        logger.debug(
            f"Refinement completed in {len(steps)} steps, "
            f"halted={halted}, final_confidence={confidence:.3f}"
        )
        
        return z, y, steps
    
    def _forward_pass(self, x: np.ndarray, weights: np.ndarray) -> np.ndarray:
        """
        Simple forward pass through MLP layer with GELU activation.
        
        Args:
            x: Input vector
            weights: Weight matrix
            
        Returns:
            Output vector after activation
        """
        # Linear transformation
        output = np.dot(x, weights)
        
        # GELU activation (approximate)
        output = 0.5 * output * (1 + np.tanh(
            np.sqrt(2 / np.pi) * (output + 0.044715 * np.power(output, 3))
        ))
        
        return output
    
    def _compute_halt_probability(self, z: np.ndarray) -> float:
        """
        Compute halting probability from latent state.
        
        Args:
            z: Latent state vector
            
        Returns:
            Probability of halting (0-1)
        """
        # Forward pass through halting head
        logit = np.dot(z, self.halt_weights).item()
        
        # Sigmoid activation
        halt_prob = 1.0 / (1.0 + np.exp(-logit))
        
        return float(halt_prob)
    
    def _compute_confidence(self, z: np.ndarray, y: np.ndarray) -> float:
        """
        Compute confidence score from latent state and answer coherence.
        
        Args:
            z: Latent state vector
            y: Answer embedding
            
        Returns:
            Confidence score (0-1)
        """
        # State coherence: inverse of standard deviation (lower std = more coherent)
        state_coherence = 1.0 / (1.0 + np.std(z))
        
        # Answer magnitude (normalized)
        answer_strength = np.linalg.norm(y) / np.sqrt(len(y))
        
        # Combined confidence
        confidence = 0.7 * state_coherence + 0.3 * answer_strength
        
        return float(np.clip(confidence, 0.0, 1.0))
    
    def _compute_attention(
        self,
        z: np.ndarray,
        context: Dict[str, Any]
    ) -> np.ndarray:
        """
        Compute attention over context.
        
        Args:
            z: Current latent state (query)
            context: Context dictionary with attention keys/values
            
        Returns:
            Attention-weighted context vector
        """
        if 'attention_context' not in context:
            # No attention context available, return zero vector
            return np.zeros_like(z)
        
        attention_contexts = context['attention_context']
        
        if not isinstance(attention_contexts, list) or len(attention_contexts) == 0:
            return np.zeros_like(z)
        
        # Compute attention scores
        scores = []
        for ctx_vec in attention_contexts:
            if isinstance(ctx_vec, np.ndarray) and len(ctx_vec) == len(z):
                # Dot product attention
                score = np.dot(z, ctx_vec) / np.sqrt(len(z))
                scores.append(score)
            else:
                scores.append(0.0)
        
        # Softmax normalization
        scores = np.array(scores)
        exp_scores = np.exp(scores - np.max(scores))  # Numerical stability
        attention_weights = exp_scores / np.sum(exp_scores)
        
        # Weighted sum of context vectors
        attended_context = np.zeros_like(z)
        for weight, ctx_vec in zip(attention_weights, attention_contexts):
            if isinstance(ctx_vec, np.ndarray) and len(ctx_vec) == len(z):
                attended_context += weight * ctx_vec
        
        return attended_context
    
    def _update_metrics(self, steps: List[RefinementStep], halted: bool):
        """Update performance metrics."""
        self.performance_metrics["total_refinements"] += 1
        
        # Update average steps to halt
        n = self.performance_metrics["total_refinements"]
        old_avg = self.performance_metrics["avg_steps_to_halt"]
        new_avg = (old_avg * (n - 1) + len(steps)) / n
        self.performance_metrics["avg_steps_to_halt"] = new_avg
        
        # Track early vs max steps halting
        if halted:
            self.performance_metrics["early_halt_count"] += 1
        else:
            self.performance_metrics["max_steps_count"] += 1
        
        # Halt accuracy (percentage of early halts)
        total = self.performance_metrics["total_refinements"]
        early = self.performance_metrics["early_halt_count"]
        self.performance_metrics["halt_accuracy"] = early / total if total > 0 else 0.0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return self.performance_metrics.copy()
    
    def learn_from_feedback(
        self,
        refinement_steps: List[RefinementStep],
        actual_outcome: float,
        target_outcome: float
    ):
        """
        Learn from feedback by adjusting weights.
        
        Args:
            refinement_steps: Steps from a previous refinement
            actual_outcome: Actual outcome achieved
            target_outcome: Target/desired outcome
        """
        # Compute error
        error = target_outcome - actual_outcome
        
        # Simple gradient descent update (in practice would use proper backprop)
        learning_rate = self.config.learning_rate
        
        # Reward early halting if outcome was good
        if abs(error) < 0.1 and len(refinement_steps) < self.config.max_inner_steps:
            # Positive feedback for efficient halting
            for step in refinement_steps:
                if step.halt_probability > 0.5:
                    # Strengthen halt signal
                    self.halt_weights *= (1 + learning_rate * 0.1)
        
        # Penalize early halting if outcome was poor
        elif abs(error) > 0.3 and len(refinement_steps) < self.config.max_inner_steps:
            # Negative feedback for premature halting
            for step in refinement_steps:
                if step.halt_probability > 0.5:
                    # Weaken halt signal
                    self.halt_weights *= (1 - learning_rate * 0.1)
        
        # Clip weights to prevent explosion
        self.halt_weights = np.clip(
            self.halt_weights,
            -self.config.gradient_clip,
            self.config.gradient_clip
        )
        
        logger.debug(f"Applied feedback: error={error:.3f}, steps={len(refinement_steps)}")
    
    def reset_seed(self, seed: Optional[int] = None):
        """Reset random seed for reproducibility."""
        if seed is not None:
            self.config.random_seed = seed
        
        if self.config.random_seed is not None:
            np.random.seed(self.config.random_seed)
            random.seed(self.config.random_seed)
            logger.info(f"Reset random seed to {self.config.random_seed}")


def create_trm_module(
    latent_dim: int = 112,
    answer_dim: int = 64,
    max_inner_steps: int = 5,
    max_outer_steps: int = 3,
    halt_threshold: float = 0.8,
    random_seed: Optional[int] = 42
) -> TRMRefinementModule:
    """
    Factory function to create TRM refinement module.
    
    Args:
        latent_dim: Dimension of latent state
        answer_dim: Dimension of answer embedding
        max_inner_steps: Maximum inner refinement cycles
        max_outer_steps: Maximum outer answer updates
        halt_threshold: Confidence threshold for halting
        random_seed: Random seed for reproducibility
        
    Returns:
        Configured TRMRefinementModule
    """
    config = TRMConfig(
        latent_dim=latent_dim,
        answer_dim=answer_dim,
        max_inner_steps=max_inner_steps,
        max_outer_steps=max_outer_steps,
        halt_threshold=halt_threshold,
        random_seed=random_seed
    )
    
    return TRMRefinementModule(config)
