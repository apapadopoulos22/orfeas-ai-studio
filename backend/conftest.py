"""
BOB AI v9.0 - pytest Configuration and Test Runner
Comprehensive testing setup for 200+ tests

Created: October 27, 2025
Version: 9.0.0
"""

import pytest
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Auto-tag tests based on naming conventions"""
    for item in items:
        # Tag unit tests
        if "test_" in item.nodeid and "integration" not in item.nodeid:
            item.add_marker(pytest.mark.unit)

        # Tag integration tests
        if "integration" in item.nodeid or "EndToEnd" in item.nodeid:
            item.add_marker(pytest.mark.integration)

        # Tag performance tests
        if "Performance" in item.nodeid or "performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)

        # Tag slow tests
        if "slow" in item.nodeid or "concurrent" in item.nodeid:
            item.add_marker(pytest.mark.slow)


# Test suite configurations
TEST_SUITES = {
    "unit": {
        "description": "Unit tests only (fast)",
        "args": ["-m", "unit", "-v", "--tb=short"],
        "timeout": 300,
    },
    "integration": {
        "description": "Integration tests only",
        "args": ["-m", "integration", "-v", "--tb=short"],
        "timeout": 600,
    },
    "performance": {
        "description": "Performance benchmarks",
        "args": ["-m", "performance", "-v", "--tb=short"],
        "timeout": 900,
    },
    "all": {
        "description": "All tests",
        "args": ["-v", "--tb=short", "--durations=10"],
        "timeout": 1800,
    },
    "quick": {
        "description": "Quick smoke test (not slow)",
        "args": ["-m", "not slow", "-v", "--tb=short"],
        "timeout": 300,
    },
}


def get_pytest_args(suite: str = "quick") -> list:
    """Get pytest arguments for a test suite"""
    return TEST_SUITES.get(suite, TEST_SUITES["quick"])["args"]


def run_test_suite(suite: str = "quick") -> int:
    """Run a specific test suite"""
    suite_config = TEST_SUITES.get(suite, TEST_SUITES["quick"])
    print(f"\n{'='*70}")
    print(f"Running: {suite_config['description']}")
    print(f"Timeout: {suite_config['timeout']}s")
    print(f"{'='*70}\n")

    return pytest.main(suite_config["args"] + [__file__])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run BOB AI v9.0 test suites")
    parser.add_argument(
        "suite",
        nargs="?",
        default="quick",
        choices=list(TEST_SUITES.keys()),
        help="Test suite to run"
    )
    parser.add_argument(
        "-x",
        "--exitfirst",
        action="store_true",
        help="Exit on first failure"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "-s",
        "--capture",
        action="store_false",
        help="Don't capture output"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )

    args = parser.parse_args()

    # Build custom args
    custom_args = TEST_SUITES[args.suite]["args"].copy()

    if args.exitfirst:
        custom_args.append("-x")

    if args.capture:
        custom_args.append("-s")

    if args.coverage:
        custom_args.extend([
            "--cov=.",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])

    # Run pytest
    exit_code = pytest.main(custom_args + [__file__])

    print(f"\n{'='*70}")
    if exit_code == 0:
        print("✅ ALL TESTS PASSED")
    else:
        print(f"❌ TESTS FAILED (exit code: {exit_code})")
    print(f"{'='*70}\n")

    sys.exit(exit_code)
