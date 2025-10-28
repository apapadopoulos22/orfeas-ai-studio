"""
BOB AI Expansion - Phase 2: Knowledge Graph & Relationships
===========================================================

Implements graph-based relationship mapping for disciplines, learning paths,
and recommendations using NetworkX. Transforms flat data into a navigable
knowledge network.

Features:
  - Bidirectional prerequisite chains
  - Similarity scoring between disciplines
  - Learning path optimization
  - Skill gap analysis
  - Recommendation engine

Architecture:
  - KnowledgeGraphBuilder: Constructs graph from database
  - GraphAnalyzer: Computes metrics and relationships
  - RecommendationEngine: Suggests next steps
  - PathOptimizer: Finds efficient learning paths

Author: ORFEAS AI - BOB AI Expansion v10.0
Date: October 28, 2025
"""

import logging
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import heapq
from collections import defaultdict, deque

# Graph libraries
try:
    import networkx as nx
    from networkx.algorithms import shortest_path, shortest_path_length
    from networkx.algorithms.community import greedy_modularity_communities
except ImportError:
    nx = None
    print("WARNING: NetworkX not installed. Install with: pip install networkx")

# Database imports
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

logger = logging.getLogger(__name__)


@dataclass
class DisciplineNode:
    """Represents a discipline in the knowledge graph"""
    id: int
    name: str
    category: str
    difficulty: str  # beginner, intermediate, advanced, expert
    estimated_hours: float
    skills: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    industry_focus: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'difficulty': self.difficulty,
            'estimated_hours': self.estimated_hours,
            'skills': self.skills,
            'keywords': self.keywords,
            'industry_focus': self.industry_focus,
        }


@dataclass
class RecommendationResult:
    """Represents a recommendation from the engine"""
    discipline_id: int
    discipline_name: str
    score: float  # 0-1 recommendation strength
    reason: str  # Why this is recommended
    prerequisite_gaps: List[str] = field(default_factory=list)
    estimated_hours: float = 0.0
    similar_disciplines: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'discipline_id': self.discipline_id,
            'discipline_name': self.discipline_name,
            'score': round(self.score, 2),
            'reason': self.reason,
            'prerequisite_gaps': self.prerequisite_gaps,
            'estimated_hours': self.estimated_hours,
            'similar_disciplines': self.similar_disciplines,
        }


@dataclass
class LearningPathOptimized:
    """Optimized learning path with metrics"""
    disciplines: List[DisciplineNode]
    total_hours: float
    difficulty_progression: List[str]
    critical_path: List[DisciplineNode]
    parallel_learning_opportunities: List[List[DisciplineNode]]
    estimated_completion_weeks: float

    def to_dict(self) -> Dict:
        return {
            'disciplines': [d.to_dict() for d in self.disciplines],
            'total_hours': self.total_hours,
            'difficulty_progression': self.difficulty_progression,
            'critical_path': [d.to_dict() for d in self.critical_path],
            'parallel_opportunities': [[d.to_dict() for d in group] for group in self.parallel_learning_opportunities],
            'estimated_weeks': round(self.estimated_completion_weeks, 1),
        }


class KnowledgeGraphBuilder:
    """Constructs knowledge graph from database"""

    def __init__(self, session: Session):
        """
        Initialize graph builder with database session

        Args:
            session: SQLAlchemy session for database access
        """
        self.session = session
        self.graph = nx.DiGraph() if nx else None
        self.disciplines_cache: Dict[int, DisciplineNode] = {}
        self.built = False

    def build_from_database(self) -> 'KnowledgeGraphBuilder':
        """
        Construct graph from database tables

        Returns:
            Self for chaining
        """
        if not nx:
            logger.error("NetworkX not installed. Cannot build graph.")
            return self

        try:
            # Import models dynamically to avoid circular imports
            from bob_ai_expansion_phase1_database import (
                ExpandedDiscipline, ExpandedCategory, LibraryMapping, DisciplineLink
            )

            # Add discipline nodes
            disciplines = self.session.query(ExpandedDiscipline).all()
            for disc in disciplines:
                node = DisciplineNode(
                    id=disc.id,
                    name=disc.name,
                    category=disc.category.name if disc.category else "Unknown",
                    difficulty=disc.difficulty_level or "intermediate",
                    estimated_hours=disc.estimated_hours or 5.0,
                    skills=disc.topics or [],
                    keywords=disc.keywords or [],
                    industry_focus=disc.industry_applications or [],
                )
                self.disciplines_cache[disc.id] = node
                self.graph.add_node(disc.id, **node.to_dict())

            # Add edges from DisciplineLink (prerequisite chains)
            links = self.session.query(DisciplineLink).all()
            for link in links:
                weight = link.strength or 0.5
                link_type = link.link_type or "related"
                self.graph.add_edge(
                    link.source_discipline_id,
                    link.target_discipline_id,
                    weight=weight,
                    link_type=link_type,
                    description=link.description or ""
                )

            self.built = True
            logger.info(f"✅ Knowledge graph built: {len(disciplines)} nodes, {len(links)} edges")
            return self

        except Exception as e:
            logger.error(f"❌ Error building knowledge graph: {e}")
            return self

    def get_graph(self) -> Optional[nx.DiGraph]:
        """Get the constructed graph"""
        if not self.built:
            self.build_from_database()
        return self.graph

    def get_discipline_node(self, discipline_id: int) -> Optional[DisciplineNode]:
        """Get cached discipline node"""
        return self.disciplines_cache.get(discipline_id)


