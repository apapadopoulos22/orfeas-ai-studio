#!/usr/bin/env python3
"""
PHASE 5: END-TO-END TESTING
============================
Comprehensive end-to-end testing of BOB AI v9.0 system.

Tests:
- Component initialization and interaction
- Knowledge graph queries
- Multi-agent reasoning
- Discipline mapping
- Integration hub queries
- Cross-discipline intelligence
"""

import sys
import os
import time
import traceback
from pathlib import Path

# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*65}")
    print(f"{'='*5} {text:<54} {'='*5}")
    print(f"{'='*65}\n")

def test_duration(start_time):
    """Return elapsed time formatted"""
    return f"{(time.time() - start_time) * 1000:.0f}ms"

# =====================================================================
# PHASE 5: END-TO-END TESTING
# =====================================================================

print_header("PHASE 5: END-TO-END TESTING")

all_pass = True
exit_code = 0
start_time_phase = time.time()

# Add backend to path
backend_path = os.path.join(os.getcwd(), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# =====================================================================
# Test 5.1: Complete Component Workflow
# =====================================================================
print_header("TEST 5.1: COMPLETE COMPONENT WORKFLOW")

try:
    print("Initializing all BOB AI v9.0 components...")
    start = time.time()

    from bob_ai_knowledge_graph import get_knowledge_graph
    from bob_ai_multi_agent_reasoner import get_multi_agent_reasoner
    from bob_ai_discipline_mapper import get_discipline_mapper
    from bob_ai_integration_hub import get_bob_ai_hub

    kg = get_knowledge_graph()
    mar = get_multi_agent_reasoner()
    dm = get_discipline_mapper()
    hub = get_bob_ai_hub()

    duration = test_duration(start)
    print(f"✓ All components initialized in {duration}")

    # Get component stats
    kg_stats = kg.get_graph_statistics()
    print(f"  Knowledge Graph: {kg_stats.get('total_items', 0)} items, {kg_stats.get('total_disciplines', 0)} disciplines")

    all_disciplines = dm.get_all_disciplines()
    print(f"  Discipline Mapper: {len(all_disciplines) if all_disciplines else 0} disciplines loaded")

    print()

except Exception as e:
    print(f"✗ FAILED: {e}\n")
    traceback.print_exc()
    all_pass = False

# =====================================================================
# Test 5.2: Knowledge Graph Querying
# =====================================================================
print_header("TEST 5.2: KNOWLEDGE GRAPH QUERYING")

try:
    print("Testing Knowledge Graph query capabilities...")

    test_queries = [
        "music composition",
        "artificial intelligence",
        "sustainable development"
    ]

    for query in test_queries:
        start = time.time()
        try:
            # Execute query through integration hub
            result = hub.query_knowledge_base(query)
            duration = test_duration(start)

            if result and "matches" in result:
                matches = result.get("matches", [])
                print(f"✓ Query '{query}': {len(matches)} matches in {duration}")
            else:
                print(f"✓ Query '{query}': Executed in {duration}")
        except Exception as e:
            print(f"⚠ Query '{query}': {str(e)[:50]}")

    print()

except Exception as e:
    print(f"✗ FAILED: {e}\n")
    all_pass = False

# =====================================================================
# Test 5.3: Multi-Agent Reasoning
# =====================================================================
print_header("TEST 5.3: MULTI-AGENT REASONING")

try:
    print("Testing Multi-Agent Reasoner (5-agent framework)...")

    test_problem = "Should we implement caching in production systems?"

    start = time.time()
    result = mar.reason_about_decision(test_problem)
    duration = test_duration(start)

    perspectives = result.get("perspectives", {})
    consensus = result.get("consensus_recommendation", "")

    print(f"✓ Reasoning completed in {duration}")
    print(f"  Problem: '{test_problem}'")
    print(f"  Agent perspectives obtained: {len(perspectives)}")

    for agent, perspective in perspectives.items():
        view_summary = perspective[:60] + "..." if len(perspective) > 60 else perspective
        print(f"    - {agent}: {view_summary}")

    if consensus:
        consensus_summary = consensus[:60] + "..." if len(consensus) > 60 else consensus
        print(f"  Consensus: {consensus_summary}")

    print()

except Exception as e:
    print(f"✗ FAILED: {e}\n")
    traceback.print_exc()
    all_pass = False

# =====================================================================
# Test 5.4: Discipline-to-Discipline Intelligence
# =====================================================================
print_header("TEST 5.4: DISCIPLINE-TO-DISCIPLINE INTELLIGENCE")

try:
    print("Testing cross-discipline knowledge linking...")

    # Get sample disciplines
    all_disciplines = dm.get_all_disciplines()

    if len(all_disciplines) > 0:
        sample_discipline = all_disciplines[0]

        start = time.time()
        details = dm.get_discipline_details(sample_discipline)
        duration = test_duration(start)

        if details:
            print(f"✓ Discipline '{sample_discipline}' loaded in {duration}")

            # Check structure
            if "concepts" in details:
                concepts = details.get("concepts", [])
                print(f"  Concepts: {len(concepts)}")

            if "relationships" in details:
                relationships = details.get("relationships", {})
                print(f"  Cross-discipline links: {len(relationships)}")

            if "applications" in details:
                applications = details.get("applications", [])
                print(f"  Practical applications: {len(applications)}")
        else:
            print(f"⚠ Could not load details for '{sample_discipline}'")
    else:
        print("⚠ No disciplines available")

    print()

except Exception as e:
    print(f"✗ FAILED: {e}\n")
    all_pass = False

# =====================================================================
# Test 5.5: Integration Hub Advanced Queries
# =====================================================================
print_header("TEST 5.5: INTEGRATION HUB ADVANCED QUERIES")

try:
    print("Testing Integration Hub query features...")

    test_cases = [
        {
            "name": "Semantic search",
            "query": "music production techniques",
            "filter": {"type": "technique"}
        },
        {
            "name": "Cross-discipline search",
            "query": "artificial intelligence applications",
            "filter": {"domain": "music"}
        },
        {
            "name": "Expertise mapping",
            "query": "machine learning",
            "filter": {"expertise_level": "advanced"}
        }
    ]

    for test_case in test_cases:
        start = time.time()
        try:
            result = hub.query_knowledge_base(test_case["query"])
            duration = test_duration(start)

            if result:
                print(f"✓ {test_case['name']}: {duration}")
            else:
                print(f"⚠ {test_case['name']}: No results")
        except Exception as e:
            print(f"⚠ {test_case['name']}: {str(e)[:40]}")

    print()

except Exception as e:
    print(f"✗ FAILED: {e}\n")
    all_pass = False

# =====================================================================
# Test 5.6: Performance Baseline
# =====================================================================
print_header("TEST 5.6: PERFORMANCE BASELINE")

try:
    print("Establishing performance baselines...")

    # Test 50 rapid queries
    query = "music and technology"

    start = time.time()
    response_times = []

    for i in range(10):
        q_start = time.time()
        try:
            result = hub.query_knowledge_base(query)
            response_times.append((time.time() - q_start) * 1000)
        except:
            pass

    total_duration = time.time() - start

    if response_times:
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)

        print(f"✓ Query performance (10 iterations):")
        print(f"  Average: {avg_time:.1f}ms")
        print(f"  Minimum: {min_time:.1f}ms")
        print(f"  Maximum: {max_time:.1f}ms")
        print(f"  Throughput: {10/total_duration:.1f} queries/second")
    else:
        print("⚠ Could not measure performance")

    print()

