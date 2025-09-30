"""
IngestorAgent - Agent A for extracting entities and relationships from text.

This agent specializes in parsing text content (logs, READMEs, configuration files)
and extracting structured entities and relationships that are stored in the memory graph.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from .base_agent import BaseAgent, AgentCapability, AgentContext
from .memory_graph import Node, Edge

logger = logging.getLogger(__name__)


@dataclass
class ExtractionPattern:
    """Pattern for extracting entities and relationships from text"""
    name: str
    entity_regex: str
    relationship_regex: Optional[str] = None
    entity_type: str = ""
    relationship_type: str = ""


class IngestorAgent(BaseAgent):
    """
    Agent specialized in extracting entities and relationships from text content.
    
    Capabilities:
    - Parse deployment logs for services and environment variables
    - Extract configuration dependencies from README files
    - Identify incident patterns and their impacts
    - Convert unstructured text to structured memory graph data
    """
    
    def __init__(self):
        super().__init__(
            name="ingestor",
            capabilities={AgentCapability.CODE_ANALYSIS}
        )
        
        # Predefined extraction patterns for CRM7 demo
        self.extraction_patterns = [
            # Service + environment variable requirements
            ExtractionPattern(
                name="service_env_requirement",
                entity_regex=r"(\w+)\s+(?:on\s+\w+\s+)?(?:requires?|needs?)\s+([\w_,\s]+)",
                relationship_regex=r"SERVICE_REQUIRES_ENVVAR",
                entity_type="Service",
                relationship_type="SERVICE_REQUIRES_ENVVAR"
            ),
            
            # Environment variable definitions
            ExtractionPattern(
                name="env_var_definition", 
                entity_regex=r"([A-Z_][A-Z0-9_]*)\s*=\s*([^\n\r;]+)",
                entity_type="EnvVar"
            ),
            
            # Incident descriptions
            ExtractionPattern(
                name="incident_impact",
                entity_regex=r"(?:incident|error|failure)\s*[:#]?\s*([^.!?]+)",
                entity_type="Incident"
            ),
            
            # Service deployment patterns
            ExtractionPattern(
                name="service_deployment",
                entity_regex=r"(?:deploy|deploying|deployed)\s+(\w+)",
                entity_type="Service"
            )
        ]
    
    async def _setup(self):
        """Initialize the ingestor agent"""
        logger.info("IngestorAgent initialized with extraction patterns")
    
    async def process(self, task: str, context: AgentContext) -> Dict[str, Any]:
        """
        Process text input and extract entities/relationships.
        
        Args:
            task: Text content to analyze (deployment log, README, config file)
            context: Agent context with metadata
            
        Returns:
            Dictionary with extracted entities and relationships
        """
        logger.info(f"IngestorAgent processing task: {task[:100]}...")
        
        # Extract entities and relationships
        extracted_entities = []
        extracted_relationships = []
        
        # Try each extraction pattern
        for pattern in self.extraction_patterns:
            entities, relationships = self._extract_with_pattern(task, pattern, context)
            extracted_entities.extend(entities)
            extracted_relationships.extend(relationships)
        
        # Add entities to memory graph
        entity_ids = []
        for entity_data in extracted_entities:
            entity_id = self.add_entity(
                entity_type=entity_data["type"],
                properties=entity_data["props"],
                entity_id=entity_data.get("id"),  # Use provided ID if available
                source=f"ingestor:task:{context.task_id}"
            )
            entity_ids.append(entity_id)
        
        # Add relationships to memory graph
        relationship_ids = []
        for rel_data in extracted_relationships:
            success = self.add_relationship(
                from_entity_id=rel_data["from_id"],
                to_entity_id=rel_data["to_id"],
                relationship_type=rel_data["type"],
                properties=rel_data.get("props", {}),
                source=f"ingestor:task:{context.task_id}"
            )
            if success:
                relationship_ids.append(rel_data["type"])
        
        result = {
            "extracted_entities": len(entity_ids),
            "extracted_relationships": len(relationship_ids),
            "entity_ids": entity_ids,
            "relationship_types": relationship_ids,
            "source_text_length": len(task),
            "patterns_used": [p.name for p in self.extraction_patterns]
        }
        
        logger.info(f"IngestorAgent extracted {len(entity_ids)} entities and {len(relationship_ids)} relationships")
        
        return result
    
    def _extract_with_pattern(self, text: str, pattern: ExtractionPattern, 
                             context: AgentContext) -> Tuple[List[Dict], List[Dict]]:
        """Extract entities and relationships using a specific pattern"""
        entities = []
        relationships = []
        
        try:
            if pattern.name == "service_env_requirement":
                entities, relationships = self._extract_service_env_requirements(text, context)
            elif pattern.name == "env_var_definition":
                entities.extend(self._extract_env_var_definitions(text, context))
            elif pattern.name == "incident_impact":
                entities.extend(self._extract_incidents(text, context))
            elif pattern.name == "service_deployment":
                entities.extend(self._extract_services(text, context))
                
        except Exception as e:
            logger.error(f"Error extracting with pattern {pattern.name}: {e}")
        
        return entities, relationships
    
    def _extract_service_env_requirements(self, text: str, context: AgentContext) -> Tuple[List[Dict], List[Dict]]:
        """Extract service and environment variable requirements"""
        entities = []
        relationships = []
        
        # Look for service requirements pattern - enhanced to handle multi-line requirements
        lines = text.split('\n')
        current_service = None
        
        for line in lines:
            line = line.strip()
            
            # Match service requirement pattern
            service_match = re.search(r'(\w+)\s+(?:service\s+)?(?:on\s+\w+\s+)?(?:requires?|needs?)', line, re.IGNORECASE)
            if service_match:
                current_service = service_match.group(1)
                
                # Create service entity
                service_id = f"service:{current_service.lower()}"
                service_entity = {
                    "id": service_id,
                    "type": "Service",
                    "props": {
                        "name": current_service,
                        "extracted_from": line[:100],
                        "context": context.task_id
                    }
                }
                entities.append(service_entity)
            
            # Look for environment variables in current line and following bullet points
            env_vars = re.findall(r'([A-Z_][A-Z0-9_]*)', line)
            
            for env_var in env_vars:
                # Skip common words that aren't env vars
                if env_var in ['THE', 'FOR', 'AND', 'WITH', 'KEY', 'URL']:
                    continue
                    
                env_id = f"envvar:{env_var.lower()}"
                env_entity = {
                    "id": env_id,
                    "type": "EnvVar",
                    "props": {
                        "key": env_var,
                        "context": context.task_id,
                        "present": False  # Default to missing
                    }
                }
                entities.append(env_entity)
                
                # If we have a current service, create relationship
                if current_service:
                    service_id = f"service:{current_service.lower()}"
                    relationship = {
                        "type": "SERVICE_REQUIRES_ENVVAR",
                        "from_id": service_id,
                        "to_id": env_id,
                        "props": {
                            "extracted_from": line,
                            "context": context.task_id
                        }
                    }
                    relationships.append(relationship)
        
        return entities, relationships
    
    def _extract_env_var_definitions(self, text: str, context: AgentContext) -> List[Dict]:
        """Extract environment variable definitions"""
        entities = []
        
        # Pattern: "SUPABASE_URL=https://example.com"
        pattern = r'([A-Z_][A-Z0-9_]*)\s*=\s*([^\n\r;]+)'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            var_name = match.group(1)
            var_value = match.group(2).strip()
            
            entity = {
                "id": f"envvar:{var_name.lower()}",
                "type": "EnvVar",
                "props": {
                    "key": var_name,
                    "value": var_value if len(var_value) < 100 else var_value[:97] + "...",
                    "present": True,  # Mark as present since we found a definition
                    "context": context.task_id
                }
            }
            entities.append(entity)
        
        return entities
    
    def _extract_incidents(self, text: str, context: AgentContext) -> List[Dict]:
        """Extract incident descriptions"""
        entities = []
        
        # Pattern for incidents/errors
        patterns = [
            r'(?:incident|error|failure)\s*[:#]?\s*([^.!?\n]+)',
            r'missing\s+([A-Z_][A-Z0-9_]*)',
            r'failed\s+to\s+([^.!?\n]+)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                description = match.group(1).strip()
                # Create standardized incident ID
                incident_id = f"incident:{description[:20].lower().replace(' ', '_').replace('-', '_')}"
                
                entity = {
                    "id": incident_id,
                    "type": "Incident",
                    "props": {
                        "description": description,
                        "severity": self._estimate_severity(description),
                        "context": context.task_id,
                        "extracted_text": match.group(0)
                    }
                }
                entities.append(entity)
        
        return entities
    
    def _extract_services(self, text: str, context: AgentContext) -> List[Dict]:
        """Extract service names from deployment text"""
        entities = []
        
        # Pattern: "deploy crm7" or "deploying frontend-app"
        pattern = r'(?:deploy(?:ing|ed)?|service)\s+([a-z][\w-]*)'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            service_name = match.group(1).lower()
            
            entity = {
                "id": f"service:{service_name}",
                "type": "Service",
                "props": {
                    "name": service_name,
                    "status": "deploying" if "deploy" in match.group(0).lower() else "unknown",
                    "context": context.task_id
                }
            }
            entities.append(entity)
        
        return entities
    
    def _estimate_severity(self, description: str) -> str:
        """Estimate incident severity from description"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['critical', 'down', 'outage', 'failed']):
            return "high"
        elif any(word in description_lower for word in ['warning', 'slow', 'timeout']):
            return "medium"
        else:
            return "low"
    
    async def ingest_from_file(self, file_path: str, context: AgentContext) -> Dict[str, Any]:
        """Ingest entities and relationships from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add file source to context
            context.metadata["source_file"] = file_path
            
            return await self.process(content, context)
            
        except Exception as e:
            logger.error(f"Failed to ingest from file {file_path}: {e}")
            return {"error": str(e), "extracted_entities": 0, "extracted_relationships": 0}
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get statistics about extraction patterns and performance"""
        graph_stats = self.get_memory_graph_stats()
        
        return {
            "agent_name": self.name,
            "available_patterns": len(self.extraction_patterns),
            "pattern_names": [p.name for p in self.extraction_patterns],
            "memory_graph": graph_stats
        }