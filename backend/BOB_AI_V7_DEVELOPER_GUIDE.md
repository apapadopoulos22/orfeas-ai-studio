"""
BOB AI v7 - Developer Guide
Phase 10.2: Complete Developer Documentation

How to:

1. Add knowledge items
2. Create relationships
3. Use quality dashboard
4. Query knowledge graph
5. Integrate with LLM
"""

# ============================================================================

# 1. ADDING KNOWLEDGE ITEMS

# ============================================================================

"""
Two methods: Direct API or Python SDK
"""

# METHOD 1: REST API

import requests

url = "<http://localhost:5000/api/v7/add>"
item = {
    "label": "Supervised Learning",
    "category": "AI",
    "description": "Learning with labeled training data",
    "quality": 0.93,
    "metadata": {
        "confidence": 0.95,
        "precision": 0.90,
        "completeness": 0.92
    }
}

response = requests.post(url, json=item)
print(response.json())

# Output: {'success': True, 'item_id': 'sl-001', 'quality': 0.93}

# METHOD 2: Python SDK (Direct Import)

from bob_ai_v7_quality_system import QualityDashboard
from bob_ai_v7_knowledge_graph_core import KnowledgeNode

node = KnowledgeNode(
    label="Supervised Learning",
    category="AI",
    quality=0.93
)
print(f"Created: {node.label} (Quality: {node.quality})")

# ============================================================================

# 2. CREATING RELATIONSHIPS

# ============================================================================

"""
Connect items semantically using 15 relationship types
"""

# METHOD 1: REST API

relationship = {
    "source_id": "sl-001",
    "target_id": "ml-001",  # Machine Learning
    "relationship_type": "is_a",
    "strength": 0.92
}

response = requests.post(
    "<http://localhost:5000/api/v7/relationships>",
    json=relationship
)
print(response.json())

# METHOD 2: Python SDK

from bob_ai_v7_semantic_links import SemanticLinkManager

link_manager = SemanticLinkManager()
result = link_manager.add_relationship(
    source_label="Supervised Learning",
    target_label="Machine Learning",
    rel_type="is_a"
)
print(f"Relationship added: {result}")

# ============================================================================

# 3. USING THE QUALITY DASHBOARD

# ============================================================================

"""
Monitor quality metrics in real-time
"""

from bob_ai_v7_quality_system import QualityDashboard

dashboard = QualityDashboard()

# Get overall metrics

metrics = dashboard.get_overall_metrics()
print(f"Total Items: {metrics['total_items']}")
print(f"Average Quality: {metrics['avg_quality']:.3f}")
print(f"High-Quality %: {metrics['high_quality_percentage']:.1f}%")

# Get domain metrics

domain_metrics = dashboard.get_domain_metrics("ai")
print(f"\nAI Domain:")
print(f"  Items: {domain_metrics['item_count']}")
print(f"  Avg Quality: {domain_metrics['avg_quality']:.3f}")

# Check item quality

item_quality = dashboard.get_item_quality("ml-001")
print(f"\nMachine Learning Quality: {item_quality:.3f}")

# Generate report

report = dashboard.generate_report()
print(f"\nQuality Report:")
print(f"  Generated: {report['generated_at']}")
print(f"  Status: {report['status']}")

# ============================================================================

# 4. QUERYING THE KNOWLEDGE GRAPH

# ============================================================================

"""
Multiple search methods with different scopes
"""

from bob_ai_v7_integration_manager import KnowledgeIntegrationManager

manager = KnowledgeIntegrationManager()
search_engine = manager.search_engine

# 4A: Label Search (Fastest)

results = search_engine.search_by_label("neural networks", max_results=5)
print("Label Search Results:")
for result in results:
    print(f"  - {result['label']} (Quality: {result['quality']})")

# 4B: Domain Search

results = search_engine.search_by_domain("medicine", max_results=3)
print("\nMedicine Domain Items:")
for result in results:
    print(f"  - {result['label']}")

# 4C: Advanced Search (Multi-stage)

advanced_results = search_engine.search_advanced(
    query="deep learning applications",
    max_results=10
)
print(f"\nAdvanced Search Results: {len(advanced_results['results'])} items")
print(f"Search Time: {advanced_results['search_time_ms']:.2f}ms")

# 4D: Get Item Details

item_details = search_engine.get_item_details("ml-001")
print(f"\nItem Details: {item_details['label']}")
print(f"  Quality: {item_details['quality']}")
print(f"  Relationships: {len(item_details.get('relationships', []))}")

# ============================================================================

# 5. CROSS-DOMAIN QUERIES

# ============================================================================

"""
Find connections across different knowledge domains
"""

from bob_ai_v7_cross_domain_analyzer import CrossDomainAnalyzer

