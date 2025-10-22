"""
LLM Cache Layer - Intelligent Response Caching

Purpose:
    Cache LLM responses to reduce API calls and costs by:
    - Hash-based prompt matching
    - Semantic similarity detection
    - Time-to-live (TTL) management
    - Cache statistics and monitoring
    - Integration with Phase 6C.5 cache system

Performance Targets:
    - Cache hit rate: >70%
    - Get latency: <1ms
    - Set latency: <5ms
    - Cost reduction: 50%+
"""

import logging
import time
import hashlib
from typing import Dict, Optional, Any, Tuple, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

from .error_handler import (
    error_context,
    safe_execute,
    CacheError,
    ErrorAggregator
)
from .tracing import (
    trace_performance,
    trace_block_async,
    PerformanceTracer
)

logger = logging.getLogger(__name__)


@dataclass
class CachedResponse:
    """A cached LLM response entry."""
    key: str
    prompt: str
    response: str
    model: str
    timestamp: float
    ttl_seconds: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        age = time.time() - self.timestamp
        return age > self.ttl_seconds

    def mark_accessed(self) -> None:
        """Mark this entry as accessed."""
        self.access_count += 1
        self.last_accessed = time.time()


@dataclass
class CacheStats:
    """Cache statistics."""
    total_gets: int = 0
    total_sets: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    evictions: int = 0
    total_requests: int = 0
    total_cost_saved: float = 0.0
    avg_latency_ms: float = 0.0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        if self.total_gets == 0:
            return 0.0
        return self.cache_hits / self.total_gets

    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate."""
        if self.total_gets == 0:
            return 0.0
        return self.cache_misses / self.total_gets


class LLMCacheLayer:
    """
    Intelligent LLM response caching system.

    Reduces API calls and costs through smart caching strategies.
    """

    def __init__(self, max_size: int = 1000, default_ttl_seconds: int = 86400):
        """
        Initialize cache layer.

        Args:
            max_size: Maximum number of cache entries
            default_ttl_seconds: Default TTL for entries (24 hours)
        """
        self.cache: Dict[str, CachedResponse] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl_seconds
        self.stats = CacheStats()
        self.semantic_cache: Dict[str, List[str]] = {}  # For similarity matching
        self.error_agg = ErrorAggregator()
        self.perf_tracer = PerformanceTracer()
        logger.info(f"LLMCacheLayer initialized (max_size={max_size}, ttl={default_ttl_seconds}s)")
    @error_context(component='llm_cache_layer', operation='get')

    @trace_performance(operation='get', component='llm_cache_layer')
    def get(self, prompt: str, model: str = "default") -> Optional[str]:
        """
        Get cached response for a prompt.        Args:
            prompt: The LLM prompt
            model: The model used

        Returns:
            Cached response if hit, None if miss
        """
        start_time = time.time()
        key = self._generate_key(prompt, model)

        self.stats.total_gets += 1

        # Check exact match first
        if key in self.cache:
            entry = self.cache[key]

            # Check if expired
            if entry.is_expired():
                logger.debug(f"Cache entry expired: {key}")
                self._remove_entry(key)
                self.stats.cache_misses += 1
                return None

            # Hit!
            entry.mark_accessed()
            self.stats.cache_hits += 1
            latency = (time.time() - start_time) * 1000
            self._update_latency(latency)
            logger.debug(f"Cache hit for {key} ({latency:.2f}ms)")
            return entry.response

        # Check semantic similarity
        similar_key = self._find_similar(prompt)
        if similar_key:
            entry = self.cache[similar_key]
            if not entry.is_expired():
                entry.mark_accessed()
                self.stats.cache_hits += 1
                latency = (time.time() - start_time) * 1000
                self._update_latency(latency)
                logger.debug(f"Cache hit (semantic) for {key} ({latency:.2f}ms)")
                return entry.response

        # Miss
        self.stats.cache_misses += 1
        latency = (time.time() - start_time) * 1000
        self._update_latency(latency)
        logger.debug(f"Cache miss for {key}")
        return None

    @trace_performance(operation='set', component='llm_cache_layer')
    @error_context(component='llm_cache_layer', operation='set')
    def set(
        self,
        prompt: str,
        response: str,
        model: str = "default",
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Cache an LLM response.

        Args:
            prompt: The LLM prompt
            response: The LLM response
            model: The model used
            ttl_seconds: Time-to-live in seconds
            metadata: Optional metadata to store
        """
        start_time = time.time()
        key = self._generate_key(prompt, model)

        self.stats.total_sets += 1

        # Check if we need to evict
        if len(self.cache) >= self.max_size:
            self._evict_oldest()

        # Create entry
        entry = CachedResponse(
            key=key,
            prompt=prompt,
            response=response,
            model=model,
            timestamp=time.time(),
            ttl_seconds=ttl_seconds or self.default_ttl,
            metadata=metadata or {},
        )

        # Store in cache
        self.cache[key] = entry

        # Track semantic similarity
        self._track_semantic(prompt, key)

        latency = (time.time() - start_time) * 1000
        self._update_latency(latency)
        logger.debug(f"Cached response for {key} (latency: {latency:.2f}ms)")

    def _generate_key(self, prompt: str, model: str) -> str:
        """Generate cache key from prompt and model."""
        # Normalize prompt
        normalized = prompt.strip().lower()
        # Create hash
        hash_obj = hashlib.md5(f"{normalized}:{model}".encode())
        return hash_obj.hexdigest()
    @error_context(component='llm_cache_layer', operation='find_similar')

    @trace_performance(operation='find_similar', component='llm_cache_layer')
    def _find_similar(self, prompt: str, threshold: float = 0.85) -> Optional[str]:
        """
        Find semantically similar cached prompt.        Args:
            prompt: Query prompt
            threshold: Similarity threshold (0.0-1.0)

        Returns:
            Key of similar entry if found
        """
        query_tokens = set(prompt.lower().split())

        best_match = None
        best_score = threshold

        for cached_key, entry in self.cache.items():
            if entry.is_expired():
                continue

            cached_tokens = set(entry.prompt.lower().split())

            # Jaccard similarity
            intersection = len(query_tokens & cached_tokens)
            union = len(query_tokens | cached_tokens)
            similarity = intersection / union if union > 0 else 0.0

            if similarity > best_score:
                best_score = similarity
                best_match = cached_key

        return best_match

    def _evict_oldest(self) -> None:
        """Evict oldest/least-used entry."""
        if not self.cache:
            return

        # Find entry with lowest access count and oldest timestamp
        oldest = min(
            self.cache.values(),
            key=lambda e: (e.access_count, e.last_accessed)
        )

        key = oldest.key
        self._remove_entry(key)
        self.stats.evictions += 1
        logger.debug(f"Evicted cache entry: {key}")

    def _remove_entry(self, key: str) -> None:
        """Remove entry from cache."""
        if key in self.cache:
            del self.cache[key]
            # Also remove from semantic tracking
            for similar_keys in self.semantic_cache.values():
                if key in similar_keys:
                    similar_keys.remove(key)

    def _track_semantic(self, prompt: str, key: str) -> None:
        """Track semantic similarity for prompt."""
        tokens = frozenset(prompt.lower().split())
        if tokens not in self.semantic_cache:
            self.semantic_cache[tokens] = []
        self.semantic_cache[tokens].append(key)

    def _update_latency(self, latency_ms: float) -> None:
        """Update average latency."""
        old_avg = self.stats.avg_latency_ms
        count = self.stats.total_gets + self.stats.total_sets
        self.stats.avg_latency_ms = (old_avg * (count - 1) + latency_ms) / count

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.semantic_cache.clear()
        logger.info("Cache cleared")

    def cleanup_expired(self) -> int:
        """
        Remove expired entries.

        Returns:
            Number of entries removed
        """
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]

        for key in expired_keys:
            self._remove_entry(key)

        logger.debug(f"Cleaned up {len(expired_keys)} expired entries")
        return len(expired_keys)

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self.stats

    def reset_stats(self) -> None:
        """Reset statistics."""
        self.stats = CacheStats()
        logger.info("Cache statistics reset")

    def get_cache_info(self) -> Dict[str, Any]:
        """Get detailed cache information."""
        self.cleanup_expired()

        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.stats.cache_hits,
            'misses': self.stats.cache_misses,
            'hit_rate': f"{self.stats.hit_rate:.1%}",
            'evictions': self.stats.evictions,
            'avg_latency_ms': f"{self.stats.avg_latency_ms:.2f}",
            'ttl_seconds': self.default_ttl,
        }

    def estimate_cost_savings(self, cost_per_call: float = 0.001) -> float:
        """
        Estimate cost saved through caching.

        Args:
            cost_per_call: Cost per API call

        Returns:
            Estimated cost saved
        """
        return self.stats.cache_hits * cost_per_call


# Factory function for singleton access
_cache_instance = None


def get_llm_cache() -> LLMCacheLayer:
    """Get or create the LLM cache singleton."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = LLMCacheLayer()
    return _cache_instance
