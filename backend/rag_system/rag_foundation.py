"""
ORFEAS AI 2D→3D Studio - RAG Foundation
========================================
Core Retrieval-Augmented Generation architecture for knowledge enhancement.

Features:
- Multi-source knowledge retrieval
- Semantic search and ranking
- Context enhancement for LLM prompts
- Citation and source tracking
- Knowledge graph integration
- Hybrid retrieval (vector + keyword)
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class RetrievalMode(Enum):
    """Knowledge retrieval modes"""
    VECTOR_ONLY = "vector_only"
    KEYWORD_ONLY = "keyword_only"
    HYBRID = "hybrid"
    GRAPH_TRAVERSAL = "graph_traversal"


class RerankingStrategy(Enum):
    """Re-ranking strategies for retrieved documents"""
    RELEVANCE = "relevance"
    RECENCY = "recency"
    DIVERSITY = "diversity"
    AUTHORITY = "authority"
    COMBINED = "combined"


@dataclass
class Document:
    """Represents a knowledge document"""
    id: str
    content: str
    metadata: Dict[str, Any]
    source: str
    created_at: datetime
    embeddings: Optional[List[float]] = None
    score: float = 0.0


@dataclass
class RetrievalQuery:
    """Query for knowledge retrieval"""
    query_text: str
    mode: RetrievalMode = RetrievalMode.HYBRID
    top_k: int = 5
    min_score: float = 0.7
    filters: Dict[str, Any] = field(default_factory=dict)
    reranking: RerankingStrategy = RerankingStrategy.COMBINED


@dataclass
class RetrievalResult:
    """Result from knowledge retrieval"""
    query: str
    documents: List[Document]
    retrieval_time_ms: float
    total_candidates: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnhancedPrompt:
    """Prompt enhanced with retrieved knowledge"""
    original_prompt: str
    enhanced_prompt: str
    retrieved_documents: List[Document]
    citations: List[str]
    confidence: float


class RAGFoundation:
    """
    Core RAG system for knowledge-enhanced generation
    """

    def __init__(
        self,
        vector_db_type: str = "pinecone",
        enable_graph: bool = True,
        enable_caching: bool = True
    ):
        self.vector_db_type = vector_db_type
        self.enable_graph = enable_graph
        self.enable_caching = enable_caching

        # Components (to be initialized)
        self.vector_db = None
        self.knowledge_graph = None
        self.embedding_model = None

        # Configuration
        self.default_top_k = 5
        self.min_relevance_score = 0.7
        self.max_context_length = 4000

        # Cache
        self.query_cache: Dict[str, RetrievalResult] = {}
        self.cache_ttl = 3600  # 1 hour

        # Statistics
        self.total_queries = 0
        self.cache_hits = 0
        self.total_documents_retrieved = 0

        logger.info(
            f"[ORFEAS-RAG] RAG Foundation initialized "
            f"(vector_db={vector_db_type}, graph={enable_graph})"
        )

    async def initialize(self):
        """Initialize RAG components"""
        try:
            # Initialize vector database
            await self._initialize_vector_db()

            # Initialize knowledge graph if enabled
            if self.enable_graph:
                await self._initialize_knowledge_graph()

            # Initialize embedding model
            await self._initialize_embedding_model()

            logger.info("[ORFEAS-RAG] All components initialized successfully")

        except Exception as e:
            logger.error(f"[ORFEAS-RAG] Initialization failed: {e}")
            raise

    async def retrieve_knowledge(
        self,
        query: RetrievalQuery,
        context: Optional[Dict[str, Any]] = None
    ) -> RetrievalResult:
        """
        Retrieve relevant knowledge for query

        Args:
            query: Retrieval query with parameters
            context: Additional context for retrieval

        Returns:
            RetrievalResult with retrieved documents
        """
        import time
        start_time = time.time()

        try:
            self.total_queries += 1

            # Check cache
            if self.enable_caching:
                cached_result = self._check_cache(query)
                if cached_result:
                    self.cache_hits += 1
                    logger.info(f"[ORFEAS-RAG] Cache hit for query: {query.query_text[:50]}")
                    return cached_result

            # Retrieve based on mode
            if query.mode == RetrievalMode.VECTOR_ONLY:
                documents = await self._vector_retrieval(query)
            elif query.mode == RetrievalMode.KEYWORD_ONLY:
                documents = await self._keyword_retrieval(query)
            elif query.mode == RetrievalMode.HYBRID:
                documents = await self._hybrid_retrieval(query)
            elif query.mode == RetrievalMode.GRAPH_TRAVERSAL:
                documents = await self._graph_retrieval(query)
            else:
                documents = await self._hybrid_retrieval(query)

            # Apply filters
            if query.filters:
                documents = self._apply_filters(documents, query.filters)

            # Re-rank documents
            documents = await self._rerank_documents(documents, query)

            # Take top K
            documents = documents[:query.top_k]

            # Filter by min score
            documents = [d for d in documents if d.score >= query.min_score]

            elapsed_ms = (time.time() - start_time) * 1000

            result = RetrievalResult(
                query=query.query_text,
                documents=documents,
                retrieval_time_ms=elapsed_ms,
                total_candidates=len(documents)
            )

            # Cache result
            if self.enable_caching:
                self._cache_result(query, result)

            self.total_documents_retrieved += len(documents)

            logger.info(
                f"[ORFEAS-RAG] Retrieved {len(documents)} documents "
                f"in {elapsed_ms:.1f}ms"
            )

            return result

        except Exception as e:
            logger.error(f"[ORFEAS-RAG] Retrieval failed: {e}")
            raise

    async def enhance_prompt(
        self,
        original_prompt: str,
        retrieval_query: Optional[RetrievalQuery] = None,
        max_context_tokens: int = 4000
    ) -> EnhancedPrompt:
        """
        Enhance prompt with retrieved knowledge

        Args:
            original_prompt: Original user prompt
            retrieval_query: Optional custom retrieval query
            max_context_tokens: Maximum tokens for context

        Returns:
            EnhancedPrompt with knowledge context
        """
        try:
            # Create retrieval query if not provided
            if retrieval_query is None:
                retrieval_query = RetrievalQuery(
                    query_text=original_prompt,
                    mode=RetrievalMode.HYBRID,
                    top_k=5
                )

            # Retrieve relevant knowledge
            retrieval_result = await self.retrieve_knowledge(retrieval_query)

            # Build enhanced prompt
            enhanced_prompt = self._build_enhanced_prompt(
                original_prompt,
                retrieval_result.documents,
                max_context_tokens
            )

            # Generate citations
            citations = self._generate_citations(retrieval_result.documents)

            # Calculate confidence
            confidence = self._calculate_confidence(retrieval_result.documents)

            return EnhancedPrompt(
                original_prompt=original_prompt,
                enhanced_prompt=enhanced_prompt,
                retrieved_documents=retrieval_result.documents,
                citations=citations,
                confidence=confidence
            )

        except Exception as e:
            logger.error(f"[ORFEAS-RAG] Prompt enhancement failed: {e}")

            # Return original prompt on failure
            return EnhancedPrompt(
                original_prompt=original_prompt,
                enhanced_prompt=original_prompt,
                retrieved_documents=[],
                citations=[],
                confidence=0.0
            )

    async def _vector_retrieval(self, query: RetrievalQuery) -> List[Document]:
        """Retrieve using vector similarity search"""

        if self.vector_db is None:
            logger.warning("[ORFEAS-RAG] Vector DB not initialized")
            return []

        # Get query embedding
        query_embedding = await self._get_embedding(query.query_text)

        # Search vector database
        results = await self.vector_db.similarity_search(
            query_embedding,
            top_k=query.top_k * 2,  # Retrieve more for reranking
            namespace=query.filters.get('namespace')
        )

        return results

    async def _keyword_retrieval(self, query: RetrievalQuery) -> List[Document]:
        """Retrieve using keyword/BM25 search"""

        # Extract keywords from query
        keywords = self._extract_keywords(query.query_text)

        # Perform keyword search (would integrate with search engine)
        # For now, return empty list
        logger.warning("[ORFEAS-RAG] Keyword search not yet implemented")
        return []

    async def _hybrid_retrieval(self, query: RetrievalQuery) -> List[Document]:
        """Retrieve using hybrid vector + keyword search"""

        # Perform both retrievals
        vector_docs = await self._vector_retrieval(query)
        keyword_docs = await self._keyword_retrieval(query)

        # Combine and deduplicate
        all_docs = self._merge_results(vector_docs, keyword_docs)

        return all_docs

    async def _graph_retrieval(self, query: RetrievalQuery) -> List[Document]:
        """Retrieve using knowledge graph traversal"""

        if self.knowledge_graph is None:
            logger.warning("[ORFEAS-RAG] Knowledge graph not initialized")
            return await self._vector_retrieval(query)

        # Find related entities in knowledge graph
        related_docs = await self.knowledge_graph.find_related(
            query.query_text,
            max_depth=2
        )

        return related_docs

    async def _rerank_documents(
        self,
        documents: List[Document],
        query: RetrievalQuery
    ) -> List[Document]:
        """Re-rank retrieved documents"""

        if query.reranking == RerankingStrategy.RELEVANCE:
            # Already sorted by relevance from retrieval
            return documents

        elif query.reranking == RerankingStrategy.RECENCY:
            # Sort by creation time
            return sorted(documents, key=lambda d: d.created_at, reverse=True)

        elif query.reranking == RerankingStrategy.DIVERSITY:
            # Maximize diversity in results
            return self._diversify_results(documents)

        elif query.reranking == RerankingStrategy.AUTHORITY:
            # Sort by authority/trust score
            return sorted(
                documents,
                key=lambda d: d.metadata.get('authority', 0.5),
                reverse=True
            )

        elif query.reranking == RerankingStrategy.COMBINED:
            # Combine multiple signals
            return self._combined_reranking(documents, query)

        return documents

    def _combined_reranking(
        self,
        documents: List[Document],
        query: RetrievalQuery
    ) -> List[Document]:
        """Re-rank using combined signals"""

        for doc in documents:
            # Relevance score (already set)
            relevance_score = doc.score

            # Recency score
            age_days = (datetime.utcnow() - doc.created_at).days
            recency_score = 1.0 / (1.0 + age_days / 30)  # Decay over 30 days

            # Authority score
            authority_score = doc.metadata.get('authority', 0.5)

            # Combined score
            doc.score = (
                relevance_score * 0.5 +
                recency_score * 0.2 +
                authority_score * 0.3
            )

        return sorted(documents, key=lambda d: d.score, reverse=True)

    def _diversify_results(self, documents: List[Document]) -> List[Document]:
        """Maximize diversity in result set"""

        if len(documents) <= 1:
            return documents

        diversified = [documents[0]]  # Start with top result
        remaining = documents[1:]

        while remaining and len(diversified) < len(documents):
            # Find most different from current set
            max_diversity = -1
            best_doc = None

            for doc in remaining:
                avg_similarity = sum(
                    self._calculate_similarity(doc, d) for d in diversified
                ) / len(diversified)

                diversity = 1.0 - avg_similarity

                if diversity > max_diversity:
                    max_diversity = diversity
                    best_doc = doc

            if best_doc:
                diversified.append(best_doc)
                remaining.remove(best_doc)

        return diversified

    def _calculate_similarity(self, doc1: Document, doc2: Document) -> float:
        """Calculate similarity between two documents"""

        # Simple content-based similarity
        # In production, would use embeddings
        words1 = set(doc1.content.lower().split())
        words2 = set(doc2.content.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def _build_enhanced_prompt(
        self,
        original_prompt: str,
        documents: List[Document],
        max_tokens: int
    ) -> str:
        """Build enhanced prompt with retrieved context"""

        if not documents:
            return original_prompt

        # Build context from documents
        context_parts = []
        total_tokens = 0

        for i, doc in enumerate(documents, 1):
            # Estimate tokens (rough approximation)
            doc_tokens = len(doc.content.split()) * 1.3

            if total_tokens + doc_tokens > max_tokens:
                break

            context_part = f"[Source {i}] {doc.content}"
            context_parts.append(context_part)
            total_tokens += doc_tokens

        # Build enhanced prompt
        context_text = "\n\n".join(context_parts)

        enhanced = f"""Based on the following context, please answer the question.

