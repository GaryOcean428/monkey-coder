"""
Production-grade Redis-based rate limiting middleware.
"""
import time
import redis
import os
from typing import Dict, Optional
from fastapi import HTTPException, Request
import logging

logger = logging.getLogger(__name__)

class RedisRateLimiter:
    """Redis-based sliding window rate limiter."""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
        self.window_seconds = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "300"))  # 5 minutes
        self.max_requests = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "8"))  # per IP+route window
        
    def _get_key(self, ip: str, route_tag: str) -> str:
        """Generate Redis key for rate limiting."""
        return f"rate_limit:{ip}:{route_tag}"
        
    async def check_rate_limit(self, request: Request, route_tag: str) -> None:
        """Check rate limit using Redis sliding window. Raises HTTPException(429) if exceeded."""
        ip = request.client.host if request.client else "unknown"
        key = self._get_key(ip, route_tag)
        now = time.time()
        window_start = now - self.window_seconds
        
        try:
            pipe = self.redis_client.pipeline()
            
            pipe.zremrangebyscore(key, 0, window_start)
            
            pipe.zcard(key)
            
            results = pipe.execute()
            current_count = results[1]
            
            if current_count >= self.max_requests:
                logger.warning(f"Rate limit exceeded for {ip}:{route_tag} - {current_count}/{self.max_requests}")
                raise HTTPException(status_code=429, detail="Too many requests, slow down")
            
            self.redis_client.zadd(key, {str(now): now})
            
            self.redis_client.expire(key, self.window_seconds)
            
        except redis.RedisError as e:
            logger.error(f"Redis rate limiting error: {e}")

_rate_limiter: Optional[RedisRateLimiter] = None

def get_rate_limiter() -> RedisRateLimiter:
    """Get or create global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RedisRateLimiter()
    return _rate_limiter

async def check_rate_limit(request: Request, route_tag: str) -> None:
    """Convenience function for rate limiting."""
    limiter = get_rate_limiter()
    await limiter.check_rate_limit(request, route_tag)
