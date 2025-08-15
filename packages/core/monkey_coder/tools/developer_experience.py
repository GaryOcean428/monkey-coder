"""
Enhanced Developer Experience Tools
===================================

Advanced tooling for developer productivity, including intelligent
code generation, automated testing, and comprehensive validation.
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
import tempfile
import shutil

logger = logging.getLogger(__name__)

class TestFramework(Enum):
    """Supported testing frameworks."""
    JEST = "jest"
    PYTEST = "pytest"
    MOCHA = "mocha"
    VITEST = "vitest"
    CYPRESS = "cypress"
    PLAYWRIGHT = "playwright"

class CodeQuality(Enum):
    """Code quality assessment levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

@dataclass
class DevelopmentTask:
    """Development task definition."""
    task_id: str
    title: str
    description: str
    priority: int
    estimated_hours: float
    dependencies: List[str]
    tags: List[str]
    assignee: Optional[str] = None
    status: str = "todo"  # todo, in_progress, review, done
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class CodeAnalysisResult:
    """Result of code analysis."""
    file_path: str
    language: str
    lines_of_code: int
    complexity_score: float
    quality_rating: CodeQuality
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    test_coverage: Optional[float] = None
    performance_score: Optional[float] = None

@dataclass
class TestResult:
    """Test execution result."""
    framework: TestFramework
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    duration_seconds: float
    coverage_percent: Optional[float]
    failed_test_details: List[Dict[str, Any]]

