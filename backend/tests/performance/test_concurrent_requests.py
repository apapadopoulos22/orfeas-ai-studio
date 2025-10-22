"""
ORFEAS Performance Tests - Concurrent Request Load Testing
Locust-style load testing configuration for stress testing
"""
import pytest
import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# ============================================================================
# Configuration
# ============================================================================

SERVER_URL = "http://127.0.0.1:5000"
MAX_USERS = 100  # Maximum concurrent users
SPAWN_RATE = 10  # Users spawned per second
TEST_DURATION = 30  # Test duration in seconds
TARGET_RPS = 50  # Target requests per second
MAX_FAILURE_RATE = 0.01  # Maximum 1% failure rate


# ============================================================================
# User Behavior Classes (Locust-style)
# ============================================================================

class BaseUser:
    """Base class for user behavior"""

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.session = requests.Session()
        self.request_count = 0
        self.failure_count = 0
        self.response_times = []

    def make_request(self, method: str, endpoint: str, **kwargs):
        """Make a request and record metrics"""
        start_time = time.time()
        try:
            response = self.session.request(method, f"{SERVER_URL}{endpoint}", **kwargs)
            response_time = (time.time() - start_time) * 1000  # Convert to ms

            self.request_count += 1
            self.response_times.append(response_time)

            if response.status_code >= 400:
                self.failure_count += 1

            return response
        except Exception as e:
            self.failure_count += 1
            self.request_count += 1
            return None

    def get_stats(self):
        """Get user statistics"""
        return {
            "user_id": self.user_id,
            "requests": self.request_count,
            "failures": self.failure_count,
            "avg_response_time": statistics.mean(self.response_times) if self.response_times else 0,
            "min_response_time": min(self.response_times) if self.response_times else 0,
            "max_response_time": max(self.response_times) if self.response_times else 0,
        }


class HealthCheckUser(BaseUser):
    """User that only checks health endpoint"""

    def run(self, duration: int):
        """Run health check requests for specified duration"""
        end_time = time.time() + duration

        while time.time() < end_time:
            self.make_request("GET", "/api/health", timeout=5)
            time.sleep(0.1)  # 10 RPS per user


class ModelsInfoUser(BaseUser):
    """User that checks models-info endpoint"""

    def run(self, duration: int):
        """Run models-info requests for specified duration"""
        end_time = time.time() + duration

        while time.time() < end_time:
            self.make_request("GET", "/api/models-info", timeout=10)
            time.sleep(0.5)  # 2 RPS per user


class MixedUser(BaseUser):
    """User with mixed behavior (health + models-info)"""

    def run(self, duration: int):
        """Run mixed requests for specified duration"""
        end_time = time.time() + duration

        while time.time() < end_time:
            # 70% health checks, 30% models-info
            if self.request_count % 10 < 7:
                self.make_request("GET", "/api/health", timeout=5)
            else:
                self.make_request("GET", "/api/models-info", timeout=10)

            time.sleep(0.2)  # 5 RPS per user


# ============================================================================
# Load Test Scenarios
# ============================================================================

