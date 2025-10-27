#!/usr/bin/env python
"""Test Phase 2 wrapper modules"""

import sys

print("=" * 70)
print("BOB AI v10.0 - PHASE 2 WRAPPER MODULES TEST")
print("=" * 70)
print()

# Test all 12 tiers
tier_modules = [
    ("backend.bob_ai_expansion_tier1_creative_arts", "Tier 1: Creative Arts"),
    ("backend.bob_ai_expansion_tier2_philosophy_theory", "Tier 2: Philosophy"),
    ("backend.bob_ai_expansion_tier3_ethics_ai_expansion", "Tier 3: Ethics & AI"),
    ("backend.bob_ai_expansion_tier4_business_economics_expanded", "Tier 4: Business"),
    ("backend.bob_ai_expansion_tier5_science_research_expanded", "Tier 5: Science"),
    ("backend.bob_ai_expansion_tier6_healthcare_medicine_expanded", "Tier 6: Healthcare"),
    ("backend.bob_ai_expansion_tier7_law_governance_expanded", "Tier 7: Law"),
    ("backend.bob_ai_expansion_tier8_arts_humanities_expanded", "Tier 8: Humanities"),
    ("backend.bob_ai_expansion_tier9_technology_engineering_expanded", "Tier 9: Technology"),
    ("backend.bob_ai_expansion_tier10_education_learning_expanded", "Tier 10: Education"),
    ("backend.bob_ai_expansion_tier11_social_behavioral_expanded", "Tier 11: Social"),
    ("backend.bob_ai_expansion_tier12_environment_sustainability_expanded", "Tier 12: Sustainability"),
]

total_disciplines = 0
total_knowledge_items = 0
successful = 0
failed = 0

for module_path, tier_name in tier_modules:
    try:
        # Import module
        module = __import__(module_path, fromlist=['get_knowledge_base'])
        get_kb = getattr(module, 'get_knowledge_base')

        # Get knowledge base
        kb = get_kb()

        # Extract stats
        disciplines = kb.get('total_items', 0)
        knowledge_items = kb.get('total_knowledge_count', 0)

        total_disciplines += disciplines
        total_knowledge_items += knowledge_items
        successful += 1

        print(f"✅ {tier_name:40} | Disciplines: {disciplines:3d} | Items: {knowledge_items:5d}")

    except Exception as e:
        failed += 1
        print(f"❌ {tier_name:40} | ERROR: {str(e)[:50]}")

print()
print("=" * 70)
print(f"PHASE 2 TEST RESULTS")
print("=" * 70)
print(f"Successful: {successful}/12")
print(f"Failed: {failed}/12")
print(f"Total Disciplines: {total_disciplines}")
print(f"Total Knowledge Items: {total_knowledge_items}")
print()

if successful == 12 and failed == 0:
    print("✅ PHASE 2 COMPLETE: All 12 wrapper modules working!")
    sys.exit(0)
else:
    print(f"⚠️ PHASE 2 INCOMPLETE: {failed} module(s) failed to load")
    sys.exit(1)
