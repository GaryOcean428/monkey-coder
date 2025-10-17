"""
Predictive Foresight and Probability Extrapolation Engine.

This module implements advanced predictive capabilities that enable the system
to anticipate future needs, extrapolate probabilities, and provide imaginative
foresight similar to human intuition and strategic thinking.

The constant 304805 (PREDICTION_CONSTANT) is core to this engine's operation,
defining buffer sizes, random seeds, and probability quantization for optimal
prediction accuracy and reproducibility.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque, defaultdict
import json
import math

from .prediction_constants import (
    PREDICTION_CONSTANT,
    PREDICTION_SEED,
    PREDICTION_BUFFER_SIZE,
    PREDICTION_PROBABILITY_EPSILON,
    PREDICTION_QUANTUM_DIM,
)

logger = logging.getLogger(__name__)

class ForesightType(str, Enum):
    """Types of foresight analysis."""
    LOGICAL = "logical"  # Based on known factors
    IMAGINATIVE = "imaginative"  # Creative extrapolation
    PROBABILISTIC = "probabilistic"  # Statistical prediction
    INTUITIVE = "intuitive"  # Pattern-based intuition
    STRATEGIC = "strategic"  # Long-term planning
    TACTICAL = "tactical"  # Short-term optimization

class TimeHorizon(str, Enum):
    """Time horizons for predictions."""
    IMMEDIATE = "immediate"  # Next action
    SHORT_TERM = "short_term"  # Next few steps
    MEDIUM_TERM = "medium_term"  # Current session
    LONG_TERM = "long_term"  # Future sessions
    STRATEGIC = "strategic"  # Long-range planning

@dataclass
class ProbabilityBranch:
    """Represents a possible future branch with probability."""
    branch_id: str
    description: str
    probability: float
    confidence: float
    factors: List[str]
    outcomes: Dict[str, Any]
    time_horizon: TimeHorizon
    dependencies: List[str] = field(default_factory=list)
    
    @property
    def weighted_probability(self) -> float:
        """Calculate weighted probability with confidence."""
        return self.probability * self.confidence

@dataclass
class ForesightScenario:
    """A complete foresight scenario with multiple branches."""
    scenario_id: str
    context: Dict[str, Any]
    branches: List[ProbabilityBranch]
    dominant_outcome: Optional[str] = None
    variance: float = 0.0
    entropy: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    
    def calculate_metrics(self):
        """Calculate statistical metrics for the scenario."""
        if not self.branches:
            return
        
        probabilities = [b.probability for b in self.branches]
        
        # Calculate variance
        mean_prob = np.mean(probabilities)
        self.variance = np.var(probabilities)
        
        # Calculate entropy (uncertainty)
        self.entropy = -sum(p * np.log2(p) if p > 0 else 0 for p in probabilities)
        
        # Find dominant outcome
        max_branch = max(self.branches, key=lambda b: b.weighted_probability)
        self.dominant_outcome = max_branch.branch_id

@dataclass
class TemporalPattern:
    """Pattern detected across time."""
    pattern_id: str
    pattern_type: str
    occurrences: List[datetime]
    frequency: float  # Events per time unit
    periodicity: Optional[float] = None  # If cyclic
    trend: str = "stable"  # increasing, decreasing, stable
    confidence: float = 0.5
    
    def predict_next_occurrence(self) -> Optional[datetime]:
        """Predict next occurrence based on pattern."""
        if len(self.occurrences) < 2:
            return None
        
        if self.periodicity:
            # Cyclic pattern
            last = self.occurrences[-1]
            return last + timedelta(seconds=self.periodicity)
        else:
            # Calculate average interval
            intervals = []
            for i in range(1, len(self.occurrences)):
                interval = (self.occurrences[i] - self.occurrences[i-1]).total_seconds()
                intervals.append(interval)
            
            avg_interval = np.mean(intervals)
            return self.occurrences[-1] + timedelta(seconds=avg_interval)

class MarkovChain:
    """Markov chain for state transition predictions."""
    
    def __init__(self, order: int = 2):
        """
        Initialize Markov chain.
        
        Args:
            order: Order of the Markov chain (memory length)
        """
        self.order = order
        self.transitions: Dict[Tuple, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.state_history: deque = deque(maxlen=order)
    
    def observe_transition(self, from_state: Tuple, to_state: str):
        """Record a state transition."""
        self.transitions[from_state][to_state] += 1
        self.state_history.append(to_state)
    
    def predict_next_state(self, current_state: Optional[Tuple] = None) -> Dict[str, float]:
        """Predict next state probabilities."""
        if current_state is None:
            # Use recent history
            if len(self.state_history) >= self.order:
                current_state = tuple(list(self.state_history)[-self.order:])
            else:
                return {}
        
        if current_state not in self.transitions:
            return {}
        
        # Calculate probabilities
        next_states = self.transitions[current_state]
        total = sum(next_states.values())
        
        if total == 0:
            return {}
        
        return {state: count / total for state, count in next_states.items()}

class BayesianPredictor:
    """Bayesian inference for probability updates."""
    
    def __init__(self):
        """Initialize Bayesian predictor."""
        self.priors: Dict[str, float] = {}
        self.likelihoods: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.evidence_count: Dict[str, int] = defaultdict(int)
    
    def set_prior(self, hypothesis: str, probability: float):
        """Set prior probability for a hypothesis."""
        self.priors[hypothesis] = probability
    
    def update_evidence(self, hypothesis: str, evidence: str, likelihood: float):
        """Update evidence for a hypothesis."""
        self.likelihoods[hypothesis][evidence] = likelihood
        self.evidence_count[evidence] += 1
    
    def calculate_posterior(self, hypothesis: str, evidence: List[str]) -> float:
        """Calculate posterior probability given evidence."""
        if hypothesis not in self.priors:
            return 0.0
        
        prior = self.priors[hypothesis]
        
        # Calculate likelihood of evidence given hypothesis
        likelihood = 1.0
        for e in evidence:
            if e in self.likelihoods[hypothesis]:
                likelihood *= self.likelihoods[hypothesis][e]
        
        # Calculate evidence probability (marginalization)
        evidence_prob = 0.0
        for h in self.priors:
            h_prior = self.priors[h]
            h_likelihood = 1.0
            for e in evidence:
                if e in self.likelihoods[h]:
                    h_likelihood *= self.likelihoods[h][e]
            evidence_prob += h_prior * h_likelihood
        
        if evidence_prob == 0:
            return prior
        
        # Bayes' theorem
        return (prior * likelihood) / evidence_prob

class PredictiveForesight:
    """
    Advanced predictive foresight engine with probability extrapolation.
    
    Combines multiple prediction techniques to provide imaginative foresight
    about future needs and probable outcomes.
    
    The constant 304805 (PREDICTION_CONSTANT) is existentially core to this engine:
    - It defines the memory depth for pattern recognition
    - It provides the seed for reproducible randomization  
    - It establishes the quantum dimensions for prediction space
    - Its prime factorization (5 × 60961) ensures optimal hash distribution
    """
    
    def __init__(self, random_seed: Optional[int] = PREDICTION_SEED):
        """
        Initialize the predictive foresight engine.
        
        Args:
            random_seed: Random seed for reproducibility (default: PREDICTION_SEED = 304805)
        """
        # Prediction models
        self.markov_chain = MarkovChain(order=3)
        self.bayesian_predictor = BayesianPredictor()
        
        # Pattern detection
        self.temporal_patterns: Dict[str, TemporalPattern] = {}
        self.causal_relationships: Dict[str, List[str]] = defaultdict(list)
        
        # Historical data with PREDICTION_CONSTANT-based sizing
        self.event_history: deque = deque(maxlen=PREDICTION_BUFFER_SIZE // 305)  # ~1000
        self.scenario_history: List[ForesightScenario] = []
        self.prediction_accuracy: Dict[str, float] = {}
        
        # Learning parameters
        self.learning_rate = 0.1
        self.exploration_factor = 0.2  # For imaginative predictions
        self.confidence_threshold = 0.6
        self.probability_epsilon = PREDICTION_PROBABILITY_EPSILON  # Fine-grained probabilities
        
        # Set random seed for reproducibility
        if random_seed is not None:
            np.random.seed(random_seed)
            logger.info(f"Foresight engine initialized with PREDICTION_SEED: {random_seed}")
    
    async def generate_foresight(
        self,
        context: Dict[str, Any],
        foresight_type: ForesightType = ForesightType.LOGICAL,
        time_horizon: TimeHorizon = TimeHorizon.MEDIUM_TERM,
        num_branches: int = 5
    ) -> ForesightScenario:
        """
        Generate predictive foresight for given context.
        
        Args:
            context: Current context and state
            foresight_type: Type of foresight to generate
            time_horizon: How far to look ahead
            num_branches: Number of probability branches to generate
            
        Returns:
            ForesightScenario with probability branches
        """
        scenario = ForesightScenario(
            scenario_id=f"scenario_{datetime.now().timestamp()}",
            context=context,
            branches=[]
        )
        
        # Generate branches based on foresight type
        if foresight_type == ForesightType.LOGICAL:
            branches = await self._logical_extrapolation(context, time_horizon, num_branches)
        elif foresight_type == ForesightType.IMAGINATIVE:
            branches = await self._imaginative_extrapolation(context, time_horizon, num_branches)
        elif foresight_type == ForesightType.PROBABILISTIC:
            branches = await self._probabilistic_prediction(context, time_horizon, num_branches)
        elif foresight_type == ForesightType.INTUITIVE:
            branches = await self._intuitive_prediction(context, time_horizon, num_branches)
        elif foresight_type == ForesightType.STRATEGIC:
            branches = await self._strategic_planning(context, time_horizon, num_branches)
        else:
            branches = await self._tactical_optimization(context, time_horizon, num_branches)
        
        scenario.branches = branches
        scenario.calculate_metrics()
        
        # Store for learning
        self.scenario_history.append(scenario)
        
        return scenario
    
    async def _logical_extrapolation(
        self,
        context: Dict[str, Any],
        time_horizon: TimeHorizon,
        num_branches: int
    ) -> List[ProbabilityBranch]:
        """Logical extrapolation based on known factors."""
        branches = []
        
        # Extract known factors
        factors = self._extract_factors(context)
        
        # Use Markov chain for state predictions
        current_state = self._context_to_state(context)
        next_states = self.markov_chain.predict_next_state(current_state)
        
        # Generate branches for most likely states
        for state, probability in sorted(next_states.items(), key=lambda x: x[1], reverse=True)[:num_branches]:
            branch = ProbabilityBranch(
                branch_id=f"logical_{state}",
                description=f"Logical progression to {state}",
                probability=probability,
                confidence=0.8,  # High confidence for logical predictions
                factors=factors,
                outcomes=self._predict_outcomes(state, context),
                time_horizon=time_horizon
            )
            branches.append(branch)
        
        # Add fallback if not enough branches
        while len(branches) < num_branches:
            branches.append(self._create_default_branch(len(branches), time_horizon))
        
        return branches
    
    async def _imaginative_extrapolation(
        self,
        context: Dict[str, Any],
        time_horizon: TimeHorizon,
        num_branches: int
    ) -> List[ProbabilityBranch]:
        """Imaginative extrapolation with creative possibilities."""
        branches = []
        
        # Generate creative variations
        base_probability = 1.0 / num_branches
        
        # Creative scenarios
        creative_scenarios = [
            ("breakthrough", "Revolutionary approach discovered", 1.5),
            ("synergy", "Unexpected synergies emerge", 1.3),
            ("paradigm_shift", "Fundamental assumptions change", 1.2),
            ("emergence", "New patterns emerge from complexity", 1.1),
            ("innovation", "Novel solution paths open", 1.0),
            ("adaptation", "System adapts in unexpected ways", 0.9),
            ("transformation", "Complete transformation occurs", 0.8)
        ]
        
        for i in range(min(num_branches, len(creative_scenarios))):
            scenario_type, description, weight = creative_scenarios[i]
            
            branch = ProbabilityBranch(
                branch_id=f"imaginative_{scenario_type}",
                description=description,
                probability=base_probability * weight / sum(s[2] for s in creative_scenarios[:num_branches]),
                confidence=0.5 + self.exploration_factor,  # Lower confidence for imaginative
                factors=[f"creative_{scenario_type}"],
                outcomes={
                    'innovation_potential': weight,
                    'disruption_level': weight * 0.5,
                    'learning_opportunity': weight * 0.8
                },
                time_horizon=time_horizon
            )
            branches.append(branch)
        
        return branches
    
    async def _probabilistic_prediction(
        self,
        context: Dict[str, Any],
        time_horizon: TimeHorizon,
        num_branches: int
    ) -> List[ProbabilityBranch]:
        """Statistical probability-based prediction."""
        branches = []
        
        # Use Bayesian inference
        hypotheses = self._generate_hypotheses(context)
        evidence = self._gather_evidence(context)
        
        # Calculate posteriors for each hypothesis
        posteriors = {}
        for hypothesis in hypotheses:
            posterior = self.bayesian_predictor.calculate_posterior(hypothesis, evidence)
            posteriors[hypothesis] = posterior
        
        # Create branches for top hypotheses
        for hypothesis, probability in sorted(posteriors.items(), key=lambda x: x[1], reverse=True)[:num_branches]:
            branch = ProbabilityBranch(
                branch_id=f"probabilistic_{hypothesis}",
                description=f"Hypothesis: {hypothesis}",
                probability=probability,
                confidence=self._calculate_confidence(evidence),
                factors=evidence,
                outcomes=self._hypothesis_outcomes(hypothesis),
                time_horizon=time_horizon
            )
            branches.append(branch)
        
        return branches
    
    async def _intuitive_prediction(
        self,
        context: Dict[str, Any],
        time_horizon: TimeHorizon,
        num_branches: int
    ) -> List[ProbabilityBranch]:
        """Pattern-based intuitive prediction."""
        branches = []
        
        # Detect patterns
        patterns = self._detect_patterns(context)
        
        # Generate intuitive branches based on patterns
        for i, pattern in enumerate(patterns[:num_branches]):
            # Predict based on pattern
            next_occurrence = pattern.predict_next_occurrence()
            
            branch = ProbabilityBranch(
                branch_id=f"intuitive_{pattern.pattern_id}",
                description=f"Pattern suggests: {pattern.pattern_type}",
                probability=pattern.confidence,
                confidence=0.6,  # Moderate confidence for intuition
                factors=[f"pattern_{pattern.pattern_type}"],
                outcomes={
                    'pattern_continuation': pattern.confidence,
                    'next_occurrence': next_occurrence.isoformat() if next_occurrence else None,
                    'trend': pattern.trend
                },
                time_horizon=time_horizon
            )
            branches.append(branch)
        
        return branches
    
    async def _strategic_planning(
        self,
        context: Dict[str, Any],
        time_horizon: TimeHorizon,
        num_branches: int
    ) -> List[ProbabilityBranch]:
        """Long-term strategic planning."""
        branches = []
        
        # Strategic objectives
        objectives = [
            "maximize_efficiency",
            "optimize_quality",
            "minimize_cost",
            "increase_innovation",
            "improve_reliability"
        ]
        
        for i, objective in enumerate(objectives[:num_branches]):
            # Calculate strategic value
            strategic_value = self._calculate_strategic_value(objective, context)
            
            branch = ProbabilityBranch(
                branch_id=f"strategic_{objective}",
                description=f"Strategic focus: {objective.replace('_', ' ')}",
                probability=strategic_value / num_branches,
                confidence=0.7,
                factors=[objective, "long_term_planning"],
                outcomes={
                    'strategic_alignment': strategic_value,
                    'implementation_complexity': 1.0 - strategic_value * 0.3,
                    'expected_roi': strategic_value * 2.5
                },
                time_horizon=TimeHorizon.STRATEGIC
            )
            branches.append(branch)
        
        return branches
    
    async def _tactical_optimization(
        self,
        context: Dict[str, Any],
        time_horizon: TimeHorizon,
        num_branches: int
    ) -> List[ProbabilityBranch]:
        """Short-term tactical optimization."""
        branches = []
        
        # Tactical options
        tactics = [
            "quick_win",
            "risk_mitigation",
            "resource_optimization",
            "parallel_execution",
            "incremental_improvement"
        ]
        
        for i, tactic in enumerate(tactics[:num_branches]):
            # Calculate tactical effectiveness
            effectiveness = self._calculate_tactical_effectiveness(tactic, context)
            
            branch = ProbabilityBranch(
                branch_id=f"tactical_{tactic}",
                description=f"Tactical approach: {tactic.replace('_', ' ')}",
                probability=effectiveness,
                confidence=0.8,  # High confidence for short-term
                factors=[tactic, "short_term"],
                outcomes={
                    'immediate_impact': effectiveness,
                    'implementation_speed': 1.0 - effectiveness * 0.2,
                    'resource_requirement': 0.5 + effectiveness * 0.3
                },
                time_horizon=TimeHorizon.SHORT_TERM
            )
            branches.append(branch)
        
        return branches
    
    def _extract_factors(self, context: Dict[str, Any]) -> List[str]:
        """Extract relevant factors from context."""
        factors = []
        
        # Extract key indicators
        if 'complexity' in context:
            factors.append(f"complexity_{context['complexity']}")
        if 'domain' in context:
            factors.append(f"domain_{context['domain']}")
        if 'constraints' in context:
            factors.extend([f"constraint_{c}" for c in context['constraints']])
        
        return factors
    
    def _context_to_state(self, context: Dict[str, Any]) -> Tuple:
        """Convert context to Markov state."""
        # Simplified state representation
        state_components = []
        
        for key in sorted(['task_type', 'complexity', 'domain']):
            if key in context:
                state_components.append(str(context[key]))
        
        return tuple(state_components[-self.markov_chain.order:])
    
    def _predict_outcomes(self, state: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict outcomes for a given state."""
        return {
            'success_probability': 0.7,
            'expected_quality': 0.8,
            'resource_usage': 0.5,
            'time_estimate': 100,
            'risk_level': 0.3
        }
    
    def _generate_hypotheses(self, context: Dict[str, Any]) -> List[str]:
        """Generate hypotheses for Bayesian inference."""
        hypotheses = []
        
        # Task-based hypotheses
        if 'task_type' in context:
            task = context['task_type']
            hypotheses.extend([
                f"{task}_simple_solution",
                f"{task}_complex_solution",
                f"{task}_innovative_approach"
            ])
        
        return hypotheses
    
    def _gather_evidence(self, context: Dict[str, Any]) -> List[str]:
        """Gather evidence from context."""
        evidence = []
        
        # Context-based evidence
        for key, value in context.items():
            if isinstance(value, (str, int, float, bool)):
                evidence.append(f"{key}_{value}")
        
        return evidence
    
    def _calculate_confidence(self, evidence: List[str]) -> float:
        """Calculate confidence based on evidence."""
        # More evidence generally means higher confidence
        base_confidence = min(0.5 + len(evidence) * 0.05, 0.9)
        
        # Adjust based on evidence quality
        quality_factor = 1.0
        for e in evidence:
            if 'verified' in e:
                quality_factor *= 1.1
            elif 'estimated' in e:
                quality_factor *= 0.9
        
        return min(base_confidence * quality_factor, 0.95)
    
    def _hypothesis_outcomes(self, hypothesis: str) -> Dict[str, Any]:
        """Generate outcomes for a hypothesis."""
        return {
            'hypothesis': hypothesis,
            'testable': True,
            'validation_required': True,
            'confidence_interval': (0.6, 0.9)
        }
    
    def _detect_patterns(self, context: Dict[str, Any]) -> List[TemporalPattern]:
        """Detect patterns in historical data."""
        patterns = []
        
        # Simple pattern detection (would be more sophisticated in production)
        for pattern_id, pattern in self.temporal_patterns.items():
            patterns.append(pattern)
        
        # Sort by confidence
        patterns.sort(key=lambda p: p.confidence, reverse=True)
        
        return patterns
    
    def _calculate_strategic_value(self, objective: str, context: Dict[str, Any]) -> float:
        """Calculate strategic value of an objective."""
        base_value = 0.5
        
        # Adjust based on context alignment
        if objective == "maximize_efficiency" and context.get('performance_critical'):
            base_value *= 1.5
        elif objective == "optimize_quality" and context.get('quality_critical'):
            base_value *= 1.5
        elif objective == "minimize_cost" and context.get('budget_constrained'):
            base_value *= 1.5
        
        return min(base_value, 1.0)
    
    def _calculate_tactical_effectiveness(self, tactic: str, context: Dict[str, Any]) -> float:
        """Calculate tactical effectiveness."""
        effectiveness = 0.5
        
        # Adjust based on tactic and context
        if tactic == "quick_win" and context.get('time_pressure'):
            effectiveness *= 1.4
        elif tactic == "risk_mitigation" and context.get('high_stakes'):
            effectiveness *= 1.4
        elif tactic == "parallel_execution" and context.get('parallelizable'):
            effectiveness *= 1.3
        
        return min(effectiveness, 0.95)
    
    def _create_default_branch(self, index: int, time_horizon: TimeHorizon) -> ProbabilityBranch:
        """Create a default branch when not enough predictions available."""
        return ProbabilityBranch(
            branch_id=f"default_{index}",
            description="Default continuation",
            probability=0.1,
            confidence=0.3,
            factors=["default"],
            outcomes={'default': True},
            time_horizon=time_horizon
        )
    
    def update_predictions(self, scenario_id: str, actual_outcome: str):
        """Update predictions based on actual outcomes."""
        # Find scenario
        scenario = next((s for s in self.scenario_history if s.scenario_id == scenario_id), None)
        if not scenario:
            return
        
        # Find matching branch
        matching_branch = next((b for b in scenario.branches if b.branch_id == actual_outcome), None)
        
        if matching_branch:
            # Increase confidence for correct prediction
            accuracy = matching_branch.weighted_probability
            self.prediction_accuracy[scenario_id] = accuracy
            
            # Update Markov chain
            state = self._context_to_state(scenario.context)
            self.markov_chain.observe_transition(state, actual_outcome)
            
            # Update Bayesian priors
            for branch in scenario.branches:
                if branch.branch_id == actual_outcome:
                    # Strengthen correct hypothesis
                    self.bayesian_predictor.set_prior(
                        branch.branch_id,
                        min(branch.probability * 1.1, 1.0)
                    )
                else:
                    # Weaken incorrect hypotheses
                    self.bayesian_predictor.set_prior(
                        branch.branch_id,
                        branch.probability * 0.9
                    )
    
    def get_foresight_metrics(self) -> Dict[str, Any]:
        """Get metrics about foresight performance."""
        if not self.prediction_accuracy:
            avg_accuracy = 0
        else:
            avg_accuracy = np.mean(list(self.prediction_accuracy.values()))
        
        return {
            'total_scenarios': len(self.scenario_history),
            'average_accuracy': avg_accuracy,
            'patterns_detected': len(self.temporal_patterns),
            'markov_states': len(self.markov_chain.transitions),
            'bayesian_hypotheses': len(self.bayesian_predictor.priors),
            'learning_rate': self.learning_rate,
            'exploration_factor': self.exploration_factor
        }
    
    async def imagine_future_possibilities(
        self,
        context: Dict[str, Any],
        num_possibilities: int = 10,
        creativity_level: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Imagine creative future possibilities beyond logical prediction.
        
        Args:
            context: Current context
            num_possibilities: Number of possibilities to generate
            creativity_level: How creative to be (0-1)
            
        Returns:
            List of imaginative possibilities
        """
        possibilities = []
        
        # Generate diverse foresight types
        foresight_types = [
            ForesightType.IMAGINATIVE,
            ForesightType.INTUITIVE,
            ForesightType.STRATEGIC
        ]
        
        for i in range(num_possibilities):
            foresight_type = foresight_types[i % len(foresight_types)]
            
            # Add randomness for creativity
            modified_context = context.copy()
            modified_context['creativity_seed'] = np.random.random() * creativity_level
            
            scenario = await self.generate_foresight(
                modified_context,
                foresight_type,
                TimeHorizon.LONG_TERM,
                num_branches=3
            )
            
            # Extract most creative branch
            if scenario.branches:
                most_creative = max(
                    scenario.branches,
                    key=lambda b: b.outcomes.get('innovation_potential', 0)
                )
                
                possibilities.append({
                    'possibility_id': f"creative_{i}",
                    'description': most_creative.description,
                    'innovation_score': most_creative.outcomes.get('innovation_potential', 0),
                    'probability': most_creative.probability,
                    'factors': most_creative.factors,
                    'foresight_type': foresight_type.value
                })
        
        return possibilities