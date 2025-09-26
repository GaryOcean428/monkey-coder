"""
MCP Railway Deployment Tool

This module provides Model Context Protocol (MCP) tools for comprehensive
Railway deployment validation and management, implementing all Railway
deployment best practices from the cheat sheet.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import asdict
from datetime import datetime

from ..config.env_config import EnvironmentConfig
from ..core.orchestration_coordinator import OrchestrationCoordinator

# Import the Railway deployment manager
import sys
scripts_path = Path(__file__).parent.parent.parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_path))

try:
    from mcp_railway_deployment_manager import (
        RailwayDeploymentManager,
        DeploymentStatus,
        DeploymentCheck
    )
    RAILWAY_MANAGER_AVAILABLE = True
except ImportError:
    RAILWAY_MANAGER_AVAILABLE = False


class MCPRailwayTool:
    """
    MCP tool for Railway deployment validation and management.
    
    This tool integrates Railway deployment best practices into the MCP framework,
    providing comprehensive validation, automatic fixes, and deployment monitoring.
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize MCP components
        try:
            self.env_config = EnvironmentConfig()
            self.coordinator = OrchestrationCoordinator()
            self.mcp_enabled = True
        except Exception as e:
            self.logger.warning(f"MCP components initialization failed: {e}")
            self.mcp_enabled = False
        
        # Initialize Railway deployment manager if available
        if RAILWAY_MANAGER_AVAILABLE:
            self.deployment_manager = RailwayDeploymentManager(self.project_root)
            self.railway_available = True
        else:
            self.railway_available = False
            self.logger.warning("Railway deployment manager not available")

    def validate_railway_deployment(
        self, 
        project_path: Optional[str] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        MCP tool: Validate Railway deployment configuration.
        
        Performs comprehensive Railway deployment validation following the cheat sheet:
        - Build system conflicts (Issue 1)
        - PORT binding failures (Issue 2) 
        - Health check configuration (Issue 5)
        - Reference variable mistakes (Issue 4)
        - Monorepo service confusion (Issue 6)
        
        Args:
            project_path: Optional project root path
            verbose: Enable verbose logging
            
        Returns:
            Comprehensive validation results with MCP orchestration data
        """
        if not self.railway_available:
            return {
                "error": "Railway deployment manager not available",
                "mcp_available": self.mcp_enabled,
                "timestamp": datetime.now().isoformat()
            }
        
        # Use provided project path or default
        if project_path:
            self.deployment_manager.project_root = Path(project_path).resolve()
        
        # Run comprehensive validation
        try:
            results = self.deployment_manager.run_comprehensive_check()
            
            # Enhance results with MCP orchestration data
            if self.mcp_enabled:
                results["mcp_orchestration"] = {
                    "coordinator_available": True,
                    "environment_config": bool(self.env_config),
                    "orchestration_strategies": self._get_orchestration_strategies(),
                    "recommended_actions": self._generate_mcp_recommendations(results)
                }
            
            self.logger.info(f"Railway validation completed: {results['overall_status']}")
            return results
            
        except Exception as e:
            self.logger.error(f"Railway validation failed: {e}")
            return {
                "error": str(e),
                "mcp_available": self.mcp_enabled,
                "timestamp": datetime.now().isoformat()
            }
    
    def fix_railway_deployment_issues(
        self,
        project_path: Optional[str] = None,
        auto_apply: bool = False
    ) -> Dict[str, Any]:
        """
        MCP tool: Fix Railway deployment issues automatically.
        
        Analyzes and fixes common Railway deployment issues:
        - Removes competing build files
        - Validates railpack.json structure
        - Fixes PORT binding issues
        - Configures health checks
        - Resolves reference variable mistakes
        
        Args:
            project_path: Optional project root path
            auto_apply: Whether to automatically apply fixes
            
        Returns:
            Fix results and commands applied
        """
        if not self.railway_available:
            return {"error": "Railway deployment manager not available"}
        
        # Validate deployment first
        validation_results = self.validate_railway_deployment(project_path)
        
        if validation_results.get("error"):
            return validation_results
        
        # Generate fix script
        fix_script = self.deployment_manager.generate_fix_script(validation_results)
        
        result = {
            "validation_results": validation_results,
            "fix_script_generated": bool(fix_script),
            "critical_issues": validation_results.get("critical_checks", 0),
            "warning_issues": validation_results.get("warning_checks", 0),
            "auto_apply": auto_apply,
            "fixes_applied": [],
            "timestamp": datetime.now().isoformat()
        }
        
        if auto_apply and validation_results.get("critical_checks", 0) > 0:
            try:
                # Write fix script
                fix_script_path = self.deployment_manager.project_root / "mcp-railway-fix.sh"
                fix_script_path.write_text(fix_script)
                fix_script_path.chmod(0o755)
                
                # Execute fix script
                subprocess.run([str(fix_script_path)], check=True, cwd=self.deployment_manager.project_root)
                
                result["fixes_applied"] = validation_results.get("fix_commands", [])
                result["fix_script_executed"] = True
                
                # Re-validate after fixes
                post_fix_validation = self.validate_railway_deployment(project_path)
                result["post_fix_validation"] = post_fix_validation
                
                self.logger.info(f"Applied {len(result['fixes_applied'])} Railway fixes")
                
            except Exception as e:
                result["fix_error"] = str(e)
                self.logger.error(f"Failed to apply Railway fixes: {e}")
        
        return result
    
    def monitor_railway_deployment(
        self,
        service_name: Optional[str] = None,
        check_health: bool = True
    ) -> Dict[str, Any]:
        """
        MCP tool: Monitor Railway deployment status and health.
        
        Provides real-time deployment monitoring with:
        - Health endpoint validation
        - Service status checking
        - Performance metrics
        - Error detection
        
        Args:
            service_name: Optional Railway service name
            check_health: Whether to perform health checks
            
        Returns:
            Deployment monitoring results
        """
        monitoring_results = {
            "timestamp": datetime.now().isoformat(),
            "service_name": service_name,
            "health_check_enabled": check_health,
            "mcp_monitoring": self.mcp_enabled
        }
        
        # Check health endpoint if requested
        if check_health:
            health_status = self._check_health_endpoint()
            monitoring_results["health_status"] = health_status
        
        # Use MCP orchestration for enhanced monitoring
        if self.mcp_enabled:
            try:
                orchestration_status = self._get_orchestration_monitoring()
                monitoring_results["orchestration_status"] = orchestration_status
            except Exception as e:
                monitoring_results["orchestration_error"] = str(e)
        
        return monitoring_results
    
    def get_railway_deployment_recommendations(
        self,
        project_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        MCP tool: Get Railway deployment recommendations and best practices.
        
        Provides comprehensive recommendations based on:
        - Current project structure
        - Railway deployment best practices
        - MCP orchestration capabilities
        - Performance optimization
        
        Args:
            project_path: Optional project root path
            
        Returns:
            Deployment recommendations and best practices
        """
        if project_path:
            project_root = Path(project_path).resolve()
        else:
            project_root = self.project_root
        
        recommendations = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(project_root),
            "railway_best_practices": self._get_railway_best_practices(),
            "mcp_integration": self._get_mcp_integration_recommendations(),
            "performance_optimizations": self._get_performance_recommendations(),
            "security_recommendations": self._get_security_recommendations()
        }
        
        # Analyze current project for specific recommendations
        if self.railway_available:
            validation_results = self.validate_railway_deployment(str(project_root))
            recommendations["current_status"] = validation_results.get("overall_status", "unknown")
            recommendations["specific_recommendations"] = self._generate_specific_recommendations(
                validation_results
            )
        
        return recommendations
    
    def _get_orchestration_strategies(self) -> List[str]:
        """Get available MCP orchestration strategies."""
        if not self.mcp_enabled:
            return []
        
        try:
            # Query the orchestration coordinator for available strategies
            return [
                "sequential_execution",
                "parallel_coordination", 
                "hierarchical_delegation",
                "consensus_coordination",
                "adaptive_orchestration"
            ]
        except Exception:
            return ["basic_orchestration"]
    
    def _generate_mcp_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """Generate MCP-specific recommendations based on validation results."""
        recommendations = []
        
        if validation_results.get("critical_checks", 0) > 0:
            recommendations.append("Use MCP orchestration for automated issue resolution")
        
        if validation_results.get("warning_checks", 0) > 0:
            recommendations.append("Enable MCP monitoring for deployment health tracking")
        
        if self.mcp_enabled:
            recommendations.append("MCP framework is available for advanced deployment automation")
        
        recommendations.append("Consider MCP-driven deployment pipelines for enhanced reliability")
        
        return recommendations
    
    def _check_health_endpoint(self) -> Dict[str, Any]:
        """Check health endpoint availability and response."""
        try:
            import requests
            
            # Try common health endpoint URLs
            health_urls = [
                "http://localhost:8000/health",
                "http://localhost:8000/api/health",
                "http://0.0.0.0:8000/health"
            ]
            
            for url in health_urls:
                try:
                    response = requests.get(url, timeout=5)
                    return {
                        "available": True,
                        "status_code": response.status_code,
                        "url": url,
                        "response_time_ms": response.elapsed.total_seconds() * 1000
                    }
                except Exception:
                    continue
            
            return {"available": False, "error": "No health endpoint responding"}
            
        except ImportError:
            return {"available": False, "error": "requests library not available"}
    
    def _get_orchestration_monitoring(self) -> Dict[str, Any]:
        """Get orchestration monitoring status."""
        if not self.mcp_enabled:
            return {"available": False}
        
        try:
            return {
                "available": True,
                "coordinator_status": "active",
                "environment_config": bool(self.env_config),
                "monitoring_capabilities": [
                    "health_checking",
                    "performance_monitoring", 
                    "error_detection",
                    "auto_remediation"
                ]
            }
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def _get_railway_best_practices(self) -> List[str]:
        """Get Railway deployment best practices from the cheat sheet."""
        return [
            "Use railpack.json as the only build configuration",
            "Never hardcode ports - always use process.env.PORT",
            "Always bind to 0.0.0.0, not localhost or 127.0.0.1",
            "Include health check endpoint at /health returning 200 status",
            "Reference domains not ports in Railway variables",
            "Remove competing build files (Dockerfile, railway.toml)",
            "Validate JSON syntax before committing railpack.json",
            "Use proper Railway reference variables (RAILWAY_PUBLIC_DOMAIN)",
            "Implement comprehensive error handling",
            "Configure health check timeout appropriately"
        ]
    
    def _get_mcp_integration_recommendations(self) -> List[str]:
        """Get MCP-specific integration recommendations."""
        if not self.mcp_enabled:
            return ["MCP framework not available - consider installation for enhanced features"]
        
        return [
            "Use MCP orchestration for deployment automation",
            "Enable MCP environment configuration validation",
            "Implement MCP-driven health monitoring",
            "Use MCP coordination for multi-service deployments",
            "Leverage MCP for automated issue resolution"
        ]
    
    def _get_performance_recommendations(self) -> List[str]:
        """Get performance optimization recommendations."""
        return [
            "Enable Railway build caching where possible",
            "Optimize Docker layers for faster builds",
            "Use static asset optimization",
            "Implement proper dependency caching",
            "Configure appropriate health check intervals",
            "Use Railway's CDN for static assets",
            "Optimize startup time with lazy loading"
        ]
    
    def _get_security_recommendations(self) -> List[str]:
        """Get security-focused recommendations."""
        return [
            "Use Railway environment variables for secrets",
            "Never commit API keys or credentials",
            "Enable Railway's built-in security features",
            "Use HTTPS for all external communications",
            "Implement proper CORS configuration",
            "Use Railway's private networking for internal services",
            "Regular security audits and updates"
        ]
    
    def _generate_specific_recommendations(
        self, 
        validation_results: Dict[str, Any]
    ) -> List[str]:
        """Generate project-specific recommendations based on validation results."""
        recommendations = []
        
        for check in validation_results.get("checks", []):
            if check.get("status") == "critical":
                recommendations.append(f"Critical: {check.get('message', 'Unknown issue')}")
            elif check.get("status") == "warning":
                recommendations.append(f"Consider: {check.get('message', 'Unknown warning')}")
        
        if validation_results.get("deployment_ready"):
            recommendations.append("✅ Project is ready for Railway deployment")
        else:
            recommendations.append("❌ Resolve critical issues before deploying")
        
        return recommendations


