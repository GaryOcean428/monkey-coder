#!/usr/bin/env python3
"""Validate all imports in main application files"""
import ast
import sys
from pathlib import Path

def check_imports_in_file(file_path):
    try:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module)
        
        return imports
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def main():
    app_files = Path("packages/core").rglob("*.py")
    all_imports = set()
    
    for file_path in app_files:
        imports = check_imports_in_file(file_path)
        all_imports.update(imports)
    
    print("All detected imports:")
    for imp in sorted(all_imports):
        if imp and not imp.startswith('.'):
            print(f"  {imp}")

if __name__ == "__main__":
    main()
