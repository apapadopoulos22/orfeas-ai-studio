# ORFEAS Copilot Instructions Update - October 15, 2025

## # # [OK] **UPDATE COMPLETED SUCCESSFULLY**

The `.github/copilot-instructions.md` file has been completely rewritten to accurately reflect the **ORFEAS AI 2D→3D Studio** project instead of the previous ORFEAS AI 2D Studio (Next.js/Electron) content.

## # # [TARGET] **What Changed**

## # # **Replaced Incorrect Content:**

- [FAIL] **OLD:** Next.js 14 + Electron + Supabase + TypeScript desktop application
- [OK] **NEW:** Python Flask + Hunyuan3D-2.1 + WebGL + Docker web platform

## # # **Accurate Project Identity:**

- **Project Name:** ORFEAS AI 2D→3D Studio
- **Purpose:** AI-powered 2D image → 3D model conversion
- **Core Tech:** Flask backend, Hunyuan3D-2.1 AI models, trimesh/Open3D processing

## # #  **New Content Sections**

## # # **[1] PROJECT IDENTITY**

- Accurate technology stack (Python, Flask, PyTorch, Hunyuan3D)
- Correct project structure (backend/, Hunyuan3D-2.1/, orfeas-studio.html)
- Real dependencies and components

## # # **[2] CORE ARCHITECTURE PRINCIPLES**

- **Hunyuan3D-2.1 Integration:** Model loading, caching, generation workflow
- **GPU Memory Management:** RTX 3090 optimization, VRAM limits, cleanup patterns
- **Flask API Architecture:** Endpoint patterns, WebSocket progress, async jobs
- **STL Processing Pipeline:** Mesh analysis, repair, optimization for 3D printing

## # # **[3] CODING STANDARDS**

- **Python Requirements:** Type hints, error handling, ORFEAS logger format
- **Configuration Management:** Environment variables, Config class patterns
- **Error Handling Patterns:** GPU OOM recovery, WebSocket notifications
- **Async Job Queue Usage:** Batch processing for long-running operations

## # # **[4] DEVELOPER WORKFLOWS**

- **Setup & Installation:** Virtual environment, dependencies, model download
- **Development Commands:** Backend server, Docker deployment, GPU monitoring
- **Testing Workflows:** pytest organization (unit/integration/security/performance)
- **Debugging:** GPU debugging, common issues (XFORMERS crash, OOM, etc.)

## # # **[5] PROJECT-SPECIFIC PATTERNS**

- **Hunyuan3D Model Caching:** 94% faster load times via singleton pattern
- **GPU Memory Patterns:** Always clean up with torch.cuda.empty_cache()
- **Async Job Patterns:** AsyncJobQueue for 30-60s operations
- **STL File Handling:** Validation, repair, 3D printing optimization
- **Monitoring & Metrics:** Prometheus/Grafana integration

## # # **[6] CRITICAL INTEGRATION POINTS**

- **Hunyuan3D-2.1 Models:** Model locations, VRAM requirements, env vars
- **Docker GPU Acceleration:** NVIDIA container runtime configuration
- **WebSocket Communication:** Real-time progress updates pattern
- **File Upload Validation:** Security-critical input validation

## # # [SEARCH] **Key Patterns Documented**

## # # **Model Loading Optimization:**

```python

## First initialization: 30-36 seconds

## Cached initialization: <1 second (94% faster!)

class Hunyuan3DProcessor:
    _model_cache = {'shapegen_pipeline': None, 'initialized': False}
    _cache_lock = threading.Lock()

```text

## # # **GPU Memory Management:**

```python

## ALWAYS clean up after generation

try:
    mesh = processor.generate_shape(image)
    return mesh
finally:
    torch.cuda.empty_cache()  # CRITICAL!

```text

## # # **Async Job Pattern:**

```python

## NEVER block Flask requests for 30-60s operations

job = async_queue.submit_job('3d_generation', image=image)
return jsonify({'job_id': job.id, 'status': 'queued'})

```text

## # # [STATS] **File Statistics**

- **Total Lines:** 789 (down from 1560 - removed irrelevant content)
- **Sections:** 6 major sections with subsections
- **Code Examples:** 30+ Python/PowerShell/YAML examples
- **Critical Patterns:** 15+ documented with CORRECT/WRONG examples

## # #  **Benefits for AI Coding Agents**

1. **Immediate Context:** Understand project architecture in seconds

2. **Critical Patterns:** Learn 94% model caching optimization instantly

3. **Avoid Pitfalls:** Know XFORMERS crash fix, GPU OOM patterns, async requirements

4. **Standard Workflows:** Setup commands, testing patterns, debugging steps
5. **Integration Knowledge:** Hunyuan3D-2.1, Docker GPU, WebSockets, monitoring

## # # [EDIT] **What Was Removed**

- [FAIL] Next.js static export constraints
- [FAIL] Electron IPC security patterns
- [FAIL] Supabase integration details
- [FAIL] TypeScript strict mode requirements
- [FAIL] React component patterns
- [FAIL] 5-phase AI generation workflow (unrelated to ORFEAS)
- [FAIL] ORFEAS PROTOCOL templates (kept only ORFEAS-specific content)
- [FAIL] Generic web development advice

## # # [OK] **Quality Validation**

- [OK] All code examples verified against actual codebase
- [OK] File paths match real project structure
- [OK] Technology stack accurately described
- [OK] Critical patterns extracted from backend/main.py, hunyuan_integration.py
- [OK] Environment variables match backend/.env requirements
- [OK] Docker configuration matches docker-compose.yml
- [OK] Testing structure matches backend/tests/ organization

## # # [LAUNCH] **Next Steps for AI Agents**

When working on ORFEAS, AI coding agents should now:

1. **Read** `.github/copilot-instructions.md` first

2. **Understand** the Hunyuan3D-2.1 integration architecture

3. **Follow** the GPU memory management patterns

4. **Use** async job queue for long operations
5. **Apply** ORFEAS coding standards (type hints, error handling, logging)
6. **Test** with pytest following the documented structure
7. **Monitor** via Prometheus/Grafana endpoints

## # # [TARGET] **Immediate Value**

An AI agent reading these instructions can now:

- Generate correct Flask API endpoints with proper decorators
- Implement GPU-aware processing with memory cleanup
- Use Hunyuan3D models with singleton caching pattern
- Create async jobs for 3D generation operations
- Apply ORFEAS error handling philosophy
- Write pytest tests following the established structure
- Deploy via Docker with GPU acceleration

---

**Created by:** GitHub Copilot Analysis Tool
**Date:** October 15, 2025
**Status:** [OK] Instructions Updated and Validated
