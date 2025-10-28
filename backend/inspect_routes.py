#!/usr/bin/env python3
"""
Inspect all registered routes on the running Flask app
"""
import requests
import json

# Get the Flask app internally and print all routes
print("\n" + "="*80)
print("INSPECTING RUNNING FLASK SERVER ROUTES")
print("="*80)

# Try a Python HTTP GET to check if route is registered
routes_to_test = [
    '/health',
    '/api/health',
    '/api/disciplines/all',
    '/api/disciplines/Machine%20Learning/libraries',
    '/api/disciplines/health',
    '/',
    '/test-file.html',
]

print("\nTesting individual routes (to see which match and which don't):\n")

for route in routes_to_test:
    try:
        url = f'http://localhost:5000{route}'
        response = requests.get(url, timeout=2)
        print(f"✓ {route:50} → {response.status_code} {response.reason}")
        if response.status_code == 404:
            try:
                data = response.json()
                print(f"   Response: {data}")
            except:
                print(f"   Response: {response.text[:100]}")
    except Exception as e:
        print(f"✗ {route:50} → ERROR: {str(e)[:50]}")

print("\n" + "="*80)
print("Now let's try importing the Flask app directly and inspecting routes")
print("="*80 + "\n")

try:
    import sys
    sys.path.insert(0, 'c:\\Users\\johng\\Documents\\oscar\\backend')

    # Import the app
    from main import app

    print(f"Found Flask app: {app}")
    print(f"Total URL rules: {len(app.url_map._rules)}\n")

    print("All registered routes:")
    print("-" * 100)
    print(f"{'Rule':60} | {'Endpoint':35} | {'Methods':20}")
    print("-" * 100)

    for rule in app.url_map.iter_rules():
        if 'static' not in rule.endpoint and 'static' not in str(rule):
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            print(f"{str(rule):60} | {rule.endpoint:35} | {methods:20}")

    print("\nNow filter for /api routes:")
    print("-" * 100)
    for rule in app.url_map.iter_rules():
        if '/api' in str(rule):
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            print(f"{str(rule):60} | {rule.endpoint:35} | {methods:20}")

    print("\nNow filter for /disciplines routes:")
    print("-" * 100)
    for rule in app.url_map.iter_rules():
        if 'disciplines' in str(rule):
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            print(f"{str(rule):60} | {rule.endpoint:35} | {methods:20}")

except Exception as e:
    print(f"ERROR importing Flask app: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("DONE")
print("="*80 + "\n")
