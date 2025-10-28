# BOB AI Mega Expansion - REST API Integration Guide

## Overview

The `bob_ai_api_endpoints.py` module provides 5 new REST API endpoints for accessing BOB AI's vast discipline library through a RESTful interface.

## New Endpoints

### 1. GET `/api/disciplines/all`

**Get all available disciplines**

Returns paginated list of all 136+ disciplines with their library counts.

**Query Parameters:**

- `limit`: Max results (default: 100, max: 500)
- `offset`: Pagination offset (default: 0)
- `search`: Filter disciplines by name

**Example Request:**

```bash
curl "http://localhost:5000/api/disciplines/all?limit=10&offset=0"
```

**Example Response:**

```json
{
  "status": "success",
  "timestamp": "2025-10-28T09:15:00",
  "data": {
    "total": 136,
    "returned": 10,
    "offset": 0,
    "limit": 10,
    "disciplines": [
      {
        "name": "Linear Regression",
        "packages_count": 3,
        "tools_count": 3,
        "resources_count": 3
      }
    ]
  }
}
```

---

### 2. GET `/api/disciplines/<name>/libraries`

**Get all libraries for a specific discipline**

Returns packages, tools, and resources for a discipline.

**Path Parameters:**

- `name`: Discipline name (URL-encoded)

**Example Request:**

```bash
curl "http://localhost:5000/api/disciplines/Linear%20Regression/libraries"
```

**Example Response:**

```json
{
  "status": "success",
  "timestamp": "2025-10-28T09:15:00",
  "data": {
    "discipline": "Linear Regression",
    "packages": ["scikit-learn", "statsmodels", "scipy"],
    "tools": ["jupyter", "numpy", "pandas"],
    "resources": ["scikit-learn documentation", "Statistics tutorial"],
    "summary": {
      "packages_count": 3,
      "tools_count": 3,
      "resources_count": 2,
      "total_libraries": 8
    }
  }
}
```

---

### 3. GET `/api/categories`

**Get category structure**

Returns categorized grouping of disciplines.

**Example Request:**

```bash
curl "http://localhost:5000/api/categories"
```

**Example Response:**

```json
{
  "status": "success",
  "timestamp": "2025-10-28T09:15:00",
  "data": {
    "total_categories": 1000,
    "categories_defined": 5,
    "sample_categories": [
      {
        "name": "AI & Machine Learning",
        "discipline_count": 45,
        "sample_disciplines": ["Linear Regression", "Decision Trees", ...]
      }
    ],
    "statistics": {
      "total_disciplines": 136,
      "total_packages": 234,
      "total_tools": 89,
      "average_disciplines_per_category": 27.2
    }
  }
}
```

---

### 4. POST `/api/learning-path`

**Generate a learning path for a discipline**

Creates a structured learning path with phases, timelines, and resources.

**Request Body:**

```json
{
  "discipline": "Machine Learning",
  "estimated_hours": 250,
  "skill_level": "beginner"
}
```

**Example Request:**

```bash
curl -X POST "http://localhost:5000/api/learning-path" \
  -H "Content-Type: application/json" \
  -d '{"discipline": "Linear Regression", "estimated_hours": 100, "skill_level": "beginner"}'
```

**Example Response:**

```json
{
  "status": "success",
  "timestamp": "2025-10-28T09:15:00",
  "data": {
    "discipline": "Linear Regression",
    "estimated_hours": 100,
    "skill_level": "beginner",
    "phases": [
      {
        "phase": 1,
        "name": "Fundamentals",
        "hours": 15,
        "topics": ["Basic Concepts", "Theory Introduction"],
        "difficulty": "beginner"
      },
      {
        "phase": 2,
        "name": "Core Concepts",
        "hours": 30,
        "topics": ["Deep Dive", "Hands-on Practice"],
        "difficulty": "intermediate"
      },
      {
        "phase": 3,
        "name": "Advanced Topics",
        "hours": 30,
        "topics": ["Complex Scenarios", "Optimization"],
        "difficulty": "advanced"
      },
      {
        "phase": 4,
        "name": "Capstone Project",
        "hours": 25,
        "topics": ["Real-world Application", "Portfolio Building"],
        "difficulty": "advanced"
      }
    ],
    "resources": {
      "packages": ["scikit-learn", "statsmodels", "scipy"],
      "tools": ["jupyter", "numpy", "pandas"],
      "learning_resources": ["Documentation", "Tutorials"]
    },
    "total_phases": 4,
    "completion_weeks": 14.3
  }
}
```

