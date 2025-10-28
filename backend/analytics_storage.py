"""
[ORFEAS PHASE 2 TASK 3] Analytics Storage Module
Persistent storage for analytics data with Redis backend.

Purpose:
  Stores aggregated metrics and historical data.
  Manages data retention policies.
  Provides query interface for retrieving analytics.

Key Components:
  - AnalyticsStore: Redis-backed storage
  - HistoricalDataManager: Data lifecycle management
  - AnalyticsQuery: Query engine

Usage:
  from analytics_storage import get_storage

  store = get_storage()
  metrics = store.query("cache_hit_rate", time_range="1hour")
"""

import json
import logging
import threading
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AnalyticsStore:
    """Redis-backed analytics storage."""

    _instance: Optional["AnalyticsStore"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "AnalyticsStore":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize storage."""
        if hasattr(self, "_initialized"):
            return

        self._initialized = True

        # In-memory fallback storage
        self.store: Dict[str, Dict[str, Any]] = {}
        self.store_lock = threading.Lock()

        # Data retention policies (in seconds)
        self.retention_policies = {
            "1s": 3600,  # Keep 1-second metrics for 1 hour
            "1m": 86400,  # Keep 1-minute metrics for 1 day
            "1h": 2592000,  # Keep 1-hour metrics for 30 days
            "1d": 31536000,  # Keep 1-day metrics for 1 year
        }

        # Try to import redis, but continue if not available
        try:
            import redis

            self.redis_client = redis.Redis(host="localhost", port=6379, db=0)
            self.redis_client.ping()
            self.use_redis = True
            logger.info("[ANALYTICS] Connected to Redis backend")
        except Exception as e:
            logger.warning(f"[ANALYTICS] Redis not available: {e}, using in-memory storage")
            self.redis_client = None
            self.use_redis = False

    def store_metric(self, metric_data: Dict[str, Any]) -> None:
        """
        Store aggregated metric.

        Args:
            metric_data: Metric dictionary
        """
        metric_name = metric_data.get("metric_name", "unknown")
        window = metric_data.get("window", "1s")
        timestamp = metric_data.get("timestamp", time.time())

        key = f"metrics:{metric_name}:{window}:{timestamp}"

        if self.use_redis and self.redis_client:
            try:
                # Store in Redis with TTL
                ttl = self.retention_policies.get(window, 3600)
                self.redis_client.setex(key, ttl, json.dumps(metric_data))
            except Exception as e:
                logger.error(f"[ANALYTICS] Redis store error: {e}")
                self._store_in_memory(key, metric_data)
        else:
            self._store_in_memory(key, metric_data)

    def _store_in_memory(self, key: str, data: Dict[str, Any]) -> None:
        """Store data in-memory."""
        with self.store_lock:
            self.store[key] = data

            # Clean old data (keep only recent)
            if len(self.store) > 100000:
                # Remove oldest 10%
                keys_to_remove = sorted(self.store.keys())[: len(self.store) // 10]
                for k in keys_to_remove:
                    del self.store[k]

    def query_metrics(
        self, metric_name: str, window: str = "1m", limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query stored metrics.

        Args:
            metric_name: Name of metric
            window: Time window
            limit: Maximum results

        Returns:
            List of metric dictionaries
        """
        key_pattern = f"metrics:{metric_name}:{window}:*"
        metrics = []

        if self.use_redis and self.redis_client:
            try:
                keys = self.redis_client.keys(key_pattern)
                for key in sorted(keys, reverse=True)[:limit]:
                    data = self.redis_client.get(key)
                    if data:
                        metrics.append(json.loads(data))
            except Exception as e:
                logger.error(f"[ANALYTICS] Redis query error: {e}")
                metrics = self._query_in_memory(metric_name, window, limit)
        else:
            metrics = self._query_in_memory(metric_name, window, limit)

        return metrics

    def _query_in_memory(self, metric_name: str, window: str, limit: int) -> List[Dict[str, Any]]:
        """Query in-memory storage."""
        with self.store_lock:
            prefix = f"metrics:{metric_name}:{window}:"
            results = [v for k, v in self.store.items() if k.startswith(prefix)]
            return sorted(results, key=lambda x: x.get("timestamp", 0), reverse=True)[:limit]

    def get_metric_summary(self, metric_name: str) -> Dict[str, Any]:
        """Get summary of metric across all windows."""
        summary = {}

        for window in ["1s", "1m", "1h", "1d"]:
            metrics = self.query_metrics(metric_name, window, limit=1)
            if metrics:
                summary[window] = metrics[0]

        return summary

    def cleanup_old_data(self) -> int:
        """
        Clean up old data based on retention policies.

        Returns:
            Number of items deleted
        """
        deleted_count = 0
        now = time.time()

        if self.use_redis and self.redis_client:
            # Redis handles TTL automatically
            logger.debug("[ANALYTICS] Redis cleanup (automatic via TTL)")
            return 0
        else:
            # Clean in-memory storage
            with self.store_lock:
                keys_to_delete = []

                for key, value in self.store.items():
                    # Extract window from key
                    parts = key.split(":")
                    if len(parts) >= 2:
                        window = parts[2]
                        timestamp = float(parts[3]) if len(parts) > 3 else 0

                        ttl = self.retention_policies.get(window, 3600)

                        if now - timestamp > ttl:
                            keys_to_delete.append(key)

                for key in keys_to_delete:
                    del self.store[key]
                    deleted_count += 1

        return deleted_count

    def clear(self) -> None:
        """Clear all storage."""
        if self.use_redis and self.redis_client:
            try:
                self.redis_client.flushdb()
            except Exception as e:
                logger.error(f"[ANALYTICS] Redis flush error: {e}")

        with self.store_lock:
            self.store.clear()

        logger.info("[ANALYTICS] Storage cleared")


# Global storage instance
_storage: Optional[AnalyticsStore] = None


def get_storage() -> AnalyticsStore:
    """Get singleton storage."""
    global _storage
    if _storage is None:
        _storage = AnalyticsStore()
    return _storage
