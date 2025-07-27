"""
E2B Sandbox Integration

Provides secure code execution environment using E2B cloud sandboxes.
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from e2b_code_interpreter import Sandbox
from e2b import DataAnalysis

logger = logging.getLogger(__name__)


class E2BSandboxManager:
    """Manages E2B sandbox instances for secure code execution."""
    
    def __init__(self):
        self.active_sandboxes: Dict[str, Sandbox] = {}
        self.sandbox_metadata: Dict[str, Dict[str, Any]] = {}
        self.api_key = os.getenv("E2B_API_KEY")
        
        if not self.api_key:
            logger.warning("E2B_API_KEY not found. E2B integration disabled.")
    
    async def execute_code(
        self,
        code: str,
        execution_id: str,
        timeout: int = 30,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute Python code in a secure E2B sandbox.
        
        Args:
            code: Python code to execute
            execution_id: Unique execution identifier
            timeout: Execution timeout in seconds
            metadata: Additional execution metadata
            
        Returns:
            Dictionary containing execution results and logs
        """
        if not self.api_key:
            raise RuntimeError("E2B API key not configured")
        
        sandbox = None
        try:
            # Create new sandbox instance
            sandbox = await self._create_sandbox(execution_id, timeout)
            
            # Execute code with timeout
            result = await asyncio.wait_for(
                self._run_code_in_sandbox(sandbox, code),
                timeout=timeout
            )
            
            # Capture sandbox logs
            logs = await self._get_sandbox_logs(sandbox)
            
            return {
                "output": result,
                "logs": logs,
                "sandbox_id": sandbox.sandbox_id,
                "execution_time": result.get("execution_time", 0)
            }
            
        except asyncio.TimeoutError:
            logger.error(f"Code execution timeout for {execution_id}")
            return {
                "output": None,
                "logs": [f"Execution timed out after {timeout} seconds"],
                "error": "TIMEOUT"
            }
        except Exception as e:
            logger.error(f"E2B execution failed for {execution_id}: {str(e)}")
            return {
                "output": None,
                "logs": [f"Execution error: {str(e)}"],
                "error": str(e)
            }
        finally:
            if sandbox and execution_id in self.active_sandboxes:
                await self._cleanup_sandbox(execution_id)
    
    async def _create_sandbox(
        self,
        execution_id: str,
        timeout: int
    ) -> Sandbox:
        """Create and configure a new E2B sandbox."""
        try:
            # Create sandbox with timeout
            sandbox = Sandbox(timeout=timeout)
            
            # Store sandbox reference
            self.active_sandboxes[execution_id] = sandbox
            self.sandbox_metadata[execution_id] = {
                "created_at": datetime.utcnow(),
                "timeout": timeout,
                "sandbox_id": sandbox.sandbox_id
            }
            
            # Install commonly needed packages
            await self._setup_sandbox_environment(sandbox)
            
            logger.info(f"Created E2B sandbox {sandbox.sandbox_id} for {execution_id}")
            return sandbox
            
        except Exception as e:
            logger.error(f"Failed to create E2B sandbox: {str(e)}")
            raise
    
    async def _setup_sandbox_environment(self, sandbox: Sandbox):
        """Set up the sandbox environment with common packages."""
        try:
            # Install commonly used packages
            setup_code = '''
import sys
import os
import json
import requests
import numpy as np
import pandas as pd
from datetime import datetime
import asyncio

# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("Sandbox environment ready")
'''
            await sandbox.notebook.exec_cell(setup_code)
            
        except Exception as e:
            logger.warning(f"Failed to setup sandbox environment: {str(e)}")
    
    async def _run_code_in_sandbox(
        self,
        sandbox: Sandbox,
        code: str
    ) -> Dict[str, Any]:
        """Execute code in the sandbox and return results."""
        try:
            # Execute the code
            execution = await sandbox.notebook.exec_cell(code)
            
            # Process results
            results = []
            logs = []
            
            for result in execution.results:
                if result.is_main_result:
                    if result.text:
                        results.append(result.text)
                    if result.html:
                        results.append({"html": result.html})
                    if result.png:
                        results.append({"image": result.png})
                    if result.svg:
                        results.append({"svg": result.svg})
                
                # Capture any errors
                if hasattr(result, 'error') and result.error:
                    logs.append(f"Error: {result.error}")
            
            # Capture stdout/stderr
            if execution.logs.stdout:
                logs.extend(execution.logs.stdout)
            if execution.logs.stderr:
                logs.extend(execution.logs.stderr)
            
            return {
                "results": results,
                "logs": logs,
                "execution_time": execution.execution_time,
                "success": len(results) > 0 or len(logs) == 0
            }
            
        except Exception as e:
            logger.error(f"Code execution failed: {str(e)}")
            return {
                "results": [],
                "logs": [f"Execution error: {str(e)}"],
                "execution_time": 0,
                "success": False,
                "error": str(e)
            }
    
    async def _get_sandbox_logs(self, sandbox: Sandbox) -> List[str]:
        """Retrieve logs from the sandbox."""
        try:
            # Get sandbox info and logs
            info = sandbox.get_info()
            logs = [f"Sandbox ID: {info.sandbox_id}"]
            
            # Add any available logs
            # Note: E2B logs are typically captured during execution
            return logs
            
        except Exception as e:
            logger.warning(f"Failed to get sandbox logs: {str(e)}")
            return []
    
    async def _cleanup_sandbox(self, execution_id: str):
        """Clean up a sandbox instance."""
        try:
            if execution_id in self.active_sandboxes:
                sandbox = self.active_sandboxes[execution_id]
                
                # Close the sandbox
                sandbox.close()
                
                # Remove from tracking
                del self.active_sandboxes[execution_id]
                del self.sandbox_metadata[execution_id]
                
                logger.info(f"Cleaned up sandbox for {execution_id}")
                
        except Exception as e:
            logger.error(f"Failed to cleanup sandbox {execution_id}: {str(e)}")
    
    async def get_active_count(self) -> int:
        """Get the number of active sandboxes."""
        return len(self.active_sandboxes)
    
    async def cleanup_idle(self) -> int:
        """Clean up idle sandboxes older than 10 minutes."""
        cleaned_count = 0
        cutoff_time = datetime.utcnow() - timedelta(minutes=10)
        
        idle_executions = []
        for execution_id, metadata in self.sandbox_metadata.items():
            if metadata["created_at"] < cutoff_time:
                idle_executions.append(execution_id)
        
        for execution_id in idle_executions:
            await self._cleanup_sandbox(execution_id)
            cleaned_count += 1
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} idle E2B sandboxes")
        
        return cleaned_count
    
    async def cleanup_all(self):
        """Clean up all active sandboxes."""
        execution_ids = list(self.active_sandboxes.keys())
        for execution_id in execution_ids:
            await self._cleanup_sandbox(execution_id)
        
        logger.info("Cleaned up all E2B sandboxes")
