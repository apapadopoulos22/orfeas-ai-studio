#!/usr/bin/env python3
"""Test both STL files against the backend endpoint."""
import requests
import time
from pathlib import Path

def test_stl_upload(file_path, label):
    """Test uploading a specific STL file."""
    print(f"\n{'='*70}")
    print(f"Testing: {label}")
    print(f"File: {file_path}")
    print('='*70)

    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return False

    url = 'http://localhost:5000/api/optimize-halotbox'

    try:
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, 'application/octet-stream')}
            data = {
                'material': 'standard',
                'quality': 'standard',
                'auto_repair': 'true'
            }

            print(f"📤 Uploading {Path(file_path).stat().st_size / (1024*1024):.2f} MB...")
            start_time = time.time()

            response = requests.post(url, files=files, data=data, timeout=300)
            elapsed = time.time() - start_time

            print(f"⏱️  Response time: {elapsed:.2f}s")
            print(f"📊 Status code: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS")
                print(f"   Job ID: {result.get('job_id', 'N/A')}")
                print(f"   Status: {result.get('status', 'N/A')}")
                if 'report' in result:
                    report = result['report']
                    print(f"   Vertices: {report.get('mesh_stats', {}).get('vertices', 'N/A')}")
                    print(f"   Faces: {report.get('mesh_stats', {}).get('faces', 'N/A')}")
                    print(f"   Supports needed: {report.get('support_analysis', {}).get('needs_supports', 'N/A')}")
                return True
            else:
                print(f"❌ FAILED")
                print(f"   Response: {response.text[:500]}")
                return False

    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False

if __name__ == '__main__':
    print("\n🚀 Testing STL File Upload to Backend")
    print("="*70)

    # Test working file
    working_path = r"C:\Users\johng\Downloads\model_4.STL"
    working_result = test_stl_upload(working_path, "WORKING EXAMPLE")

    # Test "broken" file
    broken_path = r"C:\Users\johng\Downloads\houndeye_no tail.stl"
    broken_result = test_stl_upload(broken_path, "NON-WORKING EXAMPLE")

    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"Working file (model_4.STL): {'✅ PASSED' if working_result else '❌ FAILED'}")
    print(f"Broken file (houndeye_no tail.stl): {'✅ PASSED' if broken_result else '❌ FAILED'}")
    print("="*70)
