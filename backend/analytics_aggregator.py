"""
[ORFEAS PHASE 2 TASK 3] Analytics Aggregator Module
Real-time aggregation pipeline for analytics metrics.

Purpose:
  Aggregates raw events into metrics using time-window bucketing.
  Calculates 1-second, 1-minute, 1-hour, 1-day aggregations.
  Maintains running statistics for real-time dashboards.

Key Components:
  - TimeWindowAggregator: Main aggregation coordinator
  - MetricsCalculator: Statistics computation
  - DataRollup: Higher-level aggregation

Usage:
  from analytics_aggregator import get_aggregator

  aggregator = get_aggregator()
  metrics = aggregator.get_metrics("cache_hit_rate", "1hour")
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class AggregatedMetric:
    """Container for aggregated metric data."""

    metric_name: str
    window: str  # "1s", "1m", "1h", "1d"
    timestamp: float
    value: float
    count: int = 0
    min_val: float = float("inf")
    max_val: float = float("-inf")
    sum_val: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_name": self.metric_name,
            "window": self.window,
            "timestamp": self.timestamp,
            "value": self.value,
            "count": self.count,
            "min": self.min_val if self.min_val != float("inf") else None,
            "max": self.max_val if self.max_val != float("-inf") else None,
            "sum": self.sum_val,
            "metadata": self.metadata,
        }


class MetricsCalculator:
    """Calculates statistics from raw events."""

    @staticmethod
    def calculate_cache_hit_rate(events: List[Dict[str, Any]]) -> float:
        """Calculate cache hit rate from events."""
        if not events:
            return 0.0

        hits = sum(1 for e in events if e.get("event_type") == "cache_hit")
        total = sum(1 for e in events if e.get("event_type") in ("cache_hit", "cache_miss"))

        return hits / total if total > 0 else 0.0

    @staticmethod
    def calculate_error_rate(events: List[Dict[str, Any]]) -> float:
        """Calculate error rate from events."""
        if not events:
            return 0.0

        errors = sum(
            1
            for e in events
            if not e.get("success", True) or e.get("event_type", "").endswith("_error")
        )
        total = len(events)

        return errors / total if total > 0 else 0.0

    @staticmethod
    def calculate_average_latency(events: List[Dict[str, Any]]) -> float:
        """Calculate average latency from events."""
        if not events:
            return 0.0

        latencies = [e.get("duration_ms", 0) for e in events]
        return sum(latencies) / len(latencies) if latencies else 0.0

    @staticmethod
    def calculate_throughput(events: List[Dict[str, Any]], window_seconds: int) -> float:
        """Calculate throughput (events/sec) in time window."""
        if not events or window_seconds <= 0:
            return 0.0

        return len(events) / window_seconds

    @staticmethod
    def calculate_p95_latency(events: List[Dict[str, Any]]) -> float:
        """Calculate 95th percentile latency."""
        if not events:
            return 0.0

        latencies = sorted([e.get("duration_ms", 0) for e in events])
        idx = int(len(latencies) * 0.95)
        return latencies[idx] if idx < len(latencies) else latencies[-1]


class TimeWindowAggregator:
    """Aggregates events into time windows."""

    _instance: Optional["TimeWindowAggregator"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "TimeWindowAggregator":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize aggregator."""
        if hasattr(self, "_initialized"):
            return

        self._initialized = True

        # Aggregation windows (in seconds)
        self.windows = {
            "1s": 1,
            "1m": 60,
            "1h": 3600,
            "1d": 86400,
        }

        # Metric storage: metric_name -> window -> list of aggregated metrics
        self.metrics: Dict[str, Dict[str, List[AggregatedMetric]]] = {}
        self.metrics_lock = threading.Lock()

        # Buckets: window -> {timestamp -> events}
        self.buckets: Dict[str, Dict[float, List[Dict[str, Any]]]] = {
            window: {} for window in self.windows
        }
        self.buckets_lock = threading.Lock()

        self.calculator = MetricsCalculator()

        logger.info("[ANALYTICS] Time window aggregator initialized")

    def add_event(self, event_data: Dict[str, Any]) -> None:
        """
        Add event to aggregation buckets.

        Args:
            event_data: Event dictionary
        """
        timestamp = event_data.get("timestamp", time.time())

        with self.buckets_lock:
            # Add to each time window
            for window_name, window_seconds in self.windows.items():
                bucket_time = (timestamp // window_seconds) * window_seconds
                bucket_key = window_name

                if bucket_key not in self.buckets:
                    self.buckets[bucket_key] = {}

                if bucket_time not in self.buckets[bucket_key]:
                    self.buckets[bucket_key][bucket_time] = []

                self.buckets[bucket_key][bucket_time].append(event_data)

                # Clean old buckets (keep only last 1000)
                if len(self.buckets[bucket_key]) > 1000:
                    oldest = min(self.buckets[bucket_key].keys())
                    del self.buckets[bucket_key][oldest]

    def aggregate_metric(self, metric_name: str, window: str, events: List[Dict[str, Any]]) -> AggregatedMetric:
        """
        Aggregate events into a metric.

        Args:
            metric_name: Name of metric (e.g., "cache_hit_rate")
            window: Time window (e.g., "1m")
            events: Events to aggregate

        Returns:
            AggregatedMetric with calculated value
        """
        timestamp = time.time()

        # Calculate metric value based on name
        if metric_name == "cache_hit_rate":
            value = self.calculator.calculate_cache_hit_rate(events)
        elif metric_name == "error_rate":
            value = self.calculator.calculate_error_rate(events)
        elif metric_name == "average_latency":
            value = self.calculator.calculate_average_latency(events)
        elif metric_name == "throughput":
            value = self.calculator.calculate_throughput(events, self.windows.get(window, 1))
        elif metric_name == "p95_latency":
            value = self.calculator.calculate_p95_latency(events)
        else:
            # Unknown metric, return 0
            value = 0.0

        return AggregatedMetric(
            metric_name=metric_name,
            window=window,
            timestamp=timestamp,
            value=value,
            count=len(events),
            min_val=min([e.get("duration_ms", 0) for e in events], default=0.0),
            max_val=max([e.get("duration_ms", 0) for e in events], default=0.0),
            sum_val=sum([e.get("duration_ms", 0) for e in events]),
        )

    def get_metrics(
        self, metric_name: str, window: str, limit: int = 100
    ) -> List[AggregatedMetric]:
        """
        Get aggregated metrics for a specific metric and window.

        Args:
            metric_name: Name of metric
            window: Time window
            limit: Maximum number of aggregations to return

        Returns:
            List of AggregatedMetric objects
        """
        with self.buckets_lock:
            if window not in self.buckets:
                return []

            # Get bucket data
            bucket_data = self.buckets[window]

            # Aggregate each bucket
            metrics = []
            for bucket_time in sorted(bucket_data.keys(), reverse=True)[:limit]:
                events = bucket_data[bucket_time]
                metric = self.aggregate_metric(metric_name, window, events)
                metrics.append(metric)

            return metrics

    def get_current_metric(self, metric_name: str) -> Optional[AggregatedMetric]:
        """
        Get current metric value (1-second window).

        Args:
            metric_name: Name of metric

        Returns:
            Current AggregatedMetric or None
        """
        metrics = self.get_metrics(metric_name, "1s", limit=1)
        return metrics[0] if metrics else None

    def get_metrics_snapshot(self) -> Dict[str, Any]:
        """Get snapshot of all current metrics."""
        snapshot = {}

        metrics_to_calculate = [
            "cache_hit_rate",
            "error_rate",
            "average_latency",
            "p95_latency",
            "throughput",
        ]

        for metric_name in metrics_to_calculate:
            current = self.get_current_metric(metric_name)
            if current:
                snapshot[metric_name] = current.to_dict()

        return snapshot

    def clear(self) -> None:
        """Clear all aggregated data."""
        with self.buckets_lock:
            for window in self.buckets:
                self.buckets[window].clear()

        logger.info("[ANALYTICS] Aggregator cleared")


# Global aggregator instance
_aggregator: Optional[TimeWindowAggregator] = None


def get_aggregator() -> TimeWindowAggregator:
    """Get singleton aggregator."""
    global _aggregator
    if _aggregator is None:
        _aggregator = TimeWindowAggregator()
    return _aggregator
