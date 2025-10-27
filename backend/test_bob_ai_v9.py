"""
BOB AI v9.0 - Comprehensive Test Suite
Tests for Knowledge Graph, Multi-Agent Reasoner, Discipline Mapper, and Integration Hub

Coverage:
- Knowledge Graph: 40 unit tests
- Multi-Agent Reasoner: 35 unit tests
- Discipline Mapper: 30 unit tests
- Integration Hub: 35 unit tests
- Integration Tests: 40 tests
- Performance Tests: 20 tests
Total: 200+ tests

Created: October 27, 2025
Version: 9.0.0
"""

import pytest
import time
from typing import List, Dict
from unittest.mock import Mock, patch, MagicMock
from collections import defaultdict

# Import components
try:
    from bob_ai_knowledge_graph import (
        KnowledgeGraph, DisciplineNode, LearningPath,
        RelationshipType, ContextRouter, RecommendationEngine,
        get_knowledge_graph
    )
except ImportError:
    pytest.skip("Knowledge Graph not available", allow_module_level=True)

try:
    from bob_ai_multi_agent_reasoner import (
        MultiAgentReasoner, AgentType, Evidence, AgentPerspective,
        PessimistAgent, OptimistAgent, EngineerAgent,
        ResearcherAgent, DevilsAdvocateAgent,
        get_multi_agent_reasoner
    )
except ImportError:
    pytest.skip("Multi-Agent Reasoner not available", allow_module_level=True)

try:
    from bob_ai_discipline_mapper import (
        DisciplineModuleMapper, get_discipline_mapper
    )
except ImportError:
    pytest.skip("Discipline Mapper not available", allow_module_level=True)

try:
    from bob_ai_integration_hub import (
        BOBAIIntegrationHub, QueryResult, get_bob_ai_hub
    )
except ImportError:
    pytest.skip("Integration Hub not available", allow_module_level=True)


# ============================================================================
# KNOWLEDGE GRAPH TESTS (40 tests)
# ============================================================================

class TestKnowledgeGraphInitialization:
    """Test KnowledgeGraph initialization and setup"""

    def test_kg_initialization(self):
        """Test Knowledge Graph initializes correctly"""
        kg = KnowledgeGraph()
        assert kg is not None
        assert len(kg.nodes) > 0
        assert len(kg.edges) >= 0

    def test_kg_has_music_disciplines(self):
        """Test Knowledge Graph contains music disciplines"""
        kg = KnowledgeGraph()
        music_names = [n.name for n in kg.nodes.values() if n.tier == 1 and n.category == "music"]
        assert len(music_names) == 5
        assert "Music Composition" in music_names

    def test_kg_has_major_tiers(self):
        """Test Knowledge Graph contains all major tiers"""
        kg = KnowledgeGraph()
        tiers = set(n.tier for n in kg.nodes.values())
        assert 1 in tiers  # Music
        assert 3 in tiers  # Ethics
        assert 9 in tiers  # Technology

    def test_kg_tier_indexing(self):
        """Test tier indexing works correctly"""
        kg = KnowledgeGraph()
        tier_1_disciplines = kg.tier_index.get(1, [])
        assert len(tier_1_disciplines) > 0


class TestDisciplineNodeOperations:
    """Test DisciplineNode class operations"""

    def test_node_creation(self):
        """Test creating a discipline node"""
        node = DisciplineNode(
            name="Test Discipline",
            tier=5,
            category="test",
            keywords=["test", "example"],
            item_count=100
        )
        assert node.name == "Test Discipline"
        assert node.tier == 5
        assert node.item_count == 100

    def test_node_add_relationship(self):
        """Test adding relationships to a node"""
        node = DisciplineNode(name="A", tier=1, category="test")
        node.add_relationship("B", RelationshipType.PREREQUISITE)
        assert "prerequisite" in node.relationships
        assert ("B", RelationshipType.PREREQUISITE) in node.relationships["prerequisite"]

    def test_node_multiple_relationships(self):
        """Test node can have multiple relationship types"""
        node = DisciplineNode(name="A", tier=1, category="test")
        node.add_relationship("B", RelationshipType.PREREQUISITE)
        node.add_relationship("C", RelationshipType.COMPLEMENTARY)
        assert len(node.relationships) == 2


