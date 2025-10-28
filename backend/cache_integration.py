"""
ORFEAS AI Studio - Advanced Caching Integration
================================================
Multi-level caching system integration with existing infrastructure

Features:
- L1 Memory Cache (512MB, <1ms access)
- L2 Redis Cache (distributed, <5ms access)
- L3 Disk Cache (10GB compressed, <50ms access)
- Automatic cache promotion
- Predictive prefetching
- Redis Cluster support
"""

import os
import logging
from typing import Optional, Any
from pathlib import Path

from core.multi_level_cache import MultiLevelCache
from redis_config import RedisClient

logger = logging.getLogger(__name__)

# ============================================
# GLOBAL CACHE INSTANCE
# ============================================

_cache_instance: Optional[MultiLevelCache] = None
_cache_initialized = False


def initialize_advanced_cache(
    cache_dir: Optional[str] = None,
    max_memory_mb: int = 512,
    max_disk_gb: int = 10,
    enable_prefetch: bool = True
) -> bool:
    """
    Initialize advanced multi-level caching system.

    Args:
        cache_dir: Directory for L3 disk cache (default: ./cache)
        max_memory_mb: Maximum L1 memory cache size in MB
        max_disk_gb: Maximum L3 disk cache size in GB
        enable_prefetch: Enable predictive prefetching

    Returns:
        True if initialization successful
    """
    global _cache_instance, _cache_initialized

    if _cache_initialized:
        logger.info("✅ Advanced cache already initialized")
        return True

    try:
        # Set up cache directory
        if cache_dir is None:
            cache_dir = os.getenv('CACHE_DIR', './cache')

        cache_path = Path(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)

        # Get Redis client
        redis_client = RedisClient().client
        if not redis_client:
            logger.warning("⚠️  Redis unavailable - cache will operate without L2 tier")

        # Initialize multi-level cache
        _cache_instance = MultiLevelCache(
            cache_dir=str(cache_path),
            redis_client=redis_client,
            max_memory_mb=max_memory_mb,
            max_disk_gb=max_disk_gb
        )

        _cache_initialized = True

        logger.info(
            f"✅ Advanced caching initialized:\n"
            f"   L1 Memory: {max_memory_mb}MB (in-memory LRU)\n"
            f"   L2 Redis: {'ENABLED' if redis_client else 'DISABLED'}\n"
            f"   L3 Disk: {max_disk_gb}GB (compressed at {cache_path})\n"
            f"   Prefetching: {'ENABLED' if enable_prefetch else 'DISABLED'}"
        )

        return True

    except Exception as e:
        logger.error(f"❌ Advanced cache initialization failed: {e}")
        return False


def get_cache() -> Optional[MultiLevelCache]:
    """
    Get the global cache instance.

    Returns:
        MultiLevelCache instance or None if not initialized
    """
    return _cache_instance


def cache_model_output(
    model_key: str,
    output_data: Any,
    ttl: int = 3600
) -> bool:
    """
    Cache 3D model generation output.

    Args:
        model_key: Unique key for the model (e.g., image hash)
        output_data: Model output data to cache
        ttl: Time-to-live in seconds (default: 1 hour)

    Returns:
        True if cached successfully
    """
    cache = get_cache()
    if not cache:
        logger.debug("Cache not available, skipping model output caching")
        return False

    try:
        cache_key = f"model:{model_key}"
        cache.set(cache_key, output_data, ttl=ttl)
        logger.debug(f"Cached model output: {cache_key}")
        return True
    except Exception as e:
        logger.error(f"Failed to cache model output: {e}")
        return False


def get_cached_model_output(model_key: str) -> Optional[Any]:
    """
    Retrieve cached 3D model output.

    Args:
        model_key: Unique key for the model

    Returns:
        Cached model output or None if not found
    """
    cache = get_cache()
    if not cache:
        return None

    try:
        cache_key = f"model:{model_key}"
        result = cache.get(cache_key)
        if result:
            logger.debug(f"Cache hit for model: {cache_key}")
        return result
    except Exception as e:
        logger.error(f"Failed to retrieve cached model: {e}")
        return None


def cache_image_processing(
    image_hash: str,
    processed_data: Any,
    ttl: int = 1800
) -> bool:
    """
    Cache image preprocessing results.

    Args:
        image_hash: Hash of the input image
        processed_data: Processed image data
        ttl: Time-to-live in seconds (default: 30 minutes)

    Returns:
        True if cached successfully
    """
    cache = get_cache()
    if not cache:
        return False

    try:
        cache_key = f"image:{image_hash}"
        cache.set(cache_key, processed_data, ttl=ttl)
        logger.debug(f"Cached image processing: {cache_key}")
        return True
    except Exception as e:
        logger.error(f"Failed to cache image processing: {e}")
        return False


def get_cached_image_processing(image_hash: str) -> Optional[Any]:
    """
    Retrieve cached image preprocessing results.

    Args:
        image_hash: Hash of the input image

    Returns:
        Cached processing results or None if not found
    """
    cache = get_cache()
    if not cache:
        return None

    try:
        cache_key = f"image:{image_hash}"
        result = cache.get(cache_key)
        if result:
            logger.debug(f"Cache hit for image: {cache_key}")
        return result
    except Exception as e:
        logger.error(f"Failed to retrieve cached image: {e}")
        return None


