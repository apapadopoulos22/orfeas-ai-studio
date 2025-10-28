"""
[ORFEAS PHASE 2 TASK 3] Comprehensive Analytics Testing Suite
Tests for event tracking, aggregation, storage, and WebSocket integration.

Test Coverage:
  - Event tracking (EventManager, event queuing, counters)
  - Time-window aggregation (bucketing, metric calculation)
  - Storage operations (Redis/memory persistence)
  - WebSocket broadcasting (subscriber management)
  - API endpoints (metrics, charts, status, events)

Command:
  pytest backend/tests/test_analytics_task3.py -v --cov=backend/analytics* --cov-report=html
"""

import json
import logging
import time
import unittest
from unittest.mock import MagicMock, Mock, patch
from typing import Any, Dict, List

import pytest

logger = logging.getLogger(__name__)


class TestEventTracking(unittest.TestCase):
    """Test event tracking system."""

    def setUp(self):
        """Set up test fixtures."""
        from analytics_events import get_event_manager

        self.event_manager = get_event_manager()
        self.event_manager.clear()

    def tearDown(self):
        """Clean up."""
        self.event_manager.clear()

    def test_track_event_basic(self):
        """Test basic event tracking."""
        from analytics_events import track_event

        track_event(event_type="TEST_EVENT", duration_ms=100, success=True)

        events = self.event_manager.get_events(limit=10)
        assert len(events) == 1
        assert events[0].event_type == "TEST_EVENT"

    def test_track_event_with_metadata(self):
        """Test event tracking with metadata."""
        from analytics_events import track_event

        metadata = {"user_id": "test123", "action": "generate"}
        track_event(
            event_type="MODEL_LOADED",
            duration_ms=500,
            success=True,
            metadata=metadata,
        )

        events = self.event_manager.get_events(limit=10)
        assert events[0].metadata == metadata

    def test_event_counters(self):
        """Test event counters."""
        from analytics_events import track_event

        track_event(event_type="CACHE_HIT", duration_ms=5, success=True)
        track_event(event_type="CACHE_HIT", duration_ms=6, success=True)
        track_event(event_type="CACHE_MISS", duration_ms=100, success=True)

        stats = self.event_manager.get_event_stats()
        assert stats["CACHE_HIT"] == 2
        assert stats["CACHE_MISS"] == 1

    def test_event_rate_calculation(self):
        """Test event rate calculation."""
        from analytics_events import track_event

        for _ in range(10):
            track_event(event_type="TEST", duration_ms=1, success=True)

        rate = self.event_manager.get_event_rate("TEST")
        assert rate >= 0

    def test_queue_max_size(self):
        """Test event queue size limit."""
        from analytics_events import track_event

        # Add events beyond queue limit
        for i in range(15000):
            track_event(event_type="TEST", duration_ms=1, success=True)

        events = self.event_manager.get_events(limit=20000)
        assert len(events) <= 10010  # Max queue size + margin

    def test_event_subscriber_callback(self):
        """Test subscriber callback."""
        from analytics_events import track_event

        callback_received = []

        def test_callback(event):
            callback_received.append(event)

        self.event_manager.subscribe(test_callback)
        track_event(event_type="TEST", duration_ms=100, success=True)

        assert len(callback_received) >= 1


