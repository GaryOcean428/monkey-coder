"""
Redis Caching Module for Quantum Routing System

This module provides caching functionality for quantum routing decisions,
reducing computation overhead by storing and retrieving previous routing results.
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Set, Tuple
from collections import defaultdict
import asyncio

try:
    import redis.asyncio as redis
except ImportError:
    redis = None
    logging.warning("Redis not available - caching disabled")

logger = logging.getLogger(__name__)


@dataclass
class CacheMetrics:
    """Performance metrics for cache operations."""
    hits: int = 0
    misses: int = 0
    invalidations: int = 0
    total_requests: int = 0
    avg_hit_time_ms: float = 0.0
    avg_miss_time_ms: float = 0.0
    cache_size: int = 0
    last_reset: datetime = None

    def __post_init__(self):
        if self.last_reset is None:
            self.last_reset = datetime.now()

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests

    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate."""
        if self.total_requests == 0:
            return 0.0
        return self.misses / self.total_requests

    def to_dict(self) -> dict:
        """Convert metrics to dictionary."""
        return {
            **asdict(self),
            'hit_rate': self.hit_rate,
            'miss_rate': self.miss_rate,
            'last_reset': self.last_reset.isoformat() if self.last_reset else None
        }


class QuantumRouteCacheManager:
    """
    Redis-based caching manager for quantum routing decisions.
    
    Features:
    - TTL-based cache expiration
    - Cache invalidation on model updates
    - Performance metrics tracking
    - Integration with QuantumManager
    - Versioned cache keys for consistency
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        default_ttl: int = 3600,
        max_cache_size: int = 10000,
        cache_prefix: str = "quantum_route",
        enable_metrics: bool = True
    ):
        """
        Initialize the cache manager.
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default TTL in seconds
            max_cache_size: Maximum number of cache entries
            cache_prefix: Prefix for cache keys
            enable_metrics: Enable performance metrics tracking
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.max_cache_size = max_cache_size
        self.cache_prefix = cache_prefix
        self.enable_metrics = enable_metrics
        
        self.redis_client = None
        self.metrics = CacheMetrics()
        self.model_version = "v1.0.0"
        self._lock = asyncio.Lock()
        
        # Track cache keys for efficient invalidation
        self.cache_keys: Set[str] = set()
        
        logger.info(f"Initialized QuantumRouteCacheManager with TTL={default_ttl}s")

    async def connect(self) -> None:
        """Establish Redis connection."""
        if redis is None:
            logger.warning("Redis library not available - caching disabled")
            return
            
        try:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
            logger.info("Disconnected from Redis")

    def generate_cache_key(self, routing_params: Dict[str, Any]) -> str:
        """
        Generate deterministic cache key from routing parameters.
        
        Args:
            routing_params: Dictionary of routing parameters
            
        Returns:
            Cache key string
        """
        # Include model version for consistency
        key_data = {
            **routing_params,
            'model_version': self.model_version
        }
        
        # Create deterministic string representation
        key_str = json.dumps(key_data, sort_keys=True)
        
        # Generate hash for compact key
        key_hash = hashlib.sha256(key_str.encode()).hexdigest()[:16]
        
        return f"{self.cache_prefix}:{self.model_version}:{key_hash}"

    async def get_cached_route(self, routing_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached routing decision.
        
        Args:
            routing_params: Routing parameters
            
        Returns:
            Cached route result or None if not found
        """
        if not self.redis_client:
            return None
            
        cache_key = self.generate_cache_key(routing_params)
        start_time = time.time()
        
        try:
            cached_value = await self.redis_client.get(cache_key)
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            if cached_value:
                # Cache hit
                result = json.loads(cached_value)
                
                if self.enable_metrics:
                    async with self._lock:
                        self.metrics.hits += 1
                        self.metrics.total_requests += 1
                        # Update rolling average
                        self.metrics.avg_hit_time_ms = (
                            0.9 * self.metrics.avg_hit_time_ms + 0.1 * elapsed_ms
                        )
                
                logger.debug(f"Cache HIT for key {cache_key} ({elapsed_ms:.2f}ms)")
                return result
            else:
                # Cache miss
                if self.enable_metrics:
                    async with self._lock:
                        self.metrics.misses += 1
                        self.metrics.total_requests += 1
                        self.metrics.avg_miss_time_ms = (
                            0.9 * self.metrics.avg_miss_time_ms + 0.1 * elapsed_ms
                        )
                
                logger.debug(f"Cache MISS for key {cache_key}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving from cache: {e}")
            return None

    async def cache_route(
        self,
        routing_params: Dict[str, Any],
        route_result: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Store routing decision in cache.
        
        Args:
            routing_params: Routing parameters
            route_result: Route computation result
            ttl: TTL in seconds (uses default if None)
            
        Returns:
            True if successfully cached
        """
        if not self.redis_client:
            return False
            
        cache_key = self.generate_cache_key(routing_params)
        ttl = ttl or self.default_ttl
        
        try:
            # Check cache size limit
            if len(self.cache_keys) >= self.max_cache_size:
                # Evict oldest entries (simple FIFO for now)
                await self._evict_old_entries()
            
            # Store with TTL
            value = json.dumps(route_result)
            await self.redis_client.setex(cache_key, ttl, value)
            
            # Track key for management
            self.cache_keys.add(cache_key)
            
            if self.enable_metrics:
                async with self._lock:
                    self.metrics.cache_size = len(self.cache_keys)
            
            logger.debug(f"Cached route with key {cache_key} (TTL={ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error caching route: {e}")
            return False

    async def invalidate_cache(
        self,
        pattern: Optional[str] = None,
        model_version: Optional[str] = None
    ) -> int:
        """
        Invalidate cache entries.
        
        Args:
            pattern: Optional pattern to match keys
            model_version: Invalidate specific model version
            
        Returns:
            Number of invalidated entries
        """
        if not self.redis_client:
            return 0
            
        try:
            if model_version:
                # Invalidate specific model version
                pattern = f"{self.cache_prefix}:{model_version}:*"
            elif pattern is None:
                # Invalidate all cache entries
                pattern = f"{self.cache_prefix}:*"
            
            # Find matching keys
            cursor = '0'
            invalidated = 0
            
            while cursor != 0:
                cursor, keys = await self.redis_client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100
                )
                
                if keys:
                    await self.redis_client.delete(*keys)
                    invalidated += len(keys)
                    
                    # Remove from tracked keys
                    for key in keys:
                        self.cache_keys.discard(key)
            
            if self.enable_metrics:
                async with self._lock:
                    self.metrics.invalidations += invalidated
                    self.metrics.cache_size = len(self.cache_keys)
            
            logger.info(f"Invalidated {invalidated} cache entries")
            return invalidated
            
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return 0

    async def update_model_version(self, new_version: str) -> None:
        """
        Update model version and invalidate old cache.
        
        Args:
            new_version: New model version string
        """
        old_version = self.model_version
        self.model_version = new_version
        
        # Invalidate old version cache
        await self.invalidate_cache(model_version=old_version)
        
        logger.info(f"Updated model version from {old_version} to {new_version}")

    async def _evict_old_entries(self, count: int = 100) -> None:
        """
        Evict old cache entries to maintain size limit.
        
        Args:
            count: Number of entries to evict
        """
        if not self.cache_keys:
            return
            
        # Simple FIFO eviction (could be improved with LRU)
        to_evict = list(self.cache_keys)[:count]
        
        if to_evict and self.redis_client:
            try:
                await self.redis_client.delete(*to_evict)
                for key in to_evict:
                    self.cache_keys.discard(key)
                logger.debug(f"Evicted {len(to_evict)} cache entries")
            except Exception as e:
                logger.error(f"Error evicting cache entries: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current cache performance metrics.
        
        Returns:
            Dictionary of metrics
        """
        return self.metrics.to_dict()

    async def reset_metrics(self) -> None:
        """Reset performance metrics."""
        async with self._lock:
            self.metrics = CacheMetrics()
        logger.info("Reset cache metrics")

    async def warmup_cache(self, common_routes: List[Tuple[Dict, Dict]]) -> int:
        """
        Pre-populate cache with common routes.
        
        Args:
            common_routes: List of (params, result) tuples
            
        Returns:
            Number of entries cached
        """
        cached = 0
        for params, result in common_routes:
            if await self.cache_route(params, result):
                cached += 1
        
        logger.info(f"Warmed up cache with {cached} entries")
        return cached

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on cache system.
        
        Returns:
            Health status dictionary
        """
        health = {
            'status': 'unknown',
            'connected': False,
            'metrics': self.get_metrics()
        }
        
        if self.redis_client:
            try:
                await self.redis_client.ping()
                health['status'] = 'healthy'
                health['connected'] = True
                
                # Get Redis info
                info = await self.redis_client.info()
                health['redis_info'] = {
                    'version': info.get('redis_version'),
                    'used_memory': info.get('used_memory_human'),
                    'connected_clients': info.get('connected_clients')
                }
            except Exception as e:
                health['status'] = 'unhealthy'
                health['error'] = str(e)
        else:
            health['status'] = 'disconnected'
        
        return health


# Integration with existing QuantumManager
class CachedQuantumManager:
    """
    Example integration of cache manager with QuantumManager.
    """
    
    def __init__(self, cache_manager: Optional[QuantumRouteCacheManager] = None):
        """
        Initialize with optional cache manager.
        
        Args:
            cache_manager: Cache manager instance
        """
        self.cache_manager = cache_manager
        
    async def compute_route(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute route with caching support.
        
        Args:
            params: Routing parameters
            
        Returns:
            Route result
        """
        # Try cache first
        if self.cache_manager:
            cached_result = await self.cache_manager.get_cached_route(params)
            if cached_result:
                return cached_result
        
        # Compute if not cached
        result = await self._compute_quantum_route(params)
        
        # Cache the result
        if self.cache_manager:
            await self.cache_manager.cache_route(params, result)
        
        return result
    
    async def _compute_quantum_route(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actual quantum route computation (placeholder).
        
        Args:
            params: Routing parameters
            
        Returns:
            Computed route
        """
        # Simulate computation
        await asyncio.sleep(0.1)
        return {
            'route': f"quantum_path_{params.get('source')}_{params.get('destination')}",
            'confidence': 0.95,
            'computed_at': datetime.now().isoformat()
        }