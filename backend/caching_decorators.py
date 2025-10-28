"""
[ORFEAS PHASE 2 TASK 2] Caching Decorators Module
Production-ready decorators for automatic caching with metrics tracking.

Purpose:
  Provides ready-to-use decorators (@cached_response, @cached_prediction,
  @cached_query) for automatic caching with configurable TTL, automatic key
  generation, and hit/miss tracking.

Key Decorators:
  - @cached_response(ttl=3600) - Cache API responses
  - @cached_prediction(ttl=3600) - Cache ML predictions
  - @cached_query(ttl=600) - Cache database queries
  - @invalidate_on(event) - Trigger cache invalidation

Usage:
  @cached_response(ttl=1800)
  def get_model_metrics():
      return expensive_computation()

  @cached_prediction(ttl=3600)
  def predict(features, model_version):
      return ensemble.predict(features)

  @cached_query(ttl=600)
  def get_versions(status):
      return database.query(status)
"""

import functools
import hashlib
import json
import logging
import time
from typing import Any, Callable, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def _generate_cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    try:
        # Build key components
        key_parts = []

        # Include positional arguments (skip 'self' for methods)
        for arg in args:
            if arg == 'self':
                continue
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            else:
                # Hash complex objects
                try:
                    serialized = json.dumps(arg, sort_keys=True, default=str)
                    key_parts.append(hashlib.md5(serialized.encode()).hexdigest()[:8])
                except:
                    key_parts.append(str(type(arg).__name__))

        # Include keyword arguments
        for k in sorted(kwargs.keys()):
            v = kwargs[k]
            if isinstance(v, (str, int, float, bool)):
                key_parts.append(f"{k}={v}")
            else:
                try:
                    serialized = json.dumps(v, sort_keys=True, default=str)
                    key_parts.append(f"{k}={hashlib.md5(serialized.encode()).hexdigest()[:8]}")
                except:
                    key_parts.append(f"{k}={type(v).__name__}")

        return ":".join(key_parts) if key_parts else "default"
    except Exception as e:
        logger.warning(f"Failed to generate cache key: {e}")
        return "error"


def cached_response(ttl: int = 3600, prefix: str = "response") -> Callable:
    """
    Decorator to cache API response with TTL.

    Args:
        ttl: Time-to-live in seconds (default: 1 hour)
        prefix: Cache key prefix (default: "response")

    Returns:
        Decorated function with caching

    Example:
        @cached_response(ttl=1800)
        def get_model_metrics():
            return expensive_computation()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Import here to avoid circular dependency
            from cache_manager import get_cache_manager

            try:
                cache = get_cache_manager()

                # Generate cache key
                key_suffix = _generate_cache_key(*args, **kwargs)
                cache_key = f"{prefix}:{func.__name__}:{key_suffix}"

                # Try to get from cache
                cached_value = cache.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"[CACHE DECORATOR] HIT: {cache_key}")
                    return cached_value

                # Cache miss - compute value
                logger.debug(f"[CACHE DECORATOR] MISS: {cache_key}")
                result = func(*args, **kwargs)

                # Store in cache
                cache.set(cache_key, result, ttl=ttl)
                return result

            except Exception as e:
                logger.warning(f"Caching error in {func.__name__}: {e}")
                # Fallback: execute without caching
                return func(*args, **kwargs)

        return wrapper
    return decorator


def cached_prediction(ttl: int = 3600, prefix: str = "prediction") -> Callable:
    """
    Decorator to cache ML predictions.

    Args:
        ttl: Time-to-live in seconds (default: 1 hour)
        prefix: Cache key prefix (default: "prediction")

    Returns:
        Decorated function with caching

    Example:
        @cached_prediction(ttl=3600)
        def predict(features, model_version):
            return model.predict(features)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            from cache_manager import get_cache_manager

            try:
                cache = get_cache_manager()

                # For predictions, include model_version in key
                model_version = kwargs.get("model_version", args[1] if len(args) > 1 else "default")
                features = kwargs.get("features", args[0] if len(args) > 0 else None)

                # Hash features for consistency
                if isinstance(features, (list, tuple)):
                    features_hash = hashlib.md5(
                        json.dumps(features, sort_keys=True, default=str).encode()
                    ).hexdigest()[:8]
                else:
                    features_hash = hashlib.md5(str(features).encode()).hexdigest()[:8]

                cache_key = f"{prefix}:{model_version}:{features_hash}:{int(time.time() // 300)}"

                # Try to get from cache
                cached_value = cache.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"[CACHE DECORATOR] PREDICTION HIT: {cache_key}")
                    return cached_value

                # Cache miss - compute prediction
                logger.debug(f"[CACHE DECORATOR] PREDICTION MISS: {cache_key}")
                result = func(*args, **kwargs)

                # Store in cache
                cache.set(cache_key, result, ttl=ttl)
                return result

            except Exception as e:
                logger.warning(f"Caching error in {func.__name__}: {e}")
                return func(*args, **kwargs)

        return wrapper
    return decorator


