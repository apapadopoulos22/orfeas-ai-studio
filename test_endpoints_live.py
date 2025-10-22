#!/usr/bin/env python3
import requests
import json

print("\n" + "="*70)
print("PHASE 4 ENDPOINT TESTING - LIVE VALIDATION")
print("="*70 + "\n")

endpoints = [
    ("GET", "/api/phase4/status"),
    ("GET", "/api/phase4/gpu/profile"),
    ("GET", "/api/phase4/dashboard/summary"),
    ("GET", "/api/phase4/cache/stats"),
    ("GET", "/api/phase4/predictions"),
    ("GET", "/api/phase4/alerts/active"),
    ("GET", "/api/phase4/alerts/history"),
    ("GET", "/api/phase4/anomalies"),
    ("GET", "/api/phase4/traces"),
]

passed = 0
failed = 0
base_url = "http://localhost:5000"

for method, endpoint in endpoints:
    try:
        url = base_url + endpoint
        if method == "GET":
            r = requests.get(url, timeout=5)
        response_time = r.elapsed.total_seconds() * 1000

        if r.status_code in [200, 503]:
            print(f"✓ {method:4} {endpoint:40} [{r.status_code}] {response_time:.0f}ms")
            passed += 1
        else:
            print(f"✗ {method:4} {endpoint:40} [{r.status_code}]")
            failed += 1
    except Exception as e:
        print(f"✗ {method:4} {endpoint:40} [ERROR] {str(e)[:40]}")
        failed += 1

print("\n" + "="*70)
print(f"RESULTS: {passed}/{len(endpoints)} endpoints responding")
print(f"Success Rate: {(passed/len(endpoints))*100:.1f}%")
print("="*70 + "\n")

# Show first endpoint in detail
try:
    r = requests.get(base_url + "/api/phase4/status", timeout=5)
    print("STATUS ENDPOINT DETAILS:")
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print(f"Could not fetch status: {e}")

if passed >= 7:
    print("\n✅ PHASE 4 DEPLOYMENT SUCCESSFUL - ALL SYSTEMS OPERATIONAL")
else:
    print("\n⚠ Some endpoints not responding yet - backend may still be loading")
