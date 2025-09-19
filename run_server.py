#!/usr/bin/env python3
"""
Monkey Coder Server Runner

This module handles the startup, frontend build verification, and server launch
for the Monkey Coder application. Designed for Railway deployment with fallback
support for local development.
"""

import os
import sys
import platform
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any
import signal

# Third-party imports
try:
    import uvicorn
except ImportError:
    print("❌ Error: uvicorn not found. Install with: pip install uvicorn")
    sys.exit(1)


class ServerConfig:
    """Configuration manager for server settings."""

    def __init__(self):
        self.port = self._get_port()
        self.host = "0.0.0.0"
        self.log_level = os.getenv("LOG_LEVEL", "info").lower()
        self.environment = os.getenv("RAILWAY_ENVIRONMENT", "development")
        self.is_production = self.environment == "production"

    def _get_port(self) -> int:
        """Get port from environment with proper validation."""
        port_str = os.getenv("PORT", "8000")
        try:
            port = int(port_str)
            if not (1 <= port <= 65535):
                raise ValueError(f"Port must be between 1-65535, got {port}")
            return port
        except ValueError as e:
            logging.warning(f"Invalid PORT value '{port_str}': {e}. Using default 8000")
            return 8000

    @property
    def frontend_urls(self) -> Dict[str, str]:
        """Get frontend URL configuration."""
        base_url = os.getenv("NEXT_PUBLIC_APP_URL", "https://coder.fastmonkey.au")
        return {
            "NEXTAUTH_URL": os.getenv("NEXTAUTH_URL", base_url),
            "NEXT_PUBLIC_API_URL": os.getenv("NEXT_PUBLIC_API_URL", base_url),
            "NEXT_PUBLIC_APP_URL": base_url,
        }


class SystemInfo:
    """System information collector and logger."""

    @staticmethod
    def collect() -> Dict[str, Any]:
        """Collect comprehensive system and environment information."""
        return {
            "python_version": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation(),
                "compiler": platform.python_compiler(),
                "executable": sys.executable,
            },
            "system": {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "processor": platform.processor() or "Unknown",
                "architecture": platform.architecture()[0],
            },
            "environment": {
                "workdir": str(Path.cwd()),
                "railway_env": os.getenv("RAILWAY_ENVIRONMENT", "local"),
                "node_env": os.getenv("NODE_ENV", "development"),
                "path_entries": len(os.environ.get("PATH", "").split(os.pathsep)),
                "pythonpath_entries": len(os.environ.get("PYTHONPATH", "").split(os.pathsep)),
            },
        }

    @staticmethod
    def log_startup_banner(config: ServerConfig):
        """Log formatted system information and startup banner."""
        info = SystemInfo.collect()

        print("\n" + "=" * 60)
        print("🚀 Starting Monkey Coder Server")
        print("=" * 60)

        print("\n🐍 Python Environment:")
        py = info["python_version"]
        print(f"  • Version:      {py['version']} ({py['implementation']})")
        print(f"  • Executable:   {py['executable']}")

        print("\n💻 System Information:")
        sys_info = info["system"]
        print(f"  • OS:           {sys_info['system']} {sys_info['release']}")
        print(f"  • Architecture: {sys_info['architecture']}")
        print(f"  • Machine:      {sys_info['machine']}")
        if sys_info['processor'] != "Unknown":
            print(f"  • Processor:    {sys_info['processor']}")

        print("\n🌐 Server Configuration:")
        print(f"  • Host:         {config.host}")
        print(f"  • Port:         {config.port}")
        print(f"  • Environment:  {config.environment}")
        print(f"  • Log Level:    {config.log_level}")

        env = info["environment"]
        print("\n📁 Environment:")
        print(f"  • Working Dir:  {env['workdir']}")
        print(f"  • Railway Env:  {env['railway_env']}")
        print(f"  • Node Env:     {env['node_env']}")

        print("=" * 60 + "\n")


