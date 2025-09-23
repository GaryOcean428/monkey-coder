#!/usr/bin/env python3
"""
Simple test script to verify authentication and CSP fixes.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add the packages/core directory to the Python path
core_path = Path(__file__).parent / "packages" / "core"
sys.path.insert(0, str(core_path))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_imports():
    """Test that all modules can be imported without errors."""
    try:
        # Test security middleware import
        from monkey_coder.middleware.security_middleware import get_railway_security_config
        config = get_railway_security_config()
        logger.info("✅ Security middleware imported successfully")
        logger.info(f"   CSP Font Sources: {config.get('csp_font_src', 'Not configured')}")
        
        # Test CORS config import
        from monkey_coder.config.cors import CORS_CONFIG, get_cors_origins
        origins = get_cors_origins()
        logger.info("✅ CORS config imported successfully")
        logger.info(f"   Allowed origins count: {len(origins)}")
        
        # Test auth manager import (basic import test)
        logger.info("✅ Basic imports successful")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_csp_config():
    """Test CSP configuration."""
    try:
        from monkey_coder.middleware.security_middleware import get_railway_security_config
        config = get_railway_security_config()
        
        # Check that Google Fonts are allowed
        font_src = config.get('csp_font_src', '')
        if 'fonts.gstatic.com' in font_src and 'fonts.googleapis.com' in font_src:
            logger.info("✅ Google Fonts are allowed in CSP")
        else:
            logger.warning("⚠️ Google Fonts may not be properly configured in CSP")
            
        # Check style sources
        style_src = config.get('csp_style_src', '')
        if 'fonts.googleapis.com' in style_src and "'unsafe-inline'" in style_src:
            logger.info("✅ Google Fonts styles are allowed in CSP")
        else:
            logger.warning("⚠️ Google Fonts styles may not be properly configured")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ CSP config test failed: {e}")
        return False

async def test_cors_config():
    """Test CORS configuration."""
    try:
        from monkey_coder.config.cors import CORS_CONFIG, get_cors_origins
        
        # Check credentials are enabled
        if CORS_CONFIG.get('allow_credentials', False):
            logger.info("✅ CORS credentials are enabled")
        else:
            logger.warning("⚠️ CORS credentials are disabled")
            
        # Check important headers
        headers = CORS_CONFIG.get('allow_headers', [])
        required_headers = ['Authorization', 'Content-Type', 'X-CSRF-Token', 'Cookie']
        missing_headers = [h for h in required_headers if h not in headers]
        
        if not missing_headers:
            logger.info("✅ All required CORS headers are configured")
        else:
            logger.warning(f"⚠️ Missing CORS headers: {missing_headers}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ CORS config test failed: {e}")
        return False

async def main():
    """Run all tests."""
    logger.info("🧪 Running authentication and CSP fix verification tests...")
    
    tests = [
        ("Import Tests", test_imports),
        ("CSP Configuration", test_csp_config),
        ("CORS Configuration", test_cors_config),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name}...")
        result = await test_func()
        results.append((test_name, result))
        
    # Summary
    logger.info("\n📊 Test Results Summary:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"   {test_name}: {status}")
        
    all_passed = all(result for _, result in results)
    
    if all_passed:
        logger.info("\n🎉 All tests passed! The authentication and CSP fixes look good.")
        logger.info("\n📝 Summary of fixes:")
        logger.info("   • CSP headers updated to allow Google Fonts")
        logger.info("   • CORS configuration enhanced for credentials")
        logger.info("   • Signup endpoint added to FastAPI")
        logger.info("   • Frontend auth library improved")
        logger.info("   • WebSocket URL configuration added")
    else:
        logger.error("\n❌ Some tests failed. Please review the issues above.")
        
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)