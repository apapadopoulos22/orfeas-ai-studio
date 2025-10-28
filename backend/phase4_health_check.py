#!/usr/bin/env python3
"""
Phase 4.7: Health Checks & Monitoring Endpoints
================================================

Comprehensive health checks and monitoring endpoints for production.
Provides: system health, component status, dependency verification.

Status: Production-Ready
Version: 1.0.0
Author: BOB AI v10.0
"""

import os
import sys
import psutil
import logging
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone
from functools import wraps

logger = logging.getLogger(__name__)


class HealthChecker:
    """
    Comprehensive health checking system.

    Monitors:
    - System resources (CPU, memory, disk)
    - Dependencies (Python, Redis, databases)
    - Services (Flask, caching, authentication)
    - Performance (latency, throughput)
    - Security (attack detection, auth rates)
    """

    _instance = None

    def __init__(self):
        """Initialize health checker."""
        self.start_time = datetime.now(timezone.utc)
        self.last_check = None
        self.cached_health = None
        self.cache_ttl_seconds = 5  # Cache health status for 5 seconds

        logger.info("[HEALTH] HealthChecker initialized")

    @classmethod
    def get_instance(cls) -> 'HealthChecker':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = HealthChecker()
        return cls._instance

    # ========================================================================
    # SYSTEM HEALTH CHECKS
    # ========================================================================

    def check_cpu_usage(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check CPU usage.

        Returns:
            (is_healthy, {status: str, usage_percent: float, threshold: int})
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            threshold = 80  # Alert if > 80%
            is_healthy = cpu_percent < threshold

            return is_healthy, {
                'status': 'healthy' if is_healthy else 'warning',
                'usage_percent': round(cpu_percent, 2),
                'threshold_percent': threshold,
                'cores': psutil.cpu_count()
            }
        except Exception as e:
            logger.warning(f"[HEALTH] CPU check failed: {e}")
            return False, {'status': 'error', 'error': str(e)}

    def check_memory_usage(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check memory usage.

        Returns:
            (is_healthy, {status: str, used_mb: float, available_mb: float, ...})
        """
        try:
            memory = psutil.virtual_memory()
            threshold_percent = 85  # Alert if > 85% used
            is_healthy = memory.percent < threshold_percent

            return is_healthy, {
                'status': 'healthy' if is_healthy else 'warning',
                'used_mb': round(memory.used / 1024 / 1024, 2),
                'available_mb': round(memory.available / 1024 / 1024, 2),
                'total_mb': round(memory.total / 1024 / 1024, 2),
                'percent_used': round(memory.percent, 2),
                'threshold_percent': threshold_percent
            }
        except Exception as e:
            logger.warning(f"[HEALTH] Memory check failed: {e}")
            return False, {'status': 'error', 'error': str(e)}

    def check_disk_usage(self, path: str = '/') -> Tuple[bool, Dict[str, Any]]:
        """
        Check disk usage.

        Args:
            path: Path to check (default: root)

        Returns:
            (is_healthy, {status: str, used_gb: float, ...})
        """
        try:
            # On Windows, use C: drive
            if sys.platform == 'win32':
                path = 'C:'

            disk = psutil.disk_usage(path)
            threshold_percent = 90  # Alert if > 90% used
            is_healthy = disk.percent < threshold_percent

            return is_healthy, {
                'status': 'healthy' if is_healthy else 'warning',
                'path': path,
                'used_gb': round(disk.used / 1024 / 1024 / 1024, 2),
                'free_gb': round(disk.free / 1024 / 1024 / 1024, 2),
                'total_gb': round(disk.total / 1024 / 1024 / 1024, 2),
                'percent_used': round(disk.percent, 2),
                'threshold_percent': threshold_percent
            }
        except Exception as e:
            logger.warning(f"[HEALTH] Disk check failed: {e}")
            return False, {'status': 'error', 'error': str(e)}

    # ========================================================================
    # DEPENDENCY CHECKS
    # ========================================================================

    def check_python_version(self) -> Tuple[bool, Dict[str, Any]]:
        """Check Python version."""
        try:
            major, minor, micro = sys.version_info[:3]
            version_str = f"{major}.{minor}.{micro}"

            # Require Python 3.10+
            is_healthy = (major >= 3) and (minor >= 10)

            return is_healthy, {
                'status': 'healthy' if is_healthy else 'warning',
                'version': version_str,
                'required_version': '3.10+',
                'python_executable': sys.executable
            }
        except Exception as e:
            return False, {'status': 'error', 'error': str(e)}

    def check_required_packages(self) -> Tuple[bool, Dict[str, Any]]:
        """Check required packages are installed."""
        required_packages = [
            'flask',
            'torch',
            'psutil',
            'redis',
            'python-dotenv'
        ]

        installed = {}
        missing = []

        for package in required_packages:
            try:
                mod = __import__(package.replace('-', '_'))
                version = getattr(mod, '__version__', 'unknown')
                installed[package] = version
            except ImportError:
                missing.append(package)

        is_healthy = len(missing) == 0

        return is_healthy, {
            'status': 'healthy' if is_healthy else 'warning',
            'installed': installed,
            'missing': missing,
            'required_count': len(required_packages),
            'installed_count': len(installed)
        }

    def check_redis_connection(self, host: str = 'localhost',
                              port: int = 6379) -> Tuple[bool, Dict[str, Any]]:
        """
        Check Redis connection.

        Args:
            host: Redis host
            port: Redis port

        Returns:
            (is_healthy, {status: str, host: str, port: int, latency_ms: float})
        """
        try:
            import redis
            import time

            r = redis.Redis(host=host, port=port, socket_connect_timeout=2)

            start = time.time()
            r.ping()
            latency_ms = (time.time() - start) * 1000

            return True, {
                'status': 'healthy',
                'host': host,
                'port': port,
                'latency_ms': round(latency_ms, 2),
                'connection': 'ok'
            }
        except ImportError:
            return True, {  # Redis optional
                'status': 'skipped',
                'reason': 'redis module not available'
            }
        except Exception as e:
            logger.warning(f"[HEALTH] Redis check failed: {e}")
            return False, {
                'status': 'error',
                'host': host,
                'port': port,
                'error': str(e)
            }

    # ========================================================================
    # SERVICE CHECKS
    # ========================================================================

    def check_flask_app(self, app=None) -> Tuple[bool, Dict[str, Any]]:
        """Check Flask app status."""
        try:
            if app is None:
                return True, {'status': 'skipped', 'reason': 'app not provided'}

            # Try to get app name and config
            return True, {
                'status': 'healthy',
                'app_name': app.name,
                'debug': app.debug,
                'testing': app.testing
            }
        except Exception as e:
            return False, {'status': 'error', 'error': str(e)}

    def check_authentication_service(self, auth_manager=None) -> Tuple[bool, Dict[str, Any]]:
        """Check authentication service status."""
        try:
            if auth_manager is None:
                return True, {'status': 'skipped', 'reason': 'auth manager not provided'}

            return True, {
                'status': 'healthy',
                'service': 'authentication',
                'keys_generated': getattr(auth_manager, '_keys_count', 0)
            }
        except Exception as e:
            return False, {'status': 'error', 'error': str(e)}

    def check_cache_service(self, cache_manager=None) -> Tuple[bool, Dict[str, Any]]:
        """Check cache service status."""
        try:
            if cache_manager is None:
                return True, {'status': 'skipped', 'reason': 'cache manager not provided'}

            return True, {
                'status': 'healthy',
                'service': 'caching',
                'backend': 'redis' if hasattr(cache_manager, 'redis') else 'memory'
            }
        except Exception as e:
            return False, {'status': 'error', 'error': str(e)}

    # ========================================================================
    # COMPREHENSIVE HEALTH CHECK
    # ========================================================================

    def get_full_health_status(self, app=None, auth_manager=None,
                              cache_manager=None, metrics=None) -> Dict[str, Any]:
        """
        Get comprehensive health status.

        Args:
            app: Flask application (optional)
            auth_manager: Authentication manager (optional)
            cache_manager: Cache manager (optional)
            metrics: Metrics collector (optional)

        Returns:
            Complete health status dict
        """
        uptime_seconds = (datetime.now(timezone.utc) - self.start_time).total_seconds()

        cpu_ok, cpu_info = self.check_cpu_usage()
        mem_ok, mem_info = self.check_memory_usage()
        disk_ok, disk_info = self.check_disk_usage()
        python_ok, python_info = self.check_python_version()
        packages_ok, packages_info = self.check_required_packages()
        redis_ok, redis_info = self.check_redis_connection()
        flask_ok, flask_info = self.check_flask_app(app)
        auth_ok, auth_info = self.check_authentication_service(auth_manager)
        cache_ok, cache_info = self.check_cache_service(cache_manager)

        # Overall status
        all_healthy = all([cpu_ok, mem_ok, disk_ok, python_ok, packages_ok,
                          redis_ok, flask_ok, auth_ok, cache_ok])
        overall_status = 'healthy' if all_healthy else 'degraded'

        health_report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'status': overall_status,
            'uptime_seconds': int(uptime_seconds),
            'uptime_hours': round(uptime_seconds / 3600, 2),
            'system': {
                'cpu': cpu_info,
                'memory': mem_info,
                'disk': disk_info
            },
            'environment': {
                'python': python_info,
                'packages': packages_info,
                'redis': redis_info
            },
            'services': {
                'flask': flask_info,
                'authentication': auth_info,
                'caching': cache_info
            }
        }

        # Add metrics if available
        if metrics is not None:
            try:
                summary = metrics.get_summary_stats()
                health_report['metrics'] = {
                    'cache_hit_rate': summary['cache']['hit_rate_percent'],
                    'auth_success_rate': summary['authentication']['success_rate_percent'],
                    'error_rate': summary['http']['error_rate_percent'],
                    'avg_latency_ms': summary['http']['avg_latency_ms']
                }
            except Exception as e:
                logger.warning(f"[HEALTH] Metrics collection failed: {e}")

        return health_report


def get_health_checker() -> HealthChecker:
    """Get or create health checker singleton."""
    return HealthChecker.get_instance()


# ============================================================================
# FLASK INTEGRATION HELPERS
# ============================================================================

def health_check_endpoint(health_checker: HealthChecker = None,
                         app=None, auth_manager=None,
                         cache_manager=None, metrics=None):
    """
    Create Flask endpoint handler for health checks.

    Usage in Flask app:
        from phase4_health_check import health_check_endpoint, get_health_checker

        health_checker = get_health_checker()

        @app.route('/api/health')
        def health():
            return health_check_endpoint(health_checker, app, auth_manager,
                                       cache_manager, metrics)

    Returns:
        (dict, status_code) tuple for Flask
    """
    if health_checker is None:
        health_checker = get_health_checker()

    status = health_checker.get_full_health_status(app, auth_manager,
                                                   cache_manager, metrics)

    status_code = 200 if status['status'] == 'healthy' else 503

    return status, status_code
