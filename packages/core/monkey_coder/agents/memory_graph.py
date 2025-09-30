"""
Memory graph system for structured entity-relationship storage.

This module provides a graph-based memory system that enables agents to:
1. Store structured entities and relationships
2. Query connections across multiple hops
3. Reason about complex dependencies and patterns
4. Maintain traceability of all graph operations
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid
import logging

logger = logging.getLogger(__name__)


# Core Graph Types
@dataclass
class Node:
    """A node in the memory graph representing an entity"""
    id: str
    type: str  # Entity type (e.g., "Service", "EnvVar", "Incident")
    props: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None  # Source pointer for traceability
    
    def __post_init__(self):
        if not self.id:
            self.id = f"{self.type.lower()}:{uuid.uuid4().hex[:8]}"


@dataclass
class Edge:
    """An edge in the memory graph representing a relationship"""
    type: str  # Relationship type (e.g., "SERVICE_REQUIRES_ENVVAR")
    from_id: str  # Source node ID
    to_id: str    # Target node ID
    props: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None  # Source pointer for traceability
    
    @property
    def id(self) -> str:
        """Generate a unique edge identifier"""
        return f"{self.type}:{self.from_id}:{self.to_id}"


class QueryStrategy(Enum):
    """Strategies for graph traversal and querying"""
    BREADTH_FIRST = "breadth_first"
    DEPTH_FIRST = "depth_first"
    SHORTEST_PATH = "shortest_path"


@dataclass
class QueryResult:
    """Result of a graph query operation"""
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    paths: List[List[str]] = field(default_factory=list)  # Node ID paths
    query_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class MemoryGraph:
    """In-memory graph storage with query capabilities"""
    
    def __init__(self):
        self._nodes: Dict[str, Node] = {}
        self._edges: Dict[str, Edge] = {}
        self._adjacency_out: Dict[str, Set[str]] = {}  # node_id -> set of outgoing edge_ids
        self._adjacency_in: Dict[str, Set[str]] = {}   # node_id -> set of incoming edge_ids
        self._type_index: Dict[str, Set[str]] = {}     # node_type -> set of node_ids
        
    # CRUD Operations
    def add_node(self, node: Node) -> bool:
        """Add a node to the graph"""
        try:
            if node.id in self._nodes:
                logger.warning(f"Node {node.id} already exists, updating")
            
            self._nodes[node.id] = node
            
            # Update type index
            if node.type not in self._type_index:
                self._type_index[node.type] = set()
            self._type_index[node.type].add(node.id)
            
            # Initialize adjacency sets
            if node.id not in self._adjacency_out:
                self._adjacency_out[node.id] = set()
            if node.id not in self._adjacency_in:
                self._adjacency_in[node.id] = set()
                
            logger.debug(f"Added node: {node.id} (type: {node.type})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add node {node.id}: {e}")
            return False
    
    def add_edge(self, edge: Edge) -> bool:
        """Add an edge to the graph"""
        try:
            # Verify nodes exist
            if edge.from_id not in self._nodes:
                logger.error(f"Source node {edge.from_id} does not exist")
                return False
            if edge.to_id not in self._nodes:
                logger.error(f"Target node {edge.to_id} does not exist")
                return False
            
            edge_id = edge.id
            self._edges[edge_id] = edge
            
            # Update adjacency lists
            self._adjacency_out[edge.from_id].add(edge_id)
            self._adjacency_in[edge.to_id].add(edge_id)
            
            logger.debug(f"Added edge: {edge.type} from {edge.from_id} to {edge.to_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add edge {edge.id}: {e}")
            return False
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID"""
        return self._nodes.get(node_id)
    
    def get_nodes_by_type(self, node_type: str) -> List[Node]:
        """Get all nodes of a specific type"""
        node_ids = self._type_index.get(node_type, set())
        return [self._nodes[node_id] for node_id in node_ids]
    
    def get_edges_from(self, node_id: str) -> List[Edge]:
        """Get all outgoing edges from a node"""
        edge_ids = self._adjacency_out.get(node_id, set())
        return [self._edges[edge_id] for edge_id in edge_ids]
    
    def get_edges_to(self, node_id: str) -> List[Edge]:
        """Get all incoming edges to a node"""
        edge_ids = self._adjacency_in.get(node_id, set())
        return [self._edges[edge_id] for edge_id in edge_ids]
    
    def remove_node(self, node_id: str) -> bool:
        """Remove a node and all its edges"""
        try:
            if node_id not in self._nodes:
                return False
            
            node = self._nodes[node_id]
            
            # Remove from type index
            if node.type in self._type_index:
                self._type_index[node.type].discard(node_id)
            
            # Remove all edges connected to this node
            outgoing_edges = list(self._adjacency_out.get(node_id, set()))
            incoming_edges = list(self._adjacency_in.get(node_id, set()))
            
            for edge_id in outgoing_edges + incoming_edges:
                if edge_id in self._edges:
                    edge = self._edges[edge_id]
                    self._remove_edge_references(edge)
                    del self._edges[edge_id]
            
            # Remove node
            del self._nodes[node_id]
            self._adjacency_out.pop(node_id, None)
            self._adjacency_in.pop(node_id, None)
            
            logger.debug(f"Removed node: {node_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove node {node_id}: {e}")
            return False
    
    def _remove_edge_references(self, edge: Edge):
        """Remove edge references from adjacency lists"""
        edge_id = edge.id
        if edge.from_id in self._adjacency_out:
            self._adjacency_out[edge.from_id].discard(edge_id)
        if edge.to_id in self._adjacency_in:
            self._adjacency_in[edge.to_id].discard(edge_id)
    
    # Query Operations
    def neighbors(self, node_id: str, edge_type: Optional[str] = None, 
                  direction: str = "out") -> List[Node]:
        """Get neighboring nodes"""
        neighbors = []
        
        if direction == "out":
            edges = self.get_edges_from(node_id)
        elif direction == "in":
            edges = self.get_edges_to(node_id)
        else:  # both
            edges = self.get_edges_from(node_id) + self.get_edges_to(node_id)
        
        for edge in edges:
            if edge_type and edge.type != edge_type:
                continue
                
            if direction == "out":
                neighbor_id = edge.to_id
            elif direction == "in":
                neighbor_id = edge.from_id
            else:
                neighbor_id = edge.to_id if edge.from_id == node_id else edge.from_id
            
            neighbor = self.get_node(neighbor_id)
            if neighbor and neighbor not in neighbors:
                neighbors.append(neighbor)
        
        return neighbors
    
    def query_subgraph(self, start_node_id: str, max_hops: int = 2, 
                      edge_types: Optional[List[str]] = None) -> QueryResult:
        """Get subgraph within N hops of a starting node"""
        start_time = datetime.now()
        
        visited_nodes = set()
        visited_edges = set()
        queue = [(start_node_id, 0)]  # (node_id, hop_count)
        
        result_nodes = []
        result_edges = []
        
        while queue:
            current_id, hops = queue.pop(0)
            
            if hops > max_hops or current_id in visited_nodes:
                continue
                
            visited_nodes.add(current_id)
            current_node = self.get_node(current_id)
            if current_node:
                result_nodes.append(current_node)
            
            if hops < max_hops:
                # Add outgoing edges
                for edge in self.get_edges_from(current_id):
                    if edge_types and edge.type not in edge_types:
                        continue
                    if edge.id not in visited_edges:
                        visited_edges.add(edge.id)
                        result_edges.append(edge)
                        queue.append((edge.to_id, hops + 1))
                
                # Add incoming edges
                for edge in self.get_edges_to(current_id):
                    if edge_types and edge.type not in edge_types:
                        continue
                    if edge.id not in visited_edges:
                        visited_edges.add(edge.id)
                        result_edges.append(edge)
                        queue.append((edge.from_id, hops + 1))
        
        query_time = (datetime.now() - start_time).total_seconds()
        
        return QueryResult(
            nodes=result_nodes,
            edges=result_edges,
            query_time=query_time,
            metadata={"start_node": start_node_id, "max_hops": max_hops}
        )
    
    def find_paths(self, from_id: str, to_id: str, max_depth: int = 5) -> List[List[str]]:
        """Find paths between two nodes"""
        paths = []
        
        def dfs(current_id: str, target_id: str, path: List[str], visited: Set[str]):
            if len(path) > max_depth:
                return
            
            if current_id == target_id:
                paths.append(path.copy())
                return
            
            if current_id in visited:
                return
                
            visited.add(current_id)
            
            for edge in self.get_edges_from(current_id):
                next_id = edge.to_id
                if next_id not in visited:
                    path.append(next_id)
                    dfs(next_id, target_id, path, visited)
                    path.pop()
            
            visited.remove(current_id)
        
        dfs(from_id, to_id, [from_id], set())
        return paths
    
    # Utility Methods
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        return {
            "node_count": len(self._nodes),
            "edge_count": len(self._edges),
            "node_types": list(self._type_index.keys()),
            "type_counts": {t: len(ids) for t, ids in self._type_index.items()},
            "edge_types": list(set(edge.type for edge in self._edges.values()))
        }
    
    def clear(self):
        """Clear all graph data"""
        self._nodes.clear()
        self._edges.clear()
        self._adjacency_out.clear()
        self._adjacency_in.clear()
        self._type_index.clear()
        logger.debug("Graph cleared")


