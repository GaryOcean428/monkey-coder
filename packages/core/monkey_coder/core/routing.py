"""
Advanced Router System (Gary8D-inspired) for intelligent model and persona selection.

This module implements sophisticated routing logic with:
- Complexity analysis and scoring
- Context-aware model selection
- Capability matching with provider models
- SuperClaude persona integration
- Slash-command parsing and routing
"""

import re
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from ..models import (
    ExecuteRequest, 
    PersonaType, 
    ProviderType, 
    TaskType,
    MODEL_REGISTRY
)

logger = logging.getLogger(__name__)


class ComplexityLevel(str, Enum):
    """Task complexity levels for routing decisions."""
    TRIVIAL = "trivial"        # Simple queries, basic info retrieval
    SIMPLE = "simple"          # Straightforward coding tasks
    MODERATE = "moderate"      # Multi-step processes, standard algorithms
    COMPLEX = "complex"        # Architecture decisions, complex logic
    CRITICAL = "critical"      # Mission-critical, high-stakes tasks


class ContextType(str, Enum):
    """Context types for routing analysis."""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review" 
    DEBUGGING = "debugging"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    REFACTORING = "refactoring"


@dataclass
class RoutingDecision:
    """Encapsulates routing decision with rationale."""
    provider: ProviderType
    model: str
    persona: PersonaType
    complexity_score: float
    context_score: float
    capability_score: float
    confidence: float
    reasoning: str
    metadata: Dict[str, Any]


@dataclass
class ModelCapabilities:
    """Model capability profile for matching."""
    code_generation: float
    reasoning: float
    context_window: int
    latency_ms: float
    cost_per_token: float
    reliability: float
    specializations: List[str]
    

