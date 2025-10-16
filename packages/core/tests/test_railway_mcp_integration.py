"""
Test Railway MCP (Model Context Protocol) Integration

This test suite validates the Railway deployment MCP tools including:
- Railway deployment validation
- Automatic issue detection and fixing
- Deployment monitoring and health checks
- Deployment recommendations and best practices
"""

import os
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add project paths for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "core"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# Import the Railway MCP tools
try:
    from monkey_coder.mcp.railway_deployment_tool import MCPRailwayTool
    RAILWAY_MCP_AVAILABLE = True
except ImportError as e:
    RAILWAY_MCP_AVAILABLE = False
    print(f"Warning: Railway MCP not available: {e}")

try:
    from mcp_railway_deployment_manager import RailwayDeploymentManager, DeploymentStatus
    RAILWAY_MANAGER_AVAILABLE = True
except ImportError:
    RAILWAY_MANAGER_AVAILABLE = False


# Skip all tests if Railway MCP is not available
pytestmark = pytest.mark.skipif(
    not RAILWAY_MCP_AVAILABLE,
    reason="Railway MCP tools not available"
)


@pytest.fixture
def test_project_root(tmp_path):
    """Create a temporary test project structure."""
    # Create basic project structure
    (tmp_path / "packages" / "core").mkdir(parents=True)
    (tmp_path / "scripts").mkdir(parents=True)
    
    # Create a sample railpack.json
    railpack_config = {
        "build": {
            "provider": "nixpacks"
        },
        "deploy": {
            "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
            "healthCheckPath": "/health",
            "healthCheckTimeout": 305
        }
    }
    
    with open(tmp_path / "railpack.json", "w") as f:
        json.dump(railpack_config, f, indent=2)
    
    # Create a basic run_server.py
    server_code = """
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
"""
    with open(tmp_path / "run_server.py", "w") as f:
        f.write(server_code)
    
    return tmp_path


@pytest.fixture
def railway_mcp_tool(test_project_root):
    """Create a Railway MCP tool instance for testing."""
    return MCPRailwayTool(project_root=test_project_root)


class TestRailwayMCPToolInitialization:
    """Test Railway MCP tool initialization and configuration."""
    
    def test_tool_initialization(self, railway_mcp_tool):
        """Test that Railway MCP tool initializes correctly."""
        assert railway_mcp_tool is not None
        assert hasattr(railway_mcp_tool, 'validate_railway_deployment')
        assert hasattr(railway_mcp_tool, 'fix_railway_deployment_issues')
        assert hasattr(railway_mcp_tool, 'monitor_railway_deployment')
        assert hasattr(railway_mcp_tool, 'get_railway_deployment_recommendations')
    
    def test_tool_has_logger(self, railway_mcp_tool):
        """Test that the tool has a configured logger."""
        assert hasattr(railway_mcp_tool, 'logger')
        assert railway_mcp_tool.logger is not None
    
    def test_tool_project_root_set(self, railway_mcp_tool, test_project_root):
        """Test that project root is properly set."""
        assert railway_mcp_tool.project_root == test_project_root


class TestRailwayDeploymentValidation:
    """Test Railway deployment validation functionality."""
    
    def test_validate_deployment_basic(self, railway_mcp_tool, test_project_root):
        """Test basic deployment validation."""
        results = railway_mcp_tool.validate_railway_deployment(
            project_path=str(test_project_root)
        )
        
        assert results is not None
        assert isinstance(results, dict)
        assert "timestamp" in results
        
        # Check for expected validation fields
        if "error" not in results:
            assert "overall_status" in results
            assert "deployment_ready" in results
            assert "checks" in results
    
    def test_validate_deployment_with_verbose(self, railway_mcp_tool, test_project_root):
        """Test deployment validation with verbose output."""
        results = railway_mcp_tool.validate_railway_deployment(
            project_path=str(test_project_root),
            verbose=True
        )
        
        assert results is not None
        assert isinstance(results, dict)
    
    def test_validate_missing_railpack(self, railway_mcp_tool, tmp_path):
        """Test validation when railpack.json is missing."""
        # Create empty directory without railpack.json
        empty_dir = tmp_path / "empty_project"
        empty_dir.mkdir()
        
        results = railway_mcp_tool.validate_railway_deployment(
            project_path=str(empty_dir)
        )
        
        assert results is not None
        # Should either return error or show critical issues
        if "error" not in results:
            assert results.get("critical_checks", 0) > 0 or results.get("deployment_ready", True) == False
    
    def test_validate_invalid_json_railpack(self, railway_mcp_tool, tmp_path):
        """Test validation with invalid JSON in railpack.json."""
        invalid_dir = tmp_path / "invalid_project"
        invalid_dir.mkdir()
        
        # Create invalid JSON file
        with open(invalid_dir / "railpack.json", "w") as f:
            f.write("{ invalid json }")
        
        results = railway_mcp_tool.validate_railway_deployment(
            project_path=str(invalid_dir)
        )
        
        assert results is not None
        # Should show critical issues for invalid JSON
        if "error" not in results:
            assert results.get("critical_checks", 0) > 0 or results.get("deployment_ready", True) == False


