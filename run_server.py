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

        html_files = list(self.out_dir.glob("*.html"))
        total_files = len(list(self.out_dir.glob("*")))

        if not html_files:
            self.logger.warning("⚠️ Frontend build directory exists but contains no HTML files")
            return False

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

        # Try multiple build strategies
        strategies = [
            ("workspace", self._build_via_workspace),
            ("direct", self._build_via_direct),
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

        # Create fallback if all strategies fail
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

    def _build_via_workspace(self, env: Dict[str, str]) -> bool:
        """Build frontend using Yarn workspace command."""
        result = subprocess.run(
            ["yarn", "workspace", "@monkey-coder/web", "run", "export"],
            env=env,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=self.base_dir
        )

        if result.returncode != 0:
            self.logger.error(f"Workspace build failed: {result.stderr}")
            return False

        return self.out_dir.exists() and len(list(self.out_dir.glob("*.html"))) > 0

    def _build_via_direct(self, env: Dict[str, str]) -> bool:
        """Build frontend using direct commands in web directory."""
        if not self.web_dir.exists():
            self.logger.error(f"Web directory not found: {self.web_dir}")
            return False

        # Install dependencies first
        install_result = subprocess.run(
            ["yarn", "install"],
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
            self.logger.error(f"Direct build failed: {build_result.stderr}")
            return False

        return self.out_dir.exists() and len(list(self.out_dir.glob("*.html"))) > 0

    def _create_fallback_frontend(self) -> bool:
        """Create minimal fallback frontend when build fails."""
        try:
            self.out_dir.mkdir(parents=True, exist_ok=True)

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
    </style>
</head>
<body>
    <div class="header">
        <h1>🐒 Monkey Coder</h1>
        <p>AI-powered development platform</p>
    </div>

    <div class="status">
        <strong>Status:</strong> API server running, frontend build in progress
    </div>

    <div class="links">
        <a href="/api/docs" class="link">📖 API Documentation</a>
        <a href="/api/health" class="link">🔍 Health Check</a>
    </div>
</body>
</html>"""

            (self.out_dir / "index.html").write_text(fallback_html, encoding="utf-8")

            # Create a basic 404 page
            (self.out_dir / "404.html").write_text(fallback_html.replace(
                "API server running, frontend build in progress",
                "Page not found - redirecting to API documentation"
            ), encoding="utf-8")

            self.logger.info("⚠️ Created fallback frontend with basic navigation")
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
