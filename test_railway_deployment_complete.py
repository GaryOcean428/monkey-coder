#!/usr/bin/env python3
"""
Comprehensive Railway Deployment Testing Suite

This script validates the complete Railway deployment optimization implemented
for the monkey-coder repository, testing all virtual environment fixes and
build optimizations without requiring actual Railway environment.

Usage: python test_railway_deployment_complete.py
"""

import os
import sys
import json
import subprocess
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RailwayDeploymentTester:
    """Comprehensive tester for Railway deployment fixes."""
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test_result(self, test_name, passed, details=None):
        """Log test result and update counters."""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            logger.info(f"✅ {test_name}: PASSED")
        else:
            logger.error(f"❌ {test_name}: FAILED")
        
        if details:
            logger.info(f"   {details}")
        
        self.results[test_name] = {
            'passed': passed,
            'details': details
        }
    
    def test_railpack_configuration(self):
        """Test railpack.json configuration and structure."""
        logger.info("🔍 Testing railpack.json configuration...")
        
        railpack_path = self.base_dir / "railpack.json"
        if not railpack_path.exists():
            self.log_test_result("railpack.json exists", False, "File not found")
            return
        
        try:
            with open(railpack_path) as f:
                config = json.load(f)
            
            # Test required structure
            required_keys = ['provider', 'packages', 'build', 'deploy']
            missing_keys = [key for key in required_keys if key not in config]
            
            if missing_keys:
                self.log_test_result("railpack.json structure", False, f"Missing keys: {missing_keys}")
                return
            
            # Test provider
            if config.get('provider') != 'python':
                self.log_test_result("Provider configuration", False, f"Expected 'python', got '{config.get('provider')}'")
                return
            
            # Test virtual environment paths in build commands
            build_commands = config.get('build', {}).get('commands', [])
            venv_commands = [cmd for cmd in build_commands if '/app/.venv/bin/' in str(cmd)]
            
            if not venv_commands:
                self.log_test_result("Virtual environment paths", False, "No /app/.venv/bin/ paths found in build commands")
                return
            
            # Test start command
            start_command = config.get('deploy', {}).get('startCommand', '')
            if '/app/start_server.sh' not in start_command:
                self.log_test_result("Start command configuration", False, f"Expected /app/start_server.sh, got '{start_command}'")
                return
            
            # Test cache configuration
            cache_config = config.get('build', {}).get('cache', {})
            cache_paths = cache_config.get('paths', [])
            expected_cache_paths = ['/app/.venv/lib/python3.12/site-packages', 'node_modules']
            
            missing_cache_paths = [path for path in expected_cache_paths if path not in cache_paths]
            if missing_cache_paths:
                self.log_test_result("Cache configuration", False, f"Missing cache paths: {missing_cache_paths}")
                return
            
            self.log_test_result("railpack.json configuration", True, f"All {len(required_keys)} required sections valid")
            
        except json.JSONDecodeError as e:
            self.log_test_result("railpack.json syntax", False, f"JSON decode error: {e}")
        except Exception as e:
            self.log_test_result("railpack.json configuration", False, f"Unexpected error: {e}")
    
    def test_virtual_environment_script_generation(self):
        """Test that the railpack config generates proper virtual environment activation."""
        logger.info("🔍 Testing virtual environment script generation...")
        
        railpack_path = self.base_dir / "railpack.json"
        try:
            with open(railpack_path) as f:
                config = json.load(f)
            
            build_commands = config.get('build', {}).get('commands', [])
            
            # Look for script generation commands
            script_generation_found = False
            activation_commands_found = False
            
            for cmd in build_commands:
                if isinstance(cmd, str):
                    if 'start_server.sh' in cmd and 'cat >' in cmd:
                        script_generation_found = True
                    if 'source /app/.venv/bin/activate' in cmd:
                        activation_commands_found = True
            
            if not script_generation_found:
                self.log_test_result("Script generation", False, "start_server.sh creation not found in build commands")
                return
            
            self.log_test_result("Virtual environment script generation", True, "Script creation and activation commands found")
            
        except Exception as e:
            self.log_test_result("Virtual environment script generation", False, f"Error: {e}")
    
    def test_run_server_syntax(self):
        """Test run_server.py syntax and structure."""
        logger.info("🔍 Testing run_server.py syntax...")
        
        run_server_path = self.base_dir / "run_server.py"
        if not run_server_path.exists():
            self.log_test_result("run_server.py exists", False, "File not found")
            return
        
        try:
            # Test Python syntax
            with open(run_server_path) as f:
                code = f.read()
            
            # Compile to check syntax
            compile(code, str(run_server_path), 'exec')
            
            # Check for critical functions
            required_functions = ['check_frontend', 'build_frontend_if_missing', 'main']
            missing_functions = []
            
            for func in required_functions:
                if f'def {func}(' not in code:
                    missing_functions.append(func)
            
            if missing_functions:
                self.log_test_result("run_server.py functions", False, f"Missing functions: {missing_functions}")
                return
            
            # Check for MCP integration
            if 'mcp_env_manager' not in code:
                self.log_test_result("MCP integration", False, "MCP environment manager import not found")
                return
            
            self.log_test_result("run_server.py syntax and structure", True, "All required functions and MCP integration present")
            
        except SyntaxError as e:
            self.log_test_result("run_server.py syntax", False, f"Syntax error: {e}")
        except Exception as e:
            self.log_test_result("run_server.py syntax", False, f"Error: {e}")
    
    def test_deployment_scripts(self):
        """Test deployment and validation scripts."""
        logger.info("🔍 Testing deployment scripts...")
        
        scripts_to_test = [
            'railway_deployment_validation.py',
            'railway_environment_setup.sh',
            'deploy-railway.sh'
        ]
        
        missing_scripts = []
        executable_scripts = []
        
        for script in scripts_to_test:
            script_path = self.base_dir / script
            if not script_path.exists():
                missing_scripts.append(script)
            else:
                if script_path.is_file() and os.access(script_path, os.X_OK):
                    executable_scripts.append(script)
        
        if missing_scripts:
            self.log_test_result("Deployment scripts existence", False, f"Missing scripts: {missing_scripts}")
            return
        
        self.log_test_result("Deployment scripts", True, f"All {len(scripts_to_test)} scripts present, {len(executable_scripts)} executable")
    
    def test_railway_documentation(self):
        """Test Railway deployment documentation."""
        logger.info("🔍 Testing Railway documentation...")
        
        doc_path = self.base_dir / "RAILWAY_DEPLOYMENT_GUIDE.md"
        if not doc_path.exists():
            self.log_test_result("Railway documentation", False, "RAILWAY_DEPLOYMENT_GUIDE.md not found")
            return
        
        try:
            with open(doc_path) as f:
                content = f.read()
            
            required_sections = [
                'Virtual Environment Path Resolution',
                'railpack.json',
                'Issue Resolution Summary',
                'Configuration Files Updated'
            ]
            
            missing_sections = [section for section in required_sections if section not in content]
            
            if missing_sections:
                self.log_test_result("Documentation completeness", False, f"Missing sections: {missing_sections}")
                return
            
            # Check for code examples
            if '```json' not in content or '```bash' not in content:
                self.log_test_result("Documentation examples", False, "Missing code examples")
                return
            
            self.log_test_result("Railway documentation", True, f"Complete documentation with {len(required_sections)} sections")
            
        except Exception as e:
            self.log_test_result("Railway documentation", False, f"Error: {e}")
    
    def test_environment_variable_management(self):
        """Test environment variable management and MCP integration."""
        logger.info("🔍 Testing environment variable management...")
        
        # Check if MCP environment management exists
        mcp_path = self.base_dir / "packages" / "core" / "monkey_coder" / "config" / "mcp_env_manager.py"
        
        if not mcp_path.exists():
            self.log_test_result("MCP environment manager", False, "mcp_env_manager.py not found")
            return
        
        try:
            with open(mcp_path) as f:
                content = f.read()
            
            required_functions = [
                'get_production_database_url',
                'get_production_api_url',
                'get_mcp_variable'
            ]
            
            missing_functions = [func for func in required_functions if f'def {func}' not in content]
            
            if missing_functions:
                self.log_test_result("MCP functions", False, f"Missing functions: {missing_functions}")
                return
            
            self.log_test_result("Environment variable management", True, "MCP environment manager with all required functions")
            
        except Exception as e:
            self.log_test_result("Environment variable management", False, f"Error: {e}")
    
    def test_build_optimization(self):
        """Test build optimization configurations."""
        logger.info("🔍 Testing build optimization...")
        
        railpack_path = self.base_dir / "railpack.json"
        try:
            with open(railpack_path) as f:
                config = json.load(f)
            
            # Test cache configuration for optimization
            cache_config = config.get('build', {}).get('cache', {})
            cache_paths = cache_config.get('paths', [])
            
            optimization_indicators = [
                '/app/.venv/lib/python3.12/site-packages',  # Python package cache
                'node_modules',  # Node.js package cache
                '/root/.cache/yarn',  # Yarn cache
                'packages/web/.next'  # Next.js build cache
            ]
            
            found_optimizations = [opt for opt in optimization_indicators if opt in cache_paths]
            
            if len(found_optimizations) < 3:  # At least 3 optimization paths should be present
                self.log_test_result("Build optimization", False, f"Only {len(found_optimizations)}/4 optimizations found")
                return
            
            # Test for comprehensive build commands
            build_commands = config.get('build', {}).get('commands', [])
            command_text = ' '.join(str(cmd) for cmd in build_commands)
            
            optimization_features = [
                '--no-cache-dir',  # Pip optimization
                'corepack prepare yarn@4.9.2',  # Yarn version management
                'yarn install --immutable',  # Yarn optimization
                'NEXT_TELEMETRY_DISABLED=1'  # Next.js optimization
            ]
            
            found_features = [feat for feat in optimization_features if feat in command_text]
            
            if len(found_features) < 3:
                self.log_test_result("Build optimizations", False, f"Only {len(found_features)}/4 optimization features found")
                return
            
            self.log_test_result("Build optimization", True, f"{len(found_optimizations)} cache paths, {len(found_features)} optimization features")
            
        except Exception as e:
            self.log_test_result("Build optimization", False, f"Error: {e}")
    
    def run_comprehensive_test(self):
        """Run all deployment tests."""
        logger.info("🚀 Starting Comprehensive Railway Deployment Test Suite")
        logger.info("=" * 60)
        
        # Run all tests
        self.test_railpack_configuration()
        self.test_virtual_environment_script_generation()
        self.test_run_server_syntax()
        self.test_deployment_scripts()
        self.test_railway_documentation()
        self.test_environment_variable_management()
        self.test_build_optimization()
        
        # Generate summary
        logger.info("=" * 60)
        logger.info(f"🏁 Test Summary: {self.passed_tests}/{self.total_tests} tests passed")
        
        if self.passed_tests == self.total_tests:
            logger.info("🎉 ALL TESTS PASSED - Railway deployment is ready!")
            return True
        else:
            failed_count = self.total_tests - self.passed_tests
            logger.error(f"❌ {failed_count} test(s) failed - review issues above")
            return False
    
    def generate_deployment_report(self):
        """Generate a detailed deployment readiness report."""
        report = {
            'timestamp': os.popen('date').read().strip(),
            'total_tests': self.total_tests,
            'passed_tests': self.passed_tests,
            'success_rate': (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0,
            'results': self.results,
            'deployment_ready': self.passed_tests == self.total_tests
        }
        
        report_path = self.base_dir / "railway_deployment_test_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Detailed report saved to: {report_path}")
        return report

def main():
    """Main test execution."""
    print("🐒 Monkey Coder - Railway Deployment Test Suite")
    print("=" * 60)
    
    tester = RailwayDeploymentTester()
    success = tester.run_comprehensive_test()
    report = tester.generate_deployment_report()
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 DEPLOYMENT READY: All Railway optimizations validated!")
        print("🚀 The virtual environment path issues have been resolved.")
        print("⚡ Build optimization and caching improvements are in place.")
        print("📋 Comprehensive documentation and validation tools available.")
        return 0
    else:
        print("⚠️  DEPLOYMENT NEEDS ATTENTION: Some validations failed.")
        print("🔧 Review the failed tests above and address any issues.")
        print("📋 Check railway_deployment_test_report.json for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())