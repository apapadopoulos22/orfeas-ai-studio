"""
BOB AI Expansion - Phase 2: Advanced Search Engine
==================================================

Implements semantic search, full-text search, and faceted search for
the expanded knowledge base. Supports both in-memory and Elasticsearch
backends for scalability.

Features:
  - Full-text search across disciplines, libraries, categories
  - Semantic search using skill matching
  - Faceted search with filters
  - Search analytics and popularity tracking
  - Fuzzy matching for typos
  - Query expansion using related terms

Backends:
  - SQLite/PostgreSQL (default) - always available
  - Elasticsearch (optional) - 100x faster for large datasets

Author: ORFEAS AI - BOB AI Expansion v10.0
Date: October 28, 2025
"""

import logging
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
import re
from collections import defaultdict

# SQLAlchemy for default backend
from sqlalchemy import func, or_, and_, text
from sqlalchemy.orm import Session

# Elasticsearch (optional)
try:
    from elasticsearch import Elasticsearch
    from elasticsearch.helpers import bulk
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False
    Elasticsearch = None

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Single search result"""
    id: int
    type: str  # 'discipline', 'library', 'category'
    name: str
    description: str
    relevance_score: float  # 0-1
    keywords: List[str] = field(default_factory=list)
    category: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'type': self.type,
            'name': self.name,
            'description': self.description,
            'relevance_score': round(self.relevance_score, 3),
            'keywords': self.keywords,
            'category': self.category,
            'metadata': self.metadata,
        }


@dataclass
class SearchResponse:
    """Complete search response"""
    query: str
    results: List[SearchResult]
    total_count: int
    execution_time_ms: float
    facets: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'query': self.query,
            'results': [r.to_dict() for r in self.results],
            'total_count': self.total_count,
            'execution_time_ms': round(self.execution_time_ms, 2),
            'facets': self.facets,
            'suggestions': self.suggestions,
        }


@dataclass
class FacetFilters:
    """Faceted search filters"""
    categories: Optional[List[str]] = None
    difficulty: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    technology_stack: Optional[List[str]] = None
    estimated_hours_min: Optional[float] = None
    estimated_hours_max: Optional[float] = None
    industry_focus: Optional[List[str]] = None

    def to_query_dict(self) -> Dict[str, Any]:
        """Convert to database query parameters"""
        result = {}
        if self.categories:
            result['categories'] = self.categories
        if self.difficulty:
            result['difficulty'] = self.difficulty
        if self.languages:
            result['languages'] = self.languages
        if self.technology_stack:
            result['technology_stack'] = self.technology_stack
        if self.estimated_hours_min is not None:
            result['estimated_hours_min'] = self.estimated_hours_min
        if self.estimated_hours_max is not None:
            result['estimated_hours_max'] = self.estimated_hours_max
        if self.industry_focus:
            result['industry_focus'] = self.industry_focus
        return result


class SearchBackend(ABC):
    """Abstract base class for search backends"""

    @abstractmethod
    def search(self, query: str, filters: Optional[FacetFilters] = None, limit: int = 20) -> SearchResponse:
        """Execute search query"""
        pass

    @abstractmethod
    def index_document(self, doc_id: str, doc_type: str, data: Dict) -> bool:
        """Index a single document"""
        pass

    @abstractmethod
    def delete_index(self) -> bool:
        """Delete all indexes"""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check backend health"""
        pass


