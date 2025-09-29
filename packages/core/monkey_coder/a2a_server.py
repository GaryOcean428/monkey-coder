"""
A2A Server for Monkey-Coder Agent
Implements Agent-to-Agent interface with specialized skills for code generation and analysis
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

from python_a2a import A2AServer, skill, AgentCard
from python_a2a.models import Message, MessageRole, TextContent

from .agents.base_agent import AgentContext, AgentCapability
from .agents.specialized.code_generator import CodeGeneratorAgent
from .agents.specialized.code_analyzer import CodeAnalyzerAgent
from .mcp.client import MCPClient
from .config.env_config import get_config

logger = logging.getLogger(__name__)


class MonkeyCoderA2AAgent:
    """
    Monkey-Coder specialized A2A agent with code generation and analysis capabilities
    """
    
    def __init__(self, port: int = 7702):
        self.port = port
        self.server: Optional[A2AServer] = None
        self.code_generator = CodeGeneratorAgent()
        self.code_analyzer = None  # Will initialize if available
        self.mcp_clients: Dict[str, MCPClient] = {}
        self.config = get_config()
        
        # Agent card metadata
        self.agent_card = AgentCard(
            name="Monkey-Coder Agent",
            description="Specialized Deep Agent for code generation, repository analysis, and testing",
            url="http://localhost:7702",  # A2A server URL
            version="1.0.0",
            capabilities={
                "code_generation": True,
                "code_analysis": True, 
                "testing": True,
                "repository_analysis": True,
                "mcp_integration": True
            },
            skills=[
                {
                    "name": "generate_code",
                    "description": "Generate code implementing a feature specification",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "spec": {
                                "type": "string",
                                "description": "Feature specification or description of code to generate"
                            },
                            "context": {
                                "type": "object",
                                "description": "Optional context including files, language, style preferences",
                                "properties": {
                                    "language": {"type": "string", "description": "Programming language"},
                                    "style": {"type": "string", "description": "Code style preference"},
                                    "files": {"type": "object", "description": "Related files for context"}
                                }
                            }
                        },
                        "required": ["spec"]
                    }
                },
                {
                    "name": "analyze_repo",
                    "description": "Analyze a repository or module for structure, issues, and improvements",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "repo_path": {
                                "type": "string",
                                "description": "Path to repository or module to analyze"
                            },
                            "analysis_type": {
                                "type": "string",
                                "enum": ["structure", "issues", "improvements", "comprehensive"],
                                "description": "Type of analysis to perform"
                            }
                        },
                        "required": ["repo_path"]
                    }
                },
                {
                    "name": "run_tests",
                    "description": "Execute tests and return results",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to test files or directory"
                            },
                            "test_framework": {
                                "type": "string",
                                "enum": ["pytest", "unittest", "jest", "auto"],
                                "description": "Test framework to use"
                            },
                            "options": {
                                "type": "object",
                                "description": "Additional test options"
                            }
                        },
                        "required": ["path"]
                    }
                }
            ]
        )
        
    async def initialize(self) -> None:
        """Initialize the A2A agent and its dependencies"""
        try:
            # Initialize agents
            await self.code_generator.initialize()
            
            # Try to initialize code analyzer if available
            try:
                from .agents.specialized.code_analyzer import CodeAnalyzerAgent
                self.code_analyzer = CodeAnalyzerAgent()
                await self.code_analyzer.initialize()
            except ImportError:
                logger.warning("Code analyzer not available, creating basic implementation")
                self.code_analyzer = None
            
            # Initialize MCP clients
            await self._initialize_mcp_clients()
            
            # Create A2A server
            self.server = A2AServer(
                agent_card=self.agent_card
            )
            
            # Register skills
            self._register_skills()
            
            logger.info(f"Monkey-Coder A2A Agent initialized on port {self.port}")
            
        except Exception as e:
            logger.error(f"Failed to initialize A2A agent: {e}")
            raise
            
    async def _initialize_mcp_clients(self) -> None:
        """Initialize MCP clients for filesystem and GitHub operations"""
        try:
            # Initialize filesystem MCP client
            fs_client = await MCPClient.connect("filesystem")
            self.mcp_clients["filesystem"] = fs_client
            logger.info("Connected to filesystem MCP server")
            
            # Initialize GitHub MCP client if token available
            github_token = os.getenv("GITHUB_TOKEN")
            if github_token:
                github_client = await MCPClient.connect({
                    "name": "github",
                    "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
                    "env": {"GITHUB_TOKEN": github_token}
                })
                self.mcp_clients["github"] = github_client
                logger.info("Connected to GitHub MCP server")
            else:
                logger.warning("No GitHub token found, GitHub MCP server not available")
                
        except Exception as e:
            logger.error(f"Failed to initialize MCP clients: {e}")
            # Continue without MCP if it fails
            
    def _register_skills(self) -> None:
        """Register A2A skills with the server"""
        if not self.server:
            raise RuntimeError("Server not initialized")
            
        # Skills are automatically registered via @skill decorators
        logger.info("Skills registered via decorators")
        
    @skill(name="generate_code")
    async def generate_code(self, spec: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate code implementing a feature specification
        
        Args:
            spec: Feature specification or description
            context: Optional context including files, language preferences
            
        Returns:
            Generated code as string
        """
        try:
            # Create agent context
            agent_context = AgentContext(
                task_id=f"generate_{hash(spec)}",
                user_id="a2a_user",
                session_id=f"a2a_session_{hash(spec)}",
                files=context.get("files", {}) if context else {},
                metadata=context or {},
                mcp_servers=list(self.mcp_clients.keys())
            )
            
            # Connect MCP servers to agent
            if self.mcp_clients:
                await self.code_generator.connect_mcp_servers(list(self.mcp_clients.keys()))
                # Update agent's MCP clients
                self.code_generator.mcp_clients = self.mcp_clients
            
            # Generate code using quantum execution for best results
            result = await self.code_generator.execute_with_quantum(
                task=spec,
                context=agent_context
            )
            
            # Extract generated code
            if isinstance(result, dict):
                if "code" in result:
                    return result["code"]
                elif "content" in result:
                    return result["content"]
                else:
                    return str(result)
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return f"Error generating code: {str(e)}"
    
    @skill(name="analyze_repo")
    async def analyze_repo(self, repo_path: str, analysis_type: str = "comprehensive") -> str:
        """
        Analyze a repository or module for structure, issues, and improvements
        
        Args:
            repo_path: Path to repository or module
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results as string
        """
        try:
            # Use MCP filesystem tools to read repository structure
            repo_structure = await self._get_repo_structure(repo_path)
            
            if self.code_analyzer:
                # Use specialized code analyzer if available
                agent_context = AgentContext(
                    task_id=f"analyze_{hash(repo_path)}",
                    user_id="a2a_user",
                    session_id=f"a2a_session_{hash(repo_path)}",
                    workspace_path=repo_path,
                    metadata={"analysis_type": analysis_type, "repo_structure": repo_structure},
                    mcp_servers=list(self.mcp_clients.keys())
                )
                
                await self.code_analyzer.connect_mcp_servers(list(self.mcp_clients.keys()))
                self.code_analyzer.mcp_clients = self.mcp_clients
                
                result = await self.code_analyzer.process(
                    task=f"Analyze repository at {repo_path} for {analysis_type}",
                    context=agent_context
                )
                
                if isinstance(result, dict):
                    return result.get("analysis", str(result))
                return str(result)
            else:
                # Basic analysis using code generator
                analysis_prompt = f"""
                Analyze the repository structure at {repo_path} for {analysis_type} analysis.
                
                Repository structure:
                {repo_structure}
                
                Provide insights on:
                - Code organization and structure
                - Potential issues or improvements
                - Architecture patterns
                - Code quality observations
                """
                
                return await self.generate_code(analysis_prompt, {"analysis_mode": True})
                
        except Exception as e:
            logger.error(f"Error analyzing repository: {e}")
            return f"Error analyzing repository: {str(e)}"
    
    @skill(name="run_tests")
    async def run_tests(self, path: str, test_framework: str = "auto", options: Optional[Dict[str, Any]] = None) -> str:
        """
        Execute tests and return results
        
        Args:
            path: Path to test files or directory
            test_framework: Test framework to use
            options: Additional test options
            
        Returns:
            Test execution results
        """
        try:
            # Use MCP filesystem to check if path exists
            if "filesystem" in self.mcp_clients:
                fs_client = self.mcp_clients["filesystem"]
                
                # Check if path exists
                try:
                    path_info = await fs_client.call_tool("list_directory", {"path": path})
                except Exception:
                    return f"Error: Test path '{path}' not found or not accessible"
            
            # Auto-detect test framework if needed
            if test_framework == "auto":
                test_framework = await self._detect_test_framework(path)
            
            # Execute tests based on framework
            if test_framework == "pytest":
                return await self._run_pytest(path, options or {})
            elif test_framework == "unittest":
                return await self._run_unittest(path, options or {})
            elif test_framework == "jest":
                return await self._run_jest(path, options or {})
            else:
                return f"Unsupported test framework: {test_framework}"
                
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return f"Error running tests: {str(e)}"
    
    async def _get_repo_structure(self, repo_path: str) -> str:
        """Get repository structure using MCP filesystem tools"""
        try:
            if "filesystem" not in self.mcp_clients:
                return "Filesystem MCP client not available"
            
            fs_client = self.mcp_clients["filesystem"]
            
            # Get directory listing
            result = await fs_client.call_tool("list_directory", {"path": repo_path})
            
            if isinstance(result, list) and result:
                content = result[0] if len(result) > 0 else {}
                if isinstance(content, dict) and "text" in content:
                    return content["text"]
            
            return str(result)
            
        except Exception as e:
            logger.error(f"Error getting repo structure: {e}")
            return f"Error reading repository structure: {str(e)}"
    
    async def _detect_test_framework(self, path: str) -> str:
        """Auto-detect test framework based on files and structure"""
        try:
            if "filesystem" not in self.mcp_clients:
                return "pytest"  # Default fallback
            
            fs_client = self.mcp_clients["filesystem"]
            
            # Check for common test framework indicators
            path_obj = Path(path)
            
            # Check for pytest.ini, conftest.py
            for indicator in ["pytest.ini", "conftest.py", "pyproject.toml"]:
                try:
                    await fs_client.call_tool("read_file", {"path": str(path_obj.parent / indicator)})
                    return "pytest"
                except:
                    continue
            
            # Check for package.json (Jest)
            try:
                await fs_client.call_tool("read_file", {"path": str(path_obj.parent / "package.json")})
                return "jest"
            except:
                pass
            
            # Default to pytest for Python, jest for JS/TS
            if any(path.endswith(ext) for ext in [".py"]):
                return "pytest"
            elif any(path.endswith(ext) for ext in [".js", ".ts", ".jsx", ".tsx"]):
                return "jest"
            
            return "pytest"  # Default fallback
            
        except Exception:
            return "pytest"
    
    async def _run_pytest(self, path: str, options: Dict[str, Any]) -> str:
        """Run pytest tests"""
        try:
            import subprocess
            
            cmd = ["python", "-m", "pytest", path, "-v"]
            
            # Add common options
            if options.get("coverage"):
                cmd.extend(["--cov", "--cov-report=term-missing"])
            
            if options.get("verbose"):
                cmd.append("-vv")
            
            # Execute tests
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            output = f"Exit code: {result.returncode}\n\n"
            output += f"STDOUT:\n{result.stdout}\n\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            
            return output
            
        except subprocess.TimeoutExpired:
            return "Test execution timed out after 5 minutes"
        except Exception as e:
            return f"Error running pytest: {str(e)}"
    
    async def _run_unittest(self, path: str, options: Dict[str, Any]) -> str:
        """Run unittest tests"""
        try:
            import subprocess
            
            cmd = ["python", "-m", "unittest", "discover", "-s", path, "-v"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            output = f"Exit code: {result.returncode}\n\n"
            output += f"STDOUT:\n{result.stdout}\n\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            
            return output
            
        except subprocess.TimeoutExpired:
            return "Test execution timed out after 5 minutes"
        except Exception as e:
            return f"Error running unittest: {str(e)}"
    
    async def _run_jest(self, path: str, options: Dict[str, Any]) -> str:
        """Run Jest tests"""
        try:
            import subprocess
            
            cmd = ["npx", "jest", path, "--verbose"]
            
            if options.get("coverage"):
                cmd.append("--coverage")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            output = f"Exit code: {result.returncode}\n\n"
            output += f"STDOUT:\n{result.stdout}\n\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            
            return output
            
        except subprocess.TimeoutExpired:
            return "Test execution timed out after 5 minutes"
        except Exception as e:
            return f"Error running jest: {str(e)}"
    
    async def start(self) -> None:
        """Start the A2A server"""
        if not self.server:
            await self.initialize()
        
        if self.server:
            logger.info(f"Monkey-Coder A2A server initialized on port {self.port}")
        else:
            raise RuntimeError("Failed to initialize A2A server")
    
    async def stop(self) -> None:
        """Stop the A2A server and cleanup"""
        if self.server:
            logger.info("A2A server cleanup initiated")
        
        # Disconnect MCP clients
        for client in self.mcp_clients.values():
            try:
                await client.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting MCP client: {e}")
        
        # Disconnect agents from MCP
        if self.code_generator:
            await self.code_generator.disconnect_mcp_servers()
        if self.code_analyzer:
            await self.code_analyzer.disconnect_mcp_servers()
        
        logger.info("Monkey-Coder A2A server stopped")


async def main():
    """Main entry point for running the A2A server"""
    # Get port from environment or use default
    port = int(os.getenv("A2A_PORT", "7702"))
    
    # Create and start agent
    agent = MonkeyCoderA2AAgent(port=port)
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await agent.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