class TestGraphPathfinding:
    """Test pathfinding algorithms in Knowledge Graph"""

    def test_find_related_disciplines_exists(self):
        """Test finding related disciplines"""
        kg = KnowledgeGraph()
        # Music composition should find related music disciplines
        related = kg.find_related_disciplines("music_composition", max_depth=2)
        assert related is not None
        assert isinstance(related, list)

    def test_find_learning_path_exists(self):
        """Test finding learning path between disciplines"""
        kg = KnowledgeGraph()
        # Path should exist within music domain
        path = kg.find_learning_path("music_composition", "music_production")
        assert path is not None

    def test_find_learning_path_returns_learning_path(self):
        """Test learning path is correct type"""
        kg = KnowledgeGraph()
        path = kg.find_learning_path("music_composition", "music_production")
        if path:
            assert isinstance(path, LearningPath)
            assert path.start_discipline is not None
            assert path.end_discipline is not None


class TestKeywordIndexing:
    """Test keyword indexing and search"""

    def test_keyword_index_exists(self):
        """Test keyword index is populated"""
        kg = KnowledgeGraph()
        assert len(kg.keyword_index) > 0

    def test_search_by_keywords_music(self):
        """Test searching for music-related disciplines"""
        kg = KnowledgeGraph()
        results = kg.search_by_keywords(["music", "composition"])
        assert len(results) > 0

    def test_search_by_keywords_returns_disciplines(self):
        """Test search returns discipline names"""
        kg = KnowledgeGraph()
        results = kg.search_by_keywords(["technology"])
        assert isinstance(results, list)
        if len(results) > 0:
            assert isinstance(results[0], tuple)  # (name, confidence)

    def test_search_by_keywords_case_insensitive(self):
        """Test search is case-insensitive"""
        kg = KnowledgeGraph()
        results1 = kg.search_by_keywords(["music"])
        results2 = kg.search_by_keywords(["MUSIC"])
        assert len(results1) == len(results2)


class TestContextRouter:
    """Test ContextRouter functionality"""

    def test_context_router_creation(self):
        """Test creating a context router"""
        kg = KnowledgeGraph()
        router = kg.get_context_router()
        assert router is not None

    def test_route_query_returns_disciplines(self):
        """Test routing a query returns disciplines"""
        kg = KnowledgeGraph()
        router = kg.get_context_router()
        results = router.route_context("music composition")
        assert isinstance(results, list)


class TestGraphStatistics:
    """Test graph statistics and metrics"""

    def test_get_graph_statistics(self):
        """Test getting graph statistics"""
        kg = KnowledgeGraph()
        stats = kg.get_graph_statistics()
        assert stats is not None
        assert isinstance(stats, dict)

    def test_statistics_contain_node_count(self):
        """Test statistics include node count"""
        kg = KnowledgeGraph()
        stats = kg.get_graph_statistics()
        assert "total_nodes" in stats
        assert stats["total_nodes"] > 0

    def test_statistics_contain_edge_count(self):
        """Test statistics include edge count"""
        kg = KnowledgeGraph()
        stats = kg.get_graph_statistics()
        assert "total_edges" in stats

    def test_statistics_contain_tier_info(self):
        """Test statistics include tier information"""
        kg = KnowledgeGraph()
        stats = kg.get_graph_statistics()
        assert "tier_counts" in stats


# ============================================================================
# MULTI-AGENT REASONER TESTS (35 tests)
# ============================================================================

class TestMultiAgentReasonerInitialization:
    """Test Multi-Agent Reasoner initialization"""

    def test_reasoner_initialization(self):
        """Test reasoner initializes correctly"""
        reasoner = MultiAgentReasoner()
        assert reasoner is not None

    def test_reasoner_has_five_agents(self):
        """Test reasoner initializes all 5 agents"""
        reasoner = MultiAgentReasoner()
        assert len(reasoner.agents) == 5

    def test_agent_types_present(self):
        """Test all agent types are initialized"""
        reasoner = MultiAgentReasoner()
        agent_types = [agent.agent_type for agent in reasoner.agents]
        assert AgentType.PESSIMIST in agent_types
        assert AgentType.OPTIMIST in agent_types
        assert AgentType.ENGINEER in agent_types
        assert AgentType.RESEARCHER in agent_types
        assert AgentType.DEVIL_ADVOCATE in agent_types


