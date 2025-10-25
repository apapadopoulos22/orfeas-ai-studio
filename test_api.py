import requests
import json

# Test the API endpoint
print("Testing HalotBox API endpoint...")
with open('test_cube.stl', 'rb') as f:
    files = {'file': f}
    data = {'material': 'standard', 'quality': 'standard'}
    try:
        response = requests.post('http://localhost:5000/api/optimize-halotbox', files=files, data=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"\nResponse Body (first 3000 chars):")
        print(response.text[:3000])

        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS - Response JSON:")
            print(json.dumps(result, indent=2)[:2000])
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print("Full response:")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
