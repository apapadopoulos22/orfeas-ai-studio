#!/usr/bin/env python3
"""Simple Phase 3 validation test with ASCII output"""

import sys
sys.path.insert(0, 'backend')

from bob_ai_discipline_mapper import get_discipline_mapper

print("PHASE 3 VALIDATION TEST")
print("="*70)

mapper = get_discipline_mapper()

# Test 1: Get stats
print("\n[1] Getting system statistics...")
stats = mapper.get_phase3_statistics()
print(f"    Disciplines: {stats['total_disciplines']}")
print(f"    Knowledge items: {stats['total_knowledge_items']}")
print(f"    Relationships: {stats['semantic_relationships']}")

# Test 2: Build relationships
print("\n[2] Building semantic relationships...")
rels = mapper.build_semantic_relationships()
print(f"    Relationships built: {len(rels)} disciplines")
total_rels = sum(len(v) for v in rels.values())
print(f"    Total connections: {total_rels}")

# Test 3: Get graph
print("\n[3] Building knowledge graph...")
graph = mapper.get_knowledge_graph()
print(f"    Nodes: {len(graph['nodes'])}")
print(f"    Edges: {len(graph['edges'])}")

# Test 4: Pathfinding
print("\n[4] Testing pathfinding...")
path = mapper.find_discipline_path('Physics', 'Physics')
print(f"    Path (Physics->Physics): {path}")

# Test 5: Related disciplines
print("\n[5] Testing related disciplines...")
related = mapper.get_related_disciplines('Physics')
print(f"    Related to Physics: {len(related) if related else 0}")

# Test 6: Cross-tier links
print("\n[6] Testing cross-tier links...")
links = mapper.get_cross_tier_links('Physics')
print(f"    Cross-tier links: {len(links)}")

print("\n" + "="*70)
print("VALIDATION RESULTS:")
print("="*70)

passed = 0
failed = 0

# Validation checks
if stats['total_disciplines'] >= 391:
    print("[OK] Discipline count: PASS")
    passed += 1
else:
    print("[FAIL] Discipline count: FAIL")
    failed += 1

if stats['total_knowledge_items'] >= 51000:
    print("[OK] Knowledge items: PASS")
    passed += 1
else:
    print("[FAIL] Knowledge items: FAIL")
    failed += 1

if total_rels > 0:
    print("[OK] Semantic relationships: PASS")
    passed += 1
else:
    print("[FAIL] Semantic relationships: FAIL")
    failed += 1

if len(graph['nodes']) >= 391:
    print("[OK] Knowledge graph: PASS")
    passed += 1
else:
    print("[FAIL] Knowledge graph: FAIL")
    failed += 1

if path is not None and len(path) >= 1:
    print("[OK] Pathfinding: PASS")
    passed += 1
else:
    print("[FAIL] Pathfinding: FAIL")
    failed += 1

print("\n" + "="*70)
print(f"TOTAL: {passed}/5 tests passed")
if failed == 0:
    print("PHASE 3 VALIDATION: SUCCESS!")
    sys.exit(0)
else:
    print(f"PHASE 3 VALIDATION: {failed} failures")
    sys.exit(1)
