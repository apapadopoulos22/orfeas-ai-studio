# BOB AI v8.0 - Local Deployment Guide

**Quick local deployment for testing and development**

---

## Prerequisites

- Python 3.10+ (check: `python --version`)
- pip package manager
- Virtual environment (venv)

---

## Quick Start (5 minutes)

### Step 1: Create Virtual Environment

```powershell
cd c:\Users\johng\Documents\oscar
python -m venv local_env
.\local_env\Scripts\Activate.ps1
```

### Step 2: Install BOB AI Dependencies

```powershell
cd backend
pip install --quiet flask flask-cors python-socketio python-socketio[client] pytest
```

### Step 3: Verify Installation

```powershell
python -m pytest bob_ai_v8_test_suite_comprehensive.py::TestComprehensiveIntegration::test_phase3_modules_loadable -v
```

Expected output: `PASSED` ✅

### Step 4: Start Local Server

```powershell
# Option A: Simple HTTP server (for testing)
python -m http.server 8000

# Option B: Flask development server (recommended)
python -c "
from bob_ai_v8_loader import BobAIV8ModuleLoader
loader = BobAIV8ModuleLoader()
modules = loader.load_all_modules()
print('✅ BOB AI v8.0 - Local Deployment Ready')
print(f'Loaded {len(modules)} modules')
print('14 disciplines ready for testing')
"
```

---

## Testing BOB AI v8.0 Locally

### Test 1: Module Loading

```powershell
python -c "
from bob_ai_v8_loader import BobAIV8ModuleLoader
loader = BobAIV8ModuleLoader()
modules = loader.load_all_modules()
print('✅ Modules loaded:', list(modules.keys())[:3], '...')
print(f'Total: {len(modules)} modules')
"
```

### Test 2: Cross-Discipline Linking

```powershell
python -c "
from bob_ai_v8_cross_discipline_linker import CrossDisciplineLinker
linker = CrossDisciplineLinker()
recommendations = linker.get_cross_discipline_recommendations('book_writing', 'writing improvement')
print('✅ Cross-discipline recommendations:')
for disc, score in recommendations[:5]:
    print(f'  - {disc}: {score:.1%}')
"
```

### Test 3: Performance Profiling

```powershell
python -c "
from bob_ai_v8_performance_optimizer import PerformanceProfiler
profiler = PerformanceProfiler()
profile = profiler.profile_bootstrap()
print('✅ Bootstrap Performance:')
print(f'  Time: {profile[\"bootstrap_ms\"]:.0f}ms')
print(f'  Target: 500ms')
print(f'  Status: {'PASS ✅' if profile['bootstrap_ms'] < 500 else 'FAIL ❌'}')
"
```

### Test 4: Run Full Test Suite

```powershell
# Run all 50 comprehensive tests
python -m pytest bob_ai_v8_test_suite_comprehensive.py -v --tb=short

# Run integration tests
python -m pytest bob_ai_v8_cross_discipline_tests.py -v --tb=short
```

---

## API Testing

### Using Python (Recommended)

```python
# test_local_deployment.py
from bob_ai_v8_loader import BobAIV8ModuleLoader
from bob_ai_v8_cross_discipline_linker import CrossDisciplineLinker

# Load system
loader = BobAIV8ModuleLoader()
modules = loader.load_all_modules()

# Test discipline
photography = modules.get('photography')
if photography:
    enhancement = photography.enhance(
        user_input="Improve my photography composition",
        context={"style": "portrait"}
    )
    print("✅ Enhancement result:")
    print(enhancement[:200] + "...")

# Test cross-discipline
linker = CrossDisciplineLinker()
related = linker.get_related_disciplines('photography')
print(f"\n✅ Related disciplines: {[d[0] for d in related]}")

# Test learning path
learning = linker.suggest_adjacent_learning('photography')
print(f"\n✅ Learning path: {learning[:3]}")
```

Run it:

```powershell
python test_local_deployment.py
```

### Using cURL

```bash
# Health check
curl http://localhost:5000/health

# Get module info
curl http://localhost:5000/api/module/photography

# Test enhancement
curl -X POST http://localhost:5000/api/enhance \
  -H "Content-Type: application/json" \
  -d '{
    "module": "book_writing",
    "input": "Help me write an opening scene",
    "context": {"genre": "fantasy"}
  }'
```

---

## Troubleshooting

### Issue: Module not found

```powershell
# Solution: Add backend to Python path
$env:PYTHONPATH = "c:\Users\johng\Documents\oscar\backend"
python script.py
```

### Issue: Permission denied

```powershell
# Solution: Run PowerShell as Administrator
```

### Issue: Virtual environment not activating

```powershell
# Solution: Run with absolute path
& "C:\Users\johng\Documents\oscar\local_env\Scripts\Activate.ps1"
```

### Issue: Tests failing

```powershell
# Check Python version
python --version  # Should be 3.10+

# Check requirements
pip list | grep -E "flask|pytest"

# Reinstall
pip install --upgrade --quiet flask flask-cors pytest
```

---

## Development Workflow

### Recommended Local Setup

```
project/
├── backend/
│   ├── bob_ai_v8_*.py          (Modules - don't edit)
│   ├── local_env/              (Virtual environment)
│   └── test_local_deployment.py (Your test file)
├── LOCAL_DEPLOYMENT.md
└── local_debug.log
```

### Edit Safe Pattern

```python
# ✅ DO: Copy module and enhance locally
from bob_ai_v8_book_writing import BookWritingModule

class LocalBookWriting(BookWritingModule):
    def custom_enhance(self, user_input, context):
        # Your custom logic here
        return self.enhance(user_input, context) + "\n[LOCAL ENHANCEMENT]"

# Test it
writer = LocalBookWriting()
result = writer.custom_enhance("Hello", {})
print(result)
```

```python
# ❌ DON'T: Edit original modules directly
# (They'll be overwritten on updates)
```

---

## Performance Baseline (Local)

Expected performance on development machine:

| Operation | Time | Notes |
|-----------|------|-------|
| Import modules | ~50ms | First load only |
| Load all 14 disciplines | ~300ms | Subsequent loads ~50ms |
| Cross-discipline link | ~30-40ms | Per recommendation |
| Batch (10 operations) | ~400ms | Parallel possible |
| Single enhancement | ~60ms | In-memory operation |

**If slower, check:**

- CPU usage (Task Manager)
- Disk activity (may indicate I/O)
- Python version (should be 3.10+)
- Other programs using system resources

---

## Next Steps

1. ✅ Local testing complete
2. Deploy to staging environment
3. Run 24-hour stability test
4. Execute load testing
5. Production launch

---

## Support

- **Documentation:** See `BOB_AI_V8_API_REFERENCE.md`
- **Issues:** Check `BOB_AI_V8_TROUBLESHOOTING.md`
- **Performance:** Check `BOB_AI_V8_DEPLOYMENT_GUIDE.md`

---

**Version:** 8.0.0
**Status:** Production-ready for local testing
**Last Updated:** October 27, 2025
