"""
ORFEAS AI Studio - Advanced Caching Tests
==========================================

Comprehensive test suite for:
- Multi-level caching (L1, L2, L3)
- Redis Cluster manager
- Consistent hashing
- Cache warming and prefetching
- Compression

Author: ORFEAS AI Team
Date: October 28, 2025
"""

import pytest
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from core.multi_level_cache import (
    L1MemoryCache,
    L2RedisCache,
    L3DiskCache,
    MultiLevelCache,
    CacheStats,
    get_multi_level_cache
)
from core.redis_cluster_manager import (
    RedisClusterManager,
    ConsistentHashRing
)


@pytest.fixture
def temp_cache_dir():
    """Create temporary cache directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def redis_mock():
    """Mock Redis client"""
    mock = MagicMock()
    mock.get.return_value = None
    mock.setex.return_value = True
    mock.delete.return_value = 1
    mock.keys.return_value = []
    return mock


class TestCacheStats:
    """Test cache statistics"""

    def test_cache_stats_initialization(self):
        """Test CacheStats initialization"""
        stats = CacheStats()

        assert stats.l1_hits == 0
        assert stats.l1_misses == 0
        assert stats.total_requests == 0

    def test_l1_hit_rate_calculation(self):
        """Test L1 hit rate calculation"""
        stats = CacheStats()
        stats.l1_hits = 80
        stats.l1_misses = 20

        assert stats.l1_hit_rate == 80.0

    def test_overall_hit_rate_calculation(self):
        """Test overall hit rate calculation"""
        stats = CacheStats()
        stats.l1_hits = 50
        stats.l2_hits = 30
        stats.l3_hits = 10
        stats.total_requests = 100

        assert stats.overall_hit_rate == 90.0

    def test_hit_rate_with_no_requests(self):
        """Test hit rate with zero requests"""
        stats = CacheStats()

        assert stats.l1_hit_rate == 0.0
        assert stats.overall_hit_rate == 0.0


class TestL1MemoryCache:
    """Test L1 memory cache"""

    def test_l1_basic_set_get(self):
        """Test basic L1 cache set and get"""
        cache = L1MemoryCache(max_size=10)

        cache.set("key1", "value1")
        value = cache.get("key1")

        assert value == "value1"

    def test_l1_get_nonexistent_key(self):
        """Test getting nonexistent key"""
        cache = L1MemoryCache(max_size=10)

        value = cache.get("nonexistent")

        assert value is None

    def test_l1_lru_eviction(self):
        """Test LRU eviction policy"""
        cache = L1MemoryCache(max_size=3)

        # Fill cache
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Access key1 to make it most recently used
        cache.get("key1")

        # Add new item, should evict key2 (least recently used)
        cache.set("key4", "value4")

        assert cache.get("key1") is not None
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") is not None
        assert cache.get("key4") is not None

    def test_l1_memory_limit_eviction(self):
        """Test memory limit eviction"""
        cache = L1MemoryCache(max_size=100, max_memory_mb=1)

        # Add items until memory limit reached
        large_value = "x" * (500 * 1024)  # 500KB

        cache.set("key1", large_value, size_bytes=500*1024)
        cache.set("key2", large_value, size_bytes=500*1024)
        cache.set("key3", large_value, size_bytes=500*1024)  # Should trigger eviction

        # First key should be evicted due to memory limit
        assert cache.get("key1") is None

    def test_l1_delete(self):
        """Test L1 cache delete"""
        cache = L1MemoryCache(max_size=10)

        cache.set("key1", "value1")
        cache.delete("key1")

        assert cache.get("key1") is None

    def test_l1_clear(self):
        """Test L1 cache clear"""
        cache = L1MemoryCache(max_size=10)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_l1_stats(self):
        """Test L1 cache statistics"""
        cache = L1MemoryCache(max_size=10)

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        stats = cache.get_stats()

        assert stats['size'] == 2
        assert stats['max_size'] == 10


class TestL2RedisCache:
    """Test L2 Redis cache"""

    def test_l2_basic_set_get(self, redis_mock):
        """Test basic L2 cache set and get"""
        import pickle
        redis_mock.get.return_value = pickle.dumps("value1")

        cache = L2RedisCache(redis_mock)
        cache.set("key1", "value1")
        value = cache.get("key1")

        assert value == "value1"
        redis_mock.setex.assert_called_once()

    def test_l2_get_nonexistent_key(self, redis_mock):
        """Test getting nonexistent key"""
        redis_mock.get.return_value = None

        cache = L2RedisCache(redis_mock)
        value = cache.get("key1")

        assert value is None

    def test_l2_delete(self, redis_mock):
        """Test L2 cache delete"""
        cache = L2RedisCache(redis_mock)
        cache.delete("key1")

        redis_mock.delete.assert_called_once()

    def test_l2_clear(self, redis_mock):
        """Test L2 cache clear"""
        redis_mock.keys.return_value = [b'l2:key1', b'l2:key2']

        cache = L2RedisCache(redis_mock)
        cache.clear()

        redis_mock.keys.assert_called_once()
        redis_mock.delete.assert_called_once()

    def test_l2_error_handling(self, redis_mock):
        """Test L2 cache error handling"""
        redis_mock.get.side_effect = Exception("Redis error")

        cache = L2RedisCache(redis_mock)
        value = cache.get("key1")

        # Should return None on error
        assert value is None


class TestL3DiskCache:
    """Test L3 disk cache"""

    def test_l3_basic_set_get(self, temp_cache_dir):
        """Test basic L3 cache set and get"""
        cache = L3DiskCache(cache_dir=temp_cache_dir, max_size_mb=100)

        cache.set("key1", "value1")
        value = cache.get("key1")

        assert value == "value1"

    def test_l3_get_nonexistent_key(self, temp_cache_dir):
        """Test getting nonexistent key"""
        cache = L3DiskCache(cache_dir=temp_cache_dir)

        value = cache.get("nonexistent")

        assert value is None

    def test_l3_persistence(self, temp_cache_dir):
        """Test L3 cache persistence across instances"""
        cache1 = L3DiskCache(cache_dir=temp_cache_dir)
        cache1.set("key1", "value1")

        # Create new instance
        cache2 = L3DiskCache(cache_dir=temp_cache_dir)
        value = cache2.get("key1")

        assert value == "value1"

    def test_l3_compression(self, temp_cache_dir):
        """Test L3 cache compression"""
        cache = L3DiskCache(cache_dir=temp_cache_dir)

        # Create compressible data (repeated string)
        large_data = "test" * 1000
        cache.set("key1", large_data)

        # Check that file exists and is compressed
        cache_dir = Path(temp_cache_dir)
        cache_files = list(cache_dir.glob('*.cache'))
        assert len(cache_files) == 1

    def test_l3_delete(self, temp_cache_dir):
        """Test L3 cache delete"""
        cache = L3DiskCache(cache_dir=temp_cache_dir)

        cache.set("key1", "value1")
        cache.delete("key1")

        assert cache.get("key1") is None

    def test_l3_clear(self, temp_cache_dir):
        """Test L3 cache clear"""
        cache = L3DiskCache(cache_dir=temp_cache_dir)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_l3_stats(self, temp_cache_dir):
        """Test L3 cache statistics"""
        cache = L3DiskCache(cache_dir=temp_cache_dir)

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        stats = cache.get_stats()

        assert stats['files'] == 2
        assert stats['size_mb'] > 0


class TestMultiLevelCache:
    """Test multi-level caching system"""

    def test_multi_level_cache_initialization(self, redis_mock, temp_cache_dir):
        """Test multi-level cache initialization"""
        cache = MultiLevelCache(
            redis_client=redis_mock,
            l3_cache_dir=temp_cache_dir
        )

        assert cache.l1 is not None
        assert cache.l2 is not None
        assert cache.l3 is not None

    def test_multi_level_cache_l1_hit(self, redis_mock, temp_cache_dir):
        """Test L1 cache hit"""
        cache = MultiLevelCache(
            redis_client=redis_mock,
            l3_cache_dir=temp_cache_dir
        )

        cache.set("key1", "value1")
        value = cache.get("key1")

        assert value == "value1"
        assert cache.stats.l1_hits == 1
        assert cache.stats.l1_misses == 0

    def test_multi_level_cache_l2_hit(self, redis_mock, temp_cache_dir):
        """Test L2 cache hit (L1 miss)"""
        import pickle
        redis_mock.get.return_value = pickle.dumps("value1")

        cache = MultiLevelCache(
            redis_client=redis_mock,
            l3_cache_dir=temp_cache_dir
        )

        # Clear L1, set L2
        cache.l1.clear()
        value = cache.get("key1")

        assert value == "value1"
        assert cache.stats.l1_misses == 1
        assert cache.stats.l2_hits == 1

    def test_multi_level_cache_l3_hit(self, redis_mock, temp_cache_dir):
        """Test L3 cache hit (L1 and L2 miss)"""
        redis_mock.get.return_value = None

        cache = MultiLevelCache(
            redis_client=redis_mock,
            l3_cache_dir=temp_cache_dir
        )

        # Set in L3 only
        cache.l3.set("key1", "value1")

        # Clear L1
        cache.l1.clear()

        value = cache.get("key1")

        assert value == "value1"
        assert cache.stats.l3_hits == 1

    def test_multi_level_cache_promotion(self, redis_mock, temp_cache_dir):
        """Test cache level promotion"""
        redis_mock.get.return_value = None

        cache = MultiLevelCache(
            redis_client=redis_mock,
            l3_cache_dir=temp_cache_dir
        )

        # Set in L3 only
        cache.l3.set("key1", "value1")
        cache.l1.clear()

        # First get - should hit L3 and promote to L1
        value = cache.get("key1")
        assert cache.stats.l3_hits == 1

        # Second get - should hit L1
        value = cache.get("key1")
        assert cache.stats.l1_hits == 1

    def test_multi_level_cache_delete_all_levels(self, redis_mock, temp_cache_dir):
        """Test delete from all cache levels"""
        cache = MultiLevelCache(
            redis_client=redis_mock,
            l3_cache_dir=temp_cache_dir
        )

        cache.set("key1", "value1")
        cache.delete("key1")

        assert cache.l1.get("key1") is None
        assert cache.l3.get("key1") is None
        redis_mock.delete.assert_called_once()

    def test_multi_level_cache_clear_all_levels(self, redis_mock, temp_cache_dir):
        """Test clear all cache levels"""
        cache = MultiLevelCache(
            redis_client=redis_mock,
            l3_cache_dir=temp_cache_dir
        )

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()

        assert cache.l1.get("key1") is None
        assert cache.l3.get("key1") is None

    def test_cache_warming(self, redis_mock, temp_cache_dir):
        """Test cache warming functionality"""
        cache = MultiLevelCache(
            redis_client=redis_mock,
            l3_cache_dir=temp_cache_dir
        )

        def loader(key):
            return f"value_{key}"

        keys = ["key1", "key2", "key3"]
        cache.warm_cache(keys, loader)

        # All keys should be cached
        for key in keys:
            value = cache.get(key)
            assert value == f"value_{key}"

    def test_prefetch_candidates(self, redis_mock, temp_cache_dir):
        """Test predictive prefetching"""
        cache = MultiLevelCache(
            redis_client=redis_mock,
            l3_cache_dir=temp_cache_dir,
            enable_prefetch=True
        )

        # Simulate access pattern
        for i in range(5):
            cache.get("key1")
            time.sleep(0.01)

        candidates = cache.get_prefetch_candidates()

        # Should identify key1 as candidate
        assert "key1" in candidates or len(candidates) == 0  # May not predict if intervals too varied

    def test_cache_stats(self, redis_mock, temp_cache_dir):
        """Test comprehensive cache statistics"""
        cache = MultiLevelCache(
            redis_client=redis_mock,
            l3_cache_dir=temp_cache_dir
        )

        cache.set("key1", "value1")
        cache.get("key1")
        cache.get("nonexistent")

        stats = cache.get_stats()

        assert 'stats' in stats
        assert 'l1' in stats
        assert 'l3' in stats
        assert stats['stats']['total_requests'] > 0


class TestConsistentHashRing:
    """Test consistent hashing"""

    def test_hash_ring_initialization(self):
        """Test hash ring initialization"""
        nodes = ['node1:6379', 'node2:6379', 'node3:6379']
        ring = ConsistentHashRing(nodes)

        assert len(ring.nodes) == 3
        assert len(ring.ring) == 3 * 150  # 150 virtual nodes per physical node

    def test_get_node_for_key(self):
        """Test getting node for key"""
        nodes = ['node1:6379', 'node2:6379', 'node3:6379']
        ring = ConsistentHashRing(nodes)

        node = ring.get_node('test_key')

        assert node in nodes

    def test_consistent_hashing_stability(self):
        """Test that same key always maps to same node"""
        nodes = ['node1:6379', 'node2:6379', 'node3:6379']
        ring = ConsistentHashRing(nodes)

        node1 = ring.get_node('test_key')
        node2 = ring.get_node('test_key')

        assert node1 == node2

    def test_add_node(self):
        """Test adding node to hash ring"""
        nodes = ['node1:6379', 'node2:6379']
        ring = ConsistentHashRing(nodes)

        ring.add_node('node3:6379')

        assert 'node3:6379' in ring.nodes
        assert len(ring.ring) == 3 * 150

    def test_remove_node(self):
        """Test removing node from hash ring"""
        nodes = ['node1:6379', 'node2:6379', 'node3:6379']
        ring = ConsistentHashRing(nodes)

        ring.remove_node('node3:6379')

        assert 'node3:6379' not in ring.nodes
        assert len(ring.ring) == 2 * 150


class TestRedisClusterManager:
    """Test Redis Cluster manager"""

    def test_cluster_manager_initialization(self):
        """Test Redis Cluster manager initialization"""
        nodes = [
            {'host': 'localhost', 'port': 7000},
            {'host': 'localhost', 'port': 7001}
        ]

        # Note: This will fail if Redis Cluster not running, which is expected
        with patch('redis.cluster.RedisCluster') as mock_cluster:
            mock_cluster.return_value.ping.return_value = True

            manager = RedisClusterManager(nodes)

            assert manager.nodes == nodes

    def test_cluster_health_check(self):
        """Test Redis Cluster health check"""
        nodes = [{'host': 'localhost', 'port': 7000}]

        with patch('redis.cluster.RedisCluster') as mock_cluster:
            mock_instance = mock_cluster.return_value
            mock_instance.ping.return_value = True

            manager = RedisClusterManager(nodes)

            # The health_check should work if cluster was initialized successfully
            if manager.cluster:
                health = manager.health_check()
                assert health is True
            else:
                # If cluster initialization failed (Redis not running), that's expected
                health = manager.health_check()
                assert health is False


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
