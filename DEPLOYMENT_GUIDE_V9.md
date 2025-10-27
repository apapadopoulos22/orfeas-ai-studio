# BOB AI v9.0 - Deployment & Configuration Guide

**Version:** 9.0.0
**Date:** October 27, 2025
**Audience:** DevOps, System Administrators, Deployment Engineers

---

## Quick Start Deployment (10 minutes)

### Prerequisites

```bash
# System Requirements
# - Python 3.10 or later
# - 2GB RAM minimum (4GB+ recommended)
# - 500MB disk space
# - Windows, macOS, or Linux

# Verify Python
python --version  # Should be 3.10+
```

### Step 1: Install Dependencies

```bash
# Navigate to project
cd c:\Users\johng\Documents\oscar

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install test dependencies (optional)
pip install -r backend/test_requirements.txt
```

### Step 2: Verify Installation

```bash
# Quick test
python -c "from bob_ai_integration_hub import get_integration_hub; hub = get_integration_hub(); print('✓ BOB AI v9.0 Ready')"

# Run health check
python backend/health_check.py

# Expected output:
# ✓ Knowledge Graph: READY
# ✓ Multi-Agent Reasoner: READY
# ✓ Discipline Mapper: READY
# ✓ Integration Hub: READY
# Overall Status: OPERATIONAL
```

### Step 3: Run First Query

```python
# quick_test.py
from bob_ai_integration_hub import get_integration_hub

hub = get_integration_hub()
result = hub.query_knowledge("music composition basics")

print(f"✓ Query successful")
print(f"  Found: {len(result.relevant_disciplines)} disciplines")
print(f"  Top result: {result.relevant_disciplines[0][0]}")
```

```bash
python quick_test.py
# Output:
# ✓ Query successful
#   Found: 5 disciplines
#   Top result: Music Composition
```

---

## Local Development Deployment

### Environment Setup

```bash
# Create .env file for local development
cat > .env << EOF
# Environment
ENV=development
DEBUG=true
LOG_LEVEL=INFO

# BOB AI Settings
ENABLE_CACHE=true
CACHE_SIZE=1000
ENABLE_METRICS=true

# Module Loading
AUTO_LOAD_MODULES=true
MODULE_PATH=./backend

# Performance
MAX_QUERY_TIME=1000  # milliseconds
MAX_REASONING_TIME=2000  # milliseconds
EOF
```

### Running in Development Mode

```python
# main.py - Development entry point
import os
from dotenv import load_dotenv

load_dotenv()

if os.getenv('ENV') == 'development':
    # Enable debug logging
    import logging
    logging.basicConfig(level=logging.DEBUG)

    # Load with debugging
    from bob_ai_integration_hub import get_integration_hub
    hub = get_integration_hub()

    # Start interactive session
    print("BOB AI v9.0 - Development Mode")
    print("Commands: query, reason, search, exit")

    while True:
        cmd = input("\n> ").strip()
        if cmd == "exit":
            break
        elif cmd.startswith("query "):
            result = hub.query_knowledge(cmd[6:])
            print(f"Found: {len(result.relevant_disciplines)} results")
        elif cmd.startswith("reason "):
            result = hub.reason_about_problem(cmd[7:])
            print(f"Confidence: {result['confidence']}%")
        # ... more commands
```

### Running Tests Locally

```bash
# Run all tests
pytest backend/test_bob_ai_v9.py -v

# Run specific category
pytest backend/test_bob_ai_v9.py -m unit -v

# Run with coverage
pytest backend/test_bob_ai_v9.py --cov=backend --cov-report=html -v

# Run performance tests
pytest backend/test_bob_ai_v9.py -m performance -v

# Run with parallel execution
pytest backend/test_bob_ai_v9.py -n auto -v
```

---

## Configuration Reference

### Environment Variables

