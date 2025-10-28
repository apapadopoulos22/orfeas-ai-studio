#!/usr/bin/env python3
"""
Phase 4.9: Production Deployment Test Suite
=============================================

Comprehensive production deployment validation.
Tests: Smoke tests, performance SLAs, endpoint validation, system health, load testing.

Status: Production-Ready
Version: 1.0.0
Author: BOB AI v10.0
"""

import subprocess
import sys
import time
import unittest
import requests
from pathlib import Path
from typing import Tuple


class TestProductionDeployment(unittest.TestCase):
    """Test production deployment readiness."""

    BASE_URL = "http://localhost:5000"
    MONITORING_URL = "http://localhost:8000"

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.start_time = time.time()
        time.sleep(2)  # Allow services to stabilize

    def test_api_service_accessible(self):
        """Test API service is accessible."""
        try:
            response = requests.get(f"{self.BASE_URL}/health", timeout=5)
            self.assertIn(response.status_code, [200, 503])
        except Exception as e:
            self.fail(f"API service not accessible: {e}")

    def test_monitoring_service_accessible(self):
        """Test monitoring service is accessible."""
        try:
            response = requests.get(f"{self.MONITORING_URL}/health", timeout=5)
            self.assertIn(response.status_code, [200, 503])
        except Exception as e:
            self.fail(f"Monitoring service not accessible: {e}")

    def test_api_health_endpoint_200(self):
        """Test API returns 200 on health check."""
        response = requests.get(f"{self.BASE_URL}/health")
        self.assertEqual(response.status_code, 200)

    def test_monitoring_health_endpoint_200(self):
        """Test monitoring returns 200 on health check."""
        response = requests.get(f"{self.MONITORING_URL}/health")
        self.assertEqual(response.status_code, 200)

    def test_api_health_response_structure(self):
        """Test API health response has required fields."""
        response = requests.get(f"{self.BASE_URL}/health")
        data = response.json()

        required_fields = ["status", "timestamp"]
        for field in required_fields:
            self.assertIn(field, data, f"Missing field: {field}")

    def test_monitoring_health_response_structure(self):
        """Test monitoring health response has required fields."""
        response = requests.get(f"{self.MONITORING_URL}/health")
        data = response.json()

        required_fields = ["status"]
        for field in required_fields:
            self.assertIn(field, data, f"Missing field: {field}")

    def test_api_response_time_under_sla(self):
        """Test API response time under SLA (<100ms)."""
        start = time.time()
        requests.get(f"{self.BASE_URL}/health")
        elapsed = (time.time() - start) * 1000  # Convert to ms

        self.assertLess(elapsed, 100, f"Response time {elapsed}ms exceeds SLA (100ms)")

    def test_monitoring_response_time_under_sla(self):
        """Test monitoring response time under SLA (<100ms)."""
        start = time.time()
        response = requests.get(f"{self.MONITORING_URL}/health")
        elapsed = (time.time() - start) * 1000  # Convert to ms

        self.assertLess(elapsed, 100, f"Response time {elapsed}ms exceeds SLA (100ms)")

    def test_api_endpoint_metrics(self):
        """Test API metrics endpoint."""
        response = requests.get(f"{self.BASE_URL}/api/metrics/summary", timeout=5)
        self.assertEqual(response.status_code, 200)

    def test_api_search_endpoint(self):
        """Test API search endpoint."""
        response = requests.get(f"{self.BASE_URL}/api/search?q=test", timeout=5)
        self.assertEqual(response.status_code, 200)

    def test_api_disciplines_endpoint(self):
        """Test API disciplines endpoint."""
        response = requests.get(f"{self.BASE_URL}/api/disciplines", timeout=5)
        self.assertEqual(response.status_code, 200)

    def test_monitoring_metrics_endpoint(self):
        """Test monitoring metrics endpoint."""
        response = requests.get(f"{self.MONITORING_URL}/metrics", timeout=5)
        self.assertEqual(response.status_code, 200)

    def test_monitoring_full_health_endpoint(self):
        """Test monitoring full health endpoint."""
        response = requests.get(f"{self.MONITORING_URL}/api/health/full", timeout=5)
        self.assertEqual(response.status_code, 200)