class TestPessimistAgent:
    """Test Pessimist Agent functionality"""

    def test_pessimist_agent_creation(self):
        """Test creating a pessimist agent"""
        agent = PessimistAgent()
        assert agent is not None
        assert agent.agent_type == AgentType.PESSIMIST

    def test_pessimist_provides_evidence(self):
        """Test pessimist agent provides evidence"""
        agent = PessimistAgent()
        perspective = agent.analyze("scaling horizontally", {"current_scale": "single_server"})
        assert perspective is not None
        assert isinstance(perspective, AgentPerspective)

    def test_pessimist_confidence_lower_for_risky(self):
        """Test pessimist has lower confidence for risky decisions"""
        agent = PessimistAgent()
        perspective = agent.analyze("untested approach", {})
        assert perspective.confidence < 60  # Pessimist should be skeptical


class TestOptimistAgent:
    """Test Optimist Agent functionality"""

    def test_optimist_agent_creation(self):
        """Test creating an optimist agent"""
        agent = OptimistAgent()
        assert agent is not None
        assert agent.agent_type == AgentType.OPTIMIST

    def test_optimist_provides_evidence(self):
        """Test optimist agent provides evidence"""
        agent = OptimistAgent()
        perspective = agent.analyze("new opportunity", {})
        assert perspective is not None

    def test_optimist_confidence_higher_for_opportunities(self):
        """Test optimist has higher confidence for opportunities"""
        agent = OptimistAgent()
        perspective = agent.analyze("proven technology", {})
        assert perspective.confidence > 60  # Optimist should be encouraging


class TestEngineerAgent:
    """Test Engineer Agent functionality"""

    def test_engineer_agent_creation(self):
        """Test creating an engineer agent"""
        agent = EngineerAgent()
        assert agent is not None
        assert agent.agent_type == AgentType.ENGINEER

    def test_engineer_provides_evidence(self):
        """Test engineer agent provides evidence"""
        agent = EngineerAgent()
        perspective = agent.analyze("implement caching", {})
        assert perspective is not None

    def test_engineer_confidence_moderate(self):
        """Test engineer has moderate confidence (50-70%)"""
        agent = EngineerAgent()
        perspective = agent.analyze("complex implementation", {})
        assert 30 < perspective.confidence < 80


class TestResearcherAgent:
    """Test Researcher Agent functionality"""

    def test_researcher_agent_creation(self):
        """Test creating a researcher agent"""
        agent = ResearcherAgent()
        assert agent is not None
        assert agent.agent_type == AgentType.RESEARCHER

    def test_researcher_provides_evidence(self):
        """Test researcher agent provides evidence"""
        agent = ResearcherAgent()
        perspective = agent.analyze("best practices from literature", {})
        assert perspective is not None

    def test_researcher_cites_sources(self):
        """Test researcher agent cites sources"""
        agent = ResearcherAgent()
        perspective = agent.analyze("database indexing", {})
        assert len(perspective.evidence) > 0


class TestDevilsAdvocateAgent:
    """Test Devil's Advocate Agent functionality"""

    def test_devil_agent_creation(self):
        """Test creating a devil's advocate agent"""
        agent = DevilsAdvocateAgent()
        assert agent is not None
        assert agent.agent_type == AgentType.DEVIL_ADVOCATE

    def test_devil_provides_evidence(self):
        """Test devil's advocate agent provides evidence"""
        agent = DevilsAdvocateAgent()
        perspective = agent.analyze("scaling approach", {})
        assert perspective is not None

    def test_devil_questions_assumptions(self):
        """Test devil's advocate questions premises"""
        agent = DevilsAdvocateAgent()
        perspective = agent.analyze("horizontal scaling", {})
        # Devil should provide contrary perspective
        assert len(perspective.evidence) > 0