class MCPEnvironmentManager:
    """Manager for MCP (Model Context Protocol) environment integration."""

    def __init__(self):
        self.available = False
        self.logger = logging.getLogger(f"{__name__}.MCPEnvironmentManager")
        self._initialize()

    def _initialize(self):
        """Initialize MCP environment manager if available."""
        try:
            # Add core package to path for MCP imports
            base_dir = Path(__file__).parent
            core_path = base_dir / "packages" / "core"
            if core_path.exists():
                sys.path.insert(0, str(core_path))

            from monkey_coder.config.mcp_env_manager import (
                get_production_database_url,
                get_production_api_url,
                get_mcp_variable
            )

            # Store references for later use
            self.get_database_url = get_production_database_url
            self.get_api_url = get_production_api_url
            self.get_variable = get_mcp_variable

            self.available = True
            self.logger.info("✅ MCP environment manager initialized")

        except ImportError as e:
            self.logger.warning(f"⚠️ MCP environment manager not available: {e}")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize MCP environment manager: {e}")

    def is_available(self) -> bool:
        """Check if MCP environment manager is available."""
        return self.available


class FrontendManager:
    """Manager for frontend build operations and verification."""

    def __init__(self, config: ServerConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.FrontendManager")
        self.base_dir = Path(__file__).parent
        self.web_dir = self.base_dir / "packages" / "web"
        self.out_dir = self.web_dir / "out"

    def check_build_exists(self) -> bool:
        """Check if frontend build exists and contains files."""
        self.logger.info(f"🔍 Checking for frontend build at: {self.out_dir}")

        if not self.out_dir.exists():
            self.logger.warning("⚠️ Frontend build directory not found")
            return False

        # Check for index.html specifically
        index_path = self.out_dir / "index.html"
        if not index_path.exists():
            self.logger.warning("⚠️ Frontend build directory exists but missing index.html")
            return False

        # Check if it's the fallback HTML (contains "frontend build in progress")
        try:
            content = index_path.read_text(encoding='utf-8')
            if "frontend build in progress" in content:
                self.logger.warning("⚠️ Found fallback HTML, not actual build")
                return False
        except Exception as e:
            self.logger.warning(f"⚠️ Could not read index.html: {e}")

        html_files = list(self.out_dir.glob("*.html"))
        total_files = len(list(self.out_dir.glob("**/*")))

        self.logger.info(f"✅ Frontend build found: {total_files} files including {[f.name for f in html_files[:3]]}")
        return True

    def build_frontend(self) -> bool:
        """Build the frontend application with multiple fallback strategies."""
        if self.check_build_exists():
            self.logger.info("✅ Frontend already built, skipping build process")
            return True

        self.logger.info("🏗️ Building frontend at runtime...")

        # Prepare build environment
        env = self._prepare_build_environment()

        # Try multiple build strategies with enhanced error handling
        strategies = [
            ("workspace-export", self._build_via_workspace_export),
            ("workspace-build", self._build_via_workspace_build),
            ("direct-export", self._build_via_direct_export),
            ("direct-build", self._build_via_direct_build),
        ]

        for strategy_name, build_func in strategies:
            try:
                self.logger.info(f"🔄 Attempting {strategy_name} build strategy...")
                if build_func(env):
                    self.logger.info(f"✅ Frontend built successfully via {strategy_name}")
                    return True
            except Exception as e:
                self.logger.warning(f"⚠️ {strategy_name} build failed: {e}")
                continue

        # If all strategies fail, create fallback
        self.logger.warning("⚠️ All frontend build strategies failed, creating fallback")
        return self._create_fallback_frontend()

    def _prepare_build_environment(self) -> Dict[str, str]:
        """Prepare environment variables for frontend build."""
        env = os.environ.copy()
        build_vars = {
            "NODE_ENV": "production",
            "NEXT_OUTPUT_EXPORT": "true",
            "NEXT_TELEMETRY_DISABLED": "1",
            **self.config.frontend_urls
        }
        env.update(build_vars)
        return env

    def _build_via_workspace_export(self, env: Dict[str, str]) -> bool:
        """Build frontend using Yarn workspace export command."""
        result = subprocess.run(
            ["yarn", "workspace", "@monkey-coder/web", "run", "export"],
            env=env,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=self.base_dir
        )

        if result.returncode != 0:
            self.logger.error(f"Workspace export build failed: {result.stderr}")
            return False

        return self.out_dir.exists() and len(list(self.out_dir.glob("*.html"))) > 0

    def _build_via_workspace_build(self, env: Dict[str, str]) -> bool:
        """Build frontend using Yarn workspace build command."""
        result = subprocess.run(
            ["yarn", "workspace", "@monkey-coder/web", "run", "build"],
            env=env,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=self.base_dir
        )

        if result.returncode != 0:
            self.logger.error(f"Workspace build failed: {result.stderr}")
            return False

        # After build, try to convert .next to static export
        next_dir = self.web_dir / ".next"
        if next_dir.exists():
            self.logger.info("Converting .next build to static export...")
            self.out_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy static files
            static_dir = next_dir / "static"
            if static_dir.exists():
                subprocess.run(["cp", "-r", str(static_dir), str(self.out_dir / "_next")], check=False)
            
            # Try to find and copy HTML files
            for html_file in next_dir.rglob("*.html"):
                if "server" not in str(html_file):  # Skip server-side files
                    dest = self.out_dir / html_file.name
                    subprocess.run(["cp", str(html_file), str(dest)], check=False)
            
            return self.out_dir.exists() and len(list(self.out_dir.glob("*.html"))) > 0

        return False

    def _build_via_direct_export(self, env: Dict[str, str]) -> bool:
        """Build frontend using direct export commands in web directory."""
        if not self.web_dir.exists():
            self.logger.error(f"Web directory not found: {self.web_dir}")
            return False

        # Install dependencies first
        install_result = subprocess.run(
            ["yarn", "install", "--frozen-lockfile"],
            cwd=self.web_dir,
            timeout=180,
            capture_output=True,
            text=True
        )

        if install_result.returncode != 0:
            self.logger.error(f"Dependencies installation failed: {install_result.stderr}")
            return False

        # Build the frontend
        build_result = subprocess.run(
            ["yarn", "run", "export"],
            cwd=self.web_dir,
            env=env,
            timeout=300,
            capture_output=True,
            text=True
        )

        if build_result.returncode != 0:
            self.logger.error(f"Direct export build failed: {build_result.stderr}")
            return False

        return self.out_dir.exists() and len(list(self.out_dir.glob("*.html"))) > 0

    def _build_via_direct_build(self, env: Dict[str, str]) -> bool:
        """Build frontend using direct build command in web directory."""
        if not self.web_dir.exists():
            self.logger.error(f"Web directory not found: {self.web_dir}")
            return False

        # Build the frontend
        build_result = subprocess.run(
            ["yarn", "run", "build"],
            cwd=self.web_dir,
            env=env,
            timeout=300,
            capture_output=True,
            text=True
        )

        if build_result.returncode != 0:
            self.logger.error(f"Direct build failed: {build_result.stderr}")
            return False

        # Convert .next to out directory manually
        next_dir = self.web_dir / ".next"
        if next_dir.exists():
            self.logger.info("Manually converting .next to out directory...")
            self.out_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy essential files
            try:
                subprocess.run(["cp", "-r", str(next_dir), str(self.out_dir / "_next")], check=True)
                
                # Create a basic index.html that loads the Next.js app
                index_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Monkey Coder</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body>
    <div id="__next"></div>
    <script>window.location.href = '/_next/static/index.html';</script>
</body>
</html>"""
                (self.out_dir / "index.html").write_text(index_html, encoding="utf-8")
                return True
            except Exception as e:
                self.logger.error(f"Failed to convert .next to out: {e}")
                return False

        return False

    def _create_fallback_frontend(self) -> bool:
        """Create minimal fallback frontend when build fails."""
        try:
            # Check if there's already an index.html - don't overwrite it!
            index_path = self.out_dir / "index.html"
            if index_path.exists():
                self.logger.info("✅ index.html already exists, skipping fallback creation")
                return True

            self.out_dir.mkdir(parents=True, exist_ok=True)

            # Create an enhanced fallback that indicates the build issue more clearly
            fallback_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monkey Coder - AI Development Platform</title>
    <style>
        body { font-family: -apple-system, system-ui, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 40px; }
        .links { display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; }
        .link { text-decoration: none; padding: 10px 20px; background: #007acc; color: white; border-radius: 5px; }
        .status { background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🐒 Monkey Coder</h1>
        <p>AI-powered development platform</p>
    </div>

    <div class="status">
        <strong>Status:</strong> ✅ API server is running successfully!
    </div>

    <div class="warning">
        <strong>⚠️ Frontend Build Notice:</strong> The web UI failed to build during deployment.
        <br><br>
        <strong>Workaround:</strong> Use the CLI tool or API endpoints below to access all features.
        <br><br>
        <em>The development team has been notified about this build issue.</em>
    </div>

    <div class="links">
        <a href="/api/docs" class="link">📖 API Documentation</a>
        <a href="/api/health" class="link">🔍 Health Check</a>
        <a href="/frontend-status" class="link">🔧 Build Status</a>
        <a href="https://github.com/GaryOcean428/monkey-coder" class="link">📚 GitHub Repository</a>
    </div>

    <div style="margin-top: 30px; padding: 20px; background: #f9f9f9; border-radius: 5px;">
        <h3>Quick Start:</h3>
        <p>Install the CLI tool:</p>
        <pre style="background: #000; color: #0f0; padding: 10px; border-radius: 3px;">npm install -g monkey-coder-cli</pre>
        <p>Or use the API directly with your preferred HTTP client.</p>
    </div>
</body>
</html>"""

            (self.out_dir / "index.html").write_text(fallback_html, encoding="utf-8")

            # Create a basic 404 page
            (self.out_dir / "404.html").write_text(fallback_html.replace(
                "✅ API server is running successfully!",
                "404 - Page not found"
            ).replace(
                "The web UI failed to build during deployment.",
                "The page you're looking for doesn't exist."
            ), encoding="utf-8")

            self.logger.warning("⚠️ Created fallback frontend indicating build failure")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to create fallback frontend: {e}")
            return False


class ServerRunner:
    """Main server runner orchestrating all components."""

    def __init__(self):
        self.config = ServerConfig()
        self.mcp_manager = MCPEnvironmentManager()
        self.frontend_manager = FrontendManager(self.config)
        self.logger = self._setup_logging()

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        return logging.getLogger(__name__)

    def _signal_handler(self, signum, frame):
        """Handle graceful shutdown signals."""
        self.logger.info(f"🔄 Received signal {signum}, initiating graceful shutdown...")
        # Add any cleanup logic here if needed
        sys.exit(0)

    def _setup_python_path(self):
        """Setup Python path for package imports."""
        base_dir = Path(__file__).parent.absolute()
        paths_to_add = [
            str(base_dir),
            str(base_dir / "packages" / "core"),
        ]

        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)

        self.logger.debug(f"Added paths to sys.path: {paths_to_add}")

    def _validate_environment(self) -> bool:
        """Validate that required environment components are available."""
        try:
            # Check if core application exists
            core_path = Path(__file__).parent / "packages" / "core" / "monkey_coder" / "app" / "main.py"
            if not core_path.exists():
                self.logger.error(f"❌ Core application not found at: {core_path}")
                return False

            self.logger.info("✅ Environment validation passed")
            return True

        except Exception as e:
            self.logger.error(f"❌ Environment validation failed: {e}")
            return False

    def run(self) -> int:
        """Main execution method."""
        try:
            # Display startup information
            SystemInfo.log_startup_banner(self.config)

            # Setup environment
            self._setup_python_path()

            # Validate environment
            if not self._validate_environment():
                return 1

            # Handle frontend building
            if not self.frontend_manager.build_frontend():
                self.logger.warning("⚠️ Frontend build failed, continuing with API-only mode")

            # Log MCP availability
            if self.mcp_manager.is_available():
                self.logger.info("🔌 MCP environment manager ready")

            # Start the server
            self.logger.info(f"🚀 Starting uvicorn server on {self.config.host}:{self.config.port}")

            uvicorn.run(
                "monkey_coder.app.main:app",
                host=self.config.host,
                port=self.config.port,
                log_level=self.config.log_level,
                reload=False,  # Disable reload in production
                access_log=not self.config.is_production,  # Reduce logs in production
            )

            return 0

        except KeyboardInterrupt:
            self.logger.info("🔄 Server stopped by user")
            return 0
        except Exception as e:
            self.logger.error(f"❌ Server startup failed: {e}")
            return 1


def main() -> int:
    """Entry point for the server runner."""
    runner = ServerRunner()
    return runner.run()


if __name__ == "__main__":
    sys.exit(main())