analyzer = CrossDomainAnalyzer()

# Find cross-domain bridges

bridges = analyzer.find_bridges_between("medicine", "environment")
print("Medicine ↔ Environment Bridges:")
for bridge in bridges:
    print(f"  - {bridge['topic']} (strength: {bridge['strength']})")

# Get domain connectivity

connectivity = analyzer.get_domain_connectivity()
print(f"\nDomain Connectivity:")
for domain, connections in connectivity.items():
    print(f"  {domain}: {connections['count']} connections")

# ============================================================================

# 6. LLM INTEGRATION

# ============================================================================

"""
Use knowledge graph to enhance LLM prompts
"""

from bob_ai_v7_llm_integration import LLMIntegrationV7

llm = LLMIntegrationV7()

# Generate context for LLM

user_prompt = "Explain machine learning applications in healthcare"
response = llm.generate_response(user_prompt, use_v7_enhancement=True)

print("LLM Integration Result:")
print(f"  Original Prompt: {response['original_prompt']}")
print(f"  Enhanced Prompt: {response['enhanced_prompt']}")
print(f"  Domains Detected: {response['domains_detected']}")
print(f"  Context Items: {response['ranked_results_count']}")

# Get ranked context

context = response.get('context_metrics', {})
print(f"\nContext Metrics:")
print(f"  Total Items: {context.get('total_context_items', 0)}")
print(f"  Quality Avg: {context.get('quality_avg', 0):.3f}")
print(f"  Retrieval Time: {context.get('retrieval_time_ms', 0):.2f}ms")

# ============================================================================

# 7. BATCH OPERATIONS

# ============================================================================

"""
Add/update multiple items efficiently
"""

# Batch add

items = [
    {"label": "Random Forest", "category": "AI", "quality": 0.91},
    {"label": "SVM", "category": "AI", "quality": 0.89},
    {"label": "Clustering", "category": "AI", "quality": 0.87},
]

batch_response = requests.post(
    "<http://localhost:5000/api/v7/batch/add>",
    json={"items": items}
)
print(f"Batch Add Result: {batch_response.json()}")

# ============================================================================

# 8. QUALITY MANAGEMENT

# ============================================================================

"""
Retrofit quality scores and manage quality degradation
"""

from bob_ai_v7_retrofit_knowledge import KnowledgeRetrofitter

retrofitter = KnowledgeRetrofitter()

# Retrofit existing items

items_to_retrofit = [
    {"label": "Neural Network", "category": "AI"},
    {"label": "Deep Learning", "category": "AI"},
]

results = retrofitter.retrofit_items(items_to_retrofit)
print(f"Retrofitted Items: {results['successful']}/{len(items_to_retrofit)}")
print(f"Average Quality: {results['average_quality']:.3f}")

# ============================================================================

# 9. PERFORMANCE MONITORING

# ============================================================================

"""
Monitor system performance metrics
"""

# Check cache performance

from bob_ai_v7_caching import CacheManager

cache = CacheManager()
cache_stats = cache.get_stats()
print("Cache Statistics:")
print(f"  Hit Rate: {cache_stats['hit_rate']:.1f}%")
print(f"  Size: {cache_stats['size_mb']:.2f}MB")
print(f"  Entries: {cache_stats['entry_count']}")

# Check indexing performance

from bob_ai_v7_indexing import KnowledgeIndexer

indexer = KnowledgeIndexer()
perf = indexer.get_performance_stats()
print(f"\nIndexing Performance:")
print(f"  Avg Search Time: {perf['avg_search_time_ms']:.3f}ms")
print(f"  P95 Search Time: {perf['p95_search_time_ms']:.3f}ms")

# ============================================================================

# 10. EXTERNAL ENRICHMENT

# ============================================================================

"""
Enrich knowledge with Wikipedia/Wikidata
"""

from bob_ai_v7_wikipedia_connector import WikipediaEnricher

enricher = WikipediaEnricher()

# Enrich an item

enriched = enricher.enrich_item(
    label="Machine Learning",
    domain="AI"
)
print("Enriched Item:")
print(f"  Wikipedia URL: {enriched.get('wikipedia_url')}")
print(f"  Summary: {enriched.get['summary', ''](:100)}...")

# ============================================================================

# 11. ERROR HANDLING

# ============================================================================

"""
Proper error handling patterns
"""

try:
    response = requests.post(
        "<http://localhost:5000/api/v7/add>",
        json={"label": "Test"}  # Missing required fields
    )
    if not response.json().get('success'):
        error = response.json().get('error')
        print(f"API Error: {error}")
except requests.exceptions.ConnectionError:
    print("Backend not available")
