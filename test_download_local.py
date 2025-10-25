#!/usr/bin/env python3
"""Test local backend download endpoint"""
import requests
import time
import os

# Configuration - test LOCAL backend first
JOB_ID = "2c118d08-54e3-4102-b702-669c9666dd14"
DOWNLOAD_URL = f"http://127.0.0.1:5000/api/download/{JOB_ID}/model_{JOB_ID}.stl"
OUTPUT_FILE = f"test_download_local_{JOB_ID}.stl"

print(f"[TEST] Testing LOCAL backend at: http://127.0.0.1:5000")
print(f"[TEST] Download URL: {DOWNLOAD_URL}")
print(f"[TEST] Will save to: {OUTPUT_FILE}")

try:
    print(f"\n[TEST] Sending download request...")
    start_time = time.time()

    response = requests.get(DOWNLOAD_URL, stream=True, timeout=30)

    print(f"[TEST] Response Status: {response.status_code}")
    print(f"[TEST] Response Headers:")
    for key, value in response.headers.items():
        if key.lower() in ['content-length', 'content-type', 'content-disposition']:
            print(f"  {key}: {value}")

    content_length = response.headers.get('Content-Length')
    if content_length:
        print(f"[TEST] Expected file size: {int(content_length):,} bytes")

    # Download file
    bytes_downloaded = 0
    print(f"\n[TEST] Downloading...")

    with open(OUTPUT_FILE, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
                bytes_downloaded += len(chunk)
                if bytes_downloaded % (5*1024*1024) == 0:  # Print every 5MB
                    print(f"[TEST]   Downloaded: {bytes_downloaded:,} bytes")

    elapsed = time.time() - start_time
    actual_size = os.path.getsize(OUTPUT_FILE)

    print(f"\n[TEST] ✅ Download complete!")
    print(f"[TEST] Time taken: {elapsed:.2f} seconds")
    print(f"[TEST] Actual file size: {actual_size:,} bytes")
    print(f"[TEST] Expected file size: {int(content_length) if content_length else 'Unknown'} bytes")

    if content_length and actual_size != int(content_length):
        print(f"\n[TEST] ❌ SIZE MISMATCH!")
        print(f"[TEST]    Expected: {int(content_length):,} bytes")
        print(f"[TEST]    Actual: {actual_size:,} bytes")
        print(f"[TEST]    Missing: {int(content_length) - actual_size:,} bytes")
    else:
        print(f"\n[TEST] ✅ File size matches!")

except Exception as e:
    print(f"\n[TEST] ❌ Error: {e}")
    import traceback
    traceback.print_exc()