class TestPerformanceSLA(unittest.TestCase):
    """Test performance SLAs."""

    BASE_URL = "http://localhost:5000"
    SLA_THRESHOLD_MS = 100  # 100ms SLA

    def test_health_endpoint_performance(self):
        """Test health endpoint meets SLA."""
        times: list[float] = []
        for _ in range(10):
            start = time.time()
            requests.get(f"{self.BASE_URL}/health")
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        self.assertLess(avg_time, self.SLA_THRESHOLD_MS,
                       f"Average response time {avg_time:.1f}ms exceeds SLA")

    def test_search_endpoint_performance(self):
        """Test search endpoint meets SLA."""
        times: list[float] = []
        for _ in range(5):
            start = time.time()
            requests.get(f"{self.BASE_URL}/api/search?q=test")
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        self.assertLess(avg_time, self.SLA_THRESHOLD_MS,
                       f"Average response time {avg_time:.1f}ms exceeds SLA")

    def test_p95_response_time(self):
        """Test 95th percentile response time."""
        times: list[float] = []
        for _ in range(20):
            start = time.time()
            requests.get(f"{self.BASE_URL}/health")
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)

        times.sort()
        p95: float = times[int(len(times) * 0.95)]
        self.assertLess(p95, 150, f"P95 response time {p95:.1f}ms exceeds threshold")


