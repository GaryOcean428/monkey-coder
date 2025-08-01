"""
DevOps Agent - Specialized in deployment and infrastructure automation
Focuses on CI/CD, containerization, orchestration, monitoring, and cloud infrastructure
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base_agent import BaseAgent, AgentCapability, AgentContext

logger = logging.getLogger(__name__)


class DevOpsAgent(BaseAgent):
    """
    Specialized agent for DevOps and infrastructure automation
    Expertise in CI/CD, containerization, orchestration, monitoring
    """
    
    def __init__(self):
        super().__init__(
            name="DevOpsSpecialist",
            capabilities={
                AgentCapability.CODE_GENERATION,
                AgentCapability.ARCHITECTURE_DESIGN,
                AgentCapability.PERFORMANCE_OPTIMIZATION,
                AgentCapability.SECURITY_ANALYSIS,
                AgentCapability.TESTING,
            }
        )
        self.specialization = "devops"
        self.preferred_model = "gpt-4.1"  # Use flagship model for complex infrastructure
        
    async def _setup(self):
        """Initialize DevOps-specific resources"""
        logger.info("Setting up DevOps Specialist Agent")
        
        # CI/CD platforms and tools
        self.update_memory("cicd_platforms", {
            "github_actions": {
                "features": ["workflows", "actions", "matrix_builds", "environments"],
                "integrations": ["aws", "azure", "gcp", "docker", "kubernetes"],
                "security": ["secrets", "oidc", "security_hardening"]
            },
            "gitlab_ci": {
                "features": ["pipelines", "stages", "jobs", "artifacts"],
                "integrations": ["docker", "kubernetes", "helm", "terraform"],
                "security": ["variables", "protected_branches", "security_scanning"]
            },
            "jenkins": {
                "features": ["declarative_pipelines", "plugins", "distributed_builds"],
                "integrations": ["docker", "kubernetes", "ansible", "terraform"],
                "security": ["credentials", "authorization", "audit_trails"]
            },
            "azure_devops": {
                "features": ["pipelines", "releases", "artifacts", "test_plans"],
                "integrations": ["azure", "kubernetes", "terraform"],
                "security": ["service_connections", "variable_groups"]
            }
        }, memory_type="long_term")
        
        # Container and orchestration technologies
        self.update_memory("container_orchestration", {
            "docker": {
                "patterns": ["multi_stage_builds", "layer_optimization", "security_scanning"],
                "best_practices": ["minimal_base_images", "non_root_user", "health_checks"],
                "tools": ["docker_compose", "buildkit", "registry"]
            },
            "kubernetes": {
                "resources": ["deployments", "services", "configmaps", "secrets"],
                "patterns": ["blue_green", "canary", "rolling_updates"],
                "tools": ["helm", "kustomize", "istio", "ingress_controllers"],
                "monitoring": ["prometheus", "grafana", "jaeger", "fluentd"]
            },
            "serverless": {
                "aws": ["lambda", "api_gateway", "eventbridge", "step_functions"],
                "azure": ["functions", "logic_apps", "event_grid"],
                "gcp": ["cloud_functions", "cloud_run", "pub_sub"]
            }
        }, memory_type="long_term")
        
        # Infrastructure as Code tools
        self.update_memory("iac_tools", {
            "terraform": {
                "features": ["state_management", "modules", "workspaces", "providers"],
                "best_practices": ["remote_state", "state_locking", "plan_validation"],
                "cloud_support": ["aws", "azure", "gcp", "multicloud"]
            },
            "cloudformation": {
                "features": ["stacks", "nested_stacks", "custom_resources"],
                "best_practices": ["templates", "parameters", "outputs"]
            },
            "pulumi": {
                "features": ["multiple_languages", "state_management", "policy_as_code"],
                "languages": ["typescript", "python", "go", "csharp"]
            },
            "ansible": {
                "features": ["playbooks", "roles", "inventory", "vault"],
                "best_practices": ["idempotency", "testing", "documentation"]
            }
        }, memory_type="long_term")
        
        # Monitoring and observability
        self.update_memory("monitoring_tools", {
            "metrics": {
                "prometheus": ["metrics", "alerting", "service_discovery"],
                "grafana": ["dashboards", "alerting", "data_sources"],
                "datadog": ["apm", "infrastructure", "logs", "synthetics"],
                "new_relic": ["apm", "infrastructure", "browser", "mobile"]
            },
            "logging": {
                "elk_stack": ["elasticsearch", "logstash", "kibana", "beats"],
                "fluentd": ["log_forwarding", "parsing", "filtering"],
                "splunk": ["search", "dashboards", "alerting"],
                "cloud_logging": ["aws_cloudwatch", "azure_monitor", "gcp_logging"]
            },
            "tracing": {
                "jaeger": ["distributed_tracing", "service_map", "performance"],
                "zipkin": ["tracing", "dependencies", "latency_analysis"],
                "opentelemetry": ["vendor_neutral", "auto_instrumentation"]
            }
        }, memory_type="long_term")
        
        # Security and compliance tools
        self.update_memory("security_tools", {
            "vulnerability_scanning": {
                "container": ["trivy", "clair", "anchore", "snyk"],
                "code": ["sonarqube", "veracode", "checkmarx", "semgrep"],
                "infrastructure": ["checkov", "terrascan", "tfsec"]
            },
            "secrets_management": {
                "vault": ["secret_storage", "dynamic_secrets", "encryption"],
                "aws_secrets": ["rotation", "cross_service", "encryption"],
                "azure_keyvault": ["keys", "secrets", "certificates"],
                "kubernetes_secrets": ["encryption_at_rest", "external_secrets"]
            },
            "compliance": {
                "frameworks": ["soc2", "pci_dss", "hipaa", "gdpr"],
                "tools": ["falco", "open_policy_agent", "compliance_scanner"]
            }
        }, memory_type="long_term")
        
    async def can_handle_task(self, task_description: str, context: AgentContext) -> float:
        """Determine if this agent can handle the task"""
        devops_keywords = [
            "devops", "deployment", "infrastructure", "ci/cd", "pipeline", "automation",
            "docker", "kubernetes", "k8s", "container", "orchestration",
            "terraform", "ansible", "cloudformation", "iac", "infrastructure as code",
            "monitoring", "logging", "metrics", "alerting", "observability",
            "aws", "azure", "gcp", "cloud", "serverless", "lambda",
            "jenkins", "github actions", "gitlab ci", "azure devops",
            "prometheus", "grafana", "elk", "splunk", "datadog",
            "security", "scanning", "compliance", "vault", "secrets",
            "scaling", "load balancing", "high availability", "disaster recovery"
        ]
        
        task_lower = task_description.lower()
        matches = sum(1 for keyword in devops_keywords if keyword in task_lower)
        
        # Higher confidence for DevOps-specific tasks
        base_confidence = min(0.9, matches * 0.12)
        
        # Boost confidence for specific DevOps patterns
        if any(pattern in task_lower for pattern in ["deploy", "infrastructure", "ci/cd", "pipeline"]):
            base_confidence += 0.25
            
        if any(tool in task_lower for tool in ["docker", "kubernetes", "terraform", "ansible"]):
            base_confidence += 0.3
            
        return min(1.0, base_confidence)
    
    async def _execute_task(self, task_description: str, context: AgentContext) -> Dict[str, Any]:
        """Execute DevOps task"""
        logger.info(f"DevOps Agent executing: {task_description}")
        
        # Analyze task type
        task_type = self._determine_task_type(task_description)
        
        # Prepare specialized prompt based on task type
        if task_type == "cicd_pipeline":
            result = await self._handle_cicd_pipeline(task_description, context)
        elif task_type == "containerization":
            result = await self._handle_containerization(task_description, context)
        elif task_type == "infrastructure":
            result = await self._handle_infrastructure_task(task_description, context)
        elif task_type == "monitoring":
            result = await self._handle_monitoring_task(task_description, context)
        elif task_type == "security":
            result = await self._handle_security_task(task_description, context)
        elif task_type == "scaling":
            result = await self._handle_scaling_task(task_description, context)
        elif task_type == "disaster_recovery":
            result = await self._handle_disaster_recovery(task_description, context)
        else:
            result = await self._handle_general_devops_task(task_description, context)
        
        return {
            "type": "devops_automation",
            "task_type": task_type,
            "result": result,
            "specialization": "devops",
            "tools_used": self._detect_tools(task_description),
            "cloud_providers": self._detect_cloud_providers(task_description),
            "automation_level": self._assess_automation_level(task_description)
        }
    
    def _determine_task_type(self, task_description: str) -> str:
        """Determine the specific type of DevOps task"""
        task_lower = task_description.lower()
        
        if any(word in task_lower for word in ["pipeline", "ci/cd", "build", "deploy"]):
            return "cicd_pipeline"
        elif any(word in task_lower for word in ["docker", "container", "image", "registry"]):
            return "containerization"
        elif any(word in task_lower for word in ["infrastructure", "terraform", "cloudformation", "iac"]):
            return "infrastructure"
        elif any(word in task_lower for word in ["monitor", "metrics", "logging", "alerting"]):
            return "monitoring"
        elif any(word in task_lower for word in ["security", "scanning", "compliance", "vault"]):
            return "security"
        elif any(word in task_lower for word in ["scale", "autoscaling", "load balancing"]):
            return "scaling"
        elif any(word in task_lower for word in ["backup", "disaster", "recovery", "failover"]):
            return "disaster_recovery"
        else:
            return "general"
    
    def _detect_tools(self, task_description: str) -> List[str]:
        """Detect DevOps tools mentioned in task description"""
        tools = []
        task_lower = task_description.lower()
        
        tool_keywords = {
            "docker": ["docker"],
            "kubernetes": ["kubernetes", "k8s"],
            "terraform": ["terraform"],
            "ansible": ["ansible"],
            "jenkins": ["jenkins"],
            "github_actions": ["github actions", "github-actions"],
            "prometheus": ["prometheus"],
            "grafana": ["grafana"],
            "helm": ["helm"]
        }
        
        for tool, keywords in tool_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                tools.append(tool)
        
        return tools
    
    def _detect_cloud_providers(self, task_description: str) -> List[str]:
        """Detect cloud providers mentioned in task description"""
        providers = []
        task_lower = task_description.lower()
        
        provider_keywords = {
            "aws": ["aws", "amazon web services"],
            "azure": ["azure", "microsoft azure"],
            "gcp": ["gcp", "google cloud", "google cloud platform"],
            "digitalocean": ["digitalocean"],
            "linode": ["linode"]
        }
        
        for provider, keywords in provider_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                providers.append(provider)
        
        return providers
    
    def _assess_automation_level(self, task_description: str) -> str:
        """Assess the level of automation required"""
        task_lower = task_description.lower()
        
        automation_keywords = [
            "automate", "automatic", "automation", "ci/cd", "pipeline",
            "trigger", "webhook", "schedule", "event-driven"
        ]
        
        if any(keyword in task_lower for keyword in automation_keywords):
            return "high"
        elif any(keyword in task_lower for keyword in ["manual", "interactive"]):
            return "low"
        else:
            return "medium"
    
    async def _handle_cicd_pipeline(self, task_description: str, context: AgentContext) -> str:
        """Handle CI/CD pipeline creation and optimization"""
        tools = self._detect_tools(task_description)
        cicd_tool = "github_actions"  # Default
        
        if "jenkins" in tools:
            cicd_tool = "jenkins"
        elif "gitlab" in task_description.lower():
            cicd_tool = "gitlab_ci"
        elif "azure" in task_description.lower():
            cicd_tool = "azure_devops"
        
        prompt = f"""
