"""
+==============================================================================─
|              ORFEAS Cache Manager Tests - Unit Test Suite                   |
|              Testing LRU cache behavior, statistics, and thread safety      |
+==============================================================================─
"""

import pytest
import time
import threading
from pathlib import Path
import sys

backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from cache_manager import LRUCache, get_cache, clear_cache


@pytest.mark.unit
class TestLRUCacheBasics:
    """Test basic LRU cache operations."""

    def test_cache_initialization(self):
        """Test cache initializes with correct parameters."""
        cache = LRUCache(max_size=100, max_memory_mb=256.0)
        assert cache.max_size == 100
        assert cache.max_memory_mb == 256.0
        assert len(cache) == 0
        assert cache.stats["hits"] == 0
        assert cache.stats["misses"] == 0

    def test_cache_set_and_get(self):
        """Test basic set and get operations."""
        cache = LRUCache()
        cache.set("key1", "value1", size_mb=1.0)
        assert cache.get("key1") == "value1"
        assert cache.stats["hits"] == 1
        assert cache.stats["misses"] == 0

    def test_cache_miss(self):
        """Test cache miss tracking."""
        cache = LRUCache()
        result = cache.get("nonexistent")
        assert result is None
        assert cache.stats["misses"] == 1
        assert cache.stats["hits"] == 0

    def test_cache_delete(self):
        """Test explicit cache deletion."""
        cache = LRUCache()
        cache.set("key1", "value1", size_mb=1.0)
        assert cache.get("key1") == "value1"
        assert cache.delete("key1") is True
        assert cache.get("key1") is None
        assert cache.delete("key1") is False

    def test_cache_clear(self):
        """Test clearing all cache entries."""
        cache = LRUCache()
        cache.set("key1", "value1", size_mb=1.0)
        cache.set("key2", "value2", size_mb=1.0)
        assert len(cache) == 2
        cache.clear()
        assert len(cache) == 0
        assert cache.stats["current_items"] == 0


@pytest.mark.unit
class TestLRUEviction:
    """Test LRU eviction policies."""

    def test_eviction_by_count(self):
        """Test eviction when max item count is reached."""
        cache = LRUCache(max_size=3)

        # Fill cache
        cache.set("a", "value_a", size_mb=1.0)
        cache.set("b", "value_b", size_mb=1.0)
        cache.set("c", "value_c", size_mb=1.0)
        assert len(cache) == 3

        # Add one more, should evict 'a' (oldest/least recently used)
        cache.set("d", "value_d", size_mb=1.0)
        assert len(cache) == 3
        assert cache.get("a") is None  # 'a' was evicted
        assert cache.get("b") == "value_b"  # 'b' still in cache
        assert cache.stats["evictions"] == 1

    def test_eviction_by_memory(self):
        """Test eviction when max memory is reached."""
        cache = LRUCache(max_size=1000, max_memory_mb=15.0)

        # Add items that total 12MB
        cache.set("x", "big_data_x", size_mb=6.0)
        cache.set("y", "big_data_y", size_mb=6.0)
        assert len(cache) == 2
        assert cache.stats["current_memory_mb"] == pytest.approx(12.0, abs=0.1)

        # Try to add another 6MB item, should evict 'x'
        cache.set("z", "big_data_z", size_mb=6.0)
        assert len(cache) == 2  # Only 2 items fit
        assert cache.get("x") is None  # 'x' was evicted
        assert cache.get("y") == "big_data_y"
        assert cache.get("z") == "big_data_z"
        assert cache.stats["evictions"] >= 1

    def test_lru_order_maintained(self):
        """Test that LRU order is properly maintained on access."""
        cache = LRUCache(max_size=3)

        cache.set("a", "value_a", size_mb=1.0)
        cache.set("b", "value_b", size_mb=1.0)
        cache.set("c", "value_c", size_mb=1.0)

        # Access 'a' to make it recently used
        cache.get("a")
        cache.get("a")

        # Now 'b' is least recently used
        cache.set("d", "value_d", size_mb=1.0)  # Should evict 'b'
        assert cache.get("a") == "value_a"  # 'a' still there (recently accessed)
        assert cache.get("b") is None  # 'b' was evicted
        assert cache.get("c") == "value_c"

    def test_eviction_counter(self):
        """Test eviction counter accuracy."""
        cache = LRUCache(max_size=2)
        cache.set("a", "value_a", size_mb=1.0)
        cache.set("b", "value_b", size_mb=1.0)
        assert cache.stats["evictions"] == 0

        cache.set("c", "value_c", size_mb=1.0)
        assert cache.stats["evictions"] == 1

        cache.set("d", "value_d", size_mb=1.0)
        assert cache.stats["evictions"] == 2


