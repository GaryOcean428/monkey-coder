"""
Backend Specialist Agent - Specialized in API and infrastructure development
Focuses on databases, APIs, microservices, cloud architecture, and backend frameworks
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base_agent import BaseAgent, AgentCapability, AgentContext

logger = logging.getLogger(__name__)


class BackendAgent(BaseAgent):
    """
    Specialized agent for backend development tasks
    Expertise in APIs, databases, microservices, cloud architecture
    """
    
    def __init__(self):
        super().__init__(
            name="BackendSpecialist",
            capabilities={
                AgentCapability.CODE_GENERATION,
                AgentCapability.CODE_REVIEW,
                AgentCapability.ARCHITECTURE_DESIGN,
                AgentCapability.TESTING,
                AgentCapability.PERFORMANCE_OPTIMIZATION,
                AgentCapability.SECURITY_ANALYSIS,
            }
        )
        self.specialization = "backend"
        self.preferred_model = "gpt-4.1"  # Use flagship model for complex system design
        
    async def _setup(self):
        """Initialize backend-specific resources"""
        logger.info("Setting up Backend Specialist Agent")
        
        # Backend frameworks and patterns
        self.update_memory("backend_frameworks", {
            "python": {
                "frameworks": ["fastapi", "django", "flask", "starlette", "quart"],
                "orm": ["sqlalchemy", "django-orm", "peewee", "tortoise-orm"],
                "async": ["asyncio", "aiohttp", "uvloop", "trio"],
                "testing": ["pytest", "unittest", "pytest-asyncio"]
            },
            "node": {
                "frameworks": ["express", "koa", "nestjs", "fastify", "hapi"],
                "orm": ["sequelize", "typeorm", "mongoose", "prisma"],
                "async": ["async/await", "promises", "streams"],
                "testing": ["jest", "mocha", "supertest"]
            },
            "java": {
                "frameworks": ["spring-boot", "quarkus", "micronaut", "vert.x"],
                "orm": ["hibernate", "jpa", "mybatis", "jdbi"],
                "testing": ["junit", "testng", "mockito"]
            },
            "go": {
                "frameworks": ["gin", "echo", "fiber", "chi", "gorilla"],
                "orm": ["gorm", "sqlx", "ent"],
                "testing": ["testing", "testify", "ginkgo"]
            },
            "rust": {
                "frameworks": ["actix-web", "warp", "rocket", "axum"],
                "orm": ["diesel", "sqlx", "sea-orm"],
                "testing": ["cargo test", "tokio-test"]
            }
        }, memory_type="long_term")
        
        # Database patterns and technologies
        self.update_memory("database_patterns", {
            "relational": {
                "databases": ["postgresql", "mysql", "sqlite", "mariadb"],
                "patterns": ["normalization", "indexing", "partitioning", "sharding"],
                "optimization": ["query-optimization", "connection-pooling", "caching"]
            },
            "nosql": {
                "document": ["mongodb", "couchdb", "amazon-documentdb"],
                "key_value": ["redis", "memcached", "dynamodb", "etcd"],
                "graph": ["neo4j", "amazon-neptune", "arangodb"],
                "column": ["cassandra", "hbase", "clickhouse"]
            },
            "patterns": ["repository", "unit-of-work", "active-record", "data-mapper"],
            "migrations": ["versioning", "rollback", "schema-evolution"]
        }, memory_type="long_term")
        
        # API design patterns
        self.update_memory("api_patterns", {
            "rest": {
                "principles": ["stateless", "cacheable", "uniform-interface"],
                "patterns": ["resource-oriented", "hateoas", "versioning"],
                "security": ["oauth2", "jwt", "api-keys", "rate-limiting"]
            },
            "graphql": {
                "patterns": ["schema-first", "resolver-pattern", "dataloader"],
                "security": ["query-depth-limiting", "query-complexity"],
                "optimization": ["batching", "caching", "persisted-queries"]
            },
            "grpc": {
                "patterns": ["protocol-buffers", "streaming", "interceptors"],
                "features": ["bidirectional-streaming", "load-balancing"]
            },
            "websockets": {
                "patterns": ["pub-sub", "real-time-updates", "connection-management"]
            }
        }, memory_type="long_term")
        
        # Cloud and infrastructure patterns
        self.update_memory("cloud_patterns", {
            "microservices": {
                "patterns": ["service-mesh", "api-gateway", "circuit-breaker"],
                "communication": ["event-driven", "saga-pattern", "choreography"],
                "data": ["database-per-service", "event-sourcing", "cqrs"]
            },
            "containers": {
                "technologies": ["docker", "kubernetes", "docker-compose"],
                "patterns": ["multi-stage-builds", "health-checks", "secrets"]
            },
            "serverless": {
                "platforms": ["aws-lambda", "azure-functions", "google-cloud-functions"],
                "patterns": ["function-per-feature", "event-driven", "cold-start-optimization"]
            },
            "monitoring": {
                "logging": ["structured-logging", "correlation-ids", "log-aggregation"],
                "metrics": ["prometheus", "grafana", "datadog", "custom-metrics"],
                "tracing": ["jaeger", "zipkin", "opentelemetry"]
            }
        }, memory_type="long_term")
        
    async def can_handle_task(self, task_description: str, context: AgentContext) -> float:
        """Determine if this agent can handle the task"""
        backend_keywords = [
            "api", "backend", "server", "database", "microservice", "endpoint",
            "rest", "graphql", "grpc", "websocket", "authentication", "authorization",
            "postgresql", "mysql", "mongodb", "redis", "cache", "queue",
            "docker", "kubernetes", "cloud", "aws", "azure", "gcp",
            "fastapi", "django", "flask", "express", "spring", "gin",
            "orm", "sql", "nosql", "migration", "schema", "model",
            "middleware", "service", "infrastructure", "deployment",
            "performance", "scaling", "load balancing", "monitoring"
        ]
        
        task_lower = task_description.lower()
        matches = sum(1 for keyword in backend_keywords if keyword in task_lower)
        
        # Higher confidence for backend-specific tasks
        base_confidence = min(0.9, matches * 0.12)
        
        # Boost confidence for specific backend patterns
        if any(pattern in task_lower for pattern in ["api", "backend", "server", "database"]):
            base_confidence += 0.25
            
        if any(tech in task_lower for tech in ["fastapi", "django", "express", "spring"]):
            base_confidence += 0.3
            
        return min(1.0, base_confidence)
    
    async def _execute_task(self, task_description: str, context: AgentContext) -> Dict[str, Any]:
        """Execute backend development task"""
        logger.info(f"Backend Agent executing: {task_description}")
        
        # Analyze task type
        task_type = self._determine_task_type(task_description)
        
        # Prepare specialized prompt based on task type
        if task_type == "api_development":
            result = await self._handle_api_development(task_description, context)
        elif task_type == "database_design":
            result = await self._handle_database_design(task_description, context)
        elif task_type == "microservices":
            result = await self._handle_microservices_task(task_description, context)
        elif task_type == "authentication":
            result = await self._handle_authentication_task(task_description, context)
        elif task_type == "performance":
            result = await self._handle_performance_task(task_description, context)
        elif task_type == "infrastructure":
            result = await self._handle_infrastructure_task(task_description, context)
        elif task_type == "testing":
            result = await self._handle_testing_task(task_description, context)
        else:
            result = await self._handle_general_backend_task(task_description, context)
        
        return {
            "type": "backend_development",
            "task_type": task_type,
            "result": result,
            "specialization": "backend",
            "frameworks_used": self._detect_frameworks(task_description),
            "databases_used": self._detect_databases(task_description),
            "cloud_services": self._detect_cloud_services(task_description)
        }
    
    def _determine_task_type(self, task_description: str) -> str:
        """Determine the specific type of backend task"""
        task_lower = task_description.lower()
        
        if any(word in task_lower for word in ["api", "endpoint", "rest", "graphql", "grpc"]):
            return "api_development"
        elif any(word in task_lower for word in ["database", "schema", "migration", "orm"]):
            return "database_design"
        elif any(word in task_lower for word in ["microservice", "service mesh", "distributed"]):
            return "microservices"
        elif any(word in task_lower for word in ["auth", "login", "jwt", "oauth", "security"]):
            return "authentication"
        elif any(word in task_lower for word in ["performance", "optimize", "scale", "cache"]):
            return "performance"
        elif any(word in task_lower for word in ["docker", "kubernetes", "deploy", "infrastructure"]):
            return "infrastructure"
        elif any(word in task_lower for word in ["test", "testing", "spec", "mock"]):
            return "testing"
        else:
            return "general"
    
    def _detect_frameworks(self, task_description: str) -> List[str]:
        """Detect backend frameworks mentioned in task description"""
        frameworks = []
        task_lower = task_description.lower()
        
        framework_keywords = {
            "fastapi": ["fastapi"],
            "django": ["django"],
            "flask": ["flask"],
            "express": ["express", "express.js"],
            "spring": ["spring", "spring-boot"],
            "gin": ["gin"],
            "nestjs": ["nestjs", "nest.js"]
        }
        
        for framework, keywords in framework_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                frameworks.append(framework)
        
        return frameworks
    
    def _detect_databases(self, task_description: str) -> List[str]:
        """Detect databases mentioned in task description"""
        databases = []
        task_lower = task_description.lower()
        
        db_keywords = {
            "postgresql": ["postgresql", "postgres", "psql"],
            "mysql": ["mysql"],
            "mongodb": ["mongodb", "mongo"],
            "redis": ["redis"],
            "sqlite": ["sqlite"],
            "cassandra": ["cassandra"],
            "dynamodb": ["dynamodb"]
        }
        
        for db, keywords in db_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                databases.append(db)
        
        return databases
    
    def _detect_cloud_services(self, task_description: str) -> List[str]:
        """Detect cloud services mentioned in task description"""
        services = []
        task_lower = task_description.lower()
        
        cloud_keywords = {
            "aws": ["aws", "amazon web services"],
            "azure": ["azure", "microsoft azure"],
            "gcp": ["gcp", "google cloud"],
            "docker": ["docker"],
            "kubernetes": ["kubernetes", "k8s"]
        }
        
        for service, keywords in cloud_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                services.append(service)
        
        return services
    
    async def _handle_api_development(self, task_description: str, context: AgentContext) -> str:
        """Handle API development tasks"""
        frameworks = self._detect_frameworks(task_description)
        framework = frameworks[0] if frameworks else "fastapi"  # Default to FastAPI
        
        prompt = f"""
