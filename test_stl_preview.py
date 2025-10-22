#!/usr/bin/env python
"""
Test STL Preview - Verify that generated STL files are accessible and valid
"""
import requests
import json
import time
from pathlib import Path

BASE_URL = "http://127.0.0.1:5000"

def test_stl_generation():
    """Test the complete STL generation workflow"""

    print("=" * 70)
    print("ORFEAS STL PREVIEW TEST")
    print("=" * 70)

    # 1. Check backend health
    print("\n[1] Checking backend health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"    ✓ Backend healthy: {response.json()}")
        else:
            print(f"    ✗ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"    ✗ Backend connection failed: {e}")
        return False

    # 2. Create a test image
    print("\n[2] Creating test image...")
    try:
        from PIL import Image
        import io

        # Create a simple test image
        img = Image.new('RGB', (256, 256), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        print(f"    ✓ Test image created (256x256 PNG)")
    except Exception as e:
        print(f"    ✗ Failed to create image: {e}")
        return False

    # 3. Upload image
    print("\n[3] Uploading image...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/upload-image",
            files={'image': ('test.png', img_bytes, 'image/png')}
        )

        if response.status_code == 200:
            data = response.json()
            job_id = data.get('job_id')
            print(f"    ✓ Image uploaded, Job ID: {job_id}")
        else:
            print(f"    ✗ Upload failed: {response.status_code} - {response.text[:100]}")
            return False
    except Exception as e:
        print(f"    ✗ Upload error: {e}")
        return False

    # 4. Request 3D generation
    print("\n[4] Requesting 3D generation...")
    try:
        payload = {
            'job_id': job_id,
            'format': 'stl',
            'quality': 7,
            'dimensions': {
                'width': 512,
                'height': 512,
                'depth': 256
            }
        }

        response = requests.post(
            f"{BASE_URL}/api/generate-3d",
            json=payload
        )

        if response.status_code == 200:
            data = response.json()
            print(f"    ✓ Generation started: status={data.get('status')}")
        else:
            print(f"    ✗ Generation request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ✗ Generation request error: {e}")
        return False

    # 5. Wait for completion
    print("\n[5] Waiting for generation to complete...")
    max_attempts = 30  # 30 seconds max
    attempt = 0

    while attempt < max_attempts:
        try:
            response = requests.get(f"{BASE_URL}/api/job-status/{job_id}")

            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                progress = data.get('progress', 0)

                print(f"    • Status: {status} ({progress}%)")

                if status == 'completed':
                    download_url = data.get('download_url')
                    print(f"    ✓ Generation complete!")
                    print(f"    • Download URL: {download_url}")
                    break
                elif status in ['failed', 'error']:
                    print(f"    ✗ Generation failed: {data.get('error')}")
                    return False
        except Exception as e:
            print(f"    ✗ Status check error: {e}")
            return False

        time.sleep(1)
        attempt += 1

    if attempt >= max_attempts:
        print("    ✗ Generation timed out")
        return False

    # 6. Download STL file
    print("\n[6] Downloading STL file...")
    try:
        download_url = f"{BASE_URL}{download_url}"
        print(f"    • Full URL: {download_url}")

        response = requests.get(download_url, timeout=10)

        if response.status_code == 200:
            file_size = len(response.content)
            print(f"    ✓ STL downloaded: {file_size} bytes")

            # Analyze STL
            if file_size > 84:
                # Binary STL header check
                header = response.content[:80]
                triangle_count = int.from_bytes(response.content[80:84], 'little')

                print(f"\n[7] STL File Analysis:")
                print(f"    • Header: {header[:30]}...")
                print(f"    • Triangles: {triangle_count}")
                print(f"    • Expected size: ~{84 + 4 + triangle_count * 50} bytes")
                print(f"    • Actual size: {file_size} bytes")

                if triangle_count > 0:
                    print(f"\n    ✅ SUCCESS: Valid STL with {triangle_count} triangles!")
                    print(f"    • File should display properly in 3D viewer")
                    return True
                else:
                    print(f"\n    ✗ WARNING: STL has 0 triangles (placeholder file)")
                    return False
            else:
                print(f"    ✗ File size too small ({file_size} bytes) - appears to be placeholder")
                return False
        else:
            print(f"    ✗ Download failed: {response.status_code}")
            print(f"    • Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"    ✗ Download error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_stl_generation()

    print("\n" + "=" * 70)
    if success:
        print("✅ STL PREVIEW TEST PASSED")
        print("\nNext steps:")
        print("1. Open browser DevTools (F12)")
        print("2. Go to the Console tab")
        print("3. Upload an image and generate STL")
        print("4. Watch for console messages like:")
        print("   [ORFEAS] Loading 3D model from: ...")
        print("   [ORFEAS] Loading STL from: ...")
        print("   [ORFEAS] STL loaded, triangles: 12")
    else:
        print("❌ STL PREVIEW TEST FAILED")
        print("\nDebugging steps:")
        print("1. Verify backend is running: http://127.0.0.1:5000/health")
        print("2. Check backend logs for errors")
        print("3. Verify STL files are being generated in backend/output/")
    print("=" * 70)
