# ORFEAS API ENDPOINT CONSISTENCY AUDIT (Updated)

Date: 2025-10-19
Status: AUDIT UPDATED (code-verified)

Summary

- This update reconciles the authoritative backend routes in backend/main.py and blueprints with documentation, adding new sections for LLM (/api/llm/*), Local LLM (/api/local-llm/*), Agent API (/api/agent/*), Agent Coordination (/api/agents/*), and Performance/GPU/Ultra endpoints. Prior Core/STL/Advanced/Static sections remain valid.
- Source of truth: backend/main.py + blueprints backend/llm_routes.py and backend/agent_api.py.

Core API Endpoints (verified)

- GET /api/health
- GET /api/models-info
- POST /api/upload-image
- POST /api/text-to-image
- POST /api/generate-3d
- GET /api/job-status/<job_id>
- GET /api/download/<job_id>/<filename>
- GET /api/preview/<filename>
- GET /api/preview-output/<job_id>/<filename>

STL Processing (verified)

- POST /api/stl/analyze
- POST /api/stl/repair
- POST /api/stl/optimize
- POST /api/stl/simplify

Advanced Generation/Presets (verified)

- POST /api/batch-generate
- GET  /api/materials/presets
- GET  /api/lighting/presets
- POST /api/materials/metadata
- POST /api/materials/export-mtl

LLM Endpoints (implemented in backend/main.py)

- POST /api/llm/generate
- POST /api/llm/code-generate
- POST /api/llm/orchestrate
- POST /api/llm/analyze-code
- POST /api/llm/debug-code
- GET  /api/llm/models
- GET  /api/llm/status

Local LLM Blueprint (backend/llm_routes.py, mounted at /api/local-llm)

- GET  /api/local-llm/status
- POST /api/local-llm/generate

Notes: Controlled by ENABLE_LOCAL_LLMS (default true). Uses local_llm_router; separate from /api/llm/*.

Agent API Blueprint (backend/agent_api.py, mounted at /api/agent)

- POST /api/agent/generate-3d
- POST /api/agent/batch
- GET  /api/agent/status/<job_id>
- GET  /api/agent/download/<filename>
- GET  /api/agent/health

Notes: HMAC-auth wrapper via require_agent_token; job queue and GPU manager integrated.

Agent Coordination (implemented in backend/main.py)

- GET  /api/agents/status
- POST /api/agents/submit-task
- POST /api/agents/intelligent-generation
- GET  /api/agents/coordination/status
- GET  /api/agents/communication/message-stats

Notes: Distinct from `/api/agent/*` (which is a blueprint). `/api/agents/*` is orchestration/coordination.

Performance/GPU/Ultra (backend/main.py)

- GET  /api/performance/summary
- GET  /api/performance/recommendations
- GET  /api/gpu/status
- GET  /api/ultra-performance/status
- GET|POST /api/ultra-performance/config
- POST /api/ultra-performance/enable
- POST /api/ultra-performance/disable

Debug/Introspection

- GET /debug/flask-blueprints

Static/Frontend

- GET / (redirects to /studio)
- GET /studio (serves orfeas-studio.html)
- GET /<path:filename> (static files)

Totals (current)

- Core + STL + Advanced + Static: 9 + 4 + 5 + 3 = 21
- LLM: 7
- Local LLM: 2
- Agent API: 5
- Agent Coordination: 5
- Performance/GPU/Ultra: 7
- Debug: 1

Grand total endpoints/routes listed: 48

Conventions & Status

- Prefix: All API endpoints use /api/ except debug/static.
- Naming: Kebab-case for multiword segments (e.g., text-to-image).
- Methods: GET for read; POST for create/process; mixed where appropriate (ultra-performance/config supports GET|POST).
- Responses: JSON for APIs; binary for downloads/previews; consistent error format in main.py/agent_api.py.

## Distinctions to keep clear

- `/api/llm/*` vs `/api/local-llm/*`: Cloud/enterprise LLM orchestration vs local Ollama (blueprint).
- `/api/agent/*` vs `/api/agents/*`: Authenticated agent execution API vs coordination/orchestration endpoints.

Changes since 2025-10-16 audit

- Added LLM endpoints under /api/llm/* (implemented in main.py lines ~3015–3304).
- Confirmed Local LLM blueprint at /api/local-llm/* (llm_routes.py; registered in main.py line ~1065).
- Added Agent API blueprint endpoints at /api/agent/* (agent_api.py).
- Added Agent Coordination suite at /api/agents/* (main.py lines ~1400–1569).
- Added Performance/GPU/Ultra endpoints (main.py lines ~1198–1373).
- Core/STL/Advanced/static routes remain accurate.

Open items and recommendations

- OpenAPI: Generate and publish OpenAPI 3.0 spec covering all endpoint groups.
- DELETE endpoints: Consider job/resource cleanup endpoints (e.g., DELETE /api/job/<id>).
- Batch status: Optional GET /api/batch-status/<batch_id> for batch tracking.
- Versioning: Consider /api/v1/... on next major release.
- Tests: Expand integration tests for STL, batch, presets, LLM and agents; include performance endpoints.

Verification notes

- Verified via targeted grep in backend/main.py for each group and direct reads of backend/llm_routes.py and backend/agent_api.py.
- For quick introspection at runtime, use GET /debug/flask-blueprints.

Quality gates (doc-only)

- Markdown lint: Cleaned to pass standard MD rules (headings, lists, links). Will validate via fix_markdown_lint.ps1.

End of audit (2025-10-19)
