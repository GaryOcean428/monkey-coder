"""
Comprehensive File I/O Operations Module for Quantum Routing System

This module provides safe file operations including reading, writing,
project structure analysis, AST manipulation, and file watching capabilities.
"""

import ast
import json
import logging
import os
import shutil
import tempfile
import threading
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union
import yaml

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = object

logger = logging.getLogger(__name__)


class FileType(Enum):
    """Supported file types."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JSON = "json"
    YAML = "yaml"
    TEXT = "text"
    UNKNOWN = "unknown"


@dataclass
class FileInfo:
    """Information about a file."""
    path: Path
    type: FileType
    size: int
    lines: int
    encoding: str = "utf-8"
    is_binary: bool = False


class SecurityError(Exception):
    """Raised when a security violation is detected."""
    pass


class FileOperationsManager:
    """
    Manages file operations with safety, atomic writes, and monitoring.
    """
    
    def __init__(self, root_path: Optional[Path] = None):
        """
        Initialize the file operations manager.
        
        Args:
            root_path: Root directory for operations (prevents traversal outside)
        """
        self.root_path = Path(root_path) if root_path else Path.cwd()
        self.watchers: Dict[str, Observer] = {}
        self._lock = threading.Lock()
        
        # File type mappings
        self.extensions = {
            '.py': FileType.PYTHON,
            '.js': FileType.JAVASCRIPT,
            '.mjs': FileType.JAVASCRIPT,
            '.jsx': FileType.JAVASCRIPT,
            '.ts': FileType.TYPESCRIPT,
            '.tsx': FileType.TYPESCRIPT,
            '.json': FileType.JSON,
            '.yaml': FileType.YAML,
            '.yml': FileType.YAML,
        }
        
        logger.info(f"Initialized FileOperationsManager with root: {self.root_path}")

    def _validate_path(self, path: Union[str, Path]) -> Path:
        """
        Validate and resolve a path, preventing directory traversal.
        
        Args:
            path: Path to validate
            
        Returns:
            Resolved safe path
            
        Raises:
            SecurityError: If path is outside root directory
        """
        path = Path(path)
        
        # Resolve to absolute path
        if not path.is_absolute():
            path = self.root_path / path
        
        # Resolve symlinks and normalize
        try:
            resolved = path.resolve()
        except (OSError, RuntimeError) as e:
            raise SecurityError(f"Cannot resolve path {path}: {e}")
        
        # Check if path is within root
        try:
            resolved.relative_to(self.root_path)
        except ValueError:
            raise SecurityError(f"Path {path} is outside root directory")
        
        return resolved

    def safe_read(
        self,
        file_path: Union[str, Path],
        encoding: str = "utf-8"
    ) -> Optional[str]:
        """
        Safely read a file with validation.
        
        Args:
            file_path: Path to file
            encoding: File encoding
            
        Returns:
            File content or None if error
        """
        try:
            path = self._validate_path(file_path)
            
            if not path.exists():
                logger.warning(f"File does not exist: {path}")
                return None
            
            if not path.is_file():
                logger.warning(f"Path is not a file: {path}")
                return None
            
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            
            logger.debug(f"Successfully read {len(content)} bytes from {path}")
            return content
            
        except SecurityError as e:
            logger.error(f"Security error reading file: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None

    def atomic_write(
        self,
        file_path: Union[str, Path],
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True
    ) -> bool:
        """
        Atomically write to a file using temporary file and rename.
        
        Args:
            file_path: Target file path
            content: Content to write
            encoding: File encoding
            create_dirs: Create parent directories if they don't exist
            
        Returns:
            True if successful
        """
        try:
            path = self._validate_path(file_path)
            
            # Create parent directories if needed
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to temporary file
            with tempfile.NamedTemporaryFile(
                mode='w',
                encoding=encoding,
                dir=path.parent,
                delete=False
            ) as tmp_file:
                tmp_file.write(content)
                tmp_path = Path(tmp_file.name)
            
            # Atomic rename
            tmp_path.replace(path)
            
            logger.info(f"Atomically wrote {len(content)} bytes to {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            # Clean up temp file if it exists
            if 'tmp_path' in locals() and tmp_path.exists():
                try:
                    tmp_path.unlink()
                except:
                    pass
            return False

    def read_json(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Read and parse JSON file."""
        content = self.safe_read(file_path)
        if content:
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON from {file_path}: {e}")
        return None

    def write_json(
        self,
        file_path: Union[str, Path],
        data: Dict[str, Any],
        indent: int = 2
    ) -> bool:
        """Write data as JSON."""
        try:
            content = json.dumps(data, indent=indent)
            return self.atomic_write(file_path, content)
        except Exception as e:
            logger.error(f"Error writing JSON to {file_path}: {e}")
            return False

    def read_yaml(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Read and parse YAML file."""
        content = self.safe_read(file_path)
        if content:
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError as e:
                logger.error(f"Error parsing YAML from {file_path}: {e}")
        return None

    def write_yaml(
        self,
        file_path: Union[str, Path],
        data: Dict[str, Any]
    ) -> bool:
        """Write data as YAML."""
        try:
            content = yaml.dump(data, default_flow_style=False)
            return self.atomic_write(file_path, content)
        except Exception as e:
            logger.error(f"Error writing YAML to {file_path}: {e}")
            return False

    def analyze_project_structure(
        self,
        root_path: Optional[Union[str, Path]] = None,
        max_depth: int = 5,
        ignore_patterns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze project structure and return metadata.
        
        Args:
            root_path: Root directory to analyze
            max_depth: Maximum depth to traverse
            ignore_patterns: Patterns to ignore (e.g., ['*.pyc', '__pycache__'])
            
        Returns:
            Project structure information
        """
        if root_path:
            root = self._validate_path(root_path)
        else:
            root = self.root_path
        
        if ignore_patterns is None:
            ignore_patterns = [
                '__pycache__', '*.pyc', '.git', 'node_modules',
                '.venv', 'venv', '*.egg-info', '.pytest_cache'
            ]
        
        structure = {
            'root': str(root),
            'files': [],
            'directories': [],
            'statistics': {
                'total_files': 0,
                'total_directories': 0,
                'file_types': {},
                'total_size': 0,
                'total_lines': 0
            }
        }
        
        def should_ignore(path: Path) -> bool:
            name = path.name
            for pattern in ignore_patterns:
                if pattern.startswith('*'):
                    if name.endswith(pattern[1:]):
                        return True
                elif name == pattern:
                    return True
            return False
        
        def traverse(current_path: Path, depth: int = 0):
            if depth > max_depth:
                return
            
            try:
                for item in current_path.iterdir():
                    if should_ignore(item):
                        continue
                    
                    if item.is_file():
                        file_info = self.get_file_info(item)
                        structure['files'].append({
                            'path': str(item.relative_to(root)),
                            'type': file_info.type.value,
                            'size': file_info.size,
                            'lines': file_info.lines
                        })
                        
                        structure['statistics']['total_files'] += 1
                        structure['statistics']['total_size'] += file_info.size
                        structure['statistics']['total_lines'] += file_info.lines
                        
                        file_type = file_info.type.value
                        structure['statistics']['file_types'][file_type] = \
                            structure['statistics']['file_types'].get(file_type, 0) + 1
                    
                    elif item.is_dir():
                        structure['directories'].append(
                            str(item.relative_to(root))
                        )
                        structure['statistics']['total_directories'] += 1
                        traverse(item, depth + 1)
            
            except PermissionError:
                logger.warning(f"Permission denied accessing {current_path}")
        
        traverse(root)
        return structure

    def get_file_info(self, file_path: Union[str, Path]) -> FileInfo:
        """
        Get information about a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            FileInfo object
        """
        path = self._validate_path(file_path)
        
        # Determine file type
        suffix = path.suffix.lower()
        file_type = self.extensions.get(suffix, FileType.UNKNOWN)
        
        # Get file stats
        stat = path.stat()
        size = stat.st_size
        
        # Count lines (for text files)
        lines = 0
        if file_type != FileType.UNKNOWN:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = sum(1 for _ in f)
            except:
                pass
        
        return FileInfo(
            path=path,
            type=file_type,
            size=size,
            lines=lines
        )

    def parse_python_ast(
        self,
        file_path: Union[str, Path]
    ) -> Optional[ast.AST]:
        """
        Parse Python file and return AST.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            AST or None if error
        """
        content = self.safe_read(file_path)
        if content:
            try:
                return ast.parse(content)
            except SyntaxError as e:
                logger.error(f"Syntax error parsing {file_path}: {e}")
        return None

    def modify_python_ast(
        self,
        tree: ast.AST,
        transformer: ast.NodeTransformer
    ) -> ast.AST:
        """
        Apply a transformer to Python AST.
        
        Args:
            tree: AST to modify
            transformer: AST transformer
            
        Returns:
            Modified AST
        """
        return transformer.visit(tree)

    def ast_to_source(self, tree: ast.AST) -> str:
        """
        Convert AST back to Python source code.
        
        Args:
            tree: AST to convert
            
        Returns:
            Source code string
        """
        import ast
        return ast.unparse(tree)

    def watch_file(
        self,
        file_path: Union[str, Path],
        callback: Callable[[FileSystemEvent], None],
        recursive: bool = False
    ) -> bool:
        """
        Start watching a file or directory for changes.
        
        Args:
            file_path: Path to watch
            callback: Function to call on changes
            recursive: Watch subdirectories
            
        Returns:
            True if watching started
        """
        if not WATCHDOG_AVAILABLE:
            logger.error("watchdog library not available for file watching")
            return False
        
        try:
            path = self._validate_path(file_path)
            
            class Handler(FileSystemEventHandler):
                def on_any_event(self, event):
                    callback(event)
            
            observer = Observer()
            observer.schedule(Handler(), str(path), recursive=recursive)
            observer.start()
            
            # Store observer
            watch_id = str(path)
            with self._lock:
                self.watchers[watch_id] = observer
            
            logger.info(f"Started watching {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting file watch: {e}")
            return False

    def stop_watch(self, file_path: Union[str, Path]) -> bool:
        """
        Stop watching a file or directory.
        
        Args:
            file_path: Path to stop watching
            
        Returns:
            True if stopped
        """
        try:
            path = self._validate_path(file_path)
            watch_id = str(path)
            
            with self._lock:
                if watch_id in self.watchers:
                    observer = self.watchers[watch_id]
                    observer.stop()
                    observer.join()
                    del self.watchers[watch_id]
                    logger.info(f"Stopped watching {path}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error stopping file watch: {e}")
            return False

    def stop_all_watches(self):
        """Stop all file watches."""
        with self._lock:
            for observer in self.watchers.values():
                observer.stop()
                observer.join()
            self.watchers.clear()
        logger.info("Stopped all file watches")

    def __del__(self):
        """Cleanup watches on deletion."""
        self.stop_all_watches()


# Example AST transformer for adding logging
class LoggingTransformer(ast.NodeTransformer):
    """Example AST transformer that adds logging to functions."""
    
    def visit_FunctionDef(self, node):
        # Add logging at the start of each function
        log_call = ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='logger', ctx=ast.Load()),
                    attr='debug',
                    ctx=ast.Load()
                ),
                args=[
                    ast.Constant(value=f"Entering function {node.name}")
                ],
                keywords=[]
            )
        )
        node.body.insert(0, log_call)
        return self.generic_visit(node)


# Convenience functions
def safe_read_file(file_path: Union[str, Path]) -> Optional[str]:
    """Convenience function for safe file reading."""
    manager = FileOperationsManager()
    return manager.safe_read(file_path)


def atomic_write_file(file_path: Union[str, Path], content: str) -> bool:
    """Convenience function for atomic file writing."""
    manager = FileOperationsManager()
    return manager.atomic_write(file_path, content)


# Example usage
if __name__ == "__main__":
    # Initialize manager
    manager = FileOperationsManager()
    
    # Example: Read a JSON file
    config = manager.read_json("config.json")
    print(f"Config: {config}")
    
    # Example: Analyze project structure
    structure = manager.analyze_project_structure()
    print(f"Project has {structure['statistics']['total_files']} files")
    
    # Example: Watch for changes
    def on_change(event):
        print(f"File changed: {event.src_path}")
    
    if manager.watch_file(".", on_change, recursive=True):
        print("Watching current directory for changes...")
        # Keep watching until interrupted
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop_all_watches()
            print("Stopped watching")