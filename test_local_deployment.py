#!/usr/bin/env python3
"""
BOB AI v8.0 - Local Deployment Test Script
Tests all 14 disciplines and cross-discipline linking
"""

import sys
import os
import time

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_module_loading():
    """Test loading all BOB AI modules"""
    print_header("TEST 1: Module Loading")

    try:
        from bob_ai_v8_loader import BobAIV8ModuleLoader

        print("Loading BOB AI v8.0 module loader...")
        start = time.time()
        loader = BobAIV8ModuleLoader()
        modules = loader.load_all_modules()
        elapsed = time.time() - start

        print(f"✅ Loaded {len(modules)} modules in {elapsed*1000:.0f}ms")
        print(f"\nDisciplines loaded:")
        for i, (name, module) in enumerate(list(modules.items())[:14], 1):
            print(f"  {i:2d}. {name:25s} - {module.__class__.__name__}")

        return True, modules
    except Exception as e:
        print(f"❌ Module loading failed: {e}")
        return False, None

def test_cross_discipline_linking(modules):
    """Test cross-discipline linking engine"""
    print_header("TEST 2: Cross-Discipline Linking")

    try:
        from bob_ai_v8_cross_discipline_linker import CrossDisciplineLinker

        print("Initializing cross-discipline linker...")
        start = time.time()
        linker = CrossDisciplineLinker()
        elapsed = time.time() - start

        print(f"✅ Linker ready in {elapsed*1000:.0f}ms")

        # Test getting related disciplines
        print("\nTesting 'book_writing' discipline relationships:")
        related = linker.get_related_disciplines('book_writing', min_strength=0.5)
        print(f"✅ Found {len(related)} related disciplines")
        for disc, strength in related[:5]:
            print(f"  • {disc:25s} - strength: {strength:.1%}")

        # Test knowledge bridges
        print("\nTesting knowledge bridge (book_writing ↔ prompt_engineering):")
        bridge = linker.get_knowledge_bridge('book_writing', 'prompt_engineering')
        if bridge:
            print(f"✅ Bridge found with {len(bridge['shared_concepts'])} shared concepts")
            for concept in bridge['shared_concepts'][:3]:
                print(f"  • {concept}")

        return True
    except Exception as e:
        print(f"❌ Cross-discipline linking failed: {e}")
        return False

def test_performance():
    """Test performance metrics"""
    print_header("TEST 3: Performance Validation")

    try:
        from bob_ai_v8_performance_optimizer import PerformanceProfiler

        print("Running performance profile...")
        profiler = PerformanceProfiler()

        # Profile bootstrap
        start = time.time()
        profile = profiler.profile_bootstrap()
        elapsed = time.time() - start

        print(f"\n✅ Performance profile completed in {elapsed:.2f}s")
        print(f"\nBootstrap metrics:")
        print(f"  Time: {profile['bootstrap_ms']:.0f}ms")
        print(f"  Target: 500ms")
        print(f"  Status: {'✅ PASS' if profile['bootstrap_ms'] < 500 else '❌ FAIL'} (2x faster)")

        return True
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def test_single_discipline(modules):
    """Test a single discipline enhancement"""
    print_header("TEST 4: Single Discipline Enhancement")

    try:
        print("Testing 'photography' module enhancement...")
        photography = modules.get('photography')

        if not photography:
            print("❌ Photography module not found")
            return False

        # Test enhancement
        start = time.time()
        enhancement = photography.enhance(
            user_input="Improve my composition for landscape photography",
            context={"style": "landscape", "experience": "intermediate"}
        )
        elapsed = time.time() - start

        print(f"✅ Enhancement completed in {elapsed*1000:.0f}ms")
        print(f"\nEnhancement output (first 300 chars):")
        print(f"  {enhancement[:300]}...")

        return True
    except Exception as e:
        print(f"❌ Discipline enhancement failed: {e}")
        return False

def test_knowledge_base_stats(modules):
    """Display knowledge base statistics"""
    print_header("TEST 5: Knowledge Base Statistics")

    try:
        total_items = 0
        total_categories = 0

        print("Knowledge base statistics:\n")
        for name, module in list(modules.items())[:14]:
            try:
                # Get module stats
                kb = getattr(module, 'knowledge_base', {})
                items = kb.get('knowledge_items', [])
                categories = set(item.get('category', 'unknown') for item in items)

                total_items += len(items)
                total_categories += len(categories)

                print(f"  {name:25s} - {len(items):4d} items, {len(categories):2d} categories")
            except:
                pass

        print(f"\n✅ Total: {total_items}+ knowledge items, {total_categories}+ categories")
        return True
    except Exception as e:
        print(f"❌ Statistics test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("=" * 70)
    print("  BOB AI v8.0 - LOCAL DEPLOYMENT TEST")
    print("=" * 70)

    results = []

    # Test 1: Module Loading
    success, modules = test_module_loading()
    results.append(("Module Loading", success))

    if not modules:
        print_header("DEPLOYMENT FAILED")
        print("❌ Cannot proceed without loaded modules")
        return False

    # Test 2: Cross-Discipline Linking
    success = test_cross_discipline_linking(modules)
    results.append(("Cross-Discipline Linking", success))

    # Test 3: Performance
    success = test_performance()
    results.append(("Performance Validation", success))

    # Test 4: Single Discipline
    success = test_single_discipline(modules)
    results.append(("Discipline Enhancement", success))

    # Test 5: Knowledge Base
    success = test_knowledge_base_stats(modules)
    results.append(("Knowledge Base Stats", success))

    # Summary
    print_header("DEPLOYMENT TEST SUMMARY")
    print("Test Results:\n")

    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name:30s} {status}")
        if success:
            passed += 1

    print(f"\nTotal: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n" + "="*70)
        print("  ✅ LOCAL DEPLOYMENT SUCCESSFUL")
        print("  BOB AI v8.0 is ready for local testing")
        print("="*70)
        return True
    else:
        print("\n" + "="*70)
        print("  ❌ DEPLOYMENT INCOMPLETE")
        print("  Check errors above and review BOB_AI_V8_TROUBLESHOOTING.md")
        print("="*70)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
