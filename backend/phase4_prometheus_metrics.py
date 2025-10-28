#!/usr/bin/env python3
"""
Phase 4.7: Prometheus Metrics Collection
==========================================

Comprehensive metrics collection for production monitoring.
Tracks: API performance, cache statistics, authentication, rate limiting,
errors, throughput, and system health.

Status: Production-Ready
Version: 1.0.0
Author: BOB AI v10.0
"""

import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from threading import Lock
from collections import defaultdict, deque

# Setup logging
logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Singleton metrics collector for Prometheus-compatible statistics.

    Tracks:
    - API endpoint performance (latency, throughput)
    - Cache hit/miss rates
    - Authentication attempts and failures
    - Rate limit violations
    - Error rates and types
    - System health indicators
    - Request/response sizes
    - Database query performance
    """

    _instance = None
    _lock = Lock()

    def __init__(self):
        """Initialize metrics collector with all counters and histograms."""
        self._lock_internal = Lock()

        # Counters (monotonically increasing)
        self.http_requests_total: Dict[str, int] = defaultdict(int)  # {method_path: count}
        self.http_errors_total: Dict[str, int] = defaultdict(int)    # {status_code: count}
        self.cache_hits_total: int = 0
        self.cache_misses_total: int = 0
        self.cache_deletes_total: int = 0
        self.auth_successes_total: int = 0
        self.auth_failures_total: int = 0
        self.rate_limit_violations_total: int = 0
        self.sql_injection_attempts_total: int = 0
        self.xss_attempts_total: int = 0

        # Gauges (can go up/down)
        self.http_requests_in_progress: int = 0
        self.cache_size_bytes: int = 0
        self.active_connections: int = 0
        self.memory_usage_mb: float = 0.0

        # Histograms (latency tracking, last 1000 samples)
        self.http_request_duration_ms: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )  # {endpoint: [latency_ms, ...]}
        self.cache_lookup_duration_ms: deque = deque(maxlen=1000)
        self.auth_check_duration_ms: deque = deque(maxlen=1000)
        self.rate_limit_check_duration_ms: deque = deque(maxlen=1000)

        # Request/Response sizes
        self.request_size_bytes: deque = deque(maxlen=1000)
        self.response_size_bytes: deque = deque(maxlen=1000)

        # Error tracking
        self.recent_errors: deque = deque(maxlen=100)  # {timestamp, error_type, message}

        # Performance percentiles cache
        self.p50_cache = {}
        self.p95_cache = {}
        self.p99_cache = {}

        # Timestamps
        self.start_time = datetime.utcnow()
        self.last_reset = datetime.utcnow()

        logger.info("[METRICS] MetricsCollector initialized")

    @classmethod
    def get_instance(cls) -> 'MetricsCollector':
        """Get singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = MetricsCollector()
        return cls._instance

    # ========================================================================
    # COUNTER OPERATIONS
    # ========================================================================

    def record_http_request(self, method: str, path: str, status_code: int,
                           duration_ms: float, request_size: int = 0,
                           response_size: int = 0) -> None:
        """
        Record HTTP request metrics.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            status_code: HTTP status code (200, 404, 500, etc.)
            duration_ms: Request duration in milliseconds
            request_size: Request body size in bytes
            response_size: Response body size in bytes
        """
        with self._lock_internal:
            key = f"{method}_{path}"
            self.http_requests_total[key] += 1

            if status_code >= 400:
                self.http_errors_total[str(status_code)] += 1

            self.http_request_duration_ms[key].append(duration_ms)

            if request_size > 0:
                self.request_size_bytes.append(request_size)
            if response_size > 0:
                self.response_size_bytes.append(response_size)

    def record_cache_hit(self, duration_ms: float = 0.0) -> None:
        """Record cache hit."""
        with self._lock_internal:
            self.cache_hits_total += 1
            if duration_ms > 0:
                self.cache_lookup_duration_ms.append(duration_ms)

    def record_cache_miss(self, duration_ms: float = 0.0) -> None:
        """Record cache miss."""
        with self._lock_internal:
            self.cache_misses_total += 1
            if duration_ms > 0:
                self.cache_lookup_duration_ms.append(duration_ms)

    def record_cache_delete(self) -> None:
        """Record cache delete operation."""
        with self._lock_internal:
            self.cache_deletes_total += 1

    def record_auth_success(self, duration_ms: float = 0.0) -> None:
        """Record successful authentication."""
        with self._lock_internal:
            self.auth_successes_total += 1
            if duration_ms > 0:
                self.auth_check_duration_ms.append(duration_ms)

    def record_auth_failure(self, reason: str = "invalid_key") -> None:
        """Record authentication failure."""
        with self._lock_internal:
            self.auth_failures_total += 1
            self.recent_errors.append({
                'timestamp': datetime.utcnow(),
                'type': 'auth_failure',
                'reason': reason
            })

    def record_rate_limit_violation(self) -> None:
        """Record rate limit violation."""
        with self._lock_internal:
            self.rate_limit_violations_total += 1
            self.recent_errors.append({
                'timestamp': datetime.utcnow(),
                'type': 'rate_limit',
                'reason': 'quota_exceeded'
            })

    def record_security_event(self, event_type: str, details: str = "") -> None:
        """
        Record security event (SQL injection, XSS, etc.).

        Args:
            event_type: 'sql_injection' or 'xss'
            details: Additional context
        """
        with self._lock_internal:
            if event_type == 'sql_injection':
                self.sql_injection_attempts_total += 1
            elif event_type == 'xss':
                self.xss_attempts_total += 1

            self.recent_errors.append({
                'timestamp': datetime.utcnow(),
                'type': event_type,
                'details': details
            })

    # ========================================================================
    # GAUGE OPERATIONS
    # ========================================================================

    def set_http_requests_in_progress(self, count: int) -> None:
        """Set current in-progress request count."""
        with self._lock_internal:
            self.http_requests_in_progress = count

    def increment_http_requests_in_progress(self) -> None:
        """Increment in-progress request count."""
        with self._lock_internal:
            self.http_requests_in_progress += 1

    def decrement_http_requests_in_progress(self) -> None:
        """Decrement in-progress request count."""
        with self._lock_internal:
            if self.http_requests_in_progress > 0:
                self.http_requests_in_progress -= 1

    def set_cache_size_bytes(self, size: int) -> None:
        """Set current cache size in bytes."""
        with self._lock_internal:
            self.cache_size_bytes = size

    def set_memory_usage_mb(self, usage: float) -> None:
        """Set current memory usage in MB."""
        with self._lock_internal:
            self.memory_usage_mb = usage

    def set_active_connections(self, count: int) -> None:
        """Set current active connection count."""
        with self._lock_internal:
            self.active_connections = count

    # ========================================================================
    # STATISTICS & QUERIES
    # ========================================================================

    def get_cache_hit_rate(self) -> float:
        """Get cache hit rate as percentage (0-100)."""
        with self._lock_internal:
            total = self.cache_hits_total + self.cache_misses_total
            if total == 0:
                return 0.0
            return (self.cache_hits_total / total) * 100

    def get_auth_success_rate(self) -> float:
        """Get authentication success rate as percentage (0-100)."""
        with self._lock_internal:
            total = self.auth_successes_total + self.auth_failures_total
            if total == 0:
                return 0.0
            return (self.auth_successes_total / total) * 100

    def get_error_rate(self) -> float:
        """Get error rate as percentage of all requests."""
        with self._lock_internal:
            total = sum(self.http_requests_total.values())
            errors = sum(self.http_errors_total.values())
            if total == 0:
                return 0.0
            return (errors / total) * 100

    def get_percentile(self, histogram: deque, percentile: int) -> float:
        """
        Calculate percentile from histogram data.

        Args:
            histogram: Deque of numeric values
            percentile: Percentile (50, 95, 99, etc.)

        Returns:
            Percentile value or 0 if empty
        """
        with self._lock_internal:
            if not histogram:
                return 0.0

            sorted_data = sorted(histogram)
            index = int((percentile / 100) * len(sorted_data))
            return float(sorted_data[min(index, len(sorted_data) - 1)])

    def get_endpoint_stats(self, endpoint: str) -> Dict[str, Any]:
        """
        Get statistics for specific endpoint.

        Args:
            endpoint: Endpoint path (e.g., '/api/disciplines')

        Returns:
            Dict with: count, avg_duration_ms, p50, p95, p99
        """
        with self._lock_internal:
            # Find matching endpoint (handle both GET/POST variants)
            matching_keys = [k for k in self.http_requests_total.keys()
                           if endpoint in k]

            if not matching_keys:
                return {
                    'endpoint': endpoint,
                    'count': 0,
                    'avg_duration_ms': 0.0,
                    'p50': 0.0,
                    'p95': 0.0,
                    'p99': 0.0
                }

            # Aggregate data across all matching keys
            all_durations = []
            total_requests = 0

            for key in matching_keys:
                all_durations.extend(self.http_request_duration_ms[key])
                total_requests += self.http_requests_total[key]

            if not all_durations:
                return {
                    'endpoint': endpoint,
                    'count': total_requests,
                    'avg_duration_ms': 0.0,
                    'p50': 0.0,
                    'p95': 0.0,
                    'p99': 0.0
                }

            avg_duration = sum(all_durations) / len(all_durations)
            sorted_durations = sorted(all_durations)

            def percentile_value(pct):
                idx = int((pct / 100) * len(sorted_durations))
                return float(sorted_durations[min(idx, len(sorted_durations) - 1)])

            return {
                'endpoint': endpoint,
                'count': total_requests,
                'avg_duration_ms': round(avg_duration, 2),
                'p50': round(percentile_value(50), 2),
                'p95': round(percentile_value(95), 2),
                'p99': round(percentile_value(99), 2)
            }

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get comprehensive summary statistics."""
        with self._lock_internal:
            uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()

            total_requests = sum(self.http_requests_total.values())
            total_errors = sum(self.http_errors_total.values())

            total_cache_ops = self.cache_hits_total + self.cache_misses_total
            cache_hit_rate = (self.cache_hits_total / total_cache_ops * 100) if total_cache_ops > 0 else 0

            avg_request_latency = 0.0
            all_latencies = []
            for latencies in self.http_request_duration_ms.values():
                all_latencies.extend(latencies)
            if all_latencies:
                avg_request_latency = sum(all_latencies) / len(all_latencies)

            auth_success_rate = (self.auth_successes_total /
                               (self.auth_successes_total + self.auth_failures_total) * 100
                               if (self.auth_successes_total + self.auth_failures_total) > 0 else 0)

            return {
                'system': {
                    'uptime_seconds': int(uptime_seconds),
                    'uptime_hours': round(uptime_seconds / 3600, 2),
                    'start_time': self.start_time.isoformat(),
                    'memory_usage_mb': round(self.memory_usage_mb, 2),
                    'active_connections': self.active_connections,
                    'cache_size_bytes': self.cache_size_bytes,
                    'requests_in_progress': self.http_requests_in_progress
                },
                'http': {
                    'total_requests': total_requests,
                    'total_errors': total_errors,
                    'error_rate_percent': round(total_errors / total_requests * 100 if total_requests > 0 else 0, 2),
                    'avg_latency_ms': round(avg_request_latency, 2),
                    'requests_per_minute': round(total_requests / max(uptime_seconds / 60, 1), 2),
                    'request_count_by_status': dict(self.http_errors_total)
                },
                'cache': {
                    'hits': self.cache_hits_total,
                    'misses': self.cache_misses_total,
                    'deletes': self.cache_deletes_total,
                    'hit_rate_percent': round(cache_hit_rate, 2),
                    'total_operations': total_cache_ops
                },
                'authentication': {
                    'successes': self.auth_successes_total,
                    'failures': self.auth_failures_total,
                    'success_rate_percent': round(auth_success_rate, 2),
                    'avg_check_ms': round(sum(self.auth_check_duration_ms) / len(self.auth_check_duration_ms)
                                         if self.auth_check_duration_ms else 0, 2)
                },
                'rate_limiting': {
                    'violations_total': self.rate_limit_violations_total,
                    'avg_check_ms': round(sum(self.rate_limit_check_duration_ms) /
                                         len(self.rate_limit_check_duration_ms)
                                         if self.rate_limit_check_duration_ms else 0, 2)
                },
                'security': {
                    'sql_injection_attempts': self.sql_injection_attempts_total,
                    'xss_attempts': self.xss_attempts_total,
                    'total_security_events': (self.sql_injection_attempts_total +
                                             self.xss_attempts_total)
                }
            }

    def get_recent_errors(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent errors."""
        with self._lock_internal:
            return list(self.recent_errors)[-limit:]

    def export_prometheus_metrics(self) -> str:
        """
        Export metrics in Prometheus text format.

        Returns:
            Multi-line string in Prometheus exposition format
        """
        with self._lock_internal:
            lines = []

            # HELP and TYPE comments
            lines.append("# HELP http_requests_total Total HTTP requests")
            lines.append("# TYPE http_requests_total counter")

            # HTTP requests
            for key, count in self.http_requests_total.items():
                lines.append(f'http_requests_total{{endpoint="{key}"}} {count}')

            # HTTP errors
            lines.append("# HELP http_errors_total Total HTTP errors by status code")
            lines.append("# TYPE http_errors_total counter")
            for status, count in self.http_errors_total.items():
                lines.append(f'http_errors_total{{status="{status}"}} {count}')

            # Cache metrics
            lines.append("# HELP cache_hits_total Total cache hits")
            lines.append("# TYPE cache_hits_total counter")
            lines.append(f"cache_hits_total {self.cache_hits_total}")

            lines.append("# HELP cache_misses_total Total cache misses")
            lines.append("# TYPE cache_misses_total counter")
            lines.append(f"cache_misses_total {self.cache_misses_total}")

            lines.append("# HELP cache_hit_rate_percent Cache hit rate percentage")
            lines.append("# TYPE cache_hit_rate_percent gauge")
            lines.append(f"cache_hit_rate_percent {self.get_cache_hit_rate()}")

            # Auth metrics
            lines.append("# HELP auth_successes_total Total successful authentications")
            lines.append("# TYPE auth_successes_total counter")
            lines.append(f"auth_successes_total {self.auth_successes_total}")

            lines.append("# HELP auth_failures_total Total authentication failures")
            lines.append("# TYPE auth_failures_total counter")
            lines.append(f"auth_failures_total {self.auth_failures_total}")

            # Rate limit metrics
            lines.append("# HELP rate_limit_violations_total Total rate limit violations")
            lines.append("# TYPE rate_limit_violations_total counter")
            lines.append(f"rate_limit_violations_total {self.rate_limit_violations_total}")

            # Security metrics
            lines.append("# HELP sql_injection_attempts_total Total SQL injection attempts detected")
            lines.append("# TYPE sql_injection_attempts_total counter")
            lines.append(f"sql_injection_attempts_total {self.sql_injection_attempts_total}")

            lines.append("# HELP xss_attempts_total Total XSS attempts detected")
            lines.append("# TYPE xss_attempts_total counter")
            lines.append(f"xss_attempts_total {self.xss_attempts_total}")

            # Gauge metrics
            lines.append("# HELP http_requests_in_progress Current HTTP requests in progress")
            lines.append("# TYPE http_requests_in_progress gauge")
            lines.append(f"http_requests_in_progress {self.http_requests_in_progress}")

            lines.append("# HELP cache_size_bytes Current cache size in bytes")
            lines.append("# TYPE cache_size_bytes gauge")
            lines.append(f"cache_size_bytes {self.cache_size_bytes}")

            lines.append("# HELP memory_usage_mb Current memory usage in MB")
            lines.append("# TYPE memory_usage_mb gauge")
            lines.append(f"memory_usage_mb {self.memory_usage_mb}")

            return "\n".join(lines) + "\n"

    def reset_metrics(self) -> None:
        """Reset all metrics to initial state."""
        with self._lock_internal:
            self.http_requests_total.clear()
            self.http_errors_total.clear()
            self.cache_hits_total = 0
            self.cache_misses_total = 0
            self.cache_deletes_total = 0
            self.auth_successes_total = 0
            self.auth_failures_total = 0
            self.rate_limit_violations_total = 0
            self.sql_injection_attempts_total = 0
            self.xss_attempts_total = 0
            self.http_request_duration_ms.clear()
            self.cache_lookup_duration_ms.clear()
            self.auth_check_duration_ms.clear()
            self.rate_limit_check_duration_ms.clear()
            self.recent_errors.clear()
            self.last_reset = datetime.utcnow()
            logger.info("[METRICS] All metrics reset")


def get_metrics_collector() -> MetricsCollector:
    """Get or create metrics collector singleton."""
    return MetricsCollector.get_instance()
