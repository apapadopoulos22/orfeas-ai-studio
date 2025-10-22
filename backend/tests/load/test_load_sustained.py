"""
Load Test Scenario 5: Sustained Load (1 Hour Endurance Test)
==============================================================

Tests system stability under sustained load for 1 hour.
Detects memory leaks, resource degradation, and long-term reliability.

Test Configuration:
- Concurrent users: 5
- Test duration: 60 minutes (3600 seconds)
- Requests per user: ~30-60 (random intervals 60-120s)
- Expected total requests: 150-300
- Image: temp/test_images/quality_test_unique2.png

Success Criteria:
1. Server uptime: 99.9% (max 1 error per 1000 requests)
2. No performance degradation over time
3. Memory growth: <5% over test duration
4. GPU memory stable (no leaks)
5. Average response time consistent across duration

Expected Duration: ~60 minutes (1 hour)
"""

import sys
import os
import time
import random
import threading
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import psutil

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
NUM_USERS = 5
TEST_DURATION_SECONDS = 3600  # 60 minutes
MIN_INTERVAL_SECONDS = 60
MAX_INTERVAL_SECONDS = 120
BASE_URL = "http://localhost:5000"
TEST_IMAGE = "../../temp/test_images/quality_test_unique2.png"
OUTPUT_FILE = "results_sustained.json"

# Monitoring configuration
MONITOR_INTERVAL_SECONDS = 60  # Check metrics every minute

