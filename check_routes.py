import json
import requests
import sys

try:
    resp = requests.get('http://localhost:5000/debug/flask-blueprints', timeout=5)
    data = resp.json()

    print(f"Total routes registered: {data.get('total_rules', '?')}\n")

    # Look for enhance-prompt or similar
    print("Searching for 'enhance' in routes...")
    found_enhance = False
    for rule in data.get('llm_url_rules', []):
        if 'enhance' in rule.get('rule', '').lower():
            print(f"  Found: {rule['rule']} -> {rule['methods']}")
            found_enhance = True

    if not found_enhance:
        print("  NOT FOUND!\n")
        print("Routes containing 'api': ")
        for rule in data.get('llm_url_rules', [])[:10]:
            print(f"  {rule['rule']} -> {rule['methods']}")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
