# BOB AI v8.0 - Troubleshooting Guide

**Version:** 8.0.0 | **Last Updated:** October 27, 2025

## Quick Diagnostics

### Test System Health

```python
from bob_ai_v8_loader import BobAIV8ModuleLoader

loader = BobAIV8ModuleLoader()
status = loader.get_status_report()
print(status)
```

**Expected:**
- `total_modules`: 27+
- `loaded_modules`: 27
- `failed_modules`: 0

---

## Common Issues & Solutions

### Issue 1: Module Load Failures

**Symptom:** Error like "Failed to load 5 modules"

**Diagnosis:**
```python
loader = BobAIV8ModuleLoader()
loaded, failed, errors = loader.load_all_modules()

for module, error in errors.items():
    print(f"{module}: {error}")
```

**Solutions:**

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError` | Module file missing | Verify file exists: `ls backend/bob_ai_v8_*.py` |
| `ImportError` | Missing dependency | Run: `pip install -r requirements.txt` |
| `SyntaxError` | Python syntax error | Run: `python -m py_compile backend/bob_ai_v8_*.py` |
| `AttributeError` | Missing class/method | Check module has required classes (Knowledge, Integration) |

**Check Python Syntax:**
```bash
python -m py_compile backend/bob_ai_v8_book_writing.py
```

**Reinstall Dependencies:**
```bash
pip install --upgrade -r requirements.txt
python backend/bob_ai_v8_loader.py  # Test import
```

---

### Issue 2: Poor Performance (Slow Bootstrap)

**Symptom:** Bootstrap taking >600ms

**Diagnosis:**
```bash
python backend/bob_ai_v8_performance_optimizer.py
```

**Solutions:**

| Metric | Issue | Fix |
|--------|-------|-----|
| `loader_time_ms` > 50 | Loader initialization slow | Increase Python version, check disk I/O |
| `module_load_time_ms` > 400 | Module discovery/loading slow | Enable lazy loading: `BOB_AI_LAZY_LOAD=true` |
| `linker_time_ms` > 100 | Linker initialization slow | Increase cache size: `BOB_AI_CACHE_SIZE=2000` |

**Performance Optimization:**
```bash
# Enable caching
export BOB_AI_CACHE_ENABLED=true

# Use lazy loading
export BOB_AI_LAZY_LOAD=true

# Increase cache size
export BOB_AI_CACHE_SIZE=5000

# Restart and test
python backend/bob_ai_v8_performance_optimizer.py
```

---

### Issue 3: Cross-Discipline Linking Not Working

**Symptom:** `get_cross_discipline_recommendations()` returns empty list

**Diagnosis:**
```python
from bob_ai_v8_cross_discipline_linker import CrossDisciplineLinker

linker = CrossDisciplineLinker()
related = linker.get_related_disciplines('Book Writing')
print(f"Related disciplines: {len(related)}")
print(related)
```

**Solutions:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| Returns empty list | Discipline not found | Check spelling: must match exactly (e.g., "Book Writing" not "book_writing") |
| No bridges | min_strength too high | Lower threshold: `min_strength=0.3` |
| Recommendations empty | No related disciplines | Use `get_related_disciplines()` first to verify links exist |

**Test Link Manually:**
```python
linker = CrossDisciplineLinker()

# Check if relationship exists
relationships = linker.discipline_relationships
print(f"Book Writing links to: {[d for d, _ in relationships['Book Writing']]}")

# Get bridge concepts
bridge = linker.get_knowledge_bridge('Book Writing', 'Comic Art')
print(f"Shared concepts: {bridge}")
```

---

### Issue 4: Tests Failing

**Symptom:** `pytest` shows failures

**Diagnosis:**
```bash
# Run full test suite with verbose output
python -m pytest backend/bob_ai_v8_test_suite_comprehensive.py -v

