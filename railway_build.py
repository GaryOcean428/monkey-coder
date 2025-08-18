"""
Railway Build Script - Python Implementation
Ensures frontend is built before backend starts
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """Execute a shell command and handle errors."""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    print(f"✅ {result.stdout}")
    return True

def main():
    """Main build process for Railway deployment."""
    print("🚀 Starting Railway build process...")
    
    # 1. Setup Yarn
    print("\n📦 Setting up Yarn package manager...")
    if not run_command("corepack enable"):
        print("⚠️ Corepack enable failed, continuing...")
    
    if not run_command("corepack prepare yarn@4.9.2 --activate"):
        print("⚠️ Yarn setup failed, trying with npm...")
        use_npm = True
    else:
        use_npm = False
    
    # 2. Install dependencies
    print("\n📦 Installing Node.js dependencies...")
    if use_npm:
        if not run_command("npm install", cwd="packages/web"):
            print("❌ npm install failed!")
            sys.exit(1)
    else:
        if not run_command("yarn install --immutable"):
            print("❌ Yarn install failed!")
            sys.exit(1)
    
    # 3. Build frontend
    print("\n🏗️ Building Next.js frontend...")
    web_dir = Path("packages/web")
    
    # Use npm if yarn failed
    if use_npm:
        build_cmd = "npm run build"
    else:
        build_cmd = "yarn build"
    
    if not run_command(build_cmd, cwd=str(web_dir)):
        print("❌ Frontend build failed!")
        sys.exit(1)
    
    # 4. Verify build output
    out_dir = web_dir / "out"
    if out_dir.exists():
        file_count = len(list(out_dir.glob("**/*")))
        print(f"✅ Frontend build successful! Generated {file_count} files")
        
        # List some files for verification
        print("📁 Sample files generated:")
        for file in list(out_dir.glob("*.html"))[:5]:
            print(f"   - {file.name}")
    else:
        print("❌ Frontend build directory not found!")
        sys.exit(1)
    
    # 5. Install Python dependencies
    print("\n🐍 Installing Python dependencies...")
    if not run_command("pip install --no-cache-dir -r requirements.txt"):
        print("❌ Python dependency installation failed!")
        sys.exit(1)
    
    # Install core package
    if not run_command("pip install --no-cache-dir -e .", cwd="packages/core"):
        print("❌ Core package installation failed!")
        sys.exit(1)
    
    print("\n✅ Build process complete!")
    print("   Frontend ready at: packages/web/out/")
    print("   Backend ready to start with: python run_server.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
