"""
Test script to directly check Hunyuan3D processor status
"""
import sys
sys.path.insert(0, 'c:/Users/johng/Documents/Erevus/orfeas/backend')

from hunyuan_integration import get_3d_processor

print("=" * 80)
print("DIRECT PROCESSOR TEST")
print("=" * 80)

print("\n1. Calling get_3d_processor()...")
processor = get_3d_processor("cuda")

print(f"\n2. Processor type: {type(processor).__name__}")

print("\n3. Checking is_available()...")
available = processor.is_available()
print(f"   is_available(): {available}")

print("\n4. Getting model info...")
info = processor.get_model_info()
print(f"   Model Type: {info.get('model_type', 'UNKNOWN')}")
print(f"   Status: {info.get('status', 'UNKNOWN')}")
print(f"   Capabilities: {info.get('capabilities', [])}")

print("\n5. Checking attributes...")
if hasattr(processor, 'model_loaded'):
    print(f"   model_loaded: {processor.model_loaded}")
if hasattr(processor, 'shapegen_pipeline'):
    print(f"   shapegen_pipeline: {processor.shapegen_pipeline is not None}")
if hasattr(processor, 'rembg'):
    print(f"   rembg: {processor.rembg is not None}")

print("\n" + "=" * 80)
