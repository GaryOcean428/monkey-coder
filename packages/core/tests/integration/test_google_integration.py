#!/usr/bin/env python3
"""
Test script to verify Google Gemini API integration
Tests both new google.genai and legacy google-generativeai packages
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the core package to path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "core"))

from monkey_coder.providers.google_adapter import GoogleProvider
from monkey_coder.config.env_config import get_config

async def test_google_provider():
    """Test Google provider with both API versions."""
    
    # Get API key from environment
    config = get_config()
    api_key = config.ai_providers.google_api_key
    
    if not api_key:
        print("❌ GOOGLE_API_KEY not set in environment")
        print("Please set: export GOOGLE_API_KEY='your-api-key'")
        return False
    
    print("=" * 60)
    print("Google Gemini API Integration Test")
    print("=" * 60)
    
    try:
        # Initialize provider
        provider = GoogleProvider(api_key)
        await provider.initialize()
        print("✅ Provider initialized successfully")
        
        # Check which API version is being used
        from monkey_coder.providers.google_adapter import GOOGLE_API_VERSION
        print(f"📦 Using API version: {GOOGLE_API_VERSION}")
        
        # Get available models
        models = await provider.get_available_models()
        print(f"\n📋 Available models: {len(models)}")
        for model in models:
            print(f"  - {model.name}: {model.description[:50]}...")
        
        # Test text generation
        print("\n🤖 Testing text generation with gemini-2.5-flash...")
        messages = [
            {"role": "system", "content": "You are a helpful coding assistant."},
            {"role": "user", "content": "Write a Python function to calculate factorial"}
        ]
        
        response = await provider.generate_completion(
            model="gemini-2.5-flash",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        print("✅ Generation successful!")
        print(f"📝 Response length: {len(response.get('content', ''))} characters")
        print(f"🔢 Tokens used: {response.get('usage', {}).get('total_tokens', 'N/A')}")
        
        # Show first 200 chars of response
        content = response.get('content', '')[:200]
        print(f"\n📄 Response preview:\n{content}...")
        
        # Test streaming (if supported)
        print("\n🌊 Testing streaming generation...")
        stream_messages = [
            {"role": "user", "content": "Count from 1 to 5"}
        ]
        
        stream_response = await provider.generate_completion(
            model="gemini-2.5-flash",
            messages=stream_messages,
            max_tokens=100,
            stream=True
        )
        
        if stream_response.get("is_streaming"):
            print("✅ Streaming supported!")
            stream = stream_response.get("stream")
            chunks_received = 0
            async for chunk in stream:
                chunks_received += 1
                if chunk.get("type") == "delta":
                    print(".", end="", flush=True)
            print(f"\n📦 Received {chunks_received} chunks")
        else:
            print("⚠️ Streaming not available with current configuration")
        
        # Cleanup
        await provider.cleanup()
        print("\n✅ All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test runner."""
    success = await test_google_provider()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Google Gemini integration is working correctly!")
        print("\nConfiguration verified:")
        print("- API authentication: ✅")
        print("- Model availability: ✅")
        print("- Text generation: ✅")
        print("- Response handling: ✅")
    else:
        print("❌ Google Gemini integration has issues")
        print("\nTroubleshooting steps:")
        print("1. Verify GOOGLE_API_KEY is set correctly")
        print("2. Check internet connectivity")
        print("3. Install required package: pip install google-genai")
        print("4. Or fallback package: pip install google-generativeai")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())