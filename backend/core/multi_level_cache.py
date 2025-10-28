"""
ORFEAS AI Studio - Multi-Level Caching System
==============================================

Advanced caching strategy with:
- L1: In-memory LRU cache (fastest, smallest)
- L2: Redis cache (fast, distributed)
- L3: Disk cache (slower, largest capacity)
- Automatic cache warming on startup
- Predictive prefetching based on access patterns
- Compression for large objects
- Cache coherency across levels

Author: ORFEAS AI Team
Date: October 28, 2025
"""

import os
import pickle
import hashlib
import logging
import time
import zlib
from typing import Any, Optional, Dict, List, Tuple
from collections import OrderedDict
from dataclasses import dataclass
import threading
import redis
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """Statistics for cache performance tracking"""
    l1_hits: int = 0
    l1_misses: int = 0
    l2_hits: int = 0
    l2_misses: int = 0
    l3_hits: int = 0
    l3_misses: int = 0
    total_requests: int = 0
    evictions: int = 0
    prefetch_hits: int = 0
    compression_savings_bytes: int = 0

    @property
    def l1_hit_rate(self) -> float:
        """Calculate L1 cache hit rate"""
        total = self.l1_hits + self.l1_misses
        return (self.l1_hits / total * 100) if total > 0 else 0.0

    @property
    def l2_hit_rate(self) -> float:
        """Calculate L2 cache hit rate"""
        total = self.l2_hits + self.l2_misses
        return (self.l2_hits / total * 100) if total > 0 else 0.0

    @property
    def l3_hit_rate(self) -> float:
        """Calculate L3 cache hit rate"""
        total = self.l3_hits + self.l3_misses
        return (self.l3_hits / total * 100) if total > 0 else 0.0

    @property
    def overall_hit_rate(self) -> float:
        """Calculate overall cache hit rate"""
        hits = self.l1_hits + self.l2_hits + self.l3_hits
        return (hits / self.total_requests * 100) if self.total_requests > 0 else 0.0


class L1MemoryCache:
    """
    L1 Cache: Fast in-memory LRU cache
    - Millisecond access time
    - Limited capacity (configurable)
    - Thread-safe
    """

    def __init__(self, max_size: int = 1000, max_memory_mb: int = 512):
        """
        Initialize L1 cache.

        Args:
            max_size: Maximum number of items
            max_memory_mb: Maximum memory usage in MB
        """
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: OrderedDict = OrderedDict()
        self.sizes: Dict[str, int] = {}
        self.current_memory = 0
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from L1 cache"""
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return self.cache[key]
            return None

    def set(self, key: str, value: Any, size_bytes: int = 0) -> bool:
        """
        Set value in L1 cache.

        Args:
            key: Cache key
            value: Value to cache
            size_bytes: Size of value in bytes

        Returns:
            True if cached, False if evicted
        """
        with self.lock:
            # Estimate size if not provided
            if size_bytes == 0:
                size_bytes = len(pickle.dumps(value))

            # Remove old entry if exists
            if key in self.cache:
                self.current_memory -= self.sizes.get(key, 0)
                del self.cache[key]
                del self.sizes[key]

            # Evict if necessary
            while (len(self.cache) >= self.max_size or
                   self.current_memory + size_bytes > self.max_memory_bytes):
                if not self.cache:
                    return False

                oldest_key, _ = self.cache.popitem(last=False)
                self.current_memory -= self.sizes.pop(oldest_key, 0)

            # Add new entry
            self.cache[key] = value
            self.sizes[key] = size_bytes
            self.current_memory += size_bytes
            return True

    def delete(self, key: str):
        """Delete key from L1 cache"""
        with self.lock:
            if key in self.cache:
                self.current_memory -= self.sizes.pop(key, 0)
                del self.cache[key]

    def clear(self):
        """Clear all L1 cache"""
        with self.lock:
            self.cache.clear()
            self.sizes.clear()
            self.current_memory = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get L1 cache statistics"""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'memory_mb': self.current_memory / (1024 * 1024),
                'max_memory_mb': self.max_memory_bytes / (1024 * 1024)
            }


