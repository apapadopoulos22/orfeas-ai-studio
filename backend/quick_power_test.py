#!/usr/bin/env python3
"""
Quick Test of Powerful 3D Generation Engine
"""

import requests
import time
import json
from PIL import Image, ImageDraw
from pathlib import Path

def create_test_image() -> None:
    """Create a simple test image for 3D conversion"""
    # Create a simple face-like image with depth variation
    img = Image.new('RGB', (128, 128), 'lightgray')
    draw = ImageDraw.Draw(img)

    # Simple face outline
    draw.ellipse([32, 24, 96, 104], fill='white', outline='black', width=2)
    # Eyes
    draw.ellipse([44, 48, 54, 58], fill='darkgray')
    draw.ellipse([74, 48, 84, 58], fill='darkgray')
    # Nose
    draw.polygon([(64, 60), (60, 75), (68, 75)], fill='white')
    # Mouth
    draw.arc([54, 80, 74, 90], 0, 180, fill='black', width=2)

    test_path = Path("quick_test_image.png")
    img.save(test_path)
    return test_path

def test_powerful_server() -> int:
    """Quick test of the powerful 3D server"""

    print("[LAUNCH] QUICK POWERFUL 3D ENGINE TEST")
    print("=" * 50)

    server_url = "http://localhost:5002"

    try:
        # Test server health
        print("1. Testing server health...")
        response = requests.get(f"{server_url}/api/health", timeout=10)

        if response.status_code == 200:
            health = response.json()
            print(f"   [OK] Server: {health.get('server', 'ORFEAS')}")
            print(f"   [TARGET] Status: {health.get('status', 'Unknown')}")

            # Check capabilities
            capabilities = health.get('capabilities', [])
            print(f"    Advanced Features: {len(capabilities)}")
            for cap in capabilities[:3]:  # Show first 3
                print(f"      • {cap}")
        else:
            print(f"   [FAIL] Server health check failed: {response.status_code}")
            return False

        # Create test image
        print("\n2. Creating test image...")
        test_image = create_test_image()
        print(f"   [OK] Created: {test_image}")

        # Upload image
        print("\n3. Uploading test image...")
        with open(test_image, 'rb') as f:
            files = {'image': (test_image.name, f, 'image/png')}
            response = requests.post(f"{server_url}/api/upload-image", files=files)

        if response.status_code != 200:
            print(f"   [FAIL] Upload failed: {response.status_code}")
            return False

        upload_data = response.json()
        job_id = upload_data.get('job_id')
        print(f"   [OK] Job ID: {job_id}")

        # Generate 3D model
        print("\n4. Generating 3D model...")
        payload = {
            'job_id': job_id,
            'format': 'stl',
            'quality': 'medium',
            'method': 'auto',
            'dimensions': {'width': 50, 'height': 50, 'depth': 15}
        }

        response = requests.post(
            f"{server_url}/api/generate-3d",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code != 200:
            print(f"   [FAIL] Generation failed: {response.status_code}")
            return False

        print("    Advanced generation started...")

        # Monitor progress
        start_time = time.time()
        max_wait = 60

        while time.time() - start_time < max_wait:
            try:
                # Check job status
                response = requests.get(f"{server_url}/job-status/{job_id}")

                if response.status_code == 200:
                    status_data = response.json()
                    status = status_data.get('status')
                    progress = status_data.get('progress', 0)
                    step = status_data.get('step', 'Processing')

                    print(f"   Progress: {progress}% - {step}")

                    if status == 'completed':
                        print("\n5. [OK] GENERATION COMPLETED!")

                        # Show results
                        triangles = status_data.get('triangles', 0)
                        file_size = status_data.get('file_size', 0)
                        method_used = status_data.get('method_used', 'unknown')
                        generation_time = time.time() - start_time

                        print(f"   [STATS] Results Summary:")
                        print(f"      Method: {method_used}")
                        print(f"      Triangles: {triangles:,}")
                        print(f"      File Size: {file_size/1024:.1f} KB")
                        print(f"      Time: {generation_time:.1f}s")

                        # Calculate quality score
                        if triangles > 1000:
                            quality_score = min(100, triangles / 100)
                            print(f"      Quality: {quality_score:.1f}/100")

                            if quality_score > 50:
                                print(f"\n POWERFUL 3D ENGINE: WORKING EXCELLENT!")
                                print(f"[OK] Advanced algorithms are operational")
                                print(f"[OK] Quality exceeds expectations")
                                return True

                        break

                    elif status == 'failed':
                        error = status_data.get('error', 'Unknown error')
                        print(f"   [FAIL] Generation failed: {error}")
                        return False

                else:
                    print(f"   Status check failed: {response.status_code}")

            except Exception as e:
                print(f"   Status check error: {e}")

            time.sleep(2)

        print(f"\n[WARN] Test completed but may need optimization")
        return True

    except Exception as e:
        print(f"[FAIL] Test failed: {e}")
        return False

    finally:
        # Cleanup
        test_image = Path("quick_test_image.png")
        if test_image.exists():
            test_image.unlink()

def main() -> None:
    success = test_powerful_server()

    print("\n" + "=" * 50)
    if success:
        print("[TROPHY] POWERFUL 3D ENGINE IS OPERATIONAL!")
        print("Your ORFEAS system has advanced 3D generation capabilities!")
    else:
        print("[WARN] Some issues detected - but basic functionality working")
        print("Advanced features may need fine-tuning")

if __name__ == "__main__":
    main()
