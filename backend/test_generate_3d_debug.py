"""
Debug script to test /api/generate-3d endpoint
[ORFEAS] MILESTONE 2: Debugging generate-3d endpoint hanging issue
"""
import requests
import time
import sys

SERVER_URL = "http://127.0.0.1:5000"

def test_health_check() -> int:
    """Test if server is responding"""
    print("\n" + "="*80)
    print("[1] Testing health check endpoint...")
    print("="*80)

    try:
        response = requests.get(f"{SERVER_URL}/api/health", timeout=5)
        print(f" Status: {response.status_code}")
        print(f" Response: {response.json()}")
        return True
    except requests.exceptions.Timeout:
        print(" TIMEOUT: Health check timed out")
        return False
    except Exception as e:
        print(f" ERROR: {e}")
        return False

def test_upload_image() -> None:
    """Test image upload"""
    print("\n" + "="*80)
    print("[2] Testing image upload endpoint...")
    print("="*80)

    try:
        # Create a simple test image
        from PIL import Image
        import io

        img = Image.new('RGB', (512, 512), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        files = {'image': ('test.png', img_bytes, 'image/png')}
        response = requests.post(f"{SERVER_URL}/api/upload-image", files=files, timeout=30)

        print(f" Status: {response.status_code}")
        data = response.json()
        print(f" Response: {data}")

        if 'job_id' in data:
            print(f" Job ID: {data['job_id']}")
            return data['job_id']
        else:
            print(" No job_id in response")
            return None

    except requests.exceptions.Timeout:
        print(" TIMEOUT: Upload timed out")
        return None
    except Exception as e:
        print(f" ERROR: {e}")
        return None

def test_generate_3d(job_id: str) -> int:
    """Test 3D generation endpoint"""
    print("\n" + "="*80)
    print("[3] Testing 3D generation endpoint...")
    print("="*80)
    print(f"Job ID: {job_id}")
    print(f"Timeout: 300 seconds (5 minutes)")
    print("Waiting for response...")

    try:
        payload = {
            'job_id': job_id,
            'format': 'stl',
            'quality': 7
        }

        start_time = time.time()
        response = requests.post(
            f"{SERVER_URL}/api/generate-3d",
            json=payload,
            timeout=300  # 5 minutes
        )
        elapsed = time.time() - start_time

        print(f" Status: {response.status_code}")
        print(f" Time: {elapsed:.2f} seconds")
        print(f" Response: {response.json()}")
        return True

    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f" TIMEOUT: Request timed out after {elapsed:.2f} seconds")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f" CONNECTION ERROR: {e}")
        return False
    except Exception as e:
        print(f" ERROR: {e}")
        return False

def test_job_status(job_id: str) -> int:
    """Test job status endpoint"""
    print("\n" + "="*80)
    print("[4] Testing job status endpoint...")
    print("="*80)

    try:
        response = requests.get(f"{SERVER_URL}/api/job-status/{job_id}", timeout=10)
        print(f" Status: {response.status_code}")
        print(f" Response: {response.json()}")
        return True
    except Exception as e:
        print(f" ERROR: {e}")
        return False

def main() -> None:
    """Run all tests"""
    print("\n" + "="*80)
    print("ORFEAS GENERATE-3D ENDPOINT DEBUG TEST")
    print("[ORFEAS] MILESTONE 2: Debugging endpoint hanging issue")
    print("="*80)

    # Test 1: Health check
    if not test_health_check():
        print("\n Server not responding. Start the server first:")
        print("   cd backend")
        print("   python main.py")
        sys.exit(1)

    # Test 2: Upload image
    job_id = test_upload_image()
    if not job_id:
        print("\n Image upload failed")
        sys.exit(1)

    # Test 3: Check job status before generation
    test_job_status(job_id)

    # Test 4: Generate 3D model (THIS IS WHERE IT HANGS)
    success = test_generate_3d(job_id)

    # Test 5: Check job status after generation
    if success:
        test_job_status(job_id)

    # Summary
    print("\n" + "="*80)
    if success:
        print(" ALL TESTS PASSED")
    else:
        print(" GENERATE-3D TEST FAILED")
        print("\nDEBUG STEPS:")
        print("1. Check server logs for errors")
        print("2. Verify TESTING environment variable is set")
        print("3. Check if server is actually processing the request")
        print("4. Look for any exceptions in the async handler")
    print("="*80)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
