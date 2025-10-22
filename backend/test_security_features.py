"""
ORFEAS AI Security Features Test Suite
========================================
Tests rate limiting, input validation, file upload security, and security headers
"""

import sys
import time
from validation import (
    Generate3DRequest,
    TextToImageRequest,
    FileUploadValidator,
    get_rate_limiter,
    SecurityHeaders
)
from pydantic import ValidationError


def test_input_validation() -> int:
    """Test Pydantic input validation"""
    print("\n[SECURE] TESTING INPUT VALIDATION")
    print("=" * 60)

    # Test 1: Valid Generate3DRequest
    try:
        valid_request = Generate3DRequest(
            job_id="550e8400-e29b-41d4-a716-446655440000",
            format="stl",
            dimensions={"width": 100, "height": 100, "depth": 20},
            quality=7
        )
        print(f"[OK] Valid request accepted: {valid_request.job_id}")
    except ValidationError as e:
        print(f"[FAIL] Unexpected error on valid request: {e}")
        return False

    # Test 2: Invalid UUID format
    try:
        invalid_request = Generate3DRequest(
            job_id="not-a-uuid",
            format="stl",
            dimensions={"width": 100, "height": 100, "depth": 20},
            quality=7
        )
        print(f"[FAIL] Invalid UUID accepted (should have been rejected): {invalid_request.job_id}")
        return False
    except ValidationError as e:
        print(f"[OK] Invalid UUID correctly rejected")

    # Test 3: Invalid format
    try:
        invalid_request = Generate3DRequest(
            job_id="550e8400-e29b-41d4-a716-446655440000",
            format="invalid_format",  # Should only accept stl/obj/glb/ply
            dimensions={"width": 100, "height": 100, "depth": 20},
            quality=7
        )
        print(f"[FAIL] Invalid format accepted: {invalid_request.format}")
        return False
    except ValidationError as e:
        print(f"[OK] Invalid format correctly rejected")

    # Test 4: Out of range dimensions
    try:
        invalid_request = Generate3DRequest(
            job_id="550e8400-e29b-41d4-a716-446655440000",
            format="stl",
            dimensions={"width": 2000, "height": 100, "depth": 20},  # width > 1000
            quality=7
        )
        print(f"[FAIL] Out of range width accepted: {invalid_request.dimensions.width}")
        return False
    except ValidationError as e:
        print(f"[OK] Out of range dimensions correctly rejected")

    # Test 5: Invalid quality
    try:
        invalid_request = Generate3DRequest(
            job_id="550e8400-e29b-41d4-a716-446655440000",
            format="stl",
            dimensions={"width": 100, "height": 100, "depth": 20},
            quality=15  # Should be 1-10
        )
        print(f"[FAIL] Invalid quality accepted: {invalid_request.quality}")
        return False
    except ValidationError as e:
        print(f"[OK] Invalid quality correctly rejected")

    # Test 6: Valid TextToImageRequest
    try:
        valid_prompt = TextToImageRequest(
            prompt="A beautiful landscape painting",
            style="artistic",
            width=512,
            height=512
        )
        print(f"[OK] Valid prompt accepted: '{valid_prompt.prompt[:30]}...'")
    except ValidationError as e:
        print(f"[FAIL] Unexpected error on valid prompt: {e}")
        return False

    # Test 7: SQL injection prevention
    try:
        malicious_prompt = TextToImageRequest(
            prompt="Test prompt DROP TABLE users",
            style="realistic"
        )
        print(f"[FAIL] SQL injection attempt accepted: {malicious_prompt.prompt}")
        return False
    except ValidationError as e:
        print(f"[OK] SQL injection attempt correctly rejected")

    # Test 8: Empty prompt
    try:
        empty_prompt = TextToImageRequest(
            prompt="   ",  # Only whitespace
            style="realistic"
        )
        print(f"[FAIL] Empty prompt accepted")
        return False
    except ValidationError as e:
        print(f"[OK] Empty prompt correctly rejected")

    print("\n[OK] ALL INPUT VALIDATION TESTS PASSED")
    return True


