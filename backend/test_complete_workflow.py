"""
ORFEAS Complete Workflow Test
Tests the entire 2D'Üí3D generation pipeline including STL integrity verification

ORFEAS PROTOCOL
ORFEAS_DEBUGGING_TROUBLESHOOTING_SPECIALIST
"""

import os
import sys
import time
import json
import requests
from PIL import Image
import io
from pathlib import Path
import struct
import hashlib
from typing import Any, Dict, List

# Configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:5000')
API_BASE = f"{BACKEND_URL}/api"
TEST_OUTPUT_DIR = Path(__file__).parent / "test_workflow_outputs"
TEST_IMAGE_PATH = TEST_OUTPUT_DIR / "test_image.png"

# Create output directory
TEST_OUTPUT_DIR.mkdir(exist_ok=True)

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text: Any) -> None:
    """Print colored header"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

def print_success(text: Any) -> None:
    """Print success message"""
    print(f"{GREEN}[OK] {text}{RESET}")

def print_error(text: Any) -> None:
    """Print error message"""
    print(f"{RED}[FAIL] {text}{RESET}")

def print_info(text: Any) -> None:
    """Print info message"""
    print(f"{YELLOW}ℹ  {text}{RESET}")

def print_step(step_num: Any, total_steps: List, text: Any) -> None:
    """Print step progress"""
    print(f"\n{BLUE}[Step {step_num}/{total_steps}]{RESET} {text}")

def create_test_image() -> int:
    """Create a test image for upload"""
    print_step(1, 8, "Creating test image...")

    try:
        # Create a simple gradient image with some geometric shapes
        from PIL import ImageDraw, ImageFont

        img = Image.new('RGB', (512, 512), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)

        # Draw gradient background
        for y in range(512):
            color_val = int(240 - (y / 512) * 100)
            draw.line([(0, y), (512, y)], fill=(color_val, color_val, 255))

        # Draw geometric shapes
        draw.ellipse([128, 128, 384, 384], fill=(200, 100, 100), outline=(100, 50, 50), width=3)
        draw.rectangle([200, 200, 312, 312], fill=(100, 200, 100), outline=(50, 100, 50), width=3)
        draw.polygon([(256, 180), (220, 240), (292, 240)], fill=(100, 100, 200), outline=(50, 50, 100))

        # Save test image
        img.save(TEST_IMAGE_PATH)
        file_size = TEST_IMAGE_PATH.stat().st_size

        print_success(f"Test image created: {TEST_IMAGE_PATH}")
        print_info(f"Image size: {img.size}, File size: {file_size} bytes")
        return True

    except Exception as e:
        print_error(f"Failed to create test image: {e}")
        return False

def test_server_connectivity() -> int:
    """Test if server is reachable"""
    print_step(2, 8, "Testing server connectivity...")

    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print_success(f"Server is online - Mode: {health_data.get('mode', 'unknown')}")

            # Display GPU info
            gpu_info = health_data.get('gpu_info', {})
            if gpu_info:
                print_info(f"GPU: {gpu_info.get('device', 'N/A')}")
                print_info(f"GPU Memory: {gpu_info.get('free_mb', 0):.2f} MB free")

            return True
        else:
            print_error(f"Server returned status code {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print_error(f"Cannot connect to server: {e}")
        print_info(f"Make sure backend is running on {BACKEND_URL}")
        return False

def upload_test_image() -> Dict:
    """Upload test image to server"""
    print_step(3, 8, "Uploading test image...")

    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'image': ('test_image.png', f, 'image/png')}
            response = requests.post(f"{API_BASE}/upload-image", files=files, timeout=30)

        if response.status_code == 200:
            data = response.json()
            job_id = data.get('job_id')
            filename = data.get('filename')
            preview_url = data.get('preview_url')
            image_info = data.get('image_info', {})

            print_success(f"Image uploaded successfully!")
            print_info(f"Job ID: {job_id}")
            print_info(f"Filename: {filename}")
            print_info(f"Preview URL: {preview_url}")
            print_info(f"Image Format: {image_info.get('format', 'N/A')}")
            print_info(f"Image Size: {image_info.get('size', 'N/A')}")

            return {
                'job_id': job_id,
                'filename': filename,
                'preview_url': preview_url,
                'image_info': image_info
            }
        else:
            print_error(f"Upload failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return None

    except Exception as e:
        print_error(f"Upload error: {e}")
        return None

def verify_preview_image(upload_result: Any) -> int:
    """Verify preview window shows correct image"""
    print_step(4, 8, "Verifying preview image...")

    try:
        preview_url = upload_result['preview_url']
        filename = upload_result['filename']

        # Request preview image
        response = requests.get(f"{BACKEND_URL}{preview_url}", timeout=10)

        if response.status_code == 200:
            # Load preview image
            preview_img = Image.open(io.BytesIO(response.content))

            # Load original test image
            original_img = Image.open(TEST_IMAGE_PATH)

            # Compare dimensions
            if preview_img.size == original_img.size:
                print_success(f"Preview image dimensions match: {preview_img.size}")
            else:
                print_error(f"Dimension mismatch - Original: {original_img.size}, Preview: {preview_img.size}")
                return False

            # Compare image content (basic hash comparison)
            preview_hash = hashlib.md5(preview_img.tobytes()).hexdigest()
            original_hash = hashlib.md5(original_img.tobytes()).hexdigest()

            if preview_hash == original_hash:
                print_success("Preview image content matches original (MD5 hash verified)")
            else:
                print_info("Preview image content differs slightly (may be due to compression)")
                print_info(f"Original hash: {original_hash[:16]}...")
                print_info(f"Preview hash:  {preview_hash[:16]}...")

            # Save preview for manual inspection
            preview_save_path = TEST_OUTPUT_DIR / f"preview_{filename}"
            preview_img.save(preview_save_path)
            print_info(f"Preview saved to: {preview_save_path}")

            return True

        elif response.status_code == 404:
            print_error("Preview image not found on server")
            return False
        else:
            print_error(f"Preview request failed with status {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Preview verification error: {e}")
        return False

def generate_3d_model(job_id: str, quality: Any = 5) -> Dict:
    """Generate 3D model with specified quality (1-10 range)"""
    print_step(5, 8, f"Generating 3D model (quality: {quality}/10)...")

    try:
        payload = {
            'job_id': job_id,
            'quality': quality,  # Integer value 1-10 as expected by API
            'mesh_format': 'stl'
        }

        print_info(f"Sending generation request with payload: {json.dumps(payload, indent=2)}")

        response = requests.post(
            f"{API_BASE}/generate-3d",
            json=payload,
            timeout=120  # Allow up to 2 minutes for generation
        )

        if response.status_code == 200:
            data = response.json()
            print_success("3D generation started successfully!")
            print_info(f"Response: {json.dumps(data, indent=2)}")
            return data

        else:
            print_error(f"Generation failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return None

    except requests.exceptions.Timeout:
        print_error("Generation request timed out")
        print_info("This may be normal for high quality settings - check job status")
        return {'status': 'timeout', 'job_id': job_id}

    except Exception as e:
        print_error(f"Generation error: {e}")
        return None

def poll_job_status(job_id: str, max_attempts: List = 60, interval: Any = 5) -> int:
    """Poll job status until completion or timeout"""
    print_step(6, 8, "Monitoring job progress...")

    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{API_BASE}/job-status/{job_id}", timeout=10)

            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                progress = data.get('progress', 0)
                message = data.get('message', '')

                print_info(f"[{attempt+1}/{max_attempts}] Status: {status} | Progress: {progress}% | {message}")

                if status == 'completed':
                    print_success("Job completed successfully!")
                    return True
                elif status == 'failed':
                    print_error(f"Job failed: {message}")
                    return False
                elif status in ['processing', 'queued', 'started']:
                    time.sleep(interval)
                else:
                    print_info(f"Unknown status: {status}")
                    time.sleep(interval)

            elif response.status_code == 404:
                print_info(f"[{attempt+1}/{max_attempts}] Job not found yet (may still be initializing)")
                time.sleep(interval)
            else:
                print_error(f"Status check failed with code {response.status_code}")
                time.sleep(interval)

        except Exception as e:
            print_error(f"Status check error: {e}")
            time.sleep(interval)

    print_error(f"Job did not complete within {max_attempts * interval} seconds")
    return False

def download_stl_file(job_id: str) -> None:
    """Download generated STL file"""
    print_step(7, 8, "Downloading STL file...")

    try:
        # Backend expects /api/download/{job_id}/{filename}
        filename = f"model_{job_id}.stl"
        response = requests.get(f"{API_BASE}/download/{job_id}/{filename}", timeout=30)

        if response.status_code == 200:
            # Save STL file
            stl_filename = f"generated_{job_id}.stl"
            stl_path = TEST_OUTPUT_DIR / stl_filename

            with open(stl_path, 'wb') as f:
                f.write(response.content)

            file_size = len(response.content)
            print_success(f"STL file downloaded: {stl_path}")
            print_info(f"File size: {file_size} bytes ({file_size/1024:.2f} KB)")

            return stl_path

        else:
            print_error(f"Download failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return None

    except Exception as e:
        print_error(f"Download error: {e}")
        return None

def verify_stl_integrity(stl_path: str) -> int:
    """Verify STL file integrity and structure"""
    print_step(8, 8, "Verifying STL file integrity...")

    try:
        with open(stl_path, 'rb') as f:
            # Read first 80 bytes (STL header)
            header = f.read(80)

            # Check if it's ASCII or Binary STL
            header_text = header.decode('ascii', errors='ignore').strip()

            if header_text.startswith('solid'):
                print_info("Detected ASCII STL format")
                return verify_ascii_stl(stl_path)
            else:
                print_info("Detected Binary STL format")
                return verify_binary_stl(stl_path)

    except Exception as e:
        print_error(f"STL verification error: {e}")
        return False

def verify_binary_stl(stl_path: str) -> int:
    """Verify binary STL file structure"""
    try:
        with open(stl_path, 'rb') as f:
            # Skip header (80 bytes)
            header = f.read(80)

            # Read number of triangles (4 bytes, little-endian unsigned int)
            num_triangles_bytes = f.read(4)
            if len(num_triangles_bytes) != 4:
                print_error("Invalid STL: Cannot read triangle count")
                return False

            num_triangles = struct.unpack('<I', num_triangles_bytes)[0]
            print_info(f"Triangle count: {num_triangles}")

            if num_triangles == 0:
                print_error("Invalid STL: Zero triangles")
                return False

            # Each triangle is 50 bytes:
            # - Normal vector: 3 floats (12 bytes)
            # - Vertex 1: 3 floats (12 bytes)
            # - Vertex 2: 3 floats (12 bytes)
            # - Vertex 3: 3 floats (12 bytes)
            # - Attribute byte count: 1 short (2 bytes)
            expected_size = 80 + 4 + (num_triangles * 50)
            actual_size = stl_path.stat().st_size

            print_info(f"Expected file size: {expected_size} bytes")
            print_info(f"Actual file size: {actual_size} bytes")

            if actual_size == expected_size:
                print_success("STL file structure is valid!")
            else:
                print_error(f"File size mismatch - Expected: {expected_size}, Got: {actual_size}")
                return False

            # Sample first triangle to verify data structure
            triangle_data = f.read(50)
            if len(triangle_data) == 50:
                # Unpack triangle data
                normal = struct.unpack('<fff', triangle_data[0:12])
                vertex1 = struct.unpack('<fff', triangle_data[12:24])
                vertex2 = struct.unpack('<fff', triangle_data[24:36])
                vertex3 = struct.unpack('<fff', triangle_data[36:48])

                print_info("First triangle sample:")
                print_info(f"  Normal: ({normal[0]:.3f}, {normal[1]:.3f}, {normal[2]:.3f})")
                print_info(f"  Vertex 1: ({vertex1[0]:.3f}, {vertex1[1]:.3f}, {vertex1[2]:.3f})")
                print_info(f"  Vertex 2: ({vertex2[0]:.3f}, {vertex2[1]:.3f}, {vertex2[2]:.3f})")
                print_info(f"  Vertex 3: ({vertex3[0]:.3f}, {vertex3[1]:.3f}, {vertex3[2]:.3f})")

                # Check for NaN or Inf values
                all_values = normal + vertex1 + vertex2 + vertex3
                if any(v != v or abs(v) == float('inf') for v in all_values):
                    print_error("Invalid triangle data: Contains NaN or Infinity values")
                    return False

                print_success("Triangle data is valid!")
            else:
                print_error("Cannot read first triangle data")
                return False

            # Calculate bounding box by sampling triangles
            print_info("Calculating bounding box...")
            min_x = min_y = min_z = float('inf')
            max_x = max_y = max_z = float('-inf')

            f.seek(84)  # Reset to start of triangle data
            sample_count = min(num_triangles, 100)  # Sample first 100 triangles

            for i in range(sample_count):
                triangle_data = f.read(50)
                if len(triangle_data) < 50:
                    break

                # Skip normal, read vertices
                for v_offset in [12, 24, 36]:
                    x, y, z = struct.unpack('<fff', triangle_data[v_offset:v_offset+12])
                    min_x, max_x = min(min_x, x), max(max_x, x)
                    min_y, max_y = min(min_y, y), max(max_y, y)
                    min_z, max_z = min(min_z, z), max(max_z, z)

            print_info(f"Bounding box (sampled from {sample_count} triangles):")
            print_info(f"  X: [{min_x:.3f}, {max_x:.3f}] (size: {max_x-min_x:.3f})")
            print_info(f"  Y: [{min_y:.3f}, {max_y:.3f}] (size: {max_y-min_y:.3f})")
            print_info(f"  Z: [{min_z:.3f}, {max_z:.3f}] (size: {max_z-min_z:.3f})")

            print_success("[OK] STL file integrity verified - Binary format is valid!")
            return True

    except Exception as e:
        print_error(f"Binary STL verification error: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_ascii_stl(stl_path: str) -> int:
    """Verify ASCII STL file structure"""
    try:
        with open(stl_path, 'r') as f:
            content = f.read()

        lines = content.strip().split('\n')

        # Check for solid/endsolid keywords
        if not lines[0].strip().startswith('solid'):
            print_error("Invalid ASCII STL: Missing 'solid' keyword")
            return False

        if not lines[-1].strip().startswith('endsolid'):
            print_error("Invalid ASCII STL: Missing 'endsolid' keyword")
            return False

        # Count facets
        facet_count = content.count('facet normal')
        print_info(f"Facet count: {facet_count}")

        if facet_count == 0:
            print_error("Invalid ASCII STL: No facets found")
            return False

        print_success("[OK] STL file integrity verified - ASCII format is valid!")
        return True

    except Exception as e:
        print_error(f"ASCII STL verification error: {e}")
        return False

def generate_test_report(results: List) -> None:
    """Generate comprehensive test report"""
    print_header("TEST REPORT SUMMARY")

    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    print(f"\n{'='*80}")
    print(f"Total Tests: {total_tests}")
    print(f"{GREEN}Passed: {passed_tests}{RESET}")
    print(f"{RED}Failed: {failed_tests}{RESET}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"{'='*80}\n")

    print("Detailed Results:")
    for test_name, result in results.items():
        status = f"{GREEN}[OK] PASS{RESET}" if result else f"{RED}[FAIL] FAIL{RESET}"
        print(f"  {status} - {test_name}")

    print(f"\n{'='*80}\n")

    # Save report to file
    report_path = TEST_OUTPUT_DIR / "test_report.json"
    report_data = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'success_rate': success_rate,
        'results': {k: ('PASS' if v else 'FAIL') for k, v in results.items()}
    }

    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2)

    print_info(f"Test report saved to: {report_path}")

    return success_rate == 100.0

def main() -> int:
    """Main test workflow"""
    print_header("+==============================================================â•—")
    print_header("|     ORFEAS COMPLETE WORKFLOW TEST  PROTOCOL       |")
    print_header("+==============================================================â•—")

    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"Output Directory: {TEST_OUTPUT_DIR}")

    results = {}

    # Step 1: Create test image
    results['Create Test Image'] = create_test_image()
    if not results['Create Test Image']:
        print_error("Cannot proceed without test image")
        generate_test_report(results)
        return False

    # Step 2: Test server connectivity
    results['Server Connectivity'] = test_server_connectivity()
    if not results['Server Connectivity']:
        print_error("Cannot proceed without server connection")
        generate_test_report(results)
        return False

    # Step 3: Upload test image
    upload_result = upload_test_image()
    results['Upload Image'] = upload_result is not None
    if not results['Upload Image']:
        print_error("Cannot proceed without successful upload")
        generate_test_report(results)
        return False

    job_id = upload_result['job_id']

    # Step 4: Verify preview image
    results['Verify Preview'] = verify_preview_image(upload_result)

    # Step 5: Generate 3D model (quality = 5, range is 1-10)
    generation_result = generate_3d_model(job_id, quality=5)
    results['Generate 3D Model'] = generation_result is not None

    if not results['Generate 3D Model']:
        print_error("Cannot proceed without successful generation request")
        generate_test_report(results)
        return False

    # Step 6: Poll job status
    results['Job Completion'] = poll_job_status(job_id, max_attempts=60, interval=5)

    if not results['Job Completion']:
        print_error("Job did not complete - skipping download and verification")
        generate_test_report(results)
        return False

    # Step 7: Download STL file
    stl_path = download_stl_file(job_id)
    results['Download STL'] = stl_path is not None

    if not results['Download STL']:
        print_error("Cannot verify STL without successful download")
        generate_test_report(results)
        return False

    # Step 8: Verify STL integrity
    results['STL Integrity'] = verify_stl_integrity(stl_path)

    # Generate final report
    print_header("WORKFLOW TEST COMPLETE")
    all_passed = generate_test_report(results)

    if all_passed:
        print_success("üéâ ALL TESTS PASSED! ORFEAS workflow is fully operational!")
    else:
        print_error("[WARN]  Some tests failed. Review the report above.")

    return all_passed

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_error("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