class L2RedisCache:
    """
    L2 Cache: Distributed Redis cache
    - Sub-millisecond access time
    - Shared across instances
    - Persistence optional
    """

    def __init__(self, redis_client: redis.Redis, prefix: str = "l2"):
        """
        Initialize L2 cache.

        Args:
            redis_client: Redis client instance
            prefix: Key prefix for namespacing
        """
        self.redis = redis_client
        self.prefix = prefix

    def _make_key(self, key: str) -> str:
        """Create prefixed Redis key"""
        return f"{self.prefix}:{key}"

    def get(self, key: str) -> Optional[Any]:
        """Get value from L2 cache"""
        try:
            redis_key = self._make_key(key)
            data = self.redis.get(redis_key)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            logger.error(f"L2 cache get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set value in L2 cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Returns:
            True if successful
        """
        try:
            redis_key = self._make_key(key)
            data = pickle.dumps(value)
            self.redis.setex(redis_key, ttl, data)
            return True
        except Exception as e:
            logger.error(f"L2 cache set error: {e}")
            return False

    def delete(self, key: str):
        """Delete key from L2 cache"""
        try:
            redis_key = self._make_key(key)
            self.redis.delete(redis_key)
        except Exception as e:
            logger.error(f"L2 cache delete error: {e}")

    def clear(self, pattern: str = "*"):
        """Clear L2 cache keys matching pattern"""
        try:
            pattern_key = self._make_key(pattern)
            keys = self.redis.keys(pattern_key)
            if keys:
                self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"L2 cache clear error: {e}")


class L3DiskCache:
    """
    L3 Cache: Persistent disk cache
    - Millisecond to second access time
    - Large capacity
    - Survives restarts
    """

    def __init__(self, cache_dir: str = "./cache/l3", max_size_mb: int = 10240):
        """
        Initialize L3 cache.

        Args:
            cache_dir: Directory for cache files
            max_size_mb: Maximum cache size in MB
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.lock = threading.Lock()

    def _get_path(self, key: str) -> Path:
        """Get file path for cache key"""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    def get(self, key: str) -> Optional[Any]:
        """Get value from L3 cache"""
        try:
            path = self._get_path(key)
            if path.exists():
                with open(path, 'rb') as f:
                    compressed_data = f.read()
                    data = zlib.decompress(compressed_data)
                    return pickle.loads(data)
            return None
        except Exception as e:
            logger.error(f"L3 cache get error: {e}")
            return None

    def set(self, key: str, value: Any) -> bool:
        """
        Set value in L3 cache.

        Args:
            key: Cache key
            value: Value to cache

        Returns:
            True if successful
        """
        try:
            with self.lock:
                # Check total cache size
                total_size = sum(f.stat().st_size for f in self.cache_dir.glob('*.cache'))

                # Evict oldest files if necessary
                while total_size > self.max_size_bytes:
                    files = sorted(self.cache_dir.glob('*.cache'),
                                 key=lambda f: f.stat().st_mtime)
                    if not files:
                        break

                    oldest = files[0]
                    total_size -= oldest.stat().st_size
                    oldest.unlink()

                # Write new cache file
                path = self._get_path(key)
                data = pickle.dumps(value)
                compressed_data = zlib.compress(data, level=6)

                with open(path, 'wb') as f:
                    f.write(compressed_data)

                return True
        except Exception as e:
            logger.error(f"L3 cache set error: {e}")
            return False

    def delete(self, key: str):
        """Delete key from L3 cache"""
        try:
            path = self._get_path(key)
            if path.exists():
                path.unlink()
        except Exception as e:
            logger.error(f"L3 cache delete error: {e}")

    def clear(self):
        """Clear all L3 cache"""
        try:
            for file in self.cache_dir.glob('*.cache'):
                file.unlink()
        except Exception as e:
            logger.error(f"L3 cache clear error: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get L3 cache statistics"""
        try:
            files = list(self.cache_dir.glob('*.cache'))
            total_size = sum(f.stat().st_size for f in files)
            return {
                'files': len(files),
                'size_mb': total_size / (1024 * 1024),
                'max_size_mb': self.max_size_bytes / (1024 * 1024)
            }
        except Exception as e:
            logger.error(f"L3 cache stats error: {e}")
            return {'files': 0, 'size_mb': 0, 'max_size_mb': 0}


class MultiLevelCache:
    """
    Multi-level caching system with automatic cache warming
    and predictive prefetching.
    """

    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        l1_max_size: int = 1000,
        l1_max_memory_mb: int = 512,
        l2_ttl: int = 3600,
        l3_cache_dir: str = "./cache/l3",
        l3_max_size_mb: int = 10240,
        enable_compression: bool = True,
        enable_prefetch: bool = True
    ):
        """
        Initialize multi-level cache.

        Args:
            redis_client: Redis client for L2 cache
            l1_max_size: L1 cache max items
            l1_max_memory_mb: L1 cache max memory
            l2_ttl: L2 cache TTL in seconds
            l3_cache_dir: L3 cache directory
            l3_max_size_mb: L3 cache max size
            enable_compression: Enable compression for L3
            enable_prefetch: Enable predictive prefetching
        """
        self.l1 = L1MemoryCache(l1_max_size, l1_max_memory_mb)
        self.l2 = L2RedisCache(redis_client, prefix="l2") if redis_client else None
        self.l3 = L3DiskCache(l3_cache_dir, l3_max_size_mb)

        self.l2_ttl = l2_ttl
        self.enable_compression = enable_compression
        self.enable_prefetch = enable_prefetch

        self.stats = CacheStats()
        self.access_patterns: Dict[str, List[float]] = {}
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache (tries L1 -> L2 -> L3).

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        self.stats.total_requests += 1

        # Try L1 cache
        value = self.l1.get(key)
        if value is not None:
            self.stats.l1_hits += 1
            self._record_access(key)
            return value
        self.stats.l1_misses += 1

        # Try L2 cache
        if self.l2:
            value = self.l2.get(key)
            if value is not None:
                self.stats.l2_hits += 1
                # Promote to L1
                self.l1.set(key, value)
                self._record_access(key)
                return value
            self.stats.l2_misses += 1

        # Try L3 cache
        value = self.l3.get(key)
        if value is not None:
            self.stats.l3_hits += 1
            # Promote to L1 and L2
            self.l1.set(key, value)
            if self.l2:
                self.l2.set(key, value, self.l2_ttl)
            self._record_access(key)
            return value
        self.stats.l3_misses += 1

        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in all cache levels.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live (L2 only)

        Returns:
            True if cached successfully
        """
        ttl = ttl or self.l2_ttl

        # Set in all levels
        l1_success = self.l1.set(key, value)

        l2_success = True
        if self.l2:
            l2_success = self.l2.set(key, value, ttl)

        l3_success = self.l3.set(key, value)

        self._record_access(key)

        return l1_success and l2_success and l3_success

    def delete(self, key: str):
        """Delete key from all cache levels"""
        self.l1.delete(key)
        if self.l2:
            self.l2.delete(key)
        self.l3.delete(key)

        # Remove from access patterns
        with self.lock:
            if key in self.access_patterns:
                del self.access_patterns[key]

    def clear(self):
        """Clear all cache levels"""
        self.l1.clear()
        if self.l2:
            self.l2.clear()
        self.l3.clear()

        with self.lock:
            self.access_patterns.clear()

    def warm_cache(self, keys: List[str], loader_func):
        """
        Warm cache with frequently accessed keys.

        Args:
            keys: List of keys to warm
            loader_func: Function to load values (key) -> value
        """
        logger.info(f"Warming cache with {len(keys)} keys...")

        for key in keys:
            try:
                value = loader_func(key)
                if value is not None:
                    self.set(key, value)
            except Exception as e:
                logger.error(f"Cache warming error for key {key}: {e}")

        logger.info("Cache warming complete")

    def _record_access(self, key: str):
        """Record cache access for prefetching"""
        if not self.enable_prefetch:
            return

        with self.lock:
            now = time.time()
            if key not in self.access_patterns:
                self.access_patterns[key] = []

            self.access_patterns[key].append(now)

            # Keep only last 100 accesses
            if len(self.access_patterns[key]) > 100:
                self.access_patterns[key] = self.access_patterns[key][-100:]

    def get_prefetch_candidates(self, limit: int = 10) -> List[str]:
        """
        Get keys that should be prefetched based on access patterns.

        Args:
            limit: Maximum number of candidates

        Returns:
            List of keys to prefetch
        """
        if not self.enable_prefetch:
            return []

        with self.lock:
            # Calculate access frequency
            candidates = []
            for key, timestamps in self.access_patterns.items():
                if len(timestamps) < 2:
                    continue

                # Calculate average access interval
                intervals = [timestamps[i] - timestamps[i-1]
                           for i in range(1, len(timestamps))]
                avg_interval = sum(intervals) / len(intervals)

                # Predict next access time
                last_access = timestamps[-1]
                predicted_next = last_access + avg_interval

                # If predicted to be accessed soon, add to candidates
                if predicted_next - time.time() < avg_interval:
                    candidates.append((key, predicted_next))

            # Sort by predicted access time
            candidates.sort(key=lambda x: x[1])

            return [key for key, _ in candidates[:limit]]

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        return {
            'stats': {
                'l1_hits': self.stats.l1_hits,
                'l1_misses': self.stats.l1_misses,
                'l1_hit_rate': f"{self.stats.l1_hit_rate:.2f}%",
                'l2_hits': self.stats.l2_hits,
                'l2_misses': self.stats.l2_misses,
                'l2_hit_rate': f"{self.stats.l2_hit_rate:.2f}%",
                'l3_hits': self.stats.l3_hits,
                'l3_misses': self.stats.l3_misses,
                'l3_hit_rate': f"{self.stats.l3_hit_rate:.2f}%",
                'overall_hit_rate': f"{self.stats.overall_hit_rate:.2f}%",
                'total_requests': self.stats.total_requests,
                'prefetch_hits': self.stats.prefetch_hits
            },
            'l1': self.l1.get_stats(),
            'l3': self.l3.get_stats(),
            'prefetch_candidates': len(self.get_prefetch_candidates())
        }


# Global multi-level cache instance
_multi_level_cache: Optional[MultiLevelCache] = None


def get_multi_level_cache() -> MultiLevelCache:
    """Get global multi-level cache instance"""
    global _multi_level_cache

    if _multi_level_cache is None:
        try:
            from core.rate_limiter import get_redis_client
            redis_client = get_redis_client()
        except Exception as e:
            logger.warning(f"Redis not available for L2 cache: {e}")
            redis_client = None

        _multi_level_cache = MultiLevelCache(
            redis_client=redis_client,
            l1_max_size=1000,
            l1_max_memory_mb=512,
            l2_ttl=3600,
            l3_cache_dir="./cache/l3",
            l3_max_size_mb=10240,
            enable_compression=True,
            enable_prefetch=True
        )

    return _multi_level_cache


if __name__ == "__main__":
    print("Testing Multi-Level Cache...")

    # Create cache instance
    cache = MultiLevelCache(redis_client=None)

    # Test basic operations
    print("\n1. Testing basic set/get:")
    cache.set("test_key", {"data": "test_value"})
    value = cache.get("test_key")
    print(f"   Retrieved: {value}")

    # Test cache levels
    print("\n2. Testing cache levels:")
    cache.set("level_test", "data")

    # Clear L1, should hit L2/L3
    cache.l1.clear()
    value = cache.get("level_test")
    print(f"   After L1 clear: {value}")

    # Test statistics
    print("\n3. Cache statistics:")
    stats = cache.get_stats()
    print(f"   L1 hit rate: {stats['stats']['l1_hit_rate']}")
    print(f"   L3 hit rate: {stats['stats']['l3_hit_rate']}")
    print(f"   Overall hit rate: {stats['stats']['overall_hit_rate']}")

    print("\n✅ Multi-level cache test complete")
