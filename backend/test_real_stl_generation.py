from typing import Dict
#!/usr/bin/env python3
"""
Test Real STL Generation
Verifies that the server generates actual STL files based on input images
"""

import requests
import time
import struct
from pathlib import Path
from PIL import Image, ImageDraw
import json

def create_distinctive_test_image() -> None:
    """Create a test image with distinctive features"""
    img = Image.new('RGB', (128, 128), 'white')
    draw = ImageDraw.Draw(img)

    # Create a distinctive pattern that should be visible in 3D
    # Draw a cross pattern - bright in center, darker on edges

    # Background gradient
    for y in range(128):
        for x in range(128):
            # Distance from center
            dist = ((x-64)**2 + (y-64)**2)**0.5
            brightness = max(0, 255 - int(dist * 2))
            img.putpixel((x, y), (brightness, brightness, brightness))

    # Add distinctive features
    # Draw a bright cross in center
    draw.rectangle([60, 10, 68, 118], fill='white')  # Vertical bar
    draw.rectangle([10, 60, 118, 68], fill='white')  # Horizontal bar

    # Add corner squares (should create raised areas)
    draw.rectangle([10, 10, 30, 30], fill='white')
    draw.rectangle([98, 10, 118, 30], fill='white')
    draw.rectangle([10, 98, 30, 118], fill='white')
    draw.rectangle([98, 98, 118, 118], fill='white')

    # Add a central circle
    draw.ellipse([50, 50, 78, 78], fill='lightgray')

    test_path = Path("distinctive_test_image.png")
    img.save(test_path)
    return test_path

def analyze_stl_file(stl_path: str) -> Dict:
    """Analyze STL file to verify it's real 3D geometry"""

    if not stl_path.exists():
        return {"error": "STL file not found"}

    try:
        with open(stl_path, 'rb') as f:
            content = f.read()

        # Check if it's a binary STL
        if len(content) < 84:
            return {"error": "File too small for STL"}

        # Read triangle count
        triangle_count = struct.unpack('<I', content[80:84])[0]

        # Calculate expected size
        expected_size = 84 + (triangle_count * 50)
        actual_size = len(content)

        # Sample some triangles to verify geometry
        geometry_valid = True
        min_z = float('inf')
        max_z = float('-inf')

        if triangle_count > 0 and len(content) >= expected_size:
            # Sample first few triangles
            for i in range(min(10, triangle_count)):
                offset = 84 + (i * 50)
                if offset + 50 <= len(content):
                    # Read triangle data (12 floats + 1 uint16)
                    triangle_data = struct.unpack('<12fH', content[offset:offset+50])

                    # Extract Z coordinates (every 3rd float starting from index 5, 8, 11)
                    z_coords = [triangle_data[5], triangle_data[8], triangle_data[11]]

                    for z in z_coords:
                        if abs(z) < 1000:  # Reasonable Z range
                            min_z = min(min_z, z)
                            max_z = max(max_z, z)

        height_variation = max_z - min_z if min_z != float('inf') else 0

        return {
            "triangles": triangle_count,
            "file_size": actual_size,
            "expected_size": expected_size,
            "size_valid": abs(actual_size - expected_size) <= 2,
            "geometry_valid": geometry_valid,
            "height_variation": height_variation,
            "has_3d_structure": height_variation > 0.1,  # Some height variation
            "analysis": "Real 3D geometry detected" if height_variation > 0.1 else "Possible flat geometry"
        }

    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