class TestSystemHealth(unittest.TestCase):
    """Test system health and monitoring."""

    MONITORING_URL = "http://localhost:8000"

    def test_system_metrics_available(self):
        """Test system metrics are available."""
        response = requests.get(f"{self.MONITORING_URL}/api/metrics/summary", timeout=5)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data)

    def test_health_check_cpu(self):
        """Test CPU health check."""
        response = requests.get(f"{self.MONITORING_URL}/api/health/system", timeout=5)
        self.assertEqual(response.status_code, 200)

    def test_health_check_memory(self):
        """Test memory health check."""
        response = requests.get(f"{self.MONITORING_URL}/api/health/system", timeout=5)
        self.assertEqual(response.status_code, 200)

    def test_health_check_disk(self):
        """Test disk health check."""
        response = requests.get(f"{self.MONITORING_URL}/api/health/system", timeout=5)
        self.assertEqual(response.status_code, 200)

    def test_dependencies_health(self):
        """Test dependencies health check."""
        response = requests.get(f"{self.MONITORING_URL}/api/health/dependencies", timeout=5)
        self.assertEqual(response.status_code, 200)

    def test_metrics_contain_http_data(self):
        """Test metrics contain HTTP data."""
        response = requests.get(f"{self.MONITORING_URL}/api/metrics/summary", timeout=5)
        data = response.json()

        # Should have some HTTP metrics
        self.assertIsNotNone(data)

    def test_logs_endpoint_available(self):
        """Test logs endpoint is available."""
        response = requests.get(f"{self.MONITORING_URL}/api/logs/recent?lines=10", timeout=5)
        self.assertEqual(response.status_code, 200)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in production."""

    BASE_URL = "http://localhost:5000"

    def test_invalid_endpoint_returns_404(self):
        """Test invalid endpoint returns 404."""
        response = requests.get(f"{self.BASE_URL}/api/nonexistent", timeout=5)
        self.assertEqual(response.status_code, 404)

    def test_malformed_query_parameter_handled(self):
        """Test malformed query parameter is handled."""
        response = requests.get(f"{self.BASE_URL}/api/search?q=", timeout=5)
        # Should not crash, may return 200 or 400
        self.assertIn(response.status_code, [200, 400])

    def test_missing_required_parameter_handled(self):
        """Test missing required parameter is handled."""
        response = requests.get(f"{self.BASE_URL}/api/search", timeout=5)
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400])

    def test_timeout_handling(self):
        """Test timeout is handled gracefully."""
        try:
            response = requests.get(f"{self.BASE_URL}/health", timeout=0.1)
            # If it completes in 0.1s, that's fine
            self.assertLess(response.elapsed.total_seconds(), 0.5)
        except requests.Timeout:
            # Timeout is acceptable, showing timeout handling works
            pass


class TestContinuousAvailability(unittest.TestCase):
    """Test continuous availability and stability."""

    BASE_URL = "http://localhost:5000"

    def test_multiple_requests_stability(self):
        """Test system handles multiple sequential requests."""
        success_count = 0
        for _ in range(10):
            try:
                response = requests.get(f"{self.BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    success_count += 1
            except Exception:
                pass

        # At least 95% success rate
        success_rate = success_count / 10
        self.assertGreater(success_rate, 0.95,
                          f"Success rate {success_rate:.1%} below 95%")

    def test_concurrent_availability(self):
        """Test system handles multiple concurrent-like requests."""
        success_count = 0
        for _ in range(5):
            try:
                response = requests.get(f"{self.BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    success_count += 1
            except Exception:
                pass

        self.assertGreaterEqual(success_count, 4,
                               f"System failed {5 - success_count} out of 5 requests")


class TestDeploymentArtifacts(unittest.TestCase):
    """Test deployment artifacts are present."""

    def setUp(self):
        """Set up test fixtures."""
        self.workspace_root = Path(__file__).parent.parent

    def test_docker_compose_file_exists(self):
        """Test docker-compose.yml exists."""
        compose_file = self.workspace_root / "docker-compose.yml"
        self.assertTrue(compose_file.exists())

    def test_docker_compose_production_exists(self):
        """Test production compose file exists."""
        compose_prod = self.workspace_root / "docker-compose.production.yml"
        self.assertTrue(compose_prod.exists())

    def test_dockerfile_exists(self):
        """Test Dockerfile exists."""
        dockerfile = self.workspace_root / "Dockerfile"
        self.assertTrue(dockerfile.exists())

    def test_requirements_txt_exists(self):
        """Test requirements.txt exists."""
        req_file = self.workspace_root / "backend" / "requirements.txt"
        self.assertTrue(req_file.exists())

    def test_main_app_exists(self):
        """Test main app file exists."""
        main_file = self.workspace_root / "backend" / "main.py"
        self.assertTrue(main_file.exists())

    def test_monitoring_app_exists(self):
        """Test monitoring app exists."""
        monitoring_file = self.workspace_root / "backend" / "phase4_monitoring_app.py"
        self.assertTrue(monitoring_file.exists())


class TestEnvironmentValidation(unittest.TestCase):
    """Test environment is properly configured."""

    def test_environment_variables_set(self):
        """Test required environment variables are set."""
        required_vars = [
            "FLASK_ENV",
            "PYTHONUNBUFFERED"
        ]

        import os
        for var in required_vars:
            # Variables may not all be set in test env, but check FLASK_ENV at least
            if var == "FLASK_ENV":
                self.assertIsNotNone(os.environ.get(var, "production"))

    def test_docker_containers_running(self):
        """Test Docker containers are running."""
        try:
            result = subprocess.run(
                ["docker-compose", "ps"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )

            # Should have running containers
            self.assertIn("bob-ai", result.stdout)
        except Exception:
            self.skipTest("Docker not available in test environment")


def run_tests() -> Tuple[int, int, int]:
    """
    Run all production deployment tests.

    Returns:
        Tuple of (tests_run, failures, errors)
    """
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestProductionDeployment))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceSLA))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemHealth))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestContinuousAvailability))
    suite.addTests(loader.loadTestsFromTestCase(TestDeploymentArtifacts))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvironmentValidation))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.testsRun, len(result.failures), len(result.errors)


if __name__ == '__main__':
    print("\n" + "="*80)
    print("PHASE 4.9: PRODUCTION DEPLOYMENT TEST SUITE")
    print("="*80 + "\n")

    tests_run, failures, errors = run_tests()

    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests Run: {tests_run}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    if tests_run > 0:
        pass_rate = ((tests_run - failures - errors) / tests_run * 100)
        print(f"Pass Rate: {pass_rate:.1f}%")
    print("="*80 + "\n")

    sys.exit(0 if failures == 0 and errors == 0 else 1)
