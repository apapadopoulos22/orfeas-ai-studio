# BOB AI v9.0 - Troubleshooting & FAQ Guide

**Version:** 9.0.0
**Date:** October 27, 2025
**Purpose:** Quick reference for common issues and frequently asked questions

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Runtime Issues](#runtime-issues)
3. [Performance Issues](#performance-issues)
4. [Query Issues](#query-issues)
5. [Integration Issues](#integration-issues)
6. [Testing Issues](#testing-issues)
7. [Deployment Issues](#deployment-issues)
8. [Frequently Asked Questions](#frequently-asked-questions)

---

## Installation Issues

### Issue: Python Version Incompatible

**Symptom:** `TypeError: unsupported operand type(s)` or version-related errors

**Cause:** Running Python <3.10

**Solution:**

```bash
# Check Python version
python --version

# Upgrade Python if needed
# Visit https://www.python.org/downloads/

# Use specific version
python3.10 -m pip install -r requirements.txt

# Or use pyenv for version management
pyenv install 3.10.0
pyenv local 3.10.0
```

---

### Issue: Pip Install Fails

**Symptom:** `ERROR: Could not find a version that satisfies the requirement`

**Cause:** Network issues or package not found

**Solution:**

```bash
# Upgrade pip first
pip install --upgrade pip

# Use specific index (if behind corporate firewall)
pip install -r requirements.txt -i https://pypi.org/simple/

# Check for offline packages
pip list

# Install one at a time to identify culprit
pip install pytest
pip install flask
# ... continue for each requirement

# Use verbose mode for debugging
pip install -vvv -r requirements.txt
```

---

### Issue: Module Not Found Error

**Symptom:** `ModuleNotFoundError: No module named 'bob_ai_integration_hub'`

**Cause:** Backend directory not in Python path

**Solution:**

```bash
# Add backend to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"  # macOS/Linux
set PYTHONPATH=%PYTHONPATH%;%cd%\backend          # Windows

# Or add to code
import sys
sys.path.insert(0, './backend')

# Verify paths
python -c "import sys; print('\n'.join(sys.path))"

# Check file exists
ls backend/bob_ai_integration_hub.py
```

---

### Issue: Virtual Environment Issues

**Symptom:** Commands run from wrong Python or packages not installed

**Cause:** Virtual environment not activated

**Solution:**

```bash
# Create fresh virtual environment
rm -rf venv
python -m venv venv

# Activate
source venv/bin/activate           # macOS/Linux
venv\Scripts\activate              # Windows

# Verify activated
which python                        # macOS/Linux
where python                        # Windows

# Should show path in venv directory
```

---

## Runtime Issues

### Issue: ImportError on Startup

**Symptom:** `ImportError: cannot import name 'X' from 'module'`

**Cause:** Circular imports or missing dependencies

**Solution:**

```python
# Check import order in main.py
# Verify no circular dependencies

# Test import in isolation
python -c "from bob_ai_knowledge_graph import get_knowledge_graph"
python -c "from bob_ai_multi_agent_reasoner import get_multi_agent_reasoner"
python -c "from bob_ai_discipline_mapper import get_discipline_mapper"
python -c "from bob_ai_integration_hub import get_integration_hub"

# Check for missing __init__.py files
ls backend/__init__.py

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

---

### Issue: Singleton Not Initializing

**Symptom:** `RuntimeError: Singleton not initialized` or `None` returned

**Cause:** Lazy initialization or import order issue

**Solution:**

```python
# Ensure correct import
from bob_ai_knowledge_graph import get_knowledge_graph

# First call initializes singleton
kg = get_knowledge_graph()
assert kg is not None, "KG singleton failed to initialize"

# Verify all singletons
from bob_ai_integration_hub import get_integration_hub
hub = get_integration_hub()

# Check initialization status
print(f"KG ready: {kg is not None}")
print(f"Hub ready: {hub is not None}")

# Force re-initialization if needed
import importlib
import bob_ai_knowledge_graph
importlib.reload(bob_ai_knowledge_graph)
```

---

### Issue: Memory Leak

**Symptom:** Process memory grows continuously

**Cause:** Unreleased objects or unclosed connections

**Solution:**

```python
import gc
import psutil
import os

# Check current memory
process = psutil.Process(os.getpid())
mem_before = process.memory_info().rss / 1024 / 1024

# Run operation
result = hub.query_knowledge("test query")

# Force garbage collection
gc.collect()

# Check memory after
mem_after = process.memory_info().rss / 1024 / 1024
print(f"Memory before: {mem_before:.1f}MB")
print(f"Memory after: {mem_after:.1f}MB")
print(f"Increase: {mem_after - mem_before:.1f}MB")

# If still high, check for cache growth
status = hub.get_hub_status()
print(f"Cache size: {status.get('cache_size', 'unknown')}")

# Disable caching if problematic
os.environ['BOB_AI_ENABLE_CACHE'] = 'false'
```

---

## Performance Issues

### Issue: Query Too Slow (>1s)

**Symptom:** Query responses taking >1 second

**Cause:** Graph is large, no caching, or too broad search

**Solution:**

```python
import time

# Measure query time
start = time.time()
result = hub.query_knowledge("complex query")
elapsed = time.time() - start
print(f"Query took {elapsed*1000:.0f}ms")

# Enable caching
import os
os.environ['BOB_AI_ENABLE_CACHE'] = 'true'
os.environ['BOB_AI_CACHE_SIZE'] = '5000'

# Narrow search scope
result = hub.query_knowledge(
    query="music",
    disciplines=['Music Composition', 'Music Theory'],  # Specific
    limit=5
)

# Use lazy loading for modules
os.environ['BOB_AI_LAZY_LOAD_MODULES'] = 'true'

# Profile the query
import cProfile
cProfile.run('hub.query_knowledge("test")')
```

---

### Issue: Reasoning Takes Too Long (>2s)

**Symptom:** Multi-agent reasoning very slow

**Cause:** Too many agents, complex problem, or inefficient evidence collection

**Solution:**

```python
# Use single agent for quick analysis
from bob_ai_multi_agent_reasoner import get_multi_agent_reasoner
reasoner = get_multi_agent_reasoner()

# Get single perspective (fast)
perspective = reasoner.get_agent_perspective(
    agent_type='engineer',  # Just one
    problem_statement="problem"
)

# Or limit disciplines
analysis = hub.reason_about_problem(
    "problem",
    disciplines=['Music', 'Technology']  # Specific set
)

# Profile reasoning
import cProfile
cProfile.run('hub.reason_about_problem("problem")')
```

---

### Issue: Graph Pathfinding Slow

**Symptom:** find_learning_path() takes >500ms

**Cause:** Large graph, deep search, or inefficient algorithm

**Solution:**

```python
# Limit depth
kg = get_knowledge_graph()
path = kg.find_learning_path("A", "B", max_depth=2)  # Shallow search

# Use BFS for faster results
# (Already implemented, but verify)

# Check graph statistics
stats = kg.get_graph_statistics()
print(f"Graph size: {stats['num_nodes']} nodes, {stats['num_edges']} edges")

# Consider caching paths
@functools.lru_cache(maxsize=100)
def get_cached_path(start, end):
    return kg.find_learning_path(start, end)
```

---

## Query Issues

### Issue: Query Returns Empty Results

**Symptom:** `query_knowledge()` returns no results

**Cause:** Query too specific, discipline not loaded, or keywords not matching

**Solution:**

```python
# Use broader query
result = hub.query_knowledge("music")  # Instead of "baroque counterpoint"

# Check what's loaded
from bob_ai_discipline_mapper import get_discipline_mapper
mapper = get_discipline_mapper()
stats = mapper.get_mapper_statistics()
print(f"Loaded modules: {stats['total_modules']}")
print(f"Total items: {stats['total_items']}")

# Try alternative keywords
result = hub.query_knowledge("composition techniques")

# Search instead of query
results = hub.search_knowledge("music")
print(f"Search results: {len(results)}")

# Enable debug to see routing
import logging
logging.basicConfig(level=logging.DEBUG)
result = hub.query_knowledge("test")
```

---

### Issue: Results Not Relevant

**Symptom:** Query results have low confidence or seem unrelated

**Cause:** Poor keyword matching or context not understood

**Solution:**

```python
# Add context for disambiguation
result = hub.query_knowledge(
    query="performance",
    context="music performance, not computer system performance",
    limit=5
)

# Use specific disciplines
result = hub.query_knowledge(
    query="technique",
    disciplines=['Music Performance', 'Music Composition'],
    limit=5
)

# Check confidence scores
for discipline, confidence in result.relevant_disciplines:
    if confidence < 0.7:  # Low confidence
        print(f"Warning: {discipline} confidence low ({confidence:.0%})")

# Use search instead of query
results = hub.search_knowledge("music performance technique")
```

---

### Issue: Path Not Found

**Symptom:** `find_learning_path()` returns None

**Cause:** No connection exists between disciplines

**Solution:**

```python
# Check if both disciplines exist
kg = get_knowledge_graph()
try:
    info_a = kg.get_discipline_info("Discipline A")
    info_b = kg.get_discipline_info("Discipline B")
except ValueError as e:
    print(f"Discipline not found: {e}")

# Increase search depth
path = kg.find_learning_path("A", "B", max_depth=4)  # Deeper search

# Find what IS related
related_a = kg.find_related_disciplines("A")
related_b = kg.find_related_disciplines("B")

# Look for intersection
common = set(related_a) & set(related_b)
if common:
    print(f"Common ancestors: {common}")

# Try reverse direction
path = kg.find_learning_path("B", "A")  # May work in one direction
```

---

## Integration Issues

### Issue: Hub Component Not Initialized

**Symptom:** AttributeError when calling hub methods

**Cause:** Component didn't initialize properly

**Solution:**

```python
# Check hub status
hub = get_integration_hub()
status = hub.get_hub_status()

print(f"Operational: {status['operational']}")
print(f"Components:")
for component, comp_status in status['components'].items():
    print(f"  {component}: {comp_status['status']}")

# Reinitialize if needed
import importlib
import bob_ai_integration_hub
importlib.reload(bob_ai_integration_hub)

# Verify each component separately
from bob_ai_knowledge_graph import get_knowledge_graph
from bob_ai_multi_agent_reasoner import get_multi_agent_reasoner
from bob_ai_discipline_mapper import get_discipline_mapper

kg = get_knowledge_graph()
assert kg is not None
print("✓ KG ready")

reasoner = get_multi_agent_reasoner()
assert reasoner is not None
print("✓ Reasoner ready")

mapper = get_discipline_mapper()
assert mapper is not None
print("✓ Mapper ready")
```

---

### Issue: Data Inconsistency

**Symptom:** Same query returns different results

**Cause:** Cache issues or concurrent modifications

**Solution:**

```python
# Disable cache to verify data
import os
os.environ['BOB_AI_ENABLE_CACHE'] = 'false'

# Run query again
result = hub.query_knowledge("test")

# If results now consistent, cache issue
# If still inconsistent, data issue

# Check for concurrent modifications
import threading
print(f"Thread count: {threading.active_count()}")

# Force single-threaded mode
import os
os.environ['PYTHONUNBUFFERED'] = '1'
```

---

## Testing Issues

### Issue: Tests Fail to Run

**Symptom:** `pytest` command not found or tests don't execute

**Cause:** pytest not installed or not in path

**Solution:**

```bash
# Install pytest
pip install pytest pytest-cov pytest-xdist

# Verify installation
pytest --version

# Run with python module
python -m pytest backend/test_bob_ai_v9.py -v

# Check conftest exists
ls backend/conftest.py

# Run specific test
python -m pytest backend/test_bob_ai_v9.py::TestKnowledgeGraphInitialization::test_kg_initialization -v
```

---

### Issue: Tests Timeout

**Symptom:** Tests hang or timeout after N seconds

**Cause:** Infinite loop, slow operation, or network wait

**Solution:**

```bash
# Run with timeout
pytest backend/test_bob_ai_v9.py --timeout=30 -v

# Run only quick tests
pytest backend/test_bob_ai_v9.py -m "not slow" -v

# Run with verbose output
pytest backend/test_bob_ai_v9.py -vv --tb=short

# Profile slow tests
pytest backend/test_bob_ai_v9.py --durations=10 -v
```

---

### Issue: Intermittent Test Failures

**Symptom:** Tests pass sometimes, fail other times

**Cause:** Race conditions, timing issues, or random data

**Solution:**

```bash
# Run tests multiple times
for i in {1..10}; do pytest backend/test_bob_ai_v9.py -x; done

# Run with different random seeds
pytest backend/test_bob_ai_v9.py --randomly-seed=random -v

# Run without random order
pytest backend/test_bob_ai_v9.py -p no:randomly -v

# Run with thread checking
pytest backend/test_bob_ai_v9.py -v

# Check for global state issues in code
grep -r "global " backend/bob_ai*.py
```

---

## Deployment Issues

### Issue: Docker Build Fails

**Symptom:** `docker build` command fails

**Cause:** Missing requirements, bad Dockerfile, or system issues

**Solution:**

```bash
# Rebuild with no cache
docker build --no-cache -t bob-ai:v9 .

# Build with verbose output
docker build --build-arg BUILDKIT_INLINE_CACHE=1 -t bob-ai:v9 .

# Check Dockerfile syntax
docker run --rm -i hadolint/hadolint < Dockerfile

# Test requirements file
pip install -r requirements.txt

# Build intermediate image
docker build --target intermediate -t bob-ai:intermediate .
```

---

### Issue: Container Crashes on Startup

**Symptom:** `docker run` or `docker-compose up` exits immediately

**Cause:** Import error, missing file, or init failure

**Solution:**

```bash
# Check logs
docker logs bob-ai

# Run with interactive terminal
docker run -it bob-ai:v9 /bin/bash

# Test imports in container
docker run bob-ai:v9 python -c "from bob_ai_integration_hub import get_integration_hub; print('OK')"

# Check health endpoint
docker run -d -p 5000:5000 bob-ai:v9
sleep 2
curl http://localhost:5000/health
docker stop $(docker ps -q)
```

---

### Issue: Port Already in Use

**Symptom:** `Address already in use` error

**Cause:** Another process using port 5000

**Solution:**

```bash
# Find process using port 5000
lsof -i :5000                          # macOS/Linux
netstat -ano | findstr :5000           # Windows

# Kill process
kill -9 <PID>                          # macOS/Linux
taskkill /PID <PID> /F                 # Windows

# Or use different port
docker run -p 8000:5000 bob-ai:v9
docker-compose.yml - change ports to 8000:5000
```

---

## Frequently Asked Questions

### Q1: What Python versions are supported

**A:** Python 3.10, 3.11, and 3.12 are tested and supported.

```bash
# Check version
python --version

# Use pyenv for multiple versions
pyenv versions
pyenv local 3.10.0
```

---

### Q2: How many disciplines can be loaded

**A:** Currently 1,300+ disciplines are configured. Can scale to 10,000+ with optimization.

```python
# Check loaded disciplines
mapper = get_discipline_mapper()
stats = mapper.get_mapper_statistics()
print(f"Disciplines: {stats['total_modules']}")
print(f"Items: {stats['total_items']}")
```

---

### Q3: What's the memory requirement

**A:** Minimum 2GB, recommended 4GB+ for optimal performance.

```python
import psutil
mem = psutil.virtual_memory()
print(f"Available: {mem.available / 1024 / 1024 / 1024:.1f}GB")
```

---

### Q4: How long do queries take

**A:** Typical query: 100-200ms. Complex reasoning: 500-1000ms.

```python
import time
start = time.time()
result = hub.query_knowledge("test")
print(f"Query time: {(time.time()-start)*1000:.0f}ms")
```

---

### Q5: Can I add custom disciplines

**A:** Yes, add modules following the `bob_ai_v9_<tier>_<name>.py` pattern.

```python
# Create new module
# File: backend/bob_ai_v9_custom_discipline.py

class CustomDisciplineKB:
    def __init__(self):
        self.items = [...]

# Register in mapper
# Update TIER_MODULES configuration
```

---

### Q6: How do I export results

**A:** Convert to dict/JSON or use search results:

```python
# Export query result
result = hub.query_knowledge("test")
import json
json_data = json.dumps(result.to_dict(), indent=2)

# Export to file
with open('results.json', 'w') as f:
    json.dump(result.to_dict(), f, indent=2)
```

---

### Q7: Can I use this in production

**A:** Yes, v9.0 is production-ready. See DEPLOYMENT_GUIDE_V9.md for details.

```bash
# Verify production readiness
pytest backend/test_bob_ai_v9.py -v
python backend/health_check.py
curl http://localhost:5000/health
```

---

### Q8: How do I contribute

**A:** Fork, create branch, make changes, run tests, submit PR.

```bash
# Run tests before PR
pytest backend/test_bob_ai_v9.py -v --cov=backend

# Check code style
pylint backend/bob_ai*.py
```

---

### Q9: Where's the documentation

**A:** Complete docs in project root:

- **README_V9.md** - Overview
- **API_REFERENCE_V9.md** - API documentation
- **USAGE_GUIDE_V9.md** - Usage guide
- **ARCHITECTURE_DIAGRAMS_V9.md** - Architecture
- **DEPLOYMENT_GUIDE_V9.md** - Deployment
- **This file** - Troubleshooting

---

### Q10: How do I report bugs

**A:** Create GitHub issue with:

1. Python version
2. Error message and traceback
3. Steps to reproduce
4. Expected vs actual behavior

---

## Debug Mode

### Enable Debug Logging

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now run queries
result = hub.query_knowledge("test")
```

### Profile Code

```bash
# Identify slow functions
python -m cProfile -s cumtime main.py

# Line-by-line profiling
pip install line-profiler
kernprof -l -v main.py
```

### Memory Profiling

```bash
pip install memory-profiler
python -m memory_profiler main.py
```

---

## Support Resources

| Resource | Link |
|----------|------|
| **API Docs** | API_REFERENCE_V9.md |
| **Usage Guide** | USAGE_GUIDE_V9.md |
| **Architecture** | ARCHITECTURE_DIAGRAMS_V9.md |
| **Deployment** | DEPLOYMENT_GUIDE_V9.md |
| **Source Code** | backend/bob_ai_*.py |
| **Tests** | backend/test_bob_ai_v9.py |

---

**Troubleshooting Guide Version:** 9.0.0
**Last Updated:** October 27, 2025
**Status:** ✅ Complete
