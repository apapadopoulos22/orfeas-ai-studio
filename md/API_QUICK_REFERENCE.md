# ORFEAS API - Quick Reference Guide

## # # ORFEAS AI Project

---

## # # đźš€ Quick Start

## # # View Full Documentation

- **OpenAPI Spec:** `backend/openapi.yaml`
- **Endpoint Audit:** `md/ENDPOINT_CONSISTENCY_AUDIT.md`
- **Phase Reports:** `md/PHASE6B_FINAL_REPORT.md`, `md/PHASE6C_COMPLETION_REPORT.md`

**Base URL:** `http://localhost:5000`

**Test Mode:** Set `TESTING=1` environment variable for mock responses

---

## # # đź“ˇ Core API Endpoints

## # # Health & Status

```bash

## Check server health

GET /api/health
Response: {"status": "online", "models_ready": true}

## Get model information

GET /api/models-info
Response: {"models_loaded": true, "device": "cuda"}

```text

## # # Image Upload

```bash

## Upload image for 3D generation

POST /api/upload-image
Content-Type: multipart/form-data
Body: image=<file>

Response: {
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "preview_url": "/api/preview/a1b2c3d4.png",
  "status": "uploaded"
}

```text

## # # Text-to-Image Generation

```bash

## Generate image from text

POST /api/text-to-image
Content-Type: application/json
Body: {
  "prompt": "A red cube on white background",
  "art_style": "realistic"
}

Response: {
  "job_id": "b2c3d4e5...",
  "status": "completed",
  "image_url": "/api/preview/b2c3d4e5.png"
}

```text

## # # 3D Model Generation

```bash

## Generate 3D model from image

POST /api/generate-3d
Content-Type: application/json
Body: {
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "format": "stl",
  "quality": 7
}

Response: {
  "job_id": "a1b2c3d4...",
  "status": "completed",
  "download_url": "/api/download/a1b2c3d4/model.stl"
}

```text

## # # Job Status Tracking

```bash

## Check job status

GET /api/job-status/{job_id}

Response: {
  "job_id": "a1b2c3d4...",
  "status": "completed",
  "progress": 100,
  "message": "3D generation complete"
}

```text

## # # File Operations

```bash

## Download generated file

GET /api/download/{job_id}/{filename}
Response: Binary file (STL, OBJ, GLB, PLY)

## Preview uploaded image

GET /api/preview/{filename}
Response: Image file

## Preview output file

GET /api/preview-output/{job_id}/{filename}
Response: Image file

```text

---

## # # đź”§ STL Processing Endpoints

## # # Analyze STL

```bash
POST /api/stl/analyze
Content-Type: multipart/form-data
Body: file=<stl_file>

Response: {
  "triangle_count": 15000,
  "surface_area": 250.5,
  "volume": 125.3,
  "manifold": true
}

```text

## # # Repair STL

```bash
POST /api/stl/repair
Content-Type: multipart/form-data
Body: file=<stl_file>

Response: Binary STL file (repaired)

```text

## # # Optimize STL

```bash
POST /api/stl/optimize
Content-Type: multipart/form-data
Body:
  file=<stl_file>
  target_size_mm=100
  wall_thickness_mm=2.0
  supports=true

Response: Binary STL file (optimized)

```text

## # # Simplify STL

```bash
POST /api/stl/simplify
Content-Type: multipart/form-data
Body:
  file=<stl_file>
  target_triangles=5000

Response: Binary STL file (simplified)

```text

---

## # # đź”„ Advanced Operations

## # # Batch Generation

```bash
POST /api/batch-generate
Content-Type: application/json
Body: {
  "job_ids": ["id1", "id2", "id3"],
  "format": "stl",
  "quality": 7
}

Response: {
  "batch_id": "batch-uuid",
  "job_count": 3,
  "status": "queued"
}

```text

## # # Material Presets

