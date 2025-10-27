"""
Bob AI v7 - Knowledge Graph Core Infrastructure

Implements the foundation for structured, disciplined knowledge management:
- KnowledgeNode: Base entity for all knowledge items
- KnowledgeMetadata: Rich metadata framework with quality scoring
- Relationship system: 15+ semantic relationship types
- Difficulty/Scope classification system

Status: Phase 1 - Foundation Ready for Integration

Author: GitHub Copilot
Date: October 26, 2025
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS FOR CLASSIFICATION
# ============================================================================

class DifficultyLevel(Enum):
    """Knowledge difficulty assessment"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class KnowledgeScope(Enum):
    """Knowledge scope classification"""
    GENERAL = "general"
    SPECIALIZED = "specialized"
    NICHE = "niche"
    FOUNDATIONAL = "foundational"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Example:
    """Usage example for knowledge item"""
    label: str
    description: str
    context: str
    relevance: float = 1.0  # 0.0-1.0 scale


@dataclass
class Reference:
    """Reference source for knowledge item"""
    title: str
    url: Optional[str] = None
    source_type: str = "unknown"  # "wikipedia", "academic", "book", etc.
    retrieved_date: Optional[str] = None


@dataclass
class KnowledgeMetadata:
    """Rich metadata for knowledge items - drives quality scoring"""

    # Quality Metrics (0.0-1.0 scale)
    confidence: float = 0.8  # How confident we are this is correct
    precision: float = 0.8   # How precise/specific the knowledge is
    completeness: float = 0.8  # How complete the coverage is
    relevance: float = 0.8   # How relevant to domain
    currency_days: int = 30  # How many days since last update

    # Sourcing & Verification
    source: str = ""  # Where this knowledge came from
    references: List[Reference] = field(default_factory=list)
    reviewed_by: List[str] = field(default_factory=list)  # Expert reviewers
    verified: bool = False  # Has it been fact-checked?

    # Knowledge Structure
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    scope: KnowledgeScope = KnowledgeScope.GENERAL
    examples: List[Example] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)  # Node IDs
    use_cases: List[str] = field(default_factory=list)

    # Administrative
    deprecated: bool = False
    deprecation_reason: str = ""
    version: str = "1.0"
    contributors: List[str] = field(default_factory=list)
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_quality_score(self) -> float:
        """
        Calculate overall quality score using weighted formula.

        Formula:
            score = (0.25 × confidence) + (0.20 × precision) + (0.20 × completeness) +
                    (0.15 × relevance) + (0.10 × currency) + (0.05 × references) +
                    (0.05 × examples)

        Returns:
            float: Score from 0.0 (poor) to 1.0 (excellent)
        """
        # Currency score: 1.0 if updated today, declines over 365 days
        currency_score = max(0.0, 1.0 - (self.currency_days / 365.0))

        # Reference score: 1.0 if 3+ references, 0.3 if 1+, 0 otherwise
        ref_score = min(1.0, len(self.references) / 3.0)

        # Example score: 1.0 if 2+ examples, 0.5 if 1+, 0 otherwise
        example_score = min(1.0, len(self.examples) / 2.0)

        # Weighted calculation
        total_score = (
            0.25 * self.confidence +
            0.20 * self.precision +
            0.20 * self.completeness +
            0.15 * self.relevance +
            0.10 * currency_score +
            0.05 * ref_score +
            0.05 * example_score
        )

        return round(total_score, 4)

    def is_high_quality(self) -> bool:
        """Check if knowledge meets high-quality threshold (≥0.85)"""
        return self.get_quality_score() >= 0.85

    def is_verified(self) -> bool:
        """Check if knowledge is properly verified"""
        return (
            self.verified and
            len(self.references) > 0 and
            len(self.reviewed_by) > 0 and
            self.confidence >= 0.8
        )

    def get_recommendations(self) -> List[str]:
        """Get recommendations for improving quality"""
        recommendations = []

        if self.confidence < 0.8:
            recommendations.append("Increase confidence score (currently {})".format(self.confidence))

        if self.precision < 0.8:
            recommendations.append("Improve precision of definition")

        if self.completeness < 0.8:
            recommendations.append("Add more detail/examples for completeness")

        if len(self.references) == 0:
            recommendations.append("Add at least 1 reference")

        if len(self.examples) == 0:
            recommendations.append("Add usage examples")

        if not self.verified:
            recommendations.append("Get expert verification")

        if self.currency_days > 180:
            recommendations.append("Update outdated information")

        return recommendations

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "confidence": self.confidence,
            "precision": self.precision,
            "completeness": self.completeness,
            "relevance": self.relevance,
            "currency_days": self.currency_days,
            "quality_score": self.get_quality_score(),
            "is_high_quality": self.is_high_quality(),
            "is_verified": self.is_verified(),
            "source": self.source,
            "references": len(self.references),
            "reviewed_by": self.reviewed_by,
            "verified": self.verified,
            "difficulty": self.difficulty.value,
            "scope": self.scope.value,
            "examples": len(self.examples),
            "deprecated": self.deprecated,
            "version": self.version,
            "created_date": self.created_date,
            "last_updated": self.last_updated,
            "recommendations": self.get_recommendations(),
        }


