"""
BOB AI v7 - Semantic Relationship Engine
Implements 15+ semantic relationship types for connecting knowledge items
Enables rich semantic linking between concepts

Supported relationship types:
- is_a: Specialization/inheritance (A is a type of B)
- part_of: Composition (A is part of B)
- depends_on: Dependency (A depends on B)
- used_for: Purpose/use case (A is used for B)
- specializes: Inheritance reversal (A specializes B)
- contradicts: Opposition/conflict (A contradicts B)
- implies: Logical implication (A implies B)
- enables: Causation (A enables B)
- related_to: General relation (A is related to B)
- similar_to: Similarity/analogy (A is similar to B)
- opposite_of: Antonyms (A is opposite of B)
- prerequisite: Learning order (A is prerequisite for B)
- synonym: Naming variation (A is synonym for B)
- combines_with: Aggregation (A combines with B)
- template_for: Instantiation (A is template for B)

Status: Phase 3 - Semantic Relationship Infrastructure
"""

import logging
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json
from collections import defaultdict

logger = logging.getLogger(__name__)


class RelationshipType(Enum):
    """All supported semantic relationship types"""
    IS_A = "is_a"
    PART_OF = "part_of"
    DEPENDS_ON = "depends_on"
    USED_FOR = "used_for"
    SPECIALIZES = "specializes"
    CONTRADICTS = "contradicts"
    IMPLIES = "implies"
    ENABLES = "enables"
    RELATED_TO = "related_to"
    SIMILAR_TO = "similar_to"
    OPPOSITE_OF = "opposite_of"
    PREREQUISITE = "prerequisite"
    SYNONYM = "synonym"
    COMBINES_WITH = "combines_with"
    TEMPLATE_FOR = "template_for"


class RelationshipStrength(Enum):
    """Relationship confidence/strength"""
    WEAK = 0.3
    MODERATE = 0.6
    STRONG = 0.8
    VERY_STRONG = 1.0


@dataclass
class SemanticRelationship:
    """Represents a single semantic relationship between two knowledge items"""
    source_id: str          # ID of source node
    target_id: str          # ID of target node
    rel_type: RelationshipType  # Type of relationship
    strength: float         # Confidence 0.0-1.0
    description: str = ""   # Optional description
    created_by: str = "system"  # Who created this relationship
    created_date: datetime = field(default_factory=datetime.utcnow)
    verified: bool = False  # Is relationship verified?

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'source_id': self.source_id,
            'target_id': self.target_id,
            'rel_type': self.rel_type.value,
            'strength': self.strength,
            'description': self.description,
            'created_by': self.created_by,
            'created_date': self.created_date.isoformat(),
            'verified': self.verified
        }

    def get_inverse_type(self) -> Optional[RelationshipType]:
        """Get the inverse relationship type for bidirectional linking"""
        inverses = {
            RelationshipType.IS_A: RelationshipType.SPECIALIZES,
            RelationshipType.PART_OF: None,  # No direct inverse
            RelationshipType.DEPENDS_ON: None,
            RelationshipType.USED_FOR: None,
            RelationshipType.SPECIALIZES: RelationshipType.IS_A,
            RelationshipType.CONTRADICTS: RelationshipType.CONTRADICTS,
            RelationshipType.IMPLIES: None,
            RelationshipType.ENABLES: None,
            RelationshipType.RELATED_TO: RelationshipType.RELATED_TO,
            RelationshipType.SIMILAR_TO: RelationshipType.SIMILAR_TO,
            RelationshipType.OPPOSITE_OF: RelationshipType.OPPOSITE_OF,
            RelationshipType.PREREQUISITE: None,
            RelationshipType.SYNONYM: RelationshipType.SYNONYM,
            RelationshipType.COMBINES_WITH: RelationshipType.COMBINES_WITH,
            RelationshipType.TEMPLATE_FOR: None,
        }
        return inverses.get(self.rel_type)


