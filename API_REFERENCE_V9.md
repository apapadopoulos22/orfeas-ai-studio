# BOB AI v9.0 - Comprehensive API Reference

**Version:** 9.0.0
**Date:** October 27, 2025
**Status:** ✅ Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Knowledge Graph API](#knowledge-graph-api)
3. [Multi-Agent Reasoner API](#multi-agent-reasoner-api)
4. [Discipline Mapper API](#discipline-mapper-api)
5. [Integration Hub API](#integration-hub-api)
6. [Data Models](#data-models)
7. [Error Handling](#error-handling)
8. [Examples](#examples)

---

## Overview

BOB AI v9.0 provides a unified API for querying 1,300+ disciplines across 12 knowledge tiers. The system combines:

- **Knowledge Graph:** Relationship mapping and pathfinding between disciplines
- **Multi-Agent Reasoner:** 5-perspective decision analysis
- **Discipline Mapper:** Dynamic module loading and indexing
- **Integration Hub:** Unified interface coordinating all components

### Architecture

```
┌─────────────────────────────────────┐
│    Integration Hub (Primary API)    │
│  query_knowledge()                  │
│  get_learning_recommendation()      │
│  find_complementary_disciplines()   │
│  reason_about_problem()             │
└──────────────┬──────────────────────┘
               │
    ┌──────────┼──────────┬─────────────┐
    │          │          │             │
    ▼          ▼          ▼             ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐
│ KG API │ │Reasoner│ │ Mapper │ │Discipline│
│        │ │  API   │ │  API   │ │ Modules  │
└────────┘ └────────┘ └────────┘ └──────────┘
    │          │          │             │
    └──────────┼──────────┴─────────────┘
               │
    ┌──────────▼──────────┐
    │  Knowledge Base     │
    │  (1,300+ items)     │
    └────────────────────┘
```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Import components
from bob_ai_integration_hub import get_integration_hub
from bob_ai_knowledge_graph import get_knowledge_graph
from bob_ai_multi_agent_reasoner import get_multi_agent_reasoner
from bob_ai_discipline_mapper import get_discipline_mapper
```

---

## Knowledge Graph API

### Overview

The Knowledge Graph manages relationships between disciplines and enables pathfinding through the knowledge space.

### Singleton Access

```python
from bob_ai_knowledge_graph import get_knowledge_graph

kg = get_knowledge_graph()  # Thread-safe singleton
```

### Key Classes

#### `KnowledgeGraph`

Main knowledge graph class managing all disciplines and relationships.

**Methods:**

```python
class KnowledgeGraph:

    def __init__(self):
        """Initialize the knowledge graph with all disciplines"""
        pass

    def add_discipline(self, name: str, tier: int, category: str,
                      keywords: List[str], description: str,
                      item_count: int) -> None:
        """
        Add a discipline node to the graph

        Args:
            name: Discipline name (e.g., "Music Composition")
            tier: Knowledge tier (1-12)
            category: Category (e.g., "music", "technology")
            keywords: Search keywords
            description: Discipline description
            item_count: Number of knowledge items

        Returns:
            None

        Example:
            >>> kg.add_discipline(
            ...     name="Music Composition",
            ...     tier=1,
            ...     category="music",
            ...     keywords=["harmony", "orchestration", "arrangement"],
            ...     description="Theory and techniques of music composition",
            ...     item_count=250
            ... )
        """
        pass

    def add_relationship(self, source: str, target: str,
                        relationship_type: str) -> None:
        """
        Add relationship between two disciplines

        Args:
            source: Source discipline name
            target: Target discipline name
            relationship_type: Type from {prerequisite, complementary, related,
                             specialization, application, foundation}

        Returns:
            None

        Example:
            >>> kg.add_relationship(
            ...     source="Music Theory",
            ...     target="Music Composition",
            ...     relationship_type="prerequisite"
            ... )
        """
        pass

    def find_related_disciplines(self, discipline: str,
                                max_depth: int = 2) -> List[str]:
        """
        Find all related disciplines using BFS

        Args:
            discipline: Starting discipline name
            max_depth: Maximum depth for search (default: 2)

        Returns:
            List of related discipline names

        Raises:
            ValueError: If discipline not found

        Example:
            >>> kg.find_related_disciplines("Music Composition", max_depth=2)
            ['Music Theory', 'Music History', 'Orchestration', ...]
        """
        pass

    def find_learning_path(self, start: str, end: str) -> Optional[List[str]]:
        """
        Find shortest learning path between two disciplines

        Args:
            start: Starting discipline
            end: Target discipline

        Returns:
            List of disciplines forming the path, or None if no path exists

        Example:
            >>> kg.find_learning_path("Music History", "Film Scoring")
            ['Music History', 'Music Composition', 'Film Scoring']
        """
        pass

    def search_by_keywords(self, keywords: List[str]) -> List[str]:
        """
        Search for disciplines by keywords

        Args:
            keywords: List of search keywords

        Returns:
            List of matching discipline names

        Example:
            >>> kg.search_by_keywords(["harmony", "composition"])
            ['Music Composition', 'Harmonic Theory', ...]
        """
        pass

    def get_discipline_info(self, discipline: str) -> Dict[str, Any]:
        """
        Get detailed information about a discipline

        Args:
            discipline: Discipline name

        Returns:
            Dictionary with {name, tier, category, keywords, description,
                           item_count, relationships}

        Raises:
            ValueError: If discipline not found

        Example:
            >>> kg.get_discipline_info("Music Composition")
            {
                'name': 'Music Composition',
                'tier': 1,
                'category': 'music',
                'keywords': ['harmony', 'orchestration', ...],
                'item_count': 250,
                'relationships': {...}
            }
        """
        pass

    def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge graph

        Returns:
            Dictionary with {num_nodes, num_edges, avg_connections,
                           tiers_covered, total_items}

        Example:
            >>> kg.get_graph_statistics()
            {
                'num_nodes': 1300,
                'num_edges': 4200,
                'avg_connections': 3.2,
                'tiers_covered': 12,
                'total_items': 17030
            }
        """
        pass
```

#### `DisciplineNode`

Represents a single discipline in the knowledge graph.

```python
@dataclass
class DisciplineNode:
    """
    Represents a discipline in the knowledge graph

    Attributes:
        name: Discipline name
        tier: Knowledge tier (1-12)
        category: Category classification
        keywords: Search keywords
        description: Discipline description
        item_count: Number of knowledge items
        relationships: Dictionary of relationships to other disciplines
    """
    name: str
    tier: int
    category: str
    keywords: List[str] = field(default_factory=list)
    description: str = ""
    item_count: int = 0
    relationships: Dict[str, List[Tuple[str, RelationshipType]]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def add_relationship(self, target_discipline: str,
                        relationship_type: RelationshipType) -> None:
        """Add relationship to another discipline"""
        pass
```

#### `LearningPath`

Represents a pathway through related disciplines.

```python
@dataclass
class LearningPath:
    """
    Represents a learning pathway through multiple disciplines

    Attributes:
        start_discipline: Starting discipline
        end_discipline: Target discipline
        path: List of disciplines in order
        relationships: Types of relationships along the path
        estimated_duration: Estimated learning time in hours
        items_covered: Number of knowledge items along path
    """
    start_discipline: str
    end_discipline: str
    path: List[str]
    relationships: List[str]
    estimated_duration: float = 0.0
    items_covered: int = 0
```

#### `ContextRouter`

Routes queries to relevant discipline contexts.

```python
class ContextRouter:
    """Routes queries to relevant discipline contexts"""

    def route_query(self, query: str) -> List[Tuple[str, float]]:
        """
        Route query to relevant disciplines with confidence scores

        Args:
            query: User query string

        Returns:
            List of (discipline_name, confidence) tuples, sorted by confidence

        Example:
            >>> router = get_context_router()
            >>> router.route_query("How do I compose a symphony?")
            [
                ('Music Composition', 0.95),
                ('Orchestration', 0.87),
                ('Music Theory', 0.82),
                ('Music History', 0.65)
            ]
        """
        pass
```

#### `RecommendationEngine`

Generates recommendations based on queries and context.

```python
class RecommendationEngine:
    """Generates discipline recommendations"""

    def get_recommendations(self, disciplines: List[str],
                           context: Optional[str] = None,
                           limit: int = 5) -> List[str]:
        """
        Get recommendation recommendations

        Args:
            disciplines: List of current disciplines
            context: Optional context for recommendations
            limit: Maximum number of recommendations

        Returns:
            List of recommended discipline names

        Example:
            >>> engine = get_recommendation_engine()
            >>> engine.get_recommendations(
            ...     disciplines=['Music Composition'],
            ...     context='looking to learn about film scoring',
            ...     limit=5
            ... )
            ['Film Scoring', 'Orchestration', 'Music Technology', ...]
        """
        pass
```

---

## Multi-Agent Reasoner API

### Overview

The Multi-Agent Reasoner provides 5-perspective decision analysis for complex problems.

### Singleton Access

```python
from bob_ai_multi_agent_reasoner import get_multi_agent_reasoner

reasoner = get_multi_agent_reasoner()  # Thread-safe singleton
```

### Key Classes

#### `MultiAgentReasoner`

Main reasoning engine coordinating 5 agent perspectives.

```python
class MultiAgentReasoner:
    """
    Multi-agent reasoning framework with 5 distinct perspectives:
    - Pessimist: Risk-focused analysis
    - Optimist: Opportunity-focused analysis
    - Engineer: Implementation-focused analysis
    - Researcher: Knowledge-focused analysis
    - Devil's Advocate: Assumption-challenging analysis
    """

    def __init__(self):
        """Initialize the reasoner with 5 agents"""
        pass

    def reason_about_decision(self, problem_statement: str,
                             context: Optional[Dict[str, Any]] = None,
                             required_disciplines: Optional[List[str]] = None
                             ) -> Dict[str, Any]:
        """
        Analyze a decision from 5 perspectives

        Args:
            problem_statement: Description of the decision to analyze
            context: Optional context information
            required_disciplines: Optional list of disciplines to consider

        Returns:
            Dictionary with:
                - perspectives: List of AgentPerspective objects
                - consensus: Consensus recommendation
                - confidence: Overall confidence (0-100)
                - risks: Identified risks
                - opportunities: Identified opportunities
                - next_steps: Recommended next actions

        Example:
            >>> reasoner.reason_about_decision(
            ...     "Should we implement GPU caching for performance?",
            ...     context={"current_latency": "2s", "target": "500ms"},
            ...     required_disciplines=["Software Engineering", "Performance"]
            ... )
            {
                'perspectives': [
                    AgentPerspective(agent_type=PESSIMIST, ...),
                    AgentPerspective(agent_type=OPTIMIST, ...),
                    ...
                ],
                'consensus': 'Implement GPU caching with CPU fallback',
                'confidence': 85,
                'risks': [...],
                'opportunities': [...],
                'next_steps': [...]
            }
        """
        pass

    def get_agent_perspective(self, agent_type: str,
                             problem_statement: str,
                             context: Optional[Dict[str, Any]] = None
                             ) -> Dict[str, Any]:
        """
        Get perspective from a single agent

        Args:
            agent_type: Agent type (pessimist, optimist, engineer,
                       researcher, devil_advocate)
            problem_statement: Problem to analyze
            context: Optional context

        Returns:
            Dictionary with agent analysis

        Raises:
            ValueError: If agent_type is invalid

        Example:
            >>> reasoner.get_agent_perspective(
            ...     agent_type='pessimist',
            ...     problem_statement='Should we adopt this new technology?'
            ... )
        """
        pass

    def compare_alternatives(self, alternatives: List[Dict[str, Any]],
                            criteria: Optional[List[str]] = None
                            ) -> Dict[str, Any]:
        """
        Compare multiple alternatives using multi-agent reasoning

        Args:
            alternatives: List of alternatives to compare
            criteria: Optional evaluation criteria

        Returns:
            Comparison matrix with scores and recommendations

        Example:
            >>> reasoner.compare_alternatives([
            ...     {'option': 'GPU Caching', 'pros': [...], 'cons': [...]},
            ...     {'option': 'CPU Only', 'pros': [...], 'cons': [...]}
            ... ])
        """
        pass
```

#### `Evidence`

Represents supporting or opposing evidence.

```python
@dataclass
class Evidence:
    """
    Represents evidence for or against a position

    Attributes:
        claim: The evidence claim
        supporting: True if supports position, False if against
        confidence: Confidence level (0.0-1.0)
        reasoning: Detailed reasoning
        source: Optional source reference
        weight: Evidence weight (default: 1.0)
    """
    claim: str
    supporting: bool
    confidence: float  # 0.0-1.0
    reasoning: str
    source: Optional[str] = None
    weight: float = 1.0
```

#### `AgentPerspective`

Perspective from a single reasoning agent.

```python
@dataclass
class AgentPerspective:
    """
    Perspective from a single agent

    Attributes:
        agent_type: Type of agent (AgentType enum)
        position: Agent's position on the problem
        evidence_for: List of supporting evidence
        evidence_against: List of opposing evidence
        confidence: Overall confidence (0.0-1.0)
        recommendation: Agent's recommendation
        key_insights: Key insights from analysis
    """
    agent_type: AgentType
    position: str
    evidence_for: List[Evidence] = field(default_factory=list)
    evidence_against: List[Evidence] = field(default_factory=list)
    confidence: float = 0.0
    recommendation: str = ""
    key_insights: List[str] = field(default_factory=list)
```

#### Agent Types

```python
class AgentType(Enum):
    """Types of reasoning agents"""
    PESSIMIST = "pessimist"
    OPTIMIST = "optimist"
    ENGINEER = "engineer"
    RESEARCHER = "researcher"
    DEVIL_ADVOCATE = "devil_advocate"
```

**Agent Characteristics:**

| Agent | Focus | Tone | Role |
|-------|-------|------|------|
| **Pessimist** | Risk minimization | Cautious | Identifies worst-case scenarios |
| **Optimist** | Opportunity maximization | Encouraging | Highlights best-case potential |
| **Engineer** | Implementation feasibility | Practical | Assesses technical viability |
| **Researcher** | Evidence and precedent | Academic | References industry standards |
| **Devil's Advocate** | Assumption testing | Questioning | Challenges fundamental premises |

---

## Discipline Mapper API

### Overview

The Discipline Mapper dynamically loads and indexes all 1,300+ discipline modules.

### Singleton Access

```python
from bob_ai_discipline_mapper import get_discipline_mapper

mapper = get_discipline_mapper()  # Thread-safe singleton
```

### Key Classes

#### `DisciplineModuleMapper`

Maps and indexes all discipline modules.

```python
class DisciplineModuleMapper:
    """
    Maps and indexes all discipline modules across 12 tiers

    Tiers:
        1: Music & Sound (5 modules)
        2: External AI Integration (4 modules)
        3: Ethics & AI Safety (1+ modules)
        4: Business & Economics (1+ modules)
        5: Science & Research (1+ modules)
        6: Healthcare & Medicine (1+ modules)
        7: Law & Governance (1+ modules)
        8: Arts & Humanities (1+ modules)
        9: Technology & Engineering (1+ modules)
        10: Education & Learning (1+ modules)
        11: Social & Behavioral (1+ modules)
        12: Environment & Sustainability (1+ modules)
    """

    def __init__(self):
        """Initialize mapper and load all modules"""
        pass

    def load_module(self, module_name: str) -> Any:
        """
        Load a specific discipline module

        Args:
            module_name: Module name (e.g., "bob_ai_v9_music_composition")

        Returns:
            Loaded module object

        Raises:
            ImportError: If module not found
            ModuleNotFoundError: If dependencies missing

        Example:
            >>> mapper.load_module("bob_ai_v9_music_composition")
            <module 'bob_ai_v9_music_composition' ...>
        """
        pass

    def get_all_disciplines(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all loaded discipline modules

        Returns:
            Dictionary mapping {discipline_name: module_metadata}

        Example:
            >>> all_disciplines = mapper.get_all_disciplines()
            >>> list(all_disciplines.keys())
            ['Music Composition', 'Music History', 'Music Performance', ...]
        """
        pass

    def get_disciplines_by_tier(self, tier: int) -> List[str]:
        """
        Get all disciplines in a specific tier

        Args:
            tier: Tier number (1-12)

        Returns:
            List of discipline names in that tier

        Example:
            >>> mapper.get_disciplines_by_tier(tier=1)
            ['Music Composition', 'Music History', 'Music Performance',
             'Music Production', 'Music Education']
        """
        pass

    def search_disciplines(self, query: str) -> List[Tuple[str, float]]:
        """
        Search for disciplines by name or keywords

        Args:
            query: Search query

        Returns:
            List of (discipline_name, relevance_score) tuples

        Example:
            >>> mapper.search_disciplines("music theory")
            [('Music Theory', 0.95), ('Music Composition', 0.82), ...]
        """
        pass

    def get_discipline_knowledge(self, discipline: str) -> Dict[str, Any]:
        """
        Get knowledge base for a specific discipline

        Args:
            discipline: Discipline name

        Returns:
            Knowledge dictionary with all items for discipline

        Raises:
            ValueError: If discipline not found

        Example:
            >>> kb = mapper.get_discipline_knowledge("Music Composition")
            >>> len(kb['items'])
            250
        """
        pass

    def get_mapper_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about loaded modules

        Returns:
            Dictionary with {total_modules, total_items, tier_breakdown,
                           modules_by_tier, load_status}

        Example:
            >>> mapper.get_mapper_statistics()
            {
                'total_modules': 40,
                'total_items': 17030,
                'tier_breakdown': {1: 5, 2: 4, 3: 1, ...},
                'modules_by_tier': {...},
                'load_status': 'all_loaded'
            }
        """
        pass
```

---

## Integration Hub API

### Overview

The Integration Hub provides a unified interface coordinating all components.

### Singleton Access

```python
from bob_ai_integration_hub import get_integration_hub

hub = get_integration_hub()  # Thread-safe singleton
```

### Key Classes

#### `IntegrationHub`

Unified interface for the entire v9.0 system.

```python
class IntegrationHub:
    """
    Central coordination hub for all BOB AI v9.0 components

    Coordinates:
    - Knowledge Graph for relationship mapping
    - Multi-Agent Reasoner for decision analysis
    - Discipline Mapper for module management
    - Recommendation Engine for suggestions
    """

    def __init__(self):
        """Initialize hub with all components"""
        pass

    def query_knowledge(self, query: str,
                       context: Optional[str] = None,
                       limit: int = 10) -> QueryResult:
        """
        Query knowledge across all disciplines

        Args:
            query: Knowledge query
            context: Optional context for disambiguation
            limit: Maximum number of results

        Returns:
            QueryResult with relevant disciplines and recommendations

        Example:
            >>> hub = get_integration_hub()
            >>> result = hub.query_knowledge(
            ...     query="How do I improve my composition skills?",
            ...     context="classical music",
            ...     limit=5
            ... )
            >>> result.relevant_disciplines
            [('Music Composition', 0.95), ('Music Theory', 0.92), ...]
            >>> result.recommendations
            ['Study harmonic theory', 'Practice orchestration', ...]
        """
        pass

    def get_learning_recommendation(self, current_disciplines: List[str],
                                   learning_goal: str,
                                   max_steps: int = 5) -> LearningPathRecommendation:
        """
        Get recommended learning path

        Args:
            current_disciplines: Disciplines already known
            learning_goal: Target discipline or capability
            max_steps: Maximum steps in path

        Returns:
            Learning path recommendation with progression steps

        Example:
            >>> hub.get_learning_recommendation(
            ...     current_disciplines=['Music Theory'],
            ...     learning_goal='Film Scoring',
            ...     max_steps=5
            ... )
            {
                'path': ['Music Theory', 'Music Composition', 'Orchestration',
                        'Film Music', 'Film Scoring'],
                'estimated_duration': '40 hours',
                'key_milestones': [...]
            }
        """
        pass

    def find_complementary_disciplines(self, discipline: str,
                                      limit: int = 5) -> List[Tuple[str, str]]:
        """
        Find disciplines that complement a given one

        Args:
            discipline: Reference discipline
            limit: Maximum results

        Returns:
            List of (discipline_name, relationship_type) tuples

        Example:
            >>> hub.find_complementary_disciplines("Music Composition")
            [
                ('Music History', 'foundation'),
                ('Orchestration', 'specialization'),
                ('Music Technology', 'application'),
                ...
            ]
        """
        pass

    def search_knowledge(self, query: str,
                        disciplines: Optional[List[str]] = None,
                        limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for specific knowledge items

        Args:
            query: Search query
            disciplines: Optional list to limit search
            limit: Maximum results

        Returns:
            List of knowledge items matching query

        Example:
            >>> hub.search_knowledge("harmony progression")
            [
                {'item': 'I-IV-V-I progression', 'discipline': 'Music Theory'},
                {'item': 'functional harmony', 'discipline': 'Music Composition'},
                ...
            ]
        """
        pass

    def reason_about_problem(self, problem: str,
                            disciplines: Optional[List[str]] = None,
                            return_consensus: bool = True) -> Dict[str, Any]:
        """
        Multi-agent analysis of a problem

        Args:
            problem: Problem statement
            disciplines: Disciplines to apply
            return_consensus: Whether to return consensus

        Returns:
            Analysis with perspectives and recommendations

        Example:
            >>> hub.reason_about_problem(
            ...     "Should I pursue film scoring or composition as a career?",
            ...     disciplines=['Music Composition', 'Film Scoring', 'Career Planning']
            ... )
            {
                'perspectives': [5 AgentPerspective objects],
                'consensus': 'Pursue film scoring with strong composition foundation',
                'confidence': 78,
                'reasoning': '...'
            }
        """
        pass

    def get_hub_status(self) -> Dict[str, Any]:
        """
        Get status of all hub components

        Returns:
            Dictionary with component status, statistics, health indicators

        Example:
            >>> hub.get_hub_status()
            {
                'operational': True,
                'components': {
                    'knowledge_graph': {'status': 'ready', 'nodes': 1300, ...},
                    'reasoner': {'status': 'ready', 'agents': 5, ...},
                    'mapper': {'status': 'ready', 'modules': 40, ...}
                },
                'performance': {
                    'avg_query_time': 120,  # ms
                    'avg_reasoning_time': 800,  # ms
                    'cache_hits': 0.75
                }
            }
        """
        pass
```

#### `QueryResult`

Result of a knowledge query.

```python
@dataclass
class QueryResult:
    """
    Result of a knowledge query

    Attributes:
        query: Original query string
        relevant_disciplines: List of (discipline_name, confidence) tuples
        recommendations: List of recommended next steps
        multi_agent_analysis: Optional analysis from reasoner
        learning_paths: Optional learning paths to goals
    """
    query: str
    relevant_disciplines: List[Tuple[str, float]]
    recommendations: List[str]
    multi_agent_analysis: Optional[Dict[str, Any]] = None
    learning_paths: Optional[List[List[str]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        pass
```

#### `LearningPathRecommendation`

Recommended learning path.

```python
@dataclass
class LearningPathRecommendation:
    """
    Recommended learning path

    Attributes:
        path: List of disciplines in learning order
        estimated_duration: Total time estimate (hours)
        key_milestones: Milestones along the path
        prerequisites: Prerequisites for the goal
        resources: Recommended resources per step
    """
    path: List[str]
    estimated_duration: float
    key_milestones: List[str]
    prerequisites: List[str]
    resources: Optional[Dict[str, List[str]]] = None
```

---

## Data Models

### Enums

```python
class RelationshipType(Enum):
    """Types of relationships between disciplines"""
    PREREQUISITE = "prerequisite"        # B requires knowledge of A
    COMPLEMENTARY = "complementary"      # A and B enhance each other
    RELATED = "related"                  # A and B are related
    SPECIALIZATION = "specialization"    # B specializes A
    APPLICATION = "application"          # B applies knowledge from A
    FOUNDATION = "foundation"            # A is foundation for B

class AgentType(Enum):
    """Types of reasoning agents"""
    PESSIMIST = "pessimist"
    OPTIMIST = "optimist"
    ENGINEER = "engineer"
    RESEARCHER = "researcher"
    DEVIL_ADVOCATE = "devil_advocate"
```

### Dataclasses

See sections above for complete dataclass definitions:

- `DisciplineNode`
- `LearningPath`
- `Evidence`
- `AgentPerspective`
- `QueryResult`
- `LearningPathRecommendation`

---

## Error Handling

### Exception Hierarchy

```python
class BOBAIException(Exception):
    """Base exception for BOB AI errors"""
    pass

class DisciplineNotFoundError(BOBAIException):
    """Raised when discipline not found"""
    pass

class ModuleLoadError(BOBAIException):
    """Raised when module fails to load"""
    pass

class ReasoningError(BOBAIException):
    """Raised when reasoning fails"""
    pass

class PathNotFoundError(BOBAIException):
    """Raised when no path exists between disciplines"""
    pass
```

### Error Handling Patterns

```python
# Example 1: Handling discipline not found
from bob_ai_knowledge_graph import get_knowledge_graph, DisciplineNotFoundError

kg = get_knowledge_graph()
try:
    info = kg.get_discipline_info("Nonexistent Discipline")
except DisciplineNotFoundError:
    print("Discipline not found in knowledge base")

# Example 2: Handling module load errors
from bob_ai_discipline_mapper import get_discipline_mapper, ModuleLoadError

mapper = get_discipline_mapper()
try:
    module = mapper.load_module("bob_ai_v9_invalid_module")
except ModuleLoadError as e:
    print(f"Failed to load module: {e}")

# Example 3: Handling no path errors
try:
    path = kg.find_learning_path("Music", "Quantum Physics")
except PathNotFoundError:
    print("No learning path exists between these disciplines")
```

---

## Examples

### Example 1: Simple Query

```python
from bob_ai_integration_hub import get_integration_hub

hub = get_integration_hub()

# Query knowledge
result = hub.query_knowledge("What are the basics of music composition?")

print("Query:", result.query)
print("Relevant disciplines:")
for discipline, confidence in result.relevant_disciplines:
    print(f"  - {discipline} (confidence: {confidence:.0%})")

print("\nRecommendations:")
for rec in result.recommendations:
    print(f"  - {rec}")
```

**Output:**

```
Query: What are the basics of music composition?
Relevant disciplines:
  - Music Composition (confidence: 95%)
  - Music Theory (confidence: 92%)
  - Harmony (confidence: 88%)
  - Orchestration (confidence: 75%)

Recommendations:
  - Start with music theory fundamentals
  - Study harmonic progressions
  - Practice voice leading
  - Learn orchestration techniques
```

### Example 2: Learning Path

```python
# Get learning path recommendation
rec = hub.get_learning_recommendation(
    current_disciplines=["Music Theory"],
    learning_goal="Film Scoring",
    max_steps=5
)

print("Learning path to Film Scoring:")
for i, discipline in enumerate(rec.path, 1):
    print(f"  {i}. {discipline}")

print(f"\nEstimated duration: {rec.estimated_duration}")
print("\nKey milestones:")
for milestone in rec.key_milestones:
    print(f"  ✓ {milestone}")
```

### Example 3: Multi-Agent Reasoning

```python
# Analyze a decision with multiple perspectives
analysis = hub.reason_about_problem(
    problem="Should I specialize in classical composition or film scoring?",
    disciplines=["Music Composition", "Film Scoring", "Career Planning"]
)

print("Decision analysis:")
print(f"Confidence: {analysis['confidence']}%\n")

print("Perspectives:")
for perspective in analysis['perspectives']:
    print(f"\n{perspective.agent_type.value.upper()}:")
    print(f"  Position: {perspective.position}")
    print(f"  Confidence: {perspective.confidence:.0%}")
    print(f"  Recommendation: {perspective.recommendation}")

print(f"\nConsensus: {analysis['consensus']}")
```

### Example 4: Finding Complementary Disciplines

```python
# Find disciplines that complement composition
complementary = hub.find_complementary_disciplines(
    discipline="Music Composition",
    limit=5
)

print("Disciplines that complement Music Composition:")
for discipline, relationship in complementary:
    print(f"  - {discipline} ({relationship})")
```

### Example 5: Knowledge Search

```python
# Search for specific knowledge items
results = hub.search_knowledge(
    query="harmonic progressions",
    limit=10
)

print(f"Found {len(results)} results for 'harmonic progressions':")
for result in results:
    print(f"\n  • {result['item']}")
    print(f"    Discipline: {result['discipline']}")
    print(f"    Category: {result.get('category', 'N/A')}")
```

---

## Best Practices

### 1. Use Singleton Pattern

Always use getter functions for component access (thread-safe):

```python
# ✅ Good
from bob_ai_knowledge_graph import get_knowledge_graph
kg = get_knowledge_graph()

# ❌ Avoid
from bob_ai_knowledge_graph import KnowledgeGraph
kg = KnowledgeGraph()  # Creates new instance each time
```

### 2. Handle Exceptions

Always wrap external API calls in try-except:

```python
# ✅ Good
try:
    result = hub.query_knowledge(query)
except Exception as e:
    logger.error(f"Query failed: {e}")
    return fallback_result()

# ❌ Avoid
result = hub.query_knowledge(query)  # Can crash silently
```

### 3. Use Type Hints

All methods support type hints for IDE assistance:

```python
# ✅ Good
result: QueryResult = hub.query_knowledge("...")
disciplines: List[str] = kg.search_by_keywords([...])

# ❌ Avoid
result = hub.query_knowledge("...")  # Type unknown
```

### 4. Cache Results

Query results can be cached for repeated queries:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def query_cached(query: str) -> QueryResult:
    hub = get_integration_hub()
    return hub.query_knowledge(query)
```

### 5. Monitor Performance

Check hub status for performance metrics:

```python
status = hub.get_hub_status()
if status['performance']['avg_query_time'] > 500:
    logger.warning("Query performance degraded")
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 9.0.0 | Oct 27, 2025 | Initial release with 1,300+ disciplines |
| 8.0.0 | Oct 26, 2025 | 14 disciplines, basic integration |
| 7.0.0 | Oct 25, 2025 | Music modules only |

---

## Support & Troubleshooting

### Common Issues

**Issue: Module not found error**

```
ModuleNotFoundError: No module named 'bob_ai_v9_music_composition'
```

**Solution:** Ensure all tier modules are in the Python path and dependencies are installed.

**Issue: Query timeout**

```
TimeoutError: Query took longer than 1000ms
```

**Solution:** Reduce the number of disciplines or use a narrower search scope.

**Issue: Memory usage high**

```
MemoryError: Unable to allocate memory
```

**Solution:** Check `get_hub_status()` for memory metrics; consider clearing cache with `gc.collect()`.

---

**API Reference Version:** 9.0.0
**Last Updated:** October 27, 2025
**Status:** ✅ Production Ready
