"""
Q-Learning implementation for intelligent AI model and strategy routing.

This module implements Q-learning algorithms that learn optimal routing decisions
based on task characteristics, model performance, and cost efficiency.
"""

import json
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import asyncio
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class State:
    """Represents the state for Q-learning decision making."""
    task_type: str  # code_generation, analysis, testing, etc.
    complexity: float  # 0.0 to 1.0
    domain: str  # frontend, backend, infrastructure, etc.
    persona: str  # developer, architect, reviewer, etc.
    context_size: int  # Number of tokens in context
    urgency: float  # 0.0 to 1.0 (time sensitivity)
    quality_requirement: float  # 0.0 to 1.0 (quality vs speed tradeoff)
    
    def to_tuple(self) -> tuple:
        """Convert state to hashable tuple for Q-table indexing."""
        return (
            self.task_type,
            round(self.complexity, 1),  # Discretize to 0.1 intervals
            self.domain,
            self.persona,
            min(self.context_size // 1000, 32),  # Bucket by thousands up to 32k
            round(self.urgency, 1),
            round(self.quality_requirement, 1)
        )
    
    def to_vector(self) -> np.ndarray:
        """Convert state to numerical vector for neural network."""
        # One-hot encode categorical features
        task_types = ['code_generation', 'analysis', 'testing', 'custom', 'documentation']
        domains = ['frontend', 'backend', 'infrastructure', 'security', 'general']
        personas = ['developer', 'architect', 'reviewer', 'tester', 'analyst']
        
        vector = []
        
        # One-hot task type
        for t in task_types:
            vector.append(1.0 if self.task_type == t else 0.0)
        
        # One-hot domain
        for d in domains:
            vector.append(1.0 if self.domain == d else 0.0)
        
        # One-hot persona
        for p in personas:
            vector.append(1.0 if self.persona == p else 0.0)
        
        # Continuous features (normalized)
        vector.extend([
            self.complexity,
            min(self.context_size / 32000, 1.0),  # Normalize to 32k max
            self.urgency,
            self.quality_requirement
        ])
        
        return np.array(vector, dtype=np.float32)

@dataclass
class Action:
    """Represents an action (routing decision) in Q-learning."""
    provider: str  # openai, anthropic, google, groq, xai
    model: str  # Specific model name
    strategy: str  # sequential, parallel, quantum, hybrid
    temperature: float  # 0.0 to 1.0
    max_tokens: int  # Token limit for response
    
    def to_tuple(self) -> tuple:
        """Convert action to hashable tuple."""
        return (
            self.provider,
            self.model,
            self.strategy,
            round(self.temperature, 1),
            self.max_tokens
        )
    
    def to_index(self) -> int:
        """Convert action to discrete index for Q-table."""
        # Map to discrete action space
        providers = ['openai', 'anthropic', 'google', 'groq', 'xai']
        strategies = ['sequential', 'parallel', 'quantum', 'hybrid']
        
        provider_idx = providers.index(self.provider) if self.provider in providers else 0
        strategy_idx = strategies.index(self.strategy) if self.strategy in strategies else 0
        temp_idx = int(self.temperature * 10)  # 0-10
        token_idx = min(self.max_tokens // 1000, 8)  # 0-8 (up to 8k)
        
        # Combine into single index (5 * 4 * 11 * 9 = 1980 possible actions)
        index = (provider_idx * 4 * 11 * 9 +
                strategy_idx * 11 * 9 +
                temp_idx * 9 +
                token_idx)
        
        return index

@dataclass
class Experience:
    """Represents an experience tuple for learning."""
    state: State
    action: Action
    reward: float
    next_state: Optional[State]
    done: bool
    metadata: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class QLearningRouter:
    """Q-Learning based routing engine for model and strategy selection."""
    
    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
        save_path: Optional[str] = None
    ):
        """Initialize Q-learning router."""
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        # Q-table for tabular Q-learning
        self.q_table: Dict[tuple, Dict[tuple, float]] = defaultdict(lambda: defaultdict(float))
        
        # Experience replay buffer for batch learning
        self.experience_buffer: List[Experience] = []
        self.max_buffer_size = 10000
        
        # Performance tracking
        self.episode_rewards: List[float] = []
        self.success_rate_history: List[float] = []
        
        # Save/load path
        self.save_path = Path(save_path) if save_path else Path("data/q_learning/q_table.json")
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Action space definition
        self.action_space = self._build_action_space()
        
        # Load existing Q-table if available
        self.load_q_table()
    
    def _build_action_space(self) -> List[Action]:
        """Build the discrete action space."""
        actions = []
        
        # Define provider-model combinations
        provider_models = {
            'openai': ['gpt-4-turbo-preview', 'gpt-3.5-turbo'],
            'anthropic': ['claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022'],
            'google': ['gemini-2.5-pro', 'gemini-2.5-flash'],
            'groq': ['llama-3.1-8b-instant', 'llama-3.3-70b-versatile'],
            'xai': ['grok-4-latest', 'grok-3']
        }
        
        strategies = ['sequential', 'parallel', 'quantum', 'hybrid']
        temperatures = [0.0, 0.3, 0.7, 1.0]
        max_tokens = [1000, 2000, 4000, 8000]
        
        for provider, models in provider_models.items():
            for model in models:
                for strategy in strategies:
                    for temp in temperatures:
                        for tokens in max_tokens:
                            actions.append(Action(
                                provider=provider,
                                model=model,
                                strategy=strategy,
                                temperature=temp,
                                max_tokens=tokens
                            ))
        
        return actions
    
    def get_q_value(self, state: State, action: Action) -> float:
        """Get Q-value for state-action pair."""
        state_key = state.to_tuple()
        action_key = action.to_tuple()
        return self.q_table[state_key][action_key]
    
    def set_q_value(self, state: State, action: Action, value: float):
        """Set Q-value for state-action pair."""
        state_key = state.to_tuple()
        action_key = action.to_tuple()
        self.q_table[state_key][action_key] = value
    
    def select_action(self, state: State, explore: bool = True) -> Action:
        """
        Select action using epsilon-greedy strategy.
        
        Args:
            state: Current state
            explore: Whether to use exploration (training) or exploitation (inference)
        
        Returns:
            Selected action
        """
        # Epsilon-greedy exploration
        if explore and np.random.random() < self.epsilon:
            # Random exploration
            return np.random.choice(self.action_space)
        
        # Exploitation: choose best action based on Q-values
        state_key = state.to_tuple()
        
        if state_key not in self.q_table or not self.q_table[state_key]:
            # No knowledge about this state, choose based on heuristics
            return self._heuristic_action_selection(state)
        
        # Get action with maximum Q-value
        best_action_key = max(
            self.q_table[state_key].items(),
            key=lambda x: x[1]
        )[0]
        
        # Reconstruct action from tuple
        provider, model, strategy, temp, tokens = best_action_key
        return Action(
            provider=provider,
            model=model,
            strategy=strategy,
            temperature=temp,
            max_tokens=tokens
        )
    
    def _heuristic_action_selection(self, state: State) -> Action:
        """Use heuristics for initial action selection."""
        # Default heuristics based on task characteristics
        
        # High complexity tasks -> stronger models
        if state.complexity > 0.7:
            provider = 'openai'
            model = 'gpt-4-turbo-preview'
            strategy = 'quantum' if state.complexity > 0.8 else 'hybrid'
        elif state.complexity > 0.4:
            provider = 'anthropic'
            model = 'claude-3-5-sonnet-20241022'
            strategy = 'sequential'
        else:
            provider = 'groq'
            model = 'llama-3.1-8b-instant'
            strategy = 'sequential'
        
        # Quality vs speed tradeoff
        if state.quality_requirement > 0.7:
            temperature = 0.1
            max_tokens = 4000
        else:
            temperature = 0.3
            max_tokens = 2000
        
        return Action(
            provider=provider,
            model=model,
            strategy=strategy,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def calculate_reward(
        self,
        state: State,
        action: Action,
        result: Dict[str, Any]
    ) -> float:
        """
        Calculate reward based on execution results.
        
        Args:
            state: Initial state
            action: Action taken
            result: Execution result containing metrics
        
        Returns:
            Reward value
        """
        reward = 0.0
        
        # Success/failure base reward
        if result.get('success', False):
            reward += 10.0
        else:
            reward -= 20.0
            return reward  # Early return for failures
        
        # Quality score component (0-5 points)
        quality_score = result.get('quality_score', 0.5)
        reward += quality_score * 5.0
        
        # Cost efficiency component (0-5 points)
        # Lower cost is better
        cost = result.get('cost', 0.01)
        cost_efficiency = max(0, 5.0 - cost * 100)  # Assuming $0.05 is expensive
        reward += cost_efficiency
        
        # Speed component (0-3 points)
        # Faster is better
        execution_time = result.get('execution_time', 10.0)
        speed_bonus = max(0, 3.0 - execution_time / 5.0)  # 5 seconds is slow
        reward += speed_bonus
        
        # Token efficiency (0-2 points)
        tokens_used = result.get('tokens_used', 1000)
        token_efficiency = max(0, 2.0 - tokens_used / 4000)  # 4000 tokens is high
        reward += token_efficiency
        
        # User feedback if available (±5 points)
        user_rating = result.get('user_rating')
        if user_rating is not None:
            reward += (user_rating - 3) * 2.5  # Centered at 3/5 stars
        
        # Penalty for inappropriate model selection
        if state.urgency > 0.7 and execution_time > 5.0:
            reward -= 3.0  # Penalty for slow response when urgent
        
        if state.quality_requirement > 0.7 and quality_score < 0.7:
            reward -= 5.0  # Penalty for low quality when required
        
        return reward
    
    def update_q_value(
        self,
        state: State,
        action: Action,
        reward: float,
        next_state: Optional[State] = None
    ):
        """
        Update Q-value using Q-learning update rule.
        
        Q(s,a) = Q(s,a) + α * [r + γ * max(Q(s',a')) - Q(s,a)]
        """
        current_q = self.get_q_value(state, action)
        
        if next_state is None:
            # Terminal state
            target = reward
        else:
            # Get maximum Q-value for next state
            next_state_key = next_state.to_tuple()
            if next_state_key in self.q_table and self.q_table[next_state_key]:
                max_next_q = max(self.q_table[next_state_key].values())
            else:
                max_next_q = 0.0
            
            target = reward + self.discount_factor * max_next_q
        
        # Q-learning update
        new_q = current_q + self.learning_rate * (target - current_q)
        self.set_q_value(state, action, new_q)
    
    def add_experience(
        self,
        state: State,
        action: Action,
        reward: float,
        next_state: Optional[State],
        done: bool,
        metadata: Dict[str, Any]
    ):
        """Add experience to replay buffer."""
        experience = Experience(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done,
            metadata=metadata
        )
        
        self.experience_buffer.append(experience)
        
        # Maintain buffer size
        if len(self.experience_buffer) > self.max_buffer_size:
            self.experience_buffer.pop(0)
    
    def learn_from_experience(self, batch_size: int = 32):
        """Learn from batch of experiences (experience replay)."""
        if len(self.experience_buffer) < batch_size:
            return
        
        # Sample random batch
        batch_indices = np.random.choice(
            len(self.experience_buffer),
            size=batch_size,
            replace=False
        )
        
        for idx in batch_indices:
            exp = self.experience_buffer[idx]
            self.update_q_value(
                exp.state,
                exp.action,
                exp.reward,
                exp.next_state
            )
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def save_q_table(self):
        """Save Q-table to disk."""
        try:
            # Convert Q-table to serializable format
            q_table_dict = {}
            for state_key, actions in self.q_table.items():
                state_str = json.dumps(state_key)
                q_table_dict[state_str] = {}
                for action_key, value in actions.items():
                    action_str = json.dumps(action_key)
                    q_table_dict[state_str][action_str] = value
            
            # Save with metadata
            save_data = {
                'q_table': q_table_dict,
                'epsilon': self.epsilon,
                'episode_count': len(self.episode_rewards),
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.save_path, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            logger.info(f"Q-table saved to {self.save_path}")
            
        except Exception as e:
            logger.error(f"Failed to save Q-table: {e}")
    
    def load_q_table(self):
        """Load Q-table from disk."""
        if not self.save_path.exists():
            logger.info("No saved Q-table found, starting fresh")
            return
        
        try:
            with open(self.save_path, 'r') as f:
                save_data = json.load(f)
            
            # Restore Q-table
            q_table_dict = save_data.get('q_table', {})
            for state_str, actions in q_table_dict.items():
                state_key = tuple(json.loads(state_str))
                for action_str, value in actions.items():
                    action_key = tuple(json.loads(action_str))
                    self.q_table[state_key][action_key] = value
            
            # Restore metadata
            self.epsilon = save_data.get('epsilon', self.epsilon)
            
            logger.info(f"Q-table loaded from {self.save_path}")
            logger.info(f"Loaded {len(self.q_table)} states, epsilon={self.epsilon:.3f}")
            
        except Exception as e:
            logger.error(f"Failed to load Q-table: {e}")
    
    async def route_task(
        self,
        task_type: str,
        prompt: str,
        context: Dict[str, Any]
    ) -> Tuple[Action, float]:
        """
        Route a task to optimal provider/model/strategy.
        
        Args:
            task_type: Type of task
            prompt: Task prompt
            context: Additional context
        
        Returns:
            Tuple of (selected action, confidence score)
        """
        # Build state from task characteristics
        state = State(
            task_type=task_type,
            complexity=context.get('complexity', 0.5),
            domain=context.get('domain', 'general'),
            persona=context.get('persona', 'developer'),
            context_size=len(prompt),
            urgency=context.get('urgency', 0.5),
            quality_requirement=context.get('quality_requirement', 0.7)
        )
        
        # Select action (exploitation mode for production)
        action = self.select_action(state, explore=False)
        
        # Calculate confidence based on Q-value
        q_value = self.get_q_value(state, action)
        
        # Normalize Q-value to confidence score (0-1)
        # Assuming Q-values typically range from -20 to +20
        confidence = (q_value + 20) / 40
        confidence = max(0.0, min(1.0, confidence))
        
        logger.info(f"Q-Learning routing: {action.provider}/{action.model} "
                   f"with strategy={action.strategy}, confidence={confidence:.2f}")
        
        return action, confidence
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get learning statistics."""
        stats = {
            'total_states': len(self.q_table),
            'total_experiences': len(self.experience_buffer),
            'epsilon': self.epsilon,
            'episodes': len(self.episode_rewards),
            'avg_reward': np.mean(self.episode_rewards[-100:]) if self.episode_rewards else 0,
            'success_rate': np.mean(self.success_rate_history[-100:]) if self.success_rate_history else 0
        }
        
        # Get most confident routes
        top_routes = []
        for state_key, actions in list(self.q_table.items())[:10]:
            if actions:
                best_action_key, best_q = max(actions.items(), key=lambda x: x[1])
                top_routes.append({
                    'state': state_key,
                    'action': best_action_key,
                    'q_value': best_q
                })
        
        stats['top_routes'] = sorted(top_routes, key=lambda x: x['q_value'], reverse=True)[:5]
        
        return stats