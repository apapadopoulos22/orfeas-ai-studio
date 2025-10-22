# ORFEAS AI 2D3D STUDIO - GitHub Copilot Instructions (SLIM CORE)

**Project:** Enterprise AI multimedia for 2D3D generation + video composition + code development
**Stack:** Python 3.10+/Flask/PyTorch + HTML5/PWA + Docker GPU (RTX 3090 CUDA 12.0)
**Quality:** 92% Grade A (ISO 9001/27001, 464 tests, 50K+ LOC)

## 5-MINUTE QUICKSTART

### Backend

```powershell
cd backend
python main.py  # Runs on http://127.0.0.1:5000

```text

### Local LLM (Recommended)

```powershell
.\ps1\START_LOCAL_LLM_AUTO.ps1  # Ollama + Mistral

```text

### Docker Stack

```powershell
docker-compose up -d  # Full 7-service stack with GPU

```text

## CRITICAL PATTERNS (Must Know)

### 1. Model Caching (94% Speed Gain)

```python
class Hunyuan3DProcessor:
    _model_cache = {'pipeline': None, 'initialized': False}
    _cache_lock = threading.Lock()

    def __init__(self):
        with self._cache_lock:
            if self._model_cache['initialized']:
                self.pipeline = self._model_cache['pipeline']
                return
        self.initialize_model()

```text

### 2. GPU Memory (RTX 3090: 24GB total)

```python
try:
    result = processor.generate_shape(image)
finally:
    torch.cuda.empty_cache()

gpu_mgr = get_gpu_manager()
if not gpu_mgr.can_process_job(estimated_vram=6000):
    raise ResourceError('Insufficient GPU memory')

```text

### 3. Async Jobs (for operations >10s)

```python
async_queue = get_async_queue()
job = async_queue.submit_job('3d_generation',
                              image=image, quality=7)
return jsonify({'job_id': job.id, 'status': 'queued'})

```text

### 4. Error Handling

```python
try:
    result = processor.generate(image)
except torch.cuda.OutOfMemoryError as e:
    logger.error(f'GPU OOM: {e}')
    torch.cuda.empty_cache()
finally:
    torch.cuda.empty_cache()

```text

## Key Files

| File | Purpose |
|------|---------|
| backend/main.py | Flask API entry (WebSocket + REST) |
| backend/hunyuan_integration.py | 3D generation (model cache, GPU) |
| backend/gpu_manager.py | GPU resource management |
| backend/batch_processor.py | Async job queue |
| backend/llm_local_integration.py | Local Ollama integration |
| Hunyuan3D-2.1/ | Model submodule |

## Environment Variables

```bash
DEVICE=cuda
XFORMERS_DISABLED=1
GPU_MEMORY_LIMIT=0.8
MAX_CONCURRENT_JOBS=3
LOCAL_LLM_ENABLED=true
LOCAL_LLM_ENDPOINT=http://localhost:11434
LOCAL_LLM_MODEL=mistral
ENABLE_MONITORING=true
LOG_LEVEL=INFO

```text

## Testing & Validation

```powershell
pytest tests/ -m unit
pytest tests/ -m integration
curl http://localhost:5000/health

```text

## Troubleshooting

| Problem | Solution |
|---------|----------|
| xformers DLL error | Set XFORMERS_DISABLED=1 |
| CUDA out of memory | Set GPU_MEMORY_LIMIT=0.7 |
| Model not found | Run download_models.py |
| WebSocket timeout | Check CORS_ORIGINS in .env |
| Ollama unresponsive | Restart ollama container |

## Markdownlint Prevention (Repo Standard)

Keep markdown clean and lint-free by following repo rules:

- Surround headings and lists with blank lines above and below
- Use fenced code blocks with allowed languages: powershell, bash,
  python, json, yaml, text, html, ini
- Keep lines under 80 characters
- Avoid trailing spaces

For exceptions, use pragmas:

```text
<!-- markdownlint-disable MD022 MD032 MD040 -->
<!-- content that needs exceptions -->
<!-- markdownlint-enable -->

```text

Quick checks and auto-fixes:

```powershell
.\fix_markdown_lint.ps1 -Mode check
.\fix_markdown_lint.ps1 -Mode fix

```text

## Extended Documentation

- Advanced Patterns: md/COPILOT_ADVANCED_PATTERNS.md
- Deployment Guide: md/COPILOT_DEPLOYMENT_GUIDE.md
- TQM/Quality: md/COPILOT_TQM_REFERENCE.md
- LLM Integration: md/COPILOT_LLM_PATTERNS.md
- Full Original: .github/copilot-instructions-full.md

## Development Tips

1. **Focus on one component** - Not whole project
2. **Ask specific questions** - Not broad requests
3. **Check logs first** - docker-compose logs -f backend
4. **Test incrementally** - Run pytest -m unit frequently
5. **Use WebSocket monitor** - Watch real-time progress

---

**This is the SLIM CORE version. All ORFEAS work uses these**
**instructions + extended reference docs.**
