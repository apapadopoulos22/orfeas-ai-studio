"""
Test script to verify STL generation is working correctly
"""
import requests
import struct
import time

BASE_URL = "http://127.0.0.1:5000"

print("=" * 60)
print("ORFEAS STL GENERATION TEST")
print("=" * 60)

# Test 1: Check health endpoint
print("\n[TEST 1] Checking backend health...")
try:
    resp = requests.get(f"{BASE_URL}/health", timeout=5)
    if resp.status_code == 200:
        print("✅ Backend is running and healthy")
        print(f"   Response: {resp.json()}")
    else:
        print(f"⚠️  Backend returned status {resp.status_code}")
except Exception as e:
    print(f"❌ Backend not responding: {e}")
    exit(1)

# Test 2: Try to generate a 3D model
print("\n[TEST 2] Testing 3D model generation...")
try:
    # Create a test image file for generation
    from PIL import Image
    import tempfile
    import os

    # Create a simple test image
    img = Image.new('RGB', (512, 512), color='blue')
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        img.save(f.name)
        temp_image = f.name

    with open(temp_image, 'rb') as f:
        files = {'image': f}
        data = {
            'quality': '7',
            'format': 'stl',
            'width': '20',
            'height': '20',
            'depth': '20'
        }
        resp = requests.post(f"{BASE_URL}/api/generate", files=files, data=data, timeout=30)

    if resp.status_code == 200:
        print("✅ Generation request successful")
        result = resp.json()
        print(f"   Job ID: {result.get('job_id')}")
        job_id = result.get('job_id')

        # Wait a moment for processing
        time.sleep(2)

        # Test 3: Download the generated file
        print("\n[TEST 3] Downloading generated STL file...")
        download_resp = requests.get(
            f"{BASE_URL}/api/download/{job_id}/model.stl",
            timeout=10
        )

        if download_resp.status_code == 200:
            stl_data = download_resp.content
            print(f"✅ STL file downloaded successfully")
            print(f"   File size: {len(stl_data)} bytes")

            # Verify it's a valid STL file
            if len(stl_data) >= 84:  # Minimum valid STL: 80 byte header + 4 byte triangle count
                header = stl_data[:80]
                triangle_count = struct.unpack('<I', stl_data[80:84])[0]
                expected_size = 84 + triangle_count * 50  # Each triangle is 50 bytes

                print(f"   Header: {header[:30].decode('latin-1', errors='ignore')}")
                print(f"   Triangles: {triangle_count}")
                print(f"   Expected size: ~{expected_size} bytes")

                if triangle_count > 0:
                    print(f"✅ VALID STL FILE with {triangle_count} triangles!")
                else:
                    print(f"⚠️  WARNING: STL has 0 triangles (placeholder)")
            else:
                print(f"❌ File too small to be valid STL: {len(stl_data)} bytes")
        else:
            print(f"❌ Download failed: {download_resp.status_code}")
            print(f"   Response: {download_resp.text}")
    else:
        print(f"❌ Generation request failed: {resp.status_code}")
        print(f"   Response: {resp.text}")

    # Cleanup
    os.unlink(temp_image)

except Exception as e:
    print(f"❌ Test failed with error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
