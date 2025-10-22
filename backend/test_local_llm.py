#!/usr/bin/env python3
"""
Quick test of Local LLM integration
"""
import os
import sys

# Set environment before imports
os.environ['ENABLE_LOCAL_LLMS'] = 'true'
os.environ['LOCAL_LLM_SERVER'] = 'http://localhost:11434'
os.environ['LOCAL_LLM_MODEL'] = 'mistral'
os.environ['LOCAL_LLM_TEMPERATURE'] = '0.3'

print("Testing Local LLM Integration...")
print(f"  ENABLE_LOCAL_LLMS: {os.getenv('ENABLE_LOCAL_LLMS')}")
print(f"  LOCAL_LLM_SERVER: {os.getenv('LOCAL_LLM_SERVER')}")
print(f"  LOCAL_LLM_MODEL: {os.getenv('LOCAL_LLM_MODEL')}")

# Import after setting env
from local_llm_router import local_llm

print("\n1. Checking availability...")
available = local_llm.is_available()
print(f"   Local LLM available: {available}")

if available:
    print("\n2. Testing generation...")
    result = local_llm.generate("What is 2+2?", max_tokens=50)

    if 'error' in result:
        print(f"   ERROR: {result['error']}")
        sys.exit(1)
    else:
        print(f"   Response: {result['response']}")
        print(f"   Model: {result['model']}")
        print(f"   Source: {result['source']}")
        print(f"   Latency: {result['latency_ms']}ms")
        print("\n✅ Local LLM integration working!")
else:
    print("\n❌ Local LLM not available")
    sys.exit(1)