---

### 5. GET `/api/recommendations/tools`

**Get tool recommendations**

Returns recommended tools based on disciplines or use case.

**Query Parameters:**

- `disciplines`: Comma-separated discipline names (optional)
- `use_case`: Specific use case (optional)
- `top_n`: Number of recommendations (default: 10, max: 50)

**Example Request:**

```bash
curl "http://localhost:5000/api/recommendations/tools?top_n=5"
```

**Example Response:**

```json
{
  "status": "success",
  "timestamp": "2025-10-28T09:15:00",
  "data": {
    "recommendations": [
      {
        "tool": "jupyter",
        "frequency": 45,
        "disciplines": ["Linear Regression", "Decision Trees", ...],
        "use_cases": ["Development", "Research", "Education"]
      },
      {
        "tool": "numpy",
        "frequency": 42,
        "disciplines": ["Data Science", "Deep Learning", ...],
        "use_cases": ["Development", "Production"]
      }
    ],
    "total_recommendations": 5,
    "based_on": "all"
  }
}
```

---

### 6. GET `/api/disciplines/health`

**Health check endpoint**

Verifies BOB AI Mega Expansion is operational and returns statistics.

**Example Request:**

```bash
curl "http://localhost:5000/api/disciplines/health"
```

**Example Response:**

```json
{
  "status": "success",
  "timestamp": "2025-10-28T09:15:00",
  "data": {
    "status": "healthy",
    "bob_ai_mega_available": true,
    "disciplines": 136,
    "packages": 234,
    "tools": 89
  },
  "message": "BOB AI Mega Expansion endpoints are operational"
}
```

---

## Integration Steps

### Step 1: Add Blueprint to main.py

In `backend/main.py`, add these imports at the top:

```python
from bob_ai_api_endpoints import bob_ai_blueprint
```

### Step 2: Register Blueprint

After Flask app initialization (around line 80-100 in main.py), add:

```python
# Register BOB AI Mega Expansion endpoints
app.register_blueprint(bob_ai_blueprint)
logger.info("[ORFEAS] BOB AI Mega Expansion API endpoints registered")
```

### Step 3: Restart Backend

```bash
cd backend
python main.py
```

### Step 4: Test Endpoints

```bash
# Test health
curl http://localhost:5000/api/disciplines/health

# Test get all disciplines
curl http://localhost:5000/api/disciplines/all?limit=5

# Test learning path
curl -X POST http://localhost:5000/api/learning-path \
  -H "Content-Type: application/json" \
  -d '{"discipline": "Linear Regression"}'
```

---

## Response Format

All endpoints follow a consistent response format:

```json
{
  "status": "success|error",
  "timestamp": "ISO-8601 timestamp",
  "data": { /* endpoint-specific data */ },
  "message": "Optional message"
}
```

**HTTP Status Codes:**

- `200`: Successful request
- `400`: Bad request (missing parameters)
- `404`: Resource not found
- `503`: BOB AI not available
- `500`: Server error

---

## CORS & Security

All endpoints support CORS (`@cross_origin()` decorator). For production deployment, update CORS settings in main.py:

```python
cors_config = {
    "origins": ["https://yourdomain.com"],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type"]
}
CORS(app, resources={"/api/*": cors_config})
```

---

## Error Handling

The module includes comprehensive error handling:

