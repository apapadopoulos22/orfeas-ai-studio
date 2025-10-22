"""
Manual test for upload endpoint
Run this while the test server is running to check if upload works
"""

import requests
import io
from PIL import Image

def test_upload() -> None:
    """Test upload endpoint manually"""

    # Create test image
    img = Image.new('RGB', (512, 512), color=(255, 0, 0))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    # Upload to server
    url = "http://127.0.0.1:5000/api/upload-image"
    files = {'image': ('test.png', img_bytes, 'image/png')}

    print(f"Sending POST request to {url}...")
    try:
        response = requests.post(url, files=files, timeout=5)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")
    except requests.Timeout:
        print("ERROR: Request timed out after 5 seconds")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    print("Testing upload endpoint...")
    test_upload()
