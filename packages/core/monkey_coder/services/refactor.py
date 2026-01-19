"""
Code refactoring service using AI models
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel
import difflib


class RefactorConfig(BaseModel):
    """Configuration for code refactoring"""
    preserve_behavior: bool = True
    apply_best_practices: bool = True
    language: str = "python"


class CodeRefactorer:
    """Refactors code according to instructions"""
    
    def __init__(self, config: Optional[RefactorConfig] = None):
        self.config = config or RefactorConfig()
    
    async def refactor(
        self,
        code: str,
        instructions: str,
        language: str = "python"
    ) -> Dict[str, Any]:
        """Refactor code according to instructions.
        
        Args:
            code: Original source code
            instructions: Refactoring instructions
            language: Programming language
            
        Returns:
            Dictionary with refactored code, diff, and metadata
        """
        # TODO: Implement actual refactoring using AI model
        # For now, return a placeholder response
        refactored_code = self._apply_basic_refactoring(code, instructions, language)
        
        # Generate diff
        diff = self._generate_diff(code, refactored_code)
        
        return {
            "original_code": code,
            "refactored_code": refactored_code,
            "diff": diff,
            "instructions": instructions,
            "language": language,
            "changes_summary": self._summarize_changes(diff)
        }
    
    def _apply_basic_refactoring(self, code: str, instructions: str, language: str) -> str:
        """Apply basic refactoring rules"""
        # This is a placeholder - in production, this would use an AI model
        refactored = code
        
        # Simple example refactorings based on instructions
        if "add type hints" in instructions.lower() and language == "python":
            refactored = f"# TODO: Add type hints\n{refactored}"
        
        if "add docstrings" in instructions.lower():
            refactored = f'"""\nRefactored code with improvements\n"""\n{refactored}'
        
        return refactored
    
    def _generate_diff(self, original: str, refactored: str) -> str:
        """Generate unified diff between original and refactored code"""
        diff_lines = difflib.unified_diff(
            original.splitlines(keepends=True),
            refactored.splitlines(keepends=True),
            fromfile='original.py',
            tofile='refactored.py',
            lineterm=''
        )
        return ''.join(diff_lines)
    
    def _summarize_changes(self, diff: str) -> str:
        """Summarize the changes made"""
        if not diff:
            return "No changes made"
        
        lines_added = diff.count('\n+')
        lines_removed = diff.count('\n-')
        
        return f"Added {lines_added} lines, removed {lines_removed} lines"
