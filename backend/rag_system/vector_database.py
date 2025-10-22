"""
ORFEAS AI 2D→3D Studio - Vector Database Integration
=====================================================
Multi-provider vector database support for RAG system.

Supported Providers:
- Pinecone (managed, high-performance)
- Weaviate (open-source, feature-rich)
- Qdrant (high-performance, on-premise)
- Chroma (embedded, lightweight)
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class VectorSearchResult:
    """Result from vector similarity search"""
    id: str
    score: float
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class IndexConfig:
    """Vector index configuration"""
    name: str
    dimension: int
    metric: str = "cosine"  # cosine, euclidean, dot_product
    metadata_fields: List[str] = None
    replicas: int = 1
    shards: int = 1


class VectorDatabase(ABC):
    """Abstract base class for vector databases"""

    @abstractmethod
    async def initialize(self):
        """Initialize database connection"""
        pass

    @abstractmethod
    async def create_index(self, config: IndexConfig):
        """Create vector index"""
        pass

    @abstractmethod
    async def upsert(
        self,
        documents: List[Dict[str, Any]],
        namespace: Optional[str] = None
    ):
        """Insert or update documents"""
        pass

    @abstractmethod
    async def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """Search for similar vectors"""
        pass

    @abstractmethod
    async def delete(
        self,
        ids: List[str],
        namespace: Optional[str] = None
    ):
        """Delete documents by ID"""
        pass

    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        pass


class PineconeVectorDB(VectorDatabase):
    """Pinecone vector database implementation"""

    def __init__(self):
        self.api_key = os.getenv('PINECONE_API_KEY', '')
        self.environment = os.getenv('PINECONE_ENVIRONMENT', 'us-west1-gcp')
        self.index = None
        self.client = None

        logger.info("[ORFEAS-VECTOR] Initializing Pinecone")

    async def initialize(self):
        """Initialize Pinecone connection"""
        try:
            import pinecone

            pinecone.init(
                api_key=self.api_key,
                environment=self.environment
            )

            self.client = pinecone
            logger.info("[ORFEAS-VECTOR] Pinecone initialized successfully")

        except Exception as e:
            logger.error(f"[ORFEAS-VECTOR] Pinecone initialization failed: {e}")
            raise

    async def create_index(self, config: IndexConfig):
        """Create Pinecone index"""
        try:
            if config.name in self.client.list_indexes():
                logger.info(f"[ORFEAS-VECTOR] Index {config.name} already exists")
                self.index = self.client.Index(config.name)
                return

            self.client.create_index(
                name=config.name,
                dimension=config.dimension,
                metric=config.metric,
                metadata_config={
                    "indexed": config.metadata_fields or []
                },
                replicas=config.replicas,
                shards=config.shards
            )

            self.index = self.client.Index(config.name)
            logger.info(f"[ORFEAS-VECTOR] Created Pinecone index: {config.name}")

        except Exception as e:
            logger.error(f"[ORFEAS-VECTOR] Index creation failed: {e}")
            raise

    async def upsert(
        self,
        documents: List[Dict[str, Any]],
        namespace: Optional[str] = None
    ):
        """Upsert documents to Pinecone"""
        try:
            vectors = []

            for doc in documents:
                vectors.append({
                    'id': doc['id'],
                    'values': doc['embedding'],
                    'metadata': doc.get('metadata', {})
                })

            # Batch upsert
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(
                    vectors=batch,
                    namespace=namespace or ""
                )

            logger.info(
                f"[ORFEAS-VECTOR] Upserted {len(documents)} documents to Pinecone"
            )

        except Exception as e:
            logger.error(f"[ORFEAS-VECTOR] Upsert failed: {e}")
            raise

    async def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """Search Pinecone for similar vectors"""
        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=namespace or "",
                filter=filters,
                include_metadata=True
            )

            search_results = []

            for match in results['matches']:
                search_results.append(VectorSearchResult(
                    id=match['id'],
                    score=match['score'],
                    content=match['metadata'].get('content', ''),
                    metadata=match['metadata']
                ))

            logger.info(
                f"[ORFEAS-VECTOR] Found {len(search_results)} similar documents"
            )

            return search_results

        except Exception as e:
            logger.error(f"[ORFEAS-VECTOR] Search failed: {e}")
            return []

    async def delete(
        self,
        ids: List[str],
        namespace: Optional[str] = None
    ):
        """Delete documents from Pinecone"""
        try:
            self.index.delete(
                ids=ids,
                namespace=namespace or ""
            )

            logger.info(f"[ORFEAS-VECTOR] Deleted {len(ids)} documents")

        except Exception as e:
            logger.error(f"[ORFEAS-VECTOR] Delete failed: {e}")
            raise

    async def get_stats(self) -> Dict[str, Any]:
        """Get Pinecone index statistics"""
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vectors': stats.get('total_vector_count', 0),
                'dimension': stats.get('dimension', 0),
                'namespaces': stats.get('namespaces', {})
            }
        except Exception as e:
            logger.error(f"[ORFEAS-VECTOR] Stats retrieval failed: {e}")
            return {}


class WeaviateVectorDB(VectorDatabase):
    """Weaviate vector database implementation"""

    def __init__(self):
        self.url = os.getenv('WEAVIATE_URL', 'http://localhost:8080')
        self.api_key = os.getenv('WEAVIATE_API_KEY', '')
        self.client = None

        logger.info("[ORFEAS-VECTOR] Initializing Weaviate")

    async def initialize(self):
        """Initialize Weaviate connection"""
        try:
            import weaviate

            self.client = weaviate.Client(
                url=self.url,
                auth_client_secret=weaviate.AuthApiKey(api_key=self.api_key) if self.api_key else None
            )

            logger.info("[ORFEAS-VECTOR] Weaviate initialized successfully")

        except Exception as e:
            logger.error(f"[ORFEAS-VECTOR] Weaviate initialization failed: {e}")
            raise

    async def create_index(self, config: IndexConfig):
        """Create Weaviate class schema"""
        try:
            class_obj = {
                "class": config.name,
                "vectorizer": "none",  # We provide vectors
                "vectorIndexConfig": {
                    "distance": config.metric
                }
            }

            # Add properties for metadata fields
            if config.metadata_fields:
                class_obj["properties"] = [
                    {"name": field, "dataType": ["text"]}
                    for field in config.metadata_fields
                ]

            self.client.schema.create_class(class_obj)
            logger.info(f"[ORFEAS-VECTOR] Created Weaviate class: {config.name}")

        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info(f"[ORFEAS-VECTOR] Class {config.name} already exists")
            else:
                logger.error(f"[ORFEAS-VECTOR] Class creation failed: {e}")
                raise

    async def upsert(
        self,
        documents: List[Dict[str, Any]],
        namespace: Optional[str] = None
    ):
        """Upsert documents to Weaviate"""
        try:
            class_name = namespace or "Document"

            with self.client.batch as batch:
                for doc in documents:
                    batch.add_data_object(
                        data_object=doc.get('metadata', {}),
                        class_name=class_name,
                        uuid=doc['id'],
                        vector=doc['embedding']
                    )

            logger.info(
                f"[ORFEAS-VECTOR] Upserted {len(documents)} documents to Weaviate"
            )

        except Exception as e:
            logger.error(f"[ORFEAS-VECTOR] Upsert failed: {e}")
            raise

    async def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """Search Weaviate for similar vectors"""
        try:
            class_name = namespace or "Document"

            query = (
                self.client.query
                .get(class_name, ["*"])
                .with_near_vector({"vector": query_embedding})
                .with_limit(top_k)
                .with_additional(["distance", "id"])
            )

            if filters:
                # Apply filters (would need to build proper Weaviate filter)
                pass

            result = query.do()

            search_results = []

            if result and "data" in result:
                objects = result["data"]["Get"].get(class_name, [])

                for obj in objects:
                    search_results.append(VectorSearchResult(
                        id=obj["_additional"]["id"],
                        score=1.0 - obj["_additional"]["distance"],  # Convert distance to similarity
                        content=obj.get("content", ""),
                        metadata=obj
                    ))

            logger.info(
                f"[ORFEAS-VECTOR] Found {len(search_results)} similar documents"
            )

            return search_results

        except Exception as e:
            logger.error(f"[ORFEAS-VECTOR] Search failed: {e}")
            return []

    async def delete(
        self,
        ids: List[str],
        namespace: Optional[str] = None
    ):
        """Delete documents from Weaviate"""
        try:
            class_name = namespace or "Document"

            for doc_id in ids:
                self.client.data_object.delete(
                    uuid=doc_id,
                    class_name=class_name
                )

            logger.info(f"[ORFEAS-VECTOR] Deleted {len(ids)} documents")

        except Exception as e:
            logger.error(f"[ORFEAS-VECTOR] Delete failed: {e}")
            raise

    async def get_stats(self) -> Dict[str, Any]:
        """Get Weaviate statistics"""
        try:
            schema = self.client.schema.get()
            return {
                'classes': len(schema.get('classes', [])),
                'schema': schema
            }
        except Exception as e:
            logger.error(f"[ORFEAS-VECTOR] Stats retrieval failed: {e}")
            return {}


class QdrantVectorDB(VectorDatabase):
    """Qdrant vector database implementation"""

    def __init__(self):
        self.url = os.getenv('QDRANT_URL', 'http://localhost:6333')
        self.api_key = os.getenv('QDRANT_API_KEY', '')
        self.client = None

        logger.info("[ORFEAS-VECTOR] Initializing Qdrant")

    async def initialize(self):
        """Initialize Qdrant connection"""
        try:
            from qdrant_client import QdrantClient

            self.client = QdrantClient(
                url=self.url,
                api_key=self.api_key if self.api_key else None
            )

            logger.info("[ORFEAS-VECTOR] Qdrant initialized successfully")

        except Exception as e:
            logger.error(f"[ORFEAS-VECTOR] Qdrant initialization failed: {e}")
            raise

    async def create_index(self, config: IndexConfig):
        """Create Qdrant collection"""
        try:
            from qdrant_client.models import Distance, VectorParams

            distance_map = {
                "cosine": Distance.COSINE,
                "euclidean": Distance.EUCLID,
                "dot_product": Distance.DOT
            }

            self.client.recreate_collection(
                collection_name=config.name,
                vectors_config=VectorParams(
                    size=config.dimension,
                    distance=distance_map.get(config.metric, Distance.COSINE)
                )
            )

            logger.info(f"[ORFEAS-VECTOR] Created Qdrant collection: {config.name}")

        except Exception as e:
            logger.error(f"[ORFEAS-VECTOR] Collection creation failed: {e}")
            raise

    async def upsert(
        self,
        documents: List[Dict[str, Any]],
        namespace: Optional[str] = None
    ):
        """Upsert documents to Qdrant"""
        try:
            from qdrant_client.models import PointStruct

            collection_name = namespace or "default"

            points = []
            for doc in documents:
                points.append(PointStruct(
                    id=doc['id'],
                    vector=doc['embedding'],
                    payload=doc.get('metadata', {})
                ))

            self.client.upsert(
                collection_name=collection_name,
                points=points
            )

            logger.info(
                f"[ORFEAS-VECTOR] Upserted {len(documents)} documents to Qdrant"
            )

        except Exception as e:
            logger.error(f"[ORFEAS-VECTOR] Upsert failed: {e}")
            raise

    async def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """Search Qdrant for similar vectors"""
        try:
            collection_name = namespace or "default"

            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=filters
            )

            search_results = []

            for result in results:
                search_results.append(VectorSearchResult(
                    id=str(result.id),
                    score=result.score,
                    content=result.payload.get('content', ''),
                    metadata=result.payload
                ))

            logger.info(
                f"[ORFEAS-VECTOR] Found {len(search_results)} similar documents"
            )

            return search_results

        except Exception as e:
            logger.error(f"[ORFEAS-VECTOR] Search failed: {e}")
            return []

    async def delete(
        self,
        ids: List[str],
        namespace: Optional[str] = None
    ):
        """Delete documents from Qdrant"""
        try:
            collection_name = namespace or "default"

            self.client.delete(
                collection_name=collection_name,
                points_selector=ids
            )

            logger.info(f"[ORFEAS-VECTOR] Deleted {len(ids)} documents")

        except Exception as e:
            logger.error(f"[ORFEAS-VECTOR] Delete failed: {e}")
            raise

    async def get_stats(self) -> Dict[str, Any]:
        """Get Qdrant collection statistics"""
        try:
            collections = self.client.get_collections()
            return {
                'collections': len(collections.collections),
                'collection_names': [c.name for c in collections.collections]
            }
        except Exception as e:
            logger.error(f"[ORFEAS-VECTOR] Stats retrieval failed: {e}")
            return {}


class VectorDatabaseManager:
    """
    Manager for vector database operations
    Handles provider selection and failover
    """

    def __init__(
        self,
        primary_provider: str = "pinecone",
        fallback_providers: Optional[List[str]] = None
    ):
        self.primary_provider = primary_provider
        self.fallback_providers = fallback_providers or []

        self.providers: Dict[str, VectorDatabase] = {}
        self.active_provider = None

        self.total_operations = 0
        self.provider_stats: Dict[str, Dict[str, int]] = {}

        logger.info(
            f"[ORFEAS-VECTOR] VectorDatabaseManager initialized "
            f"(primary={primary_provider}, fallbacks={fallback_providers})"
        )

    async def initialize(self):
        """Initialize all configured providers"""

        providers_to_init = [self.primary_provider] + self.fallback_providers

        for provider_name in providers_to_init:
            try:
                provider = self._create_provider(provider_name)
                await provider.initialize()
                self.providers[provider_name] = provider

                self.provider_stats[provider_name] = {
                    'operations': 0,
                    'failures': 0,
                    'successes': 0
                }

                logger.info(f"[ORFEAS-VECTOR] Initialized provider: {provider_name}")

            except Exception as e:
                logger.warning(
                    f"[ORFEAS-VECTOR] Failed to initialize {provider_name}: {e}"
                )

        # Set active provider
        if self.primary_provider in self.providers:
            self.active_provider = self.providers[self.primary_provider]
        elif self.providers:
            self.active_provider = list(self.providers.values())[0]
        else:
            raise RuntimeError("No vector database providers available")

    def _create_provider(self, provider_name: str) -> VectorDatabase:
        """Create vector database provider instance"""

        if provider_name == "pinecone":
            return PineconeVectorDB()
        elif provider_name == "weaviate":
            return WeaviateVectorDB()
        elif provider_name == "qdrant":
            return QdrantVectorDB()
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

    async def execute_with_failover(
        self,
        operation: str,
        *args,
        **kwargs
    ) -> Any:
        """Execute operation with automatic failover"""

        self.total_operations += 1

        # Try active provider first
        providers_to_try = [self.active_provider]

        # Add fallback providers
        for provider_name in self.fallback_providers:
            if provider_name in self.providers:
                provider = self.providers[provider_name]
                if provider != self.active_provider:
                    providers_to_try.append(provider)

        last_error = None

        for provider in providers_to_try:
            provider_name = self._get_provider_name(provider)

            try:
                self.provider_stats[provider_name]['operations'] += 1

                # Execute operation
                method = getattr(provider, operation)
                result = await method(*args, **kwargs)

                self.provider_stats[provider_name]['successes'] += 1

                return result

            except Exception as e:
                self.provider_stats[provider_name]['failures'] += 1
                last_error = e

                logger.warning(
                    f"[ORFEAS-VECTOR] {provider_name} {operation} failed: {e}"
                )

                # Try next provider
                continue

        # All providers failed
        logger.error(
            f"[ORFEAS-VECTOR] All providers failed for {operation}: {last_error}"
        )
        raise RuntimeError(f"Vector database operation failed: {operation}")

    def _get_provider_name(self, provider: VectorDatabase) -> str:
        """Get provider name from instance"""
        for name, p in self.providers.items():
            if p == provider:
                return name
        return "unknown"

    def get_statistics(self) -> Dict[str, Any]:
        """Get manager statistics"""

        return {
            'total_operations': self.total_operations,
            'active_provider': self._get_provider_name(self.active_provider),
            'provider_stats': self.provider_stats
        }


# Global vector database manager
_vector_db_manager: Optional[VectorDatabaseManager] = None


def get_vector_db_manager() -> VectorDatabaseManager:
    """Get global vector database manager instance"""
    global _vector_db_manager
    if _vector_db_manager is None:
        primary = os.getenv('VECTOR_DB_PRIMARY', 'pinecone')
        fallbacks = os.getenv('VECTOR_DB_FALLBACKS', '').split(',')
        fallbacks = [f.strip() for f in fallbacks if f.strip()]

        _vector_db_manager = VectorDatabaseManager(
            primary_provider=primary,
            fallback_providers=fallbacks
        )
    return _vector_db_manager
