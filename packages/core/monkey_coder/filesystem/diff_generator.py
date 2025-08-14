"""
Diff generation and application for code modifications.

Provides unified diff generation, patch creation, and diff application.
"""

import difflib
import re
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DiffHunk:
    """Represents a single hunk in a diff."""
    old_start: int
    old_lines: int
    new_start: int
    new_lines: int
    lines: List[str]
    context: Optional[str] = None


@dataclass
class FileDiff:
    """Represents a diff for a single file."""
    old_path: Path
    new_path: Path
    hunks: List[DiffHunk]
    is_new_file: bool = False
    is_deleted: bool = False
    is_binary: bool = False


class DiffGenerator:
    """
    Generates and applies unified diffs for code modifications.
    """
    
    def __init__(self, context_lines: int = 3):
        """
        Initialize diff generator.
        
        Args:
            context_lines: Number of context lines to include
        """
        self.context_lines = context_lines
    
    def generate_unified_diff(self, old_content: str, new_content: str,
                            old_name: str = "original", new_name: str = "modified",
                            old_date: Optional[datetime] = None,
                            new_date: Optional[datetime] = None) -> str:
        """
        Generate a unified diff between two strings.
        
        Args:
            old_content: Original content
            new_content: Modified content
            old_name: Name for original file
            new_name: Name for modified file
            old_date: Timestamp for original file
            new_date: Timestamp for modified file
            
        Returns:
            Unified diff as string
        """
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        # Ensure lines end with newline
        if old_lines and not old_lines[-1].endswith('\n'):
            old_lines[-1] += '\n'
        if new_lines and not new_lines[-1].endswith('\n'):
            new_lines[-1] += '\n'
        
        # Generate timestamps
        old_timestamp = old_date.isoformat() if old_date else "original"
        new_timestamp = new_date.isoformat() if new_date else "modified"
        
        # Generate unified diff
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"{old_name}\t{old_timestamp}",
            tofile=f"{new_name}\t{new_timestamp}",
            n=self.context_lines,
            lineterm=''
        )
        
        return ''.join(diff)
    
    def generate_file_diff(self, old_path: Union[str, Path],
                          new_path: Union[str, Path]) -> Optional[FileDiff]:
        """
        Generate diff between two files.
        
        Args:
            old_path: Path to original file
            new_path: Path to modified file
            
        Returns:
            FileDiff object or None if files are identical
        """
        old_path = Path(old_path)
        new_path = Path(new_path)
        
        # Check file existence
        old_exists = old_path.exists()
        new_exists = new_path.exists()
        
        if not old_exists and not new_exists:
            logger.error("Both files do not exist")
            return None
        
        # Handle new file
        if not old_exists and new_exists:
            new_content = new_path.read_text(encoding='utf-8')
            diff_text = self.generate_unified_diff(
                "", new_content,
                str(old_path), str(new_path)
            )
            hunks = self._parse_unified_diff(diff_text)
            return FileDiff(
                old_path=old_path,
                new_path=new_path,
                hunks=hunks,
                is_new_file=True
            )
        
        # Handle deleted file
        if old_exists and not new_exists:
            old_content = old_path.read_text(encoding='utf-8')
            diff_text = self.generate_unified_diff(
                old_content, "",
                str(old_path), str(new_path)
            )
            hunks = self._parse_unified_diff(diff_text)
            return FileDiff(
                old_path=old_path,
                new_path=new_path,
                hunks=hunks,
                is_deleted=True
            )
        
        # Both files exist
        try:
            old_content = old_path.read_text(encoding='utf-8')
            new_content = new_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # Binary files
            return FileDiff(
                old_path=old_path,
                new_path=new_path,
                hunks=[],
                is_binary=True
            )
        
        # Generate diff
        diff_text = self.generate_unified_diff(
            old_content, new_content,
            str(old_path), str(new_path),
            datetime.fromtimestamp(old_path.stat().st_mtime),
            datetime.fromtimestamp(new_path.stat().st_mtime)
        )
        
        if not diff_text:
            # Files are identical
            return None
        
        hunks = self._parse_unified_diff(diff_text)
        
        return FileDiff(
            old_path=old_path,
            new_path=new_path,
            hunks=hunks
        )
    
    def create_patch(self, diffs: List[FileDiff]) -> str:
        """
        Create a patch file from multiple file diffs.
        
        Args:
            diffs: List of FileDiff objects
            
        Returns:
            Patch content as string
        """
        patch_lines = []
        
        for diff in diffs:
            # File header
            if diff.is_new_file:
                patch_lines.append(f"--- /dev/null")
                patch_lines.append(f"+++ {diff.new_path}")
            elif diff.is_deleted:
                patch_lines.append(f"--- {diff.old_path}")
                patch_lines.append(f"+++ /dev/null")
            else:
                patch_lines.append(f"--- {diff.old_path}")
                patch_lines.append(f"+++ {diff.new_path}")
            
            # Binary file notification
            if diff.is_binary:
                patch_lines.append("Binary files differ")
                continue
            
            # Add hunks
            for hunk in diff.hunks:
                # Hunk header
                header = f"@@ -{hunk.old_start},{hunk.old_lines} +{hunk.new_start},{hunk.new_lines} @@"
                if hunk.context:
                    header += f" {hunk.context}"
                patch_lines.append(header)
                
                # Hunk lines
                patch_lines.extend(hunk.lines)
        
        return '\n'.join(patch_lines) + '\n'
    
    def apply_diff(self, content: str, diff: str) -> Tuple[bool, str]:
        """
        Apply a unified diff to content.
        
        Args:
            content: Original content
            diff: Unified diff to apply
            
        Returns:
            Tuple of (success, result_content/error_message)
        """
        try:
            lines = content.splitlines(keepends=True)
            hunks = self._parse_unified_diff(diff)
            
            # Apply hunks in reverse order to maintain line numbers
            for hunk in reversed(hunks):
                success, lines = self._apply_hunk(lines, hunk)
                if not success:
                    return False, f"Failed to apply hunk at line {hunk.old_start}"
            
            return True, ''.join(lines)
            
        except Exception as e:
            logger.error(f"Failed to apply diff: {e}")
            return False, str(e)
    
    def _parse_unified_diff(self, diff_text: str) -> List[DiffHunk]:
        """
        Parse unified diff text into hunks.
        
        Args:
            diff_text: Unified diff as string
            
        Returns:
            List of DiffHunk objects
        """
        hunks = []
        lines = diff_text.splitlines()
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Look for hunk header
            match = re.match(r'^@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@(.*)$', line)
            if match:
                old_start = int(match.group(1))
                old_lines = int(match.group(2)) if match.group(2) else 1
                new_start = int(match.group(3))
                new_lines = int(match.group(4)) if match.group(4) else 1
                context = match.group(5).strip() if match.group(5) else None
                
                # Collect hunk lines
                hunk_lines = []
                i += 1
                
                while i < len(lines):
                    if lines[i].startswith('@@') or lines[i].startswith('---') or lines[i].startswith('+++'):
                        break
                    hunk_lines.append(lines[i])
                    i += 1
                
                hunks.append(DiffHunk(
                    old_start=old_start,
                    old_lines=old_lines,
                    new_start=new_start,
                    new_lines=new_lines,
                    lines=hunk_lines,
                    context=context
                ))
            else:
                i += 1
        
        return hunks
    
    def _apply_hunk(self, lines: List[str], hunk: DiffHunk) -> Tuple[bool, List[str]]:
        """
        Apply a single hunk to lines.
        
        Args:
            lines: Original lines
            hunk: Hunk to apply
            
        Returns:
            Tuple of (success, modified_lines)
        """
        # Convert to 0-based indexing
        start_line = hunk.old_start - 1
        
        # Verify context
        old_lines = []
        new_lines = []
        
        for hunk_line in hunk.lines:
            if hunk_line.startswith('-'):
                old_lines.append(hunk_line[1:])
            elif hunk_line.startswith('+'):
                new_lines.append(hunk_line[1:])
            elif hunk_line.startswith(' '):
                old_lines.append(hunk_line[1:])
                new_lines.append(hunk_line[1:])
        
        # Check if we can apply the hunk
        end_line = start_line + len(old_lines)
        if end_line > len(lines):
            # Try fuzzy matching
            match_index = self._find_fuzzy_match(lines, old_lines)
            if match_index is None:
                return False, lines
            start_line = match_index
            end_line = start_line + len(old_lines)
        
        # Apply the hunk
        result = lines[:start_line] + new_lines + lines[end_line:]
        
        return True, result
    
    def _find_fuzzy_match(self, lines: List[str], target_lines: List[str],
                         threshold: float = 0.8) -> Optional[int]:
        """
        Find fuzzy match for target lines in lines.
        
        Args:
            lines: Lines to search in
            target_lines: Lines to find
            threshold: Similarity threshold (0-1)
            
        Returns:
            Starting index of match or None
        """
        if not target_lines:
            return 0
        
        target_len = len(target_lines)
        
        for i in range(len(lines) - target_len + 1):
            window = lines[i:i + target_len]
            
            # Calculate similarity
            matcher = difflib.SequenceMatcher(None, window, target_lines)
            ratio = matcher.ratio()
            
            if ratio >= threshold:
                return i
        
        return None
    
    def generate_context_diff(self, old_content: str, new_content: str,
                             old_name: str = "original", new_name: str = "modified") -> str:
        """
        Generate a context diff (alternative to unified diff).
        
        Args:
            old_content: Original content
            new_content: Modified content
            old_name: Name for original file
            new_name: Name for modified file
            
        Returns:
            Context diff as string
        """
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = difflib.context_diff(
            old_lines,
            new_lines,
            fromfile=old_name,
            tofile=new_name,
            n=self.context_lines,
            lineterm=''
        )
        
        return ''.join(diff)


# Convenience functions
def generate_unified_diff(old_content: str, new_content: str,
                         old_name: str = "original", new_name: str = "modified") -> str:
    """Generate unified diff between two strings."""
    generator = DiffGenerator()
    return generator.generate_unified_diff(old_content, new_content, old_name, new_name)


def apply_diff(content: str, diff: str) -> Tuple[bool, str]:
    """Apply a unified diff to content."""
    generator = DiffGenerator()
    return generator.apply_diff(content, diff)


def create_patch(diffs: List[FileDiff]) -> str:
    """Create a patch from multiple file diffs."""
    generator = DiffGenerator()
    return generator.create_patch(diffs)


def parse_diff(diff_text: str) -> List[DiffHunk]:
    """Parse unified diff text into hunks."""
    generator = DiffGenerator()
    return generator._parse_unified_diff(diff_text)