```bash
# BOB AI Core Configuration
BOB_AI_DEBUG=false              # Enable debug logging
BOB_AI_LOG_LEVEL=INFO           # Log level (DEBUG, INFO, WARNING, ERROR)
BOB_AI_ENABLE_CACHE=true        # Enable result caching
BOB_AI_CACHE_SIZE=1000          # Cache size (items)
BOB_AI_CACHE_TTL=3600           # Cache TTL (seconds)

# Performance Configuration
BOB_AI_MAX_QUERY_TIME=1000      # Max query time (ms)
BOB_AI_MAX_REASONING_TIME=2000  # Max reasoning time (ms)
BOB_AI_MAX_GRAPH_DEPTH=3        # Max graph search depth
BOB_AI_MAX_RESULTS=20           # Max results per query

# Module Configuration
BOB_AI_MODULE_PATH=./backend    # Module directory
BOB_AI_AUTO_LOAD_MODULES=true   # Auto-load on startup
BOB_AI_LAZY_LOAD_MODULES=false  # Load modules on demand
BOB_AI_PRELOAD_TIER_1=true      # Preload Tier 1 modules

# Monitoring & Metrics
BOB_AI_ENABLE_METRICS=true      # Enable metrics collection
BOB_AI_METRICS_INTERVAL=60      # Metrics interval (seconds)
BOB_AI_ENABLE_PROFILING=false   # Enable performance profiling
BOB_AI_MEMORY_LIMIT=2048        # Memory limit (MB)

# Integration & APIs
BOB_AI_ENABLE_EXTERNAL_APIS=false  # Enable external APIs
BOB_AI_API_TIMEOUT=5000         # API timeout (ms)
BOB_AI_RETRY_ATTEMPTS=3         # Retry attempts for failures

# Security
BOB_AI_ENABLE_AUTH=false        # Enable authentication
BOB_AI_API_KEY=""               # API key (if auth enabled)
BOB_AI_RATE_LIMIT=100           # Requests per minute
```

### Configuration File (`config.yaml`)

```yaml
# BOB AI v9.0 Configuration File

environment:
  mode: production  # development, staging, production
  debug: false
  log_level: INFO

performance:
  cache:
    enabled: true
    size: 1000
    ttl_seconds: 3600

  timeouts:
    query_ms: 1000
    reasoning_ms: 2000
    api_ms: 5000

  limits:
    max_results: 20
    max_depth: 3
    max_memory_mb: 2048

modules:
  path: ./backend
  auto_load: true
  lazy_load: false
  preload:
    - tier_1
    - tier_2

  discipline_modules:
    - bob_ai_v9_music_composition
    - bob_ai_v9_music_history
    - bob_ai_v9_music_performance
    # ... more modules

knowledge_graph:
  optimization: true
  cache_relationships: true
  rebuild_interval_hours: 24

reasoner:
  agents: 5
  enable_all: true
  default_agents:
    - pessimist
    - optimist
    - engineer
    - researcher
    - devil_advocate

monitoring:
  enabled: true
  metrics_interval_seconds: 60
  profiling: false
  health_check_interval_seconds: 30

security:
  authentication: false
  api_keys: []
  rate_limiting:
    enabled: false
    requests_per_minute: 100
```

### Loading Configuration

```python
# Load configuration
import yaml
from pathlib import Path

def load_config(env='production'):
    """Load configuration from YAML file"""
    config_path = Path('config.yaml')

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Apply environment overrides
    import os
    for key, value in os.environ.items():
        if key.startswith('BOB_AI_'):
            # Convert BOB_AI_DEBUG=true to config.environment.debug
            parts = key[7:].lower().split('_')
            # ... apply override

    return config

# Usage
config = load_config('production')
print(f"Mode: {config['environment']['mode']}")
print(f"Cache enabled: {config['performance']['cache']['enabled']}")
```

---

## Docker Deployment

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "from bob_ai_integration_hub import get_integration_hub; get_integration_hub()" || exit 1