CONTEXT:
{context_text}

QUESTION:
{original_prompt}

Please provide a comprehensive answer citing the relevant sources."""

        return enhanced

    def _generate_citations(self, documents: List[Document]) -> List[str]:
        """Generate citations for retrieved documents"""

        citations = []

        for i, doc in enumerate(documents, 1):
            citation = f"[{i}] {doc.metadata.get('title', 'Untitled')} - {doc.source}"
            citations.append(citation)

        return citations

    def _calculate_confidence(self, documents: List[Document]) -> float:
        """Calculate confidence in retrieved knowledge"""

        if not documents:
            return 0.0

        # Average relevance score
        avg_score = sum(d.score for d in documents) / len(documents)

        # Boost for multiple high-quality sources
        source_diversity = len(set(d.source for d in documents))
        diversity_boost = min(source_diversity / 5.0, 0.2)

        confidence = min(avg_score + diversity_boost, 1.0)

        return confidence

    def _apply_filters(
        self,
        documents: List[Document],
        filters: Dict[str, Any]
    ) -> List[Document]:
        """Apply metadata filters to documents"""

        filtered = []

        for doc in documents:
            match = True

            for key, value in filters.items():
                if key not in doc.metadata:
                    match = False
                    break

                if doc.metadata[key] != value:
                    match = False
                    break

            if match:
                filtered.append(doc)

        return filtered

    def _merge_results(
        self,
        vector_docs: List[Document],
        keyword_docs: List[Document]
    ) -> List[Document]:
        """Merge and deduplicate results from multiple retrievals"""

        # Deduplicate by document ID
        seen_ids = set()
        merged = []

        # Interleave results
        max_len = max(len(vector_docs), len(keyword_docs))

        for i in range(max_len):
            if i < len(vector_docs):
                doc = vector_docs[i]
                if doc.id not in seen_ids:
                    seen_ids.add(doc.id)
                    merged.append(doc)

            if i < len(keyword_docs):
                doc = keyword_docs[i]
                if doc.id not in seen_ids:
                    seen_ids.add(doc.id)
                    merged.append(doc)

        return merged

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""

        # Simple keyword extraction
        # In production, would use NLP library
        words = text.lower().split()

        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or'}
        keywords = [w for w in words if w not in stop_words and len(w) > 3]

        return keywords[:10]  # Top 10 keywords

    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text"""

        if self.embedding_model is None:
            # Return dummy embedding
            return [0.0] * 1536

        return await self.embedding_model.encode(text)

    def _check_cache(self, query: RetrievalQuery) -> Optional[RetrievalResult]:
        """Check cache for query result"""

        cache_key = f"{query.query_text}_{query.mode.value}_{query.top_k}"
        return self.query_cache.get(cache_key)

    def _cache_result(self, query: RetrievalQuery, result: RetrievalResult):
        """Cache query result"""

        cache_key = f"{query.query_text}_{query.mode.value}_{query.top_k}"
        self.query_cache[cache_key] = result

        # Simple cache eviction (remove old entries)
        if len(self.query_cache) > 1000:
            # Remove oldest 100 entries
            oldest_keys = list(self.query_cache.keys())[:100]
            for key in oldest_keys:
                del self.query_cache[key]

    async def _initialize_vector_db(self):
        """Initialize vector database connection"""

        logger.info(f"[ORFEAS-RAG] Initializing vector database: {self.vector_db_type}")

        # Import appropriate vector DB
        if self.vector_db_type == "pinecone":
            from .vector_database import PineconeVectorDB
            self.vector_db = PineconeVectorDB()
        elif self.vector_db_type == "weaviate":
            from .vector_database import WeaviateVectorDB
            self.vector_db = WeaviateVectorDB()
        else:
            logger.warning(f"[ORFEAS-RAG] Unknown vector DB: {self.vector_db_type}")

    async def _initialize_knowledge_graph(self):
        """Initialize knowledge graph connection"""

        logger.info("[ORFEAS-RAG] Initializing knowledge graph")

        # Would initialize Neo4j or similar
        # For now, just log
        self.knowledge_graph = None

    async def _initialize_embedding_model(self):
        """Initialize embedding model"""

        logger.info("[ORFEAS-RAG] Initializing embedding model")

        # Would load sentence transformer or similar
        # For now, just log
        self.embedding_model = None

    def get_statistics(self) -> Dict[str, Any]:
        """Get RAG system statistics"""

        cache_hit_rate = (self.cache_hits / self.total_queries * 100) if self.total_queries > 0 else 0

        return {
            'total_queries': self.total_queries,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
            'total_documents_retrieved': self.total_documents_retrieved,
            'avg_docs_per_query': self.total_documents_retrieved / self.total_queries if self.total_queries > 0 else 0,
            'cache_size': len(self.query_cache)
        }


# Global RAG instance
_rag_instance: Optional[RAGFoundation] = None


def get_rag_foundation() -> RAGFoundation:
    """Get global RAG foundation instance"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGFoundation()
    return _rag_instance
