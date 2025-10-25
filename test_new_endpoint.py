import requests
import json

# Test file upload to NEW /api/optimize-halotbox-file endpoint
print("Testing HalotBox API file upload (NEW ENDPOINT)...")
print("=" * 60)

with open('test_cube.stl', 'rb') as f:
    files = {'file': f}
    data = {
        'material': 'standard',
        'quality': 'standard',
        'auto_repair': 'true'
    }

    response = requests.post(
        'http://localhost:5000/api/optimize-halotbox-file',
        files=files,
        data=data,
        timeout=60
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")

    if response.status_code == 200:
        print("\n✅ SUCCESS! File upload endpoint working correctly!")
        resp_data = response.json()
        if resp_data.get('success'):
            print(f"✅ Optimization successful!")
            print(f"   Job ID: {resp_data.get('job_id')}")
            report = resp_data['optimization_report']
            print(f"   Compression: {report['compression_ratio']:.2f}x")
            print(f"   Vertices: {report['original_vertices']} → {report['optimized_vertices']}")
    else:
        print(f"\n❌ FAILED! Status code {response.status_code}")

print("\n" + "=" * 60)
print("Testing OLD /api/optimize-halotbox endpoint...")
print("=" * 60)

# Test with old endpoint for comparison
with open('test_cube.stl', 'rb') as f:
    files = {'file': f}
    data = {
        'material': 'standard',
        'quality': 'standard'
    }

    response = requests.post(
        'http://localhost:5000/api/optimize-halotbox',
        files=files,
        data=data,
        timeout=30
    )

    print(f"Status Code: {response.status_code}")
    resp_json = response.json()
    if 'error' in resp_json:
        print(f"❌ ERROR: {resp_json['error']}")
    else:
        print(f"Response: {json.dumps(resp_json, indent=2)[:500]}")
