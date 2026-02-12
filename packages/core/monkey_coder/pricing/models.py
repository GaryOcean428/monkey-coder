"""
Model pricing data and management.

This module handles pricing information for different AI models,
including fetching updated pricing data and calculating costs.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from pathlib import Path

from pydantic import BaseModel, Field

# Local helper to determine pricing file path without importing config package/module
def _get_pricing_file_path() -> Path:
    """Resolve the pricing data file path consistently across environments."""
    try:
        base_dir = Path("/data") if os.path.exists("/data") and os.access("/data", os.W_OK) else Path.cwd() / "data"
        pricing_dir = base_dir / "pricing"
        pricing_dir.mkdir(parents=True, exist_ok=True)
        return pricing_dir / "pricing_data.json"
    except Exception:
        # Fallback to current directory if anything goes wrong
        return Path("pricing_data.json")

logger = logging.getLogger(__name__)


class ModelPricing(BaseModel):
    """
    Pricing information for an AI model.
    """
    model_id: str = Field(..., description="Model identifier")
    provider: str = Field(..., description="Provider name")

    # Pricing per token (in USD)
    input_cost_per_token: float = Field(..., description="Cost per input token")
    output_cost_per_token: float = Field(..., description="Cost per output token")

    # Additional pricing info
    context_length: int = Field(default=4096, description="Maximum context length")
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> Tuple[float, float, float]:
        """
        Calculate costs for token usage.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Tuple[float, float, float]: (input_cost, output_cost, total_cost)
        """
        input_cost = input_tokens * self.input_cost_per_token
        output_cost = output_tokens * self.output_cost_per_token
        total_cost = input_cost + output_cost

        return input_cost, output_cost, total_cost


# Current pricing data (updated nightly)
# Prices are per 1 token (not per 1K tokens) for easier calculation
# Models must match exactly with MODEL_REGISTRY in models.py
MODEL_PRICING_DATA: Dict[str, ModelPricing] = {
    # OpenAI — GPT-5.x Series (Latest)
    "gpt-5.2": ModelPricing(
        model_id="gpt-5.2",
        provider="openai",
        input_cost_per_token=0.00000175,  # $1.75 per 1M input tokens
        output_cost_per_token=0.000014,   # $14.00 per 1M output tokens
        context_length=400000
    ),
    "gpt-5.2-codex": ModelPricing(
        model_id="gpt-5.2-codex",
        provider="openai",
        input_cost_per_token=0.00000175,  # $1.75 per 1M input tokens
        output_cost_per_token=0.000014,   # $14.00 per 1M output tokens
        context_length=400000
    ),
    "gpt-5.2-pro": ModelPricing(
        model_id="gpt-5.2-pro",
        provider="openai",
        input_cost_per_token=0.000021,    # $21.00 per 1M input tokens
        output_cost_per_token=0.000168,   # $168.00 per 1M output tokens
        context_length=400000
    ),
    "gpt-5.3-codex": ModelPricing(
        model_id="gpt-5.3-codex",
        provider="openai",
        input_cost_per_token=0.000002,    # $2.00 per 1M input tokens
        output_cost_per_token=0.000014,   # $14.00 per 1M output tokens
        context_length=400000
    ),
    "gpt-5.1": ModelPricing(
        model_id="gpt-5.1",
        provider="openai",
        input_cost_per_token=0.00000125,  # $1.25 per 1M input tokens
        output_cost_per_token=0.00001,    # $10.00 per 1M output tokens
        context_length=400000
    ),
    "gpt-5": ModelPricing(
        model_id="gpt-5",
        provider="openai",
        input_cost_per_token=0.0000025,   # $2.50 per 1M input tokens
        output_cost_per_token=0.00001,    # $10.00 per 1M output tokens
        context_length=200000
    ),
    "gpt-5-mini": ModelPricing(
        model_id="gpt-5-mini",
        provider="openai",
        input_cost_per_token=0.00000015,  # $0.15 per 1M input tokens
        output_cost_per_token=0.0000006,  # $0.60 per 1M output tokens
        context_length=200000
    ),
    "gpt-5-nano": ModelPricing(
        model_id="gpt-5-nano",
        provider="openai",
        input_cost_per_token=0.00000005,  # $0.05 per 1M input tokens
        output_cost_per_token=0.0000002,  # $0.20 per 1M output tokens
        context_length=200000
    ),
    # OpenAI — GPT-4.1 Series (Production)
    "gpt-4.1": ModelPricing(
        model_id="gpt-4.1",
        provider="openai",
        input_cost_per_token=0.0000025,   # $2.50 per 1M input tokens
        output_cost_per_token=0.00001,    # $10.00 per 1M output tokens
        context_length=200000
    ),
    "gpt-4.1-mini": ModelPricing(
        model_id="gpt-4.1-mini",
        provider="openai",
        input_cost_per_token=0.00000012,  # $0.12 per 1M input tokens
        output_cost_per_token=0.00000048, # $0.48 per 1M output tokens
        context_length=1000000
    ),
    "gpt-4.1-nano": ModelPricing(
        model_id="gpt-4.1-nano",
        provider="openai",
        input_cost_per_token=0.00000005,  # $0.05 per 1M input tokens
        output_cost_per_token=0.0000002,  # $0.20 per 1M output tokens
        context_length=1000000
    ),
    # OpenAI — Reasoning models
    "o3-pro": ModelPricing(
        model_id="o3-pro",
        provider="openai",
        input_cost_per_token=0.000015,    # $15.00 per 1M input tokens
        output_cost_per_token=0.00006,    # $60.00 per 1M output tokens
        context_length=200000
    ),
    "o3": ModelPricing(
        model_id="o3",
        provider="openai",
        input_cost_per_token=0.000002,    # $2.00 per 1M input tokens
        output_cost_per_token=0.000008,   # $8.00 per 1M output tokens
        context_length=200000
    ),
    "o3-mini": ModelPricing(
        model_id="o3-mini",
        provider="openai",
        input_cost_per_token=0.0000006,   # $0.60 per 1M input tokens
        output_cost_per_token=0.0000024,  # $2.40 per 1M output tokens
        context_length=200000
    ),
    "o4-mini": ModelPricing(
        model_id="o4-mini",
        provider="openai",
        input_cost_per_token=0.0000011,   # $1.10 per 1M input tokens
        output_cost_per_token=0.0000044,  # $4.40 per 1M output tokens
        context_length=200000
    ),
    "o3-deep-research": ModelPricing(
        model_id="o3-deep-research",
        provider="openai",
        input_cost_per_token=0.000015,    # $15.00 per 1M input tokens
        output_cost_per_token=0.00006,    # $60.00 per 1M output tokens
        context_length=200000
    ),
    "o4-mini-deep-research": ModelPricing(
        model_id="o4-mini-deep-research",
        provider="openai",
        input_cost_per_token=0.000003,    # $3.00 per 1M input tokens
        output_cost_per_token=0.000012,   # $12.00 per 1M output tokens
        context_length=200000
    ),
    # OpenAI — Open-weight models
    "gpt-oss-120b": ModelPricing(
        model_id="gpt-oss-120b",
        provider="openai",
        input_cost_per_token=0.0,         # Free (Apache 2.0)
        output_cost_per_token=0.0,
        context_length=131072
    ),
    "gpt-oss-20b": ModelPricing(
        model_id="gpt-oss-20b",
        provider="openai",
        input_cost_per_token=0.0,         # Free (Apache 2.0)
        output_cost_per_token=0.0,
        context_length=131072
    ),

    # Anthropic Claude Models
    "claude-opus-4-6": ModelPricing(
        model_id="claude-opus-4-6",
        provider="anthropic",
        input_cost_per_token=0.000005,    # $5.00 per 1M input tokens
        output_cost_per_token=0.000025,   # $25.00 per 1M output tokens
        context_length=200000
    ),
    "claude-opus-4-5": ModelPricing(
        model_id="claude-opus-4-5",
        provider="anthropic",
        input_cost_per_token=0.000005,    # $5.00 per 1M input tokens
        output_cost_per_token=0.000025,   # $25.00 per 1M output tokens
        context_length=200000
    ),
    "claude-sonnet-4-5": ModelPricing(
        model_id="claude-sonnet-4-5",
        provider="anthropic",
        input_cost_per_token=0.000003,    # $3.00 per 1M input tokens
        output_cost_per_token=0.000015,   # $15.00 per 1M output tokens
        context_length=200000
    ),
    "claude-haiku-4-5": ModelPricing(
        model_id="claude-haiku-4-5",
        provider="anthropic",
        input_cost_per_token=0.000001,    # $1.00 per 1M input tokens
        output_cost_per_token=0.000005,   # $5.00 per 1M output tokens
        context_length=200000
    ),

    # Google Gemini Models
    "gemini-3-pro-preview": ModelPricing(
        model_id="gemini-3-pro-preview",
        provider="google",
        input_cost_per_token=0.000002,    # $2.00 per 1M input tokens
        output_cost_per_token=0.000012,   # $12.00 per 1M output tokens
        context_length=1000000
    ),
    "gemini-3-flash-preview": ModelPricing(
        model_id="gemini-3-flash-preview",
        provider="google",
        input_cost_per_token=0.0000005,   # $0.50 per 1M input tokens
        output_cost_per_token=0.000003,   # $3.00 per 1M output tokens
        context_length=1000000
    ),
    "gemini-3-pro-image-preview": ModelPricing(
        model_id="gemini-3-pro-image-preview",
        provider="google",
        input_cost_per_token=0.000002,    # $2.00 per 1M input tokens
        output_cost_per_token=0.000004,   # $4.00 per 1M output tokens
        context_length=65000
    ),
    "gemini-2.5-pro": ModelPricing(
        model_id="gemini-2.5-pro",
        provider="google",
        input_cost_per_token=0.00000125,  # $1.25 per 1M input tokens
        output_cost_per_token=0.000005,   # $5.00 per 1M output tokens
        context_length=1000000
    ),
    "gemini-2.5-flash": ModelPricing(
        model_id="gemini-2.5-flash",
        provider="google",
        input_cost_per_token=0.0000003,   # $0.30 per 1M input tokens
        output_cost_per_token=0.0000012,  # $1.20 per 1M output tokens
        context_length=1000000
    ),
    "gemini-2.5-flash-lite": ModelPricing(
        model_id="gemini-2.5-flash-lite",
        provider="google",
        input_cost_per_token=0.000000018, # $0.018 per 1M input tokens
        output_cost_per_token=0.000000075, # $0.075 per 1M output tokens
        context_length=1000000
    ),

    # xAI Grok Models
    "grok-4.1-fast-reasoning": ModelPricing(
        model_id="grok-4.1-fast-reasoning",
        provider="grok",
        input_cost_per_token=0.000002,    # $2.00 per 1M input tokens
        output_cost_per_token=0.00001,    # $10.00 per 1M output tokens
        context_length=2000000
    ),
    "grok-4.1-fast-non-reasoning": ModelPricing(
        model_id="grok-4.1-fast-non-reasoning",
        provider="grok",
        input_cost_per_token=0.0000005,   # $0.50 per 1M input tokens
        output_cost_per_token=0.000002,   # $2.00 per 1M output tokens
        context_length=1000000
    ),
    "grok-4": ModelPricing(
        model_id="grok-4",
        provider="grok",
        input_cost_per_token=0.00001,     # $10.00 per 1M input tokens
        output_cost_per_token=0.00002,    # $20.00 per 1M output tokens
        context_length=131072
    ),
    "grok-3": ModelPricing(
        model_id="grok-3",
        provider="grok",
        input_cost_per_token=0.000005,    # $5.00 per 1M input tokens
        output_cost_per_token=0.000015,   # $15.00 per 1M output tokens
        context_length=131072
    ),
    "grok-3-mini": ModelPricing(
        model_id="grok-3-mini",
        provider="grok",
        input_cost_per_token=0.0000005,   # $0.50 per 1M input tokens
        output_cost_per_token=0.0000015,  # $1.50 per 1M output tokens
        context_length=131072
    ),
    "grok-code-fast-1": ModelPricing(
        model_id="grok-code-fast-1",
        provider="grok",
        input_cost_per_token=0.0000002,   # $0.20 per 1M input tokens
        output_cost_per_token=0.0000015,  # $1.50 per 1M output tokens
        context_length=256000
    ),

    # Groq Models (hardware-accelerated inference)
    "groq/compound": ModelPricing(
        model_id="groq/compound",
        provider="groq",
        input_cost_per_token=0.00000027,  # $0.27 per 1M input tokens
        output_cost_per_token=0.0000011,  # $1.10 per 1M output tokens
        context_length=131072
    ),
    "llama-3.3-70b-versatile": ModelPricing(
        model_id="llama-3.3-70b-versatile",
        provider="groq",
        input_cost_per_token=0.00000059,  # $0.59 per 1M input tokens
        output_cost_per_token=0.00000079, # $0.79 per 1M output tokens
        context_length=131072
    ),
    "llama-3.1-8b-instant": ModelPricing(
        model_id="llama-3.1-8b-instant",
        provider="groq",
        input_cost_per_token=0.00000005,  # $0.05 per 1M input tokens
        output_cost_per_token=0.00000008, # $0.08 per 1M output tokens
        context_length=131072
    ),
}


def get_model_pricing(model_id: str) -> Optional[ModelPricing]:
    """
    Get pricing information for a model.

    Args:
        model_id: Model identifier

    Returns:
        Optional[ModelPricing]: Pricing info if available
    """
    return MODEL_PRICING_DATA.get(model_id)


async def update_pricing_data(force_update: bool = False) -> bool:
    """
    Update pricing data from external sources.

    This function fetches updated pricing information and updates
    the in-memory pricing data. It's designed to be called nightly
    via a cron job.

    Args:
        force_update: Force update even if data is recent

    Returns:
        bool: True if update was successful
    """
    try:
        # Use global storage config for pricing data path
        pricing_file = _get_pricing_file_path()
        should_update = force_update

        if not should_update:
            try:
                stat = pricing_file.stat()
                last_update = datetime.fromtimestamp(stat.st_mtime)
                should_update = datetime.now() - last_update > timedelta(hours=12)
            except (OSError, FileNotFoundError):
                should_update = True

        if not should_update:
            logger.debug("Pricing data is recent, skipping update")
            return True

        logger.info("Updating pricing data from external sources")

        # In a real implementation, you would fetch from APIs like:
        # - OpenAI pricing API
        # - Anthropic pricing information
        # - Google Cloud Vertex AI pricing
        # For now, we'll use static data but demonstrate the structure

        updated_pricing = {}

        # Example: Fetch OpenAI pricing (pseudo-code)
        try:
            # This would be a real API call in production
            openai_pricing = await _fetch_openai_pricing()
            updated_pricing.update(openai_pricing)
        except Exception as e:
            logger.warning(f"Failed to fetch OpenAI pricing: {e}")

        # Example: Fetch Anthropic pricing
        try:
            anthropic_pricing = await _fetch_anthropic_pricing()
            updated_pricing.update(anthropic_pricing)
        except Exception as e:
            logger.warning(f"Failed to fetch Anthropic pricing: {e}")

        # Example: Fetch Google pricing
        try:
            google_pricing = await _fetch_google_pricing()
            updated_pricing.update(google_pricing)
        except Exception as e:
            logger.warning(f"Failed to fetch Google pricing: {e}")

        # Save updated pricing to file
        if updated_pricing:
            with open(pricing_file, 'w') as f:
                pricing_dict = {}
                for model_id, pricing in updated_pricing.items():
                    pricing_dict[model_id] = pricing.dict()
                json.dump(pricing_dict, f, indent=2, default=str)

            logger.info(f"Saved pricing data to {pricing_file}")

            # Update in-memory data
            MODEL_PRICING_DATA.update(updated_pricing)
            logger.info(f"Updated pricing for {len(updated_pricing)} models")

        return True

    except Exception as e:
        logger.error(f"Failed to update pricing data: {e}")
        return False


async def _fetch_openai_pricing() -> Dict[str, ModelPricing]:
    """
    Fetch OpenAI pricing information.

    In production, this would call OpenAI's pricing API or scrape
    their pricing page for the latest rates.
    """
    # This is a placeholder implementation
    # In reality, you'd fetch from OpenAI's API or pricing page

    # For now, return empty dict to keep existing pricing
    return {}


async def _fetch_anthropic_pricing() -> Dict[str, ModelPricing]:
    """
    Fetch Anthropic pricing information.

    In production, this would fetch from Anthropic's pricing information.
    """
    # Placeholder implementation
    return {}


async def _fetch_google_pricing() -> Dict[str, ModelPricing]:
    """
    Fetch Google Cloud Vertex AI pricing information.

    In production, this would fetch from Google Cloud's pricing API.
    """
    # Placeholder implementation
    return {}


def load_pricing_from_file() -> None:
    """
    Load pricing data from file if available.

    This is called on startup to load any updated pricing data
    that was fetched by the nightly cron job.
    """
    try:
        # Use global storage config for pricing data path
        pricing_file = _get_pricing_file_path()
        if not pricing_file.exists():
            logger.debug(f"No pricing data file found at {pricing_file}")
            return

        with open(pricing_file, 'r') as f:
            pricing_dict = json.load(f)

        for model_id, pricing_data in pricing_dict.items():
            if isinstance(pricing_data.get('last_updated'), str):
                pricing_data['last_updated'] = datetime.fromisoformat(pricing_data['last_updated'])

            MODEL_PRICING_DATA[model_id] = ModelPricing(**pricing_data)

        logger.info(f"Loaded pricing data for {len(pricing_dict)} models from file")

    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        logger.debug(f"Could not load pricing from file: {e}")
        # Use default pricing data
