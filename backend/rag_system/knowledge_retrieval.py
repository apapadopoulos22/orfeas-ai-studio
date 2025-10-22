"""
ORFEAS AI 2D→3D Studio - Knowledge Retrieval
=============================================
Advanced knowledge retrieval with semantic search, hybrid search, and re-ranking.

Features:
- Semantic search with dense embeddings
- Hybrid search (dense + sparse/BM25)
- Cross-encoder re-ranking
- Multi-hop retrieval for complex queries
- Query expansion and reformulation
- Retrieval quality metrics
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class SearchMode(Enum):
    """Search mode enumeration"""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    MULTI_HOP = "multi_hop"


@dataclass
class SearchQuery:
    """Search query with parameters"""
    query_text: str
    mode: SearchMode = SearchMode.HYBRID
    top_k: int = 10
    alpha: float = 0.5  # Hybrid search weight (0=keyword, 1=semantic)
    enable_reranking: bool = True
    enable_expansion: bool = False
    max_hops: int = 2  # For multi-hop retrieval


@dataclass
class RetrievalMetrics:
    """Metrics for retrieval quality"""
    precision: float
    recall: float
    f1_score: float
    mrr: float  # Mean Reciprocal Rank
    ndcg: float  # Normalized Discounted Cumulative Gain
    latency_ms: float


@dataclass
class SearchResult:
    """Single search result"""
    id: str
    content: str
    score: float
    metadata: Dict[str, Any]
    rank: int
    reranked_score: Optional[float] = None


@dataclass
class KnowledgeRetrievalResult:
    """Complete retrieval result"""
    query: str
    results: List[SearchResult]
    total_found: int
    search_mode: SearchMode
    metrics: Optional[RetrievalMetrics] = None
    expanded_queries: List[str] = field(default_factory=list)


class EmbeddingModel:
    """Embedding model wrapper"""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.dimension = 384  # Default for MiniLM

        logger.info(f"[ORFEAS-RETRIEVAL] Initializing embedding model: {model_name}")

    async def initialize(self):
        """Initialize embedding model"""
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(self.model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()

            logger.info(f"[ORFEAS-RETRIEVAL] Embedding model loaded (dim={self.dimension})")

        except Exception as e:
            logger.error(f"[ORFEAS-RETRIEVAL] Failed to load embedding model: {e}")
            raise

    async def encode(self, texts: List[str]) -> List[List[float]]:
        """Encode texts to embeddings"""
        try:
            if self.model is None:
                await self.initialize()

            embeddings = self.model.encode(texts, show_progress_bar=False)
            return embeddings.tolist()

        except Exception as e:
            logger.error(f"[ORFEAS-RETRIEVAL] Encoding failed: {e}")
            return [[0.0] * self.dimension for _ in texts]


class CrossEncoderReranker:
    """Cross-encoder for result re-ranking"""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.model = None

        logger.info(f"[ORFEAS-RETRIEVAL] Initializing cross-encoder: {model_name}")

    async def initialize(self):
        """Initialize cross-encoder model"""
        try:
            from sentence_transformers import CrossEncoder

            self.model = CrossEncoder(self.model_name)

            logger.info("[ORFEAS-RETRIEVAL] Cross-encoder loaded")

        except Exception as e:
            logger.error(f"[ORFEAS-RETRIEVAL] Failed to load cross-encoder: {e}")
            raise

    async def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: Optional[int] = None
    ) -> List[Tuple[int, float]]:
        """
        Re-rank documents using cross-encoder

        Returns:
            List of (index, score) tuples sorted by score
        """
        try:
            if self.model is None:
                await self.initialize()

            # Create query-document pairs
            pairs = [[query, doc] for doc in documents]

            # Get scores
            scores = self.model.predict(pairs)

            # Sort by score
            ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

            if top_k:
                ranked = ranked[:top_k]

            return ranked

        except Exception as e:
            logger.error(f"[ORFEAS-RETRIEVAL] Re-ranking failed: {e}")
            # Return original order with dummy scores
            return [(i, 1.0) for i in range(len(documents))]


class KnowledgeRetrieval:
    """
    Advanced knowledge retrieval system
    """

    def __init__(
        self,
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        enable_caching: bool = True
    ):
        self.embedding_model = EmbeddingModel(embedding_model_name)
        self.reranker = CrossEncoderReranker(reranker_model_name)
        self.enable_caching = enable_caching

        # Get vector database from rag_system
        from .vector_database import get_vector_db_manager
        self.vector_db = get_vector_db_manager()

        # Cache
        self.query_cache: Dict[str, KnowledgeRetrievalResult] = {}
        self.embedding_cache: Dict[str, List[float]] = {}

        # Statistics
        self.total_queries = 0
        self.cache_hits = 0
        self.total_reranks = 0

        logger.info("[ORFEAS-RETRIEVAL] KnowledgeRetrieval initialized")

    async def initialize(self):
        """Initialize all components"""
        try:
            await self.embedding_model.initialize()
            await self.reranker.initialize()
            await self.vector_db.initialize()

            logger.info("[ORFEAS-RETRIEVAL] All components initialized")

        except Exception as e:
            logger.error(f"[ORFEAS-RETRIEVAL] Initialization failed: {e}")
            raise

    async def search(
        self,
        query: SearchQuery,
        context: Optional[Dict[str, Any]] = None
    ) -> KnowledgeRetrievalResult:
        """
        Execute knowledge retrieval

        Args:
            query: Search query with parameters
            context: Additional context

        Returns:
            KnowledgeRetrievalResult with retrieved documents
        """
        import time
        start_time = time.time()

        try:
            self.total_queries += 1

            # Check cache
            if self.enable_caching:
                cached = self._check_cache(query)
                if cached:
                    self.cache_hits += 1
                    logger.info(f"[ORFEAS-RETRIEVAL] Cache hit for: {query.query_text[:50]}")
                    return cached

            # Expand query if enabled
            expanded_queries = [query.query_text]
            if query.enable_expansion:
                expanded_queries = await self._expand_query(query.query_text)

            # Execute search based on mode
            if query.mode == SearchMode.SEMANTIC:
                results = await self._semantic_search(query)
            elif query.mode == SearchMode.KEYWORD:
                results = await self._keyword_search(query)
            elif query.mode == SearchMode.HYBRID:
                results = await self._hybrid_search(query)
            elif query.mode == SearchMode.MULTI_HOP:
                results = await self._multi_hop_search(query)
            else:
                results = await self._hybrid_search(query)

            # Re-rank if enabled
            if query.enable_reranking and results:
                results = await self._rerank_results(query.query_text, results)

            # Take top K
            results = results[:query.top_k]

            # Assign ranks
            for i, result in enumerate(results, 1):
                result.rank = i

            elapsed_ms = (time.time() - start_time) * 1000

            retrieval_result = KnowledgeRetrievalResult(
                query=query.query_text,
                results=results,
                total_found=len(results),
                search_mode=query.mode,
                expanded_queries=expanded_queries if query.enable_expansion else []
            )

            # Cache result
            if self.enable_caching:
                self._cache_result(query, retrieval_result)

            logger.info(
                f"[ORFEAS-RETRIEVAL] Retrieved {len(results)} results "
                f"in {elapsed_ms:.1f}ms (mode={query.mode.value})"
            )

            return retrieval_result

        except Exception as e:
            logger.error(f"[ORFEAS-RETRIEVAL] Search failed: {e}")
            raise

    async def _semantic_search(self, query: SearchQuery) -> List[SearchResult]:
        """Semantic search using dense embeddings"""

        # Get query embedding
        query_embedding = await self._get_embedding(query.query_text)

        # Search vector database
        vector_results = await self.vector_db.execute_with_failover(
            'similarity_search',
            query_embedding=query_embedding,
            top_k=query.top_k * 2  # Retrieve more for re-ranking
        )

        # Convert to SearchResult
        search_results = []
        for i, vr in enumerate(vector_results):
            search_results.append(SearchResult(
                id=vr.id,
                content=vr.content,
                score=vr.score,
                metadata=vr.metadata,
                rank=i + 1
            ))

        return search_results

    async def _keyword_search(self, query: SearchQuery) -> List[SearchResult]:
        """Keyword search using BM25 or similar"""

        # Extract keywords
        keywords = self._extract_keywords(query.query_text)

        # Would integrate with search engine like Elasticsearch
        # For now, return empty results
        logger.warning("[ORFEAS-RETRIEVAL] Keyword search not fully implemented")

        return []

    async def _hybrid_search(self, query: SearchQuery) -> List[SearchResult]:
        """Hybrid search combining semantic and keyword"""

        # Perform both searches
        semantic_results = await self._semantic_search(query)
        keyword_results = await self._keyword_search(query)

        # Combine with weighted scores
        combined = self._combine_search_results(
            semantic_results,
            keyword_results,
            alpha=query.alpha
        )

        return combined

    async def _multi_hop_search(self, query: SearchQuery) -> List[SearchResult]:
        """Multi-hop retrieval for complex queries"""

        all_results: List[SearchResult] = []
        seen_ids: Set[str] = set()

        # First hop - initial search
        current_query = query.query_text
        first_hop = await self._semantic_search(query)

        for result in first_hop:
            if result.id not in seen_ids:
                all_results.append(result)
                seen_ids.add(result.id)

        # Additional hops
        for hop in range(1, query.max_hops):
            # Extract key entities/concepts from previous results
            hop_queries = self._extract_follow_up_queries(first_hop[:3])

            for hop_query_text in hop_queries[:2]:  # Limit follow-up queries
                hop_query = SearchQuery(
                    query_text=hop_query_text,
                    mode=SearchMode.SEMANTIC,
                    top_k=5
                )

                hop_results = await self._semantic_search(hop_query)

                for result in hop_results:
                    if result.id not in seen_ids:
                        # Adjust score based on hop distance
                        result.score *= 0.8 ** hop
                        all_results.append(result)
                        seen_ids.add(result.id)

        # Sort by score
        all_results.sort(key=lambda r: r.score, reverse=True)

        return all_results

    async def _rerank_results(
        self,
        query: str,
        results: List[SearchResult]
    ) -> List[SearchResult]:
        """Re-rank results using cross-encoder"""

        if not results:
            return results

        self.total_reranks += 1

        try:
            # Extract documents
            documents = [r.content for r in results]

            # Re-rank
            ranked = await self.reranker.rerank(query, documents)

            # Update results with reranked scores
            reranked_results = []
            for idx, score in ranked:
                result = results[idx]
                result.reranked_score = float(score)
                reranked_results.append(result)

            return reranked_results

        except Exception as e:
            logger.error(f"[ORFEAS-RETRIEVAL] Re-ranking failed: {e}")
            return results

    def _combine_search_results(
        self,
        semantic_results: List[SearchResult],
        keyword_results: List[SearchResult],
        alpha: float = 0.5
    ) -> List[SearchResult]:
        """Combine semantic and keyword results with weighted scoring"""

        # Create mapping by ID
        combined_map: Dict[str, SearchResult] = {}

        # Add semantic results
        for result in semantic_results:
            result.score = result.score * alpha
            combined_map[result.id] = result

        # Add/update with keyword results
        for result in keyword_results:
            keyword_score = result.score * (1 - alpha)

            if result.id in combined_map:
                # Update score
                combined_map[result.id].score += keyword_score
            else:
                result.score = keyword_score
                combined_map[result.id] = result

        # Sort by combined score
        combined_results = list(combined_map.values())
        combined_results.sort(key=lambda r: r.score, reverse=True)

        return combined_results

    async def _expand_query(self, query: str) -> List[str]:
        """Expand query with synonyms and related terms"""

        expanded = [query]

        # Simple expansion - would use WordNet or LLM for production
        # For now, just return original query
        logger.debug(f"[ORFEAS-RETRIEVAL] Query expansion for: {query}")

        return expanded

    def _extract_follow_up_queries(self, results: List[SearchResult]) -> List[str]:
        """Extract follow-up queries from results"""

        follow_ups = []

        for result in results:
            # Extract key phrases from content
            # Simple implementation - would use NER or other NLP
            words = result.content.split()
            if len(words) > 10:
                # Take middle section as potential follow-up
                middle = ' '.join(words[len(words)//3:2*len(words)//3])
                follow_ups.append(middle[:100])

        return follow_ups

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""

        words = text.lower().split()

        # Remove stop words
        stop_words = {
            'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for',
            'of', 'and', 'or', 'is', 'are', 'was', 'were'
        }
        keywords = [w for w in words if w not in stop_words and len(w) > 3]

        return keywords[:15]

    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text with caching"""

        # Check cache
        if text in self.embedding_cache:
            return self.embedding_cache[text]

        # Generate embedding
        embeddings = await self.embedding_model.encode([text])
        embedding = embeddings[0]

        # Cache
        self.embedding_cache[text] = embedding

        # Limit cache size
        if len(self.embedding_cache) > 10000:
            # Remove oldest 1000 entries
            oldest_keys = list(self.embedding_cache.keys())[:1000]
            for key in oldest_keys:
                del self.embedding_cache[key]

        return embedding

    def _check_cache(self, query: SearchQuery) -> Optional[KnowledgeRetrievalResult]:
        """Check query cache"""

        cache_key = f"{query.query_text}_{query.mode.value}_{query.top_k}"
        return self.query_cache.get(cache_key)

    def _cache_result(self, query: SearchQuery, result: KnowledgeRetrievalResult):
        """Cache retrieval result"""

        cache_key = f"{query.query_text}_{query.mode.value}_{query.top_k}"
        self.query_cache[cache_key] = result

        # Limit cache size
        if len(self.query_cache) > 1000:
            oldest_keys = list(self.query_cache.keys())[:100]
            for key in oldest_keys:
                del self.query_cache[key]

    def calculate_metrics(
        self,
        retrieved: List[SearchResult],
        relevant_ids: Set[str],
        k: int = 10
    ) -> RetrievalMetrics:
        """Calculate retrieval quality metrics"""

        retrieved_ids = {r.id for r in retrieved[:k]}

        # Precision and Recall
        true_positives = len(retrieved_ids.intersection(relevant_ids))
        precision = true_positives / k if k > 0 else 0.0
        recall = true_positives / len(relevant_ids) if relevant_ids else 0.0

        # F1 Score
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # Mean Reciprocal Rank
        mrr = 0.0
        for i, result in enumerate(retrieved[:k], 1):
            if result.id in relevant_ids:
                mrr = 1.0 / i
                break

        # Normalized Discounted Cumulative Gain
        dcg = 0.0
        idcg = sum(1.0 / np.log2(i + 2) for i in range(min(len(relevant_ids), k)))

        for i, result in enumerate(retrieved[:k], 1):
            if result.id in relevant_ids:
                dcg += 1.0 / np.log2(i + 1)

        ndcg = dcg / idcg if idcg > 0 else 0.0

        return RetrievalMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1,
            mrr=mrr,
            ndcg=ndcg,
            latency_ms=0.0  # Set externally
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get retrieval statistics"""

        cache_hit_rate = (self.cache_hits / self.total_queries * 100) if self.total_queries > 0 else 0

        return {
            'total_queries': self.total_queries,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
            'total_reranks': self.total_reranks,
            'query_cache_size': len(self.query_cache),
            'embedding_cache_size': len(self.embedding_cache)
        }


# Global knowledge retrieval instance
_knowledge_retrieval: Optional[KnowledgeRetrieval] = None


def get_knowledge_retrieval() -> KnowledgeRetrieval:
    """Get global knowledge retrieval instance"""
    global _knowledge_retrieval
    if _knowledge_retrieval is None:
        _knowledge_retrieval = KnowledgeRetrieval()
    return _knowledge_retrieval
