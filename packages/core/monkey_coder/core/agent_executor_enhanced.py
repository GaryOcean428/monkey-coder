"""
Enhanced Agent Executor with Web Search Capabilities

This module extends the agent executor to include web search tools,
date awareness, and instructions for verifying current information.

Supports web search features from:
- OpenAI (web_search_preview)
- Anthropic (search result injection)
- xAI/Grok (live search)
- Groq (web search)
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json

from ..providers import ProviderRegistry
from ..models import ProviderType

logger = logging.getLogger(__name__)


class EnhancedAgentExecutor:
    """Executes agent tasks with web search capabilities and date awareness."""
    
    def __init__(self, provider_registry: Optional[ProviderRegistry] = None):
        """Initialize the enhanced agent executor with provider registry."""
        self.provider_registry = provider_registry
        self.logger = logger
        self.current_date = datetime.utcnow().strftime("%B %d, %Y")
        
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
        Execute an agent task with web search capabilities.
        
        Args:
            agent_type: Type of agent (developer, reviewer, architect, etc.)
            prompt: The prompt to send to the AI
            provider: Specific provider to use (openai, anthropic, etc.)
            model: Specific model to use
            context: Additional context for the agent
            enable_web_search: Whether to enable web search tools
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
            
        # Build the messages with date awareness and web search reminders
        # Pass model info in context for tool selection
        enhanced_context = context or {}
        enhanced_context["model"] = model
        messages, tools = self._build_messages_with_tools(
            agent_type, prompt, enhanced_context, provider, enable_web_search
        )
        
        try:
            # Get the provider instance
            provider_instance = self._get_provider_instance(provider)
            
            if not provider_instance:
                raise ValueError(f"Provider {provider} not available")
            
            # Make the actual API call with tool support
            self.logger.info(
                f"Executing {agent_type} agent with {provider}/{model} "
                f"(web_search={'enabled' if enable_web_search and tools else 'disabled'})"
            )
            
            # Prepare the API call parameters
            api_params = {
                "model": model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 0.1),
                "stream": kwargs.get("stream", False)
            }
            
            # Add tools if supported by the provider
            if tools and self._provider_supports_tools(provider):
                api_params["tools"] = tools
                # Some providers need additional parameters
                if provider == "openai":
                    api_params["reasoning"] = kwargs.get("reasoning", {
                        "effort": "high",
                        "summary": "auto"
                    })
            
            # Call the provider's generate_completion method
            response = await provider_instance.generate_completion(**api_params)
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            # Extract the generated content
            if isinstance(response, dict):
                content = response.get("content", "")
                usage = response.get("usage", {})
                # Check if web search was used
                web_search_used = response.get("tools_used", [])
            else:
                content = str(response)
                usage = {}
                web_search_used = []
            
            self.logger.info(
                f"{agent_type} agent completed in {execution_time:.2f}s, "
                f"tokens: {usage.get('total_tokens', 'unknown')}, "
                f"web_search: {len(web_search_used) > 0}"
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
                "confidence": self._calculate_confidence(content, usage, web_search_used),
                "web_search_used": web_search_used,
                "current_date_aware": True
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
                "confidence": 0.0,
                "web_search_used": [],
                "current_date_aware": True
            }
    
    def _get_provider_for_agent(self, agent_type: str) -> str:
        """Determine the best provider for a given agent type."""
        # Map agent types to preferred providers with web search capability
        agent_provider_map = {
            "developer": "openai",  # GPT-4 with web search
            "reviewer": "anthropic",  # Claude for code review
            "architect": "openai",  # GPT-4 for architecture with web search
            "tester": "groq",  # Fast response with web search
            "documenter": "anthropic",  # Claude for documentation
            "security": "openai",  # GPT-4 for security analysis with web search
            "researcher": "grok",  # xAI Grok with live search
        }
        return agent_provider_map.get(agent_type, "openai")
    
    def _get_model_for_agent(self, agent_type: str, provider: str) -> str:
        """Determine the best model for a given agent type and provider."""
        model_map = {
            "openai": {
                "developer": "gpt-4.1",
                "reviewer": "gpt-4.1",
                "architect": "gpt-4.1",
                "security": "gpt-4.1",
                "researcher": "gpt-4.1",
                "default": "gpt-4.1"
            },
            "anthropic": {
                "developer": "claude-3-5-sonnet-20241022",
                "reviewer": "claude-3-5-sonnet-20241022",
                "documenter": "claude-3-5-sonnet-20241022",
                "default": "claude-3-5-sonnet-20241022"
            },
            "groq": {
                "tester": "llama-3.3-70b-versatile",
                "default": "llama-3.3-70b-versatile"
            },
            "google": {
                "default": "gemini-2.5-pro"
            },
            "grok": {
                "researcher": "grok-3",
                "default": "grok-3"
            },
            "xai": {
                "researcher": "grok-3",
                "default": "grok-3"
            }
        }
        
        provider_models = model_map.get(provider, {})
        return provider_models.get(agent_type, provider_models.get("default", "gpt-4.1"))
    
    def _build_messages_with_tools(
        self,
        agent_type: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None,
        enable_web_search: bool = True
    ) -> Tuple[List[Dict[str, str]], Optional[List[Dict[str, Any]]]]:
        """Build the message array with date awareness and tool configuration."""
        
        # Enhanced system prompts with date awareness and web search reminders
        system_prompts = {
            "developer": f"""You are an expert software developer. Today's date is {self.current_date}.