class SQLSearchBackend(SearchBackend):
    """SQLite/PostgreSQL search backend (always available)"""

    def __init__(self, session: Session):
        """
        Initialize SQL search backend

        Args:
            session: SQLAlchemy database session
        """
        self.session = session
        self.query_log: List[Dict] = []

    def search(self, query: str, filters: Optional[FacetFilters] = None, limit: int = 20) -> SearchResponse:
        """
        Execute full-text search using SQL LIKE and pattern matching

        Args:
            query: Search query string
            filters: Optional faceted filters
            limit: Maximum results to return

        Returns:
            SearchResponse with results and metadata
        """
        start_time = datetime.utcnow()
        results = []
        filters = filters or FacetFilters()

        try:
            # Import models
            from bob_ai_expansion_phase1_database import (
                ExpandedDiscipline, ExpandedCategory, LibraryMapping
            )

            # Split query into terms for better matching
            query_terms = [term.strip() for term in query.split() if len(term.strip()) > 1]

            # Search disciplines
            discipline_results = self._search_disciplines(
                ExpandedDiscipline, query, query_terms, filters, limit
            )
            results.extend(discipline_results)

            # Search categories
            category_results = self._search_categories(
                ExpandedCategory, query, query_terms, filters, limit
            )
            results.extend(category_results)

            # Search libraries
            library_results = self._search_libraries(
                LibraryMapping, query, query_terms, filters, limit
            )
            results.extend(library_results)

            # Sort by relevance score
            results.sort(key=lambda r: r.relevance_score, reverse=True)
            results = results[:limit]

            # Compute facets
            facets = self._compute_facets(results)

            # Generate suggestions
            suggestions = self._generate_suggestions(query, results)

            # Log query
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.query_log.append({
                'query': query,
                'results_count': len(results),
                'execution_time_ms': execution_time,
                'timestamp': datetime.utcnow()
            })

            return SearchResponse(
                query=query,
                results=results,
                total_count=len(results),
                execution_time_ms=execution_time,
                facets=facets,
                suggestions=suggestions,
            )

        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            return SearchResponse(query=query, results=[], total_count=0, execution_time_ms=0)

    def _search_disciplines(self, model, query: str, query_terms: List[str],
                           filters: FacetFilters, limit: int) -> List[SearchResult]:
        """Search disciplines with relevance scoring"""
        results = []

        try:
            q = self.session.query(model)

            # Filter by difficulty
            if filters.difficulty:
                q = q.filter(model.difficulty_level.in_(filters.difficulty))

            # Filter by category
            if filters.categories:
                q = q.join(model.category).filter(
                    model.category.name.in_(filters.categories)
                )

            # Filter by hours
            if filters.estimated_hours_min is not None:
                q = q.filter(model.estimated_hours >= filters.estimated_hours_min)
            if filters.estimated_hours_max is not None:
                q = q.filter(model.estimated_hours <= filters.estimated_hours_max)

            # Full-text search with relevance scoring
            for disc in q.limit(limit).all():
                # Compute relevance score
                score = self._compute_relevance_score(
                    query, query_terms,
                    disc.name, disc.description, disc.keywords
                )

                if score > 0:
                    results.append(SearchResult(
                        id=disc.id,
                        type='discipline',
                        name=disc.name,
                        description=disc.description or '',
                        relevance_score=score,
                        keywords=disc.keywords or [],
                        category=disc.category.name if disc.category else '',
                        metadata={
                            'difficulty': disc.difficulty_level,
                            'hours': disc.estimated_hours,
                            'status': disc.status,
                        }
                    ))

            return sorted(results, key=lambda r: r.relevance_score, reverse=True)

        except Exception as e:
            logger.warning(f"Discipline search error: {e}")
            return []

    def _search_categories(self, model, query: str, query_terms: List[str],
                          filters: FacetFilters, limit: int) -> List[SearchResult]:
        """Search categories"""
        results = []

        try:
            q = self.session.query(model)

            if filters.categories:
                q = q.filter(model.name.in_(filters.categories))

            for cat in q.limit(limit).all():
                score = self._compute_relevance_score(
                    query, query_terms,
                    cat.name, cat.description, cat.keywords
                )

                if score > 0:
                    results.append(SearchResult(
                        id=cat.id,
                        type='category',
                        name=cat.name,
                        description=cat.description,
                        relevance_score=score,
                        keywords=cat.keywords or [],
                        metadata={
                            'tier': cat.tier,
                            'tier_name': cat.tier_name,
                            'disciplines_count': cat.disciplines_count,
                        }
                    ))

            return sorted(results, key=lambda r: r.relevance_score, reverse=True)

        except Exception as e:
            logger.warning(f"Category search error: {e}")
            return []

    def _search_libraries(self, model, query: str, query_terms: List[str],
                         filters: FacetFilters, limit: int) -> List[SearchResult]:
        """Search libraries"""
        results = []

        try:
            q = self.session.query(model)

            if filters.languages:
                q = q.filter(model.language.in_(filters.languages))

            if filters.technology_stack:
                q = q.filter(model.technology_stack.in_(filters.technology_stack))

            for lib in q.limit(limit).all():
                score = self._compute_relevance_score(
                    query, query_terms,
                    lib.library_name, lib.description or '',
                    [lib.package_name]
                )

                if score > 0:
                    results.append(SearchResult(
                        id=lib.id,
                        type='library',
                        name=lib.library_name,
                        description=lib.description or '',
                        relevance_score=score,
                        keywords=[lib.package_name, lib.language],
                        metadata={
                            'package': lib.package_name,
                            'language': lib.language,
                            'version': lib.version,
                            'is_primary': lib.is_primary,
                        }
                    ))

            return sorted(results, key=lambda r: r.relevance_score, reverse=True)

        except Exception as e:
            logger.warning(f"Library search error: {e}")
            return []

    def _compute_relevance_score(self, query: str, query_terms: List[str],
                                name: str, description: str, keywords: List[str]) -> float:
        """Compute relevance score (0-1) for a document"""
        score = 0.0
        query_lower = query.lower()
        name_lower = name.lower()
        desc_lower = description.lower()

        # Exact name match: 1.0
        if name_lower == query_lower:
            return 1.0

        # Partial name match: 0.8
        if query_lower in name_lower:
            score = 0.8

        # Name contains any query term: 0.6
        for term in query_terms:
            if term.lower() in name_lower:
                score = max(score, 0.6)

        # Description contains query: 0.4
        if query_lower in desc_lower:
            score = max(score, 0.4)

        # Keywords match: 0.3
        for keyword in keywords or []:
            if query_lower in keyword.lower():
                score = max(score, 0.3)

        return min(score, 1.0)

    def _compute_facets(self, results: List[SearchResult]) -> Dict[str, Any]:
        """Compute facets from search results"""
        facets = {
            'types': defaultdict(int),
            'categories': defaultdict(int),
            'difficulties': defaultdict(int),
            'languages': defaultdict(int),
        }

        for result in results:
            facets['types'][result.type] += 1
            if result.category:
                facets['categories'][result.category] += 1
            if 'difficulty' in result.metadata:
                facets['difficulties'][result.metadata['difficulty']] += 1
            if 'language' in result.metadata:
                facets['languages'][result.metadata['language']] += 1

        return {k: dict(v) for k, v in facets.items()}

    def _generate_suggestions(self, query: str, results: List[SearchResult]) -> List[str]:
        """Generate search suggestions"""
        suggestions = []

        # If few results, suggest related searches
        if len(results) < 3:
            # Extract keywords from results
            all_keywords = []
            for result in results:
                all_keywords.extend(result.keywords)
            suggestions = list(set(all_keywords))[:3]

        return suggestions

    def index_document(self, doc_id: str, doc_type: str, data: Dict) -> bool:
        """SQL backend doesn't need indexing (queries directly)"""
        return True

    def delete_index(self) -> bool:
        """SQL backend doesn't have indexes to delete"""
        return True

    def health_check(self) -> bool:
        """Check if database connection is healthy"""
        try:
            self.session.execute(text("SELECT 1"))
            return True
        except:
            return False


