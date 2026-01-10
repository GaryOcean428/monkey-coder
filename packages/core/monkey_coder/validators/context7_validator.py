"""
Context7 Model Validator

This module integrates with Context7 MCP server to get real-time
documentation about available AI models, preventing the use of
outdated models that AI agents keep suggesting.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Set, Any
from datetime import datetime, timedelta
import aiohttp

from ..config.mcp_config import MCPConfig

logger = logging.getLogger(__name__)


class Context7ModelValidator:
    """
    Validates models against real-time documentation from Context7.
    
    This validator queries Context7 MCP server for up-to-date model
    information, ensuring we never use deprecated or non-existent models.
    """
    
    def __init__(self, cache_ttl_minutes: int = 60):
        """
        Initialize Context7 validator.
        
        Args:
            cache_ttl_minutes: How long to cache model info (default 60 min)
        """
        self.context7_url = MCPConfig.get_context7_url()
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self._cache: Dict[str, Any] = {}
        self._cache_time: Optional[datetime] = None
        
    async def fetch_model_docs(self, provider: str) -> Optional[Dict[str, Any]]:
        """
        Fetch current model documentation from Context7.
        
        Args:
            provider: Provider name (openai, anthropic, google, etc.)
            
        Returns:
            Model documentation or None if fetch fails
        """
        # Check cache first
        if self._is_cache_valid():
            cached = self._cache.get(f"{provider}_models")
            if cached:
                logger.debug(f"Using cached model info for {provider}")
                return cached
        
        try:
            # Prepare Context7 MCP request
            request_data = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "get-library-docs",
                    "arguments": {
                        "context7CompatibleLibraryID": f"/{provider}/models",
                        "tokens": 5000,
                        "topic": "available-models"
                    }
                },
                "id": f"model-query-{provider}-{datetime.now().timestamp()}"
            }
            
            logger.info(f"Fetching {provider} model docs from Context7...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.context7_url,
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Parse Context7 response
                        if "result" in result:
                            model_info = self._parse_context7_response(result["result"], provider)
                            
                            # Cache the result
                            self._cache[f"{provider}_models"] = model_info
                            self._cache_time = datetime.now()
                            
                            logger.info(f"Successfully fetched {provider} models from Context7")
                            return model_info
                        else:
                            logger.warning(f"Invalid Context7 response for {provider}: {result}")
                    else:
                        logger.warning(f"Context7 returned status {response.status} for {provider}")
                        
        except asyncio.TimeoutError:
            logger.warning(f"Context7 request timed out for {provider}")
        except Exception as e:
            logger.error(f"Error fetching {provider} models from Context7: {e}")
        
        return None
    
    def _parse_context7_response(self, response: Dict[str, Any], provider: str) -> Dict[str, Any]:
        """
        Parse Context7 response to extract model information.
        
        Args:
            response: Raw Context7 response
            provider: Provider name
            
        Returns:
            Parsed model information
        """
        model_info = {
            "provider": provider,
            "models": [],
            "deprecated": [],
            "last_updated": datetime.now().isoformat()
        }
        
        # Extract content from Context7 response
        content = response.get("content", "")
        
        if isinstance(content, str):
            # Parse markdown content for model names
            lines = content.split("\n")
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                # Detect sections
                if "available" in line.lower() and "model" in line.lower():
                    current_section = "available"
                elif "deprecated" in line.lower():
                    current_section = "deprecated"
                elif "legacy" in line.lower():
                    current_section = "deprecated"
                
                # Extract model names (usually in code blocks or lists)
                if current_section and (line.startswith("-") or line.startswith("*")):
                    # Extract model name from list item
                    import re
                    match = re.search(r'`([^`]+)`', line)
                    if match:
                        model_name = match.group(1)
                        if current_section == "available":
                            model_info["models"].append(model_name)
                        elif current_section == "deprecated":
                            model_info["deprecated"].append(model_name)
        
        return model_info
    
    async def validate_model_with_context7(self, model: str, provider: str) -> tuple[bool, Optional[str]]:
        """
        Validate a model against Context7 documentation.
        
        Args:
            model: Model name to validate
            provider: Provider name
            
        Returns:
            Tuple of (is_valid, suggestion)
        """
        # Fetch current model docs
        model_docs = await self.fetch_model_docs(provider)
        
        if not model_docs:
            # Context7 unavailable, fall back to local validation
            logger.debug(f"Context7 unavailable, cannot validate {model} for {provider}")
            return None, None
        
        # Check if model is in available list
        available_models = model_docs.get("models", [])
        deprecated_models = model_docs.get("deprecated", [])
        
        if model in available_models:
            return True, None
        
        if model in deprecated_models:
            # Suggest the newest available model
            suggestion = available_models[0] if available_models else None
            return False, suggestion
        
        # Model not found, suggest closest match
        suggestion = self._find_closest_model(model, available_models)
        return False, suggestion
    
    def _find_closest_model(self, model: str, available_models: List[str]) -> Optional[str]:
        """
        Find the closest matching model from available models.
        
        Args:
            model: Invalid model name
            available_models: List of valid models
            
        Returns:
            Closest matching model or None
        """
        if not available_models:
            return None
        
        # Simple heuristic: find models with similar prefixes
        model_lower = model.lower()
        
        for available in available_models:
            if model_lower.startswith(available.lower()[:3]):
                return available
        
        # Default to the first (usually newest) model
        return available_models[0]
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if not self._cache_time:
            return False
        return datetime.now() - self._cache_time < self.cache_ttl
    
    async def get_all_provider_models(self) -> Dict[str, List[str]]:
        """
        Get all available models for all providers from Context7.
        
        Returns:
            Dictionary mapping provider to list of available models
        """
        providers = ["openai", "anthropic", "google", "groq", "xai"]
        all_models = {}
        
        for provider in providers:
            model_docs = await self.fetch_model_docs(provider)
            if model_docs:
                all_models[provider] = model_docs.get("models", [])
            else:
                all_models[provider] = []
        
        return all_models
    
    async def sync_with_manifest(self, manifest_path: str) -> Dict[str, Any]:
        """
        Sync Context7 data with local MODEL_MANIFEST.md.
        
        Args:
            manifest_path: Path to MODEL_MANIFEST.md
            
        Returns:
            Sync report with differences found
        """
        # Get models from Context7
        context7_models = await self.get_all_provider_models()
        
        # Read local manifest
        from .model_validator import ModelManifestValidator
        local_validator = ModelManifestValidator(manifest_path)
        local_models = local_validator.get_valid_models()
        
        # Compare and report differences
        report = {
            "timestamp": datetime.now().isoformat(),
            "source": "Context7",
            "differences": {}
        }
        
        for provider in context7_models:
            context7_set = set(context7_models.get(provider, []))
            local_set = set(local_models.get(provider, []))
            
            only_in_context7 = context7_set - local_set
            only_in_local = local_set - context7_set
            
            if only_in_context7 or only_in_local:
                report["differences"][provider] = {
                    "only_in_context7": list(only_in_context7),
                    "only_in_local": list(only_in_local),
                    "context7_count": len(context7_set),
                    "local_count": len(local_set)
                }
        
        return report


class HybridModelValidator:
    """
    Combines local MODEL_MANIFEST.md validation with Context7 real-time checks.
    
    This provides the best of both worlds:
    - Fast local validation from MODEL_MANIFEST.md
    - Real-time updates from Context7 when available
    """
    
    def __init__(self, manifest_path: Optional[str] = None):
        """Initialize hybrid validator."""
        from .model_validator import ModelManifestValidator
        
        self.local_validator = ModelManifestValidator(manifest_path)
        self.context7_validator = Context7ModelValidator()
        
    async def validate_model(self, model: str, provider: str) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Validate model using both local and Context7 sources.
        
        Args:
            model: Model name to validate
            provider: Provider name
            
        Returns:
            Tuple of (is_valid, error_message, suggestion)
        """
        # First try Context7 for real-time validation
        try:
            context7_valid, context7_suggestion = await asyncio.wait_for(
                self.context7_validator.validate_model_with_context7(model, provider),
                timeout=2.0  # Fast timeout
            )
            
            if context7_valid is not None:
                # Got a response from Context7
                if context7_valid:
                    return True, None, None
                else:
                    error = f"Model '{model}' not found in Context7 documentation"
                    return False, error, context7_suggestion
        except asyncio.TimeoutError:
            logger.debug("Context7 validation timed out, falling back to local")
        except Exception as e:
            logger.debug(f"Context7 validation failed: {e}, falling back to local")
        
        # Fall back to local validation
        return self.local_validator.validate_model(model, provider)
    
    async def update_manifest_from_context7(self) -> Dict[str, Any]:
        """
        Update MODEL_MANIFEST.md with latest data from Context7.
        
        Returns:
            Update report
        """
        report = await self.context7_validator.sync_with_manifest(
            self.local_validator.manifest_path
        )
        
        if report["differences"]:
            logger.info(f"Found differences between Context7 and local manifest: {report}")
            # Could automatically update the manifest here if desired
        
        return report


# Example usage
if __name__ == "__main__":
    async def test_context7():
        """Test Context7 integration."""
        validator = Context7ModelValidator()
        
        # Test fetching OpenAI models
        print("Fetching OpenAI models from Context7...")
        models = await validator.fetch_model_docs("openai")
        if models:
            print(f"Found {len(models.get('models', []))} OpenAI models")
            print(f"Models: {models.get('models', [])[:5]}...")
        else:
            print("Could not fetch models from Context7")
        
        # Test validation
        test_cases = [
            ("gpt-4-turbo", "openai"),
            ("gpt-4.1", "openai"),
            ("claude-3-opus", "anthropic"),
        ]
        
        for model, provider in test_cases:
            is_valid, suggestion = await validator.validate_model_with_context7(model, provider)
            print(f"\n{model} ({provider}):")
            print(f"  Valid: {is_valid}")
            if suggestion:
                print(f"  Suggestion: {suggestion}")
    
    # Run the test
    asyncio.run(test_context7())