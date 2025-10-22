"""
Load Test Scenario 3: Peak Load (10 Concurrent Users)
========================================================

Simulates peak traffic with 10 concurrent users making
generation requests to test system limits.

Test Configuration:
- Concurrent users: 10
- Test duration: 5 minutes (300 seconds)
- Requests per user: ~5-10 (random intervals 20-60s)
- Expected total requests: 50-100
- Image: temp/test_images/quality_test_unique2.png

Success Criteria:
1. Server uptime: ≥99% (max 3 failed requests)
2. Error rate: <5%
3. Average response time: <150s
4. P95 response time: <180s
5. At least 50 successful completions

Expected Duration: ~5 minutes
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
NUM_USERS = 10
TEST_DURATION_SECONDS = 300  # 5 minutes
MIN_INTERVAL_SECONDS = 20
MAX_INTERVAL_SECONDS = 60
BASE_URL = "http://localhost:5000"
TEST_IMAGE = "../../temp/test_images/quality_test_unique2.png"
OUTPUT_FILE = "results_peak.json"

def user_simulation(user_id: int, results: List[RequestResult], test_start_time: float):
    """Simulate a single user making requests during peak load"""
    client = LoadTestClient(BASE_URL)
    request_count = 0

    print(f"[User {user_id:02d}] Starting peak load simulation")

    while True:
        elapsed = time.time() - test_start_time
        if elapsed >= TEST_DURATION_SECONDS:
            print(f"[User {user_id:02d}] Test duration reached (made {request_count} requests)")
            break

        interval = random.uniform(MIN_INTERVAL_SECONDS, MAX_INTERVAL_SECONDS)

        if elapsed + interval > TEST_DURATION_SECONDS:
            print(f"[User {user_id:02d}] Not enough time for another request")
            break

        time.sleep(interval)

        request_count += 1
        print(f"[User {user_id:02d}] Request #{request_count} (t={elapsed:.1f}s)")

        result = client.generate_3d(TEST_IMAGE, timeout=300)
        results.append(result)

        status = "" if result.success else ""
        print(f"[User {user_id:02d}] {status} #{request_count} ({result.duration:.1f}s)")

        if not result.success:
            print(f"[User {user_id:02d}] Error: {result.error}")

    client.close()
    print(f"[User {user_id:02d}] Completed: {request_count} requests")

def main():
    """Run peak load test with 10 concurrent users"""

    print("=" * 80)
    print("LOAD TEST SCENARIO 3: PEAK LOAD (10 CONCURRENT USERS)")
    print("=" * 80)
    print(f"Configuration:")
    print(f"  Concurrent users: {NUM_USERS}")
    print(f"  Test duration: {TEST_DURATION_SECONDS}s ({TEST_DURATION_SECONDS // 60} minutes)")
    print(f"  Request interval: {MIN_INTERVAL_SECONDS}-{MAX_INTERVAL_SECONDS}s per user")
    print(f"  Expected requests: ~50-100 total")
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

    # Phase 2: Verify test image
    print("\n[PHASE 2] Verifying test image...")
    test_image_path = Path(__file__).parent / TEST_IMAGE
    if not test_image_path.exists():
        print(f" Test image not found: {test_image_path}")
        return 1
    print(f" Test image exists")

    # Phase 3: Run concurrent user simulations
    print("\n[PHASE 3] Starting PEAK LOAD test...")
    print(f"  WARNING: This will stress-test the system with {NUM_USERS} concurrent users")
    print(f"   Starting {NUM_USERS} user threads...")

    test_start_time = time.time()
    results: List[RequestResult] = []
    threads: List[threading.Thread] = []

    # Start all user threads quickly to create peak load
    for user_id in range(1, NUM_USERS + 1):
        thread = threading.Thread(
            target=user_simulation,
            args=(user_id, results, test_start_time),
            daemon=False
        )
        thread.start()
        threads.append(thread)
        print(f" User {user_id:02d} started")
        time.sleep(0.5)  # Minimal delay to avoid overwhelming initial connection

    print(f"\n All {NUM_USERS} users started - PEAK LOAD ACTIVE!")
    print(f"⏳ Test running for {TEST_DURATION_SECONDS}s ({TEST_DURATION_SECONDS // 60} minutes)...")

    # Wait for all threads
    for i, thread in enumerate(threads, 1):
        thread.join()
        print(f" User {i:02d} completed")

    test_end_time = time.time()
    actual_duration = test_end_time - test_start_time

    print(f"\n PEAK LOAD TEST COMPLETED!")
    print(f"   Actual duration: {actual_duration:.1f}s")
    print(f"   Total requests: {len(results)}")

    # Phase 4: Aggregate results
    print("\n[PHASE 4] Aggregating results...")
    metrics = aggregate_results(
        results,
        scenario="peak_load",
        test_start=test_start_time,
        test_end=test_end_time
    )

    # Phase 5: Validate results
    print("\n[PHASE 5] Validating results (Peak Load Criteria)...")
    print("=" * 80)

    validation_passed = True

    # Criterion 1: At least 50 requests attempted
    criterion1_pass = len(results) >= 50
    print(f"1. Minimum Load Achieved")
    print(f"   Expected: ≥50 requests")
    print(f"   Actual: {len(results)} requests")
    print(f"   Status: {' PASS' if criterion1_pass else ' FAIL'}")
    validation_passed = validation_passed and criterion1_pass

    # Criterion 2: Server uptime ≥99% (max 1% failed)
    criterion2_pass = metrics.error_rate <= 5.0
    print(f"\n2. Error Rate (Peak Load Tolerance)")
    print(f"   Expected: <5% (peak load allows some errors)")
    print(f"   Actual: {metrics.error_rate:.2f}%")
    print(f"   Status: {' PASS' if criterion2_pass else ' FAIL'}")
    validation_passed = validation_passed and criterion2_pass

    # Criterion 3: Average response time <150s (higher tolerance for peak)
    criterion3_pass = metrics.avg_duration <= 150
    print(f"\n3. Average Response Time (Peak Load)")
    print(f"   Expected: <150s")
    print(f"   Actual: {metrics.avg_duration:.1f}s")
    print(f"   Status: {' PASS' if criterion3_pass else ' FAIL'}")
    validation_passed = validation_passed and criterion3_pass

    # Criterion 4: P95 response time <180s
    criterion4_pass = metrics.p95_duration <= 180
    print(f"\n4. P95 Response Time")
    print(f"   Expected: <180s")
    print(f"   Actual: {metrics.p95_duration:.1f}s")
    print(f"   Status: {' PASS' if criterion4_pass else ' FAIL'}")
    validation_passed = validation_passed and criterion4_pass

    # Criterion 5: At least 50 successful completions
    successful_count = sum(1 for r in results if r.success)
    criterion5_pass = successful_count >= 50
    print(f"\n5. Successful Completions")
    print(f"   Expected: ≥50 successful")
    print(f"   Actual: {successful_count} successful")
    print(f"   Status: {' PASS' if criterion5_pass else ' FAIL'}")
    validation_passed = validation_passed and criterion5_pass

    print("=" * 80)

    # Phase 6: Print full metrics
    print("\n[PHASE 6] Full Metrics Summary")
    print_metrics_summary(metrics)

    # Phase 7: Save results
    print("\n[PHASE 7] Saving results to JSON...")
    output_path = Path(__file__).parent / OUTPUT_FILE
    save_results_json(metrics, str(output_path))
    print(f" Results saved to: {output_path}")

    # Final result
    print("\n" + "=" * 80)
    if validation_passed:
        print(" PEAK LOAD TEST PASSED - System handled peak load!")
        print(f"   Successfully processed {successful_count} requests with {NUM_USERS} concurrent users")
        return 0
    else:
        print(" PEAK LOAD TEST FAILED - System struggled under peak load")
        print("   Consider scaling or optimization")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
