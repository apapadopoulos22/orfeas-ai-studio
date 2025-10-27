"""
BOB AI v9.0 - Integration Hub
Central coordination for knowledge graph, reasoning engines, and discipline modules

Features:
- Unified interface for all components
- Query routing and synthesis
- Context-aware discipline selection
- Multi-agent reasoning orchestration
- Recommendation generation

Created: October 27, 2025
Version: 9.0.0
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from bob_ai_knowledge_graph import (
    get_knowledge_graph,
    get_context_router,
    get_recommendation_engine,
    KnowledgeGraph,
    ContextRouter,
    RecommendationEngine
)
from bob_ai_multi_agent_reasoner import (
    get_multi_agent_reasoner,
    MultiAgentReasoner
)
from bob_ai_discipline_mapper import (
    get_discipline_mapper,
    DisciplineModuleMapper
)

@dataclass
class QueryResult:
    """Result of a knowledge query"""
    query: str
    relevant_disciplines: List[Tuple[str, float]]  # (discipline, confidence)
    recommendations: List[str]
    multi_agent_analysis: Optional[Dict[str, Any]] = None
    learning_paths: List[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "query": self.query,
            "relevant_disciplines": self.relevant_disciplines,
            "recommendations": self.recommendations,
            "multi_agent_analysis": self.multi_agent_analysis,
            "learning_paths": self.learning_paths or [],
        }

class BOBAIIntegrationHub:
    """Central integration hub for BOB AI v9.0"""

    def __init__(self):
        # Initialize all components
        self.knowledge_graph: KnowledgeGraph = get_knowledge_graph()
        self.context_router: ContextRouter = get_context_router()
        self.recommendation_engine: RecommendationEngine = get_recommendation_engine()
        self.multi_agent_reasoner: MultiAgentReasoner = get_multi_agent_reasoner()
        self.discipline_mapper: DisciplineModuleMapper = get_discipline_mapper()

        self._initialized = True

    def query_knowledge(self, query: str, apply_reasoning: bool = False) -> QueryResult:
        """Query the knowledge system"""
        # Extract context from query
        context = self._parse_query_context(query)

        # Route to relevant disciplines
        relevant = self.context_router.route_context(context)

        # Get recommendations
        recommendations = self.recommendation_engine.recommend_for_problem(context)

        # Apply multi-agent reasoning if requested
        analysis = None
        if apply_reasoning:
            analysis = self.multi_agent_reasoner.reason_about_decision(query, context)

        # Build result
        result = QueryResult(
            query=query,
            relevant_disciplines=relevant,
            recommendations=[r[0] for r in recommendations[:5]],
            multi_agent_analysis=analysis,
            learning_paths=[]
        )

        return result

    def get_learning_recommendation(self, current_expertise: str, goal_expertise: str) -> Optional[List[str]]:
        """Recommend learning path between two disciplines"""
        path = self.knowledge_graph.find_learning_path(current_expertise, goal_expertise)
        return path.path if path else None

    def get_complementary_disciplines(self, discipline: str, limit: int = 5) -> List[str]:
        """Get disciplines that complement the given one"""
        return self.recommendation_engine.recommend_complementary_disciplines(discipline, limit)

    def search_knowledge(self, query_text: str, discipline: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search knowledge across disciplines"""
        return self.discipline_mapper.search_knowledge(query_text, discipline)

    def get_system_status(self) -> Dict[str, Any]:
        """Get status of the integrated system"""
        graph_stats = self.knowledge_graph.get_graph_statistics()
        mapper_stats = self.discipline_mapper.get_mapper_statistics()

        return {
            "initialized": self._initialized,
            "knowledge_graph": graph_stats,
            "discipline_modules": mapper_stats,
            "components": {
                "knowledge_graph": "operational",
                "context_router": "operational",
                "recommendation_engine": "operational",
                "multi_agent_reasoner": "operational",
                "discipline_mapper": "operational",
            }
        }

    def _parse_query_context(self, query: str) -> Dict[str, Any]:
        """Parse query into context dictionary"""
        # Simple keyword extraction (can be enhanced)
        query_lower = query.lower()
        keywords = [w for w in query_lower.split() if len(w) > 3]

        return {
            "keywords": keywords,
            "topics": keywords,  # Simplified
            "query": query,
        }

    def get_discipline_details(self, discipline: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a discipline"""
        return self.discipline_mapper.get_discipline_details(discipline)

    def reason_about_problem(self, problem: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get multi-agent reasoning about a problem"""
        if context is None:
            context = self._parse_query_context(problem)

        reasoning = self.multi_agent_reasoner.reason_about_decision(problem, context)

        # Add relevant disciplines
        relevant = self.context_router.route_context(context)

        return {
            "problem": problem,
            "reasoning": reasoning,
            "relevant_disciplines": relevant[:5],
        }

    def get_knowledge_base(self, discipline: str) -> Optional[Dict[str, Any]]:
        """Get knowledge base for a discipline"""
        return self.discipline_mapper.get_discipline_knowledge(discipline)

    def list_all_disciplines(self) -> List[str]:
        """List all available disciplines"""
        return self.discipline_mapper.get_all_disciplines()

    def get_disciplines_by_tier(self, tier: int) -> List[str]:
        """Get disciplines in a tier"""
        return self.discipline_mapper.get_disciplines_by_tier(tier)

# Global hub instance
_hub_instance = None

def get_bob_ai_hub() -> BOBAIIntegrationHub:
    """Get singleton BOB AI integration hub"""
    global _hub_instance
    if _hub_instance is None:
        _hub_instance = BOBAIIntegrationHub()
    return _hub_instance

# Example usage
def example_usage():
    """Example of using the integrated system"""
    hub = get_bob_ai_hub()

    # Example 1: Query with routing
    print("=== Query Routing Example ===")
    result = hub.query_knowledge("How do I improve my machine learning models?")
    print(f"Relevant disciplines: {result.relevant_disciplines}")
    print(f"Recommendations: {result.recommendations}")

    # Example 2: Learning path
    print("\n=== Learning Path Example ===")
    path = hub.get_learning_recommendation("music_composition", "technology_engineering")
    print(f"Path: {path}")

    # Example 3: Multi-agent reasoning
    print("\n=== Multi-Agent Reasoning Example ===")
    reasoning = hub.reason_about_problem(
        "Should we use microservices or monolithic architecture?"
    )
    print(f"Reasoning: {reasoning['reasoning']['consensus_recommendation']}")

    # Example 4: System status
    print("\n=== System Status ===")
    status = hub.get_system_status()
    print(f"Total disciplines: {status['knowledge_graph']['total_disciplines']}")
    print(f"Total items: {status['knowledge_graph']['total_items']}")

__all__ = [
    "BOBAIIntegrationHub",
    "QueryResult",
    "get_bob_ai_hub",
    "example_usage",
]
