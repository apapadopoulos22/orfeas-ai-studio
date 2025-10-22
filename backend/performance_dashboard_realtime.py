"""
Real-Time Performance Dashboard - Phase 4 Tier 1
WebSocket-based live metrics streaming for real-time monitoring
Supports multi-client subscriptions with configurable update frequency
"""

import asyncio
import json
import logging
from typing import Dict, Set, Optional, List
from datetime import datetime, timedelta
from dataclasses import asdict, dataclass
import threading
import uuid

logger = logging.getLogger(__name__)


@dataclass
class MetricsSnapshot:
    """Metrics snapshot at a point in time"""
    timestamp: datetime
    gpu_memory_mb: float
    cpu_usage_percent: float
    cache_hit_rate: float
    cache_miss_rate: float
    latency_ms: float
    throughput_rps: float
    active_requests: int
    error_rate_percent: float


class RealtimePerformanceDashboard:
    """Real-time performance metrics broadcaster with history tracking"""

    def __init__(self, max_history: int = 300, update_interval_seconds: float = 1.0):
        """
        Initialize real-time dashboard

        Args:
            max_history: Maximum number of historical samples to keep
            update_interval_seconds: Frequency of metric updates
        """
        self.subscribers: Set[str] = set()
        self.current_metrics: Dict = {}
        self.current_snapshot: Optional[MetricsSnapshot] = None
        self.max_history = max_history
        self.update_interval_seconds = update_interval_seconds

        # Metrics history organized by metric type
        self.metrics_history: Dict[str, List[Dict]] = {
            'gpu_memory': [],
            'cpu_usage': [],
            'cache_hits': [],
            'latency': [],
            'throughput': [],
            'error_rate': [],
            'active_requests': []
        }

        self._lock = threading.Lock()
        self._subscriber_lock = threading.Lock()
        self.message_queue: List[Dict] = []
        self.stats = {
            'total_broadcasts': 0,
            'total_snapshots': 0,
            'subscriber_connects': 0,
            'subscriber_disconnects': 0
        }

    async def broadcast_metrics(self, metrics: Dict) -> None:
        """Broadcast metrics to all subscribers"""
        try:
            with self._lock:
                self.current_metrics = metrics
                self._update_history(metrics)

                # Create snapshot
                self.current_snapshot = MetricsSnapshot(
                    timestamp=datetime.now(),
                    gpu_memory_mb=metrics.get('gpu_memory', 0),
                    cpu_usage_percent=metrics.get('cpu_usage', 0),
                    cache_hit_rate=metrics.get('cache_hit_rate', 0),
                    cache_miss_rate=metrics.get('cache_miss_rate', 0),
                    latency_ms=metrics.get('latency_ms', 0),
                    throughput_rps=metrics.get('throughput', 0),
                    active_requests=metrics.get('active_requests', 0),
                    error_rate_percent=metrics.get('error_rate', 0)
                )

                self.stats['total_broadcasts'] += 1
                self.stats['total_snapshots'] += 1

            # Format for WebSocket transmission
            message = {
                'type': 'metrics_update',
                'timestamp': datetime.now().isoformat(),
                'sequence': self.stats['total_broadcasts'],
                'data': metrics,
                'snapshot': {
                    'timestamp': self.current_snapshot.timestamp.isoformat(),
                    'gpu_memory_mb': self.current_snapshot.gpu_memory_mb,
                    'cpu_usage_percent': self.current_snapshot.cpu_usage_percent,
                    'cache_hit_rate': self.current_snapshot.cache_hit_rate,
                    'latency_ms': self.current_snapshot.latency_ms,
                    'throughput_rps': self.current_snapshot.throughput_rps,
                    'error_rate_percent': self.current_snapshot.error_rate_percent
                },
                'history': self._get_recent_history(),
                'subscriber_count': len(self.subscribers)
            }

            with self._subscriber_lock:
                if self.subscribers:
                    logger.debug(
                        f"[DASHBOARD] Broadcasting to {len(self.subscribers)} subscribers: "
                        f"GPU {metrics.get('gpu_memory', 0):.0f}MB, "
                        f"Throughput {metrics.get('throughput', 0):.1f} RPS"
                    )

            # Queue message for subscribers
            with self._lock:
                self.message_queue.append(message)
                # Keep only recent messages
                if len(self.message_queue) > 100:
                    self.message_queue = self.message_queue[-100:]

            return message

        except Exception as e:
            logger.error(f"[DASHBOARD] Broadcast failed: {e}")
            return {'error': str(e)}

    def subscribe(self, client_id: Optional[str] = None) -> str:
        """
        Subscribe to metrics updates

        Args:
            client_id: Optional client identifier, generates UUID if not provided

        Returns:
            The client_id that was registered
        """
        if client_id is None:
            client_id = str(uuid.uuid4())

        with self._subscriber_lock:
            self.subscribers.add(client_id)
            self.stats['subscriber_connects'] += 1

        logger.info(
            f"[DASHBOARD] Client {client_id} subscribed "
            f"(total: {len(self.subscribers)}, connects: {self.stats['subscriber_connects']})"
        )

        return client_id

    def unsubscribe(self, client_id: str) -> None:
        """Unsubscribe from metrics updates"""
        with self._subscriber_lock:
            self.subscribers.discard(client_id)
            self.stats['subscriber_disconnects'] += 1

        logger.info(
            f"[DASHBOARD] Client {client_id} unsubscribed "
            f"(remaining: {len(self.subscribers)}, disconnects: {self.stats['subscriber_disconnects']})"
        )

    def _update_history(self, metrics: Dict) -> None:
        """Update metrics history for trending and charting"""
        timestamp = datetime.now().isoformat()

        # Update each metric category
        metric_mappings = {
            'gpu_memory': 'gpu_memory',
            'cpu_usage': 'cpu_usage',
            'cache_hits': 'cache_hit_rate',
            'latency': 'latency_ms',
            'throughput': 'throughput',
            'error_rate': 'error_rate',
            'active_requests': 'active_requests'
        }

        with self._lock:
            for history_key, metric_key in metric_mappings.items():
                if metric_key in metrics:
                    self.metrics_history[history_key].append({
                        'time': timestamp,
                        'value': metrics[metric_key]
                    })

                    # Trim history to max size
                    if len(self.metrics_history[history_key]) > self.max_history:
                        self.metrics_history[history_key] = \
                            self.metrics_history[history_key][-self.max_history:]

    def _get_recent_history(self, minutes: int = 5) -> Dict:
        """Get recent history for charting and analysis"""
        with self._lock:
            # Calculate number of samples based on update interval
            num_samples = max(1, int((minutes * 60) / self.update_interval_seconds))

            return {
                key: values[-num_samples:] if num_samples else values
                for key, values in self.metrics_history.items()
            }

    def get_dashboard_summary(self) -> Dict:
        """Get summary for dashboard display"""
        with self._lock:
            gpu_mem = self.metrics_history.get('gpu_memory', [])
            cpu = self.metrics_history.get('cpu_usage', [])
            cache_hits = self.metrics_history.get('cache_hits', [])
            latency = self.metrics_history.get('latency', [])
            throughput = self.metrics_history.get('throughput', [])
            errors = self.metrics_history.get('error_rate', [])

            def get_stat(data, stat_type='avg'):
                if not data:
                    return 0
                values = [d['value'] for d in data]
                if stat_type == 'avg':
                    return sum(values) / len(values)
                elif stat_type == 'max':
                    return max(values)
                elif stat_type == 'min':
                    return min(values)
                elif stat_type == 'latest':
                    return values[-1] if values else 0
                return 0

            return {
                'current': self.current_metrics,
                'current_snapshot': {
                    'timestamp': self.current_snapshot.timestamp.isoformat() if self.current_snapshot else None,
                    'gpu_memory_mb': self.current_snapshot.gpu_memory_mb if self.current_snapshot else 0,
                    'cpu_usage_percent': self.current_snapshot.cpu_usage_percent if self.current_snapshot else 0,
                    'cache_hit_rate': self.current_snapshot.cache_hit_rate if self.current_snapshot else 0,
                    'latency_ms': self.current_snapshot.latency_ms if self.current_snapshot else 0,
                    'throughput_rps': self.current_snapshot.throughput_rps if self.current_snapshot else 0,
                    'error_rate_percent': self.current_snapshot.error_rate_percent if self.current_snapshot else 0
                },
                'averages': {
                    'gpu_memory_mb': round(get_stat(gpu_mem, 'avg'), 2),
                    'cpu_usage_percent': round(get_stat(cpu, 'avg'), 2),
                    'cache_hit_rate': round(get_stat(cache_hits, 'avg'), 4),
                    'latency_ms': round(get_stat(latency, 'avg'), 2),
                    'throughput_rps': round(get_stat(throughput, 'avg'), 2),
                    'error_rate_percent': round(get_stat(errors, 'avg'), 2)
                },
                'peaks': {
                    'gpu_memory_mb': round(get_stat(gpu_mem, 'max'), 2),
                    'cpu_usage_percent': round(get_stat(cpu, 'max'), 2),
                    'cache_hit_rate': round(get_stat(cache_hits, 'max'), 4),
                    'latency_ms': round(get_stat(latency, 'max'), 2),
                    'throughput_rps': round(get_stat(throughput, 'max'), 2),
                    'error_rate_percent': round(get_stat(errors, 'max'), 2)
                },
                'minimums': {
                    'latency_ms': round(get_stat(latency, 'min'), 2),
                    'error_rate_percent': round(get_stat(errors, 'min'), 2)
                },
                'subscribers': len(self.subscribers),
                'history_points': sum(len(v) for v in self.metrics_history.values()),
                'stats': self.stats
            }

    def get_health_status(self) -> Dict:
        """Get dashboard health and connectivity status"""
        return {
            'operational': True,
            'timestamp': datetime.now().isoformat(),
            'subscribers': len(self.subscribers),
            'message_queue_size': len(self.message_queue),
            'stats': self.stats.copy(),
            'history_samples': {
                key: len(val) for key, val in self.metrics_history.items()
            }
        }

    def clear_history(self) -> Dict:
        """Clear all historical data"""
        with self._lock:
            total_samples = sum(len(v) for v in self.metrics_history.values())
            for key in self.metrics_history:
                self.metrics_history[key] = []

        logger.info(f"[DASHBOARD] Cleared {total_samples} historical samples")
        return {'samples_cleared': total_samples}

    def export_metrics_csv(self) -> str:
        """Export current metrics as CSV format"""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        with self._lock:
            # Get all historical data points
            if not self.metrics_history or not self.metrics_history['latency']:
                return "No data available"

            # Write header
            writer.writerow(['timestamp', 'gpu_memory_mb', 'cpu_usage_percent',
                           'cache_hit_rate', 'latency_ms', 'throughput_rps'])

            # Merge all histories by timestamp
            num_samples = max(len(v) for v in self.metrics_history.values())
            for i in range(num_samples):
                row = [
                    self.metrics_history['latency'][i]['time'] if i < len(self.metrics_history['latency']) else '',
                    self.metrics_history['gpu_memory'][i]['value'] if i < len(self.metrics_history['gpu_memory']) else 0,
                    self.metrics_history['cpu_usage'][i]['value'] if i < len(self.metrics_history['cpu_usage']) else 0,
                    self.metrics_history['cache_hits'][i]['value'] if i < len(self.metrics_history['cache_hits']) else 0,
                    self.metrics_history['latency'][i]['value'] if i < len(self.metrics_history['latency']) else 0,
                    self.metrics_history['throughput'][i]['value'] if i < len(self.metrics_history['throughput']) else 0,
                ]
                writer.writerow(row)

        return output.getvalue()


# Singleton instance
_dashboard_instance: Optional[RealtimePerformanceDashboard] = None
_dashboard_lock = threading.Lock()


def get_dashboard(max_history: int = 300, update_interval: float = 1.0) -> RealtimePerformanceDashboard:
    """Get or create dashboard singleton"""
    global _dashboard_instance
    if _dashboard_instance is None:
        with _dashboard_lock:
            if _dashboard_instance is None:
                _dashboard_instance = RealtimePerformanceDashboard(
                    max_history=max_history,
                    update_interval_seconds=update_interval
                )
                logger.info(
                    f"[DASHBOARD] Initialized with {max_history} max samples, "
                    f"{update_interval}s update interval"
                )
    return _dashboard_instance


def reset_dashboard() -> None:
    """Reset dashboard instance (for testing)"""
    global _dashboard_instance
    with _dashboard_lock:
        _dashboard_instance = None