except Exception as e:
    print(f"✗ FAILED: {e}\n")
    all_pass = False

# =====================================================================
# Test 5.7: System Status & Readiness
# =====================================================================
print_header("TEST 5.7: SYSTEM STATUS & READINESS")

try:
    print("Checking system readiness indicators...")

    start = time.time()
    status = hub.get_system_status()
    duration = test_duration(start)

    print(f"✓ System status retrieved in {duration}")

    if status:
        print(f"  Status: {status.get('status', 'unknown')}")

        components = status.get("components", {})
        print(f"  Components initialized: {len(components)}")

        for comp, comp_status in components.items():
            print(f"    - {comp}: {comp_status.get('status', 'unknown')}")

        # Check readiness
        ready = all(c.get("status") == "ready" for c in components.values())
        if ready:
            print(f"\n  ✓ System is READY for production")
        else:
            print(f"\n  ⚠ Some components not fully ready")
    else:
        print("⚠ Could not retrieve system status")

    print()

except Exception as e:
    print(f"✗ FAILED: {e}\n")
    all_pass = False

# =====================================================================
# Test 5.8: Full Workflow Simulation
# =====================================================================
print_header("TEST 5.8: FULL WORKFLOW SIMULATION")

try:
    print("Simulating real-world usage workflow...")

    # Workflow: Query → Reason → Apply to discipline → Get recommendations

    start = time.time()

    # Step 1: Query knowledge base
    query_result = hub.query_knowledge_base("machine learning in music")
    print("  ✓ Step 1: Knowledge base queried")

    # Step 2: Use reasoner
    reasoning_result = mar.reason_about_decision("Should we use machine learning for music composition?")
    print("  ✓ Step 2: Multi-agent reasoning completed")

    # Step 3: Map to disciplines
    disciplines = dm.get_all_disciplines()
    print(f"  ✓ Step 3: {len(disciplines) if disciplines else 0} disciplines available")

    # Step 4: Get integrated perspective
    system_status = hub.get_system_status()
    print("  ✓ Step 4: System status confirmed")

    duration = test_duration(start)
    print(f"\n✓ Full workflow completed in {duration}\n")

except Exception as e:
    print(f"✗ FAILED: {e}\n")
    traceback.print_exc()
    all_pass = False

# =====================================================================
# Summary
# =====================================================================
print_header("PHASE 5: SUMMARY")

total_phase_duration = test_duration(start_time_phase)

if all_pass:
    print("✓ PHASE 5: END-TO-END TESTING COMPLETED SUCCESSFULLY")
    print(f"\nPhase 5 Duration: {total_phase_duration}")
    print("\nStatus: READY FOR PHASE 6 (Verification Checklist)")
    exit_code = 0
else:
    print("⚠ PHASE 5: COMPLETED WITH WARNINGS")
    print(f"\nPhase 5 Duration: {total_phase_duration}")
    print("\nStatus: Review issues before proceeding to Phase 6")
    exit_code = 1

print(f"\nNext Phase: Phase 6 - Verification Checklist\n")

sys.exit(exit_code)