As a DevOps Specialist Agent, design and implement a CI/CD pipeline for:

{task_description}

Requirements:
1. Design {cicd_tool} pipeline with proper stages
2. Implement automated testing (unit, integration, e2e)
3. Add security scanning and vulnerability checks
4. Implement build optimization and caching
5. Design deployment strategies (blue-green, canary)
6. Add monitoring and rollback mechanisms
7. Implement secrets and environment management
8. Design multi-environment promotion workflow

Context from previous work:
{self._format_context(context)}

Please provide:
1. Complete pipeline configuration
2. Build and test automation
3. Security scanning integration
4. Deployment automation
5. Environment management
6. Monitoring and alerting setup
7. Rollback procedures
8. Documentation and runbooks
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_containerization(self, task_description: str, context: AgentContext) -> str:
        """Handle containerization and orchestration tasks"""
        prompt = f"""
As a DevOps Specialist Agent, implement containerization solution for:

{task_description}

Requirements:
1. Design optimized Dockerfile with multi-stage builds
2. Implement security best practices (non-root, minimal layers)
3. Create Kubernetes manifests for orchestration
4. Design service discovery and networking
5. Implement health checks and monitoring
6. Add horizontal pod autoscaling
7. Design persistent storage and ConfigMaps
8. Implement security policies and network policies

Context from previous work:
{self._format_context(context)}

Please provide:
1. Optimized Dockerfile implementation
2. Kubernetes deployment manifests
3. Service and ingress configuration
4. ConfigMap and Secret management
5. Health check implementation
6. Autoscaling configuration
7. Security policy definitions
8. Container registry and image management
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_infrastructure_task(self, task_description: str, context: AgentContext) -> str:
        """Handle infrastructure as code tasks"""
        tools = self._detect_tools(task_description)
        iac_tool = "terraform"  # Default
        
        if "cloudformation" in task_description.lower():
            iac_tool = "cloudformation"
        elif "ansible" in tools:
            iac_tool = "ansible"
        elif "pulumi" in task_description.lower():
            iac_tool = "pulumi"
        
        cloud_providers = self._detect_cloud_providers(task_description)
        cloud = cloud_providers[0] if cloud_providers else "aws"
        
        prompt = f"""
