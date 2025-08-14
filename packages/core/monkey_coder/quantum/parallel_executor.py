"""
Quantum Parallel Execution Engine with Synaptic Connections.

This module implements quantum-inspired parallel execution where multiple solution
approaches run simultaneously with information sharing through synaptic connections.
Based on patterns from monkey1 and Gary8D projects.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

class QuantumState(str, Enum):
    """Quantum state of a parallel execution thread."""
    SUPERPOSITION = "superposition"  # Multiple possibilities exist
    ENTANGLED = "entangled"  # Connected to other threads
    COLLAPSED = "collapsed"  # Resolved to single outcome
    DECOHERENT = "decoherent"  # Lost quantum properties

class CollapseStrategy(str, Enum):
    """Strategy for collapsing quantum superposition."""
    FIRST_SUCCESS = "first_success"
    BEST_SCORE = "best_score"
    CONSENSUS = "consensus"
    COMBINED = "combined"
    WEIGHTED = "weighted"
    INTERFERENCE = "interference"  # Use quantum interference patterns

@dataclass
class QuantumThread:
    """Represents a single quantum execution thread."""
    thread_id: str = field(default_factory=lambda: f"qt_{uuid.uuid4().hex[:8]}")
    variation: Dict[str, Any] = field(default_factory=dict)
    state: QuantumState = QuantumState.SUPERPOSITION
    amplitude: complex = complex(1.0, 0.0)  # Quantum amplitude
    phase: float = 0.0  # Quantum phase
    entangled_with: Set[str] = field(default_factory=set)
    result: Optional[Any] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def probability(self) -> float:
        """Calculate probability from amplitude (Born rule)."""
        return abs(self.amplitude) ** 2
    
    @property
    def execution_time(self) -> float:
        """Calculate execution time."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

@dataclass 
class SynapticConnection:
    """Represents a synaptic connection between quantum threads."""
    connection_id: str = field(default_factory=lambda: f"syn_{uuid.uuid4().hex[:8]}")
    source_thread: str = ""
    target_thread: str = ""
    weight: float = 1.0  # Connection strength
    plasticity: float = 0.1  # Learning rate
    neurotransmitter: str = "information"  # Type of information shared
    last_signal: Optional[Any] = None
    signal_count: int = 0
    
    def strengthen(self, amount: float = 0.1):
        """Strengthen the synaptic connection (Hebbian learning)."""
        self.weight = min(1.0, self.weight + amount * self.plasticity)
        self.signal_count += 1
    
    def weaken(self, amount: float = 0.05):
        """Weaken the synaptic connection."""
        self.weight = max(0.0, self.weight - amount * self.plasticity)

