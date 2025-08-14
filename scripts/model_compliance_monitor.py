#!/usr/bin/env python3
"""
Model Compliance Monitor

This script monitors code changes and logs to detect when AI agents
(or developers) try to use deprecated or invalid model names.

It can be run as:
1. A pre-commit hook
2. A CI/CD check
3. A real-time monitor
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple
import subprocess

# Add package to path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "core"))

from monkey_coder.models.model_validator import ModelManifestValidator, DEPRECATED_MODELS


class ModelComplianceMonitor:
    """Monitor code for model compliance violations."""
    
    # Patterns to detect model usage
    MODEL_PATTERNS = [
        r'model\s*=\s*["\']([^"\']+)["\']',  # model = "gpt-4"
        r'model_name\s*=\s*["\']([^"\']+)["\']',  # model_name = "gpt-4"
        r'"model":\s*"([^"]+)"',  # "model": "gpt-4"
        r'["\']model["\']\s*:\s*["\']([^"\']+)["\']',  # 'model': 'gpt-4'
        r'--model\s+([^\s]+)',  # --model gpt-4
        r'Model\.([A-Z_]+)',  # Model.GPT_4
        r'model:\s*([^\s,\)]+)',  # model: gpt-4
    ]
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.validator = ModelManifestValidator()
        self.violations: List[Dict] = []
        
    def scan_file(self, filepath: Path) -> List[Dict]:
        """
        Scan a file for model compliance violations.
        
        Args:
            filepath: Path to file to scan
            
        Returns:
            List of violations found
        """
        violations = []
        
        # Skip non-code files
        if filepath.suffix not in ['.py', '.ts', '.js', '.tsx', '.jsx', '.yml', '.yaml', '.json', '.md']:
            return violations
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check each pattern
            for pattern in self.MODEL_PATTERNS:
                for match in re.finditer(pattern, content):
                    model_name = match.group(1)
                    
                    # Skip variables and placeholders
                    if model_name in ['model', 'MODEL', '{model}', '${model}', 'self.model']:
                        continue
                    
                    # Check if it's a deprecated model
                    if self._is_deprecated(model_name):
                        line_num = content[:match.start()].count('\n') + 1
                        line_text = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                        
                        violations.append({
                            'file': str(filepath),
                            'line': line_num,
                            'model': model_name,
                            'type': 'deprecated',
                            'context': line_text,
                            'suggestion': self._get_suggestion(model_name)
                        })
                    
                    # Check if it's completely invalid
                    elif self._is_invalid(model_name):
                        line_num = content[:match.start()].count('\n') + 1
                        line_text = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                        
                        violations.append({
                            'file': str(filepath),
                            'line': line_num,
                            'model': model_name,
                            'type': 'invalid',
                            'context': line_text,
                            'suggestion': self._get_suggestion(model_name)
                        })
        
        except Exception as e:
            if self.verbose:
                print(f"Error scanning {filepath}: {e}")
        
        return violations
    
    def _is_deprecated(self, model: str) -> bool:
        """Check if a model is deprecated."""
        return model in ModelManifestValidator.DEPRECATED_MODELS
    
    def _is_invalid(self, model: str) -> bool:
        """Check if a model is invalid (not in manifest and not deprecated)."""
        # Try to guess the provider from the model name
        provider = self._guess_provider(model)
        if not provider:
            return False
        
        is_valid, _, _ = self.validator.validate_model(model, provider)
        return not is_valid and model not in ModelManifestValidator.DEPRECATED_MODELS
    
    def _guess_provider(self, model: str) -> Optional[str]:
        """Guess provider from model name."""
        if 'gpt' in model.lower() or 'o1' in model.lower() or 'o3' in model.lower():
            return 'openai'
        elif 'claude' in model.lower():
            return 'anthropic'
        elif 'gemini' in model.lower():
            return 'google'
        elif 'llama' in model.lower() or 'qwen' in model.lower() or 'kimi' in model.lower():
            return 'groq'
        elif 'grok' in model.lower():
            return 'xai'
        return None
    
    def _get_suggestion(self, model: str) -> str:
        """Get suggestion for deprecated/invalid model."""
        provider = self._guess_provider(model)
        if provider:
            _, _, suggestion = self.validator.validate_model(model, provider)
            return suggestion or "Check MODEL_MANIFEST.md"
        return "Check MODEL_MANIFEST.md"
    
    def scan_directory(self, directory: Path) -> List[Dict]:
        """
        Recursively scan directory for violations.
        
        Args:
            directory: Directory to scan
            
        Returns:
            List of all violations found
        """
        all_violations = []
        
        # Skip common directories
        skip_dirs = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build'}
        
        for root, dirs, files in os.walk(directory):
            # Remove skip directories from search
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                filepath = Path(root) / file
                violations = self.scan_file(filepath)
                all_violations.extend(violations)
        
        return all_violations
    
    def scan_git_changes(self) -> List[Dict]:
        """
        Scan only changed files in git.
        
        Returns:
            List of violations in changed files
        """
        try:
            # Get list of changed files
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return []
            
            all_violations = []
            for filename in result.stdout.strip().split('\n'):
                if filename:
                    filepath = Path(filename)
                    if filepath.exists():
                        violations = self.scan_file(filepath)
                        all_violations.extend(violations)
            
            return all_violations
        
        except Exception as e:
            if self.verbose:
                print(f"Error scanning git changes: {e}")
            return []
    
    def format_report(self, violations: List[Dict]) -> str:
        """
        Format violations into a readable report.
        
        Args:
            violations: List of violations
            
        Returns:
            Formatted report string
        """
        if not violations:
            return "✅ No model compliance violations found!"
        
        report = ["❌ MODEL COMPLIANCE VIOLATIONS FOUND\n"]
        report.append(f"Found {len(violations)} violation(s):\n")
        
        # Group by file
        by_file = {}
        for v in violations:
            if v['file'] not in by_file:
                by_file[v['file']] = []
            by_file[v['file']].append(v)
        
        for filepath, file_violations in by_file.items():
            report.append(f"\n📄 {filepath}")
            for v in file_violations:
                emoji = "⚠️" if v['type'] == 'deprecated' else "❌"
                report.append(f"  {emoji} Line {v['line']}: '{v['model']}'")
                report.append(f"     → Suggestion: {v['suggestion']}")
                if v['context']:
                    report.append(f"     → Context: {v['context'][:80]}")
        
        report.append("\n" + "=" * 60)
        report.append("📚 Please check MODEL_MANIFEST.md for valid models")
        report.append("🔧 Run with --fix to auto-correct violations")
        
        return "\n".join(report)
    
    def fix_violations(self, violations: List[Dict]) -> int:
        """
        Attempt to auto-fix violations.
        
        Args:
            violations: List of violations to fix
            
        Returns:
            Number of fixes applied
        """
        fixes_applied = 0
        files_to_fix = {}
        
        # Group violations by file
        for v in violations:
            if v['file'] not in files_to_fix:
                files_to_fix[v['file']] = []
            files_to_fix[v['file']].append(v)
        
        # Fix each file
        for filepath, file_violations in files_to_fix.items():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Apply fixes
                for v in file_violations:
                    old_model = v['model']
                    new_model = v['suggestion']
                    
                    if new_model and new_model != "Check MODEL_MANIFEST.md":
                        # Replace the model name
                        patterns = [
                            (f'"{old_model}"', f'"{new_model}"'),
                            (f"'{old_model}'", f"'{new_model}'"),
                            (f' {old_model}', f' {new_model}'),  # For CLI args
                        ]
                        
                        for old, new in patterns:
                            if old in content:
                                content = content.replace(old, new)
                                fixes_applied += 1
                                if self.verbose:
                                    print(f"Fixed: {old} → {new} in {filepath}")
                
                # Write back
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            except Exception as e:
                print(f"Error fixing {filepath}: {e}")
        
        return fixes_applied


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Monitor code for model compliance violations')
    parser.add_argument('path', nargs='?', default='.', help='Path to scan (file or directory)')
    parser.add_argument('--git', action='store_true', help='Scan only git staged files')
    parser.add_argument('--fix', action='store_true', help='Auto-fix violations')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--ci', action='store_true', help='CI mode (exit with error on violations)')
    
    args = parser.parse_args()
    
    monitor = ModelComplianceMonitor(verbose=args.verbose)
    
    # Scan for violations
    if args.git:
        violations = monitor.scan_git_changes()
    else:
        path = Path(args.path)
        if path.is_file():
            violations = monitor.scan_file(path)
        else:
            violations = monitor.scan_directory(path)
    
    # Apply fixes if requested
    if args.fix and violations:
        fixes = monitor.fix_violations(violations)
        print(f"✅ Applied {fixes} fix(es)")
    
    # Output results
    if args.json:
        print(json.dumps(violations, indent=2))
    else:
        print(monitor.format_report(violations))
    
    # Exit code for CI
    if args.ci and violations:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()