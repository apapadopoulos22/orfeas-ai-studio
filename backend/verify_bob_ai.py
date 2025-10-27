#!/usr/bin/env python3
"""
Simple verification that Bob AI Knowledge Base is integrated
"""

print("VERIFICATION TEST - Bob AI Knowledge Base Integration")
print("=" * 60)

try:
    print("\n1. Importing Bob AI Knowledge Base...")
    from bob_ai_knowledge_base import BobAIKnowledgeBase, initialize_bob_ai_knowledge
    print("   [OK] BobAIKnowledgeBase imported")

    print("\n2. Initializing knowledge base...")
    initialize_bob_ai_knowledge()
    print("   [OK] Knowledge base initialized")

    print("\n3. Accessing semantic dictionaries...")
    dicts = BobAIKnowledgeBase.get_all_dictionaries()
    print(f"   [OK] Retrieved {len(dicts)} dictionaries")

    print("\n4. Testing prompt enhancement...")
    enhanced = BobAIKnowledgeBase.enhance_prompt("Create a house")
    print(f"   [OK] Enhanced prompt created ({len(enhanced)} chars)")

    print("\n5. Importing LLM integration...")
    from llm_local_integration import (
        enhance_prompt_with_bob_ai,
        get_bob_ai_system_prompt,
        generate_with_llm,
        BOB_AI_KB_AVAILABLE
    )
    print(f"   [OK] LLM module imported")
    print(f"   [OK] Bob AI KB available: {BOB_AI_KB_AVAILABLE}")

    print("\n6. Testing LLM enhancement function...")
    enhanced = enhance_prompt_with_bob_ai("Test prompt")
    print(f"   [OK] LLM enhancement working ({len(enhanced)} chars)")

    print("\n7. Getting system prompt...")
    system = get_bob_ai_system_prompt()
    print(f"   [OK] System prompt generated ({len(system)} chars)")

    print("\n" + "=" * 60)
    print("RESULT: All tests passed!")
    print("=" * 60)
    print("\nBob AI Knowledge Base is fully integrated and operational.")
    print("Features available:")
    print("  - enhance_prompt_with_bob_ai(prompt)")
    print("  - get_bob_ai_system_prompt()")
    print("  - generate_with_llm(prompt, use_semantic_enhancement=True)")
    print("  - BobAIKnowledgeBase.DESIGN_STYLES, .MATERIAL_PROPERTIES, etc.")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    exit(1)
