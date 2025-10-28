#!/usr/bin/env python3
import requests
import json

# Test locally
try:
    resp = requests.get('http://localhost:5000/api/disciplines/all?limit=2', timeout=5)
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Response status: {data.get('status')}")
        print(f"Total disciplines: {data.get('data', {}).get('total')}")
        print(f"Returned: {len(data.get('data', {}).get('disciplines', []))}")
    else:
        print(f"Response: {resp.text}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
