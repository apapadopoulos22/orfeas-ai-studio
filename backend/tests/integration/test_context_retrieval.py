"""
Unit Tests for Context Retrieval (File 6 - RAG)
Tests document retrieval, ranking, and relevance scoring
"""

import pytest
from backend.llm_integration.context_retrieval import (
    ContextRetriever,
    RetrievedDocument,
    RetrievalStrategy,
)


class TestContextRetriever:
    """Test suite for ContextRetriever class."""

    @pytest.fixture
    def sample_documents(self):
        """Create sample documents for testing."""
        return [
            {
                'content': 'Python is a programming language used for web development',
                'metadata': {'source': 'wiki', 'type': 'language'}
            },
            {
                'content': 'JavaScript runs in web browsers and is used for frontend',
                'metadata': {'source': 'docs', 'type': 'language'}
            },
            {
                'content': 'Machine learning models use neural networks for predictions',
                'metadata': {'source': 'research', 'type': 'ml'}
            },
            {
                'content': 'Deep learning requires GPU acceleration for training',
                'metadata': {'source': 'guide', 'type': 'ml'}
            },
        ]

    @pytest.fixture
    def retriever(self, sample_documents):
        """Create retriever instance with sample documents."""
        return ContextRetriever(sample_documents, strategy="hybrid", top_k=2)

    def test_retriever_initialization(self, retriever, sample_documents):
        """Test retriever initializes correctly."""
        assert len(retriever.document_store) == len(sample_documents)
        assert retriever.strategy == "hybrid"
        assert retriever.top_k == 2

    def test_vector_similarity_retrieval(self, sample_documents):
        """Test vector similarity retrieval strategy."""
        retriever = ContextRetriever(sample_documents, strategy="vector_similarity", top_k=2)
        results = retriever.retrieve_context("Python programming")

        assert len(results) <= 2
        assert all(isinstance(r, RetrievedDocument) for r in results)
        assert all(0.0 <= r.relevance_score <= 1.0 for r in results)

    def test_bm25_retrieval(self, sample_documents):
        """Test BM25 retrieval strategy."""
        retriever = ContextRetriever(sample_documents, strategy="bm25", top_k=2)
        results = retriever.retrieve_context("web development")

        assert len(results) <= 2
        assert all(isinstance(r, RetrievedDocument) for r in results)

    def test_hybrid_retrieval(self, sample_documents):
        """Test hybrid retrieval strategy."""
        retriever = ContextRetriever(sample_documents, strategy="hybrid", top_k=2)
        results = retriever.retrieve_context("machine learning GPU")

        assert len(results) <= 2
        # Should retrieve ML-related documents
        assert any('machine' in r.content.lower() or 'gpu' in r.content.lower()
                   for r in results)

    def test_result_ranking(self, retriever):
        """Test results are properly ranked by relevance."""
        results = retriever.retrieve_context("Python")

        # Results should be sorted by relevance
        for i in range(len(results) - 1):
            assert results[i].rank <= results[i + 1].rank

    def test_metadata_filtering(self, retriever):
        """Test metadata-based filtering."""
        results = retriever.retrieve_context(
            "programming",
            metadata_filters={'type': 'language'}
        )

        # All results should have type='language'
        assert all(r.metadata.get('type') == 'language' for r in results)

    def test_no_results(self, retriever):
        """Test retrieval with no matching documents."""
        results = retriever.retrieve_context("xyzabc1234nonsense")
        # Should still return something or empty list
        assert isinstance(results, list)

    def test_add_documents(self, retriever):
        """Test adding new documents to store."""
        initial_count = len(retriever.document_store)
        new_docs = [{'content': 'New document', 'metadata': {'source': 'new'}}]

        retriever.add_documents(new_docs)
        assert len(retriever.document_store) == initial_count + 1

    def test_stats_tracking(self, retriever):
        """Test statistics tracking."""
        retriever.retrieve_context("test query 1")
        retriever.retrieve_context("test query 2")

        stats = retriever.get_stats()
        assert stats['queries_processed'] == 2
        assert stats['avg_relevance_score'] > 0

    def test_top_k_limit(self, sample_documents):
        """Test top_k parameter limits results."""
        retriever_k1 = ContextRetriever(sample_documents, strategy="hybrid", top_k=1)
        retriever_k3 = ContextRetriever(sample_documents, strategy="hybrid", top_k=3)

        results_k1 = retriever_k1.retrieve_context("programming")
        results_k3 = retriever_k3.retrieve_context("programming")

        assert len(results_k1) <= 1
        assert len(results_k3) <= 3


class TestRetrievedDocument:
    """Test suite for RetrievedDocument dataclass."""

    def test_document_creation(self):
        """Test RetrievedDocument initialization."""
        doc = RetrievedDocument(
            content="Sample document",
            source="test_source",
            relevance_score=0.85,
            metadata={"key": "value"},
            rank=1,
            retrieval_method="vector_similarity"
        )
        assert doc.content == "Sample document"
        assert doc.relevance_score == 0.85
        assert doc.rank == 1

    def test_relevance_score_bounds(self):
        """Test relevance scores are bounded 0-1."""
        doc = RetrievedDocument(
            content="Test",
            source="test",
            relevance_score=1.5,  # Invalid
            metadata={},
            rank=0,
            retrieval_method="test"
        )
        # Should be clamped to 1.0
        assert doc.relevance_score <= 1.0


class TestRetrievalStrategy:
    """Test suite for RetrievalStrategy enum."""

    def test_strategy_values(self):
        """Test all retrieval strategies."""
        strategies = [
            RetrievalStrategy.VECTOR_SIMILARITY,
            RetrievalStrategy.BM25,
            RetrievalStrategy.HYBRID,
        ]
        assert len(strategies) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
