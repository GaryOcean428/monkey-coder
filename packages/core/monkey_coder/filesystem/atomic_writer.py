"""
Atomic file writing operations with rollback support.

Ensures data integrity through atomic writes and automatic backup creation.
"""

import os
import shutil
import tempfile
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Union, Tuple, List
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class AtomicWriter:
    """
    Provides atomic file writing with automatic backup and rollback capabilities.
    """
    
    def __init__(self, backup_dir: Optional[Path] = None):
        """
        Initialize atomic writer.
        
        Args:
            backup_dir: Directory for storing backups
        """
        self.backup_dir = backup_dir or (Path.home() / ".monkey_coder" / "backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self._active_writes = {}
        self._backup_history = []
    
    @contextmanager
    def atomic_write(self, filepath: Union[str, Path], mode: str = 'w',
                    encoding: str = 'utf-8', create_backup: bool = True):
        """
        Context manager for atomic file writing.
        
        Usage:
            with atomic_writer.atomic_write('file.txt') as f:
                f.write('content')
        
        Args:
            filepath: Path to file to write
            mode: File mode ('w' or 'wb')
            encoding: Text encoding (ignored for binary mode)
            create_backup: Whether to create backup before writing
            
        Yields:
            File handle for writing
        """
        path = Path(filepath).resolve()
        temp_path = None
        backup_path = None
        
        try:
            # Create backup if requested and file exists
            if create_backup and path.exists():
                backup_path = self._create_backup(path)
                logger.info(f"Created backup: {backup_path}")
            
            # Create temporary file in same directory (for atomic rename)
            temp_fd, temp_path = tempfile.mkstemp(
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp"
            )
            os.close(temp_fd)  # Close the file descriptor
            
            # Track active write
            self._active_writes[str(path)] = {
                "temp_path": temp_path,
                "backup_path": backup_path,
                "start_time": datetime.now()
            }
            
            # Open temp file for writing
            if 'b' in mode:
                with open(temp_path, mode) as f:
                    yield f
            else:
                with open(temp_path, mode, encoding=encoding) as f:
                    yield f
            
            # Successful write - perform atomic rename
            self._finalize_write(path, Path(temp_path))
            
            # Clean up tracking
            del self._active_writes[str(path)]
            
            logger.info(f"Atomic write completed: {path}")
            
        except Exception as e:
            logger.error(f"Atomic write failed for {path}: {e}")
            
            # Attempt rollback if backup exists
            if backup_path and Path(backup_path).exists():
                try:
                    self._rollback(path, Path(backup_path))
                    logger.info(f"Rolled back to backup: {backup_path}")
                except Exception as rollback_error:
                    logger.error(f"Rollback failed: {rollback_error}")
            
            # Clean up temp file if it exists
            if temp_path and Path(temp_path).exists():
                try:
                    Path(temp_path).unlink()
                except:
                    pass
            
            # Clean up tracking
            if str(path) in self._active_writes:
                del self._active_writes[str(path)]
            
            raise
    
    def safe_write_with_backup(self, filepath: Union[str, Path], content: Union[str, bytes],
                              encoding: str = 'utf-8') -> Tuple[bool, str]:
        """
        Safely write content to file with automatic backup.
        
        Args:
            filepath: Path to file
            content: Content to write
            encoding: Text encoding (for string content)
            
        Returns:
            Tuple of (success, message/backup_path)
        """
        try:
            path = Path(filepath).resolve()
            
            # Determine mode based on content type
            if isinstance(content, bytes):
                mode = 'wb'
            else:
                mode = 'w'
            
            # Use atomic write context manager
            with self.atomic_write(path, mode=mode, encoding=encoding) as f:
                f.write(content)
            
            # Get backup path if one was created
            backup_info = self._backup_history[-1] if self._backup_history else None
            
            if backup_info:
                return True, f"File written successfully. Backup: {backup_info['backup_path']}"
            else:
                return True, "File written successfully"
                
        except Exception as e:
            logger.error(f"Safe write failed for {filepath}: {e}")
            return False, str(e)
    
    def rollback_changes(self, filepath: Union[str, Path]) -> Tuple[bool, str]:
        """
        Rollback file to most recent backup.
        
        Args:
            filepath: Path to file to rollback
            
        Returns:
            Tuple of (success, message)
        """
        try:
            path = Path(filepath).resolve()
            
            # Find most recent backup for this file
            backup_path = self._find_latest_backup(path)
            
            if not backup_path:
                return False, "No backup found for rollback"
            
            # Perform rollback
            self._rollback(path, backup_path)
            
            logger.info(f"Successfully rolled back {path} from {backup_path}")
            return True, f"Rolled back from backup: {backup_path}"
            
        except Exception as e:
            logger.error(f"Rollback failed for {filepath}: {e}")
            return False, str(e)
    
    def _create_backup(self, path: Path) -> Path:
        """
        Create a backup of a file.
        
        Args:
            path: Path to file to backup
            
        Returns:
            Path to backup file
        """
        # Generate unique backup name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        file_hash = hashlib.md5(str(path).encode()).hexdigest()[:8]
        backup_name = f"{path.name}.{timestamp}.{file_hash}.backup"
        backup_path = self.backup_dir / backup_name
        
        # Copy file to backup location
        shutil.copy2(path, backup_path)
        
        # Track backup in history
        self._backup_history.append({
            "original_path": str(path),
            "backup_path": str(backup_path),
            "timestamp": datetime.now(),
            "file_hash": file_hash
        })
        
        # Limit backup history size
        if len(self._backup_history) > 100:
            self._backup_history = self._backup_history[-100:]
        
        return backup_path
    
    def _finalize_write(self, target_path: Path, temp_path: Path):
        """
        Finalize atomic write by renaming temp file.
        
        Args:
            target_path: Final destination path
            temp_path: Temporary file path
        """
        # Ensure data is written to disk
        if temp_path.exists():
            # On POSIX systems, rename is atomic
            # On Windows, we need to handle it differently
            if os.name == 'nt':
                # Windows: delete target first if it exists
                if target_path.exists():
                    target_path.unlink()
                temp_path.rename(target_path)
            else:
                # POSIX: atomic rename
                temp_path.rename(target_path)
    
    def _rollback(self, target_path: Path, backup_path: Path):
        """
        Rollback file from backup.
        
        Args:
            target_path: Path to restore to
            backup_path: Path to backup file
        """
        if backup_path.exists():
            shutil.copy2(backup_path, target_path)
        else:
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
    
    def _find_latest_backup(self, path: Path) -> Optional[Path]:
        """
        Find the most recent backup for a file.
        
        Args:
            path: Original file path
            
        Returns:
            Path to latest backup or None
        """
        # Search in backup history
        for backup_info in reversed(self._backup_history):
            if backup_info["original_path"] == str(path):
                backup_path = Path(backup_info["backup_path"])
                if backup_path.exists():
                    return backup_path
        
        # Search in backup directory
        pattern = f"{path.name}.*.backup"
        backups = list(self.backup_dir.glob(pattern))
        
        if backups:
            # Sort by modification time and return most recent
            backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            return backups[0]
        
        return None
    
    def cleanup_old_backups(self, days: int = 7) -> int:
        """
        Clean up backups older than specified days.
        
        Args:
            days: Number of days to keep backups
            
        Returns:
            Number of backups deleted
        """
        deleted = 0
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        
        for backup_file in self.backup_dir.glob("*.backup"):
            try:
                if backup_file.stat().st_mtime < cutoff_time:
                    backup_file.unlink()
                    deleted += 1
                    logger.info(f"Deleted old backup: {backup_file}")
            except Exception as e:
                logger.error(f"Failed to delete backup {backup_file}: {e}")
        
        return deleted
    
    def get_active_writes(self) -> List[Dict]:
        """
        Get list of currently active atomic writes.
        
        Returns:
            List of active write operations
        """
        return [
            {
                "file": filepath,
                "temp_path": info["temp_path"],
                "backup_path": info["backup_path"],
                "duration": (datetime.now() - info["start_time"]).total_seconds()
            }
            for filepath, info in self._active_writes.items()
        ]


# Global instance for convenience
_global_writer = AtomicWriter()


def atomic_write(filepath: Union[str, Path], mode: str = 'w',
                encoding: str = 'utf-8', create_backup: bool = True):
    """
    Convenience function for atomic write context manager.
    
    Usage:
        with atomic_write('file.txt') as f:
            f.write('content')
    """
    return _global_writer.atomic_write(filepath, mode, encoding, create_backup)


def safe_write_with_backup(filepath: Union[str, Path], content: Union[str, bytes],
                          encoding: str = 'utf-8') -> Tuple[bool, str]:
    """
    Convenience function for safe write with backup.
    """
    return _global_writer.safe_write_with_backup(filepath, content, encoding)


def rollback_changes(filepath: Union[str, Path]) -> Tuple[bool, str]:
    """
    Convenience function to rollback file changes.
    """
    return _global_writer.rollback_changes(filepath)