class TestRailwayDeploymentFixes:
    """Test Railway deployment automatic fix functionality."""
    
    def test_fix_deployment_issues_basic(self, railway_mcp_tool, test_project_root):
        """Test basic deployment issue fixing."""
        results = railway_mcp_tool.fix_railway_deployment_issues(
            project_path=str(test_project_root),
            auto_apply=False  # Don't actually apply fixes in test
        )
        
        assert results is not None
        assert isinstance(results, dict)
        
        # If Railway manager not available, check for error
        if "error" in results:
            assert "Railway deployment manager not available" in results["error"]
        else:
            assert "validation_results" in results
            assert "fix_script_generated" in results
    
    def test_fix_deployment_without_auto_apply(self, railway_mcp_tool, test_project_root):
        """Test that fixes are not applied when auto_apply is False."""
        results = railway_mcp_tool.fix_railway_deployment_issues(
            project_path=str(test_project_root),
            auto_apply=False
        )
        
        assert results is not None
        
        # If Railway manager not available, check for error
        if "error" in results:
            assert "Railway deployment manager not available" in results["error"]
        else:
            assert results.get("auto_apply") == False
            # Should not have applied fixes
            assert "fix_script_executed" not in results or results.get("fix_script_executed") == False


class TestRailwayDeploymentMonitoring:
    """Test Railway deployment monitoring functionality."""
    
    def test_monitor_deployment_basic(self, railway_mcp_tool):
        """Test basic deployment monitoring."""
        results = railway_mcp_tool.monitor_railway_deployment(
            check_health=False,  # Don't actually check health endpoints
            run_smoke_tests=False
        )
        
        assert results is not None
        assert isinstance(results, dict)
        assert "timestamp" in results
        assert "health_check_enabled" in results
        assert "smoke_tests_enabled" in results
    
    @patch('requests.get')
    def test_monitor_with_health_check(self, mock_get, railway_mcp_tool):
        """Test monitoring with health check enabled."""
        # Mock successful health check response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_get.return_value = mock_response
        
        results = railway_mcp_tool.monitor_railway_deployment(
            check_health=True,
            run_smoke_tests=False
        )
        
        assert results is not None
        assert "health_status" in results
    
    def test_monitor_without_smoke_tests(self, railway_mcp_tool):
        """Test that smoke tests are skipped when not enabled."""
        results = railway_mcp_tool.monitor_railway_deployment(
            check_health=False,
            run_smoke_tests=False
        )
        
        assert results is not None
        assert results.get("smoke_tests_enabled") == False


class TestRailwayDeploymentRecommendations:
    """Test Railway deployment recommendations functionality."""
    
    def test_get_recommendations_basic(self, railway_mcp_tool, test_project_root):
        """Test getting basic deployment recommendations."""
        results = railway_mcp_tool.get_railway_deployment_recommendations(
            project_path=str(test_project_root)
        )
        
        assert results is not None
        assert isinstance(results, dict)
        assert "timestamp" in results
        assert "project_root" in results
        assert "railway_best_practices" in results
    
    def test_recommendations_include_best_practices(self, railway_mcp_tool, test_project_root):
        """Test that recommendations include Railway best practices."""
        results = railway_mcp_tool.get_railway_deployment_recommendations(
            project_path=str(test_project_root)
        )
        
        best_practices = results.get("railway_best_practices", [])
        assert isinstance(best_practices, list)
        assert len(best_practices) > 0
        
        # Check for key best practices
        practices_text = " ".join(best_practices).lower()
        assert "railpack.json" in practices_text or "port" in practices_text
    
    def test_recommendations_include_mcp_integration(self, railway_mcp_tool, test_project_root):
        """Test that recommendations include MCP integration advice."""
        results = railway_mcp_tool.get_railway_deployment_recommendations(
            project_path=str(test_project_root)
        )
        
        assert "mcp_integration" in results
        mcp_recommendations = results.get("mcp_integration", [])
        assert isinstance(mcp_recommendations, list)
    
    def test_recommendations_include_security(self, railway_mcp_tool, test_project_root):
        """Test that recommendations include security advice."""
        results = railway_mcp_tool.get_railway_deployment_recommendations(
            project_path=str(test_project_root)
        )
        
        assert "security_recommendations" in results
        security_recs = results.get("security_recommendations", [])
        assert isinstance(security_recs, list)
        assert len(security_recs) > 0


