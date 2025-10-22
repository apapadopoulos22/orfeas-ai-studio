# ORFEAS AI Multimedia and Video Patterns

This guide documents how multimedia generation is implemented in code today, with pointers to real modules for text‑to‑image, 3D processing, and GPU management. Video composition notes are included for planning and alignment.

## Components in this repository

- Text‑to‑Image engine: `backend/ultimate_text_to_image.py`

  - Class: `UltimateTextToImageEngine`
  - Features: provider routing (HuggingFace, Pollinations, Stability, AUTOMATIC1111), prompt enhancement, quality modes (best/balanced/fast), retry/timeouts, image quality validation, fallback image generation, provider stats, singleton accessor `get_ultimate_engine()`

- GPU manager: `backend/gpu_manager.py`

  - Classes: `GPUMemoryManager`, `GPUManager`
  - Features: memory stats, `can_process_job()`, `allocate_job()/release_job()`, `managed_generation()` context, `cleanup_after_job()`, utilization reporting, singleton `get_gpu_manager()`

- STL processing: `backend/stl_processor.py`

  - Class: `AdvancedSTLProcessor`
  - Features: analyze → auto‑repair → simplify → optimize‑for‑printing, end‑to‑end `process_stl_complete()`

- Hunyuan 3D integration: `backend/hunyuan_integration.py`

  - Classes: `Hunyuan3DProcessor`, `FallbackProcessor`
  - Features: safe wrapper for heavy deps, image→3D and text→image paths, background removal hooks, cube/OBJ fallback, factory `get_3d_processor()`

## Text‑to‑Image patterns

1. Prompt enhancement and provider selection

- `enhance_prompt()` adds style/quality hints.
- `generate_ultimate(prompt, mode)` routes to provider methods based on mode and availability.

1. Robust networking and quality gates

- `NetworkConfig` centralizes session retries and timeouts for HTTP providers.
- `validate_image_quality()` ensures min resolution/format before returning results; otherwise `_generate_fallback_image()` is used.

1. Fallback and metrics

- If a provider fails or returns low quality, the engine falls back to alternative providers in a defined order.
- `get_provider_stats()` exposes success/latency counts for monitoring.

Contract

- Input: prompt string (+ optional style/quality mode)
- Output: image bytes/path + provider metadata and quality flags

## GPU management patterns

1. Admission control

- Use `gpu_manager.can_process_job(estimated_vram)` before allocating.
- If false, queue or reject with a clear error.

1. Managed execution and cleanup

- Wrap heavy ops in `gpu_manager.managed_generation(job_id)` (contextmanager) or `allocate_job()/release_job()`.
- Always trigger `cleanup_after_job()`; internally calls CUDA cache cleanup when available.

1. Telemetry

- `get_gpu_stats()` and `get_utilization()` inform autoscaling/queuing policies.

## STL processing patterns

1. Quality‑first pipeline

- `analyze_mesh()` for triangle count, manifold check, bounds, area/volume.
- `auto_repair()` then `simplify_mesh()` to reduce complexity while preserving quality.
- `optimize_for_printing()` for size, wall thickness, and optional supports.

Contract

- Input: mesh file path or mesh object
- Output: quality report + repaired/simplified/optimized mesh ready for export

## Hunyuan 3D integration patterns

1. Safe initialization and fallbacks

- `get_3d_processor()` selects a safe `Hunyuan3DProcessor` wrapper; falls back to `FallbackProcessor` (e.g., cube/OBJ) if heavy deps aren’t present.
- Keep GPU memory in check; pair with GPU manager contexts.

1. Image→3D and Text→Image

- `image_to_3d_generation()` supports background removal and hands off to the core pipeline.
- `text_to_image_generation()` integrates with the T2I engine when needed.

## Video composition (planning alignment)

- The Sora‑inspired video composition is planned (see Copilot instructions) with camera motion, lighting dynamics, temporal consistency, and style transfer.
- When added, it should follow the same patterns:

  - Admission control with `GPUManager`
  - Incremental generation with progress events
  - Quality gates and fallbacks for frames/sequences
  - Provider metrics for monitoring and regression detection

## Error modes and safeguards

- Provider/network failures → retries with exponential backoff; fallback providers.
- Low quality images/meshes → validation fails early; return structured error and hints.
- GPU OOM → release context, clear CUDA cache, reduce concurrency or quality, retry once if policy allows.

## Security and compliance notes

- Validate incoming files (type/size/content) before processing; use existing upload validation utilities.
- Enforce timeouts on external calls; sanitize user‑provided prompts/paths.
- Log provider selections and failures without exposing secrets or user content.

## Related files and references

- `backend/ultimate_text_to_image.py` (multi‑provider T2I)
- `backend/gpu_manager.py` (GPU memory and job management)
- `backend/stl_processor.py` (mesh quality, repair, and printing optimization)
- `backend/hunyuan_integration.py` (3D pipeline wrapper and fallbacks)
- `.github/copilot-instructions.md` (performance/GPU patterns, caching, safety)