# ============================================================================
# MAIN KNOWLEDGE NODE CLASS
# ============================================================================

class KnowledgeNode:
    """
    Core knowledge entity with rich relationships and metadata.

    Features:
    - Structured attributes and descriptions
    - Semantic relationships (15+ types)
    - Rich metadata with quality scoring
    - Full graph traversal support
    """

    # Valid relationship types
    VALID_RELATIONSHIPS = {
        "is_a",           # Specialization/inheritance
        "part_of",        # Composition
        "depends_on",     # Dependency
        "used_for",       # Purpose/use case
        "specializes",    # Inheritance reversal
        "contradicts",    # Opposition/conflict
        "implies",        # Logical implication
        "enables",        # Causation
        "related_to",     # General relation
        "similar_to",     # Similarity/analogy
        "opposite_of",    # Antonyms
        "prerequisite",   # Learning order
        "synonym",        # Naming variation
        "combines_with",  # Aggregation
        "template_for",   # Instantiation
    }

    def __init__(
        self,
        id: str,
        label: str,
        domain: str,
        description: str = "",
    ):
        """
        Initialize a knowledge node.

        Args:
            id: Unique identifier
            label: Human-readable label
            domain: Knowledge domain (e.g., "vehicles", "tools")
            description: Detailed description
        """
        self.id = id
        self.label = label
        self.domain = domain
        self.description = description

        # Structure
        self.attributes: Dict[str, Any] = {}
        self.metadata = KnowledgeMetadata()
        self.relationships: Dict[str, Set[str]] = {rel_type: set() for rel_type in self.VALID_RELATIONSHIPS}

    def add_relationship(self, rel_type: str, target_id: str) -> bool:
        """
        Add semantic relationship to another node.

        Args:
            rel_type: Relationship type (must be in VALID_RELATIONSHIPS)
            target_id: ID of target node

        Returns:
            bool: True if relationship added, False if invalid
        """
        if rel_type not in self.VALID_RELATIONSHIPS:
            logger.warning(f"Invalid relationship type: {rel_type}")
            return False

        self.relationships[rel_type].add(target_id)
        return True

    def remove_relationship(self, rel_type: str, target_id: str) -> bool:
        """Remove a relationship"""
        if rel_type not in self.VALID_RELATIONSHIPS:
            return False

        if target_id in self.relationships[rel_type]:
            self.relationships[rel_type].remove(target_id)
            return True

        return False

    def get_relationships(self, rel_type: Optional[str] = None) -> Dict[str, Set[str]]:
        """Get relationships, optionally filtered by type"""
        if rel_type:
            return {rel_type: self.relationships.get(rel_type, set())}
        return self.relationships

    def get_confidence(self) -> float:
        """Get confidence score from metadata"""
        return self.metadata.confidence

    def set_confidence(self, confidence: float) -> None:
        """Set confidence score (0.0-1.0)"""
        self.metadata.confidence = max(0.0, min(1.0, confidence))

    def add_attribute(self, key: str, value: Any) -> None:
        """Add or update an attribute"""
        self.attributes[key] = value

    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get an attribute value"""
        return self.attributes.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API/serialization"""
        return {
            "id": self.id,
            "label": self.label,
            "domain": self.domain,
            "description": self.description,
            "attributes": self.attributes,
            "confidence": self.get_confidence(),
            "metadata": self.metadata.to_dict(),
            "relationships": {
                rel_type: list(rel_ids) for rel_type, rel_ids in self.relationships.items()
                if rel_ids  # Only include non-empty relationships
            },
            "quality_score": self.metadata.get_quality_score(),
        }

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, default=str)

    def __repr__(self) -> str:
        """String representation"""
        quality = self.metadata.get_quality_score()
        return f"KnowledgeNode(id='{self.id}', label='{self.label}', domain='{self.domain}', quality={quality:.2f})"