class TestRailwayMCPToolRegistration:
    """Test Railway MCP tool registration and metadata."""
    
    def test_get_mcp_railway_tools_function(self):
        """Test that MCP tool definitions are available."""
        from monkey_coder.mcp.railway_deployment_tool import get_mcp_railway_tools
        
        tools = get_mcp_railway_tools()
        
        assert tools is not None
        assert isinstance(tools, dict)
        
        # Check for expected tool definitions
        expected_tools = [
            "validate_railway_deployment",
            "fix_railway_deployment_issues",
            "monitor_railway_deployment",
            "get_railway_deployment_recommendations"
        ]
        
        for tool_name in expected_tools:
            assert tool_name in tools
            tool_def = tools[tool_name]
            assert "name" in tool_def
            assert "description" in tool_def
            assert "parameters" in tool_def
    
    def test_tool_definitions_have_parameters(self):
        """Test that tool definitions include proper parameter schemas."""
        from monkey_coder.mcp.railway_deployment_tool import get_mcp_railway_tools
        
        tools = get_mcp_railway_tools()
        
        for tool_name, tool_def in tools.items():
            params = tool_def.get("parameters", {})
            assert "type" in params
            assert params["type"] == "object"
            assert "properties" in params


class TestRailwayMCPIntegrationScenarios:
    """Test real-world Railway MCP integration scenarios."""
    
    def test_full_validation_workflow(self, railway_mcp_tool, test_project_root):
        """Test complete validation workflow."""
        # Step 1: Validate deployment
        validation_results = railway_mcp_tool.validate_railway_deployment(
            project_path=str(test_project_root)
        )
        
        assert validation_results is not None
        
        # Step 2: Get recommendations
        recommendations = railway_mcp_tool.get_railway_deployment_recommendations(
            project_path=str(test_project_root)
        )
        
        assert recommendations is not None
        assert "railway_best_practices" in recommendations
    
    def test_validation_and_fix_workflow(self, railway_mcp_tool, test_project_root):
        """Test validation followed by fix workflow."""
        # Step 1: Validate
        validation_results = railway_mcp_tool.validate_railway_deployment(
            project_path=str(test_project_root)
        )
        
        assert validation_results is not None
        
        # Step 2: Try to fix (without auto-apply)
        fix_results = railway_mcp_tool.fix_railway_deployment_issues(
            project_path=str(test_project_root),
            auto_apply=False
        )
        
        assert fix_results is not None
        
        # If Railway manager not available, check for error
        if "error" not in fix_results:
            assert "validation_results" in fix_results


@pytest.mark.skipif(
    not RAILWAY_MANAGER_AVAILABLE,
    reason="Railway Deployment Manager not available"
)
class TestRailwayDeploymentManager:
    """Test Railway Deployment Manager integration with MCP."""
    
    def test_deployment_manager_initialization(self, test_project_root):
        """Test that deployment manager initializes correctly."""
        manager = RailwayDeploymentManager(test_project_root, verbose=False)
        
        assert manager is not None
        assert manager.project_root == test_project_root
    
    def test_deployment_manager_run_check(self, test_project_root):
        """Test running comprehensive deployment check."""
        manager = RailwayDeploymentManager(test_project_root, verbose=False)
        
        results = manager.run_comprehensive_check()
        
        assert results is not None
        assert isinstance(results, dict)
        assert "overall_status" in results
        assert "checks" in results


class TestRailwayMCPErrorHandling:
    """Test error handling in Railway MCP tools."""
    
    def test_validate_with_none_project_path(self, railway_mcp_tool):
        """Test validation with None project path."""
        results = railway_mcp_tool.validate_railway_deployment(
            project_path=None
        )
        
        # Should use default project root
        assert results is not None
    
    def test_validate_with_nonexistent_path(self, railway_mcp_tool):
        """Test validation with non-existent project path."""
        results = railway_mcp_tool.validate_railway_deployment(
            project_path="/nonexistent/path/to/project"
        )
        
        # Should handle gracefully
        assert results is not None
    
    def test_monitor_with_invalid_service_name(self, railway_mcp_tool):
        """Test monitoring with invalid service name."""
        results = railway_mcp_tool.monitor_railway_deployment(
            service_name="nonexistent_service",
            check_health=False,
            run_smoke_tests=False
        )
        
        # Should not crash
        assert results is not None


# Integration test marker for running with external dependencies
@pytest.mark.integration
class TestRailwayMCPWithExternalServices:
    """Test Railway MCP with external services (requires network)."""
    
    @pytest.mark.skip(reason="Requires external Railway service")
    def test_monitor_live_deployment(self, railway_mcp_tool):
        """Test monitoring a live Railway deployment."""
        results = railway_mcp_tool.monitor_railway_deployment(
            check_health=True,
            run_smoke_tests=True
        )
        
        assert results is not None
        assert "health_status" in results


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
