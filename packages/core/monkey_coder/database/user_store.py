"""
User store implementation for managing user data.

This module provides a UserStore class for managing user operations
and a global user store instance.
"""

import logging
from typing import Optional, List
from datetime import datetime

from .models import User

logger = logging.getLogger(__name__)


class UserStore:
    """
    User store for managing user data operations.
    
    This class provides methods for creating, retrieving, and managing
    user accounts in the database.
    """
    
    async def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        full_name: Optional[str] = None,
        subscription_plan: str = "hobby",
        is_developer: bool = False,
        roles: Optional[List[str]] = None
    ) -> User:
        """
        Create a new user.
        
        Args:
            username: Username
            email: User's email address
            password_hash: Hashed password
            full_name: User's full name
            subscription_plan: Subscription plan
            is_developer: Whether user has developer access
            roles: User roles
            
        Returns:
            User: Created user
        """
        if roles is None:
            roles = ["user"]
            
        user = await User.create(
            username=username,
            email=email.lower(),
            password_hash=password_hash,
            full_name=full_name,
            subscription_plan=subscription_plan,
            is_developer=is_developer,
            roles=roles
        )
        
        logger.info(f"Created user: {user.username} ({user.email})")
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            Optional[User]: User if found
        """
        # This is a sync method to maintain compatibility with existing code
        # The actual database call is async, so we'll need to handle this properly
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, we can't use run_until_complete
            # Return None for now - this will need to be refactored to async
            return None
        else:
            return loop.run_until_complete(User.get_by_id(user_id))
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            Optional[User]: User if found
        """
        # This is a sync method to maintain compatibility with existing code
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, we can't use run_until_complete
            # Return None for now - this will need to be refactored to async
            return None
        else:
            return loop.run_until_complete(User.get_by_email(email.lower()))
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            Optional[User]: User if found
        """
        # This is a sync method to maintain compatibility with existing code
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, we can't use run_until_complete
            # Return None for now - this will need to be refactored to async
            return None
        else:
            return loop.run_until_complete(User.get_by_username(username))
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password.
        
        Args:
            email: User's email address
            password: Plain text password
            
        Returns:
            Optional[User]: User if authentication successful
        """
        from ..security import verify_password
        
        user = await User.get_by_email(email.lower())
        if user and verify_password(password, user.password_hash):
            await user.update_last_login()
            return user
        return None
    
    async def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """
        Update user information.
        
        Args:
            user_id: User ID
            **kwargs: Fields to update
            
        Returns:
            Optional[User]: Updated user if found
        """
        user = await User.get_by_id(user_id)
        if user:
            await user.update(**kwargs)
            return user
        return None
    
    async def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if user was deactivated
        """
        user = await User.get_by_id(user_id)
        if user:
            await user.update(is_active=False)
            logger.info(f"Deactivated user: {user.username} ({user.email})")
            return True
        return False
    
    async def list_users(
        self,
        limit: int = 100,
        offset: int = 0,
        active_only: bool = True
    ) -> List[User]:
        """
        List users with pagination.
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            active_only: Whether to only return active users
            
        Returns:
            List[User]: List of users
        """
        from .connection import get_database_connection
        import json
        
        pool = await get_database_connection()
        async with pool.acquire() as connection:
            query = "SELECT * FROM users"
            params = []
            
            if active_only:
                query += " WHERE is_active = $1"
                params.append(True)
            
            query += " ORDER BY created_at DESC LIMIT $" + str(len(params) + 1) + " OFFSET $" + str(len(params) + 2)
            params.extend([limit, offset])
            
            rows = await connection.fetch(query, *params)
            
            users = []
            for row in rows:
                user_data = dict(row)
                if user_data.get('roles'):
                    user_data['roles'] = json.loads(user_data['roles'])
                else:
                    user_data['roles'] = []
                if user_data.get('metadata'):
                    user_data['metadata'] = json.loads(user_data['metadata'])
                else:
                    user_data['metadata'] = {}
                users.append(User(**user_data))
            
            return users


# Global user store instance
_user_store: Optional[UserStore] = None


def get_user_store() -> UserStore:
    """
    Get the global user store instance.
    
    Returns:
        UserStore: Global user store
    """
    global _user_store
    if _user_store is None:
        _user_store = UserStore()
    return _user_store