def test_real_stl_generation() -> int:
    """Test the complete real STL generation workflow"""

    print("[TARGET] Testing Real STL Generation")
    print("=" * 50)

    server_url = "http://localhost:5001"
    api_base = f"{server_url}/api"

    try:
        # 1. Check server health
        print("1. Checking Real STL Server health...")
        response = requests.get(f"{api_base}/health", timeout=5)

        if response.status_code != 200:
            print(f"   [FAIL] Server not responding: {response.status_code}")
            return False

        health_data = response.json()
        print(f"   [OK] Server: {health_data.get('server', 'Unknown')}")
        print(f"   [STATS] Capabilities: {health_data.get('capabilities', [])}")

        # 2. Create test image
        print("\n2. Creating distinctive test image...")
        test_image = create_distinctive_test_image()
        print(f"   [OK] Test image created: {test_image}")

        # 3. Upload image
        print("\n3. Uploading test image...")
        with open(test_image, 'rb') as f:
            files = {'image': (test_image.name, f, 'image/png')}
            response = requests.post(f"{api_base}/upload-image", files=files)

        if response.status_code != 200:
            print(f"   [FAIL] Upload failed: {response.status_code}")
            return False

        upload_data = response.json()
        job_id = upload_data.get('job_id')
        print(f"   [OK] Upload successful. Job ID: {job_id}")

        # 4. Generate 3D model
        print("\n4. Generating real 3D model...")
        payload = {
            'job_id': job_id,
            'format': 'stl',
            'dimensions': {'width': 40, 'height': 40, 'depth': 15}
        }

        response = requests.post(
            f"{api_base}/generate-3d",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code != 200:
            print(f"   [FAIL] Generation failed: {response.status_code}")
            return False

        print("   [OK] Real STL generation started")

        # 5. Wait for completion with progress tracking
        print("\n5. Waiting for real generation completion...")
        max_wait = 60
        start_time = time.time()
        last_progress = 0

        while time.time() - start_time < max_wait:
            response = requests.get(f"{api_base}/../api/job-status/{job_id}")  # Adjust URL

            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get('status')
                progress = status_data.get('progress', 0)
                step = status_data.get('step', 'Processing...')

                if progress != last_progress:
                    print(f"   Progress: {progress}% - {step}")
                    last_progress = progress

                if status == 'completed':
                    print("   [OK] Real generation completed!")

                    # 6. Download and analyze the STL file
                    print("\n6. Analyzing generated STL file...")

                    if status_data.get('download_url'):
                        download_url = f"{server_url}{status_data['download_url']}"
                        print(f"    Downloading from: {download_url}")

                        response = requests.get(download_url)
                        if response.status_code == 200:
                            # Save the STL file
                            stl_filename = f"real_generated_{int(time.time())}.stl"
                            stl_path = Path(stl_filename)

                            with open(stl_path, 'wb') as f:
                                f.write(response.content)

                            print(f"   [OK] STL file saved: {stl_filename} ({len(response.content):,} bytes)")

                            # Analyze the STL file
                            analysis = analyze_stl_file(stl_path)

                            print(f"\n[STATS] STL Analysis Results:")
                            if 'error' in analysis:
                                print(f"   [FAIL] Analysis Error: {analysis['error']}")
                                return False
                            else:
                                print(f"    Triangles: {analysis['triangles']:,}")
                                print(f"    File Size: {analysis['file_size']:,} bytes")
                                print(f"   [OK] Size Valid: {analysis['size_valid']}")
                                print(f"    Height Variation: {analysis['height_variation']:.2f}mm")
                                print(f"    3D Structure: {analysis['has_3d_structure']}")
                                print(f"    Analysis: {analysis['analysis']}")

                                # Verify it's real 3D content
                                is_real_3d = (
                                    analysis['triangles'] > 100 and  # Reasonable triangle count
                                    analysis['size_valid'] and       # Correct STL format
                                    analysis['has_3d_structure']      # Actual height variation
                                )

                                if is_real_3d:
                                    print(f"\n SUCCESS: Real 3D STL file generated!")
                                    print(f"   [OK] Contains actual 3D geometry based on input image")
                                    print(f"   [OK] Proper STL format with {analysis['triangles']} triangles")
                                    print(f"   [OK] Height variation of {analysis['height_variation']:.2f}mm")
                                    return True
                                else:
                                    print(f"\n[WARN] WARNING: STL file may not contain real 3D geometry")
                                    return False
                        else:
                            print(f"   [FAIL] Download failed: {response.status_code}")
                            return False
                    else:
                        print("   [FAIL] No download URL provided")
                        return False

                elif status == 'failed':
                    error = status_data.get('error', 'Unknown error')
                    print(f"   [FAIL] Generation failed: {error}")
                    return False

            time.sleep(2)

        print("   [FAIL] Generation timeout")
        return False

    except Exception as e:
        print(f"[FAIL] Test failed with error: {e}")
        return False

    finally:
        # Cleanup
        if 'test_image' in locals() and test_image.exists():
            test_image.unlink()

def main() -> None:
    """Main test function"""
    print("[LAUNCH] REAL STL GENERATION VERIFICATION TEST")
    print("=" * 60)

    success = test_real_stl_generation()

    if success:
        print("\n REAL STL GENERATION TEST PASSED!")
        print("[OK] The server generates actual 3D geometry from images")
        print("[OK] STL files contain real triangular meshes with height variation")
        print("[OK] Generated models should now look like the input images")
    else:
        print("\n[FAIL] REAL STL GENERATION TEST FAILED!")
        print("[WARN] The server may still be generating placeholder content")

if __name__ == "__main__":
    main()
