# BOB AI v9.0 - Comprehensive Usage Guide

**Version:** 9.0.0
**Date:** October 27, 2025
**Target Audience:** Developers, Researchers, Decision Makers

---

## Quick Navigation

- [Getting Started (5 minutes)](#getting-started-5-minutes)
- [Component Guides](#component-guides)
  - [Knowledge Graph Guide](#knowledge-graph-component-guide)
  - [Multi-Agent Reasoner Guide](#multi-agent-reasoner-component-guide)
  - [Discipline Mapper Guide](#discipline-mapper-component-guide)
  - [Integration Hub Guide](#integration-hub-component-guide)
- [Common Workflows](#common-workflows)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

---

## Getting Started (5 minutes)

### Installation

```bash
# 1. Navigate to project directory
cd c:\Users\johng\Documents\oscar

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify installation
python -c "from bob_ai_integration_hub import get_integration_hub; print('✓ BOB AI v9.0 ready')"
```

### First Query (Your First 2 Minutes)

```python
# main.py or interactive Python session
from bob_ai_integration_hub import get_integration_hub

# Get the unified interface
hub = get_integration_hub()

# Ask a question
result = hub.query_knowledge("What are the basics of music composition?")

# Print results
print("Query:", result.query)
print("\nRelevant disciplines:")
for discipline, confidence in result.relevant_disciplines[:3]:
    print(f"  • {discipline} ({confidence:.0%} match)")

print("\nRecommendations:")
for rec in result.recommendations[:3]:
    print(f"  • {rec}")
```

**Expected Output:**

```
Query: What are the basics of music composition?

Relevant disciplines:
  • Music Composition (95% match)
  • Music Theory (92% match)
  • Harmony (88% match)

Recommendations:
  • Study harmonic progressions
  • Learn voice leading
  • Practice orchestration
```

---

## Component Guides

### Knowledge Graph Component Guide

**Purpose:** Manage relationships between disciplines and find pathways through knowledge.

#### Use Case 1: Search for Related Topics

```python
from bob_ai_knowledge_graph import get_knowledge_graph

kg = get_knowledge_graph()

# Find what's related to music composition
related = kg.find_related_disciplines("Music Composition", max_depth=2)

print("Topics related to Music Composition:")
for discipline in related[:10]:
    print(f"  • {discipline}")
```

#### Use Case 2: Find Learning Paths

```python
# Plan a learning journey
path = kg.find_learning_path(
    start="Basic Music Theory",
    end="Film Scoring"
)

if path:
    print("Learning path from Theory to Film Scoring:")
    for i, step in enumerate(path, 1):
        print(f"  Step {i}: {step}")
    print(f"\nTotal steps: {len(path)}")
else:
    print("No path found between these disciplines")
```

#### Use Case 3: Search by Keywords

```python
# Find disciplines related to harmony
harmony_topics = kg.search_by_keywords(["harmony", "chord", "progression"])

print(f"Found {len(harmony_topics)} topics about harmony:")
for topic in harmony_topics[:5]:
    print(f"  • {topic}")
```

#### Use Case 4: Get Discipline Information

```python
# Learn about a specific discipline
info = kg.get_discipline_info("Music Composition")

print(f"Discipline: {info['name']}")
print(f"  Tier: {info['tier']}")
print(f"  Category: {info['category']}")
print(f"  Knowledge Items: {info['item_count']}")
print(f"  Keywords: {', '.join(info['keywords'][:5])}")
```

#### Use Case 5: Analyze the Graph

```python
# Get system-wide statistics
stats = kg.get_graph_statistics()

print("Knowledge Graph Statistics:")
print(f"  Total Disciplines: {stats['num_nodes']}")
print(f"  Total Relationships: {stats['num_edges']}")
print(f"  Coverage: {stats['tiers_covered']} tiers")
print(f"  Knowledge Items: {stats['total_items']:,}")
print(f"  Average Connections: {stats['avg_connections']:.1f}")
```

---

### Multi-Agent Reasoner Component Guide

**Purpose:** Analyze complex decisions from 5 different expert perspectives.

#### Understanding the 5 Agents

```python
from bob_ai_multi_agent_reasoner import get_multi_agent_reasoner

reasoner = get_multi_agent_reasoner()

# Each agent represents a different thinking style:
# PESSIMIST     - "What could go wrong?" (Risk-focused)
# OPTIMIST      - "Why this could work?" (Opportunity-focused)
# ENGINEER      - "How do we build it?" (Implementation-focused)
# RESEARCHER    - "What does research say?" (Evidence-focused)
# DEVIL_ADVOCATE - "Is our premise wrong?" (Assumption-testing)
```

#### Use Case 1: Analyze a Decision

```python
# Analyze a career decision
analysis = reasoner.reason_about_decision(
    problem_statement="Should I specialize in film scoring or classical composition?",
    context={
        "current_skills": "Music theory, composition basics",
        "market_demand": "Film scoring (high), Classical (moderate)",
        "personal_interest": "Film music"
    }
)

print("DECISION ANALYSIS")
print("=" * 60)

for perspective in analysis['perspectives']:
    agent_name = perspective.agent_type.value.upper()
    print(f"\n{agent_name} PERSPECTIVE:")
    print(f"  Position: {perspective.position}")
    print(f"  Confidence: {perspective.confidence:.0%}")
    print(f"  Recommendation: {perspective.recommendation}")

    if perspective.key_insights:
        print("  Key Insights:")
        for insight in perspective.key_insights[:2]:
            print(f"    • {insight}")

print(f"\nCONSENSUS: {analysis['consensus']}")
print(f"CONFIDENCE: {analysis['confidence']}%")
```

#### Use Case 2: Compare Multiple Options

```python
# Compare different approaches to a technical problem
comparison = reasoner.compare_alternatives(
    alternatives=[
        {
            "option": "GPU Caching",
            "pros": ["40x faster", "modern approach"],
            "cons": ["complex", "memory intensive"]
        },
        {
            "option": "CPU Only",
            "pros": ["simple", "reliable"],
            "cons": ["slow", "won't meet SLA"]
        },
        {
            "option": "Hybrid GPU/CPU",
            "pros": ["fast + reliable", "flexible"],
            "cons": ["complex code", "maintenance burden"]
        }
    ],
    criteria=["Performance", "Reliability", "Complexity", "Cost"]
)

print("ALTERNATIVE COMPARISON")
for option, scores in comparison.items():
    print(f"\n{option}:")
    for criterion, score in scores.items():
        print(f"  {criterion}: {'★' * int(score/20)}")
```

#### Use Case 3: Get Single Agent Perspective

```python
# Consult just the pessimist for risk analysis
pessimist_view = reasoner.get_agent_perspective(
    agent_type='pessimist',
    problem_statement="Should we migrate to microservices?",
    context={"current_monolith": "stable", "team_size": 5}
)

print("PESSIMIST'S RISK ANALYSIS:")
print(f"  Worst case: {pessimist_view['worst_case']}")
print(f"  Key risks:")
for risk in pessimist_view['identified_risks'][:3]:
    print(f"    ⚠ {risk}")
print(f"  Confidence in doom: {pessimist_view['confidence']:.0%}")
```

---

### Discipline Mapper Component Guide

**Purpose:** Discover and access the 1,300+ disciplines across all 12 tiers.

#### Use Case 1: Browse Available Disciplines

```python
from bob_ai_discipline_mapper import get_discipline_mapper

mapper = get_discipline_mapper()

# See what's available in each tier
for tier in range(1, 5):  # First 4 tiers
    disciplines = mapper.get_disciplines_by_tier(tier)
    print(f"\nTier {tier}:")
    for discipline in disciplines[:3]:
        print(f"  • {discipline}")
    if len(disciplines) > 3:
        print(f"  ... and {len(disciplines) - 3} more")
```

#### Use Case 2: Search for Disciplines

```python
# Search for all music-related disciplines
music_disciplines = mapper.search_disciplines("music")

print("Music-related disciplines:")
for discipline, score in music_disciplines[:5]:
    print(f"  • {discipline} (relevance: {score:.0%})")
```

#### Use Case 3: Get Discipline Knowledge

```python
# Access knowledge base for a specific discipline
kb = mapper.get_discipline_knowledge("Music Composition")

print(f"Music Composition Knowledge Base:")
print(f"  Total items: {len(kb['items'])}")
print(f"  Categories: {', '.join(kb['categories'][:5])}")
print(f"\nFirst 5 items:")
for i, item in enumerate(kb['items'][:5], 1):
    print(f"  {i}. {item['name']}")
    print(f"     {item['description'][:60]}...")
```

#### Use Case 4: System Statistics

```python
# Get overall mapper statistics
stats = mapper.get_mapper_statistics()

print("MAPPER STATISTICS")
print(f"  Total modules loaded: {stats['total_modules']}")
print(f"  Total knowledge items: {stats['total_items']:,}")
print(f"  Load status: {stats['load_status']}")

print("\nBy Tier:")
for tier, count in stats['tier_breakdown'].items():
    print(f"  Tier {tier}: {count} modules")
```

---

### Integration Hub Component Guide

**Purpose:** Use the unified interface for all v9.0 functionality.

#### Use Case 1: Comprehensive Knowledge Query

```python
from bob_ai_integration_hub import get_integration_hub

hub = get_integration_hub()

# Ask a complex question
result = hub.query_knowledge(
    query="How do I compose music for film?",
    context="I have background in classical composition",
    limit=5
)

print("=" * 60)
print("KNOWLEDGE QUERY RESULTS")
print("=" * 60)

print(f"\nQuery: {result.query}")
print(f"Found {len(result.relevant_disciplines)} relevant disciplines:")
for i, (discipline, confidence) in enumerate(result.relevant_disciplines, 1):
    print(f"  {i}. {discipline} ({confidence:.0%})")

print(f"\nRecommendations:")
for i, rec in enumerate(result.recommendations, 1):
    print(f"  {i}. {rec}")
```

#### Use Case 2: Learning Path Planning

```python
# Get personalized learning path
path_rec = hub.get_learning_recommendation(
    current_disciplines=["Music Theory", "Music Composition"],
    learning_goal="Professional Film Scoring",
    max_steps=6
)

print("=" * 60)
print("LEARNING PATH TO FILM SCORING")
print("=" * 60)

print("\nRecommended progression:")
for i, discipline in enumerate(path_rec.path, 1):
    print(f"  Step {i}: {discipline}")

print(f"\nEstimated duration: {path_rec.estimated_duration} hours")

print("\nKey milestones:")
for milestone in path_rec.key_milestones:
    print(f"  ✓ {milestone}")

if path_rec.prerequisites:
    print("\nPrerequisites:")
    for prereq in path_rec.prerequisites:
        print(f"  • {prereq}")
```

#### Use Case 3: Find Complementary Knowledge

```python
# What should I learn alongside film scoring?
complementary = hub.find_complementary_disciplines(
    discipline="Film Scoring",
    limit=5
)

print("Disciplines that complement Film Scoring:")
for discipline, relationship in complementary:
    print(f"  • {discipline} ({relationship})")
```

#### Use Case 4: Problem-Solving with Multi-Agent Analysis

```python
# Get multi-perspective analysis for a complex problem
analysis = hub.reason_about_problem(
    problem="Should I focus on orchestra or electronic film scoring?",
    disciplines=["Film Scoring", "Orchestration", "Music Technology"],
    return_consensus=True
)

print("=" * 60)
print("PROBLEM ANALYSIS: ORCHESTRA VS ELECTRONIC")
print("=" * 60)

print(f"\nConfidence: {analysis['confidence']}%\n")

print("Agent Perspectives:")
for i, perspective in enumerate(analysis['perspectives'], 1):
    agent = perspective.agent_type.value
    print(f"\n  {i}. {agent.upper()}")
    print(f"     Recommendation: {perspective.recommendation}")
    print(f"     Confidence: {perspective.confidence:.0%}")

print(f"\n{'FINAL CONSENSUS':^60}")
print(f"{analysis['consensus']}")
```

#### Use Case 5: Knowledge Search

```python
# Find specific items across all disciplines
results = hub.search_knowledge(
    query="orchestration techniques",
    limit=10
)

print(f"Found {len(results)} results for 'orchestration techniques':")
for i, result in enumerate(results[:5], 1):
    print(f"\n  {i}. {result['item']}")
    print(f"     Discipline: {result['discipline']}")
    print(f"     Relevance: {result.get('relevance', 'N/A')}")
```

#### Use Case 6: System Health Check

```python
# Check if everything is operational
status = hub.get_hub_status()

print("=" * 60)
print("BOB AI v9.0 - SYSTEM STATUS")
print("=" * 60)

print(f"\nOperational: {'✓ YES' if status['operational'] else '✗ NO'}")

print("\nComponent Status:")
for component, comp_status in status['components'].items():
    status_text = comp_status['status'].upper()
    symbol = "✓" if comp_status['status'] == 'ready' else "✗"
    print(f"  {symbol} {component}: {status_text}")

print("\nPerformance Metrics:")
perf = status['performance']
print(f"  Avg Query Time: {perf['avg_query_time']}ms")
print(f"  Avg Reasoning Time: {perf['avg_reasoning_time']}ms")
print(f"  Cache Hit Rate: {perf['cache_hits']:.0%}")
```

---

## Common Workflows

### Workflow 1: Learn a New Domain

```python
from bob_ai_integration_hub import get_integration_hub

hub = get_integration_hub()

# Step 1: Explore the domain
print("STEP 1: Exploring Film Scoring Domain")
result = hub.query_knowledge("What is film scoring?", limit=5)
print(f"Found {len(result.relevant_disciplines)} relevant areas\n")

# Step 2: Get learning path
print("STEP 2: Creating Learning Path")
path = hub.get_learning_recommendation(
    current_disciplines=["Music Theory"],
    learning_goal="Film Scoring",
    max_steps=5
)
print(f"Path requires {len(path.path)} steps\n")

# Step 3: Analyze complementary areas
print("STEP 3: Finding Complementary Knowledge")
complementary = hub.find_complementary_disciplines("Film Scoring", limit=3)
print(f"Also recommended: {len(complementary)} complementary areas\n")

# Step 4: Make a decision
print("STEP 4: Multi-Agent Analysis")
analysis = hub.reason_about_problem(
    "Should I pursue this learning path?",
    path.prerequisites
)
print(f"Consensus confidence: {analysis['confidence']}%")
```

### Workflow 2: Make a Career Decision

```python
# Career decision support
problem = "Should I specialize in classical or film composition?"

# Get perspectives from all angles
analysis = hub.reason_about_problem(
    problem=problem,
    disciplines=["Music Composition", "Film Scoring", "Career Planning"],
)

# Show decision matrix
print("CAREER DECISION MATRIX")
for perspective in analysis['perspectives']:
    print(f"\n{perspective.agent_type.value}:")
    print(f"  Recommendation: {perspective.recommendation}")
    print(f"  Confidence: {perspective.confidence:.0%}")

print(f"\nFinal Recommendation: {analysis['consensus']}")
print(f"Confidence Level: {analysis['confidence']}%")

# Get resources for top recommendation
if 'classical' in analysis['consensus'].lower():
    resources = hub.search_knowledge("classical composition techniques", limit=5)
else:
    resources = hub.search_knowledge("film composition techniques", limit=5)

print(f"\nTop resources:")
for resource in resources[:3]:
    print(f"  • {resource['item']}")
```

### Workflow 3: Research a Topic

```python
# Research workflow
topic = "Music production in the digital era"

# Step 1: Search across all disciplines
print(f"Searching for: {topic}")
search_results = hub.search_knowledge(topic, limit=20)
print(f"Found {len(search_results)} relevant items\n")

# Step 2: Find related disciplines
print("Related disciplines:")
query_result = hub.query_knowledge(topic)
for discipline, conf in query_result.relevant_disciplines[:5]:
    print(f"  • {discipline} ({conf:.0%})")

# Step 3: Get expert perspectives
print("\nExpert analysis:")
analysis = hub.reason_about_problem(
    f"What's the future of {topic}?"
)
print(f"Consensus: {analysis['consensus']}")

# Step 4: Find learning resources
print("\nLearning resources:")
for item in search_results[:3]:
    print(f"  • {item['item']} ({item['discipline']})")
```

---

## Advanced Usage

### Performance Optimization

```python
from bob_ai_integration_hub import get_integration_hub
from functools import lru_cache

hub = get_integration_hub()

# Cache frequent queries
@lru_cache(maxsize=128)
def cached_query(query_text):
    return hub.query_knowledge(query_text)

# Monitor performance
status = hub.get_hub_status()
if status['performance']['avg_query_time'] > 500:
    print("Warning: Query performance degraded")
    # Consider reducing search scope or caching
```

### Batch Processing

```python
# Process multiple queries
queries = [
    "Music composition basics",
    "Film scoring techniques",
    "Orchestration for beginners"
]

results = []
for query in queries:
    result = hub.query_knowledge(query)
    results.append(result)

print(f"Processed {len(results)} queries")
```

### Custom Analysis

```python
# Combine multiple analyses
kg = get_knowledge_graph()
reasoner = get_multi_agent_reasoner()

# Get related disciplines
related = kg.find_related_disciplines("Film Scoring")

# Analyze why they're related
analysis = reasoner.reason_about_decision(
    f"Why are these disciplines related? {related[:3]}"
)

print(f"Relationship analysis: {analysis['consensus']}")
```

### Integration with External Systems

```python
# Export results for external use
result = hub.query_knowledge("music composition")

# Convert to JSON for APIs
import json
json_result = json.dumps(result.to_dict(), indent=2)

# Save to file
with open('query_result.json', 'w') as f:
    f.write(json_result)
```

---

## Troubleshooting

### Issue: Module not loading

```python
# Symptom: ImportError when accessing disciplines
# Cause: Module path or dependency issue
# Solution:

import sys
sys.path.insert(0, 'c:/Users/johng/Documents/oscar/backend')

# Try again
from bob_ai_discipline_mapper import get_discipline_mapper
mapper = get_discipline_mapper()
```

### Issue: Query returns empty results

```python
# Symptom: query_knowledge returns no results
# Cause: Query too specific or discipline not loaded
# Solution:

# Try broader query
result = hub.query_knowledge("music")  # Instead of "baroque counterpoint"

# Check what's loaded
stats = mapper.get_mapper_statistics()
print(f"Loaded modules: {stats['total_modules']}")
```

### Issue: Reasoning takes too long

```python
# Symptom: reason_about_problem takes >5 seconds
# Cause: Too many disciplines or complex reasoning
# Solution:

# Limit disciplines
analysis = hub.reason_about_problem(
    problem,
    disciplines=["Music", "Technology"]  # Specific list
)

# Or use single agent instead
perspective = reasoner.get_agent_perspective(
    agent_type='engineer',  # Just one agent
    problem_statement=problem
)
```

### Issue: Memory usage high

```python
# Symptom: Python process using lots of memory
# Cause: Large knowledge base loaded
# Solution:

import gc

# Force garbage collection
gc.collect()

# Check memory status
status = hub.get_hub_status()
if 'memory_usage' in status:
    print(f"Memory: {status['memory_usage']}")
```

---

## Tips & Best Practices

1. **Always use singletons** - Don't create new instances
2. **Cache results** - Reuse query results when possible
3. **Handle exceptions** - Wrap all hub calls in try-except
4. **Monitor performance** - Check status regularly
5. **Use context** - Provide context for better results
6. **Start broad** - Search broadly, then narrow down
7. **Combine approaches** - Use multiple components together

---

## Examples Repository

See `API_REFERENCE_V9.md` for complete code examples including:

- Simple queries
- Learning paths
- Multi-agent analysis
- Advanced patterns
- Error handling

---

**Usage Guide Version:** 9.0.0
**Last Updated:** October 27, 2025
**Status:** ✅ Ready for Production Use
