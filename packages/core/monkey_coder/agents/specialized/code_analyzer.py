"""
Code Analyzer Agent - Specialized in analyzing code structure and quality
Uses quantum execution for comprehensive analysis approaches
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base_agent import BaseAgent, AgentCapability, AgentContext

logger = logging.getLogger(__name__)


class CodeAnalyzerAgent(BaseAgent):
    """
    Specialized agent for code analysis tasks
    Analyzes code structure, quality, and provides improvement recommendations
    """
    
    def __init__(self, provider_registry=None):
        super().__init__(
            name="CodeAnalyzer",
            capabilities={
                AgentCapability.CODE_ANALYSIS,
                AgentCapability.CODE_REVIEW,
                AgentCapability.ARCHITECTURE_DESIGN,
                AgentCapability.SECURITY_ANALYSIS,
                AgentCapability.PERFORMANCE_OPTIMIZATION
            }
        )
        self.provider_registry = provider_registry
        
    async def _setup(self):
        """Initialize agent-specific resources"""
        logger.info("Code analyzer agent initialized")
        
    async def process(self, task: str, context: AgentContext, **kwargs) -> Dict[str, Any]:
        """
        Process code analysis task
        
        Args:
            task: Analysis task description
            context: Agent context with files and metadata
            **kwargs: Additional parameters for variation
            
        Returns:
            Analysis results and recommendations
        """
        start_time = datetime.now()
        
        # Extract parameters
        analysis_type = kwargs.get("analysis_type", "comprehensive")
        include_suggestions = kwargs.get("include_suggestions", True)
        
        # Analyze based on type
        if analysis_type == "structure":
            result = await self._analyze_structure(task, context)
        elif analysis_type == "issues":
            result = await self._analyze_issues(task, context)
        elif analysis_type == "improvements":
            result = await self._analyze_improvements(task, context)
        else:
            result = await self._comprehensive_analysis(task, context)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "analysis": result,
            "metadata": {
                "analysis_type": analysis_type,
                "execution_time": execution_time,
                "agent": self.name,
                "timestamp": start_time.isoformat()
            }
        }
    
    def get_quantum_variations(self, task: str, context: AgentContext) -> List[Dict[str, Any]]:
        """Generate quantum variations for analysis approaches"""
        return [
            {
                "id": "structural_analysis",
                "params": {"analysis_type": "structure", "focus": "architecture"}
            },
            {
                "id": "quality_analysis", 
                "params": {"analysis_type": "issues", "focus": "quality"}
            },
            {
                "id": "improvement_analysis",
                "params": {"analysis_type": "improvements", "focus": "optimization"}
            }
        ]
    
    async def _analyze_structure(self, task: str, context: AgentContext) -> str:
        """Analyze code structure and architecture"""
        analysis = []
        
        analysis.append("# Code Structure Analysis")
        analysis.append("="*50)
        
        # Analyze workspace structure if available
        if context.workspace_path:
            analysis.append(f"\n## Workspace: {context.workspace_path}")
            
        # Analyze files in context
        if context.files:
            analysis.append(f"\n## Files Analyzed: {len(context.files)}")
            for filename, content in context.files.items():
                analysis.append(f"\n### {filename}")
                analysis.append(f"- Lines of code: {len(content.splitlines())}")
                analysis.append(f"- File size: {len(content)} characters")
                
                # Basic structure analysis
                if filename.endswith('.py'):
                    analysis.extend(self._analyze_python_structure(content))
                elif filename.endswith(('.js', '.ts')):
                    analysis.extend(self._analyze_javascript_structure(content))
                
        # MCP structure analysis if available
        if "repo_structure" in context.metadata:
            analysis.append(f"\n## Repository Structure")
            analysis.append(context.metadata["repo_structure"])
            
        return "\n".join(analysis)
    
    async def _analyze_issues(self, task: str, context: AgentContext) -> str:
        """Analyze potential issues and problems"""
        issues = []
        
        issues.append("# Code Issues Analysis")
        issues.append("="*50)
        
        issue_count = 0
        
        # Analyze files for common issues
        if context.files:
            for filename, content in context.files.items():
                file_issues = []
                
                if filename.endswith('.py'):
                    file_issues.extend(self._check_python_issues(content))
                elif filename.endswith(('.js', '.ts')):
                    file_issues.extend(self._check_javascript_issues(content))
                
                if file_issues:
                    issues.append(f"\n## Issues in {filename}:")
                    issues.extend(file_issues)
                    issue_count += len(file_issues)
        
        if issue_count == 0:
            issues.append("\n✅ No obvious issues detected in the analyzed code.")
        else:
            issues.append(f"\n⚠️ Total issues found: {issue_count}")
            
        return "\n".join(issues)
    
    async def _analyze_improvements(self, task: str, context: AgentContext) -> str:
        """Analyze potential improvements and optimizations"""
        improvements = []
        
        improvements.append("# Code Improvement Recommendations")
        improvements.append("="*50)
        
        # General improvement suggestions
        if context.files:
            for filename, content in context.files.items():
                suggestions = []
                
                if filename.endswith('.py'):
                    suggestions.extend(self._suggest_python_improvements(content))
                elif filename.endswith(('.js', '.ts')):
                    suggestions.extend(self._suggest_javascript_improvements(content))
                
                if suggestions:
                    improvements.append(f"\n## Improvements for {filename}:")
                    improvements.extend(suggestions)
        
        # Architecture improvements
        improvements.append("\n## Architecture Recommendations:")
        improvements.append("- Consider implementing dependency injection for better testability")
        improvements.append("- Add comprehensive error handling and logging")
        improvements.append("- Implement proper configuration management")
        improvements.append("- Consider adding monitoring and observability")
        
        return "\n".join(improvements)
    
    async def _comprehensive_analysis(self, task: str, context: AgentContext) -> str:
        """Perform comprehensive analysis combining all aspects"""
        results = []
        
        results.append("# Comprehensive Code Analysis")
        results.append("="*50)
        
        # Structure analysis
        structure = await self._analyze_structure(task, context)
        results.append(structure)
        
        results.append("\n" + "="*50)
        
        # Issues analysis
        issues = await self._analyze_issues(task, context)
        results.append(issues)
        
        results.append("\n" + "="*50)
        
        # Improvements analysis
        improvements = await self._analyze_improvements(task, context)
        results.append(improvements)
        
        results.append("\n" + "="*50)
        results.append("# Summary")
        results.append("Analysis completed successfully. Review the sections above for detailed insights.")
        
        return "\n".join(results)
    
    def _analyze_python_structure(self, content: str) -> List[str]:
        """Analyze Python file structure"""
        analysis = []
        lines = content.splitlines()
        
        # Count different elements
        imports = len([l for l in lines if l.strip().startswith(('import ', 'from '))])
        classes = len([l for l in lines if l.strip().startswith('class ')])
        functions = len([l for l in lines if l.strip().startswith('def ')])
        
        analysis.append(f"- Imports: {imports}")
        analysis.append(f"- Classes: {classes}")
        analysis.append(f"- Functions: {functions}")
        
        return analysis
    
    def _analyze_javascript_structure(self, content: str) -> List[str]:
        """Analyze JavaScript/TypeScript file structure"""
        analysis = []
        lines = content.splitlines()
        
        # Count different elements
        imports = len([l for l in lines if 'import ' in l or 'require(' in l])
        functions = len([l for l in lines if 'function ' in l or '=>' in l])
        classes = len([l for l in lines if 'class ' in l])
        
        analysis.append(f"- Imports/Requires: {imports}")
        analysis.append(f"- Functions: {functions}")
        analysis.append(f"- Classes: {classes}")
        
        return analysis
    
    def _check_python_issues(self, content: str) -> List[str]:
        """Check for common Python issues"""
        issues = []
        lines = content.splitlines()
        
        # Check for common issues
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Long lines
            if len(line) > 120:
                issues.append(f"- Line {i}: Line too long ({len(line)} characters)")
            
            # TODO comments
            if 'TODO' in stripped or 'FIXME' in stripped:
                issues.append(f"- Line {i}: TODO/FIXME comment found")
            
            # Bare except
            if stripped == 'except:':
                issues.append(f"- Line {i}: Bare except clause (should specify exception type)")
                
        return issues
    
    def _check_javascript_issues(self, content: str) -> List[str]:
        """Check for common JavaScript issues"""
        issues = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Long lines
            if len(line) > 120:
                issues.append(f"- Line {i}: Line too long ({len(line)} characters)")
            
            # TODO comments
            if 'TODO' in stripped or 'FIXME' in stripped:
                issues.append(f"- Line {i}: TODO/FIXME comment found")
            
            # Console.log (should use proper logging)
            if 'console.log' in stripped:
                issues.append(f"- Line {i}: console.log found (consider using proper logging)")
                
        return issues
    
    def _suggest_python_improvements(self, content: str) -> List[str]:
        """Suggest Python-specific improvements"""
        suggestions = []
        
        # Check for type hints
        if 'def ' in content and '->' not in content:
            suggestions.append("- Add type hints for better code documentation and IDE support")
        
        # Check for docstrings
        if 'def ' in content and '"""' not in content and "'''" not in content:
            suggestions.append("- Add docstrings to functions and classes")
        
        # Check for error handling
        if 'def ' in content and 'try:' not in content:
            suggestions.append("- Consider adding error handling with try/except blocks")
        
        return suggestions
    
    def _suggest_javascript_improvements(self, content: str) -> List[str]:
        """Suggest JavaScript/TypeScript-specific improvements"""
        suggestions = []
        
        # Check for TypeScript
        if '.js' in content and 'any' not in content:
            suggestions.append("- Consider migrating to TypeScript for better type safety")
        
        # Check for async/await
        if 'Promise' in content and 'async' not in content:
            suggestions.append("- Consider using async/await for better promise handling")
        
        # Check for error handling
        if 'function' in content and 'catch' not in content:
            suggestions.append("- Add proper error handling with try/catch blocks")
        
        return suggestions