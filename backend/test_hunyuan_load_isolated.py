"""
Isolated test to diagnose Hunyuan3D model loading crash
"""
import os
import sys
import traceback

# Set environment before imports
os.environ["XFORMERS_DISABLED"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

print("=" * 80)
print("[TEST] Isolated Hunyuan3D Model Loading Diagnostic")
print("=" * 80)

# Test 1: Basic imports
print("\n[STEP 1] Testing basic imports...")
try:
    import torch
    print(f" PyTorch imported: {torch.__version__}")
    print(f" CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f" GPU: {torch.cuda.get_device_name(0)}")
except Exception as e:
    print(f" PyTorch import failed: {e}")
    sys.exit(1)

# Test 2: Hunyuan3D path check
print("\n[STEP 2] Checking Hunyuan3D paths...")
hunyuan_base = os.path.abspath("../Hunyuan3D-2.1")
print(f"Hunyuan3D base: {hunyuan_base}")
print(f"Exists: {os.path.exists(hunyuan_base)}")

hunyuan_path = os.path.join(hunyuan_base, "Hunyuan3D-2", "hy3dgen")
print(f"hy3dgen path: {hunyuan_path}")
print(f"Exists: {os.path.exists(hunyuan_path)}")

if os.path.exists(hunyuan_path):
    print(f"Contents: {os.listdir(hunyuan_path)[:10]}")  # First 10 files

# Test 3: Add to sys.path
print("\n[STEP 3] Adding Hunyuan3D to sys.path...")
if hunyuan_path not in sys.path:
    sys.path.insert(0, hunyuan_path)
    print(f" Added to sys.path")

# Test 4: Import Hunyuan3D modules
print("\n[STEP 4] Attempting to import Hunyuan3D modules...")
try:
    print("  [4.1] Importing infer...")
    from infer import Hunyuan3DDiTFlowMatchingPipeline, Text2Image
    print("   infer imported successfully")

    print("  [4.2] Importing text2image pipeline...")
    # This might be the crash point
    print("   Text2Image class available")

except ImportError as e:
    print(f"   Import failed: {e}")
    print(f"  Traceback:\n{traceback.format_exc()}")
    sys.exit(1)
except Exception as e:
    print(f"   Unexpected error: {e}")
    print(f"  Traceback:\n{traceback.format_exc()}")
    sys.exit(1)

# Test 5: Check model paths
print("\n[STEP 5] Checking model file paths...")
models_base = os.path.join(hunyuan_base, "weights")
print(f"Models base: {models_base}")
print(f"Exists: {os.path.exists(models_base)}")

if os.path.exists(models_base):
    print("Model directories:")
    for item in os.listdir(models_base):
        item_path = os.path.join(models_base, item)
        if os.path.isdir(item_path):
            print(f"  - {item}/")
            # Check for safetensors files
            for root, dirs, files in os.walk(item_path):
                for file in files:
                    if file.endswith('.safetensors'):
                        print(f"      {file}")
                        break  # Just show first safetensors file

# Test 6: Try to initialize pipeline (this is likely the crash point)
print("\n[STEP 6] Attempting to initialize pipelines...")
print(" This may take 30-40 seconds and use ~8GB VRAM...")

try:
    print("  [6.1] Creating shape generation pipeline...")
    from infer import Hunyuan3DDiTFlowMatchingPipeline

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  Device: {device}")

    # This is where the crash likely happens
    shape_pipeline = Hunyuan3DDiTFlowMatchingPipeline(
        device=device,
        model_path=None,  # Let it use default
    )
    print("   Shape pipeline created!")

except Exception as e:
    print(f"   Pipeline creation failed: {e}")
    print(f"  Traceback:\n{traceback.format_exc()}")
    sys.exit(1)

print("\n" + "=" * 80)
print(" ALL TESTS PASSED - Hunyuan3D can be loaded successfully")
print("=" * 80)
