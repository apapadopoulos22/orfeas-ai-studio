#!/usr/bin/env python3
"""
Minimal test to understand Flask blueprint url_prefix behavior
"""
from flask import Flask, Blueprint, jsonify

app = Flask(__name__)

# Create blueprint without url_prefix
test_bp = Blueprint("test", __name__)

@test_bp.route("/hello")
def hello():
    return jsonify({"message": "Hello from blueprint!"})

# Register with url_prefix
print("Before registration:")
print(f"  test_bp.url_prefix = {test_bp.url_prefix}")

app.register_blueprint(test_bp, url_prefix="/api/test")

print("\nAfter registration:")
print(f"  test_bp.url_prefix = {test_bp.url_prefix}")
print(f"  Blueprints in app: {list(app.blueprints.keys())}")
print(f"  Blueprint from registry url_prefix: {app.blueprints['test'].url_prefix}")

print("\nURL rules:")
for rule in app.url_map.iter_rules():
    if 'test' in str(rule).lower():
        print(f"  {rule} -> {rule.endpoint} (methods: {rule.methods})")

print("\n✓ If url_prefix is None but route shows /api/test/hello, Flask is working correctly")
print("✗ If route shows just /hello, there's a Flask bug or version issue")
