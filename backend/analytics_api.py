"""
[ORFEAS PHASE 2 TASK 3] Analytics API Endpoints
Dashboard API for retrieving and managing analytics.

Purpose:
  Provides REST endpoints for dashboard queries.
  Exposes metrics, status, and event data.
  Supports custom event recording.

API Endpoints:
  GET  /api/analytics/metrics    - Get aggregated metrics
  GET  /api/analytics/charts     - Get chart data
  GET  /api/analytics/status     - System status
  GET  /api/analytics/events     - Event history
  POST /api/analytics/events     - Record custom event

Usage:
  from analytics_api import register_analytics_routes
  register_analytics_routes(app)
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)

# Lazy imports to avoid circular dependencies
analytics_events_bp: Optional[Blueprint] = None


def create_analytics_blueprint() -> Blueprint:
    """Create Flask blueprint for analytics routes."""
    bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

    @bp.route("/metrics", methods=["GET"])
    def get_metrics() -> Tuple[Dict[str, Any], int]:
        """
        Get current aggregated metrics.

        Query params:
          - window: Time window (1s, 1m, 1h, 1d)
          - metric: Specific metric (cache_hit_rate, error_rate, etc.)

        Returns:
            JSON with metrics data
        """
        try:
            from analytics_aggregator import get_aggregator
            from analytics_storage import get_storage

            aggregator = get_aggregator()
            storage = get_storage()

            window = request.args.get("window", "1m")
            metric_name = request.args.get("metric", None)

            # Validate window
            if window not in ["1s", "1m", "1h", "1d"]:
                return jsonify({"error": "Invalid window"}), 400

            # Get metrics
            if metric_name:
                # Get specific metric
                metrics = storage.query_metrics(metric_name, window, limit=100)
            else:
                # Get all current metrics
                metrics_snapshot = aggregator.get_metrics_snapshot()
                metrics = [
                    {"metric_name": k, "value": v.get("value"), "timestamp": time.time()}
                    for k, v in metrics_snapshot.items()
                ]

            return jsonify(
                {
                    "success": True,
                    "window": window,
                    "count": len(metrics),
                    "metrics": metrics,
                }
            ), 200

        except Exception as e:
            logger.error(f"[ANALYTICS] Metrics endpoint error: {e}")
            return jsonify({"error": str(e)}), 500

    @bp.route("/charts", methods=["GET"])
    def get_charts() -> Tuple[Dict[str, Any], int]:
        """
        Get chart data for dashboard.

        Query params:
          - metric: Metric name
          - window: Time window (1m, 1h, 1d)
          - limit: Number of data points (default 100)

        Returns:
            JSON with time-series data
        """
        try:
            from analytics_storage import get_storage

            storage = get_storage()

            metric_name = request.args.get("metric", "cache_hit_rate")
            window = request.args.get("window", "1m")
            limit = int(request.args.get("limit", "100"))

            # Validate
            if limit > 1000:
                limit = 1000

            # Get metrics
            metrics = storage.query_metrics(metric_name, window, limit=limit)

            # Format for chart
            chart_data = {
                "metric": metric_name,
                "window": window,
                "points": [
                    {
                        "timestamp": m.get("timestamp"),
                        "value": m.get("value"),
                        "count": m.get("count"),
                        "min": m.get("min_val"),
                        "max": m.get("max_val"),
                        "avg": m.get("value"),
                    }
                    for m in metrics
                ],
            }

            return jsonify(
                {
                    "success": True,
                    "count": len(metrics),
                    "data": chart_data,
                }
            ), 200

        except Exception as e:
            logger.error(f"[ANALYTICS] Charts endpoint error: {e}")
            return jsonify({"error": str(e)}), 500

    @bp.route("/status", methods=["GET"])
    def get_status() -> Tuple[Dict[str, Any], int]:
        """
        Get analytics system status.

        Returns:
            JSON with system information
        """
        try:
            from analytics_aggregator import get_aggregator
            from analytics_events import get_event_manager
            from analytics_storage import get_storage

            aggregator = get_aggregator()
            event_manager = get_event_manager()
            storage = get_storage()

            # Get current metrics
            metrics_snapshot = aggregator.get_metrics_snapshot()

            # Get event statistics
            event_stats = event_manager.get_event_stats()

            # Prepare response
            status_data = {
                "timestamp": time.time(),
                "event_count": event_stats.get("total_events", 0),
                "event_rate": event_manager.get_event_rate(),
                "metrics": metrics_snapshot,
                "storage": {
                    "backend": "redis" if storage.use_redis else "memory",
                    "retention_policies": storage.retention_policies,
                },
                "system": {
                    "uptime_seconds": 0,  # Would need to be tracked separately
                    "memory_usage": "unknown",  # Would need to be tracked separately
                },
            }

            return jsonify(
                {
                    "success": True,
                    "status": "operational",
                    "data": status_data,
                }
            ), 200

        except Exception as e:
            logger.error(f"[ANALYTICS] Status endpoint error: {e}")
            return jsonify({"error": str(e)}), 500

    @bp.route("/events", methods=["GET"])
    def get_events() -> Tuple[Dict[str, Any], int]:
        """
        Get recent events.

        Query params:
          - event_type: Filter by event type
          - limit: Number of events (default 100)

        Returns:
            JSON with recent events
        """
        try:
            from analytics_events import get_event_manager

            event_manager = get_event_manager()

            event_type = request.args.get("event_type", None)
            limit = int(request.args.get("limit", "100"))

            if limit > 1000:
                limit = 1000

            # Get events
            events = event_manager.get_events(limit=limit)

            # Filter by type if specified
            if event_type:
                events = [e for e in events if e.get("event_type") == event_type]

            return jsonify(
                {
                    "success": True,
                    "count": len(events),
                    "events": events,
                }
            ), 200

        except Exception as e:
            logger.error(f"[ANALYTICS] Events endpoint error: {e}")
            return jsonify({"error": str(e)}), 500

    @bp.route("/events", methods=["POST"])
    def record_event() -> Tuple[Dict[str, Any], int]:
        """
        Record custom event.

        POST body:
            {
                "event_type": "USER_CUSTOM_EVENT",
                "duration_ms": 1000,
                "success": true,
                "metadata": {"key": "value"}
            }

        Returns:
            JSON confirmation
        """
        try:
            from analytics_events import get_event_manager, track_event

            data = request.get_json() or {}

            event_type = data.get("event_type", "USER_EVENT")
            duration_ms = data.get("duration_ms", 0)
            success = data.get("success", True)
            metadata = data.get("metadata", {})

            # Record event
            track_event(
                event_type=event_type,
                duration_ms=duration_ms,
                success=success,
                metadata=metadata,
            )

            return jsonify(
                {
                    "success": True,
                    "message": f"Event {event_type} recorded",
                }
            ), 201

        except Exception as e:
            logger.error(f"[ANALYTICS] Record event error: {e}")
            return jsonify({"error": str(e)}), 500

    return bp


def register_analytics_routes(app: Any) -> None:
    """
    Register analytics routes with Flask app.

    Args:
        app: Flask application instance
    """
    bp = create_analytics_blueprint()
    app.register_blueprint(bp)
    logger.info("[ANALYTICS] API routes registered")
