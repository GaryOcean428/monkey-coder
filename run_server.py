import os
import sys
import subprocess
import uvicorn
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import MCP-enhanced environment manager
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "packages", "core"))
    from monkey_coder.config.mcp_env_manager import get_production_database_url, get_production_api_url, get_mcp_variable
    MCP_ENV_AVAILABLE = True
    logger.info("✅ MCP environment manager available")
except ImportError as e:
    logger.warning(f"⚠️ MCP environment manager not available: {e}")
    MCP_ENV_AVAILABLE = False

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

def get_production_database_url():
  """
  Get production database URL using MCP environment variables or Railway defaults.
  
  Avoids localhost defaults which are not useful in production.
  """
  if MCP_ENV_AVAILABLE:
    # Use MCP environment manager for intelligent variable resolution
    from monkey_coder.config.mcp_env_manager import get_production_database_url as mcp_get_db_url
    return mcp_get_db_url()
  
  # Fallback implementation when MCP is not available
  # Primary: Use explicit environment variable
  database_url = os.getenv('DATABASE_URL')
  if database_url and database_url != 'postgresql://localhost:5432/placeholder':
    return database_url
  
  # Secondary: Use Railway service references  
  railway_db_host = os.getenv('RAILWAY_DB_HOST')
  railway_db_port = os.getenv('RAILWAY_DB_PORT', '5432')
  railway_db_name = os.getenv('RAILWAY_DB_NAME', 'railway')
  railway_db_user = os.getenv('RAILWAY_DB_USER', 'postgres')
  railway_db_password = os.getenv('RAILWAY_DB_PASSWORD', '')
  
  if railway_db_host:
    return f"postgresql://{railway_db_user}:{railway_db_password}@{railway_db_host}:{railway_db_port}/{railway_db_name}"
  
  # Tertiary: Use Railway internal service discovery
  return "postgresql://railway.internal:5432/railway"

def get_production_api_url():
  """
  Get production API URL using Railway's public domain or MCP configuration.
  
  Avoids localhost defaults which are not useful in production.
  """
  if MCP_ENV_AVAILABLE:
    # Use MCP environment manager for intelligent variable resolution
    from monkey_coder.config.mcp_env_manager import get_production_api_url as mcp_get_api_url
    return mcp_get_api_url()
  
  # Fallback implementation when MCP is not available
  # Primary: Use explicit environment variable
  api_url = os.getenv('NEXT_PUBLIC_API_URL')
  if api_url and not api_url.startswith('http://localhost'):
    return api_url
  
  # Secondary: Use Railway public domain
  railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN')
  if railway_domain:
    return f"https://{railway_domain}"
  
  # Tertiary: Use Railway static URL pattern
  railway_env = os.getenv('RAILWAY_ENVIRONMENT')
  railway_project = os.getenv('RAILWAY_PROJECT_NAME', 'monkey-coder')
  if railway_env:
    return f"https://{railway_project}-{railway_env}.railway.app"
  
  # Default: Use coder.fastmonkey.au (configured production domain)
  return "https://coder.fastmonkey.au"
