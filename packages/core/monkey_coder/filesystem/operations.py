"""
filesystem_utils.py

A robust Python module for safe file system operations and project structure analysis.

Functions:
    - read_file(filepath: str) -> str
    - write_file(filepath: str, content: str, create_backup: bool = True) -> None
    - analyze_project_structure(root_path: str) -> dict

Includes:
    - Path validation to prevent directory traversal
    - Atomic file writes with optional backup
    - Project type and framework detection
    - Comprehensive logging and error handling
"""

import os
import shutil
import tempfile
import logging
from typing import Optional, Dict, Any

# --- Logging Setup ---
logger = logging.getLogger("filesystem_utils")
logger.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s')
_handler.setFormatter(_formatter)
if not logger.hasHandlers():
    logger.addHandler(_handler)

# --- Constants ---
SAFE_BASE_DIR = os.path.abspath(os.getcwd())  # Restrict file operations to current working directory

# --- Helper Functions ---

def _is_safe_path(base_dir: str, target_path: str) -> bool:
    """
    Ensure that the target_path is within base_dir to prevent directory traversal.
    """
    base_dir = os.path.abspath(base_dir)
    target_path = os.path.abspath(target_path)
    try:
        common = os.path.commonpath([base_dir, target_path])
        is_safe = common == base_dir
        if not is_safe:
            logger.warning(f"Unsafe path detected: {target_path} is outside {base_dir}")
        return is_safe
    except ValueError:
        logger.error(f"Error comparing paths: {base_dir}, {target_path}")
        return False

def _ensure_dir_exists(filepath: str) -> None:
    """
    Ensure the directory for the given file path exists.
    """
    dirpath = os.path.dirname(os.path.abspath(filepath))
    if not os.path.exists(dirpath):
        logger.info(f"Creating directory: {dirpath}")
        os.makedirs(dirpath, exist_ok=True)

def _detect_python_framework(files: set, dirs: set) -> Optional[str]:
    if 'manage.py' in files or 'django' in dirs:
        return 'Django'
    if 'pyproject.toml' in files:
        try:
            import toml
            with open('pyproject.toml', 'r', encoding='utf-8') as f:
                pyproject = toml.load(f)
            if 'tool' in pyproject and 'poetry' in pyproject['tool']:
                return 'Poetry'
        except Exception:
            pass
    if 'requirements.txt' in files:
        with open('requirements.txt', 'r', encoding='utf-8', errors='replace') as f:
            reqs = f.read().lower()
            if 'fastapi' in reqs:
                return 'FastAPI'
            if 'flask' in reqs:
                return 'Flask'
            if 'django' in reqs:
                return 'Django'
    return None

def _detect_node_framework(files: set, dirs: set, root_path: str) -> Optional[str]:
    if 'package.json' in files:
        import json
        try:
            with open(os.path.join(root_path, 'package.json'), 'r', encoding='utf-8', errors='replace') as f:
                pkg = json.load(f)
            deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
            if 'react' in deps:
                return 'React'
            if 'vue' in deps:
                return 'Vue'
            if 'next' in deps:
                return 'Next.js'
            if 'nuxt' in deps:
                return 'Nuxt.js'
            if 'express' in deps:
                return 'Express'
        except Exception as e:
            logger.warning(f"Could not parse package.json: {e}")
    return None

def _detect_php_framework(files: set, dirs: set, root_path: str) -> Optional[str]:
    if 'composer.json' in files:
        import json
        try:
            with open(os.path.join(root_path, 'composer.json'), 'r', encoding='utf-8', errors='replace') as f:
                composer = json.load(f)
            reqs = composer.get('require', {})
            if 'laravel/framework' in reqs:
                return 'Laravel'
            if 'symfony/symfony' in reqs:
                return 'Symfony'
        except Exception as e:
            logger.warning(f"Could not parse composer.json: {e}")
    if 'index.php' in files:
        return 'PHP (Generic)'
    return None

# --- Main Functions ---

