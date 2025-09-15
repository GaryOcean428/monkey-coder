#!/usr/bin/env python3
"""
Railway Deployment Validation Script

Comprehensive validation script for Railway deployment readiness.
Validates all aspects identified in the Railway AetherOS project inspection.
"""

import os
import sys
import asyncio
import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

# Add package path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir / "packages" / "core"))

from monkey_coder.config.production_config import get_production_config
from monkey_coder.config.secrets_config import get_secrets_manager, validate_production_secrets
from monkey_coder.config.logging_config import setup_production_logging
from monkey_coder.database.connection import get_database_health


class RailwayDeploymentValidator:
    """
    Comprehensive Railway deployment validator.
    
    Validates all critical aspects for production deployment:
    - Database configuration and pooling
    - Secrets management and security
    - API provider configuration
    - Error handling and monitoring
    - Performance optimizations
    """
    
    def __init__(self):
        self.validation_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "unknown",
            "ready_for_deployment": False,
            "checks": {},
            "recommendations": [],
            "critical_issues": [],
            "warnings": []
        }
    
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run all validation checks."""
        print("🚀 Railway Deployment Validation - Starting Comprehensive Checks")
        print("=" * 70)
        
        # Initialize logging for validation
        logging_config = setup_production_logging(enable_sentry=False)
        self.validation_results["checks"]["logging"] = logging_config
        
        # 1. Database Configuration Validation
        await self._validate_database_configuration()
        
        # 2. Secrets Management Validation
        await self._validate_secrets_configuration()
        
        # 3. AI Provider Configuration Validation
        await self._validate_ai_provider_configuration()
        
        # 4. Production Configuration Validation
        await self._validate_production_configuration()
        
        # 5. Performance and Monitoring Validation
        await self._validate_performance_monitoring()
        
        # 6. Security Configuration Validation
        await self._validate_security_configuration()
        
        # 7. Railway-Specific Configuration Validation
        await self._validate_railway_configuration()
        
        # Calculate overall status
        self._calculate_overall_status()
        
        # Generate final report
        self._generate_deployment_report()
        
        return self.validation_results
    
    async def _validate_database_configuration(self):
        """Validate database configuration and connection pooling."""
        print("📊 Validating Database Configuration...")
        
        check_result = {
            "status": "healthy",
            "details": {},
            "issues": []
        }
        
        try:
            # Test database health
            db_health = await get_database_health()
            check_result["details"]["health"] = db_health
            
            # Check pool configuration
            pool_config = {
                "min_size": int(os.getenv("DB_POOL_MIN_SIZE", "5")),
                "max_size": int(os.getenv("DB_POOL_MAX_SIZE", "20")),
                "max_overflow": int(os.getenv("DB_POOL_MAX_OVERFLOW", "40")),
                "timeout": int(os.getenv("DB_POOL_TIMEOUT", "30"))
            }
            check_result["details"]["pool_config"] = pool_config
            
            # Validate pool sizes
            if pool_config["min_size"] < 5:
                check_result["issues"].append("DB_POOL_MIN_SIZE should be at least 5 for production")
            
            if pool_config["max_size"] < 20:
                check_result["issues"].append("DB_POOL_MAX_SIZE should be at least 20 for production")
            
            # Check DATABASE_URL
            database_url = os.getenv("DATABASE_URL")
            if database_url:
                check_result["details"]["database_configured"] = True
                if "localhost" in database_url and os.getenv("ENVIRONMENT") == "production":
                    check_result["issues"].append("DATABASE_URL contains localhost in production")
            else:
                check_result["details"]["database_configured"] = False
                check_result["issues"].append("DATABASE_URL not configured")
            
            if check_result["issues"]:
                check_result["status"] = "warning" if len(check_result["issues"]) <= 2 else "error"
            
            print(f"   ✅ Database Status: {check_result['status']}")
            if check_result["issues"]:
                for issue in check_result["issues"]:
                    print(f"   ⚠️  {issue}")
                    
        except Exception as e:
            check_result = {
                "status": "error",
                "error": str(e),
                "details": {}
            }
            print(f"   ❌ Database validation failed: {e}")
        
        self.validation_results["checks"]["database"] = check_result
    
    async def _validate_secrets_configuration(self):
        """Validate secrets management and API key configuration."""
        print("🔐 Validating Secrets Configuration...")
        
        try:
            secrets_health = validate_production_secrets()
            
            check_result = {
                "status": secrets_health["overall_status"],
                "configured_secrets": secrets_health["configured_secrets"],
                "missing_secrets": secrets_health["missing_secrets"],
                "validation_errors": secrets_health["validation_errors"],
                "categories": secrets_health["categories"],
                "issues": []
            }
            
            # Add specific recommendations as issues
            if secrets_health["missing_secrets"] > 15:
                check_result["issues"].append(f"Many secrets missing ({secrets_health['missing_secrets']})")
            
            if secrets_health["validation_errors"] > 0:
                check_result["issues"].append(f"Validation errors in {secrets_health['validation_errors']} secrets")
            
            # Check AI provider diversity
            ai_providers = secrets_health["categories"]["ai_providers"]
            configured_ai = len([s for s in ai_providers if s["configured"]])
            if configured_ai == 0:
                check_result["issues"].append("No AI provider API keys configured")
            elif configured_ai == 1:
                check_result["issues"].append("Only one AI provider configured - consider adding backups")
            
            print(f"   ✅ Secrets Status: {check_result['status']}")
            print(f"   📊 Configured: {check_result['configured_secrets']}, Missing: {check_result['missing_secrets']}")
            
            if check_result["issues"]:
                for issue in check_result["issues"]:
                    print(f"   ⚠️  {issue}")
                    
        except Exception as e:
            check_result = {
                "status": "error",
                "error": str(e),
                "configured_secrets": 0,
                "missing_secrets": 0
            }
            print(f"   ❌ Secrets validation failed: {e}")
        
        self.validation_results["checks"]["secrets"] = check_result
    
    async def _validate_ai_provider_configuration(self):
        """Validate AI provider configuration and availability."""
        print("🤖 Validating AI Provider Configuration...")
        
        check_result = {
            "status": "healthy",
            "providers": {},
            "issues": []
        }
        
        # Check each AI provider
        ai_keys = {
            "openai": os.getenv("OPENAI_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "google": os.getenv("GOOGLE_API_KEY"),
            "groq": os.getenv("GROQ_API_KEY"),
            "grok": os.getenv("GROK_API_KEY")
        }
        
        configured_count = 0
        for provider, key in ai_keys.items():
            is_configured = bool(key and key.strip() and "REPLACE_WITH" not in key)
            check_result["providers"][provider] = {
                "configured": is_configured,
                "key_length": len(key) if key else 0
            }
            
            if is_configured:
                configured_count += 1
        
        if configured_count == 0:
            check_result["status"] = "error"
            check_result["issues"].append("No AI provider API keys configured")
        elif configured_count == 1:
            check_result["status"] = "warning"
            check_result["issues"].append("Only one AI provider configured")
        
        print(f"   ✅ AI Providers Status: {check_result['status']}")
        print(f"   📊 Configured providers: {configured_count}/5")
        
        if check_result["issues"]:
            for issue in check_result["issues"]:
                print(f"   ⚠️  {issue}")
        
        self.validation_results["checks"]["ai_providers"] = check_result
    
    async def _validate_production_configuration(self):
        """Validate production configuration management."""
        print("⚙️  Validating Production Configuration...")
        
        try:
            prod_config = get_production_config()
            health_status = await prod_config.comprehensive_health_check()
            
            check_result = {
                "status": health_status["status"],
                "health_checks": health_status["checks"],
                "uptime": health_status.get("uptime_seconds", 0),
                "issues": []
            }
            
            # Check specific health components
            for component, status in health_status["checks"].items():
                if status.get("status") == "error":
                    check_result["issues"].append(f"{component} health check failed")
                elif status.get("status") == "warning":
                    check_result["issues"].append(f"{component} has warnings")
            
            print(f"   ✅ Production Config Status: {check_result['status']}")
            
            if check_result["issues"]:
                for issue in check_result["issues"]:
                    print(f"   ⚠️  {issue}")
                    
        except Exception as e:
            check_result = {
                "status": "error",
                "error": str(e),
                "issues": [f"Production config validation failed: {e}"]
            }
            print(f"   ❌ Production config validation failed: {e}")
        
        self.validation_results["checks"]["production"] = check_result
    
    async def _validate_performance_monitoring(self):
        """Validate performance monitoring and logging configuration."""
        print("📈 Validating Performance Monitoring...")
        
        check_result = {
            "status": "healthy",
            "features": {},
            "issues": []
        }
        
        # Check logging configuration
        log_level = os.getenv("LOG_LEVEL", "INFO")
        json_logs = os.getenv("JSON_LOGS", "false").lower() == "true"
        performance_logs = os.getenv("PERFORMANCE_LOGS", "false").lower() == "true"
        
        check_result["features"]["logging"] = {
            "log_level": log_level,
            "json_logs": json_logs,
            "performance_logs": performance_logs
        }
        
        # Check Sentry configuration
        sentry_dsn = os.getenv("SENTRY_DSN")
        check_result["features"]["sentry"] = {
            "configured": bool(sentry_dsn),
            "environment": os.getenv("ENVIRONMENT", "development")
        }
        
        if not sentry_dsn and os.getenv("ENVIRONMENT") == "production":
            check_result["issues"].append("Sentry DSN not configured for production error tracking")
            check_result["status"] = "warning"
        
        # Check rate limiting configuration
        rate_limit_config = {
            "per_minute": os.getenv("RATE_LIMIT_PER_MINUTE", "50"),
            "burst": os.getenv("RATE_LIMIT_BURST", "10"),
            "enabled": os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
        }
        check_result["features"]["rate_limiting"] = rate_limit_config
        
        print(f"   ✅ Performance Monitoring Status: {check_result['status']}")
        print(f"   📊 Sentry: {'✅' if check_result['features']['sentry']['configured'] else '❌'}")
        print(f"   📊 Rate Limiting: {'✅' if rate_limit_config['enabled'] else '❌'}")
        
        if check_result["issues"]:
            for issue in check_result["issues"]:
                print(f"   ⚠️  {issue}")
        
        self.validation_results["checks"]["monitoring"] = check_result
    
    async def _validate_security_configuration(self):
        """Validate security configuration and headers."""
        print("🔒 Validating Security Configuration...")
        
        check_result = {
            "status": "healthy",
            "security_features": {},
            "issues": []
        }
        
        # Check JWT configuration
        jwt_secret = os.getenv("JWT_SECRET_KEY")
        check_result["security_features"]["jwt"] = {
            "configured": bool(jwt_secret),
            "length": len(jwt_secret) if jwt_secret else 0
        }
        
        if not jwt_secret:
            check_result["issues"].append("JWT_SECRET_KEY not configured")
            check_result["status"] = "error"
        elif len(jwt_secret) < 32:
            check_result["issues"].append("JWT_SECRET_KEY too short (minimum 32 characters)")
            check_result["status"] = "warning"
        
        # Check CORS configuration
        cors_origins = os.getenv("CORS_ORIGINS", "")
        check_result["security_features"]["cors"] = {
            "configured": bool(cors_origins),
            "origins": cors_origins.split(",") if cors_origins else []
        }
        
        # Check session configuration
        session_config = {
            "max_sessions": os.getenv("MAX_CONCURRENT_SESSIONS", "5"),
            "timeout_minutes": os.getenv("SESSION_TIMEOUT_MINUTES", "30"),
            "jwt_expire_minutes": os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "400")
        }
        check_result["security_features"]["sessions"] = session_config
        
        print(f"   ✅ Security Status: {check_result['status']}")
        print(f"   📊 JWT: {'✅' if check_result['security_features']['jwt']['configured'] else '❌'}")
        print(f"   📊 CORS: {'✅' if check_result['security_features']['cors']['configured'] else '❌'}")
        
        if check_result["issues"]:
            for issue in check_result["issues"]:
                print(f"   ⚠️  {issue}")
        
        self.validation_results["checks"]["security"] = check_result
    
    async def _validate_railway_configuration(self):
        """Validate Railway-specific configuration."""
        print("🚂 Validating Railway Configuration...")
        
        check_result = {
            "status": "healthy",
            "railway_config": {},
            "issues": []
        }
        
        # Check Railway environment variables
        railway_vars = {
            "PORT": os.getenv("PORT"),
            "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT"),
            "RAILWAY_PUBLIC_DOMAIN": os.getenv("RAILWAY_PUBLIC_DOMAIN"),
            "RAILWAY_PRIVATE_DOMAIN": os.getenv("RAILWAY_PRIVATE_DOMAIN")
        }
        
        check_result["railway_config"]["environment_vars"] = railway_vars
        
        # Check if PORT is manually set (should be auto-provided by Railway)
        if railway_vars["PORT"] and os.getenv("ENVIRONMENT") == "production":
            check_result["issues"].append("PORT manually set - Railway should auto-provide this")
        
        # Check host binding configuration
        host = os.getenv("HOST", "0.0.0.0")
        if host not in ["0.0.0.0", "127.0.0.1", "localhost"]:
            check_result["issues"].append(f"Unusual HOST configuration: {host}")
        elif host != "0.0.0.0" and os.getenv("ENVIRONMENT") == "production":
            check_result["issues"].append("HOST should be 0.0.0.0 for Railway deployment")
        
        check_result["railway_config"]["host"] = host
        
        # Check railpack.json exists
        railpack_path = Path("railpack.json")
        check_result["railway_config"]["railpack_exists"] = railpack_path.exists()
        
        if railpack_path.exists():
            try:
                with open(railpack_path) as f:
                    railpack_config = json.load(f)
                check_result["railway_config"]["railpack_config"] = railpack_config
                
                # Validate railpack configuration
                if railpack_config.get("provider") != "python":
                    check_result["issues"].append("railpack.json provider should be 'python'")
                
                deploy_config = railpack_config.get("deploy", {})
                if deploy_config.get("startCommand") != "python run_server.py":
                    check_result["issues"].append("railpack.json startCommand should be 'python run_server.py'")
                
            except Exception as e:
                check_result["issues"].append(f"Failed to parse railpack.json: {e}")
        else:
            check_result["issues"].append("railpack.json not found")
        
        if check_result["issues"]:
            check_result["status"] = "warning"
        
        print(f"   ✅ Railway Config Status: {check_result['status']}")
        print(f"   📊 railpack.json: {'✅' if check_result['railway_config']['railpack_exists'] else '❌'}")
        print(f"   📊 HOST binding: {host}")
        
        if check_result["issues"]:
            for issue in check_result["issues"]:
                print(f"   ⚠️  {issue}")
        
        self.validation_results["checks"]["railway"] = check_result
    
    def _calculate_overall_status(self):
        """Calculate overall deployment readiness status."""
        error_count = 0
        warning_count = 0
        
        for check_name, check_result in self.validation_results["checks"].items():
            status = check_result.get("status", "unknown")
            
            if status == "error":
                error_count += 1
                if check_result.get("issues"):
                    self.validation_results["critical_issues"].extend(
                        [f"{check_name}: {issue}" for issue in check_result["issues"]]
                    )
            elif status == "warning":
                warning_count += 1
                if check_result.get("issues"):
                    self.validation_results["warnings"].extend(
                        [f"{check_name}: {issue}" for issue in check_result["issues"]]
                    )
        
        # Determine overall status
        if error_count > 0:
            self.validation_results["overall_status"] = "critical"
            self.validation_results["ready_for_deployment"] = False
        elif warning_count > 3:
            self.validation_results["overall_status"] = "warning"
            self.validation_results["ready_for_deployment"] = True  # Can deploy but with warnings
        else:
            self.validation_results["overall_status"] = "healthy"
            self.validation_results["ready_for_deployment"] = True
        
        # Generate recommendations
        self._generate_recommendations()
    
    def _generate_recommendations(self):
        """Generate deployment recommendations based on validation results."""
        recommendations = []
        
        # Database recommendations
        db_check = self.validation_results["checks"].get("database", {})
        if db_check.get("status") == "warning":
            recommendations.append("Optimize database connection pool settings for production workload")
        
        # Secrets recommendations
        secrets_check = self.validation_results["checks"].get("secrets", {})
        if secrets_check.get("missing_secrets", 0) > 10:
            recommendations.append("Configure additional AI provider API keys for redundancy")
        
        # Security recommendations
        security_check = self.validation_results["checks"].get("security", {})
        if not security_check.get("security_features", {}).get("jwt", {}).get("configured"):
            recommendations.append("Configure JWT_SECRET_KEY for secure authentication")
        
        # Monitoring recommendations
        monitoring_check = self.validation_results["checks"].get("monitoring", {})
        if not monitoring_check.get("features", {}).get("sentry", {}).get("configured"):
            recommendations.append("Configure Sentry DSN for production error tracking")
        
        # General production recommendations
        if self.validation_results["overall_status"] in ["healthy", "warning"]:
            recommendations.extend([
                "Set up monitoring alerts for health check failures",
                "Configure automated API key rotation schedule",
                "Review and test backup/recovery procedures",
                "Perform load testing before production traffic"
            ])
        
        self.validation_results["recommendations"] = recommendations
    
    def _generate_deployment_report(self):
        """Generate final deployment report."""
        print("\n" + "=" * 70)
        print("📋 RAILWAY DEPLOYMENT VALIDATION REPORT")
        print("=" * 70)
        
        status_emoji = {
            "healthy": "✅",
            "warning": "⚠️",
            "critical": "❌",
            "error": "❌"
        }
        
        overall_status = self.validation_results["overall_status"]
        print(f"\n🎯 Overall Status: {status_emoji.get(overall_status, '❓')} {overall_status.upper()}")
        print(f"🚀 Ready for Deployment: {'YES' if self.validation_results['ready_for_deployment'] else 'NO'}")
        
        # Summary of checks
        print(f"\n📊 Validation Summary:")
        for check_name, check_result in self.validation_results["checks"].items():
            status = check_result.get("status", "unknown")
            emoji = status_emoji.get(status, "❓")
            print(f"   {emoji} {check_name.replace('_', ' ').title()}: {status}")
        
        # Critical issues
        if self.validation_results["critical_issues"]:
            print(f"\n🚨 Critical Issues ({len(self.validation_results['critical_issues'])}):")
            for issue in self.validation_results["critical_issues"]:
                print(f"   ❌ {issue}")
        
        # Warnings
        if self.validation_results["warnings"]:
            print(f"\n⚠️  Warnings ({len(self.validation_results['warnings'])}):")
            for warning in self.validation_results["warnings"][:5]:  # Show top 5
                print(f"   ⚠️  {warning}")
            if len(self.validation_results["warnings"]) > 5:
                print(f"   ... and {len(self.validation_results['warnings']) - 5} more")
        
        # Recommendations
        if self.validation_results["recommendations"]:
            print(f"\n💡 Recommendations:")
            for rec in self.validation_results["recommendations"][:5]:  # Show top 5
                print(f"   💡 {rec}")
        
        print(f"\n📅 Validation completed at: {self.validation_results['timestamp']}")
        print("=" * 70)


async def main():
    """Run the Railway deployment validation."""
    validator = RailwayDeploymentValidator()
    results = await validator.run_comprehensive_validation()
    
    # Save results to file
    output_file = "railway_deployment_validation.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Full validation results saved to: {output_file}")
    
    # Return exit code based on validation results
    if results["ready_for_deployment"]:
        print("\n🎉 Deployment validation passed!")
        return 0
    else:
        print("\n🚫 Deployment validation failed - critical issues must be resolved!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)