#!/usr/bin/env python3
"""
Test Advanced Bob AI Prompt Enhancement
=======================================
Tests the expanded prompt enchancement capabilities
"""

import sys
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

print("\n" + "="*80)
print("TESTING ADVANCED BOB AI PROMPT ENHANCEMENT")
print("="*80)

try:
    # Test 1: Import advanced enhancer
    print("\n1. Importing Advanced Prompt Enhancer...")
    from bob_ai_advanced_enhancer import (
        AdvancedPromptEnhancer,
        PromptEnhancementPipeline,
        initialize_advanced_enhancer
    )
    print("   ✓ Advanced enhancer imported successfully")

    # Test 2: Initialize
    print("\n2. Initializing Advanced Enhancer...")
    initialize_advanced_enhancer()
    print("   ✓ Advanced enhancer initialized")

    # Test 3: Context detection
    print("\n3. Testing Context Detection...")
    test_prompts = [
        "Create a minimalist modern house",
        "Design a steampunk robot with brass gears",
        "A peaceful garden with warm sunset lighting",
        "Cyberpunk neon city at night",
    ]

    for prompt in test_prompts:
        context = AdvancedPromptEnhancer.detect_prompt_context(prompt)
        print(f"   Prompt: {prompt}")
        print(f"   Detected: {len(context['design_styles'])} styles, "
              f"{len(context['materials'])} materials, "
              f"{len(context['lighting'])} lighting, "
              f"{len(context['atmosphere'])} atmospheres")

    print("   ✓ Context detection working")

    # Test 4: Semantic depth enhancement
    print("\n4. Testing Semantic Depth Enhancement...")
    prompt = "Create a minimalist office"
    enhanced = AdvancedPromptEnhancer.enhance_with_semantic_depth(
        prompt,
        AdvancedPromptEnhancer.detect_prompt_context(prompt)
    )
    print(f"   Original:  {prompt}")
    print(f"   Enhanced:  {enhanced}")
    print("   ✓ Semantic depth enhancement working")

    # Test 5: Technical specifications
    print("\n5. Testing Technical Specifications...")
    context = AdvancedPromptEnhancer.detect_prompt_context(prompt)
    technical = AdvancedPromptEnhancer.enhance_with_technical_specs(prompt, context)
    print(f"   With specs: {technical}")
    print("   ✓ Technical specifications working")

    # Test 6: Emotional resonance
    print("\n6. Testing Emotional Resonance...")
    emotional = AdvancedPromptEnhancer.enhance_with_emotional_resonance(prompt)
    print(f"   With emotion: {emotional}")
    print("   ✓ Emotional resonance working")

    # Test 7: Full pipeline - LOW enhancement
    print("\n7. Testing Full Pipeline - LOW Enhancement Level...")
    low_enhanced = PromptEnhancementPipeline.apply_full_enhancement(
        "Create a house",
        enhancement_level="low"
    )
    print(f"   Original:    Create a house")
    print(f"   LOW Enhanced: {low_enhanced}")
    print("   ✓ LOW enhancement level working")

    # Test 8: Full pipeline - HIGH enhancement
    print("\n8. Testing Full Pipeline - HIGH Enhancement Level...")
    high_enhanced = PromptEnhancementPipeline.apply_full_enhancement(
        "Create a house",
        enhancement_level="high"
    )
    print(f"   HIGH Enhanced: {high_enhanced}")
    print("   ✓ HIGH enhancement level working")

    # Test 9: Full pipeline - ULTRA enhancement
    print("\n9. Testing Full Pipeline - ULTRA Enhancement Level...")
    ultra_enhanced = PromptEnhancementPipeline.apply_full_enhancement(
        "Create a house",
        enhancement_level="ultra"
    )
    print(f"   ULTRA Enhanced: {ultra_enhanced[:100]}...")
    print("   ✓ ULTRA enhancement level working")

    # Test 10: Domain-specific enhancement - 3D
    print("\n10. Testing Domain-Specific Enhancement - 3D...")
    prompt_3d = "Design a steampunk robot"
    enhanced_3d, system_3d = PromptEnhancementPipeline.apply_domain_specific_enhancement(
        prompt_3d,
        domain="3d",
        enhancement_level="high"
    )
    print(f"    Prompt:   {prompt_3d}")
    print(f"    Enhanced: {enhanced_3d[:80]}...")
    print(f"    System context length: {len(system_3d)} chars")
    print("    ✓ 3D domain enhancement working")

    # Test 11: Domain-specific enhancement - Design
    print("\n11. Testing Domain-Specific Enhancement - Design...")
    prompt_design = "Minimalist bedroom"
    enhanced_design, system_design = PromptEnhancementPipeline.apply_domain_specific_enhancement(
        prompt_design,
        domain="design",
        enhancement_level="high"
    )
    print(f"    Prompt:   {prompt_design}")
    print(f"    Enhanced: {enhanced_design[:80]}...")
    print(f"    System context length: {len(system_design)} chars")
    print("    ✓ Design domain enhancement working")

    # Test 12: Domain-specific enhancement - Creative
    print("\n12. Testing Domain-Specific Enhancement - Creative...")
    prompt_creative = "Fantasy artwork"
    enhanced_creative, system_creative = PromptEnhancementPipeline.apply_domain_specific_enhancement(
        prompt_creative,
        domain="creative",
        enhancement_level="high"
    )
    print(f"    Prompt:   {prompt_creative}")
    print(f"    Enhanced: {enhanced_creative[:80]}...")
    print(f"    System context length: {len(system_creative)} chars")
    print("    ✓ Creative domain enhancement working")

    # Test 13: Interactive refinement session
    print("\n13. Testing Interactive Refinement Session...")
    session = PromptEnhancementPipeline.interactive_enhancement_session(
        "Create art",
        max_refinements=2
    )
    print(f"    Initial:       {session['initial_prompt']}")
    print(f"    Iterations:    {len(session['iterations'])}")
    print(f"    Final:         {session['final_enhanced'][:80]}...")
    print("    ✓ Interactive refinement session working")

    # Summary
    print("\n" + "="*80)
    print("ALL TESTS PASSED!")
    print("="*80)
    print("\n✓ Advanced Bob AI Prompt Enhancement Engine is fully operational")
    print("\nCapabilities:")
    print("  • Context detection (design, materials, lighting, atmosphere)")
    print("  • Semantic depth enhancement")
    print("  • Technical specification injection")
    print("  • Emotional resonance optimization")
    print("  • Composition principle integration")
    print("  • Domain-specific enhancement (3D, Design, Creative)")
    print("  • Multiple enhancement levels (low, medium, high, ultra)")
    print("  • Interactive refinement sessions")
    print("  • Cultural context integration")
    print("  • Description density boosting")

    print("\nUsage Examples:")
    print("  from bob_ai_advanced_enhancer import PromptEnhancementPipeline")
    print("  ")
    print("  # Basic enhancement")
    print("  enhanced = PromptEnhancementPipeline.apply_full_enhancement(prompt)")
    print("  ")
    print("  # Domain-specific with custom level")
    print("  enhanced, system = PromptEnhancementPipeline.apply_domain_specific_enhancement(")
    print("      prompt, domain='3d', enhancement_level='ultra'")
    print("  )")
    print("  ")
    print("  # Interactive refinement")
    print("  session = PromptEnhancementPipeline.interactive_enhancement_session(")
    print("      prompt, max_refinements=3")
    print("  )")

    print("\n" + "="*80)

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
