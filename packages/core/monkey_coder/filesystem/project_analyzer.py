"""
Project analyzer for understanding code structure and dependencies.

Provides deep analysis of project structure, dependencies, and code patterns.
"""

import os
import json
import ast
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class CodeStats:
    """Statistics about code in a project."""
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    files_by_type: Dict[str, int]
    total_functions: int
    total_classes: int
    imports: List[str]
    complexity_score: float


@dataclass
class DependencyInfo:
    """Information about project dependencies."""
    name: str
    version: Optional[str]
    source: str  # "package.json", "requirements.txt", etc.
    is_dev: bool = False


class ProjectAnalyzer:
    """
    Analyzes project structure, dependencies, and code patterns.
    """
    
    def __init__(self, root_path: Path):
        """
        Initialize project analyzer.
        
        Args:
            root_path: Root path of the project
        """
        self.root_path = Path(root_path).resolve()
        self._cache = {}
    
    def detect_project_type(self) -> Dict[str, Any]:
        """
        Detect project type and configuration.
        
        Returns:
            Dictionary with project type information
        """
        result = {
            "type": "unknown",
            "language": None,
            "framework": None,
            "build_tool": None,
            "test_framework": None,
            "package_manager": None,
            "version_control": None,
        }
        
        # Check for version control
        if (self.root_path / ".git").exists():
            result["version_control"] = "git"
        elif (self.root_path / ".svn").exists():
            result["version_control"] = "svn"
        
        # Python projects
        if (self.root_path / "requirements.txt").exists():
            result["type"] = "python"
            result["language"] = "python"
            result["package_manager"] = "pip"
            
            # Detect Python framework
            if (self.root_path / "manage.py").exists():
                result["framework"] = "django"
            elif any((self.root_path / name).exists() for name in ["app.py", "application.py", "main.py"]):
                # Check for specific frameworks
                req_file = self.root_path / "requirements.txt"
                if req_file.exists():
                    content = req_file.read_text()
                    if "fastapi" in content.lower():
                        result["framework"] = "fastapi"
                    elif "flask" in content.lower():
                        result["framework"] = "flask"
                    elif "tornado" in content.lower():
                        result["framework"] = "tornado"
            
            # Check for test framework
            if (self.root_path / "pytest.ini").exists() or (self.root_path / "setup.cfg").exists():
                result["test_framework"] = "pytest"
        
        elif (self.root_path / "pyproject.toml").exists():
            result["type"] = "python"
            result["language"] = "python"
            result["package_manager"] = "poetry"
            result["build_tool"] = "poetry"
        
        elif (self.root_path / "Pipfile").exists():
            result["type"] = "python"
            result["language"] = "python"
            result["package_manager"] = "pipenv"
        
        # JavaScript/TypeScript projects
        elif (self.root_path / "package.json").exists():
            result["type"] = "node"
            result["language"] = "javascript"
            result["package_manager"] = "npm"
            
            # Check for yarn
            if (self.root_path / "yarn.lock").exists():
                result["package_manager"] = "yarn"
            elif (self.root_path / "pnpm-lock.yaml").exists():
                result["package_manager"] = "pnpm"
            
            # Check for TypeScript
            if (self.root_path / "tsconfig.json").exists():
                result["language"] = "typescript"
            
            # Detect framework
            try:
                with open(self.root_path / "package.json", 'r') as f:
                    package_data = json.load(f)
                    deps = package_data.get("dependencies", {})
                    dev_deps = package_data.get("devDependencies", {})
                    all_deps = {**deps, **dev_deps}
                    
                    # Framework detection
                    if "next" in all_deps:
                        result["framework"] = "nextjs"
                    elif "react" in all_deps:
                        result["framework"] = "react"
                    elif "vue" in all_deps:
                        result["framework"] = "vue"
                    elif "@angular/core" in all_deps:
                        result["framework"] = "angular"
                    elif "express" in all_deps:
                        result["framework"] = "express"
                    elif "fastify" in all_deps:
                        result["framework"] = "fastify"
                    elif "svelte" in all_deps:
                        result["framework"] = "svelte"
                    
                    # Test framework detection
                    if "jest" in all_deps:
                        result["test_framework"] = "jest"
                    elif "mocha" in all_deps:
                        result["test_framework"] = "mocha"
                    elif "vitest" in all_deps:
                        result["test_framework"] = "vitest"
                    
                    # Build tool detection
                    if "webpack" in all_deps:
                        result["build_tool"] = "webpack"
                    elif "vite" in all_deps:
                        result["build_tool"] = "vite"
                    elif "parcel" in all_deps:
                        result["build_tool"] = "parcel"
                    elif "rollup" in all_deps:
                        result["build_tool"] = "rollup"
            except:
                pass
        
        # Rust projects
        elif (self.root_path / "Cargo.toml").exists():
            result["type"] = "rust"
            result["language"] = "rust"
            result["package_manager"] = "cargo"
            result["build_tool"] = "cargo"
        
        # Go projects
        elif (self.root_path / "go.mod").exists():
            result["type"] = "go"
            result["language"] = "go"
            result["package_manager"] = "go modules"
            result["build_tool"] = "go"
        
        # Java projects
        elif (self.root_path / "pom.xml").exists():
            result["type"] = "java"
            result["language"] = "java"
            result["build_tool"] = "maven"
            result["package_manager"] = "maven"
        elif (self.root_path / "build.gradle").exists():
            result["type"] = "java"
            result["language"] = "java"
            result["build_tool"] = "gradle"
            result["package_manager"] = "gradle"
        
        # C++ projects
        elif (self.root_path / "CMakeLists.txt").exists():
            result["type"] = "cpp"
            result["language"] = "c++"
            result["build_tool"] = "cmake"
        
        return result
    
    def extract_dependencies(self) -> List[DependencyInfo]:
        """
        Extract project dependencies.
        
        Returns:
            List of dependency information
        """
        dependencies = []
        
        # Python dependencies
        if (self.root_path / "requirements.txt").exists():
            with open(self.root_path / "requirements.txt", 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Parse requirement (simple version)
                        match = re.match(r'^([^=<>!]+)([=<>!]+.*)?$', line)
                        if match:
                            name = match.group(1).strip()
                            version = match.group(2) if match.group(2) else None
                            dependencies.append(DependencyInfo(
                                name=name,
                                version=version,
                                source="requirements.txt",
                                is_dev=False
                            ))
        
        # Python pyproject.toml
        if (self.root_path / "pyproject.toml").exists():
            try:
                import toml
                with open(self.root_path / "pyproject.toml", 'r') as f:
                    data = toml.load(f)
                    
                    # Poetry dependencies
                    if "tool" in data and "poetry" in data["tool"]:
                        poetry = data["tool"]["poetry"]
                        
                        # Main dependencies
                        for name, version in poetry.get("dependencies", {}).items():
                            if name != "python":
                                dependencies.append(DependencyInfo(
                                    name=name,
                                    version=str(version) if version else None,
                                    source="pyproject.toml",
                                    is_dev=False
                                ))
                        
                        # Dev dependencies
                        for name, version in poetry.get("dev-dependencies", {}).items():
                            dependencies.append(DependencyInfo(
                                name=name,
                                version=str(version) if version else None,
                                source="pyproject.toml",
                                is_dev=True
                            ))
            except ImportError:
                logger.warning("toml library not available for parsing pyproject.toml")
        
        # JavaScript/TypeScript dependencies
        if (self.root_path / "package.json").exists():
            try:
                with open(self.root_path / "package.json", 'r') as f:
                    data = json.load(f)
                    
                    # Main dependencies
                    for name, version in data.get("dependencies", {}).items():
                        dependencies.append(DependencyInfo(
                            name=name,
                            version=version,
                            source="package.json",
                            is_dev=False
                        ))
                    
                    # Dev dependencies
                    for name, version in data.get("devDependencies", {}).items():
                        dependencies.append(DependencyInfo(
                            name=name,
                            version=version,
                            source="package.json",
                            is_dev=True
                        ))
            except:
                pass
        
        return dependencies
    
    def find_entry_points(self) -> List[Path]:
        """
        Find entry points in the project.
        
        Returns:
            List of entry point file paths
        """
        entry_points = []
        
        # Common entry point names
        common_entry_names = [
            "main.py", "app.py", "application.py", "run.py", "__main__.py",
            "index.js", "index.ts", "main.js", "main.ts", "app.js", "app.ts",
            "server.js", "server.ts", "index.html",
            "main.go", "main.rs", "Main.java", "main.c", "main.cpp",
        ]
        
        # Check root directory
        for name in common_entry_names:
            entry = self.root_path / name
            if entry.exists():
                entry_points.append(entry)
        
        # Check src directory
        src_dir = self.root_path / "src"
        if src_dir.exists():
            for name in common_entry_names:
                entry = src_dir / name
                if entry.exists():
                    entry_points.append(entry)
        
        # Check package.json for scripts
        package_json = self.root_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    
                    # Check main field
                    if "main" in data:
                        main_file = self.root_path / data["main"]
                        if main_file.exists():
                            entry_points.append(main_file)
                    
                    # Check scripts for start/dev commands
                    scripts = data.get("scripts", {})
                    for script_name in ["start", "dev", "serve"]:
                        if script_name in scripts:
                            # Try to extract file from script
                            script = scripts[script_name]
                            # Simple extraction (may not work for complex scripts)
                            words = script.split()
                            for word in words:
                                if word.endswith(('.js', '.ts')):
                                    script_file = self.root_path / word
                                    if script_file.exists():
                                        entry_points.append(script_file)
            except:
                pass
        
        # Remove duplicates
        entry_points = list(set(entry_points))
        
        return entry_points
    
    def get_code_stats(self, file_patterns: Optional[List[str]] = None) -> CodeStats:
        """
        Get statistics about code in the project.
        
        Args:
            file_patterns: Patterns of files to include (e.g., ["*.py", "*.js"])
            
        Returns:
            Code statistics
        """
        stats = {
            "total_lines": 0,
            "code_lines": 0,
            "comment_lines": 0,
            "blank_lines": 0,
            "files_by_type": defaultdict(int),
            "total_functions": 0,
            "total_classes": 0,
            "imports": set(),
        }
        
        # Default patterns if not specified
        if not file_patterns:
            file_patterns = [
                "*.py", "*.js", "*.ts", "*.jsx", "*.tsx",
                "*.java", "*.go", "*.rs", "*.c", "*.cpp", "*.h",
                "*.cs", "*.rb", "*.php", "*.swift", "*.kt",
            ]
        
        # Walk through project files
        for pattern in file_patterns:
            for file_path in self.root_path.rglob(pattern):
                # Skip common directories to ignore
                relative_path = file_path.relative_to(self.root_path)
                parts = relative_path.parts
                if any(part in ['node_modules', '__pycache__', '.git', 'venv', 'dist', 'build'] for part in parts):
                    continue
                
                # Get file extension
                ext = file_path.suffix
                stats["files_by_type"][ext] += 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                        for line in lines:
                            stripped = line.strip()
                            stats["total_lines"] += 1
                            
                            if not stripped:
                                stats["blank_lines"] += 1
                            elif self._is_comment(stripped, ext):
                                stats["comment_lines"] += 1
                            else:
                                stats["code_lines"] += 1
                        
                        # Language-specific analysis
                        if ext == ".py":
                            self._analyze_python_file(file_path, stats)
                        elif ext in [".js", ".ts", ".jsx", ".tsx"]:
                            self._analyze_javascript_file(file_path, stats)
                except:
                    # Skip files that can't be read
                    continue
        
        # Calculate complexity score (simple heuristic)
        complexity = 0.0
        if stats["code_lines"] > 0:
            # Based on functions, classes, and imports relative to code lines
            complexity = (
                (stats["total_functions"] * 2 + stats["total_classes"] * 3) /
                stats["code_lines"] * 100
            )
        
        return CodeStats(
            total_lines=stats["total_lines"],
            code_lines=stats["code_lines"],
            comment_lines=stats["comment_lines"],
            blank_lines=stats["blank_lines"],
            files_by_type=dict(stats["files_by_type"]),
            total_functions=stats["total_functions"],
            total_classes=stats["total_classes"],
            imports=list(stats["imports"]),
            complexity_score=complexity,
        )
    
    def _is_comment(self, line: str, ext: str) -> bool:
        """Check if a line is a comment."""
        comment_patterns = {
            ".py": ["#"],
            ".js": ["//", "/*", "*"],
            ".ts": ["//", "/*", "*"],
            ".jsx": ["//", "/*", "*"],
            ".tsx": ["//", "/*", "*"],
            ".java": ["//", "/*", "*"],
            ".c": ["//", "/*", "*"],
            ".cpp": ["//", "/*", "*"],
            ".go": ["//", "/*", "*"],
            ".rs": ["//", "/*", "*"],
            ".rb": ["#"],
            ".php": ["//", "/*", "*", "#"],
        }
        
        patterns = comment_patterns.get(ext, [])
        for pattern in patterns:
            if line.startswith(pattern):
                return True
        return False
    
    def _analyze_python_file(self, file_path: Path, stats: Dict):
        """Analyze a Python file for functions, classes, and imports."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                        stats["total_functions"] += 1
                    elif isinstance(node, ast.ClassDef):
                        stats["total_classes"] += 1
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            stats["imports"].add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            stats["imports"].add(node.module.split('.')[0])
        except:
            # Skip files that can't be parsed
            pass
    
    def _analyze_javascript_file(self, file_path: Path, stats: Dict):
        """Analyze a JavaScript/TypeScript file for functions and imports."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Count functions (simple regex-based)
                function_patterns = [
                    r'function\s+\w+\s*\(',
                    r'const\s+\w+\s*=\s*\([^)]*\)\s*=>',
                    r'let\s+\w+\s*=\s*\([^)]*\)\s*=>',
                    r'var\s+\w+\s*=\s*function\s*\(',
                ]
                for pattern in function_patterns:
                    stats["total_functions"] += len(re.findall(pattern, content))
                
                # Count classes
                class_pattern = r'class\s+\w+\s*[{<]'
                stats["total_classes"] += len(re.findall(class_pattern, content))
                
                # Extract imports
                import_patterns = [
                    r'import\s+.*?\s+from\s+[\'"]([^\'"]]+)[\'"]',
                    r'require\s*\([\'"]([^\'"]]+)[\'"]\)',
                ]
                for pattern in import_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # Extract package name
                        package = match.split('/')[0]
                        if not package.startswith('.'):
                            stats["imports"].add(package)
        except:
            # Skip files that can't be analyzed
            pass


# Convenience functions
def detect_project_type(root_path: Path) -> Dict[str, Any]:
    """Detect project type and configuration."""
    analyzer = ProjectAnalyzer(root_path)
    return analyzer.detect_project_type()


def extract_dependencies(root_path: Path) -> List[DependencyInfo]:
    """Extract project dependencies."""
    analyzer = ProjectAnalyzer(root_path)
    return analyzer.extract_dependencies()


def find_entry_points(root_path: Path) -> List[Path]:
    """Find entry points in the project."""
    analyzer = ProjectAnalyzer(root_path)
    return analyzer.find_entry_points()


def get_code_stats(root_path: Path, file_patterns: Optional[List[str]] = None) -> CodeStats:
    """Get code statistics for the project."""
    analyzer = ProjectAnalyzer(root_path)
    return analyzer.get_code_stats(file_patterns)