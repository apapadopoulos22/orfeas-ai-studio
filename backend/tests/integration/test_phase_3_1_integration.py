"""
Integration Tests - Phase 3.1 Components
Comprehensive testing of all LLM integration modules
"""

import pytest


class TestIntegrationCacheAndRetrieval:
    """Test cache layer integration with context retrieval."""

    def test_cache_with_context_retrieval(self):
        """Test cache integration with RAG context retrieval."""
        from backend.llm_integration.llm_cache_layer import LLMCacheLayer
        from backend.llm_integration.context_retrieval import ContextRetriever

        # Setup
        cache = LLMCacheLayer(max_size=100, default_ttl_seconds=3600)
        docs = [
            {'content': 'Python is for web dev', 'metadata': {'type': 'lang'}},
            {'content': 'JavaScript runs in browsers', 'metadata': {'type': 'lang'}}
        ]
        retriever = ContextRetriever(docs, strategy="hybrid", top_k=1)

        # Test: Cache context retrieval results
        query1 = "Python programming"
        results1 = retriever.retrieve_context(query1)
        cache_key = f"retrieval:{query1}"
        cache.set(cache_key, str(results1), model="retriever")

        # Verify cached
        cached_results = cache.get(cache_key, model="retriever")
        assert cached_results is not None
        assert len(results1) > 0


class TestIntegrationQualityAndTokens:
    """Test quality monitor integration with token counter."""

    def test_quality_scoring_with_token_counting(self):
        """Test quality scoring paired with token counting."""
        from backend.llm_integration.llm_quality_monitor import LLMQualityMonitor
        from backend.llm_integration.token_counter import TokenCounter

        # Setup
        monitor = LLMQualityMonitor()
        counter = TokenCounter(budget_limit_usd=10.0)        # Generate response
        response = "Python is a high-level programming language."

        # Score quality
        quality_score = monitor.evaluate_response(response, task_type="factual")

        # Count tokens
        usage = counter.count_tokens("gpt-4-turbo", 20, 10)

        # Assertions
        assert quality_score.overall_score > 0.7
        assert usage.total_cost > 0
        assert counter.get_total_cost() < 1.0


class TestIntegrationPromptOptimization:
    """Test prompt engineering with other components."""

    def test_optimized_prompt_with_chunking(self):
        """Test prompt optimization with semantic chunking."""
        from backend.llm_integration.prompt_engineering import PromptEngineer
        from backend.llm_integration.semantic_chunking import SemanticChunker

        # Setup
        engineer = PromptEngineer()
        chunker = SemanticChunker(chunk_size=100, strategy="semantic")

        # Optimize prompt
        original = "write a function"
        optimized = engineer.optimize_prompt(original)

        # Chunk the context
        long_text = "Function definitions. Parameters and return values. Error handling. " * 10
        chunks = chunker.chunk_document(long_text)

        # Assertions
        assert len(optimized.enhancements_applied) > 0
        assert len(chunks) > 0


class TestIntegrationFailoverWithMonitoring:
    """Test failover handler with quality monitoring."""

    def test_failover_quality_feedback(self):
        """Test failover decision based on quality scores."""
        from backend.llm_integration.llm_failover_handler import LLMFailoverHandler
        from backend.llm_integration.llm_quality_monitor import LLMQualityMonitor

        # Setup
        handler = LLMFailoverHandler(
            fallback_chain=["gpt-3.5-turbo", "claude-3-sonnet"],
            circuit_failure_threshold=3
        )
        monitor = LLMQualityMonitor()

        # Simulate poor quality response
        poor_response = "xyz abc def"
        quality = monitor.evaluate_response(poor_response)

        # If quality is poor, should consider failover
        if quality.overall_score < 0.5:
            handler._record_failure("gpt-4", quality.quality_level, "Low quality response")

        # Get stats
        stats = handler.get_stats()
        assert isinstance(stats, dict)


class TestIntegrationFullPipeline:
    """Test complete pipeline integration."""

    def test_full_rag_pipeline(self):
        """Test full RAG pipeline: retrieval -> caching -> quality."""
        from backend.llm_integration.context_retrieval import ContextRetriever
        from backend.llm_integration.llm_cache_layer import LLMCacheLayer
        from backend.llm_integration.llm_quality_monitor import LLMQualityMonitor
        from backend.llm_integration.token_counter import TokenCounter

        # Setup
        docs = [
            {'content': 'Machine learning uses neural networks', 'metadata': {'src': 'ml'}},
            {'content': 'Deep learning requires GPUs', 'metadata': {'src': 'dl'}}
        ]
        retriever = ContextRetriever(docs, strategy="hybrid", top_k=2)
        cache = LLMCacheLayer(max_size=100, default_ttl_seconds=3600)
        monitor = LLMQualityMonitor()
        counter = TokenCounter(budget_limit_usd=10.0)

        # Execute pipeline
        query = "machine learning"

        # Step 1: Try cache
        cache_key = f"retrieval:{query}"
        cached = cache.get(cache_key, model="retriever")

        # Step 2: Retrieve if not cached
        if not cached:
            results = retriever.retrieve_context(query)
            cache.set(cache_key, str(results), model="retriever")
        else:
            results = eval(cached)

        # Step 3: Format response
        response_text = " ".join([r.content for r in results[:2]])

        # Step 4: Score quality
        quality_score = monitor.evaluate_response(response_text)

        # Step 5: Count tokens
        usage = counter.count_tokens("gpt-4-turbo", 100, 50)

        # Assertions
        assert len(results) > 0
        assert quality_score.overall_score > 0.5
        assert usage.total_cost > 0


class TestComponentInteroperability:
    """Test that all components work together."""

    def test_all_components_importable(self):
        """Test all components can be imported."""
        from backend.llm_integration.llm_router import LLMRouter
        from backend.llm_integration.multi_llm_orchestrator import MultiLLMOrchestrator
        from backend.llm_integration.prompt_engineering import PromptEngineer
        from backend.llm_integration.llm_cache_layer import LLMCacheLayer
        from backend.llm_integration.semantic_chunking import SemanticChunker
        from backend.llm_integration.context_retrieval import ContextRetriever
        from backend.llm_integration.token_counter import TokenCounter
        from backend.llm_integration.llm_quality_monitor import LLMQualityMonitor
        from backend.llm_integration.llm_failover_handler import LLMFailoverHandler

        # All should import successfully
        assert LLMRouter is not None
        assert MultiLLMOrchestrator is not None
        assert PromptEngineer is not None
        assert LLMCacheLayer is not None
        assert SemanticChunker is not None
        assert ContextRetriever is not None
        assert TokenCounter is not None
        assert LLMQualityMonitor is not None
        assert LLMFailoverHandler is not None

    def test_singleton_patterns(self):
        """Test singleton getter functions."""
        from backend.llm_integration.prompt_engineering import get_prompt_engineer
        from backend.llm_integration.llm_cache_layer import get_llm_cache
        from backend.llm_integration.token_counter import get_token_counter
        from backend.llm_integration.llm_quality_monitor import get_quality_monitor
        from backend.llm_integration.llm_failover_handler import get_failover_handler

        # All should have working singleton getters
        assert get_prompt_engineer() is not None
        assert get_llm_cache() is not None
        assert get_token_counter() is not None
        assert get_quality_monitor() is not None
        assert get_failover_handler() is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
