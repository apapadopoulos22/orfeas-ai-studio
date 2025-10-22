# ORFEAS API Endpoint Mapping

## Document Information

- **Date:** 2025-10-19
- **Version:** 2.0.0
- **Status:** Standardized

## Executive Summary

This document provides a complete mapping of all ORFEAS API endpoints,
including their methods, descriptions, and response formats.

## Endpoint Categories

### Health & Status Endpoints

- GET /health
- GET /ready
- GET /api/health
- GET /metrics

### 3D Generation Endpoints

- POST /api/generate-3d
- GET /api/v1/gpu/stats
- POST /api/batch-3d

### File Management Endpoints

- POST /upload
- GET /download/<file_id>
- DELETE /delete/<file_id>

### Project Management Endpoints (Phase 6C)

- POST /api/v1/projects/create
- GET /api/v1/projects/list
- GET /api/v1/projects/<id>

### WebSocket Endpoints

- WS /socket.io

## Standardization Status

### ✅ Verified Endpoints

- /metrics
- /test-simple
- /api/health
- /api/v1/gpu/stats
- /debug/flask-blueprints
- /api/performance/summary
- /api/performance/recommendations
- /api/gpu/status
- /api/ultra-performance/status
- /api/ultra-performance/config

### ⚠️ Frontend-Only Endpoints (Need Backend Implementation)

- /api/log-error
- /manifest.json

### ℹ️ Backend-Only Endpoints (Not Called by Frontend)

- /api/ultra-generate-3d
- /api/stl/repair
- /api/download/<job_id>/<filename>
- /api/performance/recommendations
- /api/performance/summary

## Recommendations

1. **Immediate:** Document all verified endpoints

2. **Short-term:** Implement missing backend endpoints

3. **Future:** Add advanced endpoints for Phase 6C features

## API Base URL

- Development: `http://localhost:5000`
- Production: `https://api.orfeas.studio`

## Authentication

API key authentication required for all endpoints (to be implemented Phase 6).

## Rate Limiting

- Default: 100 requests per minute per IP
- Authenticated: 1000 requests per minute per user
- Premium: Unlimited

## CORS Configuration

- Development: All origins allowed
- Production: Specific origins only
