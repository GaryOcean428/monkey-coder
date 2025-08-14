"""
Filesystem operations module for Monkey Coder.

Provides safe file reading, writing, and project analysis capabilities.
Implements atomic operations with backup creation for safety.
"""

from .operations import (
    FileSystemOperations,
    read_file,
    write_file,
    create_backup,
    list_directory,
    analyze_project_structure,
    is_safe_path,
    get_file_info,
    FileInfo,
    ProjectStructure,
)
from .project_analyzer import (
    ProjectAnalyzer,
    detect_project_type,
    extract_dependencies,
    find_entry_points,
    get_code_stats,
    CodeStats,
)
from .diff_generator import (
    DiffGenerator,
    generate_unified_diff,
    apply_diff,
    create_patch,
    parse_diff,
)
from .atomic_writer import (
    AtomicWriter,
    atomic_write,
    safe_write_with_backup,
    rollback_changes,
)

__all__ = [
    # Main operations
    "FileSystemOperations",
    "read_file",
    "write_file",
    "create_backup",
    "list_directory",
    "analyze_project_structure",
    "is_safe_path",
    "get_file_info",
    "FileInfo",
    "ProjectStructure",
    
    # Project analysis
    "ProjectAnalyzer",
    "detect_project_type",
    "extract_dependencies",
    "find_entry_points",
    "get_code_stats",
    "CodeStats",
    
    # Diff operations
    "DiffGenerator",
    "generate_unified_diff",
    "apply_diff",
    "create_patch",
    "parse_diff",
    
    # Atomic operations
    "AtomicWriter",
    "atomic_write",
    "safe_write_with_backup",
    "rollback_changes",
]