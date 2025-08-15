"""
MCP (Model Context Protocol) Enhanced Integration Module

This module provides advanced MCP capabilities to aid development activities
as requested in the QA review. It implements:
- Enhanced server management and discovery
- Context-aware routing and load balancing
- Advanced prompt engineering with MCP assistance
- Intelligent task delegation and orchestration
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from urllib.parse import urljoin
import aiohttp
from pydantic import BaseModel


class TaskType(str, Enum):
    """MCP task types for intelligent routing"""
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    REVIEW = "review"


class Priority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ServerStatus(str, Enum):
    """MCP server status indicators"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


@dataclass
class MCPServer:
    """Enhanced MCP server configuration with capabilities"""
    id: str
    name: str
    url: str
    capabilities: List[str] = field(default_factory=list)
    status: ServerStatus = ServerStatus.INACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPTask:
    """MCP task definition with context and requirements"""
    id: str
    type: TaskType
    context: Dict[str, Any] = field(default_factory=dict)
    requirements: List[str] = field(default_factory=list)
    priority: Priority = Priority.MEDIUM


class MCPResponse(BaseModel):
    """MCP response with metadata tracking"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any]


class EnhancedMCPManager:
    """Enhanced MCP Manager with intelligent routing and orchestration"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.task_queue: List[MCPTask] = []
        self.routing_strategies: Dict[str, Callable] = {}
        self._initialize_default_strategies()
    
    async def register_server(self, config: Dict[str, Any]) -> None:
        """Register and validate MCP servers with capability discovery"""
        server = MCPServer(
            id=config.get('id', self._generate_server_id()),
            name=config.get('name', 'Unknown Server'),
            url=config.get('url', ''),
            capabilities=config.get('capabilities', []),
            status=ServerStatus.INACTIVE,
            metadata=config.get('metadata', {})
        )
        
        # Validate server capabilities
        await self._validate_server_capabilities(server)
        
        self.servers[server.id] = server
        print(f"Server registered: {server.name} ({server.id})")
    
    async def route_task(self, task: MCPTask) -> MCPResponse:
        """Intelligent task routing based on server capabilities and load"""
        suitable_servers = self._find_suitable_servers(task)
        
        if not suitable_servers:
            raise ValueError(f"No suitable servers found for task type: {task.type}")
        
        selected_server = await self._select_optimal_server(suitable_servers, task)
        return await self._execute_task(selected_server, task)
    
    async def process_batch(self, tasks: List[MCPTask]) -> List[MCPResponse]:
        """Batch processing with parallel execution and load balancing"""
        batches = self._create_optimal_batches(tasks)
        results: List[MCPResponse] = []
        
        for batch in batches:
            batch_tasks = [self.route_task(task) for task in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    results.append(MCPResponse(
                        success=False,
                        error=str(result),
                        metadata={
                            'server_id': 'unknown',
                            'latency': 0,
                            'tokens_used': 0,
                            'confidence': 0
                        }
                    ))
                else:
                    results.append(result)
        
        return results
    
    async def enhance_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Context-aware prompt enhancement using MCP insights"""
        analysis_task = MCPTask(
            id=self._generate_task_id(),
            type=TaskType.ANALYSIS,
            context={'prompt': prompt, **context},
            requirements=['prompt_enhancement', 'context_analysis'],
            priority=Priority.MEDIUM
        )
        
        try:
            response = await self.route_task(analysis_task)
            if response.success and response.data and 'enhanced_prompt' in response.data:
                return response.data['enhanced_prompt']
        except Exception as e:
            print(f"Prompt enhancement failed: {e}")
        
        return prompt  # Fallback to original if enhancement fails
    
    async def perform_code_review(self, code: str, language: str) -> Dict[str, Any]:
        """Intelligent code review with MCP-assisted analysis"""
        review_task = MCPTask(
            id=self._generate_task_id(),
            type=TaskType.REVIEW,
            context={'code': code, 'language': language},
            requirements=['code_analysis', 'quality_assessment', 'security_review'],
            priority=Priority.HIGH
        )
        
        try:
            response = await self.route_task(review_task)
            return response.data or {
                'suggestions': [],
                'issues': [],
                'score': 0,
                'improvements': []
            }
        except Exception as e:
            print(f"Code review failed: {e}")
            return {
                'suggestions': [],
                'issues': [f"Review failed: {e}"],
                'score': 0,
                'improvements': []
            }
    
    def _initialize_default_strategies(self) -> None:
        """Initialize default routing strategies"""
        
        def load_balanced(servers: List[MCPServer], task: MCPTask = None) -> MCPServer:
            return min(servers, key=lambda s: s.metadata.get('load', 0))
        
        def capability_match(servers: List[MCPServer], task: MCPTask) -> MCPServer:
            for server in servers:
                if all(req in server.capabilities for req in task.requirements):
                    return server
            return servers[0] if servers else None
        
        def performance_based(servers: List[MCPServer], task: MCPTask = None) -> MCPServer:
            return min(servers, key=lambda s: s.metadata.get('avg_latency', float('inf')))
        
        self.routing_strategies = {
            'load_balanced': load_balanced,
            'capability_match': capability_match,
            'performance': performance_based
        }
    
    async def _validate_server_capabilities(self, server: MCPServer) -> None:
        """Validate server capabilities through health check"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{server.url}/capabilities") as response:
                    if response.status == 200:
                        capabilities = await response.json()
                        server.capabilities = capabilities.get('supported', [])
                        server.status = ServerStatus.ACTIVE
                    else:
                        server.status = ServerStatus.ERROR
        except Exception as e:
            server.status = ServerStatus.ERROR
            server.metadata['last_error'] = str(e)
    
    def _find_suitable_servers(self, task: MCPTask) -> List[MCPServer]:
        """Find servers suitable for the given task"""
        return [
            server for server in self.servers.values()
            if server.status == ServerStatus.ACTIVE and
            any(req in server.capabilities for req in task.requirements)
        ]
    
    async def _select_optimal_server(self, servers: List[MCPServer], task: MCPTask) -> MCPServer:
        """Select the optimal server using routing strategy"""
        strategy = self.routing_strategies.get('capability_match')
        return strategy(servers, task) if strategy else servers[0]
    
    async def _execute_task(self, server: MCPServer, task: MCPTask) -> MCPResponse:
        """Execute task on selected server"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    'id': task.id,
                    'type': task.type.value,
                    'context': task.context,
                    'requirements': task.requirements,
                    'priority': task.priority.value
                }
                
                async with session.post(
                    f"{server.url}/execute",
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    result = await response.json()
                    latency = int((time.time() - start_time) * 1000)
                    
                    return MCPResponse(
                        success=response.status == 200,
                        data=result,
                        metadata={
                            'server_id': server.id,
                            'latency': latency,
                            'tokens_used': result.get('tokens_used', 0),
                            'confidence': result.get('confidence', 0)
                        }
                    )
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            return MCPResponse(
                success=False,
                error=str(e),
                metadata={
                    'server_id': server.id,
                    'latency': latency,
                    'tokens_used': 0,
                    'confidence': 0
                }
            )
    
    def _create_optimal_batches(self, tasks: List[MCPTask]) -> List[List[MCPTask]]:
        """Create optimal task batches for parallel execution"""
        batches: List[List[MCPTask]] = []
        task_groups: Dict[str, List[MCPTask]] = {}
        
        # Group tasks by priority and type
        for task in tasks:
            key = f"{task.priority.value}-{task.type.value}"
            if key not in task_groups:
                task_groups[key] = []
            task_groups[key].append(task)
        
        # Create batches with optimal size
        max_batch_size = 5
        for group in task_groups.values():
            for i in range(0, len(group), max_batch_size):
                batches.append(group[i:i + max_batch_size])
        
        return batches
    
    def _generate_server_id(self) -> str:
        """Generate unique server ID"""
        import uuid
        return f"server-{uuid.uuid4().hex[:8]}"
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        import uuid
        return f"task-{uuid.uuid4().hex[:8]}"


class MCPConfigManager:
    """Enhanced MCP Configuration Manager"""
    
    def __init__(self):
        self.config: Dict[str, Any] = {}
    
    async def load_config(self, config_path: Optional[str] = None) -> None:
        """Load configuration with validation and defaults"""
        default_config = {
            'servers': [],
            'routing': {
                'strategy': 'capability_match',
                'fallback': 'load_balanced'
            },
            'performance': {
                'timeout': 30000,
                'retries': 3,
                'max_concurrent_tasks': 10
            },
            'monitoring': {
                'enabled': True,
                'metrics_interval': 60000
            }
        }
        
        self.config = default_config
        # TODO: Load from file if config_path provided
    
    def get(self, key: str) -> Any:
        """Get configuration value"""
        return self.config.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value


class MCPQualityAssurance:
    """MCP Quality Assurance and Monitoring"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
    
    async def assess_quality(self, response: MCPResponse) -> Dict[str, Any]:
        """Comprehensive quality assessment"""
        issues: List[str] = []
        recommendations: List[str] = []
        score = 100
        
        # Latency assessment
        if response.metadata.get('latency', 0) > 5000:
            issues.append('High latency detected')
            score -= 20
            recommendations.append('Consider server optimization or load balancing')
        
        # Confidence assessment
        if response.metadata.get('confidence', 0) < 0.7:
            issues.append('Low confidence in response')
            score -= 15
            recommendations.append('Validate response manually or retry with different server')
        
        # Success rate assessment
        if not response.success:
            issues.append('Task execution failed')
            score -= 50
            recommendations.append('Check server health and task requirements')
        
        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': recommendations
        }
    
    def start_monitoring(self) -> None:
        """Performance monitoring and alerting"""
        async def monitor():
            while True:
                await asyncio.sleep(60)  # Every minute
                self._collect_metrics()
                self._analyze_performance()
        
        asyncio.create_task(monitor())
    
    def _collect_metrics(self) -> None:
        """Collect and store performance metrics"""
        timestamp = time.time()
        self.metrics[f"metrics_{int(timestamp)}"] = {
            'timestamp': timestamp,
            'active_servers': 0,  # Would be populated by actual data
            'avg_latency': 0,
            'success_rate': 0,
            'error_rate': 0
        }
    
    def _analyze_performance(self) -> None:
        """Analyze metrics and trigger alerts if needed"""
        recent_metrics = list(self.metrics.values())[-10:]
        
        if not recent_metrics:
            return
        
        avg_latency = sum(m.get('avg_latency', 0) for m in recent_metrics) / len(recent_metrics)
        success_rate = sum(m.get('success_rate', 0) for m in recent_metrics) / len(recent_metrics)
        
        if avg_latency > 3000 or success_rate < 0.9:
            print(f"MCP Performance degradation detected: avg_latency={avg_latency}, success_rate={success_rate}")


# Export enhanced MCP instances for global use
enhanced_mcp = EnhancedMCPManager()
mcp_config = MCPConfigManager()
mcp_qa = MCPQualityAssurance()