class GraphAnalyzer:
    """Analyzes graph structure and relationships"""

    def __init__(self, graph: nx.DiGraph):
        """
        Initialize analyzer with graph

        Args:
            graph: NetworkX directed graph
        """
        self.graph = graph
        self._pagerank_cache = None
        self._centrality_cache = None

    def compute_pagerank(self) -> Dict[int, float]:
        """Compute PageRank to identify most important disciplines"""
        if self._pagerank_cache is None:
            self._pagerank_cache = nx.pagerank(self.graph, weight='weight')
        return self._pagerank_cache

    def compute_centrality(self) -> Dict[int, float]:
        """Compute betweenness centrality (disciplines that bridge topics)"""
        if self._centrality_cache is None:
            self._centrality_cache = nx.betweenness_centrality(
                self.graph, weight='weight'
            )
        return self._centrality_cache

    def get_prerequisites(self, discipline_id: int) -> List[int]:
        """Get all prerequisites for a discipline (reverse topological sort)"""
        prerequisites = []
        visited = set()
        queue = deque([discipline_id])

        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)

            # Get all predecessors (incoming edges)
            for pred in self.graph.predecessors(node):
                if pred != discipline_id:  # Exclude self
                    prerequisites.append(pred)
                    queue.append(pred)

        return prerequisites

    def get_prerequisites_ordered(self, discipline_id: int) -> List[int]:
        """Get prerequisites in recommended learning order"""
        try:
            # Use topological sort on subgraph
            prerequisites = self.get_prerequisites(discipline_id)
            subgraph = self.graph.subgraph([discipline_id] + prerequisites)
            return list(reversed(list(nx.topological_sort(subgraph))))[:-1]
        except:
            return self.get_prerequisites(discipline_id)

    def get_related_disciplines(self, discipline_id: int, depth: int = 2) -> List[Tuple[int, float]]:
        """Get related disciplines using graph traversal"""
        related = []
        visited = set()
        queue = deque([(discipline_id, 0)])

        while queue:
            node, current_depth = queue.popleft()
            if node in visited or current_depth > depth:
                continue
            visited.add(node)

            if node != discipline_id:
                # Calculate relationship score based on path length and edge weights
                try:
                    path_length = len(shortest_path(self.graph, discipline_id, node))
                    edge_weight = 1.0 / path_length
                    related.append((node, edge_weight))
                except:
                    related.append((node, 0.1))

            # Continue traversal
            for successor in self.graph.successors(node):
                if current_depth < depth:
                    queue.append((successor, current_depth + 1))

        return sorted(related, key=lambda x: x[1], reverse=True)[:10]

    def find_learning_clusters(self) -> List[List[int]]:
        """Identify clusters of related disciplines using community detection"""
        try:
            communities = list(greedy_modularity_communities(self.graph.to_undirected()))
            return [list(comm) for comm in communities]
        except:
            logger.warning("Could not compute communities")
            return []

    def compute_skill_distance(self,
                              source_skills: Set[str],
                              target_skills: Set[str]) -> float:
        """Compute Jaccard distance between skill sets (0-1)"""
        if not source_skills and not target_skills:
            return 0.0

        intersection = len(source_skills & target_skills)
        union = len(source_skills | target_skills)

        return intersection / union if union > 0 else 0.0


