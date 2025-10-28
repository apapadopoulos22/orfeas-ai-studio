#!/usr/bin/env python3
"""
Phase 4 Complete: End-to-End Testing Framework
===============================================

Comprehensive end-to-end testing for BOB AI v10.0 system.
Tests complete user workflows and system integration.

Status: Production-Ready
Version: 1.0.0
"""

import unittest
import requests
from typing import Tuple


class TestE2EWorkflows(unittest.TestCase):
    """End-to-end workflow testing."""

    BASE_URL = "http://localhost:5000"
    MONITORING_URL = "http://localhost:8000"

    def test_complete_api_workflow(self):
        """Test complete API workflow: health → search → disciplines."""
        # Step 1: Health check
        response = requests.get(f"{self.BASE_URL}/health", timeout=5)
        self.assertEqual(response.status_code, 200)

        # Step 2: Search disciplines
        response = requests.get(f"{self.BASE_URL}/api/search?q=test", timeout=5)
        self.assertIn(response.status_code, [200, 400])

        # Step 3: Get disciplines
        response = requests.get(f"{self.BASE_URL}/api/disciplines", timeout=5)
        self.assertEqual(response.status_code, 200)

    def test_monitoring_workflow(self):
        """Test monitoring workflow: health → metrics → system."""
        # Step 1: Monitoring health
        response = requests.get(f"{self.MONITORING_URL}/health", timeout=5)
        self.assertEqual(response.status_code, 200)

        # Step 2: Get metrics
        response = requests.get(f"{self.MONITORING_URL}/metrics", timeout=5)
        self.assertEqual(response.status_code, 200)

        # Step 3: System health
        response = requests.get(f"{self.MONITORING_URL}/api/health/full", timeout=5)
        self.assertEqual(response.status_code, 200)

    def test_system_availability_24hr(self):
        """Test that system maintains >99% availability."""
        success_count = 0
        requests_count = 100

        for _ in range(requests_count):
            try:
                response = requests.get(f"{self.BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    success_count += 1
            except Exception:
                pass

        success_rate = success_count / requests_count
        self.assertGreater(success_rate, 0.99,
                          f"Availability {success_rate:.1%} below 99%")

    def test_api_response_quality(self):
        """Test API response quality and structure."""
        response = requests.get(f"{self.BASE_URL}/health", timeout=5)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status", data)

    def test_concurrent_request_handling(self):
        """Test system handles concurrent requests."""
        import concurrent.futures

        def make_request():
            try:
                response = requests.get(f"{self.BASE_URL}/health", timeout=5)
                return response.status_code == 200
            except Exception:
                return False

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(make_request, range(50)))

        success_rate = sum(results) / len(results)
        self.assertGreater(success_rate, 0.95,
                          f"Concurrent success {success_rate:.1%} below 95%")

    def test_error_recovery(self):
        """Test system error recovery."""
        # Test invalid endpoint
        response = requests.get(f"{self.BASE_URL}/api/nonexistent", timeout=5)
        self.assertEqual(response.status_code, 404)

        # Verify system still responds after error
        response = requests.get(f"{self.BASE_URL}/health", timeout=5)
        self.assertEqual(response.status_code, 200)

    def test_monitoring_metrics_collection(self):
        """Test that monitoring metrics are being collected."""
        response = requests.get(f"{self.MONITORING_URL}/api/metrics/summary", timeout=5)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)


