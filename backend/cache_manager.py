"""
+==============================================================================─
|                  ORFEAS Cache Manager - In-Memory LRU Cache                 |
|         Phase 6C: Generation Result Caching for 2x Performance Gain         |
+==============================================================================─

High-performance LRU (Least Recently Used) cache with:
- O(1) get/set/evict operations using OrderedDict
- Automatic memory-based eviction
- Thread-safe concurrent access
- Comprehensive statistics tracking
- JSON-serializable configuration

Usage:
    cache = LRUCache(max_size=1000, max_memory_mb=512)
    cache.set('key', {'result': ...}, size_mb=1.5)
    result = cache.get('key')  # Returns cached result or None
    stats = cache.get_stats()  # Returns hit/miss/memory stats
"""

import threading
import time
import json
from collections import OrderedDict
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Single cache entry with metadata."""

    value: Any
    timestamp: float  # When cached (seconds since epoch)
    access_count: int = 0  # How many times retrieved
    size_mb: float = 0.0  # Memory footprint in MB
    expires_at: Optional[float] = None  # Optional TTL expiration

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at


class LRUCache:
    """
    Thread-safe in-memory LRU cache with memory limits.

    Features:
    - O(1) get/set operations
    - Automatic eviction based on size and count
    - Hit/miss/eviction statistics
    - Optional TTL support
    - Thread-safe with RLock
    """

    def __init__(
        self,
        max_size: int = 1000,
        max_memory_mb: float = 512.0,
        default_ttl_seconds: Optional[int] = None,
    ):
        """
        Initialize LRU cache.

        Args:
            max_size: Maximum number of items to store
            max_memory_mb: Maximum memory in MB before eviction
            default_ttl_seconds: Default time-to-live in seconds (None = no expiry)
        """
        self.max_size = max_size
        self.max_memory_mb = max_memory_mb
        self.default_ttl_seconds = default_ttl_seconds

        # Storage: key -> CacheEntry (OrderedDict maintains insertion order)
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()

        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "evictions_by_size": 0,
            "evictions_by_count": 0,
            "current_items": 0,
            "current_memory_mb": 0.0,
            "max_memory_seen_mb": 0.0,
        }

        # Thread safety
        self.lock = threading.RLock()

        logger.info(
            f"[CACHE] Initialized LRU cache: max_items={max_size}, "
            f"max_memory_mb={max_memory_mb}, ttl_seconds={default_ttl_seconds}"
        )

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve item from cache.

        Moves item to end (most recently used position).
        Updates access count and hit statistics.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found / expired
        """
        with self.lock:
            if key not in self.cache:
                self.stats["misses"] += 1
                return None

            entry = self.cache[key]

            # Check expiration
            if entry.is_expired():
                del self.cache[key]
                self.stats["current_items"] -= 1
                self.stats["current_memory_mb"] -= entry.size_mb
                self.stats["misses"] += 1
                logger.debug(f"[CACHE] Entry {key} expired")
                return None

            # Move to end (most recently used)
            self.cache.move_to_end(key)

            # Update entry metadata
            entry.access_count += 1
            self.stats["hits"] += 1

            return entry.value

    def set(
        self, key: str, value: Any, size_mb: float = 0.0, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Store item in cache.

        Evicts least recently used items if memory/count limits exceeded.

        Args:
            key: Cache key
            value: Value to cache
            size_mb: Size of value in MB (for memory tracking)
            ttl_seconds: Override default TTL for this entry
        """
        with self.lock:
            # Calculate expiration time
            expires_at = None
            if ttl_seconds is not None:
                expires_at = time.time() + ttl_seconds
            elif self.default_ttl_seconds is not None:
                expires_at = time.time() + self.default_ttl_seconds

            # If key exists, remove old entry size from memory count
            if key in self.cache:
                old_size = self.cache[key].size_mb
                self.stats["current_memory_mb"] -= old_size
            else:
                self.stats["current_items"] += 1

            # Evict until we have space
            self._evict_if_needed(size_mb)

            # Store new entry
            entry = CacheEntry(
                value=value,
                timestamp=time.time(),
                access_count=0,
                size_mb=size_mb,
                expires_at=expires_at,
            )
            self.cache[key] = entry
            self.stats["current_memory_mb"] += size_mb

            # Track max memory seen
            if self.stats["current_memory_mb"] > self.stats["max_memory_seen_mb"]:
                self.stats["max_memory_seen_mb"] = self.stats["current_memory_mb"]

            logger.debug(
                f"[CACHE] Stored {key}: size={size_mb:.1f}MB, "
                f"total={self.stats['current_memory_mb']:.1f}MB, items={self.stats['current_items']}"
            )

    def _evict_if_needed(self, new_size_mb: float) -> None:
        """Evict items if memory or count limits would be exceeded."""
        # Check count limit
        while len(self.cache) >= self.max_size:
            self._evict_oldest()
            self.stats["evictions_by_count"] += 1

        # Check memory limit
        while self.stats["current_memory_mb"] + new_size_mb > self.max_memory_mb and len(
            self.cache
        ) > 0:
            self._evict_oldest()
            self.stats["evictions_by_size"] += 1

    def _evict_oldest(self) -> None:
        """Remove least recently used (oldest) item."""
        if not self.cache:
            return

        # Remove first item (oldest due to OrderedDict ordering)
        key, entry = self.cache.popitem(last=False)
        self.stats["current_items"] -= 1
        self.stats["current_memory_mb"] -= entry.size_mb
        self.stats["evictions"] += 1
        logger.debug(f"[CACHE] Evicted {key} (age={time.time() - entry.timestamp:.1f}s)")

    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            count = len(self.cache)
            self.cache.clear()
            self.stats["current_items"] = 0
            self.stats["current_memory_mb"] = 0.0
            logger.info(f"[CACHE] Cleared {count} entries")

    def delete(self, key: str) -> bool:
        """Delete specific cache entry."""
        with self.lock:
            if key not in self.cache:
                return False

            entry = self.cache.pop(key)
            self.stats["current_items"] -= 1
            self.stats["current_memory_mb"] -= entry.size_mb
            logger.debug(f"[CACHE] Deleted {key}")
            return True

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with hits, misses, hit_rate, memory usage, etc.
        """
        with self.lock:
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (
                (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            )

            return {
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "hit_rate_percent": round(hit_rate, 2),
                "evictions": self.stats["evictions"],
                "evictions_by_count": self.stats["evictions_by_count"],
                "evictions_by_size": self.stats["evictions_by_size"],
                "current_items": self.stats["current_items"],
                "current_memory_mb": round(self.stats["current_memory_mb"], 2),
                "max_items": self.max_size,
                "max_memory_mb": self.max_memory_mb,
                "memory_utilization_percent": round(
                    self.stats["current_memory_mb"] / self.max_memory_mb * 100, 2
                ),
                "max_memory_seen_mb": round(self.stats["max_memory_seen_mb"], 2),
            }

    def get_entries_summary(self) -> list[Dict[str, Any]]:
        """Get summary of all cached entries."""
        with self.lock:
            entries = []
            for key, entry in self.cache.items():
                entries.append(
                    {
                        "key": key,
                        "size_mb": round(entry.size_mb, 2),
                        "timestamp": entry.timestamp,
                        "age_seconds": round(time.time() - entry.timestamp, 1),
                        "access_count": entry.access_count,
                        "expires_at": entry.expires_at,
                        "expired": entry.is_expired(),
                    }
                )
            return entries

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        with self.lock:
            self.stats["hits"] = 0
            self.stats["misses"] = 0
            self.stats["evictions"] = 0
            self.stats["evictions_by_count"] = 0
            self.stats["evictions_by_size"] = 0
            logger.info("[CACHE] Statistics reset")

    def get_config(self) -> Dict[str, Any]:
        """Get current cache configuration."""
        return {
            "max_size": self.max_size,
            "max_memory_mb": self.max_memory_mb,
            "default_ttl_seconds": self.default_ttl_seconds,
        }

    def update_config(self, max_size: Optional[int] = None, max_memory_mb: Optional[float] = None) -> None:
        """Update cache configuration."""
        with self.lock:
            if max_size is not None:
                self.max_size = max_size
                # Evict if new size is smaller than current items
                while len(self.cache) > self.max_size:
                    self._evict_oldest()
                logger.info(f"[CACHE] Updated max_size to {max_size}")

            if max_memory_mb is not None:
                self.max_memory_mb = max_memory_mb
                # Evict if new memory limit is smaller than current usage
                while (
                    self.stats["current_memory_mb"] > self.max_memory_mb and len(self.cache) > 0
                ):
                    self._evict_oldest()
                logger.info(f"[CACHE] Updated max_memory_mb to {max_memory_mb}")

    def __len__(self) -> int:
        """Return number of items in cache."""
        with self.lock:
            return len(self.cache)

    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_stats()
        return (
            f"LRUCache(items={stats['current_items']}/{self.max_size}, "
            f"memory={stats['current_memory_mb']:.1f}/{self.max_memory_mb}MB, "
            f"hit_rate={stats['hit_rate_percent']:.1f}%)"
        )


# Global cache instance
_cache_instance: Optional[LRUCache] = None
_cache_lock = threading.Lock()


def get_cache(
    max_size: int = 1000,
    max_memory_mb: float = 512.0,
    default_ttl_seconds: Optional[int] = None,
) -> LRUCache:
    """
    Get or create the global cache instance.

    Args:
        max_size: Maximum items (only used on first call)
        max_memory_mb: Maximum memory MB (only used on first call)
        default_ttl_seconds: Default TTL (only used on first call)

    Returns:
        Global LRUCache instance
    """
    global _cache_instance

    if _cache_instance is None:
        with _cache_lock:
            if _cache_instance is None:
                _cache_instance = LRUCache(
                    max_size=max_size,
                    max_memory_mb=max_memory_mb,
                    default_ttl_seconds=default_ttl_seconds,
                )

    return _cache_instance


def clear_cache() -> None:
    """Clear the global cache instance."""
    global _cache_instance
    if _cache_instance is not None:
        _cache_instance.clear()
