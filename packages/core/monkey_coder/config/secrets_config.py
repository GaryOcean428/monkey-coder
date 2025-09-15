"""
Secrets Management Configuration

Enhanced secrets management for Railway production deployment with:
- Environment-based secret rotation strategy
- API key validation and health monitoring
- Secure storage recommendations
- Production security best practices
"""

import os
import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class SecretType(str, Enum):
    """Types of secrets managed by the system."""
    API_KEY = "api_key"
    JWT_SECRET = "jwt_secret"
    DATABASE_URL = "database_url"
    ENCRYPTION_KEY = "encryption_key"


@dataclass
class SecretInfo:
    """Information about a managed secret."""
    name: str
    secret_type: SecretType
    is_configured: bool
    last_rotation: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    key_prefix: Optional[str] = None
    validation_errors: List[str] = field(default_factory=list)


class SecretsManager:
    """
    Production secrets manager for Railway deployment.
    
    Provides secure management of API keys, database credentials,
    and other sensitive configuration with rotation strategies.
    """
    
    def __init__(self):
        self.secrets_cache: Dict[str, SecretInfo] = {}
        self._initialize_secrets_inventory()
    
    def _initialize_secrets_inventory(self):
        """Initialize inventory of all managed secrets."""
        # AI Provider API Keys
        ai_providers = [
            ("OPENAI_API_KEY", "OpenAI API Key"),
            ("ANTHROPIC_API_KEY", "Anthropic API Key"),
            ("GOOGLE_API_KEY", "Google API Key"),
            ("GROQ_API_KEY", "Groq API Key"),
            ("GROK_API_KEY", "Grok API Key"),
            ("PERPLEXITY_API_KEY", "Perplexity API Key"),
            ("XAI_API_KEY", "XAI API Key"),
            ("QWEN_API_KEY", "Qwen API Key"),
            ("MOONSHOT_API_KEY", "Moonshot API Key"),
            ("OPENROUTER_API_KEY", "OpenRouter API Key"),
            ("HUGGINGFACE_API_KEY", "HuggingFace API Key"),
            ("TAVILY_API_KEY", "Tavily API Key"),
            ("SERPER_API_KEY", "Serper API Key")
        ]
        
        for env_var, display_name in ai_providers:
            self._register_secret(env_var, display_name, SecretType.API_KEY)
        
        # Security secrets
        self._register_secret("JWT_SECRET_KEY", "JWT Secret Key", SecretType.JWT_SECRET)
        self._register_secret("CSRF_SECRET_KEY", "CSRF Secret Key", SecretType.ENCRYPTION_KEY)
        self._register_secret("COOKIE_SECRET_KEY", "Cookie Secret Key", SecretType.ENCRYPTION_KEY)
        self._register_secret("SESSION_SECRET_KEY", "Session Secret Key", SecretType.ENCRYPTION_KEY)
        
        # Database and infrastructure
        self._register_secret("DATABASE_URL", "Database URL", SecretType.DATABASE_URL)
        self._register_secret("REDIS_URL", "Redis URL", SecretType.DATABASE_URL)
        
        # External services
        self._register_secret("SENTRY_DSN", "Sentry DSN", SecretType.API_KEY)
        self._register_secret("STRIPE_API_KEY", "Stripe API Key", SecretType.API_KEY)
        self._register_secret("GITHUB_TOKEN", "GitHub Token", SecretType.API_KEY)
    
    def _register_secret(self, env_var: str, display_name: str, secret_type: SecretType):
        """Register a secret for management."""
        value = os.getenv(env_var)
        is_configured = bool(value and value.strip())
        
        secret_info = SecretInfo(
            name=display_name,
            secret_type=secret_type,
            is_configured=is_configured,
            key_prefix=value[:10] + "..." if value and len(value) > 10 else None
        )
        
        # Validate the secret if configured
        if is_configured:
            secret_info.validation_errors = self._validate_secret(env_var, value, secret_type)
        
        self.secrets_cache[env_var] = secret_info
    
    def _validate_secret(self, env_var: str, value: str, secret_type: SecretType) -> List[str]:
        """Validate a secret value for security and format requirements."""
        errors = []
        
        if secret_type == SecretType.API_KEY:
            # API key validation
            if len(value) < 16:
                errors.append(f"{env_var}: API key too short (minimum 16 characters)")
            
            if value.lower() in ["test", "demo", "example", "placeholder"]:
                errors.append(f"{env_var}: Appears to be a placeholder value")
            
            if "REPLACE_WITH" in value:
                errors.append(f"{env_var}: Contains placeholder text - needs real API key")
                
        elif secret_type == SecretType.JWT_SECRET:
            # JWT secret validation
            if len(value) < 32:
                errors.append(f"{env_var}: JWT secret too short (minimum 32 characters)")
            
            if value.encode() == value.encode('ascii'):
                # Check for weak patterns
                if value.lower() in ["secretkey", "mysecret", "jwtsecret"]:
                    errors.append(f"{env_var}: Weak or default JWT secret")
        
        elif secret_type == SecretType.DATABASE_URL:
            # Database URL validation
            if not value.startswith(("postgresql://", "postgres://", "redis://")):
                errors.append(f"{env_var}: Invalid database URL format")
            
            if "localhost" in value and os.getenv("ENVIRONMENT") == "production":
                errors.append(f"{env_var}: Using localhost in production environment")
        
        return errors
    
    def get_secrets_health_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive secrets health report for monitoring.
        
        Returns detailed status of all secrets without exposing values.
        """
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "configured_secrets": 0,
            "missing_secrets": 0,
            "validation_errors": 0,
            "rotation_needed": 0,
            "categories": {},
            "recommendations": []
        }
        
        # Group secrets by category
        categories = {
            "ai_providers": [],
            "security": [],
            "infrastructure": [],
            "external_services": []
        }
        
        for env_var, secret_info in self.secrets_cache.items():
            # Categorize secrets
            if any(provider in env_var.lower() for provider in 
                   ["openai", "anthropic", "google", "groq", "grok", "perplexity", 
                    "xai", "qwen", "moonshot", "openrouter", "huggingface", "tavily", "serper"]):
                category = "ai_providers"
            elif any(sec in env_var.lower() for sec in ["jwt", "csrf", "cookie", "session"]):
                category = "security"
            elif any(infra in env_var.lower() for infra in ["database", "redis", "sentry"]):
                category = "infrastructure"
            else:
                category = "external_services"
            
            # Count statistics
            if secret_info.is_configured:
                report["configured_secrets"] += 1
            else:
                report["missing_secrets"] += 1
            
            if secret_info.validation_errors:
                report["validation_errors"] += len(secret_info.validation_errors)
            
            # Add to category
            categories[category].append({
                "name": secret_info.name,
                "env_var": env_var,
                "configured": secret_info.is_configured,
                "key_prefix": secret_info.key_prefix,
                "validation_errors": secret_info.validation_errors,
                "secret_type": secret_info.secret_type.value
            })
        
        report["categories"] = categories
        
        # Generate recommendations
        if report["missing_secrets"] > 0:
            report["recommendations"].append(
                f"Configure {report['missing_secrets']} missing secrets for full functionality"
            )
        
        if report["validation_errors"] > 0:
            report["overall_status"] = "warning"
            report["recommendations"].append(
                f"Fix {report['validation_errors']} validation errors in configured secrets"
            )
        
        # Check AI provider diversity
        ai_configured = len([s for s in categories["ai_providers"] if s["configured"]])
        if ai_configured == 0:
            report["overall_status"] = "critical"
            report["recommendations"].append("No AI provider API keys configured - service will not function")
        elif ai_configured == 1:
            report["recommendations"].append("Consider configuring backup AI providers for redundancy")
        
        # Security checks
        security_configured = len([s for s in categories["security"] if s["configured"]])
        if security_configured < 2 and os.getenv("ENVIRONMENT") == "production":
            report["overall_status"] = "warning"
            report["recommendations"].append("Configure all security secrets for production deployment")
        
        return report
    
    def get_rotation_strategy(self) -> Dict[str, Any]:
        """
        Get recommended API key rotation strategy.
        
        Returns rotation schedule and procedures for production security.
        """
        return {
            "rotation_schedule": {
                "ai_provider_keys": "Every 90 days",
                "jwt_secrets": "Every 180 days", 
                "database_credentials": "Every 365 days",
                "external_service_keys": "Every 120 days"
            },
            "rotation_procedures": {
                "preparation": [
                    "Generate new secret in provider dashboard",
                    "Test new secret in staging environment",
                    "Update Railway environment variables",
                    "Restart service to pick up new secrets"
                ],
                "validation": [
                    "Verify all endpoints work with new secrets",
                    "Check error logs for authentication failures",
                    "Monitor API usage quotas and rate limits",
                    "Confirm backup systems still functional"
                ],
                "cleanup": [
                    "Revoke old secrets in provider dashboards",
                    "Update documentation with rotation date",
                    "Schedule next rotation reminder",
                    "Archive old credentials securely"
                ]
            },
            "emergency_rotation": {
                "triggers": [
                    "Suspected key compromise or exposure",
                    "Unusual API usage patterns detected",
                    "Security breach in provider systems",
                    "Employee access revocation needed"
                ],
                "immediate_actions": [
                    "Revoke compromised secrets immediately",
                    "Generate and deploy new secrets",
                    "Review access logs for suspicious activity",
                    "Update monitoring and alerting rules"
                ]
            }
        }
    
    def generate_secure_secret(self, length: int = 32) -> str:
        """Generate a cryptographically secure secret."""
        return secrets.token_urlsafe(length)
    
    def get_secret_strength_score(self, value: str) -> Dict[str, Any]:
        """
        Calculate strength score for a secret value.
        
        Returns score (0-100) and recommendations for improvement.
        """
        score = 0
        recommendations = []
        
        # Length scoring
        if len(value) >= 32:
            score += 25
        elif len(value) >= 16:
            score += 15
        else:
            recommendations.append("Increase length to at least 32 characters")
        
        # Character diversity
        has_upper = any(c.isupper() for c in value)
        has_lower = any(c.islower() for c in value)
        has_digit = any(c.isdigit() for c in value)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in value)
        
        diversity_score = sum([has_upper, has_lower, has_digit, has_special]) * 15
        score += diversity_score
        
        if diversity_score < 45:
            recommendations.append("Include uppercase, lowercase, numbers, and special characters")
        
        # Entropy estimation
        entropy = len(set(value)) / len(value) * 25
        score += entropy
        
        if entropy < 15:
            recommendations.append("Avoid repeated characters and patterns")
        
        # Pattern detection
        common_patterns = ["123", "abc", "password", "secret", "key"]
        if any(pattern in value.lower() for pattern in common_patterns):
            score -= 20
            recommendations.append("Avoid common patterns and dictionary words")
        
        return {
            "score": max(0, min(100, int(score))),
            "strength": "strong" if score >= 80 else "medium" if score >= 60 else "weak",
            "recommendations": recommendations
        }


# Global secrets manager instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """Get global secrets manager instance."""
    global _secrets_manager
    
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    
    return _secrets_manager


def validate_production_secrets() -> Dict[str, Any]:
    """
    Validate all secrets for production readiness.
    
    Returns comprehensive validation report.
    """
    manager = get_secrets_manager()
    return manager.get_secrets_health_report()


def get_api_key_rotation_schedule() -> Dict[str, Any]:
    """Get API key rotation strategy for production security."""
    manager = get_secrets_manager()
    return manager.get_rotation_strategy()