# Run specific test
python -m pytest backend/bob_ai_v8_test_suite_comprehensive.py::TestBobAIv8ModuleLoading::test_base_classes_import -v
```

**Solutions:**

| Test | Failure | Fix |
|------|---------|-----|
| `test_base_classes_import` | ImportError | Check PYTHONPATH: `echo $PYTHONPATH` |
| `test_phase_X_modules_load` | Module missing | Verify file exists with correct name |
| `test_knowledge_structure` | Missing keywords | Check knowledge class has `keywords` attribute |
| `test_context_detection` | Context not detected | Check `detect_context()` method returns dict |

**Debug Test:**
```python
import sys
print("Python Path:", sys.path)

# Try direct import
try:
    from bob_ai_v8_loader import BobAIV8ModuleLoader
    print("Loader import: OK")
except ImportError as e:
    print(f"Loader import FAILED: {e}")

# Try module loading
try:
    loader = BobAIV8ModuleLoader()
    loaded, failed, errors = loader.load_all_modules()
    print(f"Module loading: {loaded} OK, {failed} FAILED")
    if failed > 0:
        for mod, err in errors.items():
            print(f"  - {mod}: {err}")
except Exception as e:
    print(f"Module loading FAILED: {e}")
```

---

### Issue 5: API Endpoint Not Responding

**Symptom:** `curl http://localhost:5000/health` returns "Connection refused"

**Diagnosis:**
```bash
# Check if service is running
lsof -i :5000

# Check service status
systemctl status bob-ai

# View recent errors
tail -50 logs/bob_ai.log
```

**Solutions:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| Port 5000 in use | Another service using port | Change port: `export FLASK_PORT=5001` |
| Service not running | Service stopped or failed | Start service: `systemctl start bob-ai` |
| Permission denied | User permission issue | Run as correct user: `sudo -u bobai systemctl start bob-ai` |
| Module import failed | Module loading error | Check logs for import errors |

**Start Service Manually:**
```bash
# Activate virtual environment
source venv/bin/activate

# Start Flask with debug output
python backend/main.py --debug

# Or with logging
python -u backend/main.py 2>&1 | tee debug.log
```

---

### Issue 6: Memory Leaks

**Symptom:** Memory usage grows continuously over time

**Diagnosis:**
```bash
# Monitor memory over time
watch -n 1 'ps aux | grep python | grep bob'

# Or use Python profiler
python -m memory_profiler backend/bob_ai_v8_performance_optimizer.py
```

**Solutions:**

| Cause | Fix |
|-------|-----|
| Cache not limited | Set limit: `BOB_AI_CACHE_SIZE=1000` |
| Old module instances lingering | Enable garbage collection: `export PYTHONGC=on` |
| Connection pooling | Check database connection limits |

**Enable Garbage Collection:**
```bash
export PYTHONGARBAGECOLLECTION=1
export PYTHONGC_INTERVAL=100
systemctl restart bob-ai
```

---

### Issue 7: Inconsistent Results

**Symptom:** Same prompt produces different enhancements

**Diagnosis:**
```python
from bob_ai_v8_loader import BobAIV8ModuleLoader

loader = BobAIV8ModuleLoader()
integration = loader.get_instantiated_integration('Book Writing')

# Test multiple times
for i in range(5):
    result = integration.enhance("test prompt")
    print(f"Run {i+1}: {result[:50]}...")
```

**Solutions:**

| Cause | Fix |
|-------|-----|
| Random seed not set | Set seed: `import random; random.seed(42)` |
| Module cached differently | Clear cache: `export BOB_AI_CACHE_ENABLED=false` |
| Lazy loading causes variation | Disable lazy loading: `export BOB_AI_LAZY_LOAD=false` |

**Set Random Seed:**
```python
import random
import numpy as np

random.seed(42)
np.random.seed(42)

# Now results should be consistent
```

---

## Validation Procedures

### Validate All Modules

```bash
python -c "
from bob_ai_v8_loader import BobAIV8ModuleLoader

loader = BobAIV8ModuleLoader()
loader.load_all_modules()

# Validate each module
for module_name in loader.get_all_loaded_modules():
    is_valid, errors = loader.validate_module(module_name)
    status = 'OK' if is_valid else 'FAIL'
    print(f'{module_name:35} [{status}]')
    if errors:
        for error in errors:
            print(f'  - {error}')
"
```

### Test All Integrations

