"""
Web Search Configuration for Agent System

This module defines configuration for web search capabilities
across different AI providers.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class WebSearchConfig:
    """Configuration for web search capabilities."""
    
    enabled: bool = True
    search_context_size: str = "high"  # low, medium, high
    verify_technical_info: bool = True
    check_library_versions: bool = True
    verify_security_updates: bool = True
    cross_reference_sources: bool = True
    
    # Provider-specific settings
    openai_settings: Dict[str, Any] = None
    anthropic_settings: Dict[str, Any] = None
    groq_settings: Dict[str, Any] = None
    grok_settings: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize provider-specific settings if not provided."""
        if self.openai_settings is None:
            self.openai_settings = {
                "web_search_preview": True,
                "search_context_size": "high",
                "user_location": {
                    "type": "approximate",
                    "country": "US"
                }
            }
        
        if self.anthropic_settings is None:
            self.anthropic_settings = {
                "inject_search_results": True,
                "max_search_results": 5
            }
        
        if self.groq_settings is None:
            self.groq_settings = {
                "web_search": True,
                "search_depth": "comprehensive"
            }
        
        if self.grok_settings is None:
            self.grok_settings = {
                "live_search": True,
                "real_time_updates": True
            }


class WebSearchPrompts:
    """Standard prompts for web search instructions."""
    
    @staticmethod
    def get_date_awareness_prompt() -> str:
        """Get the current date awareness prompt."""
        current_date = datetime.utcnow().strftime("%B %d, %Y")
        return f"Today's date is {current_date}. Please consider this when evaluating information currency."
    
    @staticmethod
    def get_verification_reminder() -> str:
        """Get the standard verification reminder."""
        return """
IMPORTANT REMINDERS:
- Verify all technical information through web search
- Check for recent updates and breaking changes
- Confirm library versions are current
- Cross-reference multiple sources when possible
- Be explicit about information sources (web search vs. training data)
"""
    
    @staticmethod
    def get_phase_specific_reminder(phase: str) -> str:
        """Get phase-specific web search reminders."""
        reminders = {
            "analysis": """
Use web search to:
- Verify technical specifications and requirements
- Check for existing solutions and patterns
- Research current best practices
- Identify potential compatibility issues
""",
            "planning": """
Use web search to:
- Research architectural patterns and designs
- Verify framework capabilities and limitations
- Check for recent technology updates
- Review industry standards and conventions
""",
            "implementation": """
Use web search to:
- Verify current API documentation
- Check for latest library versions
- Confirm syntax and usage patterns
- Research error solutions and workarounds
""",
            "testing": """
Use web search to:
- Find testing best practices and patterns
- Verify testing framework documentation
- Research common test cases and edge cases
- Check for known issues and bugs
""",
            "review": """
Use web search to:
- Verify security vulnerabilities (CVEs)
- Check for deprecated methods
- Confirm current best practices
- Research performance optimizations
""",
            "documentation": """
Use web search to:
- Verify technical accuracy
- Check current terminology and conventions
- Research documentation standards
- Confirm API references
"""
        }
        return reminders.get(phase, "")
    
    @staticmethod
    def format_search_instruction(
        task_type: str,
        specific_requirements: Optional[str] = None
    ) -> str:
        """Format a complete search instruction for an agent."""
        base_instruction = WebSearchPrompts.get_date_awareness_prompt()
        verification = WebSearchPrompts.get_verification_reminder()
        
        instruction = f"{base_instruction}\n{verification}"
        
        if specific_requirements:
            instruction += f"\nSpecific requirements to verify:\n{specific_requirements}"
        
        return instruction


class WebSearchMetrics:
    """Track web search usage and effectiveness."""
    
    def __init__(self):
        self.searches_performed = 0
        self.searches_by_provider = {}
        self.searches_by_phase = {}
        self.average_confidence_with_search = 0.0
        self.average_confidence_without_search = 0.0
        
    def record_search(
        self,
        provider: str,
        phase: str,
        confidence: float,
        search_used: bool
    ):
        """Record a web search event."""
        if search_used:
            self.searches_performed += 1
            
            # Track by provider
            if provider not in self.searches_by_provider:
                self.searches_by_provider[provider] = 0
            self.searches_by_provider[provider] += 1
            
            # Track by phase
            if phase not in self.searches_by_phase:
                self.searches_by_phase[phase] = 0
            self.searches_by_phase[phase] += 1
        
        # Update confidence metrics
        # (This would need more sophisticated tracking in production)
        if search_used:
            self.average_confidence_with_search = (
                self.average_confidence_with_search * 0.9 + confidence * 0.1
            )
        else:
            self.average_confidence_without_search = (
                self.average_confidence_without_search * 0.9 + confidence * 0.1
            )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of web search metrics."""
        return {
            "total_searches": self.searches_performed,
            "by_provider": self.searches_by_provider,
            "by_phase": self.searches_by_phase,
            "confidence_impact": {
                "with_search": self.average_confidence_with_search,
                "without_search": self.average_confidence_without_search,
                "improvement": self.average_confidence_with_search - self.average_confidence_without_search
            }
        }


# Global configuration instance
web_search_config = WebSearchConfig()
web_search_metrics = WebSearchMetrics()