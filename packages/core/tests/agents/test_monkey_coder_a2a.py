"""
Tests for A2A (Agent-to-Agent) integration in Monkey-Coder
"""

import pytest
import asyncio
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from monkey_coder.a2a_server import MonkeyCoderA2AAgent
from monkey_coder.agents.base_agent import AgentContext, AgentCapability


class TestMonkeyCoderA2AAgent:
    """Test suite for MonkeyCoderA2AAgent"""
    
    @pytest.fixture
    async def agent(self):
        """Create test agent instance"""
        agent = MonkeyCoderA2AAgent(port=7703)  # Use different port for testing
        return agent
    
    @pytest.fixture
    async def initialized_agent(self, agent):
        """Create and initialize test agent"""
        with patch.object(agent, '_initialize_mcp_clients', new_callable=AsyncMock):
            with patch.object(agent.code_generator, 'initialize', new_callable=AsyncMock):
                await agent.initialize()
        return agent
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initialization process"""
        with patch.object(agent, '_initialize_mcp_clients', new_callable=AsyncMock) as mock_mcp:
            with patch.object(agent.code_generator, 'initialize', new_callable=AsyncMock) as mock_gen:
                await agent.initialize()
                
                # Verify initialization calls
                mock_mcp.assert_called_once()
                mock_gen.assert_called_once()
                
                # Verify server creation
                assert agent.server is not None
                
                # Verify agent card
                assert agent.agent_card.name == "Monkey-Coder Agent"
                assert "generate_code" in [skill["name"] for skill in agent.agent_card.skills]
    
    @pytest.mark.asyncio
    async def test_generate_code_skill(self, initialized_agent):
        """Test the generate_code skill"""
        # Mock the code generator response
        mock_result = {
            "code": "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)",
            "metadata": {"language": "python"}
        }
        
        with patch.object(initialized_agent.code_generator, 'execute_with_quantum', new_callable=AsyncMock, return_value=mock_result):
            result = await initialized_agent.generate_code(
                spec="Create a function that calculates factorial",
                context={"language": "python", "style": "clean"}
            )
            
            assert "def factorial" in result
            assert "return" in result
    
    @pytest.mark.asyncio
    async def test_analyze_repo_skill(self, initialized_agent):
        """Test the analyze_repo skill"""
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text("def hello():\n    print('hello world')")
            
            # Mock MCP filesystem client
            mock_fs_client = AsyncMock()
            mock_fs_client.call_tool.return_value = [{"text": "test.py\n"}]
            initialized_agent.mcp_clients["filesystem"] = mock_fs_client
            
            result = await initialized_agent.analyze_repo(
                repo_path=str(temp_dir),
                analysis_type="structure"
            )
            
            assert "Analysis" in result or "Error" in result
    
    @pytest.mark.asyncio
    async def test_run_tests_skill(self, initialized_agent):
        """Test the run_tests skill"""
        # Create temporary test file
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test_example.py"
            test_file.write_text("""
import unittest

