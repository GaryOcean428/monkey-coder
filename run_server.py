import os
import sys
import subprocess
import uvicorn
from pathlib import Path

def check_frontend():
  """Check if the Next.js frontend build exists."""
  base_dir = Path(__file__).parent
  web_out_dir = base_dir / "packages" / "web" / "out"
  
  print(f"🔍 Checking for frontend build at: {web_out_dir}")
  print(f"   Base directory: {base_dir}")
  print(f"   Directory exists: {web_out_dir.exists()}")
  
  if web_out_dir.exists():
    print("✅ Frontend assets found at:", web_out_dir)
    # List some files to confirm
    files = list(web_out_dir.glob("*.html"))[:5]
    total_files = len(list(web_out_dir.glob('*')))
    print(f"   Contains {total_files} files including: {[f.name for f in files]}")
    return True
  else:
    print("⚠️ Frontend build directory not found.")
    print("   Please build the frontend locally with: ./build-frontend.sh")
    print("   Then commit the packages/web/out/ directory to git")
    return False

def main():
  # Check frontend exists
  check_frontend()
  
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
