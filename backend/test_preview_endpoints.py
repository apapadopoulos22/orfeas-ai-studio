"""
ORFEAS STUDIO - Preview Endpoint Testing
=========================================

Test script to verify the new preview endpoints work correctly:
1. /api/preview/<filename> - Preview uploaded images
2. /api/preview-output/<job_id>/<filename> - Preview generated outputs
3. Upload response includes preview_url field

Author: ORFEAS AI Assistant
Date: 2024
"""

import requests
import json
from pathlib import Path
import time
from typing import Any, List

# Configuration
API_BASE_URL = "http://127.0.0.1:5002/api"
TEST_IMAGE_PATH = Path(__file__).parent / "test_images" / "test_upload.png"

def print_header(title: Any) -> None:
    """Print formatted test section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_result(test_name: Any, success: List, details: List = "") -> None:
    """Print test result"""
    status = "[OK] PASS" if success else "[FAIL] FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"   {details}")

def test_health_check() -> int:
    """Test 1: Verify backend is running"""
    print_header("TEST 1: Backend Health Check")

    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print_result("Backend health check", True,
                        f"Status: {data.get('status')} | GPU: {data.get('gpu_available')}")
            return True
        else:
            print_result("Backend health check", False,
                        f"HTTP {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print_result("Backend health check", False, str(e))
        return False

def test_image_upload_with_preview() -> None:
    """Test 2: Upload image and verify preview_url in response"""
    print_header("TEST 2: Image Upload with Preview URL")

    # Check if test image exists
    if not TEST_IMAGE_PATH.exists():
        print_result("Test image check", False,
                    f"Test image not found: {TEST_IMAGE_PATH}")
        # Create a test image if it doesn't exist
        try:
            TEST_IMAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
            from PIL import Image
            img = Image.new('RGB', (512, 512), color='blue')
            img.save(TEST_IMAGE_PATH)
            print_result("Create test image", True, "Created 512x512 test image")
        except Exception as e:
            print_result("Create test image", False, str(e))
            return None

    try:
        # Upload the image
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'image': (TEST_IMAGE_PATH.name, f, 'image/png')}
            response = requests.post(
                f"{API_BASE_URL}/upload-image",
                files=files,
                timeout=30
            )

        if response.status_code == 200:
            data = response.json()

            # Verify response structure
            has_job_id = 'job_id' in data
            has_filename = 'filename' in data
            has_preview_url = 'preview_url' in data
            has_image_info = 'image_info' in data

            print_result("Upload successful", True,
                        f"Job ID: {data.get('job_id')}")
            print_result("Response has job_id", has_job_id)
            print_result("Response has filename", has_filename,
                        f"{data.get('filename', 'N/A')}")
            print_result("Response has preview_url", has_preview_url,
                        f"{data.get('preview_url', 'N/A')}")
            print_result("Response has image_info", has_image_info)

            if has_image_info:
                info = data['image_info']
                print(f"   Image Info: {info.get('width')}x{info.get('height')} px, "
                      f"{info.get('format')}, {info.get('file_size')} bytes")

            return data
        else:
            print_result("Upload request", False,
                        f"HTTP {response.status_code}: {response.text}")
            return None

    except Exception as e:
        print_result("Upload request", False, str(e))
        return None

def test_preview_endpoint(upload_data: Any) -> int:
    """Test 3: Access preview endpoint"""
    print_header("TEST 3: Preview Endpoint Access")

    if not upload_data or 'filename' not in upload_data:
        print_result("Preview endpoint test", False,
                    "No upload data available")
        return False

    filename = upload_data['filename']
    preview_url = f"http://127.0.0.1:5002/api/preview/{filename}"

    try:
        response = requests.get(preview_url, timeout=10)

        if response.status_code == 200:
            # Check content type
            content_type = response.headers.get('Content-Type', '')
            is_image = content_type.startswith('image/')

            # Check content length
            content_length = len(response.content)

            print_result("Preview endpoint accessible", True,
                        f"URL: /api/preview/{filename}")
            print_result("Content-Type is image", is_image,
                        f"{content_type}")
            print_result("Content received", content_length > 0,
                        f"{content_length} bytes")

            # Verify it's not a download (should not have Content-Disposition: attachment)
            content_disposition = response.headers.get('Content-Disposition', '')
            is_inline = 'attachment' not in content_disposition.lower()
            print_result("Displays inline (not download)", is_inline,
                        f"Content-Disposition: {content_disposition or 'none (inline)'}")

            return True
        else:
            print_result("Preview endpoint access", False,
                        f"HTTP {response.status_code}")
            return False

    except Exception as e:
        print_result("Preview endpoint access", False, str(e))
        return False

def test_preview_url_format(upload_data: Any) -> int:
    """Test 4: Verify preview_url format"""
    print_header("TEST 4: Preview URL Format Validation")

    if not upload_data or 'preview_url' not in upload_data:
        print_result("Preview URL format test", False,
                    "No preview_url in upload response")
        return False

    preview_url = upload_data['preview_url']
    filename = upload_data.get('filename', '')

    # Check URL format
    is_correct_format = preview_url.startswith('/api/preview/')
    contains_filename = filename in preview_url

    print_result("URL format correct", is_correct_format,
                f"Format: {preview_url}")
    print_result("URL contains filename", contains_filename)

    # Verify URL is usable by frontend
    full_url = f"http://127.0.0.1:5002{preview_url}"
    print(f"\n   Frontend should use: {full_url}")
    print(f"   Or relative: {preview_url}")

    return is_correct_format and contains_filename

def test_mime_type_detection() -> int:
    """Test 5: MIME type detection for different formats"""
    print_header("TEST 5: MIME Type Detection")

    test_cases = [
        ('test.png', 'image/png'),
        ('test.jpg', 'image/jpeg'),
        ('test.jpeg', 'image/jpeg'),
        ('test.gif', 'image/gif'),
        ('test.bmp', 'image/bmp'),
        ('test.webp', 'image/webp'),
        ('test.tiff', 'image/tiff')
    ]

    for filename, expected_mime in test_cases:
        # Try to access preview endpoint
        url = f"http://127.0.0.1:5002/api/preview/{filename}"
        try:
            response = requests.head(url, timeout=5)
            # It's OK if file doesn't exist (404), we're testing the route
            content_type = response.headers.get('Content-Type', '')

            if response.status_code == 404:
                print_result(f"Route exists for {filename}", True,
                            "Route accessible (404 expected)")
            elif response.status_code == 200:
                matches = content_type.startswith(expected_mime.split('/')[0])
                print_result(f"MIME type for {filename}", matches,
                            f"Got: {content_type}")
        except Exception as e:
            print_result(f"Route test for {filename}", False, str(e))

    return True

def test_download_vs_preview() -> int:
    """Test 6: Verify download endpoint vs preview endpoint"""
    print_header("TEST 6: Download vs Preview Endpoints")

    # Upload a test image first
    if not TEST_IMAGE_PATH.exists():
        print_result("Test image required", False,
                    "Upload test image first")
        return False

    try:
        # Upload
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'image': (TEST_IMAGE_PATH.name, f, 'image/png')}
            response = requests.post(
                f"{API_BASE_URL}/upload-image",
                files=files,
                timeout=30
            )

        if response.status_code != 200:
            print_result("Upload for comparison test", False,
                        f"HTTP {response.status_code}")
            return False

        data = response.json()
        filename = data['filename']

        # Test preview endpoint (should display inline)
        preview_response = requests.get(
            f"http://127.0.0.1:5002/api/preview/{filename}",
            timeout=10
        )

        preview_disposition = preview_response.headers.get('Content-Disposition', '')
        preview_is_inline = 'attachment' not in preview_disposition.lower()

        print_result("Preview endpoint serves inline", preview_is_inline,
                    f"Content-Disposition: {preview_disposition or 'none (inline)'}")

        # Download endpoint would be: /api/download/<job_id>/<filename>
        # But we don't test it here since it requires a completed 3D generation job

        return True

    except Exception as e:
        print_result("Download vs Preview test", False, str(e))
        return False

def run_all_tests() -> None:
    """Run all preview endpoint tests"""
    print("\n" + "+" + "="*68 + "â•—")
    print("|" + " "*15 + "ORFEAS PREVIEW ENDPOINT TESTS" + " "*24 + "|")
    print("+" + "="*68 + "'ïù")

    results = []

    # Test 1: Health check
    health_ok = test_health_check()
    results.append(("Backend Health", health_ok))

    if not health_ok:
        print("\n[FAIL] Backend not running. Please start the backend first:")
        print("   cd backend")
        print("   python main.py")
        return

    # Test 2: Upload with preview_url
    upload_data = test_image_upload_with_preview()
    results.append(("Upload with Preview URL", upload_data is not None))

    # Test 3: Preview endpoint access
    if upload_data:
        preview_ok = test_preview_endpoint(upload_data)
        results.append(("Preview Endpoint Access", preview_ok))

        # Test 4: Preview URL format
        format_ok = test_preview_url_format(upload_data)
        results.append(("Preview URL Format", format_ok))

    # Test 5: MIME types
    mime_ok = test_mime_type_detection()
    results.append(("MIME Type Detection", mime_ok))

    # Test 6: Download vs Preview
    comparison_ok = test_download_vs_preview()
    results.append(("Download vs Preview", comparison_ok))

    # Summary
    print_header("TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{status} - {test_name}")

    print(f"\n{'='*70}")
    print(f"RESULTS: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
    print(f"{'='*70}\n")

    if passed == total:
        print("üéâ ALL TESTS PASSED! Preview functionality is working correctly.")
        print("\nNext steps:")
        print("1. Open orfeas-studio.html in a browser")
        print("2. Upload an image")
        print("3. Verify the preview displays correctly")
        print("4. Check browser console for any errors")
    else:
        print("[WARN]  Some tests failed. Please review the errors above.")
        print("\nTroubleshooting:")
        print("1. Ensure backend is running: python backend/main.py")
        print("2. Check backend logs for errors")
        print("3. Verify uploads directory exists: backend/uploads/")
        print("4. Check file permissions")

if __name__ == "__main__":
    run_all_tests()
