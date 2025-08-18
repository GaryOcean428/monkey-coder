#!/usr/bin/env python3
"""
Setup script to ensure user exists with specified credentials.
Run this to create or update the user account.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "packages" / "core"))

# Set the database URL
os.environ["DATABASE_URL"] = "postgresql://postgres:TgUReBkJMiDnpgHXvxadAmnTOAPxUYve@ballast.proxy.rlwy.net:19027/railway"

import asyncpg
import bcrypt
from datetime import datetime, timezone

async def setup_user():
    """Create or update user with specified credentials."""
    
    # User details
    email = "braden.lang77@gmail.com"
    password = "I.Am.Dev.1"
    username = "braden"
    
    # Hash the password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Connect to database
    db_url = os.environ["DATABASE_URL"]
    print(f"Connecting to database...")
    
    try:
        conn = await asyncpg.connect(db_url)
        
        # Check if users table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            );
        """)
        
        if not table_exists:
            print("Creating users table...")
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    is_active BOOLEAN DEFAULT true,
                    is_admin BOOLEAN DEFAULT false,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("Users table created.")
        
        # First, let's check the table structure
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """)
        
        print("Table structure:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']}")
        
        # Check if user exists
        existing_user = await conn.fetchrow(
            "SELECT id, email, username FROM users WHERE email = $1",
            email
        )
        
        if existing_user:
            print(f"\nUser exists: {existing_user['email']}")
            # Update password - check if updated_at column exists
            has_updated_at = any(col['column_name'] == 'updated_at' for col in columns)
            
            if has_updated_at:
                await conn.execute(
                    """
                    UPDATE users 
                    SET password_hash = $1, updated_at = $2
                    WHERE email = $3
                    """,
                    password_hash,
                    datetime.now(timezone.utc),
                    email
                )
            else:
                await conn.execute(
                    """
                    UPDATE users 
                    SET password_hash = $1
                    WHERE email = $2
                    """,
                    password_hash,
                    email
                )
            print(f"✅ Password updated for {email}")
        else:
            # Create new user - check which columns exist
            has_is_active = any(col['column_name'] == 'is_active' for col in columns)
            
            if has_is_active:
                await conn.execute(
                    """
                    INSERT INTO users (email, username, password_hash, is_active)
                    VALUES ($1, $2, $3, $4)
                    """,
                    email,
                    username,
                    password_hash,
                    True
                )
            else:
                await conn.execute(
                    """
                    INSERT INTO users (email, username, password_hash)
                    VALUES ($1, $2, $3)
                    """,
                    email,
                    username,
                    password_hash
                )
            print(f"✅ User created: {email}")
        
        # Verify the user can be retrieved
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE email = $1",
            email
        )
        
        if user:
            print(f"\n📊 User Details:")
            print(f"   ID: {user['id']}")
            print(f"   Email: {user['email']}")
            print(f"   Username: {user['username']}")
            if 'is_active' in user:
                print(f"   Active: {user['is_active']}")
            print(f"\n✅ User setup complete!")
            print(f"   Email: {email}")
            print(f"   Password: {password}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def test_login():
    """Test that login works with the credentials."""
    email = "braden.lang77@gmail.com"
    password = "I.Am.Dev.1"
    
    print(f"\n🔐 Testing login...")
    
    try:
        conn = await asyncpg.connect(os.environ["DATABASE_URL"])
        
        # Get user with password hash
        user = await conn.fetchrow(
            "SELECT id, email, username, password_hash FROM users WHERE email = $1",
            email
        )
        
        if user:
            # Verify password
            password_valid = bcrypt.checkpw(
                password.encode('utf-8'),
                user['password_hash'].encode('utf-8')
            )
            
            if password_valid:
                print(f"✅ Login successful for {email}")
                return True
            else:
                print(f"❌ Invalid password for {email}")
                return False
        else:
            print(f"❌ User not found: {email}")
            return False
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Login test error: {e}")
        return False

async def main():
    """Main function."""
    print("🚀 Setting up user account...")
    print("=" * 50)
    
    success = await setup_user()
    
    if success:
        await test_login()
    
    print("=" * 50)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())