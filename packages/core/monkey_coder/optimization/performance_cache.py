"""
Performance Optimization Module for Phase 2.0

Implements caching strategies, response optimization, and performance monitoring
for production deployment.
"""

import asyncio
import logging
import time
import hashlib
from typing import Any, Dict, Optional, List, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with TTL and metadata."""
    data: Any
    timestamp: datetime
    ttl_seconds: int
    hit_count: int = 0
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return datetime.utcnow() > self.timestamp + timedelta(seconds=self.ttl_seconds)
    
    @property
    def age_seconds(self) -> float:
        """Get age of cache entry in seconds."""
        return (datetime.utcnow() - self.timestamp).total_seconds()


class InMemoryCache:
    """
    High-performance in-memory cache with TTL and LRU eviction.
    
    Optimized for Railway deployment without Redis dependency.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: List[str] = []
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expired_removals": 0
        }
        
    def _generate_key(self, key_data: Union[str, Dict, Tuple]) -> str:
        """Generate consistent cache key from various input types."""
        if isinstance(key_data, str):
            return key_data
        elif isinstance(key_data, (dict, list, tuple)):
            # Convert to JSON and hash for consistent keys
            json_str = json.dumps(key_data, sort_keys=True, default=str)
            return hashlib.sha256(json_str.encode()).hexdigest()[:32]
        else:
            return str(key_data)
    
    def get(self, key: Union[str, Dict, Tuple]) -> Optional[Any]:
        """Get value from cache."""
        cache_key = self._generate_key(key)
        
        if cache_key not in self._cache:
            self._stats["misses"] += 1
            return None
            
        entry = self._cache[cache_key]
        
        # Check if expired
        if entry.is_expired:
            self.delete(cache_key)
            self._stats["misses"] += 1
            self._stats["expired_removals"] += 1
            return None
        
        # Update access order for LRU
        if cache_key in self._access_order:
            self._access_order.remove(cache_key)
        self._access_order.append(cache_key)
        
        entry.hit_count += 1
        self._stats["hits"] += 1
        
        logger.debug(f"Cache hit for key: {cache_key[:16]}...")
        return entry.data
    
    def set(self, key: Union[str, Dict, Tuple], value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        cache_key = self._generate_key(key)
        ttl = ttl or self.default_ttl
        
        # Check if we need to evict entries
        if len(self._cache) >= self.max_size and cache_key not in self._cache:
            self._evict_lru()
        
        entry = CacheEntry(
            data=value,
            timestamp=datetime.utcnow(),
            ttl_seconds=ttl
        )
        
        self._cache[cache_key] = entry
        
        # Update access order
        if cache_key in self._access_order:
            self._access_order.remove(cache_key)
        self._access_order.append(cache_key)
        
        logger.debug(f"Cache set for key: {cache_key[:16]}... (TTL: {ttl}s)")
    
    def delete(self, key: Union[str, Dict, Tuple]) -> bool:
        """Delete entry from cache."""
        cache_key = self._generate_key(key)
        
        if cache_key in self._cache:
            del self._cache[cache_key]
            if cache_key in self._access_order:
                self._access_order.remove(cache_key)
            return True
        return False
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self._access_order:
            lru_key = self._access_order.pop(0)
            if lru_key in self._cache:
                del self._cache[lru_key]
                self._stats["evictions"] += 1
                logger.debug(f"Evicted LRU entry: {lru_key[:16]}...")
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries and return count removed."""
        expired_keys = []
        
        for key, entry in self._cache.items():
            if entry.is_expired:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.delete(key)
        
        self._stats["expired_removals"] += len(expired_keys)
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hit_rate_percent": round(hit_rate, 2),
            "total_hits": self._stats["hits"],
            "total_misses": self._stats["misses"],
            "evictions": self._stats["evictions"],
            "expired_removals": self._stats["expired_removals"]
        }
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._access_order.clear()
        logger.info("Cache cleared")


class ResponseCache:
    """
    Response caching for API endpoints to improve performance.
    """
    
    def __init__(self, cache: InMemoryCache):
        self.cache = cache
        
    def cache_key_for_request(self, request_data: Dict[str, Any], user_id: Optional[str] = None) -> str:
        """Generate cache key for API request."""
        key_data = {
            "endpoint": request_data.get("endpoint", "unknown"),
            "method": request_data.get("method", "GET"),
            "params": request_data.get("params", {}),
            "user_id": user_id  # Include user for personalized responses
        }
        return self.cache._generate_key(key_data)
    
    def should_cache_response(self, request_data: Dict[str, Any], response_data: Dict[str, Any]) -> bool:
        """Determine if response should be cached."""
        # Don't cache error responses
        if response_data.get("error") or response_data.get("status_code", 200) >= 400:
            return False
            
        # Don't cache streaming responses
        if request_data.get("stream", False):
            return False
            
        # Don't cache file operations
        if "file" in request_data.get("endpoint", "").lower():
            return False
            
        return True
    
    def get_cached_response(self, request_data: Dict[str, Any], user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get cached response for request."""
        cache_key = self.cache_key_for_request(request_data, user_id)
        return self.cache.get(cache_key)
    
    def cache_response(self, request_data: Dict[str, Any], response_data: Dict[str, Any], 
                      user_id: Optional[str] = None, ttl: int = 300) -> None:
        """Cache response for request."""
        if self.should_cache_response(request_data, response_data):
            cache_key = self.cache_key_for_request(request_data, user_id)
            self.cache.set(cache_key, response_data, ttl)


class PerformanceMonitor:
    """
    Performance monitoring and optimization tracker.
    """
    
    def __init__(self):
        self.metrics = {
            "request_times": [],
            "slow_requests": [],
            "error_counts": {},
            "endpoint_stats": {}
        }
        
    def record_request(self, endpoint: str, method: str, duration: float, 
                      status_code: int, user_id: Optional[str] = None) -> None:
        """Record request performance metrics."""
        # Store recent request times (last 1000)
        self.metrics["request_times"].append({
            "endpoint": endpoint,
            "method": method,
            "duration": duration,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id
        })
        
        # Keep only recent entries
        if len(self.metrics["request_times"]) > 1000:
            self.metrics["request_times"] = self.metrics["request_times"][-1000:]
        
        # Track slow requests (>2 seconds)
        if duration > 2.0:
            self.metrics["slow_requests"].append({
                "endpoint": endpoint,
                "method": method,
                "duration": duration,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Keep only recent slow requests
            if len(self.metrics["slow_requests"]) > 100:
                self.metrics["slow_requests"] = self.metrics["slow_requests"][-100:]
        
        # Track error counts
        if status_code >= 400:
            error_key = f"{endpoint}:{status_code}"
            self.metrics["error_counts"][error_key] = self.metrics["error_counts"].get(error_key, 0) + 1
        
        # Track endpoint statistics
        endpoint_key = f"{method}:{endpoint}"
        if endpoint_key not in self.metrics["endpoint_stats"]:
            self.metrics["endpoint_stats"][endpoint_key] = {
                "count": 0,
                "total_duration": 0,
                "avg_duration": 0,
                "min_duration": float('inf'),
                "max_duration": 0
            }
        
        stats = self.metrics["endpoint_stats"][endpoint_key]
        stats["count"] += 1
        stats["total_duration"] += duration
        stats["avg_duration"] = stats["total_duration"] / stats["count"]
        stats["min_duration"] = min(stats["min_duration"], duration)
        stats["max_duration"] = max(stats["max_duration"], duration)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for monitoring."""
        recent_requests = self.metrics["request_times"][-100:] if self.metrics["request_times"] else []
        
        if not recent_requests:
            return {"status": "no_data", "message": "No recent requests to analyze"}
        
        durations = [r["duration"] for r in recent_requests]
        
        summary = {
            "recent_requests": len(recent_requests),
            "avg_response_time": round(sum(durations) / len(durations), 3),
            "min_response_time": round(min(durations), 3),
            "max_response_time": round(max(durations), 3),
            "slow_requests_count": len(self.metrics["slow_requests"]),
            "error_rate_percent": round(
                len([r for r in recent_requests if r["status_code"] >= 400]) / len(recent_requests) * 100, 2
            ),
            "top_endpoints": sorted(
                self.metrics["endpoint_stats"].items(),
                key=lambda x: x[1]["count"],
                reverse=True
            )[:10]
        }
        
        return summary


# Global instances
_cache: Optional[InMemoryCache] = None
_response_cache: Optional[ResponseCache] = None
_performance_monitor: Optional[PerformanceMonitor] = None


def get_cache() -> InMemoryCache:
    """Get global cache instance."""
    global _cache
    if _cache is None:
        _cache = InMemoryCache(max_size=1000, default_ttl=300)
    return _cache


def get_response_cache() -> ResponseCache:
    """Get global response cache instance."""
    global _response_cache
    if _response_cache is None:
        _response_cache = ResponseCache(get_cache())
    return _response_cache


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


async def cleanup_task():
    """Background task to cleanup expired cache entries."""
    while True:
        try:
            cache = get_cache()
            removed = cache.cleanup_expired()
            if removed > 0:
                logger.info(f"Cache cleanup: removed {removed} expired entries")
            
            # Wait 5 minutes before next cleanup
            await asyncio.sleep(300)
        except Exception as e:
            logger.error(f"Error in cache cleanup task: {e}")
            await asyncio.sleep(60)  # Wait 1 minute on error