def read_file(filepath: str) -> str:
    """
    Safely read a file with path validation to prevent directory traversal.
    Handles encoding errors with 'replace' strategy.
    Logs all operations.

    Args:
        filepath (str): Path to the file to read.

    Returns:
        str: File contents.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be accessed.
        ValueError: If the path is unsafe.
    """
    abs_path = os.path.abspath(filepath)
    if not _is_safe_path(SAFE_BASE_DIR, abs_path):
        logger.error(f"Attempted directory traversal: {filepath}")
        raise ValueError("Unsafe file path detected.")
    try:
        with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        logger.info(f"Read file: {abs_path}")
        return content
    except FileNotFoundError:
        logger.error(f"File not found: {abs_path}")
        raise
    except PermissionError:
        logger.error(f"Permission denied: {abs_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading file {abs_path}: {e}")
        raise

def write_file(filepath: str, content: str, create_backup: bool = True) -> None:
    """
    Write content to a file atomically, with optional backup of the existing file.

    Args:
        filepath (str): Path to the file to write.
        content (str): Content to write.
        create_backup (bool): Whether to create a backup of the existing file.

    Raises:
        ValueError: If the path is unsafe.
        Exception: For other I/O errors.
    """
    abs_path = os.path.abspath(filepath)
    if not _is_safe_path(SAFE_BASE_DIR, abs_path):
        logger.error(f"Attempted directory traversal: {filepath}")
        raise ValueError("Unsafe file path detected.")

    _ensure_dir_exists(abs_path)

    # Backup if requested and file exists
    if create_backup and os.path.exists(abs_path):
        backup_path = abs_path + ".bak"
        try:
            shutil.copy2(abs_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
        except Exception as e:
            logger.warning(f"Failed to create backup for {abs_path}: {e}")

    # Write atomically using tempfile
    dirpath = os.path.dirname(abs_path)
    try:
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=dirpath, delete=False) as tf:
            tf.write(content)
            tempname = tf.name
        os.replace(tempname, abs_path)
        logger.info(f"Wrote file atomically: {abs_path}")
    except Exception as e:
        logger.error(f"Error writing file {abs_path}: {e}")
        raise

def analyze_project_structure(root_path: str) -> Dict[str, Any]:
    """
    Analyze the project structure to detect project type and framework.

    Args:
        root_path (str): Path to the project root.

    Returns:
        dict: {
            'project_type': str,
            'framework': Optional[str],
            'details': dict
        }
    """
    abs_root = os.path.abspath(root_path)
    if not os.path.isdir(abs_root):
        logger.error(f"Not a directory: {abs_root}")
        raise NotADirectoryError(f"{abs_root} is not a directory.")

    files = set(os.listdir(abs_root))
    dirs = set([d for d in files if os.path.isdir(os.path.join(abs_root, d))])
    files = set([f for f in files if os.path.isfile(os.path.join(abs_root, f))])

    project_type = None
    framework = None
    details = {}

    # Python
    if 'requirements.txt' in files or 'pyproject.toml' in files or any(f.endswith('.py') for f in files):
        project_type = 'Python'
        framework = _detect_python_framework(files, dirs)
    # Node.js
    elif 'package.json' in files:
        project_type = 'Node.js'
        framework = _detect_node_framework(files, dirs, abs_root)
    # PHP
    elif 'composer.json' in files or any(f.endswith('.php') for f in files):
        project_type = 'PHP'
        framework = _detect_php_framework(files, dirs, abs_root)
    # Other
    else:
        project_type = 'Unknown'
        framework = None

    # Details: list of main files, directories, etc.
    details['files'] = sorted(list(files))
    details['directories'] = sorted(list(dirs))

    logger.info(f"Analyzed project at {abs_root}: type={project_type}, framework={framework}")
    return {
        'project_type': project_type,
        'framework': framework,
        'details': details
    }

# --- Module Test (Optional) ---
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    # Example usage
    try:
        print(analyze_project_structure('.'))
    except Exception as e:
        logger.error(f"Error: {e}")