class QuantumParallelExecutor:
    """
    Quantum-inspired parallel execution engine with synaptic connections.
    
    This implements a quantum computing approach where multiple variations
    of a task run in parallel, share information through synaptic connections,
    and collapse to the optimal solution based on interference patterns.
    """
    
    def __init__(self, max_threads: int = 5, enable_synapses: bool = True):
        """
        Initialize the quantum parallel executor.
        
        Args:
            max_threads: Maximum number of parallel threads
            enable_synapses: Whether to enable synaptic connections
        """
        self.max_threads = max_threads
        self.enable_synapses = enable_synapses
        
        # Quantum threads and connections
        self.threads: Dict[str, QuantumThread] = {}
        self.synapses: Dict[str, SynapticConnection] = {}
        self.synapse_map: Dict[str, List[str]] = defaultdict(list)  # thread_id -> [synapse_ids]
        
        # Execution history for learning
        self.execution_history: List[Dict[str, Any]] = []
        self.success_patterns: List[Dict[str, Any]] = []
        
        # Quantum interference patterns
        self.interference_matrix: Optional[np.ndarray] = None
    
    async def create_quantum_task(
        self,
        task_description: str,
        variations: List[Dict[str, Any]],
        collapse_strategy: CollapseStrategy = CollapseStrategy.INTERFERENCE,
        enable_entanglement: bool = True
    ) -> str:
        """
        Create a quantum task with multiple parallel variations.
        
        Args:
            task_description: Description of the task
            variations: List of variation configurations
            collapse_strategy: Strategy for collapsing results
            enable_entanglement: Whether to enable quantum entanglement
            
        Returns:
            Task ID
        """
        task_id = f"qtask_{uuid.uuid4().hex[:8]}"
        
        # Limit variations to max_threads
        variations = variations[:self.max_threads]
        
        # Create quantum threads for each variation
        for i, variation in enumerate(variations):
            thread = QuantumThread(
                variation=variation,
                phase=2 * np.pi * i / len(variations)  # Distribute phases evenly
            )
            self.threads[thread.thread_id] = thread
            
            # Create entanglement if enabled
            if enable_entanglement and i > 0:
                prev_thread_id = list(self.threads.keys())[i-1]
                thread.entangled_with.add(prev_thread_id)
                self.threads[prev_thread_id].entangled_with.add(thread.thread_id)
        
        # Create synaptic connections if enabled
        if self.enable_synapses:
            self._create_synaptic_network(list(self.threads.keys()))
        
        # Initialize interference matrix
        self._initialize_interference_matrix(len(variations))
        
        logger.info(f"Created quantum task {task_id} with {len(variations)} threads")
        return task_id
    
    def _create_synaptic_network(self, thread_ids: List[str]):
        """Create synaptic connections between threads."""
        # Create a mesh network with weighted connections
        for i, source_id in enumerate(thread_ids):
            for j, target_id in enumerate(thread_ids):
                if i != j:
                    # Calculate initial weight based on similarity
                    source_var = self.threads[source_id].variation
                    target_var = self.threads[target_id].variation
                    similarity = self._calculate_variation_similarity(source_var, target_var)
                    
                    synapse = SynapticConnection(
                        source_thread=source_id,
                        target_thread=target_id,
                        weight=similarity,
                        plasticity=0.1 + 0.1 * similarity  # More plastic for similar threads
                    )
                    
                    self.synapses[synapse.connection_id] = synapse
                    self.synapse_map[source_id].append(synapse.connection_id)
        
        logger.info(f"Created {len(self.synapses)} synaptic connections")
    
    def _calculate_variation_similarity(self, var1: Dict, var2: Dict) -> float:
        """Calculate similarity between two variations."""
        # Simple similarity based on common keys and values
        if not var1 or not var2:
            return 0.5
        
        common_keys = set(var1.keys()) & set(var2.keys())
        if not common_keys:
            return 0.1
        
        similarity = 0.0
        for key in common_keys:
            if var1[key] == var2[key]:
                similarity += 1.0
            elif isinstance(var1[key], (int, float)) and isinstance(var2[key], (int, float)):
                # Numerical similarity
                diff = abs(var1[key] - var2[key])
                max_val = max(abs(var1[key]), abs(var2[key]), 1)
                similarity += 1.0 - min(diff / max_val, 1.0)
        
        return min(1.0, similarity / len(common_keys))
    
    def _initialize_interference_matrix(self, n: int):
        """Initialize quantum interference matrix."""
        # Create interference patterns based on phase differences
        self.interference_matrix = np.zeros((n, n), dtype=complex)
        
        threads = list(self.threads.values())
        for i in range(n):
            for j in range(n):
                phase_diff = threads[i].phase - threads[j].phase
                # Constructive/destructive interference based on phase
                self.interference_matrix[i, j] = np.exp(1j * phase_diff)
    
    async def execute_quantum_threads(
        self,
        task_executor,  # Function to execute actual task
        task_description: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute all quantum threads in parallel with synaptic communication.
        
        Args:
            task_executor: Async function to execute the task
            task_description: Task description
            context: Execution context
            
        Returns:
            Execution results
        """
        # Create execution tasks for all threads
        tasks = []
        for thread_id, thread in self.threads.items():
            task = asyncio.create_task(
                self._execute_single_thread(
                    thread_id,
                    task_executor,
                    task_description,
                    context
                )
            )
            tasks.append(task)
        
        # If synapses enabled, start synaptic communication
        if self.enable_synapses:
            synapse_task = asyncio.create_task(self._synaptic_communication_loop())
            tasks.append(synapse_task)
        
        # Wait for all threads to complete
        results = await asyncio.gather(*tasks[:-1] if self.enable_synapses else tasks)
        
        # Cancel synaptic communication if still running
        if self.enable_synapses:
            synapse_task.cancel()
            try:
                await synapse_task
            except asyncio.CancelledError:
                pass
        
        # Apply quantum interference and collapse
        collapsed_result = self._collapse_quantum_state(CollapseStrategy.INTERFERENCE)
        
        return {
            'collapsed_result': collapsed_result,
            'thread_results': results,
            'quantum_metrics': self._calculate_quantum_metrics()
        }
    
    async def _execute_single_thread(
        self,
        thread_id: str,
        task_executor,
        task_description: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single quantum thread."""
        thread = self.threads[thread_id]
        thread.start_time = datetime.now()
        thread.state = QuantumState.ENTANGLED
        
        try:
            # Merge variation with context
            execution_context = {**context, **thread.variation}
            
            # Execute the task
            result = await task_executor(
                task_description,
                execution_context
            )
            
            thread.result = result
            thread.metrics = self._extract_metrics(result)
            
            # Update amplitude based on success
            success_score = thread.metrics.get('success_score', 0.5)
            thread.amplitude = complex(success_score, thread.phase)
            
            # Share results through synapses if successful
            if self.enable_synapses and success_score > 0.7:
                await self._propagate_through_synapses(thread_id, result)
            
        except Exception as e:
            logger.error(f"Thread {thread_id} failed: {e}")
            thread.error = str(e)
            thread.amplitude = complex(0.1, 0)  # Reduce amplitude for failed threads
        
        finally:
            thread.end_time = datetime.now()
            thread.state = QuantumState.COLLAPSED
        
        return {
            'thread_id': thread_id,
            'result': thread.result,
            'metrics': thread.metrics,
            'error': thread.error,
            'execution_time': thread.execution_time
        }
    
    async def _synaptic_communication_loop(self):
        """Continuous synaptic communication between threads."""
        while True:
            try:
                # Check for signals to propagate
                for thread_id, thread in self.threads.items():
                    if thread.state == QuantumState.ENTANGLED and thread.result:
                        # Share partial results with connected threads
                        for synapse_id in self.synapse_map[thread_id]:
                            synapse = self.synapses[synapse_id]
                            
                            # Propagate signal based on connection weight
                            if np.random.random() < synapse.weight:
                                target_thread = self.threads.get(synapse.target_thread)
                                if target_thread and target_thread.state == QuantumState.ENTANGLED:
                                    # Share information
                                    signal = {
                                        'source': thread_id,
                                        'data': thread.result,
                                        'strength': synapse.weight
                                    }
                                    synapse.last_signal = signal
                                    synapse.strengthen()  # Hebbian learning
                                    
                                    # Influence target thread's amplitude
                                    influence = synapse.weight * 0.1
                                    target_thread.amplitude *= complex(1 + influence, 0)
                
                await asyncio.sleep(0.1)  # Communication frequency
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Synaptic communication error: {e}")
    
    async def _propagate_through_synapses(self, source_thread_id: str, data: Any):
        """Propagate information through synaptic connections."""
        for synapse_id in self.synapse_map[source_thread_id]:
            synapse = self.synapses[synapse_id]
            target_thread = self.threads.get(synapse.target_thread)
            
            if target_thread and target_thread.state in [QuantumState.SUPERPOSITION, QuantumState.ENTANGLED]:
                # Influence target based on synapse weight
                synapse.last_signal = data
                synapse.strengthen()
                
                # Quantum entanglement effect
                if source_thread_id in target_thread.entangled_with:
                    # Stronger influence for entangled threads
                    target_thread.amplitude *= complex(1.2, 0)
    
    def _collapse_quantum_state(self, strategy: CollapseStrategy) -> Dict[str, Any]:
        """
        Collapse quantum superposition to a single outcome.
        
        Args:
            strategy: Collapse strategy to use
            
        Returns:
            Collapsed result
        """
        if strategy == CollapseStrategy.INTERFERENCE:
            return self._collapse_with_interference()
        elif strategy == CollapseStrategy.BEST_SCORE:
            return self._collapse_best_score()
        elif strategy == CollapseStrategy.CONSENSUS:
            return self._collapse_consensus()
        elif strategy == CollapseStrategy.WEIGHTED:
            return self._collapse_weighted()
        else:
            return self._collapse_first_success()
    
    def _collapse_with_interference(self) -> Dict[str, Any]:
        """Collapse using quantum interference patterns."""
        threads = list(self.threads.values())
        n = len(threads)
        
        if n == 0:
            return {'error': 'No threads to collapse'}
        
        # Calculate interference-enhanced probabilities
        probabilities = np.zeros(n)
        
        for i, thread in enumerate(threads):
            base_prob = thread.probability
            
            # Apply interference from other threads
            interference = 0.0
            for j, other_thread in enumerate(threads):
                if i != j and self.interference_matrix is not None:
                    interference += np.real(
                        self.interference_matrix[i, j] * 
                        other_thread.amplitude * 
                        np.conj(thread.amplitude)
                    )
            
            # Enhance probability with constructive interference
            probabilities[i] = base_prob * (1 + 0.5 * np.tanh(interference))
        
        # Normalize probabilities
        probabilities = probabilities / probabilities.sum()
        
        # Select thread based on enhanced probabilities
        selected_idx = np.argmax(probabilities)
        selected_thread = threads[selected_idx]
        
        return {
            'thread_id': selected_thread.thread_id,
            'result': selected_thread.result,
            'probability': probabilities[selected_idx],
            'metrics': selected_thread.metrics,
            'collapse_method': 'quantum_interference'
        }
    
    def _collapse_best_score(self) -> Dict[str, Any]:
        """Collapse to thread with best score."""
        best_thread = max(
            self.threads.values(),
            key=lambda t: t.metrics.get('success_score', 0) if t.result else -1
        )
        
        return {
            'thread_id': best_thread.thread_id,
            'result': best_thread.result,
            'metrics': best_thread.metrics,
            'collapse_method': 'best_score'
        }
    
    def _collapse_consensus(self) -> Dict[str, Any]:
        """Collapse to consensus result."""
        # Group threads by similar results
        result_groups = defaultdict(list)
        
        for thread in self.threads.values():
            if thread.result:
                # Simple grouping by result type/structure
                key = str(type(thread.result))
                result_groups[key].append(thread)
        
        if not result_groups:
            return {'error': 'No successful threads for consensus'}
        
        # Find largest group (consensus)
        largest_group = max(result_groups.values(), key=len)
        
        # Select best from consensus group
        best_thread = max(
            largest_group,
            key=lambda t: t.metrics.get('success_score', 0)
        )
        
        return {
            'thread_id': best_thread.thread_id,
            'result': best_thread.result,
            'consensus_size': len(largest_group),
            'total_threads': len(self.threads),
            'metrics': best_thread.metrics,
            'collapse_method': 'consensus'
        }
    
    def _collapse_weighted(self) -> Dict[str, Any]:
        """Collapse with weighted combination of results."""
        # Combine results weighted by success scores
        weighted_results = []
        total_weight = 0.0
        
        for thread in self.threads.values():
            if thread.result:
                weight = thread.metrics.get('success_score', 0.5)
                weighted_results.append({
                    'thread_id': thread.thread_id,
                    'result': thread.result,
                    'weight': weight
                })
                total_weight += weight
        
        if not weighted_results:
            return {'error': 'No successful threads for weighted collapse'}
        
        # Normalize weights
        for item in weighted_results:
            item['weight'] /= total_weight
        
        return {
            'weighted_components': weighted_results,
            'collapse_method': 'weighted',
            'total_weight': total_weight
        }
    
    def _collapse_first_success(self) -> Dict[str, Any]:
        """Collapse to first successful result."""
        for thread in self.threads.values():
            if thread.result and not thread.error:
                return {
                    'thread_id': thread.thread_id,
                    'result': thread.result,
                    'metrics': thread.metrics,
                    'collapse_method': 'first_success'
                }
        
        return {'error': 'No successful threads'}
    
    def _extract_metrics(self, result: Any) -> Dict[str, float]:
        """Extract metrics from execution result."""
        metrics = {}
        
        if isinstance(result, dict):
            metrics['success_score'] = result.get('success', 0.5)
            metrics['quality'] = result.get('quality', 0.5)
            metrics['cost'] = result.get('cost', 0.01)
            metrics['tokens'] = result.get('tokens', 0)
        else:
            # Default metrics
            metrics['success_score'] = 0.5
            
        return metrics
    
    def _calculate_quantum_metrics(self) -> Dict[str, Any]:
        """Calculate quantum execution metrics."""
        total_threads = len(self.threads)
        successful = sum(1 for t in self.threads.values() if t.result and not t.error)
        
        # Calculate entanglement strength
        entanglement = 0.0
        for thread in self.threads.values():
            entanglement += len(thread.entangled_with) / max(total_threads - 1, 1)
        entanglement /= max(total_threads, 1)
        
        # Calculate synaptic strength
        synaptic_strength = 0.0
        if self.synapses:
            synaptic_strength = sum(s.weight for s in self.synapses.values()) / len(self.synapses)
        
        return {
            'total_threads': total_threads,
            'successful_threads': successful,
            'success_rate': successful / max(total_threads, 1),
            'entanglement_strength': entanglement,
            'synaptic_strength': synaptic_strength,
            'total_synapses': len(self.synapses),
            'average_execution_time': np.mean([t.execution_time for t in self.threads.values()])
        }
    
    def learn_from_execution(self, result: Dict[str, Any]):
        """Learn from execution results to improve future performance."""
        # Store in history
        self.execution_history.append(result)
        
        # If successful, store pattern
        if result.get('collapsed_result', {}).get('result'):
            self.success_patterns.append({
                'variations': [t.variation for t in self.threads.values()],
                'metrics': result.get('quantum_metrics', {}),
                'timestamp': datetime.now().isoformat()
            })
        
        # Adjust synaptic weights based on success
        for synapse in self.synapses.values():
            source_thread = self.threads.get(synapse.source_thread)
            target_thread = self.threads.get(synapse.target_thread)
            
            if source_thread and target_thread:
                # Strengthen connections between successful threads
                if source_thread.result and target_thread.result:
                    source_success = source_thread.metrics.get('success_score', 0)
                    target_success = target_thread.metrics.get('success_score', 0)
                    
                    if source_success > 0.7 and target_success > 0.7:
                        synapse.strengthen(0.2)
                    elif source_success < 0.3 or target_success < 0.3:
                        synapse.weaken(0.1)