As a DevOps Specialist Agent, design infrastructure using {iac_tool} for:

{task_description}

Requirements:
1. Design {iac_tool} modules for {cloud} infrastructure
2. Implement proper state management and locking
3. Design for high availability and fault tolerance
4. Implement security best practices and compliance
5. Add cost optimization and resource tagging
6. Design backup and disaster recovery
7. Implement monitoring and alerting
8. Add auto-scaling and load balancing

Context from previous work:
{self._format_context(context)}

Please provide:
1. Infrastructure as Code implementation
2. Module structure and organization
3. Security and compliance configuration
4. High availability architecture
5. Cost optimization strategies
6. Backup and recovery procedures
7. Monitoring and alerting setup
8. Documentation and operational procedures
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_monitoring_task(self, task_description: str, context: AgentContext) -> str:
        """Handle monitoring and observability tasks"""
        prompt = f"""
As a DevOps Specialist Agent, implement comprehensive monitoring for:

{task_description}

Requirements:
1. Design metrics collection with Prometheus/Grafana
2. Implement centralized logging with ELK stack
3. Add distributed tracing with Jaeger/Zipkin
4. Create comprehensive dashboards and visualizations
5. Implement intelligent alerting and escalation
6. Add performance monitoring and SLA tracking
7. Design capacity planning and trend analysis
8. Implement incident response automation

Context from previous work:
{self._format_context(context)}

Please provide:
1. Monitoring stack deployment
2. Metrics collection configuration
3. Logging pipeline setup
4. Distributed tracing implementation
5. Dashboard and visualization design
6. Alerting rules and escalation
7. SLA monitoring and reporting
8. Incident response procedures
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_security_task(self, task_description: str, context: AgentContext) -> str:
        """Handle security and compliance tasks"""
        prompt = f"""
