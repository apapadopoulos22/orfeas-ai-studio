#!/usr/bin/env python3
"""
Phase 4.7: Monitoring Test Suite
=================================

Comprehensive tests for all monitoring components.
Tests: Prometheus metrics, health checks, logging, endpoints.

Status: Production-Ready
Version: 1.0.0
Author: BOB AI v10.0
"""

import time
import unittest
import tempfile
import os
from datetime import datetime, timezone, timedelta

# Import modules to test
from phase4_prometheus_metrics import MetricsCollector, get_metrics_collector
from phase4_health_check import HealthChecker, get_health_checker
from phase4_logging import LoggingManager, configure_logging, get_logging_manager
from phase4_monitoring_app import create_monitoring_app


class TestMetricsCollector(unittest.TestCase):
    """Test MetricsCollector functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.metrics = MetricsCollector()

    def test_singleton_pattern(self):
        """Test metrics collector is singleton."""
        metrics1 = get_metrics_collector()
        metrics2 = get_metrics_collector()
        self.assertIs(metrics1, metrics2)

    def test_record_http_request(self):
        """Test HTTP request recording."""
        self.metrics.record_http_request('GET', '/api/test', 200, 25.5)

        self.assertEqual(self.metrics.http_requests_total['GET_/api/test'], 1)
        self.assertEqual(len(self.metrics.http_request_duration_ms['GET_/api/test']), 1)

    def test_cache_operations(self):
        """Test cache metrics."""
        self.metrics.record_cache_hit()
        self.metrics.record_cache_hit()
        self.metrics.record_cache_miss()

        self.assertEqual(self.metrics.cache_hits_total, 2)
        self.assertEqual(self.metrics.cache_misses_total, 1)
        self.assertAlmostEqual(self.metrics.get_cache_hit_rate(), 66.67, places=1)

    def test_auth_metrics(self):
        """Test authentication metrics."""
        self.metrics.record_auth_success()
        self.metrics.record_auth_success()
        self.metrics.record_auth_failure("invalid_key")

        self.assertEqual(self.metrics.auth_successes_total, 2)
        self.assertEqual(self.metrics.auth_failures_total, 1)
        self.assertAlmostEqual(self.metrics.get_auth_success_rate(), 66.67, places=1)

    def test_rate_limit_violation(self):
        """Test rate limit violation tracking."""
        self.metrics.record_rate_limit_violation()
        self.metrics.record_rate_limit_violation()

        self.assertEqual(self.metrics.rate_limit_violations_total, 2)

    def test_security_events(self):
        """Test security event tracking."""
        self.metrics.record_security_event('sql_injection', 'SELECT * FROM...')
        self.metrics.record_security_event('xss', 'script tag detected')

        self.assertEqual(self.metrics.sql_injection_attempts_total, 1)
        self.assertEqual(self.metrics.xss_attempts_total, 1)

    def test_cache_hit_rate(self):
        """Test cache hit rate calculation."""
        self.metrics.cache_hits_total = 80
        self.metrics.cache_misses_total = 20

        rate = self.metrics.get_cache_hit_rate()
        self.assertEqual(rate, 80.0)

    def test_percentile_calculation(self):
        """Test percentile calculation."""
        from collections import deque
        data = deque([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        p50 = self.metrics.get_percentile(data, 50)
        self.assertGreater(p50, 0)

    def test_endpoint_stats(self):
        """Test endpoint statistics."""
        self.metrics.record_http_request('GET', '/api/disciplines', 200, 10.0)
        self.metrics.record_http_request('GET', '/api/disciplines', 200, 15.0)
        self.metrics.record_http_request('GET', '/api/disciplines', 200, 20.0)

        stats = self.metrics.get_endpoint_stats('/api/disciplines')

        self.assertEqual(stats['count'], 3)
        self.assertEqual(stats['avg_duration_ms'], 15.0)
        self.assertGreater(stats['p95'], 0)

    def test_summary_stats(self):
        """Test comprehensive summary statistics."""
        self.metrics.record_http_request('GET', '/api/test', 200, 10.0)
        self.metrics.record_cache_hit()
        self.metrics.record_auth_success()

        summary = self.metrics.get_summary_stats()

        self.assertIn('system', summary)
        self.assertIn('http', summary)
        self.assertIn('cache', summary)
        self.assertIn('authentication', summary)
        self.assertEqual(summary['http']['total_requests'], 1)

    def test_prometheus_export(self):
        """Test Prometheus metrics export."""
        self.metrics.record_http_request('GET', '/api/test', 200, 10.0)

        prometheus_output = self.metrics.export_prometheus_metrics()

        self.assertIn('# HELP', prometheus_output)
        self.assertIn('# TYPE', prometheus_output)
        self.assertIn('http_requests_total', prometheus_output)

    def test_reset_metrics(self):
        """Test metrics reset."""
        self.metrics.record_http_request('GET', '/api/test', 200, 10.0)
        self.metrics.record_cache_hit()

        self.assertGreater(self.metrics.cache_hits_total, 0)

        self.metrics.reset_metrics()

        self.assertEqual(self.metrics.cache_hits_total, 0)
        self.assertEqual(len(self.metrics.http_requests_total), 0)


class TestHealthChecker(unittest.TestCase):
    """Test HealthChecker functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.health_checker = HealthChecker()

    def test_singleton_pattern(self):
        """Test health checker is singleton."""
        hc1 = get_health_checker()
        hc2 = get_health_checker()
        self.assertIs(hc1, hc2)

    def test_cpu_check(self):
        """Test CPU usage check."""
        is_healthy, info = self.health_checker.check_cpu_usage()

        self.assertIn('status', info)
        self.assertIn('usage_percent', info)
        self.assertIn('threshold_percent', info)
        self.assertGreaterEqual(info['usage_percent'], 0)
        self.assertLessEqual(info['usage_percent'], 100)

    def test_memory_check(self):
        """Test memory usage check."""
        is_healthy, info = self.health_checker.check_memory_usage()

        self.assertIn('status', info)
        self.assertIn('used_mb', info)
        self.assertIn('available_mb', info)
        self.assertIn('percent_used', info)

    def test_disk_check(self):
        """Test disk usage check."""
        is_healthy, info = self.health_checker.check_disk_usage()

        self.assertIn('status', info)
        self.assertIn('used_gb', info)
        self.assertIn('percent_used', info)

    def test_python_version_check(self):
        """Test Python version check."""
        is_healthy, info = self.health_checker.check_python_version()

        self.assertIn('status', info)
        self.assertIn('version', info)
        self.assertIn('required_version', info)

    def test_packages_check(self):
        """Test required packages check."""
        is_healthy, info = self.health_checker.check_required_packages()

        self.assertIn('status', info)
        self.assertIn('installed', info)
        self.assertIn('missing', info)

    def test_full_health_status(self):
        """Test full health status."""
        status = self.health_checker.get_full_health_status()

        self.assertIn('status', status)
        self.assertIn('timestamp', status)
        self.assertIn('uptime_seconds', status)
        self.assertIn('system', status)
        self.assertIn('environment', status)


