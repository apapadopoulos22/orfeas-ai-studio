import requests
import tempfile
from PIL import Image
import time
import struct

# Create test image
img = Image.new('RGB', (512, 512), color='blue')
with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
    img.save(f.name)
    temp_img = f.name

print("=" * 60)
print("TESTING STL GENERATION")
print("=" * 60)

print("\n[1] Creating 3D model...")
# Use correct endpoint
with open(temp_img, 'rb') as f:
    resp = requests.post(
        'http://127.0.0.1:5000/api/generate-3d',
        files={'image': f},
        data={'quality': '7', 'format': 'stl'},
        timeout=30
    )

print(f"[2] Response status: {resp.status_code}")
if resp.status_code == 200:
    result = resp.json()
    print(f"[3] Response: {result}")
    job_id = result.get('job_id')
    if job_id:
        print(f"[4] Job created: {job_id}")

        time.sleep(3)

        # Download the file
        print("[5] Downloading STL...")
        dl_resp = requests.get(f'http://127.0.0.1:5000/api/download/{job_id}/model.stl', timeout=10)
        print(f"[6] Download status: {dl_resp.status_code}")
        file_size = len(dl_resp.content)
        print(f"[7] File size: {file_size} bytes")

        if file_size > 100:
            try:
                triangles = struct.unpack('<I', dl_resp.content[80:84])[0]
                print(f"[8] Triangles: {triangles}")
                if triangles > 0:
                    print("\n✅ SUCCESS: Valid STL with real geometry!")
                else:
                    print("\n❌ FAIL: STL has 0 triangles (placeholder)")
            except Exception as e:
                print(f"[ERROR] Could not parse STL: {e}")
        else:
            print(f"\n❌ FAIL: File too small ({file_size} < 100)")
    else:
        print("❌ No job_id in response")
else:
    print(f"❌ Error: {resp.text}")

print("\n" + "=" * 60)
