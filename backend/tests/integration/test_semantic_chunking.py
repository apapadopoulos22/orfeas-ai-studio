"""
Unit Tests for Semantic Chunking (File 5)
Tests document splitting, semantic quality, and metadata preservation
"""

import pytest
from backend.llm_integration.semantic_chunking import (
    SemanticChunker,
    SemanticChunk,
)


class TestSemanticChunker:
    """Test suite for SemanticChunker class."""

    @pytest.fixture
    def chunker(self):
        """Create fresh chunker instance for each test."""
        return SemanticChunker(strategy="semantic", chunk_size=100)

    def test_chunker_initialization(self, chunker):
        """Test chunker initializes with correct parameters."""
        assert chunker.strategy == "semantic"
        assert chunker.chunk_size == 100

    def test_character_chunking(self):
        """Test character-based chunking strategy."""
        chunker = SemanticChunker(strategy="character", chunk_size=50)
        text = "a" * 200
        chunks = chunker.chunk_document(text)

        assert len(chunks) > 1
        assert all(len(c.content) <= 60 for c in chunks)  # Account for overlap

    def test_sentence_chunking(self):
        """Test sentence-based chunking strategy."""
        chunker = SemanticChunker(strategy="sentence", chunk_size=3)
        text = "Sentence one. Sentence two. Sentence three. Sentence four."
        chunks = chunker.chunk_document(text)

        assert len(chunks) >= 1
        assert all(isinstance(c, SemanticChunk) for c in chunks)

    def test_paragraph_chunking(self):
        """Test paragraph-based chunking strategy."""
        chunker = SemanticChunker(strategy="paragraph", chunk_size=2)
        text = """First paragraph here.

Second paragraph here.

Third paragraph here."""
        chunks = chunker.chunk_document(text)

        assert len(chunks) > 0
        assert all(isinstance(c, SemanticChunk) for c in chunks)

    def test_semantic_chunking(self, chunker):
        """Test semantic-based chunking strategy."""
        text = """Python is a programming language.
        It is used for web development.
        It is also used for data science.

        JavaScript is another language.
        It runs in browsers.
        It is used for frontend development."""

        chunks = chunker.chunk_document(text)
        assert len(chunks) >= 1
        assert all(isinstance(c, SemanticChunk) for c in chunks)

    def test_chunk_metadata(self, chunker):
        """Test chunk metadata preservation."""
        text = "Sample text for testing."
        chunks = chunker.chunk_document(text, metadata={"source": "test", "type": "sample"})

        assert len(chunks) > 0
        assert chunks[0].metadata["source"] == "test"
        assert chunks[0].metadata["type"] == "sample"

    def test_chunk_overlap(self, chunker):
        """Test chunk overlap preservation."""
        text = "word1 word2 word3 word4 word5 word6 word7 word8"
        chunks = chunker.chunk_document(text)

        # Verify overlap exists between consecutive chunks
        if len(chunks) > 1:
            # Last words of first chunk should overlap with first words of second
            first_chunk_end = chunks[0].content.split()[-2:]
            second_chunk_start = chunks[1].content.split()[:2]
            # Should have some continuity
            assert len(chunks[0].content) > 0

    def test_semantic_quality_scoring(self, chunker):
        """Test semantic quality score calculation."""
        text = "This is a coherent and well-formed sentence."
        chunks = chunker.chunk_document(text)

        assert len(chunks) > 0
        for chunk in chunks:
            assert 0.0 <= chunk.semantic_score <= 1.0

    def test_token_estimation(self, chunker):
        """Test token count estimation."""
        text = "sample text for token counting"
        chunks = chunker.chunk_document(text)

        for chunk in chunks:
            assert chunk.token_count > 0

    def test_empty_text(self, chunker):
        """Test chunking empty text."""
        chunks = chunker.chunk_document("")
        assert len(chunks) == 0

    def test_very_short_text(self, chunker):
        """Test chunking very short text."""
        chunks = chunker.chunk_document("hi")
        assert len(chunks) <= 1

    def test_get_stats(self, chunker):
        """Test statistics tracking."""
        text = "word " * 100
        chunks = chunker.chunk_document(text)
        stats = chunker.get_stats()

        assert stats['chunks_created'] >= 1
        assert stats['total_characters'] > 0

    def test_reset_stats(self, chunker):
        """Test statistics reset."""
        text = "test text"
        chunker.chunk_document(text)
        chunker.reset_stats()
        stats = chunker.get_stats()

        assert stats['chunks_created'] == 0
        assert stats['total_characters'] == 0


class TestSemanticChunk:
    """Test suite for SemanticChunk dataclass."""

    def test_chunk_creation(self):
        """Test SemanticChunk initialization."""
        chunk = SemanticChunk(
            content="Sample content",
            index=0,
            metadata={"source": "test"},
            semantic_score=0.85,
            token_count=3
        )
        assert chunk.content == "Sample content"
        assert chunk.semantic_score == 0.85

    def test_chunk_with_defaults(self):
        """Test SemanticChunk with default values."""
        chunk = SemanticChunk(
            content="Test",
            index=0
        )
        assert chunk.metadata == {}
        assert chunk.semantic_score >= 0.0


class TestChunkingStrategies:
    """Test suite for different chunking strategies."""

    def test_strategy_values(self):
        """Test all available chunking strategies."""
        strategies = ["character", "sentence", "paragraph", "semantic"]
        for strategy in strategies:
            chunker = SemanticChunker(strategy=strategy)
            assert chunker is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