class IntelligentCodeGenerator:
    """AI-powered code generation system."""
    
    def __init__(self):
        self._templates = {}
        self._patterns = {}
        self._quality_rules = []
    
    async def generate_code(self, specification: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on specification."""
        prompt = self._build_prompt(specification)
        
        # This would integrate with AI services
        generated_code = await self._call_ai_service(prompt)
        
        # Validate and improve generated code
        validated_code = await self._validate_generated_code(generated_code, specification)
        
        return {
            'code': validated_code,
            'language': specification.get('language', 'python'),
            'framework': specification.get('framework'),
            'tests': await self._generate_tests(validated_code, specification),
            'documentation': await self._generate_documentation(validated_code, specification)
        }
    
    def _build_prompt(self, specification: Dict[str, Any]) -> str:
        """Build AI prompt from specification."""
        language = specification.get('language', 'python')
        framework = specification.get('framework', '')
        functionality = specification.get('functionality', '')
        requirements = specification.get('requirements', [])
        
        prompt = f"""
Generate high-quality {language} code for the following specification:

Functionality: {functionality}
Framework: {framework}
Requirements:
{chr(10).join(f"- {req}" for req in requirements)}

Please ensure the code follows these standards:
- Clean, readable code with proper comments
- Error handling and input validation
- Type hints (for Python) or proper typing
- Modular design with clear separation of concerns
- Performance optimizations where applicable
- Security best practices
- Comprehensive test coverage

Generated code should be production-ready and follow industry best practices.
"""
        return prompt
    
    async def _call_ai_service(self, prompt: str) -> str:
        """Call AI service for code generation."""
        # This would integrate with actual AI services like OpenAI, Anthropic, etc.
        # For now, return a placeholder
        return f"# Generated code based on prompt:\n# {prompt[:100]}...\n\ndef placeholder_function():\n    pass"
    
    async def _validate_generated_code(self, code: str, specification: Dict[str, Any]) -> str:
        """Validate and improve generated code."""
        language = specification.get('language', 'python')
        
        # Basic validation
        if not code.strip():
            raise ValueError("Generated code is empty")
        
        # Language-specific validation
        if language == 'python':
            return await self._validate_python_code(code)
        elif language in ['javascript', 'typescript']:
            return await self._validate_js_code(code)
        
        return code
    
    async def _validate_python_code(self, code: str) -> str:
        """Validate Python code."""
        try:
            # Check syntax
            compile(code, '<string>', 'exec')
            
            # Add improvements
            improved_code = self._add_python_improvements(code)
            return improved_code
        except SyntaxError as e:
            logger.error(f"Generated Python code has syntax error: {e}")
            # Try to fix common issues
            return self._fix_python_syntax(code)
    
    async def _validate_js_code(self, code: str) -> str:
        """Validate JavaScript/TypeScript code."""
        # This would use tools like ESLint, TypeScript compiler, etc.
        return code
    
    def _add_python_improvements(self, code: str) -> str:
        """Add improvements to Python code."""
        lines = code.split('\n')
        improved_lines = []
        
        for line in lines:
            # Add type hints if missing
            if 'def ' in line and '->' not in line and line.strip().endswith(':'):
                # Basic type hint addition (would be more sophisticated in practice)
                if '(' in line and ')' in line:
                    line = line.replace('):', ') -> Any:')
            
            improved_lines.append(line)
        
        return '\n'.join(improved_lines)
    
    def _fix_python_syntax(self, code: str) -> str:
        """Attempt to fix common Python syntax errors."""
        # Basic fixes - in practice this would be more sophisticated
        fixed_code = code.replace('\t', '    ')  # Replace tabs with spaces
        return fixed_code
    
    async def _generate_tests(self, code: str, specification: Dict[str, Any]) -> str:
        """Generate test code for the main code."""
        language = specification.get('language', 'python')
        
        if language == 'python':
            return await self._generate_python_tests(code, specification)
        elif language in ['javascript', 'typescript']:
            return await self._generate_js_tests(code, specification)
        
        return "# Tests not generated for this language"
    
    async def _generate_python_tests(self, code: str, specification: Dict[str, Any]) -> str:
        """Generate Python tests using pytest."""
        # Extract function names from code
        import re
        functions = re.findall(r'def (\w+)\(', code)
        
        test_code = "import pytest\nfrom your_module import " + ", ".join(functions) + "\n\n"
        
        for func in functions:
            test_code += f"""
def test_{func}_basic():
    \"\"\"Test basic functionality of {func}.\"\"\"
    # TODO: Add proper test cases
    result = {func}()
    assert result is not None

def test_{func}_edge_cases():
    \"\"\"Test edge cases for {func}.\"\"\"
    # TODO: Add edge case tests
    pass

"""
        
        return test_code
    
    async def _generate_js_tests(self, code: str, specification: Dict[str, Any]) -> str:
        """Generate JavaScript/TypeScript tests."""
        # Similar to Python test generation but for JS/TS
        return "// Jest tests would be generated here"
    
    async def _generate_documentation(self, code: str, specification: Dict[str, Any]) -> str:
        """Generate documentation for the code."""
        functionality = specification.get('functionality', 'Generated code')
        
        doc = f"""
# {functionality}

## Overview

This module provides {functionality.lower()}.

## Usage

```python
# Example usage
from your_module import your_function

result = your_function()
```

## Functions

{self._extract_function_docs(code)}

## Requirements

- Python 3.8+
- Required dependencies (see requirements.txt)

## Testing

Run tests with:
```bash
pytest tests/
```
"""
        return doc
    
    def _extract_function_docs(self, code: str) -> str:
        """Extract function documentation from code."""
        import re
        functions = re.findall(r'def (\w+)\([^)]*\):', code)
        
        docs = ""
        for func in functions:
            docs += f"### {func}()\n\nDescription of {func} function.\n\n"
        
        return docs

class AutomatedTestRunner:
    """Automated test execution and reporting system."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self._test_history: List[TestResult] = []
    
    async def run_tests(self, framework: TestFramework, 
                       test_pattern: Optional[str] = None) -> TestResult:
        """Run tests using specified framework."""
        start_time = time.time()
        
        try:
            if framework == TestFramework.JEST:
                result = await self._run_jest_tests(test_pattern)
            elif framework == TestFramework.PYTEST:
                result = await self._run_pytest_tests(test_pattern)
            elif framework == TestFramework.PLAYWRIGHT:
                result = await self._run_playwright_tests(test_pattern)
            else:
                raise ValueError(f"Unsupported test framework: {framework}")
            
            result.duration_seconds = time.time() - start_time
            self._test_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            # Return failed result
            return TestResult(
                framework=framework,
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                skipped_tests=0,
                duration_seconds=time.time() - start_time,
                coverage_percent=None,
                failed_test_details=[{"error": str(e)}]
            )
    
    async def _run_jest_tests(self, pattern: Optional[str]) -> TestResult:
        """Run Jest tests."""
        cmd = ["npx", "jest", "--json"]
        if pattern:
            cmd.append(pattern)
        
        result = await self._execute_command(cmd)
        return self._parse_jest_result(result)
    
    async def _run_pytest_tests(self, pattern: Optional[str]) -> TestResult:
        """Run pytest tests."""
        cmd = ["python", "-m", "pytest", "--json-report", "--json-report-file=/tmp/pytest_report.json"]
        if pattern:
            cmd.append(pattern)
        
        result = await self._execute_command(cmd)
        return self._parse_pytest_result(result)
    
    async def _run_playwright_tests(self, pattern: Optional[str]) -> TestResult:
        """Run Playwright tests."""
        cmd = ["npx", "playwright", "test", "--reporter=json"]
        if pattern:
            cmd.append(pattern)
        
        result = await self._execute_command(cmd)
        return self._parse_playwright_result(result)
    
    async def _execute_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Execute command and return result."""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.project_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=process.returncode,
            stdout=stdout.decode(),
            stderr=stderr.decode()
        )
    
    def _parse_jest_result(self, result: subprocess.CompletedProcess) -> TestResult:
        """Parse Jest test results."""
        try:
            data = json.loads(result.stdout)
            return TestResult(
                framework=TestFramework.JEST,
                total_tests=data.get('numTotalTests', 0),
                passed_tests=data.get('numPassedTests', 0),
                failed_tests=data.get('numFailedTests', 0),
                skipped_tests=data.get('numPendingTests', 0),
                duration_seconds=0,  # Will be set by caller
                coverage_percent=self._extract_coverage_from_jest(data),
                failed_test_details=self._extract_failed_tests_jest(data)
            )
        except json.JSONDecodeError:
            logger.error(f"Failed to parse Jest results: {result.stdout}")
            return self._create_error_result(TestFramework.JEST)
    
    def _parse_pytest_result(self, result: subprocess.CompletedProcess) -> TestResult:
        """Parse pytest test results."""
        try:
            with open('/tmp/pytest_report.json', 'r') as f:
                data = json.load(f)
            
            summary = data.get('summary', {})
            return TestResult(
                framework=TestFramework.PYTEST,
                total_tests=summary.get('total', 0),
                passed_tests=summary.get('passed', 0),
                failed_tests=summary.get('failed', 0),
                skipped_tests=summary.get('skipped', 0),
                duration_seconds=0,  # Will be set by caller
                coverage_percent=None,  # Would need separate coverage run
                failed_test_details=self._extract_failed_tests_pytest(data)
            )
        except (FileNotFoundError, json.JSONDecodeError):
            logger.error(f"Failed to parse pytest results")
            return self._create_error_result(TestFramework.PYTEST)
    
    def _parse_playwright_result(self, result: subprocess.CompletedProcess) -> TestResult:
        """Parse Playwright test results."""
        # Similar to Jest parsing but for Playwright format
        return self._create_error_result(TestFramework.PLAYWRIGHT)
    
    def _extract_coverage_from_jest(self, data: Dict[str, Any]) -> Optional[float]:
        """Extract coverage percentage from Jest results."""
        coverage = data.get('coverageMap')
        if coverage:
            # Calculate overall coverage percentage
            total_lines = sum(len(file_data.get('statementMap', {})) for file_data in coverage.values())
            covered_lines = sum(
                sum(1 for count in file_data.get('s', {}).values() if count > 0)
                for file_data in coverage.values()
            )
            return (covered_lines / total_lines * 100) if total_lines > 0 else 0
        return None
    
    def _extract_failed_tests_jest(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract failed test details from Jest results."""
        failed_tests = []
        test_results = data.get('testResults', [])
        
        for test_file in test_results:
            for assertion in test_file.get('assertionResults', []):
                if assertion.get('status') == 'failed':
                    failed_tests.append({
                        'test_name': assertion.get('title'),
                        'file': test_file.get('name'),
                        'error': assertion.get('failureMessages', ['Unknown error'])[0]
                    })
        
        return failed_tests
    
    def _extract_failed_tests_pytest(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract failed test details from pytest results."""
        failed_tests = []
        tests = data.get('tests', [])
        
        for test in tests:
            if test.get('outcome') == 'failed':
                failed_tests.append({
                    'test_name': test.get('nodeid'),
                    'file': test.get('setup', {}).get('file'),
                    'error': test.get('call', {}).get('longrepr', 'Unknown error')
                })
        
        return failed_tests
    
    def _create_error_result(self, framework: TestFramework) -> TestResult:
        """Create error test result."""
        return TestResult(
            framework=framework,
            total_tests=0,
            passed_tests=0,
            failed_tests=1,
            skipped_tests=0,
            duration_seconds=0,
            coverage_percent=None,
            failed_test_details=[{"error": "Test execution failed"}]
        )
    
    def get_test_history(self, limit: int = 10) -> List[TestResult]:
        """Get recent test history."""
        return self._test_history[-limit:]
    
    def get_test_trends(self) -> Dict[str, Any]:
        """Analyze test trends over time."""
        if not self._test_history:
            return {"message": "No test history available"}
        
        recent_results = self._test_history[-10:]  # Last 10 runs
        
        success_rates = [
            (r.passed_tests / r.total_tests * 100) if r.total_tests > 0 else 0
            for r in recent_results
        ]
        
        return {
            'avg_success_rate': sum(success_rates) / len(success_rates),
            'trend': 'improving' if success_rates[-1] > success_rates[0] else 'declining',
            'total_runs': len(self._test_history),
            'avg_duration': sum(r.duration_seconds for r in recent_results) / len(recent_results)
        }

class CodeQualityAnalyzer:
    """Advanced code quality analysis system."""
    
    def __init__(self):
        self._quality_rules = []
        self._analysis_cache = {}
    
    async def analyze_code(self, file_path: str, code_content: str) -> CodeAnalysisResult:
        """Analyze code quality comprehensively."""
        language = self._detect_language(file_path)
        
        # Basic metrics
        lines_of_code = len([line for line in code_content.split('\n') if line.strip()])
        complexity_score = await self._calculate_complexity(code_content, language)
        
        # Quality assessment
        issues = await self._find_issues(code_content, language)
        suggestions = await self._generate_suggestions(code_content, language, issues)
        quality_rating = self._assess_quality(complexity_score, issues)
        
        # Performance analysis
        performance_score = await self._analyze_performance(code_content, language)
        
        return CodeAnalysisResult(
            file_path=file_path,
            language=language,
            lines_of_code=lines_of_code,
            complexity_score=complexity_score,
            quality_rating=quality_rating,
            issues=issues,
            suggestions=suggestions,
            performance_score=performance_score
        )
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        extension = Path(file_path).suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby'
        }
        
        return language_map.get(extension, 'unknown')
    
    async def _calculate_complexity(self, code: str, language: str) -> float:
        """Calculate cyclomatic complexity."""
        if language == 'python':
            return self._calculate_python_complexity(code)
        elif language in ['javascript', 'typescript']:
            return self._calculate_js_complexity(code)
        
        # Basic complexity calculation for other languages
        complexity_keywords = ['if', 'for', 'while', 'switch', 'case', 'catch', 'except']
        lines = code.lower().split('\n')
        complexity = 1  # Base complexity
        
        for line in lines:
            for keyword in complexity_keywords:
                if keyword in line:
                    complexity += 1
        
        return complexity
    
    def _calculate_python_complexity(self, code: str) -> float:
        """Calculate Python-specific complexity."""
        import ast
        try:
            tree = ast.parse(code)
            complexity = 1
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
            
            return complexity
        except SyntaxError:
            return 0  # Invalid syntax
    
    def _calculate_js_complexity(self, code: str) -> float:
        """Calculate JavaScript/TypeScript complexity."""
        # Simplified complexity calculation
        complexity_patterns = [
            r'\bif\s*\(',
            r'\bfor\s*\(',
            r'\bwhile\s*\(',
            r'\bswitch\s*\(',
            r'\bcatch\s*\(',
            r'\b&&\b',
            r'\b\|\|\b'
        ]
        
        import re
        complexity = 1
        
        for pattern in complexity_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            complexity += len(matches)
        
        return complexity
    
    async def _find_issues(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Find code quality issues."""
        issues = []
        
        if language == 'python':
            issues.extend(self._find_python_issues(code))
        elif language in ['javascript', 'typescript']:
            issues.extend(self._find_js_issues(code))
        
        # Common issues for all languages
        issues.extend(self._find_common_issues(code))
        
        return issues
    
    def _find_python_issues(self, code: str) -> List[Dict[str, Any]]:
        """Find Python-specific issues."""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Long lines
            if len(line) > 88:  # PEP 8 recommends 79, but 88 is common
                issues.append({
                    'type': 'style',
                    'severity': 'minor',
                    'line': i,
                    'message': f'Line too long ({len(line)} > 88 characters)',
                    'rule': 'line-length'
                })
            
            # Missing docstrings for functions
            if line.strip().startswith('def ') and not any('"""' in lines[j] or "'''" in lines[j] for j in range(i, min(i+3, len(lines)))):
                issues.append({
                    'type': 'documentation',
                    'severity': 'minor',
                    'line': i,
                    'message': 'Function missing docstring',
                    'rule': 'missing-docstring'
                })
        
        return issues
    
    def _find_js_issues(self, code: str) -> List[Dict[str, Any]]:
        """Find JavaScript/TypeScript-specific issues."""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Missing semicolons (basic check)
            stripped = line.strip()
            if stripped and not stripped.endswith((';', '{', '}', ')', ']')) and not stripped.startswith(('if', 'for', 'while', 'function', 'class')):
                if any(stripped.endswith(ending) for ending in [')', ']', '`', '"', "'"]) and not stripped.endswith('};'):
                    issues.append({
                        'type': 'style',
                        'severity': 'minor',
                        'line': i,
                        'message': 'Missing semicolon',
                        'rule': 'missing-semicolon'
                    })
        
        return issues
    
    def _find_common_issues(self, code: str) -> List[Dict[str, Any]]:
        """Find common issues across all languages."""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # TODO comments
            if 'TODO' in line.upper():
                issues.append({
                    'type': 'maintenance',
                    'severity': 'info',
                    'line': i,
                    'message': 'TODO comment found',
                    'rule': 'todo-comment'
                })
            
            # Hardcoded passwords or keys (basic check)
            if any(keyword in line.lower() for keyword in ['password', 'secret', 'key', 'token']) and '=' in line:
                issues.append({
                    'type': 'security',
                    'severity': 'major',
                    'line': i,
                    'message': 'Potential hardcoded credential',
                    'rule': 'hardcoded-credential'
                })
        
        return issues
    
    async def _generate_suggestions(self, code: str, language: str, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        
        # Based on issues found
        issue_counts = {}
        for issue in issues:
            issue_type = issue['rule']
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        if issue_counts.get('line-length', 0) > 5:
            suggestions.append("Consider breaking long lines for better readability")
        
        if issue_counts.get('missing-docstring', 0) > 0:
            suggestions.append("Add docstrings to improve code documentation")
        
        if issue_counts.get('hardcoded-credential', 0) > 0:
            suggestions.append("Move credentials to environment variables or secure storage")
        
        # General suggestions based on language
        if language == 'python':
            suggestions.append("Consider using type hints for better code clarity")
            suggestions.append("Follow PEP 8 style guidelines")
        elif language in ['javascript', 'typescript']:
            suggestions.append("Consider using ESLint for consistent code style")
            suggestions.append("Add JSDoc comments for better documentation")
        
        return suggestions
    
    def _assess_quality(self, complexity_score: float, issues: List[Dict[str, Any]]) -> CodeQuality:
        """Assess overall code quality."""
        # Calculate quality score
        score = 100
        
        # Penalize based on complexity
        if complexity_score > 20:
            score -= 30
        elif complexity_score > 10:
            score -= 15
        elif complexity_score > 5:
            score -= 5
        
        # Penalize based on issues
        for issue in issues:
            severity = issue.get('severity', 'minor')
            if severity == 'major':
                score -= 10
            elif severity == 'minor':
                score -= 3
            elif severity == 'info':
                score -= 1
        
        # Determine quality rating
        if score >= 90:
            return CodeQuality.EXCELLENT
        elif score >= 75:
            return CodeQuality.GOOD
        elif score >= 50:
            return CodeQuality.FAIR
        elif score >= 25:
            return CodeQuality.POOR
        else:
            return CodeQuality.CRITICAL
    
    async def _analyze_performance(self, code: str, language: str) -> Optional[float]:
        """Analyze code performance characteristics."""
        # This would be enhanced with actual performance analysis tools
        # For now, return a basic heuristic score
        
        performance_score = 100.0
        
        # Check for common performance anti-patterns
        if 'nested loop' in code.lower() or ('for' in code and 'for' in code):
            performance_score -= 20
        
        if 'sql' in code.lower() and 'select * from' in code.lower():
            performance_score -= 15
        
        if language == 'python' and 'print(' in code:
            performance_score -= 5  # Console output can be slow
        
        return max(0, performance_score)

# Global instances
_code_generator: Optional[IntelligentCodeGenerator] = None
_quality_analyzer: Optional[CodeQualityAnalyzer] = None

def get_code_generator() -> IntelligentCodeGenerator:
    """Get global code generator instance."""
    global _code_generator
    if _code_generator is None:
        _code_generator = IntelligentCodeGenerator()
    return _code_generator

def get_quality_analyzer() -> CodeQualityAnalyzer:
    """Get global quality analyzer instance."""
    global _quality_analyzer
    if _quality_analyzer is None:
        _quality_analyzer = CodeQualityAnalyzer()
    return _quality_analyzer