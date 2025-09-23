#!/usr/bin/env python3
"""
Test server static directory detection
"""
from pathlib import Path
import os

def test_static_directory_detection():
    """Test the static directory detection logic from main.py"""
    print("🔍 Testing static directory detection (simulating main.py):")
    
    # Simulate the static_dir_options from main.py
    # Using current directory as the reference point
    base_dir = Path.cwd()
    
    static_dir_options = [
        Path("/app/packages/web/out"),  # Primary Railway path
        Path("/app/out"),  # Fallback copy location  
        base_dir / "packages" / "web" / "out",  # Relative path
        base_dir / "out",  # Root out for local dev
        Path("/tmp/test_app_out"),  # Our simulation fallback
    ]

    static_dir = None
    for option in static_dir_options:
        print(f"   Checking: {option} - Exists: {option.exists()}")
        if option.exists():
            static_dir = option
            print(f"✅ Found static directory at: {static_dir}")
            try:
                contents = list(static_dir.iterdir())[:5]
                print(f"   Contains {len(list(static_dir.iterdir()))} items including: {[p.name for p in contents]}")
                
                # Check for index.html specifically
                index_path = static_dir / "index.html"
                if index_path.exists():
                    print(f"   ✅ index.html found at: {index_path}")
                    # Check file size to verify it's not empty
                    file_size = index_path.stat().st_size
                    print(f"   📏 index.html size: {file_size} bytes")
                else:
                    print(f"   ⚠️ index.html NOT found in {static_dir}")
                    
            except Exception as e:
                print(f"   ⚠️ Could not list directory contents: {e}")
            break

    if static_dir:
        print("🎉 SUCCESS: Server would find frontend files!")
        return True
    else:
        print("❌ FAILURE: Server would not find frontend files!")
        return False

if __name__ == "__main__":
    success = test_static_directory_detection()
    exit(0 if success else 1)