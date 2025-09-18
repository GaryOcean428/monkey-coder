#!/usr/bin/env python3
"""
Script to update developer user permissions to maximum level.

This script ensures the developer user has all possible permissions.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the packages/core directory to the Python path
core_path = Path(__file__).parent / "packages" / "core"
sys.path.insert(0, str(core_path))

from monkey_coder.database import get_user_store, User
from monkey_coder.security import UserRole, Permission, get_user_permissions

async def update_developer_user_permissions():
    """Update the developer user to have maximum permissions."""
    try:
        print("🔧 Updating Developer User Permissions")
        print("=" * 50)
        
        email = "braden.lang77@gmail.com"
        
        # Get existing user
        user = await User.get_by_email(email.lower())
        if not user:
            print(f"❌ User with email {email} not found!")
            return False
        
        print(f"📋 Current user details:")
        print(f"   ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   Full Name: {user.full_name}")
        print(f"   Email: {user.email}")
        print(f"   Current Roles: {user.roles}")
        print(f"   Is Developer: {user.is_developer}")
        print(f"   Subscription Plan: {user.subscription_plan}")
        
        # Update to have maximum permissions
        new_roles = [UserRole.ADMIN, UserRole.DEVELOPER, UserRole.API_USER]
        
        # Calculate all permissions for these roles
        all_permissions = get_user_permissions(new_roles)
        
        print(f"\n🚀 Updating user permissions...")
        print(f"   New Roles: {[role.value for role in new_roles]}")
        print(f"   Total Permissions: {len(all_permissions)}")
        print(f"   Permissions: {[perm.value for perm in all_permissions]}")
        
        # Update the user
        await user.update(
            roles=[role.value for role in new_roles],
            is_developer=True,
            subscription_plan="pro"
        )
        
        # Verify the update
        updated_user = await User.get_by_email(email.lower())
        if updated_user:
            print(f"\n✅ User updated successfully!")
            print(f"   Updated Roles: {updated_user.roles}")
            print(f"   Is Developer: {updated_user.is_developer}")
            print(f"   Subscription Plan: {updated_user.subscription_plan}")
            
            # Calculate permissions again to show final state
            updated_permissions = get_user_permissions([UserRole(role) for role in updated_user.roles if role in [r.value for r in UserRole]])
            print(f"   Final Permissions: {[perm.value for perm in updated_permissions]}")
            
            return True
        else:
            print(f"❌ Failed to verify user update!")
            return False
        
    except Exception as e:
        print(f"❌ Error updating developer user permissions: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function."""
    print("🚀 Monkey Coder - Developer User Permissions Update")
    print("=" * 60)
    
    success = await update_developer_user_permissions()
    
    if success:
        print("\n✅ Developer user permissions updated successfully!")
        print(f"\nThe user braden.lang77@gmail.com now has:")
        print(f"  - Admin permissions (full system access)")
        print(f"  - Developer permissions (code execution, sandbox access)")
        print(f"  - API User permissions (API access)")
        print(f"  - Pro subscription plan")
    else:
        print("\n❌ Developer user permissions update failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())