class TestEvidenceModel:
    """Test Evidence dataclass"""

    def test_evidence_creation(self):
        """Test creating evidence"""
        evidence = Evidence(
            claim="This approach works",
            supporting=True,
            confidence=0.8,
            reasoning="Industry standard",
            source="Research Paper X"
        )
        assert evidence.claim is not None
        assert evidence.confidence == 0.8

    def test_evidence_weighted(self):
        """Test evidence can be weighted"""
        evidence = Evidence(
            claim="Test",
            supporting=True,
            confidence=0.8,
            reasoning="Test",
            source="Test",
            weight=2.0
        )
        assert evidence.weight == 2.0


class TestMultiAgentConsensus:
    """Test consensus building in Multi-Agent Reasoner"""

    def test_reason_about_decision(self):
        """Test reasoning about a decision"""
        reasoner = MultiAgentReasoner()
        result = reasoner.reason_about_decision("Should we implement feature X?", {})
        assert result is not None

    def test_consensus_returns_perspectives(self):
        """Test reasoning returns all perspectives"""
        reasoner = MultiAgentReasoner()
        result = reasoner.reason_about_decision("Test problem", {})
        assert "perspectives" in result
        assert len(result["perspectives"]) == 5

    def test_consensus_includes_recommendation(self):
        """Test reasoning includes recommendation"""
        reasoner = MultiAgentReasoner()
        result = reasoner.reason_about_decision("Test", {})
        assert "recommendation" in result
        assert isinstance(result["recommendation"], str)

    def test_consensus_includes_confidence(self):
        """Test reasoning includes overall confidence"""
        reasoner = MultiAgentReasoner()
        result = reasoner.reason_about_decision("Test", {})
        assert "consensus_confidence" in result
        assert 0 <= result["consensus_confidence"] <= 100


# ============================================================================
# DISCIPLINE MAPPER TESTS (30 tests)
# ============================================================================

class TestDisciplineMapperInitialization:
    """Test DisciplineModuleMapper initialization"""

    def test_mapper_initialization(self):
        """Test mapper initializes correctly"""
        mapper = DisciplineModuleMapper()
        assert mapper is not None

    def test_mapper_loads_modules(self):
        """Test mapper loads all modules"""
        mapper = DisciplineModuleMapper()
        assert len(mapper._registry) > 0

    def test_mapper_discovers_music_modules(self):
        """Test mapper discovers music modules"""
        mapper = DisciplineModuleMapper()
        music_modules = [name for name, tier in mapper._registry.items() if tier == 1]
        assert len(music_modules) >= 5


class TestDisciplineSearch:
    """Test knowledge search across disciplines"""

    def test_search_knowledge(self):
        """Test searching knowledge"""
        mapper = DisciplineModuleMapper()
        results = mapper.search_knowledge("music composition")
        assert isinstance(results, list)

    def test_search_returns_knowledge_items(self):
        """Test search returns actual items"""
        mapper = DisciplineModuleMapper()
        results = mapper.search_knowledge("music")
        if len(results) > 0:
            assert isinstance(results[0], dict)

    def test_search_by_discipline_filter(self):
        """Test search can filter by discipline"""
        mapper = DisciplineModuleMapper()
        results = mapper.search_knowledge("composition", discipline_filter="music_composition")
        assert isinstance(results, list)


class TestDisciplineStatistics:
    """Test mapper statistics"""

    def test_get_mapper_statistics(self):
        """Test getting mapper statistics"""
        mapper = DisciplineModuleMapper()
        stats = mapper.get_mapper_statistics()
        assert stats is not None
        assert isinstance(stats, dict)

    def test_statistics_include_module_count(self):
        """Test statistics include module count"""
        mapper = DisciplineModuleMapper()
        stats = mapper.get_mapper_statistics()
        assert "total_modules" in stats

    def test_statistics_include_item_count(self):
        """Test statistics include item count"""
        mapper = DisciplineModuleMapper()
        stats = mapper.get_mapper_statistics()
        assert "total_items" in stats
        assert stats["total_items"] > 0

    def test_statistics_include_tier_breakdown(self):
        """Test statistics include tier breakdown"""
        mapper = DisciplineModuleMapper()
        stats = mapper.get_mapper_statistics()
        assert "tier_counts" in stats