As a Backend Specialist Agent, design and implement a robust API for:

{task_description}

Requirements:
1. Use {framework} following best practices
2. Implement proper HTTP status codes and error handling
3. Add request/response validation and serialization
4. Include authentication and authorization
5. Implement rate limiting and security measures
6. Add comprehensive API documentation (OpenAPI/Swagger)
7. Include proper logging and monitoring
8. Design for scalability and performance

Context from previous work:
{self._format_context(context)}

Please provide:
1. API implementation with endpoints
2. Data models and validation schemas
3. Authentication/authorization implementation
4. Error handling and middleware
5. API documentation
6. Testing strategies
7. Deployment considerations
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_database_design(self, task_description: str, context: AgentContext) -> str:
        """Handle database design and implementation tasks"""
        databases = self._detect_databases(task_description)
        db_type = databases[0] if databases else "postgresql"  # Default to PostgreSQL
        
        prompt = f"""
As a Backend Specialist Agent, design and implement database solution for:

{task_description}

Requirements:
1. Design normalized {db_type} schema with proper relationships
2. Create efficient indexes for query optimization
3. Implement data validation and constraints
4. Design migration strategy for schema evolution
5. Consider performance optimization (partitioning, sharding)
6. Implement backup and recovery strategies
7. Add proper security measures (encryption, access control)
8. Design for horizontal and vertical scaling

Context from previous work:
{self._format_context(context)}

Please provide:
1. Database schema design (DDL)
2. Migration scripts
3. Index optimization strategy
4. ORM models and relationships
5. Query optimization examples
6. Backup and recovery procedures
7. Security implementation
8. Performance monitoring setup
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_microservices_task(self, task_description: str, context: AgentContext) -> str:
        """Handle microservices architecture tasks"""
        prompt = f"""
