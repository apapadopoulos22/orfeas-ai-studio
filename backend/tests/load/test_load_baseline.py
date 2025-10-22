"""
ORFEAS Load Test - Scenario 1: Baseline
========================================
Single user validation test

Purpose: Verify single generation matches 82s baseline from Phase 2.3

Configuration:
- Concurrent users: 1
- Total generations: 5
- Expected duration: ~410s (5 √ó 82s)
- Image: 512√ó512 PNG

Success Criteria:
- Average generation time: 75-90s (±10% of 82s baseline)
- 0 errors
- GPU utilization: 60-70%
- All metrics updating correctly

ORFEAS AI Project
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.load.load_test_utils import (
    LoadTestClient,
    aggregate_results,
    print_metrics_summary,
    save_results_json
)


def run_baseline_test() -> int:
    """Run baseline load test with single user"""

    print("=" * 80)
    print("ORFEAS LOAD TEST - BASELINE (Scenario 1)")
    print("=" * 80)
    print("Configuration:")
    print("  - Users: 1")
    print("  - Generations: 5")
    print("  - Expected time: ~410s (5 √ó 82s baseline)")
    print("  - Image: temp/test_images/quality_test_unique2.png")
    print("=" * 80)
    print()

    # Initialize client
    client = LoadTestClient(base_url="http://localhost:5000")

    # Check server health
    print("[1/4] Checking server health...")
    if not client.health_check():
        print("'ùå Server health check failed!")
        print("Please ensure backend is running: cd backend && python main.py")
        return 1
    print("'úÖ Server healthy")
    print()

    # Check test image exists
    test_image = Path("temp/test_images/quality_test_unique2.png")
    if not test_image.exists():
        print(f"'ùå Test image not found: {test_image}")
        print("Creating test image...")
        import subprocess
        subprocess.run(["python", "create_test_image.py", str(test_image)], check=True)
        print("'úÖ Test image created")
    else:
        print(f"'úÖ Test image found: {test_image}")
    print()

    # Run test
    print("[2/4] Running baseline test...")
    print("Expected duration: ~410 seconds (6-7 minutes)")
    print("Please wait...\n")

    results = []
    start_time = datetime.now()

    for i in range(5):
        print(f"Generation {i+1}/5...")
        gen_start = time.time()

        result = client.generate_3d(str(test_image), timeout=300)
        results.append(result)

        gen_duration = time.time() - gen_start
        status_icon = "'úÖ" if result.success else "'ùå"
        print(f"  {status_icon} Duration: {gen_duration:.1f}s | Status: {result.status_code}")

        if not result.success:
            print(f"    Error: {result.error}")

    end_time = datetime.now()
    print()

    # Aggregate results
    print("[3/4] Analyzing results...")
    metrics = aggregate_results(results, "Baseline (1 user, 5 generations)", start_time, end_time)

    # Print summary
    print_metrics_summary(metrics)

    # Validate against success criteria
    print("[4/4] Validating success criteria...")
    validation_results = []

    # Check 1: Average time within ±10% of 82s baseline
    baseline = 82.0
    tolerance = 0.10
    min_expected = baseline * (1 - tolerance)
    max_expected = baseline * (1 + tolerance)

    avg_in_range = min_expected <= metrics.avg_duration <= max_expected
    validation_results.append({
        'check': 'Average generation time',
        'expected': f'{min_expected:.1f}s - {max_expected:.1f}s (±10% of 82s)',
        'actual': f'{metrics.avg_duration:.1f}s',
        'pass': avg_in_range
    })

    # Check 2: Zero errors
    no_errors = metrics.failed_requests == 0
    validation_results.append({
        'check': 'Zero errors',
        'expected': '0 errors',
        'actual': f'{metrics.failed_requests} errors',
        'pass': no_errors
    })

    # Check 3: Success rate 100%
    perfect_success = metrics.success_rate == 100.0
    validation_results.append({
        'check': 'Success rate',
        'expected': '100%',
        'actual': f'{metrics.success_rate:.1f}%',
        'pass': perfect_success
    })

    # Check 4: All requests completed
    all_completed = metrics.total_requests == 5
    validation_results.append({
        'check': 'All generations completed',
        'expected': '5 generations',
        'actual': f'{metrics.total_requests} generations',
        'pass': all_completed
    })

    # Print validation results
    print("\nValidation Results:")
    print("-" * 80)
    for check in validation_results:
        status = "'úÖ PASS" if check['pass'] else "'ùå FAIL"
        print(f"{status} | {check['check']}")
        print(f"         Expected: {check['expected']}")
        print(f"         Actual:   {check['actual']}")
        print()

    # Overall result
    all_passed = all(check['pass'] for check in validation_results)

    print("=" * 80)
    if all_passed:
        print("üéâ BASELINE TEST PASSED")
        print("System performance matches expected baseline (82s warm cache)")
    else:
        print("  BASELINE TEST FAILED")
        print("Some validation criteria not met - investigate performance issues")
    print("=" * 80)
    print()

    # Save results
    output_path = Path("backend/tests/load/results_baseline.json")
    save_results_json(metrics, str(output_path))

    # Cleanup
    client.close()

    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        exit_code = run_baseline_test()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n'ùå Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