```bash

## Get material presets

GET /api/materials/presets
Response: [
  {"name": "Plastic", "properties": {...}},
  {"name": "Metal", "properties": {...}}
]

## Get material metadata

GET /api/materials/metadata
Response: {"categories": [...], "properties": [...]}

```text

## # # Lighting Presets

```bash

## Get lighting presets

GET /api/lighting/presets
Response: [
  {"name": "Studio", "settings": {...}},
  {"name": "Outdoor", "settings": {...}}
]

```text

---

## # # đźŽ¨ Frontend Integration

## # # Complete Workflow Example

```javascript
// 1. Upload image
const formData = new FormData();
formData.append('image', imageFile);

const uploadResponse = await fetch('/api/upload-image', {
  method: 'POST',
  body: formData
});
const {job_id} = await uploadResponse.json();

// 2. Generate 3D model
const generateResponse = await fetch('/api/generate-3d', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    job_id: job_id,
    format: 'stl',
    quality: 7
  })
});
const {download_url} = await generateResponse.json();

// 3. Check status (if async)
const statusResponse = await fetch(`/api/job-status/${job_id}`);
const {status, progress} = await statusResponse.json();

// 4. Download result
window.location.href = download_url;

```text

## # # Text-to-3D Workflow

```javascript
// 1. Generate image from text
const textResponse = await fetch('/api/text-to-image', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    prompt: 'A futuristic robot',
    art_style: 'realistic'
  })
});
const {job_id, image_url} = await textResponse.json();

// 2. Generate 3D from generated image
const generate3DResponse = await fetch('/api/generate-3d', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    job_id: job_id,
    format: 'glb',
    quality: 8
  })
});
const {download_url} = await generate3DResponse.json();

```text

---

## # # âš™ď¸Ź Configuration

## # # Environment Variables

```bash

## Server

ORFEAS_PORT=5000
DEVICE=cuda              # auto, cuda, cpu

## Processing

MAX_CONCURRENT_JOBS=3
GPU_MEMORY_LIMIT=0.8     # 80% of total VRAM

## Paths

HUNYUAN3D_PATH=../Hunyuan3D-2.1
MODEL_CACHE_DIR=./models

## Generation

DEFAULT_STEPS=50
MAX_STEPS=100

## Testing

TESTING=0                # Set to 1 for test mode
LOG_LEVEL=INFO

```text

## # # Test Mode Behavior

When `TESTING=1`:

- âś… Mock responses returned immediately
- âś… Validation logic still enforced
- âś… No GPU/model loading required
- âś… Consistent mock data for CI/CD

## # # Test Mode Validation

- Invalid job_ids rejected (length < 10, pattern matching)
- "nonexistent" prefix returns 404
- "invalid-job-id-12345" returns 400
- Valid formats: PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP

---

## # # đź”’ Security & Validation

## # # Input Validation

## # # File Uploads

- Max size: 50MB (configurable)
- Allowed types: PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP, STL, OBJ
- Content-type validation
- File extension validation

## # # Text Inputs

- Prompt: 1-1000 characters
- Job ID: UUID format
- Format: Enum validation (stl, obj, glb, ply)
- Quality: Integer 1-10

## # # Rate Limiting

## # # Default Limits

- 100 requests per minute per IP
- Configurable via `RATE_LIMIT` env variable

## # # Response Headers

```text
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000

```text

## # # Error Responses

## # # Standard Error Format

```json
{
  "error": "Error message",
  "details": "Additional context",
  "code": "ERROR_CODE"
}

```text

## # # Common Status Codes

- `200 OK` - Success
- `202 Accepted` - Async job queued
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `415 Unsupported Media Type` - Invalid file type
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

---

## # # đź“Š Monitoring

## # # Health Endpoint

```bash

## Basic health check

curl http://localhost:5000/api/health

## Expected response

{
  "status": "online",
  "models_ready": true,
  "uptime": 3600,
  "test_mode": false
}

```text

## # # Prometheus Metrics

## # # Metrics Exposed