@pytest.mark.unit
class TestCacheStatistics:
    """Test cache statistics tracking."""

    def test_hit_rate_calculation(self):
        """Test hit rate percentage calculation."""
        cache = LRUCache()
        cache.set("key", "value", size_mb=1.0)

        # 2 hits, 1 miss
        cache.get("key")
        cache.get("key")
        cache.get("nonexistent")

        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate_percent"] == pytest.approx(66.67, abs=0.1)

    def test_memory_tracking(self):
        """Test accurate memory usage tracking."""
        cache = LRUCache()
        cache.set("a", "value_a", size_mb=5.0)
        cache.set("b", "value_b", size_mb=3.0)

        stats = cache.get_stats()
        assert stats["current_memory_mb"] == pytest.approx(8.0, abs=0.1)
        assert stats["current_items"] == 2

    def test_stats_reset(self):
        """Test statistics reset."""
        cache = LRUCache()
        cache.set("key", "value", size_mb=1.0)
        cache.get("key")
        cache.get("key")
        cache.get("nonexistent")

        assert cache.stats["hits"] == 2
        assert cache.stats["misses"] == 1

        cache.reset_stats()
        assert cache.stats["hits"] == 0
        assert cache.stats["misses"] == 0

    def test_max_memory_tracking(self):
        """Test max memory seen tracking."""
        cache = LRUCache(max_memory_mb=100.0)
        cache.set("a", "value_a", size_mb=30.0)
        cache.set("b", "value_b", size_mb=20.0)

        stats = cache.get_stats()
        assert stats["max_memory_seen_mb"] == pytest.approx(50.0, abs=0.1)


@pytest.mark.unit
class TestCacheTTL:
    """Test time-to-live (TTL) expiration."""

    def test_entry_ttl_expiration(self):
        """Test that entries expire after TTL."""
        cache = LRUCache()
        cache.set("key", "value", size_mb=1.0, ttl_seconds=1)

        # Should be in cache initially
        assert cache.get("key") == "value"

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired now
        assert cache.get("key") is None
        assert cache.stats["misses"] == 1

    def test_default_ttl(self):
        """Test default TTL for cache."""
        cache = LRUCache(default_ttl_seconds=1)
        cache.set("key", "value", size_mb=1.0)

        # Should expire after default TTL
        time.sleep(1.1)
        assert cache.get("key") is None

    def test_override_ttl(self):
        """Test overriding default TTL per entry."""
        cache = LRUCache(default_ttl_seconds=5)
        cache.set("key", "value", size_mb=1.0, ttl_seconds=1)

        # Should expire after 1 second (not 5)
        time.sleep(1.1)
        assert cache.get("key") is None