# ============================================================================
# KNOWLEDGE GRAPH MANAGER
# ============================================================================

class KnowledgeGraphCore:
    """
    Core knowledge graph manager.

    Features:
    - Node creation and management
    - Relationship validation
    - Graph statistics
    - Quality reporting
    """

    def __init__(self):
        """Initialize knowledge graph"""
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.domain_index: Dict[str, Set[str]] = {}  # domain → node_ids
        logger.info("Knowledge graph core initialized")

    def add_node(self, node: KnowledgeNode) -> bool:
        """Add a node to the graph"""
        if node.id in self.nodes:
            logger.warning(f"Node {node.id} already exists")
            return False

        self.nodes[node.id] = node

        # Update domain index
        if node.domain not in self.domain_index:
            self.domain_index[node.domain] = set()
        self.domain_index[node.domain].add(node.id)

        logger.debug(f"Added node: {node.id}")
        return True

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get a node by ID"""
        return self.nodes.get(node_id)

    def get_nodes_by_domain(self, domain: str) -> List[KnowledgeNode]:
        """Get all nodes in a domain"""
        node_ids = self.domain_index.get(domain, set())
        return [self.nodes[nid] for nid in node_ids if nid in self.nodes]

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics"""
        total_nodes = len(self.nodes)
        total_relationships = sum(
            len(rel_ids)
            for node in self.nodes.values()
            for rel_ids in node.relationships.values()
        )
        avg_quality = (
            sum(node.metadata.get_quality_score() for node in self.nodes.values()) / total_nodes
            if total_nodes > 0
            else 0.0
        )

        high_quality_count = sum(
            1 for node in self.nodes.values()
            if node.metadata.is_high_quality()
        )

        return {
            "total_nodes": total_nodes,
            "total_relationships": total_relationships,
            "total_domains": len(self.domain_index),
            "average_quality_score": round(avg_quality, 4),
            "high_quality_count": high_quality_count,
            "high_quality_percentage": round((high_quality_count / total_nodes * 100) if total_nodes > 0 else 0, 2),
            "domains": {
                domain: len(node_ids)
                for domain, node_ids in self.domain_index.items()
            }
        }


# ============================================================================
# TEST & DEMONSTRATION
# ============================================================================

def demo_knowledge_graph():
    """Demonstrate knowledge graph functionality"""
    print("\n" + "="*70)
    print("BOB AI v7 - Knowledge Graph Core Demo")
    print("="*70 + "\n")

    # Create graph
    graph = KnowledgeGraphCore()

    # Create sample nodes
    node1 = KnowledgeNode(
        id="vehicle_car",
        label="Car",
        domain="vehicles",
        description="A car is a wheeled motor vehicle designed primarily for transportation on roads"
    )
    node1.metadata.confidence = 0.95
    node1.metadata.precision = 0.9
    node1.metadata.completeness = 0.85
    node1.metadata.relevance = 0.9
    node1.metadata.difficulty = DifficultyLevel.BEGINNER
    node1.metadata.scope = KnowledgeScope.GENERAL
    node1.add_attribute("wheels", 4)
    node1.add_attribute("seats", "1-8")

    node2 = KnowledgeNode(
        id="vehicle_sedan",
        label="Sedan",
        domain="vehicles",
        description="A sedan is a four-door passenger car with a separate trunk"
    )
    node2.metadata.confidence = 0.92
    node2.metadata.precision = 0.92
    node2.metadata.completeness = 0.88
    node2.metadata.relevance = 0.9
    node2.add_attribute("doors", 4)

    # Add relationships
    node2.add_relationship("is_a", "vehicle_car")
    node1.add_relationship("has_child", "vehicle_sedan")

    # Add to graph
    graph.add_node(node1)
    graph.add_node(node2)

    # Display results
    print(f"Node 1: {node1}")
    print(f"  Quality Score: {node1.metadata.get_quality_score()}")
    print(f"  Is High Quality: {node1.metadata.is_high_quality()}\n")

    print(f"Node 2: {node2}")
    print(f"  Quality Score: {node2.metadata.get_quality_score()}")
    print(f"  Is High Quality: {node2.metadata.is_high_quality()}\n")

    # Graph statistics
    stats = graph.get_statistics()
    print("Graph Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    demo_knowledge_graph()
