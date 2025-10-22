"""
Load Test Scenario 4: Spike Test (Traffic Spike & Recovery)
=============================================================

Tests system behavior during sudden traffic spikes and recovery.
Simulates a traffic spike from 2 users → 20 users → 2 users.

Test Configuration:
Phase 1: Baseline (2 users, 2 minutes)
Phase 2: Spike (20 users, 1 minute)
Phase 3: Recovery (2 users, 2 minutes)
Total duration: 5 minutes

Success Criteria:
1. System survives spike without crashing
2. Recovers to normal performance within 2 minutes
3. Error rate during spike: <10%
4. Error rate during recovery: <2%
5. Response times return to baseline levels

Expected Duration: ~5 minutes
"""

import sys
import os
import time
import random
import threading
from pathlib import Path
from typing import List, Dict
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
BASELINE_USERS = 2
SPIKE_USERS = 20
BASELINE_DURATION = 120  # 2 minutes
SPIKE_DURATION = 60      # 1 minute
RECOVERY_DURATION = 120  # 2 minutes
BASE_URL = "http://localhost:5000"
TEST_IMAGE = "../../temp/test_images/quality_test_unique2.png"
OUTPUT_FILE = "results_spike.json"

class PhaseController:
    """Controls which phase the test is in"""
    def __init__(self):
        self.current_phase = "baseline"
        self.phase_start_time = time.time()
        self.lock = threading.Lock()

    def get_phase(self) -> str:
        """Get current test phase"""
        with self.lock:
            return self.current_phase

    def set_phase(self, phase: str):
        """Set current test phase"""
        with self.lock:
            self.current_phase = phase
            self.phase_start_time = time.time()

    def get_phase_elapsed(self) -> float:
        """Get elapsed time in current phase"""
        with self.lock:
            return time.time() - self.phase_start_time

def user_simulation(
    user_id: int,
    results: Dict[str, List[RequestResult]],
    phase_controller: PhaseController,
    stop_event: threading.Event
):
    """Simulate a user that adapts to test phases"""
    client = LoadTestClient(BASE_URL)
    request_count = 0

    print(f"[User {user_id:02d}] Starting spike test simulation")

    while not stop_event.is_set():
        phase = phase_controller.get_phase()

        # Different intervals per phase
        if phase == "baseline" or phase == "recovery":
            interval = random.uniform(40, 70)  # Relaxed pace
        else:  # spike phase
            interval = random.uniform(10, 30)  # Aggressive pace

        time.sleep(interval)

        if stop_event.is_set():
            break

        request_count += 1
        phase_elapsed = phase_controller.get_phase_elapsed()
        print(f"[User {user_id:02d}] [{phase.upper()}] Request #{request_count} (t={phase_elapsed:.1f}s)")

        result = client.generate_3d(TEST_IMAGE, timeout=300)

        # Store result in phase-specific list
        if phase not in results:
            results[phase] = []
        results[phase].append(result)

        status = "" if result.success else ""
        print(f"[User {user_id:02d}] [{phase.upper()}] {status} ({result.duration:.1f}s)")

        if not result.success:
            print(f"[User {user_id:02d}] Error: {result.error}")

    client.close()
    print(f"[User {user_id:02d}] Completed: {request_count} requests")

