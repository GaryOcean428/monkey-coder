#!/usr/bin/env python3
"""
Test script to simulate Railway deployment frontend building
"""
import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

# Import the FrontendManager from run_server
from run_server import FrontendManager, ServerConfig

def test_frontend_build():
    """Test the frontend building process"""
    print("🧪 Testing Frontend Build Process")
    print("=" * 50)
    
    # Create server config
    config = ServerConfig()
    print(f"📝 Server config - Port: {config.port}, Host: {config.host}")
    
    # Create frontend manager
    frontend_manager = FrontendManager(config)
    print(f"📁 Web directory: {frontend_manager.web_dir}")
    print(f"📁 Out directory: {frontend_manager.out_dir}")
    
    # Check if build already exists
    if frontend_manager.check_build_exists():
        print("✅ Frontend build already exists!")
        return True
    else:
        print("⚠️ No existing frontend build found")
    
    # Attempt to build frontend
    print("\n🏗️ Attempting to build frontend...")
    result = frontend_manager.build_frontend()
    
    if result:
        print("✅ Frontend build completed successfully!")
        
        # Check the contents
        if frontend_manager.out_dir.exists():
            files = list(frontend_manager.out_dir.glob("*"))
            print(f"📁 Output directory contains {len(files)} items:")
            for f in files[:10]:  # Show first 10 items
                print(f"   - {f.name}")
            if len(files) > 10:
                print(f"   ... and {len(files) - 10} more items")
    else:
        print("❌ Frontend build failed!")
        
    return result

if __name__ == "__main__":
    success = test_frontend_build()
    sys.exit(0 if success else 1)