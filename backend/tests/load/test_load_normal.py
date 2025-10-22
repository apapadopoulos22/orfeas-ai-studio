"""
Load Test Scenario 2: Normal Load (3 Concurrent Users)
=========================================================

Simulates typical production traffic with 3 concurrent users
making generation requests over a 10-minute period.

Test Configuration:
- Concurrent users: 3
- Test duration: 10 minutes (600 seconds)
- Requests per user: ~8-10 (random intervals 60-90s)
- Expected total requests: 24-30
- Image: temp/test_images/quality_test_unique2.png

Success Criteria:
1. Server uptime: 100% (no crashes)
2. Error rate: <1% (at most 1 error across all requests)
3. Average response time: <90s
4. P95 response time: <120s
5. P99 response time: <150s
6. All concurrent requests complete

Expected Duration: ~10 minutes
"""

import sys
import os
import time
import random
import threading
from pathlib import Path
from typing import List
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from load_test_utils import (
    LoadTestClient,
    RequestResult,
    aggregate_results,
    print_metrics_summary,
    save_results_json
)

# Test configuration
NUM_USERS = 3
TEST_DURATION_SECONDS = 600  # 10 minutes
MIN_INTERVAL_SECONDS = 60
MAX_INTERVAL_SECONDS = 90
BASE_URL = "http://localhost:5000"
TEST_IMAGE = "../../temp/test_images/quality_test_unique2.png"
OUTPUT_FILE = "results_normal.json"

def user_simulation(user_id: int, results: List[RequestResult], test_start_time: float):
    """
    Simulate a single user making requests over the test duration

    Args:
        user_id: Unique user identifier
        results: Shared list to store request results
        test_start_time: Start time of the test (for elapsed time calculation)
    """
    client = LoadTestClient(BASE_URL)
    request_count = 0

    print(f"[User {user_id}] Starting simulation")

    while True:
        # Check if test duration exceeded
        elapsed = time.time() - test_start_time
        if elapsed >= TEST_DURATION_SECONDS:
            print(f"[User {user_id}] Test duration reached, exiting (made {request_count} requests)")
            break

        # Random interval between requests
        interval = random.uniform(MIN_INTERVAL_SECONDS, MAX_INTERVAL_SECONDS)

        # Check if there's time for another request
        if elapsed + interval > TEST_DURATION_SECONDS:
            print(f"[User {user_id}] Not enough time for another request, exiting")
            break

        # Wait random interval
        print(f"[User {user_id}] Waiting {interval:.1f}s before next request...")
        time.sleep(interval)

        # Make request
        request_count += 1
        print(f"[User {user_id}] Making request #{request_count} (t={elapsed:.1f}s)")

        result = client.generate_3d(
            TEST_IMAGE,
            timeout=300  # 5-minute timeout per request
        )

        results.append(result)

        status = " SUCCESS" if result.success else " FAILED"
        print(f"[User {user_id}] Request #{request_count} {status} ({result.duration:.1f}s)")

        if not result.success:
            print(f"[User {user_id}] Error: {result.error}")

    client.close()
    print(f"[User {user_id}] Completed: {request_count} requests")