CRITICAL REMINDERS:
- Always verify library versions and API documentation through web search
- Check for breaking changes in recent updates  
- Confirm compatibility with current best practices
- Use web search for: package versions, API changes, security updates, best practices
- Be explicit when information comes from web search vs. training data

Your task is to write clean, efficient, and well-documented code using the most current libraries and patterns.
Focus on best practices, error handling, and maintainability.""",
            
            "reviewer": f"""You are a senior code reviewer. Today's date is {self.current_date}.

VERIFICATION REQUIREMENTS:
- Cross-check security vulnerabilities against current CVE databases using web search
- Verify deprecated methods against latest documentation
- Confirm current best practices through web search
- Check for recent updates that might affect the code
- Explicitly mention when using web-searched information

Analyze the provided code or requirements for potential issues, improvements, and best practices.
Provide constructive feedback and specific suggestions based on current standards.""",
            
            "architect": f"""You are a software architect. Today's date is {self.current_date}.

IMPORTANT:
- Research current architectural patterns and industry best practices through web search
- Verify framework capabilities and limitations with latest documentation
- Check for recent technology updates that might influence design decisions
- Consider current security recommendations and compliance requirements

Design scalable, maintainable system architectures using current best practices.
Consider design patterns, system boundaries, and technical trade-offs.""",
            
            "tester": f"""You are a QA engineer. Today's date is {self.current_date}.

TESTING REQUIREMENTS:
- Verify testing framework syntax against current documentation
- Check for recent updates to testing best practices
- Research common issues and edge cases for the technologies involved
- Use web search to find relevant test patterns and examples

Create comprehensive test cases, identify edge cases, and ensure code quality through testing strategies.""",
            
            "documenter": f"""You are a technical writer. Today's date is {self.current_date}.

DOCUMENTATION STANDARDS:
- Verify API documentation against current versions
- Check for recent changes in documentation best practices
- Research proper terminology and conventions for the technology stack
- Use web search to ensure accuracy of technical details

Create clear, comprehensive documentation that helps developers understand and use the code effectively.""",
            
            "security": f"""You are a security expert. Today's date is {self.current_date}.

SECURITY REQUIREMENTS:
- Search for recent CVEs and security advisories related to the code
- Verify current OWASP recommendations and security best practices
- Check for recent security patches and updates
- Research current threat landscape for the technology stack

Identify potential vulnerabilities, suggest security improvements, and ensure best security practices.""",
            
            "researcher": f"""You are a technical researcher. Today's date is {self.current_date}.

RESEARCH REQUIREMENTS:
- Use web search extensively to find current information
- Verify all technical details against recent documentation
- Cross-reference multiple sources for accuracy
- Clearly distinguish between web-searched facts and training knowledge

Research and provide accurate, up-to-date technical information."""
        }
        
        messages = [
            {
                "role": "system",
                "content": system_prompts.get(
                    agent_type,
                    f"""You are a helpful AI assistant specialized in software development. 
