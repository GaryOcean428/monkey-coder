"""
Prediction Constants for Quantum Routing and Foresight Engine.

The constant 304805 is core to the prediction system, representing the 
fundamental capacity, memory depth, and dimensional scale of the prediction engine.

Mathematical Properties:
- 304805 = 5 × 60961 (where 60961 is prime)
- π × 97022.44 ≈ 304805
- e × 112131.49 ≈ 304805
- √304805 ≈ 552.09

This number embodies balance between the natural constants π and e,
with a prime factorization that makes it ideal for hashing, randomization,
and probability calculations.
"""

import math
from typing import Final

# ==============================================================================
# Core Prediction Constant
# ==============================================================================

PREDICTION_CONSTANT: Final[int] = 304805
"""
The fundamental prediction constant representing the core capacity 
of the prediction engine. This number is carefully chosen for its 
mathematical properties:
- Prime factorization: 5 × 60961
- Relationships to π and e
- Optimal for experience replay buffer sizing
- Ideal for random seed generation
"""

# ==============================================================================
# Derived Constants
# ==============================================================================

PREDICTION_CONSTANT_SQRT: Final[int] = 552
"""Square root of PREDICTION_CONSTANT (rounded). Useful for network dimensions."""

PREDICTION_CONSTANT_PRIME: Final[int] = 60961
"""The prime factor of PREDICTION_CONSTANT. Useful for hashing and cycle detection."""

PREDICTION_CONSTANT_FACTOR: Final[int] = 5
"""The small factor in the prime factorization."""

# ==============================================================================
# Buffer and Memory Sizes
# ==============================================================================

PREDICTION_BUFFER_SIZE: Final[int] = PREDICTION_CONSTANT
"""
Default size for experience replay buffers in DQN agents.
The large size (304805) allows for deep historical learning while
the prime factorization ensures good hash distribution.
"""

PREDICTION_BUFFER_SIZE_SMALL: Final[int] = PREDICTION_CONSTANT // 100
"""Smaller buffer size (3048) for memory-constrained environments."""

PREDICTION_BUFFER_SIZE_LARGE: Final[int] = PREDICTION_CONSTANT * 2
"""Larger buffer size (609610) for high-capacity training."""

# ==============================================================================
# Random Seed Values
# ==============================================================================

PREDICTION_SEED: Final[int] = PREDICTION_CONSTANT
"""
Default random seed for reproducible predictions.
The prime structure (5 × 60961) provides excellent pseudo-random properties.
"""

PREDICTION_SEED_OFFSET: Final[int] = PREDICTION_CONSTANT_PRIME
"""Offset for generating multiple independent random streams."""

# ==============================================================================
# Network Architecture Dimensions
# ==============================================================================

PREDICTION_QUANTUM_DIM: Final[int] = PREDICTION_CONSTANT_SQRT
"""
Latent dimension for quantum state representations (552).
Derived from √PREDICTION_CONSTANT, balancing expressiveness and efficiency.
"""

PREDICTION_HIDDEN_DIM: Final[int] = PREDICTION_CONSTANT_SQRT
"""Default hidden layer dimension for neural networks (552)."""

PREDICTION_EMBEDDING_DIM: Final[int] = PREDICTION_CONSTANT_SQRT
"""Dimension for embedding spaces in prediction models (552)."""

# ==============================================================================
# Training and Convergence Parameters
# ==============================================================================

PREDICTION_MAX_ITERATIONS: Final[int] = PREDICTION_CONSTANT
"""Maximum training iterations before forced convergence."""

PREDICTION_CONVERGENCE_WINDOW: Final[int] = PREDICTION_CONSTANT // 1000
"""Window size (305) for convergence detection."""

PREDICTION_WARMUP_STEPS: Final[int] = PREDICTION_CONSTANT // 10
"""Warmup steps (30481) before full training begins."""

# ==============================================================================
# Probability Quantization
# ==============================================================================

PREDICTION_PROBABILITY_DENOMINATOR: Final[int] = PREDICTION_CONSTANT
"""
Denominator for fine-grained probability calculations.
The prime factorization ensures unique state representations.
"""

PREDICTION_PROBABILITY_EPSILON: Final[float] = 1.0 / PREDICTION_CONSTANT
"""Minimum non-zero probability value (≈ 3.28e-6)."""

