#!/usr/bin/env python3
"""
Automated Test Runner - PHASE 6A
Runs all tests and generates report
"""
import subprocess
import json
from pathlib import Path

def run_tests():
    """Run all tests"""
    backend_dir = Path(__file__).parent / "backend"

    # Run pytest with coverage
    cmd = "pytest tests/ -v --tb=short --junit-xml=test_results.xml"

    result = subprocess.run(
        cmd,
        shell=True,
        cwd=str(backend_dir),
        capture_output=True,
        text=True
    )

    return result.returncode, result.stdout, result.stderr

if __name__ == "__main__":
    returncode, stdout, stderr = run_tests()
    print(stdout)
    if stderr:
        print("STDERR:", stderr)
    exit(returncode)
