#!/usr/bin/env python3
"""
Test script for direct Monkey Coder backend API access.

This script demonstrates how to integrate with the Monkey Coder backend
from external Python projects.
"""

import requests
import json
import os
from typing import Dict, Any, Optional

class MonkeyCoderBackendClient:
    """Client for direct backend API access."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            })
    
    def create_dev_api_key(self) -> Dict[str, Any]:
        """Create a development API key (no authentication required)."""
        response = self.session.post(f"{self.base_url}/api/v1/auth/keys/dev")
        response.raise_for_status()
        return response.json()
    
    def check_health(self) -> Dict[str, Any]:
        """Check backend health status."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_auth_status(self) -> Dict[str, Any]:
        """Check authentication status."""
        if not self.api_key:
            raise ValueError("API key required for authentication check")
        
        response = self.session.get(f"{self.base_url}/api/v1/auth/status")
        response.raise_for_status()
        return response.json()
    
    def execute_task(self, 
                    prompt: str, 
                    task_type: str = "code_generation",
                    persona: str = "developer",
                    **kwargs) -> Dict[str, Any]:
        """Execute an AI task."""
        if not self.api_key:
            raise ValueError("API key required for task execution")
        
        task_data = {
            "task_id": f"api-task-{hash(prompt) % 1000000}",
            "task_type": task_type,
            "prompt": prompt,
            "context": {
                "user_id": "api-user",
                "session_id": f"session-{hash(prompt) % 1000}",
                "environment": "direct-backend-access",
                **kwargs.get("context", {})
            },
            "persona_config": {
                "persona": persona,
                **kwargs.get("persona_config", {})
            },
            **{k: v for k, v in kwargs.items() if k not in ["context", "persona_config"]}
        }
        
        response = self.session.post(f"{self.base_url}/api/v1/execute", json=task_data)
        response.raise_for_status()
        return response.json()
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get system capabilities."""
        response = self.session.get(f"{self.base_url}/api/v1/capabilities")
        response.raise_for_status()
        return response.json()

def main():
    """Demonstrate backend API access."""
    print("🐒 Monkey Coder Backend API Access Test\n")
    
    # Initialize client
    client = MonkeyCoderBackendClient()
    
    # Test 1: Health check
    print("1. Testing backend health...")
    try:
        health = client.check_health()
        print(f"   ✓ Backend is {health['status']}")
        print(f"   ✓ Version: {health['version']}")
    except Exception as e:
        print(f"   ✗ Health check failed: {e}")
        return
    
    # Test 2: Create API key
    print("\n2. Creating development API key...")
    try:
        key_data = client.create_dev_api_key()
        api_key = key_data['key']
        print(f"   ✓ Created API key: {api_key[:20]}...")
        
        # Update client with new key
        client.api_key = api_key
        client.session.headers.update({"Authorization": f"Bearer {api_key}"})
        
    except Exception as e:
        print(f"   ✗ API key creation failed: {e}")
        return
    
    # Test 3: Authentication status
    print("\n3. Testing authentication...")
    try:
        auth_status = client.get_auth_status()
        if auth_status.get('authenticated'):
            user = auth_status.get('user', {})
            print(f"   ✓ Authenticated as: {user.get('name', 'Unknown')}")
            print(f"   ✓ Subscription tier: {user.get('subscription_tier', 'Unknown')}")
            print(f"   ✓ Credits: ${(user.get('credits', 0) / 100):.2f}")
        else:
            print("   ✗ Authentication failed")
            return
    except Exception as e:
        print(f"   ✗ Authentication check failed: {e}")
        return
    
    # Test 4: Get capabilities
    print("\n4. Getting system capabilities...")
    try:
        capabilities = client.get_capabilities()
        print(f"   ✓ Available features: {len(capabilities.get('features', []))}")
        print(f"   ✓ Available models: {len(capabilities.get('models', []))}")
    except Exception as e:
        print(f"   ✗ Capabilities check failed: {e}")
    
    # Test 5: Execute a simple task
    print("\n5. Testing task execution...")
    try:
        result = client.execute_task(
            prompt="Create a simple Hello World function in Python",
            task_type="code_generation"
        )
        
        task_id = result.get('task_id', 'Unknown')
        status = result.get('status', 'Unknown')
        confidence = result.get('confidence', 0)
        
        print(f"   ✓ Task executed: {task_id}")
        print(f"   ✓ Status: {status}")
        print(f"   ✓ Confidence: {confidence}%")
        
        # Show first 100 chars of result if available
        if 'result' in result:
            result_text = str(result['result'])[:100]
            print(f"   ✓ Result preview: {result_text}...")
            
    except Exception as e:
        print(f"   ✗ Task execution failed: {e}")
    
    print(f"\n✅ Backend API access test completed!")
    print(f"🔑 API Key: {api_key}")
    print(f"📚 Full documentation: BACKEND_API_ACCESS.md")

if __name__ == "__main__":
    main()