# Specialized query functions for common patterns
def missing_env_vars_for_service(graph: MemoryGraph, service_id: str) -> List[Node]:
    """Find missing environment variables for a service"""
    # Get required env vars
    required_edges = [e for e in graph.get_edges_from(service_id) 
                     if e.type == "SERVICE_REQUIRES_ENVVAR"]
    required_vars = [graph.get_node(e.to_id) for e in required_edges]
    
    # In a real system, we'd check against actual environment
    # For demo, assume missing if not explicitly marked as present
    missing = []
    for var in required_vars:
        if var and not var.props.get("present", False):
            missing.append(var)
    
    return missing


def related_incidents_for_service(graph: MemoryGraph, service_id: str) -> List[Node]:
    """Find incidents related to a service"""
    incidents = []
    
    # Direct incidents
    incident_edges = [e for e in graph.get_edges_to(service_id) 
                     if e.type == "INCIDENT_IMPACTS_SERVICE"]
    for edge in incident_edges:
        incident = graph.get_node(edge.from_id)
        if incident:
            incidents.append(incident)
    
    # Incidents via missing env vars (multi-hop reasoning)
    missing_vars = missing_env_vars_for_service(graph, service_id)
    for var in missing_vars:
        var_incidents = [e for e in graph.get_edges_to(var.id) 
                        if e.type == "INCIDENT_CAUSED_BY_ENVVAR"]
        for edge in var_incidents:
            incident = graph.get_node(edge.from_id)
            if incident and incident not in incidents:
                incidents.append(incident)
    
    return incidents