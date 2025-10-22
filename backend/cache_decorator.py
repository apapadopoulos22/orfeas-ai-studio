"""
+==============================================================================─
|            ORFEAS Cache Decorator - Async Function Caching                  |
|    Decorator for transparent caching of async generation functions          |
+==============================================================================─

Usage:
    @cached_result(cache_key_fn=lambda img, prompt: f"{hash(img)}-{hash(prompt)}")
    async def generate_3d(image_data, prompt, quality):
        return expensive_computation()

    result = await generate_3d(image_data, prompt, quality)
    # First call: computes and caches
    # Second call with same args: returns cached result instantly
"""

import functools
import inspect
import hashlib
import json
import sys
import logging
from typing import Any, Callable, Optional, Coroutine
from cache_manager import get_cache

logger = logging.getLogger(__name__)


def _default_cache_key_fn(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    try:
        # Create hashable representation of arguments
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        key_str = "|".join(key_parts)

        # Hash to keep key size reasonable
        key_hash = hashlib.sha256(key_str.encode()).hexdigest()[:16]
        return key_hash
    except Exception as e:
        logger.warning(f"[CACHE] Failed to generate key: {e}")
        return None


def _estimate_result_size(result: Any) -> float:
    """Estimate memory size of result in MB."""
    try:
        # Convert to JSON to estimate size
        if isinstance(result, dict):
            size_bytes = len(json.dumps(result, default=str).encode())
        else:
            size_bytes = sys.getsizeof(result)

        size_mb = size_bytes / (1024 * 1024)
        return max(size_mb, 0.1)  # Minimum 0.1MB
    except Exception:
        return 1.0  # Default estimate


def cached_result(
    cache_key_fn: Optional[Callable[..., str]] = None,
    ttl_seconds: Optional[int] = None,
    enabled: bool = True,
):
    """
    Decorator for caching async function results.

    Args:
        cache_key_fn: Function to generate cache key from args/kwargs.
                      If None, uses default hash-based key.
        ttl_seconds: Time-to-live in seconds. If None, uses cache default.
        enabled: Whether caching is enabled (useful for feature flags)

    Returns:
        Decorated async function with caching
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            if not enabled:
                # If caching disabled, call function directly
                return await func(*args, **kwargs)

            # Generate cache key
            if cache_key_fn:
                try:
                    cache_key = cache_key_fn(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"[CACHE] Key generation failed: {e}, bypassing cache")
                    return await func(*args, **kwargs)
            else:
                cache_key = _default_cache_key_fn(*args, **kwargs)

            if cache_key is None:
                # Failed to generate key, call function directly
                return await func(*args, **kwargs)

            # Try to get from cache
            cache = get_cache()
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"[CACHE] Cache hit for {func.__name__}({cache_key})")
                return cached_value

            # Not in cache, call function
            logger.debug(f"[CACHE] Cache miss for {func.__name__}({cache_key})")
            result = await func(*args, **kwargs)

            # Store in cache
            try:
                size_mb = _estimate_result_size(result)
                cache.set(cache_key, result, size_mb=size_mb, ttl_seconds=ttl_seconds)
                logger.debug(f"[CACHE] Cached result for {cache_key} ({size_mb:.2f}MB)")
            except Exception as e:
                logger.warning(f"[CACHE] Failed to cache result: {e}")

            return result

        return wrapper

    return decorator


def cached_result_sync(
    cache_key_fn: Optional[Callable[..., str]] = None,
    ttl_seconds: Optional[int] = None,
    enabled: bool = True,
):
    """
    Decorator for caching synchronous function results.

    Args:
        cache_key_fn: Function to generate cache key from args/kwargs
        ttl_seconds: Time-to-live in seconds
        enabled: Whether caching is enabled

    Returns:
        Decorated function with caching
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if not enabled:
                return func(*args, **kwargs)

            # Generate cache key
            if cache_key_fn:
                try:
                    cache_key = cache_key_fn(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"[CACHE] Key generation failed: {e}")
                    return func(*args, **kwargs)
            else:
                cache_key = _default_cache_key_fn(*args, **kwargs)

            if cache_key is None:
                return func(*args, **kwargs)

            # Try to get from cache
            cache = get_cache()
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"[CACHE] Cache hit for {func.__name__}({cache_key})")
                return cached_value

            # Not in cache, call function
            logger.debug(f"[CACHE] Cache miss for {func.__name__}({cache_key})")
            result = func(*args, **kwargs)

            # Store in cache
            try:
                size_mb = _estimate_result_size(result)
                cache.set(cache_key, result, size_mb=size_mb, ttl_seconds=ttl_seconds)
                logger.debug(f"[CACHE] Cached result for {cache_key} ({size_mb:.2f}MB)")
            except Exception as e:
                logger.warning(f"[CACHE] Failed to cache result: {e}")

            return result

        return wrapper

    return decorator
