import json
import requests
import sys

try:
    # Get all Flask URL rules
    resp = requests.get('http://localhost:5000/debug/flask-blueprints', timeout=5)
    data = resp.json()

    print(f"Total routes: {data.get('total_rules', '?')}\n")

    # We need to get the actual rules
    # The debug endpoint doesn't give us all rules, so let's try OPTIONS
    print("Trying OPTIONS request to /api/enhance-prompt...")
    try:
        resp2 = requests.options('http://localhost:5000/api/enhance-prompt', timeout=2)
        print(f"OPTIONS response: {resp2.status_code}")
        print(f"Allowed methods: {resp2.headers.get('Allow', 'Not specified')}")
    except Exception as e:
        print(f"OPTIONS failed: {e}")

    print("\nTrying GET to /api/enhance-prompt...")
    try:
        resp3 = requests.get('http://localhost:5000/api/enhance-prompt', timeout=2)
        print(f"GET response: {resp3.status_code}")
    except Exception as e:
        print(f"GET failed: {e}")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