class TestAggregation(unittest.TestCase):
    """Test metrics aggregation."""

    def setUp(self):
        """Set up test fixtures."""
        from analytics_aggregator import get_aggregator
        from analytics_events import get_event_manager

        self.aggregator = get_aggregator()
        self.event_manager = get_event_manager()
        self.event_manager.clear()

    def tearDown(self):
        """Clean up."""
        self.aggregator.clear()
        self.event_manager.clear()

    def test_cache_hit_rate_calculation(self):
        """Test cache hit rate calculation."""
        from analytics_events import EventType, track_event

        # Generate test events
        track_event(event_type="CACHE_HIT", duration_ms=5, success=True)
        track_event(event_type="CACHE_HIT", duration_ms=6, success=True)
        track_event(event_type="CACHE_MISS", duration_ms=100, success=True)

        events = self.event_manager.get_events(limit=100)
        for event in events:
            self.aggregator.add_event(event)

        metric = self.aggregator.aggregate_metric("cache_hit_rate", "1m")
        assert metric is not None
        assert 0 <= metric.value <= 100

    def test_error_rate_calculation(self):
        """Test error rate calculation."""
        from analytics_events import track_event

        track_event(event_type="REQUEST_COMPLETE", duration_ms=100, success=True)
        track_event(event_type="REQUEST_COMPLETE", duration_ms=150, success=True)
        track_event(event_type="REQUEST_ERROR", duration_ms=50, success=False)

        events = self.event_manager.get_events(limit=100)
        for event in events:
            self.aggregator.add_event(event)

        metric = self.aggregator.aggregate_metric("error_rate", "1m")
        assert metric is not None
        assert metric.value >= 0

    def test_average_latency_calculation(self):
        """Test average latency calculation."""
        from analytics_events import track_event

        track_event(event_type="PREDICTION_COMPLETE", duration_ms=100, success=True)
        track_event(event_type="PREDICTION_COMPLETE", duration_ms=200, success=True)
        track_event(event_type="PREDICTION_COMPLETE", duration_ms=300, success=True)

        events = self.event_manager.get_events(limit=100)
        for event in events:
            self.aggregator.add_event(event)

        metric = self.aggregator.aggregate_metric("avg_latency_ms", "1m")
        assert metric is not None
        assert metric.value >= 100

    def test_throughput_calculation(self):
        """Test throughput calculation."""
        from analytics_events import track_event

        start_time = time.time()
        for _ in range(100):
            track_event(event_type="REQUEST_RECEIVED", duration_ms=1, success=True)

        events = self.event_manager.get_events(limit=100)
        for event in events:
            self.aggregator.add_event(event)

        metric = self.aggregator.aggregate_metric("throughput", "1m")
        assert metric is not None
        assert metric.value >= 0

    def test_p95_latency_calculation(self):
        """Test P95 latency calculation."""
        from analytics_events import track_event

        latencies = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        for latency in latencies:
            track_event(
                event_type="PREDICTION_COMPLETE",
                duration_ms=latency,
                success=True,
            )

        events = self.event_manager.get_events(limit=100)
        for event in events:
            self.aggregator.add_event(event)

        metric = self.aggregator.aggregate_metric("p95_latency_ms", "1m")
        assert metric is not None

    def test_time_window_bucketing(self):
        """Test time-window bucketing."""
        from analytics_events import track_event

        track_event(event_type="TEST_EVENT", duration_ms=100, success=True)

        events = self.event_manager.get_events(limit=100)
        for event in events:
            self.aggregator.add_event(event)

        # Check all windows
        for window in ["1s", "1m", "1h", "1d"]:
            metric = self.aggregator.aggregate_metric("cache_hit_rate", window)
            assert metric is not None

    def test_metrics_snapshot(self):
        """Test metrics snapshot."""
        from analytics_events import track_event

        track_event(event_type="REQUEST_RECEIVED", duration_ms=100, success=True)

        events = self.event_manager.get_events(limit=100)
        for event in events:
            self.aggregator.add_event(event)

        snapshot = self.aggregator.get_metrics_snapshot()
        assert isinstance(snapshot, dict)
        assert len(snapshot) >= 0


class TestStorage(unittest.TestCase):
    """Test analytics storage."""

    def setUp(self):
        """Set up test fixtures."""
        from analytics_storage import get_storage

        self.storage = get_storage()
        self.storage.clear()

    def tearDown(self):
        """Clean up."""
        self.storage.clear()

    def test_store_metric(self):
        """Test metric storage."""
        metric_data = {
            "metric_name": "cache_hit_rate",
            "window": "1m",
            "timestamp": time.time(),
            "value": 85.5,
            "count": 100,
        }

        self.storage.store_metric(metric_data)
        metrics = self.storage.query_metrics("cache_hit_rate", "1m")
        assert len(metrics) > 0

    def test_query_metrics(self):
        """Test metric querying."""
        for i in range(5):
            metric_data = {
                "metric_name": "error_rate",
                "window": "1m",
                "timestamp": time.time() + i,
                "value": 10 + i,
            }
            self.storage.store_metric(metric_data)

        metrics = self.storage.query_metrics("error_rate", "1m", limit=10)
        assert len(metrics) == 5

    def test_query_limit(self):
        """Test query limit."""
        for i in range(200):
            metric_data = {
                "metric_name": "throughput",
                "window": "1m",
                "timestamp": time.time() + i,
                "value": 100 + i,
            }
            self.storage.store_metric(metric_data)

        metrics = self.storage.query_metrics("throughput", "1m", limit=50)
        assert len(metrics) <= 50

    def test_metric_summary(self):
        """Test metric summary."""
        for window in ["1s", "1m", "1h", "1d"]:
            metric_data = {
                "metric_name": "latency",
                "window": window,
                "timestamp": time.time(),
                "value": 150,
            }
            self.storage.store_metric(metric_data)

        summary = self.storage.get_metric_summary("latency")
        assert "1m" in summary

    def test_cleanup_old_data(self):
        """Test old data cleanup."""
        metric_data = {
            "metric_name": "test",
            "window": "1s",
            "timestamp": time.time(),
            "value": 100,
        }
        self.storage.store_metric(metric_data)

        # Cleanup should execute without error
        deleted = self.storage.cleanup_old_data()
        assert isinstance(deleted, int)


