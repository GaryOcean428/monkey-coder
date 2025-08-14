"""
Agent Executor - Real AI Provider Integration with Web Search

This module connects the orchestration system to actual AI providers,
replacing mock simulations with real API calls and web search capabilities.

Implements modern orchestration patterns inspired by OpenAI's agents framework:
- Specialized agents for different tasks
- Real provider API calls instead of mocks
- Integrated web search for current information
- Proper handoff between agents
- Context management across agent calls
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..providers import ProviderRegistry
from ..models import ProviderType
from ..tools.web_search_tool import web_search_tool, SearchResult
from ..config.web_search_config import WebSearchPrompts, web_search_metrics

logger = logging.getLogger(__name__)


class AgentExecutor:
    """Executes agent tasks by making real calls to AI providers."""
    
    def __init__(self, provider_registry: Optional[ProviderRegistry] = None):
        """Initialize the agent executor with provider registry."""
        self.provider_registry = provider_registry
        self.logger = logger
        
    async def execute_agent_task(
        self,
        agent_type: str,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        enable_web_search: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute an agent task using real AI provider calls with optional web search.
        
        Args:
            agent_type: Type of agent (developer, reviewer, architect, etc.)
            prompt: The prompt to send to the AI
            provider: Specific provider to use (openai, anthropic, etc.)
            model: Specific model to use
            context: Additional context for the agent
            enable_web_search: Whether to enable web search for current information
            **kwargs: Additional parameters for the API call
            
        Returns:
            Dict containing the agent's response and metadata
        """
        start_time = datetime.utcnow()
        
        # Determine provider and model based on agent type if not specified
        if not provider:
            provider = self._get_provider_for_agent(agent_type)
        if not model:
            model = self._get_model_for_agent(agent_type, provider)
        
        # Perform web search if enabled and relevant
        web_search_results = []
        if enable_web_search and self._should_use_web_search(agent_type, prompt):
            web_search_results = await self._perform_web_search(agent_type, prompt, context)
            
        # Build the messages for the AI with web search results
        messages = self._build_messages(agent_type, prompt, context, web_search_results)
        
        try:
            # Get the provider instance
            provider_instance = self._get_provider_instance(provider)
            
            if not provider_instance:
                raise ValueError(f"Provider {provider} not available")
            
            # Make the actual API call
            self.logger.info(f"Executing {agent_type} agent with {provider}/{model}")
            
            # Call the provider's generate_completion method
            response = await provider_instance.generate_completion(
                model=model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 4096),
                temperature=kwargs.get("temperature", 0.1),
                stream=kwargs.get("stream", False)
            )
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            # Extract the generated content
            if isinstance(response, dict):
                content = response.get("content", "")
                usage = response.get("usage", {})
            else:
                # Handle streaming or other response types
                content = str(response)
                usage = {}
            
            self.logger.info(
                f"{agent_type} agent completed in {execution_time:.2f}s, "
                f"tokens: {usage.get('total_tokens', 'unknown')}"
            )
            
            return {
                "agent_id": f"{agent_type}_{provider}",
                "agent_type": agent_type,
                "status": "completed",
                "output": content,
                "provider": provider,
                "model": model,
                "usage": usage,
                "execution_time": execution_time,
                "confidence": self._calculate_confidence(content, usage)
            }
            
        except Exception as e:
            self.logger.error(f"Error executing {agent_type} agent: {str(e)}")
            return {
                "agent_id": f"{agent_type}_{provider}",
                "agent_type": agent_type,
                "status": "failed",
                "error": str(e),
                "provider": provider,
                "model": model,
                "output": f"Error: {str(e)}",
                "confidence": 0.0
            }
    
    def _get_provider_for_agent(self, agent_type: str) -> str:
        """Determine the best provider for a given agent type."""
        # Map agent types to preferred providers
        agent_provider_map = {
            "developer": "openai",  # GPT-4 for code generation
            "reviewer": "anthropic",  # Claude for code review
            "architect": "openai",  # GPT-4 for architecture
            "tester": "groq",  # Fast response for test generation
            "documenter": "anthropic",  # Claude for documentation
            "security": "openai",  # GPT-4 for security analysis
        }
        return agent_provider_map.get(agent_type, "openai")
    
    def _get_model_for_agent(self, agent_type: str, provider: str) -> str:
        """Determine the best model for a given agent type and provider."""
        # Map to actual available models (not future models)
        model_map = {
            "openai": {
                "developer": "gpt-4.1",
                "reviewer": "gpt-4.1",
                "architect": "gpt-4.1",
                "default": "gpt-4.1"
            },
            "anthropic": {
                "developer": "claude-3-5-sonnet-20241022",
                "reviewer": "claude-3-5-sonnet-20241022",
                "documenter": "claude-3-5-sonnet-20241022",
                "default": "claude-3-5-sonnet-20241022"
            },
            "groq": {
                "default": "llama-3.3-70b-versatile"
            },
            "google": {
                "default": "gemini-2.5-pro"
            },
            "xai": {
                "default": "grok-3"
            }
        }
        
        provider_models = model_map.get(provider, {})
        return provider_models.get(agent_type, provider_models.get("default", "gpt-4.1"))
    
    def _build_messages(
        self,
        agent_type: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        web_search_results: Optional[List[SearchResult]] = None
    ) -> List[Dict[str, str]]:
        """Build the message array for the AI API with web search integration."""
        # System prompts for different agent types with web search awareness
        system_prompts = {
            "developer": """You are an expert software developer with access to current web information. Your task is to write clean, efficient, and well-documented code. 
Focus on best practices, error handling, and maintainability. Provide complete, working implementations.
When web search results are provided, use them to ensure you're using the latest APIs and best practices.""",
            
            "reviewer": """You are a senior code reviewer with access to current documentation. Analyze the provided code or requirements for potential issues, 
improvements, and best practices. Provide constructive feedback and specific suggestions.
When web search results are provided, verify against current standards and known issues.""",
            
            "architect": """You are a software architect with access to current architectural patterns. Design scalable, maintainable system architectures. 
Consider design patterns, system boundaries, and technical trade-offs.
When web search results are provided, incorporate modern patterns and industry standards.""",
            
            "tester": """You are a QA engineer with access to testing best practices. Create comprehensive test cases, identify edge cases, 
and ensure code quality through testing strategies.
When web search results are provided, use them to identify common failure patterns.""",
            
            "documenter": """You are a technical writer with access to documentation standards. Create clear, comprehensive documentation 
that helps developers understand and use the code effectively.
When web search results are provided, ensure accuracy and follow current conventions.""",
            
            "security": """You are a security expert with access to current CVE databases. Identify potential vulnerabilities, 
suggest security improvements, and ensure best security practices.
When web search results are provided, check for known vulnerabilities and latest security patches."""
        }
        
        # Add date awareness
        system_content = system_prompts.get(
            agent_type,
            "You are a helpful AI assistant specialized in software development."
        )
        system_content += f"\n\n{WebSearchPrompts.get_date_awareness_prompt()}"
        
        messages = [
            {
                "role": "system",
                "content": system_content
            }
        ]
        
        # Add web search results if available
        if web_search_results:
            search_content = self._format_web_search_results(web_search_results)
            messages.append({
                "role": "system",
                "content": f"Web Search Results (current information):\n{search_content}"
            })
        
        # Add context if provided
        if context:
            if "previous_code" in context:
                messages.append({
                    "role": "user",
                    "content": f"Previous code context:\n```\n{context['previous_code']}\n```"
                })
            if "requirements" in context:
                messages.append({
                    "role": "user",
                    "content": f"Requirements:\n{context['requirements']}"
                })
            if "phase" in context:
                # Add phase-specific web search reminder
                reminder = WebSearchPrompts.get_phase_specific_reminder(context["phase"])
                if reminder:
                    messages.append({
                        "role": "system",
                        "content": reminder
                    })
        
        # Add the main prompt
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        return messages
    
    def _get_provider_instance(self, provider_name: str):
        """Get a provider instance from the registry."""
        try:
            # Convert string to ProviderType enum
            provider_type_map = {
                "openai": ProviderType.OPENAI,
                "anthropic": ProviderType.ANTHROPIC,
                "google": ProviderType.GOOGLE,
                "groq": ProviderType.GROQ,
                "xai": ProviderType.GROK,
                "grok": ProviderType.GROK
            }
            
            provider_type = provider_type_map.get(provider_name.lower())
            if not provider_type:
                self.logger.error(f"Unknown provider: {provider_name}")
                return None
            
            # Get the provider from registry
            provider = self.provider_registry.get_provider(provider_type)
            if not provider:
                self.logger.error(f"Provider {provider_name} not initialized")
                return None
                
            return provider
            
        except Exception as e:
            self.logger.error(f"Error getting provider {provider_name}: {str(e)}")
            return None
    
    def _calculate_confidence(self, content: str, usage: Dict[str, Any]) -> float:
        """Calculate confidence score based on response quality."""
        if not content:
            return 0.0
        
        # Basic confidence calculation
        confidence = 0.5  # Base confidence
        
        # Adjust based on content length (longer is usually more complete)
        if len(content) > 1000:
            confidence += 0.2
        elif len(content) > 500:
            confidence += 0.1
        
        # Adjust based on token usage (if available)
        if usage and usage.get("total_tokens", 0) > 1000:
            confidence += 0.2
        
        # Check for code blocks (indicates actual code generation)
        if "```" in content:
            confidence += 0.1
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def _should_use_web_search(self, agent_type: str, prompt: str) -> bool:
        """Determine if web search should be used for this task."""
        # Keywords that suggest web search would be helpful
        search_keywords = [
            "latest", "current", "recent", "documentation", "api",
            "error", "bug", "issue", "best practice", "standard",
            "security", "vulnerability", "cve", "patch", "update",
            "version", "release", "deprecated", "breaking change",
            "library", "framework", "package", "dependency"
        ]
        
        prompt_lower = prompt.lower()
        
        # Check if any search keywords are in the prompt
        needs_search = any(keyword in prompt_lower for keyword in search_keywords)
        
        # Agent types that benefit most from web search
        search_agents = ["developer", "reviewer", "security", "documenter"]
        
        return needs_search or agent_type in search_agents
    
    async def _perform_web_search(
        self,
        agent_type: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Perform web search based on agent type and prompt."""
        search_results = []
        
        try:
            # Determine search type based on agent
            search_type_map = {
                "developer": "technical",
                "reviewer": "best_practices",
                "architect": "documentation",
                "tester": "testing",
                "documenter": "documentation",
                "security": "security"
            }
            search_type = search_type_map.get(agent_type, "general")
            
            # Extract key terms from prompt for search
            search_query = self._extract_search_query(prompt, context)
            
            if search_query:
                self.logger.info(f"Performing web search for {agent_type}: {search_query[:100]}")
                
                # Perform the actual web search
                search_results = await web_search_tool.search(
                    query=search_query,
                    search_type=search_type,
                    max_results=5,
                    filter_recent=True
                )
                
                # Record metrics
                phase = context.get("phase", "unknown") if context else "unknown"
                confidence_boost = 0.1 if search_results else 0.0
                web_search_metrics.record_search(
                    provider=agent_type,
                    phase=phase,
                    confidence=0.8 + confidence_boost,
                    search_used=True
                )
                
                self.logger.info(f"Found {len(search_results)} web search results")
        
        except Exception as e:
            self.logger.error(f"Web search failed: {str(e)}")
            # Continue without search results rather than failing
        
        return search_results
    
    def _extract_search_query(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Extract a search query from the prompt and context."""
        # Simple extraction - in production would use NLP
        query_parts = []
        
        # Look for specific technical terms
        tech_terms = []
        keywords = ["fastapi", "python", "javascript", "react", "api", "database", "async", "error"]
        prompt_lower = prompt.lower()
        
        for keyword in keywords:
            if keyword in prompt_lower:
                tech_terms.append(keyword)
        
        if tech_terms:
            query_parts.extend(tech_terms[:2])  # Limit to 2 terms
        
        # Add task type if available
        if context and "task_type" in context:
            query_parts.append(str(context["task_type"]))
        
        # Extract error messages if present
        if "error:" in prompt_lower or "exception:" in prompt_lower:
            # Try to extract the error message
            error_start = max(
                prompt_lower.find("error:"),
                prompt_lower.find("exception:")
            )
            if error_start > -1:
                error_text = prompt[error_start:error_start+100].strip()
                query_parts.append(f'"{error_text}"')
        
        # If no specific terms found, use first 50 chars of prompt
        if not query_parts:
            query_parts.append(prompt[:50])
        
        return " ".join(query_parts)
    
    def _format_web_search_results(self, results: List[SearchResult]) -> str:
        """Format web search results for inclusion in AI prompt."""
        if not results:
            return "No web search results available."
        
        formatted = []
        for i, result in enumerate(results[:5], 1):  # Limit to top 5
            formatted.append(f"""
Result {i}:
Title: {result.title}
Source: {result.source}
URL: {result.url}
Summary: {result.snippet[:200]}...
Relevance: {result.relevance_score:.2f}
""")
        
        return "\n".join(formatted)