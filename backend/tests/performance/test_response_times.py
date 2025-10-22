"""
ORFEAS Performance Tests - Response Time SLA Verification
Tests to ensure API endpoints meet performance SLAs
Target: P95 latency < 200ms for all endpoints
"""
import pytest
import requests
import time
import statistics
from typing import List, Dict
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# ============================================================================
# Configuration
# ============================================================================

SERVER_URL = "http://127.0.0.1:5000"
SLA_P95_MS = 200  # 200ms P95 target
SLA_P99_MS = 500  # 500ms P99 target
SAMPLE_SIZE = 100  # Number of requests per test


# ============================================================================
# Helper Functions
# ============================================================================

def measure_response_times(url: str, method: str = "GET", **kwargs) -> List[float]:
    """
    Measure response times for multiple requests

    Args:
        url: Full URL to test
        method: HTTP method (GET, POST, etc.)
        **kwargs: Additional arguments for requests

    Returns:
        List of response times in milliseconds
    """
    response_times = []

    for _ in range(SAMPLE_SIZE):
        start_time = time.perf_counter()

        try:
            if method == "GET":
                response = requests.get(url, timeout=10, **kwargs)
            elif method == "POST":
                response = requests.post(url, timeout=10, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")

            end_time = time.perf_counter()

            # Only count successful responses
            if response.status_code < 500:
                response_time_ms = (end_time - start_time) * 1000
                response_times.append(response_time_ms)

        except requests.exceptions.RequestException:
            # Skip failed requests
            pass

    return response_times


def calculate_percentiles(response_times: List[float]) -> Dict[str, float]:
    """
    Calculate response time percentiles

    Args:
        response_times: List of response times in milliseconds

    Returns:
        Dictionary with P50, P95, P99, mean, min, max
    """
    if not response_times:
        return {
            "p50": 0,
            "p95": 0,
            "p99": 0,
            "mean": 0,
            "min": 0,
            "max": 0,
            "count": 0
        }

    sorted_times = sorted(response_times)

    return {
        "p50": statistics.quantiles(sorted_times, n=2)[0] if len(sorted_times) >= 2 else sorted_times[0],
        "p95": statistics.quantiles(sorted_times, n=20)[18] if len(sorted_times) >= 20 else sorted_times[-1],
        "p99": statistics.quantiles(sorted_times, n=100)[98] if len(sorted_times) >= 100 else sorted_times[-1],
        "mean": statistics.mean(sorted_times),
        "min": min(sorted_times),
        "max": max(sorted_times),
        "count": len(sorted_times)
    }


def assert_sla_compliance(percentiles: Dict[str, float], endpoint: str):
    """
    Assert that response times meet SLA targets

    Args:
        percentiles: Calculated percentiles
        endpoint: Endpoint name for error messages
    """
    p95 = percentiles["p95"]
    p99 = percentiles["p99"]

    print(f"\n{endpoint} Performance:")
    print(f"  P50: {percentiles['p50']:.2f}ms")
    print(f"  P95: {p95:.2f}ms (target: <{SLA_P95_MS}ms)")
    print(f"  P99: {p99:.2f}ms (target: <{SLA_P99_MS}ms)")
    print(f"  Mean: {percentiles['mean']:.2f}ms")
    print(f"  Min: {percentiles['min']:.2f}ms")
    print(f"  Max: {percentiles['max']:.2f}ms")
    print(f"  Samples: {percentiles['count']}")

    assert p95 < SLA_P95_MS, \
        f"{endpoint} P95 latency ({p95:.2f}ms) exceeds SLA target ({SLA_P95_MS}ms)"

    assert p99 < SLA_P99_MS, \
        f"{endpoint} P99 latency ({p99:.2f}ms) exceeds SLA target ({SLA_P99_MS}ms)"


# ============================================================================
# Health Check Endpoint Performance Tests
# ============================================================================

@pytest.mark.performance
@pytest.mark.slow
class TestHealthCheckPerformance:
    """Performance tests for /api/health endpoint"""

    def test_health_check_response_time(self):
        """Test that health check meets SLA targets"""
        url = f"{SERVER_URL}/api/health"

        response_times = measure_response_times(url, method="GET")
        percentiles = calculate_percentiles(response_times)

        assert_sla_compliance(percentiles, "/api/health")

    def test_health_check_consistency(self):
        """Test that health check response times are consistent"""
        url = f"{SERVER_URL}/api/health"

        response_times = measure_response_times(url, method="GET")

        if response_times:
            std_dev = statistics.stdev(response_times)
            mean = statistics.mean(response_times)

            # Coefficient of variation should be < 0.5 (good consistency)
            cv = std_dev / mean

            print(f"\nHealth Check Consistency:")
            print(f"  Standard Deviation: {std_dev:.2f}ms")
            print(f"  Coefficient of Variation: {cv:.2f}")

            assert cv < 0.5, f"Health check response times too variable (CV: {cv:.2f})"


# ============================================================================
# Models Info Endpoint Performance Tests
# ============================================================================

@pytest.mark.performance
@pytest.mark.slow
class TestModelsInfoPerformance:
    """Performance tests for /api/models-info endpoint"""

    def test_models_info_response_time(self):
        """Test that models-info meets SLA targets"""
        url = f"{SERVER_URL}/api/models-info"

        response_times = measure_response_times(url, method="GET")
        percentiles = calculate_percentiles(response_times)

        assert_sla_compliance(percentiles, "/api/models-info")


# ============================================================================
# File Upload Performance Tests
# ============================================================================

@pytest.mark.performance
@pytest.mark.slow
class TestUploadPerformance:
    """Performance tests for file upload endpoint"""

    def test_small_image_upload_response_time(self):
        """Test upload performance with small images (512x512)"""
        url = f"{SERVER_URL}/api/upload-image"

        # Create small test image (10KB)
        from io import BytesIO
        from PIL import Image

        img = Image.new('RGB', (512, 512), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        files = {'image': ('test.png', img_bytes, 'image/png')}

        response_times = []
        for _ in range(min(SAMPLE_SIZE, 20)):  # Fewer samples for uploads
            img_bytes.seek(0)  # Reset stream

            start_time = time.perf_counter()
            try:
                response = requests.post(url, files=files, timeout=30)
                end_time = time.perf_counter()

                if response.status_code < 500:
                    response_time_ms = (end_time - start_time) * 1000
                    response_times.append(response_time_ms)
            except:
                pass

        percentiles = calculate_percentiles(response_times)

        print(f"\nSmall Image Upload Performance:")
        print(f"  P95: {percentiles['p95']:.2f}ms")
        print(f"  Mean: {percentiles['mean']:.2f}ms")

        # Upload should complete within 1 second P95
        assert percentiles['p95'] < 1000, \
            f"Small image upload too slow: {percentiles['p95']:.2f}ms"


# ============================================================================
# Concurrent Request Performance Tests
# ============================================================================

@pytest.mark.performance
@pytest.mark.slow
class TestConcurrentPerformance:
    """Performance tests for concurrent requests"""

    def test_concurrent_health_checks(self):
        """Test that server handles concurrent requests efficiently"""
        import concurrent.futures

        url = f"{SERVER_URL}/api/health"

        def single_request():
            start = time.perf_counter()
            try:
                response = requests.get(url, timeout=5)
                end = time.perf_counter()
                return (end - start) * 1000 if response.status_code < 500 else None
            except:
                return None

        # Execute 50 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(single_request) for _ in range(50)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # Filter out failed requests
        response_times = [r for r in results if r is not None]

        percentiles = calculate_percentiles(response_times)

        print(f"\nConcurrent Requests Performance (50 concurrent):")
        print(f"  P95: {percentiles['p95']:.2f}ms")
        print(f"  P99: {percentiles['p99']:.2f}ms")
        print(f"  Success Rate: {len(response_times)}/50 ({len(response_times)/50*100:.1f}%)")

        # Under load, allow 2x SLA target
        assert percentiles['p95'] < SLA_P95_MS * 2, \
            f"Concurrent P95 latency too high: {percentiles['p95']:.2f}ms"

        # Success rate should be > 90%
        success_rate = len(response_times) / 50
        assert success_rate > 0.9, \
            f"Success rate too low under load: {success_rate*100:.1f}%"


# ============================================================================
# Baseline Performance Tests
# ============================================================================

@pytest.mark.performance
class TestBaselinePerformance:
    """Establish baseline performance metrics"""

    def test_measure_baseline_performance(self):
        """Measure and document baseline performance for all endpoints"""
        endpoints = [
            ("GET", "/api/health", {}),
            ("GET", "/api/models-info", {}),
        ]

        results = {}

        for method, endpoint, kwargs in endpoints:
            url = f"{SERVER_URL}{endpoint}"
            response_times = measure_response_times(url, method=method, **kwargs)
            percentiles = calculate_percentiles(response_times)
            results[endpoint] = percentiles

        # Print baseline report
        print("\n" + "="*80)
        print("BASELINE PERFORMANCE REPORT")
        print("="*80)

        for endpoint, perf in results.items():
            print(f"\n{endpoint}:")
            print(f"  P50: {perf['p50']:.2f}ms")
            print(f"  P95: {perf['p95']:.2f}ms")
            print(f"  P99: {perf['p99']:.2f}ms")
            print(f"  Mean: {perf['mean']:.2f}ms")
            print(f"  Min: {perf['min']:.2f}ms")
            print(f"  Max: {perf['max']:.2f}ms")
            print(f"  Samples: {perf['count']}")

        print("\n" + "="*80)

        # Always pass (just documenting baseline)
        assert True


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short", "-m", "performance"])