@pytest.mark.unit
class TestCacheConfiguration:
    """Test cache configuration and updates."""

    def test_get_config(self):
        """Test getting cache configuration."""
        cache = LRUCache(max_size=500, max_memory_mb=256.0, default_ttl_seconds=3600)
        config = cache.get_config()

        assert config["max_size"] == 500
        assert config["max_memory_mb"] == 256.0
        assert config["default_ttl_seconds"] == 3600

    def test_update_max_size(self):
        """Test updating max size configuration."""
        cache = LRUCache(max_size=3)
        cache.set("a", "value_a", size_mb=1.0)
        cache.set("b", "value_b", size_mb=1.0)
        cache.set("c", "value_c", size_mb=1.0)

        # Reduce max size to 2, should evict
        cache.update_config(max_size=2)
        assert len(cache) == 2
        assert cache.stats["evictions"] == 1

    def test_update_max_memory(self):
        """Test updating max memory configuration."""
        cache = LRUCache(max_memory_mb=10.0)
        cache.set("a", "value_a", size_mb=3.0)
        cache.set("b", "value_b", size_mb=3.0)
        cache.set("c", "value_c", size_mb=3.0)

        # Reduce max memory to 5MB, should evict
        cache.update_config(max_memory_mb=5.0)
        assert cache.stats["current_memory_mb"] <= 5.0
        assert cache.stats["evictions"] >= 1


@pytest.mark.unit
class TestThreadSafety:
    """Test thread safety of cache operations."""

    def test_concurrent_set_get(self):
        """Test concurrent set and get operations."""
        cache = LRUCache(max_size=1000)
        results = {"errors": 0, "success": 0}
        lock = threading.Lock()

        def worker(thread_id: int):
            try:
                for i in range(100):
                    key = f"key_{thread_id}_{i}"
                    cache.set(key, f"value_{i}", size_mb=0.1)
                    result = cache.get(key)
                    if result != f"value_{i}":
                        with lock:
                            results["errors"] += 1
                    else:
                        with lock:
                            results["success"] += 1
            except Exception as e:
                with lock:
                    results["errors"] += 1

        # Run 10 threads
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert results["errors"] == 0
        assert results["success"] == 1000

    def test_concurrent_eviction(self):
        """Test thread safety during eviction."""
        cache = LRUCache(max_size=100)
        results = {"errors": 0}
        lock = threading.Lock()

        def worker(thread_id: int):
            try:
                for i in range(200):
                    key = f"key_{thread_id}_{i}"
                    cache.set(key, f"value_{i}", size_mb=0.1)
                    # Randomly access some keys
                    if i % 3 == 0:
                        cache.get(f"key_{thread_id}_{i-1}")
            except Exception as e:
                with lock:
                    results["errors"] += 1

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert results["errors"] == 0
        assert len(cache) <= 100  # Max size should be respected


@pytest.mark.unit
class TestCacheEntries:
    """Test cache entries management."""

    def test_get_entries_summary(self):
        """Test getting summary of all entries."""
        cache = LRUCache()
        cache.set("a", "value_a", size_mb=1.0)
        cache.set("b", "value_b", size_mb=2.0)

        entries = cache.get_entries_summary()
        assert len(entries) == 2

        # Check entry structure
        entry_a = next((e for e in entries if e["key"] == "a"), None)
        assert entry_a is not None
        assert entry_a["size_mb"] == 1.0
        assert "age_seconds" in entry_a
        assert "access_count" in entry_a

    def test_entry_access_count(self):
        """Test entry access count tracking."""
        cache = LRUCache()
        cache.set("key", "value", size_mb=1.0)

        entries = cache.get_entries_summary()
        assert entries[0]["access_count"] == 0

        cache.get("key")
        entries = cache.get_entries_summary()
        assert entries[0]["access_count"] == 1

        cache.get("key")
        entries = cache.get_entries_summary()
        assert entries[0]["access_count"] == 2


@pytest.mark.unit
class TestGlobalCacheInstance:
    """Test global cache singleton."""

    def test_global_cache_singleton(self):
        """Test that get_cache returns same instance."""
        clear_cache()
        cache1 = get_cache()
        cache2 = get_cache()
        assert cache1 is cache2

    def test_global_cache_persistence(self):
        """Test that data persists in global cache."""
        clear_cache()
        cache = get_cache()
        cache.set("key", "value", size_mb=1.0)

        # Get from cache again
        cache2 = get_cache()
        assert cache2.get("key") == "value"
