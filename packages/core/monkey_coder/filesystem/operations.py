"""
Safe file system operations for Monkey Coder.

Implements secure file reading/writing with path validation,
atomic operations, and backup creation.
"""

import os
import shutil
import hashlib
import logging
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class FileType(Enum):
    """Enumeration of file types."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    HTML = "html"
    CSS = "css"
    TEXT = "text"
    BINARY = "binary"
    UNKNOWN = "unknown"


@dataclass
class FileInfo:
    """Information about a file."""
    path: Path
    name: str
    size: int
    type: FileType
    mime_type: str
    encoding: str
    created_at: datetime
    modified_at: datetime
    is_readable: bool
    is_writable: bool
    hash: Optional[str] = None
    content: Optional[str] = None


@dataclass
class ProjectStructure:
    """Information about project structure."""
    root_path: Path
    files: List[FileInfo]
    directories: List[Path]
    total_files: int
    total_size: int
    project_type: Optional[str] = None
    framework: Optional[str] = None
    language: Optional[str] = None
    dependencies: Optional[Dict[str, Any]] = None


class FileSystemOperations:
    """
    Safe file system operations with security checks and atomic writes.
    """
    
    # Default allowed directories (can be configured)
    DEFAULT_ALLOWED_DIRS = [
        Path.cwd(),  # Current working directory
        Path.home() / "projects",  # User projects directory
        Path("/tmp"),  # Temporary directory
    ]
    
    # Dangerous file patterns to block
    DANGEROUS_PATTERNS = [
        ".git/config",
        ".ssh/",
        ".env",
        "id_rsa",
        "credentials",
        "password",
        "secret",
        "token",
        ".aws/",
    ]
    
    # Maximum file size for reading (10MB default)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    def __init__(self, allowed_dirs: Optional[List[Path]] = None,
                 max_file_size: Optional[int] = None):
        """
        Initialize file system operations.
        
        Args:
            allowed_dirs: List of allowed directories for operations
            max_file_size: Maximum file size for reading
        """
        self.allowed_dirs = allowed_dirs or self.DEFAULT_ALLOWED_DIRS
        self.max_file_size = max_file_size or self.MAX_FILE_SIZE
        self.backup_dir = Path.home() / ".monkey_coder" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def is_safe_path(self, path: Union[str, Path]) -> bool:
        """
        Check if a path is safe to access.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is safe, False otherwise
        """
        try:
            path = Path(path).resolve()
            
            # Check if path contains dangerous patterns
            path_str = str(path).lower()
            for pattern in self.DANGEROUS_PATTERNS:
                if pattern.lower() in path_str:
                    logger.warning(f"Dangerous pattern detected in path: {path}")
                    return False
            
            # Check if path is within allowed directories
            for allowed_dir in self.allowed_dirs:
                try:
                    allowed_dir = allowed_dir.resolve()
                    path.relative_to(allowed_dir)
                    return True
                except ValueError:
                    continue
            
            logger.warning(f"Path not in allowed directories: {path}")
            return False
            
        except Exception as e:
            logger.error(f"Error checking path safety: {e}")
            return False
    
    def read_file(self, filepath: Union[str, Path],
                  encoding: str = "utf-8") -> Tuple[bool, Union[str, str]]:
        """
        Safely read a file with validation.
        
        Args:
            filepath: Path to file to read
            encoding: File encoding
            
        Returns:
            Tuple of (success, content/error_message)
        """
        try:
            path = Path(filepath).resolve()
            
            # Security check
            if not self.is_safe_path(path):
                return False, f"Access denied: {filepath}"
            
            # Check if file exists
            if not path.exists():
                return False, f"File not found: {filepath}"
            
            # Check if it's a file
            if not path.is_file():
                return False, f"Not a file: {filepath}"
            
            # Check file size
            file_size = path.stat().st_size
            if file_size > self.max_file_size:
                return False, f"File too large: {file_size} bytes (max: {self.max_file_size})"
            
            # Try to read the file
            try:
                with open(path, 'r', encoding=encoding) as f:
                    content = f.read()
                    logger.info(f"Successfully read file: {path} ({file_size} bytes)")
                    return True, content
            except UnicodeDecodeError:
                # Try with binary mode for non-text files
                with open(path, 'rb') as f:
                    content = f.read()
                    logger.info(f"Read binary file: {path} ({file_size} bytes)")
                    return True, content.decode('latin-1', errors='replace')
            
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {e}")
            return False, str(e)
    
    def write_file(self, filepath: Union[str, Path], content: str,
                   create_backup: bool = True,
                   encoding: str = "utf-8") -> Tuple[bool, str]:
        """
        Safely write content to a file with optional backup.
        
        Args:
            filepath: Path to file to write
            content: Content to write
            create_backup: Whether to create backup before writing
            encoding: File encoding
            
        Returns:
            Tuple of (success, message/backup_path)
        """
        try:
            path = Path(filepath).resolve()
            
            # Security check
            if not self.is_safe_path(path):
                return False, f"Access denied: {filepath}"
            
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup if file exists and backup requested
            backup_path = None
            if path.exists() and create_backup:
                success, backup_result = self.create_backup(path)
                if not success:
                    return False, f"Failed to create backup: {backup_result}"
                backup_path = backup_result
            
            # Write file atomically (write to temp file and rename)
            temp_path = path.with_suffix(path.suffix + '.tmp')
            try:
                with open(temp_path, 'w', encoding=encoding) as f:
                    f.write(content)
                    f.flush()
                    os.fsync(f.fileno())  # Ensure data is written to disk
                
                # Atomic rename
                temp_path.replace(path)
                
                logger.info(f"Successfully wrote file: {path} ({len(content)} chars)")
                
                if backup_path:
                    return True, f"File written successfully. Backup: {backup_path}"
                else:
                    return True, "File written successfully"
                    
            except Exception as e:
                # Clean up temp file if it exists
                if temp_path.exists():
                    temp_path.unlink()
                raise e
                
        except Exception as e:
            logger.error(f"Error writing file {filepath}: {e}")
            return False, str(e)
    
    def create_backup(self, filepath: Union[str, Path]) -> Tuple[bool, str]:
        """
        Create a backup of a file.
        
        Args:
            filepath: Path to file to backup
            
        Returns:
            Tuple of (success, backup_path/error_message)
        """
        try:
            path = Path(filepath).resolve()
            
            if not path.exists():
                return False, "File does not exist"
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_hash = hashlib.md5(str(path).encode()).hexdigest()[:8]
            backup_name = f"{path.name}.{timestamp}.{file_hash}.backup"
            backup_path = self.backup_dir / backup_name
            
            # Copy file to backup location
            shutil.copy2(path, backup_path)
            
            logger.info(f"Created backup: {backup_path}")
            return True, str(backup_path)
            
        except Exception as e:
            logger.error(f"Error creating backup for {filepath}: {e}")
            return False, str(e)
    
    def list_directory(self, dirpath: Union[str, Path],
                      recursive: bool = False,
                      patterns: Optional[List[str]] = None) -> Tuple[bool, Union[List[FileInfo], str]]:
        """
        List files in a directory.
        
        Args:
            dirpath: Directory path
            recursive: Whether to list recursively
            patterns: File patterns to match (e.g., ["*.py", "*.js"])
            
        Returns:
            Tuple of (success, file_list/error_message)
        """
        try:
            path = Path(dirpath).resolve()
            
            # Security check
            if not self.is_safe_path(path):
                return False, f"Access denied: {dirpath}"
            
            if not path.exists():
                return False, f"Directory not found: {dirpath}"
            
            if not path.is_dir():
                return False, f"Not a directory: {dirpath}"
            
            files = []
            
            if recursive:
                # Recursive listing
                for item in path.rglob("*"):
                    if item.is_file():
                        if patterns:
                            # Check if file matches any pattern
                            if not any(item.match(pattern) for pattern in patterns):
                                continue
                        files.append(self._get_file_info(item))
            else:
                # Non-recursive listing
                for item in path.iterdir():
                    if item.is_file():
                        if patterns:
                            if not any(item.match(pattern) for pattern in patterns):
                                continue
                        files.append(self._get_file_info(item))
            
            logger.info(f"Listed {len(files)} files in {path}")
            return True, files
            
        except Exception as e:
            logger.error(f"Error listing directory {dirpath}: {e}")
            return False, str(e)
    
    def _get_file_info(self, path: Path) -> FileInfo:
        """Get information about a file."""
        stat = path.stat()
        mime_type, _ = mimetypes.guess_type(str(path))
        
        # Determine file type
        file_type = self._detect_file_type(path)
        
        # Detect encoding for text files
        encoding = "utf-8"
        if file_type != FileType.BINARY:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    f.read(100)  # Try reading first 100 chars
            except UnicodeDecodeError:
                encoding = "binary"
                file_type = FileType.BINARY
        
        return FileInfo(
            path=path,
            name=path.name,
            size=stat.st_size,
            type=file_type,
            mime_type=mime_type or "application/octet-stream",
            encoding=encoding,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            is_readable=os.access(path, os.R_OK),
            is_writable=os.access(path, os.W_OK),
        )
    
    def _detect_file_type(self, path: Path) -> FileType:
        """Detect the type of a file based on extension."""
        ext = path.suffix.lower()
        
        type_map = {
            '.py': FileType.PYTHON,
            '.js': FileType.JAVASCRIPT,
            '.jsx': FileType.JAVASCRIPT,
            '.ts': FileType.TYPESCRIPT,
            '.tsx': FileType.TYPESCRIPT,
            '.json': FileType.JSON,
            '.yaml': FileType.YAML,
            '.yml': FileType.YAML,
            '.md': FileType.MARKDOWN,
            '.html': FileType.HTML,
            '.css': FileType.CSS,
            '.txt': FileType.TEXT,
        }
        
        return type_map.get(ext, FileType.UNKNOWN)
    
    def analyze_project_structure(self, root_path: Union[str, Path]) -> Tuple[bool, Union[ProjectStructure, str]]:
        """
        Analyze project structure and detect project type.
        
        Args:
            root_path: Root directory of the project
            
        Returns:
            Tuple of (success, project_structure/error_message)
        """
        try:
            path = Path(root_path).resolve()
            
            # Security check
            if not self.is_safe_path(path):
                return False, f"Access denied: {root_path}"
            
            if not path.exists() or not path.is_dir():
                return False, f"Invalid project directory: {root_path}"
            
            # Collect all files and directories
            files = []
            directories = []
            total_size = 0
            
            for item in path.rglob("*"):
                if item.is_file():
                    # Skip hidden files and common ignore patterns
                    relative_path = item.relative_to(path)
                    parts = relative_path.parts
                    if any(part.startswith('.') for part in parts):
                        continue
                    if any(part in ['node_modules', '__pycache__', 'venv', '.git'] for part in parts):
                        continue
                    
                    file_info = self._get_file_info(item)
                    files.append(file_info)
                    total_size += file_info.size
                elif item.is_dir():
                    directories.append(item)
            
            # Detect project type and framework
            project_type, framework, language = self._detect_project_type(path)
            
            structure = ProjectStructure(
                root_path=path,
                files=files,
                directories=directories,
                total_files=len(files),
                total_size=total_size,
                project_type=project_type,
                framework=framework,
                language=language,
            )
            
            logger.info(f"Analyzed project: {path} - {project_type}/{framework}/{language}")
            return True, structure
            
        except Exception as e:
            logger.error(f"Error analyzing project structure: {e}")
            return False, str(e)
    
    def _detect_project_type(self, path: Path) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Detect project type, framework, and language."""
        project_type = None
        framework = None
        language = None
        
        # Check for common project files
        if (path / "package.json").exists():
            project_type = "node"
            language = "javascript"
            
            # Try to detect framework
            try:
                import json
                with open(path / "package.json", 'r') as f:
                    data = json.load(f)
                    deps = data.get("dependencies", {})
                    dev_deps = data.get("devDependencies", {})
                    all_deps = {**deps, **dev_deps}
                    
                    if "next" in all_deps:
                        framework = "nextjs"
                    elif "react" in all_deps:
                        framework = "react"
                    elif "vue" in all_deps:
                        framework = "vue"
                    elif "angular" in all_deps:
                        framework = "angular"
                    elif "express" in all_deps:
                        framework = "express"
            except:
                pass
        
        elif (path / "requirements.txt").exists() or (path / "pyproject.toml").exists():
            project_type = "python"
            language = "python"
            
            # Try to detect framework
            if (path / "manage.py").exists():
                framework = "django"
            elif (path / "app.py").exists() or (path / "application.py").exists():
                # Could be Flask or FastAPI
                framework = "flask"  # Default assumption
        
        elif (path / "Cargo.toml").exists():
            project_type = "rust"
            language = "rust"
        
        elif (path / "go.mod").exists():
            project_type = "go"
            language = "go"
        
        elif (path / "pom.xml").exists():
            project_type = "java"
            language = "java"
            framework = "maven"
        
        elif (path / "build.gradle").exists():
            project_type = "java"
            language = "java"
            framework = "gradle"
        
        return project_type, framework, language