- **Missing Parameters**: Returns 400 with error description
- **Not Found**: Returns 404 if discipline doesn't exist
- **Server Errors**: Returns 500 with error details
- **Library Unavailable**: Returns 503 if BOB AI database not loaded

---

## Performance Notes

### Pagination

Use pagination for large result sets:

```bash
# Get first 50 disciplines
curl "http://localhost:5000/api/disciplines/all?limit=50&offset=0"

# Get next 50
curl "http://localhost:5000/api/disciplines/all?limit=50&offset=50"
```

### Caching

Recommendations: Implement client-side caching for frequently accessed endpoints:

```javascript
// Frontend example
const cache = new Map();

async function getDisciplines() {
  const cacheKey = 'disciplines-all';
  if (cache.has(cacheKey)) {
    return cache.get(cacheKey);
  }

  const response = await fetch('/api/disciplines/all');
  const data = await response.json();
  cache.set(cacheKey, data);
  return data;
}
```

---

## Testing

### Using cURL

```bash
# Get all disciplines
curl -X GET "http://localhost:5000/api/disciplines/all?limit=10"

# Get specific discipline libraries
curl -X GET "http://localhost:5000/api/disciplines/Linear%20Regression/libraries"

# Create learning path
curl -X POST "http://localhost:5000/api/learning-path" \
  -H "Content-Type: application/json" \
  -d "{\"discipline\": \"Linear Regression\", \"estimated_hours\": 100}"

# Get recommendations
curl -X GET "http://localhost:5000/api/recommendations/tools?top_n=10"
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:5000/api"

# Get all disciplines
response = requests.get(f"{BASE_URL}/disciplines/all?limit=10")
print(response.json())

# Create learning path
response = requests.post(
    f"{BASE_URL}/learning-path",
    json={
        "discipline": "Linear Regression",
        "estimated_hours": 100,
        "skill_level": "beginner"
    }
)
print(response.json())
```

### Using JavaScript/Fetch

```javascript
const BASE_URL = "http://localhost:5000/api";

// Get all disciplines
fetch(`${BASE_URL}/disciplines/all?limit=10`)
  .then(r => r.json())
  .then(data => console.log(data));

// Create learning path
fetch(`${BASE_URL}/learning-path`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    discipline: 'Linear Regression',
    estimated_hours: 100,
    skill_level: 'beginner'
  })
})
  .then(r => r.json())
  .then(data => console.log(data));
```

---

## Monitoring & Logging

All API calls are logged to the backend console:

```
[API] GET /api/disciplines/all - Returned 10 disciplines
[API] GET /api/disciplines/Linear Regression/libraries - Success
[API] POST /api/learning-path - Created path for Machine Learning
```

Errors are logged with full context:

```
[ERROR] GET /api/disciplines/all: KeyError - 'discipline'
```

---

## Troubleshooting

### "BOB AI Mega Library not available" (503)

**Problem**: BOB AI database not loaded

**Solution**:

1. Verify `bob_ai_mega_library_database_5000.py` exists in backend folder
2. Check imports are correct in `bob_ai_api_endpoints.py`
3. Restart backend: `python main.py`

### "Discipline not found" (404)

**Problem**: Discipline name doesn't match

**Solution**:

1. Get list of all disciplines: `GET /api/disciplines/all`
2. Use exact name from list
3. URL-encode special characters: `/Linear%20Regression`

### CORS errors

**Problem**: Frontend can't access API

**Solution**:

1. Update CORS config in main.py
2. Ensure frontend URL is in `cors_config["origins"]`
3. Check browser console for error details

---

## Documentation Index

- **API Reference**: This file
- **Backend Integration**: `backend/bob_ai_api_endpoints.py`
- **Database**: `backend/bob_ai_mega_library_database_5000.py`
- **Frontend Integration**: (Next.js hooks in frontend)

---

**Last Updated:** October 28, 2025
**Status:** Ready for Integration
**Version:** 1.0.0
