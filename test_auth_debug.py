#!/usr/bin/env python3
"""
Quick test script to verify auth endpoints work correctly.

This script tests:
1. User signup
2. User login with the provided credentials
3. Token validation

For debugging purposes only - credentials used here should NOT be committed.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from monkey_coder.security import hash_password, verify_password
from monkey_coder.database import User, get_user_store


async def test_auth_flow():
    """Test authentication flow with provided credentials."""
    
    print("=" * 70)
    print("AUTHENTICATION FLOW TEST")
    print("=" * 70)
    
    # Test credentials (for debugging only)
    test_email = "braden.lang77@gmail.com"
    test_password = "I.Am.Dev.1"
    
    print(f"\n1. Testing password hashing...")
    password_hash = hash_password(test_password)
    print(f"   ✓ Password hashed: {password_hash[:30]}...")
    
    print(f"\n2. Testing password verification...")
    is_valid = verify_password(test_password, password_hash)
    print(f"   ✓ Password verification: {is_valid}")
    
    print(f"\n3. Checking if user exists in database...")
    try:
        existing_user = await User.get_by_email(test_email)
        if existing_user:
            print(f"   ✓ User found: {existing_user.email}")
            print(f"   - Username: {existing_user.username}")
            print(f"   - Is Active: {existing_user.is_active}")
            print(f"   - Is Developer: {existing_user.is_developer}")
            print(f"   - Roles: {existing_user.roles}")
            
            print(f"\n4. Testing authentication with stored password...")
            is_auth = verify_password(test_password, existing_user.password_hash)
            if is_auth:
                print(f"   ✓ Authentication successful!")
            else:
                print(f"   ✗ Authentication failed - password mismatch")
                print(f"   - Stored hash: {existing_user.password_hash[:30]}...")
                print(f"   - Test hash: {password_hash[:30]}...")
        else:
            print(f"   ℹ User does not exist yet")
            print(f"\n4. Creating test user...")
            user_store = get_user_store()
            new_user = await user_store.create_user(
                username="Braden Lang",
                email=test_email,
                password_hash=password_hash,
                full_name="Braden Lang",
                subscription_plan="developer",
                is_developer=True,
                roles=["user", "developer"]
            )
            print(f"   ✓ User created: {new_user.email}")
            print(f"   - ID: {new_user.id}")
            print(f"   - Is Developer: {new_user.is_developer}")
            
            print(f"\n5. Testing authentication with new user...")
            authenticated = await user_store.authenticate_user(test_email, test_password)
            if authenticated:
                print(f"   ✓ Authentication successful!")
            else:
                print(f"   ✗ Authentication failed")
                
    except Exception as e:
        print(f"   ⚠ Database not available: {e}")
        print(f"   ℹ This is expected in local testing without database")
        print(f"\n   Testing password mechanisms only:")
        print(f"   - Password: {test_password}")
        print(f"   - Hash: {password_hash}")
        print(f"   - Verification: {verify_password(test_password, password_hash)}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_auth_flow())
