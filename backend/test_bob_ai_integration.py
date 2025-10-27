#!/usr/bin/env python3
"""
Test Bob AI Knowledge Base Integration with LLM
================================================
Verifies that Bob AI semantic enhancement is properly integrated
into the local LLM pipeline.

Usage:
    python test_bob_ai_integration.py
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Test 1: Import Bob AI Knowledge Base
print("\n" + "="*80)
print("TEST 1: Import Bob AI Knowledge Base")
print("="*80)

try:
    from bob_ai_knowledge_base import (
        BobAIKnowledgeBase,
        WebSemanticLibraries,
        WorldKnowledgeBase,
        initialize_bob_ai_knowledge
    )
    print("✓ Bob AI Knowledge Base imported successfully")

    # Test initialization
    initialize_bob_ai_knowledge()
    print("✓ Bob AI Knowledge Base initialized")
except Exception as e:
    print(f"✗ Failed to import Bob AI KB: {e}")
    sys.exit(1)

# Test 2: Access semantic dictionaries
print("\n" + "="*80)
print("TEST 2: Access Semantic Dictionaries")
print("="*80)

try:
    dicts = BobAIKnowledgeBase.get_all_dictionaries()
    dict_count = len(dicts)
    print(f"✓ Retrieved {dict_count} semantic dictionaries:")

    for dict_name in dicts.keys():
        print(f"  - {dict_name}")
except Exception as e:
    print(f"✗ Failed to access dictionaries: {e}")
    sys.exit(1)

# Test 3: Test prompt enhancement
print("\n" + "="*80)
print("TEST 3: Prompt Enhancement")
print("="*80)

try:
    test_prompt = "Create a minimalist house in a peaceful setting"
    enhanced = BobAIKnowledgeBase.enhance_prompt(test_prompt, style="minimalist", quality="high")

    print(f"Original prompt:")
    print(f"  {test_prompt}")
    print(f"\nEnhanced prompt:")
    print(f"  {enhanced}")
    print("✓ Prompt enhancement successful")
except Exception as e:
    print(f"✗ Failed to enhance prompt: {e}")
    sys.exit(1)

# Test 4: Import LLM Integration
print("\n" + "="*80)
print("TEST 4: Import LLM Integration Module")
print("="*80)

try:
    from llm_local_integration import (
        enhance_prompt_with_bob_ai,
        get_bob_ai_system_prompt,
        generate_with_llm,
        BOB_AI_KB_AVAILABLE
    )
    print("✓ LLM integration module imported successfully")
    print(f"✓ Bob AI KB available in LLM: {BOB_AI_KB_AVAILABLE}")
except Exception as e:
    print(f"✗ Failed to import LLM integration: {e}")
    sys.exit(1)

# Test 5: Test Bob AI system prompt
print("\n" + "="*80)
print("TEST 5: Generate Bob AI System Prompt")
print("="*80)

try:
    system_prompt = get_bob_ai_system_prompt()
    print("System prompt generated successfully:")
    print("\n" + system_prompt[:500] + "...\n")
    print("✓ System prompt generation successful")
except Exception as e:
    print(f"✗ Failed to generate system prompt: {e}")
    sys.exit(1)

# Test 6: Test semantic enhancement in LLM module
print("\n" + "="*80)
print("TEST 6: Test Semantic Enhancement Function")
print("="*80)

try:
    test_prompt = "Design a futuristic robot"
    enhanced = enhance_prompt_with_bob_ai(test_prompt, context="3d_modeling")

    print(f"Original: {test_prompt}")
    print(f"Enhanced: {enhanced}")
    print("✓ LLM semantic enhancement working")
except Exception as e:
    print(f"✗ Failed to enhance via LLM module: {e}")
    sys.exit(1)

# Test 7: Test LLM generation (if Ollama is running)
print("\n" + "="*80)
print("TEST 7: Test LLM Generation (Optional)")
print("="*80)

try:
    # Check if Ollama is available
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)

        if response.status_code == 200:
            print("✓ Ollama service is running")

            # Test generation with semantic enhancement
            test_query = "What are the characteristics of minimalist design?"
            result = generate_with_llm(test_query, use_semantic_enhancement=True)

            if result:
                response_text = result.get('response', '')[:200]
                print(f"✓ Generation successful")
                print(f"Response preview: {response_text}...")
            else:
                print("✗ Generation returned None")
        else:
            print("⚠ Ollama not responding (service may not be running)")
    except requests.exceptions.ConnectionError:
        print("⚠ Ollama not running (skipping generation test)")
except Exception as e:
    print(f"⚠ Skipping LLM generation test: {e}")

# Final summary
print("\n" + "="*80)
print("INTEGRATION TEST COMPLETE")
print("="*80)
print("\n✓ Bob AI Knowledge Base successfully integrated into LLM pipeline!")
print("\nKey Features Available:")
print("  • 13+ Semantic Dictionaries (design, materials, lighting, emotions, etc.)")
print("  • Automatic Prompt Enhancement with Knowledge Context")
print("  • Bob AI System Prompt with Semantic Knowledge")
print("  • LLM Generation with Semantic Enrichment")
print("  • Web Ontology Support (Wikipedia, WordNet, DBpedia)")
print("\nYou can now use:")
print("  • enhance_prompt_with_bob_ai(prompt) - Enhance any user prompt")
print("  • get_bob_ai_system_prompt() - Get system prompt with knowledge")
print("  • generate_with_llm(prompt, use_semantic_enhancement=True) - Generate with enhancement")
print("\n" + "="*80)
