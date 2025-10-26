# Framework & Dependency Upgrade Guide - ORFEAS AI Studio

**Version**: 1.0
**Date**: October 26, 2025
**Purpose**: Update Flask, PyTorch, and dependencies to latest stable versions

---

## Overview

This guide provides step-by-step instructions to upgrade all dependencies to latest stable versions with security patches and performance improvements.

### What's Being Upgraded

| Framework | Current | Latest | Status |
|-----------|---------|--------|--------|
| **Python** | 3.10+ | 3.12 | ✅ Supported |
| **Flask** | 2.x | 3.x | ✅ New features |
| **PyTorch** | 1.x | 2.x | ✅ GPU optimized |
| **CUDA** | 12.0 | 12.x | ✅ Latest |
| **pip** | varies | Latest | ✅ Latest |

### Expected Improvements

| Area | Benefit |
|------|---------|
| **Security** | Patch all CVEs, update SSL/TLS |
| **Performance** | 5-15% faster (PyTorch 2.x improvements) |
| **Stability** | Bug fixes, better error handling |
| **Features** | New APIs, better GPU support |
| **Compatibility** | Modern Python ecosystem |

---

## Step 1: Analyze Current Dependencies

### List All Installed Packages

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# List all packages
pip list

# Check for outdated packages
pip list --outdated

# Generate requirements report
pip freeze > current-requirements.txt
```

### Expected Output

```
Package                    Current    Latest    Type
pip                        23.x       24.x      UPDATE
setuptools                 65.x       68.x      UPDATE
wheel                      0.40.x     0.42.x    UPDATE
Flask                      2.3.x      3.0.x     UPDATE
PyTorch                    2.0.x      2.1.x     UPDATE
Werkzeug                   2.3.x      3.x       UPDATE
MarkupSafe                 2.1.x      2.1.x     OK
Jinja2                     3.1.x      3.1.x     OK
```

### Security Audit

```bash
# Check for security vulnerabilities
pip install pip-audit
pip-audit

# Expected output:
# Found X vulnerabilities in Y dependencies
# WARNING / CRITICAL / HIGH (with fix recommendations)
```

---

## Step 2: Update Python Version (Optional but Recommended)

### Check Current Python

```bash
python --version
# Current: Python 3.10.x
# Target: Python 3.12.x
```

### Upgrade Python (Ubuntu/Linux)

```bash
# Check available versions
python3 --version
python3.12 --version  # Check if available

# Install Python 3.12
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev

# Set as default (optional)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

# Verify
python3 --version
```

### Create New Virtual Environment

```bash
# With Python 3.12
python3.12 -m venv venv-new

# Activate
source venv-new/bin/activate

# Verify
python --version  # Should show 3.12.x
```

---

## Step 3: Backup Current Dependencies

### Save Current Environment

```bash
# Backup requirements
cp requirements.txt requirements.txt.backup

# Save freeze file
pip freeze > venv-current-freeze.txt

# Save pip cache (optional)
cp -r ~/.cache/pip ~/.cache/pip.backup
```

---

## Step 4: Update Core Dependencies

### Update pip, setuptools, wheel First

```bash
# Activate virtual environment
source venv/bin/activate

# Update pip
pip install --upgrade pip

# Update setuptools and wheel
pip install --upgrade setuptools wheel

# Verify
pip --version
```

### Expected Versions

```
pip 24.x (current version)
setuptools 68.x
wheel 0.42.x
```

---

## Step 5: Update Flask & Web Framework

### Check Flask Version

```bash
pip show Flask

# Current:
# Name: Flask
# Version: 2.3.x
```

### Update Flask

```bash
# Update to Flask 3.x
pip install --upgrade Flask

# Verify
pip show Flask
pip show Flask-SocketIO Flask-CORS Werkzeug

# Expected:
# Flask 3.x
# Werkzeug 3.x
# Flask-SocketIO 5.x
# Flask-CORS 4.x
```

### Check for Breaking Changes

```python
# Test imports
python -c "import Flask; print(Flask.__version__)"
python -c "from flask import Flask; app = Flask(__name__); print('Flask OK')"
python -c "from flask_socketio import SocketIO; print('SocketIO OK')"
```

---

## Step 6: Update PyTorch & GPU Libraries

### Check Current PyTorch Version

```bash
python -c "import torch; print(torch.__version__)"

# Current:
# 2.0.x+cuXXX

python -c "import torch; print(torch.cuda.is_available())"
# Expected: True
```

### Update PyTorch

```bash
# Install latest PyTorch (GPU support)
pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Expected download size: ~2-3 GB
# This installs:
# - torch 2.1.x+cuXXX
# - torchvision (for image processing)
# - torchaudio (for audio processing)
```

### Verify PyTorch Installation

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
python -c "import torch; print(f'GPU Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
python -c "import torch; print(f'GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')"
```

### Expected Output

```
PyTorch: 2.1.0+cu121
CUDA Available: True
GPU Device: NVIDIA GeForce RTX 3090
GPU Memory: 24.0 GB
```

---

## Step 7: Update Other Key Dependencies

### Update Important Packages