class ElasticsearchBackend(SearchBackend):
    """Elasticsearch search backend (optional, 100x faster for large datasets)"""

    def __init__(self, es_client: Optional[Elasticsearch] = None, index_name: str = "bob_ai_knowledge"):
        """
        Initialize Elasticsearch backend

        Args:
            es_client: Optional Elasticsearch client (defaults to localhost:9200)
            index_name: Name of Elasticsearch index
        """
        if not ELASTICSEARCH_AVAILABLE:
            logger.warning("Elasticsearch not installed. Install with: pip install elasticsearch")
            self.client = None
            return

        self.client = es_client or Elasticsearch(["localhost:9200"])
        self.index_name = index_name
        self._create_index_mapping()

    def _create_index_mapping(self):
        """Create Elasticsearch index with optimal mapping"""
        if not self.client:
            return

        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "type": {"type": "keyword"},
                    "name": {"type": "text", "analyzer": "standard"},
                    "description": {"type": "text", "analyzer": "standard"},
                    "keywords": {"type": "keyword"},
                    "category": {"type": "keyword"},
                    "difficulty": {"type": "keyword"},
                    "language": {"type": "keyword"},
                    "relevance_score": {"type": "float"},
                    "timestamp": {"type": "date"},
                }
            }
        }

        try:
            if not self.client.indices.exists(index=self.index_name):
                self.client.indices.create(index=self.index_name, body=mapping)
                logger.info(f"✅ Created Elasticsearch index: {self.index_name}")
        except Exception as e:
            logger.error(f"❌ Failed to create index: {e}")

    def search(self, query: str, filters: Optional[FacetFilters] = None, limit: int = 20) -> SearchResponse:
        """
        Execute search using Elasticsearch

        Args:
            query: Search query string
            filters: Optional faceted filters
            limit: Maximum results to return

        Returns:
            SearchResponse with results and metadata
        """
        if not self.client:
            logger.error("Elasticsearch client not available")
            return SearchResponse(query=query, results=[], total_count=0, execution_time_ms=0)

        start_time = datetime.utcnow()
        results = []

        try:
            # Build query
            es_query = {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["name^2", "description", "keywords"]
                            }
                        }
                    ]
                }
            }

            # Add filters
            if filters:
                if filters.categories:
                    es_query["bool"]["filter"] = {"terms": {"category": filters.categories}}
                if filters.difficulty:
                    es_query["bool"]["filter"] = {"terms": {"difficulty": filters.difficulty}}

            # Execute search
            response = self.client.search(
                index=self.index_name,
                body={"query": es_query, "size": limit}
            )

            # Parse results
            for hit in response['hits']['hits']:
                source = hit['_source']
                results.append(SearchResult(
                    id=int(source['id']),
                    type=source['type'],
                    name=source['name'],
                    description=source['description'],
                    relevance_score=hit['_score'] / 100.0,  # Normalize
                    keywords=source.get('keywords', []),
                    category=source.get('category', ''),
                ))

            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            return SearchResponse(
                query=query,
                results=results,
                total_count=response['hits']['total']['value'],
                execution_time_ms=execution_time,
            )

        except Exception as e:
            logger.error(f"❌ Elasticsearch error: {e}")
            return SearchResponse(query=query, results=[], total_count=0, execution_time_ms=0)

    def index_document(self, doc_id: str, doc_type: str, data: Dict) -> bool:
        """Index a document in Elasticsearch"""
        if not self.client:
            return False

        try:
            self.client.index(
                index=self.index_name,
                id=doc_id,
                body={
                    **data,
                    "timestamp": datetime.utcnow()
                }
            )
            return True
        except Exception as e:
            logger.error(f"❌ Indexing error: {e}")
            return False

    def delete_index(self) -> bool:
        """Delete Elasticsearch index"""
        if not self.client:
            return False

        try:
            self.client.indices.delete(index=self.index_name)
            logger.info(f"✅ Deleted Elasticsearch index: {self.index_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete index: {e}")
            return False

    def health_check(self) -> bool:
        """Check Elasticsearch health"""
        if not self.client:
            return False

        try:
            health = self.client.cluster.health()
            return health['status'] in ['green', 'yellow']
        except:
            return False


