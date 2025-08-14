"""
Quantum Synapse Layer for Inter-Branch Communication

This module implements a synapse layer that enables quantum branches to share
information, insights, and partial results, fostering emergent creativity and
collaborative problem-solving.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable
from uuid import uuid4

import numpy as np

logger = logging.getLogger(__name__)


class InsightType(Enum):
    """Types of insights that can be shared between branches."""
    
    PATTERN = "pattern"                # Discovered pattern or structure
    OPTIMIZATION = "optimization"      # Performance optimization
    CONSTRAINT = "constraint"          # Identified constraint or limitation
    OPPORTUNITY = "opportunity"        # Creative opportunity
    WARNING = "warning"               # Potential issue or risk
    DISCOVERY = "discovery"           # Novel finding or approach
    SYNTHESIS = "synthesis"           # Combined insight from multiple sources


@dataclass
class Insight:
    """Represents an insight discovered by a quantum branch."""
    
    id: str
    branch_id: str
    type: InsightType
    content: Any
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if not self.id:
            self.id = f"insight_{uuid4().hex[:12]}"
        if not self.timestamp:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert insight to dictionary representation."""
        data = asdict(self)
        data['type'] = self.type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Insight':
        """Create insight from dictionary representation."""
        data['type'] = InsightType(data['type'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class SharedMemoryBus:
    """
    Asynchronous message bus for sharing information between quantum branches.
    Implements publish-subscribe pattern with topic-based routing.
    """
    
    def __init__(self, max_queue_size: int = 1000):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.active = False
        self.processing_task: Optional[asyncio.Task] = None
        
        logger.info(f"SharedMemoryBus initialized with max_queue_size={max_queue_size}")
    
    async def start(self):
        """Start the message bus processing."""
        self.active = True
        self.processing_task = asyncio.create_task(self._process_messages())
        logger.info("SharedMemoryBus started")
    
    async def stop(self):
        """Stop the message bus processing."""
        self.active = False
        if self.processing_task:
            await self.processing_task
        logger.info("SharedMemoryBus stopped")
    
    async def _process_messages(self):
        """Process messages from the queue."""
        while self.active:
            try:
                if not self.message_queue.empty():
                    topic, message = await self.message_queue.get()
                    await self._deliver_message(topic, message)
                else:
                    await asyncio.sleep(0.01)  # Small delay when queue is empty
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    async def _deliver_message(self, topic: str, message: Any):
        """Deliver message to all subscribers of a topic."""
        # Direct topic subscribers
        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                try:
                    await callback(message)
                except Exception as e:
                    logger.error(f"Error in subscriber callback for topic {topic}: {e}")
        
        # Wildcard subscribers (e.g., "branch.*" matches all branch topics)
        for pattern, callbacks in self.subscribers.items():
            if self._matches_pattern(topic, pattern):
                for callback in callbacks:
                    try:
                        await callback(message)
                    except Exception as e:
                        logger.error(f"Error in wildcard subscriber for pattern {pattern}: {e}")
    
    def _matches_pattern(self, topic: str, pattern: str) -> bool:
        """Check if topic matches a wildcard pattern."""
        if '*' not in pattern:
            return topic == pattern
        
        # Simple wildcard matching (e.g., "branch.*" matches "branch.123")
        pattern_parts = pattern.split('.')
        topic_parts = topic.split('.')
        
        if len(pattern_parts) != len(topic_parts):
            return False
        
        for p, t in zip(pattern_parts, topic_parts):
            if p != '*' and p != t:
                return False
        
        return True
    
    async def publish(self, topic: str, message: Any):
        """Publish a message to a topic."""
        if not self.active:
            logger.warning("Cannot publish to inactive SharedMemoryBus")
            return
        
        try:
            await self.message_queue.put((topic, message))
            logger.debug(f"Published message to topic: {topic}")
        except asyncio.QueueFull:
            logger.warning(f"Message queue full, dropping message for topic: {topic}")
    
    def subscribe(self, topic: str, callback: Callable):
        """Subscribe to messages on a topic."""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
        logger.debug(f"Subscribed to topic: {topic}")
    
    def unsubscribe(self, topic: str, callback: Callable):
        """Unsubscribe from a topic."""
        if topic in self.subscribers and callback in self.subscribers[topic]:
            self.subscribers[topic].remove(callback)
            if not self.subscribers[topic]:
                del self.subscribers[topic]
            logger.debug(f"Unsubscribed from topic: {topic}")


class InsightPool:
    """
    Pool for storing and retrieving insights discovered by quantum branches.
    Provides pattern recognition and insight synthesis capabilities.
    """
    
    def __init__(self, max_insights: int = 10000):
        self.insights: Dict[str, Insight] = {}
        self.insights_by_type: Dict[InsightType, List[str]] = {}
        self.insights_by_branch: Dict[str, List[str]] = {}
        self.max_insights = max_insights
        
        logger.info(f"InsightPool initialized with max_insights={max_insights}")
    
    async def add(self, insight: Insight):
        """Add an insight to the pool."""
        # Limit pool size by removing oldest insights
        if len(self.insights) >= self.max_insights:
            oldest_id = min(self.insights.keys(), 
                          key=lambda k: self.insights[k].timestamp)
            await self.remove(oldest_id)
        
        # Store insight
        self.insights[insight.id] = insight
        
        # Index by type
        if insight.type not in self.insights_by_type:
            self.insights_by_type[insight.type] = []
        self.insights_by_type[insight.type].append(insight.id)
        
        # Index by branch
        if insight.branch_id not in self.insights_by_branch:
            self.insights_by_branch[insight.branch_id] = []
        self.insights_by_branch[insight.branch_id].append(insight.id)
        
        logger.debug(f"Added insight {insight.id} from branch {insight.branch_id}")
    
    async def remove(self, insight_id: str):
        """Remove an insight from the pool."""
        if insight_id not in self.insights:
            return
        
        insight = self.insights[insight_id]
        
        # Remove from indices
        if insight.type in self.insights_by_type:
            self.insights_by_type[insight.type].remove(insight_id)
        if insight.branch_id in self.insights_by_branch:
            self.insights_by_branch[insight.branch_id].remove(insight_id)
        
        # Remove insight
        del self.insights[insight_id]
        
        logger.debug(f"Removed insight {insight_id}")
    
    async def get_by_type(self, insight_type: InsightType) -> List[Insight]:
        """Get all insights of a specific type."""
        insight_ids = self.insights_by_type.get(insight_type, [])
        return [self.insights[id] for id in insight_ids if id in self.insights]
    
    async def get_by_branch(self, branch_id: str) -> List[Insight]:
        """Get all insights from a specific branch."""
        insight_ids = self.insights_by_branch.get(branch_id, [])
        return [self.insights[id] for id in insight_ids if id in self.insights]
    
    async def get_recent(self, limit: int = 10) -> List[Insight]:
        """Get the most recent insights."""
        sorted_insights = sorted(
            self.insights.values(),
            key=lambda i: i.timestamp,
            reverse=True
        )
        return sorted_insights[:limit]
    
    async def find_patterns(self, min_confidence: float = 0.7) -> List[Dict[str, Any]]:
        """Find patterns in the collected insights."""
        patterns = []
        
        # Group insights by similar content
        insight_groups = {}
        for insight in self.insights.values():
            if insight.confidence >= min_confidence:
                # Simple content hashing for grouping (can be made more sophisticated)
                content_key = str(insight.content)[:50]  # Simplified grouping
                if content_key not in insight_groups:
                    insight_groups[content_key] = []
                insight_groups[content_key].append(insight)
        
        # Identify patterns from groups
        for content_key, group in insight_groups.items():
            if len(group) >= 2:  # Pattern requires at least 2 similar insights
                patterns.append({
                    'pattern_id': f"pattern_{uuid4().hex[:12]}",
                    'insights': [i.id for i in group],
                    'branches': list(set(i.branch_id for i in group)),
                    'confidence': np.mean([i.confidence for i in group]),
                    'type': group[0].type.value,
                    'discovered_at': datetime.utcnow().isoformat()
                })
        
        return patterns


class PatternRecognizer:
    """
    Recognizes patterns across partial results from quantum branches.
    Uses statistical and ML techniques to identify emergent patterns.
    """
    
    def __init__(self):
        self.patterns_cache = {}
        self.pattern_history = []
        
        logger.info("PatternRecognizer initialized")
    
    async def extract(self, partial_results: List[Any]) -> List[Dict[str, Any]]:
        """Extract patterns from partial results."""
        patterns = []
        
        # Statistical pattern detection
        if len(partial_results) >= 3:
            # Frequency analysis
            frequency_pattern = await self._analyze_frequency(partial_results)
            if frequency_pattern:
                patterns.append(frequency_pattern)
            
            # Sequence pattern detection
            sequence_pattern = await self._detect_sequences(partial_results)
            if sequence_pattern:
                patterns.append(sequence_pattern)
            
            # Clustering pattern detection
            cluster_pattern = await self._detect_clusters(partial_results)
            if cluster_pattern:
                patterns.append(cluster_pattern)
        
        # Cache patterns for future reference
        for pattern in patterns:
            pattern_id = pattern.get('id', f"pattern_{uuid4().hex[:12]}")
            self.patterns_cache[pattern_id] = pattern
            self.pattern_history.append(pattern_id)
        
        return patterns
    
    async def _analyze_frequency(self, results: List[Any]) -> Optional[Dict[str, Any]]:
        """Analyze frequency patterns in results."""
        # Simplified frequency analysis (can be enhanced with actual ML)
        frequency_map = {}
        for result in results:
            key = str(result)[:100]  # Simplified key generation
            frequency_map[key] = frequency_map.get(key, 0) + 1
        
        # Find dominant patterns
        if frequency_map:
            dominant_key = max(frequency_map, key=frequency_map.get)
            if frequency_map[dominant_key] >= len(results) * 0.3:  # 30% threshold
                return {
                    'id': f"freq_{uuid4().hex[:12]}",
                    'type': 'frequency',
                    'dominant_pattern': dominant_key,
                    'frequency': frequency_map[dominant_key] / len(results),
                    'confidence': frequency_map[dominant_key] / len(results)
                }
        
        return None
    
    async def _detect_sequences(self, results: List[Any]) -> Optional[Dict[str, Any]]:
        """Detect sequential patterns in results."""
        # Simplified sequence detection (can be enhanced)
        sequences = []
        for i in range(len(results) - 1):
            # Check if results follow a pattern
            if hasattr(results[i], '__dict__') and hasattr(results[i+1], '__dict__'):
                # Simple progression check
                sequences.append((results[i], results[i+1]))
        
        if sequences:
            return {
                'id': f"seq_{uuid4().hex[:12]}",
                'type': 'sequence',
                'sequence_count': len(sequences),
                'confidence': len(sequences) / max(1, len(results) - 1)
            }
        
        return None
    
    async def _detect_clusters(self, results: List[Any]) -> Optional[Dict[str, Any]]:
        """Detect clustering patterns in results."""
        # Simplified clustering (can be enhanced with actual clustering algorithms)
        clusters = {}
        for result in results:
            # Simple clustering by result type/category
            cluster_key = type(result).__name__
            if cluster_key not in clusters:
                clusters[cluster_key] = []
            clusters[cluster_key].append(result)
        
        if len(clusters) > 1:
            return {
                'id': f"cluster_{uuid4().hex[:12]}",
                'type': 'cluster',
                'cluster_count': len(clusters),
                'largest_cluster': max(len(c) for c in clusters.values()),
                'confidence': max(len(c) for c in clusters.values()) / len(results)
            }
        
        return None


class CreativeSynthesizer:
    """
    Synthesizes creative solutions by combining patterns and insights.
    Uses various creativity techniques to generate novel approaches.
    """
    
    def __init__(self):
        self.synthesis_strategies = {
            'combination': self._combine_patterns,
            'transformation': self._transform_patterns,
            'analogy': self._create_analogies,
            'inversion': self._invert_patterns,
            'abstraction': self._abstract_patterns
        }
        
        logger.info("CreativeSynthesizer initialized with strategies: " + 
                   ", ".join(self.synthesis_strategies.keys()))
    
    async def generate(self, patterns: List[Dict[str, Any]]) -> List[Any]:
        """Generate creative solutions from patterns."""
        creative_solutions = []
        
        # Apply different synthesis strategies
        for strategy_name, strategy_func in self.synthesis_strategies.items():
            try:
                solution = await strategy_func(patterns)
                if solution:
                    creative_solutions.append({
                        'strategy': strategy_name,
                        'solution': solution,
                        'creativity_score': await self._score_creativity(solution),
                        'timestamp': datetime.utcnow().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error in synthesis strategy {strategy_name}: {e}")
        
        # Sort by creativity score
        creative_solutions.sort(key=lambda x: x['creativity_score'], reverse=True)
        
        return creative_solutions
    
    async def _combine_patterns(self, patterns: List[Dict[str, Any]]) -> Any:
        """Combine multiple patterns into a new solution."""
        if len(patterns) < 2:
            return None
        
        # Simple combination (can be enhanced with actual combination logic)
        combined = {
            'type': 'combined',
            'source_patterns': [p.get('id', 'unknown') for p in patterns],
            'confidence': np.mean([p.get('confidence', 0.5) for p in patterns]),
            'elements': []
        }
        
        for pattern in patterns:
            combined['elements'].append(pattern)
        
        return combined
    
    async def _transform_patterns(self, patterns: List[Dict[str, Any]]) -> Any:
        """Transform patterns into new forms."""
        if not patterns:
            return None
        
        # Simple transformation (can be enhanced)
        transformed = {
            'type': 'transformed',
            'original_pattern': patterns[0].get('id', 'unknown'),
            'transformation': 'scaled',
            'scale_factor': np.random.uniform(0.5, 2.0),
            'confidence': patterns[0].get('confidence', 0.5) * 0.9
        }
        
        return transformed
    
    async def _create_analogies(self, patterns: List[Dict[str, Any]]) -> Any:
        """Create analogies from patterns."""
        if not patterns:
            return None
        
        # Simple analogy creation (can be enhanced with actual analogy generation)
        analogy = {
            'type': 'analogy',
            'source_domain': patterns[0].get('type', 'unknown'),
            'target_domain': 'creative_solution',
            'mapping': {
                'structure': 'preserved',
                'function': 'adapted',
                'context': 'transformed'
            },
            'confidence': patterns[0].get('confidence', 0.5) * 0.8
        }
        
        return analogy
    
    async def _invert_patterns(self, patterns: List[Dict[str, Any]]) -> Any:
        """Invert patterns to create opposite solutions."""
        if not patterns:
            return None
        
        # Simple inversion (can be enhanced)
        inverted = {
            'type': 'inverted',
            'original_pattern': patterns[0].get('id', 'unknown'),
            'inversion_type': 'logical',
            'confidence': patterns[0].get('confidence', 0.5) * 0.7
        }
        
        return inverted
    
    async def _abstract_patterns(self, patterns: List[Dict[str, Any]]) -> Any:
        """Abstract patterns to higher-level concepts."""
        if not patterns:
            return None
        
        # Simple abstraction (can be enhanced)
        abstracted = {
            'type': 'abstracted',
            'concrete_patterns': [p.get('id', 'unknown') for p in patterns],
            'abstraction_level': 'conceptual',
            'generalized_principle': 'pattern_based_solution',
            'confidence': np.mean([p.get('confidence', 0.5) for p in patterns])
        }
        
        return abstracted
    
    async def _score_creativity(self, solution: Any) -> float:
        """Score the creativity of a solution."""
        # Simple creativity scoring (can be enhanced with ML models)
        score = 0.5  # Base score
        
        if isinstance(solution, dict):
            # Novelty bonus
            if solution.get('type') in ['transformed', 'inverted', 'analogy']:
                score += 0.2
            
            # Complexity bonus
            if len(str(solution)) > 200:
                score += 0.1
            
            # Confidence factor
            confidence = solution.get('confidence', 0.5)
            score *= confidence
        
        return min(1.0, score)


class QuantumSynapse:
    """
    Main synapse class that coordinates quantum branch communication.
    Integrates all components for emergent creativity.
    """
    
    def __init__(self):
        self.shared_memory = SharedMemoryBus()
        self.insight_pool = InsightPool()
        self.pattern_recognizer = PatternRecognizer()
        self.creative_synthesizer = CreativeSynthesizer()
        self.active_branches: Set[str] = set()
        
        logger.info("QuantumSynapse initialized")
    
    async def initialize(self):
        """Initialize the synapse system."""
        await self.shared_memory.start()
        
        # Subscribe to all branch communications
        self.shared_memory.subscribe("branch.*", self._handle_branch_message)
        self.shared_memory.subscribe("insight.*", self._handle_insight_message)
        
        logger.info("QuantumSynapse initialized and ready")
    
    async def shutdown(self):
        """Shutdown the synapse system."""
        await self.shared_memory.stop()
        logger.info("QuantumSynapse shutdown complete")
    
    async def register_branch(self, branch_id: str):
        """Register a new quantum branch."""
        self.active_branches.add(branch_id)
        await self.shared_memory.publish(
            "system.branch_registered",
            {'branch_id': branch_id, 'timestamp': datetime.utcnow().isoformat()}
        )
        logger.debug(f"Registered branch: {branch_id}")
    
    async def unregister_branch(self, branch_id: str):
        """Unregister a quantum branch."""
        self.active_branches.discard(branch_id)
        await self.shared_memory.publish(
            "system.branch_unregistered",
            {'branch_id': branch_id, 'timestamp': datetime.utcnow().isoformat()}
        )
        logger.debug(f"Unregistered branch: {branch_id}")
    
    async def broadcast_insight(self, branch_id: str, insight: Insight):
        """Broadcast an insight from a branch to all other branches."""
        # Add to insight pool
        await self.insight_pool.add(insight)
        
        # Broadcast to all branches
        await self.shared_memory.publish(f"insight.{insight.type.value}", insight.to_dict())
        
        # Check for patterns when we have enough insights
        if len(self.insight_pool.insights) >= 5:
            patterns = await self.insight_pool.find_patterns()
            if patterns:
                await self._process_patterns(patterns)
        
        logger.debug(f"Broadcast insight {insight.id} from branch {branch_id}")
    
    async def synthesize_creative_solution(self, partial_results: List[Any]) -> List[Any]:
        """Synthesize creative solutions from partial results."""
        # Extract patterns
        patterns = await self.pattern_recognizer.extract(partial_results)
        
        # Generate creative solutions
        creative_solutions = await self.creative_synthesizer.generate(patterns)
        
        # Broadcast best solutions
        if creative_solutions:
            best_solution = creative_solutions[0]  # Highest creativity score
            await self.shared_memory.publish(
                "creative.solution",
                best_solution
            )
        
        return creative_solutions
    
    async def get_shared_context(self) -> Dict[str, Any]:
        """Get the current shared context across all branches."""
        return {
            'active_branches': list(self.active_branches),
            'total_insights': len(self.insight_pool.insights),
            'insight_types': {
                t.value: len(ids) 
                for t, ids in self.insight_pool.insights_by_type.items()
            },
            'recent_patterns': self.pattern_recognizer.pattern_history[-10:],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _handle_branch_message(self, message: Any):
        """Handle messages from branches."""
        logger.debug(f"Received branch message: {message}")
        # Process branch-specific messages
        # This can be extended based on specific message types
    
    async def _handle_insight_message(self, message: Any):
        """Handle insight messages."""
        logger.debug(f"Received insight message: {message}")
        # Process insight-specific messages
        # This can be extended based on specific insight types
    
    async def _process_patterns(self, patterns: List[Dict[str, Any]]):
        """Process discovered patterns."""
        for pattern in patterns:
            # Broadcast pattern discovery
            await self.shared_memory.publish(
                "pattern.discovered",
                pattern
            )
            
            # Generate creative solutions from pattern
            creative_solutions = await self.creative_synthesizer.generate([pattern])
            if creative_solutions:
                logger.info(f"Generated {len(creative_solutions)} creative solutions from pattern")


# Example usage
async def example_usage():
    """Example of using the quantum synapse system."""
    synapse = QuantumSynapse()
    await synapse.initialize()
    
    # Register branches
    branch1_id = "branch_001"
    branch2_id = "branch_002"
    await synapse.register_branch(branch1_id)
    await synapse.register_branch(branch2_id)
    
    # Create and broadcast insights
    insight1 = Insight(
        id="",
        branch_id=branch1_id,
        type=InsightType.PATTERN,
        content="Discovered recursive pattern in algorithm",
        confidence=0.85,
        timestamp=datetime.utcnow(),
        metadata={"algorithm": "quicksort", "optimization": "tail-recursion"}
    )
    await synapse.broadcast_insight(branch1_id, insight1)
    
    insight2 = Insight(
        id="",
        branch_id=branch2_id,
        type=InsightType.OPTIMIZATION,
        content="Found 30% performance improvement",
        confidence=0.92,
        timestamp=datetime.utcnow(),
        metadata={"technique": "memoization", "impact": "high"}
    )
    await synapse.broadcast_insight(branch2_id, insight2)
    
    # Synthesize creative solutions from partial results
    partial_results = [
        {"type": "algorithm", "performance": 0.8},
        {"type": "algorithm", "performance": 0.85},
        {"type": "optimization", "improvement": 0.3}
    ]
    creative_solutions = await synapse.synthesize_creative_solution(partial_results)
    
    print(f"Generated {len(creative_solutions)} creative solutions")
    for solution in creative_solutions[:3]:
        print(f"  Strategy: {solution['strategy']}, Score: {solution['creativity_score']:.2f}")
    
    # Get shared context
    context = await synapse.get_shared_context()
    print(f"\nShared Context:")
    print(f"  Active branches: {context['active_branches']}")
    print(f"  Total insights: {context['total_insights']}")
    print(f"  Insight types: {context['insight_types']}")
    
    # Cleanup
    await synapse.shutdown()


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())