class SystemMonitor:
    """Monitor system resources during sustained test"""
    def __init__(self):
        self.samples: List[Dict] = []
        self.monitoring = False
        self.monitor_thread = None

    def start(self):
        """Start monitoring system resources"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("[MONITOR] System monitoring started")

    def stop(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("[MONITOR] System monitoring stopped")

    def _monitor_loop(self):
        """Monitor system resources periodically"""
        while self.monitoring:
            try:
                # CPU and memory
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()

                # Try to get GPU memory if available
                gpu_memory_mb = None
                try:
                    import torch
                    if torch.cuda.is_available():
                        gpu_memory_mb = torch.cuda.memory_allocated() / 1024 / 1024
                except:
                    pass

                sample = {
                    'timestamp': time.time(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_mb': memory.used / 1024 / 1024,
                    'gpu_memory_mb': gpu_memory_mb
                }

                self.samples.append(sample)

                print(f"[MONITOR] CPU: {cpu_percent:.1f}% | "
                      f"RAM: {memory.percent:.1f}% ({memory.used / 1024 / 1024:.0f}MB) | "
                      f"GPU: {gpu_memory_mb:.0f}MB" if gpu_memory_mb else "N/A")

            except Exception as e:
                print(f"[MONITOR] Error: {e}")

            time.sleep(MONITOR_INTERVAL_SECONDS)

    def get_summary(self) -> Dict:
        """Get monitoring summary statistics"""
        if not self.samples:
            return {}

        initial = self.samples[0]
        final = self.samples[-1]

        memory_growth_pct = (
            (final['memory_percent'] - initial['memory_percent']) / initial['memory_percent'] * 100
        )

        avg_cpu = sum(s['cpu_percent'] for s in self.samples) / len(self.samples)
        max_cpu = max(s['cpu_percent'] for s in self.samples)

        summary = {
            'samples_collected': len(self.samples),
            'duration_minutes': (final['timestamp'] - initial['timestamp']) / 60,
            'cpu_avg_percent': avg_cpu,
            'cpu_max_percent': max_cpu,
            'memory_initial_mb': initial['memory_mb'],
            'memory_final_mb': final['memory_mb'],
            'memory_growth_percent': memory_growth_pct
        }

        # Add GPU stats if available
        gpu_samples = [s['gpu_memory_mb'] for s in self.samples if s['gpu_memory_mb'] is not None]
        if gpu_samples:
            summary['gpu_memory_initial_mb'] = gpu_samples[0]
            summary['gpu_memory_final_mb'] = gpu_samples[-1]
            summary['gpu_memory_max_mb'] = max(gpu_samples)
            if gpu_samples[0] > 0:
                gpu_growth_pct = (gpu_samples[-1] - gpu_samples[0]) / gpu_samples[0] * 100
                summary['gpu_memory_growth_percent'] = gpu_growth_pct

        return summary

def user_simulation(user_id: int, results: List[RequestResult], test_start_time: float):
    """Simulate a user making sustained requests"""
    client = LoadTestClient(BASE_URL)
    request_count = 0

    print(f"[User {user_id}] Starting sustained load simulation")

    while True:
        elapsed = time.time() - test_start_time
        if elapsed >= TEST_DURATION_SECONDS:
            print(f"[User {user_id}] Test duration reached (made {request_count} requests)")
            break

        interval = random.uniform(MIN_INTERVAL_SECONDS, MAX_INTERVAL_SECONDS)

        if elapsed + interval > TEST_DURATION_SECONDS:
            print(f"[User {user_id}] Not enough time for another request")
            break

        time.sleep(interval)

        request_count += 1
        elapsed_minutes = elapsed / 60
        print(f"[User {user_id}] Request #{request_count} (t={elapsed_minutes:.1f}min)")

        result = client.generate_3d(TEST_IMAGE, timeout=300)
        results.append(result)

        status = "" if result.success else ""
        print(f"[User {user_id}] {status} #{request_count} ({result.duration:.1f}s)")

        if not result.success:
            print(f"[User {user_id}] Error: {result.error}")

    client.close()
    print(f"[User {user_id}] Completed: {request_count} requests over {elapsed_minutes:.1f} minutes")

def analyze_performance_degradation(results: List[RequestResult], duration_seconds: float) -> Dict:
    """Analyze if performance degrades over time"""
    # Split results into time buckets (e.g., 10-minute intervals)
    bucket_size = 600  # 10 minutes
    num_buckets = int(duration_seconds / bucket_size) + 1

    buckets: List[List[RequestResult]] = [[] for _ in range(num_buckets)]

    for result in results:
        bucket_idx = int(result.timestamp / bucket_size)
        if bucket_idx < num_buckets:
            buckets[bucket_idx].append(result)

    # Calculate average response time per bucket
    bucket_stats = []
    for i, bucket in enumerate(buckets):
        if not bucket:
            continue

        avg_duration = sum(r.duration for r in bucket) / len(bucket)
        error_rate = sum(1 for r in bucket if not r.success) / len(bucket) * 100

        bucket_stats.append({
            'bucket_index': i,
            'time_range_minutes': f"{i*10}-{(i+1)*10}",
            'requests': len(bucket),
            'avg_duration': avg_duration,
            'error_rate': error_rate
        })

    # Check for degradation (later buckets slower than earlier)
    if len(bucket_stats) >= 2:
        first_avg = bucket_stats[0]['avg_duration']
        last_avg = bucket_stats[-1]['avg_duration']
        degradation_pct = (last_avg - first_avg) / first_avg * 100 if first_avg > 0 else 0
    else:
        degradation_pct = 0

    return {
        'bucket_stats': bucket_stats,
        'performance_degradation_percent': degradation_pct
    }

def main():
    """Run sustained load test for 1 hour"""

    print("=" * 80)
    print("LOAD TEST SCENARIO 5: SUSTAINED LOAD (1 HOUR ENDURANCE)")
    print("=" * 80)
    print(f"  WARNING: This test will run for 60 MINUTES")
    print(f"Configuration:")
    print(f"  Concurrent users: {NUM_USERS}")
    print(f"  Test duration: {TEST_DURATION_SECONDS}s ({TEST_DURATION_SECONDS // 60} minutes)")
    print(f"  Request interval: {MIN_INTERVAL_SECONDS}-{MAX_INTERVAL_SECONDS}s per user")
    print(f"  Expected requests: ~150-300 total")
    print(f"  System monitoring: Every {MONITOR_INTERVAL_SECONDS}s")
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

    # Phase 3: Start system monitoring
    print("\n[PHASE 3] Starting system monitoring...")
    monitor = SystemMonitor()
    monitor.start()

    # Phase 4: Run sustained load test
    print("\n[PHASE 4] Starting SUSTAINED LOAD test...")
    print(f"⏳ This will run for {TEST_DURATION_SECONDS // 60} MINUTES - be patient!")
    print(f"   Starting {NUM_USERS} user threads...")

    test_start_time = time.time()
    results: List[RequestResult] = []
    threads: List[threading.Thread] = []

    for user_id in range(1, NUM_USERS + 1):
        thread = threading.Thread(
            target=user_simulation,
            args=(user_id, results, test_start_time),
            daemon=False
        )
        thread.start()
        threads.append(thread)
        print(f" User {user_id} started")
        time.sleep(1)

    print(f"\n All {NUM_USERS} users started - SUSTAINED LOAD ACTIVE!")
    print(f"⏳ Test will run until {datetime.fromtimestamp(test_start_time + TEST_DURATION_SECONDS).strftime('%H:%M:%S')}")

    # Wait for all threads
    for i, thread in enumerate(threads, 1):
        thread.join()
        print(f" User {i} completed")

    test_end_time = time.time()
    actual_duration = test_end_time - test_start_time

    # Stop monitoring
    monitor.stop()

    print(f"\n SUSTAINED LOAD TEST COMPLETED!")
    print(f"   Actual duration: {actual_duration / 60:.1f} minutes")
    print(f"   Total requests: {len(results)}")

    # Phase 5: Aggregate results
    print("\n[PHASE 5] Aggregating results...")
    metrics = aggregate_results(
        results,
        scenario="sustained_load",
        test_start=test_start_time,
        test_end=test_end_time
    )

    # Phase 6: Analyze performance degradation
    print("\n[PHASE 6] Analyzing performance degradation...")
    degradation_analysis = analyze_performance_degradation(results, actual_duration)

    print("Performance over time (10-minute buckets):")
    for bucket in degradation_analysis['bucket_stats']:
        print(f"  {bucket['time_range_minutes']}min: "
              f"{bucket['requests']} reqs, "
              f"avg {bucket['avg_duration']:.1f}s, "
              f"errors {bucket['error_rate']:.1f}%")

    degradation_pct = degradation_analysis['performance_degradation_percent']
    print(f"\nPerformance degradation: {degradation_pct:+.1f}% (first vs last bucket)")

    # Phase 7: System resource analysis
    print("\n[PHASE 7] System resource analysis...")
    monitor_summary = monitor.get_summary()

    print(f"System Resources:")
    print(f"  CPU average: {monitor_summary.get('cpu_avg_percent', 0):.1f}%")
    print(f"  CPU max: {monitor_summary.get('cpu_max_percent', 0):.1f}%")
    print(f"  Memory initial: {monitor_summary.get('memory_initial_mb', 0):.0f}MB")
    print(f"  Memory final: {monitor_summary.get('memory_final_mb', 0):.0f}MB")
    print(f"  Memory growth: {monitor_summary.get('memory_growth_percent', 0):+.1f}%")

    if 'gpu_memory_growth_percent' in monitor_summary:
        print(f"  GPU memory initial: {monitor_summary.get('gpu_memory_initial_mb', 0):.0f}MB")
        print(f"  GPU memory final: {monitor_summary.get('gpu_memory_final_mb', 0):.0f}MB")
        print(f"  GPU memory growth: {monitor_summary.get('gpu_memory_growth_percent', 0):+.1f}%")

    # Phase 8: Validation
    print("\n[PHASE 8] Validating sustained load criteria...")
    print("=" * 80)

    validation_passed = True

    # Criterion 1: Server uptime 99.9%
    criterion1_pass = metrics.error_rate <= 0.1
    print(f"1. Server Uptime (99.9%)")
    print(f"   Expected: Error rate <0.1%")
    print(f"   Actual: {metrics.error_rate:.2f}%")
    print(f"   Status: {' PASS' if criterion1_pass else ' FAIL'}")
    validation_passed = validation_passed and criterion1_pass

    # Criterion 2: No significant performance degradation (<10%)
    criterion2_pass = abs(degradation_pct) <= 10.0
    print(f"\n2. Performance Stability")
    print(f"   Expected: Degradation <10%")
    print(f"   Actual: {degradation_pct:+.1f}%")
    print(f"   Status: {' PASS' if criterion2_pass else ' FAIL'}")
    validation_passed = validation_passed and criterion2_pass

    # Criterion 3: Memory growth <5%
    memory_growth = monitor_summary.get('memory_growth_percent', 0)
    criterion3_pass = memory_growth <= 5.0
    print(f"\n3. Memory Stability (No Leaks)")
    print(f"   Expected: Growth <5%")
    print(f"   Actual: {memory_growth:+.1f}%")
    print(f"   Status: {' PASS' if criterion3_pass else ' FAIL'}")
    validation_passed = validation_passed and criterion3_pass

    # Criterion 4: GPU memory stable (<10% growth)
    if 'gpu_memory_growth_percent' in monitor_summary:
        gpu_growth = monitor_summary.get('gpu_memory_growth_percent', 0)
        criterion4_pass = abs(gpu_growth) <= 10.0
        print(f"\n4. GPU Memory Stability")
        print(f"   Expected: Growth <10%")
        print(f"   Actual: {gpu_growth:+.1f}%")
        print(f"   Status: {' PASS' if criterion4_pass else ' FAIL'}")
        validation_passed = validation_passed and criterion4_pass

    # Criterion 5: Minimum requests completed
    criterion5_pass = len(results) >= 150
    print(f"\n5. Sustained Activity")
    print(f"   Expected: ≥150 requests")
    print(f"   Actual: {len(results)} requests")
    print(f"   Status: {' PASS' if criterion5_pass else ' FAIL'}")
    validation_passed = validation_passed and criterion5_pass

    print("=" * 80)

    # Phase 9: Print full metrics
    print("\n[PHASE 9] Full Metrics Summary")
    print_metrics_summary(metrics)

    # Phase 10: Save results
    print("\n[PHASE 10] Saving results to JSON...")
    output_path = Path(__file__).parent / OUTPUT_FILE

    # Combine all analysis into one JSON
    full_results = {
        **metrics.to_dict(),
        'degradation_analysis': degradation_analysis,
        'system_monitoring': monitor_summary,
        'validation': {
            'uptime_ok': criterion1_pass,
            'performance_stable': criterion2_pass,
            'memory_stable': criterion3_pass,
            'sustained_activity': criterion5_pass,
            'overall': validation_passed
        }
    }

    import json
    with open(output_path, 'w') as f:
        json.dump(full_results, f, indent=2)
    print(f" Results saved to: {output_path}")

    # Final result
    print("\n" + "=" * 80)
    if validation_passed:
        print(" SUSTAINED LOAD TEST PASSED - System is production-ready!")
        print(f"   Successfully ran for {actual_duration / 60:.1f} minutes with {NUM_USERS} users")
        print(f"   Completed {len(results)} requests with {metrics.success_rate:.1f}% success rate")
        return 0
    else:
        print(" SUSTAINED LOAD TEST FAILED - System not ready for production")
        print("   Review metrics for memory leaks or performance degradation")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
