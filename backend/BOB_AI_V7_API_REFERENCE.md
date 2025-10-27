# BOB AI v7 - REST API Reference

**Complete API Documentation | October 27, 2025**

---

## Overview

The BOB AI v7 REST API provides programmatic access to the enhanced knowledge management system with 1,330+ items across 10 domains.

**Base URL:** `http://localhost:5000/api/v7`
**Authentication:** Optional (rate limiting: 100 req/min)
**Response Format:** JSON
**Status Codes:** 200 (Success), 400 (Bad Request), 404 (Not Found), 429 (Rate Limited), 500 (Server Error)

---

## Endpoints

### 1. Add Knowledge Item

**Endpoint:** `POST /add`

Add a new knowledge item to the graph.

**Request:**

```json
{
  "label": "Machine Learning",
  "category": "AI",
  "description": "Automated learning from data",
  "quality": 0.92,
  "metadata": {
    "confidence": 0.95,
    "precision": 0.88,
    "completeness": 0.90
  }
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "item_id": "ml-001",
  "label": "Machine Learning",
  "quality": 0.92,
  "created_at": "2025-10-27T15:30:00Z"
}
```

**Error (400 Bad Request):**

```json
{
  "success": false,
  "error": "Missing required field: label"
}
```

---

### 2. Update Knowledge Item

**Endpoint:** `PUT /update/{item_id}`

Update an existing knowledge item.

**Request:**

```json
{
  "quality": 0.95,
  "metadata": {
    "confidence": 0.97
  }
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "item_id": "ml-001",
  "quality": 0.95,
  "updated_at": "2025-10-27T15:35:00Z"
}
```

---

### 3. Remove Knowledge Item

**Endpoint:** `DELETE /remove/{item_id}`

Remove a knowledge item from the graph.

**Response (200 OK):**

```json
{
  "success": true,
  "deleted_item": "ml-001",
  "message": "Item successfully removed"
}
```

---

### 4. Search Knowledge Base

**Endpoint:** `GET /search?q={query}&domain={domain}&max_results={count}`

Search for knowledge items.

**Query Parameters:**

- `q` (required): Search query
- `domain` (optional): Filter by domain (ai, medicine, business, etc.)
- `max_results` (optional): Max results (default: 10, max: 100)

**Response (200 OK):**

```json
{
  "query": "machine learning",
  "results": [
    {
      "item_id": "ml-001",
      "label": "Machine Learning",
      "category": "AI",
      "quality": 0.92,
      "relevance_score": 0.95
    }
  ],
  "total": 1,
  "search_time_ms": 0.5
}
```

**Example:**

```bash
curl "http://localhost:5000/api/v7/search?q=neural+networks&domain=ai&max_results=5"
```

---

### 5. Get Domain Items

**Endpoint:** `GET /domain/{domain_name}`

Retrieve all items in a specific domain.

**Path Parameters:**

- `domain_name`: Domain name (ai, medicine, business, law, environment, history, philosophy, arts)

**Response (200 OK):**

```json
{
  "domain": "ai",
  "item_count": 42,
  "quality_avg": 0.90,
  "items": [
    {
      "item_id": "ai-001",
      "label": "Artificial Intelligence",
      "quality": 0.92
    }
  ]
}
```

---

### 6. Get Item Details

**Endpoint:** `GET /{item_id}`

Retrieve detailed information about a specific item.

**Response (200 OK):**

```json
{
  "item_id": "ml-001",
  "label": "Machine Learning",
  "category": "AI",
  "description": "Automated learning from data",
  "quality": 0.92,
  "metadata": {
    "confidence": 0.95,
    "precision": 0.88,
    "completeness": 0.90,
    "relevance": 0.85,
    "currency": 0.80
  },
  "relationships": [
    {
      "type": "is_a",
      "target": "Artificial Intelligence",
      "strength": 0.92
    }
  ],
  "created_at": "2025-10-26T12:00:00Z",
  "updated_at": "2025-10-27T15:35:00Z"
}
```

---

### 7. Add Relationship

**Endpoint:** `POST /relationships`

Add a semantic relationship between two items.

**Request:**

```json
{
  "source_id": "ml-001",
  "target_id": "ai-001",
  "relationship_type": "is_a",
  "strength": 0.92
}
```

**Supported Relationship Types:**

- `is_a`: Hierarchical classification
- `part_of`: Composition relationship
- `depends_on`: Dependency
- `related_to`: General association
- `similar_to`: Similarity
- `enables`: Causal enablement
- `requires`: Prerequisite
- `produces`: Production relationship
- `contradicts`: Contradiction
- `refines`: Refinement
- `specializes`: Specialization
- `generalizes`: Generalization
- `aliases`: Alternative names
- `precedes`: Temporal ordering
- `competes_with`: Competition

