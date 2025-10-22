"""
Quick diagnostic to check what processor is loaded
"""
import requests
import json

print("=" * 80)
print("ORFEAS PROCESSOR DIAGNOSTIC")
print("=" * 80)

# Check models-info
print("\n1. Checking /api/models-info endpoint...")
try:
    response = requests.get("http://localhost:5000/api/models-info")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))

    processor_type = data.get("processor", {}).get("model_type", "UNKNOWN")
    print(f"\n  Processor Type: {processor_type}")

    if processor_type == "Fallback Processor":
        print(" PROBLEM: Using Fallback Processor (not Hunyuan3D!)")
    elif "Hunyuan" in processor_type:
        print(" GOOD: Using Hunyuan3D Processor")

except Exception as e:
    print(f" Error: {e}")

# Check ready status
print("\n2. Checking /ready endpoint...")
try:
    response = requests.get("http://localhost:5000/ready")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))

    if data.get("checks", {}).get("models"):
        print(" Models reported as ready")
    else:
        print(" Models NOT ready")

except Exception as e:
    print(f" Error: {e}")

# Check health
print("\n3. Checking /health endpoint...")
try:
    response = requests.get("http://localhost:5000/health")
    print(f"Status: {response.status_code}")
    data = response.json()
    mode = data.get("mode", "UNKNOWN")
    status = data.get("status", "UNKNOWN")
    print(f"Mode: {mode}")
    print(f"Status: {status}")

except Exception as e:
    print(f" Error: {e}")

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
