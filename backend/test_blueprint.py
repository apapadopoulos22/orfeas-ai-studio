#!/usr/bin/env python3
from flask import Flask
from bob_ai_api_endpoints import bob_ai_blueprint, BOB_AI_MEGA_AVAILABLE

print(f"BOB_AI_MEGA_AVAILABLE: {BOB_AI_MEGA_AVAILABLE}")

app = Flask(__name__)
app.register_blueprint(bob_ai_blueprint)

# List routes
print(f"\nRoutes registered:")
for rule in app.url_map.iter_rules():
    if 'discipline' in str(rule).lower():
        print(f"  {rule}")

# Test locally - CORRECT URL
with app.test_client() as client:
    resp = client.get('/api/disciplines/all?limit=2')
    print(f"\nTest request to /api/disciplines/all:")
    print(f"  Status: {resp.status_code}")
    print(f"  Content-Type: {resp.content_type}")
    data = resp.get_json()
    if data:
        print(f"  Success: {data.get('status')}")
        print(f"  Total: {data.get('data', {}).get('total')}")
    else:
        print(f"  Response: {resp.data}")
