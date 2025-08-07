#!/usr/bin/env python3
"""
Script to create developer user account.

This script creates the developer user account for Braden James Lang.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the packages/core directory to the Python path
core_path = Path(__file__).parent / "packages" / "core"
sys.path.insert(0, str(core_path))

from monkey_coder.database import get_user_store, User
from monkey_coder.security import hash_password

async def create_developer_user():
    """Create the developer user account."""
    try:
        print("Creating developer user account...")
        
        # User details
        username = "GaryOcean"
        full_name = "Braden James Lang"
        email = "braden.lang77@gmail.com"
        password = "I.Am.Dev.1"  # This will be hashed
        
        # Check if user already exists
        existing_user = await User.get_by_email(email.lower())
        if existing_user:
            print(f"User with email {email} already exists!")
            print(f"Existing user: {existing_user.username} ({existing_user.full_name})")
            return existing_user
        
        # Check if username already exists
        existing_username = await User.get_by_username(username)
        if existing_username:
            print(f"Username '{username}' already taken!")
            print(f"Existing user: {existing_username.username} ({existing_username.full_name})")
            return existing_username
        
        # Hash password
        password_hash = hash_password(password)
        
        # Get user store
        user_store = get_user_store()
        
        # Create developer user with appropriate roles
        new_user = await user_store.create_user(
            username=username,
            email=email.lower(),
            password_hash=password_hash,
            full_name=full_name,
            subscription_plan="pro",
            is_developer=True,
            roles=["developer", "api_user", "admin"],
        )
        
        print(f"✅ Successfully created developer user:")
        print(f"   ID: {new_user.id}")
        print(f"   Username: {new_user.username}")
        print(f"   Full Name: {new_user.full_name}")
        print(f"   Email: {new_user.email}")
        print(f"   Is Developer: {new_user.is_developer}")
        print(f"   Roles: {new_user.roles}")
        print(f"   Subscription Plan: {new_user.subscription_plan}")
        
        return new_user
        
    except Exception as e:
        print(f"❌ Error creating developer user: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Main function."""
    print("🚀 Monkey Coder - Developer User Creation Script")
    print("=" * 50)
    
    user = await create_developer_user()
    
    if user:
        print("\n✅ Developer user creation completed successfully!")
        print(f"\nYou can now log in with:")
        print(f"  Email: braden.lang77@gmail.com")
        print(f"  Username: GaryOcean")
        print(f"  Password: I.Am.Dev.1")
    else:
        print("\n❌ Developer user creation failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())