class AdvancedRouter:
    """
    Gary8D-inspired Advanced Router with quantum-inspired decision making.
    
    Features:
    - Multi-dimensional complexity analysis
    - Context-aware persona selection
    - Dynamic capability scoring
    - SuperClaude slash-command integration
    - Cost-performance optimization
    """
    
    def __init__(self):
        self.model_capabilities = self._initialize_model_capabilities()
        self.persona_mappings = self._initialize_persona_mappings()
        self.slash_commands = self._initialize_slash_commands()
        self.routing_history = []
        
    def route_request(self, request: ExecuteRequest) -> RoutingDecision:
        """
        Main routing method with comprehensive analysis.
        
        Args:
            request: The execution request to route
            
        Returns:
            RoutingDecision with selected model, persona, and reasoning
        """
        logger.info(f"Routing request: {request.task_type}")
        
        # Phase 1: Analyze request complexity
        complexity_score = self._analyze_complexity(request)
        complexity_level = self._classify_complexity(complexity_score)
        
        # Phase 2: Extract and score context
        context_type = self._extract_context_type(request)
        context_score = self._score_context_match(request, context_type)
        
        # Phase 3: Parse slash commands and determine persona
        slash_command = self._parse_slash_commands(request.prompt)
        persona = self._select_persona(request, slash_command, context_type)
        
        # Phase 4: Calculate capability requirements
        capability_requirements = self._calculate_capability_requirements(
            request, complexity_level, context_type, persona
        )
        
        # Phase 5: Score and rank models
        model_scores = self._score_models(capability_requirements)
        
        # Phase 6: Make final selection with optimization
        provider, model = self._select_optimal_model(
            model_scores, request, complexity_score, context_score
        )
        
        # Phase 7: Calculate overall confidence
        confidence = self._calculate_confidence(
            complexity_score, context_score, model_scores[(provider, model)]
        )
        
        # Create routing decision
        decision = RoutingDecision(
            provider=provider,
            model=model,
            persona=persona,
            complexity_score=complexity_score,
            context_score=context_score,
            capability_score=model_scores[(provider, model)],
            confidence=confidence,
            reasoning=self._generate_reasoning(
                complexity_level, context_type, persona, provider, model
            ),
            metadata={
                "timestamp": datetime.utcnow().isoformat(),
                "slash_command": slash_command,
                "context_type": context_type.value,
                "complexity_level": complexity_level.value,
                "model_scores": model_scores,
            }
        )
        
        # Store in history for learning
        self.routing_history.append(decision)
        
        logger.info(f"Routing decision: {provider.value}/{model} ({persona.value})")
        return decision
    
    def _analyze_complexity(self, request: ExecuteRequest) -> float:
        """
        Analyze request complexity using multiple signals.
        
        Returns complexity score from 0.0 (trivial) to 1.0 (critical)
        """
        score = 0.0
        prompt = request.prompt.lower()
        
        # Text length indicators
        word_count = len(prompt.split())
        if word_count > 500:
            score += 0.3
        elif word_count > 200:
            score += 0.2
        elif word_count > 50:
            score += 0.1
            
        # Technical complexity keywords
        complex_keywords = [
            'architecture', 'design pattern', 'scalability', 'performance',
            'optimization', 'algorithm', 'data structure', 'system design',
            'distributed', 'microservices', 'database', 'security', 'concurrent',
            'async', 'threading', 'machine learning', 'ai', 'neural network'
        ]
        
        keyword_matches = sum(1 for kw in complex_keywords if kw in prompt)
        score += min(keyword_matches * 0.1, 0.4)
        
        # Code complexity indicators
        if any(indicator in prompt for indicator in ['class', 'function', 'method', 'import']):
            score += 0.1
            
        # Multi-step process indicators
        step_indicators = ['step', 'phase', 'first', 'then', 'next', 'finally']
        if sum(1 for ind in step_indicators if ind in prompt) >= 3:
            score += 0.2
            
        # File count complexity
        if request.files and len(request.files) > 5:
            score += 0.2
        elif request.files and len(request.files) > 1:
            score += 0.1
            
        return min(score, 1.0)
    
    def _classify_complexity(self, score: float) -> ComplexityLevel:
        """Classify numeric complexity score into levels."""
        if score >= 0.8:
            return ComplexityLevel.CRITICAL
        elif score >= 0.6:
            return ComplexityLevel.COMPLEX
        elif score >= 0.4:
            return ComplexityLevel.MODERATE
        elif score >= 0.2:
            return ComplexityLevel.SIMPLE
        else:
            return ComplexityLevel.TRIVIAL
    
    def _extract_context_type(self, request: ExecuteRequest) -> ContextType:
        """Extract primary context type from request."""
        prompt = request.prompt.lower()
        
        # Task type mapping
        task_context_map = {
            TaskType.CODE_GENERATION: ContextType.CODE_GENERATION,
            TaskType.CODE_REVIEW: ContextType.CODE_REVIEW,
            TaskType.DEBUGGING: ContextType.DEBUGGING,
            TaskType.DOCUMENTATION: ContextType.DOCUMENTATION,
            TaskType.TESTING: ContextType.TESTING,
            TaskType.REFACTORING: ContextType.REFACTORING,
        }
        
        if request.task_type in task_context_map:
            return task_context_map[request.task_type]
        
        # Keyword-based detection
        context_keywords = {
            ContextType.CODE_GENERATION: ['generate', 'create', 'write', 'implement', 'build'],
            ContextType.CODE_REVIEW: ['review', 'analyze', 'check', 'evaluate', 'assess'],
            ContextType.DEBUGGING: ['debug', 'fix', 'error', 'bug', 'issue', 'problem'],
            ContextType.ARCHITECTURE: ['architecture', 'design', 'structure', 'pattern'],
            ContextType.SECURITY: ['security', 'vulnerability', 'exploit', 'secure', 'auth'],
            ContextType.PERFORMANCE: ['performance', 'optimize', 'speed', 'memory', 'efficient'],
            ContextType.DOCUMENTATION: ['document', 'explain', 'describe', 'comment'],
            ContextType.TESTING: ['test', 'unittest', 'spec', 'verify', 'validate'],
            ContextType.REFACTORING: ['refactor', 'improve', 'clean', 'restructure'],
        }
        
        best_match = ContextType.CODE_GENERATION
        max_score = 0
        
        for context_type, keywords in context_keywords.items():
            score = sum(1 for kw in keywords if kw in prompt)
            if score > max_score:
                max_score = score
                best_match = context_type
                
        return best_match
    
    def _score_context_match(self, request: ExecuteRequest, context_type: ContextType) -> float:
        """Score how well the request matches the identified context."""
        prompt = request.prompt.lower()
        
        # Context-specific scoring
        if context_type == ContextType.CODE_GENERATION:
            indicators = ['function', 'class', 'method', 'create', 'implement']
        elif context_type == ContextType.DEBUGGING:
            indicators = ['error', 'exception', 'traceback', 'fix', 'debug']
        elif context_type == ContextType.ARCHITECTURE:
            indicators = ['design', 'pattern', 'structure', 'component', 'system']
        else:
            indicators = []
            
        matches = sum(1 for ind in indicators if ind in prompt)
        return min(matches * 0.2, 1.0)
    
    def _parse_slash_commands(self, prompt: str) -> Optional[str]:
        """Parse slash commands from prompt."""
        slash_pattern = r'/([a-zA-Z_-]+)'
        matches = re.findall(slash_pattern, prompt)
        return matches[0] if matches else None
    
    def _select_persona(
        self, 
        request: ExecuteRequest, 
        slash_command: Optional[str], 
        context_type: ContextType
    ) -> PersonaType:
        """Select appropriate persona based on request analysis."""
        
        # Slash command persona mapping (prioritize over explicit config if present)
        if slash_command and slash_command in self.slash_commands:
            return self.slash_commands[slash_command]
        
        # Explicit persona from request config (if not overridden by slash command)
        if hasattr(request, 'superclause_config') and request.superclause_config:
            # If the persona is explicitly set and not default, use it
            if hasattr(request.superclause_config, 'persona'):
                return request.superclause_config.persona
        
        # Context-based persona selection
        context_persona_map = {
            ContextType.CODE_GENERATION: PersonaType.DEVELOPER,
            ContextType.CODE_REVIEW: PersonaType.REVIEWER,
            ContextType.DEBUGGING: PersonaType.DEVELOPER,
            ContextType.ARCHITECTURE: PersonaType.ARCHITECT,
            ContextType.SECURITY: PersonaType.SECURITY_ANALYST,
            ContextType.PERFORMANCE: PersonaType.PERFORMANCE_EXPERT,
            ContextType.DOCUMENTATION: PersonaType.TECHNICAL_WRITER,
            ContextType.TESTING: PersonaType.TESTER,
            ContextType.REFACTORING: PersonaType.DEVELOPER,
        }
        
        return context_persona_map.get(context_type, PersonaType.DEVELOPER)
    
    def _calculate_capability_requirements(
        self,
        request: ExecuteRequest,
        complexity_level: ComplexityLevel, 
        context_type: ContextType,
        persona: PersonaType
    ) -> Dict[str, float]:
        """Calculate required capabilities for the request."""
        requirements = {
            'code_generation': 0.5,
            'reasoning': 0.5,
            'context_window': 8192,
            'reliability': 0.7,
        }
        
        # Adjust based on complexity
        complexity_multipliers = {
            ComplexityLevel.TRIVIAL: 0.6,
            ComplexityLevel.SIMPLE: 0.7,
            ComplexityLevel.MODERATE: 0.8,
            ComplexityLevel.COMPLEX: 0.9,
            ComplexityLevel.CRITICAL: 1.0,
        }
        
        multiplier = complexity_multipliers[complexity_level]
        requirements['code_generation'] *= multiplier
        requirements['reasoning'] *= multiplier
        requirements['reliability'] = max(requirements['reliability'], multiplier * 0.8)
        
        # Adjust based on context
        if context_type == ContextType.CODE_GENERATION:
            requirements['code_generation'] = 0.9
        elif context_type == ContextType.ARCHITECTURE:
            requirements['reasoning'] = 0.95
            requirements['context_window'] = 32768
        elif context_type == ContextType.SECURITY:
            requirements['reliability'] = 0.95
            
        # Adjust based on persona
        if persona == PersonaType.ARCHITECT:
            requirements['reasoning'] = 0.9
            requirements['context_window'] = max(requirements['context_window'], 16384)
        elif persona == PersonaType.SECURITY_ANALYST:
            requirements['reliability'] = 0.95
            
        return requirements
    
    def _score_models(self, requirements: Dict[str, float]) -> Dict[Tuple[ProviderType, str], float]:
        """Score all available models against requirements."""
        scores = {}
        
        for provider, models in MODEL_REGISTRY.items():
            for model in models:
                if (provider, model) in self.model_capabilities:
                    capabilities = self.model_capabilities[(provider, model)]
                    score = self._calculate_model_score(capabilities, requirements)
                    scores[(provider, model)] = score
                    
        return scores
    
    def _calculate_model_score(
        self, 
        capabilities: ModelCapabilities, 
        requirements: Dict[str, float]
    ) -> float:
        """Calculate fitness score for a model against requirements."""
        score = 0.0
        
        # Code generation capability match
        code_gen_score = min(capabilities.code_generation / requirements['code_generation'], 1.0)
        score += code_gen_score * 0.3
        
        # Reasoning capability match
        reasoning_score = min(capabilities.reasoning / requirements['reasoning'], 1.0)
        score += reasoning_score * 0.3
        
        # Context window adequacy
        context_score = 1.0 if capabilities.context_window >= requirements['context_window'] else 0.5
        score += context_score * 0.2
        
        # Reliability match
        reliability_score = min(capabilities.reliability / requirements['reliability'], 1.0)
        score += reliability_score * 0.2
        
        return score
    
    def _select_optimal_model(
        self,
        model_scores: Dict[Tuple[ProviderType, str], float],
        request: ExecuteRequest,
        complexity_score: float,
        context_score: float
    ) -> Tuple[ProviderType, str]:
        """Select optimal model considering scores and preferences."""
        
        # Apply user preferences
        preferred_providers = getattr(request, 'preferred_providers', [])
        if preferred_providers:
            # Filter to preferred providers
            filtered_scores = {
                (p, m): score for (p, m), score in model_scores.items()
                if p in preferred_providers
            }
            if filtered_scores:
                model_scores = filtered_scores
        
        # Apply model preferences
        model_preferences = getattr(request, 'model_preferences', {})
        for provider, preferred_model in model_preferences.items():
            if (provider, preferred_model) in model_scores:
                # Boost preferred model scores
                model_scores[(provider, preferred_model)] *= 1.2
        
        # Cost-performance optimization for simple tasks
        if complexity_score < 0.4:
            # Prefer cost-effective models for simple tasks
            for (provider, model), score in model_scores.items():
                capabilities = self.model_capabilities.get((provider, model))
                if capabilities and capabilities.cost_per_token < 0.001:  # Cheap models
                    model_scores[(provider, model)] *= 1.1
        
        # Select highest scoring model
        if not model_scores:
            # Fallback to default model
            return ProviderType.OPENAI, "gpt-4o-mini"
            
        best_model = max(model_scores.items(), key=lambda x: x[1])
        return best_model[0]
    
    def _calculate_confidence(
        self, 
        complexity_score: float, 
        context_score: float, 
        capability_score: float
    ) -> float:
        """Calculate confidence in routing decision."""
        # Higher confidence for clear contexts and well-matched capabilities
        confidence = (context_score * 0.4 + capability_score * 0.6)
        
        # Adjust for complexity - harder tasks have lower base confidence
        complexity_penalty = complexity_score * 0.2
        confidence = max(0.1, confidence - complexity_penalty)
        
        return min(confidence, 1.0)
    
    def _generate_reasoning(
        self,
        complexity_level: ComplexityLevel,
        context_type: ContextType, 
        persona: PersonaType,
        provider: ProviderType,
        model: str
    ) -> str:
        """Generate human-readable reasoning for routing decision."""
        return (
            f"Selected {provider.value}/{model} for {complexity_level.value} "
            f"{context_type.value} task with {persona.value} persona. "
            f"Model chosen for optimal capability match and cost-performance ratio."
        )
    
    def _initialize_model_capabilities(self) -> Dict[Tuple[ProviderType, str], ModelCapabilities]:
        """Initialize model capability profiles."""
        capabilities = {}
        
        # OpenAI models
        capabilities[(ProviderType.OPENAI, "gpt-4o")] = ModelCapabilities(
            code_generation=0.95, reasoning=0.98, context_window=128000,
            latency_ms=2000, cost_per_token=0.005, reliability=0.95,
            specializations=["general", "coding", "reasoning"]
        )
        
        capabilities[(ProviderType.OPENAI, "gpt-4o-mini")] = ModelCapabilities(
            code_generation=0.85, reasoning=0.88, context_window=128000,
            latency_ms=1000, cost_per_token=0.0001, reliability=0.90,
            specializations=["general", "coding", "fast"]
        )
        
        capabilities[(ProviderType.OPENAI, "o1-preview")] = ModelCapabilities(
            code_generation=0.98, reasoning=0.99, context_window=32768,
            latency_ms=15000, cost_per_token=0.015, reliability=0.98,
            specializations=["reasoning", "complex_problems", "math"]
        )
        
        # Anthropic models
        capabilities[(ProviderType.ANTHROPIC, "claude-3-5-sonnet-20241022")] = ModelCapabilities(
            code_generation=0.92, reasoning=0.94, context_window=200000,
            latency_ms=2500, cost_per_token=0.003, reliability=0.93,
            specializations=["coding", "analysis", "long_context"]
        )
        
        capabilities[(ProviderType.ANTHROPIC, "claude-3-5-haiku-20241022")] = ModelCapabilities(
            code_generation=0.80, reasoning=0.82, context_window=200000,
            latency_ms=800, cost_per_token=0.0008, reliability=0.88,
            specializations=["fast", "efficient", "basic_coding"]
        )
        
        # Google models
        capabilities[(ProviderType.GOOGLE, "gemini-2.0-flash-exp")] = ModelCapabilities(
            code_generation=0.88, reasoning=0.90, context_window=1000000,
            latency_ms=1200, cost_per_token=0.001, reliability=0.87,
            specializations=["multimodal", "long_context", "fast"]
        )
        
        # Qwen models
        capabilities[(ProviderType.QWEN, "qwen2.5-coder-32b-instruct")] = ModelCapabilities(
            code_generation=0.94, reasoning=0.85, context_window=32768,
            latency_ms=3000, cost_per_token=0.002, reliability=0.90,
            specializations=["coding", "open_source", "multilingual"]
        )
        
        return capabilities
    
    def _initialize_persona_mappings(self) -> Dict[PersonaType, Dict[str, Any]]:
        """Initialize persona configuration mappings."""
        return {
            PersonaType.DEVELOPER: {
                "specializations": ["coding", "implementation", "debugging"],
                "preferred_providers": [ProviderType.QWEN, ProviderType.OPENAI],
                "context_boost": {"code_generation": 1.2, "debugging": 1.1}
            },
            PersonaType.ARCHITECT: {
                "specializations": ["design", "architecture", "patterns"],
                "preferred_providers": [ProviderType.OPENAI, ProviderType.ANTHROPIC],
                "context_boost": {"architecture": 1.3, "reasoning": 1.2}
            },
            PersonaType.SECURITY_ANALYST: {
                "specializations": ["security", "vulnerabilities", "auditing"],
                "preferred_providers": [ProviderType.ANTHROPIC, ProviderType.OPENAI],
                "context_boost": {"security": 1.4, "reliability": 1.3}
            },
        }
    
    def _initialize_slash_commands(self) -> Dict[str, PersonaType]:
        """Initialize slash command to persona mappings."""
        return {
            "dev": PersonaType.DEVELOPER,
            "develop": PersonaType.DEVELOPER,
            "arch": PersonaType.ARCHITECT,
            "architect": PersonaType.ARCHITECT,
            "review": PersonaType.REVIEWER,
            "security": PersonaType.SECURITY_ANALYST,
            "sec": PersonaType.SECURITY_ANALYST,
            "perf": PersonaType.PERFORMANCE_EXPERT,
            "performance": PersonaType.PERFORMANCE_EXPERT,
            "test": PersonaType.TESTER,
            "testing": PersonaType.TESTER,
            "docs": PersonaType.TECHNICAL_WRITER,
            "documentation": PersonaType.TECHNICAL_WRITER,
        }
    
    def get_routing_debug_info(self, request: ExecuteRequest) -> Dict[str, Any]:
        """Get detailed debug information for routing decision."""
        decision = self.route_request(request)
        
        return {
            "routing_decision": {
                "provider": decision.provider.value,
                "model": decision.model,
                "persona": decision.persona.value,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning,
            },
            "scoring_breakdown": {
                "complexity_score": decision.complexity_score,
                "context_score": decision.context_score,
                "capability_score": decision.capability_score,
            },
            "metadata": decision.metadata,
            "available_models": list(self.model_capabilities.keys()),
            "routing_history_count": len(self.routing_history),
        }