As a DevOps Specialist Agent focused on security, implement:

{task_description}

Requirements:
1. Implement container and infrastructure scanning
2. Design secrets management and rotation
3. Add compliance monitoring and reporting
4. Implement network security and policies
5. Design identity and access management
6. Add security monitoring and incident response
7. Implement vulnerability management
8. Design security automation and remediation

Context from previous work:
{self._format_context(context)}

Please provide:
1. Security scanning implementation
2. Secrets management solution
3. Compliance monitoring setup
4. Network security configuration
5. IAM policies and procedures
6. Security monitoring and alerting
7. Vulnerability management process
8. Incident response automation
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_scaling_task(self, task_description: str, context: AgentContext) -> str:
        """Handle scaling and performance optimization tasks"""
        prompt = f"""
As a DevOps Specialist Agent focused on scaling, implement:

{task_description}

Requirements:
1. Design horizontal and vertical autoscaling
2. Implement load balancing and traffic distribution
3. Add performance monitoring and optimization
4. Design caching strategies and CDN integration
5. Implement database scaling and sharding
6. Add capacity planning and resource optimization
7. Design cost-effective scaling strategies
8. Implement performance testing and validation

Context from previous work:
{self._format_context(context)}

Please provide:
1. Autoscaling configuration
2. Load balancing implementation
3. Performance optimization strategies
4. Caching and CDN setup
5. Database scaling solutions
6. Capacity planning procedures
7. Cost optimization measures
8. Performance testing framework
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_disaster_recovery(self, task_description: str, context: AgentContext) -> str:
        """Handle disaster recovery and business continuity tasks"""
        prompt = f"""
As a DevOps Specialist Agent focused on disaster recovery, implement:

{task_description}

Requirements:
1. Design comprehensive backup strategies
2. Implement cross-region disaster recovery
3. Add automated failover and failback
4. Design data replication and synchronization
5. Implement RTO/RPO monitoring and testing
6. Add business continuity planning
7. Design incident response procedures
8. Implement recovery testing automation

Context from previous work:
{self._format_context(context)}

Please provide:
1. Backup strategy implementation
2. Disaster recovery architecture
3. Failover automation
4. Data replication setup
5. Recovery testing procedures
6. Business continuity plan
7. Incident response procedures
8. Documentation and runbooks
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_general_devops_task(self, task_description: str, context: AgentContext) -> str:
        """Handle general DevOps tasks"""
        prompt = f"""
As a DevOps Specialist Agent, complete this infrastructure and automation task:

{task_description}

Requirements:
1. Follow DevOps best practices and principles
2. Implement automation and Infrastructure as Code
3. Ensure security and compliance
4. Design for scalability and reliability
5. Add comprehensive monitoring and alerting
6. Implement proper CI/CD practices
7. Include documentation and runbooks
8. Design for cost optimization

Context from previous work:
{self._format_context(context)}

Please provide a complete, production-ready DevOps solution with comprehensive automation and documentation.
"""
        
        return await self._generate_response(prompt, context)    
    async def process(self, task: str, context: AgentContext) -> Dict[str, Any]:
        """Process a DevOps task"""
        return await self._execute_task(task, context)
