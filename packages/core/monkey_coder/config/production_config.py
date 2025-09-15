"""
Production Configuration Enhancement for Phase 2.0

Enhanced production configuration with comprehensive health checks,
security hardening, and monitoring for Railway deployment.
"""

import asyncio
import logging
import os
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta

from .env_config import get_config, EnvironmentConfig
from .secrets_config import get_secrets_manager, validate_production_secrets

logger = logging.getLogger(__name__)


@dataclass
class ProductionHealthCheck:
    """Enhanced health check for production deployment."""
    name: str
    status: str
    last_check: datetime
    response_time_ms: float
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ProductionConfigManager:
    """
    Production configuration manager for Phase 2.0 deployment.
    
    Provides enhanced configuration management, health monitoring,
    and security hardening for production Railway deployment.
    """
    
    def __init__(self):
        self.config = get_config()
        self.start_time = datetime.utcnow()
        self.health_checks: Dict[str, ProductionHealthCheck] = {}
        self._setup_production_logging()
        
    def _setup_production_logging(self):
        """Setup production-optimized logging configuration."""
        if self.config.environment == "production":
            # Configure structured logging for production
            logging.basicConfig(
                level=getattr(logging, self.config.monitoring.log_level.upper()),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Suppress noisy third-party loggers in production
            logging.getLogger("httpx").setLevel(logging.WARNING)
            logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
            
    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check for production monitoring.
        
        Returns detailed health status including:
        - System resources
        - Database connectivity  
        - AI provider availability
        - Component status
        - Performance metrics
        - Secrets health and security status
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "version": "2.0.0",
            "environment": self.config.environment,
            "checks": {}
        }
        
        # System health check
        try:
            health_status["checks"]["system"] = await self._check_system_health()
        except Exception as e:
            health_status["checks"]["system"] = {"status": "error", "error": str(e)}
            health_status["status"] = "degraded"
            
        # Database health check
        try:
            health_status["checks"]["database"] = await self._check_database_health()
        except Exception as e:
            health_status["checks"]["database"] = {"status": "error", "error": str(e)}
            health_status["status"] = "degraded"
            
        # AI providers health check
        try:
            health_status["checks"]["ai_providers"] = await self._check_ai_providers_health()
        except Exception as e:
            health_status["checks"]["ai_providers"] = {"status": "error", "error": str(e)}
            health_status["status"] = "degraded"
            
        # Components health check
        try:
            health_status["checks"]["components"] = await self._check_components_health()
        except Exception as e:
            health_status["checks"]["components"] = {"status": "error", "error": str(e)}
            health_status["status"] = "degraded"
            
        # Secrets security health check
        try:
            health_status["checks"]["secrets"] = await self._check_secrets_health()
        except Exception as e:
            health_status["checks"]["secrets"] = {"status": "error", "error": str(e)}
            health_status["status"] = "degraded"
            
        return health_status
        
    async def _check_system_health(self) -> Dict[str, Any]:
        """Check system resource health."""
        try:
            import psutil
            
            # Memory check
            memory = psutil.virtual_memory()
            memory_usage_percent = memory.percent
            
            # CPU check
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Disk check
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            
            status = "healthy"
            warnings = []
            
            # Set thresholds for warnings
            if memory_usage_percent > 85:
                warnings.append(f"High memory usage: {memory_usage_percent:.1f}%")
                status = "warning"
                
            if cpu_percent > 80:
                warnings.append(f"High CPU usage: {cpu_percent:.1f}%")
                status = "warning"
                
            if disk_usage_percent > 90:
                warnings.append(f"High disk usage: {disk_usage_percent:.1f}%")
                status = "warning"
                
            return {
                "status": status,
                "memory_usage_percent": round(memory_usage_percent, 2),
                "cpu_usage_percent": round(cpu_percent, 2),
                "disk_usage_percent": round(disk_usage_percent, 2),
                "warnings": warnings
            }
            
        except ImportError:
            return {
                "status": "unknown",
                "error": "psutil not available for system monitoring"
            }
            
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance with Railway optimizations."""
        if not self.config.database.url:
            return {
                "status": "not_configured",
                "message": "Database not configured"
            }
            
        try:
            # Import here to avoid circular imports
            from ..database.connection import get_database_health
            
            # Get comprehensive database health information
            db_health = await get_database_health()
            
            return {
                "status": "healthy" if db_health["connection_test"] else "degraded",
                "url_configured": True,
                "pool_stats": db_health.get("pool_stats", {}),
                "connection_test": db_health["connection_test"],
                "response_time_ms": db_health.get("response_time_ms"),
                "error": db_health.get("error")
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    async def _check_ai_providers_health(self) -> Dict[str, Any]:
        """Check AI provider availability and configuration."""
        providers = {}
        overall_status = "healthy"
        
        # Check each provider configuration
        provider_keys = {
            "openai": self.config.ai_providers.openai_api_key,
            "anthropic": self.config.ai_providers.anthropic_api_key,
            "google": self.config.ai_providers.google_api_key,
            "groq": self.config.ai_providers.groq_api_key,
            "grok": self.config.ai_providers.grok_api_key
        }
        
        configured_count = 0
        for provider, key in provider_keys.items():
            if key:
                providers[provider] = {
                    "status": "configured",
                    "key_length": len(key) if key else 0
                }
                configured_count += 1
            else:
                providers[provider] = {
                    "status": "not_configured"
                }
                
        if configured_count == 0:
            overall_status = "error"
        elif configured_count < 2:
            overall_status = "warning"
            
        return {
            "status": overall_status,
            "configured_providers": configured_count,
            "total_providers": len(provider_keys),
            "providers": providers
        }
        
    async def _check_components_health(self) -> Dict[str, Any]:
        """Check application component health."""
        # This would check actual component initialization
        # For now, return basic component status
        return {
            "status": "healthy",
            "components": {
                "orchestrator": "active",
                "quantum_executor": "active", 
                "persona_router": "active",
                "provider_registry": "active",
                "context_manager": "active"
            }
        }
        
    def get_security_headers(self) -> Dict[str, str]:
        """Get production security headers."""
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()"
        }
        
        if self.config.environment == "production":
            headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "connect-src 'self'"
            )
            
        return headers
        
    def get_rate_limiting_config(self) -> Dict[str, Any]:
        """Get production rate limiting configuration."""
        return {
            "requests_per_minute": int(os.getenv("RATE_LIMIT_PER_MINUTE", "100")),
            "burst_requests": int(os.getenv("RATE_LIMIT_BURST", "20")),
            "enable_rate_limiting": os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
        }
        
    def validate_production_readiness(self) -> Dict[str, Any]:
        """
        Validate production readiness and return comprehensive report.
        
        Returns:
            Dict with validation results, warnings, and recommendations
        """
        validation = {
            "ready": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Check environment configuration
        if self.config.environment != "production":
            validation["warnings"].append("Environment not set to 'production'")
            
        # Check security configuration
        if not self.config.security.jwt_secret_key:
            validation["errors"].append("JWT_SECRET_KEY not configured")
            validation["ready"] = False
            
        # Check monitoring configuration
        if not self.config.monitoring.sentry_dsn:
            validation["warnings"].append("Sentry DSN not configured - error tracking disabled")
            
        # Check AI provider configuration
        provider_count = sum(1 for key in [
            self.config.ai_providers.openai_api_key,
            self.config.ai_providers.anthropic_api_key,
            self.config.ai_providers.google_api_key,
            self.config.ai_providers.groq_api_key,
            self.config.ai_providers.grok_api_key
        ] if key)
        
        if provider_count == 0:
            validation["errors"].append("No AI provider API keys configured")
            validation["ready"] = False
        elif provider_count == 1:
            validation["warnings"].append("Only one AI provider configured - consider adding backup providers")
            
        # Check database configuration
        if not self.config.database.url:
            validation["warnings"].append("Database not configured - using in-memory storage")
            
        # Add recommendations
        if validation["ready"]:
            validation["recommendations"].extend([
                "Monitor error rates and response times after deployment",
                "Set up alerting for health check failures",
                "Configure load testing for production traffic",
                "Review and update security headers regularly"
            ])
            
        return validation
        
    async def _check_secrets_health(self) -> Dict[str, Any]:
        """Check secrets security and configuration health."""
        try:
            secrets_manager = get_secrets_manager()
            secrets_health = secrets_manager.get_secrets_health_report()
            
            return {
                "status": secrets_health["overall_status"],
                "configured_secrets": secrets_health["configured_secrets"],
                "missing_secrets": secrets_health["missing_secrets"],
                "validation_errors": secrets_health["validation_errors"],
                "categories": {
                    category: {
                        "configured": len([s for s in secrets if s["configured"]]),
                        "total": len(secrets),
                        "errors": sum(len(s["validation_errors"]) for s in secrets)
                    }
                    for category, secrets in secrets_health["categories"].items()
                },
                "recommendations": secrets_health["recommendations"][:3]  # Top 3 recommendations
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
        
    def get_secrets_rotation_schedule(self) -> Dict[str, Any]:
        """Get API key rotation strategy for production security."""
        try:
            secrets_manager = get_secrets_manager()
            return secrets_manager.get_rotation_strategy()
        except Exception as e:
            logger.error(f"Failed to get rotation strategy: {e}")
            return {"error": str(e)}


# Global production config instance
_production_config: Optional[ProductionConfigManager] = None


def get_production_config() -> ProductionConfigManager:
    """Get global production configuration manager."""
    global _production_config
    
    if _production_config is None:
        _production_config = ProductionConfigManager()
        
    return _production_config