@pytest.mark.performance
@pytest.mark.slow
class TestBasicLoadScenarios:
    """Basic load testing scenarios"""

    def test_constant_load_health_check(self):
        """Test constant load on health check endpoint"""
        num_users = 20
        duration = 10

        print(f"\n{'='*60}")
        print(f"LOAD TEST: {num_users} users, {duration}s duration")
        print(f"{'='*60}")

        users = [HealthCheckUser(i) for i in range(num_users)]

        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(user.run, duration) for user in users]

            # Wait for all users to complete
            for future in as_completed(futures):
                future.result()

        # Aggregate statistics
        total_requests = sum(user.request_count for user in users)
        total_failures = sum(user.failure_count for user in users)
        all_response_times = []
        for user in users:
            all_response_times.extend(user.response_times)

        failure_rate = total_failures / total_requests if total_requests > 0 else 0
        avg_response_time = statistics.mean(all_response_times) if all_response_times else 0
        p95_response_time = statistics.quantiles(all_response_times, n=20)[18] if all_response_times else 0
        requests_per_second = total_requests / duration

        print(f"\nResults:")
        print(f"  Total Requests: {total_requests}")
        print(f"  Total Failures: {total_failures}")
        print(f"  Failure Rate: {failure_rate*100:.2f}%")
        print(f"  Avg Response Time: {avg_response_time:.2f} ms")
        print(f"  P95 Response Time: {p95_response_time:.2f} ms")
        print(f"  Requests/Second: {requests_per_second:.2f}")

        # Assertions
        assert failure_rate < MAX_FAILURE_RATE, \
            f"Failure rate too high: {failure_rate*100:.2f}%"
        assert p95_response_time < 500, \
            f"P95 response time too high: {p95_response_time:.2f} ms"

    def test_ramping_load(self):
        """Test ramping load from 10 to 50 users"""
        stages = [
            (10, 5),  # 10 users for 5 seconds
            (25, 5),  # 25 users for 5 seconds
            (50, 5),  # 50 users for 5 seconds
        ]

        print(f"\n{'='*60}")
        print(f"RAMPING LOAD TEST")
        print(f"{'='*60}")

        all_stats = []

        for num_users, duration in stages:
            print(f"\n--- Stage: {num_users} users for {duration}s ---")

            users = [HealthCheckUser(i) for i in range(num_users)]

            with ThreadPoolExecutor(max_workers=num_users) as executor:
                futures = [executor.submit(user.run, duration) for user in users]

                for future in as_completed(futures):
                    future.result()

            # Collect stats for this stage
            total_requests = sum(user.request_count for user in users)
            total_failures = sum(user.failure_count for user in users)
            all_response_times = []
            for user in users:
                all_response_times.extend(user.response_times)

            failure_rate = total_failures / total_requests if total_requests > 0 else 0
            avg_response_time = statistics.mean(all_response_times) if all_response_times else 0
            requests_per_second = total_requests / duration

            stats = {
                "users": num_users,
                "requests": total_requests,
                "failures": total_failures,
                "failure_rate": failure_rate,
                "avg_response_time": avg_response_time,
                "rps": requests_per_second,
            }
            all_stats.append(stats)

            print(f"  Requests: {total_requests}")
            print(f"  Failures: {total_failures}")
            print(f"  Failure Rate: {failure_rate*100:.2f}%")
            print(f"  Avg Response Time: {avg_response_time:.2f} ms")
            print(f"  RPS: {requests_per_second:.2f}")

        # Verify performance degrades gracefully
        for stats in all_stats:
            assert stats["failure_rate"] < 0.05, \
                f"Failure rate too high at {stats['users']} users: {stats['failure_rate']*100:.2f}%"


@pytest.mark.performance
@pytest.mark.slow
class TestSpikeLoadScenarios:
    """Spike and stress testing scenarios"""

    def test_sudden_spike(self):
        """Test sudden spike from 10 to 100 users"""
        print(f"\n{'='*60}")
        print(f"SPIKE TEST: 10 â†’ 100 users")
        print(f"{'='*60}")

        # Start with 10 users
        initial_users = 10
        spike_users = 100
        duration = 5

        print(f"\n--- Baseline: {initial_users} users ---")
        users = [HealthCheckUser(i) for i in range(initial_users)]

        with ThreadPoolExecutor(max_workers=initial_users) as executor:
            futures = [executor.submit(user.run, duration) for user in users]
            for future in as_completed(futures):
                future.result()

        baseline_failures = sum(user.failure_count for user in users)
        baseline_total = sum(user.request_count for user in users)
        baseline_failure_rate = baseline_failures / baseline_total if baseline_total > 0 else 0

        print(f"  Requests: {baseline_total}")
        print(f"  Failure Rate: {baseline_failure_rate*100:.2f}%")

        # Spike to 100 users
        print(f"\n--- Spike: {spike_users} users ---")
        users = [HealthCheckUser(i) for i in range(spike_users)]

        with ThreadPoolExecutor(max_workers=spike_users) as executor:
            futures = [executor.submit(user.run, duration) for user in users]
            for future in as_completed(futures):
                future.result()

        spike_failures = sum(user.failure_count for user in users)
        spike_total = sum(user.request_count for user in users)
        spike_failure_rate = spike_failures / spike_total if spike_total > 0 else 0

        print(f"  Requests: {spike_total}")
        print(f"  Failure Rate: {spike_failure_rate*100:.2f}%")

        # Verify system handles spike (allow higher failure rate during spike)
        assert spike_failure_rate < 0.10, \
            f"Spike failure rate too high: {spike_failure_rate*100:.2f}%"

    def test_sustained_heavy_load(self):
        """Test sustained heavy load with 80 users for 15 seconds"""
        num_users = 80
        duration = 15

        print(f"\n{'='*60}")
        print(f"SUSTAINED LOAD TEST: {num_users} users, {duration}s")
        print(f"{'='*60}")

        users = [HealthCheckUser(i) for i in range(num_users)]

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(user.run, duration) for user in users]
            for future in as_completed(futures):
                future.result()

        elapsed_time = time.time() - start_time

        # Aggregate statistics
        total_requests = sum(user.request_count for user in users)
        total_failures = sum(user.failure_count for user in users)
        all_response_times = []
        for user in users:
            all_response_times.extend(user.response_times)

        failure_rate = total_failures / total_requests if total_requests > 0 else 0
        avg_response_time = statistics.mean(all_response_times) if all_response_times else 0
        p95_response_time = statistics.quantiles(all_response_times, n=20)[18] if all_response_times else 0
        requests_per_second = total_requests / elapsed_time

        print(f"\nResults:")
        print(f"  Total Requests: {total_requests}")
        print(f"  Total Failures: {total_failures}")
        print(f"  Failure Rate: {failure_rate*100:.2f}%")
        print(f"  Avg Response Time: {avg_response_time:.2f} ms")
        print(f"  P95 Response Time: {p95_response_time:.2f} ms")
        print(f"  Requests/Second: {requests_per_second:.2f}")
        print(f"  Elapsed Time: {elapsed_time:.2f}s")

        # Assertions for sustained load
        assert failure_rate < 0.05, \
            f"Failure rate too high under sustained load: {failure_rate*100:.2f}%"
        assert requests_per_second >= TARGET_RPS, \
            f"RPS too low: {requests_per_second:.2f} < {TARGET_RPS}"


