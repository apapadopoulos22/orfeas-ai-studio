#!/usr/bin/env python3
"""Test Flask routes"""
import sys
import json
import os

os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    print("=" * 80)
    print("Testing Flask Routes")
    print("=" * 80)

    print("\n[1] Creating server...")
    from main import OrfeasUnifiedServer, ProcessorMode
    server = OrfeasUnifiedServer(mode=ProcessorMode.FULL_AI)
    app = server.app
    print("OK - Server created\n")

    print("[2] Creating test client...")
    client = app.test_client()
    print("OK - Test client created\n")

    print("[3] Testing routes with test client...\n")

    tests = [
        ('/api/health', 'GET'),
        ('/api/disciplines/all', 'GET'),
        ('/health', 'GET'),
        ('/', 'GET'),
    ]

    for path, method in tests:
        resp = client.get(path) if method == 'GET' else client.post(path)
        print(f"{path}: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  -> SUCCESS")
        elif resp.status_code == 404:
            print(f"  -> 404 NOT FOUND")
        print()

    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
