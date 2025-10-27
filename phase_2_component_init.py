#!/usr/bin/env python
"""
BOB AI v9.0 - Phase 2: Component Initialization
Tests loading and initialization of all core components with data verification
"""

import sys
import time
from pathlib import Path

def print_header(title: str) -> None:
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")

def phase_2_component_init():
    """Phase 2: Component Initialization"""
    print_header("PHASE 2: COMPONENT INITIALIZATION")

    all_pass = True
    start_time = time.time()

    # Add backend to path
    sys.path.insert(0, str(Path("backend").absolute()))

    # =====================================================================
    # Test 2.1: Knowledge Graph Initialization
    # =====================================================================
    print_header("TEST 2.1: KNOWLEDGE GRAPH INITIALIZATION")

    try:
        from bob_ai_knowledge_graph import get_knowledge_graph

        print("Loading Knowledge Graph...")
        kg = get_knowledge_graph()

        # Get statistics
        stats = kg.get_graph_statistics()
        total_items = stats.get("total_items", 0)
        total_disciplines = stats.get("total_disciplines", 0)

        print(f"✓ Knowledge Graph loaded successfully")
        print(f"  Total items: {total_items:,}")
        print(f"  Total disciplines: {total_disciplines:,}")
        print(f"  Total relationships: {stats.get('total_relationships', 0):,}")

        if total_items > 0 and total_disciplines > 0:
            print("✓ Knowledge Graph: READY\n")
        else:
            print("⚠ Knowledge Graph: Items or disciplines empty\n")
            all_pass = False

    except Exception as e:
        print(f"✗ Knowledge Graph initialization failed: {e}\n")
        all_pass = False    # =====================================================================
    # Test 2.2: Multi-Agent Reasoner Initialization
    # =====================================================================
    print_header("TEST 2.2: MULTI-AGENT REASONER INITIALIZATION")

    try:
        from bob_ai_multi_agent_reasoner import get_multi_agent_reasoner

        print("Initializing Multi-Agent Reasoner...")
        mar = get_multi_agent_reasoner()

        # Test reasoning
        print(f"✓ Multi-Agent Reasoner initialized")

        test_problem = "Should we use GPU or CPU for processing?"
        result = mar.reason_about_decision(test_problem)

        perspectives = result.get("perspectives", {})
        print(f"  Agents reasoning: {len(perspectives)}")

        for agent_name in perspectives.keys():
            print(f"    - {agent_name}")

        if len(perspectives) >= 5:
            print("✓ Multi-Agent Reasoner: READY\n")
        else:
            print(f"⚠ Multi-Agent Reasoner: Only {len(perspectives)} perspectives (expected 5)\n")

    except Exception as e:
        print(f"✗ Multi-Agent Reasoner initialization failed: {e}\n")
        all_pass = False    # =====================================================================
    # Test 2.3: Discipline Mapper Initialization
    # =====================================================================
    print_header("TEST 2.3: DISCIPLINE MAPPER INITIALIZATION")

    try:
        from bob_ai_discipline_mapper import get_discipline_mapper

        print("Initializing Discipline Mapper...")
        dm = get_discipline_mapper()

        # Get disciplines and stats
        print("Retrieving discipline data...")
        all_disciplines = dm.get_all_disciplines()
        mapper_stats = dm.get_mapper_statistics()

        print(f"✓ Discipline Mapper initialized")
        print(f"  Total disciplines: {len(all_disciplines):,}")
        print(f"  Total tiers: {mapper_stats.get('total_tiers', 'N/A')}")

        if len(all_disciplines) > 0:
            print("  Sample disciplines:")
            for i, discipline in enumerate(all_disciplines[:5], 1):
                print(f"    {i}. {discipline}")

        if len(all_disciplines) > 100:
            print("✓ Discipline Mapper: READY\n")
        else:
            print(f"⚠ Discipline Mapper: Only {len(all_disciplines)} disciplines\n")

    except Exception as e:
        print(f"✗ Discipline Mapper initialization failed: {e}\n")
        all_pass = False

    # =====================================================================
    # Test 2.4: Integration Hub Initialization
    # =====================================================================
    print_header("TEST 2.4: INTEGRATION HUB INITIALIZATION")

    try:
        from bob_ai_integration_hub import get_bob_ai_hub

        print("Initializing Integration Hub...")
        hub = get_bob_ai_hub()

        print(f"✓ Integration Hub initialized")

        # Get system status
        try:
            status = hub.get_system_status()
            print(f"  System status: {status.get('status', 'unknown')}")
            print(f"  Components initialized: {len(status.get('components', {}))}")
        except:
            print("  (Status check not available)")

        print("✓ Integration Hub: READY\n")

    except Exception as e:
        print(f"✗ Integration Hub initialization failed: {e}\n")
        all_pass = False

    # =====================================================================
    # Test 2.5: Sample Query Test
    # =====================================================================
    print_header("TEST 2.5: SAMPLE QUERY TEST")

    try:
        from bob_ai_integration_hub import get_bob_ai_hub

        hub = get_bob_ai_hub()

        test_queries = [
            "music composition",
            "artificial intelligence",
            "sustainable development"
        ]

        print("Running sample queries...\n")

        for query in test_queries:
            start = time.time()
            try:
                result = hub.query_knowledge(query)
                elapsed = time.time() - start

                print(f"✓ Query: '{query}'")
                print(f"  Response time: {elapsed*1000:.0f}ms")

            except Exception as query_err:
                print(f"⚠ Query '{query}' failed: {query_err}")

        print("\n✓ Sample Query Test: COMPLETE\n")

    except Exception as e:
        print(f"⚠ Sample Query Test: {e}\n")

    # =====================================================================
    # Phase 2 Summary
    # =====================================================================
    elapsed = time.time() - start_time

    print_header("PHASE 2: SUMMARY")

    if all_pass:
        print("✓ PHASE 2: ALL COMPONENTS INITIALIZED SUCCESSFULLY")
        print(f"\nDuration: {elapsed:.1f} seconds")
        print("\nNext Phase: Phase 3 - Server Startup")
        return 0
    else:
        print("⚠ PHASE 2: SOME COMPONENTS HAD ISSUES")
        print(f"\nDuration: {elapsed:.1f} seconds")
        print("\nRecommendation: Review errors above before proceeding to Phase 3")
        return 1

if __name__ == "__main__":
    exit_code = phase_2_component_init()
    sys.exit(exit_code)