class TestLoggingManager(unittest.TestCase):
    """Test LoggingManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.log_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.log_dir, 'test.log')
        self.manager = LoggingManager('test_logger')

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.log_dir):
            shutil.rmtree(self.log_dir)

    def test_singleton_pattern(self):
        """Test logging manager is singleton."""
        lm1 = get_logging_manager()
        lm2 = get_logging_manager()
        self.assertIs(lm1, lm2)

    def test_console_handler_setup(self):
        """Test console handler setup."""
        self.manager.setup_console_handler('INFO', use_json=False)
        self.assertIn('console', self.manager.handlers)

    def test_file_handler_setup(self):
        """Test file handler setup."""
        self.manager.setup_file_handler(self.log_file, 'DEBUG', use_json=False)
        self.assertIn('file', self.manager.handlers)
        self.assertTrue(os.path.exists(self.log_file))

    def test_log_levels(self):
        """Test different log levels."""
        self.manager.setup_file_handler(self.log_file, 'DEBUG', use_json=False)

        self.manager.debug("Debug message")
        self.manager.info("Info message")
        self.manager.warning("Warning message")
        self.manager.error("Error message")

        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file, 'r') as f:
            content = f.read()
            self.assertIn("Debug message", content)

    def test_log_with_context(self):
        """Test logging with context."""
        self.manager.setup_file_handler(self.log_file, 'DEBUG', use_json=True)

        self.manager.log_with_context('INFO', 'Test message',
                                     {'user_id': 123, 'action': 'test'})

        self.assertTrue(os.path.exists(self.log_file))

    def test_log_request(self):
        """Test request logging."""
        self.manager.setup_file_handler(self.log_file, 'DEBUG', use_json=False)

        self.manager.log_request('GET', '/api/test', 200, 25.5, 'user123')

        self.assertTrue(os.path.exists(self.log_file))

    def test_log_cache_operation(self):
        """Test cache operation logging."""
        self.manager.setup_file_handler(self.log_file, 'DEBUG', use_json=False)

        self.manager.log_cache_operation('get', 'test_key', True, 0.5)

        self.assertTrue(os.path.exists(self.log_file))

    def test_log_security_event(self):
        """Test security event logging."""
        self.manager.setup_file_handler(self.log_file, 'DEBUG', use_json=False)

        self.manager.log_security_event('sql_injection', 'SELECT * FROM...', '192.168.1.1')

        self.assertTrue(os.path.exists(self.log_file))

    def test_read_recent_logs(self):
        """Test reading recent logs."""
        self.manager.setup_file_handler(self.log_file, 'DEBUG', use_json=False)
        self.manager.info("Test log message")

        recent = self.manager.read_recent_logs(10)
        self.assertIsNotNone(recent)


class TestMonitoringApp(unittest.TestCase):
    """Test monitoring Flask app."""

    def setUp(self):
        """Set up test fixtures."""
        self.app = create_monitoring_app()
        self.client = self.app.test_client()

    def test_status_endpoint(self):
        """Test status endpoint."""
        response = self.client.get('/status')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'ok')

    def test_health_endpoint(self):
        """Test health endpoint."""
        response = self.client.get('/health')
        self.assertIn(response.status_code, [200, 503])

        data = response.get_json()
        self.assertIn('status', data)

    def test_metrics_endpoint(self):
        """Test metrics endpoint."""
        response = self.client.get('/metrics')
        self.assertEqual(response.status_code, 200)

        content = response.data.decode()
        self.assertIn('# HELP', content)
        self.assertIn('# TYPE', content)

    def test_metrics_summary_endpoint(self):
        """Test metrics summary endpoint."""
        response = self.client.get('/api/metrics/summary')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn('system', data)
        self.assertIn('http', data)

    def test_info_endpoint(self):
        """Test info endpoint."""
        response = self.client.get('/api/info')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn('project', data)
        self.assertIn('phase', data)

    def test_404_endpoint(self):
        """Test 404 handling."""
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_tests():
    """Run all tests."""
    # Create test suite
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMetricsCollector))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestHealthChecker))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLoggingManager))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMonitoringApp))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Pass rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
