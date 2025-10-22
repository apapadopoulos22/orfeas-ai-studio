"""
ORFEAS Backend Endpoint Testing Suite
======================================
ORFEAS DEBUGGING_TROUBLESHOOTING_SPECIALIST

This script tests all backend endpoints to diagnose server startup issues
and verify that all API routes are working correctly.

Usage:
    python test_all_endpoints.py
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime
from io import BytesIO
from PIL import Image
from typing import Any, Dict, List, Tuple

# Configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:5000')
TIMEOUT = 10  # seconds

# Test results storage
test_results = {
    "timestamp": datetime.now().isoformat(),
    "backend_url": BACKEND_URL,
    "tests_passed": 0,
    "tests_failed": 0,
    "tests_skipped": 0,
    "results": []
}


def print_header() -> None:
    """Print test header"""
    print("\n" + "="*80)
    print("[CONFIG] ORFEAS BACKEND ENDPOINT TESTING SUITE")
    print("   ORFEAS DEBUGGING_TROUBLESHOOTING_SPECIALIST")
    print("="*80)
    print(f"\nüìç Backend URL: {BACKEND_URL}")
    print(f"'è∞ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[TIMER]  Timeout: {TIMEOUT}s per request")
    print("\n" + "="*80 + "\n")


def print_test_header(test_name: Any, description: Any) -> None:
    """Print individual test header"""
    print(f"\n{''*80}")
    print(f"[LAB] TEST: {test_name}")
    print(f"[EDIT] {description}")
    print(f"{''*80}")


def log_result(test_name: Any, status: List, message: Any, response_data: Any = None, error: Any = None) -> None:
    """Log test result"""
    result = {
        "test": test_name,
        "status": status,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }

    if response_data:
        result["response"] = response_data
    if error:
        result["error"] = str(error)

    test_results["results"].append(result)

    if status == "PASS":
        test_results["tests_passed"] += 1
        print(f"[OK] PASS: {message}")
    elif status == "FAIL":
        test_results["tests_failed"] += 1
        print(f"[FAIL] FAIL: {message}")
        if error:
            print(f"   Error: {error}")
    elif status == "SKIP":
        test_results["tests_skipped"] += 1
        print(f"⏭  SKIP: {message}")

    if response_data:
        print(f"   Response: {json.dumps(response_data, indent=2)[:200]}")


def test_1_server_connectivity() -> int:
    """Test 1: Basic Server Connectivity"""
    print_test_header("Server Connectivity", "Check if backend server is reachable")

    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=TIMEOUT)

        if response.status_code in [200, 404]:  # 404 is OK if no root route
            log_result("server_connectivity", "PASS",
                      f"Server is reachable (HTTP {response.status_code})")
            return True
        else:
            log_result("server_connectivity", "FAIL",
                      f"Unexpected status code: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError as e:
        log_result("server_connectivity", "FAIL",
                  "Cannot connect to server - is it running?", error=e)
        return False
    except Exception as e:
        log_result("server_connectivity", "FAIL",
                  f"Connection test failed", error=e)
        return False


def test_2_health_endpoint() -> int:
    """Test 2: Health Check Endpoint"""
    print_test_header("Health Check", "Verify /api/health endpoint")

    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=TIMEOUT)

        if response.status_code == 200:
            data = response.json()

            # Verify required fields
            required_fields = ["status", "timestamp", "mode", "gpu_info"]
            missing_fields = [f for f in required_fields if f not in data]

            if missing_fields:
                log_result("health_endpoint", "FAIL",
                          f"Missing fields: {missing_fields}",
                          response_data=data)
                return False

            if data.get("status") != "healthy":
                log_result("health_endpoint", "FAIL",
                          f"Status is '{data.get('status')}', expected 'healthy'",
                          response_data=data)
                return False

            log_result("health_endpoint", "PASS",
                      f"Health check passed - Mode: {data.get('mode')}",
                      response_data=data)
            return True
        else:
            log_result("health_endpoint", "FAIL",
                      f"HTTP {response.status_code}: {response.text[:200]}")
            return False

    except Exception as e:
        log_result("health_endpoint", "FAIL",
                  "Health check failed", error=e)
        return False


def test_3_models_info() -> int:
    """Test 3: Models Info Endpoint"""
    print_test_header("Models Info", "Verify /api/models-info endpoint")

    try:
        response = requests.get(f"{BACKEND_URL}/api/models-info", timeout=TIMEOUT)

        if response.status_code == 200:
            data = response.json()

            log_result("models_info", "PASS",
                      f"Models info retrieved - Device: {data.get('device')}",
                      response_data=data)
            return True
        else:
            log_result("models_info", "FAIL",
                      f"HTTP {response.status_code}: {response.text[:200]}")
            return False

    except Exception as e:
        log_result("models_info", "FAIL",
                  "Models info request failed", error=e)
        return False


def test_4_upload_image() -> Tuple:
    """Test 4: Upload Image Endpoint"""
    print_test_header("Upload Image", "Verify /api/upload-image endpoint")

    try:
        # Create a test image
        img = Image.new('RGB', (512, 512), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        files = {'image': ('test_image.png', img_bytes, 'image/png')}

        response = requests.post(
            f"{BACKEND_URL}/api/upload-image",
            files=files,
            timeout=TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()

            required_fields = ["job_id", "filename", "image_info"]
            missing_fields = [f for f in required_fields if f not in data]

            if missing_fields:
                log_result("upload_image", "FAIL",
                          f"Missing fields: {missing_fields}",
                          response_data=data)
                return False, None

            log_result("upload_image", "PASS",
                      f"Image uploaded - Job ID: {data.get('job_id')}",
                      response_data=data)
            return True, data.get('job_id')
        else:
            log_result("upload_image", "FAIL",
                      f"HTTP {response.status_code}: {response.text[:200]}")
            return False, None

    except Exception as e:
        log_result("upload_image", "FAIL",
                  "Image upload failed", error=e)
        return False, None


def test_5_generate_3d(job_id: str) -> int:
    """Test 5: Generate 3D Endpoint"""
    print_test_header("Generate 3D", "Verify /api/generate-3d endpoint")

    if not job_id:
        log_result("generate_3d", "SKIP",
                  "Skipped - no job_id from upload test")
        return False

    try:
        payload = {
            "job_id": job_id,
            "quality": "medium",
            "mesh_format": "stl"
        }

        response = requests.post(
            f"{BACKEND_URL}/api/generate-3d",
            json=payload,
            timeout=60  # Longer timeout for 3D generation
        )

        if response.status_code == 200:
            data = response.json()

            if data.get("status") == "completed" or data.get("status") == "processing":
                log_result("generate_3d", "PASS",
                          f"3D generation initiated - Status: {data.get('status')}",
                          response_data=data)
                return True
            else:
                log_result("generate_3d", "FAIL",
                          f"Unexpected status: {data.get('status')}",
                          response_data=data)
                return False
        else:
            log_result("generate_3d", "FAIL",
                      f"HTTP {response.status_code}: {response.text[:200]}")
            return False

    except Exception as e:
        log_result("generate_3d", "FAIL",
                  "3D generation failed", error=e)
        return False


def test_6_job_status(job_id: str) -> int:
    """Test 6: Job Status Endpoint"""
    print_test_header("Job Status", "Verify /api/job-status endpoint")

    if not job_id:
        log_result("job_status", "SKIP",
                  "Skipped - no job_id from upload test")
        return False

    try:
        response = requests.get(
            f"{BACKEND_URL}/api/job-status/{job_id}",
            timeout=TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()

            log_result("job_status", "PASS",
                      f"Job status retrieved - Status: {data.get('status')}",
                      response_data=data)
            return True
        elif response.status_code == 404:
            log_result("job_status", "PASS",
                      "Job not found (expected for completed/cleaned jobs)")
            return True
        else:
            log_result("job_status", "FAIL",
                      f"HTTP {response.status_code}: {response.text[:200]}")
            return False

    except Exception as e:
        log_result("job_status", "FAIL",
                  "Job status check failed", error=e)
        return False


def test_7_preview_endpoint() -> int:
    """Test 7: Preview Endpoint"""
    print_test_header("Preview", "Verify /api/preview/<filename> endpoint")

    # This test requires a real file, so we'll just check if endpoint exists
    # by trying a non-existent file (should return 404, not 500)

    try:
        response = requests.get(
            f"{BACKEND_URL}/api/preview/nonexistent.png",
            timeout=TIMEOUT
        )

        if response.status_code == 404:
            log_result("preview_endpoint", "PASS",
                      "Preview endpoint exists (returned 404 for missing file)")
            return True
        elif response.status_code == 200:
            log_result("preview_endpoint", "PASS",
                      "Preview endpoint working (file found)")
            return True
        else:
            log_result("preview_endpoint", "FAIL",
                      f"Unexpected status: {response.status_code}")
            return False

    except Exception as e:
        log_result("preview_endpoint", "FAIL",
                  "Preview endpoint test failed", error=e)
        return False


def test_8_download_endpoint() -> int:
    """Test 8: Download Endpoint"""
    print_test_header("Download", "Verify /api/download/<job_id> endpoint")

    try:
        # Test with fake job_id (should return 404 or 400)
        response = requests.get(
            f"{BACKEND_URL}/api/download/test-job-id",
            timeout=TIMEOUT
        )

        if response.status_code in [404, 400]:
            log_result("download_endpoint", "PASS",
                      "Download endpoint exists (returned error for invalid job)")
            return True
        elif response.status_code == 200:
            log_result("download_endpoint", "PASS",
                      "Download endpoint working")
            return True
        else:
            log_result("download_endpoint", "FAIL",
                      f"Unexpected status: {response.status_code}")
            return False

    except Exception as e:
        log_result("download_endpoint", "FAIL",
                  "Download endpoint test failed", error=e)
        return False


def test_9_cors_headers() -> int:
    """Test 9: CORS Headers"""
    print_test_header("CORS Headers", "Verify CORS configuration")

    try:
        response = requests.options(
            f"{BACKEND_URL}/api/health",
            headers={"Origin": "http://localhost:3000"},
            timeout=TIMEOUT
        )

        cors_header = response.headers.get('Access-Control-Allow-Origin')

        if cors_header:
            log_result("cors_headers", "PASS",
                      f"CORS enabled - Allow-Origin: {cors_header}")
            return True
        else:
            log_result("cors_headers", "FAIL",
                      "CORS headers not found")
            return False

    except Exception as e:
        log_result("cors_headers", "FAIL",
                  "CORS test failed", error=e)
        return False


def test_10_websocket_connection() -> int:
    """Test 10: WebSocket Connection"""
    print_test_header("WebSocket", "Verify WebSocket availability")

    try:
        import socketio

        sio = socketio.Client()

        @sio.event
        def connect() -> None:
            print("   WebSocket connected!")

        @sio.event
        def connect_error(data: Dict) -> None:
            print(f"   Connection error: {data}")

        # Try to connect
        sio.connect(BACKEND_URL, wait_timeout=5)

        if sio.connected:
            log_result("websocket_connection", "PASS",
                      "WebSocket connection successful")
            sio.disconnect()
            return True
        else:
            log_result("websocket_connection", "FAIL",
                      "Could not connect to WebSocket")
            return False

    except ImportError:
        log_result("websocket_connection", "SKIP",
                  "python-socketio not installed")
        return False
    except Exception as e:
        log_result("websocket_connection", "FAIL",
                  "WebSocket test failed", error=e)
        return False


def print_summary() -> None:
    """Print test summary"""
    print("\n" + "="*80)
    print("[STATS] TEST SUMMARY")
    print("="*80)
    print(f"\n[OK] Passed: {test_results['tests_passed']}")
    print(f"[FAIL] Failed: {test_results['tests_failed']}")
    print(f"⏭  Skipped: {test_results['tests_skipped']}")
    print(f"\nTotal Tests: {test_results['tests_passed'] + test_results['tests_failed'] + test_results['tests_skipped']}")

    success_rate = (test_results['tests_passed'] /
                   (test_results['tests_passed'] + test_results['tests_failed']) * 100) if (test_results['tests_passed'] + test_results['tests_failed']) > 0 else 0

    print(f"Success Rate: {success_rate:.1f}%")

    if test_results['tests_failed'] > 0:
        print("\n[FAIL] FAILED TESTS:")
        for result in test_results['results']:
            if result['status'] == 'FAIL':
                print(f"   • {result['test']}: {result['message']}")

    print("\n" + "="*80)

    # Save results to file
    results_file = Path(__file__).parent / 'test_results.json'
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    print(f"\nüíæ Results saved to: {results_file}")
    print("="*80 + "\n")


def main() -> int:
    """Run all tests"""
    print_header()

    # Test 1: Server connectivity
    server_online = test_1_server_connectivity()

    if not server_online:
        print("\n" + "="*80)
        print("[FAIL] SERVER IS NOT RUNNING!")
        print("="*80)
        print("\n[CONFIG] TROUBLESHOOTING STEPS:")
        print("\n1. Start the backend server:")
        print("   cd backend")
        print("   python main.py")
        print("\n2. Check if port 5002 is already in use:")
        print("   netstat -ano | findstr :5002")
        print("\n3. Check backend logs for errors")
        print("\n4. Verify Python dependencies:")
        print("   pip install -r requirements.txt")
        print("\n" + "="*80 + "\n")
        print_summary()
        return 1

    # Test 2: Health check
    test_2_health_endpoint()

    # Test 3: Models info
    test_3_models_info()

    # Test 4: Upload image (get job_id for subsequent tests)
    upload_success, job_id = test_4_upload_image()

    # Test 5: Generate 3D (requires job_id)
    test_5_generate_3d(job_id)

    # Test 6: Job status (requires job_id)
    test_6_job_status(job_id)

    # Test 7: Preview endpoint
    test_7_preview_endpoint()

    # Test 8: Download endpoint
    test_8_download_endpoint()

    # Test 9: CORS headers
    test_9_cors_headers()

    # Test 10: WebSocket connection
    test_10_websocket_connection()

    # Print summary
    print_summary()

    # Return exit code
    return 0 if test_results['tests_failed'] == 0 else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[WARN]  Tests interrupted by user")
        print_summary()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[FAIL] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
