# GitHub Copilot Instructions - October 28, 2025 Update

## Summary

Updated `.github/copilot-instructions.md` with comprehensive project-specific conventions and patterns to help AI coding agents be immediately productive in the ORFEAS codebase.

## What Was Added

### 1. **Quick Start for Coding Agents**

- Environment setup instructions (Windows PowerShell)
- Critical environment variable ordering
- Backend/frontend startup commands
- Pre-startup checklist

### 2. **Project-Specific Conventions & Patterns** (NEW SECTION)

#### Code Organization Conventions

- Module naming patterns (public vs. internal)
- Testing patterns with pytest markers
- Logging standards with `[ORFEAS]` prefix for traceability

#### Backend-Specific Patterns

- **Factory Functions Pattern**: Use `get_gpu_manager()` instead of direct instantiation
- **Thread-Safe Cache Pattern**: Double-check locking idiom for expensive initialization
- **Error Recovery Pattern**: Try-finally with explicit GPU cleanup
- **WebSocket Room-Based Messaging**: Publish-subscribe pattern using Socket.IO rooms

#### Frontend-Specific Patterns

- Socket.IO connection management hook (`useSocket`)
- Section navigation pattern for HTML monolith
- Three.js model loading strategy (static vs. WebGPU vs. fallback)

#### GPU Memory Management Conventions

- VRAM budget breakdown for RTX 3090 (24GB total)
- Pre-check pattern (check before job, cleanup after)
- Device selection fallback hierarchy

#### API Endpoint Patterns

- **Synchronous endpoints**: `/health`, `/metrics`, `/api/download/:id`
- **Asynchronous endpoints**: `/api/generate-3d`, `/api/upload-image`
- **Polling fallback**: `/api/job-status/:id` for WebSocket unavailability

#### Environment Variable Initialization (CRITICAL)

- 6-step initialization sequence (order matters!)
- Why this matters: Module import-time variable reading
- Common mistakes and how to avoid them

#### Quality Assurance Conventions

- 4-layer validation pipeline
- Prometheus metrics tracked automatically
- Monitoring enable flag: `ENABLE_MONITORING=true`

#### Incremental Startup Pattern

- Phase 1: Fast (~3-5s) - Framework initialization
- Phase 2: On-Demand (~30s) - Lazy model loading
- Rationale: Developer feedback + production efficiency

## Key Discoveries About This Codebase

### Architecture Insights

- **Lazy loading is mandatory**: Models load on first request, not startup (avoids 50s hangs)
- **Thread-safe singletons everywhere**: GPU manager, model cache, LLM router all use locking
- **WebSocket rooms = lightweight subscriptions**: No database required, in-memory room management
- **Graceful degradation is built-in**: GPU → CPU fallback, polling → WebSocket fallback

### Developer Workflow Essentials

- Environment variables MUST be set before Python import (import-time reading)
- GPU cleanup is critical after EVERY operation (no leaks)
- Factory functions enable mocking/testing (don't use constructors directly)
- Tests marked with `@pytest.mark.unit` or `@pytest.mark.integration` for filtering

### Common Pitfalls to Avoid

1. Setting environment variables AFTER imports (startup crash)
2. Forgetting `torch.cuda.empty_cache()` after GPU operations (memory leak)
3. Using constructors instead of factory functions (can't mock/test)
4. Broadcasting WebSocket events globally instead of using rooms (performance degradation)
5. Not implementing graceful fallback for GPU operations (service outage)

## File Changes

**Modified File**: `.github/copilot-instructions.md`

- **Lines Added**: ~250 lines of project-specific conventions
- **Total File Size**: 1,900+ lines (comprehensive reference)
- **Sections**: 16 major sections covering architecture, patterns, and conventions

## How AI Agents Should Use This

1. **First Reference**: Read "Quick Start for Coding Agents" at the top
2. **Architecture Questions**: Reference "Quick Architecture Map" and "Core Module Discovery Map"
3. **Implementation**: Jump to "PROJECT-SPECIFIC CONVENTIONS & PATTERNS" for code examples
4. **Debugging**: Check "Common Issues & Solutions" table (at line ~150 in original file)
5. **Patterns**: All patterns have real code examples from the codebase

## Validation

✅ **Patterns are discoverable** - All patterns found in actual codebase files
✅ **Examples are real** - Code snippets extracted from production files
✅ **Conventions are consistent** - Verified across multiple modules
✅ **Critical knowledge included** - Environment setup, GPU management, WebSocket patterns
✅ **Actionable** - Each pattern includes specific file references and line numbers

## Next Steps for Users

1. **Review** the new "PROJECT-SPECIFIC CONVENTIONS & PATTERNS" section
2. **Bookmark** the factory functions and error recovery patterns
3. **Verify** any assumptions about module imports and GPU handling
4. **Update** internal documentation to reference this file
5. **Share** with team members who work with AI coding agents

---

**Last Updated**: October 28, 2025
**Reference**: `.github/copilot-instructions.md` (complete file)
**Full Extended Docs**: `.github/copilot-instructions-full.md` (if available)
