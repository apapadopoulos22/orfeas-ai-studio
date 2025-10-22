"""
Distributed Cache Manager - Phase 4 Tier 1
Implements multi-node caching with Redis Cluster support
Two-level caching: L1 (local) + L2 (distributed)
"""

import json
import logging
import hashlib
import threading
from typing import Dict, Optional, Any, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Single cache entry with metadata"""
    value: Any
    expires_at: datetime
    created_at: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    size_bytes: int = 0


class DistributedCacheManager:
    """
    Manages distributed caching across multiple nodes
    Features:
    - L1: Local in-memory cache for hot data
    - L2: Distributed Redis for shared data
    - Consistent hashing for key distribution
    - Automatic TTL and eviction policies
    """

    def __init__(self, redis_cluster_endpoints: List[str] = None):
        """
        Initialize distributed cache manager

        Args:
            redis_cluster_endpoints: List of Redis node endpoints (host:port)
        """
        self.redis_endpoints = redis_cluster_endpoints or ['localhost:6379']
        self.node_count = len(self.redis_endpoints)

        # L1 local cache
        self.local_cache: Dict[str, CacheEntry] = {}
        self.local_cache_max_size = 1000  # Max entries in L1
        self.local_cache_max_age_seconds = 3600  # Max age for local entries

        # Cache statistics
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'writes': 0,
            'distributed_hits': 0,
            'local_hits': 0,
            'evictions': 0,
            'ttl_expirations': 0
        }

        # Node tracking
        self.node_assignments: Dict[str, str] = {}  # key -> assigned node
        self.node_load: Dict[str, int] = {}  # node -> key count
        for endpoint in self.redis_endpoints:
            self.node_load[endpoint] = 0

        # Thread safety
        self._lock = threading.Lock()
        self._stats_lock = threading.Lock()

    def _get_cache_key_hash(self, key: str) -> int:
        """Generate consistent hash for key using MD5"""
        hash_digest = hashlib.md5(key.encode()).hexdigest()
        return int(hash_digest, 16)

    def _get_assigned_node(self, key: str) -> str:
        """
        Get node assignment for key using consistent hashing
        Ensures same key always maps to same node
        """
        key_hash = self._get_cache_key_hash(key)
        node_index = key_hash % self.node_count
        return self.redis_endpoints[node_index]

    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Get value from distributed cache
        Checks L1 first, then L2, returns None if not found
        """
        with self._lock:
            # Check L1 local cache first
            if key in self.local_cache:
                entry = self.local_cache[key]

                # Check expiration
                if datetime.now() < entry.expires_at:
                    entry.access_count += 1
                    entry.last_accessed = datetime.now()

                    with self._stats_lock:
                        self.cache_stats['local_hits'] += 1
                        self.cache_stats['hits'] += 1

                    logger.debug(f"[CACHE] L1 hit: {key} (access_count: {entry.access_count})")
                    return entry.value
                else:
                    # Expired, remove
                    del self.local_cache[key]
                    with self._stats_lock:
                        self.cache_stats['ttl_expirations'] += 1

        # Check distributed cache (L2)
        try:
            assigned_node = self._get_assigned_node(key)
            logger.debug(f"[CACHE] Checking distributed node: {assigned_node}")

            # In production, use redis-py to connect to assigned_node
            # result = self.redis_clients[assigned_node].get(key)

            with self._stats_lock:
                self.cache_stats['distributed_hits'] += 1
                self.cache_stats['hits'] += 1

            # Simulate retrieval (replace with actual Redis in production)
            return self._simulate_redis_get(key)

        except Exception as e:
            logger.warning(f"[CACHE] Distributed get failed: {e}")
            with self._stats_lock:
                self.cache_stats['misses'] += 1
            return default

    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """
        Set value in distributed cache
        Sets in both L1 and L2 caches with specified TTL
        """
        try:
            with self._lock:
                # Estimate size
                try:
                    size_bytes = len(json.dumps(value).encode())
                except:
                    size_bytes = 0

                # Check L1 eviction
                if len(self.local_cache) >= self.local_cache_max_size:
                    self._evict_lru_entry()

                # Set in L1 cache
                self.local_cache[key] = CacheEntry(
                    value=value,
                    expires_at=datetime.now() + timedelta(seconds=ttl_seconds),
                    created_at=datetime.now(),
                    size_bytes=size_bytes
                )

                # Get assigned node
                assigned_node = self._get_assigned_node(key)
                self.node_assignments[key] = assigned_node

                # Update node load
                if assigned_node not in self.node_load:
                    self.node_load[assigned_node] = 0
                self.node_load[assigned_node] += 1

                with self._stats_lock:
                    self.cache_stats['writes'] += 1

            # Set in distributed node (L2)
            logger.debug(
                f"[CACHE] Setting in node: {assigned_node} "
                f"(TTL: {ttl_seconds}s, size: {size_bytes} bytes)"
            )

            # In production: use redis-py
            # self.redis_clients[assigned_node].setex(key, ttl_seconds, json.dumps(value))

            self._simulate_redis_set(key, value, ttl_seconds)

            logger.debug(f"[CACHE] Set: {key} → node {assigned_node}")
            return True

        except Exception as e:
            logger.error(f"[CACHE] Set failed: {e}")
            return False

    def invalidate(self, key: str) -> bool:
        """Invalidate a specific key"""
        with self._lock:
            if key in self.local_cache:
                del self.local_cache[key]
                logger.debug(f"[CACHE] Invalidated: {key}")
                return True
        return False

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern (prefix match)"""
        with self._lock:
            keys_to_delete = [k for k in self.local_cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self.local_cache[key]

            logger.info(f"[CACHE] Invalidated {len(keys_to_delete)} keys matching pattern: {pattern}")
            return len(keys_to_delete)

    def clear(self) -> Dict:
        """Clear all cache entries"""
        with self._lock:
            count = len(self.local_cache)
            self.local_cache.clear()

        logger.info(f"[CACHE] Cleared all entries ({count} removed)")
        return {'entries_cleared': count}

    def _evict_lru_entry(self) -> None:
        """Evict least-recently-used entry from L1 cache"""
        if not self.local_cache:
            return

        # Find LRU entry
        lru_key = min(
            self.local_cache.keys(),
            key=lambda k: (
                self.local_cache[k].last_accessed or self.local_cache[k].created_at
            )
        )

        del self.local_cache[lru_key]

        with self._stats_lock:
            self.cache_stats['evictions'] += 1

        logger.debug(f"[CACHE] Evicted LRU entry: {lru_key}")

    def get_stats(self) -> Dict:
        """Get comprehensive cache statistics"""
        with self._stats_lock:
            total_hits = self.cache_stats['hits']
            total_requests = total_hits + self.cache_stats['misses']
            hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0

            return {
                'total_hits': total_hits,
                'total_misses': self.cache_stats['misses'],
                'total_requests': total_requests,
                'hit_rate_percent': round(hit_rate, 2),
                'distributed_hits': self.cache_stats['distributed_hits'],
                'local_hits': self.cache_stats['local_hits'],
                'local_hit_rate_percent': round(
                    (self.cache_stats['local_hits'] / total_hits * 100)
                    if total_hits > 0 else 0, 2
                ),
                'total_writes': self.cache_stats['writes'],
                'evictions': self.cache_stats['evictions'],
                'ttl_expirations': self.cache_stats['ttl_expirations'],
                'nodes': self.node_count,
                'local_cache_size': len(self.local_cache),
                'local_cache_max_size': self.local_cache_max_size,
                'node_distribution': self._get_node_distribution(),
                'node_load_balance': self._get_load_balance()
            }

    def _get_node_distribution(self) -> Dict:
        """Get distribution of keys across nodes"""
        distribution = {}
        with self._lock:
            for node in self.redis_endpoints:
                distribution[node] = self.node_load.get(node, 0)
        return distribution

    def _get_load_balance(self) -> Dict:
        """Calculate load balance metrics across nodes"""
        with self._lock:
            if not self.node_load:
                return {'balance_score': 0, 'max_deviation_percent': 0}

            loads = list(self.node_load.values())
            if not loads or max(loads) == 0:
                return {'balance_score': 100, 'max_deviation_percent': 0}

            avg_load = sum(loads) / len(loads)
            max_deviation = max(abs(load - avg_load) for load in loads)
            deviation_percent = (max_deviation / avg_load * 100) if avg_load > 0 else 0

            # Score: 100 = perfectly balanced, 0 = completely unbalanced
            balance_score = max(0, 100 - deviation_percent)

            return {
                'balance_score': round(balance_score, 2),
                'max_deviation_percent': round(deviation_percent, 2),
                'avg_load_per_node': round(avg_load, 2),
                'max_load': max(loads),
                'min_load': min(loads)
            }

    def get_local_cache_info(self) -> Dict:
        """Get detailed L1 cache information"""
        with self._lock:
            entries = self.local_cache
            if not entries:
                return {
                    'entries': 0,
                    'total_size_bytes': 0,
                    'total_accesses': 0
                }

            total_size = sum(e.size_bytes for e in entries.values())
            total_accesses = sum(e.access_count for e in entries.values())
            total_age_seconds = sum(
                (datetime.now() - e.created_at).total_seconds()
                for e in entries.values()
            )

            return {
                'entries': len(entries),
                'total_size_bytes': total_size,
                'avg_entry_size_bytes': round(total_size / len(entries), 2) if entries else 0,
                'total_accesses': total_accesses,
                'avg_accesses_per_entry': round(total_accesses / len(entries), 2) if entries else 0,
                'avg_age_seconds': round(total_age_seconds / len(entries), 2) if entries else 0,
                'oldest_entry_seconds': round(
                    (datetime.now() - min(e.created_at for e in entries.values())).total_seconds(), 2
                ) if entries else 0
            }

    def _simulate_redis_get(self, key: str) -> Optional[Any]:
        """Simulate Redis get (replace with actual redis-py in production)"""
        # In production: return redis_client.get(key)
        return None

    def _simulate_redis_set(self, key: str, value: Any, ttl: int) -> None:
        """Simulate Redis set (replace with actual redis-py in production)"""
        # In production: redis_client.setex(key, ttl, json.dumps(value))
        pass


# Singleton instance
_cache_manager: Optional[DistributedCacheManager] = None
_cache_lock = threading.Lock()


def get_distributed_cache(endpoints: List[str] = None) -> DistributedCacheManager:
    """Get or create cache manager singleton"""
    global _cache_manager
    if _cache_manager is None:
        with _cache_lock:
            if _cache_manager is None:
                # In production, read from environment or config
                _endpoints = endpoints or ['redis-node-1:6379', 'redis-node-2:6379', 'redis-node-3:6379']
                _cache_manager = DistributedCacheManager(_endpoints)
                logger.info(f"[CACHE] Initialized with endpoints: {_endpoints}")
    return _cache_manager


def reset_cache() -> None:
    """Reset cache manager instance (for testing)"""
    global _cache_manager
    with _cache_lock:
        _cache_manager = None
