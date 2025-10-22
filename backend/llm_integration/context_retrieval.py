"""
Context Retrieval Module - RAG (Retrieval-Augmented Generation) Implementation

Purpose:
    Retrieve relevant context for LLM queries by:
    - Query processing and embedding
    - Vector similarity search
    - Semantic relevance ranking
    - Multi-source retrieval
    - Context aggregation and formatting

Performance Targets:
    - Semantic search: <500ms
    - Relevance ranking: <200ms
    - Context aggregation: <100ms
    - Total per-query: <1000ms
"""

import logging
import time
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import math

from .error_handler import (
    error_context,
    safe_execute,
    RetrievalError,
    ErrorAggregator
)
from .tracing import (
    trace_performance,
    trace_block_async,
    PerformanceTracer
)

logger = logging.getLogger(__name__)


class RetrievalStrategy(Enum):
    """Document retrieval strategies."""
    VECTOR_SIMILARITY = "vector_similarity"
    BM25 = "bm25"
    HYBRID = "hybrid"  # Combine vector + BM25


@dataclass
class RetrievedDocument:
    """A retrieved document with relevance score."""
    content: str
    source: str
    relevance_score: float  # 0.0-1.0
    metadata: Dict[str, Any]
    rank: int
    retrieval_method: str


class ContextRetriever:
    """
    RAG context retrieval system.

    Retrieves relevant documents for queries using multiple strategies.
    """

    def __init__(
        self,
        document_store: Optional[List[Dict[str, Any]]] = None,
        strategy: str = "hybrid",
        top_k: int = 3,
    ):
        """
        Initialize context retriever.

        Args:
            document_store: List of documents with 'content' and 'metadata' keys
            strategy: Retrieval strategy (vector_similarity, bm25, hybrid)
            top_k: Number of top documents to retrieve
        """
        self.document_store = document_store or []
        self.strategy = strategy
        self.top_k = top_k
        self.stats = {
            'queries_processed': 0,
            'avg_retrieval_time_ms': 0.0,
            'avg_relevance_score': 0.0,
        }
        self._build_indexes()
        self.error_agg = ErrorAggregator()
        self.perf_tracer = PerformanceTracer()
        logger.info(
            f"ContextRetriever initialized "
            f"(docs={len(self.document_store)}, strategy={strategy}, top_k={top_k})"
        )

    def _build_indexes(self) -> None:
        """Build search indexes for documents."""
        # Build vocabulary for BM25
        self.vocabulary = set()
        for doc in self.document_store:
            words = self._tokenize(doc.get('content', ''))
            self.vocabulary.update(words)

    @trace_performance(operation='retrieve_context', component='context_retrieval')
    @error_context(component='context_retrieval', operation='retrieve_context')
    def retrieve_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievedDocument]:
        """
        Retrieve relevant context documents for a query.

        Args:
            query: The query string
            top_k: Override default top_k
            metadata_filters: Optional metadata filters

        Returns:
            List of RetrievedDocument sorted by relevance
        """
        start_time = time.time()
        top_k = top_k or self.top_k

        # Retrieve using selected strategy
        if self.strategy == "vector_similarity":
            results = self._retrieve_vector_similarity(query, top_k)
        elif self.strategy == "bm25":
            results = self._retrieve_bm25(query, top_k)
        else:  # hybrid
            results = self._retrieve_hybrid(query, top_k)

        # Apply metadata filters if provided
        if metadata_filters:
            results = self._apply_filters(results, metadata_filters)

        # Rank and format results
        ranked = self._rank_results(results)

        # Update statistics
        retrieval_time = (time.time() - start_time) * 1000
        self._update_stats(retrieval_time, ranked)

        logger.info(
            f"Retrieved {len(ranked)} documents "
            f"(strategy={self.strategy}, time={retrieval_time:.2f}ms)"
        )

        return ranked

    @trace_performance(operation='retrieve_vector_similarity', component='context_retrieval')
    @error_context(component='context_retrieval', operation='retrieve_vector_similarity')
    def _retrieve_vector_similarity(
        self,
        query: str,
        top_k: int
    ) -> List[Tuple[int, float, str]]:
        """Retrieve using vector similarity (cosine similarity)."""
        query_vec = self._embed(query)
        scores = []

        for i, doc in enumerate(self.document_store):
            doc_vec = self._embed(doc.get('content', ''))
            similarity = self._cosine_similarity(query_vec, doc_vec)
            scores.append((i, similarity, "vector_similarity"))

        # Sort by score and get top-k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def _retrieve_bm25(self, query: str, top_k: int) -> List[Tuple[int, float, str]]:
        """Retrieve using BM25 ranking algorithm."""
        query_terms = self._tokenize(query)
        scores = []

        k1 = 1.5  # BM25 parameter
        b = 0.75  # BM25 parameter

        avg_doc_len = sum(len(self._tokenize(d.get('content', '')))
                          for d in self.document_store) / max(1, len(self.document_store))

        for i, doc in enumerate(self.document_store):
            doc_terms = self._tokenize(doc.get('content', ''))
            doc_len = len(doc_terms)

            score = 0.0
            for term in query_terms:
                freq = doc_terms.count(term)
                if freq > 0:
                    idf = math.log(len(self.document_store) / max(1,
                        sum(1 for d in self.document_store if term in self._tokenize(d.get('content', '')))))
                    numerator = freq * (k1 + 1)
                    denominator = freq + k1 * (1 - b + b * (doc_len / avg_doc_len))
                    score += idf * (numerator / denominator)

            scores.append((i, score, "bm25"))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def _retrieve_hybrid(self, query: str, top_k: int) -> List[Tuple[int, float, str]]:
        """Retrieve using hybrid strategy (vector + BM25)."""
        # Get results from both methods
        vec_results = self._retrieve_vector_similarity(query, len(self.document_store))
        bm25_results = self._retrieve_bm25(query, len(self.document_store))

        # Combine scores (average of normalized scores)
        combined_scores = {}

        # Normalize and add vector scores
        if vec_results:
            max_vec_score = max(r[1] for r in vec_results)
            for i, score, _ in vec_results:
                combined_scores[i] = (score / max_vec_score if max_vec_score > 0 else 0) * 0.5

        # Normalize and add BM25 scores
        if bm25_results:
            max_bm25_score = max(r[1] for r in bm25_results)
            for i, score, _ in bm25_results:
                existing = combined_scores.get(i, 0)
                combined_scores[i] = existing + (score / max_bm25_score if max_bm25_score > 0 else 0) * 0.5

        # Convert to list and sort
        scores = [(i, score, "hybrid") for i, score in combined_scores.items()]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    @trace_performance(operation='rank_results', component='context_retrieval')
    @error_context(component='context_retrieval', operation='rank_results')
    def _rank_results(self, results: List[Tuple[int, float, str]]) -> List[RetrievedDocument]:
        """Convert raw results to RetrievedDocument objects."""
        ranked = []

        for rank, (doc_idx, score, method) in enumerate(results):
            if doc_idx < len(self.document_store):
                doc = self.document_store[doc_idx]
                ranked.append(RetrievedDocument(
                    content=doc.get('content', ''),
                    source=doc.get('metadata', {}).get('source', f'doc_{doc_idx}'),
                    relevance_score=min(1.0, max(0.0, score)),  # Normalize to 0-1
                    metadata=doc.get('metadata', {}),
                    rank=rank,
                    retrieval_method=method,
                ))

        return ranked

    def _apply_filters(
        self,
        results: List[RetrievedDocument],
        filters: Dict[str, Any]
    ) -> List[RetrievedDocument]:
        """Apply metadata filters to results."""
        filtered = []

        for result in results:
            match = True
            for key, value in filters.items():
                if result.metadata.get(key) != value:
                    match = False
                    break
            if match:
                filtered.append(result)

        return filtered

    def _embed(self, text: str) -> List[float]:
        """Simple embedding representation (bag of words)."""
        words = self._tokenize(text)
        vec = [0.0] * len(self.vocabulary)
        vocab_list = sorted(list(self.vocabulary))

        for word in words:
            if word in self.vocabulary:
                idx = vocab_list.index(word)
                vec[idx] += 1.0

        # Normalize
        norm = math.sqrt(sum(v**2 for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]

        return vec

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) == 0 or len(vec2) == 0:
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))

        # Vectors should be normalized already, but check anyway
        norm1 = math.sqrt(sum(v**2 for v in vec1))
        norm2 = math.sqrt(sum(v**2 for v in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        return text.lower().split()

    def _update_stats(
        self,
        retrieval_time: float,
        results: List[RetrievedDocument]
    ) -> None:
        """Update retrieval statistics."""
        stats = self.stats
        stats['queries_processed'] += 1

        # Update average retrieval time
        old_avg_time = stats['avg_retrieval_time_ms']
        count = stats['queries_processed']
        stats['avg_retrieval_time_ms'] = (old_avg_time * (count - 1) + retrieval_time) / count

        # Update average relevance score
        if results:
            avg_relevance = sum(r.relevance_score for r in results) / len(results)
            old_avg_rel = stats['avg_relevance_score']
            stats['avg_relevance_score'] = (old_avg_rel * (count - 1) + avg_relevance) / count

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add new documents to the store."""
        self.document_store.extend(documents)
        self._build_indexes()
        logger.info(f"Added {len(documents)} documents (total: {len(self.document_store)})")

    def get_stats(self) -> Dict[str, Any]:
        """Get retrieval statistics."""
        return self.stats.copy()

    def reset_stats(self) -> None:
        """Reset statistics."""
        self.stats = {
            'queries_processed': 0,
            'avg_retrieval_time_ms': 0.0,
            'avg_relevance_score': 0.0,
        }


def retrieve_context(
    query: str,
    documents: List[Dict[str, Any]],
    top_k: int = 3,
    strategy: str = "hybrid",
) -> List[RetrievedDocument]:
    """
    Convenience function to retrieve context.

    Args:
        query: Query string
        documents: List of documents
        top_k: Number of top results
        strategy: Retrieval strategy

    Returns:
        List of retrieved documents
    """
    retriever = ContextRetriever(documents, strategy, top_k)
    return retriever.retrieve_context(query)
