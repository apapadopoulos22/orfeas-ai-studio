import requests
import tempfile
from PIL import Image
import time
import struct
import uuid

BASE_URL = "http://127.0.0.1:5000"

print("=" * 70)
print("ORFEAS STL GENERATION WORKFLOW TEST")
print("=" * 70)

# Step 1: Create test image
print("\n[STEP 1] Creating test image...")
img = Image.new('RGB', (512, 512), color='blue')
with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
    img.save(f.name)
    temp_img = f.name
print(f"✓ Test image created")

# Step 2: Upload image
print("\n[STEP 2] Uploading image to backend...")
with open(temp_img, 'rb') as f:
    upload_resp = requests.post(
        f"{BASE_URL}/api/upload-image",
        files={'image': f},
        timeout=10
    )

print(f"Upload response: {upload_resp.status_code}")
if upload_resp.status_code != 200:
    print(f"✗ Upload failed: {upload_resp.text}")
    exit(1)

upload_result = upload_resp.json()
print(f"Upload result: {upload_result}")

if 'job_id' in upload_result:
    job_id = upload_result['job_id']
    print(f"✓ Image uploaded, Job ID: {job_id}")
elif 'filename' in upload_result:
    # Might need to create our own job_id
    job_id = str(uuid.uuid4())
    print(f"✓ Image uploaded as: {upload_result['filename']}")
    print(f"✓ Using generated job ID: {job_id}")
else:
    print(f"✗ Unexpected response: {upload_result}")
    exit(1)

# Step 3: Request 3D generation
print(f"\n[STEP 3] Requesting 3D generation (job_id={job_id})...")
gen_resp = requests.post(
    f"{BASE_URL}/api/generate-3d",
    json={
        'job_id': job_id,
        'format': 'stl',
        'quality': 7,
        'dimensions': {'width': 20, 'height': 20, 'depth': 20}
    },
    timeout=10
)

print(f"Generation response: {gen_resp.status_code}")
if gen_resp.status_code not in [200, 201]:
    print(f"✗ Generation failed: {gen_resp.text}")
    exit(1)

gen_result = gen_resp.json()
print(f"Generation result: {gen_result}")
print(f"✓ Generation request accepted, status: {gen_result.get('status')}")

# Step 4: Wait for generation
print(f"\n[STEP 4] Waiting for generation to complete...")
time.sleep(4)

# Step 5: Check job status
print(f"\n[STEP 5] Checking job status...")
status_resp = requests.get(f"{BASE_URL}/api/job-status/{job_id}", timeout=10)
print(f"Status response: {status_resp.status_code}")
if status_resp.status_code == 200:
    status_result = status_resp.json()
    print(f"Job status: {status_result.get('status')}")
    print(f"Progress: {status_result.get('progress')}%")

# Step 6: Download the STL file
print(f"\n[STEP 6] Downloading STL file...")
dl_resp = requests.get(
    f"{BASE_URL}/api/download/{job_id}/model.stl",
    timeout=10
)

print(f"Download response: {dl_resp.status_code}")
if dl_resp.status_code != 200:
    print(f"✗ Download failed: {dl_resp.text}")
    exit(1)

file_size = len(dl_resp.content)
print(f"✓ File downloaded, size: {file_size} bytes")

# Step 7: Analyze STL file
print(f"\n[STEP 7] Analyzing STL file...")
if file_size < 84:
    print(f"✗ FAIL: File too small ({file_size} bytes, needs >84)")
    print(f"   This is likely a placeholder file")
    exit(1)

try:
    header = dl_resp.content[:80]
    triangles = struct.unpack('<I', dl_resp.content[80:84])[0]
    expected_size = 84 + (triangles * 50)

    print(f"Header: {header[:30]}")
    print(f"Triangles in file: {triangles}")
    print(f"Expected file size: ~{expected_size} bytes")
    print(f"Actual file size: {file_size} bytes")

    if triangles == 0:
        print(f"\n✗ FAIL: STL has 0 triangles (empty placeholder)")
        exit(1)
    elif triangles > 0:
        print(f"\n✅ SUCCESS: Valid STL with {triangles} triangles!")
        print(f"   File should display properly in 3D viewer")
    else:
        print(f"\n? Unexpected triangle count: {triangles}")
except Exception as e:
    print(f"\n? Could not parse STL: {e}")

print("\n" + "=" * 70)
