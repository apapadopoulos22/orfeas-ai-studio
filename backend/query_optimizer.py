"""
[ORFEAS PHASE 2 TASK 2] Query Optimizer Module
Query optimization and batching for improved performance.

Purpose:
  Optimizes model prediction and database queries through:
  - Batch processing (multiple predictions in single call)
  - Prefetching (load related data early)
  - Query result caching
  - N+1 query detection
  - Optimization recommendations

Key Classes:
  - QueryOptimizer - Main optimization coordinator
  - BatchProcessor - Handles batch operations
  - PrefetchStrategy - Prefetching logic
  - QueryAnalyzer - Analyzes query patterns

Usage:
  optimizer = get_query_optimizer()

  # Batch predictions
  features_list = [[5.1, 3.5, 1.4], [7.0, 3.2, 4.7]]
  results = optimizer.batch_predict(features_list)

  # Prefetch versions
  version_ids = ["v1", "v2"]
  optimizer.prefetch_versions(version_ids)

  # Analyze patterns
  analysis = optimizer.analyze_query_patterns()
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class QueryStats:
    """Statistics for a query pattern."""
    query_type: str
    total_calls: int = 0
    total_time_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    average_latency_ms: float = 0.0
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationRecommendation:
    """Optimization recommendation."""
    issue: str
    severity: str  # "low", "medium", "high"
    recommendation: str
    estimated_improvement_percent: float
    priority: int  # 1 = highest


class QueryAnalyzer:
    """Analyzes query patterns for N+1 and optimization opportunities."""

    def __init__(self):
        """Initialize query analyzer."""
        self.query_history: List[Dict[str, Any]] = []
        self.patterns: Dict[str, QueryStats] = {}
        self.lock = __import__('threading').Lock()

    def record_query(
        self,
        query_type: str,
        execution_time_ms: float,
        cache_hit: bool = False,
    ) -> None:
        """Record a query execution."""
        with self.lock:
            if query_type not in self.patterns:
                self.patterns[query_type] = QueryStats(query_type=query_type)

            stats = self.patterns[query_type]
            stats.total_calls += 1
            stats.total_time_ms += execution_time_ms
            stats.average_latency_ms = stats.total_time_ms / stats.total_calls

            if cache_hit:
                stats.cache_hits += 1
            else:
                stats.cache_misses += 1

            stats.last_seen = datetime.now()

    def detect_n_plus_one(self) -> List[str]:
        """Detect N+1 query patterns."""
        with self.lock:
            detected = []

            # Look for queries that repeat many times
            for query_type, stats in self.patterns.items():
                if stats.total_calls > 50:  # Threshold
                    detected.append(
                        f"{query_type}: Called {stats.total_calls} times "
                        f"(avg {stats.average_latency_ms:.1f}ms)"
                    )

            return detected

    def get_recommendations(self) -> List[OptimizationRecommendation]:
        """Get optimization recommendations."""
        recommendations = []

        with self.lock:
            for query_type, stats in self.patterns.items():
                # Recommend batching for frequently repeated queries
                if stats.total_calls > 50:
                    recommendations.append(OptimizationRecommendation(
                        issue=f"N+1 pattern detected: {query_type}",
                        severity="high",
                        recommendation=f"Use batch processing instead of individual calls",
                        estimated_improvement_percent=80.0,
                        priority=1,
                    ))

                # Recommend caching for low cache hit rate
                hit_rate = stats.cache_hits / (stats.cache_hits + stats.cache_misses) if (stats.cache_hits + stats.cache_misses) > 0 else 0
                if hit_rate < 0.3 and stats.total_calls > 20:
                    recommendations.append(OptimizationRecommendation(
                        issue=f"Low cache hit rate: {query_type} ({hit_rate*100:.1f}%)",
                        severity="medium",
                        recommendation="Increase cache TTL or implement intelligent caching",
                        estimated_improvement_percent=50.0,
                        priority=2,
                    ))

        # Sort by priority
        recommendations.sort(key=lambda x: x.priority)
        return recommendations

    def get_stats(self) -> Dict[str, Any]:
        """Get overall query statistics."""
        with self.lock:
            total_queries = sum(s.total_calls for s in self.patterns.values())
            total_time = sum(s.total_time_ms for s in self.patterns.values())
            total_cache_hits = sum(s.cache_hits for s in self.patterns.values())
            total_cache_misses = sum(s.cache_misses for s in self.patterns.values())

            return {
                "total_queries": total_queries,
                "total_time_ms": total_time,
                "average_query_time_ms": total_time / total_queries if total_queries > 0 else 0,
                "cache_hits": total_cache_hits,
                "cache_misses": total_cache_misses,
                "cache_hit_rate": total_cache_hits / (total_cache_hits + total_cache_misses) if (total_cache_hits + total_cache_misses) > 0 else 0,
                "unique_query_types": len(self.patterns),
            }


class BatchProcessor:
    """Processes batches of predictions efficiently."""

    def __init__(self, cache_manager: Optional[Any] = None):
        """Initialize batch processor."""
        self.cache_manager = cache_manager
        self.lock = __import__('threading').Lock()

    def batch_predict(
        self,
        features_list: List[List[float]],
        model_version: str = "default",
    ) -> List[Dict[str, Any]]:
        """
        Process batch predictions.

        Args:
            features_list: List of feature vectors
            model_version: Model version to use

        Returns:
            List of prediction results
        """
        results = []
        cached_count = 0

        for idx, features in enumerate(features_list):
            # Try cache first if available
            if self.cache_manager:
                cache_key = self._make_cache_key(features, model_version)
                cached_result = self.cache_manager.get(cache_key)
                if cached_result is not None:
                    results.append(cached_result)
                    cached_count += 1
                    logger.debug(f"[BATCH] Cache hit {idx}/{len(features_list)}")
                    continue

            # Placeholder: would call actual model
            result = {
                "prediction": 0,
                "confidence": 0.95,
                "latency_ms": 12.5,
            }
            results.append(result)

        hit_rate = (cached_count / len(features_list) * 100) if features_list else 0
        logger.info(
            f"[BATCH] Processed {len(features_list)} predictions, "
            f"cache hit rate: {hit_rate:.1f}%"
        )

        return results

    def _make_cache_key(self, features: List[float], model_version: str) -> str:
        """Generate cache key for features."""
        import hashlib
        import json
        serialized = json.dumps(features, sort_keys=True)
        features_hash = hashlib.md5(serialized.encode()).hexdigest()[:8]
        return f"batch:{model_version}:{features_hash}"


class PrefetchStrategy:
    """Implements prefetching of related data."""

    def __init__(self, cache_manager: Optional[Any] = None):
        """Initialize prefetch strategy."""
        self.cache_manager = cache_manager

    def prefetch_versions(self, version_ids: List[str]) -> Dict[str, Any]:
        """
        Prefetch model version metadata.

        Args:
            version_ids: List of version IDs to prefetch

        Returns:
            Dictionary of version metadata
        """
        results = {}

        for version_id in version_ids:
            cache_key = f"version:{version_id}:metadata"

            # Check cache first
            if self.cache_manager:
                cached = self.cache_manager.get(cache_key)
                if cached:
                    results[version_id] = cached
                    logger.debug(f"[PREFETCH] Hit: {version_id}")
                    continue

            # Placeholder: would fetch from database
            metadata = {
                "version_id": version_id,
                "status": "production",
                "accuracy": 0.96,
                "created_at": "2025-10-28",
            }
            results[version_id] = metadata

            # Cache it
            if self.cache_manager:
                self.cache_manager.set(cache_key, metadata, ttl=300)

        logger.info(f"[PREFETCH] Prefetched {len(results)} versions")
        return results

    def prefetch_predictions(
        self,
        model_version: str,
        feature_samples: List[List[float]],
    ) -> int:
        """
        Warm up prediction cache with common feature combinations.

        Args:
            model_version: Model version to prefetch
            feature_samples: Feature samples to predict

        Returns:
            Number of predictions cached
        """
        cached_count = 0

        for features in feature_samples:
            cache_key = f"prediction:{model_version}:{hash(str(features))}"

            # Check if already cached
            if self.cache_manager and self.cache_manager.exists(cache_key):
                cached_count += 1
                continue

            # Placeholder: would compute prediction
            prediction = {
                "prediction": 0,
                "confidence": 0.95,
            }

            # Cache it
            if self.cache_manager:
                self.cache_manager.set(cache_key, prediction, ttl=3600)
                cached_count += 1

        logger.info(f"[PREFETCH] Warmed up {cached_count} predictions")
        return cached_count


class QueryOptimizer:
    """Main query optimizer coordinator."""

    _instance = None
    _lock = __import__('threading').Lock()

    def __new__(cls, cache_manager: Optional[Any] = None):
        """Singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, cache_manager: Optional[Any] = None):
        """Initialize query optimizer."""
        if self._initialized:
            return

        self.cache_manager = cache_manager
        self.analyzer = QueryAnalyzer()
        self.batch_processor = BatchProcessor(cache_manager)
        self.prefetch_strategy = PrefetchStrategy(cache_manager)
        self._initialized = True

        logger.info("[OPTIMIZER] ✓ Query optimizer initialized")

    def batch_predict(
        self,
        features_list: List[List[float]],
        model_version: str = "default",
    ) -> List[Dict[str, Any]]:
        """Process batch predictions."""
        start_time = time.time()

        results = self.batch_processor.batch_predict(
            features_list,
            model_version,
        )

        elapsed_ms = (time.time() - start_time) * 1000
        self.analyzer.record_query("batch_predict", elapsed_ms)

        return results

    def prefetch_versions(self, version_ids: List[str]) -> Dict[str, Any]:
        """Prefetch model versions."""
        return self.prefetch_strategy.prefetch_versions(version_ids)

    def prefetch_predictions(
        self,
        model_version: str,
        feature_samples: List[List[float]],
    ) -> int:
        """Warm up prediction cache."""
        return self.prefetch_strategy.prefetch_predictions(
            model_version,
            feature_samples,
        )

    def analyze_query_patterns(self) -> Dict[str, Any]:
        """Analyze current query patterns."""
        return {
            "stats": self.analyzer.get_stats(),
            "n_plus_one_patterns": self.analyzer.detect_n_plus_one(),
            "recommendations": [
                {
                    "issue": r.issue,
                    "severity": r.severity,
                    "recommendation": r.recommendation,
                    "estimated_improvement": f"{r.estimated_improvement_percent:.1f}%",
                    "priority": r.priority,
                }
                for r in self.analyzer.get_recommendations()
            ],
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get optimizer statistics."""
        return self.analyzer.get_stats()


# Singleton getter
_query_optimizer = None

def get_query_optimizer(cache_manager: Optional[Any] = None) -> QueryOptimizer:
    """Get or create query optimizer singleton."""
    global _query_optimizer
    if _query_optimizer is None:
        _query_optimizer = QueryOptimizer(cache_manager)
    return _query_optimizer


def reset_query_optimizer() -> None:
    """Reset query optimizer (for testing)."""
    global _query_optimizer
    _query_optimizer = None
