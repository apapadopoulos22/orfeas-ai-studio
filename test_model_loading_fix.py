#!/usr/bin/env python
"""
Test the model loading fix - verify cache detection works correctly
"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))
sys.path.insert(0, str(Path(__file__).parent / 'Hunyuan3D-2.1' / 'Hunyuan3D-2'))

# Load environment first
from dotenv import load_dotenv
load_dotenv()

print("=" * 80)
print("TEST: Model Loading Cache Detection")
print("=" * 80)

# Check environment
hy3dgen_models = os.environ.get('HY3DGEN_MODELS')
print(f"\n1. HY3DGEN_MODELS environment variable: {hy3dgen_models}")

# Test the smart_load_model function with cache detection
print("\n2. Testing smart_load_model() function...")
print("-" * 80)

try:
    from hy3dgen.shapegen.utils import smart_load_model

    # Test parameters
    model_path = 'tencent/Hunyuan3D-2'
    subfolder = 'hunyuan3d-dit-v2-0'

    print(f"   Input model_path: {model_path}")
    print(f"   Input subfolder: {subfolder}")
    print()

    # Try to load - this should check cache first
    try:
        result = smart_load_model(
            model_path=model_path,
            subfolder=subfolder,
            use_safetensors=True,
            variant=None
        )
        print(f"   ✅ SUCCESS! Model loaded from: {result}")

    except RuntimeError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            # Expected if model not in cache yet (will download)
            print(f"   ⚠️  Model not in cache (will download): {error_msg}")
        else:
            print(f"   ❌ ERROR: {error_msg}")

    except Exception as e:
        print(f"   ❌ Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"❌ Failed to import smart_load_model: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("3. Checking HuggingFace cache structure manually...")
print("-" * 80)

if hy3dgen_models and 'hub' in hy3dgen_models:
    # Convert repo_id to cache format
    model_path = 'tencent/Hunyuan3D-2'
    model_repo_cache_name = f'models--{model_path.replace("/", "--")}'

    repo_cache_dir = os.path.join(hy3dgen_models, model_repo_cache_name, 'snapshots')
    print(f"   Cache directory: {repo_cache_dir}")
    print(f"   Exists: {os.path.exists(repo_cache_dir)}")

    if os.path.exists(repo_cache_dir):
        snapshots = os.listdir(repo_cache_dir)
        print(f"   Snapshots found: {len(snapshots)}")
        if snapshots:
            snapshot_dir = os.path.join(repo_cache_dir, snapshots[0])
            print(f"   First snapshot: {snapshots[0]}")

            model_dir = os.path.join(snapshot_dir, 'hunyuan3d-dit-v2-0')
            print(f"   Model directory: {model_dir}")
            print(f"   Exists: {os.path.exists(model_dir)}")

            if os.path.exists(model_dir):
                files = os.listdir(model_dir)
                print(f"   Files in model directory: {files[:5]}...")  # First 5 files
                print(f"   ✅ Cache structure verified!")
            else:
                print(f"   ❌ Model directory not found in snapshot")
    else:
        print(f"   ⚠️  Cache directory not found - model not yet downloaded")
else:
    print(f"   ⚠️  HY3DGEN_MODELS not pointing to hub directory")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
