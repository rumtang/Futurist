"""Cache tools for Redis integration."""

import json
import asyncio
from typing import Any, Optional, Dict
from datetime import timedelta
import redis.asyncio as redis
from loguru import logger

from src.config.base_config import settings


class CacheManager:
    """Manages Redis cache operations."""
    
    def __init__(self):
        self.redis_client = None
        self.default_ttl = 3600  # 1 hour default TTL
        
    async def initialize(self):
        """Initialize Redis connection."""
        try:
            # Check if Redis is configured
            if settings.redis_host == "localhost" and settings.redis_port == 6379:
                # Try to connect with a short timeout
                self.redis_client = await redis.Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    decode_responses=True,
                    socket_connect_timeout=2.0,  # 2 second timeout
                    retry_on_timeout=False
                )
            else:
                # Use normal connection for configured Redis
                self.redis_client = await redis.Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    decode_responses=True
                )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
            
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.warning(f"Redis connection failed: {e}")
            logger.info("Cache functionality disabled - system will work without caching")
            self.redis_client = None
        except Exception as e:
            logger.error(f"Unexpected error initializing Redis: {e}")
            # Don't raise - cache is optional
            self.redis_client = None
    
    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis_client:
            return None
            
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        if not self.redis_client:
            return False
            
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            await self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.redis_client:
            return False
            
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.redis_client:
            return False
            
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    async def get_many(self, keys: list) -> Dict[str, Any]:
        """Get multiple values from cache."""
        if not self.redis_client:
            return {}
            
        try:
            values = await self.redis_client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value:
                    result[key] = json.loads(value)
            return result
        except Exception as e:
            logger.error(f"Cache get_many error: {e}")
            return {}
    
    async def set_many(self, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple values in cache."""
        if not self.redis_client:
            return False
            
        try:
            ttl = ttl or self.default_ttl
            pipe = self.redis_client.pipeline()
            
            for key, value in data.items():
                serialized = json.dumps(value)
                pipe.setex(key, ttl, serialized)
            
            await pipe.execute()
            return True
        except Exception as e:
            logger.error(f"Cache set_many error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if not self.redis_client:
            return 0
            
        try:
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await self.redis_client.delete(*keys)
            
            return len(keys)
        except Exception as e:
            logger.error(f"Cache clear_pattern error: {e}")
            return 0


# Global cache manager instance
cache_manager = CacheManager()


async def initialize_redis():
    """Initialize Redis for the application."""
    await cache_manager.initialize()


async def close_redis():
    """Close Redis connections."""
    await cache_manager.close()


# Cache decorators
def cache_result(key_prefix: str, ttl: int = 3600):
    """Decorator to cache function results."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached = await cache_manager.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cache set: {cache_key}")
            
            return result
        
        return wrapper
    return decorator


# Convenience functions for specific cache operations
async def cache_analysis_result(analysis_id: str, result: Dict[str, Any]) -> bool:
    """Cache analysis results."""
    key = f"analysis:{analysis_id}"
    return await cache_manager.set(key, result, ttl=7200)  # 2 hours


async def get_cached_analysis(analysis_id: str) -> Optional[Dict[str, Any]]:
    """Get cached analysis results."""
    key = f"analysis:{analysis_id}"
    return await cache_manager.get(key)


async def cache_trend_data(trend_id: str, data: Dict[str, Any]) -> bool:
    """Cache trend data."""
    key = f"trend:{trend_id}"
    return await cache_manager.set(key, data, ttl=3600)  # 1 hour


async def get_cached_trend(trend_id: str) -> Optional[Dict[str, Any]]:
    """Get cached trend data."""
    key = f"trend:{trend_id}"
    return await cache_manager.get(key)


async def cache_search_results(query: str, results: list) -> bool:
    """Cache search results."""
    key = f"search:{query}"
    return await cache_manager.set(key, results, ttl=1800)  # 30 minutes


async def get_cached_search(query: str) -> Optional[list]:
    """Get cached search results."""
    key = f"search:{query}"
    return await cache_manager.get(key)