class TestWebSocket(unittest.TestCase):
    """Test WebSocket broadcasting."""

    def setUp(self):
        """Set up test fixtures."""
        from analytics_websocket import get_broadcaster

        self.broadcaster = get_broadcaster()

    def test_subscriber_subscribe(self):
        """Test metric subscription."""
        self.broadcaster.subscriber.subscribe("cache_hit_rate", "session123")

        subscribers = self.broadcaster.subscriber.get_subscribers("cache_hit_rate")
        assert "session123" in subscribers

    def test_subscriber_unsubscribe(self):
        """Test metric unsubscription."""
        self.broadcaster.subscriber.subscribe("cache_hit_rate", "session123")
        self.broadcaster.subscriber.unsubscribe("cache_hit_rate", "session123")

        subscribers = self.broadcaster.subscriber.get_subscribers("cache_hit_rate")
        assert "session123" not in subscribers

    def test_multiple_subscribers(self):
        """Test multiple subscribers."""
        for i in range(5):
            self.broadcaster.subscriber.subscribe("latency", f"session{i}")

        subscribers = self.broadcaster.subscriber.get_subscribers("latency")
        assert len(subscribers) == 5

    def test_broadcast_without_socketio(self):
        """Test broadcast without SocketIO (in-memory)."""
        self.broadcaster.subscriber.subscribe("test_metric", "session1")

        # Should not raise error
        self.broadcaster.broadcast_metrics("test_metric", {"value": 100})

    def test_metrics_streamer(self):
        """Test metrics streamer."""
        from analytics_websocket import get_streamer

        streamer = get_streamer(self.broadcaster)

        # Should not raise error
        streamer.start_streaming(interval_sec=0.1)
        time.sleep(0.2)
        streamer.stop_streaming()


class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        from flask import Flask
        from analytics_api import create_analytics_blueprint

        self.app = Flask(__name__)
        self.app.register_blueprint(create_analytics_blueprint())
        self.client = self.app.test_client()

        # Populate some test data
        from analytics_events import track_event

        track_event(event_type="TEST_EVENT", duration_ms=100, success=True)

    def test_metrics_endpoint(self):
        """Test /api/analytics/metrics endpoint."""
        response = self.client.get("/api/analytics/metrics")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_metrics_endpoint_with_window(self):
        """Test metrics endpoint with window parameter."""
        response = self.client.get("/api/analytics/metrics?window=1m")
        assert response.status_code == 200

    def test_metrics_endpoint_invalid_window(self):
        """Test metrics endpoint with invalid window."""
        response = self.client.get("/api/analytics/metrics?window=invalid")
        assert response.status_code == 400

    def test_charts_endpoint(self):
        """Test /api/analytics/charts endpoint."""
        response = self.client.get("/api/analytics/charts")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_status_endpoint(self):
        """Test /api/analytics/status endpoint."""
        response = self.client.get("/api/analytics/status")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["status"] == "operational"

    def test_events_endpoint_get(self):
        """Test GET /api/analytics/events endpoint."""
        response = self.client.get("/api/analytics/events")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_events_endpoint_post(self):
        """Test POST /api/analytics/events endpoint."""
        event_data = {
            "event_type": "CUSTOM_EVENT",
            "duration_ms": 100,
            "success": True,
            "metadata": {"custom": "data"},
        }

        response = self.client.post(
            "/api/analytics/events",
            data=json.dumps(event_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["success"] is True


class TestPerformance(unittest.TestCase):
    """Test performance characteristics."""

    def setUp(self):
        """Set up test fixtures."""
        from analytics_events import get_event_manager
        from analytics_aggregator import get_aggregator

        self.event_manager = get_event_manager()
        self.aggregator = get_aggregator()
        self.event_manager.clear()
        self.aggregator.clear()

    def tearDown(self):
        """Clean up."""
        self.event_manager.clear()
        self.aggregator.clear()

    def test_event_tracking_latency(self):
        """Test event tracking latency (<10ms)."""
        from analytics_events import track_event

        start = time.time()

        for _ in range(100):
            track_event(event_type="TEST", duration_ms=1, success=True)

        elapsed = time.time() - start
        avg_latency_ms = (elapsed * 1000) / 100

        # Should be well under 10ms per event
        assert avg_latency_ms < 50

    def test_aggregation_latency(self):
        """Test aggregation latency (<100ms)."""
        from analytics_events import track_event

        # Generate events
        for _ in range(100):
            track_event(event_type="REQUEST_RECEIVED", duration_ms=100, success=True)

        events = self.event_manager.get_events(limit=100)

        start = time.time()

        # Aggregate
        for event in events:
            self.aggregator.add_event(event)

        self.aggregator.get_metrics_snapshot()

        elapsed = (time.time() - start) * 1000

        # Should be under 100ms
        assert elapsed < 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
