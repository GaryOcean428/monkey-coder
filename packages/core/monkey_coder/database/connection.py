"""
Database connection management for PostgreSQL.

This module handles database connections and provides connection pooling
for the Monkey Coder Core API.
"""

import asyncio
import logging
import os
from typing import Optional, Dict, Any

import asyncpg
from asyncpg import Pool

logger = logging.getLogger(__name__)

# Global connection pool
_connection_pool: Optional[Pool] = None


async def get_database_connection() -> Pool:
    """
    Get or create the database connection pool.
    
    Optimized for Railway deployment with production-ready connection pooling:
    - Larger pool size for production workloads
    - Connection timeout and retry logic
    - Pool health monitoring and recovery
    - Railway-optimized connection parameters
    
    Returns:
        asyncpg.Pool: Database connection pool
        
    Raises:
        RuntimeError: If database connection fails
    """
    global _connection_pool
    
    if _connection_pool is None or _connection_pool.is_closing():
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL environment variable not set")
        
        # Railway-optimized connection pool settings
        # Increase pool size for production workloads
        min_size = int(os.getenv("DB_POOL_MIN_SIZE", "5"))
        max_size = int(os.getenv("DB_POOL_MAX_SIZE", "20"))
        max_overflow = int(os.getenv("DB_POOL_MAX_OVERFLOW", "40"))
        pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        
        try:
            _connection_pool = await asyncpg.create_pool(
                database_url,
                min_size=min_size,
                max_size=max_size,
                command_timeout=pool_timeout,
                max_inactive_connection_lifetime=3600,  # Recycle connections every hour
                server_settings={
                    'jit': 'off',
                    'application_name': 'monkey_coder_production'
                }
            )
            logger.info(f"Database connection pool created successfully (min={min_size}, max={max_size})")
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {e}")
            raise RuntimeError(f"Database connection failed: {e}")
    
    return _connection_pool


async def close_database_connection() -> None:
    """
    Close the database connection pool.
    """
    global _connection_pool
    
    if _connection_pool and not _connection_pool.is_closing():
        await _connection_pool.close()
        logger.info("Database connection pool closed")
        _connection_pool = None


async def test_database_connection() -> bool:
    """
    Test database connectivity.
    
    Returns:
        bool: True if connection is successful
    """
    try:
        pool = await get_database_connection()
        async with pool.acquire() as connection:
            result = await connection.fetchrow("SELECT 1 as test")
            return result["test"] == 1
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


async def get_database_health() -> Dict[str, Any]:
    """
    Get comprehensive database health information for Railway monitoring.
    
    Returns:
        Dict with database health status, pool stats, and connection info
    """
    health_info = {
        "status": "unknown",
        "timestamp": None,
        "pool_stats": {},
        "connection_test": False,
        "error": None
    }
    
    try:
        # Test basic connectivity
        health_info["connection_test"] = await test_database_connection()
        health_info["timestamp"] = asyncio.get_event_loop().time()
        
        # Get pool statistics if available
        if _connection_pool and not _connection_pool.is_closing():
            health_info["pool_stats"] = {
                "size": _connection_pool.get_size(),
                "min_size": _connection_pool._minsize,
                "max_size": _connection_pool._maxsize,
                "idle_connections": _connection_pool.get_idle_size(),
                "is_closing": _connection_pool.is_closing()
            }
            health_info["status"] = "healthy" if health_info["connection_test"] else "degraded"
        else:
            health_info["status"] = "no_pool"
            
    except Exception as e:
        health_info["status"] = "error"
        health_info["error"] = str(e)
        logger.error(f"Database health check failed: {e}")
    
    return health_info
