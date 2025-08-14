"""
Agent Executor - Real AI Provider Integration

This module connects the orchestration system to actual AI providers,
replacing mock simulations with real API calls.

Implements modern orchestration patterns inspired by OpenAI's agents framework:
- Specialized agents for different tasks
- Real provider API calls instead of mocks
- Proper handoff between agents
- Context management across agent calls
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..providers import ProviderRegistry
from ..models import ProviderType

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
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute an agent task using real AI provider calls.
        
        Args:
            agent_type: Type of agent (developer, reviewer, architect, etc.)
            prompt: The prompt to send to the AI
            provider: Specific provider to use (openai, anthropic, etc.)
            model: Specific model to use
            context: Additional context for the agent
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
            
        # Build the messages for the AI
        messages = self._build_messages(agent_type, prompt, context)
        
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
                "developer": "gpt-4-turbo",
                "reviewer": "gpt-4-turbo",
                "architect": "gpt-4-turbo",
                "default": "gpt-4-turbo"
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
                "default": "gemini-1.5-pro"
            },
            "xai": {
                "default": "grok-3"
            }
        }
        
        provider_models = model_map.get(provider, {})
        return provider_models.get(agent_type, provider_models.get("default", "gpt-4-turbo"))
    
    def _build_messages(
        self,
        agent_type: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """Build the message array for the AI API."""
        # System prompts for different agent types
        system_prompts = {
            "developer": """You are an expert software developer. Your task is to write clean, efficient, and well-documented code. 
Focus on best practices, error handling, and maintainability. Provide complete, working implementations.""",
            
            "reviewer": """You are a senior code reviewer. Analyze the provided code or requirements for potential issues, 
improvements, and best practices. Provide constructive feedback and specific suggestions.""",
            
            "architect": """You are a software architect. Design scalable, maintainable system architectures. 
Consider design patterns, system boundaries, and technical trade-offs.""",
            
            "tester": """You are a QA engineer. Create comprehensive test cases, identify edge cases, 
and ensure code quality through testing strategies.""",
            
            "documenter": """You are a technical writer. Create clear, comprehensive documentation 
that helps developers understand and use the code effectively.""",
            
            "security": """You are a security expert. Identify potential vulnerabilities, 
suggest security improvements, and ensure best security practices."""
        }
        
        messages = [
            {
                "role": "system",
                "content": system_prompts.get(
                    agent_type,
                    "You are a helpful AI assistant specialized in software development."
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