"""
ORFEAS AI 2D→3D Studio - Enhanced Validation Integration Test
============================================================
ORFEAS AI Project

Purpose: Verify Enhanced Image Validator is properly integrated with main.py
"""

import requests
import io
from PIL import Image
import logging
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = "http://localhost:5000"
UPLOAD_ENDPOINT = f"{BASE_URL}/api/upload-image"

def create_test_image(width: Any = 100, height: Any = 100, color: Any = (255, 0, 0)) -> None:
    """Create a test image in memory"""
    img = Image.new('RGB', (width, height), color=color)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def create_malicious_image() -> None:
    """Create image with embedded script (should be blocked)"""
    img = Image.new('RGB', (100, 100))
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')

    # Add malicious script
    buffer.write(b'<script>alert("XSS")</script>')
    buffer.seek(0)
    return buffer

def test_valid_image_upload() -> int:
    """Test: Valid image should pass all 6 layers"""
    logger.info("\n" + "="*80)
    logger.info("TEST 1: Valid Image Upload")
    logger.info("="*80)

    image = create_test_image()
    files = {'image': ('test.png', image, 'image/png')}

    try:
        response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=30)

        if response.status_code == 200:
            logger.info(" PASSED: Valid image accepted")
            logger.info(f"Response: {response.json()}")
            return True
        else:
            logger.error(f" FAILED: Got status {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f" ERROR: {e}")
        return False

def test_malicious_image_blocked() -> int:
    """Test: Malicious image should be blocked by Layer 3"""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: Malicious Image Detection")
    logger.info("="*80)

    image = create_malicious_image()
    files = {'image': ('malicious.png', image, 'image/png')}

    try:
        response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=30)

        if response.status_code == 400:
            logger.info(" PASSED: Malicious image BLOCKED by security layer")
            logger.info(f"Response: {response.json()}")
            return True
        else:
            logger.error(f" FAILED: Malicious image NOT blocked (status {response.status_code})")
            return False
    except Exception as e:
        logger.error(f" ERROR: {e}")
        return False

def test_oversized_image_blocked() -> int:
    """Test: Oversized image should be blocked by Layer 2"""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: Oversized Image Detection")
    logger.info("="*80)

    # Create 5000x5000 image (exceeds 4096x4096 limit)
    image = create_test_image(width=5000, height=5000)
    files = {'image': ('huge.png', image, 'image/png')}

    try:
        response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=30)

        if response.status_code == 400:
            logger.info(" PASSED: Oversized image BLOCKED by dimension check")
            logger.info(f"Response: {response.json()}")
            return True
        else:
            logger.error(f" FAILED: Oversized image NOT blocked (status {response.status_code})")
            return False
    except Exception as e:
        logger.error(f" ERROR: {e}")
        return False

def test_wrong_magic_number() -> int:
    """Test: File with wrong magic number should be blocked by Layer 1"""
    logger.info("\n" + "="*80)
    logger.info("TEST 4: Wrong Magic Number Detection")
    logger.info("="*80)

    # Create JPEG data but claim it's PNG
    img = Image.new('RGB', (100, 100))
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)

    files = {'image': ('fake.png', buffer, 'image/png')}  # JPEG data with PNG name

    try:
        response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=30)

        if response.status_code == 400:
            logger.info(" PASSED: Wrong magic number BLOCKED by Layer 1")
            logger.info(f"Response: {response.json()}")
            return True
        else:
            logger.error(f" FAILED: Wrong magic number NOT blocked (status {response.status_code})")
            return False
    except Exception as e:
        logger.error(f" ERROR: {e}")
        return False

def test_backend_health() -> int:
    """Test: Backend is running and healthy"""
    logger.info("\n" + "="*80)
    logger.info("PRE-CHECK: Backend Health")
    logger.info("="*80)

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            logger.info(" Backend is healthy and running")
            logger.info(f"Health response: {response.json()}")
            return True
        else:
            logger.error(f" Backend unhealthy: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f" Backend not reachable: {e}")
        logger.error("Please start the backend server first:")
        logger.error("  cd backend")
        logger.error("  python main.py")
        return False

def run_integration_tests() -> int:
    """Run all integration tests"""
    logger.info("\n")
    logger.info("")
    logger.info("â•'         ENHANCED IMAGE VALIDATION - INTEGRATION TEST SUITE                  â•'")
    logger.info("â•'         Testing 6-Layer Security System Integration                         â•'")
    logger.info("")

    # Pre-check: Backend health
    if not test_backend_health():
        logger.error("\n Backend not available - cannot run tests")
        return False

    # Run tests
    results = {
        'valid_image': test_valid_image_upload(),
        'malicious_blocked': test_malicious_image_blocked(),
        'oversized_blocked': test_oversized_image_blocked(),
        'wrong_magic': test_wrong_magic_number()
    }

    # Summary
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = " PASSED" if result else " FAILED"
        logger.info(f"{status}: {test_name}")

    logger.info("="*80)
    logger.info(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    logger.info("="*80)

    if passed == total:
        logger.info("\n ALL TESTS PASSED! Enhanced validation is working correctly! \n")
        return True
    else:
        logger.error(f"\n {total - passed} test(s) failed\n")
        return False

if __name__ == '__main__':
    import sys
    success = run_integration_tests()
    sys.exit(0 if success else 1)