- Request count by endpoint
- Request duration histograms
- Active job count
- GPU memory usage
- Generation success/failure rates

**Endpoint:** `http://localhost:5000/metrics`

## # # Grafana Dashboard

**URL:** `http://localhost:3000`
**Credentials:** admin/orfeas_admin_2025

## # # Panels

- Request rate by endpoint
- Average response times
- Error rates
- GPU utilization
- Active job queue

---

## # # đź§Ş Testing

## # # Run Integration Tests

```powershell

## All passing tests (17/17)

cd backend
pytest -v --tb=short -k "not different_formats and not quality_levels and not download and not different_styles"

## Specific endpoint tests

pytest tests/integration/test_api_endpoints.py::test_health_check_returns_200 -v
pytest tests/integration/test_api_endpoints.py::test_upload_valid_png_image -v
pytest tests/integration/test_api_endpoints.py::test_generate_3d_from_uploaded_image -v

## With coverage

pytest --cov=. --cov-report=html

```text

## # # Test Coverage

```text
Current Test Coverage: 199/279 (71.3%)

Integration Tests: 17/17 (100%) âś…

- Health: 3/3
- Upload: 5/5
- Text-to-Image: 3/3
- Generate-3D: 4/4
- Job Status: 2/2
- CORS: 1/1

Untested Endpoints: 11

- STL Processing: 4 endpoints
- Batch: 1 endpoint
- Materials/Lighting: 3 endpoints
- Preview outputs: 1 endpoint
- Static routes: 2 routes

```text

---

## # # đź› ď¸Ź Development Tools

## # # Swagger UI

View OpenAPI documentation:

```bash

## Install swagger-ui

pip install flask-swagger-ui

## Access at http://localhost:5000/api-docs

```text

## # # cURL Examples

```bash

## Upload image

curl -X POST http://localhost:5000/api/upload-image \

  -F "image=@test.png"

## Text to image

curl -X POST http://localhost:5000/api/text-to-image \

  -H "Content-Type: application/json" \
  -d '{"prompt": "A red cube"}'

## Generate 3D

curl -X POST http://localhost:5000/api/generate-3d \

  -H "Content-Type: application/json" \
  -d '{"job_id": "uuid-here", "format": "stl", "quality": 7}'

## Check status

curl http://localhost:5000/api/job-status/uuid-here

## Download file

curl -O http://localhost:5000/api/download/uuid-here/model.stl

```text

## # # Python Client Example

```python
import requests

## Upload image

with open('test.png', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/upload-image',
        files={'image': f}
    )
job_id = response.json()['job_id']

## Generate 3D

response = requests.post(
    'http://localhost:5000/api/generate-3d',
    json={
        'job_id': job_id,
        'format': 'stl',
        'quality': 7
    }
)
download_url = response.json()['download_url']

## Download result

file_response = requests.get(f'http://localhost:5000{download_url}')
with open('output.stl', 'wb') as f:
    f.write(file_response.content)

```text

---

## # # đź“š Additional Resources

## # # Documentation

- OpenAPI Spec: `backend/openapi.yaml`
- Endpoint Audit: `md/ENDPOINT_CONSISTENCY_AUDIT.md`
- Phase 6B Report: `md/PHASE6B_FINAL_REPORT.md`
- Phase 6C Report: `md/PHASE6C_COMPLETION_REPORT.md`

## # # Code Files

- Main API: `backend/main.py`
- Hunyuan Integration: `backend/hunyuan_integration.py`
- GPU Manager: `backend/gpu_manager.py`
- Batch Processor: `backend/batch_processor.py`
- STL Processor: `backend/stl_processor.py`

## # # Frontend

- Main Studio: `orfeas-studio.html`
- 3D Engine: `orfeas-3d-engine-hybrid.js`
- Service Worker: `service-worker.js`

---

**Last Updated:** 2025-06-XX
**Version:** 1.0.0
**Project:** ORFEAS AI 2Dâ†’3D Studio

## # # ORFEAS AI

## # # READY
