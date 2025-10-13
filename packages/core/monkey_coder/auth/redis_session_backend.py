"""
Redis-backed session storage with in-memory fallback.

This module provides a production-ready session backend using Redis for persistence,
with automatic fallback to in-memory storage if Redis is unavailable.
"""

import json
import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class RedisSessionBackend:
    """Redis session backend with connection pooling and fallback."""
    
    def __init__(self):
        """Initialize Redis backend with lazy connection."""
        self._redis = None
        self._redis_available = False
        self._fallback_storage: Dict[str, str] = {}  # In-memory fallback
        self._connection_attempts = 0
        self._max_connection_attempts = 3
        
    async def connect(self):
        """Connect to Redis with connection pooling."""
        if self._redis is not None:
            return  # Already connected
            
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            logger.info("REDIS_URL not configured, using in-memory session storage")
            self._redis_available = False
            return
        
        try:
            import redis.asyncio as aioredis
            
            # Create Redis connection with pool
            self._redis = await aioredis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            
            # Test connection
            await self._redis.ping()
            self._redis_available = True
            self._connection_attempts = 0
            logger.info("✅ Redis session backend connected successfully")
            
        except ImportError:
            logger.warning("redis package not installed, using in-memory session storage")
            self._redis_available = False
        except Exception as e:
            self._connection_attempts += 1
            logger.error(f"Failed to connect to Redis (attempt {self._connection_attempts}/{self._max_connection_attempts}): {e}")
            
            if self._connection_attempts >= self._max_connection_attempts:
                logger.error("Max Redis connection attempts reached, using in-memory fallback permanently")
            
            self._redis_available = False
            self._redis = None
    
    async def disconnect(self):
        """Gracefully disconnect from Redis."""
        if self._redis:
            try:
                await self._redis.close()
                logger.info("Redis session backend disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting from Redis: {e}")
            finally:
                self._redis = None
                self._redis_available = False
    
    def _serialize_session(self, data: Dict[str, Any]) -> str:
        """Serialize session data to JSON string."""
        # Convert datetime objects to ISO format strings
        serialized = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            else:
                serialized[key] = value
        return json.dumps(serialized)
    
    def _deserialize_session(self, data: str) -> Dict[str, Any]:
        """Deserialize session data from JSON string."""
        parsed = json.loads(data)
        
        # Convert ISO format strings back to datetime objects
        datetime_fields = ['created_at', 'last_activity', 'expires_at']
        for field in datetime_fields:
            if field in parsed and isinstance(parsed[field], str):
                try:
                    parsed[field] = datetime.fromisoformat(parsed[field])
                except Exception:
                    pass
        
        return parsed
    
    async def set(self, session_id: str, data: Dict[str, Any], ttl_seconds: int = 86400):
        """
        Store session data with automatic TTL.
        
        Args:
            session_id: Unique session identifier
            data: Session data dictionary
            ttl_seconds: Time to live in seconds (default: 24 hours)
        """
        key = f"session:{session_id}"
        serialized = self._serialize_session(data)
        
        # Try Redis first
        if self._redis_available and self._redis:
            try:
                await self._redis.setex(key, ttl_seconds, serialized)
                logger.debug(f"Stored session {session_id} in Redis")
                return
            except Exception as e:
                logger.warning(f"Redis set failed, using fallback: {e}")
                self._redis_available = False
        
        # Fallback to in-memory
        self._fallback_storage[key] = serialized
        logger.debug(f"Stored session {session_id} in memory (fallback)")
    
    async def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Session data dictionary or None if not found
        """
        key = f"session:{session_id}"
        
        # Try Redis first
        if self._redis_available and self._redis:
            try:
                data = await self._redis.get(key)
                if data:
                    logger.debug(f"Retrieved session {session_id} from Redis")
                    return self._deserialize_session(data)
            except Exception as e:
                logger.warning(f"Redis get failed, trying fallback: {e}")
                self._redis_available = False
        
        # Fallback to in-memory
        data = self._fallback_storage.get(key)
        if data:
            logger.debug(f"Retrieved session {session_id} from memory (fallback)")
            return self._deserialize_session(data)
        
        return None
    
    async def delete(self, session_id: str) -> bool:
        """
        Delete session data.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            True if deleted, False if not found
        """
        key = f"session:{session_id}"
        deleted = False
        
        # Try Redis first
        if self._redis_available and self._redis:
            try:
                result = await self._redis.delete(key)
                deleted = result > 0
                if deleted:
                    logger.debug(f"Deleted session {session_id} from Redis")
            except Exception as e:
                logger.warning(f"Redis delete failed: {e}")
                self._redis_available = False
        
        # Also check/delete from fallback
        if key in self._fallback_storage:
            del self._fallback_storage[key]
            deleted = True
            logger.debug(f"Deleted session {session_id} from memory (fallback)")
        
        return deleted
    
    async def exists(self, session_id: str) -> bool:
        """Check if a session exists."""
        key = f"session:{session_id}"
        
        # Try Redis first
        if self._redis_available and self._redis:
            try:
                return await self._redis.exists(key) > 0
            except Exception as e:
                logger.warning(f"Redis exists failed: {e}")
                self._redis_available = False
        
        # Fallback to in-memory
        return key in self._fallback_storage
    
    async def extend_ttl(self, session_id: str, ttl_seconds: int = 86400):
        """Extend the TTL of an existing session."""
        key = f"session:{session_id}"
        
        # Try Redis first
        if self._redis_available and self._redis:
            try:
                await self._redis.expire(key, ttl_seconds)
                logger.debug(f"Extended TTL for session {session_id}")
                return
            except Exception as e:
                logger.warning(f"Redis expire failed: {e}")
                self._redis_available = False
        
        # For in-memory fallback, we don't implement TTL expiration
        # Sessions will persist until process restart or manual deletion
        logger.debug(f"TTL extension not supported for in-memory fallback (session {session_id})")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get backend statistics."""
        return {
            "backend": "redis" if self._redis_available else "memory",
            "redis_available": self._redis_available,
            "redis_url_configured": bool(os.getenv("REDIS_URL")),
            "connection_attempts": self._connection_attempts,
            "fallback_sessions": len(self._fallback_storage),
            "health": "healthy" if self._redis_available or not os.getenv("REDIS_URL") else "degraded"
        }

# Global singleton instance
redis_session_backend = RedisSessionBackend()