# Convenience functions
def read_file(filepath: Union[str, Path], encoding: str = "utf-8") -> Tuple[bool, Union[str, str]]:
    """Convenience function to read a file."""
    ops = FileSystemOperations()
    return ops.read_file(filepath, encoding)


def write_file(filepath: Union[str, Path], content: str,
               create_backup: bool = True, encoding: str = "utf-8") -> Tuple[bool, str]:
    """Convenience function to write a file."""
    ops = FileSystemOperations()
    return ops.write_file(filepath, content, create_backup, encoding)


def create_backup(filepath: Union[str, Path]) -> Tuple[bool, str]:
    """Convenience function to create a backup."""
    ops = FileSystemOperations()
    return ops.create_backup(filepath)


def list_directory(dirpath: Union[str, Path], recursive: bool = False,
                  patterns: Optional[List[str]] = None) -> Tuple[bool, Union[List[FileInfo], str]]:
    """Convenience function to list directory."""
    ops = FileSystemOperations()
    return ops.list_directory(dirpath, recursive, patterns)


def analyze_project_structure(root_path: Union[str, Path]) -> Tuple[bool, Union[ProjectStructure, str]]:
    """Convenience function to analyze project structure."""
    ops = FileSystemOperations()
    return ops.analyze_project_structure(root_path)


def is_safe_path(path: Union[str, Path]) -> bool:
    """Convenience function to check path safety."""
    ops = FileSystemOperations()
    return ops.is_safe_path(path)


def get_file_info(filepath: Union[str, Path]) -> Optional[FileInfo]:
    """Convenience function to get file info."""
    ops = FileSystemOperations()
    path = Path(filepath).resolve()
    if ops.is_safe_path(path) and path.exists() and path.is_file():
        return ops._get_file_info(path)
    return None