def build_frontend_if_missing():
  """
  Build the frontend if the static assets are missing.
  This is a robust fallback for when Railway deployment doesn't build the frontend.
  Enhanced with MCP-based environment variable management to avoid localhost in production.
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
    # Set comprehensive environment variables for production build
    env = os.environ.copy()
    
    # Generate a unique secret if none provided
    import secrets
    random_secret = secrets.token_hex(32)
    
    # Use MCP-based environment variable management
    production_api_url = get_production_api_url()
    production_database_url = get_production_database_url()
    
    # Get additional variables using MCP if available
    if MCP_ENV_AVAILABLE:
      stripe_public_key = get_mcp_variable('STRIPE_PUBLIC_KEY', 'pk_test_placeholder')
      stripe_secret_key = get_mcp_variable('STRIPE_SECRET_KEY', 'sk_test_placeholder')
      stripe_webhook_secret = get_mcp_variable('STRIPE_WEBHOOK_SECRET', 'whsec_placeholder')
    else:
      stripe_public_key = env.get('STRIPE_PUBLIC_KEY', 'pk_test_placeholder')
      stripe_secret_key = env.get('STRIPE_SECRET_KEY', 'sk_test_placeholder')
      stripe_webhook_secret = env.get('STRIPE_WEBHOOK_SECRET', 'whsec_placeholder')
    
    env.update({
      'NEXT_OUTPUT_EXPORT': 'true',
      'NODE_ENV': 'production',
      'NEXT_TELEMETRY_DISABLED': '1',
      'NEXTAUTH_URL': env.get('NEXTAUTH_URL', production_api_url),
      'NEXTAUTH_SECRET': env.get('NEXTAUTH_SECRET', f'runtime-secret-{random_secret}'),
      'NEXT_PUBLIC_API_URL': env.get('NEXT_PUBLIC_API_URL', production_api_url),
      'NEXT_PUBLIC_APP_URL': env.get('NEXT_PUBLIC_APP_URL', production_api_url),
      'DATABASE_URL': env.get('DATABASE_URL', production_database_url),
      'STRIPE_PUBLIC_KEY': stripe_public_key,
      'STRIPE_SECRET_KEY': stripe_secret_key,
      'STRIPE_WEBHOOK_SECRET': stripe_webhook_secret,
    })
    
    logger.info(f"🔧 Environment configured with API URL: {production_api_url}")
    logger.info(f"🔧 Database URL configured: {production_database_url.split('@')[0]}@***")  # Hide credentials
    
    logger.info("🔧 Setting up package manager...")
    # Step 1: Enable Corepack and prepare Yarn 4.9.2
    try:
      subprocess.run(["corepack", "enable"], check=True, cwd=base_dir, timeout=30)
      subprocess.run(["corepack", "prepare", "yarn@4.9.2", "--activate"], check=True, cwd=base_dir, timeout=60)
      logger.info("✅ Package manager setup completed")
    except subprocess.TimeoutExpired:
      logger.error("❌ Package manager setup timed out")
      return False
    except subprocess.CalledProcessError as e:
      logger.error(f"❌ Package manager setup failed: {e}")
      return False
    
    # Step 2: Install dependencies with timeout and retries
    logger.info("📦 Installing dependencies...")
    for attempt in range(2):
      try:
        result = subprocess.run(
          ["yarn", "install", "--immutable"],
          check=False,
          cwd=base_dir,
          env=env,
          capture_output=True,
          text=True,
          timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
          logger.warning(f"⚠️ Immutable install failed (attempt {attempt + 1}), trying standard install...")
          result = subprocess.run(
            ["yarn", "install"],
            check=True,
            cwd=base_dir,
            env=env,
            timeout=300
          )
        
        logger.info("✅ Dependencies installed successfully")
        break
        
      except subprocess.TimeoutExpired:
        logger.error(f"❌ Dependency installation timed out (attempt {attempt + 1})")
        if attempt == 1:  # Last attempt
          return False
      except subprocess.CalledProcessError as e:
        logger.error(f"❌ Dependency installation failed (attempt {attempt + 1}): {e}")
        if attempt == 1:  # Last attempt
          return False
    
    # Step 3: Build the frontend with export and comprehensive error handling
    logger.info("🏗️ Building frontend with static export...")
    try:
      result = subprocess.run(
        ["yarn", "workspace", "@monkey-coder/web", "run", "export"],
        check=False,
        cwd=base_dir,
        env=env,
        capture_output=True,
        text=True,
        timeout=600  # 10 minute timeout for build
      )
      
      if result.returncode != 0:
        logger.error(f"❌ Frontend workspace build failed with exit code {result.returncode}")
        logger.error(f"STDOUT: {result.stdout[-1000:] if result.stdout else 'No stdout'}")  # Last 1000 chars
        logger.error(f"STDERR: {result.stderr[-1000:] if result.stderr else 'No stderr'}")
        
        # Try alternative build method - direct build in web directory
        logger.info("🔄 Trying alternative build method in web directory...")
        try:
          alt_env = env.copy()
          result = subprocess.run(
            ["yarn", "run", "export"],
            check=True,
            cwd=web_dir,
            env=alt_env,
            timeout=600
          )
          logger.info("✅ Alternative build method succeeded")
        except subprocess.CalledProcessError as e:
          logger.error(f"❌ Alternative build also failed: {e}")
          return False
        except subprocess.TimeoutExpired:
          logger.error("❌ Alternative build timed out")
          return False
      else:
        logger.info("✅ Frontend build completed successfully")
    
    except subprocess.TimeoutExpired:
      logger.error("❌ Frontend build timed out after 10 minutes")
      return False
    
    # Step 4: Verify the build output with detailed logging
    if web_out_dir.exists():
      try:
        html_files = list(web_out_dir.glob("*.html"))
        all_files = list(web_out_dir.glob('*'))
        total_files = len(all_files)
        
        logger.info(f"✅ Build successful! Generated {total_files} files")
        logger.info(f"   HTML files: {[f.name for f in html_files[:5]]}")
        logger.info(f"   Other files: {[f.name for f in all_files if f.suffix != '.html'][:5]}")
        
        # Check for critical files
        index_html = web_out_dir / "index.html"
        if index_html.exists():
          logger.info(f"✅ Critical file exists: index.html ({index_html.stat().st_size} bytes)")
        else:
          logger.warning("⚠️ index.html not found in build output")
        
        return True
        
      except Exception as e:
        logger.error(f"❌ Error verifying build output: {e}")
        return False
    else:
      logger.error("❌ Build completed but output directory not found")
      logger.info(f"   Expected: {web_out_dir}")
      logger.info(f"   Web dir contents: {list(web_dir.iterdir()) if web_dir.exists() else 'Web dir not found'}")
      return False
      
  except Exception as e:
    logger.error(f"❌ Unexpected error during frontend build: {e}")
    logger.error(f"   Error type: {type(e).__name__}")
    import traceback
    logger.error(f"   Traceback: {traceback.format_exc()}")
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