def main():
    """Run normal load test with 3 concurrent users"""

    print("=" * 80)
    print("LOAD TEST SCENARIO 2: NORMAL LOAD (3 CONCURRENT USERS)")
    print("=" * 80)
    print(f"Configuration:")
    print(f"  Concurrent users: {NUM_USERS}")
    print(f"  Test duration: {TEST_DURATION_SECONDS}s ({TEST_DURATION_SECONDS // 60} minutes)")
    print(f"  Request interval: {MIN_INTERVAL_SECONDS}-{MAX_INTERVAL_SECONDS}s per user")
    print(f"  Expected requests: ~24-30 total")
    print(f"  Image: {TEST_IMAGE}")
    print("=" * 80)

    # Phase 1: Health check
    print("\n[PHASE 1] Health check...")
    client = LoadTestClient(BASE_URL)
    if not client.health_check():
        print(" Backend is not healthy, aborting test")
        return 1
    print(" Backend is healthy")
    client.close()

    # Phase 2: Verify test image exists
    print("\n[PHASE 2] Verifying test image...")
    test_image_path = Path(__file__).parent / TEST_IMAGE
    if not test_image_path.exists():
        print(f" Test image not found: {test_image_path}")
        print(f"   Please run: python create_test_image.py {test_image_path}")
        return 1
    print(f" Test image exists: {test_image_path}")

    # Phase 3: Run concurrent user simulations
    print("\n[PHASE 3] Starting concurrent user simulations...")
    print(f"Starting {NUM_USERS} user threads...")

    test_start_time = time.time()
    results: List[RequestResult] = []
    threads: List[threading.Thread] = []

    # Start user threads
    for user_id in range(1, NUM_USERS + 1):
        thread = threading.Thread(
            target=user_simulation,
            args=(user_id, results, test_start_time),
            daemon=False
        )
        thread.start()
        threads.append(thread)
        print(f" User {user_id} started")
        time.sleep(1)  # Stagger thread starts slightly

    print(f"\n All {NUM_USERS} users started!")
    print(f"⏳ Test running for {TEST_DURATION_SECONDS}s (~{TEST_DURATION_SECONDS // 60} minutes)...")
    print("   Monitor progress in terminal output above")

    # Wait for all threads to complete
    for i, thread in enumerate(threads, 1):
        thread.join()
        print(f" User {i} completed")

    test_end_time = time.time()
    actual_duration = test_end_time - test_start_time

    print(f"\n All users completed!")
    print(f"   Actual duration: {actual_duration:.1f}s")
    print(f"   Total requests: {len(results)}")

    # Phase 4: Aggregate results
    print("\n[PHASE 4] Aggregating results...")
    metrics = aggregate_results(
        results,
        scenario="normal_load",
        test_start=test_start_time,
        test_end=test_end_time
    )

    # Phase 5: Validate results
    print("\n[PHASE 5] Validating results...")
    print("=" * 80)

    validation_passed = True

    # Criterion 1: Server uptime (no crashes - all requests attempted)
    expected_min_requests = 20  # At least 20 requests in 10 minutes
    criterion1_pass = len(results) >= expected_min_requests
    print(f"1. Server Uptime (Minimum requests)")
    print(f"   Expected: ≥{expected_min_requests} requests")
    print(f"   Actual: {len(results)} requests")
    print(f"   Status: {' PASS' if criterion1_pass else ' FAIL'}")
    validation_passed = validation_passed and criterion1_pass

    # Criterion 2: Error rate <1%
    criterion2_pass = metrics.error_rate <= 1.0
    print(f"\n2. Error Rate")
    print(f"   Expected: <1%")
    print(f"   Actual: {metrics.error_rate:.2f}%")
    print(f"   Status: {' PASS' if criterion2_pass else ' FAIL'}")
    validation_passed = validation_passed and criterion2_pass

    # Criterion 3: Average response time <90s
    criterion3_pass = metrics.avg_duration <= 90
    print(f"\n3. Average Response Time")
    print(f"   Expected: <90s")
    print(f"   Actual: {metrics.avg_duration:.1f}s")
    print(f"   Status: {' PASS' if criterion3_pass else ' FAIL'}")
    validation_passed = validation_passed and criterion3_pass

    # Criterion 4: P95 response time <120s
    criterion4_pass = metrics.p95_duration <= 120
    print(f"\n4. P95 Response Time")
    print(f"   Expected: <120s")
    print(f"   Actual: {metrics.p95_duration:.1f}s")
    print(f"   Status: {' PASS' if criterion4_pass else ' FAIL'}")
    validation_passed = validation_passed and criterion4_pass

    # Criterion 5: P99 response time <150s
    criterion5_pass = metrics.p99_duration <= 150
    print(f"\n5. P99 Response Time")
    print(f"   Expected: <150s")
    print(f"   Actual: {metrics.p99_duration:.1f}s")
    print(f"   Status: {' PASS' if criterion5_pass else ' FAIL'}")
    validation_passed = validation_passed and criterion5_pass

    # Criterion 6: Success rate >99%
    criterion6_pass = metrics.success_rate >= 99.0
    print(f"\n6. Success Rate")
    print(f"   Expected: >99%")
    print(f"   Actual: {metrics.success_rate:.1f}%")
    print(f"   Status: {' PASS' if criterion6_pass else ' FAIL'}")
    validation_passed = validation_passed and criterion6_pass

    print("=" * 80)

    # Phase 6: Print full metrics summary
    print("\n[PHASE 6] Full Metrics Summary")
    print_metrics_summary(metrics)

    # Phase 7: Save results to JSON
    print("\n[PHASE 7] Saving results to JSON...")
    output_path = Path(__file__).parent / OUTPUT_FILE
    save_results_json(metrics, str(output_path))
    print(f" Results saved to: {output_path}")

    # Final result
    print("\n" + "=" * 80)
    if validation_passed:
        print(" NORMAL LOAD TEST PASSED - All criteria met!")
        print("   System handles 3 concurrent users successfully")
        return 0
    else:
        print(" NORMAL LOAD TEST FAILED - Some criteria not met")
        print("   Review metrics above for details")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