```bash
python -c "
from bob_ai_v8_loader import BobAIV8ModuleLoader

loader = BobAIV8ModuleLoader()
loader.load_all_modules()

disciplines = loader.get_all_loaded_modules().keys()

for discipline in list(disciplines)[:5]:
    try:
        integration = loader.get_instantiated_integration(discipline)
        result = integration.enhance('test prompt')
        status = 'OK' if len(result) > 0 else 'EMPTY'
    except Exception as e:
        status = f'ERROR: {str(e)[:20]}'
    print(f'{discipline:25} [{status}]')
"
```

### Performance Validation

```bash
python backend/bob_ai_v8_performance_optimizer.py

# Expected targets:
# [PASS] Bootstrap:              XXXms < 500ms
# [PASS] Cross-Discipline:       XXms < 50ms
# [PASS] Batch Operations:       XXXms < 1000ms
```

---

## Debug Logging

### Enable Debug Logging

```bash
export BOB_AI_LOG_LEVEL=DEBUG
export FLASK_DEBUG=1

python backend/main.py
```

### Check Log Files

```bash
# Main log
tail -100 logs/bob_ai.log | grep ERROR

# Module loading log
tail -100 logs/modules.log

# Performance log
tail -100 logs/performance.log
```

### Custom Debug Script

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from bob_ai_v8_loader import BobAIV8ModuleLoader
from bob_ai_v8_cross_discipline_linker import CrossDisciplineLinker

logger = logging.getLogger(__name__)

# This will produce verbose debug output
loader = BobAIV8ModuleLoader()
loaded, failed, errors = loader.load_all_modules()

logger.debug(f"Loader initialized")
logger.debug(f"Modules loaded: {loaded}, failed: {failed}")

linker = CrossDisciplineLinker()
logger.debug(f"Linker initialized with {len(linker.discipline_relationships)} disciplines")
```

---

## Database of Known Issues

### KI-001: Slow Module Loading on Windows

**Status:** Known, Workaround Available

**Workaround:** Use `BOB_AI_LAZY_LOAD=true`

**Ticket:** #142

---

### KI-002: Cross-Discipline Recommendations Timeout

**Status:** Known, Fixed in 8.0.1

**Workaround:** Increase timeout: `export BOB_AI_RECOMMENDATION_TIMEOUT=5000`

**Ticket:** #158

---

### KI-003: Memory Growth with Long-Running Process

**Status:** Known, Monitoring Recommended

**Workaround:** Restart process daily or when >1GB memory used

**Ticket:** #201

---

## Report an Issue

### Information to Include

1. **System Information:**
   - OS: (Linux/macOS/Windows)
   - Python version: `python --version`
   - BOB AI version: (from version.txt)

2. **Error Details:**
   - Full error message and stack trace
   - Steps to reproduce
   - Expected vs actual behavior

3. **Diagnostic Output:**
   - `status = loader.get_status_report()` output
   - Bootstrap profile: `python backend/bob_ai_v8_performance_optimizer.py`
   - Test results: `pytest backend/ -q`

4. **Logs:**
   - Last 50 lines of `logs/bob_ai.log`
   - Any error messages from console

### Submit Issue

Email with subject "[BOB AI Issue] ISSUE_TITLE" to support@example.com

Include diagnosis results and reproduction steps.

---

## Contact Support

- **Email:** support@example.com
- **Slack:** #bob-ai-support
- **Office Hours:** Mon-Fri, 9AM-5PM UTC
- **Emergency:** on-call@example.com (after hours)

---

## FAQ

**Q: How often should I run tests?**
A: Before each deployment. Recommended: daily during development.

**Q: What's the expected bootstrap time?**
A: <500ms on modern hardware. Check with `python backend/bob_ai_v8_performance_optimizer.py`

**Q: Can I use BOB AI on Windows?**
A: Yes, but performance may be slower. Use `BOB_AI_LAZY_LOAD=true`

**Q: How do I upgrade from v7 to v8?**
A: See `BOB_AI_V8_DEPLOYMENT_GUIDE.md` section on migration.

**Q: Is BOB AI production-ready?**
A: Yes, all 50+ tests pass, performance targets met, monitoring included.
