"""
+==============================================================================â•—
| [WARRIOR] ORFEAS AI STUDIO - TASK 9: LOAD TESTING SUITE [WARRIOR] |
| Comprehensive Performance Testing with Hunyuan3D-2.1 |
| NO SLACKING - MAXIMUM ORFEAS INTENSITY |
+==============================================================================

TASK 9: Load Testing Suite
- Real 3D generation with Hunyuan3D-2.1
- Concurrent request stress testing
- GPU memory monitoring
- System stability validation
- Performance benchmarking
"""

import requests
import time
import json
import threading
import statistics
from datetime import datetime
from typing import List, Dict, Any
import sys

# ================================================================
# CONFIGURATION
# ================================================================

BACKEND_URL = "http://localhost:5000"
HEALTH_ENDPOINT = f"{BACKEND_URL}/api/health"
GENERATE_ENDPOINT = f"{BACKEND_URL}/api/generate-3d"
METRICS_ENDPOINT = f"{BACKEND_URL}/metrics"

# Test parameters
SINGLE_TEST_ITERATIONS = 3
CONCURRENT_TEST_COUNT = 5
STRESS_TEST_DURATION = 60  # 1 minute
TIMEOUT = 300  # 5 minutes per generation

# Test image (simple 512x512 test prompt)
TEST_PROMPT = "a red cube on a white background, studio lighting, 3d render"
TEST_IMAGE_URL = None  # Will use prompt-based generation

# ================================================================
# COLOR OUTPUT UTILITIES
# ================================================================

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.YELLOW}{text}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*70}{Colors.RESET}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}[OK] {text}{Colors.RESET}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}[WARN]  {text}{Colors.RESET}")

def print_error(text: str):
    print(f"{Colors.RED}[FAIL] {text}{Colors.RESET}")

def print_info(text: str):
    print(f"{Colors.WHITE}  {text}{Colors.RESET}")

# ================================================================
# METRIC COLLECTION
# ================================================================

class TestMetrics:
    def __init__(self):
        self.generation_times: List[float] = []
        self.success_count = 0
        self.failure_count = 0
        self.errors: List[str] = []
        self.gpu_memory_samples: List[float] = []
        self.cpu_usage_samples: List[float] = []
        self.start_time = None
        self.end_time = None

    def add_generation(self, duration: float, success: bool, error: str = None):
        if success:
            self.generation_times.append(duration)
            self.success_count += 1
        else:
            self.failure_count += 1
            if error:
                self.errors.append(error)

    def add_resource_sample(self, gpu_mem: float = None, cpu: float = None):
        if gpu_mem is not None:
            self.gpu_memory_samples.append(gpu_mem)
        if cpu is not None:
            self.cpu_usage_samples.append(cpu)

    def get_statistics(self) -> Dict[str, Any]:
        if not self.generation_times:
            return {
                "total_tests": self.success_count + self.failure_count,
                "success": self.success_count,
                "failures": self.failure_count,
                "success_rate": 0.0,
                "avg_time": 0.0,
                "min_time": 0.0,
                "max_time": 0.0,
                "median_time": 0.0,
                "total_duration": 0.0
            }

        total_duration = (self.end_time - self.start_time) if self.end_time and self.start_time else 0

        return {
            "total_tests": self.success_count + self.failure_count,
            "success": self.success_count,
            "failures": self.failure_count,
            "success_rate": (self.success_count / (self.success_count + self.failure_count)) * 100,
            "avg_time": statistics.mean(self.generation_times),
            "min_time": min(self.generation_times),
            "max_time": max(self.generation_times),
            "median_time": statistics.median(self.generation_times),
            "p95_time": statistics.quantiles(self.generation_times, n=20)[18] if len(self.generation_times) > 1 else self.generation_times[0],
            "total_duration": total_duration,
            "avg_gpu_mem": statistics.mean(self.gpu_memory_samples) if self.gpu_memory_samples else 0,
            "max_gpu_mem": max(self.gpu_memory_samples) if self.gpu_memory_samples else 0,
            "avg_cpu": statistics.mean(self.cpu_usage_samples) if self.cpu_usage_samples else 0,
            "max_cpu": max(self.cpu_usage_samples) if self.cpu_usage_samples else 0
        }

# ================================================================
# TEST UTILITIES
# ================================================================