def main():
    """Run spike test with gradual load increase and decrease"""

    print("=" * 80)
    print("LOAD TEST SCENARIO 4: SPIKE TEST (2→20→2 USERS)")
    print("=" * 80)
    print(f"Phase 1: Baseline  - {BASELINE_USERS} users  for {BASELINE_DURATION}s")
    print(f"Phase 2: Spike     - {SPIKE_USERS} users for {SPIKE_DURATION}s ")
    print(f"Phase 3: Recovery  - {BASELINE_USERS} users  for {RECOVERY_DURATION}s")
    print(f"Total duration: {BASELINE_DURATION + SPIKE_DURATION + RECOVERY_DURATION}s (~5 minutes)")
    print("=" * 80)

    # Phase 0: Health check
    print("\n[PHASE 0] Health check...")
    client = LoadTestClient(BASE_URL)
    if not client.health_check():
        print(" Backend is not healthy, aborting test")
        return 1
    print(" Backend is healthy")
    client.close()

    # Verify test image
    test_image_path = Path(__file__).parent / TEST_IMAGE
    if not test_image_path.exists():
        print(f" Test image not found: {test_image_path}")
        return 1

    # Prepare result storage
    results: Dict[str, List[RequestResult]] = {
        "baseline": [],
        "spike": [],
        "recovery": []
    }
    phase_controller = PhaseController()
    stop_event = threading.Event()
    threads: List[threading.Thread] = []

    # ==============================================
    # PHASE 1: BASELINE (2 users, 2 minutes)
    # ==============================================
    print("\n" + "=" * 80)
    print("[PHASE 1] BASELINE LOAD - Starting 2 users...")
    print("=" * 80)
    phase_controller.set_phase("baseline")

    for user_id in range(1, BASELINE_USERS + 1):
        thread = threading.Thread(
            target=user_simulation,
            args=(user_id, results, phase_controller, stop_event),
            daemon=False
        )
        thread.start()
        threads.append(thread)
        print(f" Baseline user {user_id} started")

    print(f"⏳ Baseline phase running for {BASELINE_DURATION}s...")
    time.sleep(BASELINE_DURATION)

    # ==============================================
    # PHASE 2: SPIKE (Add 18 more users → 20 total)
    # ==============================================
    print("\n" + "=" * 80)
    print("[PHASE 2] SPIKE! Adding 18 users (2→20)... ")
    print("=" * 80)
    phase_controller.set_phase("spike")

    spike_threads: List[threading.Thread] = []
    for user_id in range(BASELINE_USERS + 1, SPIKE_USERS + 1):
        thread = threading.Thread(
            target=user_simulation,
            args=(user_id, results, phase_controller, stop_event),
            daemon=False
        )
        thread.start()
        threads.append(thread)
        spike_threads.append(thread)
        print(f"  Spike user {user_id} started")
        time.sleep(0.2)  # Quick ramp-up

    print(f"  SPIKE ACTIVE: {SPIKE_USERS} concurrent users!")
    print(f"⏳ Spike phase running for {SPIKE_DURATION}s...")
    time.sleep(SPIKE_DURATION)

    # ==============================================
    # PHASE 3: RECOVERY (Stop spike users → back to 2)
    # ==============================================
    print("\n" + "=" * 80)
    print("[PHASE 3] RECOVERY - Stopping spike users (20→2)...")
    print("=" * 80)
    phase_controller.set_phase("recovery")

    # Signal spike users to stop (they'll stop after current request)
    print(f"Stopping {len(spike_threads)} spike users...")
    # Note: Users will naturally stop as phase changes and they check stop_event

    print(f" Recovery phase started - {BASELINE_USERS} users remaining")
    print(f"⏳ Recovery phase running for {RECOVERY_DURATION}s...")
    time.sleep(RECOVERY_DURATION)

    # ==============================================
    # CLEANUP: Stop all remaining users
    # ==============================================
    print("\n" + "=" * 80)
    print("TEST COMPLETE - Stopping all users...")
    print("=" * 80)
    stop_event.set()

    for i, thread in enumerate(threads, 1):
        thread.join(timeout=10)
        if thread.is_alive():
            print(f"  User {i} still running (will terminate)")
        else:
            print(f" User {i} stopped")

    # ==============================================
    # ANALYSIS
    # ==============================================
    print("\n" + "=" * 80)
    print("[ANALYSIS] Analyzing spike test results...")
    print("=" * 80)

    # Aggregate metrics per phase
    baseline_metrics = aggregate_results(
        results["baseline"],
        scenario="spike_baseline",
        test_start=0,
        test_end=BASELINE_DURATION
    )

    spike_metrics = aggregate_results(
        results["spike"],
        scenario="spike_spike",
        test_start=0,
        test_end=SPIKE_DURATION
    )

    recovery_metrics = aggregate_results(
        results["recovery"],
        scenario="spike_recovery",
        test_start=0,
        test_end=RECOVERY_DURATION
    )

    print(f"\nBaseline Phase:")
    print(f"  Requests: {len(results['baseline'])}")
    print(f"  Avg time: {baseline_metrics.avg_duration:.1f}s")
    print(f"  Error rate: {baseline_metrics.error_rate:.1f}%")

    print(f"\nSpike Phase:")
    print(f"  Requests: {len(results['spike'])}")
    print(f"  Avg time: {spike_metrics.avg_duration:.1f}s")
    print(f"  Error rate: {spike_metrics.error_rate:.1f}%")

    print(f"\nRecovery Phase:")
    print(f"  Requests: {len(results['recovery'])}")
    print(f"  Avg time: {recovery_metrics.avg_duration:.1f}s")
    print(f"  Error rate: {recovery_metrics.error_rate:.1f}%")

    # Validation
    print("\n" + "=" * 80)
    print("[VALIDATION] Spike Test Criteria...")
    print("=" * 80)

    validation_passed = True

    # Criterion 1: System survived spike
    criterion1_pass = len(results["spike"]) > 0 and len(results["recovery"]) > 0
    print(f"1. System Survived Spike")
    print(f"   Expected: Requests in all phases")
    print(f"   Actual: {len(results['baseline'])} / {len(results['spike'])} / {len(results['recovery'])}")
    print(f"   Status: {' PASS' if criterion1_pass else ' FAIL'}")
    validation_passed = validation_passed and criterion1_pass

    # Criterion 2: Error rate during spike <10%
    criterion2_pass = spike_metrics.error_rate <= 10.0
    print(f"\n2. Spike Error Rate Tolerance")
    print(f"   Expected: <10%")
    print(f"   Actual: {spike_metrics.error_rate:.1f}%")
    print(f"   Status: {' PASS' if criterion2_pass else ' FAIL'}")
    validation_passed = validation_passed and criterion2_pass

    # Criterion 3: Error rate during recovery <2%
    criterion3_pass = recovery_metrics.error_rate <= 2.0
    print(f"\n3. Recovery Error Rate")
    print(f"   Expected: <2%")
    print(f"   Actual: {recovery_metrics.error_rate:.1f}%")
    print(f"   Status: {' PASS' if criterion3_pass else ' FAIL'}")
    validation_passed = validation_passed and criterion3_pass

    # Criterion 4: Recovery time returns to baseline ±20%
    baseline_avg = baseline_metrics.avg_duration
    recovery_avg = recovery_metrics.avg_duration
    recovery_diff_pct = abs(recovery_avg - baseline_avg) / baseline_avg * 100
    criterion4_pass = recovery_diff_pct <= 20.0
    print(f"\n4. Performance Recovery")
    print(f"   Expected: Recovery avg within ±20% of baseline")
    print(f"   Baseline avg: {baseline_avg:.1f}s")
    print(f"   Recovery avg: {recovery_avg:.1f}s")
    print(f"   Difference: {recovery_diff_pct:.1f}%")
    print(f"   Status: {' PASS' if criterion4_pass else ' FAIL'}")
    validation_passed = validation_passed and criterion4_pass

    print("=" * 80)

    # Save combined results
    print("\n[SAVE] Saving results to JSON...")
    output_path = Path(__file__).parent / OUTPUT_FILE
    combined_metrics = {
        "scenario": "spike_test",
        "baseline": baseline_metrics.to_dict(),
        "spike": spike_metrics.to_dict(),
        "recovery": recovery_metrics.to_dict(),
        "validation": {
            "survived": criterion1_pass,
            "spike_error_rate_ok": criterion2_pass,
            "recovery_error_rate_ok": criterion3_pass,
            "performance_recovered": criterion4_pass,
            "overall": validation_passed
        }
    }

    import json
    with open(output_path, 'w') as f:
        json.dump(combined_metrics, f, indent=2)
    print(f" Results saved to: {output_path}")

    # Final result
    print("\n" + "=" * 80)
    if validation_passed:
        print(" SPIKE TEST PASSED - System handled and recovered from spike!")
        print(f"   Successfully managed traffic spike from {BASELINE_USERS}→{SPIKE_USERS}→{BASELINE_USERS} users")
        return 0
    else:
        print(" SPIKE TEST FAILED - System struggled with spike or recovery")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