```bash
# Image processing
pip install --upgrade Pillow opencv-python

# Scientific computing
pip install --upgrade numpy scipy scikit-learn

# Data handling
pip install --upgrade pandas

# API & serialization
pip install --upgrade requests jsonschema

# Database (if used)
pip install --upgrade sqlalchemy

# Async
pip install --upgrade aiohttp aiofiles

# Testing
pip install --upgrade pytest pytest-asyncio

# Code quality
pip install --upgrade black flake8 pylint

# Redis (if using caching)
pip install --upgrade redis

# Gunicorn (if using production)
pip install --upgrade gunicorn

# Logging
pip install --upgrade python-json-logger coloredlogs
```

### Batch Update All

```bash
# Update all packages to latest (use with caution)
pip install --upgrade -r requirements.txt

# Or update specific packages only
pip install --upgrade Flask PyTorch pandas numpy requests
```

---

## Step 8: Generate New Requirements.txt

### Create Updated Requirements File

```bash
# Generate new requirements from upgraded environment
pip freeze > requirements-updated.txt

# Compare old vs new
diff requirements.txt requirements-updated.txt

# Or view side by side (on Windows)
fc requirements.txt requirements-updated.txt
```

### Expected Changes

```diff
Flask==2.3.0          → Flask==3.0.0
Werkzeug==2.3.0       → Werkzeug==3.0.0
torch==2.0.0+cu118    → torch==2.1.0+cu121
torchvision==0.15.0   → torchvision==0.16.0
numpy==1.24.0         → numpy==1.26.0
pandas==2.0.0         → pandas==2.1.0
```

### Commit Updated Requirements

```bash
# Backup and replace
cp requirements.txt requirements.txt.old
cp requirements-updated.txt requirements.txt

# Commit to git
git add requirements.txt
git commit -m "chore: upgrade dependencies to latest stable versions"
```

---

## Step 9: Test Application After Upgrade

### Run Unit Tests

```bash
# Activate environment
source venv/bin/activate

# Run test suite
pytest backend/tests/ -v

# Expected: All tests pass
```

### Test Key Functionality

```bash
# Test Flask
python -c "from backend.main import app; print('Flask OK')"

# Test PyTorch
python -c "import torch; x = torch.randn(3, 3).cuda(); print('PyTorch OK')"

# Test Redis (if using)
python -c "from redis_config import initialize_redis; initialize_redis(); print('Redis OK')"

# Test model loading
python -c "from hunyuan_integration import get_3d_processor; print('Model loading OK')"
```

### Start Backend Server

```bash
# Navigate to backend directory
cd backend

# Start Flask server
python main.py

# Expected in logs:
# [SUCCESS] ✅ Flask server running on 0.0.0.0:5000
# [SUCCESS] ✅ PyTorch initialized
# [SUCCESS] ✅ GPU available
```

### Test API Endpoints

```bash
# In another terminal
curl http://localhost:5000/health

# Expected response:
# {"status": "ok", "version": "1.0"}
```

---

## Step 10: Check for Deprecation Warnings

### Monitor Startup Logs

```bash
# Run with deprecation warnings visible
python -W all main.py 2>&1 | grep -i "deprecat"

# Check for warnings in specific modules
python -W all -c "from hunyuan_integration import get_3d_processor; print('OK')" 2>&1 | grep -i "warn"
```

### Handle Deprecations

If you see deprecation warnings:

```python
# Example deprecation fix in code
# BEFORE (deprecated):
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# AFTER (better):
# Fix the actual code to use new API instead of ignoring warnings
```

---

## Step 11: Performance Benchmarking

### Benchmark Generation Speed

```python
# Create benchmark_performance.py
import time
import torch
from hunyuan_integration import get_3d_processor

# Before upgrade
print("Before upgrade baseline: [recorded earlier]")

# After upgrade
processor = get_3d_processor()

# Warm up
test_image = torch.randn(1, 3, 512, 512)

# Benchmark
start = time.time()
for i in range(3):
    _ = processor.generate_3d(test_image)
    elapsed = time.time() - start
    print(f"Generation {i+1}: {elapsed:.2f}s")

print(f"Average: {elapsed/3:.2f}s per generation")
```

### Expected Improvements

| Operation | Before | After | Improvement |
|-----------|--------|-------|------------|
| Model loading | 24s | 20s | **17% faster** |
| Shape generation | 30s | 26s | **13% faster** |
| Texture generation | 45s | 38s | **16% faster** |
| Overall generation | 75s | 64s | **15% faster** |

---

## Step 12: Update Documentation

### Update Version Info

Update in documentation:

```markdown
## System Requirements

- Python: 3.12+ (upgraded from 3.10)
- PyTorch: 2.1.x+ (upgraded from 2.0.x)
- CUDA: 12.1+ (upgraded from 12.0)
- Flask: 3.x (upgraded from 2.3)
- Node: 18+ (for frontend)
```

### Create Migration Guide

