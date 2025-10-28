#!/usr/bin/env python3
"""
Phase 4.7: Monitoring Application
==================================

Flask app with comprehensive monitoring and metrics endpoints.
Provides: Prometheus metrics, health checks, system stats, logging endpoints.

Status: Production-Ready
Version: 1.0.0
Author: BOB AI v10.0
"""

import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from flask import Flask, jsonify, request, Response

# Import monitoring modules
from phase4_prometheus_metrics import get_metrics_collector, MetricsCollector
from phase4_health_check import get_health_checker, HealthChecker, health_check_endpoint
from phase4_logging import configure_logging, get_logging_manager

# Setup logging
logging_manager = configure_logging(
    console_level='INFO',
    file_level='DEBUG',
    log_file='logs/monitoring.log'
)
logger = logging.getLogger(__name__)


def create_monitoring_app(config: Optional[Dict[str, Any]] = None) -> Flask:
    """
    Create Flask monitoring application.

    Args:
        config: Configuration dict with optional keys:
            - metrics_enabled: Enable Prometheus metrics endpoint
            - health_enabled: Enable health check endpoints
            - logging_enabled: Enable logging endpoints

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Default config
    if config is None:
        config = {}

    metrics_enabled = config.get('metrics_enabled', True)
    health_enabled = config.get('health_enabled', True)
    logging_enabled = config.get('logging_enabled', True)

    # Get singleton instances
    metrics = get_metrics_collector()
    health_checker = get_health_checker()

    # ========================================================================
    # PROMETHEUS METRICS ENDPOINTS
    # ========================================================================

    if metrics_enabled:
        @app.route('/metrics', methods=['GET'])
        def prometheus_metrics():
            """
            Prometheus metrics endpoint.

            Returns metrics in Prometheus text format for scraping.

            Example:
                curl http://localhost:8000/metrics
            """
            try:
                prometheus_output = metrics.export_prometheus_metrics()
                return Response(prometheus_output, mimetype='text/plain')
            except Exception as e:
                logger.error(f"[METRICS] Export failed: {e}")
                return jsonify({'error': str(e)}), 500

        @app.route('/api/metrics/summary', methods=['GET'])
        def metrics_summary():
            """
            Get comprehensive metrics summary.

            Returns:
                JSON with system, HTTP, cache, auth, rate limit, security metrics

            Example:
                curl http://localhost:8000/api/metrics/summary
            """
            try:
                summary = metrics.get_summary_stats()
                return jsonify(summary)
            except Exception as e:
                logger.error(f"[METRICS] Summary failed: {e}")
                return jsonify({'error': str(e)}), 500

        @app.route('/api/metrics/cache', methods=['GET'])
        def metrics_cache():
            """Get cache-specific metrics."""
            try:
                return jsonify({
                    'hits': metrics.cache_hits_total,
                    'misses': metrics.cache_misses_total,
                    'deletes': metrics.cache_deletes_total,
                    'hit_rate_percent': metrics.get_cache_hit_rate(),
                    'total_operations': metrics.cache_hits_total + metrics.cache_misses_total
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/metrics/auth', methods=['GET'])
        def metrics_auth():
            """Get authentication metrics."""
            try:
                return jsonify({
                    'successes': metrics.auth_successes_total,
                    'failures': metrics.auth_failures_total,
                    'success_rate_percent': metrics.get_auth_success_rate(),
                    'total_attempts': metrics.auth_successes_total + metrics.auth_failures_total
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/metrics/security', methods=['GET'])
        def metrics_security():
            """Get security event metrics."""
            try:
                return jsonify({
                    'sql_injection_attempts': metrics.sql_injection_attempts_total,
                    'xss_attempts': metrics.xss_attempts_total,
                    'rate_limit_violations': metrics.rate_limit_violations_total,
                    'total_security_events': (metrics.sql_injection_attempts_total +
                                             metrics.xss_attempts_total),
                    'recent_errors': metrics.get_recent_errors(10)
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/metrics/endpoints', methods=['GET'])
        def metrics_endpoints():
            """Get metrics for all tracked endpoints."""
            try:
                endpoints = []
                for endpoint in ['/api/disciplines', '/api/graph/search',
                               '/api/graph/pathfinding', '/api/statistics']:
                    endpoints.append(metrics.get_endpoint_stats(endpoint))

                return jsonify({
                    'endpoints': endpoints,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    # ========================================================================
    # HEALTH CHECK ENDPOINTS
    # ========================================================================

    if health_enabled:
        @app.route('/health', methods=['GET'])
        @app.route('/api/health', methods=['GET'])
        def health_basic():
            """
            Basic health check (public endpoint).

            Returns:
                {"status": "healthy|degraded", "uptime_seconds": int}

            Example:
                curl http://localhost:8000/health
            """
            try:
                status = health_checker.get_full_health_status(app=app, metrics=metrics)
                status_code = 200 if status['status'] == 'healthy' else 503
                return jsonify(status), status_code
            except Exception as e:
                logger.error(f"[HEALTH] Check failed: {e}")
                return jsonify({'status': 'error', 'error': str(e)}), 503

        @app.route('/api/health/full', methods=['GET'])
        def health_full():
            """
            Comprehensive health check with all details.

            Returns:
                JSON with system, environment, services, metrics

            Example:
                curl http://localhost:8000/api/health/full
            """
            try:
                status = health_checker.get_full_health_status(app=app, metrics=metrics)
                status_code = 200 if status['status'] == 'healthy' else 503
                return jsonify(status), status_code
            except Exception as e:
                logger.error(f"[HEALTH] Full check failed: {e}")
                return jsonify({'status': 'error', 'error': str(e)}), 503

        @app.route('/api/health/system', methods=['GET'])
        def health_system():
            """Get system resource health."""
            try:
                cpu_ok, cpu = health_checker.check_cpu_usage()
                mem_ok, mem = health_checker.check_memory_usage()
                disk_ok, disk = health_checker.check_disk_usage()

                return jsonify({
                    'status': 'healthy' if all([cpu_ok, mem_ok, disk_ok]) else 'warning',
                    'cpu': cpu,
                    'memory': mem,
                    'disk': disk
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/health/dependencies', methods=['GET'])
        def health_dependencies():
            """Get dependency health."""
            try:
                python_ok, python = health_checker.check_python_version()
                packages_ok, packages = health_checker.check_required_packages()
                redis_ok, redis = health_checker.check_redis_connection()

                return jsonify({
                    'status': 'healthy' if all([python_ok, packages_ok, redis_ok]) else 'warning',
                    'python': python,
                    'packages': packages,
                    'redis': redis
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    # ========================================================================
    # LOGGING ENDPOINTS
    # ========================================================================

    if logging_enabled:
        @app.route('/api/logs/recent', methods=['GET'])
        def logs_recent():
            """
            Get recent log entries.

            Query parameters:
                lines: Number of lines to return (default: 100)

            Example:
                curl "http://localhost:8000/api/logs/recent?lines=50"
            """
            try:
                lines = request.args.get('lines', 100, type=int)
                lines = max(10, min(lines, 1000))  # Clamp to 10-1000

                recent_logs = logging_manager.read_recent_logs(lines)

                return jsonify({
                    'lines_returned': len(recent_logs.split('\n')),
                    'logs': recent_logs
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/logs/stats', methods=['GET'])
        def logs_stats():
            """Get log file statistics."""
            try:
                stats = logging_manager.get_log_stats()
                return jsonify(stats)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/logs/errors', methods=['GET'])
        def logs_errors():
            """Get recent error logs."""
            try:
                errors = metrics.get_recent_errors(20)
                return jsonify({
                    'recent_errors': errors,
                    'total_tracked': len(metrics.recent_errors)
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    # ========================================================================
    # STATUS & INFO ENDPOINTS
    # ========================================================================

    @app.route('/status', methods=['GET'])
    @app.route('/api/status', methods=['GET'])
    def status():
        """
        Get system status.

        Returns:
            {"status": "ok", "version": "4.7", "timestamp": "..."}

        Example:
            curl http://localhost:8000/status
        """
        return jsonify({
            'status': 'ok',
            'version': '4.7',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'uptime_seconds': (datetime.now(timezone.utc) - health_checker.start_time).total_seconds()
        })

    @app.route('/api/info', methods=['GET'])
    def info():
        """Get system information."""
        return jsonify({
            'project': 'BOB AI v10.0',
            'phase': '4.7 - Production Monitoring',
            'endpoints': {
                'health': '/health',
                'metrics': '/metrics',
                'logs': '/api/logs/recent',
                'status': '/status'
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        })

    # ========================================================================
    # ERROR HANDLERS
    # ========================================================================

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"[ERROR] Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500

    # ========================================================================
    # STARTUP & SHUTDOWN
    # ========================================================================

    @app.before_request
    def before_request():
        """Track request metrics."""
        request.start_time = datetime.now(timezone.utc)
        metrics.increment_http_requests_in_progress()

    @app.after_request
    def after_request(response):
        """Track response metrics."""
        if hasattr(request, 'start_time'):
            duration = (datetime.now(timezone.utc) - request.start_time).total_seconds() * 1000

            # Record metrics
            metrics.record_http_request(
                method=request.method,
                path=request.path,
                status_code=response.status_code,
                duration_ms=duration,
                response_size=len(response.data) if response.data else 0
            )

        metrics.decrement_http_requests_in_progress()
        return response

    logger.info("[MONITORING] Monitoring app created successfully")
    return app


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Create monitoring app
    monitoring_app = create_monitoring_app()

    # Run on port 8000 (different from main API on 5000)
    monitoring_app.run(
        host='0.0.0.0',
        port=8000,
        debug=False,
        threaded=True
    )