def cached_query(ttl: int = 600, prefix: str = "query") -> Callable:
    """
    Decorator to cache database/API queries.

    Args:
        ttl: Time-to-live in seconds (default: 10 minutes)
        prefix: Cache key prefix (default: "query")

    Returns:
        Decorated function with caching

    Example:
        @cached_query(ttl=600)
        def get_versions(status):
            return db.query(status)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            from cache_manager import get_cache_manager

            try:
                cache = get_cache_manager()

                # Generate cache key
                key_suffix = _generate_cache_key(*args, **kwargs)
                cache_key = f"{prefix}:{func.__name__}:{key_suffix}"

                # Try to get from cache
                cached_value = cache.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"[CACHE DECORATOR] QUERY HIT: {cache_key}")
                    return cached_value

                # Cache miss - execute query
                logger.debug(f"[CACHE DECORATOR] QUERY MISS: {cache_key}")
                result = func(*args, **kwargs)

                # Store in cache
                cache.set(cache_key, result, ttl=ttl)
                return result

            except Exception as e:
                logger.warning(f"Caching error in {func.__name__}: {e}")
                return func(*args, **kwargs)

        return wrapper
    return decorator


def invalidate_on(event: str, pattern: Optional[str] = None) -> Callable:
    """
    Decorator to trigger cache invalidation on event.

    Args:
        event: Event name (e.g., "model_deployed", "version_promoted")
        pattern: Optional cache key pattern to invalidate (e.g., "prediction:*")

    Returns:
        Decorated function that invalidates cache on completion

    Example:
        @invalidate_on("model_deployed", pattern="prediction:*")
        def deploy_model(version_id):
            return deploy_logic(version_id)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            from cache_invalidation import get_invalidation_manager

            try:
                # Execute function
                result = func(*args, **kwargs)

                # Trigger invalidation
                invalidation_mgr = get_invalidation_manager()
                invalidation_mgr.handle_event(event)

                if pattern:
                    invalidation_mgr.invalidate_pattern(pattern)

                logger.info(f"[CACHE DECORATOR] Invalidated on event '{event}'")
                return result

            except Exception as e:
                logger.warning(f"Invalidation error in {func.__name__}: {e}")
                raise

        return wrapper
    return decorator


def batch_predict(func: Callable) -> Callable:
    """
    Decorator to enable batch prediction caching.

    Caches predictions for each item in a batch separately,
    then combines results.

    Example:
        @batch_predict
        def predict_batch(features_list):
            return [predict(f) for f in features_list]
    """
    @functools.wraps(func)
    def wrapper(features_list: list, **kwargs) -> list:
        from cache_manager import get_cache_manager

        try:
            cache = get_cache_manager()
            results = []
            cache_hits = 0
            cache_misses = 0

            for idx, features in enumerate(features_list):
                # Generate per-item cache key
                features_hash = hashlib.md5(
                    json.dumps(features, sort_keys=True, default=str).encode()
                ).hexdigest()[:8]
                cache_key = f"batch_predict:item:{features_hash}:{int(time.time() // 300)}"

                # Try cache
                cached = cache.get(cache_key)
                if cached is not None:
                    results.append(cached)
                    cache_hits += 1
                    logger.debug(f"[BATCH CACHE] HIT {idx}")
                else:
                    # Compute individual prediction
                    prediction = func([features], **kwargs)[0]
                    results.append(prediction)
                    cache.set(cache_key, prediction, ttl=3600)
                    cache_misses += 1
                    logger.debug(f"[BATCH CACHE] MISS {idx}")

            logger.info(f"[BATCH CACHE] Hits: {cache_hits}, Misses: {cache_misses}, Rate: {cache_hits/(cache_hits+cache_misses)*100:.1f}%")
            return results

        except Exception as e:
            logger.warning(f"Batch caching error: {e}")
            return func(features_list, **kwargs)

    return wrapper


class CacheMetricsTracker:
    """Track cache metrics across decorators."""

    _instance = None
    _lock = __import__('threading').Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.metrics: Dict[str, Dict[str, int]] = {
            "response": {"hits": 0, "misses": 0},
            "prediction": {"hits": 0, "misses": 0},
            "query": {"hits": 0, "misses": 0},
        }
        self._initialized = True

    def record_hit(self, cache_type: str) -> None:
        """Record cache hit."""
        if cache_type in self.metrics:
            self.metrics[cache_type]["hits"] += 1

    def record_miss(self, cache_type: str) -> None:
        """Record cache miss."""
        if cache_type in self.metrics:
            self.metrics[cache_type]["misses"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        return {
            cache_type: {
                "hits": self.metrics[cache_type]["hits"],
                "misses": self.metrics[cache_type]["misses"],
                "total": self.metrics[cache_type]["hits"] + self.metrics[cache_type]["misses"],
                "hit_rate": (
                    self.metrics[cache_type]["hits"] /
                    (self.metrics[cache_type]["hits"] + self.metrics[cache_type]["misses"]) * 100
                    if (self.metrics[cache_type]["hits"] + self.metrics[cache_type]["misses"]) > 0
                    else 0
                ),
            }
            for cache_type in self.metrics
        }

    def reset(self) -> None:
        """Reset all metrics."""
        for cache_type in self.metrics:
            self.metrics[cache_type]["hits"] = 0
            self.metrics[cache_type]["misses"] = 0


def get_decorator_metrics() -> Dict[str, Any]:
    """Get decorator metrics."""
    tracker = CacheMetricsTracker()
    return tracker.get_metrics()