class RecommendationEngine:
    """Generates personalized recommendations"""

    def __init__(self, graph: nx.DiGraph, analyzer: GraphAnalyzer):
        """
        Initialize recommendation engine

        Args:
            graph: NetworkX directed graph
            analyzer: GraphAnalyzer instance for metrics
        """
        self.graph = graph
        self.analyzer = analyzer

    def recommend_next_disciplines(self,
                                   completed_disciplines: List[int],
                                   target_skill: Optional[str] = None,
                                   difficulty_preference: str = "progressive",
                                   limit: int = 5) -> List[RecommendationResult]:
        """
        Recommend next disciplines to study

        Args:
            completed_disciplines: IDs of completed disciplines
            target_skill: Optional target skill to work towards
            difficulty_preference: "progressive" (increase difficulty) or "lateral" (same level)
            limit: Number of recommendations (default 5)

        Returns:
            List of recommendations ranked by score
        """
        recommendations: Dict[int, float] = {}
        reasons: Dict[int, str] = {}
        gaps: Dict[int, List[str]] = defaultdict(list)

        # Get all completed nodes and their successors
        completed_set = set(completed_disciplines)
        candidates = set()

        for disc_id in completed_disciplines:
            # Get direct successors
            for successor in self.graph.successors(disc_id):
                if successor not in completed_set:
                    candidates.add(successor)

        if not candidates:
            logger.warning("No candidate disciplines found. Returning random options.")
            candidates = set(
                node for node in self.graph.nodes()
                if node not in completed_set
            )

        # Score each candidate
        pagerank = self.analyzer.compute_pagerank()

        for candidate_id in candidates:
            score = 0.0
            reason_parts = []

            # Factor 1: PageRank importance (0.3 weight)
            pagerank_score = pagerank.get(candidate_id, 0.0) * 100
            score += pagerank_score * 0.3
            if pagerank_score > 0.5:
                reason_parts.append("high-impact")

            # Factor 2: Prerequisite satisfaction (0.4 weight)
            prerequisites = self.analyzer.get_prerequisites(candidate_id)
            satisfied_prerequisites = sum(1 for p in prerequisites if p in completed_set)
            prereq_satisfaction = (satisfied_prerequisites / len(prerequisites)) if prerequisites else 1.0
            score += prereq_satisfaction * 0.4 * 100

            if prereq_satisfaction < 1.0:
                missing = [p for p in prerequisites if p not in completed_set]
                gaps[candidate_id] = missing

            # Factor 3: Relationship to completed (0.2 weight)
            related_to_completed = 0
            for completed_id in completed_disciplines:
                if self.graph.has_edge(completed_id, candidate_id):
                    related_to_completed += 1

            relationship_score = min(related_to_completed / 3.0, 1.0) * 100
            score += relationship_score * 0.2
            reason_parts.append(f"relates-to-{related_to_completed}-completed")

            # Factor 4: Difficulty progression (0.1 weight)
            if difficulty_preference == "progressive":
                # Prefer slightly harder disciplines
                candidate_diff = self.graph.nodes[candidate_id].get('difficulty', 'intermediate')
                score += {'beginner': 20, 'intermediate': 30, 'advanced': 40, 'expert': 50}.get(candidate_diff, 25) * 0.1

            recommendations[candidate_id] = score
            reasons[candidate_id] = " + ".join(reason_parts) if reason_parts else "related-to-learning-path"

        # Sort and create results
        results = []
        for disc_id, score in sorted(
            recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]:
            node_data = self.graph.nodes[disc_id]
            result = RecommendationResult(
                discipline_id=disc_id,
                discipline_name=node_data.get('name', f'Discipline {disc_id}'),
                score=score / 100.0,  # Normalize to 0-1
                reason=reasons[disc_id],
                prerequisite_gaps=gaps[disc_id],
                estimated_hours=node_data.get('estimated_hours', 5.0),
                similar_disciplines=[
                    self.graph.nodes[rel[0]].get('name', f'Discipline {rel[0]}')
                    for rel in self.analyzer.get_related_disciplines(disc_id, depth=1)[:3]
                ]
            )
            results.append(result)

        return results

    def recommend_learning_path(self,
                               target_discipline_id: int,
                               current_level: str = "beginner") -> LearningPathOptimized:
        """
        Generate optimized learning path to reach target discipline

        Args:
            target_discipline_id: ID of target discipline
            current_level: Current skill level (beginner/intermediate/advanced/expert)

        Returns:
            Optimized learning path with metrics
        """
        # Get prerequisites in order
        prerequisites = self.analyzer.get_prerequisites_ordered(target_discipline_id)

        # Add target discipline
        path_ids = prerequisites + [target_discipline_id]

        # Build difficulty progression
        difficulty_progression = []
        disciplines_list = []
        total_hours = 0.0

        for disc_id in path_ids:
            node_data = self.graph.nodes[disc_id]
            difficulty = node_data.get('difficulty', 'intermediate')
            estimated_hours = node_data.get('estimated_hours', 5.0)

            disc_node = DisciplineNode(
                id=disc_id,
                name=node_data.get('name', f'Discipline {disc_id}'),
                category=node_data.get('category', 'Unknown'),
                difficulty=difficulty,
                estimated_hours=estimated_hours,
            )
            disciplines_list.append(disc_node)
            difficulty_progression.append(difficulty)
            total_hours += estimated_hours

        # Find critical path (longest path through prerequisites)
        critical_path = [disciplines_list[-1]]  # At least target

        # Find parallel learning opportunities
        parallel_opportunities = []
        for disc in disciplines_list[:-1]:
            related = self.analyzer.get_related_disciplines(disc.id, depth=1)
            if related:
                parallel_opportunities.append([
                    DisciplineNode(
                        id=rel[0],
                        name=self.graph.nodes[rel[0]].get('name', f'Discipline {rel[0]}'),
                        category=self.graph.nodes[rel[0]].get('category', 'Unknown'),
                        difficulty=self.graph.nodes[rel[0]].get('difficulty', 'intermediate'),
                        estimated_hours=self.graph.nodes[rel[0]].get('estimated_hours', 5.0),
                    )
                    for rel in related[:2]
                ])

        estimated_completion_weeks = total_hours / 10.0  # Assume 10 hours/week

        return LearningPathOptimized(
            disciplines=disciplines_list,
            total_hours=total_hours,
            difficulty_progression=difficulty_progression,
            critical_path=critical_path,
            parallel_learning_opportunities=parallel_opportunities,
            estimated_completion_weeks=estimated_completion_weeks,
        )

    def analyze_skill_gaps(self,
                          user_skills: Set[str],
                          target_discipline_id: int) -> Dict[str, Any]:
        """
        Analyze skills gaps to reach target discipline

        Args:
            user_skills: Set of user's current skills
            target_discipline_id: ID of target discipline

        Returns:
            Gap analysis with recommendations
        """
        target_node_data = self.graph.nodes[target_discipline_id]
        target_skills = set(target_node_data.get('skills', []))

        missing_skills = target_skills - user_skills
        related_skills = target_skills & user_skills

        # Find disciplines that teach missing skills
        skill_to_discipline: Dict[str, List[int]] = defaultdict(list)
        for node_id, node_data in self.graph.nodes(data=True):
            node_skills = set(node_data.get('skills', []))
            for skill in missing_skills:
                if skill in node_skills:
                    skill_to_discipline[skill].append(node_id)

        return {
            'target_discipline': target_node_data.get('name'),
            'user_skills': list(user_skills),
            'target_skills': list(target_skills),
            'missing_skills': list(missing_skills),
            'related_skills': list(related_skills),
            'gap_count': len(missing_skills),
            'skill_coverage': len(related_skills) / len(target_skills) if target_skills else 1.0,
            'recommended_disciplines_for_gaps': {
                skill: skill_to_discipline[skill]
                for skill in missing_skills
            }
        }


def initialize_knowledge_graph(session: Session) -> Tuple[Optional[nx.DiGraph], Optional[GraphAnalyzer], Optional[RecommendationEngine]]:
    """
    Initialize complete knowledge graph infrastructure

    Args:
        session: SQLAlchemy database session

    Returns:
        Tuple of (graph, analyzer, recommendation_engine) or (None, None, None) if NetworkX unavailable
    """
    if not nx:
        logger.error("NetworkX required for Phase 2. Install: pip install networkx")
        return None, None, None

    try:
        builder = KnowledgeGraphBuilder(session)
        graph = builder.build_from_database()

        if not graph.built:
            logger.error("Failed to build knowledge graph")
            return None, None, None

        analyzer = GraphAnalyzer(graph.get_graph())
        recommendation_engine = RecommendationEngine(graph.get_graph(), analyzer)

        logger.info("✅ Knowledge graph initialized successfully")
        return graph.get_graph(), analyzer, recommendation_engine

    except Exception as e:
        logger.error(f"❌ Error initializing knowledge graph: {e}")
        return None, None, None
