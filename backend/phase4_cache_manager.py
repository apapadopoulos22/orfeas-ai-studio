#!/usr/bin/env python3
"""
BOB AI v10.0 - PHASE 4.6 CACHE MANAGER
Redis-Based Caching with Fallback

Provides caching for API responses with TTL support
Automatic cache invalidation and memory management

Version: 1.0.0
Date: October 28, 2025
Status: PHASE 4.6 IMPLEMENTATION
"""

import json
import logging
import hashlib
import time
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from functools import wraps

logger = logging.getLogger(__name__)

# Try to import Redis, fallback to in-memory cache if unavailable
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available - using in-memory cache fallback")


class InMemoryCache:
    """Fallback in-memory cache when Redis is unavailable"""

    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        logger.info("Initialized in-memory cache")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            return None

        entry = self.cache[key]
        # Check if expired
        if entry['expires_at'] and entry['expires_at'] < time.time():
            del self.cache[key]
            return None

        logger.debug(f"Cache hit: {key}")
        return entry['value']

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL"""
        try:
            self.cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl,
                'created_at': time.time()
            }
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache deleted: {key}")
            return True
        return False

    def flush(self) -> bool:
        """Clear all cache"""
        self.cache.clear()
        logger.info("Cache flushed")
        return True

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = time.time()
        expired = sum(1 for v in self.cache.values() if v['expires_at'] and v['expires_at'] < now)
        active = len(self.cache) - expired

        return {
            'type': 'in-memory',
            'total_keys': len(self.cache),
            'active_keys': active,
            'expired_keys': expired,
            'memory_bytes': sum(len(json.dumps(v['value'])) for v in self.cache.values())
        }


class RedisCache:
    """Redis-based cache manager"""

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"Redis cache connected: {host}:{port}")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            logger.debug(f"Cache miss: {key}")
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in Redis cache with TTL"""
        try:
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value)
            )
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from Redis cache"""
        try:
            result = self.redis_client.delete(key)
            if result:
                logger.debug(f"Cache deleted: {key}")
            return bool(result)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    def flush(self) -> bool:
        """Clear all Redis cache"""
        try:
            self.redis_client.flushdb()
            logger.info("Redis cache flushed")
            return True
        except Exception as e:
            logger.error(f"Redis flush error: {e}")
            return False

    def stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics"""
        try:
            info = self.redis_client.info()
            return {
                'type': 'redis',
                'used_memory': info.get('used_memory', 0),
                'used_memory_human': info.get('used_memory_human', 'N/A'),
                'total_keys': self.redis_client.dbsize(),
                'connected_clients': info.get('connected_clients', 0)
            }
        except Exception as e:
            logger.error(f"Redis stats error: {e}")
            return {'type': 'redis', 'error': str(e)}


class CacheManager:
    """Unified cache manager with Redis fallback to in-memory"""

    _instance = None
    _backend = None

    def __new__(cls, use_redis: bool = True):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, use_redis: bool = True):
        if self._backend is not None:
            return  # Already initialized

        if use_redis and REDIS_AVAILABLE:
            try:
                self._backend = RedisCache()
            except Exception as e:
                logger.warning(f"Redis initialization failed, using in-memory cache: {e}")
                self._backend = InMemoryCache()
        else:
            logger.info("Using in-memory cache (Redis disabled or unavailable)")
            self._backend = InMemoryCache()

    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        return self._backend.get(key)

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set cached value"""
        return self._backend.set(key, value, ttl)

    def delete(self, key: str) -> bool:
        """Delete cached value"""
        return self._backend.delete(key)

    def flush(self) -> bool:
        """Clear all cache"""
        return self._backend.flush()

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self._backend.stats()

    @staticmethod
    def generate_key(*parts: str) -> str:
        """Generate cache key from parts"""
        key_string = ':'.join(str(p) for p in parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    @staticmethod
    def cache_response(ttl: int = 300, key_prefix: str = "api"):
        """Decorator to cache function responses"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                key_parts = [key_prefix, func.__name__] + [str(a) for a in args]
                cache_key = CacheManager.generate_key(*key_parts)

                # Try to get from cache
                cached_value = CacheManager().get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Returning cached response for {func.__name__}")
                    return cached_value

                # Execute function and cache result
                result = func(*args, **kwargs)
                CacheManager().set(cache_key, result, ttl)

                return result

            return wrapper
        return decorator


def get_cache_manager(use_redis: bool = True) -> CacheManager:
    """Get or create cache manager singleton"""
    return CacheManager(use_redis=use_redis)


if __name__ == '__main__':
    # Test cache manager
    logging.basicConfig(level=logging.DEBUG)

    cache = get_cache_manager(use_redis=False)

    # Test set/get
    cache.set('test_key', {'data': 'test_value'}, ttl=60)
    print(f"Retrieved: {cache.get('test_key')}")

    # Test decorator
    @cache.cache_response(ttl=60, key_prefix="test")
    def expensive_function(x):
        print(f"Computing for {x}...")
        return x * 2

    print(f"First call: {expensive_function(5)}")
    print(f"Second call (cached): {expensive_function(5)}")

    # Stats
    print(f"Cache stats: {cache.stats()}")