# Run application
CMD ["python", "app.py"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  bob-ai:
    build: .
    container_name: bob-ai-v9
    ports:
      - "5000:5000"
    environment:
      - BOB_AI_ENV=production
      - BOB_AI_LOG_LEVEL=INFO
      - BOB_AI_ENABLE_CACHE=true
      - BOB_AI_MODULE_PATH=/app/backend
    volumes:
      - ./backend:/app/backend
      - ./config:/app/config
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: Redis cache
  redis:
    image: redis:7-alpine
    container_name: bob-ai-cache
    ports:
      - "6379:6379"
    restart: unless-stopped

# Run:
# docker-compose up -d
# Check status:
# docker-compose ps
# View logs:
# docker-compose logs -f bob-ai
# Stop:
# docker-compose down
```

### Kubernetes Deployment (Advanced)

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bob-ai-v9
  labels:
    app: bob-ai
    version: v9

spec:
  replicas: 3

  selector:
    matchLabels:
      app: bob-ai

  template:
    metadata:
      labels:
        app: bob-ai

    spec:
      containers:
      - name: bob-ai
        image: bob-ai:v9.0
        ports:
        - containerPort: 5000

        env:
        - name: BOB_AI_ENV
          value: "production"
        - name: BOB_AI_LOG_LEVEL
          value: "INFO"

        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"

        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10

        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: bob-ai-service

spec:
  selector:
    app: bob-ai
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

---

## Health Checks & Monitoring

### Health Check Endpoints

```python
# Health check implementation
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Basic health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness check - all components loaded"""
    try:
        from bob_ai_integration_hub import get_integration_hub
        hub = get_integration_hub()
        status = hub.get_hub_status()

        if status['operational']:
            return jsonify({
                'ready': True,
                'components': status['components']
            }), 200
        else:
            return jsonify({
                'ready': False,
                'reason': 'Components not operational'
            }), 503
    except Exception as e:
        return jsonify({
            'ready': False,
            'error': str(e)
        }), 500

@app.route('/metrics', methods=['GET'])
def metrics():
    """Performance metrics"""
    try:
        hub = get_integration_hub()
        status = hub.get_hub_status()

        return jsonify({
            'performance': status['performance'],
            'components': status['components'],
            'uptime_seconds': status.get('uptime', 0)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Monitoring Commands

```bash
# Check service is running
curl http://localhost:5000/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2025-10-27T15:30:00"
# }

# Check readiness (all components loaded)
curl http://localhost:5000/ready

# Check metrics
curl http://localhost:5000/metrics

# Monitor logs (Docker)
docker-compose logs -f bob-ai

# Monitor performance
watch -n 1 'curl http://localhost:5000/metrics | jq ".performance"'
```

---

## Troubleshooting Deployment

### Issue: Module Import Errors

```python
# Symptom: ImportError when loading modules

# Solution 1: Check Python path
import sys
print(sys.path)

# Solution 2: Verify module directory
import os
backend_path = os.path.join(os.getcwd(), 'backend')
if os.path.exists(backend_path):
    sys.path.insert(0, backend_path)

# Solution 3: Check module syntax
python -m py_compile backend/bob_ai_*.py

# Solution 4: Verify dependencies
pip list | grep -E "(numpy|scipy|pandas)"
```

### Issue: Memory Usage High

```python
# Symptom: Process using too much memory

# Solution 1: Check memory usage
import psutil
process = psutil.Process()
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")

# Solution 2: Enable garbage collection
import gc
gc.collect()

# Solution 3: Reduce cache size
# Set BOB_AI_CACHE_SIZE=100 (smaller values)

# Solution 4: Lazy load modules
# Set BOB_AI_LAZY_LOAD_MODULES=true
```

### Issue: Slow Queries

```python
# Symptom: Queries taking >1s to complete

# Solution 1: Check configuration
hub = get_integration_hub()
status = hub.get_hub_status()
print(f"Avg query time: {status['performance']['avg_query_time']}ms")

# Solution 2: Enable caching
# Set BOB_AI_ENABLE_CACHE=true

# Solution 3: Reduce search scope
result = hub.query_knowledge(
    query="music",
    disciplines=["Music Composition"],  # Limit to specific
    limit=5
)

# Solution 4: Use lazy loading
# Set BOB_AI_LAZY_LOAD_MODULES=true
```

### Issue: Module Not Found

```bash
# Symptom: Missing module error

# Solution 1: Verify module exists
ls backend/ | grep bob_ai_v9_

# Solution 2: Check module naming
# Modules should follow pattern: bob_ai_v9_<tier>_<name>.py

# Solution 3: Verify import statements
grep -r "from bob_ai_v9" backend/

# Solution 4: Reinstall dependencies
pip install -r backend/test_requirements.txt
```

---

## Performance Tuning

### Query Performance

```python
# Optimize query performance

# 1. Enable caching
os.environ['BOB_AI_ENABLE_CACHE'] = 'true'
os.environ['BOB_AI_CACHE_SIZE'] = '5000'

# 2. Limit graph depth
from bob_ai_knowledge_graph import get_knowledge_graph
kg = get_knowledge_graph()
related = kg.find_related_disciplines("Music", max_depth=1)  # Shallow search

# 3. Use specific disciplines
result = hub.query_knowledge(
    query="composition",
    disciplines=["Music Composition", "Music Theory"],  # Narrow scope
    limit=5
)

# 4. Profile queries
import cProfile
cProfile.run('hub.query_knowledge("music")')
```

### Memory Optimization

```python
# Optimize memory usage

# 1. Monitor memory
import gc
gc.collect()

# 2. Use generators for large results
def query_iter(queries):
    for query in queries:
        yield hub.query_knowledge(query)

# 3. Clear cache periodically
from bob_ai_integration_hub import get_integration_hub
# Implement cache.clear() method

# 4. Use lazy loading
os.environ['BOB_AI_LAZY_LOAD_MODULES'] = 'true'
```

### Concurrent Request Handling

```python
# Handle concurrent requests

from concurrent.futures import ThreadPoolExecutor
from bob_ai_integration_hub import get_integration_hub

hub = get_integration_hub()

def process_query(query):
    return hub.query_knowledge(query)

# Handle 10 concurrent queries
queries = ["query1", "query2", ..., "query10"]

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(process_query, queries)
    results = list(results)

print(f"Processed {len(results)} queries")
```

---

## Backup & Recovery

### Database Backup

```bash
# Backup knowledge base
cp -r backend/knowledge_base backend/knowledge_base.backup.$(date +%Y%m%d_%H%M%S)

# Backup configuration
cp config.yaml config.yaml.backup.$(date +%Y%m%d_%H%M%S)

# Docker volume backup
docker run --rm -v bob-ai-data:/data -v $(pwd):/backup alpine tar czf /backup/bob-ai-backup.tar.gz -C /data .
```

### Recovery Procedure

```bash
# Restore from backup
cp -r backend/knowledge_base.backup.TIMESTAMP backend/knowledge_base

# Verify restoration
python -c "from bob_ai_integration_hub import get_integration_hub; hub = get_integration_hub(); print('✓ Restored')"

# Run tests to verify
pytest backend/test_bob_ai_v9.py -v
```

---

## Upgrade Procedure

### v8 → v9 Migration

```bash
# 1. Backup current installation
cp -r backend backend.v8.backup

# 2. Pull new code
git pull origin main

# 3. Install new dependencies
pip install -r requirements.txt --upgrade

# 4. Run migrations (if needed)
python scripts/migrate_v8_to_v9.py

# 5. Test
pytest backend/test_bob_ai_v9.py

# 6. Restart service
docker-compose restart bob-ai
```

---

**Deployment Guide Version:** 9.0.0
**Last Updated:** October 27, 2025
**Status:** ✅ Ready for Production Deployment
