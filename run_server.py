import os
import sys
import subprocess
import uvicorn
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    print("   Attempting to build frontend at runtime...")
    return False

def build_frontend_if_missing():
  """
  Build the frontend if the static assets are missing.
  This is a fallback for when Railway deployment doesn't build the frontend.
  """
  base_dir = Path(__file__).parent
  web_dir = base_dir / "packages" / "web"
  web_out_dir = web_dir / "out"
  
  if web_out_dir.exists():
    logger.info("✅ Frontend assets already exist, skipping build")
    return True
    
  logger.info("🔨 Frontend missing; attempting to build at runtime...")
  
  # Check if web directory exists
  if not web_dir.exists():
    logger.error(f"❌ Web directory not found at: {web_dir}")
    return False
  
  try:
    # Set environment variables for production build
    env = os.environ.copy()
    env.update({
      'NEXT_OUTPUT_EXPORT': 'true',
      'NODE_ENV': 'production',
      'NEXTAUTH_URL': env.get('NEXTAUTH_URL', 'https://coder.fastmonkey.au'),
      'NEXTAUTH_SECRET': env.get('NEXTAUTH_SECRET', 'fallback-secret-change-in-production'),
      'NEXT_PUBLIC_API_URL': env.get('NEXT_PUBLIC_API_URL', 'https://coder.fastmonkey.au'),
      'NEXT_PUBLIC_APP_URL': env.get('NEXT_PUBLIC_APP_URL', 'https://coder.fastmonkey.au'),
      'DATABASE_URL': env.get('DATABASE_URL', ''),  # Empty to prevent build errors
    })
    
    # Step 1: Enable Corepack and prepare Yarn 4.9.2
    logger.info("🔧 Setting up package manager...")
    subprocess.run(["corepack", "enable"], check=True, cwd=base_dir)
    subprocess.run(["corepack", "prepare", "yarn@4.9.2", "--activate"], check=True, cwd=base_dir)
    
    # Step 2: Install dependencies
    logger.info("📦 Installing dependencies...")
    result = subprocess.run(
      ["yarn", "install", "--immutable"],
      check=False,  # Don't fail if lockfile is not immutable
      cwd=base_dir,
      env=env,
      capture_output=True,
      text=True
    )
    
    if result.returncode != 0:
      logger.warning("⚠️ Immutable install failed, trying standard install...")
      subprocess.run(["yarn", "install"], check=True, cwd=base_dir, env=env)
    
    # Step 3: Build the frontend with export
    logger.info("🏗️ Building frontend with static export...")
    result = subprocess.run(
      ["yarn", "workspace", "@monkey-coder/web", "run", "export"],
      check=False,  # Don't fail immediately
      cwd=base_dir,
      env=env,
      capture_output=True,
      text=True
    )
    
    if result.returncode != 0:
      logger.error(f"❌ Frontend build failed with exit code {result.returncode}")
      logger.error(f"STDOUT: {result.stdout}")
      logger.error(f"STDERR: {result.stderr}")
      
      # Try alternative build method
      logger.info("🔄 Trying alternative build method...")
      try:
        # Change to web directory and build directly
        subprocess.run(["yarn", "build"], check=True, cwd=web_dir, env=env)
        logger.info("✅ Alternative build succeeded")
      except subprocess.CalledProcessError as e:
        logger.error(f"❌ Alternative build also failed: {e}")
        return False
    else:
      logger.info("✅ Frontend build completed successfully")
    
    # Verify the build output
    if web_out_dir.exists():
      files = list(web_out_dir.glob("*.html"))
      total_files = len(list(web_out_dir.glob('*')))
      logger.info(f"✅ Build successful! Generated {total_files} files including: {[f.name for f in files[:5]]}")
      return True
    else:
      logger.error("❌ Build completed but output directory not found")
      return False
      
  except subprocess.CalledProcessError as e:
    logger.error(f"❌ Frontend build failed: {e}")
    logger.error(f"Command: {e.cmd}")
    return False
  except Exception as e:
    logger.error(f"❌ Unexpected error during frontend build: {e}")
    return False

def main():
  # Check frontend exists and build if missing
  frontend_exists = check_frontend()
  
  if not frontend_exists:
    logger.info("🚀 Attempting to build frontend at runtime...")
    build_success = build_frontend_if_missing()
    if build_success:
      logger.info("✅ Runtime frontend build completed successfully")
    else:
      logger.warning("⚠️ Runtime frontend build failed, continuing with API-only mode")
  
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

  logger.info(f"🚀 Starting Monkey Coder server on {port}")
  uvicorn.run(
    "monkey_coder.app.main:app",
    host="0.0.0.0",
    port=port,
    log_level="info",
    reload=False
  )

if __name__ == "__main__":
  main()