def test_file_upload_validation() -> int:
    """Test file upload security"""
    print("\n[FOLDER] TESTING FILE UPLOAD VALIDATION")
    print("=" * 60)

    # Test 1: Valid filename
    is_valid, error = FileUploadValidator.validate_filename("my_image.jpg")
    if is_valid:
        print(f"[OK] Valid filename accepted")
    else:
        print(f"[FAIL] Valid filename rejected: {error}")
        return False

    # Test 2: Path traversal attempt
    is_valid, error = FileUploadValidator.validate_filename("../../etc/passwd")
    if not is_valid:
        print(f"[OK] Path traversal correctly rejected: {error}")
    else:
        print(f"[FAIL] Path traversal attempt accepted")
        return False

    # Test 3: Null byte injection
    is_valid, error = FileUploadValidator.validate_filename("test\x00.jpg.exe")
    if not is_valid:
        print(f"[OK] Null byte injection correctly rejected: {error}")
    else:
        print(f"[FAIL] Null byte injection accepted")
        return False

    # Test 4: Valid file size
    is_valid, error = FileUploadValidator.validate_file_size(10 * 1024 * 1024)  # 10MB
    if is_valid:
        print(f"[OK] Valid file size (10MB) accepted")
    else:
        print(f"[FAIL] Valid file size rejected: {error}")
        return False

    # Test 5: Oversized file
    is_valid, error = FileUploadValidator.validate_file_size(100 * 1024 * 1024)  # 100MB
    if not is_valid:
        print(f"[OK] Oversized file correctly rejected: {error}")
    else:
        print(f"[FAIL] Oversized file (100MB) accepted")
        return False

    # Test 6: Valid MIME type
    is_valid, error = FileUploadValidator.validate_mime_type("image/png")
    if is_valid:
        print(f"[OK] Valid MIME type (image/png) accepted")
    else:
        print(f"[FAIL] Valid MIME type rejected: {error}")
        return False

    # Test 7: Invalid MIME type
    is_valid, error = FileUploadValidator.validate_mime_type("application/x-executable")
    if not is_valid:
        print(f"[OK] Invalid MIME type correctly rejected: {error}")
    else:
        print(f"[FAIL] Invalid MIME type accepted")
        return False

    print("\n[OK] ALL FILE UPLOAD VALIDATION TESTS PASSED")
    return True


def test_rate_limiting() -> int:
    """Test rate limiting functionality"""
    print("\n[TIMER]  TESTING RATE LIMITING")
    print("=" * 60)

    # Create rate limiter with low limit for testing
    limiter = get_rate_limiter(max_requests=5, window_seconds=10)
    test_ip = "192.168.1.100"

    # Test 1: Should allow first 5 requests
    allowed_count = 0
    for i in range(5):
        is_allowed, error = limiter.is_allowed(test_ip)
        if is_allowed:
            allowed_count += 1

    if allowed_count == 5:
        print(f"[OK] Rate limiter allowed {allowed_count}/5 requests")
    else:
        print(f"[FAIL] Rate limiter allowed {allowed_count}/5 requests (expected 5)")
        return False

    # Test 2: 6th request should be blocked
    is_allowed, error = limiter.is_allowed(test_ip)
    if not is_allowed:
        print(f"[OK] Rate limiter blocked 6th request: {error}")
    else:
        print(f"[FAIL] Rate limiter allowed 6th request (should have been blocked)")
        return False

    # Test 3: Different IP should have separate limit
    other_ip = "192.168.1.200"
    is_allowed, error = limiter.is_allowed(other_ip)
    if is_allowed:
        print(f"[OK] Rate limiter allows different IP")
    else:
        print(f"[FAIL] Rate limiter blocked different IP (should be allowed): {error}")
        return False

    print("\n[OK] ALL RATE LIMITING TESTS PASSED")
    return True


def test_security_headers() -> int:
    """Test security headers application"""
    print("\n[SHIELD]  TESTING SECURITY HEADERS")
    print("=" * 60)

    # Mock response object
    class MockResponse:
        def __init__(self) -> None:
            self.headers = {}

    response = MockResponse()
    enhanced_response = SecurityHeaders.apply_security_headers(response)

    expected_headers = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'"
    }

    missing_headers = []
    for header_name, expected_value in expected_headers.items():
        if header_name not in enhanced_response.headers:
            missing_headers.append(header_name)
        elif enhanced_response.headers[header_name] != expected_value:
            print(f"[WARN]  Header '{header_name}' has unexpected value: {enhanced_response.headers[header_name]}")

    if missing_headers:
        print(f"[FAIL] Missing security headers: {missing_headers}")
        return False

    print(f"[OK] All {len(expected_headers)} security headers correctly applied")
    for header, value in enhanced_response.headers.items():
        print(f"   • {header}: {value}")

    print("\n[OK] ALL SECURITY HEADER TESTS PASSED")
    return True


def main() -> int:
    """Run all security tests"""
    print("\n" + "=" * 60)
    print("[SECURE] ORFEAS AI SECURITY FEATURES TEST SUITE")
    print("=" * 60)

    tests = [
        ("Input Validation", test_input_validation),
        ("File Upload Validation", test_file_upload_validation),
        ("Rate Limiting", test_rate_limiting),
        ("Security Headers", test_security_headers)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"\n[FAIL] {test_name} test suite FAILED")
        except Exception as e:
            failed += 1
            print(f"\n[FAIL] {test_name} test suite CRASHED: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"[STATS] TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("\n[OK] ALL SECURITY TESTS PASSED - SYSTEM SECURE")
        return 0
    else:
        print(f"\n[WARN]  {failed} TEST SUITE(S) FAILED - REVIEW REQUIRED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
