#!/usr/bin/env python3
"""Test live endpoint with Python requests library"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

print("=" * 70)
print("TESTING BOB AI ENDPOINTS WITH PYTHON REQUESTS")
print("=" * 70)

# Wait for server
time.sleep(2)

# Test 1: Health check
print("\n1. Testing /health endpoint:")
try:
    resp = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"   Status: {resp.status_code}")
    print(f"   Response: {resp.json()}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 2: API health
print("\n2. Testing /api/health endpoint:")
try:
    resp = requests.get(f"{BASE_URL}/api/health", timeout=5)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   Response: status={data.get('status')}, message={data.get('message', 'N/A')[:50]}")
    else:
        print(f"   Response: {resp.text[:100]}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 3: BOB AI disciplines endpoint
print("\n3. Testing /api/disciplines/all endpoint:")
try:
    resp = requests.get(f"{BASE_URL}/api/disciplines/all?limit=2", timeout=5)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   Response status: {data.get('status')}")
        print(f"   Total disciplines: {data.get('data', {}).get('total')}")
        print(f"   Returned: {len(data.get('data', {}).get('disciplines', []))}")
        print(f"   First discipline: {data.get('data', {}).get('disciplines', [{}])[0].get('name', 'N/A')}")
    else:
        print(f"   Response: {resp.text[:100]}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 4: Get libraries for Machine Learning
print("\n4. Testing /api/disciplines/Machine%20Learning/libraries endpoint:")
try:
    resp = requests.get(f"{BASE_URL}/api/disciplines/Machine%20Learning/libraries", timeout=5)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   Response status: {data.get('status')}")
        print(f"   Discipline: {data.get('data', {}).get('discipline')}")
        libs = data.get('data', {}).get('libraries', {})
        print(f"   Packages: {len(libs.get('packages', []))}")
        print(f"   Tools: {len(libs.get('tools', []))}")
        print(f"   Resources: {len(libs.get('resources', []))}")
    else:
        print(f"   Response: {resp.text[:100]}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