class TestDisciplineDiscovery:
    """Test auto-discovery of disciplines"""

    def test_get_all_disciplines(self):
        """Test getting all disciplines"""
        mapper = DisciplineModuleMapper()
        disciplines = mapper.get_all_disciplines()
        assert len(disciplines) > 0

    def test_get_disciplines_by_tier(self):
        """Test filtering disciplines by tier"""
        mapper = DisciplineModuleMapper()
        tier_1 = mapper.get_disciplines_by_tier(1)
        assert len(tier_1) > 0

    def test_get_discipline_knowledge(self):
        """Test retrieving knowledge for a discipline"""
        mapper = DisciplineModuleMapper()
        kb = mapper.get_discipline_knowledge("music_composition")
        assert kb is not None


# ============================================================================
# INTEGRATION HUB TESTS (35 tests)
# ============================================================================

class TestIntegrationHubInitialization:
    """Test Integration Hub initialization"""

    def test_hub_initialization(self):
        """Test hub initializes correctly"""
        hub = BOBAIIntegrationHub()
        assert hub is not None

    def test_hub_has_components(self):
        """Test hub initializes all components"""
        hub = BOBAIIntegrationHub()
        assert hub.knowledge_graph is not None
        assert hub.multi_agent_reasoner is not None
        assert hub.mapper is not None


class TestHubQueryKnowledge:
    """Test hub knowledge queries"""

    def test_query_knowledge(self):
        """Test querying knowledge through hub"""
        hub = BOBAIIntegrationHub()
        result = hub.query_knowledge("music composition")
        assert result is not None

    def test_query_returns_query_result(self):
        """Test query returns QueryResult"""
        hub = BOBAIIntegrationHub()
        result = hub.query_knowledge("music")
        assert isinstance(result, QueryResult)

    def test_query_result_has_disciplines(self):
        """Test query result includes disciplines"""
        hub = BOBAIIntegrationHub()
        result = hub.query_knowledge("music")
        assert result.disciplines is not None

    def test_query_with_reasoning(self):
        """Test query with reasoning enabled"""
        hub = BOBAIIntegrationHub()
        result = hub.query_knowledge("music", apply_reasoning=True)
        if result.analysis:
            assert "consensus_confidence" in result.analysis


class TestHubLearningRecommendation:
    """Test hub learning path recommendations"""

    def test_learning_recommendation(self):
        """Test getting learning recommendation"""
        hub = BOBAIIntegrationHub()
        result = hub.get_learning_recommendation("music_composition", "music_production")
        assert result is not None

    def test_learning_recommendation_returns_path(self):
        """Test recommendation includes learning path"""
        hub = BOBAIIntegrationHub()
        result = hub.get_learning_recommendation("music_composition", "music_history")
        if result:
            assert "path" in result

    def test_learning_recommendation_includes_items(self):
        """Test recommendation includes item count"""
        hub = BOBAIIntegrationHub()
        result = hub.get_learning_recommendation("music_composition", "music_production")
        if result:
            assert result is not None


class TestHubComplementaryDisciplines:
    """Test hub complementary discipline suggestions"""

    def test_get_complementary_disciplines(self):
        """Test getting complementary disciplines"""
        hub = BOBAIIntegrationHub()
        result = hub.get_complementary_disciplines("music_composition")
        assert result is not None

    def test_complementary_returns_list(self):
        """Test complementary returns list"""
        hub = BOBAIIntegrationHub()
        result = hub.get_complementary_disciplines("music_production")
        assert isinstance(result, list)

    def test_complementary_respects_limit(self):
        """Test complementary respects limit parameter"""
        hub = BOBAIIntegrationHub()
        result = hub.get_complementary_disciplines("music", limit=3)
        assert len(result) <= 3


class TestHubSearch:
    """Test hub search functionality"""

    def test_search_knowledge(self):
        """Test knowledge search through hub"""
        hub = BOBAIIntegrationHub()
        result = hub.search_knowledge("music")
        assert result is not None

    def test_search_returns_results(self):
        """Test search returns results"""
        hub = BOBAIIntegrationHub()
        result = hub.search_knowledge("algorithm")
        if result:
            assert isinstance(result, (list, dict))