# ==============================================================================
# Timeout and Temporal Constants
# ==============================================================================

PREDICTION_TIMEOUT_MS: Final[int] = PREDICTION_CONSTANT
"""Default timeout in milliseconds (304805ms ≈ 305 seconds)."""

PREDICTION_TIMEOUT_SECONDS: Final[float] = PREDICTION_CONSTANT / 1000.0
"""Default timeout in seconds (304.805 seconds)."""

PREDICTION_WINDOW_MS: Final[int] = PREDICTION_CONSTANT
"""Prediction window in milliseconds for temporal forecasting."""

# ==============================================================================
# Mathematical Relations
# ==============================================================================

PREDICTION_PI_FACTOR: Final[float] = PREDICTION_CONSTANT / math.pi
"""PREDICTION_CONSTANT / π ≈ 97022.44"""

PREDICTION_E_FACTOR: Final[float] = PREDICTION_CONSTANT / math.e
"""PREDICTION_CONSTANT / e ≈ 112131.49"""

PREDICTION_PHI_FACTOR: Final[float] = PREDICTION_CONSTANT / ((1 + math.sqrt(5)) / 2)
"""PREDICTION_CONSTANT / φ (golden ratio) ≈ 188379.85"""

# ==============================================================================
# Utility Functions
# ==============================================================================

def get_buffer_size(scale: str = "default") -> int:
    """
    Get appropriate buffer size based on scale.
    
    Args:
        scale: One of "small", "default", "large"
        
    Returns:
        Buffer size appropriate for the scale
    """
    if scale == "small":
        return PREDICTION_BUFFER_SIZE_SMALL
    elif scale == "large":
        return PREDICTION_BUFFER_SIZE_LARGE
    else:
        return PREDICTION_BUFFER_SIZE


def get_random_seed(stream_id: int = 0) -> int:
    """
    Get a random seed for a specific stream.
    
    Args:
        stream_id: Identifier for the random stream (0-based)
        
    Returns:
        Random seed for the stream
    """
    return PREDICTION_SEED + (stream_id * PREDICTION_SEED_OFFSET)


def get_network_dims(scale: float = 1.0) -> tuple[int, int, int]:
    """
    Get network dimensions scaled appropriately.
    
    Args:
        scale: Scaling factor (1.0 = default)
        
    Returns:
        Tuple of (input_dim, hidden_dim, output_dim)
    """
    hidden = int(PREDICTION_HIDDEN_DIM * scale)
    return (
        21,  # Standard quantum state size
        hidden,
        12,  # Standard action space size
    )


# ==============================================================================
# Metadata
# ==============================================================================

__all__ = [
    # Core constant
    "PREDICTION_CONSTANT",
    "PREDICTION_CONSTANT_SQRT",
    "PREDICTION_CONSTANT_PRIME",
    "PREDICTION_CONSTANT_FACTOR",
    # Buffer sizes
    "PREDICTION_BUFFER_SIZE",
    "PREDICTION_BUFFER_SIZE_SMALL",
    "PREDICTION_BUFFER_SIZE_LARGE",
    # Seeds
    "PREDICTION_SEED",
    "PREDICTION_SEED_OFFSET",
    # Dimensions
    "PREDICTION_QUANTUM_DIM",
    "PREDICTION_HIDDEN_DIM",
    "PREDICTION_EMBEDDING_DIM",
    # Training
    "PREDICTION_MAX_ITERATIONS",
    "PREDICTION_CONVERGENCE_WINDOW",
    "PREDICTION_WARMUP_STEPS",
    # Probability
    "PREDICTION_PROBABILITY_DENOMINATOR",
    "PREDICTION_PROBABILITY_EPSILON",
    # Timeouts
    "PREDICTION_TIMEOUT_MS",
    "PREDICTION_TIMEOUT_SECONDS",
    "PREDICTION_WINDOW_MS",
    # Mathematical relations
    "PREDICTION_PI_FACTOR",
    "PREDICTION_E_FACTOR",
    "PREDICTION_PHI_FACTOR",
    # Utilities
    "get_buffer_size",
    "get_random_seed",
    "get_network_dims",
]