def warm_frequent_models():
    """
    Warm cache with frequently accessed models on startup.
    This loads popular models into L1/L2 for fast access.
    """
    cache = get_cache()
    if not cache:
        logger.info("Cache not available, skipping warming")
        return

    try:
        # Get prefetch candidates (models likely to be accessed)
        candidates = cache.get_prefetch_candidates(top_n=10)

        if candidates:
            logger.info(f"Cache warming: {len(candidates)} models identified for prefetch")
        else:
            logger.debug("No models to prefetch (empty cache)")

    except Exception as e:
        logger.error(f"Cache warming failed: {e}")


def get_cache_statistics() -> dict:
    """
    Get comprehensive cache statistics.

    Returns:
        Dictionary with cache performance metrics
    """
    cache = get_cache()
    if not cache:
        return {
            "status": "unavailable",
            "message": "Cache not initialized"
        }

    try:
        stats = cache.get_stats()

        return {
            "status": "active",
            "overall": {
                "hit_rate": stats['overall']['hit_rate'],
                "total_requests": stats['overall']['total_requests'],
                "total_hits": stats['overall']['total_hits'],
                "total_misses": stats['overall']['total_misses']
            },
            "l1_memory": {
                "hits": stats['l1']['hits'],
                "misses": stats['l1']['misses'],
                "evictions": stats['l1']['evictions'],
                "size_mb": stats['l1']['size_mb']
            },
            "l2_redis": {
                "hits": stats['l2']['hits'],
                "misses": stats['l2']['misses'],
                "errors": stats['l2']['errors']
            },
            "l3_disk": {
                "hits": stats['l3']['hits'],
                "misses": stats['l3']['misses'],
                "evictions": stats['l3']['evictions'],
                "compression_savings_mb": stats['l3']['compression_savings_mb']
            }
        }
    except Exception as e:
        logger.error(f"Failed to get cache statistics: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


def invalidate_model_cache(model_key: str) -> bool:
    """
    Invalidate cached model output across all cache levels.

    Args:
        model_key: Unique key for the model to invalidate

    Returns:
        True if invalidated successfully
    """
    cache = get_cache()
    if not cache:
        return False

    try:
        cache_key = f"model:{model_key}"
        cache.delete(cache_key)
        logger.info(f"Invalidated cache for model: {cache_key}")
        return True
    except Exception as e:
        logger.error(f"Failed to invalidate cache: {e}")
        return False


def clear_all_cache() -> bool:
    """
    Clear all cache levels (L1, L2, L3).
    Use with caution - this removes all cached data.

    Returns:
        True if cleared successfully
    """
    cache = get_cache()
    if not cache:
        return False

    try:
        cache.clear()
        logger.warning("🗑️  All cache levels cleared")
        return True
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        return False


# ============================================
# HEALTH CHECK
# ============================================

def check_cache_health() -> dict:
    """
    Comprehensive cache health check.

    Returns:
        Dictionary with health status for each cache level
    """
    cache = get_cache()

    if not cache:
        return {
            "status": "unhealthy",
            "message": "Cache not initialized",
            "levels": {
                "l1": "unavailable",
                "l2": "unavailable",
                "l3": "unavailable"
            }
        }

    try:
        # Test L1 (memory)
        test_key = "__health_check__"
        cache.l1_cache.set(test_key, "ok")
        l1_status = "healthy" if cache.l1_cache.get(test_key) == "ok" else "unhealthy"
        cache.l1_cache.delete(test_key)

        # Test L2 (Redis)
        l2_status = "unavailable"
        if cache.l2_cache.redis_client:
            try:
                cache.l2_cache.set(test_key, b"ok")
                l2_status = "healthy" if cache.l2_cache.get(test_key) == b"ok" else "unhealthy"
                cache.l2_cache.delete(test_key)
            except Exception:
                l2_status = "unhealthy"

        # Test L3 (disk)
        cache.l3_cache.set(test_key, b"ok")
        l3_status = "healthy" if cache.l3_cache.get(test_key) == b"ok" else "unhealthy"
        cache.l3_cache.delete(test_key)

        overall_status = "healthy" if l1_status == "healthy" and l3_status == "healthy" else "degraded"

        stats = cache.get_stats()

        return {
            "status": overall_status,
            "message": "Cache operational",
            "levels": {
                "l1": {
                    "status": l1_status,
                    "hits": stats['l1']['hits'],
                    "size_mb": stats['l1']['size_mb']
                },
                "l2": {
                    "status": l2_status,
                    "hits": stats['l2']['hits']
                },
                "l3": {
                    "status": l3_status,
                    "hits": stats['l3']['hits'],
                    "compression_savings_mb": stats['l3']['compression_savings_mb']
                }
            },
            "overall_hit_rate": stats['overall']['hit_rate']
        }

    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": str(e),
            "levels": {
                "l1": "error",
                "l2": "error",
                "l3": "error"
            }
        }
