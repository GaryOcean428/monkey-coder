"""
Base Provider with Model Manifest Enforcement

All providers MUST inherit from this base class to ensure
model compliance with MODEL_MANIFEST.md.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from datetime import datetime

from ..models import ProviderType, ModelInfo
# Use compliance facade to avoid import ambiguity with models module vs package
from ..compliance import enforce_model_compliance, validate_model

logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    """
    Abstract base class for AI providers with MODEL_MANIFEST.md enforcement.

    All provider adapters must implement this interface to ensure
    consistent behavior across different AI services and model compliance.
    """

    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs
        self.client = None
        self._models_cache = None
        self._last_model_update = None

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Return the provider type."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        pass

    def validate_and_fix_model(self, model: str) -> str:
        """
        Validate model against MODEL_MANIFEST.md and auto-correct if needed.

        Args:
            model: Requested model name

        Returns:
            Valid model name (original if valid, replacement if not)
        """
        provider_name = self.provider_type.value if hasattr(self.provider_type, 'value') else str(self.provider_type).lower()

        # Enforce compliance
        valid_model = enforce_model_compliance(model, provider_name)

        if valid_model != model:
            logger.warning(
                f"MODEL COMPLIANCE: Auto-corrected '{model}' to '{valid_model}' "
                f"for {provider_name}. Please update to use the correct model name."
            )

        return valid_model

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider client."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup provider resources."""
        pass

    async def validate_model(self, model_name: str) -> bool:
        """
        Validate model name against MODEL_MANIFEST.md.

        Args:
            model_name: Model to validate

        Returns:
            True if model is valid
        """
        provider_name = self.provider_type.value if hasattr(self.provider_type, 'value') else str(self.provider_type).lower()
        is_valid, _, _ = validate_model(model_name, provider_name)
        return is_valid

    @abstractmethod
    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models from provider."""
        pass

    async def generate_completion(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate completion with automatic model validation.

        Args:
            model: Requested model (will be validated/corrected)
            messages: Conversation messages
            **kwargs: Additional parameters

        Returns:
            Completion response
        """
        # Validate and fix model name
        valid_model = self.validate_and_fix_model(model)

        # Call the actual implementation
        return await self._generate_completion_impl(valid_model, messages, **kwargs)

    @abstractmethod
    async def _generate_completion_impl(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """Actual completion implementation (model already validated)."""
        pass

    @abstractmethod
    async def get_model_info(self, model_name: str) -> ModelInfo:
        """Get detailed information about a specific model."""
        pass

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the provider."""
        try:
            models = await self.get_available_models()
            return {
                "status": "healthy",
                "model_count": len(models),
                "manifest_compliant": True,
                "last_updated": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Health check failed for {self.name}: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "manifest_compliant": False,
                "last_updated": datetime.utcnow().isoformat(),
            }