#!/usr/bin/env python3
"""
Test script to create developer user via API.

This script tests the signup API endpoint to create the developer user account.
"""

import requests
import json

def test_signup_api():
    """Test the signup API endpoint."""
    try:
        print("🚀 Testing Monkey Coder Signup API")
        print("=" * 50)
        
        # API endpoint
        url = "http://localhost:8000/api/auth/signup"
        
        # User data
        user_data = {
            "username": "GaryOcean",
            "name": "Braden James Lang",
            "email": "braden.lang77@gmail.com",
            "password": "I.Am.Dev.1",
            "plan": "pro"
        }
        
        print("Creating developer user account...")
        print(f"Username: {user_data['username']}")
        print(f"Full Name: {user_data['name']}")
        print(f"Email: {user_data['email']}")
        print(f"Plan: {user_data['plan']}")
        print()
        
        # Make API call
        response = requests.post(
            url,
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ User created successfully!")
            print(f"User ID: {result.get('user', {}).get('id', 'N/A')}")
            print(f"Email: {result.get('user', {}).get('email', 'N/A')}")
            print(f"Name: {result.get('user', {}).get('name', 'N/A')}")
            print(f"Credits: {result.get('user', {}).get('credits', 'N/A')}")
            print(f"Subscription: {result.get('user', {}).get('subscription_tier', 'N/A')}")
            print(f"Is Developer: {result.get('user', {}).get('is_developer', 'N/A')}")
            return True
        else:
            error_msg = "Unknown error"
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', str(error_data))
            except:
                error_msg = response.text
            
            print(f"❌ Failed to create user: {error_msg}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the Monkey Coder API server is running at http://localhost:8000")
        print("   You can start it with: cd packages/core && python -m uvicorn monkey_coder.app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_login_api():
    """Test login after signup."""
    try:
        print("\n🔐 Testing Login API")
        print("=" * 30)
        
        url = "http://localhost:8000/api/auth/login"
        
        login_data = {
            "email": "braden.lang77@gmail.com",
            "password": "I.Am.Dev.1"
        }
        
        print("Attempting to login...")
        
        response = requests.post(
            url,
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Login successful!")
            print(f"Access token: {result.get('access_token', 'N/A')[:50]}...")
            print(f"User ID: {result.get('user', {}).get('id', 'N/A')}")
            return True
        else:
            error_msg = "Unknown error"
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', str(error_data))
            except:
                error_msg = response.text
            
            print(f"❌ Login failed: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Login test error: {str(e)}")
        return False

if __name__ == "__main__":
    signup_success = test_signup_api()
    
    if signup_success:
        print("\n" + "="*50)
        print("✅ Signup test completed successfully!")
        print("\nNext steps:")
        print("1. You can now login with:")
        print("   Email: braden.lang77@gmail.com")
        print("   Password: I.Am.Dev.1")
        print("2. Test the login endpoint:")
        
        # Test login
        test_login_api()
    else:
        print("\n❌ Signup test failed!")
        print("\nTroubleshooting:")
        print("1. Make sure the API server is running")
        print("2. Check if the database is properly configured")
        print("3. Verify the signup endpoint is working")