Today's date is {self.current_date}.

IMPORTANT: Use web search to verify any technical information, library versions, or best practices.
Always mention when information comes from web search vs. your training data."""
                )
            }
        ]
        
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
            if "previous_results" in context:
                messages.append({
                    "role": "user",
                    "content": f"Previous analysis results:\n{json.dumps(context['previous_results'], indent=2)}"
                })
        
        # Add the main prompt with web search reminder
        enhanced_prompt = f"""{prompt}

Remember: Today is {self.current_date}. Please use web search to verify any technical details, 
library versions, or best practices relevant to this task."""
        
        messages.append({
            "role": "user",
            "content": enhanced_prompt
        })
        
        # Build tools configuration if enabled
        tools = None
        if enable_web_search:
            # Get model from context or use default
            model = context.get("model") if context else None
            tools = self._get_tools_for_provider(provider, model)
        
        return messages, tools
    
    def _get_tools_for_provider(self, provider: str, model: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """Get the appropriate tool configuration for the provider."""
        if not provider:
            return None
        
        # Provider-specific tool configurations based on MODEL_MANIFEST.md and docs
        if provider == "openai":
            # GPT-5 models and newer GPT-4 models support web_search_preview
            web_search_models = [
                "gpt-5", "gpt-4.1", "o4", "o3"  # Models that support web search
            ]
            if model and any(m in model.lower() for m in web_search_models):
                return [{
                    "type": "web_search_preview",
                    "user_location": {
                        "type": "approximate",
                        "country": "US"
                    },
                    "search_context_size": "high"
                }]
            # For other OpenAI models, don't use web search tools
            return None
        
        elif provider == "anthropic":
            # Claude 3.5, 3.7, 4, and 4.1 support search via tool calling
            # They use a search_knowledge_base tool that returns SearchResultBlockParam
            web_search_models = ["claude-3-5", "claude-3-7", "claude-4", "claude-opus-4", "claude-sonnet-4"]
            if model and any(m in model.lower() for m in web_search_models):
                return [{
                    "name": "web_search",
                    "description": "Search the web for current information",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            }
                        },
                        "required": ["query"]
                    }
                }]
            return None
        
        elif provider == "groq":
            # Groq uses compound-beta model with automatic web search
            # No explicit tools needed - it handles search internally
            if model and "compound" in model.lower():
                # Groq compound model handles search automatically
                return None  # No explicit tools needed
            # For other Groq models, standard search may be available
            web_search_models = ["llama-3.3", "llama-4", "qwen", "kimi"]
            if model and any(m in model.lower() for m in web_search_models):
                return [{
                    "type": "web_search",
                    "enabled": True
                }]
            return None
        
        elif provider in ["grok", "xai"]:
            # xAI Grok models have live search built-in
            # Per docs: "Live Search (Beta) is available for all grok models by default"
            # No explicit tools needed - it's automatic
            return None  # Live search is automatic for Grok models
        
        # Google Gemini has different search integration
        return None
    
    def _provider_supports_tools(self, provider: str) -> bool:
        """Check if a provider supports the tools parameter."""
        return provider in ["openai", "anthropic", "groq"]  # These providers use explicit tools parameter
    
    def _get_provider_instance(self, provider_name: str):
        """Get a provider instance from the registry."""
        try:
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
    
    def _calculate_confidence(
        self, 
        content: str, 
        usage: Dict[str, Any],
        web_search_used: List[Any]
    ) -> float:
        """Calculate confidence score based on response quality."""
        if not content:
            return 0.0
        
        # Base confidence
        confidence = 0.5
        
        # Boost confidence if web search was used (more current information)
        if web_search_used:
            confidence += 0.2
        
        # Adjust based on content length
        if len(content) > 1000:
            confidence += 0.15
        elif len(content) > 500:
            confidence += 0.1
        
        # Adjust based on token usage
        if usage and usage.get("total_tokens", 0) > 1000:
            confidence += 0.1
        
        # Check for code blocks
        if "```" in content:
            confidence += 0.05
        
        return min(confidence, 1.0)