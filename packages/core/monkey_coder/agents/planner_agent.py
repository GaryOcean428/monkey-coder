"""
PlannerAgent - Agent B for graph-based reasoning and planning.

This agent specializes in answering questions using ONLY the memory graph data.
It cannot access raw text or external sources, forcing structured reasoning
through entity relationships and multi-hop graph traversal.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_agent import BaseAgent, AgentCapability, AgentContext
from .memory_graph import Node, Edge, QueryResult, missing_env_vars_for_service, related_incidents_for_service

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    """
    Agent specialized in graph-based reasoning and planning.
    
    Key constraint: Can ONLY use memory graph queries - no access to raw text.
    
    Capabilities:
    - Answer questions about service dependencies
    - Identify rollout risks through graph analysis
    - Find multi-hop relationships between entities
    - Generate deployment recommendations based on graph structure
    """
    
    def __init__(self):
        super().__init__(
            name="planner", 
            capabilities={
                AgentCapability.ARCHITECTURE_DESIGN,
                AgentCapability.CODE_ANALYSIS
            }
        )
        
        # Query templates for common planning questions
        self.query_templates = {
            "rollout_risks": self._analyze_rollout_risks,
            "missing_dependencies": self._find_missing_dependencies,
            "incident_impact": self._analyze_incident_impact,
            "deployment_readiness": self._check_deployment_readiness,
            "service_health": self._assess_service_health,
            "environment_gaps": self._find_environment_gaps
        }
    
    async def _setup(self):
        """Initialize the planner agent"""
        logger.info("PlannerAgent initialized - graph-only reasoning mode")
    
    async def process(self, task: str, context: AgentContext) -> Dict[str, Any]:
        """
        Process planning questions using graph-only queries.
        
        Args:
            task: Planning question or request (e.g., "What's blocking crm7 rollout?")
            context: Agent context with metadata
            
        Returns:
            Planning analysis based solely on memory graph structure
        """
        logger.info(f"PlannerAgent processing query: {task}")
        
        # Parse the task to determine query type
        query_type = self._classify_query(task)
        
        # Execute appropriate graph-based analysis
        if query_type in self.query_templates:
            analysis = await self.query_templates[query_type](task, context)
        else:
            analysis = await self._generic_graph_analysis(task, context)
        
        # Add graph metadata
        analysis["query_metadata"] = {
            "query_type": query_type,
            "graph_stats": self.get_memory_graph_stats(),
            "query_time": datetime.now().isoformat(),
            "reasoning_source": "graph_only"
        }
        
        logger.info(f"PlannerAgent completed analysis: {query_type}")
        
        return analysis
    
    def _classify_query(self, task: str) -> str:
        """Classify the planning query to determine appropriate analysis method"""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ['rollout', 'deploy', 'blocking', 'block']):
            return "rollout_risks"
        elif any(word in task_lower for word in ['missing', 'require', 'need', 'depend']):
            return "missing_dependencies"
        elif any(word in task_lower for word in ['incident', 'error', 'fail', 'impact']):
            return "incident_impact"
        elif any(word in task_lower for word in ['ready', 'readiness', 'status']):
            return "deployment_readiness"
        elif any(word in task_lower for word in ['health', 'check', 'monitor']):
            return "service_health"
        elif any(word in task_lower for word in ['env', 'environment', 'config', 'variable']):
            return "environment_gaps"
        else:
            return "generic"
    
    async def _analyze_rollout_risks(self, task: str, context: AgentContext) -> Dict[str, Any]:
        """Analyze rollout risks using graph-only queries"""
        risks = []
        recommendations = []
        
        # Get all services from the graph
        services = self.get_entities_by_type("Service")
        
        for service in services:
            service_name = service.props.get("name", service.id)
            
            # Check for missing environment variables
            missing_vars = missing_env_vars_for_service(self.memory.graph, service.id)
            if missing_vars:
                risk = {
                    "type": "missing_environment_variables",
                    "service": service_name,
                    "missing_vars": [var.props.get("key", var.id) for var in missing_vars],
                    "severity": "high",
                    "blocker": True
                }
                risks.append(risk)
                
                recommendations.append(f"Configure missing environment variables for {service_name}: {', '.join(risk['missing_vars'])}")
            
            # Check for related incidents
            incidents = related_incidents_for_service(self.memory.graph, service.id)
            for incident in incidents:
                risk = {
                    "type": "historical_incident",
                    "service": service_name,
                    "incident_description": incident.props.get("description", "Unknown incident"),
                    "severity": incident.props.get("severity", "medium"),
                    "blocker": incident.props.get("severity") == "high"
                }
                risks.append(risk)
                
                if risk["blocker"]:
                    recommendations.append(f"Resolve {service_name} incident: {risk['incident_description']}")
        
        # Analyze service dependencies
        dependency_risks = self._analyze_service_dependencies()
        risks.extend(dependency_risks)
        
        return {
            "analysis_type": "rollout_risks",
            "total_risks": len(risks),
            "blocking_risks": len([r for r in risks if r.get("blocker", False)]),
            "risks": risks,
            "recommendations": recommendations,
            "rollout_status": "blocked" if any(r.get("blocker") for r in risks) else "ready"
        }
    
    async def _find_missing_dependencies(self, task: str, context: AgentContext) -> Dict[str, Any]:
        """Find missing dependencies using graph queries"""
        dependencies = []
        
        # Extract service name from task if possible
        service_name = self._extract_service_name_from_query(task)
        
        if service_name:
            # Focus on specific service
            services = [s for s in self.get_entities_by_type("Service") 
                       if service_name.lower() in s.props.get("name", "").lower()]
        else:
            # Analyze all services
            services = self.get_entities_by_type("Service")
        
        for service in services:
            service_name = service.props.get("name", service.id)
            
            # Get required environment variables
            required_envs = self.get_related_entities(
                service.id, 
                relationship_type="SERVICE_REQUIRES_ENVVAR", 
                direction="out"
            )
            
            missing_count = 0
            present_count = 0
            
            for env_var in required_envs:
                is_present = env_var.props.get("present", False)
                if is_present:
                    present_count += 1
                else:
                    missing_count += 1
            
            dependency_info = {
                "service": service_name,
                "required_env_vars": len(required_envs),
                "missing_env_vars": missing_count,
                "present_env_vars": present_count,
                "completion_percentage": (present_count / len(required_envs) * 100) if required_envs else 100
            }
            
            dependencies.append(dependency_info)
        
        return {
            "analysis_type": "missing_dependencies",
            "services_analyzed": len(dependencies),
            "dependencies": dependencies,
            "overall_readiness": sum(d["completion_percentage"] for d in dependencies) / len(dependencies) if dependencies else 0
        }
    
    async def _analyze_incident_impact(self, task: str, context: AgentContext) -> Dict[str, Any]:
        """Analyze incident impact using graph relationships"""
        incidents = self.get_entities_by_type("Incident")
        impact_analysis = []
        
        for incident in incidents:
            # Find services affected by this incident
            affected_services = self.get_related_entities(
                incident.id,
                relationship_type="INCIDENT_IMPACTS_SERVICE",
                direction="out"
            )
            
            # Find environment variables that might have caused the incident
            related_envvars = self.get_related_entities(
                incident.id,
                relationship_type="INCIDENT_CAUSED_BY_ENVVAR", 
                direction="out"
            )
            
            impact = {
                "incident_id": incident.id,
                "description": incident.props.get("description", "Unknown incident"),
                "severity": incident.props.get("severity", "unknown"),
                "affected_services": [s.props.get("name", s.id) for s in affected_services],
                "related_env_vars": [ev.props.get("key", ev.id) for ev in related_envvars],
                "impact_scope": len(affected_services)
            }
            
            impact_analysis.append(impact)
        
        return {
            "analysis_type": "incident_impact",
            "total_incidents": len(incidents),
            "incidents": impact_analysis,
            "high_severity_count": len([i for i in impact_analysis if i["severity"] == "high"]),
            "services_with_incidents": len(set([s for i in impact_analysis for s in i["affected_services"]]))
        }
    
    async def _check_deployment_readiness(self, task: str, context: AgentContext) -> Dict[str, Any]:
        """Check overall deployment readiness using graph analysis"""
        services = self.get_entities_by_type("Service")
        readiness_report = []
        
        for service in services:
            service_name = service.props.get("name", service.id)
            
            # Check environment variables
            missing_vars = missing_env_vars_for_service(self.memory.graph, service.id)
            env_ready = len(missing_vars) == 0
            
            # Check for blocking incidents
            incidents = related_incidents_for_service(self.memory.graph, service.id)
            blocking_incidents = [i for i in incidents if i.props.get("severity") == "high"]
            incident_ready = len(blocking_incidents) == 0
            
            # Calculate overall readiness
            overall_ready = env_ready and incident_ready
            
            readiness = {
                "service": service_name,
                "environment_ready": env_ready,
                "incidents_resolved": incident_ready,
                "overall_ready": overall_ready,
                "missing_env_vars": len(missing_vars),
                "blocking_incidents": len(blocking_incidents)
            }
            
            readiness_report.append(readiness)
        
        # Calculate overall deployment readiness
        ready_services = len([r for r in readiness_report if r["overall_ready"]])
        readiness_percentage = (ready_services / len(readiness_report) * 100) if readiness_report else 0
        
        return {
            "analysis_type": "deployment_readiness",
            "services_checked": len(readiness_report),
            "ready_services": ready_services,
            "readiness_percentage": readiness_percentage,
            "deployment_status": "ready" if readiness_percentage == 100 else "not_ready",
            "service_readiness": readiness_report
        }
    
    async def _assess_service_health(self, task: str, context: AgentContext) -> Dict[str, Any]:
        """Assess service health based on graph relationships"""
        services = self.get_entities_by_type("Service")
        health_assessment = []
        
        for service in services:
            service_name = service.props.get("name", service.id)
            
            # Count dependencies
            dependencies = len(self.get_related_entities(service.id, direction="out"))
            
            # Count dependents (services that depend on this one)
            dependents = len(self.get_related_entities(service.id, direction="in"))
            
            # Recent incidents
            incidents = related_incidents_for_service(self.memory.graph, service.id)
            recent_incidents = len(incidents)  # In real system, filter by date
            
            # Health score calculation (simplified)
            health_score = max(0, 100 - (recent_incidents * 20) - (len(missing_env_vars_for_service(self.memory.graph, service.id)) * 30))
            
            health = {
                "service": service_name,
                "health_score": health_score,
                "dependencies": dependencies,
                "dependents": dependents,
                "recent_incidents": recent_incidents,
                "status": "healthy" if health_score >= 80 else "degraded" if health_score >= 50 else "unhealthy"
            }
            
            health_assessment.append(health)
        
        return {
            "analysis_type": "service_health",
            "services_assessed": len(health_assessment),
            "healthy_services": len([h for h in health_assessment if h["status"] == "healthy"]),
            "degraded_services": len([h for h in health_assessment if h["status"] == "degraded"]),
            "unhealthy_services": len([h for h in health_assessment if h["status"] == "unhealthy"]),
            "health_details": health_assessment
        }
    
    async def _find_environment_gaps(self, task: str, context: AgentContext) -> Dict[str, Any]:
        """Find environment configuration gaps using graph analysis"""
        env_vars = self.get_entities_by_type("EnvVar")
        services = self.get_entities_by_type("Service") 
        
        gaps = []
        
        # Find required but missing environment variables
        for service in services:
            service_name = service.props.get("name", service.id)
            required_vars = self.get_related_entities(
                service.id,
                relationship_type="SERVICE_REQUIRES_ENVVAR",
                direction="out"
            )
            
            for var in required_vars:
                if not var.props.get("present", False):
                    gap = {
                        "service": service_name,
                        "env_var": var.props.get("key", var.id),
                        "gap_type": "missing_value",
                        "priority": "high" if "SUPABASE" in var.props.get("key", "") else "medium"
                    }
                    gaps.append(gap)
        
        # Find environment variables without clear ownership
        orphaned_vars = []
        for var in env_vars:
            var_key = var.props.get("key", var.id)
            requiring_services = self.get_related_entities(
                var.id,
                relationship_type="SERVICE_REQUIRES_ENVVAR", 
                direction="in"
            )
            
            if not requiring_services:
                orphaned_vars.append({
                    "env_var": var_key,
                    "gap_type": "orphaned_variable",
                    "priority": "low"
                })
        
        return {
            "analysis_type": "environment_gaps",
            "total_gaps": len(gaps),
            "missing_variables": len([g for g in gaps if g["gap_type"] == "missing_value"]),
            "orphaned_variables": len(orphaned_vars),
            "high_priority_gaps": len([g for g in gaps if g["priority"] == "high"]),
            "gaps": gaps + orphaned_vars
        }
    
    async def _generic_graph_analysis(self, task: str, context: AgentContext) -> Dict[str, Any]:
        """Generic graph analysis for unclassified queries"""
        # Get overall graph structure
        stats = self.get_memory_graph_stats()
        
        # Try to find any mentioned entities in the task
        mentioned_entities = []
        all_entities = (self.get_entities_by_type("Service") + 
                       self.get_entities_by_type("EnvVar") +
                       self.get_entities_by_type("Incident"))
        
        for entity in all_entities:
            entity_name = entity.props.get("name", entity.props.get("key", entity.id))
            if entity_name.lower() in task.lower():
                mentioned_entities.append({
                    "entity_id": entity.id,
                    "entity_type": entity.type,
                    "entity_name": entity_name,
                    "related_entities": len(self.get_related_entities(entity.id, direction="both"))
                })
        
        return {
            "analysis_type": "generic_graph_analysis",
            "graph_stats": stats,
            "mentioned_entities": mentioned_entities,
            "suggestion": "Consider using a more specific query for targeted analysis"
        }
    
    def _analyze_service_dependencies(self) -> List[Dict[str, Any]]:
        """Analyze cross-service dependencies for risks"""
        risks = []
        services = self.get_entities_by_type("Service")
        
        for service in services:
            service_name = service.props.get("name", service.id)
            
            # Count how many other services depend on this one
            dependents = self.get_related_entities(service.id, direction="in")
            
            # High-dependency services are riskier
            if len(dependents) > 2:
                risk = {
                    "type": "high_dependency_service",
                    "service": service_name,
                    "dependent_count": len(dependents),
                    "severity": "medium",
                    "blocker": False
                }
                risks.append(risk)
        
        return risks
    
    def _extract_service_name_from_query(self, query: str) -> Optional[str]:
        """Extract service name from a natural language query"""
        # Simple pattern matching - in production would use NLP
        services = self.get_entities_by_type("Service")
        
        for service in services:
            service_name = service.props.get("name", "")
            if service_name.lower() in query.lower():
                return service_name
        
        return None
    
    def get_planning_capabilities(self) -> Dict[str, Any]:
        """Get information about planning capabilities"""
        return {
            "agent_name": self.name,
            "reasoning_mode": "graph_only",
            "available_queries": list(self.query_templates.keys()),
            "memory_graph_stats": self.get_memory_graph_stats(),
            "supported_entity_types": ["Service", "EnvVar", "Incident"],
            "supported_relationship_types": ["SERVICE_REQUIRES_ENVVAR", "INCIDENT_IMPACTS_SERVICE"]
        }