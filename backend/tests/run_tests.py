"""
+==============================================================================â•—
|              ORFEAS Testing Suite - Test Runner & Configuration             |
|                    Parallel test execution with maximum efficiency           |
+=============================================================================='ïù
"""
import subprocess
import sys
from pathlib import Path
import multiprocessing


def run_tests_parallel():
    """Run tests in parallel using all CPU cores."""
    num_cores = multiprocessing.cpu_count()

    print("+==============================================================================â•—")
    print("|              ORFEAS TESTING SUITE - PARALLEL EXECUTION                      |")
    print("+=============================================================================='ïù")
    print(f"\nRunning tests with {num_cores} parallel workers\n")

    # Run pytest with parallel execution
    cmd = [
        "pytest",
        "-v",  # Verbose
        "-n", str(num_cores),  # Parallel workers
        "--cov=backend",  # Coverage
        "--cov-report=html",  # HTML coverage report
        "--cov-report=term-missing",  # Terminal coverage
        "--tb=short",  # Short traceback
        "--maxfail=5",  # Stop after 5 failures
        "backend/tests/"
    ]

    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent.parent)
    return result.returncode


def run_tests_by_category(category: str):
    """Run tests by category marker."""
    print(f"\n[TARGET] Running {category} tests...\n")

    cmd = [
        "pytest",
        "-v",
        "-m", category,
        "--tb=short",
        "backend/tests/"
    ]

    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent.parent)
    return result.returncode


def run_quick_tests():
    """Run quick unit tests only."""
    print("\n[FAST] Running quick unit tests...\n")

    cmd = [
        "pytest",
        "-v",
        "-m", "unit and not slow",
        "--tb=short",
        "backend/tests/"
    ]

    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent.parent)
    return result.returncode


def run_stress_tests():
    """Run GPU stress tests."""
    print("\nRunning GPU stress tests...\n")

    cmd = [
        "pytest",
        "-v",
        "-m", "stress",
        "--tb=short",
        "backend/tests/"
    ]

    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent.parent)
    return result.returncode


def run_e2e_tests():
    """Run end-to-end browser tests."""
    print("\n[WEB] Running E2E browser tests...\n")

    cmd = [
        "pytest",
        "-v",
        "-m", "e2e",
        "--tb=short",
        "backend/tests/"
    ]

    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent.parent)
    return result.returncode


def install_test_dependencies():
    """Install required testing dependencies."""
    print("\nüì¶ Installing test dependencies...\n")

    dependencies = [
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "pytest-xdist",  # For parallel execution
        "pytest-timeout",
        "playwright",  # For E2E tests
    ]

    for dep in dependencies:
        print(f"Installing {dep}...")
        subprocess.run([sys.executable, "-m", "pip", "install", dep], check=False)

    # Install Playwright browsers
    print("\nInstalling Playwright browsers...")
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=False)

    print("\n[OK] Test dependencies installed!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ORFEAS Testing Suite Runner")
    parser.add_argument("--install", action="store_true", help="Install test dependencies")
    parser.add_argument("--quick", action="store_true", help="Run quick unit tests only")
    parser.add_argument("--stress", action="store_true", help="Run GPU stress tests")
    parser.add_argument("--e2e", action="store_true", help="Run E2E browser tests")
    parser.add_argument("--category", type=str, help="Run tests by category (unit/integration/e2e/gpu/stress)")
    parser.add_argument("--parallel", action="store_true", help="Run all tests in parallel")

    args = parser.parse_args()

    if args.install:
        install_test_dependencies()
    elif args.quick:
        sys.exit(run_quick_tests())
    elif args.stress:
        sys.exit(run_stress_tests())
    elif args.e2e:
        sys.exit(run_e2e_tests())
    elif args.category:
        sys.exit(run_tests_by_category(args.category))
    elif args.parallel:
        sys.exit(run_tests_parallel())
    else:
        # Default: run all tests in parallel
        sys.exit(run_tests_parallel())
