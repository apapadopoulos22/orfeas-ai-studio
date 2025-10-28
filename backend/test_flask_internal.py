#!/usr/bin/env python3
"""
Test Flask routes using internal test client
This bypasses network layer to test Flask directly
"""
import sys
import json

# Start Flask app
from main import OrfeasUnifiedServer, ProcessorMode

print("=" * 80)
print("Testing Flask Routes with Internal Test Client")
print("=" * 80 + "\n")

try:
    print("[1/4] Creating OrfeasUnifiedServer...")
    server = OrfeasUnifiedServer(mode=ProcessorMode.FULL_AI)
    app = server.app
    print("✓ Server created\n")

    print("[2/4] Creating Flask test client...")
    client = app.test_client()
    print("✓ Test client created\n")

    print("[3/4] Testing endpoints...\n")

    routes_to_test = [
        ('GET', '/api/health'),
        ('GET', '/api/disciplines/all?limit=2'),
        ('GET', '/api/disciplines/Machine%20Learning/libraries'),
        ('GET', '/health'),
        ('GET', '/'),
    ]

    for method, path in routes_to_test:
        print(f"Testing {method} {path}...")
        try:
            if method == 'GET':
                response = client.get(path)
            elif method == 'POST':
                response = client.post(path)

            print(f"  Status: {response.status_code}")
            if response.status_code != 404:
                try:
                    data = json.loads(response.data)
                    # Show first part of response
                    resp_str = json.dumps(data, indent=2)[:150]
                    print(f"  Response: {resp_str}...")
                except:
                    print(f"  Response: {response.data[:100]}")
            else:
                print(f"  Response: {response.data}")
            print()
        except Exception as e:
            print(f"  ERROR: {e}\n")

    print("[4/4] Testing with live server...\n")
    import requests

    print("Note: Make sure backend is running on port 5000\n")

    for method, path in routes_to_test:
        print(f"Testing LIVE {method} {path}...")
        try:
            url = f'http://localhost:5000{path}'
            if method == 'GET':
                response = requests.get(url, timeout=2)

            print(f"  Status: {response.status_code}")
            if response.status_code < 400:
                try:
                    data = response.json()
                    resp_str = json.dumps(data, indent=2)[:150]
                    print(f"  Response: {resp_str}...")
                except:
                    print(f"  Response: {response.text[:100]}")
            else:
                print(f"  Response: {response.text}")
            print()
        except Exception as e:
            print(f"  ERROR: {e}\n")

except Exception as e:
    print(f"\n❌ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
