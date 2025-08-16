import os
import sys
import subprocess
import uvicorn
from pathlib import Path

def build_frontend_if_needed():
  """Build the Next.js frontend if the out directory doesn't exist."""
  base_dir = Path(__file__).parent
  web_out_dir = base_dir / "packages" / "web" / "out"
  
  print(f"🔍 Checking for frontend build at: {web_out_dir}")
  print(f"   Base directory: {base_dir}")
  print(f"   Directory exists: {web_out_dir.exists()}")
  
  if not web_out_dir.exists():
    print("🔨 Frontend build directory not found. Building Next.js app...")
    try:
      # Check if we have Node.js
      try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        print("✅ Node.js is available")
      except:
        print("❌ Node.js not found - cannot build frontend")
        return
      
      # Install dependencies if node_modules doesn't exist
      node_modules = base_dir / "node_modules"
      if not node_modules.exists():
        print("📦 Installing dependencies with Yarn...")
        # Use corepack to get exact Yarn version
        subprocess.run(["corepack", "enable"], check=True, cwd=str(base_dir))
        subprocess.run(["corepack", "prepare", "yarn@4.9.2", "--activate"], check=True, cwd=str(base_dir))
        subprocess.run(["yarn", "install"], check=True, cwd=str(base_dir))
      
      # Build the Next.js app
      print("🏗️ Building Next.js frontend...")
      subprocess.run(["yarn", "workspace", "@monkey-coder/web", "export"], check=True, cwd=str(base_dir))
      print("✅ Frontend build complete!")
      
      # Verify the build output
      if web_out_dir.exists():
        print(f"✅ Build output verified at: {web_out_dir}")
        # List some files to confirm
        files = list(web_out_dir.glob("*.html"))[:5]
        print(f"   Found {len(list(web_out_dir.glob('*')))} files including: {[f.name for f in files]}")
    except subprocess.CalledProcessError as e:
      print(f"⚠️ Warning: Failed to build frontend: {e}")
      print("   Continuing without frontend assets...")
    except FileNotFoundError as e:
      print(f"⚠️ Warning: Build tools not found: {e}")
      print("   Continuing without frontend assets...")
  else:
    print("✅ Frontend assets found at:", web_out_dir)
    # List some files to confirm
    files = list(web_out_dir.glob("*.html"))[:5]
    print(f"   Contains {len(list(web_out_dir.glob('*')))} files including: {[f.name for f in files]}")

def main():
  # Build frontend if needed
  build_frontend_if_needed()
  
  # Ensure package path for Monkey Coder when running from /app
  base_dir = os.path.dirname(os.path.abspath(__file__))
  sys.path.insert(0, base_dir)
  sys.path.insert(0, os.path.join(base_dir, "packages", "core"))
  # Read PORT from env (Railway sets this). Default to 8000 for local dev.
  port_str = os.getenv("PORT", "8000")
  try:
    port = int(port_str)
  except ValueError:
    # Fallback to default if non-integer provided
    port = 8000

  uvicorn.run(
    "monkey_coder.app.main:app",
    host="0.0.0.0",
    port=port,
    log_level="info",
    reload=False
  )

if __name__ == "__main__":
  main()