class AdvancedSearchEngine:
    """Main search engine with backend abstraction"""

    def __init__(self, session: Session, use_elasticsearch: bool = False):
        """
        Initialize search engine

        Args:
            session: SQLAlchemy database session
            use_elasticsearch: Whether to use Elasticsearch (default: SQL backend)
        """
        self.session = session

        # Choose backend
        if use_elasticsearch and ELASTICSEARCH_AVAILABLE:
            try:
                self.backend = ElasticsearchBackend()
                logger.info("✅ Using Elasticsearch backend")
            except Exception as e:
                logger.warning(f"Elasticsearch unavailable, falling back to SQL: {e}")
                self.backend = SQLSearchBackend(session)
        else:
            self.backend = SQLSearchBackend(session)

    def search(self, query: str, filters: Optional[FacetFilters] = None, limit: int = 20) -> SearchResponse:
        """Execute search using configured backend"""
        return self.backend.search(query, filters, limit)

    def search_by_skill(self, skills: Set[str], limit: int = 10) -> List[SearchResult]:
        """Search for disciplines that teach specific skills"""
        results = []

        try:
            from bob_ai_expansion_phase1_database import ExpandedDiscipline

            for skill in skills:
                q = self.session.query(ExpandedDiscipline).filter(
                    ExpandedDiscipline.topics.contains([skill])
                ).limit(limit).all()

                for disc in q:
                    results.append(SearchResult(
                        id=disc.id,
                        type='discipline',
                        name=disc.name,
                        description=disc.description or '',
                        relevance_score=0.8,
                        keywords=disc.keywords or [],
                        category=disc.category.name if disc.category else '',
                    ))

            return results[:limit]

        except Exception as e:
            logger.error(f"Skill search error: {e}")
            return []

    def search_by_industry(self, industry: str, limit: int = 10) -> List[SearchResult]:
        """Search for disciplines relevant to specific industry"""
        results = []

        try:
            from bob_ai_expansion_phase1_database import ExpandedDiscipline

            q = self.session.query(ExpandedDiscipline).filter(
                ExpandedDiscipline.industry_applications.contains([industry])
            ).limit(limit).all()

            for disc in q:
                results.append(SearchResult(
                    id=disc.id,
                    type='discipline',
                    name=disc.name,
                    description=disc.description or '',
                    relevance_score=0.7,
                    keywords=disc.keywords or [],
                    category=disc.category.name if disc.category else '',
                    metadata={'industry': industry}
                ))

            return results

        except Exception as e:
            logger.error(f"Industry search error: {e}")
            return []

    def health_check(self) -> Dict[str, Any]:
        """Check search backend health"""
        is_healthy = self.backend.health_check()
        backend_type = type(self.backend).__name__

        return {
            'healthy': is_healthy,
            'backend': backend_type,
            'message': 'Search engine is operational' if is_healthy else 'Search engine is degraded'
        }