As a Backend Specialist Agent specializing in microservices, design:

{task_description}

Requirements:
1. Design service boundaries following domain-driven design
2. Implement inter-service communication (REST/gRPC/Events)
3. Design data consistency patterns (Saga, Event Sourcing)
4. Implement service discovery and load balancing
5. Add circuit breaker and retry mechanisms
6. Design distributed tracing and monitoring
7. Implement API gateway and security
8. Plan deployment and orchestration strategy

Context from previous work:
{self._format_context(context)}

Please provide:
1. Service architecture diagram
2. Service interface definitions
3. Communication patterns implementation
4. Data consistency strategy
5. Resilience patterns (Circuit breaker, Bulkhead)
6. Monitoring and observability setup
7. Deployment configuration
8. Testing strategy for distributed systems
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_authentication_task(self, task_description: str, context: AgentContext) -> str:
        """Handle authentication and authorization tasks"""
        prompt = f"""
As a Backend Specialist Agent focused on security, implement:

{task_description}

Requirements:
1. Design secure authentication flow (OAuth2, JWT, etc.)
2. Implement proper password hashing and storage
3. Add multi-factor authentication support
4. Design role-based access control (RBAC)
5. Implement session management and token refresh
6. Add security headers and CORS configuration
7. Design rate limiting and brute force protection
8. Ensure compliance with security standards

Context from previous work:
{self._format_context(context)}

Please provide:
1. Authentication flow implementation
2. JWT token management
3. Password security implementation
4. RBAC system design
5. Security middleware
6. Session management
7. Rate limiting implementation
8. Security testing procedures
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_performance_task(self, task_description: str, context: AgentContext) -> str:
        """Handle backend performance optimization tasks"""
        prompt = f"""
