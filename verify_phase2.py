#!/usr/bin/env python
"""Quick Phase 2 Verification"""
from backend.bob_ai_expansion_tier1_creative_arts import get_knowledge_base as get_tier1
from backend.bob_ai_expansion_tier12_environment_sustainability_expanded import get_knowledge_base as get_tier12

print("PHASE 2 VERIFICATION")
print("="*50)

tier1 = get_tier1()
print(f"Tier 1: {tier1['total_items']} disciplines")

tier12 = get_tier12()
print(f"Tier 12: {tier12['total_items']} disciplines")

print()
print("SUCCESS: Phase 2 wrapper modules are functional!")
print("Ready for Phase 3: Dynamic Discovery & Integration")
