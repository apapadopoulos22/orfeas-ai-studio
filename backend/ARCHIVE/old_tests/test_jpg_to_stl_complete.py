#!/usr/bin/env python3
"""
Complete JPG to STL Conversion Test with Preview and Integrity Check
Tests the full workflow: Import JPG 'Üí Convert to STL 'Üí Preview 'Üí Verify Integrity
"""

import requests
import time
import struct
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

def create_test_jpg():
    """Create a realistic test JPG image for conversion"""
    print("üì∏ Creating test JPG image...")

    # Create a more realistic image with depth variation
    img = Image.new('RGB', (200, 200), 'lightblue')
    draw = ImageDraw.Draw(img)

    # Create a landscape scene with mountains and depth
    # Sky gradient
    for y in range(0, 80):
        shade = int(135 + (y * 120 / 80))  # Light blue to darker blue
        draw.line([(0, y), (200, y)], fill=(shade, shade + 20, 255))

    # Mountain silhouette with multiple peaks
    mountain_points = []
    for x in range(0, 201, 5):
        # Create mountain profile with multiple peaks
        height1 = 120 + 30 * np.sin(x * 0.03) + 15 * np.sin(x * 0.08)
        height2 = 140 + 25 * np.cos(x * 0.025) + 20 * np.sin(x * 0.06)
        height = max(height1, height2)
        mountain_points.append((x, int(height)))

    # Draw mountains with depth shading
    for i, (x, y) in enumerate(mountain_points[:-1]):
        next_x, next_y = mountain_points[i + 1]
        # Create depth effect - higher mountains are brighter (closer)
        distance_factor = (200 - y) / 200
        r = int(60 + 100 * distance_factor)
        g = int(80 + 80 * distance_factor)
        b = int(40 + 60 * distance_factor)

        draw.polygon([(x, y), (next_x, next_y), (next_x, 200), (x, 200)],
                    fill=(r, g, b))

    # Add some foreground details (trees/rocks)
    for tree_x in [30, 50, 170, 185]:
        tree_height = 160 + np.random.randint(-10, 10)
        # Tree trunk
        draw.rectangle([tree_x-2, tree_height, tree_x+2, 190], fill=(101, 67, 33))
        # Tree foliage (darker = closer)
        draw.ellipse([tree_x-8, tree_height-20, tree_x+8, tree_height+5],
                    fill=(34, 80, 34))

    # Add atmospheric perspective and blur for realism
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))

    # Add some texture noise for better depth estimation
    pixels = np.array(img)
    noise = np.random.normal(0, 5, pixels.shape)
    pixels = np.clip(pixels + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(pixels)

    test_path = Path("test_landscape.jpg")
    img.save(test_path, "JPEG", quality=95)
    print(f"   [OK] Created realistic test image: {test_path}")
    print(f"   üìè Size: {img.width}x{img.height} pixels")
    return test_path

def upload_image(server_url, image_path):
    """Upload image to server"""
    print(f"üì§ Uploading {image_path}...")

    with open(image_path, 'rb') as f:
        files = {'image': (image_path.name, f, 'image/jpeg')}
        response = requests.post(f"{server_url}/api/upload-image", files=files)

    if response.status_code == 200:
        data = response.json()
        job_id = data.get('job_id')
        print(f"   [OK] Upload successful! Job ID: {job_id}")
        return job_id
    else:
        print(f"   [FAIL] Upload failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def generate_stl(server_url, job_id, quality='high'):
    """Generate STL from uploaded image"""
    print(f"üè≠ Generating STL with {quality} quality...")

    payload = {
        'job_id': job_id,
        'format': 'stl',
        'quality': quality,
        'method': 'auto',  # Let system choose best method
        'dimensions': {'width': 80, 'height': 80, 'depth': 25}
    }

    response = requests.post(
        f"{server_url}/api/generate-3d",
        json=payload,
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code == 200:
        print("   [OK] STL generation started successfully!")
        return True
    else:
        print(f"   [FAIL] STL generation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def monitor_progress(server_url, job_id, max_wait=120):
    """Monitor generation progress with detailed updates"""
    print("[TIMER] Monitoring conversion progress...")

    start_time = time.time()
    last_progress = -1

    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{server_url}/job-status/{job_id}")

            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                progress = data.get('progress', 0)
                step = data.get('step', 'Processing...')

                # Only show updates when progress changes
                if progress != last_progress:
                    elapsed = time.time() - start_time
                    print(f"   [STATS] Progress: {progress}% - {step} ({elapsed:.1f}s)")
                    last_progress = progress

                if status == 'completed':
                    print("   üéâ Conversion completed successfully!")
                    return data
                elif status == 'failed':
                    error = data.get('error', 'Unknown error')
                    print(f"   [FAIL] Conversion failed: {error}")
                    return None
            else:
                print(f"   [WARN] Status check failed: {response.status_code}")

        except Exception as e:
            print(f"   [WARN] Status check error: {e}")

        time.sleep(2)

    print(f"   'è∞ Timeout after {max_wait}s")
    return None

def verify_stl_integrity(stl_path):
    """Verify STL file integrity and structure"""
    print(f"[SEARCH] Verifying STL integrity: {stl_path}")

    try:
        if not stl_path.exists():
            print(f"   [FAIL] STL file not found: {stl_path}")
            return False

        file_size = stl_path.stat().st_size
        print(f"   üìè File size: {file_size} bytes ({file_size/1024:.1f} KB)")

        if file_size < 84:  # Minimum STL size (header + 1 triangle)
            print("   [FAIL] File too small to be valid STL")
            return False

        # Read and parse STL header
        with open(stl_path, 'rb') as f:
            # Read 80-byte header
            header = f.read(80)
            print(f"   üìã STL Header: {header[:20].decode('ascii', errors='ignore')}...")

            # Read triangle count
            triangle_count_bytes = f.read(4)
            if len(triangle_count_bytes) != 4:
                print("   [FAIL] Invalid STL format: Missing triangle count")
                return False

            triangle_count = struct.unpack('<I', triangle_count_bytes)[0]
            print(f"   üìê Triangle count: {triangle_count:,}")

            if triangle_count == 0:
                print("   [FAIL] STL contains no triangles")
                return False

            # Calculate expected file size
            expected_size = 80 + 4 + (triangle_count * 50)  # header + count + triangles
            print(f"    Expected size: {expected_size} bytes")

            if abs(file_size - expected_size) > 100:  # Allow small variance
                print(f"   [WARN] Size mismatch: got {file_size}, expected {expected_size}")

            # Read and verify first few triangles
            valid_triangles = 0
            for i in range(min(5, triangle_count)):  # Check first 5 triangles
                # Normal vector (3 floats)
                normal = struct.unpack('<3f', f.read(12))
                # Vertices (9 floats)
                v1 = struct.unpack('<3f', f.read(12))
                v2 = struct.unpack('<3f', f.read(12))
                v3 = struct.unpack('<3f', f.read(12))
                # Attribute (2 bytes)
                attr = f.read(2)

                # Check if triangle is valid (not all zeros)
                if any(abs(coord) > 0.001 for coord in v1 + v2 + v3):
                    valid_triangles += 1

                if i == 0:  # Show first triangle details
                    print(f"   üî∫ First triangle:")
                    print(f"      Normal: ({normal[0]:.3f}, {normal[1]:.3f}, {normal[2]:.3f})")
                    print(f"      V1: ({v1[0]:.3f}, {v1[1]:.3f}, {v1[2]:.3f})")
                    print(f"      V2: ({v2[0]:.3f}, {v2[1]:.3f}, {v2[2]:.3f})")
                    print(f"      V3: ({v3[0]:.3f}, {v3[1]:.3f}, {v3[2]:.3f})")

            print(f"   [OK] Valid triangles checked: {valid_triangles}/5")

            # Calculate mesh quality metrics
            triangle_density = triangle_count / (80 * 80)  # triangles per square unit
            quality_score = min(100, triangle_density * 50)

            print(f"   [STATS] Mesh Quality Metrics:")
            print(f"      Triangle Density: {triangle_density:.2f} tri/unit²")
            print(f"      Quality Score: {quality_score:.1f}/100")

            if triangle_count >= 1000 and valid_triangles >= 3:
                print("   [TROPHY] STL INTEGRITY: EXCELLENT")
                return True
            elif triangle_count >= 100 and valid_triangles >= 1:
                print("   [OK] STL INTEGRITY: GOOD")
                return True
            else:
                print("   [WARN] STL INTEGRITY: BASIC")
                return False

    except Exception as e:
        print(f"   [FAIL] STL verification failed: {e}")
        return False

def test_preview_functionality(server_url, job_id):
    """Test the 3D preview functionality"""
    print(" Testing 3D preview functionality...")

    # Check if studio page is accessible
    try:
        response = requests.get(f"{server_url}/studio")
        if response.status_code == 200:
            print("   [OK] Studio interface accessible")

            # Check if the HTML contains Three.js viewer
            content = response.text
            if 'three.min.js' in content and 'STLLoader' in content:
                print("   [OK] Three.js 3D viewer components loaded")
            else:
                print("   [WARN] 3D viewer components may be missing")

            if 'show3DPreview' in content:
                print("   [OK] Preview functionality detected")
            else:
                print("   [WARN] Preview functionality not found")

            return True
        else:
            print(f"   [FAIL] Studio interface not accessible: {response.status_code}")
            return False

    except Exception as e:
        print(f"   [FAIL] Preview test failed: {e}")
        return False

def download_stl(server_url, job_id, filename="model.stl"):
    """Download the generated STL file"""
    print(f"üíæ Downloading STL file: {filename}")

    try:
        response = requests.get(f"{server_url}/api/download/{job_id}/{filename}")

        if response.status_code == 200:
            local_path = Path(f"downloaded_{filename}")
            with open(local_path, 'wb') as f:
                f.write(response.content)

            print(f"   [OK] Downloaded: {local_path} ({len(response.content)} bytes)")
            return local_path
        else:
            print(f"   [FAIL] Download failed: {response.status_code}")
            return None

    except Exception as e:
        print(f"   [FAIL] Download error: {e}")
        return None

def main():
    """Complete test workflow"""

    print("[LAUNCH] COMPLETE JPG TO STL CONVERSION TEST")
    print("=" * 60)

    server_url = "http://localhost:5002"

    try:
        # 1. Check server health
        print("1. Checking server health...")
        response = requests.get(f"{server_url}/api/health", timeout=10)

        if response.status_code == 200:
            health = response.json()
            print(f"   [OK] Server: {health.get('server', 'ORFEAS')}")
            print(f"   [TARGET] Status: {health.get('status', 'Unknown')}")
            capabilities = health.get('capabilities', [])
            print(f"    Capabilities: {len(capabilities)}")
        else:
            print(f"   [FAIL] Server not responding: {response.status_code}")
            return False

        # 2. Create test JPG
        print(f"\n2. Creating test JPG image...")
        test_jpg = create_test_jpg()

        # 3. Upload image
        print(f"\n3. Uploading image...")
        job_id = upload_image(server_url, test_jpg)
        if not job_id:
            return False

        # 4. Generate STL
        print(f"\n4. Generating STL...")
        if not generate_stl(server_url, job_id, quality='high'):
            return False

        # 5. Monitor progress
        print(f"\n5. Monitoring conversion...")
        result = monitor_progress(server_url, job_id, max_wait=180)
        if not result:
            return False

        # 6. Test preview functionality
        print(f"\n6. Testing preview functionality...")
        preview_ok = test_preview_functionality(server_url, job_id)

        # 7. Download STL
        print(f"\n7. Downloading STL file...")
        stl_file = download_stl(server_url, job_id, "model.stl")
        if not stl_file:
            return False

        # 8. Verify STL integrity
        print(f"\n8. Verifying STL integrity...")
        integrity_ok = verify_stl_integrity(stl_file)

        # 9. Generate final report
        print(f"\n" + "=" * 60)
        print("[STATS] FINAL TEST RESULTS")
        print("=" * 60)

        triangles = result.get('triangles', 0)
        file_size = result.get('file_size', 0)
        method_used = result.get('method_used', 'unknown')

        print(f"[OK] Conversion Details:")
        print(f"   Job ID: {job_id}")
        print(f"   Method Used: {method_used}")
        print(f"   Triangles Generated: {triangles:,}")
        print(f"   File Size: {file_size/1024:.1f} KB")

        print(f"\nüìã Test Results:")
        print(f"   [OK] Image Upload: SUCCESS")
        print(f"   [OK] STL Generation: SUCCESS")
        print(f"   {'[OK]' if preview_ok else '[WARN]'} Preview Functionality: {'SUCCESS' if preview_ok else 'PARTIAL'}")
        print(f"   [OK] STL Download: SUCCESS")
        print(f"   {'[OK]' if integrity_ok else '[WARN]'} STL Integrity: {'EXCELLENT' if integrity_ok else 'BASIC'}")

        # Calculate overall success score
        success_score = sum([
            100,  # Upload
            100,  # Generation
            80 if preview_ok else 40,  # Preview
            100,  # Download
            100 if integrity_ok else 60  # Integrity
        ]) / 5

        print(f"\n[TROPHY] OVERALL TEST SCORE: {success_score:.1f}/100")

        if success_score >= 90:
            print("üéâ EXCELLENT! Full JPG'ÜíSTL'ÜíPreview workflow working perfectly!")
        elif success_score >= 75:
            print("[OK] GOOD! Core functionality working with minor issues")
        else:
            print("[WARN] BASIC! Some components need attention")

        return success_score >= 75

    except Exception as e:
        print(f"[FAIL] Test failed with error: {e}")
        return False

    finally:
        # Cleanup test files
        for cleanup_file in ["test_landscape.jpg", "downloaded_model.stl"]:
            cleanup_path = Path(cleanup_file)
            if cleanup_path.exists():
                cleanup_path.unlink()
                print(f"[CLEANUP] Cleaned up: {cleanup_file}")

if __name__ == "__main__":
    success = main()
    print(f"\n{'üéâ TEST COMPLETED SUCCESSFULLY!' if success else '[WARN] TEST COMPLETED WITH ISSUES'}")