As a Backend Specialist Agent focused on performance, optimize:

{task_description}

Requirements:
1. Implement efficient caching strategies (Redis, in-memory)
2. Optimize database queries and indexes
3. Design connection pooling and resource management
4. Implement asynchronous processing where appropriate
5. Add load balancing and horizontal scaling
6. Optimize memory usage and garbage collection
7. Implement monitoring and alerting
8. Design for auto-scaling capabilities

Context from previous work:
{self._format_context(context)}

Please provide:
1. Performance optimization implementation
2. Caching strategy and configuration
3. Database query optimization
4. Async processing implementation
5. Load balancing configuration
6. Monitoring and metrics setup
7. Auto-scaling configuration
8. Performance testing procedures
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_infrastructure_task(self, task_description: str, context: AgentContext) -> str:
        """Handle infrastructure and deployment tasks"""
        cloud_services = self._detect_cloud_services(task_description)
        
        prompt = f"""
As a Backend Specialist Agent with infrastructure expertise, implement:

{task_description}

Requirements:
1. Design containerized deployment with Docker
2. Create Kubernetes manifests for orchestration
3. Implement CI/CD pipeline configuration
4. Design monitoring and logging infrastructure
5. Implement backup and disaster recovery
6. Add security scanning and compliance
7. Design auto-scaling and load balancing
8. Plan cost optimization strategies

Cloud Services Detected: {', '.join(cloud_services) if cloud_services else 'Generic cloud'}

Context from previous work:
{self._format_context(context)}

Please provide:
1. Dockerfile and container configuration
2. Kubernetes deployment manifests
3. CI/CD pipeline configuration
4. Infrastructure as Code (Terraform/CloudFormation)
5. Monitoring and logging setup
6. Backup and recovery procedures
7. Security configuration
8. Cost optimization recommendations
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_testing_task(self, task_description: str, context: AgentContext) -> str:
        """Handle backend testing tasks"""
        frameworks = self._detect_frameworks(task_description)
        framework = frameworks[0] if frameworks else "fastapi"
        
        prompt = f"""
As a Backend Specialist Agent, create comprehensive tests for:

{task_description}

Requirements:
1. Write unit tests for business logic and services
2. Create integration tests for API endpoints
3. Implement database testing with fixtures
4. Add performance and load testing
5. Create end-to-end testing scenarios
6. Implement mocking strategies for external services
7. Add security testing (OWASP guidelines)
8. Design test data management and cleanup

Framework: {framework}

Context from previous work:
{self._format_context(context)}

Please provide:
1. Unit test implementation
2. Integration test scenarios
3. API endpoint testing
4. Database testing strategies
5. Mock implementations
6. Performance test scripts
7. Security test cases
8. Test automation configuration
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_general_backend_task(self, task_description: str, context: AgentContext) -> str:
        """Handle general backend development tasks"""
        prompt = f"""
As a Backend Specialist Agent, complete this backend development task:

{task_description}

Requirements:
1. Follow backend development best practices
2. Ensure scalability and performance
3. Implement proper error handling and logging
4. Add comprehensive security measures
5. Design for maintainability and testability
6. Include monitoring and observability
7. Add proper documentation
8. Consider deployment and operational aspects

Context from previous work:
{self._format_context(context)}

Please provide a complete, production-ready backend solution with comprehensive documentation.
"""
        
        return await self._generate_response(prompt, context)    
    async def process(self, task: str, context: AgentContext) -> Dict[str, Any]:
        """Process a backend development task"""
        return await self._execute_task(task, context)
