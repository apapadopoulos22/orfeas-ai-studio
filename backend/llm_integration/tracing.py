"""
Performance tracing infrastructure for LLM integration layer.

Provides:
- Request-level tracing
- Component-level timing
- Performance metrics collection
- Performance reporting
"""

import time
import logging
import asyncio
from functools import wraps
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any, Coroutine
from dataclasses import dataclass, field
from contextlib import asynccontextmanager, contextmanager

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Single performance metric."""
    name: str
    component: str
    duration_ms: float
    timestamp: datetime
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'component': self.component,
            'duration_ms': self.duration_ms,
            'timestamp': self.timestamp.isoformat(),
            'success': self.success,
            'error': self.error,
            'metadata': self.metadata
        }


@dataclass
class PerformanceStats:
    """Aggregated performance statistics."""
    component: str
    operation: str
    count: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: float = float('inf')
    max_duration_ms: float = 0.0
    error_count: int = 0
    success_count: int = 0

    @property
    def avg_duration_ms(self) -> float:
        """Average duration in milliseconds."""
        return self.total_duration_ms / self.count if self.count > 0 else 0.0

    @property
    def success_rate(self) -> float:
        """Success rate (0-1)."""
        return self.success_count / self.count if self.count > 0 else 0.0

    @property
    def error_rate(self) -> float:
        """Error rate (0-1)."""
        return self.error_count / self.count if self.count > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            'component': self.component,
            'operation': self.operation,
            'count': self.count,
            'avg_duration_ms': self.avg_duration_ms,
            'min_duration_ms': self.min_duration_ms,
            'max_duration_ms': self.max_duration_ms,
            'total_duration_ms': self.total_duration_ms,
            'error_count': self.error_count,
            'success_count': self.success_count,
            'success_rate': self.success_rate,
            'error_rate': self.error_rate
        }


class PerformanceTracer:
    """Track and analyze performance across components."""

    def __init__(self, max_metrics: int = 10000):
        self.metrics: List[PerformanceMetric] = []
        self.max_metrics = max_metrics
        self.stats: Dict[str, PerformanceStats] = {}

    def record_metric(self, metric: PerformanceMetric):
        """Record a performance metric."""
        # Keep metrics under max size
        if len(self.metrics) >= self.max_metrics:
            self.metrics.pop(0)

        self.metrics.append(metric)

        # Update stats
        key = f"{metric.component}:{metric.name}"
        if key not in self.stats:
            self.stats[key] = PerformanceStats(
                component=metric.component,
                operation=metric.name
            )

        stats = self.stats[key]
        stats.count += 1
        stats.total_duration_ms += metric.duration_ms
        stats.min_duration_ms = min(stats.min_duration_ms, metric.duration_ms)
        stats.max_duration_ms = max(stats.max_duration_ms, metric.duration_ms)

        if metric.success:
            stats.success_count += 1
        else:
            stats.error_count += 1

    def get_stats(self, component: str = None, operation: str = None) -> List[PerformanceStats]:
        """Get performance statistics."""
        results = list(self.stats.values())

        if component:
            results = [s for s in results if s.component == component]

        if operation:
            results = [s for s in results if s.operation == operation]

        return results

    def get_slowest_operations(self, count: int = 10) -> List[PerformanceStats]:
        """Get slowest operations."""
        sorted_stats = sorted(
            self.stats.values(),
            key=lambda s: s.avg_duration_ms,
            reverse=True
        )
        return sorted_stats[:count]

    def get_error_operations(self, min_error_rate: float = 0.1) -> List[PerformanceStats]:
        """Get operations with high error rates."""
        return [
            s for s in self.stats.values()
            if s.error_rate >= min_error_rate
        ]

    def get_recent_metrics(self, count: int = 100, component: str = None) -> List[PerformanceMetric]:
        """Get recent metrics."""
        metrics = self.metrics[-count:]

        if component:
            metrics = [m for m in metrics if m.component == component]

        return metrics

    def get_report(self) -> dict:
        """Get comprehensive performance report."""
        all_stats = list(self.stats.values())

        total_operations = sum(s.count for s in all_stats)
        total_errors = sum(s.error_count for s in all_stats)
        avg_duration = (
            sum(s.total_duration_ms for s in all_stats) / total_operations
            if total_operations > 0 else 0.0
        )

        return {
            'timestamp': datetime.now().isoformat(),
            'total_operations': total_operations,
            'total_errors': total_errors,
            'error_rate': total_errors / total_operations if total_operations > 0 else 0.0,
            'avg_duration_ms': avg_duration,
            'slowest_operations': [s.to_dict() for s in self.get_slowest_operations(5)],
            'error_operations': [s.to_dict() for s in self.get_error_operations(0.01)],
            'all_stats': [s.to_dict() for s in all_stats]
        }

    def clear(self):
        """Clear all metrics and stats."""
        self.metrics = []
        self.stats = {}


# Global performance tracer
performance_tracer = PerformanceTracer()


def trace_performance(component: str, operation: str = None):
    """
    Decorator to trace performance of functions.

    Args:
        component: Component name
        operation: Operation name (defaults to function name)
    """
    def decorator(func):
        op_name = operation or func.__name__

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start) * 1000

                metric = PerformanceMetric(
                    name=op_name,
                    component=component,
                    duration_ms=duration_ms,
                    timestamp=datetime.now(),
                    success=True
                )
                performance_tracer.record_metric(metric)

                logger.debug(
                    f"{component}.{op_name}: {duration_ms:.2f}ms"
                )

                return result

            except Exception as e:
                duration_ms = (time.time() - start) * 1000

                metric = PerformanceMetric(
                    name=op_name,
                    component=component,
                    duration_ms=duration_ms,
                    timestamp=datetime.now(),
                    success=False,
                    error=str(type(e).__name__)
                )
                performance_tracer.record_metric(metric)

                logger.warning(
                    f"{component}.{op_name} failed: {duration_ms:.2f}ms - {e}"
                )

                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start) * 1000

                metric = PerformanceMetric(
                    name=op_name,
                    component=component,
                    duration_ms=duration_ms,
                    timestamp=datetime.now(),
                    success=True
                )
                performance_tracer.record_metric(metric)

                logger.debug(
                    f"{component}.{op_name}: {duration_ms:.2f}ms"
                )

                return result

            except Exception as e:
                duration_ms = (time.time() - start) * 1000

                metric = PerformanceMetric(
                    name=op_name,
                    component=component,
                    duration_ms=duration_ms,
                    timestamp=datetime.now(),
                    success=False,
                    error=str(type(e).__name__)
                )
                performance_tracer.record_metric(metric)

                logger.warning(
                    f"{component}.{op_name} failed: {duration_ms:.2f}ms - {e}"
                )

                raise

        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


@contextmanager
def trace_block(component: str, operation: str, metadata: dict = None):
    """
    Context manager for tracing code blocks.

    Usage:
        with trace_block('router', 'model_selection', {'model': 'gpt4'}):
            # ... code ...
    """
    start = time.time()
    metadata = metadata or {}

    try:
        yield
        duration_ms = (time.time() - start) * 1000

        metric = PerformanceMetric(
            name=operation,
            component=component,
            duration_ms=duration_ms,
            timestamp=datetime.now(),
            success=True,
            metadata=metadata
        )
        performance_tracer.record_metric(metric)

        logger.debug(f"{component}.{operation}: {duration_ms:.2f}ms")

    except Exception as e:
        duration_ms = (time.time() - start) * 1000

        metric = PerformanceMetric(
            name=operation,
            component=component,
            duration_ms=duration_ms,
            timestamp=datetime.now(),
            success=False,
            error=str(type(e).__name__),
            metadata=metadata
        )
        performance_tracer.record_metric(metric)

        logger.warning(
            f"{component}.{operation} failed: {duration_ms:.2f}ms - {e}"
        )

        raise


@asynccontextmanager
async def trace_block_async(component: str, operation: str, metadata: dict = None):
    """
    Async context manager for tracing async code blocks.

    Usage:
        async with trace_block_async('cache', 'retrieval', {'key': 'xyz'}):
            # ... async code ...
    """
    start = time.time()
    metadata = metadata or {}

    try:
        yield
        duration_ms = (time.time() - start) * 1000

        metric = PerformanceMetric(
            name=operation,
            component=component,
            duration_ms=duration_ms,
            timestamp=datetime.now(),
            success=True,
            metadata=metadata
        )
        performance_tracer.record_metric(metric)

        logger.debug(f"{component}.{operation}: {duration_ms:.2f}ms")

    except Exception as e:
        duration_ms = (time.time() - start) * 1000

        metric = PerformanceMetric(
            name=operation,
            component=component,
            duration_ms=duration_ms,
            timestamp=datetime.now(),
            success=False,
            error=str(type(e).__name__),
            metadata=metadata
        )
        performance_tracer.record_metric(metric)

        logger.warning(
            f"{component}.{operation} failed: {duration_ms:.2f}ms - {e}"
        )

        raise


def get_performance_report() -> dict:
    """Get comprehensive performance report."""
    return performance_tracer.get_report()


def get_slowest_operations(count: int = 10) -> List[dict]:
    """Get slowest operations."""
    return [s.to_dict() for s in performance_tracer.get_slowest_operations(count)]


def get_error_operations(min_error_rate: float = 0.1) -> List[dict]:
    """Get operations with high error rates."""
    return [s.to_dict() for s in performance_tracer.get_error_operations(min_error_rate)]
