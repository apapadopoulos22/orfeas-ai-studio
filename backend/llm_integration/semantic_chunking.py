"""
Semantic Chunking Module - Intelligent Document Splitting

Purpose:
    Split documents into semantically coherent chunks for RAG by:
    - Character-based fallback chunking
    - Sentence-aware splitting
    - Paragraph-based chunking
    - Semantic boundary detection
    - Overlap and metadata preservation

Performance Targets:
    - Chunking latency: <500ms per 10K chars
    - Chunk quality: High semantic coherence
    - Overlap: 10-20% for context preservation
"""

import logging
import re
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
import math

from .error_handler import (
    error_context,
    safe_execute,
    ChunkingError,
    ErrorAggregator
)
from .tracing import (
    trace_performance,
    trace_block_async,
    PerformanceTracer
)

logger = logging.getLogger(__name__)


@dataclass
class SemanticChunk:
    """A semantically coherent chunk of text."""
    content: str
    start_pos: int
    end_pos: int
    chunk_id: int
    metadata: Dict[str, Any]
    tokens_estimate: int
    semantic_score: float = 1.0  # 0.0-1.0


class SemanticChunker:
    """
    Intelligent document chunking for RAG.

    Splits documents maintaining semantic boundaries and context.
    """

    def __init__(
        self,
        chunk_size: int = 1024,
        overlap_size: int = 100,
        strategy: str = "semantic",
    ):
        """
        Initialize semantic chunker.

        Args:
            chunk_size: Target chunk size in characters
            overlap_size: Overlap between chunks in characters
            strategy: Chunking strategy (character, sentence, paragraph, semantic)
        """
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.strategy = strategy
        self.stats = {
            'documents_chunked': 0,
            'total_chunks': 0,
            'avg_chunk_size': 0,
        }
        self.error_agg = ErrorAggregator()
        self.perf_tracer = PerformanceTracer()
        logger.info(
            f"SemanticChunker initialized "
            f"(size={chunk_size}, overlap={overlap_size}, strategy={strategy})"
        )

    @trace_performance(operation='chunk_document', component='semantic_chunking')
    @error_context(component='semantic_chunking', operation='chunk_document')
    def chunk_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[SemanticChunk]:
        """
        Chunk a document using the selected strategy.

        Args:
            text: Document text to chunk
            metadata: Optional metadata to attach to chunks

        Returns:
            List of SemanticChunk objects
        """
        if not text or len(text) == 0:
            return []

        # Select chunking method
        if self.strategy == "character":
            chunks_raw = self._chunk_by_character(text)
        elif self.strategy == "sentence":
            chunks_raw = self._chunk_by_sentence(text)
        elif self.strategy == "paragraph":
            chunks_raw = self._chunk_by_paragraph(text)
        else:  # semantic (default)
            chunks_raw = self._chunk_by_semantic(text)

        # Convert to SemanticChunk objects with metadata
        chunks = []
        for i, (content, start_pos, end_pos) in enumerate(chunks_raw):
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata['source_document'] = chunk_metadata.get('source_document', 'unknown')
            chunk_metadata['chunk_number'] = i

            semantic_score = self._calculate_semantic_score(content)
            token_estimate = self._estimate_tokens(content)

            chunk = SemanticChunk(
                content=content,
                start_pos=start_pos,
                end_pos=end_pos,
                chunk_id=i,
                metadata=chunk_metadata,
                tokens_estimate=token_estimate,
                semantic_score=semantic_score,
            )
            chunks.append(chunk)

        # Update statistics
        self._update_stats(chunks)

        logger.info(
            f"Chunked document into {len(chunks)} chunks "
            f"(strategy={self.strategy}, avg_size={self.stats['avg_chunk_size']:.0f})"
        )

        return chunks

    def _chunk_by_character(self, text: str) -> List[Tuple[str, int, int]]:
        """Simple character-based chunking with overlap."""
        chunks = []
        pos = 0

        while pos < len(text):
            # Get chunk
            end = min(pos + self.chunk_size, len(text))
            chunk = text[pos:end]
            chunks.append((chunk, pos, end))

            # Move position (with overlap)
            pos += self.chunk_size - self.overlap_size

        return chunks

    def _chunk_by_sentence(self, text: str) -> List[Tuple[str, int, int]]:
        """Split by sentences while respecting chunk size."""
        # Split into sentences
        sentences = self._split_sentences(text)

        chunks = []
        current_chunk = ""
        current_start = 0

        for i, sent in enumerate(sentences):
            # Check if adding this sentence would exceed chunk size
            if current_chunk and len(current_chunk) + len(sent) > self.chunk_size:
                # Save current chunk
                start_pos = text.find(current_chunk)
                end_pos = start_pos + len(current_chunk)
                chunks.append((current_chunk.strip(), start_pos, end_pos))

                # Start new chunk with overlap
                overlap_sentences = []
                char_count = 0
                for j in range(max(0, i - 2), i):
                    if char_count < self.overlap_size:
                        overlap_sentences.append(sentences[j])
                        char_count += len(sentences[j])

                current_chunk = " ".join(overlap_sentences) + " " + sent
                current_start = len(" ".join(sentences[:i])) - len(current_chunk)
            else:
                current_chunk += " " + sent if current_chunk else sent

        # Add final chunk
        if current_chunk:
            start_pos = text.find(current_chunk)
            end_pos = start_pos + len(current_chunk)
            chunks.append((current_chunk.strip(), start_pos, end_pos))

        return chunks

    def _chunk_by_paragraph(self, text: str) -> List[Tuple[str, int, int]]:
        """Split by paragraphs while maintaining chunk size."""
        # Split into paragraphs
        paragraphs = text.split('\n\n')

        chunks = []
        current_chunk = ""
        current_start = 0

        for para in paragraphs:
            if current_chunk and len(current_chunk) + len(para) > self.chunk_size:
                # Save current chunk
                start_pos = text.find(current_chunk)
                end_pos = start_pos + len(current_chunk)
                chunks.append((current_chunk.strip(), start_pos, end_pos))
                current_chunk = para
                current_start = 0
            else:
                current_chunk += ("\n\n" + para) if current_chunk else para

        # Add final chunk
        if current_chunk:
            start_pos = text.find(current_chunk)
            end_pos = start_pos + len(current_chunk)
            chunks.append((current_chunk.strip(), start_pos, end_pos))

        return chunks

    @trace_performance(operation='chunk_by_semantic', component='semantic_chunking')
    @error_context(component='semantic_chunking', operation='chunk_by_semantic')
    def _chunk_by_semantic(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Intelligent semantic chunking.        Tries paragraph boundaries first, falls back to sentences, then characters.
        """
        # Try paragraph-based first
        paragraphs = text.split('\n\n')

        if all(len(p) <= self.chunk_size * 1.5 for p in paragraphs):
            # Paragraphs are reasonably sized, group them
            return self._chunk_paragraphs_into_groups(text, paragraphs)

        # Fall back to sentence-based
        return self._chunk_by_sentence(text)

    def _chunk_paragraphs_into_groups(
        self,
        text: str,
        paragraphs: List[str]
    ) -> List[Tuple[str, int, int]]:
        """Group paragraphs into semantic chunks."""
        chunks = []
        current_group = ""
        current_start = 0

        for para in paragraphs:
            if current_group and len(current_group) + len(para) > self.chunk_size:
                # Save current group
                start_pos = text.find(current_group)
                end_pos = start_pos + len(current_group)
                chunks.append((current_group.strip(), start_pos, end_pos))
                current_group = para
            else:
                current_group += ("\n\n" + para) if current_group else para

        if current_group:
            start_pos = text.find(current_group)
            end_pos = start_pos + len(current_group)
            chunks.append((current_group.strip(), start_pos, end_pos))

        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting on . ! ?
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s for s in sentences if s.strip()]
    @trace_performance(operation='calculate_semantic_score', component='semantic_chunking')
    @error_context(component='semantic_chunking', operation='calculate_semantic_score')
    def _calculate_semantic_score(self, text: str) -> float:
        """Calculate semantic quality score of a chunk."""
        score = 1.0

        # Penalize very short chunks
        if len(text) < 50:
            score *= 0.7

        # Penalize chunks without proper ending
        if not text.rstrip().endswith(('.', '!', '?', ')', ']', '}')):
            score *= 0.85

        # Reward chunks with good punctuation balance
        open_parens = text.count('(') + text.count('[') + text.count('{')
        close_parens = text.count(')') + text.count(']') + text.count('}')
        if open_parens == close_parens:
            score *= 1.05

        return min(1.0, score)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (approx 3-4 chars per token)."""
        return max(1, int(len(text) / 3.5))

    def _update_stats(self, chunks: List[SemanticChunk]) -> None:
        """Update statistics."""
        self.stats['documents_chunked'] += 1
        self.stats['total_chunks'] += len(chunks)

        if chunks:
            avg_size = sum(len(c.content) for c in chunks) / len(chunks)
            self.stats['avg_chunk_size'] = avg_size

    def get_stats(self) -> Dict[str, Any]:
        """Get chunking statistics."""
        return self.stats.copy()

    def reset_stats(self) -> None:
        """Reset statistics."""
        self.stats = {
            'documents_chunked': 0,
            'total_chunks': 0,
            'avg_chunk_size': 0,
        }


def chunk_text(
    text: str,
    chunk_size: int = 1024,
    overlap_size: int = 100,
    strategy: str = "semantic",
) -> List[SemanticChunk]:
    """
    Convenience function to chunk text.

    Args:
        text: Text to chunk
        chunk_size: Target chunk size
        overlap_size: Overlap between chunks
        strategy: Chunking strategy

    Returns:
        List of semantic chunks
    """
    chunker = SemanticChunker(chunk_size, overlap_size, strategy)
    return chunker.chunk_document(text)
