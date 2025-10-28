#!/usr/bin/env python3
"""
Performance Validation Script
=============================

Validates that production deployment meets performance SLAs.

Endpoints Tested:
- API: /health, /api/search, /api/disciplines
- Monitoring: /health, /metrics, /api/health/full

SLAs:
- <100ms for all endpoints (average)
- <150ms for 95th percentile
- >99% availability

Status: Production-Ready
Version: 1.0.0
"""

import time
import statistics
import requests
from typing import Dict, List, Tuple


class PerformanceValidator:
    """Validates performance against SLAs."""

    def __init__(self, base_url: str = "http://localhost:5000",
                 monitoring_url: str = "http://localhost:8000"):
        """Initialize validator."""
        self.base_url = base_url
        self.monitoring_url = monitoring_url
        self.results: Dict[str, List[float]] = {}
        self.errors: Dict[str, int] = {}

    def test_endpoint(self, endpoint: str, url: str, num_requests: int = 10) -> None:
        """Test an endpoint and record response times."""
        times: List[float] = []
        errors = 0

        for _ in range(num_requests):
            try:
                start = time.time()
                response = requests.get(url, timeout=5)
                elapsed = (time.time() - start) * 1000

                if response.status_code == 200:
                    times.append(elapsed)
                else:
                    errors += 1
            except Exception:
                errors += 1

        self.results[endpoint] = times
        self.errors[endpoint] = errors

    def get_stats(self, endpoint: str) -> Tuple[float, float, float, float]:
        """Get performance statistics for an endpoint."""
        times = self.results.get(endpoint, [])
        if not times:
            return 0.0, 0.0, 0.0, 0.0

        avg = statistics.mean(times)
        median = statistics.median(times)
        times_sorted = sorted(times)
        p95 = times_sorted[int(len(times_sorted) * 0.95)] if len(times_sorted) > 0 else 0.0
        p99 = times_sorted[int(len(times_sorted) * 0.99)] if len(times_sorted) > 0 else 0.0

        return avg, median, p95, p99

    def validate_slas(self) -> bool:
        """Validate all endpoints meet SLAs."""
        all_pass = True

        print("\n" + "="*80)
        print("PERFORMANCE SLA VALIDATION")
        print("="*80 + "\n")

        for endpoint in sorted(self.results.keys()):
            times = self.results[endpoint]
            errors = self.errors.get(endpoint, 0)

            if not times:
                print(f"❌ {endpoint:50s} - No successful requests")
                all_pass = False
                continue

            avg, median, p95, p99 = self.get_stats(endpoint)
            success_rate = len(times) / (len(times) + errors) * 100

            # Check SLAs
            sla_pass = (avg < 100 and p95 < 150 and success_rate > 99)

            status = "✅" if sla_pass else "❌"
            print(f"{status} {endpoint:50s}")
            print(f"   Average: {avg:6.1f}ms (SLA: <100ms)   {'✓' if avg < 100 else '✗'}")
            print(f"   Median:  {median:6.1f}ms")
            print(f"   P95:     {p95:6.1f}ms (SLA: <150ms)   {'✓' if p95 < 150 else '✗'}")
            print(f"   P99:     {p99:6.1f}ms")
            print(f"   Success: {success_rate:5.1f}% (SLA: >99%)   {'✓' if success_rate > 99 else '✗'}")

            if not sla_pass:
                all_pass = False

            print()

        return all_pass

    def run_validation(self) -> bool:
        """Run complete validation."""
        print("Starting performance validation...")
        print("Testing 10 requests per endpoint...\n")

        # Test API endpoints
        self.test_endpoint("API: /health",
                          f"{self.base_url}/health", 10)
        self.test_endpoint("API: /api/search",
                          f"{self.base_url}/api/search?q=test", 10)
        self.test_endpoint("API: /api/disciplines",
                          f"{self.base_url}/api/disciplines", 10)

        # Test monitoring endpoints
        self.test_endpoint("Monitoring: /health",
                          f"{self.monitoring_url}/health", 10)
        self.test_endpoint("Monitoring: /metrics",
                          f"{self.monitoring_url}/metrics", 10)
        self.test_endpoint("Monitoring: /api/health/full",
                          f"{self.monitoring_url}/api/health/full", 10)

        # Validate SLAs
        return self.validate_slas()


def main() -> int:
    """Main entry point."""
    validator = PerformanceValidator()

    try:
        if validator.run_validation():
            print("✅ All SLAs met!")
            return 0
        else:
            print("❌ Some SLAs not met")
            return 1
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
