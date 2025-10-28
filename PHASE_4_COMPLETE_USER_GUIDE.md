# Phase 4 Complete: User Guide & API Reference

**BOB AI v10.0 - Complete User Documentation**

Status: Production-Ready
Version: 1.0.0
Last Updated: October 28, 2025

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Core Features](#core-features)
3. [REST API Reference](#rest-api-reference)
4. [WebSocket Integration](#websocket-integration)
5. [Authentication & Security](#authentication--security)
6. [Usage Examples](#usage-examples)
7. [Troubleshooting Guide](#troubleshooting-guide)

---

## Getting Started

### System Requirements

**Minimum Requirements:**

- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB
- Network: Stable internet connection

**Recommended Requirements:**

- CPU: 4-8 cores
- RAM: 8-16GB
- Storage: 50GB+
- Network: 10+ Mbps

### Installation

**Option 1: Docker (Recommended)**

```powershell
# Clone repository
git clone https://github.com/example/orfeas-ai-studio.git
cd orfeas-ai-studio

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start services
docker-compose up -d

# Verify installation
curl http://localhost:5000/health
curl http://localhost:3000
```

**Option 2: Local Development**

```powershell
# Backend setup
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py

# Frontend setup (in new terminal)
cd frontend-nextjs
npm install
npm run dev
```

### First Steps

1. **Access Dashboard**
   - Open browser to <http://localhost:3000>
   - Login with default credentials (if auth enabled)

2. **Explore Features**
   - View available disciplines
   - Search knowledge base
   - Test API endpoints

3. **Run Validation**
   - Execute health checks
   - Verify database connectivity
   - Confirm monitoring active

---

## Core Features

### Feature 1: Discipline Discovery

**Purpose:** Search and explore 391 disciplines across 12 tiers.

**How to Use:**

```powershell
# Search for discipline
curl "http://localhost:5000/api/disciplines/search?q=machine-learning"

# Get discipline details
curl "http://localhost:5000/api/disciplines/1"

# List disciplines by category
curl "http://localhost:5000/api/disciplines?category=ai&limit=10"
```

**Example Response:**

```json
{
  "id": 1,
  "name": "Machine Learning",
  "category": "AI",
  "tier": 1,
  "description": "ML fundamentals and algorithms",
  "knowledge_items": 1243,
  "subcategories": ["supervised", "unsupervised", "reinforcement"]
}
```

### Feature 2: Knowledge Search

**Purpose:** Search 51,872 knowledge items using semantic matching.

**How to Use:**

```powershell
# Semantic search
curl -X POST "http://localhost:5000/api/search" `
  -H "Content-Type: application/json" `
  -d '{
    "query": "neural network architecture",
    "limit": 20,
    "filters": {"type": "algorithm"}
  }'

# Full-text search
curl "http://localhost:5000/api/search/fulltext?q=transformer"
```

**Query Types:**

- **Semantic Search:** Understands meaning, returns related concepts
- **Full-Text Search:** Exact keyword matching
- **Advanced Search:** Filters by type, category, date, author

### Feature 3: Real-Time Monitoring

**Purpose:** Monitor system performance and health metrics.

**How to Use:**

```powershell
# Get system status
curl "http://localhost:8000/api/health/full"

# Get metrics
curl "http://localhost:8000/api/metrics/summary"

# Stream events (WebSocket)
# See WebSocket Integration section
```

---

## REST API Reference

### Base Information

**Base URL:** `http://localhost:5000`
**API Version:** v1
**Response Format:** JSON
**Rate Limit:** 1000 req/min per IP

### Health & Status Endpoints

#### Health Check

```
GET /health
```

Returns system health status.

**Response (200 OK):**

```json
{
  "status": "healthy",
  "api": "operational",
  "database": "connected",
  "cache": "operational",
  "timestamp": "2025-10-28T12:00:00Z"
}
```

#### Readiness Check

```
GET /health/ready
```

Returns whether system is ready for requests.

**Response (200 OK):**

```json
{
  "ready": true,
  "services": {
    "database": "ready",
    "cache": "ready",
    "api": "ready"
  }
}
```

### Discipline Endpoints

#### List Disciplines

```
GET /api/disciplines?limit=10&offset=0&category=ai
```

**Parameters:**

- `limit` (int): Results per page (default: 10, max: 100)
- `offset` (int): Pagination offset (default: 0)
- `category` (string): Filter by category (optional)

**Response (200 OK):**

```json
{
  "data": [
    {
      "id": 1,
      "name": "Machine Learning",
      "category": "AI",
      "items_count": 1243
    }
  ],
  "total": 391,
  "limit": 10,
  "offset": 0
}
```

#### Get Discipline Details

```
GET /api/disciplines/{id}
```

**Parameters:**

- `id` (int): Discipline ID

**Response (200 OK):**

```json
{
  "id": 1,
  "name": "Machine Learning",
  "description": "ML fundamentals and algorithms",
  "tier": 1,
  "category": "AI",
  "items": [
    {
      "id": 101,
      "title": "Supervised Learning",
      "type": "concept"
    }
  ]
}
```

### Search Endpoints

#### Semantic Search

```
POST /api/search
Content-Type: application/json
```

**Request Body:**

```json
{
  "query": "neural network architecture",
  "limit": 20,
  "filters": {
    "type": "algorithm",
    "category": "AI"
  }
}
```

**Response (200 OK):**

```json
{
  "results": [
    {
      "id": 1001,
      "title": "Transformer Architecture",
      "type": "algorithm",
      "relevance": 0.95,
      "snippet": "Transformer uses self-attention mechanism..."
    }
  ],
  "total": 145,
  "execution_time_ms": 245
}
```

#### Full-Text Search

```
GET /api/search/fulltext?q=machine+learning&limit=10
```

**Response (200 OK):**

```json
{
  "results": [
    {
      "id": 1,
      "title": "Machine Learning Basics",
      "matches": ["Machine Learning", "learning algorithms"]
    }
  ],
  "total": 234
}
```

### Knowledge Items Endpoints

#### Get Knowledge Item

```
GET /api/items/{id}
```

**Response (200 OK):**

```json
{
  "id": 1001,
  "title": "Transformer Architecture",
  "content": "Transformers are deep learning models that use attention mechanisms...",
  "type": "algorithm",
  "discipline_id": 1,
  "tags": ["nlp", "attention", "deep-learning"],
  "created_date": "2025-01-15",
  "last_updated": "2025-10-28",
  "references": [
    {
      "id": 1002,
      "title": "Attention is All You Need"
    }
  ]
}
```

#### Search Items

```
GET /api/items/search?q=attention&type=algorithm&limit=20
```

**Response (200 OK):**

```json
{
  "results": [
    {
      "id": 1001,
      "title": "Attention Mechanisms",
      "preview": "Core mechanism in transformer models...",
      "relevance": 0.98
    }
  ],
  "total": 89
}
```

---

## WebSocket Integration

### Connection

```javascript
// JavaScript/TypeScript
import io from 'socket.io-client';

const socket = io('http://localhost:5000');

socket.on('connect', () => {
  console.log('Connected to server');
});

socket.on('disconnect', () => {
  console.log('Disconnected from server');
});
```

### Event Types

**Subscribe to Updates:**

```javascript
// Subscribe to knowledge updates
socket.emit('subscribe', {
  channel: 'disciplines',
  filter: { category: 'AI' }
});

// Listen for updates
socket.on('update:discipline', (data) => {
  console.log('Discipline updated:', data);
});
```

**Real-Time Notifications:**

```javascript
// Listen for system events
socket.on('notification', (data) => {
  console.log('Notification:', data.type, data.message);
});
```

---

## Authentication & Security

### API Key Authentication

**Method 1: Header**

```powershell
curl -H "X-API-Key: your-api-key-here" http://localhost:5000/api/disciplines
```

**Method 2: Query Parameter**

```powershell
curl "http://localhost:5000/api/disciplines?api_key=your-api-key-here"
```

### Generating API Keys

```powershell
# Generate new API key
curl -X POST http://localhost:5000/api/keys `
  -H "Authorization: Bearer $token" `
  -d '{"name": "my-app", "permissions": ["read"]}'
```

### CORS Configuration

**Allowed Origins:**

```powershell
# Default: localhost
# Production: Configure in .env

# Set custom origins
$env:CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"
```

### Rate Limiting

**Limits:**

| Endpoint | Limit | Window |
|----------|-------|--------|
| General API | 1000 | 1 minute |
| Search | 500 | 1 minute |
| Health | Unlimited | N/A |
| Metrics | 100 | 1 minute |

**Response on Rate Limit:**

```json
{
  "error": "Rate limit exceeded",
  "retry_after": 45,
  "limit": 1000,
  "remaining": 0
}
```

---

## Usage Examples

### Example 1: Search Disciplines by Category

```powershell
# PowerShell
$response = Invoke-RestMethod `
  -Uri "http://localhost:5000/api/disciplines?category=AI&limit=5" `
  -Headers @{"X-API-Key" = "your-api-key"}

$response.data | ForEach-Object {
  Write-Host "ID: $($_.id), Name: $($_.name), Items: $($_.items_count)"
}
```

**Output:**

```
ID: 1, Name: Machine Learning, Items: 1243
ID: 2, Name: Deep Learning, Items: 856
ID: 3, Name: NLP, Items: 542
ID: 4, Name: Computer Vision, Items: 723
ID: 5, Name: Reinforcement Learning, Items: 341
```

### Example 2: Semantic Search

```powershell
# Search for concepts related to "attention mechanisms"
$searchQuery = @{
    query = "how does attention mechanism work"
    limit = 5
    filters = @{
        type = "concept"
    }
} | ConvertTo-Json

$response = Invoke-RestMethod `
  -Uri "http://localhost:5000/api/search" `
  -Method Post `
  -ContentType "application/json" `
  -Body $searchQuery

$response.results | ForEach-Object {
  Write-Host "$($_.title) (Relevance: $($_.relevance))"
}
```

**Output:**

```
Attention Mechanism Fundamentals (Relevance: 0.98)
Query-Key-Value Attention (Relevance: 0.94)
Multi-Head Attention (Relevance: 0.92)
Scaled Dot-Product Attention (Relevance: 0.89)
Self-Attention vs Cross-Attention (Relevance: 0.87)
```

### Example 3: Real-Time Monitoring

```javascript
// JavaScript/TypeScript - Monitor system health
import io from 'socket.io-client';

const socket = io('http://localhost:5000');

socket.on('connect', () => {
  // Subscribe to metrics
  socket.emit('subscribe', { channel: 'metrics' });
});

socket.on('metric:update', (data) => {
  console.log('CPU:', data.cpu + '%');
  console.log('Memory:', data.memory + '%');
  console.log('Request/s:', data.requests_per_second);
});

// Check every 10 seconds
setInterval(() => {
  socket.emit('request:metrics');
}, 10000);
```

### Example 4: Batch Processing

```python
# Python - Process multiple queries
import requests

queries = [
    "machine learning",
    "deep learning",
    "neural networks",
    "transformers",
    "attention mechanism"
]

results = {}
for query in queries:
    response = requests.post(
        'http://localhost:5000/api/search',
        json={'query': query, 'limit': 3},
        headers={'X-API-Key': 'your-api-key'}
    )
    results[query] = response.json()['results']

for query, items in results.items():
    print(f"\n{query}:")
    for item in items:
        print(f"  - {item['title']} (relevance: {item['relevance']})")
```

---

## Troubleshooting Guide

### Issue: Connection Refused

**Symptom:** `curl: (7) Failed to connect`

**Solutions:**

```powershell
# 1. Verify service is running
docker ps | grep orfeas

# 2. Check port is accessible
Test-NetConnection -ComputerName localhost -Port 5000

# 3. Verify firewall rules
# Windows Firewall: Allow port 5000

# 4. Restart service
docker-compose restart backend
```

### Issue: Slow Response Time

**Symptom:** API requests taking >1 second

**Solutions:**

```powershell
# 1. Check system resources
docker stats orfeas-backend

# 2. Check database performance
# Query slow log
docker-compose exec postgres \
  psql -d orfeas -c "SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 5;"

# 3. Enable query caching
curl -X POST http://localhost:5000/api/cache/enable

# 4. Increase resources
# Edit docker-compose.yml and increase memory/CPU limits
```

### Issue: Search Returns No Results

**Symptom:** Semantic search returns empty results

**Solutions:**

```powershell
# 1. Verify data is loaded
curl "http://localhost:5000/api/disciplines" | ConvertFrom-Json | Select-Object -ExpandProperty total

# 2. Try full-text search
curl "http://localhost:5000/api/search/fulltext?q=your-query"

# 3. Check index status
curl "http://localhost:5000/api/admin/index/status"

# 4. Rebuild search index
curl -X POST http://localhost:5000/api/admin/index/rebuild
```

### Issue: Authentication Failures

**Symptom:** `401 Unauthorized`

**Solutions:**

```powershell
# 1. Verify API key is correct
$env:API_KEY  # Check if set

# 2. Generate new API key
curl -X POST http://localhost:5000/api/keys/generate

# 3. Check key permissions
curl -H "X-API-Key: $env:API_KEY" http://localhost:5000/api/keys/current

# 4. Ensure header format is correct
# Correct: -H "X-API-Key: your-key"
# Wrong: -H "Authorization: your-key"
```

### Issue: WebSocket Connection Timeout

**Symptom:** `WebSocket is closed` after few seconds

**Solutions:**

```javascript
// Enable automatic reconnection with backoff
const socket = io('http://localhost:5000', {
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  reconnectionAttempts: 5
});

socket.on('connect_error', (error) => {
  console.error('Connection error:', error);
});

// Add heartbeat
setInterval(() => {
  socket.emit('heartbeat');
}, 30000);
```

### Issue: Database Connection Error

**Symptom:** `Connection refused: database`

**Solutions:**

```powershell
# 1. Verify database is running
docker-compose ps postgres

# 2. Check database connectivity
docker-compose exec postgres psql -U postgres -c "SELECT 1;"

# 3. Check database credentials
$env:DATABASE_URL  # Verify format: postgresql://user:pass@host:port/db

# 4. Restart database
docker-compose restart postgres
docker-compose up -d backend  # Reconnect backend
```

### Issue: High Memory Usage

**Symptom:** Container using >80% available memory

**Solutions:**

```powershell
# 1. Check memory-intensive operations
docker exec orfeas-backend python -c "
import tracemalloc
tracemalloc.start()
# Run application
current, peak = tracemalloc.get_traced_memory()
print(f'Current: {current/1e6:.1f}MB; Peak: {peak/1e6:.1f}MB')
"

# 2. Reduce cache size
docker-compose exec redis redis-cli CONFIG SET maxmemory 1gb

# 3. Scale horizontally
# Add more backend instances
```

---

## Support & Resources

### Getting Help

**Documentation:** Online docs at <https://docs.example.com>

**Issue Tracker:** GitHub Issues at <https://github.com/example/orfeas-ai-studio/issues>

**Community:** Discord server at <https://discord.gg/example>

### Useful Commands

```powershell
# System Status
curl http://localhost:5000/health
curl http://localhost:5000/health/ready

# View Logs
docker-compose logs -f backend
docker-compose logs backend --tail=100

# Debug API
curl -v http://localhost:5000/api/disciplines

# Performance Check
docker stats
docker top orfeas-backend

# Database Management
docker-compose exec postgres psql -d orfeas -U postgres
```

### Version Information

```powershell
# Check installed version
curl http://localhost:5000/api/version

# Check for updates
curl https://api.example.com/version/latest

# Upgrade guide
# See UPGRADE.md in repository
```

---

## Appendix: API Response Codes

| Code | Meaning | When Returned |
|------|---------|---------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no response body |
| 400 | Bad Request | Invalid request format |
| 401 | Unauthorized | Missing or invalid API key |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal server error |
| 503 | Service Unavailable | Service temporarily down |

---

**End of User Guide**

For latest documentation and updates, visit: <https://docs.example.com>