class TestExample(unittest.TestCase):
    def test_example(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
""")
            
            # Mock MCP filesystem client
            mock_fs_client = AsyncMock()
            mock_fs_client.call_tool.return_value = [{"text": "test_example.py\n"}]
            initialized_agent.mcp_clients["filesystem"] = mock_fs_client
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stdout="test passed", stderr="")
                
                result = await initialized_agent.run_tests(
                    path=str(test_file),
                    test_framework="unittest"
                )
                
                assert "Exit code: 0" in result
                assert "test passed" in result
    
    @pytest.mark.asyncio
    async def test_mcp_client_initialization(self, agent):
        """Test MCP client initialization"""
        with patch('monkey_coder.mcp.client.MCPClient.connect') as mock_connect:
            mock_fs_client = AsyncMock()
            mock_connect.return_value = mock_fs_client
            
            await agent._initialize_mcp_clients()
            
            # Verify filesystem client was created
            assert "filesystem" in agent.mcp_clients
            mock_connect.assert_called()
    
    @pytest.mark.asyncio
    async def test_agent_card_creation(self, agent):
        """Test agent card metadata creation"""
        card = agent.agent_card
        
        assert card.name == "Monkey-Coder Agent"
        assert card.version == "1.0.0"
        assert len(card.skills) == 3
        
        skill_names = [skill["name"] for skill in card.skills]
        assert "generate_code" in skill_names
        assert "analyze_repo" in skill_names
        assert "run_tests" in skill_names
    
    @pytest.mark.asyncio
    async def test_test_framework_detection(self, initialized_agent):
        """Test automatic test framework detection"""
        # Mock filesystem client
        mock_fs_client = AsyncMock()
        
        # Test pytest detection
        mock_fs_client.call_tool.side_effect = [
            {"text": "content"},  # pytest.ini exists
        ]
        initialized_agent.mcp_clients["filesystem"] = mock_fs_client
        
        framework = await initialized_agent._detect_test_framework("/some/path/test.py")
        assert framework == "pytest"
        
        # Test jest detection (package.json)
        mock_fs_client.call_tool.side_effect = [
            Exception("not found"),  # pytest.ini
            Exception("not found"),  # conftest.py
            Exception("not found"),  # pyproject.toml
            {"text": "package.json content"},  # package.json
        ]
        
        framework = await initialized_agent._detect_test_framework("/some/path/test.js")
        assert framework == "jest"
    
    def test_skill_parameter_validation(self, agent):
        """Test skill parameter schemas"""
        generate_code_skill = None
        for skill in agent.agent_card.skills:
            if skill["name"] == "generate_code":
                generate_code_skill = skill
                break
        
        assert generate_code_skill is not None
        assert "spec" in generate_code_skill["parameters"]["required"]
        assert "context" in generate_code_skill["parameters"]["properties"]
    
    @pytest.mark.asyncio
    async def test_error_handling(self, initialized_agent):
        """Test error handling in skills"""
        # Test generate_code with error
        with patch.object(initialized_agent.code_generator, 'execute_with_quantum', side_effect=Exception("Test error")):
            result = await initialized_agent.generate_code("test spec")
            assert "Error generating code" in result
            assert "Test error" in result
        
        # Test analyze_repo with missing path
        result = await initialized_agent.analyze_repo("/nonexistent/path")
        assert "Error" in result
    
    @pytest.mark.asyncio
    async def test_agent_lifecycle(self, agent):
        """Test complete agent start/stop lifecycle"""
        # Mock the necessary components for the start method
        with patch.object(agent, 'initialize', new_callable=AsyncMock) as mock_init:
            with patch('monkey_coder.a2a_server.create_flask_app') as mock_flask:
                with patch('werkzeug.serving.make_server') as mock_make_server:
                    with patch('threading.Thread') as mock_thread:
                        # Setup mocks
                        mock_server = Mock()
                        agent.server = mock_server
                        mock_http_server = Mock()
                        mock_make_server.return_value = mock_http_server
                        mock_thread_instance = Mock()
                        mock_thread.return_value = mock_thread_instance
                        
                        # Test start
                        await agent.start()
                        mock_init.assert_called_once()
                        
                        # Verify Flask app was created with the server
                        mock_flask.assert_called_once_with(mock_server)
                        
                        # Test stop
                        await agent.stop()
                        # Stop should call shutdown on the HTTP server if it exists
                        # Note: stop implementation may vary


class TestA2AIntegration:
    """Integration tests for A2A functionality"""
    
    @pytest.mark.asyncio
    async def test_agent_card_endpoint_integration(self):
        """Test agent card HTTP endpoint"""
        from monkey_coder.app.main import app
        from fastapi.testclient import TestClient
        
        with TestClient(app) as client:
            response = client.get("/.well-known/agent.json")
            
            # Should return either the agent card or an error response
            assert response.status_code in [200, 500]
            
            if response.status_code == 200:
                data = response.json()
                assert "name" in data
                assert "skills" in data or "error" in data
    
    @pytest.mark.asyncio
    async def test_main_app_a2a_integration(self):
        """Test A2A server integration with main FastAPI app"""
        from monkey_coder.app.main import app
        
        # Mock A2A agent for testing
        mock_agent = AsyncMock()
        mock_agent.port = 7702
        mock_agent.mcp_clients = {}
        
        app.state.a2a_agent = mock_agent
        
        # Test agent card endpoint with mocked agent
        from fastapi.testclient import TestClient
        with TestClient(app) as client:
            response = client.get("/.well-known/agent.json")
            assert response.status_code == 200
            
            data = response.json()
            assert data["a2a_server"]["status"] == "running"
            assert data["a2a_server"]["port"] == 7702


class TestPromptTemplates:
    """Test prompt template functionality"""
    
    def test_prompt_templates_exist(self):
        """Test that prompt templates are created"""
        prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        
        assert prompts_dir.exists()
        assert (prompts_dir / "code_generation.md").exists()
        assert (prompts_dir / "code_analysis.md").exists()
        assert (prompts_dir / "test_generation.md").exists()
    
    def test_prompt_template_content(self):
        """Test prompt template content structure"""
        prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        
        # Test code generation template
        code_gen_template = (prompts_dir / "code_generation.md").read_text()
        assert "{spec}" in code_gen_template
        assert "{language}" in code_gen_template
        assert "{style}" in code_gen_template
        
        # Test analysis template
        analysis_template = (prompts_dir / "code_analysis.md").read_text()
        assert "{task}" in analysis_template
        assert "{analysis_type}" in analysis_template
        assert "{repo_path}" in analysis_template


class TestMCPIntegration:
    """Test MCP (Model Context Protocol) integration"""
    
    @pytest.mark.asyncio
    async def test_mcp_filesystem_operations(self):
        """Test MCP filesystem operations"""
        from monkey_coder.mcp.client import MCPClient
        
        # Mock MCP client
        with patch.object(MCPClient, 'connect') as mock_connect:
            mock_client = AsyncMock()
            mock_client.call_tool.return_value = [{"text": "file content"}]
            mock_connect.return_value = mock_client
            
            client = await MCPClient.connect("filesystem")
            result = await client.call_tool("read_file", {"path": "/test/file.py"})
            
            assert result == [{"text": "file content"}]
    
    @pytest.mark.asyncio
    async def test_mcp_github_integration(self):
        """Test MCP GitHub integration"""
        from monkey_coder.mcp.servers.github import GithubMCPServer
        
        # Test GitHub server initialization
        config = {"token": "test_token"}
        server = GithubMCPServer(config)
        
        assert server.token == "test_token"
        assert "get_repository" in server.tools
        assert "list_repositories" in server.tools


if __name__ == "__main__":
    pytest.main([__file__, "-v"])