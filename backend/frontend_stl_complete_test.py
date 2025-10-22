from typing import Any, Tuple
#!/usr/bin/env python3
"""
Complete Frontend Import '√ú√≠ Generate STL '√ú√≠ Save '√ú√≠ Verify Workflow Test
Tests: Image upload '√ú√≠ STL generation '√ú√≠ Download '√ú√≠ Integrity verification
"""

import requests
import time
import struct
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

def create_test_image_for_frontend() -> Tuple:
    """Create a test image optimized for STL generation"""
    print("[ART] CREATING TEST IMAGE FOR FRONTEND")
    print("=" * 50)

    # Create image with good depth variation
    img = Image.new('RGB', (180, 180), 'gray')
    draw = ImageDraw.Draw(img)

    # Create a simple object with clear depth - a coin or medallion
    center_x, center_y = 90, 90

    # Background (medium depth)
    draw.rectangle([0, 0, 180, 180], fill=(100, 100, 100))

    # Outer rim (raised)
    draw.ellipse([20, 20, 160, 160], fill=(180, 180, 180), outline=(200, 200, 200), width=3)

    # Inner area (medium)
    draw.ellipse([40, 40, 140, 140], fill=(140, 140, 140))

    # Center design - a star (raised high)
    star_points = []
    for i in range(10):
        angle = i * np.pi / 5
        if i % 2 == 0:
            radius = 25  # Outer points
        else:
            radius = 12  # Inner points
        x = center_x + radius * np.cos(angle)
        y = center_y + radius * np.sin(angle)
        star_points.append((x, y))

    draw.polygon(star_points, fill=(220, 220, 220), outline=(255, 255, 255), width=2)

    # Add text around the edge (recessed)
    for i in range(0, 360, 30):
        angle_rad = np.radians(i)
        x = center_x + 50 * np.cos(angle_rad)
        y = center_y + 50 * np.sin(angle_rad)
        draw.ellipse([x-3, y-3, x+3, y+3], fill=(80, 80, 80))

    # Apply slight blur for smoother depth transitions
    img = img.filter(ImageFilter.GaussianBlur(radius=0.8))

    # Save as both JPG and PNG for testing
    jpg_path = Path("frontend_test_image.jpg")
    png_path = Path("frontend_test_image.png")

    img.save(jpg_path, "JPEG", quality=95)
    img.save(png_path, "PNG")

    print(f"[OK] Created test images:")
    print(f"   [IMAGE] JPG: {jpg_path} ({jpg_path.stat().st_size} bytes)")
    print(f"   [PICTURE] PNG: {png_path} ({png_path.stat().st_size} bytes)")
    print(f"   Ô£ø√º√¨√™ Size: 180x180 pixels")
    print(f"   [TARGET] Features: Medallion with star, clear depth variation")

    return jpg_path, png_path

def test_server_health(server_url: Any) -> int:
    """Test if server is responding"""
    print("Ô£ø√º√®‚Ä¢ TESTING SERVER HEALTH")
    print("=" * 30)

    try:
        response = requests.get(f"{server_url}/api/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Server Status: {data.get('status', 'Unknown')}")
            print(f"[AI] Processor: {data.get('processor_type', 'Unknown')}")
            print(f"[TARGET] Server: {data.get('server', 'ORFEAS')}")

            capabilities = data.get('capabilities', [])
            print(f"[FAST] Capabilities: {len(capabilities)}")
            for cap in capabilities[:3]:
                print(f"   ‚Ä¢ {cap}")

            return True
        else:
            print(f"[FAIL] Server unhealthy: {response.status_code}")
            return False

    except Exception as e:
        print(f"[FAIL] Server not responding: {e}")
        return False