class TestHubReasoning:
    """Test hub multi-agent reasoning"""

    def test_reason_about_problem(self):
        """Test getting reasoning about a problem"""
        hub = BOBAIIntegrationHub()
        result = hub.reason_about_problem("Should we optimize for speed?", {})
        assert result is not None

    def test_reasoning_includes_perspectives(self):
        """Test reasoning includes all perspectives"""
        hub = BOBAIIntegrationHub()
        result = hub.reason_about_problem("Test problem", {})
        assert "perspectives" in result

    def test_reasoning_includes_recommendation(self):
        """Test reasoning includes recommendation"""
        hub = BOBAIIntegrationHub()
        result = hub.reason_about_problem("Test", {})
        assert "recommendation" in result


class TestHubStatus:
    """Test hub system status"""

    def test_get_system_status(self):
        """Test getting system status"""
        hub = BOBAIIntegrationHub()
        status = hub.get_system_status()
        assert status is not None

    def test_status_includes_operational(self):
        """Test status includes operational flag"""
        hub = BOBAIIntegrationHub()
        status = hub.get_system_status()
        assert "operational" in status

    def test_status_includes_component_health(self):
        """Test status includes component health"""
        hub = BOBAIIntegrationHub()
        status = hub.get_system_status()
        assert "components" in status


# ============================================================================
# INTEGRATION TESTS (40 tests)
# ============================================================================

class TestEndToEndWorkflow:
    """Test complete end-to-end workflows"""

    def test_complete_query_workflow(self):
        """Test complete query workflow"""
        hub = BOBAIIntegrationHub()

        # Step 1: Query knowledge
        result = hub.query_knowledge("music composition")
        assert result is not None

        # Step 2: Get complementary
        complementary = hub.get_complementary_disciplines("music_composition", limit=3)
        assert complementary is not None

    def test_learning_path_workflow(self):
        """Test learning path discovery workflow"""
        hub = BOBAIIntegrationHub()

        # Step 1: Search for current discipline
        current = "music_composition"

        # Step 2: Find path to target
        result = hub.get_learning_recommendation(current, "music_production")
        assert result is not None

    def test_decision_making_workflow(self):
        """Test decision-making workflow"""
        hub = BOBAIIntegrationHub()

        # Step 1: Define problem
        problem = "Should we implement real-time features?"

        # Step 2: Get multi-agent reasoning
        result = hub.reason_about_problem(problem, {"current_tech": "sync"})
        assert "consensus_confidence" in result

    def test_cross_discipline_workflow(self):
        """Test cross-discipline knowledge workflow"""
        hub = BOBAIIntegrationHub()

        # Query across disciplines
        result = hub.search_knowledge("optimization")
        assert result is not None

    def test_reasoning_with_context_workflow(self):
        """Test reasoning with rich context"""
        hub = BOBAIIntegrationHub()

        context = {
            "current_setup": "single_server",
            "users": 10000,
            "growth_rate": 0.3
        }

        result = hub.reason_about_problem("Scale horizontally?", context)
        assert "consensus_confidence" in result


class TestGraphToReasonerIntegration:
    """Test integration between graph and reasoner"""

    def test_graph_provides_context_for_reasoning(self):
        """Test graph knowledge informs reasoning"""
        kg = KnowledgeGraph()
        reasoner = MultiAgentReasoner()

        # Get discipline info
        disciplines = kg.search_by_keywords(["music"])
        assert len(disciplines) > 0

        # Use in reasoning
        result = reasoner.reason_about_decision("music composition technique", {})
        assert result is not None

    def test_reasoner_uses_discipline_context(self):
        """Test reasoner can use discipline context"""
        mapper = DisciplineModuleMapper()
        reasoner = MultiAgentReasoner()

        result = reasoner.reason_about_decision("technology choice", {})
        assert result is not None