```markdown
## Upgrade Instructions

### For Development

1. Backup current environment:
   pip freeze > requirements-old.txt

2. Update dependencies:
   pip install --upgrade -r requirements.txt

3. Test locally:
   pytest backend/tests/ -v
   python backend/main.py

4. Verify performance:
   python benchmark_performance.py

### For Production

1. Test in staging first
2. Run full test suite
3. Verify all endpoints
4. Monitor performance metrics
5. Deploy with zero downtime (rolling update)
```

---

## Step 13: Deployment Strategy

### Staging Deployment

```bash
# On staging server
cd /opt/orfeas-ai-studio

# Backup current venv
mv venv venv-old

# Create new venv with Python 3.12
python3.12 -m venv venv

# Activate and install new requirements
source venv/bin/activate
pip install -r requirements.txt

# Test
systemctl restart orfeas-ai-studio-staging
curl http://staging.orfeas:5000/health

# Monitor for 24 hours
# Check logs, metrics, performance
```

### Production Deployment (Blue-Green)

```bash
# Blue-Green deployment strategy

# Current (Blue): venv-prod-v1
# New (Green): venv-prod-v2

# Step 1: Create new environment
cp -r venv-prod-v1 venv-prod-v2
cd venv-prod-v2
pip install --upgrade -r requirements.txt

# Step 2: Run tests
systemctl start orfeas-ai-studio-test --venv venv-prod-v2
curl http://localhost:5001/health

# Step 3: Switch traffic
# Update systemd service to use venv-prod-v2
# Systemd restarts, traffic switches

# Step 4: Monitor
# Watch metrics for 1 hour

# Step 5: Keep old env as rollback
# Keep venv-prod-v1 for 24 hours, then delete
```

### Rollback Procedure

```bash
# If issues occur:

# Switch back to old environment
systemctl stop orfeas-ai-studio
# Update systemd service file to use venv-old
systemctl start orfeas-ai-studio

# Verify
curl http://localhost:5000/health

# Investigate issue
grep -i error /var/log/orfeas/*.log
```

---

## Step 14: Security & Compliance

### Check for Security Vulnerabilities

```bash
# Install security checker
pip install pip-audit bandit

# Run security audit
pip-audit
# Expected: No vulnerabilities (or only low-risk ones)

# Run code security check
bandit -r backend/

# Check for secrets in code
pip install detect-secrets
detect-secrets scan backend/
```

### Update Security Headers (in Nginx)

```nginx
# In /etc/nginx/sites-available/orfeas-ai-studio

# Add security headers
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer" always;
add_header Content-Security-Policy "default-src 'self'" always;
```

---

## Step 15: Create Upgrade Checklist

- [ ] Backup current requirements.txt
- [ ] Backup current virtual environment
- [ ] Save pip freeze output
- [ ] Create new virtual environment (optional Python 3.12)
- [ ] Update pip, setuptools, wheel
- [ ] Update Flask to 3.x
- [ ] Update PyTorch to 2.1.x
- [ ] Update other dependencies
- [ ] Run unit tests (all must pass)
- [ ] Test backend startup
- [ ] Test API endpoints
- [ ] Test GPU functionality
- [ ] Check deprecation warnings
- [ ] Benchmark performance
- [ ] Deploy to staging
- [ ] Monitor staging for 24 hours
- [ ] Deploy to production (blue-green)
- [ ] Monitor production for 1 hour
- [ ] Update documentation
- [ ] Commit changes to git

---

## Troubleshooting

### Pip Install Fails

```bash
# Clear pip cache
pip cache purge

# Try again with verbose output
pip install --upgrade -vvv torch

# If CUDA version mismatch:
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### PyTorch GPU Not Detected

```bash
# Verify CUDA installation
nvidia-smi

# Check CUDA version
python -c "import torch; print(torch.version.cuda)"

# Reinstall with correct CUDA version
pip uninstall torch -y
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### Tests Fail After Upgrade

```bash
# Check what broke
pytest backend/tests/test_hunyuan.py -v

# Common causes:
# 1. API changes in new versions
# 2. Deprecation warnings treated as errors
# 3. Different tensor shapes or dtypes

# Fix test files to match new APIs
```

### Performance Degraded

```bash
# Profile to find bottleneck
python -m cProfile -s cumtime backend/main.py

# Check if GPU is being used
nvidia-smi  # Should show GPU usage

# Verify batch sizes and memory
torch.cuda.memory_summary()
```

---

## Summary

After completing all upgrade steps:

✅ Python 3.12 (latest stable)
✅ Flask 3.x (latest stable)
✅ PyTorch 2.1.x (latest stable, +15% performance)
✅ All dependencies current with security patches
✅ All tests passing
✅ Production deployment verified

**Expected Benefits**:

- 10-15% performance improvement
- All security vulnerabilities patched
- Better GPU support and CUDA optimization
- Modern Python features available
- Better compatibility with ecosystem

---

**Next Steps**:

1. Start with backing up current environment
2. Follow upgrade steps in order
3. Test thoroughly before production
4. Use blue-green deployment for zero downtime
5. Monitor metrics after deployment

**Timeline**: 2-4 hours for development, 1 day for production deployment

**Risk Level**: Low (with proper testing and staging first)
