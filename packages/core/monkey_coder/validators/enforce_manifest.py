"""
Strict enforcement of MODEL_MANIFEST.md as the canonical source of truth.
This module ensures NO mock models, NO deprecated models, and ONLY live models.
"""

import os
import re
import sys
import logging
from pathlib import Path
from typing import Dict, Set, Tuple, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

class ModelManifestEnforcer:
    """
    Enforces strict compliance with MODEL_MANIFEST.md.
    NO mock models, NO test responses, ONLY canonical live models.
    """
    
    def __init__(self):
        self.manifest_path = Path(__file__).parent.parent.parent.parent.parent / "MODEL_MANIFEST.md"
        self._canonical_models: Dict[str, Set[str]] = {}
        self._deprecated_models: Dict[str, str] = {}
        self._load_manifest()
    
    def _load_manifest(self):
        """Parse MODEL_MANIFEST.md and extract canonical models."""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"MODEL_MANIFEST.md not found at {self.manifest_path}")
        
        content = self.manifest_path.read_text()
        
        # Extract valid models by provider
        self._canonical_models = {
            'openai': self._extract_models(content, "### OpenAI", "### Anthropic"),
            'anthropic': self._extract_models(content, "### Anthropic", "### Google"),
            'google': self._extract_models(content, "### Google", "### Groq"),
            'groq': self._extract_models(content, "### Groq", "### xAI"),
            'xai': self._extract_models(content, "### xAI", "## 🔄 Model Update Protocol"),
        }
        
        # Extract deprecated models and their replacements
        self._extract_deprecated_models(content)
        
        logger.info(f"Loaded canonical models from MODEL_MANIFEST.md")
        for provider, models in self._canonical_models.items():
            logger.info(f"  {provider}: {len(models)} models")
    
    def _extract_models(self, content: str, start_marker: str, end_marker: str) -> Set[str]:
        """Extract model names from a section of the manifest."""
        try:
            start_idx = content.index(start_marker)
            end_idx = content.index(end_marker) if end_marker in content else len(content)
            section = content[start_idx:end_idx]
            
            # Extract model names in backticks
            models = set()
            for match in re.finditer(r'`([^`]+)`', section):
                model_name = match.group(1)
                # Filter out non-model entries
                if not any(skip in model_name for skip in ['~~', '→', 'http', '/', '(', ')', 'Use']):
                    if model_name and not model_name.startswith('meta-llama'):
                        models.add(model_name)
                    elif model_name.startswith('meta-llama'):
                        # Include full path for llama models
                        models.add(model_name)
            
            return models
        except ValueError:
            logger.warning(f"Could not find section between {start_marker} and {end_marker}")
            return set()
    
    def _extract_deprecated_models(self, content: str):
        """Extract deprecated model mappings."""
        # Find all deprecated model replacements (format: ~~old~~ → Use `new`)
        for match in re.finditer(r'~~([^~]+)~~.*?Use `([^`]+)`', content):
            old_model = match.group(1)
            new_model = match.group(2)
            self._deprecated_models[old_model] = new_model
            logger.debug(f"Deprecated: {old_model} -> {new_model}")
    
    def validate_model(self, model_name: str, provider: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate if a model is canonical.
        Returns: (is_valid, error_message, suggested_replacement)
        """
        # Check for mock/test models
        if any(mock in model_name.lower() for mock in ['mock', 'test', 'fake', 'dummy', 'example']):
            return False, f"MOCK MODEL REJECTED: {model_name} is not a real model", None
        
        # Check if deprecated
        if model_name in self._deprecated_models:
            replacement = self._deprecated_models[model_name]
            return False, f"DEPRECATED MODEL: {model_name}", replacement
        
        # Check if canonical
        provider_models = self._canonical_models.get(provider.lower(), set())
        if model_name not in provider_models:
            # Try to find a close match
            suggestion = self._find_closest_model(model_name, provider_models)
            return False, f"NON-CANONICAL MODEL: {model_name} not in MODEL_MANIFEST.md", suggestion
        
        return True, None, None
    
    def _find_closest_model(self, model_name: str, valid_models: Set[str]) -> Optional[str]:
        """Find the closest valid model name."""
        # Simple heuristic: find models with similar prefixes
        for valid in valid_models:
            if model_name.startswith(valid.split('-')[0]):
                return valid
        return list(valid_models)[0] if valid_models else None
    
    def enforce_model(self, model_name: str, provider: str) -> str:
        """
        Enforce canonical model usage. Returns valid model or raises exception.
        """
        is_valid, error, suggestion = self.validate_model(model_name, provider)
        
        if not is_valid:
            if suggestion:
                logger.warning(f"{error}. Auto-correcting to: {suggestion}")
                return suggestion
            else:
                raise ValueError(f"{error}. No suitable replacement found. Check MODEL_MANIFEST.md")
        
        return model_name
    
    def validate_all_providers(self) -> Dict[str, list]:
        """Validate all provider configurations and return issues found."""
        issues = {}
        
        # Check common provider files
        provider_files = [
            'packages/core/monkey_coder/providers/openai_provider.py',
            'packages/core/monkey_coder/providers/anthropic_provider.py',
            'packages/core/monkey_coder/providers/google_provider.py',
            'packages/core/monkey_coder/providers/groq_provider.py',
        ]
        
        for file_path in provider_files:
            if Path(file_path).exists():
                content = Path(file_path).read_text()
                file_issues = []
                
                # Check for mock/test code
                if any(term in content.lower() for term in ['mock', 'fake', 'test_mode', 'dummy']):
                    file_issues.append("Contains mock/test code")
                
                # Check for deprecated models
                for deprecated in self._deprecated_models.keys():
                    if deprecated in content:
                        file_issues.append(f"References deprecated model: {deprecated}")
                
                # Check for hardcoded model lists
                if 'SUPPORTED_MODELS' in content or 'VALID_MODELS' in content:
                    file_issues.append("Contains hardcoded model list instead of using MODEL_MANIFEST.md")
                
                if file_issues:
                    issues[file_path] = file_issues
        
        return issues
    
    def get_canonical_models(self, provider: str) -> Set[str]:
        """Get all canonical models for a provider."""
        return self._canonical_models.get(provider.lower(), set())
    
    def is_mock_response(self, response: dict) -> bool:
        """Check if a response appears to be mocked."""
        if not response:
            return True
        
        # Check for common mock indicators
        mock_indicators = [
            'mock', 'test', 'fake', 'dummy', 'example',
            'This is a mock response', 'Test response',
            'TODO', 'PLACEHOLDER'
        ]
        
        response_str = str(response).lower()
        return any(indicator in response_str for indicator in mock_indicators)
    
    def startup_validation(self) -> bool:
        """
        Perform comprehensive startup validation.
        Returns True if all checks pass, False otherwise.
        """
        logger.info("=" * 60)
        logger.info("MODEL MANIFEST ENFORCEMENT - STARTUP VALIDATION")
        logger.info("=" * 60)
        
        all_valid = True
        
        # Check MODEL_MANIFEST.md exists
        if not self.manifest_path.exists():
            logger.error(f"❌ MODEL_MANIFEST.md not found at {self.manifest_path}")
            all_valid = False
        else:
            logger.info(f"✅ MODEL_MANIFEST.md found")
        
        # Check canonical models loaded
        total_models = sum(len(models) for models in self._canonical_models.values())
        logger.info(f"✅ Loaded {total_models} canonical models from {len(self._canonical_models)} providers")
        
        # Check for provider issues
        issues = self.validate_all_providers()
        if issues:
            logger.warning("⚠️  Provider issues found:")
            for file, file_issues in issues.items():
                logger.warning(f"  {file}:")
                for issue in file_issues:
                    logger.warning(f"    - {issue}")
            all_valid = False
        else:
            logger.info("✅ No provider compliance issues found")
        
        # Validate environment
        if os.getenv("MONKEY_CODER_TEST_MODE") == "1":
            logger.warning("⚠️  TEST_MODE is enabled - this should be disabled in production")
            all_valid = False
        
        if os.getenv("USE_MOCK_MODELS") == "1":
            logger.error("❌ USE_MOCK_MODELS is enabled - this MUST be disabled")
            all_valid = False
        
        logger.info("=" * 60)
        if all_valid:
            logger.info("✅ ALL VALIDATION CHECKS PASSED")
        else:
            logger.error("❌ VALIDATION FAILED - Fix issues before production")
        logger.info("=" * 60)
        
        return all_valid


# Global enforcer instance
_enforcer = None

def get_enforcer() -> ModelManifestEnforcer:
    """Get or create the global enforcer instance."""
    global _enforcer
    if _enforcer is None:
        _enforcer = ModelManifestEnforcer()
    return _enforcer

def validate_model(model_name: str, provider: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """Convenience function to validate a model."""
    return get_enforcer().validate_model(model_name, provider)

def enforce_model(model_name: str, provider: str) -> str:
    """Convenience function to enforce canonical model usage."""
    return get_enforcer().enforce_model(model_name, provider)

def startup_validation() -> bool:
    """Convenience function for startup validation."""
    return get_enforcer().startup_validation()


if __name__ == "__main__":
    # Run startup validation when executed directly
    enforcer = get_enforcer()
    is_valid = enforcer.startup_validation()
    
    # Test some model validations
    test_cases = [
        ("gpt-4-turbo", "openai"),  # Deprecated
        ("gpt-4.1", "openai"),  # Valid
        ("mock-model", "openai"),  # Mock
        ("claude-3-opus-20240229", "anthropic"),  # Deprecated
        ("claude-opus-4-20250514", "anthropic"),  # Valid
    ]
    
    print("\nTest Model Validations:")
    print("-" * 60)
    for model, provider in test_cases:
        is_valid, error, suggestion = enforcer.validate_model(model, provider)
        if is_valid:
            print(f"✅ {model} ({provider}): VALID")
        else:
            print(f"❌ {model} ({provider}): {error}")
            if suggestion:
                print(f"   Suggestion: Use {suggestion}")
    
    sys.exit(0 if is_valid else 1)