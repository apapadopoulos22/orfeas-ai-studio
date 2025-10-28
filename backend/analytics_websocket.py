"""
[ORFEAS PHASE 2 TASK 3] WebSocket Analytics Integration
Real-time metrics streaming via Socket.IO.

Purpose:
  Broadcasts aggregated metrics to connected dashboards.
  Manages subscriptions and room-based messaging.
  Handles real-time metric updates.

Key Components:
  - WebSocketBroadcaster: Broadcast engine
  - DashboardSubscriber: Subscription manager
  - MetricsStreamer: Real-time data streaming

Usage:
  from analytics_websocket import get_broadcaster

  broadcaster = get_broadcaster()
  broadcaster.broadcast_metrics(metrics_data)
"""

import json
import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class DashboardSubscriber:
    """Manages dashboard WebSocket subscriptions."""

    def __init__(self):
        """Initialize subscriber manager."""
        self.subscribers: Dict[str, Set[str]] = {}  # metric -> {session_ids}
        self.lock = threading.Lock()

    def subscribe(self, metric_name: str, session_id: str) -> None:
        """
        Subscribe to metric updates.

        Args:
            metric_name: Metric to subscribe to
            session_id: Client session ID
        """
        with self.lock:
            if metric_name not in self.subscribers:
                self.subscribers[metric_name] = set()
            self.subscribers[metric_name].add(session_id)

            logger.debug(f"[ANALYTICS] {session_id} subscribed to {metric_name}")

    def unsubscribe(self, metric_name: str, session_id: str) -> None:
        """Unsubscribe from metric."""
        with self.lock:
            if metric_name in self.subscribers:
                self.subscribers[metric_name].discard(session_id)

                if not self.subscribers[metric_name]:
                    del self.subscribers[metric_name]

            logger.debug(f"[ANALYTICS] {session_id} unsubscribed from {metric_name}")

    def get_subscribers(self, metric_name: str) -> Set[str]:
        """Get all subscribers for metric."""
        with self.lock:
            return self.subscribers.get(metric_name, set()).copy()

    def clear(self) -> None:
        """Clear all subscriptions."""
        with self.lock:
            self.subscribers.clear()


class WebSocketBroadcaster:
    """Broadcasts metrics to connected dashboards."""

    _instance: Optional["WebSocketBroadcaster"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "WebSocketBroadcaster":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize broadcaster."""
        if hasattr(self, "_initialized"):
            return

        self._initialized = True
        self.subscriber = DashboardSubscriber()
        self.socketio = None
        self.broadcast_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
        self.broadcast_lock = threading.Lock()

    def initialize(self, socketio: Any) -> None:
        """
        Initialize with Flask-SocketIO instance.

        Args:
            socketio: Flask-SocketIO instance
        """
        self.socketio = socketio
        logger.info("[ANALYTICS] WebSocket broadcaster initialized")

    def register_broadcast_callback(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """
        Register callback for metric broadcasts.

        Args:
            callback: Function(metric_name, data)
        """
        self.broadcast_callbacks.append(callback)

    def broadcast_metrics(self, metric_name: str, metric_data: Dict[str, Any]) -> None:
        """
        Broadcast metric update to subscribers.

        Args:
            metric_name: Name of metric
            metric_data: Metric data dictionary
        """
        with self.broadcast_lock:
            # Get subscribers for this metric
            subscribers = self.subscriber.get_subscribers(metric_name)

            if not subscribers:
                return

            # Prepare broadcast data
            broadcast_data = {
                "metric_name": metric_name,
                "timestamp": time.time(),
                "data": metric_data,
            }

            # Emit to each subscriber
            if self.socketio:
                try:
                    for session_id in subscribers:
                        self.socketio.emit(
                            "analytics_update",
                            broadcast_data,
                            room=f"analytics:{session_id}",
                        )

                    logger.debug(
                        f"[ANALYTICS] Broadcast {metric_name} to {len(subscribers)} subscribers"
                    )
                except Exception as e:
                    logger.error(f"[ANALYTICS] Broadcast error: {e}")

            # Call registered callbacks
            for callback in self.broadcast_callbacks:
                try:
                    callback(metric_name, metric_data)
                except Exception as e:
                    logger.error(f"[ANALYTICS] Callback error: {e}")

    def broadcast_metrics_snapshot(self, metrics_snapshot: Dict[str, Dict[str, Any]]) -> None:
        """
        Broadcast all metrics snapshot.

        Args:
            metrics_snapshot: Dictionary of all current metrics
        """
        with self.broadcast_lock:
            broadcast_data = {
                "metrics": metrics_snapshot,
                "timestamp": time.time(),
                "event": "metrics_snapshot",
            }

            if self.socketio:
                try:
                    # Broadcast to all analytics clients
                    self.socketio.emit("analytics_snapshot", broadcast_data, room="analytics:all")

                    logger.debug(f"[ANALYTICS] Broadcast snapshot with {len(metrics_snapshot)} metrics")
                except Exception as e:
                    logger.error(f"[ANALYTICS] Snapshot broadcast error: {e}")

    def subscribe_to_metric(self, metric_name: str, session_id: str) -> None:
        """Subscribe to metric updates."""
        self.subscriber.subscribe(metric_name, session_id)

    def unsubscribe_from_metric(self, metric_name: str, session_id: str) -> None:
        """Unsubscribe from metric."""
        self.subscriber.unsubscribe(metric_name, session_id)


class MetricsStreamer:
    """Handles real-time metrics streaming."""

    def __init__(self, broadcaster: WebSocketBroadcaster):
        """Initialize streamer."""
        self.broadcaster = broadcaster
        self.streaming = False
        self.streaming_thread: Optional[threading.Thread] = None
        self.streaming_lock = threading.Lock()

    def start_streaming(self, interval_sec: float = 1.0) -> None:
        """
        Start real-time metrics streaming.

        Args:
            interval_sec: Update interval in seconds
        """
        with self.streaming_lock:
            if self.streaming:
                return

            self.streaming = True
            self.streaming_thread = threading.Thread(
                target=self._stream_loop,
                args=(interval_sec,),
                daemon=True,
            )
            self.streaming_thread.start()

            logger.info(f"[ANALYTICS] Streaming started (interval: {interval_sec}s)")

    def stop_streaming(self) -> None:
        """Stop real-time metrics streaming."""
        with self.streaming_lock:
            self.streaming = False

            if self.streaming_thread:
                self.streaming_thread.join(timeout=5)

        logger.info("[ANALYTICS] Streaming stopped")

    def _stream_loop(self, interval_sec: float) -> None:
        """Main streaming loop."""
        from analytics_aggregator import get_aggregator

        aggregator = get_aggregator()

        while self.streaming:
            try:
                # Get current metrics
                snapshot = aggregator.get_metrics_snapshot()

                # Broadcast to all subscribers
                self.broadcaster.broadcast_metrics_snapshot(snapshot)

                # Sleep before next update
                time.sleep(interval_sec)

            except Exception as e:
                logger.error(f"[ANALYTICS] Stream loop error: {e}")
                time.sleep(interval_sec)


# Global broadcaster instance
_broadcaster: Optional[WebSocketBroadcaster] = None


def get_broadcaster() -> WebSocketBroadcaster:
    """Get singleton broadcaster."""
    global _broadcaster
    if _broadcaster is None:
        _broadcaster = WebSocketBroadcaster()
    return _broadcaster


def get_streamer(broadcaster: Optional[WebSocketBroadcaster] = None) -> MetricsStreamer:
    """Get metrics streamer."""
    if broadcaster is None:
        broadcaster = get_broadcaster()
    return MetricsStreamer(broadcaster)
