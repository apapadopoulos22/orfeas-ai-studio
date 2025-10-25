#!/usr/bin/env python3
"""Test the fixed /api/optimize-halotbox endpoint with file upload support"""
import requests
import json

print("=" * 70)
print("[TEST] HALOTBox API File Upload - FINAL TEST")
print("=" * 70)

# Test the /api/optimize-halotbox endpoint with multipart file upload
print("\n[PHASE 1] Testing file upload to /api/optimize-halotbox...")
print("-" * 70)

try:
    with open('test_cube.stl', 'rb') as f:
        files = {'file': f}
        data = {
            'material': 'standard',
            'quality': 'standard',
            'auto_repair': 'true'
        }

        response = requests.post(
            'http://localhost:5000/api/optimize-halotbox',
            files=files,
            data=data,
            timeout=60
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ SUCCESS!")
            resp_data = response.json()
            print(f"\nResponse (excerpt):")
            print(f"  - Job ID: {resp_data.get('job_id')}")
            print(f"  - Success: {resp_data.get('success')}")
            print(f"  - Optimization Report:")
            report = resp_data.get('optimization_report', {})
            if isinstance(report, dict):
                print(f"    - Compression ratio: {report.get('compression_ratio', 'N/A')}")
                print(f"    - Fit in volume: {report.get('fit_in_build_volume', 'N/A')}")
                print(f"    - Needs supports: {report.get('needs_supports', 'N/A')}")
        else:
            print(f"❌ FAILED!")
            print(f"Response: {response.text[:500]}")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