@pytest.mark.performance
@pytest.mark.slow
class TestMixedWorkloadScenarios:
    """Mixed workload scenarios"""

    def test_mixed_endpoint_load(self):
        """Test mixed load across health and models-info endpoints"""
        num_users = 40
        duration = 10

        print(f"\n{'='*60}")
        print(f"MIXED WORKLOAD TEST: {num_users} users, {duration}s")
        print(f"{'='*60}")

        users = [MixedUser(i) for i in range(num_users)]

        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(user.run, duration) for user in users]
            for future in as_completed(futures):
                future.result()

        # Aggregate statistics
        total_requests = sum(user.request_count for user in users)
        total_failures = sum(user.failure_count for user in users)
        all_response_times = []
        for user in users:
            all_response_times.extend(user.response_times)

        failure_rate = total_failures / total_requests if total_requests > 0 else 0
        avg_response_time = statistics.mean(all_response_times) if all_response_times else 0
        p95_response_time = statistics.quantiles(all_response_times, n=20)[18] if all_response_times else 0
        requests_per_second = total_requests / duration

        print(f"\nResults:")
        print(f"  Total Requests: {total_requests}")
        print(f"  Total Failures: {total_failures}")
        print(f"  Failure Rate: {failure_rate*100:.2f}%")
        print(f"  Avg Response Time: {avg_response_time:.2f} ms")
        print(f"  P95 Response Time: {p95_response_time:.2f} ms")
        print(f"  Requests/Second: {requests_per_second:.2f}")

        # Assertions
        assert failure_rate < 0.02, \
            f"Failure rate too high: {failure_rate*100:.2f}%"
        assert p95_response_time < 600, \
            f"P95 response time too high: {p95_response_time:.2f} ms"


# ============================================================================
# Stress Testing (Beyond Normal Load)
# ============================================================================

@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.stress
class TestStressScenarios:
    """Stress testing beyond normal operating conditions"""

    def test_maximum_throughput(self):
        """Test maximum throughput with 150 users"""
        num_users = 150
        duration = 10

        print(f"\n{'='*60}")
        print(f"STRESS TEST: {num_users} users, {duration}s")
        print(f"{'='*60}")
        print(f"WARNING: This test pushes beyond normal operating limits")

        users = [HealthCheckUser(i) for i in range(num_users)]

        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(user.run, duration) for user in users]
            for future in as_completed(futures):
                future.result()

        # Aggregate statistics
        total_requests = sum(user.request_count for user in users)
        total_failures = sum(user.failure_count for user in users)
        all_response_times = []
        for user in users:
            all_response_times.extend(user.response_times)

        failure_rate = total_failures / total_requests if total_requests > 0 else 0
        avg_response_time = statistics.mean(all_response_times) if all_response_times else 0
        requests_per_second = total_requests / duration

        print(f"\nResults:")
        print(f"  Total Requests: {total_requests}")
        print(f"  Total Failures: {total_failures}")
        print(f"  Failure Rate: {failure_rate*100:.2f}%")
        print(f"  Avg Response Time: {avg_response_time:.2f} ms")
        print(f"  Requests/Second: {requests_per_second:.2f}")
        print(f"\nMAXIMUM THROUGHPUT: {requests_per_second:.2f} RPS")

        # Relaxed assertions for stress test (document limits)
        assert failure_rate < 0.15, \
            f"Catastrophic failure rate: {failure_rate*100:.2f}%"

        print(f"\n[OK] System survived stress test")
        print(f"   Max RPS: {requests_per_second:.2f}")
        print(f"   Failure Rate: {failure_rate*100:.2f}%")


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short", "-m", "performance"])