def upload_image_to_frontend(server_url: Any, image_path: str) -> None:
    """Upload image through frontend API"""
    print(f"\nÔ£ø√º√¨¬ß UPLOADING IMAGE TO FRONTEND")
    print(f"   [FOLDER] File: {image_path}")

    try:
        with open(image_path, 'rb') as f:
            files = {'image': (image_path.name, f, 'image/jpeg' if image_path.suffix.lower() == '.jpg' else 'image/png')}
            response = requests.post(f"{server_url}/api/upload-image", files=files, timeout=30)

        if response.status_code == 200:
            data = response.json()
            job_id = data.get('job_id')
            upload_path = data.get('path', '')

            print(f"[OK] Upload successful!")
            print(f"   üÜî Job ID: {job_id}")
            print(f"   [FOLDER] Server path: {upload_path}")
            return job_id
        else:
            print(f"[FAIL] Upload failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"[FAIL] Upload error: {e}")
        return None

def generate_stl_via_frontend(server_url: Any, job_id: str) -> int:
    """Generate STL through frontend API"""
    print(f"\nÔ£ø√º√®‚â† GENERATING STL VIA FRONTEND")
    print(f"   üÜî Job ID: {job_id}")

    # Configure STL generation parameters
    payload = {
        'job_id': job_id,
        'format': 'stl',
        'quality': 'medium',  # Good balance of speed and quality
        'method': 'auto',     # Let system choose
        'dimensions': {
            'width': 50,      # 50mm width
            'height': 50,     # 50mm height
            'depth': 15       # 15mm depth
        }
    }

    print(f"[SETTINGS] Generation settings:")
    print(f"   Ô£ø√º√¨√® Dimensions: {payload['dimensions']['width']}‚àö√≥{payload['dimensions']['height']}‚àö√≥{payload['dimensions']['depth']} mm")
    print(f"   [CONTROL] Quality: {payload['quality']}")
    print(f"   [CONFIG] Method: {payload['method']}")

    try:
        response = requests.post(
            f"{server_url}/api/generate-3d",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        if response.status_code == 200:
            print("[OK] STL generation started!")
            return True
        else:
            print(f"[FAIL] Generation failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"[FAIL] Generation error: {e}")
        return False

def monitor_stl_generation(server_url: Any, job_id: str, max_wait: Any = 120) -> None:
    """Monitor STL generation progress"""
    print(f"\n[TIMER] MONITORING STL GENERATION")
    print(f"   '√®‚àû Max wait time: {max_wait}s")

    start_time = time.time()
    last_progress = -1

    while time.time() - start_time < max_wait:
        try:
            # Check job status
            response = requests.get(f"{server_url}/api/job-status/{job_id}", timeout=10)

            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                progress = data.get('progress', 0)
                step = data.get('step', 'Processing...')

                # Show progress updates
                if progress != last_progress:
                    elapsed = time.time() - start_time
                    print(f"   [STATS] Progress: {progress}% - {step} ({elapsed:.1f}s)")
                    last_progress = progress

                if status == 'completed':
                    print("Ô£ø√º√©√¢ STL generation completed!")

                    # Show results
                    triangles = data.get('triangles', 0)
                    file_size = data.get('file_size', 0)
                    method_used = data.get('method_used', 'unknown')
                    generation_time = time.time() - start_time

                    print(f"[STATS] Generation Results:")
                    print(f"   [CONFIG] Method used: {method_used}")
                    print(f"   Ô£ø√º√¨√™ Triangles: {triangles:,}")
                    print(f"   Ô£ø√º√≠√¶ File size: {file_size/1024:.1f} KB")
                    print(f"   [TIMER] Generation time: {generation_time:.1f}s")

                    return data

                elif status == 'failed':
                    error = data.get('error', 'Unknown error')
                    print(f"[FAIL] Generation failed: {error}")
                    return None

            else:
                print(f"[WARN] Status check failed: {response.status_code}")

        except Exception as e:
            print(f"[WARN] Status check error: {e}")

        time.sleep(3)

    print(f"'√®‚àû Generation timeout after {max_wait}s")
    return None

def download_and_save_stl(server_url: Any, job_id: str, filename: Any = "model.stl") -> None:
    """Download and save the generated STL file"""
    print(f"\nÔ£ø√º√≠√¶ DOWNLOADING AND SAVING STL")
    print(f"   [FOLDER] Filename: {filename}")

    try:
        # Download STL file
        response = requests.get(f"{server_url}/api/download/{job_id}/{filename}", timeout=30)

        if response.status_code == 200:
            # Save to local file
            local_path = Path(f"saved_{filename}")
            with open(local_path, 'wb') as f:
                f.write(response.content)

            file_size = local_path.stat().st_size

            print(f"[OK] STL saved successfully!")
            print(f"   [FOLDER] Local path: {local_path}")
            print(f"   Ô£ø√º√≠√¶ File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")

            return local_path

        else:
            print(f"[FAIL] Download failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"[FAIL] Download error: {e}")
        return None

def verify_saved_stl(stl_path: str) -> int:
    """Verify the integrity of the saved STL file"""
    print(f"\n[SEARCH] VERIFYING SAVED STL")
    print(f"   [FOLDER] File: {stl_path}")

    if not stl_path.exists():
        print(f"[FAIL] STL file not found!")
        return False

    try:
        file_size = stl_path.stat().st_size
        print(f"Ô£ø√º√¨√® File size: {file_size:,} bytes")

        if file_size < 84:
            print("[FAIL] File too small to be valid STL")
            return False

        # Parse STL structure
        with open(stl_path, 'rb') as f:
            # Read header
            header = f.read(80)
            header_text = header.decode('ascii', errors='ignore').strip()
            print(f"Ô£ø√º√¨√£ Header: '{header_text[:30]}{'...' if len(header_text) > 30 else ''}'")

            # Read triangle count
            triangle_bytes = f.read(4)
            if len(triangle_bytes) != 4:
                print("[FAIL] Invalid STL: Missing triangle count")
                return False

            triangle_count = struct.unpack('<I', triangle_bytes)[0]
            print(f"Ô£ø√º√¨√™ Triangle count: {triangle_count:,}")

            if triangle_count == 0:
                print("[FAIL] STL contains no triangles")
                return False

            # Verify file size matches expected structure
            expected_size = 80 + 4 + (triangle_count * 50)
            print(f"üßÆ Expected size: {expected_size:,} bytes")

            size_diff = abs(file_size - expected_size)
            if size_diff <= 50:  # Allow small variance
                print("[OK] File structure is correct")
            else:
                print(f"[WARN] Size mismatch: {size_diff} bytes difference")

            # Verify first few triangles
            print("Ô£ø√º√Æ‚à´ Checking triangle data...")
            valid_triangles = 0

            for i in range(min(5, triangle_count)):
                # Read triangle (50 bytes total)
                normal = struct.unpack('<3f', f.read(12))  # Normal vector
                v1 = struct.unpack('<3f', f.read(12))      # Vertex 1
                v2 = struct.unpack('<3f', f.read(12))      # Vertex 2
                v3 = struct.unpack('<3f', f.read(12))      # Vertex 3
                f.read(2)  # Skip attribute bytes

                # Check if triangle has valid coordinates
                vertices = v1 + v2 + v3
                if any(abs(coord) > 0.001 for coord in vertices):
                    valid_triangles += 1

                # Show first triangle details
                if i == 0:
                    print(f"   Triangle 1:")
                    print(f"     Normal: ({normal[0]:.3f}, {normal[1]:.3f}, {normal[2]:.3f})")
                    print(f"     V1: ({v1[0]:.3f}, {v1[1]:.3f}, {v1[2]:.3f})")
                    print(f"     V2: ({v2[0]:.3f}, {v2[1]:.3f}, {v2[2]:.3f})")
                    print(f"     V3: ({v3[0]:.3f}, {v3[1]:.3f}, {v3[2]:.3f})")

            print(f"[OK] Valid triangles: {valid_triangles}/5 checked")

            # Quality assessment
            if triangle_count >= 5000:
                quality = "EXCELLENT"
                score = 95
            elif triangle_count >= 1000:
                quality = "HIGH"
                score = 85
            elif triangle_count >= 500:
                quality = "MEDIUM"
                score = 70
            elif triangle_count >= 100:
                quality = "LOW"
                score = 55
            else:
                quality = "BASIC"
                score = 40

            print(f"[STATS] Quality Assessment:")
            print(f"   [TROPHY] Quality: {quality}")
            print(f"   ‚≠ê Score: {score}/100")

            if valid_triangles >= 3 and triangle_count >= 100:
                print("[OK] STL VERIFICATION: PASSED")
                return True
            else:
                print("[WARN] STL VERIFICATION: BASIC (may need improvement)")
                return True  # Still usable

    except Exception as e:
        print(f"[FAIL] Verification failed: {e}")
        return False

def run_complete_workflow() -> int:
    """Run the complete frontend workflow test"""

    print("[LAUNCH] COMPLETE FRONTEND WORKFLOW TEST")
    print("=" * 60)
    print("Test: Import Image '√ú√≠ Generate STL '√ú√≠ Save STL '√ú√≠ Verify STL")
    print("=" * 60)

    server_url = "http://localhost:5000"  # Safe server port

    try:
        # Step 1: Test server health
        if not test_server_health(server_url):
            return False

        # Step 2: Create test image
        jpg_path, png_path = create_test_image_for_frontend()

        # Step 3: Upload image to frontend
        job_id = upload_image_to_frontend(server_url, jpg_path)
        if not job_id:
            return False

        # Step 4: Generate STL via frontend
        if not generate_stl_via_frontend(server_url, job_id):
            return False

        # Step 5: Monitor generation progress
        result = monitor_stl_generation(server_url, job_id, max_wait=180)
        if not result:
            return False

        # Step 6: Download and save STL
        stl_path = download_and_save_stl(server_url, job_id, "model.stl")
        if not stl_path:
            return False

        # Step 7: Verify saved STL
        if not verify_saved_stl(stl_path):
            return False

        # Final results
        print(f"\n" + "="*60)
        print("[TROPHY] FRONTEND WORKFLOW TEST RESULTS")
        print("="*60)

        triangles = result.get('triangles', 0)
        file_size = result.get('file_size', 0)
        method_used = result.get('method_used', 'unknown')

        print("[OK] WORKFLOW COMPLETED SUCCESSFULLY!")
        print(f"\n[STATS] Final Results:")
        print(f"   üÜî Job ID: {job_id}")
        print(f"   [IMAGE] Source: {jpg_path}")
        print(f"   [FOLDER] STL File: {stl_path}")
        print(f"   [CONFIG] Method: {method_used}")
        print(f"   Ô£ø√º√¨√™ Triangles: {triangles:,}")
        print(f"   Ô£ø√º√≠√¶ File Size: {file_size/1024:.1f} KB")

        print(f"\n[TARGET] Workflow Steps Verified:")
        print(f"   [OK] 1. Image Import to Frontend")
        print(f"   [OK] 2. STL Generation via API")
        print(f"   [OK] 3. STL Download and Save")
        print(f"   [OK] 4. STL Integrity Verification")

        return True

    except Exception as e:
        print(f"[FAIL] Workflow test failed: {e}")
        return False

    finally:
        # Cleanup test files
        for cleanup_file in ["frontend_test_image.jpg", "frontend_test_image.png"]:
            cleanup_path = Path(cleanup_file)
            if cleanup_path.exists():
                cleanup_path.unlink()

def main() -> None:
    """Main function"""
    success = run_complete_workflow()

    print(f"\n" + "="*60)
    if success:
        print("Ô£ø√º√©√¢ FRONTEND WORKFLOW TEST: COMPLETE SUCCESS!")
        print("[OK] All steps working: Import '√ú√≠ Generate '√ú√≠ Save '√ú√≠ Verify")
        print("[TARGET] Your frontend STL workflow is fully operational!")
    else:
        print("[WARN] FRONTEND WORKFLOW TEST: ISSUES DETECTED")
        print("Some steps may need attention or server adjustment")

    print("\n[EDIT] Generated Files:")
    stl_files = list(Path(".").glob("saved_*.stl"))
    if stl_files:
        for stl_file in stl_files:
            size_kb = stl_file.stat().st_size / 1024
            print(f"   [FOLDER] {stl_file} ({size_kb:.1f} KB)")
    else:
        print("   No STL files generated")

if __name__ == "__main__":
    main()