class RelationshipValidator:
    """Validates semantic relationships"""

    # Rules for valid relationships between types
    VALIDITY_RULES = {
        'technology': {
            'business': [RelationshipType.ENABLES, RelationshipType.USED_FOR],
            'science': [RelationshipType.DEPENDS_ON, RelationshipType.RELATED_TO],
        },
        'science': {
            'technology': [RelationshipType.USED_FOR],
            'history': [RelationshipType.RELATED_TO],
        }
    }

    @staticmethod
    def validate_relationship(
        rel: SemanticRelationship,
        source_domain: str,
        target_domain: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if relationship is allowed between domains
        Returns (is_valid, error_message)
        """
        if rel.strength < 0.0 or rel.strength > 1.0:
            return False, "Relationship strength must be between 0.0 and 1.0"

        if rel.source_id == rel.target_id:
            return False, "Cannot create self-referential relationships"

        # Check domain compatibility rules if they exist
        if source_domain in RelationshipValidator.VALIDITY_RULES:
            domain_rules = RelationshipValidator.VALIDITY_RULES[source_domain]
            if target_domain in domain_rules:
                allowed_types = domain_rules[target_domain]
                if rel.rel_type not in allowed_types:
                    return False, f"Relationship type {rel.rel_type.value} not allowed between {source_domain} and {target_domain}"

        return True, None


class SemanticLinkManager:
    """Manages semantic relationships in knowledge graph"""

    def __init__(self):
        """Initialize link manager"""
        self.relationships: Dict[str, List[SemanticRelationship]] = defaultdict(list)
        self.reverse_index: Dict[str, List[SemanticRelationship]] = defaultdict(list)
        self.relationship_count: Dict[RelationshipType, int] = {rel_type: 0 for rel_type in RelationshipType}
        self.cycle_cache: Dict[str, Set[str]] = {}
        logger.info("SemanticLinkManager initialized")

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        rel_type: RelationshipType,
        strength: float = 0.8,
        source_domain: str = "unknown",
        target_domain: str = "unknown",
        bidirectional: bool = True,
        description: str = ""
    ) -> Tuple[bool, Optional[str]]:
        """
        Add semantic relationship

        Returns: (success, error_message)
        """
        # Validate
        rel = SemanticRelationship(
            source_id=source_id,
            target_id=target_id,
            rel_type=rel_type,
            strength=strength,
            description=description
        )

        is_valid, error = RelationshipValidator.validate_relationship(rel, source_domain, target_domain)
        if not is_valid:
            logger.warning(f"Invalid relationship: {error}")
            return False, error

        # Check for cycles in depends_on relationships
        if rel_type == RelationshipType.DEPENDS_ON or rel_type == RelationshipType.PREREQUISITE:
            if self._would_create_cycle(source_id, target_id):
                error = "Adding this relationship would create a cycle"
                logger.warning(error)
                return False, error

        # Add forward relationship
        self.relationships[source_id].append(rel)
        self.reverse_index[target_id].append(rel)
        self.relationship_count[rel_type] += 1

        # Invalidate cycle cache
        self.cycle_cache.clear()

        logger.debug(f"Relationship added: {source_id} --[{rel_type.value}]--> {target_id}")

        # Add bidirectional inverse relationship if applicable
        if bidirectional:
            inverse_type = rel.get_inverse_type()
            if inverse_type:
                inverse_rel = SemanticRelationship(
                    source_id=target_id,
                    target_id=source_id,
                    rel_type=inverse_type,
                    strength=strength,
                    description=f"Inverse of: {description}",
                    verified=rel.verified
                )
                self.relationships[target_id].append(inverse_rel)
                self.reverse_index[source_id].append(inverse_rel)
                self.relationship_count[inverse_type] += 1

        return True, None

    def get_relationships(
        self,
        node_id: str,
        rel_type: Optional[RelationshipType] = None,
        direction: str = "outgoing"  # "outgoing", "incoming", "both"
    ) -> List[SemanticRelationship]:
        """Get relationships for a node"""
        relationships = []

        if direction in ["outgoing", "both"]:
            relationships.extend(self.relationships.get(node_id, []))

        if direction in ["incoming", "both"]:
            relationships.extend(self.reverse_index.get(node_id, []))

        # Filter by type if specified
        if rel_type:
            relationships = [r for r in relationships if r.rel_type == rel_type]

        return relationships

    def get_related_nodes(
        self,
        node_id: str,
        rel_type: Optional[RelationshipType] = None,
        max_depth: int = 1,
        direction: str = "outgoing"
    ) -> Set[str]:
        """Get all nodes related to given node up to max_depth"""
        visited = set()
        frontier = {node_id}

        for _ in range(max_depth):
            next_frontier = set()

            for current_id in frontier:
                if current_id in visited:
                    continue

                visited.add(current_id)

                for rel in self.get_relationships(current_id, rel_type, direction):
                    if rel.target_id not in visited:
                        next_frontier.add(rel.target_id)

            frontier = next_frontier

        # Remove the starting node
        visited.discard(node_id)
        return visited

    def find_paths(
        self,
        source_id: str,
        target_id: str,
        rel_type: Optional[RelationshipType] = None,
        max_depth: int = 5
    ) -> List[List[SemanticRelationship]]:
        """Find all paths between two nodes"""
        paths = []

        def dfs(current_id: str, target: str, path: List[SemanticRelationship], visited: Set[str], depth: int):
            if depth > max_depth or current_id in visited:
                return

            if current_id == target:
                paths.append(path.copy())
                return

            visited.add(current_id)

            for rel in self.get_relationships(current_id, rel_type):
                if rel.target_id not in visited:
                    dfs(rel.target_id, target, path + [rel], visited.copy(), depth + 1)

        dfs(source_id, target_id, [], set(), 0)
        return paths

    def get_shared_relationships(
        self,
        node1_id: str,
        node2_id: str
    ) -> List[Tuple[SemanticRelationship, SemanticRelationship]]:
        """Find shared relationship patterns between two nodes"""
        shared = []

        node1_rels = {r.target_id: r for r in self.get_relationships(node1_id)}
        node2_rels = {r.target_id: r for r in self.get_relationships(node2_id)}

        for target_id in set(node1_rels.keys()) & set(node2_rels.keys()):
            shared.append((node1_rels[target_id], node2_rels[target_id]))

        return shared

    def _would_create_cycle(self, source_id: str, target_id: str) -> bool:
        """Check if adding relationship would create a cycle"""
        # Can we reach source from target?
        visited = set()
        frontier = {target_id}

        while frontier:
            current = frontier.pop()
            if current == source_id:
                return True

            if current in visited:
                continue

            visited.add(current)

            for rel in self.get_relationships(current):
                if rel.target_id not in visited:
                    frontier.add(rel.target_id)

        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about relationships"""
        all_rels = []
        for rels_list in self.relationships.values():
            all_rels.extend(rels_list)

        strength_sum = sum(r.strength for r in all_rels)
        avg_strength = strength_sum / len(all_rels) if all_rels else 0.0

        verified_count = sum(1 for r in all_rels if r.verified)

        # Nodes involved
        nodes = set()
        for rels_list in self.relationships.values():
            for rel in rels_list:
                nodes.add(rel.source_id)
                nodes.add(rel.target_id)

        return {
            'total_relationships': len(all_rels),
            'relationship_types': {rel_type.value: count for rel_type, count in self.relationship_count.items() if count > 0},
            'average_strength': avg_strength,
            'verified_count': verified_count,
            'verified_percentage': (verified_count / len(all_rels) * 100) if all_rels else 0.0,
            'unique_nodes': len(nodes),
            'timestamp': datetime.utcnow().isoformat()
        }

    def export_graph_json(self) -> Dict[str, Any]:
        """Export graph to JSON format"""
        nodes = set()
        edges = []

        for source_id, rels in self.relationships.items():
            nodes.add(source_id)
            for rel in rels:
                nodes.add(rel.target_id)
                edges.append({
                    'source': rel.source_id,
                    'target': rel.target_id,
                    'type': rel.rel_type.value,
                    'strength': rel.strength,
                    'verified': rel.verified
                })

        return {
            'nodes': list(nodes),
            'edges': edges,
            'stats': self.get_statistics()
        }

    def export_csv(self) -> str:
        """Export relationships to CSV format"""
        csv_lines = ['source_id,target_id,rel_type,strength,description,verified']

        for source_id, rels in self.relationships.items():
            for rel in rels:
                csv_lines.append(
                    f'{rel.source_id},{rel.target_id},{rel.rel_type.value},{rel.strength},'
                    f'"{rel.description}",{rel.verified}'
                )

        return '\n'.join(csv_lines)


def demo_semantic_relationships():
    """Demonstration of semantic relationship functionality"""
    print("\nBOB AI v7 - Semantic Relationship Engine Demo")
    print("=" * 70)
    print()

    # Initialize manager
    manager = SemanticLinkManager()

    # Create sample relationships
    print("Adding sample semantic relationships...")
    print()

    # Add relationships
    relationships_to_add = [
        ('machine_learning', 'neural_networks', RelationshipType.SPECIALIZES, 0.9),
        ('neural_networks', 'deep_learning', RelationshipType.IS_A, 0.85),
        ('deep_learning', 'machine_learning', RelationshipType.PART_OF, 0.9),
        ('machine_learning', 'artificial_intelligence', RelationshipType.PART_OF, 0.95),
        ('reinforcement_learning', 'machine_learning', RelationshipType.PART_OF, 0.85),
        ('supervised_learning', 'machine_learning', RelationshipType.PART_OF, 0.90),
        ('unsupervised_learning', 'machine_learning', RelationshipType.PART_OF, 0.88),
        ('nlp', 'deep_learning', RelationshipType.USED_FOR, 0.85),
        ('computer_vision', 'deep_learning', RelationshipType.USED_FOR, 0.92),
        ('nlp', 'neural_networks', RelationshipType.DEPENDS_ON, 0.75),
    ]

    for source, target, rel_type, strength in relationships_to_add:
        success, error = manager.add_relationship(
            source, target, rel_type, strength,
            bidirectional=True
        )
        status = "✓" if success else "✗"
        print(f"  {status} {source} --[{rel_type.value}]--> {target} ({strength})")

    print()
    print("Statistics:")
    stats = manager.get_statistics()
    print(f"  Total Relationships: {stats['total_relationships']}")
    print(f"  Average Strength: {stats['average_strength']:.3f}")
    print(f"  Unique Nodes: {stats['unique_nodes']}")
    print()

    print("Relationship Types:")
    for rel_type, count in stats['relationship_types'].items():
        print(f"  {rel_type}: {count}")
    print()

    # Find related nodes
    print("Finding related nodes to 'machine_learning'...")
    related = manager.get_related_nodes('machine_learning', max_depth=2)
    print(f"  Related nodes ({len(related)}): {', '.join(sorted(related))}")
    print()

    # Find paths
    print("Finding paths between 'nlp' and 'artificial_intelligence'...")
    paths = manager.find_paths('nlp', 'artificial_intelligence', max_depth=4)
    for i, path in enumerate(paths, 1):
        path_str = " → ".join([f"{r.source_id}[{r.rel_type.value}]" for r in path] + [path[-1].target_id if path else ""])
        print(f"  Path {i}: {path_str}")
    print()

    # Export
    print("Exporting graph to JSON format...")
    graph_data = manager.export_graph_json()
    print(f"  Nodes: {len(graph_data['nodes'])}")
    print(f"  Edges: {len(graph_data['edges'])}")


if __name__ == "__main__":
    demo_semantic_relationships()