except Exception as e:
    print(f"Unexpected error: {e}")

# ============================================================================

# 12. COMPLETE WORKFLOW EXAMPLE

# ============================================================================

"""
Full end-to-end example: Add → Link → Query → Enhance LLM
"""

def complete_workflow():
    """Complete workflow demonstration"""

    # Step 1: Add new items
    print("Step 1: Adding items...")
    items = [
        {"label": "Transformer Networks", "category": "AI", "quality": 0.94},
        {"label": "Attention Mechanism", "category": "AI", "quality": 0.93},
        {"label": "Self-Attention", "category": "AI", "quality": 0.92},
    ]

    for item in items:
        requests.post("http://localhost:5000/api/v7/add", json=item)

    # Step 2: Create relationships
    print("Step 2: Creating relationships...")
    rel = {
        "source_id": "tn-001",
        "target_id": "am-001",
        "relationship_type": "uses",
        "strength": 0.95
    }
    requests.post("http://localhost:5000/api/v7/relationships", json=rel)

    # Step 3: Query items
    print("Step 3: Querying items...")
    results = requests.get(
        "http://localhost:5000/api/v7/search?q=transformer&domain=ai"
    ).json()
    print(f"Found {results['total']} items")

    # Step 4: Use for LLM
    print("Step 4: Generating LLM context...")
    llm = LLMIntegrationV7()
    response = llm.generate_response(
        "Explain transformer networks",
        use_v7_enhancement=True
    )
    print(f"LLM Context Ready: {response['advanced_context_available']}")

    # Step 5: Check quality
    print("Step 5: Checking quality...")
    dashboard = QualityDashboard()
    metrics = dashboard.get_overall_metrics()
    print(f"System Quality: {metrics['avg_quality']:.3f}")

# Run workflow

complete_workflow()

# ============================================================================

# TROUBLESHOOTING

# ============================================================================

"""
Common issues and solutions
"""

# Issue 1: Backend not responding

# Solution: Check if main.py is running

# $ cd backend && python main.py

# Issue 2: Port 5000 already in use

# Solution: Kill existing process and restart

# $ lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# $ python main.py

# Issue 3: Quality score out of range (not 0-1)

# Solution: Quality scores are automatically normalized

# Ensure all input metrics are 0-1 range

# Issue 4: Relationships not linking

# Solution: Verify both items exist before linking

# $ curl <http://localhost:5000/api/v7/search?q=item_label>

# Issue 5: Search performance slow

# Solution: Check cache hit rate and warm cache

# manager.warm_cache()

# ============================================================================

# BEST PRACTICES

# ============================================================================

"""
Development guidelines for BOB AI v7
"""

BEST_PRACTICES = """

1. QUALITY STANDARDS
   - Always provide quality scores 0.85-1.0 for high-quality items
   - Include confidence, precision, completeness metadata
   - Run quality retrofit for batch imports

2. RELATIONSHIP MANAGEMENT
   - Use specific relationship types (not just "related_to")
   - Include relationship strength (0.0-1.0)
   - Validate relationships don't create cycles

3. PERFORMANCE
   - Use batch operations for 50+ items
   - Enable caching for frequently accessed items
   - Monitor search times (target: <1ms)

4. ERROR HANDLING
   - Always check response.success before processing
   - Log all API errors with timestamp
   - Implement retry logic for network errors

5. SECURITY
   - Validate all user inputs
   - Use rate limiting (100 req/min)
   - Sanitize labels and descriptions

6. TESTING
   - Test with unit_tests.py (40 tests)
   - Run integration_tests.py (15 tests)
   - Validate performance with performance_validation.py

7. DOCUMENTATION
   - Document all custom relationships
   - Include examples in API responses
   - Keep API Reference updated

8. MONITORING
   - Track quality metrics daily
   - Monitor cache hit rates
   - Alert on quality degradation
"""

print(BEST_PRACTICES)

---

# ============================================================================

# QUICK REFERENCE TABLE

# ============================================================================

"""
Common Operations Quick Reference
"""

QUICK_REF = {
    "Add Item": "POST /api/v7/add",
    "Update Item": "PUT /api/v7/update/{id}",
    "Delete Item": "DELETE /api/v7/remove/{id}",
    "Search": "GET /api/v7/search?q={query}",
    "Domain Items": "GET /api/v7/domain/{domain}",
    "Item Details": "GET /api/v7/{id}",
    "Add Relationship": "POST /api/v7/relationships",
    "Quality Report": "GET /api/v7/quality/report",
}

for operation, endpoint in QUICK_REF.items():
    print(f"{operation:20} → {endpoint}")

---

*Last Updated: October 27, 2025*
*BOB AI v7 Knowledge System - Developer Guide*
