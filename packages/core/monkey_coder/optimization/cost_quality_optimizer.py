"""
Cost Optimization with Quality Scoring Engine.

This module implements sophisticated cost optimization algorithms that balance
resource usage with code quality output, ensuring the highest possible quality
while maintaining cost efficiency.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class OptimizationStrategy(str, Enum):
    """Optimization strategies for cost-quality balance."""
    QUALITY_FIRST = "quality_first"  # Maximize quality, then minimize cost
    COST_FIRST = "cost_first"  # Minimize cost, maintain acceptable quality
    BALANCED = "balanced"  # Balance between cost and quality
    ADAPTIVE = "adaptive"  # Adapt based on context
    PARETO = "pareto"  # Find Pareto optimal solutions

class ResourceType(str, Enum):
    """Types of resources to optimize."""
    TOKENS = "tokens"  # API tokens
    COMPUTE = "compute"  # Computational resources
    TIME = "time"  # Execution time
    MEMORY = "memory"  # Memory usage
    NETWORK = "network"  # Network bandwidth

@dataclass
class CostModel:
    """Model for calculating costs."""
    token_costs: Dict[str, float] = field(default_factory=dict)  # provider -> cost per token
    compute_cost_per_second: float = 0.001
    memory_cost_per_gb: float = 0.01
    network_cost_per_gb: float = 0.02
    fixed_overhead: float = 0.0
    
    def calculate_token_cost(self, provider: str, tokens: int) -> float:
        """Calculate cost for API tokens."""
        rate = self.token_costs.get(provider, 0.0001)  # Default rate
        return tokens * rate
    
    def calculate_compute_cost(self, seconds: float) -> float:
        """Calculate computational cost."""
        return seconds * self.compute_cost_per_second
    
    def calculate_total_cost(self, resources: Dict[ResourceType, float]) -> float:
        """Calculate total cost from resource usage."""
        total = self.fixed_overhead
        
        if ResourceType.TOKENS in resources:
            # Assume default provider for simplicity
            total += resources[ResourceType.TOKENS] * 0.0001
        
        if ResourceType.COMPUTE in resources:
            total += self.calculate_compute_cost(resources[ResourceType.COMPUTE])
        
        if ResourceType.MEMORY in resources:
            total += resources[ResourceType.MEMORY] * self.memory_cost_per_gb
        
        if ResourceType.NETWORK in resources:
            total += resources[ResourceType.NETWORK] * self.network_cost_per_gb
        
        return total

@dataclass
class QualityMetrics:
    """Metrics for measuring code quality."""
    correctness: float = 0.0  # 0.0 to 1.0
    completeness: float = 0.0  # 0.0 to 1.0
    maintainability: float = 0.0  # 0.0 to 1.0
    performance: float = 0.0  # 0.0 to 1.0
    security: float = 0.0  # 0.0 to 1.0
    documentation: float = 0.0  # 0.0 to 1.0
    test_coverage: float = 0.0  # 0.0 to 1.0
    
    @property
    def overall_quality(self) -> float:
        """Calculate overall quality score."""
        weights = {
            'correctness': 0.3,
            'completeness': 0.2,
            'maintainability': 0.15,
            'performance': 0.1,
            'security': 0.1,
            'documentation': 0.1,
            'test_coverage': 0.05
        }
        
        total = 0.0
        for metric, weight in weights.items():
            total += getattr(self, metric) * weight
        
        return total

@dataclass
class OptimizationResult:
    """Result of optimization."""
    strategy: OptimizationStrategy
    cost: float
    quality: QualityMetrics
    resources_used: Dict[ResourceType, float]
    execution_time: float
    iterations: int
    convergence_achieved: bool
    pareto_frontier: Optional[List[Tuple[float, float]]] = None  # (cost, quality) pairs

class ParetoOptimizer:
    """Optimizer for finding Pareto optimal solutions."""
    
    def __init__(self):
        """Initialize Pareto optimizer."""
        self.solutions: List[Tuple[float, float, Any]] = []  # (cost, quality, solution)
        
    def add_solution(self, cost: float, quality: float, solution: Any):
        """Add a solution to the set."""
        self.solutions.append((cost, quality, solution))
    
    def find_pareto_frontier(self) -> List[Tuple[float, float, Any]]:
        """Find Pareto optimal solutions."""
        if not self.solutions:
            return []
        
        # Sort by cost
        sorted_solutions = sorted(self.solutions, key=lambda x: x[0])
        
        pareto_frontier = []
        max_quality = -float('inf')
        
        for cost, quality, solution in sorted_solutions:
            # A solution is Pareto optimal if it has better quality
            # than all cheaper solutions
            if quality > max_quality:
                pareto_frontier.append((cost, quality, solution))
                max_quality = quality
        
        return pareto_frontier
    
    def select_optimal(
        self,
        cost_weight: float = 0.5,
        quality_weight: float = 0.5
    ) -> Optional[Tuple[float, float, Any]]:
        """Select optimal solution based on weights."""
        frontier = self.find_pareto_frontier()
        
        if not frontier:
            return None
        
        # Normalize and score each solution
        min_cost = min(s[0] for s in frontier)
        max_cost = max(s[0] for s in frontier)
        min_quality = min(s[1] for s in frontier)
        max_quality = max(s[1] for s in frontier)
        
        best_score = -float('inf')
        best_solution = None
        
        for cost, quality, solution in frontier:
            # Normalize
            norm_cost = (cost - min_cost) / (max_cost - min_cost + 1e-10)
            norm_quality = (quality - min_quality) / (max_quality - min_quality + 1e-10)
            
            # Score (minimize cost, maximize quality)
            score = -cost_weight * norm_cost + quality_weight * norm_quality
            
            if score > best_score:
                best_score = score
                best_solution = (cost, quality, solution)
        
        return best_solution

class GeneticOptimizer:
    """Genetic algorithm for cost-quality optimization."""
    
    def __init__(
        self,
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7
    ):
        """
        Initialize genetic optimizer.
        
        Args:
            population_size: Size of population
            generations: Number of generations
            mutation_rate: Probability of mutation
            crossover_rate: Probability of crossover
        """
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        
    def optimize(
        self,
        fitness_function,
        gene_space: Dict[str, Tuple[float, float]],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run genetic optimization.
        
        Args:
            fitness_function: Function to evaluate fitness
            gene_space: Space of possible gene values
            constraints: Optional constraints
            
        Returns:
            Best solution found
        """
        # Initialize population
        population = self._initialize_population(gene_space)
        
        best_individual = None
        best_fitness = -float('inf')
        
        for generation in range(self.generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                fitness = fitness_function(individual)
                fitness_scores.append(fitness)
                
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_individual = individual.copy()
            
            # Selection
            selected = self._selection(population, fitness_scores)
            
            # Crossover
            offspring = []
            for i in range(0, len(selected), 2):
                if i + 1 < len(selected):
                    if np.random.random() < self.crossover_rate:
                        child1, child2 = self._crossover(selected[i], selected[i + 1])
                        offspring.extend([child1, child2])
                    else:
                        offspring.extend([selected[i].copy(), selected[i + 1].copy()])
            
            # Mutation
            for individual in offspring:
                if np.random.random() < self.mutation_rate:
                    self._mutate(individual, gene_space)
            
            # Apply constraints
            if constraints:
                offspring = [ind for ind in offspring if self._check_constraints(ind, constraints)]
            
            # Update population
            population = offspring[:self.population_size]
        
        return {
            'best_solution': best_individual,
            'best_fitness': best_fitness,
            'generations_run': self.generations
        }
    
    def _initialize_population(self, gene_space: Dict[str, Tuple[float, float]]) -> List[Dict[str, float]]:
        """Initialize random population."""
        population = []
        
        for _ in range(self.population_size):
            individual = {}
            for gene, (min_val, max_val) in gene_space.items():
                individual[gene] = np.random.uniform(min_val, max_val)
            population.append(individual)
        
        return population
    
    def _selection(self, population: List[Dict], fitness_scores: List[float]) -> List[Dict]:
        """Tournament selection."""
        selected = []
        tournament_size = 3
        
        for _ in range(len(population)):
            # Random tournament
            tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            
            # Select winner
            winner_idx = tournament_indices[np.argmax(tournament_fitness)]
            selected.append(population[winner_idx].copy())
        
        return selected
    
    def _crossover(self, parent1: Dict, parent2: Dict) -> Tuple[Dict, Dict]:
        """Uniform crossover."""
        child1 = {}
        child2 = {}
        
        for gene in parent1:
            if np.random.random() < 0.5:
                child1[gene] = parent1[gene]
                child2[gene] = parent2[gene]
            else:
                child1[gene] = parent2[gene]
                child2[gene] = parent1[gene]
        
        return child1, child2
    
    def _mutate(self, individual: Dict, gene_space: Dict[str, Tuple[float, float]]):
        """Gaussian mutation."""
        for gene, (min_val, max_val) in gene_space.items():
            if np.random.random() < 0.3:  # Mutate this gene
                # Add Gaussian noise
                noise = np.random.normal(0, (max_val - min_val) * 0.1)
                individual[gene] = np.clip(individual[gene] + noise, min_val, max_val)
    
    def _check_constraints(self, individual: Dict, constraints: Dict) -> bool:
        """Check if individual satisfies constraints."""
        for constraint_name, constraint_func in constraints.items():
            if not constraint_func(individual):
                return False
        return True

class CostQualityOptimizer:
    """
    Main optimizer for balancing cost and quality in code generation.
    
    Implements multiple optimization strategies to find the best balance
    between resource usage and code quality.
    """
    
    def __init__(self):
        """Initialize the optimizer."""
        self.cost_model = CostModel()
        self.pareto_optimizer = ParetoOptimizer()
        self.genetic_optimizer = GeneticOptimizer()
        
        # Historical data for learning
        self.optimization_history: List[OptimizationResult] = []
        self.quality_thresholds = {
            'minimum': 0.6,
            'acceptable': 0.7,
            'good': 0.8,
            'excellent': 0.9
        }
        
        # Cache for repeated optimizations
        self.optimization_cache: Dict[str, OptimizationResult] = {}
        
    async def optimize(
        self,
        task_description: str,
        available_resources: Dict[ResourceType, float],
        strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
        quality_threshold: float = 0.7,
        cost_limit: Optional[float] = None
    ) -> OptimizationResult:
        """
        Optimize cost and quality for a task.
        
        Args:
            task_description: Description of the task
            available_resources: Available resources
            strategy: Optimization strategy
            quality_threshold: Minimum acceptable quality
            cost_limit: Maximum acceptable cost
            
        Returns:
            Optimization result
        """
        # Check cache
        cache_key = f"{task_description}_{strategy}_{quality_threshold}"
        if cache_key in self.optimization_cache:
            logger.info(f"Using cached optimization for {cache_key}")
            return self.optimization_cache[cache_key]
        
        start_time = datetime.now()
        
        # Select optimization method based on strategy
        if strategy == OptimizationStrategy.PARETO:
            result = await self._optimize_pareto(
                task_description,
                available_resources,
                quality_threshold,
                cost_limit
            )
        elif strategy == OptimizationStrategy.ADAPTIVE:
            result = await self._optimize_adaptive(
                task_description,
                available_resources,
                quality_threshold,
                cost_limit
            )
        else:
            result = await self._optimize_standard(
                task_description,
                available_resources,
                strategy,
                quality_threshold,
                cost_limit
            )
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        result.execution_time = execution_time
        
        # Store in history and cache
        self.optimization_history.append(result)
        self.optimization_cache[cache_key] = result
        
        logger.info(f"Optimization complete: cost={result.cost:.4f}, quality={result.quality.overall_quality:.4f}")
        
        return result
    
    async def _optimize_standard(
        self,
        task_description: str,
        available_resources: Dict[ResourceType, float],
        strategy: OptimizationStrategy,
        quality_threshold: float,
        cost_limit: Optional[float]
    ) -> OptimizationResult:
        """Standard optimization for quality-first, cost-first, or balanced strategies."""
        
        # Define optimization parameters based on strategy
        if strategy == OptimizationStrategy.QUALITY_FIRST:
            quality_weight = 0.8
            cost_weight = 0.2
        elif strategy == OptimizationStrategy.COST_FIRST:
            quality_weight = 0.2
            cost_weight = 0.8
        else:  # BALANCED
            quality_weight = 0.5
            cost_weight = 0.5
        
        # Use genetic algorithm to find optimal resource allocation
        def fitness_function(allocation: Dict[str, float]) -> float:
            # Calculate quality from allocation
            quality = self._estimate_quality(allocation)
            
            # Calculate cost
            resources = {
                ResourceType.TOKENS: allocation.get('tokens', 0),
                ResourceType.COMPUTE: allocation.get('compute', 0),
                ResourceType.MEMORY: allocation.get('memory', 0)
            }
            cost = self.cost_model.calculate_total_cost(resources)
            
            # Check constraints
            if quality.overall_quality < quality_threshold:
                return -1000  # Penalty for not meeting quality threshold
            
            if cost_limit and cost > cost_limit:
                return -1000  # Penalty for exceeding cost limit
            
            # Calculate fitness
            normalized_quality = quality.overall_quality
            normalized_cost = 1.0 - min(cost / (cost_limit or 100), 1.0)
            
            fitness = quality_weight * normalized_quality + cost_weight * normalized_cost
            
            return fitness
        
        # Define gene space (resource allocation ranges)
        gene_space = {
            'tokens': (1000, min(available_resources.get(ResourceType.TOKENS, 100000), 100000)),
            'compute': (1, min(available_resources.get(ResourceType.COMPUTE, 3600), 3600)),
            'memory': (0.1, min(available_resources.get(ResourceType.MEMORY, 16), 16))
        }
        
        # Run genetic optimization
        ga_result = self.genetic_optimizer.optimize(
            fitness_function,
            gene_space,
            constraints={
                'resource_limits': lambda x: all(
                    x[k] <= available_resources.get(ResourceType[k.upper()], float('inf'))
                    for k in x
                )
            }
        )
        
        # Extract best solution
        best_allocation = ga_result['best_solution']
        
        # Calculate final metrics
        resources_used = {
            ResourceType.TOKENS: best_allocation['tokens'],
            ResourceType.COMPUTE: best_allocation['compute'],
            ResourceType.MEMORY: best_allocation['memory']
        }
        
        quality = self._estimate_quality(best_allocation)
        cost = self.cost_model.calculate_total_cost(resources_used)
        
        return OptimizationResult(
            strategy=strategy,
            cost=cost,
            quality=quality,
            resources_used=resources_used,
            execution_time=0.0,  # Will be set by caller
            iterations=self.genetic_optimizer.generations,
            convergence_achieved=True
        )
    
    async def _optimize_pareto(
        self,
        task_description: str,
        available_resources: Dict[ResourceType, float],
        quality_threshold: float,
        cost_limit: Optional[float]
    ) -> OptimizationResult:
        """Pareto optimization to find optimal trade-offs."""
        
        # Generate multiple solutions with different resource allocations
        num_samples = 100
        
        for _ in range(num_samples):
            # Random resource allocation
            allocation = {
                'tokens': np.random.uniform(1000, available_resources.get(ResourceType.TOKENS, 100000)),
                'compute': np.random.uniform(1, available_resources.get(ResourceType.COMPUTE, 3600)),
                'memory': np.random.uniform(0.1, available_resources.get(ResourceType.MEMORY, 16))
            }
            
            # Calculate quality and cost
            quality = self._estimate_quality(allocation)
            resources = {
                ResourceType.TOKENS: allocation['tokens'],
                ResourceType.COMPUTE: allocation['compute'],
                ResourceType.MEMORY: allocation['memory']
            }
            cost = self.cost_model.calculate_total_cost(resources)
            
            # Add to Pareto optimizer if constraints are met
            if quality.overall_quality >= quality_threshold:
                if not cost_limit or cost <= cost_limit:
                    self.pareto_optimizer.add_solution(
                        cost,
                        quality.overall_quality,
                        (allocation, quality, resources)
                    )
        
        # Find Pareto frontier
        frontier = self.pareto_optimizer.find_pareto_frontier()
        
        if not frontier:
            # No valid solutions found
            return OptimizationResult(
                strategy=OptimizationStrategy.PARETO,
                cost=float('inf'),
                quality=QualityMetrics(),
                resources_used={},
                execution_time=0.0,
                iterations=num_samples,
                convergence_achieved=False
            )
        
        # Select best from Pareto frontier (balanced weights)
        best = self.pareto_optimizer.select_optimal(cost_weight=0.5, quality_weight=0.5)
        
        if best:
            cost, quality_score, (allocation, quality, resources) = best
            
            return OptimizationResult(
                strategy=OptimizationStrategy.PARETO,
                cost=cost,
                quality=quality,
                resources_used=resources,
                execution_time=0.0,
                iterations=num_samples,
                convergence_achieved=True,
                pareto_frontier=[(c, q) for c, q, _ in frontier]
            )
        
        # Fallback
        return OptimizationResult(
            strategy=OptimizationStrategy.PARETO,
            cost=frontier[0][0],
            quality=self._create_quality_metrics(frontier[0][1]),
            resources_used={},
            execution_time=0.0,
            iterations=num_samples,
            convergence_achieved=True,
            pareto_frontier=[(c, q) for c, q, _ in frontier]
        )
    
    async def _optimize_adaptive(
        self,
        task_description: str,
        available_resources: Dict[ResourceType, float],
        quality_threshold: float,
        cost_limit: Optional[float]
    ) -> OptimizationResult:
        """Adaptive optimization that learns from history."""
        
        # Analyze task characteristics
        task_complexity = self._estimate_task_complexity(task_description)
        
        # Select strategy based on task and history
        if task_complexity > 0.8:
            # Complex task: prioritize quality
            strategy = OptimizationStrategy.QUALITY_FIRST
        elif cost_limit and cost_limit < self._estimate_minimum_cost(task_complexity):
            # Tight budget: prioritize cost
            strategy = OptimizationStrategy.COST_FIRST
        else:
            # Normal case: balanced approach
            strategy = OptimizationStrategy.BALANCED
        
        # Learn from similar past optimizations
        similar_optimizations = self._find_similar_optimizations(task_description)
        
        if similar_optimizations:
            # Use average of successful past optimizations as starting point
            avg_resources = defaultdict(float)
            for opt in similar_optimizations:
                for resource, amount in opt.resources_used.items():
                    avg_resources[resource] += amount / len(similar_optimizations)
            
            # Adjust based on current constraints
            for resource in avg_resources:
                if resource in available_resources:
                    avg_resources[resource] = min(avg_resources[resource], available_resources[resource])
            
            # Calculate expected quality and cost
            quality = self._estimate_quality_from_resources(dict(avg_resources))
            cost = self.cost_model.calculate_total_cost(dict(avg_resources))
            
            # Fine-tune if needed
            if quality.overall_quality < quality_threshold:
                # Increase resources to meet quality
                for resource in avg_resources:
                    avg_resources[resource] *= 1.2
                quality = self._estimate_quality_from_resources(dict(avg_resources))
                cost = self.cost_model.calculate_total_cost(dict(avg_resources))
            
            return OptimizationResult(
                strategy=OptimizationStrategy.ADAPTIVE,
                cost=cost,
                quality=quality,
                resources_used=dict(avg_resources),
                execution_time=0.0,
                iterations=len(similar_optimizations),
                convergence_achieved=True
            )
        
        # No similar optimizations found, use standard optimization
        return await self._optimize_standard(
            task_description,
            available_resources,
            strategy,
            quality_threshold,
            cost_limit
        )
    
    def _estimate_quality(self, allocation: Dict[str, float]) -> QualityMetrics:
        """Estimate quality metrics from resource allocation."""
        # Simplified quality estimation based on resources
        tokens = allocation.get('tokens', 0)
        compute = allocation.get('compute', 0)
        memory = allocation.get('memory', 0)
        
        # More tokens generally mean better quality
        token_quality = min(1.0, tokens / 50000)
        
        # More compute allows for better optimization
        compute_quality = min(1.0, compute / 60)
        
        # More memory allows for larger context
        memory_quality = min(1.0, memory / 8)
        
        # Calculate individual metrics
        quality = QualityMetrics(
            correctness=0.5 + 0.3 * token_quality + 0.2 * compute_quality,
            completeness=0.4 + 0.4 * token_quality + 0.2 * memory_quality,
            maintainability=0.5 + 0.2 * token_quality + 0.3 * compute_quality,
            performance=0.4 + 0.1 * token_quality + 0.5 * compute_quality,
            security=0.6 + 0.2 * token_quality + 0.2 * compute_quality,
            documentation=0.3 + 0.5 * token_quality + 0.2 * memory_quality,
            test_coverage=0.4 + 0.3 * token_quality + 0.3 * compute_quality
        )
        
        # Ensure all metrics are in [0, 1]
        for attr in ['correctness', 'completeness', 'maintainability', 'performance', 
                    'security', 'documentation', 'test_coverage']:
            setattr(quality, attr, min(1.0, getattr(quality, attr)))
        
        return quality
    
    def _estimate_quality_from_resources(self, resources: Dict[ResourceType, float]) -> QualityMetrics:
        """Estimate quality from resource usage."""
        allocation = {
            'tokens': resources.get(ResourceType.TOKENS, 0),
            'compute': resources.get(ResourceType.COMPUTE, 0),
            'memory': resources.get(ResourceType.MEMORY, 0)
        }
        return self._estimate_quality(allocation)
    
    def _create_quality_metrics(self, overall_score: float) -> QualityMetrics:
        """Create quality metrics from overall score."""
        # Distribute score across metrics
        base = overall_score * 0.8
        variation = overall_score * 0.2
        
        return QualityMetrics(
            correctness=base + np.random.uniform(0, variation),
            completeness=base + np.random.uniform(0, variation),
            maintainability=base + np.random.uniform(0, variation),
            performance=base + np.random.uniform(0, variation),
            security=base + np.random.uniform(0, variation),
            documentation=base + np.random.uniform(0, variation),
            test_coverage=base + np.random.uniform(0, variation)
        )
    
    def _estimate_task_complexity(self, task_description: str) -> float:
        """Estimate task complexity from description."""
        # Simplified complexity estimation
        complexity_keywords = [
            'complex', 'advanced', 'distributed', 'scalable',
            'optimize', 'refactor', 'architecture', 'enterprise'
        ]
        
        score = 0.3  # Base complexity
        for keyword in complexity_keywords:
            if keyword.lower() in task_description.lower():
                score += 0.1
        
        return min(1.0, score)
    
    def _estimate_minimum_cost(self, complexity: float) -> float:
        """Estimate minimum cost based on complexity."""
        # Base cost increases with complexity
        base_cost = 0.01 + complexity * 0.1
        return base_cost
    
    def _find_similar_optimizations(self, task_description: str) -> List[OptimizationResult]:
        """Find similar past optimizations."""
        similar = []
        
        # Simple similarity check (in practice, use better NLP methods)
        task_words = set(task_description.lower().split())
        
        for opt in self.optimization_history:
            if opt.quality.overall_quality >= 0.7:  # Only successful optimizations
                # Check if any previous optimization might be similar
                # This is a placeholder - real implementation would use better similarity metrics
                if opt.convergence_achieved:
                    similar.append(opt)
        
        return similar[-5:] if similar else []  # Return last 5 similar
    
    def get_optimization_insights(self) -> Dict[str, Any]:
        """Get insights from optimization history."""
        if not self.optimization_history:
            return {'message': 'No optimization history available'}
        
        # Calculate statistics
        avg_cost = np.mean([opt.cost for opt in self.optimization_history])
        avg_quality = np.mean([opt.quality.overall_quality for opt in self.optimization_history])
        success_rate = sum(1 for opt in self.optimization_history if opt.convergence_achieved) / len(self.optimization_history)
        
        # Find best trade-offs
        best_quality = max(self.optimization_history, key=lambda x: x.quality.overall_quality)
        best_cost = min(self.optimization_history, key=lambda x: x.cost)
        
        # Strategy distribution
        strategy_counts = defaultdict(int)
        for opt in self.optimization_history:
            strategy_counts[opt.strategy] += 1
        
        return {
            'total_optimizations': len(self.optimization_history),
            'average_cost': avg_cost,
            'average_quality': avg_quality,
            'success_rate': success_rate,
            'best_quality_achieved': best_quality.quality.overall_quality,
            'lowest_cost_achieved': best_cost.cost,
            'strategy_distribution': dict(strategy_counts),
            'cache_size': len(self.optimization_cache)
        }