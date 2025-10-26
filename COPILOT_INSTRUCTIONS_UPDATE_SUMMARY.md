# Copilot Instructions Update Summary - October 26, 2025

## Overview

Successfully analyzed the ORFEAS AI codebase and generated an updated
`.github/copilot-instructions.md` file tailored specifically to this project's
architecture and development patterns.

## What Was Updated

### Location

`c:\Users\johng\Documents\oscar\.github\copilot-instructions.md`

### Key Sections Added/Enhanced

1. **Architecture Overview** - Clear 3-layer service diagram explaining:
   - Frontend (HTML5/Next.js)
   - Backend (Flask + SocketIO + PyTorch)
   - Hunyuan3D Model (submodule with ShapeGen/TexGen)

2. **Lazy Model Loading Pattern** - Deep dive into:
   - Thread-safe singleton caching in `hunyuan_integration.py`
   - Critical environment variable initialization sequence
   - Why models load on first request (avoids 50s startup hangs)

3. **GPU Memory Management** - Production pattern:
   - Try-finally with explicit `torch.cuda.empty_cache()`
   - VRAM budget tracking with `get_gpu_manager()`
   - Reference to `gpu_optimization_advanced.py`

4. **WebSocket Real-Time Progress** - Documented pattern:
   - Backend: `websocket_manager.py` + `progress_tracker.py` integration
   - Frontend: JavaScript Socket.IO client example
   - 5-stage pipeline with ETA calculation (85-95% accurate)

5. **Error Handling & Fallbacks** - Safe degradation pattern:
   - Try-catch-finally with fallback to lightweight MiDaS processor
   - Design philosophy: "fail-safe with fallback" over strict validation

6. **Key Files Reference Table** - Documents:
   - `main.py` (6000+ lines) - Flask app, WebSocket
   - `hunyuan_integration.py` (886 lines) - 3D generation
   - `gpu_manager.py` (566 lines) - VRAM management
   - `websocket_manager.py` (350+ lines) - Real-time communication
   - `progress_tracker.py` (400+ lines) - Job tracking
   - Supporting modules with responsibilities

7. **Environment Variables** - Critical settings:
   - GPU & model loading (`DEVICE`, `XFORMERS_DISABLED`, `HOME`)
   - WebSocket configuration (`FLASK_ENV`, `CORS_ORIGINS`)
   - LLM optional settings (Ollama integration)
   - Monitoring (`LOG_LEVEL`, `ENABLE_MONITORING`)

8. **Testing & Validation** - Development commands:
   - Health check, unit tests, integration tests
   - WebSocket real-time testing
   - Load testing with Locust

9. **Common Issues & Solutions** - 6 frequent problems with fixes:
   - Startup hangs, model not found on Windows, CUDA OOM, DLL crashes
   - WebSocket timeouts, STL corruption

10. **Development Workflow** - 5-step process:
    - Change in isolated module
    - Run unit tests
    - Test with real generation
    - Check WebSocket logs
    - Don't modify core files lightly

11. **Advanced Features** - Progressive rendering (4-6x speedup)
    - 3-stage results pipeline
    - Files: `progressive_renderer.py`, `intelligent_cache.py`

12. **Documentation References** - Links to related docs:
    - `COPILOT_ADVANCED_PATTERNS.md`
    - `COPILOT_DEPLOYMENT_GUIDE.md`
    - `COPILOT_LLM_PATTERNS.md`

## Key Insights Discovered During Analysis

### Architecture Patterns

- **Lazy Loading**: Models intentionally defer to first request (avoids startup crash)
- **Thread-Safe Caching**: Uses `threading.RLock()` for concurrent access safety
- **Real-Time Streaming**: WebSocket with room-based messaging for scalability
- **Graceful Degradation**: FallbackProcessor ensures users always get results

### Critical Environment Setup

The project has strict initialization requirements that must happen BEFORE imports:

1. `ORT_TENSORRT_UNAVAILABLE=1` - Prevents ONNX Runtime crash
2. `XFORMERS_DISABLED=1` - Prevents Windows DLL initialization failure
3. `HY3DGEN_MODELS` - Must be set before hy3dgen module import
4. `HOME` - Windows path fix for cache resolution (uses backslashes only)

### Performance Optimizations Documented

- Progressive rendering returns 3 quality tiers (0.5s → 15s → 60s)
- Intelligent caching with historical learning for ETA accuracy (85-95%)
- GPU batch processing with dynamic VRAM management
- WebSocket throttling (-93% event traffic)

### Testing Strategy

- Unit tests for isolated modules
- Integration tests with real GPU operations
- WebSocket real-time tests with `test_websocket_progress.py`
- Load testing via Locust

## File Statistics

- **Total Lines**: 194 lines (concise, focused content)
- **Code Examples**: 8 production-grade code samples
- **Tables**: 4 reference tables (key files, issues, environment vars)
- **Documentation Links**: 4 references to extended docs
- **Sections**: 12 major sections

## What This Enables for AI Agents

With this updated instructions file, any GitHub Copilot or AI coding agent working
on this project will:

1. **Immediately understand** the 3-layer architecture without reading 6000 lines of code
2. **Avoid common pitfalls** (startup hangs, DLL crashes, CUDA OOM) with documented solutions
3. **Follow established patterns** for lazy loading, GPU memory, WebSocket, error handling
4. **Know which files to modify** for specific features and their dependencies
5. **Test properly** with specific pytest commands and WebSocket validation
6. **Debug efficiently** with reference to log locations and key metrics
7. **Optimize safely** with knowledge of progressive rendering and caching strategies

## Next Steps (Optional)

To further enhance the instructions, consider documenting:

1. **Database Layer** (if PostgreSQL is used for job queuing)
2. **Frontend Architecture** (Next.js + PWA + Three.js/BabylonJS integration)
3. **Deployment Pipeline** (Docker, Kubernetes, CI/CD specifics)
4. **Multi-LLM Orchestration** (how local + cloud LLM routing works)
5. **Security Model** (OAuth2, RBAC, SSL/TLS enforcement)

## Verification

The updated `.github/copilot-instructions.md` file is now:

- ✅ Created at correct location
- ✅ Contains architecture overview
- ✅ Documents 4 critical patterns with code examples
- ✅ References actual codebase files with line counts
- ✅ Includes development workflow and testing strategy
- ✅ Provides troubleshooting guide with solutions
- ✅ Formatted for clarity and quick reference