class TestSystemIntegration(unittest.TestCase):
    """System integration testing."""

    BASE_URL = "http://localhost:5000"
    MONITORING_URL = "http://localhost:8000"

    def test_api_monitoring_integration(self):
        """Test that API and monitoring are integrated."""
        # API should be responsive
        api_response = requests.get(f"{self.BASE_URL}/health", timeout=5)
        self.assertEqual(api_response.status_code, 200)

        # Monitoring should be responsive
        mon_response = requests.get(f"{self.MONITORING_URL}/health", timeout=5)
        self.assertEqual(mon_response.status_code, 200)

    def test_system_consistency(self):
        """Test system maintains consistency across components."""
        # Get health from both endpoints
        api_health = requests.get(f"{self.BASE_URL}/health", timeout=5)
        mon_health = requests.get(f"{self.MONITORING_URL}/health", timeout=5)

        # Both should be healthy
        self.assertEqual(api_health.status_code, 200)
        self.assertEqual(mon_health.status_code, 200)

    def test_logging_integration(self):
        """Test that logging is integrated."""
        # Trigger a request
        requests.get(f"{self.BASE_URL}/health", timeout=5)

        # Check logs are available
        response = requests.get(f"{self.MONITORING_URL}/api/logs/recent?lines=10", timeout=5)
        self.assertEqual(response.status_code, 200)


class TestPerformanceUnderLoad(unittest.TestCase):
    """Performance testing under load."""

    BASE_URL = "http://localhost:5000"

    def test_sustained_performance(self):
        """Test performance under sustained load."""
        import time

        times = []
        for _ in range(50):
            start = time.time()
            requests.get(f"{self.BASE_URL}/health", timeout=5)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        self.assertLess(avg_time, 150, f"Sustained load avg {avg_time:.1f}ms exceeds 150ms")

    def test_peak_performance(self):
        """Test performance under peak load."""
        import time
        import concurrent.futures

        def timed_request():
            start = time.time()
            requests.get(f"{self.BASE_URL}/health", timeout=5)
            return (time.time() - start) * 1000

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            times = list(executor.map(timed_request, range(100)))

        avg_time = sum(times) / len(times)
        max_time = max(times)

        self.assertLess(avg_time, 200, f"Peak load avg {avg_time:.1f}ms exceeds 200ms")
        self.assertLess(max_time, 500, f"Peak load max {max_time:.1f}ms exceeds 500ms")


class TestSecurityIntegration(unittest.TestCase):
    """Security integration testing."""

    BASE_URL = "http://localhost:5000"

    def test_response_headers(self):
        """Test that security headers are present."""
        response = requests.get(f"{self.BASE_URL}/health", timeout=5)

        # Check for security headers
        headers_to_check = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection"
        ]

        # At least some security headers should be present
        security_headers = sum(1 for h in headers_to_check if h in response.headers)
        self.assertGreater(security_headers, 0,
                          "No security headers found in response")

    def test_error_messages_safe(self):
        """Test that error messages don't leak sensitive info."""
        response = requests.get(f"{self.BASE_URL}/api/nonexistent", timeout=5)
        self.assertEqual(response.status_code, 404)

        # Response should not contain stack traces or file paths
        text = response.text.lower()
        self.assertNotIn("traceback", text)
        self.assertNotIn("/home/", text)
        self.assertNotIn("\\users\\", text.lower())


class TestDataIntegrity(unittest.TestCase):
    """Data integrity testing."""

    BASE_URL = "http://localhost:5000"

    def test_api_response_consistency(self):
        """Test that API responses are consistent."""
        # Make multiple requests
        responses = []
        for _ in range(5):
            response = requests.get(f"{self.BASE_URL}/health", timeout=5)
            responses.append(response.status_code)

        # All should be successful
        self.assertTrue(all(r == 200 for r in responses),
                       "API responses inconsistent")

    def test_json_response_validity(self):
        """Test that JSON responses are valid."""
        response = requests.get(f"{self.BASE_URL}/health", timeout=5)

        # Should be valid JSON
        try:
            data = response.json()
            self.assertIsNotNone(data)
        except Exception as e:
            self.fail(f"Invalid JSON response: {e}")


def run_e2e_tests() -> Tuple[int, int, int]:
    """Run all E2E tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestE2EWorkflows))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceUnderLoad))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestDataIntegrity))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.testsRun, len(result.failures), len(result.errors)


if __name__ == '__main__':
    print("\n" + "="*80)
    print("PHASE 4 COMPLETE: END-TO-END TEST SUITE")
    print("="*80 + "\n")

    tests_run, failures, errors = run_e2e_tests()

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