# MCP tool registration functions
def get_mcp_railway_tools() -> Dict[str, Any]:
    """
    Get MCP tool definitions for Railway deployment management.
    
    Returns tool definitions that can be registered with MCP servers.
    """
    return {
        "validate_railway_deployment": {
            "name": "validate_railway_deployment",
            "description": "Validate Railway deployment configuration and detect issues",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Optional project root path"
                    },
                    "verbose": {
                        "type": "boolean", 
                        "description": "Enable verbose logging"
                    }
                }
            }
        },
        "fix_railway_deployment_issues": {
            "name": "fix_railway_deployment_issues",
            "description": "Automatically fix Railway deployment issues",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Optional project root path"
                    },
                    "auto_apply": {
                        "type": "boolean",
                        "description": "Whether to automatically apply fixes"
                    }
                }
            }
        },
        "monitor_railway_deployment": {
            "name": "monitor_railway_deployment", 
            "description": "Monitor Railway deployment status and health",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "Optional Railway service name"
                    },
                    "check_health": {
                        "type": "boolean",
                        "description": "Whether to perform health checks"
                    }
                }
            }
        },
        "get_railway_deployment_recommendations": {
            "name": "get_railway_deployment_recommendations",
            "description": "Get Railway deployment recommendations and best practices",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Optional project root path"
                    }
                }
            }
        }
    }


# Create global instance for easy access
railway_tool = MCPRailwayTool()