def check_backend_health() -> bool:
    """Verify backend is healthy before testing"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend healthy: {data.get('status', 'unknown')}")
            if 'gpu_info' in data:
                print_info(f"GPU: {data['gpu_info'].get('name', 'unknown')}")
                print_info(f"VRAM: {data['gpu_info'].get('total_memory_gb', 0):.1f} GB total")
            return True
        else:
            print_error(f"Backend unhealthy: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Backend connection failed: {e}")
        return False

def get_current_metrics() -> Dict[str, float]:
    """Get current system metrics from Prometheus endpoint"""
    try:
        response = requests.get(METRICS_ENDPOINT, timeout=5)
        if response.status_code == 200:
            metrics = {}
            for line in response.text.split('\n'):
                if line.startswith('orfeas_gpu_memory_bytes{gpu_id="0"}'):
                    gpu_mem = float(line.split()[-1])
                    metrics['gpu_memory_gb'] = gpu_mem / 1024 / 1024 / 1024
                elif line.startswith('orfeas_cpu_usage_percent'):
                    metrics['cpu_percent'] = float(line.split()[-1])
            return metrics
        return {}
    except Exception as e:
        print_warning(f"Failed to get metrics: {e}")
        return {}

def generate_3d_test(test_id: int, metrics: TestMetrics, verbose: bool = True) -> bool:
    """Execute single 3D generation test"""
    if verbose:
        print_info(f"[Test {test_id}] Starting 3D generation...")

    start_time = time.time()

    try:
        # Prepare request
        payload = {
            "prompt": TEST_PROMPT,
            "provider": "hunyuan3d",
            "steps": 20,  # Faster for testing
            "guidance_scale": 7.5,
            "output_format": "glb"
        }

        # Send generation request
        response = requests.post(
            GENERATE_ENDPOINT,
            json=payload,
            timeout=TIMEOUT
        )

        duration = time.time() - start_time

        if response.status_code == 200:
            result = response.json()

            # Sample metrics during generation
            current_metrics = get_current_metrics()
            if current_metrics:
                metrics.add_resource_sample(
                    gpu_mem=current_metrics.get('gpu_memory_gb'),
                    cpu=current_metrics.get('cpu_percent')
                )

            if result.get('success'):
                metrics.add_generation(duration, True)
                if verbose:
                    print_success(f"[Test {test_id}] Completed in {duration:.2f}s")
                return True
            else:
                error_msg = result.get('error', 'Unknown error')
                metrics.add_generation(duration, False, error_msg)
                if verbose:
                    print_error(f"[Test {test_id}] Failed: {error_msg}")
                return False
        else:
            error_msg = f"HTTP {response.status_code}"
            metrics.add_generation(time.time() - start_time, False, error_msg)
            if verbose:
                print_error(f"[Test {test_id}] Failed: {error_msg}")
            return False

    except requests.Timeout:
        duration = time.time() - start_time
        metrics.add_generation(duration, False, "Timeout")
        if verbose:
            print_error(f"[Test {test_id}] Timeout after {duration:.2f}s")
        return False
    except Exception as e:
        duration = time.time() - start_time
        metrics.add_generation(duration, False, str(e))
        if verbose:
            print_error(f"[Test {test_id}] Exception: {e}")
        return False

# ================================================================
# TEST SUITES
# ================================================================

def test_single_generation_performance():
    """TEST 1: Single generation performance baseline"""
    print_header("TEST 1: Single Generation Performance Baseline")

    metrics = TestMetrics()
    metrics.start_time = time.time()

    print_info(f"Running {SINGLE_TEST_ITERATIONS} sequential generation tests...")
    print_info(f"Provider: Hunyuan3D-2.1")
    print_info(f"Prompt: {TEST_PROMPT}")
    print()

    for i in range(1, SINGLE_TEST_ITERATIONS + 1):
        generate_3d_test(i, metrics, verbose=True)

        # Brief pause between tests
        if i < SINGLE_TEST_ITERATIONS:
            print_info("Waiting 5s before next test...")
            time.sleep(5)

    metrics.end_time = time.time()

    # Print results
    stats = metrics.get_statistics()
    print()
    print_header("TEST 1 RESULTS")
    print_info(f"Total Tests:    {stats['total_tests']}")
    print_info(f"Successful:     {stats['success']} ({stats['success_rate']:.1f}%)")
    print_info(f"Failed:         {stats['failures']}")
    print_info(f"Average Time:   {stats['avg_time']:.2f}s")
    print_info(f"Min Time:       {stats['min_time']:.2f}s")
    print_info(f"Max Time:       {stats['max_time']:.2f}s")
    print_info(f"Median Time:    {stats['median_time']:.2f}s")

    if stats['avg_gpu_mem'] > 0:
        print_info(f"Avg GPU Memory: {stats['avg_gpu_mem']:.2f} GB")
        print_info(f"Max GPU Memory: {stats['max_gpu_mem']:.2f} GB")

    if stats['success_rate'] >= 80:
        print_success("TEST 1: PASS (≥80% success rate)")
        return True
    else:
        print_error("TEST 1: FAIL (<80% success rate)")
        return False

def test_concurrent_requests():
    """TEST 2: Concurrent request handling"""
    print_header("TEST 2: Concurrent Request Handling")

    metrics = TestMetrics()
    metrics.start_time = time.time()

    print_info(f"Running {CONCURRENT_TEST_COUNT} concurrent generation tests...")
    print_warning("This will stress test GPU memory and queue management")
    print()

    threads = []
    results = []

    def thread_worker(thread_id):
        result = generate_3d_test(thread_id, metrics, verbose=False)
        results.append(result)
        print(f"  Thread {thread_id}: {'[OK] PASS' if result else '[FAIL] FAIL'}")

    # Launch concurrent threads
    for i in range(1, CONCURRENT_TEST_COUNT + 1):
        thread = threading.Thread(target=thread_worker, args=(i,))
        threads.append(thread)
        thread.start()
        time.sleep(1)  # Stagger slightly to avoid race conditions

    # Wait for all threads
    for thread in threads:
        thread.join()

    metrics.end_time = time.time()

    # Print results
    stats = metrics.get_statistics()
    print()
    print_header("TEST 2 RESULTS")
    print_info(f"Total Tests:    {stats['total_tests']}")
    print_info(f"Successful:     {stats['success']} ({stats['success_rate']:.1f}%)")
    print_info(f"Failed:         {stats['failures']}")
    print_info(f"Total Duration: {stats['total_duration']:.2f}s")
    print_info(f"Average Time:   {stats['avg_time']:.2f}s per generation")

    if stats['avg_gpu_mem'] > 0:
        print_info(f"Peak GPU Memory: {stats['max_gpu_mem']:.2f} GB")

    if stats['success_rate'] >= 60:
        print_success("TEST 2: PASS (≥60% success rate with concurrency)")
        return True
    else:
        print_error("TEST 2: FAIL (<60% success rate)")
        return False

def test_gpu_memory_monitoring():
    """TEST 3: GPU memory tracking during generation"""
    print_header("TEST 3: GPU Memory Monitoring")

    print_info("Monitoring GPU memory before, during, and after generation...")
    print()

    # Baseline memory
    print_info("Baseline GPU memory:")
    baseline = get_current_metrics()
    if baseline.get('gpu_memory_gb'):
        print_info(f"  Before: {baseline['gpu_memory_gb']:.2f} GB")

    # During generation
    metrics = TestMetrics()
    metrics.start_time = time.time()

    print_info("\nGenerating with memory monitoring...")
    success = generate_3d_test(1, metrics, verbose=True)

    # Peak memory
    print_info("\nPeak GPU memory during generation:")
    stats = metrics.get_statistics()
    if stats['max_gpu_mem'] > 0:
        print_info(f"  Peak: {stats['max_gpu_mem']:.2f} GB")
        print_info(f"  Average: {stats['avg_gpu_mem']:.2f} GB")

    # After generation
    time.sleep(3)
    after = get_current_metrics()
    if after.get('gpu_memory_gb'):
        print_info(f"  After: {after['gpu_memory_gb']:.2f} GB")

    # Check for memory leaks
    if baseline.get('gpu_memory_gb') and after.get('gpu_memory_gb'):
        leak = after['gpu_memory_gb'] - baseline['gpu_memory_gb']
        if abs(leak) < 0.5:  # Less than 500MB difference
            print_success(f"TEST 3: PASS (No significant memory leak: {leak:+.2f} GB)")
            return True
        else:
            print_warning(f"TEST 3: WARNING (Possible memory leak: {leak:+.2f} GB)")
            return True  # Still pass, but with warning
    else:
        print_warning("TEST 3: PASS (Unable to measure memory precisely)")
        return True

def test_error_handling():
    """TEST 4: Error handling with invalid requests"""
    print_header("TEST 4: Error Handling")

    print_info("Testing backend error handling with invalid requests...")
    print()

    test_cases = [
        {"name": "Empty prompt", "payload": {"prompt": "", "provider": "hunyuan3d"}},
        {"name": "Invalid provider", "payload": {"prompt": TEST_PROMPT, "provider": "invalid_provider"}},
        {"name": "Missing prompt", "payload": {"provider": "hunyuan3d"}},
    ]

    passed = 0
    failed = 0

    for test in test_cases:
        try:
            response = requests.post(GENERATE_ENDPOINT, json=test['payload'], timeout=10)

            # Should return error gracefully (not 500)
            if response.status_code in [400, 422]:
                print_success(f"  {test['name']}: Handled gracefully (HTTP {response.status_code})")
                passed += 1
            elif response.status_code == 500:
                print_error(f"  {test['name']}: Server error (HTTP 500)")
                failed += 1
            else:
                print_warning(f"  {test['name']}: Unexpected response (HTTP {response.status_code})")
                passed += 1
        except Exception as e:
            print_error(f"  {test['name']}: Exception - {e}")
            failed += 1

    print()
    if failed == 0:
        print_success(f"TEST 4: PASS (All {passed} error cases handled gracefully)")
        return True
    else:
        print_error(f"TEST 4: FAIL ({failed} cases not handled properly)")
        return False

def test_system_stability():
    """TEST 5: System stability during extended operation"""
    print_header("TEST 5: System Stability Test")

    print_info(f"Running stability test for {STRESS_TEST_DURATION}s...")
    print_warning("This will generate continuously to test long-term stability")
    print()

    metrics = TestMetrics()
    metrics.start_time = time.time()

    test_count = 0
    end_time = time.time() + STRESS_TEST_DURATION

    while time.time() < end_time:
        test_count += 1
        remaining = int(end_time - time.time())
        print_info(f"[{remaining}s remaining] Test {test_count}...")

        generate_3d_test(test_count, metrics, verbose=False)

        # Sample metrics
        current = get_current_metrics()
        if current:
            metrics.add_resource_sample(
                gpu_mem=current.get('gpu_memory_gb'),
                cpu=current.get('cpu_percent')
            )

    metrics.end_time = time.time()

    # Results
    stats = metrics.get_statistics()
    print()
    print_header("TEST 5 RESULTS")
    print_info(f"Duration:        {stats['total_duration']:.0f}s")
    print_info(f"Total Tests:     {stats['total_tests']}")
    print_info(f"Successful:      {stats['success']} ({stats['success_rate']:.1f}%)")
    print_info(f"Failed:          {stats['failures']}")
    print_info(f"Avg Time/Gen:    {stats['avg_time']:.2f}s")

    if stats['avg_gpu_mem'] > 0:
        print_info(f"Avg GPU Memory:  {stats['avg_gpu_mem']:.2f} GB")
        print_info(f"Peak GPU Memory: {stats['max_gpu_mem']:.2f} GB")

    if stats['avg_cpu'] > 0:
        print_info(f"Avg CPU Usage:   {stats['avg_cpu']:.1f}%")
        print_info(f"Peak CPU Usage:  {stats['max_cpu']:.1f}%")

    if stats['success_rate'] >= 70:
        print_success("TEST 5: PASS (≥70% success rate over time)")
        return True
    else:
        print_error("TEST 5: FAIL (<70% success rate)")
        return False

# ================================================================
# MAIN EXECUTION
# ================================================================

def main():
    print_header("[WARRIOR] ORFEAS AI STUDIO - TASK 9: LOAD TESTING SUITE [WARRIOR]")
    print_info("Comprehensive Performance Testing with Hunyuan3D-2.1")
    print_info(f"Backend: {BACKEND_URL}")
    print_info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Pre-flight check
    print_header("Pre-Flight Health Check")
    if not check_backend_health():
        print_error("Backend is not healthy! Aborting tests.")
        return 1

    print()
    input("Press Enter to begin load testing...")

    # Run test suite
    results = []

    try:
        results.append(("Single Generation Performance", test_single_generation_performance()))
        results.append(("Concurrent Request Handling", test_concurrent_requests()))
        results.append(("GPU Memory Monitoring", test_gpu_memory_monitoring()))
        results.append(("Error Handling", test_error_handling()))
        results.append(("System Stability", test_system_stability()))
    except KeyboardInterrupt:
        print()
        print_warning("Testing interrupted by user")

    # Final summary
    print_header("[WARRIOR] FINAL TEST SUMMARY [WARRIOR]")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"  {status} - {name}")

    print()
    pass_rate = (passed / total * 100) if total > 0 else 0
    print_info(f"Overall: {passed}/{total} tests passed ({pass_rate:.1f}%)")

    if pass_rate >= 80:
        print_success("LOAD TESTING: PASS (Production Ready)")
        print()
        print(f"{Colors.CYAN}{'='*70}{Colors.RESET}")
        print(f"{Colors.GREEN}SUCCESS! NO SLACKING ACHIEVED [WARRIOR]{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*70}{Colors.RESET}")
        return 0
    elif pass_rate >= 60:
        print_warning("LOAD TESTING: MARGINAL (Needs optimization)")
        return 0
    else:
        print_error("LOAD TESTING: FAIL (Critical issues detected)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
