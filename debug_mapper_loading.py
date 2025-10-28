#!/usr/bin/env python3
"""Debug script to check mapper loading status"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

print("=" * 70)
print("MAPPER LOADING DIAGNOSTIC")
print("=" * 70)

# Import the mapper class to check TIER_MODULES config
from bob_ai_discipline_mapper import DisciplineModuleMapper

print("\nTier Modules Configuration:")
for tier, modules in DisciplineModuleMapper.TIER_MODULES.items():
    print(f"  Tier {tier}: {len(modules)} module(s)")
    for mod in modules:
        print(f"    - {mod}")

print("\n" + "=" * 70)
print("ATTEMPTING TO LOAD MAPPER")
print("=" * 70)

from bob_ai_discipline_mapper import get_discipline_mapper

mapper = get_discipline_mapper()

print(f"\nMapper loaded successfully!")
print(f"Total modules loaded: {len(mapper.modules)}")
print(f"Total knowledge bases: {len(mapper.knowledge_bases)}")
print(f"Total items: {sum(len(kb.get('items', [])) for kb in mapper.knowledge_bases.values())}")

print("\nModules loaded:")
for module_name, module in mapper.modules.items():
    print(f"  ✓ {module_name}")

print("\nDisciplines in knowledge bases:")
disciplines = list(mapper.knowledge_bases.keys())
print(f"Total: {len(disciplines)}")
for i, disc in enumerate(sorted(disciplines)):
    items_count = len(mapper.knowledge_bases[disc].get('items', []))
    print(f"  {i+1:3d}. {disc:50s} ({items_count:3d} items)")

print("\n" + "=" * 70)
print("TESTING MAPPER METHODS")
print("=" * 70)

try:
    rels = mapper.build_semantic_relationships()
    print(f"\n✓ Semantic relationships built: {len(rels)} disciplines")
except Exception as e:
    print(f"\n✗ Error building relationships: {e}")
    import traceback
    traceback.print_exc()

try:
    stats = mapper.get_phase3_statistics()
    print(f"\n✓ Phase 3 statistics retrieved:")
    print(f"   Total disciplines: {stats.get('total_disciplines')}")
    print(f"   Total items: {stats.get('total_knowledge_items')}")
    print(f"   Semantic relationships: {stats.get('semantic_relationships')}")
except Exception as e:
    print(f"\n✗ Error getting statistics: {e}")
    import traceback
    traceback.print_exc()
