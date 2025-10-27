#!/usr/bin/env python3
"""
PHASE 3: SERVER STARTUP VERIFICATION
======================================
Verify that the Flask backend starts correctly and responds to health checks.

Tests:
- Backend process starts on port 5000
- Health check endpoint responds
- Ready check endpoint responds
- System status is properly reported
- No critical errors in startup
"""

import subprocess
import time
import requests
import sys
import os
import signal

# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*65}")
    print(f"{'='*5} {text:<54} {'='*5}")
    print(f"{'='*65}\n")

def wait_for_server(url, max_retries=30, retry_delay=1):
    """Wait for server to be ready"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
            print(f"  Attempt {attempt + 1}/{max_retries}: Status {response.status_code}, retrying...")
        except requests.exceptions.ConnectionError:
            print(f"  Attempt {attempt + 1}/{max_retries}: Connection refused, retrying...")
        except Exception as e:
            print(f"  Attempt {attempt + 1}/{max_retries}: {e}, retrying...")

        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    return False

# =====================================================================
# PHASE 3: SERVER STARTUP
# =====================================================================

print_header("PHASE 3: SERVER STARTUP VERIFICATION")

all_pass = True
process = None

try:
    # =====================================================================
    # Test 3.1: Start Backend Server
    # =====================================================================
    print_header("TEST 3.1: START BACKEND SERVER")

    try:
        print("Starting Flask backend on port 5000...")

        # Change to backend directory
        backend_path = os.path.join(os.getcwd(), "backend")

        # Start the server as subprocess
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=backend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=None  # Windows doesn't use preexec_fn
        )

        print(f"✓ Backend process started (PID: {process.pid})")

        # Wait for server to be ready
        print("Waiting for server to initialize...")
        time.sleep(3)  # Give server time to start

        if wait_for_server("http://localhost:5000/health", max_retries=15, retry_delay=1):
            print("✓ Server responded to health check\n")
        else:
            print("⚠ Server startup delayed, continuing with tests\n")
            all_pass = False

    except Exception as e:
        print(f"✗ Failed to start backend: {e}\n")
        all_pass = False

    # =====================================================================
    # Test 3.2: Health Check Endpoint
    # =====================================================================
    print_header("TEST 3.2: HEALTH CHECK ENDPOINT")

    try:
        response = requests.get("http://localhost:5000/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check endpoint responding")
            print(f"  Status: {data.get('status', 'N/A')}")
            print(f"  GPU available: {data.get('gpu_available', 'N/A')}")
            print(f"  Uptime: {data.get('uptime', 'N/A')}s")
            print(f"  Timestamp: {data.get('timestamp', 'N/A')}\n")
        else:
            print(f"✗ Health check returned status {response.status_code}\n")
            all_pass = False

    except Exception as e:
        print(f"✗ Health check failed: {e}\n")
        all_pass = False

    # =====================================================================
    # Test 3.3: Ready Check Endpoint
    # =====================================================================
    print_header("TEST 3.3: READY CHECK ENDPOINT")

    try:
        response = requests.get("http://localhost:5000/ready", timeout=5)

        if response.status_code in [200, 503]:
            data = response.json()
            ready = response.status_code == 200
            print(f"✓ Ready check endpoint responding")
            print(f"  Ready: {ready}")
            print(f"  Message: {data.get('message', 'N/A')}\n")

            if not ready:
                print(f"⚠ Server not fully ready (models may still be loading)\n")
        else:
            print(f"✗ Ready check returned status {response.status_code}\n")
            all_pass = False

    except Exception as e:
        print(f"✗ Ready check failed: {e}\n")
        all_pass = False

    # =====================================================================
    # Test 3.4: Metrics Endpoint
    # =====================================================================
    print_header("TEST 3.4: METRICS ENDPOINT")

    try:
        response = requests.get("http://localhost:5000/metrics", timeout=5)

        if response.status_code == 200:
            print(f"✓ Metrics endpoint responding")
            print(f"  Response size: {len(response.text)} bytes")

            # Check for key Prometheus metrics
            if "# HELP" in response.text and "# TYPE" in response.text:
                print(f"  Prometheus format: Valid")
            else:
                print(f"  Prometheus format: Not detected")

            print()
        else:
            print(f"⚠ Metrics endpoint returned status {response.status_code}\n")

    except Exception as e:
        print(f"⚠ Metrics endpoint not available: {e}\n")

    # =====================================================================
    # Test 3.5: Server Stability Check
    # =====================================================================
    print_header("TEST 3.5: SERVER STABILITY CHECK")

    try:
        print("Running 5 sequential health checks (1 sec interval)...")

        success_count = 0
        for i in range(5):
            try:
                response = requests.get("http://localhost:5000/health", timeout=2)
                if response.status_code == 200:
                    success_count += 1
                    print(f"  Check {i+1}/5: ✓")
                else:
                    print(f"  Check {i+1}/5: ✗ (Status {response.status_code})")
            except Exception as e:
                print(f"  Check {i+1}/5: ✗ ({str(e)[:30]})")

            if i < 4:
                time.sleep(1)

        print(f"\n✓ Stability: {success_count}/5 health checks passed")

        if success_count < 5:
            print(f"⚠ Server stability concerns detected\n")
            all_pass = False
        else:
            print()

    except Exception as e:
        print(f"✗ Stability check failed: {e}\n")
        all_pass = False

finally:
    # =====================================================================
    # Cleanup
    # =====================================================================
    print_header("PHASE 3: CLEANUP")

    if process:
        print("Stopping backend server...")
        try:
            process.terminate()
            process.wait(timeout=5)
            print("✓ Backend process terminated\n")
        except subprocess.TimeoutExpired:
            print("⚠ Force killing backend process...")
            process.kill()
            process.wait()
            print("✓ Backend process killed\n")

    # =====================================================================
    # Summary
    # =====================================================================
    print_header("PHASE 3: SUMMARY")

    if all_pass:
        print("✓ PHASE 3: SERVER STARTUP VERIFIED SUCCESSFULLY")
        print("\nStatus: READY FOR PHASE 4 (Docker Orchestration)")
        exit_code = 0
    else:
        print("⚠ PHASE 3: COMPLETED WITH WARNINGS")
        print("\nStatus: Review issues before proceeding")
        exit_code = 1

    print(f"\nNext Phase: Phase 4 - Docker Orchestration\n")

    sys.exit(exit_code)