**Response (200 OK):**

```json
{
  "success": true,
  "relationship_id": "rel-001",
  "source": "ml-001",
  "target": "ai-001",
  "type": "is_a",
  "strength": 0.92
}
```

---

### 8. Get Quality Report

**Endpoint:** `GET /quality/report`

Get comprehensive quality metrics for the knowledge base.

**Response (200 OK):**

```json
{
  "total_items": 1330,
  "quality_metrics": {
    "average_quality": 0.89,
    "high_quality_count": 1263,
    "high_quality_percentage": 94.96,
    "low_quality_count": 67,
    "low_quality_percentage": 5.04
  },
  "domain_metrics": {
    "ai": {
      "items": 42,
      "avg_quality": 0.92
    },
    "medicine": {
      "items": 63,
      "avg_quality": 0.91
    },
    "business": {
      "items": 57,
      "avg_quality": 0.90
    }
  },
  "generated_at": "2025-10-27T15:40:00Z"
}
```

---

## Advanced Features

### Multi-Stage Context Retrieval

The LLM integration provides automatic context retrieval with semantic expansion:

```bash
curl -X POST http://localhost:5000/api/v7/llm/context \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning applications",
    "expand_relationships": true,
    "cross_domain": true
  }'
```

**Response:**

```json
{
  "query": "machine learning applications",
  "direct_results": 5,
  "semantic_expansions": 3,
  "cross_domain_links": 2,
  "total_context_items": 10,
  "quality_avg": 0.91,
  "retrieval_time_ms": 2.5
}
```

### Quality-Based Result Ranking

Results are automatically ranked by:

1. Quality score (40%)
2. Relevance to query (30%)
3. Domain diversity (15%)
4. Recency of enrichment (10%)
5. Relationship density (5%)

---

## Rate Limiting

**Limit:** 100 requests per minute
**Headers:**

- `X-RateLimit-Limit`: 100
- `X-RateLimit-Remaining`: 99
- `X-RateLimit-Reset`: 1635342000

**Response (429 Too Many Requests):**

```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

---

## Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Item added successfully |
| 400 | Bad Request | Missing required field |
| 404 | Not Found | Item ID does not exist |
| 429 | Rate Limited | Too many requests |
| 500 | Server Error | Unexpected error |

---

## Authentication

Currently no authentication required. Future versions will support:

- API Keys
- OAuth 2.0
- JWT TokeContinue with Todo

---

## Pagination

For list endpoints, use pagination:

```bash
GET /search?q=ai&page=2&per_page=20
```

**Response:**

```json
{
  "results": [...],
  "pagination": {
    "page": 2,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

---

## Batch Operations

Add multiple items efficiently:

```bash
curl -X POST http://localhost:5000/api/v7/batch/add \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"label": "Item 1", "category": "AI"},
      {"label": "Item 2", "category": "AI"}
    ]
  }'
```

---

## Webhooks (Future)

Future support for webhook notifications:

- `item.created`
- `item.updated`
- `item.deleted`
- `relationship.added`
- `quality.degraded`

---

## SDKs

### Python

```python
from bob_ai_v7_api_client import KnowledgeClient

client = KnowledgeClient(base_url="http://localhost:5000/api/v7")
results = client.search("machine learning", domain="ai")
```

### JavaScript (Future)

```javascript
const client = new KnowledgeClient({
  baseUrl: "http://localhost:5000/api/v7"
});
const results = await client.search("machine learning");
```

---

## Examples

### Search for items in AI domain

```bash
curl "http://localhost:5000/api/v7/search?q=neural+networks&domain=ai"
```

### Get all business items

```bash
curl "http://localhost:5000/api/v7/domain/business"
```

### Add new item

```bash
curl -X POST http://localhost:5000/api/v7/add \
  -H "Content-Type: application/json" \
  -d '{
    "label": "Deep Learning",
    "category": "AI",
    "quality": 0.93
  }'
```

### Get quality report

```bash
curl "http://localhost:5000/api/v7/quality/report"
```

---

## Response Format

All responses follow this format:

**Success:**

```json
{
  "success": true,
  "data": {...}
}
```

**Error:**

```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

---

## Performance

- Search response time: <1ms average
- Add item response time: <5ms average
- Full pipeline response time: <13ms average
- Cache hit rate: >95%

---

## Support

For API issues, contact: <api-support@orfeas-ai.dev>

---

*Last Updated: October 27, 2025*
*BOB AI v7 Knowledge System*