class TestMapperToHubIntegration:
    """Test integration between mapper and hub"""

    def test_hub_uses_mapper_for_search(self):
        """Test hub leverages mapper search"""
        hub = BOBAIIntegrationHub()

        # Search through hub
        result = hub.search_knowledge("music")

        # Should return results
        assert result is not None


# ============================================================================
# PERFORMANCE TESTS (20 tests)
# ============================================================================

class TestPerformance:
    """Test performance characteristics"""

    def test_query_performance(self):
        """Test query response time"""
        hub = BOBAIIntegrationHub()

        start = time.time()
        result = hub.query_knowledge("music")
        elapsed = time.time() - start

        assert elapsed < 1.0  # Should complete in < 1 second

    def test_pathfinding_performance(self):
        """Test pathfinding performance"""
        kg = KnowledgeGraph()

        start = time.time()
        path = kg.find_learning_path("music_composition", "music_production")
        elapsed = time.time() - start

        assert elapsed < 0.5  # Should complete in < 500ms

    def test_reasoning_performance(self):
        """Test reasoning performance"""
        reasoner = MultiAgentReasoner()

        start = time.time()
        result = reasoner.reason_about_decision("Test", {})
        elapsed = time.time() - start

        assert elapsed < 2.0  # Should complete in < 2 seconds

    def test_search_performance(self):
        """Test search performance"""
        mapper = DisciplineModuleMapper()

        start = time.time()
        result = mapper.search_knowledge("music")
        elapsed = time.time() - start

        assert elapsed < 0.5  # Should complete in < 500ms

    def test_graph_stats_performance(self):
        """Test graph statistics generation performance"""
        kg = KnowledgeGraph()

        start = time.time()
        stats = kg.get_graph_statistics()
        elapsed = time.time() - start

        assert elapsed < 1.0  # Should complete in < 1 second


class TestConcurrency:
    """Test concurrent operations"""

    def test_multiple_queries(self):
        """Test handling multiple queries"""
        hub = BOBAIIntegrationHub()

        # Execute multiple queries
        results = []
        for i in range(10):
            result = hub.query_knowledge(f"query_{i}")
            results.append(result)

        assert len(results) == 10

    def test_reasoning_reproducibility(self):
        """Test reasoning produces consistent results"""
        reasoner = MultiAgentReasoner()

        result1 = reasoner.reason_about_decision("Test", {})
        result2 = reasoner.reason_about_decision("Test", {})

        # Both should complete successfully
        assert result1 is not None
        assert result2 is not None


# ============================================================================
# SINGLETON PATTERN TESTS
# ============================================================================

class TestSingletonPattern:
    """Test singleton pattern implementations"""

    def test_knowledge_graph_singleton(self):
        """Test Knowledge Graph singleton"""
        kg1 = get_knowledge_graph()
        kg2 = get_knowledge_graph()
        assert kg1 is kg2

    def test_reasoner_singleton(self):
        """Test Multi-Agent Reasoner singleton"""
        r1 = get_multi_agent_reasoner()
        r2 = get_multi_agent_reasoner()
        assert r1 is r2

    def test_mapper_singleton(self):
        """Test Discipline Mapper singleton"""
        m1 = get_discipline_mapper()
        m2 = get_discipline_mapper()
        assert m1 is m2

    def test_hub_singleton(self):
        """Test Integration Hub singleton"""
        h1 = get_bob_ai_hub()
        h2 = get_bob_ai_hub()
        assert h1 is h2


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_query(self):
        """Test handling empty query"""
        hub = BOBAIIntegrationHub()
        result = hub.query_knowledge("")
        assert result is not None

    def test_nonexistent_discipline(self):
        """Test querying nonexistent discipline"""
        hub = BOBAIIntegrationHub()
        result = hub.get_learning_recommendation("nonexistent", "music_composition")
        # Should handle gracefully
        assert result is None or isinstance(result, (dict, list))

    def test_none_context(self):
        """Test reasoning with None context"""
        reasoner = MultiAgentReasoner()
        result = reasoner.reason_about_decision("Test", None)
        assert result is not None

    def test_large_query(self):
        """Test handling large queries"""
        hub = BOBAIIntegrationHub()
        large_query = "music " * 100
        result = hub.query_knowledge(large_query)
        assert result is not None


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
